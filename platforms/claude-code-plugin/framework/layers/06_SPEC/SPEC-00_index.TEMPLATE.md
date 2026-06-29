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
**Upstream (necessary)**: EARS, BDD, ADR — BRD/PRD are reachable transitively (one hop per layer), not direct upstream (necessary-upstream contract, NECESSARY-UPSTREAM-001).
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

## Coverage

Backward-coverage contract (CFB-PR-2b): every upstream EARS/BDD requirement must
be **realized** by a downstream SPEC or TDD — a requirement or acceptance
scenario that nothing designs or tests is a coverage gap. This is the backward
dual of the BRD forward-coverage rule (the BRD-template `_authored_form` rule;
`COV01`).

- **Enforced deterministically** by `sdd_doc_lint` finding `COV02` (the
  structural tier beneath GATE-06): an EARS/BDD requirement **element** that is
  cited element-level by no realizing layer is flagged — a **warning** in
  `build` mode, an **error** in `gate-code`. Reviewed at **GATE-06** (Design &
  Test).
- **Element-level binding** (ELEMENT-COVERAGE-001): `COV02` asserts each
  declared EARS/BDD *element* (not just its host doc) is picked up by a doc in
  its **realizing set** — a curated, one-hop downstream-realization map: a BDD
  scenario is realized by **SPEC/TDD**; an EARS requirement by **BDD/SPEC/TDD**
  (ADR is a decision layer and does not realize). This catches orphaned
  scenarios a doc-level check misses (one cited sibling no longer covers the
  whole doc).
- The matching forward direction (BRD FR → SPEC/IPLAN) is `COV01`, also
  element-level: each AUTHORED FR element must be cited by a **PRD** (then the
  host BRD's SPEC + IPLAN reach is retained). Both read the same `@`-tag graph
  (`tools/sdd_coverage.py` / `governance/TRACEABILITY.md`).

## Maintenance Notes

- One SPEC document per component
- Update interfaces when ADR decisions change
- Update downstream TDD references when test mappings change

---

**Last Updated**: YYYY-MM-DD
