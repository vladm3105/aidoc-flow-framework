# Requirements Index (REQ)

Purpose

- Central index for formal requirements documents.
- Tracks allocation and sequencing for `REQ-NNN_{slug}.md` files.

Allocation Rules

- Numbering: allocate sequentially starting at `001`; keep numbers stable.
- Slugs: short, descriptive, lower_snake_case by functional area.
- Organize by category subtree: `reqs/api/`, `reqs/risk/`, `reqs/ml/`, `reqs/data/`, etc.
- Each requirement should link to upstream PRD/EARS and downstream SYS/SPEC/BDD.

Organization

- `api/`: External API integration requirements (brokers, data vendors)
- `risk/`: Risk management and validation requirements
- `ml/`: Machine learning model requirements
- `data/`: Data architecture and storage requirements

Documents

- Template
  - Descriptor: [REQ-TEMPLATE.md](./REQ-TEMPLATE.md)
- API / Alpha Vantage
  - Descriptor: [REQ-001_alpha_vantage_integration.md](./api/av/REQ-001_alpha_vantage_integration.md)
- API / IB Gateway
  - Descriptor: [REQ-002_ib_gateway_integration.md](./api/ib/REQ-002_ib_gateway_integration.md)
- Risk / Limits
  - Descriptor: [REQ-003_position_limit_enforcement.md](./risk/lim/REQ-003_position_limit_enforcement.md)
