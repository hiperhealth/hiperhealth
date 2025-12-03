"""HiPerHealth utility functions."""

import datetime

from typing import Any


def is_float(value: str) -> bool:
    """Check if a string represents a decimal number (not a plain integer).

    Returns True for strings like '1.0', '-3.00', '0.02'.
    Returns False for plain integers like '1', '-2' or non-numeric strings.

    Args:
        value: The string to check

    Returns
    -------
        bool: True if string represents a decimal, False otherwise
    """
    value = value.strip()

    # Empty strings are not floats
    if not value:
        return False

    # Try to convert to float
    try:
        float(value)
    except ValueError:
        # Not a valid number at all
        return False

    # At this point, it's a valid number. Check if it's a plain integer.
    # Plain integers (like '1', '-2') should return False
    # Decimals (like '1.0', '-3.00') should return True
    if value.lstrip('-').isdigit():
        # It's a plain integer string (no decimal point)
        return False

    # It's a valid float-like string (has decimal point or scientific notation)
    return True


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
