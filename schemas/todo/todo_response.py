"""Todo response schema."""

from pydantic import BaseModel


class TodoResponse(BaseModel):
    """Response model for todo operations."""

    id: int
    title: str
    description: str
    priority: int
    complete: bool
    owner_id: int

    class Config:
        from_attributes = True
