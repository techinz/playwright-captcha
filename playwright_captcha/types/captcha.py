from enum import Enum


class CaptchaType(Enum):
    """ Supported captcha types """

    CLOUDFLARE_INTERSTITIAL = "cloudflare_interstitial"
    CLOUDFLARE_TURNSTILE = "cloudflare_turnstile"
    RECAPTCHA_V2 = "recaptcha_v2"
    RECAPTCHA_V3 = "recaptcha_v3"
