# CHANGELOG v0.8.0

**Release Date**: 2026-03-29
**Type**: Minor (REQ Template Unification — All mcp_ucx Templates Unified)

## Summary

Unified the REQ (Layer 7) artifact into a single YAML template. This completes the migration of ALL templates in `mcp_ucx/templates/` to unified YAML format — no `*-MVP-TEMPLATE.*` files remain.

## Changes

### REQ Layer Unification

**New**: `ai_dev_ssd_flow/07_REQ/REQ-TEMPLATE.yaml` (350 lines, schema v1.0)

**Replaced**: 6 files (4,175 lines → 350 lines). 20+ files archived to `REQ_v1_archive/`.

### Section Structure (11 → 10 + glossary)

Implementation Notes (Section 11) removed — SPEC/TASKS own implementation.

### Key REQ Features

- **Atomic principle**: ONE testable concept per document
- **SPEC-Ready score**: downstream readiness (>=90/100)
- **No C4 level**: decomposition step between Component (SYS) and Code (SPEC)
- **No diagram tags**: atomic requirement level, not architecture
- **Hash-based IDs**: `REQ.NN.{section}.xxxx`

### mcp_ucx Milestone

All 7 templates in `mcp_ucx/templates/` are now unified YAML:
- `BRD-TEMPLATE.yaml`, `PRD-TEMPLATE.yaml`, `EARS-TEMPLATE.yaml`
- `BDD-TEMPLATE.yaml`, `ADR-TEMPLATE.yaml`, `SYS-TEMPLATE.yaml`
- `REQ-TEMPLATE.yaml`

No `*-MVP-TEMPLATE.*` files remain.

## Seven Layers Unified

| Layer | C4 Position | Template | Lines | Readiness | Version |
|-------|-------------|----------|-------|-----------|---------|
| BRD | Context | `BRD-TEMPLATE.yaml` | 934 | PRD-Ready | v0.2.0 |
| PRD | Container | `PRD-TEMPLATE.yaml` | 605 | EARS-Ready | v0.3.0 |
| EARS | Transition | `EARS-TEMPLATE.yaml` | 387 | BDD-Ready | v0.4.0 |
| BDD | Transition | `BDD-TEMPLATE.yaml` | 365 | ADR-Ready | v0.5.0 |
| ADR | Bridge | `ADR-TEMPLATE.yaml` | 466 | SYS-Ready | v0.6.0 |
| SYS | Component | `SYS-TEMPLATE.yaml` | 437 | REQ-Ready | v0.7.0 |
| REQ | Decomposition | `REQ-TEMPLATE.yaml` | 350 | SPEC-Ready | v0.8.0 |

## Validation

- mcp_ucx: 173 passed, 0 regressions
- Template resolution: verified
- Zero stale references
