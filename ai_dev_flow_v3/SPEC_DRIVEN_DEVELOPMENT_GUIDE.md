# Specification-Driven Development Guide — SDD v3

## Overview

SDD v3 is a streamlined 7-layer documentation-to-code framework. Each layer produces one YAML document type, with cumulative traceability from business requirements to implementation specification.

```
BRD (L1) → PRD (L2) → EARS (L3) → BDD (L4) → ADR (L5) → TDD (L6) → SPEC (L7) → Code
```

## Layer Descriptions

| Layer | Artifact | Purpose | Upstream | Downstream |
|-------|----------|---------|----------|------------|
| L1 | BRD | Business requirements, objectives, scope | — | PRD |
| L2 | PRD | Product features, user stories, ADR topics | BRD | EARS |
| L3 | EARS | Formal requirements (WHEN-THE-SHALL-WITHIN) | BRD, PRD | BDD |
| L4 | BDD | Executable acceptance scenarios (Given-When-Then) | BRD, PRD, EARS | ADR, TDD |
| L5 | ADR | Architecture decisions (Context-Decision-Consequences) | BRD, PRD, EARS, BDD | TDD |
| L6 | TDD | Test pyramid, BDD-to-test mapping, TDD execution order | BRD, PRD, EARS, BDD, ADR | SPEC |
| L7 | SPEC | Component interfaces, data models, behavior, test contracts | BRD, PRD, EARS, BDD, ADR, TDD | Code |

## Cumulative Traceability

Each layer inherits tags from all upstream layers:

```
BRD: @brd
PRD: @brd @prd
EARS: @brd @prd @ears
BDD: @brd @prd @ears @bdd
ADR: @brd @prd @ears @bdd @adr
TDD: @brd @prd @ears @bdd @adr @tdd
SPEC: @brd @prd @ears @bdd @adr @tdd @spec
```

Maximum 6 cumulative tags at SPEC layer (vs 14 in SDD v2).

## Readiness Score Flow

Each layer must achieve >=90/100 readiness score before generating the next layer:

```
BRD → PRD-Ready (>=90) → PRD → EARS-Ready (>=90) → EARS → BDD-Ready (>=90)
→ BDD → ADR-Ready (>=90) → ADR → TDD-Ready (>=90) → TDD → SPEC-Ready (>=90)
→ SPEC → CODE-Ready (>=90) → Code
```

## What Was Cut from SDD v2

| Cut | Replaced By |
|-----|-------------|
| SYS (L6) | ADR captures architecture; PRD captures scope |
| REQ (L7) | EARS + BDD provide sufficient granularity |
| CTR (L8) | Only needed for multi-team API contracts |
| TSPEC (L10) 42-file suite | TDD (L6) single document per component |
| TASKS (L11) | AI generates tasks from SPEC on-the-fly |
| 09_SPEC/ subtypes (5 types) | Unified SPEC template |
| CHG/ gate system | Project-level concern |
