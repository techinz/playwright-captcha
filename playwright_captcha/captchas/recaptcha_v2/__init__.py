from playwright_captcha import BaseSolver, CaptchaType

from .apply import apply_recaptcha_v2_captcha
from .detect_data import detect_recaptcha_v2_data
from .solvers.twocaptcha import solve_recaptcha_v2_twocaptcha
from ...types.solvers import SolverType

# register solvers
BaseSolver.register_solver(SolverType.twocaptcha, CaptchaType.RECAPTCHA_V2, solve_recaptcha_v2_twocaptcha)

# register detector
BaseSolver.register_detector(CaptchaType.RECAPTCHA_V2, detect_recaptcha_v2_data)

# register appliers
BaseSolver.register_applier(CaptchaType.RECAPTCHA_V2, apply_recaptcha_v2_captcha)
