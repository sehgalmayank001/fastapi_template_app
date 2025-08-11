# FastAPI TodoApp - Production-Ready Template

A comprehensive FastAPI application template showcasing modern Python web development patterns, clean architecture, and production-ready features.

## 🚀 Features

- **Clean Architecture**: Domain-driven design with organized schemas, models, and routers
- **OAuth2 Authentication**: JWT-based auth with FastAPI dependency injection and Swagger UI integration
- **Database Integration**: PostgreSQL with SQLAlchemy ORM and Alembic migrations
- **RESTful API Design**: Resource-based URLs with proper HTTP methods and status codes
- **Comprehensive Documentation**: Auto-generated OpenAPI docs with OAuth2 password flow
- **Exception Handling**: Centralized error handling with custom exceptions
- **Configuration Management**: Environment-based config with YAML and Jinja templating
- **Request Logging**: Comprehensive request/response logging with parameter filtering
- **Code Quality**: Pylint, isort, and comprehensive linting setup
- **Performance Optimized**: Single JWT decode per request, no redundant middleware

## 📁 Project Structure

```
fastapi_template_app/
├── main.py                 # FastAPI application entry point
├── config/                 # Configuration and dependencies
│   ├── __init__.py        # Centralized exports
│   ├── settings.py        # Pydantic settings with env support
│   ├── database.py        # Database connection and session management
│   ├── database.yml       # Environment-specific DB configuration
│   ├── db_dependencies.py # Database dependency injection
│   ├── auth_helpers.py    # OAuth2 authentication dependencies
│   ├── logging_middleware.py # Request logging middleware
│   ├── logging_helpers.py # Logging utilities and parameter filtering
│   ├── logging_config.py  # Logging configuration and filter parameters
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
cd fastapi_template_app
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

## 🔐 Authentication System

### OAuth2 Password Bearer with Swagger UI

The application uses **FastAPI dependency injection** for authentication with full Swagger UI integration:

```python
# OAuth2 security scheme for Swagger UI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
```

**Features:**

- **Swagger UI Integration**: Users can login with username/password directly in docs
- **JWT Token Processing**: Single decode per request for optimal performance
- **Type-Safe Dependencies**: Full type hints for authenticated users
- **No Middleware**: Clean, dependency-based approach

### Authentication Dependencies

Use these pre-defined type aliases in route handlers:

```python
from config import CurrentUser, AdminUser

# Regular authenticated user
@router.get("/protected")
async def protected_route(user: CurrentUser):
    # user is automatically injected and validated
    return {"user_id": user.id, "username": user.username}

# Admin-only route
@router.delete("/admin-only/{item_id}")
async def admin_route(item_id: int, admin: AdminUser):
    # admin user is automatically injected and role-checked
    pass
```

### Login Endpoint

Login endpoints use `OAuth2PasswordRequestForm` for Swagger compatibility:

```python
@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: db_dependency
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(user.username, user.id, user.role, expires_delta)
    return {"access_token": token, "token_type": "bearer"}
```

### Authentication Flow

1. **User Login**: POST to `/auth/login` with username/password
2. **Token Generation**: Server returns JWT token
3. **Swagger UI**: Users can authenticate directly in docs interface
4. **Protected Routes**: Dependencies automatically validate JWT and fetch user
5. **Role-Based Access**: Admin routes check user role automatically

## 🛠️ Key Patterns and Architecture

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

### Request Logging System

**Comprehensive Request/Response Logging** with parameter filtering:

```python
# Automatically logs all requests/responses with sensitive data filtered
app.add_middleware(RequestLoggingMiddleware)
```

**Simple Environment-Based Logging**:

```python
# config/logging_config.py - Simple and clean
class LoggingConfig:
    @property
    def log_level(self) -> str:
        """LOG_LEVEL env var or APP_ENV default."""
        return os.getenv("LOG_LEVEL", self._default_log_level()).upper()

    @property
    def filter_params(self) -> List[str]:
        """Rails-style filter parameters (same across all environments)."""
        return [
            "passw", "secret", "token", "_key", "crypt", "salt", "certificate",
            "auth", "session", "cookie", "ssn", "phone_number"
        ]
```

**Example Log Output**:

```json
{
  "method": "POST",
  "url": "https://api.example.com/auth/login",
  "headers": {
    "authorization": "[FILTERED]",
    "content-type": "application/x-www-form-urlencoded"
  },
  "body": "<FORM_DATA_SKIPPED_FOR_COMPATIBILITY>",
  "process_time_ms": 45.67
}
```

**Features**:

- **Rails-style pattern matching** - "passw" matches password, user_password, etc.
- **Sensible defaults** - essential filter patterns, INFO in prod, DEBUG in dev
- **Automatic filtering** of sensitive parameters in headers and URLs
- **Performance timing** - includes request processing time
- **Form data compatibility** - doesn't interfere with OAuth2PasswordRequestForm

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
- `POST /auth/login` - User login (OAuth2 password flow, returns JWT token)

### Todos

- `GET /todos/` - Get user's todos (requires authentication)
- `POST /todos/` - Create new todo (requires authentication)
- `GET /todos/{id}` - Get specific todo (requires authentication)
- `PUT /todos/{id}` - Update todo (requires authentication)
- `DELETE /todos/{id}` - Delete todo (requires authentication)

### Users

- `GET /users/me` - Get current user profile (requires authentication)
- `PUT /users/password` - Change password (requires authentication)

### Admin

- `GET /admin/todos` - Get all todos (requires admin role)
- `DELETE /admin/todos/{id}` - Delete any todo (requires admin role)

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
from config import db_dependency, settings, CurrentUser, AdminUser
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

1. **OAuth2 Integration**: Full Swagger UI authentication support
2. **Dependency Injection**: Clean separation of concerns with FastAPI dependencies
3. **Performance Optimization**: Single JWT decode per request
4. **Type Safety**: Full type hints for authenticated users
5. **Configuration Management**: Environment-based settings
6. **Error Handling**: Centralized exception management with proper HTTP status codes
7. **API Documentation**: Comprehensive OpenAPI specs with OAuth2 flow
8. **Security**: JWT authentication with proper error chaining
9. **Database**: Proper ORM usage with migrations
10. **Code Quality**: Linting, formatting, and import organization
11. **RESTful Design**: Resource-based URLs and HTTP semantics
12. **Clean Architecture**: No redundant middleware, pure dependency injection

## 🔐 Authentication Benefits

- **Performance**: No duplicate JWT parsing or middleware overhead
- **Simplicity**: No middleware state management or context variables
- **Type Safety**: Full type hints for authenticated users in route handlers
- **Swagger Integration**: Automatic OAuth2 password flow in documentation
- **Testability**: Easy to mock authentication dependencies in tests
- **Error Handling**: Proper HTTP exceptions with chained error context

## 🤝 Contributing

1. Follow the established patterns and directory structure
2. Use dependency injection for authentication (no middleware)
3. Add docstrings to all modules, classes, and functions
4. Use type hints throughout
5. Write comprehensive tests for new features
6. Update documentation for any API changes

## 📝 License

This project serves as a template for FastAPI applications. Feel free to use it as a starting point for your own projects.

---

**Built with ❤️ using FastAPI, OAuth2, SQLAlchemy, and modern Python practices.**
