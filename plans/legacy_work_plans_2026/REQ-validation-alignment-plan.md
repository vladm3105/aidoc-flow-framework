# Plan: REQ Validation & Creation Rules Alignment
Created: 2026-01-23 00:00
Last Updated: 2026-01-23 13:45
Owner: TBD
Approver: TBD
Due: TBD

## Objective
Align REQ MVP creation/validation artifacts to remove inconsistencies and prevent generator/validator drift.

## Scope
Files: ai_dev_flow/07_REQ/REQ_MVP_CREATION_RULES.md, ai_dev_flow/07_REQ/REQ_MVP_VALIDATION_RULES.md, ai_dev_flow/07_REQ/REQ_MVP_QUALITY_GATE_VALIDATION.md (and any referenced templates/README if needed for consistency).

## Tasks (with Acceptance Criteria)
1) Fix section numbering and MVP structure
- Action: Normalize to current MVP section list (11 sections) and remove duplicate numbering references. Do not include Change History for MVP.
- Acceptance:
  - No duplicate numbering (e.g., only one “12.” anywhere).
  - REQ_MVP_CREATION_RULES.md and REQ_MVP_VALIDATION_RULES.md reference the same MVP section list (no Change History for MVP).
  - REQ_MVP_QUALITY_GATE_VALIDATION.md references MVP sections consistently.

2) Align Document Control fields
- Action: Canonicalize MVP to 12 mandatory fields; keep Template Version informational (not validated); confirm Infrastructure Type is mandatory in creation and validation rules.
- Acceptance:
  - Field count is 12 across creation/validation docs and examples.
  - validate_req_template.sh requires the 12 MVP fields and treats Template Version as informational.
  - Category values and examples are synchronized across docs.

3) Harmonize status/score mapping (MVP-only)
- Action: Define explicit mapping for MVP and sync across docs and validator messages (full profile removed).
- MVP: ≥90% = Approved; 70–89% = In Review; <70% = Draft.
- Acceptance:
  - Mapping tables present in both creation and validation rules.
  - Examples and validator messages reflect the MVP thresholds (90/70 split).

4) Update corpus quality-gate sections (CORPUS-12)
- Action: Replace legacy “v3.0 12-section” enforcement with current MVP section structure; keep legacy model as non-blocking appendix if retained.
- Acceptance:
  - REQ_MVP_QUALITY_GATE_VALIDATION.md enforces MVP sections; legacy model clearly marked non-blocking or removed.

5) Clarify size/splitting thresholds (CORPUS-10)
- Action: Declare precise, consistent thresholds and severity; state required folder split on error.
- Recommended (align across artifacts): Lines → Warning ≥600, Error ≥1200. Tokens → Warning ≥15,000, Error ≥20,000.
- Acceptance:
  - Threshold tables updated and consistent; severity explicitly stated.
  - Error guidance includes “move to nested folder” action.

6) Schema/validator sync and references
- Action: Ensure REQ_MVP_SCHEMA.yaml min thresholds and fields match MVP (spec_ready_min=90); sync path conventions and examples; validate scripts/references.
- Acceptance:
  - validate_schema_sync.py passes for REQ.
  - Path mapping note present (ai_dev_flow uses type folders at repo root; no docs/ prefix in this repo).
  - Sample validations pass on provided examples with expected warnings/errors.

## Execution & Verification
- Template validator (single file):
  - `bash ai_dev_flow/07_REQ/scripts/validate_req_template.sh ai_dev_flow/07_REQ/examples/api/REQ-01_api_integration_example.md`
- SPEC-ready scoring (MVP ≥90):
  - `python3 ai_dev_flow/07_REQ/scripts/validate_req_spec_readiness.py --req-file ai_dev_flow/07_REQ/examples/api/REQ-01_api_integration_example.md --min-score 90`
- Schema sync (REQ):
  - `python3 ai_dev_flow/scripts/validate_schema_sync.py --type REQ`
- Repo-level validators (REQ only):
  - `python3 scripts/validate_all.py --type REQ`

## Risks/Notes
- Keep mirrored content consistent across creation/validation docs to avoid drift.
- Ensure changes don’t conflict with REQ-MVP-TEMPLATE.md; defer to template if ambiguity remains.
- Path conventions: In this repository, artifact folders live at ai_dev_flow root (no docs/ prefix). Update examples accordingly.

## Out of Scope
- Do not modify non-REQ CORPUS guides beyond clarifying threshold consistency references.
