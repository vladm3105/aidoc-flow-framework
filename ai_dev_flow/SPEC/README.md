---
title: "Specifications (SPEC)"
tags:
  - index-document
  - layer-10-artifact
  - shared-architecture
custom_fields:
  document_type: readme
  artifact_type: SPEC
  layer: 10
  priority: shared
---

# Specifications (SPEC)

## Generation Rules

- Index-only: maintain `SPEC-00_index.md` as the authoritative plan and registry (mark planned items with Status: Planned).
- Templates: default to the MVP template; use the full (sectioned) template only when explicitly set in project settings or clearly requested in the prompt.
- Inputs used for generation: `SPEC-00_index.md` + selected template profile; no skeletons are used.
- Example index: `ai_dev_flow/tmp/SYS-00_index.md`.

Note: Some examples in this document show a portable `docs/` root. In this repository, artifact folders live at the ai_dev_flow root without the `docs/` prefix; see README → “Using This Repo” for path mapping.

Specifications (SPEC) are machine-readable technical blueprints that define how software components should be implemented. SPECs transform requirements into actionable design decisions, providing complete implementation guidance for developers while establishing contracts for testing and integration.

Note: `SPEC-TEMPLATE.md`/`.yaml` are reference templates. YAML stays monolithic per component for code generation. When narrative grows, split the Markdown only (index + section files) per `SPEC/SPEC_SPLITTING_RULES.md` and `../DOCUMENT_SPLITTING_RULES.md`.

## Structure Policy

- YAML: Monolithic single file per component (`SPEC-{DOC_NUM}_{slug}.yaml`).
- Markdown: Split as needed using `SPEC-{DOC_NUM}.0_index.md` and `SPEC-{DOC_NUM}.{S}_{slug}.md`.
- DOC_NUM: Variable-length starting at 2 digits (01, 02, 99, 100, 1000).
- Layout:
  - Nested (default): `SPEC/SPEC-{DOC_NUM}_{slug}/SPEC-{DOC_NUM}_{slug}.yaml` with Markdown section files alongside.
  - Flat (exception): `SPEC/SPEC-{DOC_NUM}_{slug}.yaml` for small, stable specs.

### Examples

- Flat (small): [SPEC-01_api_client_example.yaml](./SPEC-01_api_client_example.yaml)
- Nested (recommended): [SPEC-02_nested_example.yaml](./examples/SPEC-02_nested_example/SPEC-02_nested_example.yaml) with [index](./examples/SPEC-02_nested_example/SPEC-02.0_index.md)

## Codegen Compatibility

- Discovery (recursive):
  - Bash: `find SPEC -type f -name 'SPEC-*.yaml'`
  - Python: `glob.glob('SPEC/**/SPEC-*.yaml', recursive=True)`
- Identity: Use YAML `id` and `metadata.artifact_type` instead of inferring from path or fixed 3-digit IDs. DOC_NUM is variable-length (2+ digits).
- Outputs: Derive names from `codegen.module_name` (or `id`) rather than DOC_NUM or folder name.
- CTR Resolution: Prefer `interfaces[].contract_id: CTR-NN`; optionally support `contract_ref` (relative path) as fallback.
- TASKS Mapping: Reference SPEC by `@spec: SPEC-{DOC_NUM}`; optionally include `spec_path` for explicit runs.

## Complete SDD Document Flow

The workflow transforms business requirements into production-ready code through traceable artifacts:

**⚠️ See for the full document flow: [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](../SPEC_DRIVEN_DEVELOPMENT_GUIDE.md)**

## Purpose

SPECs serve as the **technical implementation contracts** that:
- **Define Component Behavior**: Specify interfaces, caching, performance, and operational characteristics
- **Establish Technical Standards**: Provide consistent patterns for observability, error handling, and resilience
- **Enable Automated Implementation**: Structure specifications for tool-assisted code generation
- **Support Verification**: Define measurable criteria for implementation correctness
- **Enable Independent Development**: Allow teams to develop components in parallel with well-defined contracts

## Position in Document Workflow

