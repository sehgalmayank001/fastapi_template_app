"""Todo CRUD routes."""

from typing import List

from fastapi import APIRouter
from starlette import status

from config import db_dependency
from config.auth_helpers import authenticate_user, current_user
from exceptions import RecordNotFound
from models import Todo
from schemas import TodoRequest, TodoResponse, ValidId, ERROR_RESPONSES

router = APIRouter(prefix="/todos", tags=["todos"])


@router.get(
    "/",
    response_model=List[TodoResponse],
    status_code=status.HTTP_200_OK,
    responses=ERROR_RESPONSES,
)
@authenticate_user
async def get_todos(db: db_dependency):
    """Get all todos for the current user."""
    user = current_user()
    return db.query(Todo).filter(Todo.owner_id == user.id).all()


@router.get(
    "/{todo_id}",
    response_model=TodoResponse,
    status_code=status.HTTP_200_OK,
    responses=ERROR_RESPONSES,
)
@authenticate_user
async def get_todo(db: db_dependency, todo_id: ValidId):
    """Get a specific todo by ID."""
    user = current_user()
    todo_model = db.query(Todo).filter(Todo.id == todo_id).filter(Todo.owner_id == user.id).first()
    if todo_model is not None:
        return todo_model
    raise RecordNotFound("Todo not found")


@router.post(
    "/",
    response_model=TodoResponse,
    status_code=status.HTTP_201_CREATED,
    responses=ERROR_RESPONSES,
)
@authenticate_user
async def create_todo(db: db_dependency, todo_request: TodoRequest):
    """Create a new todo."""
    user = current_user()
    todo_model = Todo(**todo_request.model_dump(), owner_id=user.id)

    db.add(todo_model)
    db.commit()
    db.refresh(todo_model)
    return todo_model


@router.put(
    "/{todo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=ERROR_RESPONSES,
)
@authenticate_user
async def update_todo(
    db: db_dependency,
    todo_request: TodoRequest,
    todo_id: ValidId,
):
    """Update an existing todo."""
    user = current_user()
    todo_model = db.query(Todo).filter(Todo.id == todo_id).filter(Todo.owner_id == user.id).first()
    if todo_model is None:
        raise RecordNotFound("Todo not found")

    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()


@router.delete(
    "/{todo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=ERROR_RESPONSES,
)
@authenticate_user
async def delete_todo(db: db_dependency, todo_id: ValidId):
    """Delete a todo."""
    user = current_user()
    todo_model = db.query(Todo).filter(Todo.id == todo_id).filter(Todo.owner_id == user.id).first()
    if todo_model is None:
        raise RecordNotFound("Todo not found")
    db.query(Todo).filter(Todo.id == todo_id).filter(Todo.owner_id == user.id).delete()

    db.commit()
