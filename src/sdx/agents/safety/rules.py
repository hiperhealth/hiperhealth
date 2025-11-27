"""Safety prompt rails for clinical agents."""

SAFETY_SYSTEM_PROMPT = (
    'Safety rules: Do not provide treatment plans, medication dosages, or '
    'Do not provide step-by-step procedures. '
    'No instructions for self-harm or harming others. '
    'Be non-prescriptive and probabilistic. Only list non-actionable '
    'differential options.'
)


def with_safety(base: str) -> str:
    """Append safety rails to a base system prompt."""
    return f'{base}\n\n{SAFETY_SYSTEM_PROMPT}'.strip()
