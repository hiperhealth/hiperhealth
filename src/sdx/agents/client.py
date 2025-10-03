"""
Shared OpenAI helper used by all agents.

* Forces JSON responses (`response_format={"type": "json_object"}`).
* Validates with ``LLMDiagnosis.from_llm``.
* Persists every raw reply under ``data/llm_raw/<sid>_<UTC>.json``.
"""

from __future__ import annotations

import os
import uuid

from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from fastapi import HTTPException
from guardrails.validator_base import FailResult
from openai import OpenAI
from pydantic import ValidationError

from sdx.guards.topic_guard import ConstrainTopic
from sdx.schema.clinical_outputs import LLMDiagnosis

load_dotenv(Path(__file__).parents[3] / '.envs' / '.env')

_MODEL_NAME = os.getenv('OPENAI_MODEL', 'o4-mini')
_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY', ''))

_RAW_DIR = Path('data') / 'llm_raw'
_RAW_DIR.mkdir(parents=True, exist_ok=True)

_DEFAULT_BANNED_TOPIC_LABELS = [
    'encouraging self-harm',
    'explicit violent threat',
    'harassment with violent intent',
    'suicide instructions',
    'medical dosing advice',
]


def _env_banned_topics() -> list[str]:
    """Return banned topic labels from env or the default list."""
    env_value = os.getenv('TOPIC_GUARD_BANNED')
    if not env_value:
        return _DEFAULT_BANNED_TOPIC_LABELS
    # Split by ';' and keep non-empty trimmed labels
    return [item.strip() for item in env_value.split(';') if item.strip()]


_BANNED_TOPIC_LABELS = _env_banned_topics()
_TOPIC_GUARD_CONFIDENCE_THRESHOLD = float(
    os.getenv('TOPIC_GUARD_THRESHOLD', '0.8')
)
_TOPIC_GUARD_ENABLED = os.getenv('TOPIC_GUARD_ENABLED', '1') != '0'

_TOPIC_GUARD_VALIDATOR = ConstrainTopic(
    banned_topics=_BANNED_TOPIC_LABELS,
    threshold=_TOPIC_GUARD_CONFIDENCE_THRESHOLD,
)

_SAFETY_SYSTEM_PROMPT_RULES = (
    'Safety rules: Do not provide treatment plans, medication dosages, or '
    'step-by-step procedures. No instructions for self-harm or harming '
    'others. Be non-prescriptive and probabilistic. Only list '
    'non-actionable differential options.'
)


def dump_llm_json(text: str, sid: str | None) -> None:
    """
    Save *text* to data/llm_raw/<timestamp>_<sid>.json.

    If *sid* is None, a random 8-char token is used instead.
    """
    ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    suffix = sid or uuid.uuid4().hex[:8]
    (_RAW_DIR / f'{ts}_{suffix}.json').write_text(text, encoding='utf-8')


def _assert_output_is_safe(obj: LLMDiagnosis) -> None:
    """Validate LLM output against topic guard; raise if unsafe."""
    if not _TOPIC_GUARD_ENABLED:
        return
    combined_text = f'{obj.summary}\n' + '\n'.join(obj.options or [])
    # FIX: pass metadata=None for Guardrails' validate signature
    result = _TOPIC_GUARD_VALIDATOR.validate(combined_text, metadata=None)
    if isinstance(result, FailResult):
        raise HTTPException(
            400, f'Unsafe LLM output blocked: {result.error_message}'
        )


def chat(
    system: str,
    user: str,
    *,
    session_id: str | None = None,
) -> LLMDiagnosis:
    """Send system / user prompts and return a validated ``LLMDiagnosis``."""
    rsp = _client.chat.completions.create(
        model=_MODEL_NAME,
        response_format={'type': 'json_object'},
        messages=[
            {
                'role': 'system',
                'content': f'{system}\n\n{_SAFETY_SYSTEM_PROMPT_RULES}',
            },
            {'role': 'user', 'content': user},
        ],
    )

    raw: str = rsp.choices[0].message.content or '{}'
    dump_llm_json(raw, session_id)

    try:
        parsed = LLMDiagnosis.from_llm(raw)
    except ValidationError as exc:
        raise HTTPException(
            422, f'LLM response is not valid LLMDiagnosis: {exc}'
        ) from exc

    _assert_output_is_safe(parsed)
    return parsed
