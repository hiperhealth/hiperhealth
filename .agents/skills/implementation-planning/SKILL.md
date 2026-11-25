---
name: implementation-planning
description: >
  Structured planning for multi-file or architectural changes. Defines timeboxed
  milestones, acceptance criteria, and clinical safety gates. Use when asked to
  plan, design, or implement complex features.
---

# Implementation Planning

**Use when asked to "plan", "design", or "help build" a feature that touches
multiple files or components.** Apply
[minimal-change](../minimal-change/SKILL.md) during subsequent code execution.

## Procedure

1. **Gather repository facts:**

   - Inspect existing implementations under `src/hiperhealth/`.
   - Identify relevant pipeline stages, schemas, or models involved.
   - Check existing test fixtures under `tests/data/`.
   - Never speculate on commands or module responsibilities; verify with
     `AGENTS.md`.

2. **Draft the plan in `.agents/PLAN.md`:** Structure the plan with the
   following sections:

   ```markdown
   # Feature Plan: <Feature Name>

   ## Context & Objective

   <1-2 sentences on the goal and user request>

   ## Impacted Files

   - `src/hiperhealth/...` (new/modified)
   - `tests/...` (new/modified)
   - `docs/...` (if public API or config changes)

   ## Milestones

   - **M1: <Scope 1>** - <acceptance criteria>
   - **M2: <Scope 2>** - <acceptance criteria>

   ## Verification Checklist

   - [ ] Targeted tests pass (`makim tests.unit --path tests/...`)
   - [ ] Code coverage remains >= 92% (`makim tests.unit`)
   - [ ] Type check passes (`mypy src/hiperhealth`)
   - [ ] Linter passes (`makim tests.linter`)

   ## Risks & Safety Boundaries

   - PHI/Privacy: synthetic data only; no real patient data
   - Compatibility: no breaking changes to PipelineContext or Session
   ```

3. **Validate clinical and privacy safety:**

   - Ensure no real Protected Health Information (PHI) or secrets are required.
   - Verify clinical outputs are framed as software assistance, not medical
     advice.

4. **Present the plan and wait for approval:**
   - Present the structured plan to the user.
   - Do NOT begin executing code changes until the user approves the plan.

## Anti-patterns

| Avoid                                             | Prefer                                                 |
| ------------------------------------------------- | ------------------------------------------------------ |
| Coding immediately without presenting a plan      | Writing `.agents/PLAN.md` and confirming scope         |
| Giant single-milestone plans that hide complexity | Focused, incremental milestones with acceptance checks |
| Plans that lack explicit test commands            | Explicit commands (`makim tests.unit`, `mypy`)         |
| Introducing live network/LLM dependencies         | Local deterministic mocks and synthetic fixtures       |

## Exit condition

The plan is documented in `.agents/PLAN.md`, presented to the user, and
confirmed before any code is written.
