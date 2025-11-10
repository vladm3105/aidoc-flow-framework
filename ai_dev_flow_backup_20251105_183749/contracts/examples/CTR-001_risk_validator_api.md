# CTR-001: Risk Validator API

## Position in Development Workflow

```
REQ (Atomic Requirements): Granular, testable requirements
        ↓
IMPL (Implementation Plans): Project management layer (WHO/WHEN) - phases, teams, deliverables
        ↓
**CTR (API Contracts)**: Interface contracts between components ← YOU ARE HERE
        ↓
SPEC (Technical Implementation): Implementation blueprints (HOW)
```

---

# PART 1: Contract Context and Requirements

## Status
**Status**: Active
**Date**: 2025-11-02
**Contract Owner**: Risk Management Team
**CTR Author**: AI Dev Flow Working Group
**Last Updated**: 2025-11-02
**Version**: 1.0.0

## Context

### Interface Problem Statement
Portfolio Orchestrator Agent needs to validate position risk before executing trades. Risk Validation Service must provide a synchronous validation endpoint with deterministic responses.

### Background
Currently, each strategy agent implements its own risk validation logic, leading to inconsistency. This contract establishes a centralized risk validation interface to ensure uniform risk checks across all agents.

### Driving Forces
- **Business**: Regulatory requirement for audit trail of risk decisions
- **Technical**: Reduce code duplication across 11 strategy agents
- **Operational**: Enable independent deployment of risk validation logic

### Constraints
- **Technical**:
  - Must support synchronous request/response (< 100ms latency)
  - JSON serialization for human readability
  - Payload size < 1MB per request
- **Business**:
  - 99.9% uptime required for trading hours
  - <100ms p99 latency to avoid trade delays
  - 1000+ req/s throughput for portfolio rebalancing
- **Security**:
  - mTLS for service-to-service authentication
  - RBAC for agent authorization
  - No PII in logs or error messages

## Contract Definition

### Interface Overview
Synchronous REST-style request/response contract for position risk validation. Provider accepts position parameters and risk limits, returns validation result with specific violation details if applicable.

### Parties
- **Provider**: Risk Validation Service (service layer)
  - Implements validation logic against ADR-008 risk parameters
- **Consumer(s)**:
  - Portfolio Orchestrator Agent (Level 1)
  - All Strategy Execution Agents (Level 3): Iron Condor, CSP, Covered Call, Bear Call Spread
  - Portfolio Hedging Agent

### Communication Pattern
**Request-Response (Synchronous)**
- Consumers send validation requests
- Provider responds with pass/fail + violation details
- No asynchronous callbacks

---

# PART 2: API Specification

## Request Schema

### Validation Request
```json
{
  "request_id": "uuid-v4",
  "timestamp": "2025-11-02T10:00:00Z",
  "agent_id": "portfolio-orchestrator",
  "position": {
    "symbol": "AAPL",
    "strategy_type": "iron_condor",
    "quantity": 10,
    "premium_per_contract": 1.50,
    "underlying_price": 150.00,
    "delta": 0.05,
    "gamma": 0.01,
    "theta": -0.25,
    "vega": 0.10
  },
  "portfolio_context": {
    "current_positions": 8,
    "portfolio_delta": -5.0,
    "portfolio_heat": 18500.00,
    "correlation_score": 0.65
  },
  "market_context": {
    "vix": 18.5,
    "market_regime": "stable_bull"
  }
}
```

## Response Schema

### Validation Response (Success)
```json
{
  "request_id": "uuid-v4",
  "timestamp": "2025-11-02T10:00:00.050Z",
  "validation_result": "PASS",
  "risk_score": 0.45,
  "checks_performed": [
    {
      "check_name": "max_positions",
      "status": "PASS",
      "limit": 12,
      "current_value": 8,
      "new_value": 9
    },
    {
      "check_name": "portfolio_heat",
      "status": "PASS",
      "limit": 25000.00,
      "current_value": 18500.00,
      "new_value": 19650.00
    }
  ],
  "warnings": [
    "Portfolio delta will be -5.50 (threshold: ±10.0)"
  ]
}
```

### Validation Response (Failure)
```json
{
  "request_id": "uuid-v4",
  "timestamp": "2025-11-02T10:00:00.050Z",
  "validation_result": "FAIL",
  "risk_score": 0.95,
  "violations": [
    {
      "rule": "circuit_breaker_vix",
      "severity": "CRITICAL",
      "limit": 40.0,
      "current_value": 42.5,
      "message": "VIX exceeds circuit breaker threshold. No new trades allowed."
    }
  ],
  "checks_performed": [
    {
      "check_name": "circuit_breaker_vix",
      "status": "FAIL",
      "limit": 40.0,
      "current_value": 42.5
    }
  ]
}
```

## Error Responses

### 400 Bad Request
```json
{
  "error_code": "INVALID_REQUEST",
  "message": "Missing required field: position.symbol",
  "request_id": "uuid-v4",
  "timestamp": "2025-11-02T10:00:00.050Z"
}
```

### 503 Service Unavailable
```json
{
  "error_code": "SERVICE_UNAVAILABLE",
  "message": "Risk validation service temporarily unavailable",
  "request_id": "uuid-v4",
  "timestamp": "2025-11-02T10:00:00.050Z",
  "retry_after_seconds": 30
}
```

---

# PART 3: Non-Functional Requirements

## Performance
- **Latency**: p50 < 50ms, p99 < 100ms
- **Throughput**: 1000+ requests/second
- **Concurrency**: Support 100+ concurrent connections

## Reliability
- **Uptime**: 99.9% during trading hours (9:30 AM - 4:00 PM ET)
- **Error Rate**: < 0.1% (excluding client errors)
- **Retry Policy**: Exponential backoff, max 3 retries

## Security
- **Authentication**: mTLS required for all requests
- **Authorization**: RBAC-based agent permissions
- **Audit Logging**: All validation decisions logged with request_id

---

# PART 4: Traceability

## Upstream Requirements
- **REQ-003**: Position Limit Enforcement (risk/lim/)
- **REQ-005**: Circuit Breaker Rules
- **REQ-008**: Portfolio Heat Calculation

## Architecture Decisions
- **ADR-008**: Centralized Risk Parameters
- **ADR-020**: Risk Control Service Agent

## Downstream Specifications
- **SPEC-003**: Risk Validator Implementation

---

# PART 5: Versioning and Compatibility

## Version History
| Version | Date | Changes | Breaking? |
|---------|------|---------|-----------|
| 1.0.0 | 2025-11-02 | Initial contract | N/A |

## Compatibility Policy
- **Breaking Changes**: Require new major version (2.0.0)
- **Non-Breaking Additions**: Minor version increment (1.1.0)
- **Bug Fixes**: Patch version increment (1.0.1)
- **Migration Period**: 30 days for breaking changes

---

# PART 6: Testing and Validation

## Contract Tests
- Request/response schema validation
- Error handling scenarios
- Performance benchmarks
- Security validations

## Example Scenarios
See CTR-001_risk_validator_api.yaml for complete examples.

---

**Policy Reference**: See [ADR-CTR_SEPARATE_FILES_POLICY.md](../adrs/ADR-CTR_SEPARATE_FILES_POLICY.md) for dual-file requirement.
