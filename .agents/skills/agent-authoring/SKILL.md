---
name: agent-authoring
description: >
  Create or maintain portable Agent Skills in .agents/skills/ with narrow
  triggers, minimal duplication, and safe tool permissions. Use for skill
  authoring.
---

# Agent Authoring

**Use when adding, updating, or auditing skills in
`.agents/skills/**/SKILL.md`.** Root `AGENTS.md` holds universally applicable
rules; skills provide concrete, task-specific procedures and verification
commands.

## Skill Structure Standards

1. **Discoverable YAML Frontmatter:**

   - `name`: lowercase-hyphenated string matching the folder name exactly.
   - `description`: 1-2 sentences explaining what the skill does and ending with
     a clear trigger: `"Use for <X>"` or `"Use when <Y>"`.

2. **Context & Ownership:**

   - Reference real paths (e.g. `src/hiperhealth/pipeline/`, `tests/data/`).
   - Reference real repo commands (`makim tests.unit`, `makim tests.linter`,
     `makim gen.fhir-models`, `ruff`, `mypy`).

3. **Concrete Workflow:**

   - Ordered step-by-step procedure (3 to 6 steps).
   - Anti-patterns table showing wrong vs. right approaches.
   - Clear verification commands proving the exit condition.

4. **Exit condition:**
   - One concise sentence describing exactly what "done" looks like so the agent
     stops.

## Authoring Procedure

1. **Verify need:** Check whether an existing skill can handle the task or if
   the topic is short enough (<5 lines) to belong directly in `AGENTS.md`. Only
   create a skill for repeated, multi-step task types.
2. **Inspect repo facts:** Inspect actual code, tests, and configuration rather
   than guessing commands or directory layouts.
3. **Draft the skill:** Create `.agents/skills/<name>/SKILL.md` following the
   standard structure.
4. **Update table in `AGENTS.md`:** Add the new skill to the `Agent Skills`
   table in `AGENTS.md`.
5. **Safety check:** Ensure the skill never instructs agents to bypass sandbox
   rules, commit credentials, log patient PHI, or weaken quality thresholds.

## Anti-patterns

| Avoid                                             | Prefer                                               |
| ------------------------------------------------- | ---------------------------------------------------- |
| Creating skills for single files or one-off tasks | Skills for repeated task types                       |
| Copying broad rules from `AGENTS.md`              | Linking to `AGENTS.md` instead                       |
| Generic advice ("write clean code")               | Specific commands, paths, and patterns               |
| Inventing test runners or scripts                 | Using real repo commands (`makim`, `pytest`, `ruff`) |

## Exit condition

The skill is created at `.agents/skills/<name>/SKILL.md` with valid YAML
frontmatter, referenced in `AGENTS.md`, and all relative path links resolve.
