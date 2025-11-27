"""Zero-shot topic detection + Guardrails validator (no HTTP here)."""

from __future__ import annotations

import os

from functools import lru_cache
from typing import Any, Dict, List, Optional, Sequence, Tuple

from guardrails.classes.validation.validation_result import (
    FailResult as GRFailResult,
)
from guardrails.classes.validation.validation_result import (
    PassResult as GRPassResult,
)
from guardrails.validator_base import (
    ValidationResult,
    Validator,
    register_validator,
)
from transformers.pipelines import pipeline as hf_pipeline

from sdx.agents.hardware import _get_device_id  # 0 for CUDA, -1 for CPU

# Guardrails result compatibility
if not hasattr(GRPassResult, 'is_valid'):
    setattr(GRPassResult, 'is_valid', property(lambda self: True))
if not hasattr(GRFailResult, 'is_valid'):
    setattr(GRFailResult, 'is_valid', property(lambda self: False))
if not hasattr(GRPassResult, 'error_message'):
    setattr(GRPassResult, 'error_message', property(lambda self: None))

# in topic.py
_TOPIC_DETECTOR_MODEL = os.getenv(
    'TOPIC_DETECTOR_MODEL',
    'MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7',
)
_TOPIC_HYPOTHESIS_TEMPLATE = os.getenv(
    'TOPIC_HYPOTHESIS_TEMPLATE', 'This text contains {}.'
)
_GUARD_FAIL_CLOSED = os.getenv('TOPIC_GUARD_FAIL_CLOSED', '1') != '0'
_MAX_SEQ_CHARS = int(os.getenv('TOPIC_GUARD_MAX_CHARS', '4000'))


@lru_cache(maxsize=1)
def _get_topic_classifier() -> Any:
    return hf_pipeline(
        'zero-shot-classification',
        model=_TOPIC_DETECTOR_MODEL,
        device=_get_device_id(),
    )


def detect_topics(
    text: str,
    labels: Sequence[str],
    *,
    threshold: float = 0.8,
    hypothesis_template: str = _TOPIC_HYPOTHESIS_TEMPLATE,
) -> List[Tuple[str, float]]:
    """Detect topics in text using zero-shot classification."""
    if not text or not labels:
        return []
    txt = text.strip()[:_MAX_SEQ_CHARS]
    dedup = list(dict.fromkeys(s.strip() for s in labels if s.strip()))
    if not txt or not dedup:
        return []
    try:
        result: Dict[str, List[Any]] = _get_topic_classifier()(
            txt,
            dedup,
            multi_label=True,
            hypothesis_template=hypothesis_template,
            truncation=True,
        )
    except Exception:
        return [('guard_error', 1.0)] if _GUARD_FAIL_CLOSED else []
    hits: List[Tuple[str, float]] = []
    for lbl, sc in zip(result['labels'], result['scores']):
        score = float(sc)
        if score >= float(threshold):
            hits.append((str(lbl), score))
    hits.sort(key=lambda x: x[1], reverse=True)
    return hits


@register_validator(name='constrain_topic', data_type='string')
class ConstrainTopic(Validator):
    """Fail if text matches any banned topic above a threshold."""

    def __init__(
        self,
        banned_topics: Optional[List[str]] = None,
        threshold: float = 0.8,
        hypothesis_template: Optional[str] = None,
        *,
        on_fail: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.banned_topics: List[str] = banned_topics or [
            'encouraging self-harm',
            'explicit violent threat',
            'harassment with violent intent',
            'suicide instructions',
            'medical dosing advice',
        ]
        self.threshold: float = float(threshold)
        self.hypothesis_template: str = (
            hypothesis_template or _TOPIC_HYPOTHESIS_TEMPLATE
        )
        self.on_fail: str = str(
            on_fail or os.getenv('SDX_VALIDATOR_ON_FAIL') or 'exception'
        )

    def _validate(
        self,
        value: str,
        metadata: Optional[Dict[str, str]] = None,
    ) -> ValidationResult:
        del metadata
        text = (value or '').strip()
        if not text or not self.banned_topics:
            return GRPassResult()
        hits = detect_topics(
            text,
            self.banned_topics,
            threshold=self.threshold,
            hypothesis_template=self.hypothesis_template,
        )
        if hits and hits[0][0] == 'guard_error':
            return GRFailResult(error_message='Topic guard unavailable/error.')
        if hits:
            detail = ', '.join(f'{lbl}:{s:.2f}' for lbl, s in hits)
            return GRFailResult(
                error_message=f'Banned topics detected → {detail}'
            )
        return GRPassResult()


__all__ = ['ConstrainTopic', 'detect_topics']
