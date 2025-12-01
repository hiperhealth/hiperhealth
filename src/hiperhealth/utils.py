"""HiPerHealth utility functions."""

import datetime

from typing import Any


def is_float(value: str) -> bool:
    """Check if a string represents a float (not a plain integer)."""
    value = value.strip()
    try:
        # Reject plain integers (e.g., '1', '-2')
        if value == '' or value.isnumeric() or (value.lstrip('-').isnumeric()):
            return False
        float(value)
        return True
    except ValueError:
        return False


def make_json_serializable(obj: Any) -> Any:
    """Convert objects to JSON-serializable format recursively."""
    if isinstance(obj, dict):
        return {k: make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_serializable(item) for item in obj]
    elif isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    else:
        return obj
