---
name: privacy-and-llm
description: >
  De-identification with Presidio, synthetic data safety, and provider-agnostic
  LLM calls via LiteLLM and StructuredLLM. Use when working on privacy, prompts,
  or LLM integrations.
---

# Privacy and LLM Integration

**Use when modifying LLM settings, prompts, structured output parsers, or
Presidio de-identification logic.** Apply
[testing-standards](../testing-standards/SKILL.md) for mocking LLM calls.

## Core Rules

1. **Zero PHI / De-identification First:**

   - Real patient identifiers (names, dates of birth, social security numbers,
     addresses, phone numbers) must **never** be sent to external LLM providers
     or committed to the repository.
   - Use `Deidentifier` from `hiperhealth.skills.privacy.deidentifier` to
     de-identify supported PII. Presidio may miss identifiers; do not treat it
     as a guarantee that text is safe to transmit. Apply the workflow's required
     privacy checks before external transmission and minimize submitted data.
   - Synthetic fixtures under `tests/data/` are the only allowed test data.

2. **Provider-Agnostic LLM Access:**

   - Always route LLM calls through `hiperhealth.llm.LLMSettings` and the
     `StructuredLLM` protocol.
   - Never hardcode provider-specific APIs (such as OpenAI-only or
     Anthropic-only SDK calls); LiteLLM handles model routing.
   - Update `docs/llm_configuration.md` if new environment variables or defaults
     are added.

3. **Pydantic Validation for Structured Generation:**

   - Never trust raw LLM text as a clinical output.
   - Validate all outputs with Pydantic schemas from `src/hiperhealth/schema/`.

4. **Clinical Scope and Disclaimers:**
   - AI outputs must always be framed as software assistance for clinicians.
   - Prompts must not instruct models to state binding medical conclusions.

## Implementation Pattern

```python
from hiperhealth.llm import LLMSettings, build_structured_llm
from hiperhealth.schema.clinical_outputs import LLMDiagnosis
from hiperhealth.skills.privacy.deidentifier import Deidentifier


def deidentify_for_review(raw_text: str) -> str:
    return Deidentifier().deidentify(raw_text)


def process_approved_text(
    privacy_checked_text: str,
    llm_settings: LLMSettings,
) -> LLMDiagnosis:
    llm = build_structured_llm(settings=llm_settings)
    return llm.generate(
        system=(
            'Provide clinician decision support, not a definitive diagnosis.'
        ),
        user=privacy_checked_text,
        output_type=LLMDiagnosis,
    )
```

Only pass text to `process_approved_text()` after the workflow's privacy
controls have checked it; Presidio may not detect every identifier.

## Verification

```bash
# Test privacy and de-identification with synthetic data
makim tests.unit --path tests/test_deidentifier.py

# Test LLM integration with mocked provider
makim tests.unit --path tests/test_llm.py
```

## Anti-patterns

| Avoid                                                    | Prefer                                            |
| -------------------------------------------------------- | ------------------------------------------------- |
| Sending raw clinical notes to external LLMs              | De-identifying text with Presidio first           |
| Direct SDK imports (`import openai`, `import anthropic`) | LiteLLM routing via `hiperhealth.llm.LLMSettings` |
| Trusting unvalidated LLM output                          | Validating outputs through Pydantic schemas       |
| Logging prompts containing patient data                  | Logging only de-identified metadata or tokens     |

## Exit condition

De-identification is conservative and verified with synthetic tests, LLM calls
are provider-agnostic and mocked in tests, and all outputs validate against
Pydantic schemas.
