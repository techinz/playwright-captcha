import logging
from typing import Union

from playwright.async_api import Page, Frame, ElementHandle

from playwright_captcha.solvers.click.cloudflare import solve_cloudflare_by_click
from playwright_captcha.types import FrameworkType
from playwright_captcha.utils.validators import validate_required_params

logger = logging.getLogger(__name__)


async def solve_cloudflare_interstitial_click(framework: FrameworkType,
                                              page: Page,
                                              captcha_container: Union[Page, Frame, ElementHandle],
                                              **kwargs) -> None:
    """
    Solve Cloudflare Interstitial captcha using click-based method

    :param framework: Framework type (e.g. PLAYWRIGHT, PATCHRIGHT, CAMOUFOX)
    :param page: Playwright Page object where the captcha is located
    :param captcha_container: The container where the captcha is located (Page, Frame, or ElementHandle)
    :param kwargs: Parameters for the click solver, e.g. 'expected_content_selector'
    """

    logger.debug('Solving Cloudflare Interstitial captcha using click...')

    validate_required_params([], kwargs)

    # solve the captcha using the appropriate solver function
    await solve_cloudflare_by_click(
        framework=framework,
        page=page,
        captcha_container=captcha_container,
        challenge_type='interstitial',
        **kwargs)

    logger.debug(f'Solved Cloudflare Interstitial captcha')
