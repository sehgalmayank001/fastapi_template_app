"""Shared FastAPI dependencies for todo database access."""

from typing import Annotated, Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from .settings import settings


def get_todo_db() -> Generator[Session, None, None]:
    """Yield a todo database session and ensure it is closed after use."""
    db = settings.todo_session_local()
    try:
        yield db
    finally:
        db.close()


# Reusable dependency annotation for todo routes
todo_db_dependency = Annotated[Session, Depends(get_todo_db)]

__all__ = ["get_todo_db", "todo_db_dependency"]
