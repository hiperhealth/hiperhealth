---
name: fix-issue
description: >
  Disciplined bug resolution workflow: reproduce with synthetic tests, pinpoint
  root causes, apply surgical fixes, and verify. Use for bug fix requests,
  regressions, or test failures.
---

# Fix Issue

**Use when investigating, debugging, or fixing a bug, regression, or test
failure.** Apply [testing-standards](../testing-standards/SKILL.md) when adding
reproduction tests and [minimal-change](../minimal-change/SKILL.md) when editing
code.

## Procedure

1. **Reproduce with a synthetic test first:**

   - Add a minimal test case under `tests/` that fails due to the reported bug.
   - Use synthetic fixtures only (never use real medical data or patient
     identifiers).
   - Run the reproduction test and confirm the failure:
     ```bash
     makim tests.unit --path tests/test_relevant.py
     # or
     pytest tests/test_relevant.py -k "test_repro_case" -vv
     ```

2. **Pinpoint the root cause:**

   - Trace the issue through the relevant pipeline stage, schema, or utility.
   - Check if the bug originates from data validation, hook sequencing in
     `StageRunner`, or parsing edge cases.

3. **Apply a surgical fix:**

   - Fix the root cause with minimal edits.
   - Avoid refactoring surrounding logic or changing unrelated behaviors.
   - Keep control flow flat using guard clauses.

4. **Verify reproduction test passes:**

   ```bash
   pytest tests/test_relevant.py -k "test_repro_case" -vv
   ```

5. **Verify full suite and coverage threshold:**

   - Confirm that the coverage threshold (>= 92%) is preserved:
     ```bash
     makim tests.unit
     ```

6. **Run static checks:**
   ```bash
   ruff check src tests
   ruff format src tests
   mypy src/hiperhealth
   ```

## Anti-patterns

| Avoid                                               | Prefer                                      |
| --------------------------------------------------- | ------------------------------------------- |
| Fixing code without a failing reproduction test     | Writing a reproduction test first           |
| Changing test assertions to make failing tests pass | Fixing the underlying application logic     |
| Weakening `--cov-fail-under=92` threshold           | Adding test coverage for the fixed path     |
| Committing real patient records to debug issues     | Creating synthetic anonymized test fixtures |

## Exit condition

The bug is reproduced by a test, fixed with minimal code changes, all tests pass
with coverage >= 92%, and static checks pass cleanly.
