import asyncio
import os
from typing import Optional

import pytest
import pytest_asyncio
from dotenv import load_dotenv
from twocaptcha import AsyncTwoCaptcha

from playwright_captcha import FrameworkType

load_dotenv()


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""

    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def two_captcha_api_key() -> Optional[str]:
    """Get 2Captcha API key from environment"""

    api_key = os.getenv('TWO_CAPTCHA_API_KEY')
    if not api_key:
        pytest.skip("TWO_CAPTCHA_API_KEY not found in environment")
    return api_key


@pytest.fixture(scope="session")
def two_captcha_client(two_captcha_api_key: str) -> AsyncTwoCaptcha:
    """Create AsyncTwoCaptcha client"""

    return AsyncTwoCaptcha(two_captcha_api_key)


@pytest.fixture(params=[
    FrameworkType.PLAYWRIGHT,
    FrameworkType.PATCHRIGHT,
    FrameworkType.CAMOUFOX
])
def framework(request) -> FrameworkType:
    """Parametrized fixture for all supported frameworks"""

    return request.param


@pytest_asyncio.fixture
async def browser_context(framework: FrameworkType):
    """Create browser context based on framework type"""

    headless = False

    if framework == FrameworkType.PLAYWRIGHT:
        from playwright.async_api import async_playwright
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=headless)
            context = await browser.new_context()
            page = await context.new_page()
            yield framework, page
            await browser.close()
    elif framework == FrameworkType.PATCHRIGHT:
        try:
            from patchright.async_api import async_playwright as patchright_playwright
            async with patchright_playwright() as playwright:
                browser = await playwright.chromium.launch(channel="chrome", headless=headless)
                context = await browser.new_context()
                page = await context.new_page()
                yield framework, page
                await browser.close()
        except ImportError:
            pytest.skip("Patchright not installed")
    elif framework == FrameworkType.CAMOUFOX:
        try:
            from camoufox import AsyncCamoufox
            from playwright_captcha.utils.camoufox_add_init_script.add_init_script import get_addon_path
            import os

            addon_path = get_addon_path()

            async with AsyncCamoufox(
                    headless=headless,
                    geoip=True,
                    humanize=True,
                    i_know_what_im_doing=True,
                    config={'forceScopeAccess': True},
                    disable_coop=True,
                    main_world_eval=True,
                    addons=[os.path.abspath(addon_path)]
            ) as browser:
                page = await browser.new_page()
                yield framework, page
        except ImportError:
            pytest.skip("Camoufox not installed")


# markers
pytestmark = pytest.mark.asyncio


def pytest_configure(config):
    """Configure pytest markers"""

    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "requires_api_key: marks tests that require API key"
    )
