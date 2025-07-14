from enum import Enum


class SolverType(Enum):
    """Supported solver types"""

    base = "base"

    # click
    click = "click"

    # api
    twocaptcha = "twocaptcha"
    tencaptcha = "tencaptcha"
    captchaai = "captchaai"
