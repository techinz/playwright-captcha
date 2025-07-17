import logging
from typing import Optional, Union

from playwright.async_api import ElementHandle, Frame, Page

logger = logging.getLogger(__name__)


async def detect_expected_content(
        page: Page,
        captcha_container: Union[Page, Frame, ElementHandle],
        expected_content_selector: Optional[str] = None
) -> bool:
    """
    Check if the expected content is present in the page

    :param page: Playwright Page
    :param captcha_container: Page, Frame, ElementHandle
    :param expected_content_selector: CSS selector for the expected content

    :return: True if expected content is found, False otherwise
    """

    logger.debug(f'Detecting expected content with selector: {expected_content_selector}')

    if not expected_content_selector:
        return False

    element_in_page = page.locator(expected_content_selector)
    element_in_captcha_container = captcha_container.locator(expected_content_selector)

    detected = bool(await element_in_page.count() > 0 or await element_in_captcha_container.count() > 0)

    logger.debug(f'Expected content detected: {detected}')

    return detected
