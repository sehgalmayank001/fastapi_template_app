"""Simple logging configuration."""

import os
from typing import List


class LoggingConfig:
    """Simple logging configuration."""

    @property
    def log_level(self) -> str:
        """Get log level from LOG_LEVEL env var or APP_ENV default."""
        return os.getenv("LOG_LEVEL", self._default_log_level()).upper()

    @property
    def filter_params(self) -> List[str]:
        """Get filter parameters based on environment (not configurable via env vars)."""
        return self._default_filter_params()

    def _default_log_level(self) -> str:
        """Default log level based on APP_ENV."""
        app_env = os.getenv("APP_ENV", "development").lower()
        return "INFO" if app_env == "production" else "DEBUG"

    def _default_filter_params(self) -> List[str]:
        """Filter parameters - same across all environments."""
        return [
            "passw",
            "secret",
            "token",
            "_key",
            "crypt",
            "salt",
            "certificate",
            "auth",
            "session",
            "cookie",
            "ssn",
            "phone_number",
        ]


# Global instance
logging_config = LoggingConfig()
