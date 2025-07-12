class CaptchaDetectionError(Exception):
    """ Raised when there is an error in captcha detection """
    pass


class CaptchaDataDetectionError(Exception):
    """ Raised when there is an error in captcha data detection """
    pass


class CaptchaSolvingError(Exception):
    """ Raised when there is an error in solving the captcha """
    pass


class CaptchaApplyingError(Exception):
    """ Raised when there is an error in applying the solved captcha """
    pass
