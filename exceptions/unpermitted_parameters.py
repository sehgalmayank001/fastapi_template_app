"""Unpermitted parameters exception."""

from typing import List
from starlette import status
from .api_exception import APIException


class UnpermittedParameters(APIException):
    """Exception for unpermitted parameters (400)."""

    def __init__(self, params: List[str]):
        self.params = params
        param_list = ", ".join(params)
        message = f"Unpermitted parameters: {param_list}"
        super().__init__(message, status.HTTP_400_BAD_REQUEST)
