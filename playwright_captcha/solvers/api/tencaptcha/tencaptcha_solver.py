import logging
from typing import Union

from playwright.async_api import Page, Frame, ElementHandle

from playwright_captcha.solvers.api.api_solver_base import ApiSolverBase
from playwright_captcha.solvers.api.tencaptcha.tencaptcha.async_solver import AsyncTenCaptcha
from playwright_captcha.solvers.base_solver import CaptchaType
from playwright_captcha.types import FrameworkType
from playwright_captcha.types.solvers import SolverType
from playwright_captcha.utils.misc import split_kwargs

logger = logging.getLogger(__name__)


class TenCaptchaSolver(ApiSolverBase):
    """10Captcha external solving service"""

    type: SolverType = SolverType.tencaptcha

    def __init__(self, framework: FrameworkType, page: Page,
                 async_ten_captcha_client: AsyncTenCaptcha,
                 max_attempts: int = 3, attempt_delay: int = 5):
        """
        Initialize the 10Captcha solver

        :param page: Playwright Page object
        :param async_ten_captcha_client: AsyncTenCaptcha client instance
        :param max_attempts: Maximum number of attempts to solve the captcha
        :param attempt_delay: Delay in seconds between attempts to solve the captcha
        """

        super().__init__(framework=framework, page=page, max_attempts=max_attempts, attempt_delay=attempt_delay)

        self.async_ten_captcha_client = async_ten_captcha_client

    async def _solve_captcha_once(
            self,
            captcha_container: Union[Page, Frame, ElementHandle],
            captcha_type: CaptchaType,
            **kwargs
    ) -> str:
        """
        Solve captcha using 10Captcha API

        :param captcha_container: The container where the captcha is located (Page, Frame, or ElementHandle)
        :param captcha_type: The type of captcha to solve (CaptchaType enum)
        :param kwargs: Additional parameters for the captcha solving request (e.g. sitekey, useragent, pagedata)

        :return: The solved captcha token as a string
        """

        solver_data = await self._get_solver_data(captcha_type)
        solver = solver_data.get('solver')

        # get url and set it in kwargs if not provided
        url = kwargs.get('url')
        if not url:
            url = self.page.url
            kwargs['url'] = url

        # automatically detect captcha data needed for solving/applying the captcha
        captcha_data = await self.detect_captcha_data(captcha_container, captcha_type)

        # convert captcha_data keys to match 10Captcha API syntax
        param_name_mapping = {
            'site_key': 'sitekey',
            'user_agent': 'useragent',
            'page_data': 'pagedata'
        }
        for old_key, new_key in param_name_mapping.items():
            if old_key in captcha_data:
                captcha_data[new_key] = captcha_data.pop(old_key)

        # merge detected captcha data with provided kwargs
        for key, value in captcha_data.items():
            if key not in kwargs:
                kwargs[key] = value
                logger.info(f'Detected {key}: {value}')

        # split kwargs to separate ones needed to apply the captcha from ones needed to solve it
        apply_captcha_kwargs, kwargs = split_kwargs('_apply_captcha_', kwargs)

        # solve the captcha using the appropriate solver function
        result = await solver(self.async_ten_captcha_client, **kwargs)

        token = result.get('code')

        await self.apply_captcha(captcha_type, token, **apply_captcha_kwargs)

        logger.info(f"Successfully solved {captcha_type.name} captcha")
        return token

    async def get_balance(self) -> float:
        """
        Get account balance

        :return: The current balance as a float
        """

        result = await self.async_ten_captcha_client.balance()
        return float(result)

    def get_name(self) -> str:
        return "10Captcha Solver"
