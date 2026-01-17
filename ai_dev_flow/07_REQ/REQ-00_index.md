---
title: "REQ-000: REQ Index"
tags:
  - index-document
  - layer-7-artifact
  - shared-architecture
custom_fields:
  document_type: index
  artifact_type: REQ
  layer: 7
  priority: shared
---

# Requirements Index (REQ)

## Document Control

| Item | Details |
|------|---------|
| **Template Version** | 3.0 |
| **Last Updated** | 2026-01-13 |
| **Layer** | 7 (Requirements) |
| **Status** | Active |

---

## Purpose

- Central index for formal requirements documents
- Tracks allocation and sequencing for `REQ-NN_{slug}.md` files
- Provides quick navigation to all framework and project requirements

## Allocation Rules

- **Numbering**: Allocate sequentially starting at `01`; keep numbers stable
- **Slugs**: Short, descriptive, lower_snake_case by functional area
- **Organization**: By category subtree: `07_REQ/api/`, `07_REQ/risk/`, `07_REQ/ml/`, `07_REQ/data/`, etc.
- **Traceability**: Each requirement links to upstream 02_PRD/EARS and downstream 06_SYS/10_SPEC/BDD
- **Template Selection**: Use MVP template (default) for rapid development; use full template for comprehensive requirements

## Organization

- **`api/`**: External API integration requirements
- **`data/`**: Data architecture and storage requirements
- **`auth/`**: Authentication and authorization requirements
- **`core/`**: Core business logic requirements

## Framework Templates

| Template | Version | Status | Description |
|----------|---------|--------|-------------|
| [REQ-MVP-TEMPLATE.md](REQ-MVP-TEMPLATE.md) | 1.0 | ✅ DEFAULT | Streamlined MVP template for rapid development (≥70% SPEC-Ready) |
| [REQ-TEMPLATE.md](REQ-TEMPLATE.md) | 3.0 | Archived | Full template available if enterprise/full is explicitly required |
| [REQ_VALIDATION_RULES.md](REQ_VALIDATION_RULES.md) | 3.0 | ✅ ACTIVE | V3 validation rules and fix guide |
| [REQ-00_TRACEABILITY_MATRIX-TEMPLATE.md](REQ-00_TRACEABILITY_MATRIX-TEMPLATE.md) | 3.0 | ✅ ACTIVE | Traceability matrix template |
| [REQ_SCHEMA.yaml](REQ_SCHEMA.yaml) | 1.1 | ✅ ACTIVE | YAML schema with MVP/full profile support |

## Example Requirements

| ID | Domain | File | Version | Description |
|----|--------|------|---------|-------------|
| REQ-01 | API | [examples/api/REQ-01_api_integration_example.md](examples/api/REQ-01_api_integration_example.md) | V2.1 | External API integration example |
| REQ-02 | Data | [examples/data/REQ-02_data_validation_example.md](examples/data/REQ-02_data_validation_example.md) | V2 | Data validation pipeline example |
| REQ-03 | Auth | [examples/auth/REQ-03_access_control_example.md](examples/auth/REQ-03_access_control_example.md) | V2 | RBAC access control example |

---

**Note**: Example files in `examples/` directory are for reference only and may use older template versions.

## Planned

- Use this section to list REQ documents planned but not yet created. Move rows to the main index areas when created.

| ID | Title | Source (03_EARS/SYS) | Priority | Notes |
|----|-------|--------------------|----------|-------|
| REQ-XX | … | 03_EARS/SYS-YY | High/Med/Low | … |
