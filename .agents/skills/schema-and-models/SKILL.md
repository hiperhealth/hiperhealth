---
name: schema-and-models
description: >
  Update Pydantic clinical output schemas, FHIR structures, and synchronize
  generated SQLAlchemy models. Use when adding or modifying data schemas or
  models.
---

# Schema and Model Synchronization

**Use when modifying Pydantic clinical output schemas, FHIR mappings, or
SQLAlchemy models.** Apply [testing-standards](../testing-standards/SKILL.md) to
verify serialization round-trips.

## Architecture

- **Pydantic schemas (`src/hiperhealth/schema/`):** The single source of truth
  for typed clinical output structures, evaluation models, and FHIR extensions.
- **SQLAlchemy FHIR models (`src/hiperhealth/models/sqla/`):** Generated models
  mapped to FHIR R5 resources for database storage and ORM usage.

## Synchronization Procedure

1. **Update Pydantic schema first:** Make edits in `src/hiperhealth/schema/`
   (`clinical_outputs.py`, `fhirx.py`, etc.).

   - Use explicit field types, Pydantic `Field` validators, and Enums.
   - Avoid loose `dict[str, Any]` for clinical data.
   - Keep models backward-compatible with serialized sessions.

2. **Regenerate SQLAlchemy FHIR models:** Run the model generator script via the
   task runner:

   ```bash
   makim gen.fhir-models
   ```

   _(This runs `python scripts/gen_models/gen_sqla.py`.)_

3. **Inspect the generated diff:**

   ```bash
   git diff src/hiperhealth/models/sqla/
   ```

   Verify that only intended model attributes and relationships changed. Avoid
   unrelated churn.

4. **Run serialization round-trip tests:**

   ```bash
   makim tests.unit --path tests/test_schema_models.py
   makim tests.unit --path tests/test_models_fhir_sqla.py
   ```

5. **Run type checking and formatting:**
   ```bash
   mypy src/hiperhealth
   ruff check src/hiperhealth/schema src/hiperhealth/models
   ```

## Anti-patterns

| Avoid                                                 | Prefer                                                        |
| ----------------------------------------------------- | ------------------------------------------------------------- |
| Editing generated SQLAlchemy models by hand           | Updating Pydantic schemas and running `makim gen.fhir-models` |
| Committing schema changes without regenerated models  | Committing schema and generated model diffs together          |
| Using loose dictionaries for clinical outputs         | Strictly typed Pydantic models with validation                |
| Renaming public schema fields without migration paths | Deprecating gracefully or providing aliased fields            |

## Exit condition

Pydantic schemas and generated SQLAlchemy FHIR models are synchronized,
round-trip tests pass, and `mypy` passes strictly.
