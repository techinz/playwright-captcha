from enum import Enum


class SolverType(Enum):
    """ Supported solver types """

    base = "base"

    click = "click"
    twocaptcha = "twocaptcha"
