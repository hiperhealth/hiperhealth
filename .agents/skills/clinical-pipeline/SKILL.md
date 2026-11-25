---
name: clinical-pipeline
description: >
  Develop or modify pipeline stages, built-in skills, hooks, inquiry
  requirements, and parquet sessions. Use when working on pipeline, stage
  runner, or skill implementations.
---

# Clinical Pipeline and Skills Development

**Use when modifying or creating pipeline stages, skill hooks, stage runners, or
session persistence.** Apply [schema-and-models](../schema-and-models/SKILL.md)
when modifying clinical data models.

## Architecture & Responsibilities

The HiperHealth pipeline processes patient data deterministically through
clinical stages:
`clinical data -> PipelineContext/Session -> StageRunner -> Skills -> typed outputs`

### Key Modules:

- `src/hiperhealth/pipeline/stages.py`: Supported workflow stages:
  - `Stage.SCREENING`
  - `Stage.INTAKE`
  - `Stage.DIAGNOSIS`
  - `Stage.EXAM`
  - `Stage.TREATMENT`
  - `Stage.PRESCRIPTION`
- `src/hiperhealth/pipeline/context.py`: `PipelineContext` carries patient data,
  session identifiers, language, accumulated stage results, and metadata.
- `src/hiperhealth/pipeline/skill.py`: Base skill interfaces and
  `SkillMetadata`.
- `src/hiperhealth/pipeline/runner.py`: `StageRunner` executes registered skills
  for a given stage in registration order.
- `src/hiperhealth/pipeline/session.py`: Parquet-backed persistence for
  resumable encounters.

## Procedure for Adding or Updating a Skill

1. **Define Skill Implementation:** Implement hooks only as needed (`pre()`,
   `execute()`, `post()`):

   ```python
   from hiperhealth.pipeline.context import PipelineContext
   from hiperhealth.pipeline.skill import BaseSkill, SkillMetadata
   from hiperhealth.pipeline.session import Inquiry
   from hiperhealth.pipeline.stages import Stage


   class ExampleClinicalSkill(BaseSkill):

       def __init__(self) -> None:
           super().__init__(
               SkillMetadata(
                   name='example-skill',
                   stages=(Stage.DIAGNOSIS,),
                   description='Generates structured inquiries.',
               )
           )

       def check_requirements(
           self, stage: str, ctx: PipelineContext
       ) -> list[Inquiry]:
           inquiries: list[Inquiry] = []
           if not ctx.patient.get('symptoms'):
               inquiries.append(
                   Inquiry(
                       skill_name=self.metadata.name,
                       stage=stage,
                       field='symptoms',
                       label='Symptoms',
                       description='Please provide current symptoms.',
                       priority='required',
                   )
               )
           return inquiries

       def execute(self, stage: str, ctx: PipelineContext) -> PipelineContext:
           ctx.results[stage] = {'reviewed': True}
           return ctx
   ```

2. **Register Built-in Skills:** If adding an installable built-in skill:

   - Place under `src/hiperhealth/skills/<skill_name>/`.
   - Add entry point in `pyproject.toml` under
     `[project.entry-points."hiperhealth.skills"]`.
   - Provide `skill.yaml` describing stage bindings and metadata.

3. **Preserve Session Compatibility:**

   - When modifying `PipelineContext` or `Session`, verify that saved Parquet
     event logs remain readable across versions.
   - Do not dump unredacted patient records to debug logs.

4. **Verify Execution with Unit Tests:**
   ```bash
   makim tests.unit --path tests/test_pipeline.py
   pytest tests/test_skills.py -q
   ```

## Anti-patterns

| Avoid                                            | Prefer                                                             |
| ------------------------------------------------ | ------------------------------------------------------------------ |
| Raising exceptions for missing patient input     | Returning structured `Inquiry` objects from `check_requirements()` |
| Hidden global state in skills or runners         | Explicit context and dependency injection                          |
| Hardcoding stage execution order in skills       | Letting `StageRunner` manage stage sequencing                      |
| Dumping raw patient data into parquet debug logs | De-identifying or summarizing intermediate logs                    |

## Exit condition

The stage or skill is implemented with immutable `SkillMetadata`, requirement
checks return structured `Inquiry` items, sessions remain compatible, and tests
pass with coverage >= 92%.
