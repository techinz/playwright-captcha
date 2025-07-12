from playwright_captcha import BaseSolver, CaptchaType

from .apply import apply_cloudflare_turnstile_captcha
from .detect_data import detect_turnstile_data
from .solvers.click import solve_cloudflare_turnstile_click
from .solvers.twocaptcha import solve_cloudflare_turnstile_twocaptcha
from ...types.solvers import SolverType

# register solvers
BaseSolver.register_solver(SolverType.click, CaptchaType.CLOUDFLARE_TURNSTILE, solve_cloudflare_turnstile_click)
BaseSolver.register_solver(SolverType.twocaptcha, CaptchaType.CLOUDFLARE_TURNSTILE,
                           solve_cloudflare_turnstile_twocaptcha)

# register detector
BaseSolver.register_detector(CaptchaType.CLOUDFLARE_TURNSTILE, detect_turnstile_data)

# register appliers
BaseSolver.register_applier(CaptchaType.CLOUDFLARE_TURNSTILE, apply_cloudflare_turnstile_captcha)
