# REQ-NN: API Integration (Example)

## Document Control

| Item | Details |
|------|---------|
| Status | Example/Approved |
| Version | 2.0.0 |
| Author | Example Team |
| Category | Functional - Integration |
| Verification | BDD/Integration/Contract |

---

## 1. Description

The system SHALL provide an API client to submit requests to an external provider with validation, authentication, and resilience (retry, circuit breaker, caching).

---

## 2. Acceptance Criteria

- p95 end-to-end call latency ≤ 500 ms under nominal load.
- Retries use exponential backoff with jitter; max attempts configurable.
- Requests exceeding rate limits are queued or rejected with clear error.
- Responses are validated against a schema; invalid responses result in errors.

---

## 3. Traceability

Required upstream tags (Layer 7):
```markdown
@brd: BRD-NN
@prd: PRD-NN
@ears: EARS-NN
@bdd: BDD-NN
@adr: ADR-NN
@sys: SYS-NN
```

Downstream:
- SPEC-NN (Technical specification for client)
- CTR-NN (Contracts if interface formalized)

---

## 4. Verification

- BDD: scenarios for success, retries, rate limits, invalid responses.
- Contract tests: request/response schema conformance.
- Performance: latency and throughput tests against target SLAs.

