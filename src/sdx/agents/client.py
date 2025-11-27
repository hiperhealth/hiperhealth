"""OpenAI chat helper with schema validation and topic safety."""

from __future__ import annotations

import os
import uuid

from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from fastapi import HTTPException
from openai import APIConnectionError, BadRequestError, OpenAI, RateLimitError
from pydantic import ValidationError

from sdx.agents.safety import _enforce_topic_safety, with_safety
from sdx.schema.clinical_outputs import LLMDiagnosis

# Load env once
load_dotenv(Path(__file__).parents[3] / '.envs' / '.env')

_MODEL_NAME = os.getenv('OPENAI_MODEL', 'o4-mini')
_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY', ''))

_RAW_DIR = Path('data') / 'llm_raw'
_RAW_DIR.mkdir(parents=True, exist_ok=True)


def _save_raw(text: str, sid: str | None) -> None:
    ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    suffix = sid or uuid.uuid4().hex[:8]
    (_RAW_DIR / f'{ts}_{suffix}.json').write_text(text, encoding='utf-8')


def chat(
    system: str,
    user: str,
    *,
    session_id: str | None = None,
) -> LLMDiagnosis:
    """Send system/user prompts, parse to LLMDiagnosis."""
    try:
        rsp = _client.chat.completions.create(
            model=_MODEL_NAME,
            response_format={'type': 'json_object'},
            messages=[
                {'role': 'system', 'content': with_safety(system)},
                {'role': 'user', 'content': user},
            ],
        )
    except RateLimitError as exc:
        raise HTTPException(429, f'LLM rate limit: {exc}') from exc
    except (BadRequestError, APIConnectionError) as exc:
        raise HTTPException(502, f'LLM error: {exc}') from exc

    content = (rsp.choices[0].message.content or '{}') if rsp.choices else '{}'
    _save_raw(content, session_id)

    try:
        parsed = LLMDiagnosis.from_llm(content)
    except ValidationError as exc:
        raise HTTPException(
            422, f'LLM JSON did not match schema: {exc}'
        ) from exc

    _enforce_topic_safety(parsed)
    return parsed


__all__ = ['chat']
