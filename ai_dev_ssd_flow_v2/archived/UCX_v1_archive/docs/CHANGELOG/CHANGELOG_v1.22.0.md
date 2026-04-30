# CHANGELOG v1.22.0

**Release Date**: Planned
**Type**: Minor (Workflow and Reporting Alignment)
**Status**: Planned scope snapshot

## Summary

This planned release aligns PRD creation, validation, review, remediation, and pre-commit behavior around an immutable-source workflow. The canonical PRD remains unchanged after creation, while validation, review, and remediation produce reports and copy-based derived artifacts with explicit lineage metadata.

## Planned Changes

### PRD Derived-Artifact Workflow (PLAN-012)

- Keep the canonical PRD as the only source artifact created by `ucx create prd`
- Keep `ucx validate prd` report-only
- Standardize PRD validation output as `PRD-01_validation_report.md`
- Add planned `ucx validate-fix prd` command to create `*_validation.md` copies
- Add planned `ucx remediate-apply prd` command to create `*_remediated.md` copies
- Preserve `doc_id` and semantic `version` across source and derived copies
- Track pipeline state with `custom_fields.processing_stage`

### Reporting and Lineage Alignment

- Keep review and remediation reports versioned
- Require report metadata to record the exact source artifact filename and processing stage
- Reserve `.precommit_validation_report.md` for commit-time diagnostics only
- Limit pre-commit checks to artifact availability and lineage consistency instead of rerunning validation logic

### Documentation and Plan Alignment

- Align [PLAN-009_prd_creation.md](../plans/PLAN-009_prd_creation.md) with canonical-source-only creation
- Align [PLAN-010_prd_validation.md](../plans/PLAN-010_prd_validation.md) with the planned fixed PRD validation artifact and derived-copy flow
- Align [PLAN-011_ucx_reporting_standards.md](../plans/PLAN-011_ucx_reporting_standards.md) with the PRD-specific exception defined by PLAN-012
- Update [README.md](../../README.md), [HOW_TO_USE.md](../HOW_TO_USE.md), and [ROADMAP.md](../ROADMAP.md) to separate current v1.21.6 behavior from planned v1.22.0 behavior

## Constraints

- Current released behavior in v1.21.6 remains source-protected, report-only validation
- This changelog file documents planned scope; it does not imply the PLAN-012 runtime changes are already implemented
- Generic cross-layer reporting rules remain in effect for non-PRD layers unless later generalized

## Acceptance Targets

- Source PRD never changes during validate, review, or remediation report generation
- Derived PRD copies carry correct `processing_stage`, `source_doc_id`, `source_version`, and `derived_from` metadata
- PRD report and artifact naming are deterministic and machine-checkable
- Pre-commit failures identify missing or inconsistent artifacts without duplicating full validation