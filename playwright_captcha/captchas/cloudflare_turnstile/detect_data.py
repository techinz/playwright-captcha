import logging
from typing import Union

from playwright.async_api import Page, Frame, ElementHandle

from playwright_captcha.utils.dom_helpers import search_element_by_css_selector

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

    logger.debug(f'Detected Cloudflare Turnstile data: {data}')

    return data
