# CHANGELOG v0.11.0

**Release Date**: 2026-03-30
**Type**: Minor (TSPEC Template Unification)

## Summary

Unified the TSPEC (Layer 10) parent aggregator into a single YAML template. TSPEC aggregates 6 test specification subtypes. Ten SDD layers now unified.

## Changes

- **New**: `TSPEC-TEMPLATE.yaml` (507 lines, 6 sections + glossary + subtype structure)
- **6 subtypes INTEGRATED** into parent template:
  - Shared 6-section structure (sections 1-4, 6 identical) defined once
  - Per-type overrides for Section 5 (coverage matrix) and Appendix
  - 42 subtype files (7 per type × 6 types) archived to `TSPEC_v1_archive/`
  - 95% context savings vs 6 separate templates
- **Parent TSPEC files**: archived to `TSPEC_v1_archive/`
- **Test strategy**: Test pyramid concepts + coverage requirements embedded in `_guidance`
- **mcp_ucx**: TSPEC-TEMPLATE.yaml ADDED (10 templates total)
- **Tests**: 173 passed, 0 regressions

## Ten Layers Unified

BRD → PRD → EARS → BDD → ADR → SYS → REQ → CTR → SPEC → TSPEC

Remaining: TASKS (Layer 11) — the final layer.
