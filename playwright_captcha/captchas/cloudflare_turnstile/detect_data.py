import logging
from typing import Union

from playwright.async_api import Page, Frame, ElementHandle

from playwright_captcha.utils.dom_helpers import search_element_by_css_selector

try:
    from patchright.async_api import Page as PatchrightPage
except ImportError:
    PatchrightPage = None

logger = logging.getLogger(__name__)


async def detect_turnstile_data(queryable: Union[Page, Frame, ElementHandle], **kwargs) -> dict:
    """
    Detect the data (e.g. site key) and other possible params of the captcha

    :param queryable: The Playwright Page, Frame, or ElementHandle to search for the captcha data
    :param kwargs: Additional parameters

    :return: A dictionary containing the detected captcha data needed for solving
    """

    logger.debug('Detecting Cloudflare Turnstile data...')

    data = {}

    # find sitekey by css selector
    results = await search_element_by_css_selector(queryable, '[data-sitekey]', ['data-sitekey', 'action'])
    sitekey, action = results

    data.update({'site_key': sitekey} if sitekey else {})
    data.update({'action': action} if action else {})

    # widgets created with turnstile.render() have no data-sitekey,
    # their params are intercepted by the patch API solvers inject into the page
    if not sitekey and isinstance(queryable, (Page, PatchrightPage) if PatchrightPage else Page):
        if getattr(queryable.add_init_script, 'is_camoufox_workaround', None) is True:
            script = 'mw:window.cfParams'  # main world data (camoufox)
        else:
            script = 'window.cfParams'

        intercepted_params = await queryable.evaluate(script) or {}
        data.update({key: value for key, value in {
            'site_key': intercepted_params.get('sitekey'),
            'action': intercepted_params.get('action'),
            'data': intercepted_params.get('data'),
            'page_data': intercepted_params.get('pagedata'),
            'user_agent': intercepted_params.get('userAgent'),
        }.items() if value})

    logger.debug(f'Detected Cloudflare Turnstile data: {data}')

    return data
