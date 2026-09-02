import logging

from playwright_captcha.solvers.api.peak.peak_client import AsyncPeakClient
from playwright_captcha.utils.validators import validate_required_params

logger = logging.getLogger(__name__)


async def solve_cloudflare_turnstile_peak(async_peak_client: AsyncPeakClient, **kwargs) -> dict:
    """
    Solve Cloudflare Turnstile captcha using the Peak service

    :param async_peak_client: Instance of AsyncPeakClient
    :param kwargs: Parameters for the solve request, e.g. 'sitekey', 'url', 'proxy'

    :return: Dict with the token under 'code' (same shape as the other solvers)
    """

    logger.debug('Solving Cloudflare Turnstile captcha using Peak...')

    validate_required_params(['sitekey', 'url'], kwargs)

    token = await async_peak_client.solve(
        task_type='turnstiletask',
        url=kwargs['url'],
        sitekey=kwargs['sitekey'],
        proxy=kwargs.get('proxy'),
        cdata=kwargs.get('cdata'),
        action=kwargs.get('action'),
        pagedata=kwargs.get('pagedata'),
    )

    logger.debug('Solved Cloudflare Turnstile captcha')

    return {'code': token}
