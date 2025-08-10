"""Authentication helpers - no request parameter needed!"""

from functools import wraps
from fastapi import Request
from contextvars import ContextVar
from typing import Optional

from exceptions import NotAuthorized
from models import User
from .database import SessionLocal

# Context variable to store current request (for accessing user)
_current_request: ContextVar[Request] = ContextVar("current_request")


def set_current_request(request: Request):
    """Store current request in context variable."""
    _current_request.set(request)


def current_user() -> Optional[User]:
    """
    Helper to get the current authenticated user.
    Returns cached User model object, fetching from DB only once per request.
    Handles its own database dependency.
    """
    try:
        request = _current_request.get()

        # Check if user is already cached in request state
        cached_user = getattr(request.state, "user", "__NOT_FETCHED__")
        if cached_user != "__NOT_FETCHED__":
            return cached_user  # Return cached user (could be None or actual User object)

        # Get user_id from request state
        user_id = getattr(request.state, "user_id", None)
        if not user_id:
            # Cache None to avoid repeated checks
            request.state.user = None
            return None

        # Create our own database session for user lookup
        db = SessionLocal()
        try:
            # Fetch user from database and cache it
            user = db.query(User).filter(User.id == user_id).first()
            request.state.user = user  # Cache for subsequent calls
            return user
        finally:
            db.close()  # Always close the session

    except LookupError:
        return None


def authenticate_user(func):
    """Decorator equivalent to before_action :authenticate_user!"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Find request and set in context
        request = None
        for arg in args:
            if isinstance(arg, Request):
                request = arg
                break

        if request:
            set_current_request(request)

        # Check authentication - just verify user_id exists
        try:
            request = _current_request.get()
            user_id = getattr(request.state, "user_id", None)
            if not user_id:
                raise NotAuthorized()
        except LookupError:
            raise NotAuthorized()

        return await func(*args, **kwargs)

    return wrapper


def admin_required(func):
    """Decorator equivalent to before_action :admin_required"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Find request and set in context
        request = None
        for arg in args:
            if isinstance(arg, Request):
                request = arg
                break

        if request:
            set_current_request(request)

            # Check admin authentication
        user = current_user()
        if not user:
            raise NotAuthorized()

        if user.role != "admin":
            raise NotAuthorized("Admin access required")

        return await func(*args, **kwargs)

    return wrapper


def optional_auth(func):
    """Decorator for optional authentication"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Find request and set in context
        request = None
        for arg in args:
            if isinstance(arg, Request):
                request = arg
                break

        if request:
            set_current_request(request)

        # No authentication check - user may be None
        return await func(*args, **kwargs)

    return wrapper
