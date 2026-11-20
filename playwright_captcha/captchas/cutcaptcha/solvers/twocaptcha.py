import logging

from twocaptcha import AsyncTwoCaptcha

from playwright_captcha.utils.validators import validate_required_params

logger = logging.getLogger(__name__)


async def solve_cutcaptcha_twocaptcha(async_two_captcha_client: AsyncTwoCaptcha, **kwargs) -> dict:
    """
    Solve CutCaptcha using 2Captcha service

    :param async_two_captcha_client: Instance of AsyncTwoCaptcha client
    :param kwargs: Parameters for the 2Captcha API call, e.g. 'sitekey', 'url'

    :return: Result of the captcha solving
    """

    logger.debug('Solving CutCaptcha using 2Captcha...')

    validate_required_params(['sitekey', 'url'], kwargs)

    # the client's cutcaptcha() wrapper only supports the legacy misery_key/apikey widget,
    # the current widget is solved by its sitekey
    result = await async_two_captcha_client.solve(method='cutcaptcha', **kwargs)

    logger.debug(f'Solved CutCaptcha: {result}')

    return result
