import logging

from twocaptcha import AsyncTwoCaptcha

from playwright_captcha.utils.validators import validate_required_params

logger = logging.getLogger(__name__)


async def solve_cloudflare_interstitial_twocaptcha(async_two_captcha_client: AsyncTwoCaptcha, **kwargs) -> dict:
    """
    Solve Cloudflare Interstitial captcha using 2Captcha service

    :param async_two_captcha_client: Instance of AsyncTwoCaptcha client
    :param kwargs: Parameters for the 2Captcha API call, e.g. 'sitekey'

    :return: Result of the captcha solving
    """

    logger.debug('Solving Cloudflare Interstitial captcha using 2Captcha...')

    validate_required_params(['sitekey', 'url', 'action', 'data', 'pagedata'], kwargs)

    result = await async_two_captcha_client.turnstile(
        **kwargs
    )

    logger.debug(f'Solved Cloudflare Interstitial captcha: {result}')

    return result
