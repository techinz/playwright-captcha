import asyncio
import logging
from typing import Optional, List, Tuple

from playwright.async_api import Frame, ElementHandle

from playwright_captcha.solvers.click.common.shadow_root import search_shadow_root_elements
from playwright_captcha.types import FrameworkType

logger = logging.getLogger(__name__)


async def get_ready_checkbox(
        framework: FrameworkType,
        iframes: List[Frame],
        delay: int,
        attempts: int
) -> Optional[Tuple[Frame, ElementHandle]]:
    """
    Accepts a list of Cloudflare iframes, sorts out detached ones, collects checkboxes from the remaining iframes,
    and waits until at least one checkbox is found and ready to be clicked (visible)

    :param framework: Framework type (e.g. PLAYWRIGHT, PATCHRIGHT, CAMOUFOX)
    :param iframes: Cloudflare iframes
    :param delay: Delay in seconds between attempts to find the checkbox
    :param attempts: Maximum number of attempts to find the checkbox

    :return: Tuple (checkboxes Frame, checkboxes ElementHandle) if checkbox is found and ready, None otherwise
    """

    logger.debug(f'Waiting for Cloudflare checkbox input in {len(iframes)} iframes '
                 f'with {attempts} attempts and {delay} seconds delay')

    # ensure at least one attempt
    if attempts <= 0:
        attempts = 1

    for attempt in range(attempts):
        try:
            checkboxes = []

            # search for checkboxes in each iframe
            for iframe in iframes:
                try:
                    if iframe.is_detached():  # skip detached iframes
                        continue

                    iframe_checkboxes = await search_shadow_root_elements(framework, iframe, 'input[type="checkbox"]')

                    # add found checkboxes to the list with their parent iframe
                    checkboxes += [(iframe, iframe_checkbox) for iframe_checkbox in iframe_checkboxes]
                except Exception as e:
                    logger.error(f'Error searching for checkboxes in iframe: {e}')

            logger.info(f'Found {len(checkboxes)} checkboxes in {len(iframes)} Cloudflare iframes')

            # filter checkboxes that are visible and ready to be clicked
            visible_checkboxes = []
            for iframe, checkbox in checkboxes:
                if await checkbox.is_visible():
                    visible_checkboxes.append((iframe, checkbox))

            if visible_checkboxes:
                logger.info('Checkbox input is ready to be clicked')
                return visible_checkboxes[0]  # return the first visible checkbox

            logger.info('Waiting for Cloudflare checkbox input...')
            await asyncio.sleep(delay)
        except Exception as e:
            logger.error(f'Error while waiting for checkbox: {e}')

    logger.error('Max attempts reached while waiting for Cloudflare checkbox input')
    return None
