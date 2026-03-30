# CHANGELOG v0.11.0

**Release Date**: 2026-03-30
**Type**: Minor (TSPEC Template Unification)

## Summary

Unified the TSPEC (Layer 10) parent aggregator into a single YAML template. TSPEC aggregates 6 test specification subtypes. Ten SDD layers now unified.

## Changes

- **New**: `TSPEC-TEMPLATE.yaml` (263 lines, 6 sections + glossary)
- **Replaced**: Parent TSPEC files archived to `TSPEC_v1_archive/`
- **6 subtypes kept**: UTEST, ITEST, STEST, FTEST, PTEST, SECTEST directories unchanged
- **Test strategy**: Test pyramid concepts embedded in `_guidance`
- **mcp_sdd**: TSPEC-TEMPLATE.yaml ADDED (10 templates total)
- **Tests**: 173 passed, 0 regressions

## Ten Layers Unified

BRD → PRD → EARS → BDD → ADR → SYS → REQ → CTR → SPEC → TSPEC

Remaining: TASKS (Layer 11) — the final layer.
