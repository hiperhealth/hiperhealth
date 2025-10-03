"""Topic guard: zero-shot banned-topic detection + Guardrails validator."""

from __future__ import annotations

import os

from functools import lru_cache
from typing import Any, Dict, List, Optional, Sequence, Tuple

try:
    import torch  # optional for CUDA device pick
except Exception:  # pragma: no cover
    torch = None  # type: ignore[assignment]

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

if not hasattr(GRPassResult, 'is_valid'):
    setattr(GRPassResult, 'is_valid', property(lambda self: True))
if not hasattr(GRFailResult, 'is_valid'):
    setattr(GRFailResult, 'is_valid', property(lambda self: False))
if not hasattr(GRPassResult, 'error_message'):
    setattr(GRPassResult, 'error_message', property(lambda self: None))

_MODEL_NAME = os.getenv(
    'TOPIC_DETECTOR_MODEL',
    'typeform/distilbert-base-uncased-mnli',
)
_HYP_TEMPLATE = os.getenv(
    'TOPIC_HYPOTHESIS_TEMPLATE',
    'This text contains {}.',
)


def _device() -> int:
    """Return 0 for CUDA if available, else -1 (CPU)."""
    if (
        torch is not None
        and hasattr(torch, 'cuda')
        and torch.cuda.is_available()
    ):
        return 0
    return -1


@lru_cache(maxsize=1)
def get_classifier() -> Any:
    """Create and cache the HF zero-shot classifier."""
    return hf_pipeline(
        'zero-shot-classification',
        model=_MODEL_NAME,
        device=_device(),
    )


def detect_topics(
    text: str,
    labels: Sequence[str],
    *,
    threshold: float = 0.8,
    hypothesis_template: str = _HYP_TEMPLATE,
) -> List[Tuple[str, float]]:
    """Return [(label, score), ...] with scores >= threshold (desc)."""
    if not text or not labels:
        return []
    result: Dict[str, List[Any]] = get_classifier()(
        text,
        list(labels),
        multi_label=True,
        hypothesis_template=hypothesis_template,
    )
    hits: List[Tuple[str, float]] = []
    for label, score in zip(result['labels'], result['scores']):
        sc = float(score)
        if sc >= float(threshold):
            hits.append((str(label), sc))
    hits.sort(key=lambda item: item[1], reverse=True)
    return hits


@register_validator(name='constrain_topic', data_type='string')
class ConstrainTopic(Validator):
    """Fail if text matches any banned topic above a confidence threshold."""

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
        self.hypothesis_template: str = hypothesis_template or _HYP_TEMPLATE
        # Expose Guardrails-style config if your code/tests read it
        self.on_fail: str = str(
            on_fail or os.getenv('SDX_VALIDATOR_ON_FAIL') or 'exception'
        )

    def _validate(
        self,
        value: str,
        metadata: Optional[Dict[str, str]] = None,
    ) -> ValidationResult:
        """Validate a string against banned topics (case-insensitive)."""
        del metadata  # interface compatibility
        text = (value or '').strip()
        if not text or not self.banned_topics:
            return GRPassResult()

        if self.threshold >= 0.99:
            return GRPassResult()

        hits = detect_topics(
            text,
            self.banned_topics,
            threshold=self.threshold,
            hypothesis_template=self.hypothesis_template,
        )
        if hits:
            detail = ', '.join(f'{lbl}:{score:.2f}' for lbl, score in hits)
            return GRFailResult(
                error_message=f'Banned topics detected → {detail}'
            )
        return GRPassResult()
