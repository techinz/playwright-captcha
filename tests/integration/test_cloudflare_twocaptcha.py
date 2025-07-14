import asyncio

import pytest
from playwright.async_api import Page

from playwright_captcha import CaptchaType, TwoCaptchaSolver, FrameworkType


@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.requires_api_key
@pytest.mark.asyncio
class TestCloudflareTwoCaptchaSolvers:
    """Integration tests for Cloudflare TwoCaptcha solvers with all frameworks"""

    async def test_twocaptcha_turnstile_solver(self, browser_context, two_captcha_client):
        """Test TwoCaptcha solver for Cloudflare Turnstile with all frameworks"""
        framework, page = browser_context

        framework: FrameworkType
        page: Page

        async with TwoCaptchaSolver(
                framework=framework,
                page=page,
                async_two_captcha_client=two_captcha_client
        ) as solver:
            await page.goto('https://2captcha.com/demo/cloudflare-turnstile')
            await asyncio.sleep(5)

            turnstile_container = page.locator('#cf-turnstile')
            await turnstile_container.wait_for()

            if await turnstile_container.count() == 0:
                pytest.fail('Turnstile container not found on the page')

            result = await solver.solve_captcha(
                captcha_container=turnstile_container,
                captcha_type=CaptchaType.CLOUDFLARE_TURNSTILE
            )

            # twocaptcha should return a token
            assert result is not None, "TwoCaptcha solver should return a token"
            assert isinstance(result, str), "Token should be a string"
            assert len(result) > 0, "Token should not be empty"

        submit_button = page.locator('//button[@data-action="demo_action"]')
        await submit_button.wait_for()
        await submit_button.click()
        await asyncio.sleep(5)

        try:
            success_element = page.locator('//p[text()="Captcha is passed successfully!"]')
            await success_element.wait_for(timeout=15000)

            assert True
        except Exception as e:
            pytest.fail(f"TwoCaptcha solver failed to solve Turnstile with {framework.value}: {e}")

    async def test_twocaptcha_interstitial_solver(self, browser_context, two_captcha_client):
        """Test TwoCaptcha solver for Cloudflare Interstitial with all frameworks"""

        framework, page = browser_context

        framework: FrameworkType
        page: Page

        async with TwoCaptchaSolver(
                framework=framework,
                page=page,
                async_two_captcha_client=two_captcha_client
        ) as solver:
            await page.goto('https://2captcha.com/demo/cloudflare-turnstile-challenge', wait_until='domcontentloaded')
            await asyncio.sleep(15)

            result = await solver.solve_captcha(
                captcha_container=page,
                captcha_type=CaptchaType.CLOUDFLARE_INTERSTITIAL
            )

            # twocaptcha should return a token
            assert result is not None, "TwoCaptcha solver should return a token"
            assert isinstance(result, str), "Token should be a string"
            assert len(result) > 0, "Token should not be empty"

        await asyncio.sleep(5)

        try:
            success_element = page.locator('//p[text()="Captcha is passed successfully!"]')
            await success_element.wait_for(timeout=15000)

            assert True
        except Exception as e:
            pytest.fail(f"TwoCaptcha solver failed to solve Interstitial with {framework.value}: {e}")
