"""SDX utility functions."""


def is_float(value: str) -> bool:
    """Check if a string is a float."""
    if not value.isnumeric():
        try:
            float(value)
            return True
        except ValueError:
            return False
    return False
