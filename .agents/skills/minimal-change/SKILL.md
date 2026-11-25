---
name: minimal-change
description: >
  Scope control and surgical changes. Enforces minimal diffs, protects public
  API and session compatibility, and prevents scope creep. Use for any
  implementation or refactoring task.
---

# Minimal Change

**Use for any code modification or refactoring task.** Apply
[implementation-planning](../implementation-planning/SKILL.md) when the change
spans multiple files or architecture layers.

## Core Rules

1. **Change only what was requested.** Do not "clean up" adjacent code, reformat
   unrelated files, or reorganize imports outside the affected scope.
2. **Preserve public APIs and serialized schemas.** `PipelineContext`,
   `StageRunner`, `SkillMetadata`, and parquet session structures must remain
   backward-compatible unless the task explicitly specifies a breaking change.
3. **Follow repository style strictly:**
   - Indentation: 4 spaces.
   - Max line length: 79 characters (enforced by Ruff).
   - Single quotes for string literals.
   - Flat control flow with guard clauses and early returns.
4. **Draft file changes first.** If touching more than one file, record the
   intended edit list in `.agents/PLAN.md`.

## Procedure

1. **Inspect before editing:** Read the target file and its adjacent tests to
   understand existing patterns and edge cases.
2. **State the edit list:** Note target files and functions to modify.
3. **Make the smallest sufficient edit:** Solve the immediate requirement
   cleanly. If you discover adjacent technical debt, note it in
   `.agents/PLAN.md` under "Follow-up" rather than fixing it now.
4. **Run targeted checks:**
   ```bash
   # Run only affected tests
   pytest tests/test_target.py -q
   # Format and lint touched files
   ruff format src/hiperhealth/path/to/file.py tests/test_target.py
   ruff check src/hiperhealth/path/to/file.py tests/test_target.py
   ```
5. **Inspect the git diff:** Verify every single changed line has a direct
   purpose related to the task:
   ```bash
   git diff
   ```

## Anti-patterns

| Avoid                                             | Prefer                                                  |
| ------------------------------------------------- | ------------------------------------------------------- |
| Reformatting untouched functions or files         | Formatting only the touched lines/files                 |
| Speculative helper functions "for future use"     | Code written only for current requirements              |
| Breaking public function signatures or parameters | Extending signatures with backwards-compatible defaults |
| Changing test fixtures without clear necessity    | Reusing existing synthetic fixtures in `tests/data/`    |
| Running full CI suite for single-line typos       | Running targeted `pytest <file> -q` first               |

## Exit condition

The change is the absolute smallest set of edits that satisfies the requirement,
targeted tests pass, and `git diff` contains zero unrelated churn.
