"""Pydantic schemas organized by domain."""

# Auth schemas
from .auth import CreateUserRequest, Token

# Todo schemas
from .todo import TodoRequest, TodoResponse

# User schemas
from .user import UserResponse, UserVerification

# Common schemas and validation
from .common import ValidId, ERROR_RESPONSES, ErrorResponse

__all__ = [
    # Common
    "ValidId",
    "ERROR_RESPONSES",
    "ErrorResponse",
    # Auth
    "CreateUserRequest",
    "Token",
    # Todo
    "TodoRequest",
    "TodoResponse",
    # User
    "UserResponse",
    "UserVerification",
]
