"""Tests for client guard integration."""

from __future__ import annotations

import pytest

from fastapi import HTTPException
from sdx.schema.clinical_outputs import LLMDiagnosis


@pytest.mark.hf
@pytest.mark.integration
def test_client_output_guard_blocks_unsafe_text(reload_client_module):
    """Test that unsafe text is blocked."""
    # Lower the threshold to make the test robust across HF backends.
    client = reload_client_module(
        TOPIC_GUARD_ENABLED='1',
        TOPIC_GUARD_THRESHOLD='0.5',
        TOPIC_GUARD_BANNED=(
            'medical dosing advice;'
            'explicit violent threat;'
            'suicide instructions'
        ),
    )

    obj = LLMDiagnosis(summary='Take 500 mg tid for 7 days.', options=['Flu'])

    with pytest.raises(HTTPException) as excinfo:
        client._assert_output_is_safe(obj)  # type: ignore[attr-defined]
    assert excinfo.value.status_code == 400


@pytest.mark.hf
@pytest.mark.integration
def test_client_output_guard_allows_harmless_text(reload_client_module):
    """Test that harmless text is allowed."""
    client = reload_client_module(
        TOPIC_GUARD_ENABLED='1',
        TOPIC_GUARD_THRESHOLD='0.8',
        TOPIC_GUARD_BANNED=(
            'medical dosing advice;'
            'explicit violent threat;'
            'suicide instructions'
        ),
    )

    from sdx.schema.clinical_outputs import LLMDiagnosis

    obj = LLMDiagnosis(
        summary='Symptoms are consistent with a viral illness; '
        'recommend clinical evaluation.',
        options=['Viral URTI', 'Allergic rhinitis'],
    )

    # Should NOT raise
    client._assert_output_is_safe(obj)  # type: ignore[attr-defined]


def test_env_banned_topics_parser_works(reload_client_module):
    """Test that the environment variable parser works for banned topics."""
    client = reload_client_module(TOPIC_GUARD_BANNED='a;; b ; ;c')
    # private helper but stable enough for unit test
    parsed = client._env_banned_topics()  # type: ignore[attr-defined]
    assert parsed == ['a', 'b', 'c']
