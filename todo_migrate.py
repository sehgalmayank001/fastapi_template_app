#!/usr/bin/env python3
"""Todo database migration wrapper for Alembic commands."""

import subprocess
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set the config file path for todo database
config_path = "config/todo_alembic.ini"


def run_alembic_command(args):
    """Run alembic command with the todo database configuration."""
    cmd = ["alembic", "-c", config_path] + args
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"Error running alembic: {e}", file=sys.stderr)
        print(e.stdout)
        print(e.stderr, file=sys.stderr)
        return e.returncode


def main():
    """Main entry point for todo migration commands."""
    if len(sys.argv) < 2:
        print("Usage: python todo_migrate.py <alembic_command> [args...]")
        print("Examples:")
        print("  python todo_migrate.py revision --autogenerate -m 'Create todos table'")
        print("  python todo_migrate.py upgrade head")
        print("  python todo_migrate.py downgrade -1")
        print("  python todo_migrate.py history")
        print("  python todo_migrate.py current")
        sys.exit(1)

    # Pass all arguments except the script name to alembic
    alembic_args = sys.argv[1:]
    exit_code = run_alembic_command(alembic_args)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
