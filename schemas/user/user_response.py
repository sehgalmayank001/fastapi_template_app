"""User response schema."""

from pydantic import BaseModel


class UserResponse(BaseModel):
    """Response model for user operations."""

    id: int
    email: str
    username: str
    first_name: str
    last_name: str
    is_active: bool
    role: str

    class Config:
        from_attributes = True
