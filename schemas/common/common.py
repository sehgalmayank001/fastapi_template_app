"""Common validation and response components."""

from typing import Annotated
from fastapi import Path
from .error_response import ErrorResponse

# Reusable path parameter validation for any ID
ValidId = Annotated[int, Path(gt=0, description="ID must be greater than 0")]

# Common error responses - just use one for all endpoints
ERROR_RESPONSES = {
    401: {"model": ErrorResponse, "description": "Authentication failed"},
    403: {"model": ErrorResponse, "description": "Access forbidden"},
    404: {"model": ErrorResponse, "description": "Resource not found"},
    422: {"model": ErrorResponse, "description": "Validation error"},
}
