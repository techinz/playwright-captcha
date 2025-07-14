from playwright_captcha import BaseSolver, CaptchaType

from .apply import apply_recaptcha_v3_captcha
from .detect_data import detect_recaptcha_v3_data
from .solvers.captchaai import solve_recaptcha_v3_captcha_ai
from .solvers.tencaptcha import solve_recaptcha_v3_tencaptcha
from .solvers.twocaptcha import solve_recaptcha_v3_twocaptcha
from ...types.solvers import SolverType

# register solvers
BaseSolver.register_solver(SolverType.twocaptcha, CaptchaType.RECAPTCHA_V3, solve_recaptcha_v3_twocaptcha)
BaseSolver.register_solver(SolverType.tencaptcha, CaptchaType.RECAPTCHA_V3, solve_recaptcha_v3_tencaptcha)
BaseSolver.register_solver(SolverType.captchaai, CaptchaType.RECAPTCHA_V3, solve_recaptcha_v3_captcha_ai)

# register detector
BaseSolver.register_detector(CaptchaType.RECAPTCHA_V3, detect_recaptcha_v3_data)

# register appliers
BaseSolver.register_applier(CaptchaType.RECAPTCHA_V3, apply_recaptcha_v3_captcha)
