---
title: "TDD-00: Test-Driven Development Index"
tags:
  - index-document
  - layer-7-artifact
  - shared-architecture
custom_fields:
  document_type: index-template
  artifact_type: TDD
  layer: 7
  priority: shared
  last_updated: "YYYY-MM-DD"
---

# TDD-00: Test-Driven Development Guide Index

> **Index template.** Copy this file to `TDD-00_index.md` in a project and
> populate the registry as TDD documents are created.

## Purpose

Central registry for all TDD documents. Each TDD document defines test cases, maps BDD acceptance scenarios to test implementation, and declares quality thresholds for a SPEC component.

## Position in Document Workflow

```
SPEC (L6)  ──►  TDD (L7)  ──►  IPLAN (L8)  ──►  Code
@spec            @spec           @spec
                 @adr            @adr
                 @bdd            @bdd
                 @tdd            @tdd
                                 @iplan
```

**Layer**: 7 (Test-Driven Development Layer)
**Upstream**: BRD, PRD, EARS, BDD, ADR, SPEC
**Downstream**: IPLAN (Implementation Plan, Layer 8)
**Traceability chain**: BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code

## Document Registry

| ID | Component | SPEC Ref | BDD Refs | ADR Refs | IPLAN Target | Status |
|----|-----------|----------|----------|----------|-------------|--------|
| - | - | - | - | - | - | No TDD documents created yet |

## Templates

- [TDD-TEMPLATE.yaml](TDD-TEMPLATE.yaml) — TDD guide template with test case definitions

## Quality Gate

TDD requires **IPLAN-Ready score >=90/100** before downstream IPLAN generation.

## TDD Execution Order

1. **Red**: Write failing test from TDD template test case definitions
2. **Green**: Write minimum code to pass
3. **Refactor**: Clean up without changing behavior
4. **Repeat**: Next test case from TDD document

## Test Case Categories

- **Positive**: Expected happy-path inputs → expected outputs
- **Negative**: Invalid/boundary inputs → expected error responses
- **Edge**: Edge cases and boundary conditions
- **Integration**: Cross-component interaction tests
- **Performance**: Performance-critical path tests

## Allocation Rules

- **Numbering**: Allocate sequentially starting at `01`
- **One TDD per SPEC component**: Each TDD corresponds to one SPEC
- **Filename**: `TDD-NN_{component_slug}.yaml`

## Related Documents

- **Upstream**: [06_SPEC](../06_SPEC/) — Technical Specifications
- **Downstream**: [08_IPLAN](../08_IPLAN/) — Implementation Plans

## Maintenance Notes

- One TDD document per SPEC component
- Update test cases when SPEC interfaces, data models, or behavior contracts change
- Update test mapping when BDD scenarios change
- Regenerate Phase 1 (test files) when ADR decisions change integration points

---

**Last Updated**: YYYY-MM-DD
