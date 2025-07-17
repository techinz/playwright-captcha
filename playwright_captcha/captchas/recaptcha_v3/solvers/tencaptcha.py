import logging

from playwright_captcha.solvers.api.tencaptcha.tencaptcha.async_solver import AsyncTenCaptcha
from playwright_captcha.utils.validators import validate_required_params

logger = logging.getLogger(__name__)


async def solve_recaptcha_v3_tencaptcha(async_ten_captcha_client: AsyncTenCaptcha, **kwargs) -> dict:
    """
    Solve Recaptcha V3 captcha using 10Captcha service.

    :param async_ten_captcha_client: Instance of AsyncTenCaptcha client
    :param kwargs: Parameters for the 10Captcha API call, e.g. 'sitekey'

    :return: Result of the captcha solving
    """

    logger.debug('Solving Recaptcha V3 captcha using 10Captcha...')

    validate_required_params(['sitekey', 'url'], kwargs)

    kwargs['version'] = 'v3'
    result = await async_ten_captcha_client.recaptcha(
        **kwargs
    )

    logger.debug(f'Solved Recaptcha V3: {result}')

    return result
