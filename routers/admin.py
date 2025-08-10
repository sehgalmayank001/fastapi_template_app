"""Admin routes for privileged operations."""

from typing import List

from fastapi import APIRouter
from starlette import status

from config import db_dependency
from config.auth_helpers import admin_required
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
@admin_required
async def get_all_todos(db: db_dependency):
    """Get all todos (admin only)."""
    return db.query(Todo).all()


@router.delete(
    "/todos/{todo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=ERROR_RESPONSES,
    summary="Delete any todo (admin only)",
    description="Delete any todo by ID regardless of owner. Requires admin privileges.",
)
@admin_required
async def delete_todo(db: db_dependency, todo_id: ValidId):
    """Delete any todo by ID (admin only)."""
    todo_model = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo_model is None:
        raise RecordNotFound("Todo not found")

    db.query(Todo).filter(Todo.id == todo_id).delete()
    db.commit()
