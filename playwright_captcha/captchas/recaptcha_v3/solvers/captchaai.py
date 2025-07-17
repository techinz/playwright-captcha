import logging

from playwright_captcha.solvers.api.captchaai.captchaai.async_solver import AsyncCaptchaAI
from playwright_captcha.utils.validators import validate_required_params

logger = logging.getLogger(__name__)


async def solve_recaptcha_v3_captcha_ai(async_captcha_ai_client: AsyncCaptchaAI, **kwargs) -> dict:
    """
    Solve Recaptcha V3 captcha using CaptchaAI service.

    :param async_captcha_ai_client: Instance of AsyncCaptchaAI client
    :param kwargs: Parameters for the CaptchaAI API call, e.g. 'sitekey'

    :return: Result of the captcha solving
    """

    logger.debug('Solving Recaptcha V3 captcha using CaptchaAI...')

    validate_required_params(['sitekey', 'url'], kwargs)

    kwargs['version'] = 'v3'
    result = await async_captcha_ai_client.recaptcha(
        **kwargs
    )

    logger.debug(f'Solved Recaptcha V3: {result}')

    return result
