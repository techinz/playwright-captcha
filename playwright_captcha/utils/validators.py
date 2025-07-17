from typing import List

from playwright_captcha.utils.exceptions import CaptchaDataDetectionError


def validate_required_params(required_params: List[str], kwargs: dict) -> None:
    """
    Validate that all required parameters are present in the kwargs dictionary.

    :param required_params: List of required parameter names
    :param kwargs: Dictionary of parameters to check

    :raises CaptchaDataDetectionError: If any required parameter is missing
    """

    for param in required_params:
        if param not in kwargs:
            raise CaptchaDataDetectionError(f"{param} could not be auto-detected. Please provide it explicitly")
