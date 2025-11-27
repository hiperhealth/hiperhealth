"""Tests for topic_guard.py."""

from __future__ import annotations

import pytest

from sdx.agents.safety.topic_guard import (
    ConstrainTopic,
    detect_topics,
)


def test_detect_topics_empty_inputs_returns_empty():
    """Test that detect_topics returns empty list on empty inputs."""
    assert detect_topics('', ['x'], threshold=0.5) == []
    assert detect_topics('some text', [], threshold=0.5) == []


def test_validator_passes_for_harmless_text_fast_path():
    """Test that the validator passes on innocuous text."""
    validator = ConstrainTopic(threshold=0.99)
    # With a very high threshold, even if model later loads, this passes.
    result = validator.validate('Hello world. How are you?', metadata=None)
    assert getattr(result, 'outcome', None) == 'pass', getattr(
        result, 'error_message', ''
    )


@pytest.mark.hf
@pytest.mark.slow
def test_detect_topics_flags_violent_threat():
    """Test that detect_topics finds a banned topic in text."""
    text = 'Killing you would be doing the world a service.'
    labels = [
        'encouraging self-harm',
        'explicit violent threat',
        'harassment with violent intent',
    ]
    # Use a moderate threshold to reduce model variance across devices.
    hits = detect_topics(text, labels, threshold=0.5)
    assert hits, 'Expected at least one banned-topic hit.'
    top_label, top_score = hits[0]
    assert isinstance(top_label, str) and isinstance(top_score, float)


@pytest.mark.hf
@pytest.mark.slow
def test_constrain_topic_fails_on_dosing_language():
    """Test that the validator fails on text with banned topics."""
    validator = ConstrainTopic(
        banned_topics=[
            'medical dosing advice',
            'suicide instructions',
            'explicit violent threat',
        ],
        threshold=0.5,
    )
    text = 'Start amoxicillin 500 mg tid for 7 days.'
    result = validator.validate(text)
    assert getattr(result, 'outcome', None) == 'fail'
    assert 'Banned topics detected' in (
        getattr(result, 'error_message', '') or ''
    )
