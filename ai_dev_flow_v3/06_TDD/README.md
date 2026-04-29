# 06_TDD — Test-Driven Development Guide

## Purpose

Bridges BDD acceptance scenarios (Layer 4) to test implementation ordering. Each TDD document defines the test pyramid, maps BDD scenarios to test types and file paths, and declares the TDD execution order enforced by AI code generation.

## Design Decisions

- **Single template, no subtypes** — replaces the 42-file TSPEC v1 archive (6 subtypes × ~7 files each)
- **Test-first enforcement** — test files are generated BEFORE implementation files
- **BDD as source of truth** — no new behavior descriptions; maps existing BDD scenarios to test types
- **One document per SPEC component** — same granularity as SPEC for minimal maintenance

## What's Different from TSPEC v1

| TSPEC v1 (archived) | TDD v3 |
|---------------------|--------|
| 6 subtypes (UTEST, ITEST, STEST, FTEST, PTEST, SECTEST) | Single unified template |
| 6 validation scripts + 6 quality gate calculators | No separate validation scripts |
| 9 cumulative traceability tags per subtype | Flat BDD ↔ ADR upstream |
| Separate coverage matrices per subtype | Single BDD-to-test mapping table |
| 42 files total | 3 files (template, index, README) |

## Template

See [TDD-TEMPLATE.yaml](TDD-TEMPLATE.yaml).
