# CHANGELOG v1.21.3

**Release Date**: 2026-03-20
**Type**: Patch

## Summary

This release fixes the remaining canonical-path prompt history nesting issue for `ucx create prd` and updates UCX documentation/planning artifacts to match the final PRD create/validate runtime behavior.

## Changes

### 1. Canonical Prompt-Session Folder Fix

**Problem**:
When `ucx create prd` was called with the full canonical PRD file path, document output was written correctly, but prompt history was still saved under an extra nested slug directory.

**Before**:
- Document: `docs/02_PRD/PRD-01_platform_architecture/PRD-01_platform_architecture.md`
- Prompt history: `docs/02_PRD/PRD-01_platform_architecture/PRD-01_platform_architecture/.ucx_create_session/`

**After**:
- Document: `docs/02_PRD/PRD-01_platform_architecture/PRD-01_platform_architecture.md`
- Prompt history: `docs/02_PRD/PRD-01_platform_architecture/.ucx_create_session/`

### 2. Regression Coverage Added

Added focused tests for:
- canonical-path prompt-session placement
- plain slugged filename prompt-session placement
- previously added prompt merge and guardrail behaviors

### 3. Documentation and Plan Alignment

Updated documentation to reflect the implemented create/validate baseline:
- framework + project prompt merge for PRD creation
- pre-write PRD metadata and identity guardrails
- canonical `.ucx_create_session/` location for canonical paths
- current validation report path: `.precommit_validation_report.md`
- PLAN-010 updated to keep validation rules/scripts compliant with creation behavior

## Files Changed

- `ucx/api/creation.py`
- `tests/creation/test_prd_creation.py`
- `README.md`
- `docs/HOW_TO_CREATE_PRD.md`
- `docs/HOW_TO_USE.md`
- `docs/plans/PLAN-010_prd_validation.md`

## Validation

Focused regression tests passed:
- `tests/creation/test_prd_creation.py`
- Result: 5 passed

Live runtime verification also passed:
- `ucx --cli-tool codex create prd ... --validate`
- `ucx validate prd ...`
- Result: `Status: PASSED`, `Errors: 0`, `Warnings: 0`
