"""Parameter missing exception."""

from starlette import status
from .api_exception import APIException


class ParameterMissing(APIException):
    """Exception for missing required parameters (400)."""

    def __init__(self, param: str):
        self.param = param
        message = f"Parameter '{param}' is required"
        super().__init__(message, status.HTTP_400_BAD_REQUEST)
