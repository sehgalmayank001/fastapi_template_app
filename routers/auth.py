"""Authentication routes and JWT token handling."""

from datetime import timedelta, datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from passlib.context import CryptContext
from starlette import status

from config import db_dependency, settings
from models import User
from schemas import CreateUserRequest, Token, ERROR_RESPONSES

router = APIRouter(prefix="/auth", tags=["auth"])

# Get security settings from centralized configuration
SECRET_KEY = settings.secret_key
ALGORITHM = settings.jwt_algorithm

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def authenticate_user(username: str, password: str, db):
    """Authenticate user with username and password."""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    """Create JWT access token for user."""
    encode = {"sub": username, "id": user_id, "role": role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    responses=ERROR_RESPONSES,
    summary="Register a new user",
    description="Create a new user account with username, email, and password.",
)
async def register_user(db: db_dependency, create_user_request: CreateUserRequest):
    """Register a new user account."""
    create_user_model = User(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        is_active=True,
    )

    db.add(create_user_model)
    db.commit()


@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    responses=ERROR_RESPONSES,
    summary="User login",
    description="Authenticate user and return JWT access token.",
)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    """Login and get access token."""
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=settings.user_validation_failed_message,
        )
    token = create_access_token(
        user.username,
        user.id,
        user.role,
        timedelta(minutes=settings.access_token_expire_minutes),
    )

    return {"access_token": token, "token_type": "bearer"}
