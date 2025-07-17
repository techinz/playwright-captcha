import logging
import time
from typing import Union

from playwright.async_api import Page, Frame, ElementHandle

from playwright_captcha.utils.exceptions import CaptchaDataDetectionError

try:
    from patchright.async_api import Page as PatchrightPage
except ImportError:
    PatchrightPage = None

logger = logging.getLogger(__name__)


async def detect_interstitial_data(queryable: Union[Page, Frame, ElementHandle], **kwargs) -> dict:
    """
    Detect the data (e.g. site key) and other possible params of the captcha

    :param queryable: The Playwright Page, Frame, or ElementHandle to search for the captcha data.
    :param kwargs: Additional parameters

    :return: A dictionary containing the detected captcha data needed for solving

    :raises CaptchaDataDetectionError: If the captcha data cannot be detected
    """

    logger.debug('Detecting Cloudflare interstitial data...')

    data = {}

    # for this captcha type detection should work only on Page object
    page = queryable
    if not any((
            isinstance(page, Page),
            PatchrightPage and isinstance(page, PatchrightPage)
    )):
        return data

    intercepted_params = {}

    # wait for captcha to initialize (max 30 seconds)
    max_wait_time = 30
    start_time = time.time()
    while not intercepted_params and time.time() - start_time < max_wait_time:
        if getattr(page.add_init_script, 'is_camoufox_workaround', None) is True:
            # use main world data for the add_init_script workaround (camoufox)
            script = 'mw:window.cfParams'
        else:
            script = 'window.cfParams'

        intercepted_params = await page.evaluate(script)
        await page.wait_for_timeout(1000)

    if not intercepted_params:
        raise CaptchaDataDetectionError("Failed to detect Cloudflare interstitial data within the timeout period")

    data = {
        'site_key': intercepted_params.get('sitekey'),
        'url': intercepted_params.get('pageurl'),
        'user_agent': intercepted_params.get('userAgent'),
        'action': intercepted_params.get('action'),
        'data': intercepted_params.get('data'),
        'page_data': intercepted_params.get('pagedata'),
    }

    logger.debug(f'Detected Cloudflare interstitial data: {data}')

    return data
