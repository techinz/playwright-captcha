import asyncio
import logging

from playwright.async_api import async_playwright

from playwright_captcha import CaptchaType, ClickSolver, FrameworkType

logging.basicConfig(
    level='INFO',
    format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)


async def solve_turnstile() -> None:
    # Note: click-based solvers may not reliably solve captchas in Playwright, as it isn't stealthy enough
    # For better results, use a stealth browser like camoufox/patchright (https://github.com/daijro/camoufox) - example below

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
    #         config={'forceScopeAccess': True},  # add this when creating Camoufox instance
    #         disable_coop=True,  # add this when creating Camoufox instance
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
        browser = await playwright.chromium.launch(headless=False)
        page = await browser.new_page()

        framework = FrameworkType.PLAYWRIGHT

        # create a solver instance before navigating to the page
        async with ClickSolver(framework=framework, page=page) as solver:
            await page.goto('https://2captcha.com/demo/cloudflare-turnstile')

            # wait for the page to load completely (could be replaced with a more robust check in a real scenario)
            await asyncio.sleep(5)

            # search for the element that contains the turnstile challenge (shadow DOM)
            turnstile_container = page.locator('#cf-turnstile')
            await turnstile_container.wait_for()
            if await turnstile_container.count() == 0:
                logging.error('Turnstile container not found on the page')
                return

            # solve the captcha
            await solver.solve_captcha(captcha_container=page,
                                       captcha_type=CaptchaType.CLOUDFLARE_TURNSTILE)

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
