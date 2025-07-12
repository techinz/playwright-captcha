import asyncio
import logging
import os

from dotenv import load_dotenv
from playwright.async_api import async_playwright
from twocaptcha import AsyncTwoCaptcha

from playwright_captcha import CaptchaType, TwoCaptchaSolver, FrameworkType

logging.basicConfig(
    level='INFO',
    format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

load_dotenv()

TWO_CAPTCHA_API_KEY = os.getenv('TWO_CAPTCHA_API_KEY')  # replace with your 2Captcha API key


async def solve_interstitial() -> None:
    # usage with patchright:
    # from patchright.async_api import async_playwright
    # async with async_playwright() as playwright:
    #     browser = await playwright.chromium.launch(
    #         channel="chrome",
    #         headless=True,
    #     )
    #     context = await browser.new_context()
    #     page = await context.new_page()
    #
    #     framework = FrameworkType.PATCHRIGHT
    #
    #     ...

    # usage with camoufox:
    # ! At the moment, there is a problem with `add_init_script` method in camoufox
    # ! which is needed for the captcha solving, so we use my temporary workaround:
    # ! https://github.com/techinz/camoufox-add_init_script
    # ! It is already pre-installed and automatically used in the playwright-captcha package.
    # ! You just need to add the addon when creating Camoufox instance
    # from camoufox import AsyncCamoufox
    # from playwright_captcha.utils.camoufox_add_init_script.add_init_script import get_addon_path
    # import os
    #
    # ADDON_PATH = get_addon_path()  # path to the addon script
    #
    # async with AsyncCamoufox(
    #         headless=True,
    #         geoip=True,
    #         humanize=True,
    #
    #         i_know_what_im_doing=True,
    #
    #         main_world_eval=True,  # 1. (only for camoufox) add this to use `add_init_script` temporary workaround
    #         addons=[os.path.abspath(ADDON_PATH)] # 2. (only for camoufox) add this to use `add_init_script` temporary workaround
    # ) as browser:
    #     context = await browser.new_context()
    #     page = await context.new_page()
    #
    #     framework = FrameworkType.CAMOUFOX
    #
    #     ...

    # usage with playwright (used in this example):
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        framework = FrameworkType.PLAYWRIGHT

        # create a solver instance before navigating to the page
        async with TwoCaptchaSolver(
                framework=framework,
                page=page,
                async_two_captcha_client=AsyncTwoCaptcha(TWO_CAPTCHA_API_KEY)) as solver:
            await page.goto('https://2captcha.com/demo/cloudflare-turnstile-challenge', wait_until='domcontentloaded')

            # wait for the page to load completely (could be replaced with a more robust check in a real scenario)
            await asyncio.sleep(15)

            # solve the captcha
            await solver.solve_captcha(
                captcha_container=page,
                captcha_type=CaptchaType.CLOUDFLARE_INTERSTITIAL,
            )

        await asyncio.sleep(5)  # wait for the result to be processed

        # check if the captcha was solved successfully
        try:
            await page.locator('//p[text()="Captcha is passed successfully!"]').wait_for(timeout=10000)
            logging.info('Captcha is passed successfully!')
        except Exception as e:
            await context.close()

            logging.error(f'Captcha solving failed: {e}')
            return

    logging.info('Finished')


if __name__ == '__main__':
    asyncio.run(solve_interstitial())
