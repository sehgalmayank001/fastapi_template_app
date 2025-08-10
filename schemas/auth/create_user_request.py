"""Create user request schema."""

from pydantic import BaseModel


class CreateUserRequest(BaseModel):
    """Request model for user creation."""

    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str
