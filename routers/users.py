"""User account routes."""

from fastapi import APIRouter
from passlib.context import CryptContext
from starlette import status

from config import db_dependency, CurrentUser
from exceptions import NotAuthorized
from models import User
from schemas import UserVerification, UserResponse, ERROR_RESPONSES

router = APIRouter(prefix="/users", tags=["users"])
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    responses=ERROR_RESPONSES,
    summary="Get current user profile",
    description="Retrieve the current authenticated user's profile information.",
)
async def get_current_user_info(db: db_dependency, user: CurrentUser):
    """Get current user information."""
    return db.query(User).filter(User.id == user.id).first()


@router.put(
    "/me/password",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=ERROR_RESPONSES,
    summary="Change user password",
    description="Update the current user's password. Requires current password verification.",
)
async def change_password(
    db: db_dependency,
    user_verification: UserVerification,
    user: CurrentUser,
):
    """Change current user password."""
    user_model = db.query(User).filter(User.id == user.id).first()
    if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
        raise NotAuthorized("Current password is incorrect")

    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()
