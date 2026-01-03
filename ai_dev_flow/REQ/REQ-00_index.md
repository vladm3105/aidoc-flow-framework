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
| **Last Updated** | 2025-11-19 |
| **Layer** | 7 (Requirements) |
| **Status** | Active |

---

## Purpose

- Central index for formal requirements documents
- Tracks allocation and sequencing for `REQ-NN_{slug}.md` files
- Provides quick navigation to all framework and project requirements

## Allocation Rules

- **Numbering**: Allocate sequentially starting at `001`; keep numbers stable
- **Slugs**: Short, descriptive, lower_snake_case by functional area
- **Organization**: By category subtree: `REQ/api/`, `REQ/risk/`, `REQ/ml/`, `REQ/data/`, etc.
- **Traceability**: Each requirement links to upstream PRD/EARS and downstream SYS/SPEC/BDD
- **Template Version**: All new REQs use Template V3.0

## Organization

- **`api/`**: External API integration requirements
- **`data/`**: Data architecture and storage requirements
- **`auth/`**: Authentication and authorization requirements
- **`core/`**: Core business logic requirements

## Framework Templates

| Template | Version | Status | Description |
|----------|---------|--------|-------------|
| [REQ-TEMPLATE.md](REQ-TEMPLATE.md) | 3.0 | ✅ CURRENT | Enhanced SPEC-ready template with Layer 7, absolute paths |
| [archived/REQ-TEMPLATE-V2-ARCHIVED.md](archived/REQ-TEMPLATE-V2-ARCHIVED.md) | 2.0 | 📦 ARCHIVED | Legacy V2 template (archived 2025-11-19) |
| [REQ_VALIDATION_RULES.md](REQ_VALIDATION_RULES.md) | 3.0 | ✅ ACTIVE | V3 validation rules and fix guide |
| [REQ-00_TRACEABILITY_MATRIX-TEMPLATE.md](REQ-00_TRACEABILITY_MATRIX-TEMPLATE.md) | 3.0 | ✅ ACTIVE | Traceability matrix template |

## Example Requirements

| ID | Domain | File | Version | Description |
|----|--------|------|---------|-------------|
| REQ-01 | API | [examples/api/REQ-01_api_integration_example.md](examples/api/REQ-01_api_integration_example.md) | V2.1 | External API integration example |
| REQ-02 | Data | [examples/data/REQ-02_data_validation_example.md](examples/data/REQ-02_data_validation_example.md) | V2 | Data validation pipeline example |
| REQ-03 | Auth | [examples/auth/REQ-03_access_control_example.md](examples/auth/REQ-03_access_control_example.md) | V2 | RBAC access control example |

---

**Note**: Example files in `examples/` directory are for reference only and may use older template versions.
