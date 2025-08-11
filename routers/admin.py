"""Admin routes for privileged operations."""

from typing import List

from fastapi import APIRouter
from starlette import status

from config import db_dependency
from config import AdminUser
from exceptions import RecordNotFound
from models import Todo
from schemas import TodoResponse, ValidId, ERROR_RESPONSES

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get(
    "/todos",
    response_model=List[TodoResponse],
    status_code=status.HTTP_200_OK,
    responses=ERROR_RESPONSES,
    summary="Get all todos (admin only)",
    description="Retrieve all todos from all users. Requires admin privileges.",
)
async def get_all_todos(db: db_dependency, admin: AdminUser):
    """Get all todos (admin only)."""
    return db.query(Todo).all()


@router.delete(
    "/todos/{todo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=ERROR_RESPONSES,
    summary="Delete any todo (admin only)",
    description="Delete any todo by ID regardless of owner. Requires admin privileges.",
)
async def delete_todo(db: db_dependency, todo_id: ValidId, admin: AdminUser):
    """Delete any todo by ID (admin only)."""
    todo_model = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo_model is None:
        raise RecordNotFound("Todo not found")

    db.query(Todo).filter(Todo.id == todo_id).delete()
    db.commit()
