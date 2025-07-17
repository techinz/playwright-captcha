import logging
from typing import Union

from playwright.async_api import Page, Frame, ElementHandle

from playwright_captcha.solvers.base_solver import BaseSolver, CaptchaType
from playwright_captcha.types import FrameworkType
from playwright_captcha.types.solvers import SolverType
from playwright_captcha.utils.misc import split_kwargs

logger = logging.getLogger(__name__)


class ClickSolver(BaseSolver):
    """Click solver for captchas that can be solved by automated clicking"""

    type: SolverType = SolverType.click

    def __init__(self, framework: FrameworkType, page: Page, max_attempts: int = 3, attempt_delay: int = 5):
        """
        Initialize the Click-based captcha solver

        :param page: Playwright Page object where the captcha is located
        :param max_attempts: Maximum number of attempts to solve the captcha
        :param attempt_delay: Delay in seconds between attempts to solve the captcha
        """

        super().__init__(framework=framework, page=page, max_attempts=max_attempts, attempt_delay=attempt_delay)

    async def _solve_captcha_once(
            self,
            captcha_container: Union[Page, Frame, ElementHandle],
            captcha_type: CaptchaType,
            **kwargs
    ) -> None:
        """
        Solve captcha by clicking

        :param captcha_container: The container where the captcha is located (Page, Frame, or ElementHandle)
        :param captcha_type: The type of captcha to solve (CaptchaType enum)
        :param kwargs: Additional parameters for the captcha solving request (e.g. sitekey, useragent, pagedata)
        """

        solver_data = await self._get_solver_data(captcha_type)
        solver = solver_data.get('solver')

        # split kwargs to separate ones needed to apply the captcha from ones needed to solve it
        apply_captcha_kwargs, kwargs = split_kwargs('_apply_captcha_', kwargs)

        # solve the captcha using the appropriate solver function
        await solver(framework=self.framework, page=self.page, captcha_container=captcha_container, **kwargs)

        # no need to apply captcha here, as click-based solvers don't return tokens

    def get_name(self) -> str:
        return "Click-based Captcha Solver"
