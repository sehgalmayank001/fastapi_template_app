"""User verification schema."""

from pydantic import BaseModel, Field


class UserVerification(BaseModel):
    """Request model for password change."""

    password: str
    new_password: str = Field(min_length=6)
