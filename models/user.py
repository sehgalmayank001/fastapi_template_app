"""User model for TodoApp."""

from sqlalchemy import Column, Integer, String, Boolean

from config import settings

Base = settings.base


class User(Base):
    """User model representing application users."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String)
