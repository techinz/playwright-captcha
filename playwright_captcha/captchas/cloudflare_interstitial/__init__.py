from playwright_captcha import BaseSolver, CaptchaType

from .apply import apply_cloudflare_interstitial_captcha
from .detect_data import detect_interstitial_data
from .solvers.click import solve_cloudflare_interstitial_click
from .solvers.twocaptcha import solve_cloudflare_interstitial_twocaptcha
from ...types.solvers import SolverType

# register solvers
BaseSolver.register_solver(SolverType.click, CaptchaType.CLOUDFLARE_INTERSTITIAL, solve_cloudflare_interstitial_click)
# for this captcha type's api-based solvers we need to reload the page on failure because we intercept the challenge data,
# and it not always works on the first attempt
BaseSolver.register_solver(SolverType.twocaptcha, CaptchaType.CLOUDFLARE_INTERSTITIAL,
                           solve_cloudflare_interstitial_twocaptcha, reload_on_fail=True)


# register detector
BaseSolver.register_detector(CaptchaType.CLOUDFLARE_INTERSTITIAL, detect_interstitial_data)

# register appliers
BaseSolver.register_applier(CaptchaType.CLOUDFLARE_INTERSTITIAL, apply_cloudflare_interstitial_captcha)
