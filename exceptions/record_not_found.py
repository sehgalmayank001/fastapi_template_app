"""Record not found exception."""

from starlette import status
from .api_exception import APIException


class RecordNotFound(APIException):
    """Exception for when a record is not found (404)."""

    def __init__(self, message: str = "Record not found"):
        super().__init__(message, status.HTTP_404_NOT_FOUND)
