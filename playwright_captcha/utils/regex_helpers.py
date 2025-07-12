import logging
import re
from typing import Optional, Union

from playwright.async_api import Page, ElementHandle, Frame

logger = logging.getLogger(__name__)


async def search_content_by_regex(queryable: Union[Page, Frame, ElementHandle], pattern: str) -> Optional[re.Match]:
    """ Helper to search for a pattern in the page content and return the first match """

    page = queryable
    if not getattr(page, 'content', None):
        logger.debug("Can't search content by regex: no content method found on the queryable object")
        return None

    content = await page.content()

    match = re.search(pattern, content)
    if match:
        return match
    return None
