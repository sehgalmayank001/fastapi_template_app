"""API response helpers."""

from datetime import datetime, timezone
from typing import Any, Dict

from fastapi.responses import JSONResponse


def json_response(
    data: Dict[str, Any],
    status: int = 200,
    options: Dict = None,
):
    """json_response helper."""
    if options is None:
        options = {}

    # Add timestamp to all responses
    response_data = {**data, "timestamp": datetime.now(timezone.utc).isoformat()}

    return JSONResponse(content=response_data, status_code=status)
