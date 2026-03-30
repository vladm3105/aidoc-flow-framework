# CHANGELOG v0.10.0

**Release Date**: 2026-03-29
**Type**: Minor (SPEC Template Unification — C4 Code Level Complete)

## Summary

Unified the SPEC (Layer 9) artifact. SPEC is the C4 Code level — the fourth and
final C4 level. All four C4 levels now have unified templates:
Context (BRD) → Container (PRD) → Component (SYS) → Code (SPEC).

## Changes

- **New**: `SPEC-TEMPLATE.yaml` (1,672 lines — largest template, includes full implementation spec structure)
- **Replaced**: 5 parent SPEC files + scripts/ + examples/ archived to `SPEC_v1_archive/`
- **Subtypes kept**: CSPEC, DSPEC, UXSPEC, RISKSPEC, PROCSPEC directories unchanged
- **C4 Code level**: `c4_level.value: code`, diagrams: c4-l4, dfd-l4, class diagrams
- **Orchestrator**: Routes to subtypes via `deliverable_type` (code→CSPEC, document→DSPEC, etc.)
- **Readiness scores per subtype**: TASKS-Ready (CSPEC), DOC-Ready (DSPEC), etc.
- **mcp_sdd**: SPEC-TEMPLATE.yaml ADDED (9 templates total)
- **Tests**: 173 passed, 0 regressions

## Nine Layers Unified — C4 Model Complete

| C4 Level | Layer | Template |
|----------|-------|----------|
| **Context** | BRD | `BRD-TEMPLATE.yaml` |
| **Container** | PRD | `PRD-TEMPLATE.yaml` |
| — | EARS, BDD | Transition |
| — | ADR | Bridge |
| **Component** | SYS | `SYS-TEMPLATE.yaml` |
| — | REQ, CTR | Decomposition |
| **Code** | SPEC | `SPEC-TEMPLATE.yaml` |

Remaining: TSPEC (Layer 10), TASKS (Layer 11)
