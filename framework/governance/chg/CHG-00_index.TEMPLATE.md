---
title: "CHG-000: CHG Index (TEMPLATE)"
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

> **Template.** Copy this file to `CHG-00_index.md` in a project's CHG
> directory and populate the registry as CHG documents are created.

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

## Templates

- [CHG-TEMPLATE.yaml](./CHG-TEMPLATE.yaml): Unified template (all change levels C1/C2/C3/Emergency)
- [gates/](./gates/): Gate definitions (GATE-01, 03, 06, 08, CODE)
- [templates/GATE_APPROVAL_FORM.md](./templates/GATE_APPROVAL_FORM.md): Gate approval companion
- [templates/POST_MORTEM-TEMPLATE.md](./templates/POST_MORTEM-TEMPLATE.md): Emergency post-mortem

## Gates

| Gate | Layers | Artifacts | File |
|------|--------|-----------|------|
| **GATE-01** | L1-L2 | BRD, PRD | [gates/GATE-01_BUSINESS_PRODUCT.md](./gates/GATE-01_BUSINESS_PRODUCT.md) |
| **GATE-03** | L3-L5 | EARS, BDD, ADR | [gates/GATE-03_REQUIREMENTS_ARCHITECTURE.md](./gates/GATE-03_REQUIREMENTS_ARCHITECTURE.md) |
| **GATE-06** | L6-L7 | SPEC, TDD | [gates/GATE-06_DESIGN_TEST.md](./gates/GATE-06_DESIGN_TEST.md) |
| **GATE-08** | L8 | IPLAN | [gates/GATE-08_IPLAN.md](./gates/GATE-08_IPLAN.md) |
| **GATE-CODE** | Code | Source Code | [gates/GATE-CODE_IMPLEMENTATION.md](./gates/GATE-CODE_IMPLEMENTATION.md) |

## Reference

- [gates/GATE_INTERACTION_DIAGRAM.md](./gates/GATE_INTERACTION_DIAGRAM.md): Gate interaction visualization
- [gates/GATE_ERROR_CATALOG.md](./gates/GATE_ERROR_CATALOG.md): Gate error codes and resolution

## Documents

(No CHG documents created yet. Add entries here as new CHGs are created.)

## Planned

| ID | Title | Priority | Target Date | Notes |
|----|-------|----------|-------------|-------|
| CHG-XX | ... | High/Med/Low | YYYY-MM-DDTHH:MM:SS | ... |
