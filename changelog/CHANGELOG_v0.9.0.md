# CHANGELOG v0.9.0

**Release Date**: 2026-03-29
**Type**: Minor (CTR Template Unification)

## Summary

Unified the CTR (Layer 8) artifact into a single YAML template. CTR instances remain dual-file (.md narrative + .yaml OpenAPI). Eight SDD layers now unified.

## Changes

- **New**: `CTR-TEMPLATE.yaml` (350 lines, 11 sections + glossary)
- **Replaced**: 6 files (3,049 lines). Archived to `CTR_v1_archive/`
- **Sections**: 14 + 2 appendices → 11 (refs merged into traceability, appendices removed)
- **mcp_sdd**: CTR template ADDED (was missing — first CTR template in mcp_sdd)
- **Cross-ref**: Updated ADR-CTR_SEPARATE_FILES_POLICY.md stale template refs
- **Key features**: Dual-file instances, SemVer versioning, circuit breaker, OpenAPI 3.x
- **Tests**: 173 passed, 0 regressions

## Eight Layers Unified

BRD → PRD → EARS → BDD → ADR → SYS → REQ → CTR (all unified YAML)

Remaining: SPEC (Layer 9), TSPEC (Layer 10), TASKS (Layer 11)
