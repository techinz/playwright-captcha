import logging
from typing import Union

from playwright.async_api import Page, Frame, ElementHandle

from playwright_captcha.utils.dom_helpers import search_element_by_css_selector
from playwright_captcha.utils.regex_helpers import search_content_by_regex

logger = logging.getLogger(__name__)


async def detect_recaptcha_v2_data(queryable: Union[Page, Frame, ElementHandle], **kwargs) -> dict:
    """
    Detect the data (e.g. site key) and other possible params of the captcha

    :param queryable: The Playwright Page, Frame, or ElementHandle to search for the captcha data
    :param kwargs: Additional parameters

    :return: A dictionary containing the detected captcha data needed for solving
    """

    logger.debug('Detecting reCAPTCHA v2 data...')

    data = {}

    # find sitekey by css selector
    results = await search_element_by_css_selector(queryable, '[data-sitekey]',
                                                   ['data-sitekey', 'data-size', 'data-callback', 'invisible',
                                                    'enterprise', 'data-s'])
    sitekey, size, callback, invisible, enterprise, data_s = results

    data.update({'size': size} if size else {})
    data.update({
                    '_apply_captcha_callback_function': callback} if callback else {})  # used not to solve, but to apply the captcha
    data.update({'invisible': invisible} if invisible else {})
    data.update({'enterprise': enterprise} if enterprise else {})
    data.update({'data_s': data_s} if data_s else {})

    if not sitekey:
        # find sitekey by regex
        sitekey_match = await search_content_by_regex(queryable, r'data-sitekey=["\']([^"\']+)["\']')
        sitekey = sitekey_match.group(1) if sitekey_match else None

    data.update({'site_key': sitekey} if sitekey else {})

    logger.debug(f'Detected reCAPTCHA v2 data: {data}')

    return data
