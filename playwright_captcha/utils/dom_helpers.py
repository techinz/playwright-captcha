from typing import Union, List

from playwright.async_api import Page, ElementHandle, Frame


async def search_element_by_css_selector(queryable: Union[Page, Frame, ElementHandle], selector: str,
                                         attributes: List[str]) -> List[str]:
    """
    Helper to search for an element by CSS selector and return its data-sitekey attribute

    :param queryable: Playwright Page, Frame, or ElementHandle to search in
    :param selector: CSS selector to find the element
    :param attributes: List of attributes to retrieve from the found element

    :return: List of attribute values from the found element, or None for each attribute if not found
    """

    results = []

    element = queryable.locator(selector)
    if await element.count() > 0:
        for attribute in attributes:
            result = await element.get_attribute(attribute)
            results.append(result)  # even if None, to keep the order
    else:
        results = [None] * len(attributes)  # if no element found, return None for each attribute to keep the order
    return results
