import logging
from typing import Union

from playwright.async_api import Page, Frame, ElementHandle

from playwright_captcha.utils.dom_helpers import search_element_by_css_selector

logger = logging.getLogger(__name__)


async def detect_cutcaptcha_data(queryable: Union[Page, Frame, ElementHandle], **kwargs) -> dict:
    """
    Detect the data (e.g. site key) of the CutCaptcha widget

    :param queryable: The Playwright Page, Frame, or ElementHandle to search for the captcha data
    :param kwargs: Additional parameters

    :return: A dictionary containing the detected captcha data needed for solving
    """

    logger.debug('Detecting CutCaptcha data...')

    data = {}

    [sitekey] = await search_element_by_css_selector(queryable, '.cutcaptcha[data-sitekey]', ['data-sitekey'])

    data.update({'site_key': sitekey} if sitekey else {})

    logger.debug(f'Detected CutCaptcha data: {data}')

    return data
