"""
Playwright Captcha - Automatically solve captcha using Playwright
"""

try:
    import playwright
except ImportError:
    raise ImportError("Playwright is not installed. Please install it with 'pip install playwright'.")

from playwright_captcha.solvers.api.twocaptcha.twocaptcha_solver import TwoCaptchaSolver
from playwright_captcha.solvers.base_solver import BaseSolver
from .solvers.api.api_solver_base import ApiSolverBase
from .solvers.click import ClickSolver
from .types import CaptchaType, FrameworkType

from .captchas import *  # register all components

__all__ = [
    'CaptchaType',
    'FrameworkType',
    'BaseSolver',
    'ClickSolver',
    'ApiSolverBase',
    'TwoCaptchaSolver'
]
