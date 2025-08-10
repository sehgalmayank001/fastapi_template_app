# FastAPI TodoApp - Production-Ready Template

A comprehensive FastAPI application template showcasing modern Python web development patterns, clean architecture, and production-ready features.

## 🚀 Features

- **Clean Architecture**: Domain-driven design with organized schemas, models, and routers
- **Authentication & Authorization**: JWT-based auth with middleware and decorators
- **Database Integration**: PostgreSQL with SQLAlchemy ORM and Alembic migrations
- **RESTful API Design**: Resource-based URLs with proper HTTP methods and status codes
- **Comprehensive Documentation**: Auto-generated OpenAPI docs with detailed responses
- **Exception Handling**: Centralized error handling with custom exceptions
- **Configuration Management**: Environment-based config with YAML and Jinja templating
- **Code Quality**: Pylint, isort, and comprehensive linting setup
- **Caching**: Request-level user caching for optimal performance
- **Middleware**: Custom authentication middleware for seamless user injection

## 📁 Project Structure

```
TodoApp/
├── main.py                 # FastAPI application entry point
├── config/                 # Configuration and dependencies
│   ├── __init__.py        # Centralized exports
│   ├── settings.py        # Pydantic settings with env support
│   ├── database.py        # Database connection and session management
│   ├── database.yml       # Environment-specific DB configuration
│   ├── db_dependencies.py # Database dependency injection
│   ├── auth_middleware.py # Authentication middleware
│   ├── auth_helpers.py    # Authentication decorators and helpers
│   ├── api_response.py    # JSON response utilities
│   ├── rescue.py          # Global exception handlers
│   └── alembic.ini        # Alembic migration configuration
├── models/                # SQLAlchemy models (one per file)
│   ├── __init__.py
│   ├── user.py           # User model
│   └── todo.py           # Todo model
├── schemas/               # Pydantic schemas (domain-organized)
│   ├── __init__.py        # Main schema exports
│   ├── auth/              # Authentication schemas
│   │   ├── create_user_request.py
│   │   └── token.py
│   ├── todo/              # Todo domain schemas
│   │   ├── todo_request.py
│   │   └── todo_response.py
│   ├── user/              # User domain schemas
│   │   ├── user_response.py
│   │   └── user_verification.py
│   └── common/            # Shared validation and error schemas
│       ├── common.py      # ValidId, ERROR_RESPONSES
│       └── error_response.py
├── exceptions/            # Custom exception classes
│   ├── __init__.py
│   ├── api_exception.py   # Base exception
│   ├── record_not_found.py
│   ├── not_authorized.py
│   └── record_invalid.py
├── routers/               # API route modules
│   ├── __init__.py
│   ├── auth.py           # Authentication endpoints
│   ├── todos.py          # Todo CRUD operations
│   ├── users.py          # User account management
│   └── admin.py          # Admin-only operations
├── db/                    # Alembic migrations
│   ├── env.py
│   └── versions/
├── migrate.py            # Migration wrapper script
├── .env                  # Environment variables
├── requirements.txt      # Python dependencies
└── pyproject.toml       # Tool configuration
```

## 🛠️ Setup and Installation

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- pip or poetry

### 1. Clone and Setup

```bash
git clone <repository-url>
cd TodoApp
pip install -r requirements.txt
```

### 2. Environment Configuration

Create `.env` file:

```bash
cp env.example .env
```

Configure your environment variables:

```env
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/todosapp_development
DB_NAME=todosapp_development
DB_USERNAME=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Security
SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=20

# Application
APP_ENV=development
DEBUG=true
```

### 3. Database Setup

```bash
# Run migrations
python migrate.py upgrade head

# Or create new migration
python migrate.py revision --autogenerate -m "Add new table"
```

### 4. Run the Application

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Visit `http://localhost:8000/docs` for interactive API documentation.

## 🔧 Key Patterns and Architecture

### Configuration Management

**Centralized Settings** with Pydantic BaseSettings:

```python
# config/settings.py
class Settings(BaseSettings):
    secret_key: str = Field(alias="SECRET_KEY")
    database_url: str = Field(computed=True)

    class Config:
        env_file = ".env"
```

**YAML-based Database Configuration** with Jinja templating:

```yaml
# config/database.yml
development:
  database: "{{ DB_NAME | default('app_development') }}"
  username: "{{ DB_USERNAME | default('') }}"
  url: "{{ DATABASE_URL | default('') }}"
```

### Authentication System

**Middleware-based Authentication**:

```python
# Automatic user injection via middleware
app.add_middleware(AuthMiddleware)
```

