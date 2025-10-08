import logging

from playwright.async_api import Page

from playwright_captcha.utils.exceptions import CaptchaApplyingError
from playwright_captcha.utils.js_script import load_js_script

logger = logging.getLogger(__name__)


async def apply_cloudflare_interstitial_captcha(page: Page, token: str, *args, **kwargs) -> None:
    """
    Apply a token to bypass Cloudflare interstitial captcha and submit the verification
    
    :param page: Playwright Page containing the captcha
    :param token: The token returned by solving the captcha

    :raises CaptchaApplyingError: If the token could not be applied
    """

    logger.debug('Attempting to apply Cloudflare Interstitial token...')

    try:
        if getattr(page.add_init_script, 'is_camoufox_workaround', None) is True:
            # use main world data for the add_init_script workaround (camoufox)
            js_script = await load_js_script('appliers/applyCloudflareInterstitial_camoufox.js')
            # yeah, looks weird with formating js but otherwise there is an error because of "mw:" prefix in the script
            js_script = js_script.format(token=token)
        else:
            js_script = await load_js_script('appliers/applyCloudflareInterstitial.js')

        # apply multiple times just in case - not always works on the first try for this captcha type
        for attempt in range(5):
            await page.evaluate(js_script, token)

        logger.info("Token applied successfully")

        return
    except Exception as e:
        logger.error(f"Error applying token to Cloudflare Interstitial: {e}", exc_info=True)

    raise CaptchaApplyingError("Failed to apply Cloudflare Interstitial token")
