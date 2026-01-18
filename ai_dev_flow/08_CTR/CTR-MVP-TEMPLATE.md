---
title: "CTR-TEMPLATE: Contract Specification"
tags:
  - ctr-template
  - layer-8-artifact
  - shared-architecture
  - document-template
custom_fields:
  document_type: template
  artifact_type: CTR
  layer: 8
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  complexity: 1 # 1-5 scale
  template_for: contract-specification
  schema_reference: "CTR_SCHEMA.yaml"
  schema_version: "1.0"
---

>
> **📋 Document Authority**: This is the **PRIMARY STANDARD** for CTR structure. Schema: `CTR_SCHEMA.yaml v1.0`. Creation Rules: `CTR_CREATION_RULES.md`. Validation Rules: `CTR_VALIDATION_RULES.md`.

# CTR-NN: [Contract Title]

## 1. Document Control

| Item | Details |
|------|---------|
| **Project Name** | [Enter project name] |
| **Document Version** | [e.g., 1.0] |
| **Date** | [Current date] |
| **Document Owner** | [Name and owner's title] |
| **Prepared By** | [API Designer/Architect name] |
| **Status** | [Draft / In Review / Approved] |
| **SPEC-Ready Score** | [Score]/100 (Target: ≥90/100) |

### 1.1 Document Revision History

| Version | Date | Author | Changes Made | Approver |
|---------|------|--------|--------------|----------|
| 1.0 | [Date] | [Name] | Initial draft | |
| | | | | |

### 1.2 Contract Status

- **Status**: Draft | Active | Deprecated
- **Contract Owner**: [Team/Person names]
- **Version**: 1.0.0 (semantic versioning)

---

> **⚠️ UPSTREAM ARTIFACT REQUIREMENT**: Before completing traceability tags: (1) Check existing artifacts in `docs/`, (2) Reference only existing documents with actual IDs, (3) Use `null` only when upstream artifact type doesn't exist for this feature, (4) Do NOT create phantom references to non-existent documents, (5) Do NOT create missing upstream artifacts - skip that functionality.

---

## 2. PART 1: Contract Context and Requirements

## 2. Context

### 2.1 Interface Problem Statement

[What interface contract is needed? What components need to communicate?
Example: "[ORCHESTRATION_COMPONENT] needs to validate resource risk before executing trades. Risk Validation Service must provide a synchronous validation endpoint with deterministic responses."]

### 2.2 Background

[Current state of component integration, existing APIs, pain points.
Example: "Currently, each strategy agent implements its own risk validation logic, leading to inconsistency. This contract establishes a centralized risk validation interface to ensure uniform risk checks across all agents."]

### 2.3 Driving Forces

[Why this contract is needed now - new feature, refactoring, service decoupling.

- Business: Regulatory requirement for audit trail of risk decisions
- Technical: Reduce code duplication across 11 strategy agents
- Operational: Enable independent deployment of risk validation logic]

### 2.4 Constraints

- **Technical**: Protocol limitations, serialization formats, payload size limits
  - Must support synchronous request/response (< 100ms latency)
  - JSON serialization for human readability
  - Payload size < 1MB per request
- **Business**: SLA requirements, throughput targets, latency budgets
  - 99.9% uptime required for operating hours
  - <100ms p99 latency to avoid trade delays
  - 1000+ req/s throughput for resource collection rebalancing
- **Operational**: Monitoring, versioning, backward compatibility needs
  - Must support gradual rollout via feature flags
  - Contract changes require 30-day migration period
  - Full audit logging for compliance
- **security**: Authentication, authorization, data protection requirements
  - mTLS for service-to-service authentication
  - RBAC for agent authorization
  - No PII in logs or error messages

### 2.5 Trade-offs

**Benefits**: Parallel development, early validation, type safety, testability, decoupling
**Costs**: Contract coordination overhead, network latency vs in-process, single point of failure risk
**Risk Mitigations**: Contract tests in CI/CD, semantic versioning, circuit breaker + fallback

## 3. Contract Definition

### 3.1 Interface Overview

[Concise description of what this contract defines - request/response, message schema, event format.
Example: "Synchronous REST-style request/response contract for resource risk validation. Provider accepts resource parameters and risk limits, returns validation result with specific violation details if applicable."]

### 3.2 Parties

- **Provider**: [Service/component that implements this contract]
  - [SERVICE_NAME - e.g., Validation Service, Data Service] (service layer)
  - Implements [FUNCTIONALITY] logic against [ADR-NN] parameters
- **Consumer(s)**: [Services/components that use this contract]
  - [PRIMARY_CONSUMER - e.g., Orchestrator] (Level 1)
  - [ADDITIONAL_CONSUMERS - e.g., Service Agents, Worker Agents]
  - [BATCH_CONSUMER - e.g., Batch Processing Agent]

### 3.3 Communication Pattern

- **Type**: Synchronous
- **Protocol**: REST over HTTP/2
- **Data Format**: JSON
- **Transport**: Internal service network/service mesh (e.g., Istio, Linkerd, cloud-native runtime)

## 4. Requirements Satisfied

### 4.1 Primary Requirements

| Requirement ID | Description | How This Contract Satisfies It |
|----------------|-------------|-------------------------------|
| [REQ-NN] | [Requirement description] | [How contract satisfies this requirement] |
| [REQ-NN] | [Requirement description] | [How contract satisfies this requirement] |
| [SYS-NN] | [System requirement description] | [How contract satisfies this requirement] |
| [ADR-NN] | [Architecture decision description] | [How contract satisfies this requirement] |

### 4.2 Source Business Logic

References to product strategy or business rules requiring this interface:

- `{domain_strategy}/business_logic.md` section 4.2: Dynamic Risk Budgeting requires pre-trade validation
- `{domain_strategy}/risk_management.md` section 2.2: Resource limits must be checked before new positions

### 4.3 Quality Attributes

See [Section 7: Quality Attributes](#7-quality-attributes) for detailed performance, security, reliability, and observability requirements.

### 4.4 Thresholds Referenced

| Category | Platform Thresholds (from PRD) | API-Specific (unique to CTR) |
|----------|-------------------------------|------------------------------|
| Performance | `@threshold: PRD.NN.perf.api.p99_latency` | N/A |
| SLA | `@threshold: PRD.NN.sla.uptime.target` | N/A |
| Limits | `@threshold: PRD.NN.limit.api.requests_per_second` | `@threshold: CTR.NN.limit.consumer.requests_per_minute` |
| Timeouts | `@threshold: PRD.NN.timeout.request.sync` | N/A |
| Payload | N/A | `@threshold: CTR.NN.limit.payload.max_size_bytes` |
| Retry | N/A | `@threshold: CTR.NN.retry.max_attempts` |

**Reference**: [THRESHOLD_NAMING_RULES.md](../THRESHOLD_NAMING_RULES.md)

---

## 5. PART 2: Interface Specification and Schema

## 5. Interface Definition

### 5.1 Schema Reference
<!-- VALIDATOR:IGNORE-LINKS-START -->
[Schema: CTR-NN_descriptive_name.yaml](./CTR-NN_descriptive_name.yaml)
<!-- VALIDATOR:IGNORE-LINKS-END -->

**Operations**: `validatePositionRisk` (single resource), `validatecollectionRisk` (batch)

**Data Types**: `resource` (symbol, metrics), `collectionState` (positions, capital), `RiskLimits` (constraints), `ValidationResult` (decision + violations)

### 5.2 Endpoints / Functions / Messages

#### Endpoint 1: validatePositionRisk

- **Description**: Validates a single proposed resource against current resource collection state and risk limits
- **Request Schema**: See YAML `request_schema` for `validatePositionRisk`
  - `resource`: Proposed resource parameters (symbol, [METRIC_1 - e.g., error rate, response time], [VALUE - e.g., subscription fee, processing cost], etc.)
  - `collection_state`: Current resource collection [METRICS - e.g., performance indicators, quality scores] and capital
  - `risk_limits`: Risk parameters from ADR-008 configuration
- **Response Schema**: See YAML `response_schema` for `validatePositionRisk`
  - `is_valid`: Boolean - true if resource passes all checks
  - `decision_id`: UUID for audit trail
  - `violations`: Array of specific rule violations (if any)
  - `risk_impact`: Projected resource collection [METRICS - e.g., performance indicators, quality scores] after resource
- **Idempotent**: Yes (same request always yields same result for given resource collection state)
- **Retry Safe**: Yes (no side effects, read-only operation)

#### Endpoint 2: validatecollectionRisk (Future)

- **Description**: Validates entire resource collection against risk limits (for batch rebalancing)
- **Request Schema**: See YAML `request_schema` for `validatecollectionRisk`
- **Response Schema**: See YAML `response_schema` for `validatecollectionRisk`
- **Idempotent**: Yes
- **Retry Safe**: Yes

## 6. Error Handling

### 6.1 Error Codes

| Error Code | HTTP Status | Description | Retry Strategy |
|------------|-------------|-------------|----------------|
| INVALID_INPUT | 400 | Request validation failed (missing required fields, invalid types) | Do not retry |
| INSUFFICIENT_DATA | 400 | Missing required resource collection state or risk limits | Do not retry |
| LIMIT_EXCEEDED | 200 | resource violates risk limits (valid response, not error) | Do not retry |
| RATE_LIMITED | 429 | Too many requests from consumer | Exponential backoff, max 3 retries |
| SERVICE_UNAVAILABLE | 503 | Risk validation service temporarily unavailable | Exponential backoff, max 5 retries |
| INTERNAL_ERROR | 500 | Unexpected server processing error | Exponential backoff, max 3 retries |

### 6.2 Failure Modes & Recovery

- **Critical Failure Modes**:
  - Service crash during validation (likelihood: low, SLA: 99.9%)
  - Configuration service unavailable (ADR-008 parameters unreachable)
  - Network partition between consumer and provider
- **Recovery Strategies**:
  - [SAFETY_MECHANISM - e.g., rate limiter, error threshold]: Open after 5 consecutive failures, half-open after 60s
  - Fallback: Return validation failure (conservative approach)
  - Monitoring: Alert on >1% error rate or >200ms p99 latency
- **[SAFETY_MECHANISM - e.g., rate limiter, error threshold]**: Open after 5 failures within 60s, enter half-open state after 60s cooldown

---

## 7. PART 3: Quality Attributes and Operations

## 7. Quality Attributes

### 7.1 Performance Targets

- **Max Latency**: <100ms p99 (critical for [OPERATION_EXECUTION - e.g., order processing, task execution])
- **Min Throughput**: >1000 req/s sustained (resource collection rebalancing peak)
- **Payload Size Limit**: <1MB per request (typical: 10KB)

### 7.2 Reliability Requirements

- **Idempotency**: Yes - same input always produces same output for given resource collection state
- **Retry Strategy**: Exponential backoff (100ms, 200ms, 400ms), max 3 retries for 500/503 errors
- **Timeout**: 5000ms request timeout (fails fast to avoid blocking agents)
- **[SAFETY_MECHANISM - e.g., rate limiter, error threshold]**:
  - Open after 5 consecutive failures within 60s
  - Half-open after 60s cooldown
  - Close after 3 successful calls in half-open state

### 7.3 Security Requirements

- **Authentication**: mTLS for service-to-service (GCP service mesh)
- **Authorization**: RBAC - only agents with `risk:validate` permission can call endpoint
- **Encryption**: TLS 1.3 in transit, no at-rest encryption needed (ephemeral data)
- **Rate Limiting**: 100 req/s per consumer, burst up to 150 req/s
- **Audit Logging**: Log all validation requests with `decision_id`, consumer identity, timestamp

### 7.4 Observability

- **Success Rate**: Target >99.9%, Alert if >1% error rate for 5 minutes
- **Latency**: p50 <20ms, p95 <50ms, p99 <100ms
- **Throughput**: 1000 req/s sustained, 5000 req/s peak
- **Alerting**: Page on-call if >5% error rate or >3 consecutive failures

## 8. Versioning Strategy

### 8.1 Version Policy

- **Current Version**: 1.0.0
- **Semantic Versioning**: MAJOR.MINOR.PATCH
  - **MAJOR**: Breaking changes (incompatible request/response schema)
  - **MINOR**: Backward-compatible additions (new optional fields, new endpoints)
  - **PATCH**: Backward-compatible fixes (bug fixes, documentation)

### 8.2 Compatibility Rules

- **Backward Compatibility**: Provider must accept requests from consumers on n-1 major version
- **Forward Compatibility**: Consumers must ignore unknown fields in responses
- **Breaking Changes**: Require new major version, 30-day migration period, simultaneous deployment of n and n+1

### 8.3 Deprecation Policy

- **Notice Period**: 30 days minimum before removal
- **Migration Path**: Provider supports both old and new versions simultaneously during transition
- **Sunset Schedule**:
  - Day 0: Announce deprecation, publish migration guide
  - Day 30: Remove old version from documentation
  - Day 60: Remove old version from service (enforce via contract tests)

## 9. Examples

### 9.1 Success Response

**Request**: `POST /validate` with `resource`, `collection_state`, `risk_limits`

```json
{"resource": {"symbol": "ITEM-001", "metric_1": 25.3}, "collection_state": {"open_positions": 8}, "risk_limits": {"max_positions": 12}}
```

**Response** (HTTP 200):

```json
{"is_valid": true, "decision_id": "550e8400-e29b-41d4-a716-446655440000", "violations": [], "risk_impact": {"projected_positions": 9}}
```

### 9.2 Validation Failure

**Request**: Resource exceeds limit

```json
{"resource": {"symbol": "ITEM-002"}, "collection_state": {"open_positions": 12}, "risk_limits": {"max_positions": 12}}
```

**Response** (HTTP 200 - valid response, failed validation):

```json
{"is_valid": false, "decision_id": "...", "violations": [{"rule": "max_positions", "limit": 12, "projected": 13, "severity": "critical"}]}
```

### 9.3 Error Response

**Request**: Invalid input (missing required fields)

```json
{"resource": {"symbol": "", "metric_1": -999}}
```

**Response** (HTTP 400):

```json
{"error_code": "INVALID_INPUT", "error_message": "Validation failed: 'symbol' cannot be empty, missing required field 'collection_state'"}
```

---

## 10. PART 4: Testing and Traceability

## 10. Verification

### 10.1 Contract Testing

**Provider Tests** (Risk Validation Service):

- Schema validation: All responses match CTR-NN YAML schema
- Error handling: Each error code tested with appropriate scenarios
- Performance: Load test validates <100ms p99 latency at 1000 req/s
- Idempotency: Same request produces same result (deterministic)

**Consumer Tests** (All Agents):

- Request generation: Agent constructs valid requests per schema
- Response handling: Agent correctly interprets validation results
- Error handling: Agent handles all error codes gracefully
- Retry logic: Exponential backoff implemented correctly

**Contract Tests** (Pact/Spring Cloud Contract):

- Consumer-driven: Each agent publishes expected request/response pairs
- Provider validation: Risk service validates it satisfies all consumer expectations
- CI/CD integration: Contract tests run on every PR

### 10.2 BDD Scenarios

[BDD scenarios that validate this contract:

- Scenario: Agent validates resource before execution - File: BDD-012_risk_validation.feature#L15
- Scenario: Multiple agents validate concurrently - File: BDD-012_risk_validation.feature#L45
- Scenario: Risk service returns validation failure for limit breach - File: BDD-012_risk_validation.feature#L60]

### 10.3 Specification Impact

[SPEC files that will implement this contract:

- SPEC-05_risk_validation_service.yaml: Provider implementation
- SPEC-01_service_orchestrator.yaml: Primary consumer
- SPEC-015_service_request_agent.yaml: Strategy agent consumer]

### 10.4 Validation Criteria

**Technical Validation**:

- Schema validation passes for all request/response examples
- Performance benchmarks: p99 <100ms at 1000 req/s sustained
- security: mTLS authentication, RBAC authorization, audit logging implemented
- Idempotency: Same request produces same result across 1000 test iterations

**Integration Validation**:

- Provider implements contract correctly (all contract tests pass)
- All 11 consumer agents migrate successfully (contract tests pass)
- End-to-end test: resource collection rebalancing with 100 positions completes successfully

### 10.5 Impact Analysis

- **Provider**: [Service to implement contract]
- **Consumers**: [List of consuming services/agents]
- **Data Flow**: Consumer → Provider (sync/async) → Dependencies → Audit

### 10.6 Migration Strategy

1. Contract definition and validation setup
2. Provider implementation with feature flag
3. Consumer migration (canary first, then batches)
4. Enable feature flag, monitor, remove legacy code

## 11. Traceability

### 11.1 Related Contracts

**Depends On**:

- CTR-NN (Common Data Types): Shared resource/resource collection types
- ADR-008 (Risk Parameters): Configuration contract for risk limits

**Supersedes**:

- None (new contract, replaces informal in-process validation)

**Related**:

- CTR-02 ([METRICS - e.g., performance indicators, quality scores] Calculation): Provides [METRICS - e.g., performance indicators, quality scores] values used in validation
- CTR-006 (resource collection State): Provides current resource collection state

**Impacts**:

- CTR-NN (Future strategy contracts): Will reference this validation contract

### 11.2 Upstream Sources

| Source Type | Document ID | Document Title | Relevant sections | Relationship |
|-------------|-------------|----------------|-------------------|--------------|
<!-- VALIDATOR:IGNORE-LINKS-START -->
| REQ | [REQ-03](../07_REQ/risk/lim/REQ-03_resource_limit_enforcement.md) | [RESOURCE_LIMIT - e.g., request quota, concurrent sessions] Enforcement | section 3.1 | Defines validation requirements |
<!-- VALIDATOR:IGNORE-LINKS-END -->
| REQ | [REQ-008](../07_REQ/risk/cfg/REQ-008_centralized_risk_parameters.md) | Centralized Risk Parameters | section 2.0 | Defines risk limits to validate against |
| ADR | [ADR-008](../05_ADR/ADR-008_centralized_risk_parameters.md) | Centralized Risk Parameters | section 4.0 | Architecture decision for centralization |
| SYS | [SYS-004](../06_SYS/SYS-004_centralized_risk_controls.md) | Centralized Risk Controls | section 5.2 | System requirement for validation service |

### 11.3 SPEC Requirements

> **Note**: This section describes what SPEC files must implement to satisfy this contract. Do NOT reference specific SPEC-XX IDs as they don't exist yet during CTR creation.

**Provider SPEC Requirements**:
- Must implement all interface methods defined in Section 4 (Interface Definition)
- Must satisfy all quality attributes from Section 6 (Quality Attributes)
- Must handle all error scenarios from Section 5 (Error Handling)
- Must expose contract validation via Pydantic models (`.model_json_schema()`)
- Must include all contract versioning metadata from Section 8

**Consumer SPEC Requirements**:
- Must call provider using the exact interface defined in Section 4
- Must handle all error codes defined in Section 5.1 (Error Catalog)
- Must implement retry/fallback strategies per Section 5.2 (Recovery Strategy)
- Must respect all quality attribute constraints from Section 6

**Implementation Validation**:
- Provider implementations will be validated against this CTR's JSON schema
- Consumer implementations will be tested using contract tests (Pact/similar)
- All SPEC files must reference this CTR using `@ctr: CTR-NN` tags

### 11.4 Document Links

- **Anchors/IDs**: `#CTR-NN` (internal document reference)
<!-- VALIDATOR:IGNORE-LINKS-START -->
- **YAML Schema**: [CTR-NN_risk_validation.yaml](./CTR-NN_risk_validation.yaml)
<!-- VALIDATOR:IGNORE-LINKS-END -->
- **Code Path(s)**:
  - Provider: `src/services/risk_validation_service.py`
  - Consumers: `src/agents/*/risk_validator_client.py`

### 11.5 Same-Type References (Conditional)

**Include this section only if same-type relationships exist between CTR documents.**

| Relationship | Document ID | Document Title | Purpose |
|--------------|-------------|----------------|---------|
<!-- VALIDATOR:IGNORE-LINKS-START -->
| Related | [CTR-NN](./CTR-NN_...md) | [Related CTR title] | Shared API context |
<!-- VALIDATOR:IGNORE-LINKS-END -->
<!-- VALIDATOR:IGNORE-LINKS-START -->
| Depends | [CTR-NN](./CTR-NN_...md) | [Prerequisite CTR title] | Must complete before this |
<!-- VALIDATOR:IGNORE-LINKS-END -->

**Tags:**

```markdown
@related-ctr: CTR-NN
@depends-ctr: CTR-NN
```

### 11.6 Traceability Tags

**Required Tags** (Layer 8 - Cumulative Hierarchy):

```markdown
@brd: BRD.01.01.30    @prd: PRD.03.01.02    @ears: EARS.01.24.03    @bdd: BDD.03.13.01
@adr: ADR-NN         @sys: SYS.08.25.01    @req: REQ.03.26.01
```

**Format**: `@artifact-type: TYPE.NN.TT.SS` (or `TYPE-NN` for ADR)
**Validation**: All tags must reference existing documents. See [TRACEABILITY.md](../TRACEABILITY.md#cumulative-tagging-hierarchy) for hierarchy rules.

## 12. References

### 12.1 Internal Links

- [REQ-03: [RESOURCE_LIMIT - e.g., request quota, concurrent sessions] Enforcement](../07_REQ/risk/lim/REQ-03_resource_limit_enforcement.md)
- [REQ-008: Centralized Risk Parameters](../07_REQ/risk/cfg/REQ-008_centralized_risk_parameters.md)
- [ADR-008: Centralized Risk Parameters Architecture](../05_ADR/ADR-008_centralized_risk_parameters.md)
- [SYS-004: Centralized Risk Controls](../06_SYS/SYS-004_centralized_risk_controls.md)
<!-- VALIDATOR:IGNORE-LINKS-START -->
- [SPEC-05: Risk Validation Service](../09_SPEC/SPEC-05_risk_validation_service/SPEC-05_risk_validation_service.yaml)
<!-- VALIDATOR:IGNORE-LINKS-END -->
- [BDD-NN: Risk Validation Scenarios] (../04_BDD/BDD-NN_risk_validation/BDD-NN.1_risk_validation.feature)  
  (example placeholder)

### 12.2 External Links

- [JSON Schema Specification](https://json-schema.org/): JSON schema validation standard
- [OpenAPI 3.0](https://spec.openapis.org/oas/v3.0.0): REST API contract standard
- [Pact Contract Testing](https://docs.pact.io/): Consumer-driven contract testing framework
- [gRPC Best Practices](https://grpc.io/docs/guides/): Alternative protocol considerations

### 12.3 Additional Context

- **Related Patterns**:
  - API Gateway pattern for centralized validation
  - [SAFETY_MECHANISM - e.g., rate limiter, error threshold] pattern for failure resilience
  - Retry pattern with exponential backoff
- **Industry Standards**:
  - REST API design guidelines (Microsoft, Google)
  - JSON Schema for contract validation
  - OAuth 2.0 / mTLS for service authentication
- **Lessons Learned**:
  - V3 architecture: In-process validation led to configuration drift and compliance issues
  - V4 architecture: Synchronous validation critical for atomic trade decisions
  - Industry: Contract-first development reduces integration time by 60%

---

## 13. Appendix A: Alternatives Considered

### 13.1 A.1 Alternative A: In-Process Validation (Library)

**Description**: Distribute validation as a shared library imported by each consumer

**Pros**: Zero network latency, no additional infrastructure, simpler deployment
**Cons**: Code duplication, configuration inconsistency, difficult updates, no centralized audit trail
**Rejection Reason**: Violates centralization requirements; configuration drift leads to compliance issues
**Fit Score**: Poor

### 13.2 A.2 Alternative B: Asynchronous Event-Driven

**Description**: Consumers publish events, service responds asynchronously

**Pros**: Decoupling, better scalability, enables complex workflows
**Cons**: 50-200ms latency, complex state management, difficult atomic decisions
**Rejection Reason**: Unacceptable latency for synchronous operations
**Fit Score**: Good for non-critical validation, poor for synchronous operations

### 13.3 A.3 Alternative C: GraphQL Contract

**Description**: Use GraphQL schema instead of REST-style contract

**Pros**: Flexible querying, built-in schema validation, strongly typed
**Cons**: Additional complexity, overkill for simple patterns, learning curve
**Rejection Reason**: Adds unnecessary complexity for straightforward use case
**Fit Score**: Good for complex APIs, poor for simple validation

---

## 14. Appendix B: Implementation Notes

### 14.1 B.1 Development Phases

1. **Phase 1**: Contract definition and YAML schema creation
   - Collaborative contract design with consumer teams
   - YAML schema finalization
   - Contract test framework setup
2. **Phase 2**: Provider implementation with contract tests
   - Provider service implementation
   - Contract tests (provider validates all consumer expectations)
   - Load testing and performance optimization
3. **Phase 3**: Consumer integration and validation
   - Consumer code changes to call endpoint
   - Contract tests (consumer validates provider contract)
   - End-to-end integration testing

### 14.2 B.2 Code Locations

- **Provider Implementation**: `src/services/[service_name].py`
- **Consumer Implementation**: `src/agents/[agent_name]/[service]_client.py`
- **Contract Tests**: `tests/08_CTR/[contract]/provider_contract_test.py`, `consumer_contract_test.py`
- **Schema Validation**: `src/common/schemas/ctr_nnn_validation.py`

### 14.3 B.3 Configuration Management

- **Contract Version**: Environment variable `[CONTRACT]_VERSION=1.0.0`
- **Feature Flags**: `ENABLE_[FEATURE]=true|false`
- **Environment-Specific**: Different rate limits per environment (dev/prod)

---

**Template Version**: 1.0
**Last Reviewed**: YYYY-MM-DD
**Next Review**: YYYY-MM-DD (recommend quarterly for active contracts)

---

> **Template Guidance** (remove when creating actual contracts):
>
> - Target: 300–500 lines; Maximum: 600 lines (Markdown)
> - Split large contracts by endpoint groups with matching `.md` + `.yaml` pairs
> - See `CTR_CREATION_RULES.md` and `README.md` for detailed guidance
