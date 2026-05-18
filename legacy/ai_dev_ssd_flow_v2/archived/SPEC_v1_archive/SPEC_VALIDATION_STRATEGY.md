---
title: "SPEC Validation Strategy (Quick Reference)"
tags:
  - validation
  - spec
  - quick-reference
custom_fields:
  document_type: quick-reference
  artifact_type: SPEC
  priority: high
  version: "1.0"
  scope: spec-validation
---

# SPEC Validation Strategy (Quick Reference)

**Purpose:** Quick reference for SPEC validation architecture, gates, and patterns.

**Full Documentation:** See [../VALIDATION_STRATEGY_GUIDE.md](../VALIDATION_STRATEGY_GUIDE.md) for framework-wide architecture and patterns.

**CLI Reference:** See [SPEC_VALIDATION_COMMANDS.md](./SPEC_VALIDATION_COMMANDS.md) for command syntax.

**Decision Guide:** See [SPEC_AI_VALIDATION_DECISION_GUIDE.md](./SPEC_AI_VALIDATION_DECISION_GUIDE.md) for SPEC-specific decision patterns.

---

## SPEC Validation Architecture

- Validation scripts live in [scripts](./scripts).
- Implemented validators:
  - [scripts/validate_spec_quality_score.sh](scripts/validate_spec_quality_score.sh) — quality gates (see [SPEC_MVP_QUALITY_GATE_VALIDATION.md](./SPEC_MVP_QUALITY_GATE_VALIDATION.md)).
  - [scripts/validate_spec.py](scripts/validate_spec.py) — standard SPEC validator; run with `--help` to view supported modes.
  - [scripts/validate_spec_implementation_readiness.py](scripts/validate_spec_implementation_readiness.py) — **NEW**: Implementation-readiness scorer evaluates SPEC completeness for coding (≥90% target); checks for architecture, interfaces, behavior specs, performance targets, security specs, observability requirements, verification strategies, implementation details, REQ-to-code mapping, and concrete examples.
- Quality gates enforce complete architectural specification, behavior algorithms, performance targets, and concrete code/pseudocode examples.

---

## SPEC Quality Gates and Rules

- Gate definitions: [SPEC_MVP_QUALITY_GATE_VALIDATION.md](./SPEC_MVP_QUALITY_GATE_VALIDATION.md)
- Validation rules: [SPEC_MVP_VALIDATION_RULES.md](./SPEC_MVP_VALIDATION_RULES.md)
- Creation rules: [SPEC_MVP_CREATION_RULES.md](./SPEC_MVP_CREATION_RULES.md)
- Use the framework guidance in [../VALIDATION_STRATEGY_GUIDE.md](../VALIDATION_STRATEGY_GUIDE.md) to organize gates and validators.

---

## Implementation-Readiness Scoring Criteria

The `validate_spec_implementation_readiness.py` validator awards 10 points per passing check (100 total):

| Check | Criterion | Notes |
|-------|-----------|-------|
| **Architecture** | Component structure with dependencies documented | Required for all SPECs |
| **Interfaces** | External APIs, internal APIs, class definitions | Request/response schemas required |
| **Behavior** | State machines, algorithms, workflows | Pseudocode or formal descriptions |
| **Performance** | Latency targets, throughput, resource limits | Concrete targets (e.g., p95 < 100ms) |
| **Security** | Auth, authorization, encryption, rate limiting | Specific mechanisms documented |
| **Observability** | Logging, metrics, tracing, alerts | What to measure and when |
| **Verification** | Test strategies (unit, integration, contract, perf) | How implementation is validated |
| **Implementation** | Configuration, deployment, scaling, dependencies | How to deploy and operate |
| **REQ Mapping** | Every REQ linked to implementation logic | req_implementations section required |
| **Concrete Examples** | Pseudocode, algorithms, API examples, data models | ≥5 code/algo examples |

**Target**: ≥90 points (9/10 checks) for implementation readiness.

**Pseudocode & Algorithm Pattern**:
```yaml
behavior:
  process_order: |
    Algorithm: Process Trading Order
    1. Validate order parameters (symbol, quantity, price)
    2. Check account funds/margin requirements
    3. If insufficient: throw InsufficientFundsError
    4. Submit to broker API (retry up to 3 times)
    5. On success: update position tracker, emit OrderExecuted event
    6. On failure: log error, alert risk team, trigger circuit breaker
  
  error_handling:
    - error_code: INVALID_SYMBOL
      http_status: 400
      message: "Symbol not found in market data"
      recovery: "Validate against known symbols before submission"
    - error_code: RATE_LIMITED
      http_status: 429
      message: "Rate limit exceeded"
      recovery: "Implement exponential backoff with jitter; max 3 retries"
```

**Concrete Examples Pattern** (API, Data Models, Configs):
```yaml
interfaces:
  external_apis:
    - endpoint: "POST /api/v1/orders"
      example_request:
        symbol: "TSLA"
        quantity: 10
        action: "BUY"
        order_type: "LMT"
        limit_price: 150.50
      example_response:
        order_id: "ord_789"
        status: "accepted"
        filled_quantity: 0
        avg_price: null

implementation:
  configuration:
    broker:
      host: "localhost"
      port: 4002
      timeout_ms: 20000
      max_retries: 3
      backoff_strategy: "exponential"
    
  deployment:
    container: "trading-engine:v1.0.0"
    replicas: 3
    resources:
      memory: "2Gi"
      cpu: "1000m"
    scaling:
      metric: "order_queue_depth"
      target: 100
      max_replicas: 10
```

---

## Quick Usage

### Quality Gates & Structure
```bash
bash scripts/validate_spec_quality_score.sh <spec-directory>
python3 scripts/validate_spec.py --help
```

### Implementation-Readiness (≥90% for coding phase)
```bash
python validate_spec_implementation_readiness.py --directory docs/09_SPEC --min-score 90
python validate_spec_implementation_readiness.py --spec-file docs/09_SPEC/SPEC-01_iam.yaml
```

---

## More Information

**Framework-Level Docs:**
- [../VALIDATION_STRATEGY_GUIDE.md](../VALIDATION_STRATEGY_GUIDE.md)
- [../VALIDATION_COMMANDS.md](../VALIDATION_COMMANDS.md)
- [../AI_VALIDATION_DECISION_GUIDE.md](../AI_VALIDATION_DECISION_GUIDE.md)

**SPEC-Specific Docs:**
- [SPEC_VALIDATION_COMMANDS.md](./SPEC_VALIDATION_COMMANDS.md)
- [SPEC_AI_VALIDATION_DECISION_GUIDE.md](./SPEC_AI_VALIDATION_DECISION_GUIDE.md)
- [scripts/README.md](./scripts/README.md)