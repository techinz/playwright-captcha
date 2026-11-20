import json
import logging

from playwright.async_api import Page

from playwright_captcha.utils.exceptions import CaptchaApplyingError
from playwright_captcha.utils.js_script import load_js_script

logger = logging.getLogger(__name__)


async def apply_cutcaptcha(page: Page, token: str, *args, **kwargs) -> None:
    """
    Apply a solved CutCaptcha token to the page

    :param page: Playwright Page containing the captcha
    :param token: The token returned by solving the captcha

    :raises CaptchaApplyingError: If the token could not be applied
    """

    logger.debug("Attempting to apply CutCaptcha token...")

    js_script = await load_js_script('appliers/applyCutCaptcha.js')

    if getattr(page.add_init_script, 'is_camoufox_workaround', None) is True:
        # run in the main world (camoufox), otherwise page callbacks and window.cutcaptcha are not reachable
        applied = await page.evaluate(f'mw:({js_script})({json.dumps(token)})')
    else:
        applied = await page.evaluate(js_script, token)

    if not applied:
        raise CaptchaApplyingError("Failed to apply CutCaptcha token: no CutCaptcha widget found")

    logger.info("Successfully applied CutCaptcha token")
