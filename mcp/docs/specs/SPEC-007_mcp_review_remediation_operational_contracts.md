# SPEC-007: MCP Review and Remediation Operational Contracts

| Field | Value |
| --- | --- |
| Canonical ID | SPEC-007 |
| Status | Active |
| Version | 1.0 |
| Date | 2026-03-24 |
| Scope | Operational contracts for review-build behavior and remediation handoff artifacts |

---

## 1. Purpose

Define review-build operational behavior, output contracts, and remediation handoff prerequisites.

Implementation complexity: 4/5.

---

## 2. Scope and Boundaries

In scope:
- review-build command contract
- required sections-json behavior
- review artifact emission contracts
- handoff requirements for downstream remediation workflows

Out of scope:
- automated remediation algorithm implementation details
- non-MCP external review pipelines

---

## 3. review-build Command Contract

Required arguments:
- project
- persona
- doc-type
- template
- sections-json
- out

Optional argument:
- layer

Normative behavior:
1. parse and validate required arguments
2. load sections payload into SourceSection objects
3. run review prompt assembly
4. produce prompt text, sidecar, and inspection payload
5. write artifacts to output directory

Required artifact names:
- review_prompt.txt
- review_prompt_sidecar.json
- review_prompt_inspection.json

---

## 4. Inspection and Sidecar Contract

Required sidecar behavior:
- sidecar output must serialize prompt metadata sidecar from validated prompt bundle.

Required inspection behavior:
- inspection output must be deterministic for repeated identical inputs.
- inspection output must surface warnings for missing structure blocks or token budget conditions when thresholds are met.

---

## 5. Remediation Handoff Preconditions

Remediation handoff requires:
- review prompt artifact exists
- metadata sidecar exists
- inspection artifact exists
- source sections identity can be traced from sidecar and context contracts

Failure modes:
- missing review artifact in handoff package
- sidecar metadata missing required fields
- inspection artifact malformed or unreadable

---

## 6. Review Flow Failure Modes

| Failure Mode | Detection Point | Required Behavior |
| --- | --- | --- |
| sections-json missing | argument parse stage | command parse failure |
| sections-json malformed | deserialization stage | command failure with input correction required |
| missing project assets | loader validation stage | ProjectSkillsNotFound |
| prompt bundle invalid | validation stage | contract validation failure |
| output path not writable | artifact write stage | command failure with I/O error |

---

## 7. Validation Evidence Requirements

Required checks:
- argument parity check against cli/main.py
- review runner output naming check against review/runner.py
- prompt bundle validation flow check against prompts/context_builder.py
- project path validation behavior check against skills/project_ucx_loader.py

---

## 8. Constraints

- Review/remediation operational documentation must remain aligned with implemented prompt bundle and sidecar contracts.
- Any contract-impacting change requires quality gate revalidation and lifecycle policy-compliant version increment.
