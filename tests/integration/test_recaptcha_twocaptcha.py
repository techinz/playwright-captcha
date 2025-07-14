import asyncio

import pytest
from playwright.async_api import Page

from playwright_captcha import CaptchaType, TwoCaptchaSolver, FrameworkType


@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.requires_api_key
@pytest.mark.asyncio
class TestRecaptchaTwoCaptchaSolvers:
    """Integration tests for reCAPTCHA TwoCaptcha solvers with all frameworks"""

    async def test_twocaptcha_recaptcha_v2_solver(self, browser_context, two_captcha_client):
        """Test TwoCaptcha solver for reCAPTCHA v2 with all frameworks"""

        framework, page = browser_context

        framework: FrameworkType
        page: Page

        async with TwoCaptchaSolver(
                framework=framework,
                page=page,
                async_two_captcha_client=two_captcha_client
        ) as solver:
            await page.goto('https://2captcha.com/demo/recaptcha-v2')
            await asyncio.sleep(5)

            recaptcha_v2_container = page.locator('#g-recaptcha')
            await recaptcha_v2_container.wait_for()

            if await recaptcha_v2_container.count() == 0:
                pytest.fail('reCAPTCHA v2 container not found on the page')

            result = await solver.solve_captcha(
                captcha_container=recaptcha_v2_container,
                captcha_type=CaptchaType.RECAPTCHA_V2
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
            pytest.fail(f"TwoCaptcha solver failed to solve reCAPTCHA v2 with {framework.value}: {e}")

    async def test_twocaptcha_recaptcha_v3_solver(self, browser_context, two_captcha_client):
        """Test TwoCaptcha solver for reCAPTCHA v3 with all frameworks"""

        framework, page = browser_context

        framework: FrameworkType
        page: Page

        async with TwoCaptchaSolver(
                framework=framework,
                page=page,
                async_two_captcha_client=two_captcha_client
        ) as solver:
            await page.goto('https://2captcha.com/demo/recaptcha-v3')
            await asyncio.sleep(5)

            # v3 doesn't have visible container, so we use the page itself
            result = await solver.solve_captcha(
                captcha_container=page,
                captcha_type=CaptchaType.RECAPTCHA_V3
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
            pytest.fail(f"TwoCaptcha solver failed to solve reCAPTCHA v3 with {framework.value}: {e}")

    async def test_recaptcha_solver_error_handling(self, browser_context, two_captcha_client):
        """Test error handling for reCAPTCHA solvers"""

        framework, page = browser_context

        framework: FrameworkType
        page: Page

        async with TwoCaptchaSolver(
                framework=framework,
                page=page,
                async_two_captcha_client=two_captcha_client
        ) as solver:
            # navigate to a page without captcha
            await page.goto('https://example.com')
            await asyncio.sleep(2)

            # try to solve non-existent captcha
            with pytest.raises(Exception):  # expecting some kind of error
                await solver.solve_captcha(
                    captcha_container=page,
                    captcha_type=CaptchaType.RECAPTCHA_V2
                )
