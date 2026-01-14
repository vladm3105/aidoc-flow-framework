---
title: "SPEC Splitting Rules"
tags:
  - framework-guide
  - shared-architecture
  - layer-10-artifact
custom_fields:
  document_type: splitting-rules
  artifact_type: SPEC
  priority: shared
  development_status: active
  version: 1.0
  last_updated: 2025-12-28
---

# SPEC Splitting Rules

Purpose: Extend the core splitting rules for SPEC artifacts. SPEC YAML is the single machine-readable source for code generation and MUST remain monolithic per component. When a SPEC needs more narrative, rationale, or operational detail, split the Markdown only. Read with DOCUMENT_SPLITTING_RULES.md.

## Policy Summary

- YAML: Keep monolithic per `SPEC-{DOC_NUM}`. Do not split YAML into multiple files unless a toolchain explicitly supports includes and you document it (not recommended).
- Markdown: Split as needed for readability and audience-specific content.
- DOC_NUM: Variable-length starting at 2 digits (01, 02, 99, 100, 1000).

## When To Split (Markdown Only)

- Narrative exceeds ~25–30KB or will grow rapidly.
- Multiple audiences (architecture, QA, ops) need focused sections.
- You need to include diagrams, runbooks, validation evidence, or CTR examples.

## Structure And Naming (Markdown Sections)

- Canonical ID: `SPEC-{DOC_NUM}` remains the identifier for the component.
- Index (recommended when split): `SPEC-{DOC_NUM}.0_index.md` from `SPEC-SECTION-0-TEMPLATE.md`.
- Section files: `SPEC-{DOC_NUM}.{S}_{slug}.md` (S starts at 1 and increments contiguously).
- YAML file path (monolithic): keep as either nested default or flat exception:
  - Nested default: `SPEC/SPEC-{DOC_NUM}_{slug}/SPEC-{DOC_NUM}_{slug}.yaml`
  - Flat exception: `SPEC/SPEC-{DOC_NUM}_{slug}.yaml` (for small, stable specs)

## Cross‑References

- Markdown sections reference the monolithic YAML using relative links.
- CTR references inside YAML prefer `contract_id` with optional `contract_ref` path fallback.
- Maintain stable IDs and paths; avoid circular references.

## Validation

- Link check: `python3 ./scripts/validate_links.py`
- Cross‑doc coherence: `python3 ./scripts/validate_cross_document.py`
- SPEC YAML schema validation: `python3 ./scripts/validate_spec.py <SPEC YAML>`

## Migration Checklist (YAML stays monolithic)

1) Do not split the YAML. Keep the existing `SPEC-{DOC_NUM}_{slug}.yaml` as-is.
2) Create `SPEC-{DOC_NUM}.0_index.md` from `SPEC-SECTION-0-TEMPLATE.md`.
3) Add Markdown sections: `SPEC-{DOC_NUM}.1_{slug}.md`, `SPEC-{DOC_NUM}.2_{slug}.md`, as needed.
4) Move narrative/rationale/ops content out of the YAML into Markdown sections where appropriate.
5) Ensure traceability is complete in YAML; mirror high-level tags in Markdown for navigation.
6) Run link and cross-document validators.

Notes:
- Keep component boundaries intact—never split a single component across multiple canonical IDs.
- If referencing CTR schemas, ensure version alignment and compatible changes are clearly noted.
