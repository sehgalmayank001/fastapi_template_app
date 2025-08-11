"""Logging helper functions for parameter filtering and message formatting."""

import json
import re
from typing import Any, Dict, List


def filter_sensitive_data(data: Any, filter_params: List[str]) -> Any:
    """
    Recursively filter sensitive parameters from data structures.
    Similar to Rails' filter_parameters functionality.

    Args:
        data: The data to filter (dict, list, or primitive)
        filter_params: List of parameter names to redact

    Returns:
        Filtered data with sensitive values replaced with [FILTERED]
    """
    if data is None:
        return None

    if isinstance(data, dict):
        return _filter_dict(data, filter_params)
    elif isinstance(data, list):
        return [filter_sensitive_data(item, filter_params) for item in data]
    else:
        return data


def _filter_dict(data: Dict[str, Any], filter_params: List[str]) -> Dict[str, Any]:
    """Filter sensitive parameters from dictionary."""
    filtered = {}

    for key, value in data.items():
        if _should_filter_key(key, filter_params):
            filtered[key] = "[FILTERED]"
        elif isinstance(value, dict):
            filtered[key] = _filter_dict(value, filter_params)
        elif isinstance(value, list):
            filtered[key] = [filter_sensitive_data(item, filter_params) for item in value]
        else:
            filtered[key] = value

    return filtered


def _should_filter_key(key: str, filter_params: List[str]) -> bool:
    """
    Check if a key should be filtered based on filter_params.
    Supports exact matches and partial matches (case-insensitive).
    """
    key_lower = key.lower()

    for filter_param in filter_params:
        filter_param_lower = filter_param.lower()

        # Exact match
        if key_lower == filter_param_lower:
            return True

        # Partial match - key contains filter param
        if filter_param_lower in key_lower:
            return True

        # Pattern match - filter param contains wildcards
        if "*" in filter_param_lower:
            pattern = filter_param_lower.replace("*", ".*")
            if re.match(f"^{pattern}$", key_lower):
                return True

    return False


def filter_headers(headers: Dict[str, str], filter_params: List[str]) -> Dict[str, str]:
    """Filter sensitive headers specifically."""
    # Common sensitive headers to always filter
    always_filter = ["authorization", "cookie", "set-cookie", "x-api-key", "x-auth-token"]
    combined_filters = filter_params + always_filter

    return _filter_dict(headers, combined_filters)


def filter_query_params(params: Dict[str, Any], filter_params: List[str]) -> Dict[str, Any]:
    """Filter sensitive query parameters."""
    return _filter_dict(params, filter_params)


def format_log_message(message_type: str, data: Dict[str, Any], filter_params: List[str]) -> str:
    """
    Format a comprehensive log message with filtered sensitive data.

    Args:
        message_type: Type of message (e.g., "INCOMING REQUEST", "OUTGOING RESPONSE")
        data: Dictionary of data to log
        filter_params: List of parameters to filter

    Returns:
        Formatted log message string
    """
    # Filter sensitive data
    filtered_data = filter_sensitive_data(data, filter_params)

    # Special handling for headers
    if "headers" in filtered_data:
        filtered_data["headers"] = filter_headers(filtered_data["headers"], filter_params)

    # Special handling for query params
    if "query_params" in filtered_data:
        filtered_data["query_params"] = filter_query_params(
            filtered_data["query_params"], filter_params
        )

    # Format the message
    try:
        formatted_data = json.dumps(filtered_data, indent=2, default=str)
    except (TypeError, ValueError):
        # Fallback to string representation if JSON serialization fails
        formatted_data = str(filtered_data)

    return f"{message_type}:\n{formatted_data}"


def get_client_info(request) -> Dict[str, Any]:
    """Extract client information from request for logging."""
    client_info = {
        "ip": None,
        "user_agent": None,
        "referer": None,
    }

    if hasattr(request, "client") and request.client:
        client_info["ip"] = request.client.host

    if hasattr(request, "headers"):
        headers = request.headers
        client_info["user_agent"] = headers.get("user-agent")
        client_info["referer"] = headers.get("referer")

        # Handle X-Forwarded-For for proxied requests
        forwarded_for = headers.get("x-forwarded-for")
        if forwarded_for:
            # Take the first IP in the chain
            client_info["ip"] = forwarded_for.split(",")[0].strip()

        # Handle X-Real-IP
        real_ip = headers.get("x-real-ip")
        if real_ip:
            client_info["ip"] = real_ip

    return client_info


def sanitize_url(url: str, filter_params: List[str]) -> str:
    """
    Sanitize URL by filtering sensitive query parameters.

    Args:
        url: The URL to sanitize
        filter_params: List of parameters to filter

    Returns:
        URL with sensitive query parameters replaced with [FILTERED]
    """
    if "?" not in url:
        return url

    base_url, query_string = url.split("?", 1)

    # Parse query parameters
    params = {}
    for param in query_string.split("&"):
        if "=" in param:
            key, value = param.split("=", 1)
            params[key] = value
        else:
            params[param] = ""

    # Filter sensitive parameters
    filtered_params = filter_query_params(params, filter_params)

    # Rebuild query string
    filtered_query_parts = []
    for key, value in filtered_params.items():
        if value:
            filtered_query_parts.append(f"{key}={value}")
        else:
            filtered_query_parts.append(key)

    if filtered_query_parts:
        return f"{base_url}?{'&'.join(filtered_query_parts)}"
    else:
        return base_url


def truncate_large_data(data: Any, max_length: int = 1000) -> Any:
    """
    Truncate large data structures to prevent log bloat.

    Args:
        data: Data to potentially truncate
        max_length: Maximum string length before truncation

    Returns:
        Truncated data if necessary
    """
    if isinstance(data, str) and len(data) > max_length:
        return data[:max_length] + f"... [TRUNCATED - {len(data)} total chars]"
    elif isinstance(data, (list, tuple)) and len(data) > 10:
        return list(data[:10]) + [f"... [TRUNCATED - {len(data)} total items]"]
    elif isinstance(data, dict) and len(data) > 20:
        items = list(data.items())[:20]
        truncated = dict(items)
        truncated["..."] = f"[TRUNCATED - {len(data)} total keys]"
        return truncated

    return data
