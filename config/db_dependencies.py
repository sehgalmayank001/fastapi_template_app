"""Shared FastAPI dependencies for database access."""

from typing import Annotated, Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from .settings import settings


def get_db() -> Generator[Session, None, None]:
    """Yield a database session and ensure it is closed after use."""
    db = settings.session_local()
    try:
        yield db
    finally:
        db.close()


# Reusable dependency annotation for routes
db_dependency = Annotated[Session, Depends(get_db)]

__all__ = ["get_db", "db_dependency"]
