"""Not authorized exception."""

from starlette import status
from .api_exception import APIException


class NotAuthorized(APIException):
    """Exception for authentication/authorization errors (401/403)."""

    def __init__(self, message: str = "Authentication Failed"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)
