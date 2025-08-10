"""Token response schema."""

from pydantic import BaseModel


class Token(BaseModel):
    """Response model for authentication token."""

    access_token: str
    token_type: str
