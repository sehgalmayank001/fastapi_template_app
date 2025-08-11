"""FastAPI TodoApp main application entry point."""

from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer

from config import setup_exception_handlers, RequestLoggingMiddleware
from routers import auth, todos, admin, users
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="FastAPI Todo App",
    description="A comprehensive todo application with JWT authentication",
    version="1.0.0",
)

# Configure OAuth2 security scheme for Swagger UI
# This tells Swagger UI to use the /auth/login endpoint for authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Add request logging middleware (logs all requests/responses with filtering)
app.add_middleware(RequestLoggingMiddleware)

# Setup exception handlers
setup_exception_handlers(app)

# Tables are managed by Alembic migrations
# settings.base.metadata.create_all(bind=settings.database_engine)

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)
