"""Todo model for TodoApp."""

from sqlalchemy import Column, Integer, String, Boolean

from config import settings

TodoBase = settings.todo_base


class Todo(TodoBase):
    """Todo model representing user tasks."""

    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer)  # No foreign key since users are in different DB
