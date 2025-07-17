import logging
from typing import Union
from urllib.parse import urlparse, parse_qs

from playwright.async_api import Page, Frame, ElementHandle

from playwright_captcha.utils.dom_helpers import search_element_by_css_selector
from playwright_captcha.utils.regex_helpers import search_content_by_regex

logger = logging.getLogger(__name__)


async def detect_recaptcha_v3_data(queryable: Union[Page, Frame, ElementHandle], **kwargs) -> dict:
    """
    Detect the data (e.g. site key) and other possible params of the captcha

    :param queryable: The Playwright Page, Frame, or ElementHandle to search for the captcha data
    :param kwargs: Additional parameters

    :return: A dictionary containing the detected captcha data needed for solving
    """

    logger.debug('Detecting reCAPTCHA v3 data...')

    data = {}

    # find iframe by css selector
    results = await search_element_by_css_selector(queryable, 'iframe[title="reCAPTCHA"]', ['src'])
    iframe_src = results[0] if results else None
    iframe_src_parsed = urlparse(iframe_src)
    iframe_src_params = parse_qs(iframe_src_parsed.query)

    sitekey = iframe_src_params.get('k', [None])[0]  # get sitekey from params

    for param in ['size', 'callback', 'invisible', 'enterprise', 'action']:
        if param in iframe_src_params:
            data[param] = iframe_src_params[param][0]

    if not sitekey:
        # find sitekey by regex
        sitekey_match = await search_content_by_regex(queryable, r'\/recaptcha\/api\.js\?render=(.*)\" ')
        sitekey = sitekey_match.group(1) if sitekey_match else None

    data.update({'site_key': sitekey} if sitekey else {})

    logger.debug(f'Detected reCAPTCHA v3 data: {data}')

    return data
