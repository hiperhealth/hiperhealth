"""Topic-based guard for harmful or prescriptive content.

This module provides:
- A zero-shot topic detector using a lightweight MNLI model.
- A Guardrails validator ``ConstrainTopic`` that fails when banned
  topics are detected above a confidence threshold.

The detector is cached on first use for low-latency calls thereafter.
"""

from __future__ import annotations

import os

from functools import lru_cache
from typing import Any, Dict, List, Optional, Sequence, Tuple

try:
    import torch
except Exception:  # pragma: no cover
    torch = None  # type: ignore[assignment]

# Importing from pipelines avoids mypy attr export warnings.
from guardrails.validator_base import (
    FailResult,
    PassResult,
    ValidationResult,
    Validator,
    register_validator,
)
from transformers.pipelines import pipeline as hf_pipeline

_MODEL_NAME = os.getenv(
    'TOPIC_DETECTOR_MODEL',
    'typeform/distilbert-base-uncased-mnli',
)
_HYPOTHESIS_TEMPLATE = os.getenv(
    'TOPIC_HYPOTHESIS_TEMPLATE',
    'This text contains {}.',
)


def _select_device() -> int:
    """Return 0 for CUDA if available, else -1 (CPU)."""
    if (
        torch is not None
        and hasattr(torch, 'cuda')
        and torch.cuda.is_available()
    ):
        return 0
    return -1


@lru_cache(maxsize=1)
def _get_classifier() -> Any:
    """Create and cache the HF zero-shot classifier."""
    return hf_pipeline(
        task='zero-shot-classification',
        model=_MODEL_NAME,
        device=_select_device(),
    )


def detect_topics(
    text: str,
    labels: Sequence[str],
    *,
    threshold: float = 0.8,
    template: str = _HYPOTHESIS_TEMPLATE,
) -> List[Tuple[str, float]]:
    """Return [(label, score), ...] for labels scoring >= threshold (desc)."""
    if not text or not labels:
        return []
    classifier = _get_classifier()
    result: Dict[str, List[Any]] = classifier(
        text,
        list(labels),
        multi_label=True,
        hypothesis_template=template,
    )
    out: List[Tuple[str, float]] = []
    for label, score in zip(result['labels'], result['scores']):
        if float(score) >= float(threshold):
            out.append((str(label), float(score)))
    out.sort(key=lambda item: item[1], reverse=True)
    return out


@register_validator(name='constrain_topic', data_type='string')
class ConstrainTopic(Validator):
    """Guardrails validator that fails when banned topics are detected."""

    def __init__(
        self,
        banned_topics: Optional[List[str]] = None,
        threshold: float = 0.8,
        template: Optional[str] = None,
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
        self.template: str = template or _HYPOTHESIS_TEMPLATE

    def _validate(
        self,
        value: str,
        metadata: Optional[Dict[str, str]] = None,
    ) -> ValidationResult:
        """Validate a string value against banned topics."""
        del metadata  # unused, kept for Validator interface
        matches = detect_topics(
            value,
            self.banned_topics,
            threshold=self.threshold,
            template=self.template,
        )
        if matches:
            detail = ', '.join(
                f'{label}:{score:.2f}' for label, score in matches
            )
            return FailResult(
                error_message=f'Banned topics detected → {detail}'
            )
        return PassResult()
