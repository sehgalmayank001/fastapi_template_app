"""Error response schema."""

from typing import Any, Dict
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Standard error response format."""

    errors: Dict[str, Any]
    timestamp: str
