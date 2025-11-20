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
- Tracks allocation and sequencing for `REQ-NNN_{slug}.md` files
- Provides quick navigation to all framework and project requirements

## Allocation Rules

- **Numbering**: Allocate sequentially starting at `001`; keep numbers stable
- **Slugs**: Short, descriptive, lower_snake_case by functional area
- **Organization**: By category subtree: `REQ/api/`, `REQ/risk/`, `REQ/ml/`, `REQ/data/`, etc.
- **Traceability**: Each requirement links to upstream PRD/EARS and downstream SYS/SPEC/BDD
- **Template Version**: All new REQs use Template V3.0

## Organization

- **`api/`**: External API integration requirements (brokers, data vendors)
- **`risk/`**: Risk management and validation requirements
- **`ml/`**: Machine learning model requirements
- **`data/`**: Data architecture and storage requirements

## Framework Templates

| Template | Version | Status | Description |
|----------|---------|--------|-------------|
| [REQ-TEMPLATE.md](REQ-TEMPLATE.md) | 3.0 | ✅ CURRENT | Enhanced SPEC-ready template with Layer 7, absolute paths |
| [archived/REQ-TEMPLATE-V2-ARCHIVED.md](archived/REQ-TEMPLATE-V2-ARCHIVED.md) | 2.0 | 📦 ARCHIVED | Legacy V2 template (archived 2025-11-19) |
| [REQ-VALIDATION-RULES.md](REQ-VALIDATION-RULES.md) | 3.0 | ✅ ACTIVE | V3 validation rules and fix guide |
| [REQ-000_TRACEABILITY_MATRIX-TEMPLATE.md](REQ-000_TRACEABILITY_MATRIX-TEMPLATE.md) | 3.0 | ✅ ACTIVE | Traceability matrix template |

## Example Requirements

| ID | Domain | File | Version | Description |
|----|--------|------|---------|-------------|
| REQ-001 | API/AV | [examples/api/av/REQ-001_alpha_vantage_integration.md](examples/api/av/REQ-001_alpha_vantage_integration.md) | V2 | Alpha Vantage API integration |
| REQ-002 | API/IB | [examples/api/ib/REQ-002_ib_gateway_integration.md](examples/api/ib/REQ-002_ib_gateway_integration.md) | V2 | IB Gateway integration |
| REQ-003 | Risk/Limits | [examples/risk/lim/REQ-003_position_limit_enforcement.md](examples/risk/lim/REQ-003_position_limit_enforcement.md) | V1 | Position limit enforcement |
| REQ-001 | API | [examples/api/REQ-001_api_integration_example.md](examples/api/REQ-001_api_integration_example.md) | V2 | Complete API integration example |
| REQ-002 | Data | [examples/data/REQ-002_data_validation_example.md](examples/data/REQ-002_data_validation_example.md) | V2 | Data validation pipeline example |
| REQ-003 | Auth | [examples/auth/REQ-003_access_control_example.md](examples/auth/REQ-003_access_control_example.md) | V2 | RBAC access control example |

---

**Note**: Example files in `examples/` directory are for reference only and may use older template versions.
