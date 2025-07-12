from typing import Union, List

from playwright.async_api import Page, ElementHandle, Frame


async def search_element_by_css_selector(queryable: Union[Page, Frame, ElementHandle], selector: str,
                                         attributes: List[str]) -> List[str]:
    """ Helper to search for an element by CSS selector and return its data-sitekey attribute """

    results = []

    element = queryable.locator(selector)
    if await element.count() > 0:
        for attribute in attributes:
            result = await element.get_attribute(attribute)
            results.append(result)  # even if None, to keep the order
    else:
        results = [None] * len(attributes)  # if no element found, return None for each attribute to keep the order
    return results
