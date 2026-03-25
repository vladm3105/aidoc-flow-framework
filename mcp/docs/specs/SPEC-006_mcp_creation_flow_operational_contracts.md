# SPEC-006: MCP Creation Flow Operational Contracts

| Field | Value |
| --- | --- |
| Canonical ID | SPEC-006 |
| Status | Active |
| Version | 1.0 |
| Date | 2026-03-24 |
| Scope | Operational contracts for init and create-build flows |

---

## 1. Purpose

Define operational contracts for initialization and creation prompt assembly behavior.

Implementation complexity: 4/5.

---

## 2. Scope and Boundaries

In scope:
- init command operational behavior
- create-build command operational behavior
- creation artifact emission behavior
- project-local UCX dependency requirements

Out of scope:
- review-build operational details except where needed for cross-reference
- external source-to-sections conversion pipelines

---

## 3. init Command Contract

Normative behavior:
- init requires project argument.
- command scaffolds project-local docs/UCX files.
- existing files may be skipped without failure.

Required outputs:
- initialized project path
- created count
- skipped count

Failure modes:
- invalid or inaccessible project path
- scaffold write failure

---

## 4. create-build Command Contract

Required arguments:
- project
- persona
- doc-type
- layer
- template
- out

Optional arguments:
- sections-json

Normative behavior:
1. resolve project and output paths
2. parse sections-json when provided
3. invoke creation build runner
4. emit creation artifacts when output path exists and is writable

Required artifact names when output enabled:
- creation_prompt.txt
- creation_prompt_sidecar.json
- creation_prompt_inspection.json

---

## 5. Project UCX Dependency Contract

Runtime must load required project-local assets from docs/UCX paths.

If required paths are missing, runtime must raise:
- ProjectSkillsNotFound

Required error payload fields:
- error_code
- project_root
- missing_paths
- resolution

Required resolution behavior:
- instruct operator to run init with project path

---

## 6. Creation Flow Failure Modes

| Failure Mode | Detection Point | Required Behavior |
| --- | --- | --- |
| Missing required CLI argument | argument parse stage | command parse failure |
| sections-json payload invalid | deserialization stage | command failure with input correction required |
| Missing project UCX assets | loader validation stage | ProjectSkillsNotFound |
| Prompt bundle validation failure | assembly validation stage | contract validation failure |
| Artifact write failure | output stage | command failure with path and I/O context |

---

## 7. Validation Evidence Requirements

Required checks:
- argument parity verification against cli/main.py
- runner artifact naming verification against review/runner.py creation result
- missing asset behavior verification against skills/project_ucx_loader.py

---

## 8. Constraints

- Creation flow contracts represent implemented runtime behavior only.
- Future-state creation modes must be documented separately and must not alter active contract claims without version update.
