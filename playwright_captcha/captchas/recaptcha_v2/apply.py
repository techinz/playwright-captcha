import logging

from playwright.async_api import Page

from playwright_captcha.utils.exceptions import CaptchaApplyingError
from playwright_captcha.utils.js_script import load_js_script

logger = logging.getLogger(__name__)


async def apply_recaptcha_v2_captcha(page: Page, token: str, *args, **kwargs) -> None:
    """
    Apply a token to the reCAPTCHA v2 challenge on the page

    :param page: Playwright Page containing the captcha
    :param token: The token returned by solving the captcha

    :raises CaptchaApplyingError: If the token could not be applied
    """

    logger.debug("Attempting to apply reCAPTCHA v2 token...")

    applied = await page.evaluate(await load_js_script('appliers/applyRecaptchaV2.js'), token)

    if not applied:
        raise CaptchaApplyingError("Failed to apply reCAPTCHA v2 token")

    logger.info("Successfully applied reCAPTCHA v2 token")