**Decorator-based Authorization**:

```python
@router.get("/todos")
@authenticate_user  # Ensures user is logged in
async def get_todos(db: db_dependency):
    user = current_user()  # Get current user (cached)
    return db.query(Todos).filter(Todos.owner_id == user.id).all()

@router.get("/admin/users")
@admin_required  # Ensures user has admin role
async def get_all_users(db: db_dependency):
    return db.query(Users).all()
```

**Current User Helper** with caching:

```python
# Access authenticated user anywhere
user = current_user()  # Returns full User model object
print(user.id, user.username, user.email)  # Direct attribute access
```

### Schema Organization

**Domain-Driven Design** with hierarchical imports:

```python
# schemas/auth/create_user_request.py
class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')

# Usage in routers
from schemas import CreateUserRequest, TodoRequest, ValidId, ERROR_RESPONSES
```

### Exception Handling

**Custom Exception Classes**:

```python
# exceptions/not_authorized.py
class NotAuthorized(APIException):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, 401)
```

**Global Exception Handlers**:

```python
# Automatically converts exceptions to JSON responses
raise NotAuthorized("Invalid credentials")
# Returns: {"message": "Invalid credentials", "status_code": 401, "timestamp": "..."}
```

### API Documentation

**Comprehensive OpenAPI Documentation**:

```python
@router.post(
    "/todos",
    response_model=TodoResponse,
    status_code=status.HTTP_201_CREATED,
    responses=ERROR_RESPONSES,  # Reusable error responses
    summary="Create a new todo",
    description="Create a new todo item for the authenticated user.",
)
```

### Database Patterns

**Dependency Injection**:

```python
# config/db_dependencies.py
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
```

**Model Organization** (Single Responsibility Principle):

```python
# models/todo.py
class Todos(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
```

## 📊 API Endpoints

### Authentication

- `POST /auth/register` - User registration
- `POST /auth/login` - User login (returns JWT token)

### Todos

- `GET /todos/` - Get user's todos
- `POST /todos/` - Create new todo
- `GET /todos/{id}` - Get specific todo
- `PUT /todos/{id}` - Update todo
- `DELETE /todos/{id}` - Delete todo

### Users

- `GET /users/me` - Get current user profile
- `PUT /users/password` - Change password

### Admin

- `GET /admin/todos` - Get all todos (admin only)
- `DELETE /admin/todos/{id}` - Delete any todo (admin only)

## 🧪 Code Quality

### Linting Configuration

```toml
# pyproject.toml
[tool.pylint."MESSAGES CONTROL"]
disable = ["C0111", "R0903", "R0801", "W0511", "C0301"]

[tool.isort]
profile = "black"
known_first_party = ["config", "models", "routers", "schemas", "exceptions"]
```

### Import Organization

```python
# Standard library imports
from datetime import datetime
from typing import List, Optional

# Third-party imports (alphabetical)
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

# First-party imports (alphabetical)
from config import db_dependency, settings
from exceptions import NotAuthorized, RecordNotFound
from schemas import TodoRequest, ValidId, ERROR_RESPONSES
```

## 🔄 Database Migrations

### Create Migration

```bash
python migrate.py revision --autogenerate -m "Add user table"
```

### Run Migrations

```bash
python migrate.py upgrade head
```

### Migration History

```bash
python migrate.py history
```

## 🚀 Deployment

### Environment Variables

Set these in production:

```env
APP_ENV=production
DEBUG=false
SECRET_KEY=your-production-secret-key
DATABASE_URL=postgresql://user:pass@prod-db:5432/app_prod
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🎯 Best Practices Demonstrated

1. **Single Responsibility Principle**: One class per file, focused responsibilities
2. **Dependency Injection**: Clean separation of concerns
3. **Configuration Management**: Environment-based settings
4. **Error Handling**: Centralized exception management
5. **API Documentation**: Comprehensive OpenAPI specs
6. **Security**: JWT authentication with proper middleware
7. **Database**: Proper ORM usage with migrations
8. **Code Quality**: Linting, formatting, and import organization
9. **Caching**: Request-level optimizations
10. **RESTful Design**: Resource-based URLs and HTTP semantics

## 🤝 Contributing

1. Follow the established patterns and directory structure
2. Add docstrings to all modules, classes, and functions
3. Use type hints throughout
4. Write comprehensive tests for new features
5. Update documentation for any API changes

## 📝 License

This project serves as a template for FastAPI applications. Feel free to use it as a starting point for your own projects.

---

**Built with ❤️ using FastAPI, SQLAlchemy, and modern Python practices.**
