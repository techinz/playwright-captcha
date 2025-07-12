from typing import List

from playwright_captcha.utils.exceptions import CaptchaDataDetectionError


def validate_required_params(required_params: List[str], kwargs: dict):
    for param in required_params:
        if param not in kwargs:
            raise CaptchaDataDetectionError(f"{param} could not be auto-detected. Please provide it explicitly")
