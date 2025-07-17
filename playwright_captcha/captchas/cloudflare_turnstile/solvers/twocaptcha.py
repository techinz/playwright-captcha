import logging

from twocaptcha import AsyncTwoCaptcha

from playwright_captcha.utils.validators import validate_required_params

logger = logging.getLogger(__name__)


async def solve_cloudflare_turnstile_twocaptcha(async_two_captcha_client: AsyncTwoCaptcha, **kwargs) -> dict:
    """
    Solve Cloudflare Turnstile captcha using 2Captcha service

    :param async_two_captcha_client: Instance of AsyncTwoCaptcha client
    :param kwargs: Parameters for the 2Captcha API call, e.g. 'sitekey'

    :return: Result of the captcha solving
    """

    logger.debug('Solving Cloudflare Turnstile captcha using 2Captcha...')

    validate_required_params(['sitekey', 'url'], kwargs)

    result = await async_two_captcha_client.turnstile(
        **kwargs
    )

    logger.debug(f'Solved Cloudflare Turnstile captcha: {result}')

    return result
