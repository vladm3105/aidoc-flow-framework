---
title: "SPEC-00: Technical Specification Index"
tags:
  - index-document
  - layer-6-artifact
  - shared-architecture
custom_fields:
  document_type: index-template
  artifact_type: SPEC
  layer: 6
  priority: shared
  last_updated: "YYYY-MM-DD"
---

# SPEC-00: Technical Specification Index

> **Index template.** Copy this file to `SPEC-00_index.md` in a project and
> populate the registry as SPEC documents are created.

## Purpose

Central registry for all SPEC documents. Each SPEC defines the implementation contract for a single component: interfaces, data models, behavior contracts, and downstream TDD contract references.

## Position in Document Workflow

**Layer**: 6 (Technical Specification Layer)
**Upstream**: BRD, PRD, EARS, BDD, ADR
**Downstream**: TDD (Test-Driven Development, Layer 7)
**Traceability chain**: BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code

## Document Registry

| ID | Component | ADR Ref | TDD Target | Status |
|----|-----------|---------|-----------|--------|
| - | - | - | - | No SPEC documents created yet |

## Templates

- [SPEC-TEMPLATE.yaml](SPEC-TEMPLATE.yaml) — Unified technical specification template (no subtypes — single unified SPEC)

## Quality Gate

SPEC requires **TDD-Ready score >=90/100** before downstream TDD generation:

| Criteria | Weight |
|----------|--------|
| Interface completeness | 30% |
| Data model clarity | 25% |
| Behavior specification | 20% |
| Downstream TDD contract references | 15% |
| Traceability | 10% |

## Allocation Rules

- **Numbering**: Allocate sequentially starting at `01`
- **One component per file**: Each SPEC covers a single component
- **Filename**: `SPEC-NN_{component_slug}.yaml`
- **Hash-based element IDs**: Format `SPEC.NN.SS.xxxx`

## Related Documents

- **Upstream**: [05_ADR](../05_ADR/) — Architecture Decision Records
- **Downstream**: [07_TDD](../07_TDD/) — Test-Driven Development Guide

## Maintenance Notes

- One SPEC document per component
- Update interfaces when ADR decisions change
- Update downstream TDD references when test mappings change

---

**Last Updated**: YYYY-MM-DD
