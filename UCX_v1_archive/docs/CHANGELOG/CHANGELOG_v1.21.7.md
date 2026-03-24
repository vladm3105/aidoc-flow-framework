# CHANGELOG v1.21.7

**Release Date**: 2026-03-22
**Type**: Patch (PRD Fixer Coverage and Handoff Alignment)

## Summary

This patch extends PRD fixer coverage for deterministic structural warnings and aligns PRD behavior with the fixer-to-LLM handoff model already used by BRD workflows.

## Changes

### PRD Fixer Coverage Expansion

**File**: `ucx/validators/prd/fixer.py`

Added deterministic handlers and dispatch wiring for these PRD warning codes:

- `PRD-W006`: missing Section 10 subsection skeletons
- `PRD-W011`: missing feature IDs in Section 7 tables (`PRD.NN.22.SS`)
- `PRD-W012`: missing/normalization of user story IDs in Section 8 tables (`PRD.NN.09.SS`)
- `PRD-W019`: missing quality attribute IDs in Section 21 tables (`PRD.NN.02.SS`)
- `PRD-W021`: missing Section 14 release/launch criteria checklist block

### Invalid Type-Code Guardrail (Section 14)

Updated `PRD-W021` fix template to avoid generating invalid type-code IDs in Section 14.

- Removed generated `PRD.NN.14.xx` and `PRD.NN.14.xx.yy` identifiers
- Section 14 checklist is now generated as structural content only (no element IDs)

This aligns with PRD section/type mapping where Section 14 has no valid element type codes.

### LLM Handoff Action Generation for PRD

Added PRD LLM handoff classification and manual action generation:

- `LLM_ONLY_CODES` added for semantic/manual remediation routing:
  - `PRD-W004` (traceability gaps)
  - `PRD-W009` (acceptance criteria semantics)
  - `PRD-W013` (user story format semantics)
  - `PRD-W014` (priority notation normalization)
- `LLM_COMPLETION_CODES` added for partial script + LLM completion context:
  - `PRD-W006`
  - `PRD-W021`
- New `_handoff_*` methods create `manual` `FixAction` records with explicit context for UCRem consumption.

## Documentation Updates

Updated:

- `README.md` version history and release pointers
- `docs/HOW_TO_USE.md` PRD validation section with fixer coverage and handoff boundaries

## Backward Compatibility

✅ Fully backward compatible

- Existing validate/review/remediate commands remain unchanged
- Fixer report format remains `UCX-ACTION` compatible
- New behavior only expands PRD fixer coverage and improves handoff fidelity

## Validation Notes

- `fixer.py` imports successfully after changes
- New PRD handoff methods return `manual` actions as expected
- `PRD-W021` template no longer emits invalid Section 14 IDs
