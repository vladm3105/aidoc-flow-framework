---
title: "CHG-000: CHG Index"
tags:
  - index-document
  - change-management
  - shared-architecture
custom_fields:
  document_type: index
  artifact_type: CHG
  priority: shared
---

# CHG Index (Change Management Documents)

## Purpose

- Central index for Change Management (CHG) documents.
- Tracks allocation and sequencing for `CHG-NN_{descriptive}.yaml` descriptors.

## Allocation Rules

- Numbering: allocate sequentially starting at `01`; keep numbers stable.
- CHG documents define change requests, impact analysis, and approval workflows.
- Each CHG should link to affected artifacts across the SDD framework layers.
- CHG documents are created when changes require formal tracking and approval.

## Document Organization

- CHG documents focus on change classification, impact scope, and regeneration requirements
- Include change source, affected layers, and approval gates
- Reference upstream artifacts and downstream impacts

## Gates

| Gate | Layers | Artifacts | Entry for |
|------|--------|-----------|-----------|
| **GATE-01** | L1-L2 | BRD, PRD | upstream / external |
| **GATE-03** | L3-L5 | EARS, BDD, ADR | midstream |
| **GATE-06** | L6-L7 | SPEC, TDD | design |
| **GATE-08** | L8 | IPLAN | execution |
| **GATE-CODE** | Code | Source Code | feedback |
| **GATE-SPEC** | meta | `framework/` spec | spec |

## Documents

| ID | Title | Level | Source | Entry Gate | Status | Date Proposed |
|----|-------|-------|--------|-----------|--------|---------------|
| [CHG-01](./CHG-01.md) | Add visit-rate analytics dashboard | C3 | upstream | GATE-01 | Proposed | 2026-06-12 |

## Planned

| ID | Title | Priority | Target Date | Notes |
|----|-------|----------|-------------|-------|
| — | — | — | — | — |
