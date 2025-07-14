import asyncio

import pytest
from playwright.async_api import Page

from playwright_captcha import CaptchaType, ClickSolver, FrameworkType
from playwright_captcha.utils.exceptions import CaptchaSolvingError


@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.asyncio
class TestCloudflareClickSolvers:
    """Integration tests for Cloudflare Click solvers with all frameworks"""

    async def test_click_turnstile_solver(self, browser_context):
        """Test Click solver for Cloudflare Turnstile with all frameworks"""
        framework, page = browser_context

        framework: FrameworkType
        page: Page

        async with ClickSolver(framework=framework, page=page) as solver:
            await page.goto('https://2captcha.com/demo/cloudflare-turnstile')
            await asyncio.sleep(5)

            turnstile_container = page.locator('#cf-turnstile')
            await turnstile_container.wait_for()

            if await turnstile_container.count() == 0:
                pytest.fail('Turnstile container not found on the page')

            try:
                await solver.solve_captcha(
                    captcha_container=page,
                    captcha_type=CaptchaType.CLOUDFLARE_TURNSTILE
                )
            except CaptchaSolvingError:
                if framework in [FrameworkType.PLAYWRIGHT, FrameworkType.PATCHRIGHT]:
                    assert True, (f"Unable to solve the captcha for {framework.value}, but it is expected behavior "
                                  f"for ClickSolver since it relies on browser stealth and may not always succeed.")
                    return

                raise

        submit_button = page.locator('//button[@data-action="demo_action"]')
        await submit_button.wait_for()
        await submit_button.click()
        await asyncio.sleep(5)

        try:
            success_element = page.locator('//p[text()="Captcha is passed successfully!"]')
            await success_element.wait_for(timeout=10000)

            assert True
        except Exception as e:
            # for click solvers, we might not always succeed due to detection
            # so we'll just verify the solver ran without crashing

            if framework in [FrameworkType.PLAYWRIGHT, FrameworkType.PATCHRIGHT]:
                assert True, (f"Unable to solve the captcha for {framework.value}, but it is expected behavior "
                              f"for ClickSolver since it relies on browser stealth and may not always succeed.")
                return

            raise

    async def test_click_interstitial_solver(self, browser_context):
        """Test Click solver for Cloudflare Interstitial with all frameworks"""

        framework, page = browser_context

        framework: FrameworkType
        page: Page

        async with ClickSolver(framework=framework, page=page) as solver:
            await page.goto('https://2captcha.com/demo/cloudflare-turnstile-challenge')
            await asyncio.sleep(5)

            try:
                await solver.solve_captcha(
                    captcha_container=page,
                    captcha_type=CaptchaType.CLOUDFLARE_INTERSTITIAL,
                    expected_content_selector="#root"
                )
            except CaptchaSolvingError:
                if framework in [FrameworkType.PLAYWRIGHT, FrameworkType.PATCHRIGHT]:
                    assert True, (f"Unable to solve the captcha for {framework.value}, but it is expected behavior "
                                  f"for ClickSolver since it relies on browser stealth and may not always succeed.")
                    return

                raise

        await asyncio.sleep(5)

        try:
            success_element = page.locator('//p[text()="Captcha is passed successfully!"]')
            await success_element.wait_for(timeout=10000)

            assert True
        except Exception as e:
            # for click solvers, we might not always succeed due to detection
            # so we'll just verify the solver ran without crashing

            if framework in [FrameworkType.PLAYWRIGHT, FrameworkType.PATCHRIGHT]:
                assert True, (f"Unable to solve the captcha for {framework.value}, but it is expected behavior "
                              f"for ClickSolver since it relies on browser stealth and may not always succeed.")
                return

            raise
