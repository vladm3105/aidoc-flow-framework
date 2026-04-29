# TDD-00_index.md — Test-Driven Development Guide Index

## Purpose

Central registry for all TDD documents. Each TDD document maps BDD acceptance scenarios to test implementation ordering for a SPEC component.

## Document Registry

| ID | Component | BDD Refs | ADR Refs | SPEC Target | Status |
|----|-----------|----------|----------|-------------|--------|
| TDD-01 | [Template] | - | - | - | Template |

## Traceability Chain

```
BDD (L4)  ──►  TDD (L6)  ──►  SPEC (L7)  ──►  Code
@bdd            @bdd           @bdd
                @adr           @adr
                               @tdd
                               @spec
```

## Templates

- [TDD-TEMPLATE.yaml](TDD-TEMPLATE.yaml) — Lightweight TDD guide template

## Maintenance Notes

- One TDD document per SPEC component
- Update test mapping when BDD scenarios change
- Regenerate Phase 1 (test files) when ADR decisions change integration points
