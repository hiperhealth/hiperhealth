---
name: open-pr
description: >
  Preparation and verification for pull requests. Verifies CI gates (makim
  tests.ci), conventional commits, and clean git state. Use when preparing
  commits or opening a PR.
---

# Open Pull Request

**Use when preparing a branch for commit, creating a pull request, or validating
CI readiness.** Apply [pr-review](../pr-review/SKILL.md) to self-review before
pushing.

## Step-by-Step Preparation

### 1. Verify Clean and Minimal Working Tree

Inspect changed files to ensure no accidental artifacts, virtual environments,
or temporary test outputs are tracked:

```bash
git status
```

Ensure `.coverage`, `build/`, `dist/`, or cache folders are not staged.

### 2. Run Local Quality Stack (CI Simulation)

Execute the complete test and lint suite configured for CI:

```bash
# Run unit tests (coverage >= 92%) and linter stack
makim tests.ci
```

Or run the individual gates:

```bash
makim tests.unit
makim tests.linter
mypy src/hiperhealth
```

### 3. Check Documentation and Generated Models

- If schemas in `src/hiperhealth/schema/` were modified, ensure generated models
  were updated:
  ```bash
  makim gen.fhir-models
  ```
- If CLI flags, pipeline stages, or LLM configs changed, update the
  corresponding markdown files in `docs/` or `README.md`.

### 4. Format Commit Message (Semantic Release Requirement)

HiperHealth uses `semantic-release` to automate versioning and changelogs.
Commit messages and PR titles **must** follow the Conventional Commits format:

```text
<type>(<optional scope>): <short summary in imperative present tense>
```

Allowed types:

- `feat:` A new feature or stage capability (triggers minor release)
- `fix:` A bug fix in pipeline, schema, or extraction (triggers patch release)
- `docs:` Documentation updates only
- `test:` Adding or updating tests without code changes
- `refactor:` Code changes that neither fix a bug nor add a feature
- `chore:` Maintenance, dependency bumps, or tool configuration

_Example:_
`feat(pipeline): add support for async inquiry resolution in stage runner`

### 5. Review Diff Before Staging

```bash
git diff
```

Verify:

1. No unredacted PHI, fake patient secrets, or live credentials.
2. No out-of-scope edits or formatting churn.

## Anti-patterns

| Avoid                                                    | Prefer                                                                             |
| -------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| Non-conventional PR titles (e.g. "updates", "fixes bug") | Conventional commit format (e.g. `fix(privacy): handle none tokens in anonymizer`) |
| Opening PR with failing `makim tests.ci`                 | Resolving all test and linter failures locally first                               |
| Bundling unrelated changes in one PR                     | Opening focused, single-purpose PRs                                                |

## Exit condition

Local CI checks pass cleanly (`makim tests.ci`), commit message follows
Conventional Commits, and the working tree is clean.
