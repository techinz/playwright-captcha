from playwright_captcha import BaseSolver, CaptchaType

from .apply import apply_cutcaptcha
from .detect_data import detect_cutcaptcha_data
from .solvers.twocaptcha import solve_cutcaptcha_twocaptcha
from ...types.solvers import SolverType

# register solvers
BaseSolver.register_solver(SolverType.twocaptcha, CaptchaType.CUTCAPTCHA, solve_cutcaptcha_twocaptcha)

# register detector
BaseSolver.register_detector(CaptchaType.CUTCAPTCHA, detect_cutcaptcha_data)

# register appliers
BaseSolver.register_applier(CaptchaType.CUTCAPTCHA, apply_cutcaptcha)
