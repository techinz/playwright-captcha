import asyncio
import pytest
import pytest_asyncio
from typing import Optional, Union

from playwright.async_api import ElementHandle, Frame, Page

from playwright_captcha import BaseSolver, CaptchaType, ClickSolver, FrameworkType
from playwright_captcha.types import SolverType


@pytest.mark.asyncio
class TestCloudflareClickSolversLocal:
    """Unit tests for Cloudflare Click solvers with all frameworks"""

    async def fake_solve_cloudflare_by_click(
            self,
            framework: FrameworkType,
            page: Page,
            captcha_container: Union[Page, Frame, ElementHandle],
            expected_content_selector: Optional[str] = None,
            solve_click_delay: int = 1,
            wait_checkbox_attempts: int = 2,
            wait_checkbox_delay: int = 3,
            checkbox_click_attempts: int = 4,
    ) -> None:
        self.solve_click_delay_effective = solve_click_delay
        self.wait_checkbox_attempts_effective = wait_checkbox_attempts
        self.wait_checkbox_delay_effective = wait_checkbox_delay
        self.checkbox_click_attempts_effective = checkbox_click_attempts

    #@pytest_asyncio.fixture(autouse=True) # incorrect order
    @pytest_asyncio.fixture
    async def patch_solver(self, browser_context):
        timings = {}
        try:
            timings['solve_click_delay'] = self.solve_click_delay
        except AttributeError:
            pass
        try:
            timings['wait_checkbox_attempts'] = self.wait_checkbox_attempts
        except AttributeError:
            pass
        try:
            timings['wait_checkbox_delay'] = self.wait_checkbox_delay
        except AttributeError:
            pass
        try:
            timings['checkbox_click_attempts'] = self.checkbox_click_attempts
        except AttributeError:
            pass

        BaseSolver.register_solver(
            SolverType.click,
            CaptchaType.CLOUDFLARE_TURNSTILE,
            self.fake_solve_cloudflare_by_click,
            **timings,
        )

    @pytest_asyncio.fixture
    async def page_mock(self, browser_context):
        """Create page based on browser context"""
        framework, page = browser_context

        framework: FrameworkType
        page: Page

        MOCKUP = "<!DOCTYPE html><html><head><title>Hello, world!</title></head><body></body></html>"

        url = "https://2captcha.com/demo/cloudflare-turnstile"
        await page.route(url, lambda route: route.fulfill(body=MOCKUP, status=200))
        await page.goto(url)

        assert await page.content() == MOCKUP

        yield framework, page

    async def test_click_turnstile_solver(self, page_mock, patch_solver):
        """Test Click solver for Cloudflare Turnstile with all frameworks"""
        framework, page = page_mock

        framework: FrameworkType
        page: Page

        async with ClickSolver(framework=framework, page=page) as solver:
            await solver.solve_captcha(captcha_container=page,
                                       captcha_type=CaptchaType.CLOUDFLARE_TURNSTILE)

    @pytest_asyncio.fixture
    async def solver_timings(self, browser_context):
        self.solve_click_delay = 5
        self.wait_checkbox_attempts = 6
        self.wait_checkbox_delay = 7
        self.checkbox_click_attempts = 8

    async def test_click_turnstile_solver_timings_register(self, page_mock, solver_timings, patch_solver):
        """Test Click solver timings set at registration for Cloudflare Turnstile with all frameworks"""
        framework, page = page_mock

        framework: FrameworkType
        page: Page

        async with ClickSolver(framework=framework, page=page) as solver:
            await solver.solve_captcha(captcha_container=page,
                                       captcha_type=CaptchaType.CLOUDFLARE_TURNSTILE)
        assert self.solve_click_delay_effective == 5
        assert self.wait_checkbox_attempts_effective == 6
        assert self.wait_checkbox_delay_effective == 7
        assert self.checkbox_click_attempts_effective == 8

    async def test_click_turnstile_solver_timings_kwargs(self, page_mock, patch_solver):
        """Test Click solver timings set via kwargs for Cloudflare Turnstile with all frameworks"""
        framework, page = page_mock

        framework: FrameworkType
        page: Page

        async with ClickSolver(framework=framework, page=page) as solver:
            await solver.solve_captcha(
                captcha_container=page,
                captcha_type=CaptchaType.CLOUDFLARE_TURNSTILE,
                solve_click_delay=9,
                wait_checkbox_attempts=10,
                wait_checkbox_delay=11,
                checkbox_click_attempts=12,
            )
        assert self.solve_click_delay_effective == 9
        assert self.wait_checkbox_attempts_effective == 10
        assert self.wait_checkbox_delay_effective == 11
        assert self.checkbox_click_attempts_effective == 12

    async def test_click_turnstile_solver_timings_register_kwargs(self, page_mock, solver_timings, patch_solver):
        """Test Click solver timings set at registration and kwargs for Cloudflare Turnstile with all frameworks"""
        framework, page = page_mock

        framework: FrameworkType
        page: Page

        async with ClickSolver(framework=framework, page=page) as solver:
            await solver.solve_captcha(
                captcha_container=page,
                captcha_type=CaptchaType.CLOUDFLARE_TURNSTILE,
                solve_click_delay=9,
                wait_checkbox_attempts=10,
                wait_checkbox_delay=11,
                checkbox_click_attempts=12,
            )
        assert self.solve_click_delay_effective == 9
        assert self.wait_checkbox_attempts_effective == 10
        assert self.wait_checkbox_delay_effective == 11
        assert self.checkbox_click_attempts_effective == 12
