"""Record invalid exception."""

from starlette import status
from .api_exception import APIException


class RecordInvalid(APIException):
    """Exception for validation errors (422)."""

    def __init__(self, message: str = "Record is invalid"):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY)