**⚠️ See [../index.md](../index.md#traceability-flow) for the authoritative workflow visualization.**

**Layer 10: Technical Specifications**

SPECs sit between REQ (atomic requirements) and TASKS (implementation tasks) in the 16-layer architecture (Layer 0-15):

**⚠️ See for the full document flow: [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](../SPEC_DRIVEN_DEVELOPMENT_GUIDE.md)**

## SPEC YAML Structure

Note: For large specifications that warrant splitting, see `SPEC/SPEC_SPLITTING_RULES.md` for SPEC-specific guidance and `../DOCUMENT_SPLITTING_RULES.md` for core splitting standards.

### Header with Traceability Comments

YAML files include traceability links in comment headers:

```yaml
# @requirement:[REQ-NN](../../REQ/.../REQ-NN_...md#REQ-NN)
# @adr:[ADR-NN](../../ADR/ADR-NN_...md#ADR-NN)
# @bdd:[BDD-NN.SS:scenarios](../../BDD/BDD-NN_{suite}/BDD-NN.SS_{slug}.feature#scenarios)
id: component_name
summary: Single-sentence description of component purpose and scope.
```

### Core Specification Fields

```yaml
id: component_snake_case_name
summary: Brief description of component purpose
traceability:
  upstream:
    - "[REQ-NN](../../REQ/.../REQ-NN_...md#REQ-NN)"
    - "[ADR-NN](../../ADR/ADR-NN_...md#ADR-NN)"
  downstream:
    - code: path/to/implementation.py
    - contract: path/to/api.yaml

requirements_source:
  - "[PRD-NN](../../../PRD/PRD-NN_...md)"
  - "[SYS-NN](../../../SYS/SYS-NN_...md)"
```

## Interface Specifications

### Function Interfaces
Define component function signatures and contracts:

```yaml
interfaces:
  functions:
    - name: function_name
      input:
        parameter1: { type: string, required: true, description: "Parameter purpose" }
        parameter2: { type: number, minimum: 0, description: "Validated parameter" }
      output:
        result: { type: boolean, description: "Operation success indicator" }
        data: { type: object, description: "Structured response data" }
      errors:
        INVALID_INPUT: "Input validation failed"
        EXTERNAL_SERVICE_UNAVAILABLE: "Dependent service unreachable"
```

### Class/Service Interfaces
Define object-oriented interfaces:

```yaml
interfaces:
  classes:
    - name: ServiceClient
      methods:
        - name: initialize
          params: { config: object }
          return: boolean
        - name: process_request
          params: { request: RequestObject }
          return: ResponseObject
          raises: [ValidationError, NetworkTimeout]
  properties:
    timeout_seconds: { type: integer, default: 30, minimum: 1, maximum: 300 }
```

## Behavioral Specifications

### State Management
Define component state transitions and invariants:

```yaml
state_management:
  states: [INITIALIZING, READY, PROCESSING, ERROR, SHUTDOWN]
  transitions:
    INITIALIZING -> READY: "successful_initialization"
    READY -> PROCESSING: "new_request"
    PROCESSING -> READY: "request_completed"
    ANY -> ERROR: "fatal_error"
    ERROR -> READY: "error_resolved"
  invariants:
    - "cache_size <= max_cache_entries"
    - "active_connections <= max_connections"
```

### Error Handling
Specify error conditions and recovery patterns:

```yaml
error_handling:
  recoverable_errors:
    - code: NETWORK_TIMEOUT
      retry_limit: 3
      backoff_strategy: exponential
    - code: EXTERNAL_SERVICE_DEGRADED
      fallback_strategy: cached_response
  fatal_errors:
    - code: CONFIGURATION_ERROR
      action: terminate_gracefully
    - code: RESOURCE_EXHAUSTED
      action: circuit_breaker_trip
```

## Operational Specifications

### Caching Strategy
Define cache behavior and management:

```yaml
caching:
  strategy: memory_with_overflow_to_disk
  policies:
    global_quote_seconds: 300
    time_series_minutes: 60
    fundamentals_days: 1
  eviction:
    strategy: lru
    max_entries: 10000
  serialization:
    format: json
    compression: gzip
```

### Rate Limiting
Specify request rate controls:

```yaml
rate_limiting:
  strategy: token_bucket
  configuration:
    capacity: 100
    refill_rate: 10
    refill_period: seconds
  tiers:
    free: { rpm: 5, burst_limit: 10 }
    [VALUE - e.g., subscription fee, processing cost]: { rpm: 75, burst_limit: 150 }
  enforcement:
    rejection_response: 429_TOO_MANY_REQUESTS
    retry_after_header: true
```

### Circuit Breakers
Define failure protection mechanisms:

```yaml
circuit_breaker:
  strategy: time_based
  thresholds:
    failure_percentage: 50
    min_requests: 10
    window_seconds: 60
  states:
    closed: normal_operation
    open: { wait_seconds: 30, reject_all_requests: true }
    half_open: { test_request_percentage: 10 }
```

## Performance Specifications

### Latency Requirements
Define response time expectations:

```yaml
performance:
  latency:
    p50_milliseconds: 50
    p95_milliseconds: 200
    p99_milliseconds: 1000
  throughput:
    sustained_rps: 100
    burst_rps: 200
    cooldown_period_seconds: 300
  resource_limits:
    cpu_cores: 2
    memory_mb: 1024
    connections: 100
```

## Observability Specifications

### Metrics Collection
Define monitoring and alerting metrics:

```yaml
observability:
  metrics:
    - name: requests_total
      type: counter
      labels: [method, status_code]
      description: "Total number of requests processed"
    - name: request_duration_seconds
      type: histogram
      buckets: [0.1, 0.5, 1.0, 2.0, 5.0]
      description: "Request processing time distribution"
    - name: error_rate
      type: gauge
      thresholds:
        warning: 0.05
        critical: 0.10
      description: "Proportion of requests resulting in errors"
```

### Logging Specification
Define structured logging requirements:

```yaml
observability:
  logging:
    level: INFO
    events:
      - event: request_started
        level: DEBUG
        fields: [correlation_id, user_id]
      - event: external_api_call
        level: INFO
        fields: [api_name, endpoint, status_code, duration_ms, correlation_id]
      - event: rate_limit_exceeded
        level: WARN
        fields: [user_id, limit_type, current_usage, correlation_id]
      - event: circuit_breaker_tripped
        level: ERROR
        fields: [reason, affected_service, correlation_id]
    sensitive_fields: [password, credit_card_number, personal_id]
    correlation_tracking: enabled
```

## Verification and Validation

### BDD Scenario Mapping
Link specifications to behavioral tests:

```yaml
verification:
  bdd_scenarios:
    - "[BDD-NN.SS_{slug}.feature:L23](../../BDD/BDD-NN_{suite}/BDD-NN.SS_{slug}.feature#L23)"  # Specific scenario line
    - "[BDD-NN.SS_{slug}.feature:L45](../../BDD/BDD-NN_{suite}/BDD-NN.SS_{slug}.feature#L45)"  # Additional scenarios
  contract_tests:
  load_tests:
    - target_rps: 1000
      duration_minutes: 10
      success_criteria: "p95_latency_ms < 500, error_rate < 0.01"
```

### Code Generation Template
Reference implementation generation:

```yaml
implementation:
  language: python
  framework: fastapi
  template: service_client_template
  generation_config:
    enable_validation: true
    enable_metrics: true
    enable_circuit_breaker: true
  custom_extensions:
    - external_api_normalization.py
    - rate_limiting_custom.py
```

## File Organization Hierarchy

```
SPEC/
├── services/         # Service component specifications
│   ├── SPEC-01_external_api_client.yaml
│   └── SPEC-02_ib_gateway_service.yaml
├── data/            # Data processing and storage SPEC
├── api/             # API gateway and routing SPEC
├── integration/     # External system integration SPEC
└── infrastructure/  # Deployment and infrastructure SPEC
```

## File Naming Convention

```
SPEC/{domain}/SPEC-NN_{component_name}.yaml
```

Where:
- `SPEC/` is the base specifications directory
- `{domain}` is architectural domain (`services`, `data`, `api`, etc.)
- `SPEC` is the constant prefix
- `NNN` is the 2+ digit sequence number (01, 02, 003, etc.)
- `{component_name}` uses snake_case describing the component
- `.yaml` is the required file extension

**Examples:**
- `SPEC/SPEC-01_external_api_client/SPEC-01_external_api_client.yaml`
- `SPEC/data/SPEC-042_real_time_price_processor.yaml`
- `SPEC/api/SPEC-102_service_api_gateway.yaml`

## SPEC Quality Gates

**Every SPEC must:**
- Include complete traceability links to upstream and downstream artifacts
- Define interfaces with input/output schemas and error conditions
- Specify performance, caching, and operational characteristics
- Include observability requirements (metrics, logging, monitoring)
- Reference implementing code paths (proposed or existing)
- Be validated against corresponding BDD scenarios
- Follow YAML schema validation rules

**SPEC validation checklist:**
- ✅ Valid YAML syntax with proper indentation
- ✅ id field uses snake_case naming convention
- ✅ All required interface fields are specified
- ✅ Error conditions are documented with specific codes
- ✅ Performance targets are quantifiable (not "fast" but "p95 < 200ms")
- ✅ Observability requirements include specific metric names and thresholds
- ✅ Cross-reference links resolve to existing artifacts
- ✅ Component responsibilities are clearly bounded

## SPEC Writing Guidelines

### 1. Component Scope Definition
Clearly define what the component does and doesn't do:

**Good:**
```yaml
id: user_authentication_service
summary: Handles user authentication, session management, and basic authorization checks for [APPLICATION_TYPE - e.g., e-commerce platform, SaaS application] access.
scope:
  includes: [login, logout, session validation, password policies]
  excludes: [user registration, role management, advanced permissions]
```

### 2. Interface Completeness
Specify full contracts, not just method signatures:

**Complete Interface:**
```yaml
interfaces:
  functions:
    - name: authenticate_user
      input:
        username: { type: string, minLength: 3, maxLength: 50 }
        password_hash: { type: string, pattern: "^[a-f0-9]{64}$" }
        client_ip: { type: string, format: ipv4 }
        correlation_id: { type: string, format: uuid }
      output:
        success: { type: boolean }
        session_token: { type: string, nullable: true }
        error_code: { type: string, nullable: true }
      preconditions: ["User account exists and is active"]
      postconditions: ["Session created on success", "No session created on failure"]
```

### 3. Behavioral Specification
Define complete behavior including edge cases:

```yaml
behavior:
  authentication:
    max_attempts_per_hour: 5
    lockout_duration_minutes: 15
    session_timeout_hours: 8
  password_policy:
    min_length: 8
    require_uppercase: true
    require_numbers: true
    require_special_chars: true
    prevent_recent_reuse: 12
  multi_factor:
    enabled_by_default: true
    methods: [sms, email, authenticator_app]
    grace_period_days: 7
```

### 4. Operational Characteristics
Define how the component behaves in production:

```yaml
operational:
  startup:
    config_validation: required
    dependency_checks: [database, external_services]
    warm_up_strategy: "cache preload"
  shutdown:
    graceful_timeout_seconds: 30
    connection_draining: enabled
    persistence_flush: synchronous
  health_checks:
    endpoints: ["/health/ready", "/health/live"]
    dependencies: ["database", "message_queue"]
    response_timeout_seconds: 5
```

## SPEC Evolution and Maintenance

### Draft Phase
Initial specification development:

```yaml
# Draft status - interfaces subject to change
status: draft
versioning:
  breaking_changes_allowed: true
  review_required: true
```

### Implementation Phase
Stable specification for development:

```yaml
# Implementation ready - changes require ADR
status: implemented
versioning:
  semantic_versioning: enabled
  backward_compatibility: maintained
```

### Maintenance Phase
Specification updates for new requirements:

```yaml
changelog:
  - version: 1.2.0
    date: "2025-01-15"
    changes:
      - "Added support for mobile push notifications"
      - "Improved rate limiting accuracy"
    type: minor
```

## Common SPEC Patterns

### API Client Specifications
```yaml
id: external_api_client
interfaces:
  functions:
    - name: call_endpoint
      input: { endpoint: string, params: object, timeout: integer }
      output: { status: integer, data: object, headers: object }
caching:
  ttl_seconds: { success: 300, error: 60, unavailable: 30 }
rate_limiting:
  strategy: token_bucket
  capacity: 1000
  refill_rate_per_minute: 100
circuit_breaker:
  failure_threshold: 50
  recovery_timeout_seconds: 60
  monitoring_period_seconds: 300
metrics:
  - requests_total
  - errors_total
  - response_time_histogram
  - rate_limit_hits_total
```

### Data Processing Specifications
```yaml
id: data_transformation_service
interfaces:
  functions:
    - name: transform_data
      input: { source_data: object, target_schema: string }
      output: { transformed_data: object, validation_errors: array }
processing:
  batch_size: 1000
  parallelism: 4
  error_handling: continue_on_error
schemas:
  input_validation: strict
  output_guarantee: complete_transformation
  partial_failure_handling: error_collection
monitoring:
  records_processed_total
  transformation_errors_total
  processing_time_histogram
  queue_depth_gauge
```

### Storage Component Specifications
```yaml
id: data_storage_service
interfaces:
  classes:
    - name: Repository
      methods:
        - save: { params: object, return: string }
        - find_by_id: { params: string, return: object }
        - find_by_query: { params: object, return: array }
        - delete_by_id: { params: string, return: boolean }
storage:
  engine: postgresql
  connection_pool: { min: 2, max: 20, timeout: 30 }
  retry_policy: { max_attempts: 3, backoff: exponential }
  indexing: { primary_key: true, timestamp: true }
  partitioning: daily_by_created_at
durability:
  replication_factor: 3
  write_consistency: quorum
  backup_frequency_hours: 6
monitoring:
  connections_active
  query_duration_histogram
  replication_lag_seconds
  storage_used_bytes
```

## Integration with Development Workflow

### Design Time
- Use SPECs as contracts for component interactions
- Reference SPECs in architecture reviews and ADRs
- Validate SPECs against requirement acceptance criteria

### Development Time
- Generate boilerplate code from SPEC interfaces
- Implement against SPEC-defined contracts
- Use SPECs for automated test generation
- Validate implementation compliance with SPEC requirements

### Testing Time
- Test against SPEC-defined success criteria
- Validate performance against SPEC targets
- Monitor using SPEC-defined metrics
- Verify contracts between components

### Deployment Time
- Configure components using SPEC parameters
- Set up monitoring based on SPEC requirements
- Validate deployment against SPEC operational requirements

## Benefits of Specification-Driven Development

1. **Implementation Consistency**: Standardized component patterns across the system
2. **Automated Validation**: Specifications enable automated testing and compliance checking
3. **Parallel Development**: Clear contracts allow independent team development
4. **Operational Clarity**: Defined operational characteristics and monitoring
5. **Evolution Safety**: Structured change processes prevent unintended side effects

## Avoiding Common SPEC Pitfalls

1. **Incomplete Interfaces**: Missing error conditions or edge cases
   - Solution: Include exhaustive input/output specifications with error handling

2. **Ambiguous Performance**: Vague targets like "fast" or "reliable"
   - Solution: Use quantifiable metrics with specific units and thresholds

3. **Missing Operational Context**: Specifications without deployment considerations
   - Solution: Include startup, shutdown, health checks, and scaling requirements

4. **Technology Lock-in**: Specifications tied to specific implementations
   - Solution: Focus on behaviors and interfaces, not specific technology choices

5. **Maintenance Debt**: Specifications becoming outdated with code changes
   - Solution: Implement continuous validation and automated synchronization

## Tools and Automation

### Code Generation
```bash
# Generate Python client from SPEC (nested default)
generate-client --spec SPEC/SPEC-01_external_api_client/SPEC-01_external_api_client.yaml --output client_sdk/

# Generate interface stubs (nested default)
generate-stubs --spec SPEC/SPEC-02_ib_gateway_service/SPEC-02_ib_gateway_service.yaml --language python --framework flask

# Generate tests from SPEC (nested default)
generate-tests --spec SPEC/SPEC-03_resource_limit_service/SPEC-03_resource_limit_service.yaml --framework pytest
```

### Validation and Compliance
```bash
# Validate SPEC against schema (nested default)
validate-spec --spec SPEC/SPEC-NN_{slug}/SPEC-NN_{slug}.yaml --schema spec_schema.json

# Check SPEC-test alignment (nested default)
verify-spec-coverage --spec SPEC/SPEC-NN_{slug}/SPEC-NN_{slug}.yaml --tests tests/test_external_api/

# Generate API documentation (nested default)
generate-docs --spec SPEC/SPEC-NN_{slug}/SPEC-NN_{slug}.yaml --format openapi --output docs/api/
```

### Monitoring Configuration
```bash
# Generate monitoring configuration (nested default)
generate-monitoring --spec SPEC/SPEC-NN_{slug}/SPEC-NN_{slug}.yaml --output prometheus.yml

# Validate metrics against SPEC (nested default)
validate-metrics --spec SPEC/SPEC-NN_{slug}/SPEC-NN_{slug}.yaml --actual-metrics metrics.json
```

## Example SPEC Template

See `SPEC/SPEC-01_external_api_client.yaml` for a flat example (small, stable). For nested default, see `SPEC/examples/SPEC-02_nested_example/SPEC-02_nested_example.yaml`.
## File Size Limits

- Target: 300–500 lines per file
- Maximum (Markdown): 600 lines per file (absolute)
- YAML Exception (monolithic): Warnings at ~1000 lines, errors at ~2000 lines in linter; splitting is not required unless readability suffers.
- If a file approaches/exceeds limits, split specifications by domain/component while preserving coherent interfaces (prefer keeping YAML monolithic where logical).

## Document Splitting Standard

SPEC files (YAML) are typically monolithic per component/domain:
- Prefer monolithic unless extremely large or impacting readability
- If splitting, create multiple YAML specs grouped by domain/component and update references
- Keep interfaces coherent and avoid cross-file fragmentation of single interfaces
- Validate references and run size lints
