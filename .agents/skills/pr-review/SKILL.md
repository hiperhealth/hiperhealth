---
name: pr-review
description: >
  Checklist for pull requests: PHI safety, backward compatibility, test
  coverage, static typing, and docstrings. Use when asked to review a PR, check
  a diff, or validate readiness.
---

# Pull Request Review

**Use when reviewing code changes, checking diffs, or evaluating PR readiness.**
Apply [testing-standards](../testing-standards/SKILL.md) and
[minimal-change](../minimal-change/SKILL.md) to evaluate code quality.

## Review Procedure

1. **Drop review notes in `.agents/REVIEW.md`** during the inspection.
2. **Review against the Quality Gates:**

### Gate 1: Privacy and Clinical Safety

- [ ] **Zero PHI:** Confirm no real patient names, records, IDs, or images were
      added.
- [ ] **No Secrets:** Confirm no API keys, tokens, or auth headers are logged or
      committed.
- [ ] **Clinical Scope:** Software outputs must be scoped as clinician decision
      support, not definitive diagnostic medical advice.

### Gate 2: Compatibility and Public API

- [ ] **Pipeline Compatibility:** `PipelineContext`, `StageRunner`, and skill
      hooks remain backwards-compatible.
- [ ] **Session Parquet Format:** Event log structure in parquet sessions
      remains deserializable.
- [ ] **Schema & Models:** If Pydantic schemas changed, generated SQLAlchemy
      FHIR models (`src/hiperhealth/models/sqla/`) are updated in sync via
      `makim gen.fhir-models`.

### Gate 3: Test Coverage & Determinism

- [ ] Unit tests cover all new branches.
- [ ] Standard test suite does not require network access or live API keys.
- [ ] `makim tests.unit` passes with coverage at or above 92%.

### Gate 4: Code Style & Quality

- [ ] Max line length is 79 characters; single quotes used for strings.
- [ ] Strict type checking passes (`mypy src/hiperhealth`).
- [ ] Public functions and classes contain Douki-style YAML docstrings.
- [ ] Pre-commit linter stack passes (`makim tests.linter`).

### Gate 5: Semantic Release Compatibility

- [ ] PR title and commit messages follow Conventional Commits (e.g. `feat:`,
      `fix:`, `docs:`, `chore:`).

## Review Report Template

When delivering the review in chat, use this format:

```markdown
### PR Review Summary

**Status:** APPROVED / CHANGES REQUESTED

#### Critical Checks

- [x] Zero PHI or secrets committed
- [x] Public API / serialized format backward compatible
- [x] Test coverage >= 92% preserved
- [x] Linter & mypy pass

#### Findings & Feedback

- **Issue 1:** <file>:<line> - Description and suggested fix.

#### Verification Run

- `makim tests.unit`: PASS (Coverage: X%)
- `makim tests.linter`: PASS
```

## Exit condition

All 5 quality gates are verified, documented in `.agents/REVIEW.md`, and
reported with clear actionable feedback.
