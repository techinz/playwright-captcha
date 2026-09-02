import asyncio
import logging
import os

from dotenv import load_dotenv
from playwright.async_api import async_playwright

from playwright_captcha import CaptchaType, PeakSolver, FrameworkType
from playwright_captcha.solvers.api.peak.peak_client import AsyncPeakClient

logging.basicConfig(
    level='INFO',
    format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

load_dotenv()

PEAK_API_KEY = os.getenv('PEAK_API_KEY')  # your Peak API key (get one free at https://peak.fo)
PEAK_PROXY = os.getenv('PEAK_PROXY')  # proxy the solve runs through, e.g. 'http://user:pass@host:port'


async def solve_turnstile() -> None:
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        framework = FrameworkType.PLAYWRIGHT

        # create a solver instance before navigating to the page
        async with PeakSolver(
                framework=framework,
                page=page,
                async_peak_client=AsyncPeakClient(PEAK_API_KEY)) as solver:
            await page.goto('https://2captcha.com/demo/cloudflare-turnstile')

            # wait for the page to load completely (could be replaced with a more robust check in a real scenario)
            await asyncio.sleep(5)

            # search for the element that contains the turnstile challenge
            turnstile_container = page.locator('#cf-turnstile')
            await turnstile_container.wait_for()
            if await turnstile_container.count() == 0:
                logging.error('Turnstile container not found on the page')
                return

            # solve the captcha (Peak runs the solve through the proxy you pass)
            await solver.solve_captcha(
                captcha_container=turnstile_container,
                captcha_type=CaptchaType.CLOUDFLARE_TURNSTILE,
                proxy=PEAK_PROXY,
            )

        # submit the form after solving the captcha
        submit_button = page.locator('//button[@data-action="demo_action"]')
        await submit_button.wait_for()
        await submit_button.click()

        await asyncio.sleep(5)  # wait for the result to be processed

        # check if the captcha was solved successfully
        try:
            await page.locator('//p[text()="Captcha is passed successfully!"]').wait_for(timeout=10000)
            logging.info('Captcha is passed successfully!')
        except Exception as e:
            logging.error(f'Captcha solving failed: {e}')
            return

    logging.info('Finished')


if __name__ == '__main__':
    asyncio.run(solve_turnstile())
