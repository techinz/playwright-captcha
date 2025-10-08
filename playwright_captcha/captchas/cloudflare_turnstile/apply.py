import logging

from playwright.async_api import Page

from playwright_captcha.utils.exceptions import CaptchaApplyingError
from playwright_captcha.utils.js_script import load_js_script

logger = logging.getLogger(__name__)


async def apply_cloudflare_turnstile_captcha(page: Page, token: str, *args, **kwargs) -> None:
    """
    Apply a token to bypass Cloudflare interstitial captcha

    :param page: Playwright Page containing the captcha
    :param token: The token returned by solving the captcha

    :raises CaptchaApplyingError: If the token could not be applied
    """

    # try to find and fill the input field(s)
    logger.debug("Attempting to apply Cloudflare Turnstile token...")

    if getattr(page.add_init_script, 'is_camoufox_workaround', None) is True:
        # use main world data for the add_init_script workaround (camoufox)
        js_script = await load_js_script('appliers/applyCloudflareTurnstile_camoufox.js')
        # yeah, looks weird with formating js but otherwise there is an error because of "mw:" prefix in the script
        js_script = js_script.format(token=token)
    else:
        js_script = await load_js_script('appliers/applyCloudflareTurnstile.js')

    await page.evaluate(js_script, token)

    # try to find and call callback function
    logger.debug("Attempting to call Turnstile callback functions...")

    # even tho we don't check if the token is applied successfully, we try to submit it anyway. won't hurt.
    if getattr(page.add_init_script, 'is_camoufox_workaround', None) is True:
        # use main world data for the add_init_script workaround (camoufox)
        js_script = await load_js_script('appliers/submitCloudflareTurnstile_camoufox.js')
        # yeah, looks weird with formating js but otherwise there is an error because of "mw:" prefix in the script
        js_script = js_script.format(token=token)
    else:
        js_script = await load_js_script('appliers/submitCloudflareTurnstile.js')

    callback_result = await page.evaluate(js_script, token)
    if not callback_result and getattr(page.add_init_script, 'is_camoufox_workaround', None) is not True:
        raise CaptchaApplyingError("Failed to apply Cloudflare Turnstile token")

    logger.info("Successfully called Turnstile callback")
