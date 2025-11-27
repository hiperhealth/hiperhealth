"""Safety utilities for agent outputs and prompts."""

from __future__ import annotations

import os

from typing import TYPE_CHECKING

from fastapi import HTTPException

from .rules import SAFETY_SYSTEM_PROMPT, with_safety
from .topic import ConstrainTopic, detect_topics

if TYPE_CHECKING:
    from sdx.schema.clinical_outputs import LLMDiagnosis

_DEFAULT_BANNED = [
    'encouraging self-harm',
    'explicit violent threat',
    'harassment with violent intent',
    'suicide instructions',
    'medical dosing advice',
]


def _env_banned_topics() -> list[str]:
    raw = os.getenv('TOPIC_GUARD_BANNED', '')
    labels = [s.strip() for s in raw.split(';') if s.strip()]
    return labels or list(_DEFAULT_BANNED)


TOPIC_GUARD_ENABLED = os.getenv('TOPIC_GUARD_ENABLED', '1') != '0'
TOPIC_GUARD_THRESHOLD = float(os.getenv('TOPIC_GUARD_THRESHOLD', '0.8'))
TOPIC_GUARD_BANNED = _env_banned_topics()

_TOPIC_VALIDATOR = ConstrainTopic(
    banned_topics=TOPIC_GUARD_BANNED,
    threshold=TOPIC_GUARD_THRESHOLD,
)


def _enforce_topic_safety(obj: 'LLMDiagnosis') -> None:
    """Raise HTTP 400 if LLM output violates topic policy."""
    if not TOPIC_GUARD_ENABLED:
        return
    combined = f'{obj.summary}\n' + '\n'.join(obj.options or [])
    result = _TOPIC_VALIDATOR.validate(combined, metadata=None)
    if getattr(result, 'outcome', '') == 'fail':
        msg = getattr(result, 'error_message', 'Banned topics detected.')
        raise HTTPException(400, f'Unsafe LLM output blocked: {msg}')


__all__ = [
    'SAFETY_SYSTEM_PROMPT',
    'ConstrainTopic',
    '_enforce_topic_safety',
    'detect_topics',
    'with_safety',
]
