"""Authentication helpers - FastAPI dependencies for JWT authentication."""

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from jose import jwt, JWTError

from models import User
from .database import SessionLocal
from .settings import settings

# OAuth2 security scheme for Swagger UI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user_dependency(token: str = Depends(oauth2_scheme)) -> User:
    """FastAPI dependency to get current authenticated user."""
    try:
        # Decode JWT token directly (no middleware needed)
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        user_id = payload.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")

    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Could not validate credentials") from exc

    # Fetch user from database
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    finally:
        db.close()


def get_admin_user_dependency(token: str = Depends(oauth2_scheme)) -> User:
    """FastAPI dependency to get current authenticated admin user."""
    user = get_current_user_dependency(token)
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


# Type aliases for easier use in route handlers
CurrentUser = Annotated[User, Depends(get_current_user_dependency)]
AdminUser = Annotated[User, Depends(get_admin_user_dependency)]

