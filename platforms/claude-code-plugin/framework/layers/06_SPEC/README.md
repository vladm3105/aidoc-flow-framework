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

## Specification Baseline

| Area | SPEC Standard |
|--------------------|-------------------|
| Metadata model | `schema_version: 1.0` unified model |
| Traceability | Flat upstream tags |
| Template model | Single unified template |
| Upstream | ADR + BDD |
| Downstream | TDD → IPLAN → Code |
| Document shape | 8 core sections |
| Readiness gate | TDD-Ready score |

## Template

See [SPEC-TEMPLATE.yaml](SPEC-TEMPLATE.yaml).
