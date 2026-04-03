import logging
from asyncio import create_task, wait, gather, FIRST_COMPLETED, Task, CancelledError
from typing import Union, List, Optional

from playwright.async_api import ElementHandle, Page, Frame, TimeoutError as PlaywrightTimeoutError

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

    js_script = """
    () => {
        const roots = [];

        function collectShadowRoots(node) {
            if (!node) return;

            const shadow = node.shadowRoot;
            if (shadow) {
                roots.push(shadow);
                collectShadowRoots(shadow);
            }

            for (const el of node.querySelectorAll("*")) {
                if (el.shadowRoot) {
                    collectShadowRoots(el);
                }
            }
        }

        collectShadowRoots(document);
        return roots;
    }
    """

    if framework == FrameworkType.PATCHRIGHT:
        handle = await queryable.evaluate_handle(js_script, isolated_context=False)
    else:
        handle = await queryable.evaluate_handle(js_script)

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
        selector: str,
        timeout: float = 10
) -> List[ElementHandle]:
    """
    Search for elements by selector within the shadow DOM of the queryable object

    :param framework: Framework type (e.g. PATCHRIGHT, CAMOUFOX, PLAYWRIGHT)
    :param queryable: Page, Frame, ElementHandle
    :param selector: CSS selector to search for elements
    :param timeout: Timeout value in seconds to wait for selector to appear (Default: 10)

    :return: List of ElementHandles that match the selector
    """

    logger.debug(f'Searching for elements by selector "{selector}" in {queryable}')

    elements = []
    tasks: set[Task] = set()
    try:
        shadow_roots = await get_shadow_roots(framework, queryable)  # get all shadow roots in the queryable object
        for shadow_root in shadow_roots:
            # find all elements by selector within the shadow root
            tasks.add(
                create_task(shadow_root.wait_for_selector(selector, timeout=timeout * 1000))
            )

        while tasks:
            completed_tasks, tasks = await wait(tasks, return_when=FIRST_COMPLETED)
            for task in completed_tasks:
                try:
                    if element_handle := task.result():
                        if element := element_handle.as_element():
                            elements.append(element)
                            break
                except PlaywrightTimeoutError:
                    logger.debug("Searching shadow root for selector (%s) timed out", selector)
                except CancelledError:
                    continue
            else:
                continue
            break

    except Exception as e:
        logger.error(f'Error searching for elements: {e}')

    finally:
        if tasks:
            for task in tasks:
                task.cancel()
            await gather(*tasks, return_exceptions=True)

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