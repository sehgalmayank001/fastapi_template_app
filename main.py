"""FastAPI TodoApp main application entry point."""

from fastapi import FastAPI

from config import setup_exception_handlers, AuthMiddleware
from routers import auth, todos, admin, users
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Add authentication middleware (automatically injects user)
app.add_middleware(AuthMiddleware)

# Setup exception handlers
setup_exception_handlers(app)

# Tables are managed by Alembic migrations
# settings.base.metadata.create_all(bind=settings.database_engine)

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)
