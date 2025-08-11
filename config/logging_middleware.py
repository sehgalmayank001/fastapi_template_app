"""Request logging middleware with configurable parameter filtering."""

import json
import time
import logging
from typing import Dict, Any, List, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


from .logging_config import logging_config
from .logging_helpers import format_log_message

# Configure logger with environment-based level
logger = logging.getLogger("request_logger")
logger.setLevel(getattr(logging, logging_config.log_level))

# Create console handler if not already configured
if not logger.handlers:
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for comprehensive request/response logging with parameter filtering."""

    def __init__(self, app, filter_params: Optional[List[str]] = None):
        """
        Initialize middleware with parameter filtering.

        Args:
            app: FastAPI application
            filter_params: Optional explicit filter parameters. If None, uses settings.filter_params
        """
        super().__init__(app)
        # Use explicit params or fall back to config defaults
        self.filter_params = filter_params or logging_config.filter_params

    async def dispatch(self, request: Request, call_next):
        """Log request and response with timing information."""
        start_time = time.time()

        # Extract request information
        request_data = await self._extract_request_data(request)

        # Build request log data
        request_log_data = {
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers),
            "query_params": dict(request.query_params),
            "path_params": request.path_params,
            "body": request_data.get("body"),
            "user_agent": request.headers.get("user-agent"),
            "remote_addr": request.client.host if request.client else None,
        }

        # Process request
        response = await call_next(request)

        # Calculate processing time
        process_time = time.time() - start_time
        process_time_ms = round(process_time * 1000, 2)

        # Log incoming request (DEBUG level - detailed info)
        logger.debug(format_log_message("INCOMING REQUEST", request_log_data, self.filter_params))

        # Extract and log response information
        response_data = await self._extract_response_data(response)
        response_log_data = {
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": response_data.get("body"),
            "process_time_ms": process_time_ms,
        }

        # Log outgoing response (INFO level - important info)
        logger.info(format_log_message("OUTGOING RESPONSE", response_log_data, self.filter_params))

        # Add timing header to response
        response.headers["X-Process-Time"] = str(process_time)

        return response

    async def _extract_request_data(self, request: Request) -> Dict[str, Any]:
        """Extract request body data safely."""
        request_data = {}

        try:
            # Handle different content types
            content_type = request.headers.get("content-type", "")

            if "application/json" in content_type:
                body = await request.body()
                if body:
                    try:
                        request_data["body"] = json.loads(body.decode())
                    except json.JSONDecodeError:
                        request_data["body"] = (
                            body.decode()[:500] + "..." if len(body) > 500 else body.decode()
                        )
            elif "application/x-www-form-urlencoded" in content_type:
                # Skip logging form data to avoid consuming the request stream
                # Form data will be processed by FastAPI dependencies
                request_data["body"] = "<FORM_DATA_SKIPPED_FOR_COMPATIBILITY>"
            elif "multipart/form-data" in content_type:
                # Skip logging multipart data to avoid consuming the request stream
                # Multipart data will be processed by FastAPI dependencies
                request_data["body"] = "<MULTIPART_DATA_SKIPPED_FOR_COMPATIBILITY>"
            else:
                body = await request.body()
                if body:
                    # Truncate large non-JSON bodies
                    body_str = body.decode()[:200] + "..." if len(body) > 200 else body.decode()
                    request_data["body"] = body_str

        except (UnicodeDecodeError, ValueError, AttributeError) as e:
            request_data["body"] = f"<ERROR READING BODY: {str(e)}>"

        return request_data

    async def _extract_response_data(self, response: Response) -> Dict[str, Any]:
        """Extract response body data safely."""
        response_data = {}

        try:
            # Only log response body for certain content types and status codes
            content_type = response.headers.get("content-type", "")

            if (
                response.status_code < 500  # Don't log server error responses
                and "application/json" in content_type
                and hasattr(response, "body")
            ):
                try:
                    body = getattr(response, "body", None)
                    if body:
                        if isinstance(body, bytes):
                            response_data["body"] = json.loads(body.decode())
                        else:
                            response_data["body"] = body
                except (json.JSONDecodeError, AttributeError):
                    # Skip if we can't parse response body
                    pass

        except (json.JSONDecodeError, AttributeError, UnicodeDecodeError):
            # Skip response body logging if there's any issue
            pass

        return response_data
