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

Purpose

- Central index for Change Management (CHG) documents.
- Tracks allocation and sequencing for `CHG-NN_{descriptive}.md` descriptors.

Allocation Rules

- Numbering: allocate sequentially starting at `01`; keep numbers stable.
- CHG documents define change requests, impact analysis, and approval workflows.
- Each CHG should link to affected artifacts across the SDD framework layers.
- CHG documents are created when changes require formal tracking and approval.

Document Organization

- CHG documents focus on change classification, impact scope, and regeneration requirements
- Include change source, affected layers, and approval gates
- Reference upstream artifacts and downstream impacts

Templates

- [CHG-MVP-TEMPLATE.md](./CHG-MVP-TEMPLATE.md): Minimal viable CHG template (default)
- [CHG-TEMPLATE.md](./CHG-TEMPLATE.md): Full CHG template
- [CHG_MVP_CREATION_RULES.md](./CHG_MVP_CREATION_RULES.md): Creation rules for CHG documents
- [CHG_MVP_SCHEMA.yaml](./CHG_MVP_SCHEMA.yaml): Schema validation for CHG documents

Guides

- [CHANGE_MANAGEMENT_GUIDE.md](./CHANGE_MANAGEMENT_GUIDE.md): Comprehensive change management guide
- [CHANGE_CLASSIFICATION_GUIDE.md](./CHANGE_CLASSIFICATION_GUIDE.md): Change classification reference

Gates

- [gates/GATE-01_BUSINESS_PRODUCT.md](./gates/GATE-01_BUSINESS_PRODUCT.md): Business and Product gate (Layers 1-2)
- [gates/GATE-05_ARCHITECTURE_CONTRACT.md](./gates/GATE-05_ARCHITECTURE_CONTRACT.md): Architecture and Contract gate (Layers 5, 9)
- [gates/GATE-09_DESIGN_TEST.md](./gates/GATE-09_DESIGN_TEST.md): Design and Test gate (Layers 3-4, 8)
- [gates/GATE-12_IMPLEMENTATION.md](./gates/GATE-12_IMPLEMENTATION.md): Implementation gate (Layers 10-12)
- [gates/GATE_INTERACTION_DIAGRAM.md](./gates/GATE_INTERACTION_DIAGRAM.md): Gate interaction visualization
- [gates/GATE_ERROR_CATALOG.md](./gates/GATE_ERROR_CATALOG.md): Gate error codes and resolution

Workflows

- [workflows/UPSTREAM_WORKFLOW.md](./workflows/UPSTREAM_WORKFLOW.md): Upstream change workflow (BRD/PRD)
- [workflows/MIDSTREAM_WORKFLOW.md](./workflows/MIDSTREAM_WORKFLOW.md): Midstream change workflow (ADR/CTR)
- [workflows/DESIGN_WORKFLOW.md](./workflows/DESIGN_WORKFLOW.md): Design change workflow (EARS/BDD/SPEC)
- [workflows/DOWNSTREAM_WORKFLOW.md](./workflows/DOWNSTREAM_WORKFLOW.md): Downstream change workflow (TASKS/IPLAN)
- [workflows/EMERGENCY_WORKFLOW.md](./workflows/EMERGENCY_WORKFLOW.md): Emergency change workflow

Sources

- [sources/UPSTREAM_CHANGE_GUIDE.md](./sources/UPSTREAM_CHANGE_GUIDE.md): Upstream change source guide
- [sources/MIDSTREAM_CHANGE_GUIDE.md](./sources/MIDSTREAM_CHANGE_GUIDE.md): Midstream change source guide
- [sources/DOWNSTREAM_CHANGE_GUIDE.md](./sources/DOWNSTREAM_CHANGE_GUIDE.md): Downstream change source guide
- [sources/EXTERNAL_CHANGE_GUIDE.md](./sources/EXTERNAL_CHANGE_GUIDE.md): External change source guide
- [sources/FEEDBACK_CHANGE_GUIDE.md](./sources/FEEDBACK_CHANGE_GUIDE.md): Feedback change source guide

Templates (Additional)

- [templates/CHG-EMERGENCY-TEMPLATE.md](./templates/CHG-EMERGENCY-TEMPLATE.md): Emergency change template
- [templates/POST_MORTEM-TEMPLATE.md](./templates/POST_MORTEM-TEMPLATE.md): Post-mortem analysis template
- [templates/GATE_APPROVAL_FORM.md](./templates/GATE_APPROVAL_FORM.md): Gate approval form

Validation Scripts

- [scripts/validate_gate01.sh](./scripts/validate_gate01.sh): Gate 01 validation
- [scripts/validate_gate05.sh](./scripts/validate_gate05.sh): Gate 05 validation
- [scripts/validate_gate09.sh](./scripts/validate_gate09.sh): Gate 09 validation
- [scripts/validate_gate12.sh](./scripts/validate_gate12.sh): Gate 12 validation
- [scripts/validate_chg_routing.py](./scripts/validate_chg_routing.py): CHG routing validation
- [scripts/validate_emergency_bypass.sh](./scripts/validate_emergency_bypass.sh): Emergency bypass validation
- [scripts/validate_all_gates.sh](./scripts/validate_all_gates.sh): All gates validation

Documents

(No CHG documents created yet. Add entries here as new CHGs are created.)

## Planned

- Use this section to list CHGs planned but not yet created. Move rows to the documents table when created.

| ID | Title | Priority | Target Date | Notes |
|----|-------|----------|-------------|-------|
| CHG-XX | ... | High/Med/Low | YYYY-MM-DDTHH:MM:SS | ... |
