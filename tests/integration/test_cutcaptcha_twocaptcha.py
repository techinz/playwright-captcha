import asyncio

import pytest
from playwright.async_api import Page

from playwright_captcha import CaptchaType, TwoCaptchaSolver, FrameworkType


@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.requires_api_key
@pytest.mark.asyncio
class TestCutCaptchaTwoCaptchaSolvers:
    """Integration tests for CutCaptcha TwoCaptcha solver with all frameworks"""

    async def test_twocaptcha_cutcaptcha_solver(self, browser_context, two_captcha_client):
        """Test TwoCaptcha solver for CutCaptcha with all frameworks"""
        framework, page = browser_context

        framework: FrameworkType
        page: Page

        async with TwoCaptchaSolver(
                framework=framework,
                page=page,
                async_two_captcha_client=two_captcha_client
        ) as solver:
            # the contact form on cutcaptcha.net has a live widget, the form itself is not submitted
            await page.goto('https://cutcaptcha.net/#contact')
            await page.locator('.cutcaptcha').wait_for()
            await asyncio.sleep(5)

            result = await solver.solve_captcha(
                captcha_container=page,
                captcha_type=CaptchaType.CUTCAPTCHA
            )

            assert isinstance(result, str) and result, "TwoCaptcha solver should return a non-empty token"

        applied_token = await page.locator('.cutcaptcha input[name="cutcaptcha-response"]').input_value()
        assert applied_token == result, f"Token was not applied to the page with {framework.value}"
