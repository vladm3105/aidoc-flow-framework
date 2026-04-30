# CHANGELOG — Framework v0.20.0

**Release Date**: 2026-04-29

## Summary

SDD v3 migration: collapsed from 14 layers to 8 layers with C4 architecture mapping, new TDD and IPLAN artifacts, 5-gate CHG governance overlay, and 39 new framework files in `ucx_flow_v3/`.

## SDD v3 Layer Migration

### v3.0 — Layer Collapse (2026-04-28)

- Collapsed from 14 to 7 SDD layers: `BRD → PRD → EARS → BDD → ADR → TDD → SPEC`
- Cut: SYS (L6), REQ (L7), CTR (L8), TSPEC (L10, 42 subtype files), TASKS (L11), TESTS, VALIDATION
- SPEC promoted to L7 as unified single template — 5 subtypes dissolved (CSPEC, DSPEC, UXSPEC, RISKSPEC, PROCSPEC)
- TDD added as lightweight test-driven development guide (replaces TSPEC)
- Cumulative traceability tags reduced from 14 to 6 maximum

### v3.1 — IPLAN Execution Bridge (2026-04-29)

- Added IPLAN (L8) as mandatory execution bridge between TDD and Code
- File manifest with test-first creation order
- Stateless MCP executor session handoff protocol
- `IPLAN-TEMPLATE.yaml` (168 lines) and `IPLAN-00_index.yaml` (171 lines)

### v3.2 — Reordering + CHG Overlay (2026-04-29)

- Swapped SPEC and TDD layer positions: `ADR(L5) → SPEC(L6) → TDD(L7)` for logical spec-first ordering
- Expanded TDD template with test case definitions (inputs, outputs, edge cases)
- Added `spec_trace` field to BDD for req-to-SPEC trace links
- Added CHG governance overlay (see below)

## C4 Architecture Model Mapping

| C4 Level | SDD Layer | Artifact | Diagram Tags |
|----------|-----------|----------|-------------|
| C4-L1 Context | L1 | BRD | `@diagram: c4-l1`, `@diagram: dfd-l1` |
| C4-L2 Container | L2 | PRD | `@diagram: c4-l2`, `@diagram: dfd-l2` |
| Decision Bridge | L3-L5 | EARS, BDD, ADR | _(none)_ |
| C4-L3 Component | L6 | SPEC | `@diagram: c4-l3`, `@diagram: dfd-l3` |
| Implementation Bridge | L7-L8 | TDD, IPLAN | _(none)_ |
| C4-L4 Code | — | Source Code | `@diagram: c4-l4` |

Authoritative layer definitions in `ucx_flow_v3/LAYER_REGISTRY.yaml` (232 lines).

## CHG Governance Overlay

- New 5-gate change management system: GATE-01 (Business/Product), GATE-03 (Requirements/Architecture), GATE-06 (Design/Test), GATE-08 (IPLAN), GATE-CODE (Implementation)
- C1/C2/C3 change level naming — no collision with L1-L8 layer numbers
- 12 CHG files: template, index, README, 7 gate docs, 2 companion templates
- `GATE_INTERACTION_DIAGRAM.md` and `GATE_ERROR_CATALOG.md`
- `GATE_APPROVAL_FORM.md` and `POST_MORTEM-TEMPLATE.md`
- CHG migration plan: `ucx_flow_v3/plans/CHG_MIGRATION_PLAN.md` (357 lines)

## New Files — ucx_flow_v3/

**Framework core** (39 files):

| Directory | Files | Contents |
|-----------|-------|----------|
| Root | 10 | README, LAYER_REGISTRY.yaml, QUICK_REFERENCE, DIAGRAM_STANDARDS, ID_NAMING_STANDARDS, TRACEABILITY, THRESHOLD_NAMING_RULES, TESTING_STRATEGY_TDD, SPEC_DRIVEN_DEVELOPMENT_GUIDE, AI_ASSISTANT_RULES |
| 01_BRD/ | 3 | BRD-TEMPLATE.yaml (978 lines), BRD-00_index.md, README |
| 02_PRD/ | 3 | PRD-TEMPLATE.yaml (607 lines), PRD-00_index.md, README |
| 03_EARS/ | 3 | EARS-TEMPLATE.yaml (376 lines), EARS-00_index.md, README |
| 04_BDD/ | 3 | BDD-TEMPLATE.yaml (367 lines), BDD-00_index.md, README |
| 05_ADR/ | 3 | ADR-TEMPLATE.yaml (446 lines), ADR-00_index.md, README |
| 06_SPEC/ | 3 | SPEC-TEMPLATE.yaml (189 lines), SPEC-00_index.md, README |
| 07_TDD/ | 3 | TDD-TEMPLATE.yaml (266 lines), TDD-00_index.md, README |
| 08_IPLAN/ | 3 | IPLAN-TEMPLATE.yaml, IPLAN-00_index.yaml, README |
| CHG/ | 12 | CHG-TEMPLATE.yaml, CHG-00_index.md, README, 7 gate docs, 2 templates |
| plans/ | 2 | CHG_MIGRATION_PLAN.md, MIGRATION_PLAN_GAP_ANALYSIS.md |

## v2 Documentation Updates

- Fixed stale indexes in 24 ucx_flow_v3/ files (removed `_draft` suffixes, corrected cross-references)
- Updated layer count references from 14 to reflect v3 8-layer structure
- `ucx_flow_v3/README.md`: added v3 availability notice and cross-reference
- `ucx_flow_v3/PROJECT/PROJECT_MODEL.md`: 6 lines updated for dev/deploy separation
- `ucx_flow_v3/11_TASKS/IMPLEMENTATION_PLAN_README.md`: 5 lines updated for IPLAN handoff
- `ucx_flow_v3/11_TASKS/TASKS-00_index.md`: 3 lines updated

## mcp_ucx Template Updates

- Removed `_draft` prefix references from BRD, PRD, EARS templates

## Backward Compatibility

- v2 ucx_flow_v3/ preserved as-is — existing projects continue unaffected
- v3 is an opt-in migration for new projects
- v2 → v3 migration guidance in `ucx_flow_v3/plans/`
- CHG overlay follows same opt-in pattern — gates trigger only when CHG process is invoked
