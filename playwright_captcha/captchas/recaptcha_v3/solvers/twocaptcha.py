import logging

from twocaptcha import AsyncTwoCaptcha

from playwright_captcha.utils.validators import validate_required_params

logger = logging.getLogger(__name__)


async def solve_recaptcha_v3_twocaptcha(async_two_captcha_client: AsyncTwoCaptcha, **kwargs) -> dict:
    """
    Solve Recaptcha V3 captcha using 2Captcha service.

    :param async_two_captcha_client: Instance of AsyncTwoCaptcha client
    :param kwargs: Parameters for the 2Captcha API call, e.g. 'sitekey'

    :return: Result of the captcha solving
    """

    logger.debug('Solving Recaptcha V3 captcha using 2Captcha...')

    validate_required_params(['sitekey', 'url'], kwargs)

    kwargs['version'] = 'v3'
    result = await async_two_captcha_client.recaptcha(
        **kwargs
    )

    logger.debug(f'Solved Recaptcha V3: {result}')

    return result
