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


async def solve_cutcaptcha() -> None:
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
    #         addons=[os.path.abspath(ADDON_PATH)]
    #         # 2. (only for camoufox) add this to use `add_init_script` temporary workaround
    # ) as browser:
    #     context = await browser.new_context()
    #     page = await context.new_page()
    #
    #     framework = FrameworkType.CAMOUFOX
    #
    #     ...

    # usage with playwright (used in this example):
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        framework = FrameworkType.PLAYWRIGHT

        # create a solver instance before navigating to the page
        async with TwoCaptchaSolver(
                framework=framework,
                page=page,
                async_two_captcha_client=AsyncTwoCaptcha(TWO_CAPTCHA_API_KEY)) as solver:
            # the contact form on cutcaptcha.net has a live CutCaptcha widget
            await page.goto('https://cutcaptcha.net/#contact')

            # wait for the widget to appear
            await page.locator('.cutcaptcha').wait_for()
            await asyncio.sleep(5)

            # solve the captcha, the token is put into the widget's `cutcaptcha-response` input
            token = await solver.solve_captcha(
                captcha_container=page,
                captcha_type=CaptchaType.CUTCAPTCHA,
            )

        # the form is not submitted here, so we only check that the token is in place
        applied_token = await page.locator('.cutcaptcha input[name="cutcaptcha-response"]').input_value()
        if applied_token == token:
            logging.info(f'Captcha token applied: {token}')
        else:
            logging.error('Captcha token was not applied')
            return

    logging.info('Finished')


if __name__ == '__main__':
    asyncio.run(solve_cutcaptcha())
