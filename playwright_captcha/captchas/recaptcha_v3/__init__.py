from playwright_captcha import BaseSolver, CaptchaType

from .apply import apply_recaptcha_v3_captcha
from .detect_data import detect_recaptcha_v3_data
from .solvers.twocaptcha import solve_recaptcha_v3_twocaptcha
from ...types.solvers import SolverType

# register solvers
BaseSolver.register_solver(SolverType.twocaptcha, CaptchaType.RECAPTCHA_V3, solve_recaptcha_v3_twocaptcha)

# register detector
BaseSolver.register_detector(CaptchaType.RECAPTCHA_V3, detect_recaptcha_v3_data)

# register appliers
BaseSolver.register_applier(CaptchaType.RECAPTCHA_V3, apply_recaptcha_v3_captcha)
