"""Authentication middleware - stores user ID in request state."""

from typing import Optional
from fastapi import Request
from jose import JWTError, jwt
from starlette.middleware.base import BaseHTTPMiddleware

from .settings import settings


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware to extract user ID from JWT and store in request.state."""

    async def dispatch(self, request: Request, call_next):
        """Extract user ID from JWT token and store in request.state."""
        # Get user ID from token and store in request state
        user_id = self._get_user_id_from_request(request)
        request.state.user_id = user_id

        # Initialize user cache as "not fetched yet" (different from None user)
        # We'll use a sentinel value to distinguish between "not checked" and "no user"
        request.state.user = "__NOT_FETCHED__"

        # Continue with the request
        response = await call_next(request)
        return response

    def _get_user_id_from_request(self, request: Request) -> Optional[int]:
        """Extract user ID from JWT token (don't fetch from DB here)."""
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            return None

        token = authorization.split(" ")[1]

        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
            return payload.get("id")
        except JWTError:
            return None
