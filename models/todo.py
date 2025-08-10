"""Todo model for TodoApp."""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

from config import settings

Base = settings.base


class Todo(Base):
    """Todo model representing user tasks."""

    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
