#!/usr/bin/env python3
"""Database migration helper script for TodoApp."""

import sys
import subprocess
from pathlib import Path


def run_alembic_command(args):
    """Run alembic command with the correct config file."""
    config_path = Path(__file__).parent / "config" / "alembic.ini"
    cmd = ["alembic", "-c", str(config_path)] + args
    return subprocess.run(cmd, check=False)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python migrate.py <alembic_command>")
        print("Examples:")
        print("  python migrate.py current")
        print("  python migrate.py upgrade head")
        print("  python migrate.py revision --autogenerate -m 'Description'")
        return

    args = sys.argv[1:]
    result = run_alembic_command(args)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
