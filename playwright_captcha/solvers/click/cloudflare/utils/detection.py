import logging
from typing import Literal, Union

from playwright.async_api import ElementHandle, Frame, Page

logger = logging.getLogger(__name__)

# selectors for detecting Cloudflare interstitial challenge (page)
CF_INTERSTITIAL_INDICATORS_SELECTORS = [
    'script[src*="/cdn-cgi/challenge-platform/"]',
]

# selectors for detecting Cloudflare turnstile challenge (small embedded captcha)
CF_TURNSTILE_INDICATORS_SELECTORS = [
    'input[name="cf-turnstile-response"]',
    'script[src*="challenges.cloudflare.com/turnstile/v0"]',
]


async def detect_cloudflare_challenge(
        captcha_container: Union[Page, Frame, ElementHandle],
        challenge_type: Literal['turnstile', 'interstitial'] = 'turnstile'
) -> bool:
    """
    Detect if a Cloudflare challenge is present in the provided captcha container by checking for specific predefined selectors

    :param captcha_container: Page, Frame, ElementHandle
    :param challenge_type: Type of challenge to detect ('turnstile' or 'interstitial')

    :return: True if Cloudflare challenge is detected, False otherwise
    """

    logger.debug('Detecting Cloudflare challenge...')

    if challenge_type not in ('turnstile', 'interstitial'):
        raise ValueError("Invalid challenge_type: it must be either 'turnstile' or 'interstitial'")

    selectors = CF_TURNSTILE_INDICATORS_SELECTORS if challenge_type == 'turnstile' else CF_INTERSTITIAL_INDICATORS_SELECTORS
    for selector in selectors:
        try:
            element = captcha_container.locator(selector)
            if await element.count() == 0:
                continue
        except Exception as e:
            if 'Execution context was destroyed, most likely because of a navigation' in str(e):
                logger.warning(
                    'Execution context was destroyed while detecting Cloudflare challenge - counting as not detected')
                return False

        logger.debug(f'Cloudflare {challenge_type} challenge detected using selector: {selector}')
        return True

    logger.debug('Cloudflare challenge not detected')
    return False
