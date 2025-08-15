"""Todo database configuration and session management for TodoApp."""

import os
import yaml
from jinja2 import Template
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


def load_todo_database_config():
    """Load todo database configuration from todo_database.yml with Jinja templating."""
    # Get current environment
    env = os.getenv("APP_ENV", "development")

    # Read todo_database.yml file
    config_path = os.path.join(os.path.dirname(__file__), "todo_database.yml")
    with open(config_path, "r", encoding="utf-8") as file:
        template_content = file.read()

    # Render Jinja template with environment variables
    template = Template(template_content)
    rendered_yaml = template.render(**os.environ)

    # Parse YAML
    config = yaml.safe_load(rendered_yaml)

    return config[env]


def get_todo_database_url(config):
    """Generate SQLAlchemy database URL from todo configuration."""
    # If url is provided, use it directly (takes precedence)
    if "url" in config and config["url"]:
        return config["url"]

    # Otherwise, build URL from individual components
    return (
        f"postgresql://{config['username']}:{config['password']}"
        f"@{config['host']}:{config['port']}/{config['database']}"
    )


def create_todo_database_engine():
    """Create SQLAlchemy engine for todo database with pool configuration from YAML."""
    config = load_todo_database_config()
    database_url = get_todo_database_url(config)

    # Extract pool configuration from YAML
    pool_size = int(config.get("pool", 5))
    timeout = int(config.get("timeout", 5000))

    return create_engine(
        database_url,
        pool_size=pool_size,
        pool_timeout=timeout / 1000,  # Convert milliseconds to seconds
        pool_recycle=3600,  # Recycle connections after 1 hour
    )


todo_engine = create_todo_database_engine()
TODO_SQLALCHEMY_DATABASE_URL = todo_engine.url

TodoSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=todo_engine)

TodoBase = declarative_base()
