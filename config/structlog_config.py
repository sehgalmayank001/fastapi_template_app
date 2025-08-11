"""Structlog configuration for FastAPI application."""

import os
import sys
import logging
import structlog
from typing import Any, Dict


def configure_structlog() -> None:
    """Configure structlog for the application."""
    # Determine if we're in development or production
    is_development = os.getenv("APP_ENV", "development") == "development"

    # Determine log level from environment
    log_level = os.getenv("LOG_LEVEL")
    if not log_level:
        # Default: DEBUG in development, INFO in production
        log_level = "DEBUG" if is_development else "INFO"

    log_level = log_level.upper()
    numeric_level = getattr(logging, log_level, logging.INFO)

    # Base processors that are always applied
    processors = [
        # Filter by log level
        structlog.stdlib.filter_by_level,
        # Add logger name
        structlog.stdlib.add_logger_name,
        # Add log level
        structlog.stdlib.add_log_level,
        # Add timestamp
        structlog.processors.TimeStamper(fmt="iso"),
        # Process stack info if present
        structlog.processors.StackInfoRenderer(),
        # Format exception info
        structlog.processors.format_exc_info,
        # Ensure unicode
        structlog.processors.UnicodeDecoder(),
    ]

    # Add environment-specific processors
    if is_development:
        # Development: colorized console output
        processors.append(structlog.dev.ConsoleRenderer(colors=True))
    else:
        # Production: JSON output for log aggregation
        processors.append(structlog.processors.JSONRenderer())

    # Configure standard library logging to be consistent
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=numeric_level,
    )

    # Set the root logger level to control all logging
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Silence noisy loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("passlib").setLevel(logging.WARNING)
    logging.getLogger("multipart").setLevel(logging.WARNING)

    # Set uvicorn access logs to WARNING to reduce noise
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        context_class=dict,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a configured structlog logger."""
    return structlog.get_logger(name)


def filter_sensitive_fields(
    logger: Any, method_name: str, event_dict: Dict[str, Any]
) -> Dict[str, Any]:
    """Processor to filter sensitive fields from log entries."""
    sensitive_patterns = [
        "password",
        "token",
        "secret",
        "key",
        "auth",
        "session",
        "cookie",
        "credential",
        "ssn",
        "phone",
        "email",
    ]

    def _filter_dict(data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively filter sensitive data from dictionary."""
        if not isinstance(data, dict):
            return data

        filtered = {}
        for key, value in data.items():
            key_lower = str(key).lower()

            # Check if key contains sensitive patterns
            if any(pattern in key_lower for pattern in sensitive_patterns):
                filtered[key] = "[FILTERED]"
            elif isinstance(value, dict):
                filtered[key] = _filter_dict(value)
            elif isinstance(value, list):
                filtered[key] = [
                    _filter_dict(item) if isinstance(item, dict) else item for item in value
                ]
            else:
                filtered[key] = value

        return filtered

    # Filter the entire event dict
    return _filter_dict(event_dict)
