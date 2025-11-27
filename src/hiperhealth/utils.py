"""HiPerHealth utility functions."""

import datetime

from typing import Any


def is_float(value: str) -> bool:
    """Check if a string is a float."""
    if not value.isnumeric():
        try:
            float(value)
            return True
        except ValueError:
            return False
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
