import asyncio
import logging
from typing import Optional, Union, Literal

from playwright.async_api import Page, ElementHandle, Frame, TimeoutError as PlaywrightTimeoutError

from playwright_captcha.solvers.click.cloudflare.utils.detection import detect_cloudflare_challenge
from playwright_captcha.solvers.click.cloudflare.utils.dom_helpers import get_ready_checkbox
from playwright_captcha.solvers.click.common.detection import detect_expected_content
from playwright_captcha.solvers.click.common.shadow_root import search_shadow_root_iframes, search_shadow_root_elements
from playwright_captcha.types import FrameworkType
from playwright_captcha.utils.exceptions import CaptchaSolvingError, CaptchaDetectionError

logger = logging.getLogger(__name__)


async def solve_cloudflare_by_click(
        framework: FrameworkType,
        page: Page,
        captcha_container: Union[Page, Frame, ElementHandle],
        challenge_type: Literal["interstitial", "turnstile"] = "interstitial",
        expected_content_selector: Optional[str] = None,
        solve_click_delay: int = 6,
        wait_checkbox_attempts: int = 10,
        wait_checkbox_delay: int = 6,
        checkbox_click_attempts: int = 3,
) -> None:
    """
    Solve Cloudflare challenge by searching for & clicking the checkbox input

    :param framework: Framework type (e.g. PLAYWRIGHT, PATCHRIGHT, CAMOUFOX)
    :param page: Playwright Page
    :param captcha_container: Page, Frame, ElementHandle
    :param challenge_type: Type of Cloudflare challenge: "interstitial" or "turnstile"
    :param expected_content_selector: Optional CSS selector to verify page content is accessible after solving
    :param solve_click_delay: Delay after clicking the checkbox to allow Cloudflare to process the click
    :param wait_checkbox_attempts: Maximum number of attempts to find the checkbox and wait for it to be ready
    :param wait_checkbox_delay: Delay between wait_checkbox_attempts in seconds to find the checkbox and wait for it to be ready
    :param checkbox_click_attempts: Maximum number of attempts to click the checkbox

    :return: None if solved, Exception otherwise

    :raises CaptchaDetectionError: If Cloudflare iframes are not found
    :raises CaptchaSolvingError: If checkbox is not found or not ready, or if challenge is not solved after clicking
    """

    logger.info(f'Starting Cloudflare {challenge_type} challenge solving by click...')

    # 1. Check if a Cloudflare challenge is present
    cloudflare_detected = await detect_cloudflare_challenge(captcha_container, challenge_type)
    expected_content_detected = await detect_expected_content(page, captcha_container, expected_content_selector)
    if not cloudflare_detected or expected_content_detected:
        logger.info('No Cloudflare challenge detected')
        return

    # 2. Find Cloudflare iframes
    cf_iframes = await search_shadow_root_iframes(
        framework=framework,
        captcha_container=captcha_container,
        src_filter='https://challenges.cloudflare.com/cdn-cgi/challenge-platform/'
    )
    if not cf_iframes:
        raise CaptchaDetectionError(f'Cloudflare iframes not found')

    # 3. In all found iframes, search for the valid checkbox input and wait until it's ready to be clicked
    checkbox_data = await get_ready_checkbox(
        framework=framework,
        iframes=cf_iframes,
        delay=wait_checkbox_delay,
        attempts=wait_checkbox_attempts)
    if not checkbox_data:
        raise CaptchaDetectionError(f'Cloudflare checkbox not found or not ready')
    iframe, checkbox = checkbox_data

    logger.info('Found checkbox in Cloudflare iframe')

    # 4. Click the checkbox and validate success
    if challenge_type == "interstitial":
        try:
            async with page.expect_event("load", timeout=solve_click_delay * 1000) as reload_event:
                await click_checkbox(checkbox, checkbox_click_attempts)

            cloudflare_detected = await detect_cloudflare_challenge(captcha_container)
            challenge_solved = not cloudflare_detected
        except PlaywrightTimeoutError as e:
            logger.error("Page did not load within the alloted time after clicking the button")
            challenge_solved = False

    elif challenge_type == "turnstile":
        # Turnstile Success - Check that the `success` element is visible and showing
        await click_checkbox(checkbox, checkbox_click_attempts)
        success_elements = await search_shadow_root_elements(framework, iframe, 'div[id="success"]')
        if success_element := next(iter(success_elements), None):
            try:
                await success_element.wait_for_element_state("visible", timeout=solve_click_delay * 1000)
                challenge_solved = True
            except PlaywrightTimeoutError as e:
                challenge_solved = False
        else:
            raise CaptchaDetectionError("Cloudflare turnstile success element does not exist on the page.")
    else:
        raise CaptchaDetectionError("Unsupported Cloudflare Captcha Type: %s", challenge_type)

    # 6 Validate Success
    expected_content_detected = await detect_expected_content(page, captcha_container, expected_content_selector)
    if challenge_solved or expected_content_detected:
        logger.info('Solved successfully')
        return

    raise CaptchaSolvingError(
        'Failed to solve Cloudflare challenge by click: challenge still present or expected content not detected')


async def click_checkbox(checkbox: ElementHandle, checkbox_click_attempts: int):
    for checkbox_click_attempt in range(checkbox_click_attempts):
        try:
            await checkbox.click()
            logger.info('Checkbox clicked successfully')

            break
        except Exception as e:
            logger.error(
                f'Error clicking checkbox ({checkbox_click_attempt + 1}/{checkbox_click_attempts} attempt): {e}')
    else:
        raise CaptchaSolvingError(f'Failed to click checkbox after maximum attempts')