# SPEC-00_index.md — Technical Specification Index

## Purpose

Central registry for all SPEC documents. Each SPEC defines the implementation contract for a single component: interfaces, data models, behavior, and test contract references.

## Document Registry

| ID | Component | ADR Ref | TDD Ref | Status |
|----|-----------|---------|---------|--------|
| SPEC-01 | [Template] | - | - | Template |

## Traceability Chain

```
BRD (L1) ─► PRD (L2) ─► EARS (L3) ─► BDD (L4) ─► ADR (L5) ─► TDD (L6) ─► SPEC (L7) ─► Code
```

## Templates

- [SPEC-TEMPLATE.yaml](SPEC-TEMPLATE.yaml) — Unified technical specification template

## Code-Ready Score

SPEC requires >=90/100 Code-Ready score before implementation begins:
- Interface completeness (30%)
- Data model clarity (25%)
- Behavior specification (20%)
- Test contract references (15%)
- Traceability (10%)

## Maintenance Notes

- One SPEC document per component
- Update interfaces when ADR decisions change
- Update test contracts when TDD mappings change
- Regenerate code from SPEC; do not edit generated code directly
