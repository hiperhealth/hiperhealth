---
name: testing-standards
description: >
  Pytest conventions, coverage threshold enforcement (>=92%), synthetic clinical
  fixtures, and deterministic LLM mocking. Use when writing, maintaining, or
  reviewing tests.
---

# Testing Standards

**Use when writing, refactoring, or reviewing tests in `tests/`.** Apply
[fix-issue](../fix-issue/SKILL.md) when writing reproduction tests.

## Core Rules

1. **Coverage threshold is enforced at >= 92%:** `makim tests.unit` runs
   `pytest --cov=hiperhealth --cov-fail-under=92`. Any decrease below 92% fails
   CI.
2. **Synthetic data only:** Never commit real patient data, medical records,
   dates of birth, or addresses. Use synthetic fixtures located under
   `tests/data/`:
   - `tests/data/diagnostics/`
   - `tests/data/symptoms/`
   - `tests/data/patients/`
   - `tests/data/wearable/`
   - `tests/data/reports/`
3. **No live LLM or network calls in tests:**
   - Never require real API keys or live LLM provider connections in standard
     tests.
   - Inject fake completion functions or mock `StructuredLLM` / `LLMSettings`.
4. **Deterministic execution:** Stage runner tests, session tests, and
   extraction tests must be repeatable and independent of environment state.

## Test Commands

```bash
# Run all unit tests with coverage check (>=92%)
makim tests.unit

# Run a specific test file
makim tests.unit --path tests/test_pipeline.py

# Fast targeted test execution with pytest directly
pytest tests/test_session.py -q

# Run a specific test by name
pytest tests/test_pipeline.py -k "test_stage_runner_order" -vv
```

## Writing Tests

### 1. Mocking LLM completions

```python
from hiperhealth.llm import LLMSettings


def test_clinical_skill_with_fake_llm(monkeypatch):
    fake_response = {"diagnosis": "Hypertension", "confidence": 0.95}

    def fake_completion(*args, **kwargs):
        return fake_response

    # Inject fake completion without network calls
    ...
```

### 2. Testing Stage & Skill Execution

```python
from hiperhealth.pipeline.context import PipelineContext
from hiperhealth.pipeline.runner import StageRunner
from hiperhealth.pipeline.skill import BaseSkill, SkillMetadata
from hiperhealth.pipeline.stages import Stage


class ScreeningSkill(BaseSkill):
    def __init__(self) -> None:
        super().__init__(
            SkillMetadata(
                name='screening-example',
                stages=(Stage.SCREENING,),
            )
        )

    def execute(
        self, stage: str, ctx: PipelineContext
    ) -> PipelineContext:
        ctx.results[stage] = {'screened': True}
        return ctx


def test_stage_execution():
    context = PipelineContext(patient={'symptoms': 'synthetic cough'})
    runner = StageRunner(skills=[ScreeningSkill()])

    result_context = runner.run(Stage.SCREENING, context)

    assert result_context.results['screening'] == {'screened': True}
```

## Anti-patterns

| Avoid                                                   | Prefer                                               |
| ------------------------------------------------------- | ---------------------------------------------------- |
| Live API calls (`litellm.completion` to real endpoints) | Fake LLM client or injected response mock            |
| Real patient records, PDFs, or scan images              | Synthetic fixtures under `tests/data/`               |
| Broad catch-all assertions (`assert result`)            | Specific assertions on typed schema fields           |
| Lowering coverage threshold when adding new code        | Adding comprehensive unit tests for all new branches |

## Exit condition

New or modified code is thoroughly covered by deterministic unit tests,
synthetic fixtures are used, and `makim tests.unit` passes with coverage >= 92%.
