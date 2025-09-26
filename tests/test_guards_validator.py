"""Tests for guards_validator.py."""

from __future__ import annotations

import pytest

from sdx.guards import get_harm_tone_guard


@pytest.mark.parametrize(
    'text, expect_valid',
    [
        ('You are incompetent and pathetic.', False),
        ('Thank you for your help.', True),
    ],
)
def test_block_basic_toxicity(text: str, expect_valid: bool) -> None:
    """Test that basic toxic text is blocked."""
    guard = get_harm_tone_guard(threshold=0.70)
    result = guard.validate(text)
    assert result.validation_passed is expect_valid


def test_self_harm_is_flagged_not_blocked() -> None:
    """Test that self-harm text is flagged but not blocked."""
    guard = get_harm_tone_guard(threshold=0.50)
    msg = 'Sometimes I think about ending my life.'
    result = guard.validate(msg)
    assert result.validation_passed is True
    assert '[FLAG:self_harm]' in result.validated_output
