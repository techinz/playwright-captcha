import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Union, ClassVar, Dict, Callable, Optional, Any

from playwright.async_api import Page, Frame, ElementHandle

from playwright_captcha.types import CaptchaType, FrameworkType
from playwright_captcha.types.solvers import SolverType
from playwright_captcha.utils.js_script import load_js_script

logger = logging.getLogger(__name__)


class BaseSolver(ABC):
    """Universal base class for all captcha solvers"""

    type: SolverType = SolverType.base  # default solver type, should be overridden in subclasses

    _detectors: ClassVar[Dict[CaptchaType, Callable]] = {}
    _solvers: ClassVar[Dict[SolverType, Dict[CaptchaType, Dict[str, Callable]]]] = {}
    _appliers: ClassVar[Dict[CaptchaType, Callable]] = {}

    def __init__(self, framework: FrameworkType, page: Page, max_attempts: int = 3, attempt_delay: int = 5):
        """
        Initialize the base solver

        :param page: Playwright Page object where the captcha is located
        :param max_attempts: Maximum number of attempts to solve the captcha
        :param attempt_delay: Delay in seconds between attempts to solve the captcha
        """

        self.framework = framework
        self.page = page
        self.max_attempts = max_attempts
        self.attempt_delay = attempt_delay

        self._prepare_called = False
        self._cleanup_called = False

        self._original_methods = {}  # to store original methods that need to be restored on cleanup

    # context manager
    async def __aenter__(self):
        """Async context manager entry"""
        await self.prepare()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with cleanup"""
        await self.cleanup()

    @classmethod
    def register_detector(cls, captcha_type: CaptchaType, detector_func: Callable) -> None:
        """
        Register a detector function for a captcha type

        :param captcha_type: Type of captcha to register the detector for
        :param detector_func: Function that detects captcha data (e.g. site key, callback) for the given captcha type
        """

        cls._detectors[captcha_type] = detector_func

    @classmethod
    def register_solver(cls, solver_type: SolverType, captcha_type: CaptchaType, solver_func: Callable,
                        **kwargs) -> None:
        """
        Register a solver function for a captcha type under a specific solver type

        :param solver_type: Type of solver (e.g. SolverType.click, SolverType.twocaptcha)
        :param captcha_type: Type of captcha to register the solver for
        :param solver_func: Function that solves the captcha of the given type
        """

        if solver_type not in cls._solvers:
            cls._solvers[solver_type] = {}
        cls._solvers[solver_type][captcha_type] = {'solver': solver_func, **kwargs}

    @classmethod
    def register_applier(cls, captcha_type: CaptchaType, applier_func: Callable) -> None:
        """
        Register an applier function for a captcha type

        :param captcha_type: Type of captcha to register the applier for
        :param applier_func: Function that applies the solved captcha token to the page
        """

        cls._appliers[captcha_type] = applier_func

    async def prepare(self) -> None:
        """Prepare the solver, e.g. apply patches or requests interceptors for self.detect_data()"""

        if self._prepare_called:
            logger.warning(f"{self.get_name()} is already prepared, skipping prepare()")
            return

        self._prepare_called = True

        await self._prepare_framework()

        # monkey-patch to open closed shadowRoots
        await self.page.add_init_script(await load_js_script('patches/unlockShadowRoot.js'))

        if self.type == SolverType.twocaptcha:  # or other api-based solvers that needed this data
            # cloudflare interstitial requires to inject a script to intercept the challenge parameters
            await self.page.add_init_script(await load_js_script('patches/interceptCloudflareInterstitialData.js'))

    async def _prepare_framework(self) -> None:
        """Framework preparation"""

        if self.framework == FrameworkType.CAMOUFOX:
            await self._prepare_camoufox()
        elif self.framework == FrameworkType.PATCHRIGHT:
            await self._prepare_patchright()
        else:
            await self._prepare_playwright()

    async def _prepare_camoufox(self) -> None:
        """Camoufox preparation"""

        logger.info("Applying Camoufox optimizations...")

        # check if workaround is needed
        if not (hasattr(self.page, 'add_init_script') and
                hasattr(self.page.add_init_script, 'is_camoufox_workaround')):
            logger.info("Applying add_init_script workaround for Camoufox...")
            from playwright_captcha.utils.camoufox_add_init_script.add_init_script import add_init_script, \
                get_addon_path, clean_scripts

            addon_path = get_addon_path()
            clean_scripts(addon_path)

            # store original method for cleanup
            self._original_methods['add_init_script'] = getattr(self.page, 'add_init_script', None)

            # apply the workaround
            self.page.add_init_script = lambda script: add_init_script(script, addon_path)
            self.page.add_init_script.is_camoufox_workaround = True

            logger.info("Camoufox workaround applied")
        else:
            logger.info("Camoufox workaround already applied")

    async def _prepare_patchright(self) -> None:
        """Patchright preparation"""

        # patch patchright's page.evaluate() to execute out of the isolated context by default
        original_evaluate = self.page.evaluate
        self._original_methods['evaluate'] = original_evaluate

        async def evaluate_wrapper(expression: str,
                                   arg: Optional[Any] = None,
                                   *,
                                   isolated_context: Optional[bool] = False):
            return await original_evaluate(expression, arg, isolated_context=isolated_context)

        self.page.evaluate = evaluate_wrapper

    async def _prepare_playwright(self) -> None:
        """Playwright preparation"""
        pass

    async def cleanup(self) -> None:
        """Cleanup resources and restore original methods"""

        if self._cleanup_called:
            return

        self._cleanup_called = True
        logger.info(f"Cleaning up {self.get_name()}...")

        for method_name, original_method in self._original_methods.items():
            if hasattr(self.page, method_name):
                setattr(self.page, method_name, original_method)
                logger.info(f"Restored original {method_name} method")

        await self._cleanup_framework()

        logger.info(f"{self.get_name()} cleanup completed")

    async def _cleanup_framework(self) -> None:
        """Framework cleanup"""
        pass

    async def detect_captcha_data(self, captcha_container: Union[Page, Frame, ElementHandle], captcha_type: CaptchaType,
                                  **kwargs) -> Dict:
        """
        Detect captcha data needed for solving or submitting such as site key, callback, etc.

        :param captcha_container: Page, Frame or ElementHandle containing the captcha
        :param captcha_type: Type of captcha to detect data for
        :param kwargs: Additional parameters passed to the detector function (e.g. useragent, pagedata)

        :return: Dictionary containing the detected captcha data (e.g. site key, callback)
        """

        detector = self._detectors.get(captcha_type)

        # get the required captcha data (e.g. site key) if not provided
        # first get data found in the page and then in the captcha container (the captcha container has priority,
        # so if the same key is found in both, the one from the container will be used)
        data = {}
        data.update(await detector(queryable=self.page, **kwargs))
        # don't call it for captcha container for cloudflare interstitial, because:
        # 1. detection method for cloudflare can be called only 1 time after reload
        # 2. cloudflare interstitial is a whole-page captcha
        if captcha_type != CaptchaType.CLOUDFLARE_INTERSTITIAL:
            data.update(await detector(queryable=captcha_container, **kwargs))

        return data

    async def _get_solver_data(self, captcha_type: CaptchaType) -> Dict:
        """
        Get the solver data for the given captcha type

        :param captcha_type: Type of captcha to get the solver data for

        :return: Dictionary containing the solver data

        :raises ValueError: If no solver is registered for the given type and captcha type
        """

        solver_data = self._solvers.get(self.type, {}).get(captcha_type)
        if not solver_data:
            raise ValueError(f"Unsupported: No solver registered for {self.type} and {captcha_type.value}")

        return solver_data

    @abstractmethod
    async def _solve_captcha_once(
            self,
            captcha_container: Union[Page, Frame, ElementHandle],
            captcha_type: CaptchaType,
            **kwargs
    ) -> Union[bool, str]:
        """
        Universal captcha solving function

        :param captcha_container: Page, Frame or ElementHandle containing the captcha
        :param captcha_type: Type of captcha to solve
        **kwargs: Additional parameters passed to the solver

        :return bool or str: True/False for success-based solvers, token string for token-based solvers

        Example:
            page = await context.new_page() # create a new page

            # initialize the solver
            solver = TwoCaptchaSolver(
                page=page,
                async_two_captcha_client=AsyncTwoCaptcha("your_api_key")
            )
            await solver.prepare() # prepare the solver (e.g. apply patches)

            await page.goto("https://example.com") # navigate to the page with captcha

            # solve the captcha
            token = await solver.solve_captcha(
                captcha_container=page,
                captcha_type=CaptchaType.CLOUDFLARE_INTERSTITIAL
            )
        """

        raise NotImplementedError('This method must be implemented in subclasses')

    async def solve_captcha(self, captcha_container, captcha_type, **kwargs) -> Union[bool, str]:
        """
        Universal captcha solving function

        :param captcha_container: Page, Frame or ElementHandle containing the captcha
        :param captcha_type: Type of captcha to solve
        **kwargs: Additional parameters passed to the solver

        :return bool or str: True/False for success-based solvers, token string for token-based solvers

        :raises RuntimeError: If the solver is not prepared
        :raises ValueError: If the captcha type is not supported by this solver
        :raises TypeError: If captcha_type is not a CaptchaType enum value
        :raises Exception: If an error occurs while solving the captcha
        """

        # ensure the solver is prepared
        if not self._prepare_called:
            raise RuntimeError(
                "Solver must be prepared by calling self.prepare() after page initializing before solving captchas"
            )

        # ensure this is not the base solver (overridden in subclasses)
        if self.type == SolverType.base:
            raise ValueError(f"BaseSolver is an abstract class and cannot be used directly")

        # ensure captcha_type is a valid CaptchaType
        if not isinstance(captcha_type, CaptchaType):
            raise TypeError(f"captcha_type must be a CaptchaType enum value, not {type(captcha_type).__name__}")

        # verify this solver can handle this captcha type
        if not self.can_solve(captcha_type):
            raise ValueError(f"{self.get_name()} cannot solve {captcha_type.value} captchas")

        solver_data = await self._get_solver_data(captcha_type)

        last_exception = None
        for attempt in range(1, self.max_attempts + 1):
            logger.info(f'Solving {captcha_type.value} captcha, attempt {attempt}/{self.max_attempts}')

            try:
                return await self._solve_captcha_once(captcha_container, captcha_type, **kwargs)
            except Exception as e:
                logger.exception(f'Error solving {captcha_type.value} captcha on attempt {attempt}: {e}', exc_info=True)

                last_exception = e

            if attempt < self.max_attempts:
                if solver_data.get('reload_on_fail', False):
                    logger.info('Reloading page before next attempt...')
                    await self.page.reload()

                logger.info(f'Retrying in {self.attempt_delay} seconds...')
                await asyncio.sleep(self.attempt_delay)

        raise last_exception

    async def apply_captcha(self, captcha_type: CaptchaType, token: str, **kwargs) -> None:
        """
        Apply the solved captcha token to the page

        :param captcha_type: Type of captcha to apply
        :param token: The solved captcha token to apply
        :param kwargs: Additional parameters for the captcha application (e.g. sitekey, useragent, pagedata)

        :raises ValueError: If no applier is registered for the given captcha type
        """

        apply_captcha = self._appliers.get(captcha_type)
        if not apply_captcha:
            raise ValueError(f"No captcha applier found for {captcha_type.value}")

        await apply_captcha(self.page, token, **kwargs)

    def can_solve(self, captcha_type: CaptchaType) -> bool:
        """
        Check if this solver can solve this captcha type

        :param captcha_type: The type of captcha to check

        :return: True if the captcha type is supported, False otherwise
        """

        return captcha_type in self._solvers.get(self.type, {})

    @abstractmethod
    def get_name(self) -> str:
        """ Get the display name of this solver """
        pass
