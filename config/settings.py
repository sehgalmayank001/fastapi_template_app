"""Application settings configuration."""

from typing import List
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings

from .database import load_database_config, get_database_url, engine, SessionLocal, Base


class Settings(BaseSettings):
    """Application settings with automatic environment variable loading."""

    class Config:
        """Pydantic configuration for Settings."""

        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Allow extra environment variables

    # Basic application settings
    app_env: str = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=False, alias="DEBUG")

    # Security settings
    secret_key: str = Field(
        default="197b2c37c391bed93fe80344fe73b806947a65e36206e05a1a23c2fa12702fe3",
        alias="SECRET_KEY",
    )
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=20, alias="ACCESS_TOKEN_EXPIRE_MINUTES")

    # Common error messages
    auth_failed_message: str = Field(default="Authentication Failed", alias="AUTH_FAILED_MESSAGE")
    user_validation_failed_message: str = Field(
        default="Could not validate user.", alias="USER_VALIDATION_FAILED_MESSAGE"
    )
    record_not_found_message: str = Field(
        default="Todo not found.", alias="RECORD_NOT_FOUND_MESSAGE"
    )

    @computed_field
    @property
    def database_url(self) -> str:
        """Generate database URL from YAML configuration."""
        db_config = load_database_config()
        return get_database_url(db_config)

    @computed_field
    @property
    def database_pool_size(self) -> int:
        """Get database pool size from YAML configuration."""
        db_config = load_database_config()
        return db_config.get("pool", 5)

    @computed_field
    @property
    def database_timeout(self) -> int:
        """Get database timeout from YAML configuration."""
        db_config = load_database_config()
        return db_config.get("timeout", 5000)

    @property
    def database_engine(self):
        """Get database engine from database module."""
        return engine

    @property
    def session_local(self):
        """Get session factory from database module."""
        return SessionLocal

    @property
    def base(self):
        """Get declarative base from database module."""
        return Base


# Global settings instance - loaded once, used everywhere
settings = Settings()
