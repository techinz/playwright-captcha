import logging
from abc import abstractmethod

from playwright.async_api import Page

from playwright_captcha.solvers.base_solver import BaseSolver
from playwright_captcha.types import FrameworkType

logger = logging.getLogger(__name__)


class ApiSolverBase(BaseSolver):
    """ Base class for external API-based captcha solvers """

    def __init__(self, framework: FrameworkType, page: Page, max_attempts: int = 3, attempt_delay: int = 5):
        """
        Initialize the API-based solver

        :param page: Playwright Page object where the captcha is located
        :param max_attempts: Maximum number of attempts to solve the captcha
        :param attempt_delay: Delay in seconds between attempts to solve the captcha
        """

        super().__init__(framework=framework, page=page, max_attempts=max_attempts, attempt_delay=attempt_delay)

    @abstractmethod
    async def get_balance(self) -> float:
        """ Get account balance """
        pass
