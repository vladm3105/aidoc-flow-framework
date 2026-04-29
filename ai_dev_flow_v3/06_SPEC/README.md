# 06_SPEC — Technical Specification

## C4 Model Position

SPEC is the **C4-L3 (Component)** level in the C4 architecture model. Content describes component interfaces, data models, and behavior contracts — not architecture decisions (ADR) or code implementation (Code).

Required diagram tags: `@diagram: c4-l3`, `@diagram: dfd-l3`.

```text
Context (BRD)    — business environment, actors, boundaries       C4-L1
Container (PRD)  — product features, functional blocks            C4-L2
  └─ EARS/BDD    — formalize Context→Container transition
  └─ ADR         — decision bridge (no C4 level)
Component (SPEC) — interfaces, data models, behavior contracts   C4-L3 ← this layer
  └─ TDD/IPLAN   — implementation bridge (no C4 level)
Code             — source code                                    C4-L4
```

## Purpose

Implementation-ready technical specification for a single software component. Defines interfaces, data models, and behavior contracts before downstream TDD test cases are written.

## Design Decisions

- **Unified template** — no CSPEC/DSPEC/UXSPEC/PROCSPEC/RISKSPEC subtypes
- **Positioned at L6** — after ADR (architecture decisions) and before TDD (test definitions). Logical flow: decide architecture → specify components → define tests → implement.
- **Test contract references** — links to TDD layer (Layer 7) for test case definitions
- **Unified v1.0 metadata model** — same structure as all other layers

## What's Different from SPEC v2 (ai_dev_ssd_flow)

| SPEC v2 (14-layer) | SPEC v3.2 (8-layer) |
|--------------------|-------------------|
| schema_version 2.0, different metadata model | schema_version 1.0, unified model |
| Massive nested traceability tree | Flat upstream tags |
| 5 subtypes with separate templates | Single unified template |
| Upstream: REQ + CTR + SYS + ADR | Upstream: ADR + BDD |
| Downstream: TSPEC → TASKS → Code | Downstream: TDD → IPLAN → Code |
| 30+ subsections | 8 clean sections |
| Code-Ready score | TDD-Ready score |

## Template

See [SPEC-TEMPLATE.yaml](SPEC-TEMPLATE.yaml).
