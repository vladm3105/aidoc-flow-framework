# CHANGELOG v0.7.0

**Release Date**: 2026-03-29
**Type**: Minor (SYS Template Unification — C4 Component Level)

## Summary

Unified the SYS (Layer 6) artifact into a single YAML template. SYS is the first C4 Component level layer — it defines system structure, interfaces, and quality attributes. Six SDD layers now unified.

## Changes

### SYS Layer Unification

**New**: `ai_dev_ssd_flow/06_SYS/SYS-TEMPLATE.yaml` (437 lines, schema v1.0)

**Replaced**: 6 files (3,785 lines → 437 lines). 17+ files archived to `SYS_v1_archive/`.

### Section Structure (15 → 12 + glossary)

| Removed/Merged | Action |
|----------------|--------|
| Section 10 (Compliance) | Merged into Section 5 (Quality Attributes) |
| Section 14 (Implementation Notes) | Removed (SPEC/TASKS own this) |
| Section 15 (Change History) | Merged into Section 1 (revision_history) |

### C4 Component Level

First layer with `c4_level.value: component` since PRD (container).
Diagram tags: `c4-l3`, `dfd-l3`, `sequence-sync`.

### Quality Attributes (6 Categories)

Performance, Reliability, Scalability, Security, Observability, Maintainability — all with measurable metrics and `@threshold:` references.

### Other Changes

- Hash-based IDs: `SYS.NN.{section}.xxxx`
- REQ-Ready score (dropped stale ears_ready_score)
- Old `@adr: ADR-NN` → `@adr: ADR.NN.03.xxxx` (hash format)
- BRD downstream SYS description updated (removed stale section ref)
- mcp_ucx: SYS-TEMPLATE.yaml copied, SYS-MVP-TEMPLATE.md removed

## Six Layers Unified

| Layer | C4 Position | Template | Readiness | Version |
|-------|-------------|----------|-----------|---------|
| BRD | Context | `BRD-TEMPLATE.yaml` | PRD-Ready | v0.2.0 |
| PRD | Container | `PRD-TEMPLATE.yaml` | EARS-Ready | v0.3.0 |
| EARS | Transition | `EARS-TEMPLATE.yaml` | BDD-Ready | v0.4.0 |
| BDD | Transition | `BDD-TEMPLATE.yaml` | ADR-Ready | v0.5.0 |
| ADR | Bridge | `ADR-TEMPLATE.yaml` | SYS-Ready | v0.6.0 |
| SYS | **Component** | `SYS-TEMPLATE.yaml` | REQ-Ready | v0.7.0 |

## Validation

- mcp_ucx: 173 passed, 0 regressions
- Template resolution: verified
- Zero stale references
