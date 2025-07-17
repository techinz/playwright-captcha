import logging
from typing import Union, List, Optional

from playwright.async_api import ElementHandle, Page, Frame

from playwright_captcha.types import FrameworkType

logger = logging.getLogger(__name__)


async def get_shadow_roots(
        framework: FrameworkType,
        queryable: Union[Page, Frame, ElementHandle],
) -> List[ElementHandle]:
    """
    Get all shadow roots on the page

    :param framework: Framework type (e.g. PLAYWRIGHT, PATCHRIGHT, CAMOUFOX)
    :param queryable: Page, Frame, ElementHandle

    :return: List of shadow roots ElementHandles
    """

    logger.debug(f'Collecting shadow roots from {queryable}')

    # script to collect all shadow roots
    js_script = """
    () => {
        const roots = [];

        function collectShadowRoots(node) {
            if (!node) return;

            if (node.shadowRootUnl) {
                roots.push(node.shadowRootUnl);
                node = node.shadowRootUnl;
            }

            for (const el of node.querySelectorAll("*")) {
                if (el.shadowRootUnl) {
                    collectShadowRoots(el);
                }
            }
        }

        collectShadowRoots(document);
        console.log(roots);
        return roots;
    }
    """

    if framework == FrameworkType.PATCHRIGHT:
        handle = await queryable.evaluate_handle(js_script, isolated_context=False)
    else:
        handle = await queryable.evaluate_handle(js_script)

    # convert JSHandle array to python list of ElementHandle
    properties = await handle.get_properties()

    shadow_roots = []
    for prop_handle in properties.values():
        element = prop_handle.as_element()
        if element:
            shadow_roots.append(element)

    logger.debug(f'Found {len(shadow_roots)} shadow roots')

    return shadow_roots


async def search_shadow_root_elements(
        framework: FrameworkType,
        queryable: Union[Page, Frame, ElementHandle],
        selector: str
) -> List[ElementHandle]:
    """
    Search for elements by selector within the shadow DOM of the queryable object

    :param framework: Framework type (e.g. PATCHRIGHT, CAMOUFOX, PLAYWRIGHT)
    :param queryable: Page, Frame, ElementHandle
    :param selector: CSS selector to search for elements

    :return: List of ElementHandles that match the selector
    """

    logger.debug(f'Searching for elements by selector "{selector}" in {queryable}')

    elements = []

    try:
        shadow_roots = await get_shadow_roots(framework, queryable)  # get all shadow roots in the queryable object
        for shadow_root in shadow_roots:
            # find all elements by selector within the shadow root
            js_script = f"shadow => shadow.querySelector('{selector}')"

            element_handle = await shadow_root.evaluate_handle(js_script)
            if not element_handle:
                continue

            element = element_handle.as_element()
            if element:
                elements.append(element)
    except Exception as e:
        logger.error(f'Error searching for elements: {e}')

    logger.debug(f'Found {len(elements)} elements matching selector "{selector}"')

    return elements


async def search_shadow_root_iframes(
        framework: FrameworkType,
        captcha_container: Union[Page, Frame, ElementHandle],
        src_filter: str
) -> Optional[List[Frame]]:
    """
    Search for an iframe within the shadow DOM, src of which includes the src_filter

    :param framework: Framework type (e.g. PATCHRIGHT, CAMOUFOX, PLAYWRIGHT)
    :param captcha_container: Page, Frame, ElementHandle
    :param src_filter: String to filter the iframe's src attribute

    :return: list of matched iframes or empty list if no iframes found
    """

    logger.debug(f'Searching for iframes with src containing "{src_filter}" in {captcha_container}')

    matched_iframes = []

    try:
        iframe_elements = await search_shadow_root_elements(framework, captcha_container, 'iframe')
        for iframe_element in iframe_elements:
            src_prop = await iframe_element.get_property('src')
            src = await src_prop.json_value()

            if src_filter in src:
                cf_iframe = await iframe_element.content_frame()
                if cf_iframe and cf_iframe.is_detached():  # skip detached iframes
                    continue

                matched_iframes.append(cf_iframe)
    except Exception as e:
        logger.error(f'Error searching for iframes: {e}')

    logger.debug(f'Found {len(matched_iframes)} iframes with src containing "{src_filter}"')

    return matched_iframes
