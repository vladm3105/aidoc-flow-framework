# REQ-003: [RESOURCE_LIMIT - e.g., request quota, concurrent sessions] Enforcement
@adr:[ADR-033](../../../../ADR/ADR-033_risk_limit_enforcement_architecture.md#ADR-033)
@PRD:[PRD-003](../../../../PRD/PRD-003_position_risk_limits.md)
@SYS:[SYS-003](../../../../SYS/SYS-003_position_risk_limits.md)
@EARS:[EARS-003](../../../../EARS/EARS-003_position_limit_enforcement.md)
@spec:[position_limit_service](../../../../SPEC/services/SPEC-003_position_limit_service.yaml)

@bdd:[BDD-003_risk_limits_requirements.feature:scenarios](../../../../BDD/BDD-003_risk_limits_requirements.feature#scenarios)

### Description
The system MUST block any order that would cause the post-trade [RESOURCE_INSTANCE - e.g., database connection, workflow instance] to exceed the configured per-symbol limit for an account.

### Acceptance Criteria
- Given a current [RESOURCE_INSTANCE - e.g., database connection, workflow instance], pending open orders, and a new order, when the computed post-trade quantity exceeds `max_position_qty`, then the order is rejected with `RISK_LIMIT_EXCEEDED` and includes `allowed_qty` suggestion.
- Given missing limit config for an account/symbol, the system responds with `CONFIG_NOT_FOUND` and does not allow the order.

### Related ADRs
- [ADR-033](../../../../ADR/ADR-033_risk_limit_enforcement_architecture.md#ADR-033): Risk Limit Enforcement Architecture

### EARS Source
- [EARS-003](../../../../EARS/EARS-003_position_limit_enforcement.md): Event/State/Ubiquitous statements

### Verification
- BDD: [BDD-003_risk_limits_requirements.feature](../../../../BDD/BDD-003_risk_limits_requirements.feature#scenarios)
- Spec: [SPEC-003_position_limit_service.yaml](../../../../SPEC/services/SPEC-003_position_limit_service.yaml)

## Traceability
- Upstream Sources: [PRD-003](../../../../PRD/PRD-003_position_risk_limits.md), [SYS-003](../../../../SYS/SYS-003_position_risk_limits.md), [EARS-003](../../../../EARS/EARS-003_position_limit_enforcement.md)
- Anchors/IDs: `# REQ-003`
- Code Path(s): `option_strategy/risk/position_limit_service.py`
