"""Structlog-based request logging middleware."""

import re
import time
import uuid
from typing import Optional
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from .structlog_config import get_logger


class StructlogMiddleware(BaseHTTPMiddleware):
    """Middleware for structured request/response logging using structlog."""

    async def dispatch(self, request: Request, call_next):
        """Log request and response with structured data."""
        # Generate unique request ID
        request_id = str(uuid.uuid4())[:8]

        # Extract user ID from request state (set by auth dependencies)
        user_id = self._get_user_id_from_request(request)

        # Create logger with bound context
        logger = get_logger("request").bind(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            user_id=user_id,
            ip=self._get_client_ip(request),
            user_agent=self._get_user_agent(request),
        )

        # Debug log for request start (only in DEBUG level)
        headers = self._filter_sensitive_headers(dict(request.headers))
        logger.debug("Request received", headers=headers, query_params=dict(request.query_params))

        # Process request
        start_time = time.time()
        response = await call_next(request)
        duration_ms = round((time.time() - start_time) * 1000, 2)

        # Structured log entry with all request data
        log_level = "info"
        if response.status_code >= 400:
            log_level = "error"
        elif response.status_code >= 300:
            log_level = "warning"

        getattr(logger, log_level)(
            "Request completed",
            status=response.status_code,
            duration_ms=duration_ms,
            content_length=response.headers.get("content-length", 0),
        )

        # Add request ID to response headers for tracing
        response.headers["X-Request-ID"] = request_id

        return response

    def _get_user_id_from_request(self, request: Request) -> Optional[int]:
        """Extract user ID from JWT token in Authorization header."""
        try:
            from jose import jwt, JWTError
            from .settings import settings

            authorization = request.headers.get("Authorization")
            if not authorization or not authorization.startswith("Bearer "):
                return None

            token = authorization.split(" ")[1]
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
            return payload.get("id")

        except (JWTError, ImportError, AttributeError):
            return None

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address."""
        # Check for forwarded IP first (for load balancers)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        # Check for real IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fall back to client host
        return request.client.host if request.client else "unknown"

    def _get_user_agent(self, request: Request) -> str:
        """Get simplified user agent string."""
        user_agent = request.headers.get("User-Agent", "")

        # Simplify common user agents
        if "Chrome" in user_agent:
            # Extract Chrome version
            match = re.search(r"Chrome/(\d+\.\d+)", user_agent)
            return f"Chrome/{match.group(1)}" if match else "Chrome"
        elif "Firefox" in user_agent:
            match = re.search(r"Firefox/(\d+\.\d+)", user_agent)
            return f"Firefox/{match.group(1)}" if match else "Firefox"
        elif "Safari" in user_agent and "Chrome" not in user_agent:
            return "Safari"
        elif "curl" in user_agent.lower():
            return "curl"
        elif "postman" in user_agent.lower():
            return "Postman"
        else:
            # Return first 50 characters for unknown agents
            return user_agent[:50] if user_agent else "unknown"

    def _filter_sensitive_headers(self, headers: dict) -> dict:
        """Filter sensitive information from request headers."""
        sensitive_patterns = [
            "authorization",
            "cookie",
            "x-api-key",
            "x-auth-token",
            "authentication",
            "proxy-authorization",
        ]

        filtered_headers = {}
        for key, value in headers.items():
            key_lower = key.lower()

            # Check if header contains sensitive patterns
            if any(pattern in key_lower for pattern in sensitive_patterns):
                filtered_headers[key] = "[FILTERED]"
            else:
                filtered_headers[key] = value

        return filtered_headers
