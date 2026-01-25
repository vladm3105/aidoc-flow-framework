---
title: "Specifications (SPEC)"
tags:
  - index-document
  - layer-9-artifact
  - shared-architecture
custom_fields:
  document_type: readme
  artifact_type: SPEC
  layer: 9
  priority: shared
---

# Specifications (SPEC)

## Generation Rules

- Index-only: maintain `SPEC-00_index.md` as the authoritative plan and registry (mark planned items with Status: Planned).
- Templates: default to the MVP template (`SPEC-MVP-TEMPLATE.yaml`); use the full profile only when explicitly set in project settings or clearly requested in the prompt.
- Inputs used for generation: `SPEC-00_index.md` + selected template profile (MVP by default); no skeletons are used.
- Example index: `ai_dev_flow/tmp/SYS-00_index.md`.

Note: Some examples in this document show a portable `docs/` root. In this repository, artifact folders live at the ai_dev_flow root without the `docs/` prefix; see README → “Using This Repo” for path mapping.

## Pre-Generation Planning Checklist

**⚠️ MANDATORY: Execute ALL checks below BEFORE creating a SPEC generation plan.**

This checklist prevents critical errors discovered in production (e.g., Trading Nexus v4.2 where 13 of 16 SPECs exceeded 20KB file size limit by 2-9x).

### 1. REQ-to-SPEC Mapping Analysis

**Purpose**: Verify which specific REQ files will be implemented by each SPEC.

**Required Actions**:
- [ ] **List all REQ files** in project: `find docs/07_REQ -name "REQ-*.md" | wc -l`
- [ ] **Identify REQ folder structure**: Verify FLAT vs NESTED organization
  ```bash
  ls -la docs/07_REQ/
  # FLAT: REQ files directly in 07_REQ/
  # NESTED: REQ-NN_{folder}/ subdirectories
  ```
- [ ] **Map REQs to SPECs**: Create detailed table showing:
  - SPEC ID
  - PRD alignment (vertical ID alignment check)
  - Specific REQ files (e.g., REQ-01.01 through REQ-01.12)
  - REQ count per SPEC
  - REQ folder path (NESTED structure)

**Output**: Section in generation plan titled "Detailed REQ-to-SPEC Mapping" with complete file-level assignments.

### 2. File Size Impact Analysis

**Purpose**: Estimate SPEC file sizes to prevent framework limit violations (20KB target, 20KB maximum for YAML).

**Required Actions**:
- [ ] **Check archived SPECs** (if available):
  ```bash
  ls -lh docs/09_SPEC/archive/*.yaml | awk '{print $5, $9}'
  ```
- [ ] **Calculate size-to-REQ ratio**: Analyze archived files
  ```bash
  for f in docs/09_SPEC/archive/SPEC-*.yaml; do
    echo "=== $f ==="
    wc -l "$f"
    grep -c "req_id:" "$f" || echo "0"
  done
  ```
- [ ] **Estimate new SPEC sizes** using formula:
  ```
  Estimated Size = (Average KB per REQ) × (REQ count for this SPEC)

  Example:
  - Archived SPEC-11: 79KB with 32 REQs = 2.47 KB/REQ
  - New SPEC with 60 REQs ≈ 148KB (7.4x over limit!)
  ```
- [ ] **Identify violations**: Flag any SPEC estimated >20KB
- [ ] **Document mitigation strategy**:
  - Option A: Accept warnings (not recommended)
  - Option B: Split into micro-SPECs (SPEC-NN.01, SPEC-NN.02)
  - Option C: Condensed YAML format (experimental)

**Output**: Section in generation plan titled "File Size Impact Analysis" with:
- Estimated size per SPEC
- Violation flags (⚠️ 2-5x over, 🔴 5x+ over)
- Mitigation recommendations

### 3. One-to-Many Structure Validation

**Purpose**: Verify correct application of vertical ID alignment and one-to-many rules.

**Required Actions**:
- [ ] **Count PRDs**: `ls docs/02_PRD/PRD-*.md | grep -v "00_Index" | wc -l`
- [ ] **Check SYS structure**: Identify which PRDs use one-to-many
  ```bash
  # Look for nested SYS folders
  ls -d docs/06_SYS/SYS-*/ 2>/dev/null
  ```
- [ ] **Verify SPEC IDs match PRD IDs**: SPEC-01 for PRD-01, SPEC-08.01 for PRD-08, etc.
- [ ] **Validate folder structure**:
  - Flat SPECs: `SPEC-NN_{slug}.yaml` (one-to-one)
  - Nested SPECs: `SPEC-NN_{slug}/SPEC-NN.01_{component}.yaml` (one-to-many)

**Output**: Section in generation plan showing SPEC structure (flat vs nested) aligned with PRD/SYS patterns.

### 4. CTR Integration Verification

**Purpose**: Ensure all required CTR (API Contract) files exist before referencing in SPECs.

**Required Actions**:
- [ ] **List available CTRs**:
  ```bash
  ls docs/08_CTR/CTR-*.{md,yaml} | grep -oE "CTR-[0-9]+" | sort -u
  ```
- [ ] **Map CTRs to SPECs**: Verify each SPEC has corresponding CTR
- [ ] **Check external CTRs**: Identify vendor API contracts (e.g., CTR-21 Vertex AI, CTR-22 Anthropic)

**Output**: CTR integration table in generation plan with status verification.

### 5. Framework Document Review

**Purpose**: Confirm latest framework rules are applied.

**Required Actions**:
- [ ] **Read creation rules**: `/opt/data/docs_flow_framework/ai_dev_flow/09_SPEC/SPEC_MVP_CREATION_RULES.md`
- [ ] **Check template version**: Verify `SPEC-MVP-TEMPLATE.yaml` is current
- [ ] **Review validation rules**: `/opt/data/docs_flow_framework/ai_dev_flow/09_SPEC/SPEC_MVP_VALIDATION_RULES.md`
- [ ] **Verify ID naming standards**: `/opt/data/docs_flow_framework/ai_dev_flow/ID_NAMING_STANDARDS.md`

**Output**: Reference to framework documents in generation plan with version/date confirmation.

### Checklist Summary

| Check | Purpose | Critical Risk if Skipped |
|-------|---------|--------------------------|
| 1. REQ Mapping | Complete traceability | Missing REQ implementations |
| 2. File Size Analysis | Prevent limit violations | Unprocessable YAML files, code gen failures |
| 3. One-to-Many Validation | Correct structure | ID misalignment, broken traceability |
| 4. CTR Integration | Complete API contracts | Missing interface definitions |
| 5. Framework Review | Latest rules applied | Non-compliant documents |

**Execution Time**: 15-30 minutes for thorough analysis
**Benefit**: Prevents hours of rework and generation failures

---

### Pre-Generation Plan Template Section

Every SPEC generation plan MUST include these sections (copy to generation plan):

```markdown
## Pre-Plan Verification (COMPLETED ✅)

### REQ Inventory Verification
- Total REQ files: [COUNT]
- REQ structure: [FLAT/NESTED]
- REQ naming pattern: [PATTERN]

### File Size Analysis
[TABLE with SPEC, REQ Count, Estimated Size, Status]

### One-to-Many Structure
[LIST of PRDs and their SPEC mapping]

### CTR Availability
[TABLE of CTR files with verification status]

### Framework Compliance
- Creation rules version: [DATE]
- Template version: [VERSION]
- ID naming standards: [COMPLIANCE %]
```

Specifications (SPEC) are machine-readable technical blueprints that define how software components should be implemented. SPECs transform requirements into actionable design decisions, providing complete implementation guidance for developers while establishing contracts for testing and integration.

Note: `SPEC-MVP-TEMPLATE.yaml` is the reference template. YAML stays monolithic per component for code generation.

## Structure Policy

- YAML: Monolithic single file per component (`SPEC-{DOC_NUM}_{slug}.yaml`).
- DOC_NUM: Variable-length starting at 2 digits (01, 02, 99, 100, 1000).
- Layout:
  - Flat (default): `09_SPEC/SPEC-{DOC_NUM}_{slug}.yaml` - single YAML per component
  - Nested (exception): `09_SPEC/SPEC-{DOC_NUM}_{slug}/SPEC-{DOC_NUM}_{slug}.yaml` when supporting files needed

### Examples

- Flat (default): [SPEC-01_api_client_example.yaml](./SPEC-01_api_client_example.yaml)
- Nested (exception): [SPEC-02_nested_example.yaml](./examples/SPEC-02_nested_example/SPEC-02_nested_example.yaml) - with split Markdown

## Codegen Compatibility

- Discovery (recursive):
  - Bash: `find SPEC -type f -name 'SPEC-*.yaml'`
  - Python: `glob.glob('09_SPEC/**/SPEC-*.yaml', recursive=True)`
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

## REQ → SPEC Relationship (Critical)

**Core Principle**: SPEC implements REQ requirements without duplicating them.

### Source of Truth
- **REQ files** = Source of truth for the "WHAT" (requirements, acceptance criteria, constraints)
- **SPEC files** = Source of truth for the "HOW" (interfaces, methods, types, implementation details)

### Reference, Don't Duplicate (Option A)
SPECs **reference** REQ files rather than copying requirement text:

```yaml
# ✅ CORRECT: Reference the REQ
traceability:
  upstream_sources:
    atomic_requirements:
      - id: "REQ-042"
        link: "../07_REQ/SYS-03_session/REQ-042_session_creation.md"
        title: "Session Creation Requirements"

# ❌ WRONG: Duplicating requirement text in SPEC
# requirement_text: "The system shall create a session within 100ms..."
```

### Per-REQ Implementation Sections (Option D)
Each SPEC contains a `req_implementations` section that maps REQs to implementation details:

```yaml
req_implementations:
  - req_id: "REQ-042"
    req_link: "../07_REQ/SYS-03_session/REQ-042_session_creation.md"
    implementation:
      interfaces:
        - class: "SessionManager"
          method: "create_session"
          signature: "async def create_session(user_id: str, context: dict) -> Session"
      data_models:
        - name: "Session"
          fields: ["session_id", "user_id", "created_at", "expires_at"]
      validation_rules:
        - "user_id must be non-empty string"
        - "context must contain 'client_ip'"
      error_handling:
        - error: "INVALID_USER_ID"
          condition: "user_id is empty or None"
          response: "400 Bad Request"

  - req_id: "REQ-043"
    req_link: "../07_REQ/SYS-03_session/REQ-043_session_validation.md"
    implementation:
      interfaces:
        - class: "SessionManager"
          method: "validate_session"
          signature: "async def validate_session(session_id: str) -> ValidationResult"
      # ... implementation details for this REQ
```

### Benefits of This Approach
1. **Single Source of Truth**: Requirements live in REQ files only
2. **No Information Loss**: Every REQ gets its own implementation section
3. **Clear Traceability**: Direct mapping from REQ to implementation code
4. **Maintainability**: Update requirement in REQ file, not in multiple SPECs
5. **Code Generation Ready**: Implementation sections are machine-readable

## Position in Document Workflow

**⚠️ See [../index.md](../index.md#traceability-flow) for the authoritative workflow visualization.**

**Layer 9: Technical Specifications**

SPECs sit between REQ (atomic requirements) and TASKS (implementation tasks) in the 14-layer architecture (Layers 0-13):

**⚠️ See for the full document flow: [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](../SPEC_DRIVEN_DEVELOPMENT_GUIDE.md)**

## Implementation-Readiness & Concrete Examples

### Implementation-Readiness Scoring

Before starting code development, validate SPEC completeness using the `validate_spec_implementation_readiness.py` script. The validator scores SPEC files on 10 dimensions (0-100 points):

| Criterion | Requirement | Points |
|-----------|-------------|--------|
| Architecture | Component structure, dependencies, patterns | 10 |
| Interfaces | External APIs, internal APIs, classes | 10 |
| Behavior | State machines, algorithms, workflows | 10 |
| Performance | Latency targets, throughput, resource limits | 10 |
| Security | Authentication, authorization, encryption | 10 |
| Observability | Logging, metrics, tracing, alerts | 10 |
| Verification | Unit, integration, contract, performance tests | 10 |
| Implementation | Configuration, deployment, scaling details | 10 |
| REQ Mapping | req_implementations linking REQs to code | 10 |
| Concrete Examples | Pseudocode, algorithms, API examples, models | 10 |

**Target**: ≥90 points for implementation readiness.

**Usage**:
```bash
python scripts/validate_spec_implementation_readiness.py --directory docs/09_SPEC --min-score 90
```

### Pseudocode & Algorithm Pattern

Include detailed algorithms and pseudocode in behavior sections:

```yaml
behavior:
  process_order: |
    Algorithm: Process Trading Order
    
    INPUTS: order (symbol, quantity, action, price)
    OUTPUT: order_id or error
    
    STEPS:
    1. Validate order parameters
       - symbol in market_data.symbols → success
       - quantity > 0 → success
       - price > 0 → success
       - On failure → throw ValidationError
    
    2. Check account resources
       - If (action == BUY):
         * Required funds = quantity × price
         * If account.balance >= required_funds → success
         * Else → throw InsufficientFundsError
       - Else (action == SELL):
         * If account.positions[symbol] >= quantity → success
         * Else → throw InsufficientSharesError
    
    3. Submit to broker (with retries)
       - MAX_RETRIES = 3
       - For attempt = 1 to MAX_RETRIES:
         * Try: call broker_api.submit_order(order)
         * If success: break
         * If RateLimitError: sleep(2^attempt), continue
         * If ConnectionError: sleep(2^attempt), continue
         * If ServiceError: log error, break
       - If all attempts failed: throw BrokerSubmissionError
    
    4. Update state
       - order_id = broker_response.order_id
       - position_tracker.update(order)
       - emit OrderExecuted(order_id, status)
    
    5. Return
       - success: return order_id
       - failure: raise error with recovery_hint
  
  error_recovery: |
    Recovery Strategy by Error Type:
    
    - ValidationError:
      * Action: Reject request, return 400
      * Recovery: Client validates before retry
    
    - RateLimitError:
      * Action: Exponential backoff (2^n seconds, max 32s)
      * Recovery: Automatic retry, max 3 attempts
    
    - BrokerConnectionError:
      * Action: Circuit breaker trips after 5 consecutive failures
      * Recovery: Half-open state after 30s, test with single request
    
    - ResourceExhausted:
      * Action: Shed low-priority requests
      * Recovery: Scale horizontally or increase resource limits
```

### Concrete API Examples

Include realistic request/response examples with actual data:

```yaml
interfaces:
  external_apis:
    - endpoint: "POST /api/v1/orders"
      description: "Submit trading order"
      
      example_request:
        symbol: "TSLA"
        quantity: 10
        action: "BUY"
        order_type: "LMT"
        limit_price: 150.50
        time_in_force: "DAY"
      
      example_response:
        order_id: "ord_789456"
        status: "accepted"
        filled_quantity: 0
        avg_fill_price: null
        created_at: "2026-01-25T14:30:00Z"
      
      example_error:
        error_code: "INSUFFICIENT_FUNDS"
        message: "Account balance insufficient"
        required_amount: 1505.00
        available_amount: 1000.00
```

### Data Model Examples (Pydantic)

Include typed data models with Field validators and examples:

```yaml
implementation:
  data_models:
    # Python/Pydantic format
    - name: "OrderRequest"
      language: "python"
      code: |
        from pydantic import BaseModel, Field
        from typing import Literal
        from decimal import Decimal
        
        class OrderRequest(BaseModel):
            symbol: str = Field(..., example="TSLA", min_length=1)
            quantity: int = Field(..., example=10, gt=0)
            action: Literal["BUY", "SELL"] = Field(default="BUY")
            order_type: Literal["MKT", "LMT", "STP"] = "MKT"
            limit_price: Decimal = Field(optional=True, example=150.50, decimal_places=2)
            time_in_force: Literal["DAY", "GTC", "IOC"] = "DAY"
    
    - name: "OrderResponse"
      language: "python"
      code: |
        class OrderResponse(BaseModel):
            order_id: str = Field(..., example="ord_789")
            status: Literal["pending", "accepted", "filled", "cancelled"]
            filled_quantity: int = Field(default=0, ge=0)
            avg_fill_price: Decimal = Field(optional=True, decimal_places=2)
            created_at: datetime
            expires_at: datetime = Field(optional=True)
```

### Configuration & Deployment Examples

Include realistic deployment configurations:

```yaml
implementation:
  configuration:
    # Development environment
    development:
      broker:
        host: "localhost"
        port: 4002
        timeout_ms: 20000
        max_retries: 3
      cache:
        type: "in_memory"
        max_entries: 1000
      observability:
        log_level: "DEBUG"
        trace_sample_rate: 1.0
    
    # Production environment
    production:
      broker:
        host: "${BROKER_HOST}"
        port: 4002
        timeout_ms: 5000
        max_retries: 3
      cache:
        type: "redis"
        host: "${REDIS_HOST}"
        ttl_seconds: 300
      observability:
        log_level: "INFO"
        trace_sample_rate: 0.1
  
  deployment:
    container_image: "trading-engine:v1.0.0"
    replicas:
      min: 3
      max: 10
      target_cpu_percent: 70
    resources:
      memory: "2Gi"
      cpu: "1000m"
    health_checks:
      startup_delay_seconds: 10
      liveness_probe:
        path: "/health/live"
        interval_seconds: 30
        timeout_seconds: 5
```

---

## SPEC YAML Structure

### Header with Traceability Comments

YAML files include traceability links in comment headers:

```yaml
# @requirement:[REQ-NN](../../07_REQ/.../REQ-NN_...md#REQ-NN)
# @adr:[ADR-NN](../../05_ADR/ADR-NN_...md#ADR-NN)
# @bdd:[BDD-NN.SS:scenarios](../../04_BDD/BDD-NN_{suite}/BDD-NN.SS_{slug}.feature#scenarios)
id: component_name
summary: Single-sentence description of component purpose and scope.
```

### Core Specification Fields

```yaml
id: component_snake_case_name
summary: Brief description of component purpose
traceability:
  upstream:
    - "[REQ-NN](../../07_REQ/.../REQ-NN_...md#REQ-NN)"
    - "[ADR-NN](../../05_ADR/ADR-NN_...md#ADR-NN)"
  downstream:
    - code: path/to/implementation.py
    - contract: path/to/api.yaml

requirements_source:
  - "[PRD-NN](../../../02_PRD/PRD-NN_...md)"
  - "[SYS-NN](../../../06_SYS/SYS-NN_...md)"
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
    - "[BDD-NN.SS_{slug}.feature:L23](../../04_BDD/BDD-NN_{suite}/BDD-NN.SS_{slug}.feature#L23)"  # Specific scenario line
    - "[BDD-NN.SS_{slug}.feature:L45](../../04_BDD/BDD-NN_{suite}/BDD-NN.SS_{slug}.feature#L45)"  # Additional scenarios
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

## Layer Scripts

This layer includes a dedicated `scripts/` directory containing validation and utility scripts specific to this document type.

- **Location**: `09_SPEC/scripts/`
- **Primary Validator**: `validate_spec_quality_score.sh`
- **Usage**: Run scripts directly or usage via `validate_all.py`.

## File Organization Hierarchy

```
`09_SPEC/
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
`09_SPEC/{domain}/SPEC-NN_{component_name}.yaml
```

Where:
- `09_SPEC/` is the base specifications directory
- `{domain}` is architectural domain (`services`, `data`, `api`, etc.)
- `SPEC` is the constant prefix
- `NNN` is the 2+ digit sequence number (01, 02, 003, etc.)
- `{component_name}` uses snake_case describing the component
- `.yaml` is the required file extension

**Examples:**
- `09_SPEC/SPEC-01_external_api_client/SPEC-01_external_api_client.yaml`
- `09_SPEC/data/SPEC-042_real_time_price_processor.yaml`
- `09_SPEC/api/SPEC-102_service_api_gateway.yaml`

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
# Generate Python client from SPEC (flat default)
generate-client --spec 09_SPEC/SPEC-01_external_api_client.yaml --output client_sdk/

generate-stubs --spec 09_SPEC/SPEC-02_ib_gateway_service.yaml --language python --framework flask

generate-tests --spec 09_SPEC/SPEC-03_resource_limit_service.yaml --framework pytest

```

### Validation and Compliance
```bash
# Validate SPEC against schema (flat default)
validate-spec --spec 09_SPEC/SPEC-NN_{slug}.yaml --schema spec_schema.json

verify-spec-coverage --spec 09_SPEC/SPEC-NN_{slug}.yaml --tests tests/test_external_api/

generate-docs --spec 09_SPEC/SPEC-NN_{slug}.yaml --format openapi --output docs/api/

```

### Monitoring Configuration
```bash
# Generate monitoring configuration (flat default)
generate-monitoring --spec 09_SPEC/SPEC-NN_{slug}.yaml --output prometheus.yml

validate-metrics --spec 09_SPEC/SPEC-NN_{slug}.yaml --actual-metrics metrics.json

```

## Example SPEC Template

See `09_SPEC/SPEC-01_external_api_client.yaml` for the flat default layout. For nested exception (with supporting files), see `09_SPEC/examples/SPEC-02_nested_example/SPEC-02_nested_example.yaml`.

## File Size Limits (Warning)

- **Target**: <15,000 tokens per file
- **Maximum**: 20,000 tokens (Error limit)
- **YAML (monolithic)**: Warning at 20,000 tokens

---

## SPEC Generation Plan Requirements (MANDATORY)

When creating a `SPEC_GENERATION_PLAN.md` for a project, the following requirements MUST be satisfied to ensure accuracy and framework compliance.

### Pre-Plan Verification Checklist

Before writing any generation plan, execute these verification steps:

#### 1. Verify Actual REQ Inventory

```bash
# Count actual REQ files in project
find docs/07_REQ -name "REQ-*.md" | wc -l

# List all REQ files to verify naming pattern
find docs/07_REQ -name "REQ-*.md" | head -20

# Determine structure: FLAT vs NESTED
ls -la docs/07_REQ/
```

**Critical**: Do NOT assume REQ counts or ranges. Verify actual file inventory.

#### 2. Verify REQ Path Structure

REQ files may be organized in two patterns:

| Pattern | Example Path | Detection |
|---------|--------------|-----------|
| **Flat** | `07_REQ/REQ-01_jwt_authentication.md` | Files directly in `07_REQ/` |
| **Nested** | `07_REQ/SYS-01_iam/REQ-01_authentication.md` | Subdirectories per SYS module |

**Use the actual project structure** - never assume nested when flat or vice versa.

#### 3. Verify SYS Module Mapping

```bash
# List SYS modules if nested structure
ls -d docs/07_REQ/SYS-* 2>/dev/null || echo "Flat structure detected"

# Count REQs per SYS module (if nested)
for dir in docs/07_REQ/SYS-*/; do
  echo "$dir: $(ls "$dir"REQ-*.md 2>/dev/null | wc -l) REQs"
done
```

### Required Plan Sections

Every SPEC Generation Plan MUST include:

| Section | Purpose | Reference |
|---------|---------|-----------|
| **Index-Only Workflow** | Explain `SPEC-00_index.md` role as authoritative registry | README.md line 18 |
| **REQ Inventory (Verified)** | Actual REQ count and ranges from filesystem scan | Pre-Plan Step 1 |
| **REQ Path Format** | Actual path structure (flat vs nested) | Pre-Plan Step 2 |
| **TASKS-Ready Scoring Criteria** | 4×25% breakdown for scoring | Creation Rules Section 7 |
| **Cross-Document Validation** | Validation loop and XDOC error codes | Creation Rules Section 15 |
| **Threshold Registry Format** | `threshold_references` section with `keys_used` | Creation Rules Section 14 |
| **Common Mistakes Reference** | Link to Creation Rules Section 12 | Creation Rules Section 12 |
| **File Size Limits** | 20,000 tokens hard limit, 15,000 warning | This section |

### TASKS-Ready Scoring Criteria (Include in Plan)

Plans MUST document the 4×25% scoring breakdown:

| Category | Weight | Criteria |
|----------|--------|----------|
| **YAML Completeness** | 25% | Metadata (10%), Traceability (10%), Sections (5%) |
| **Interface Definitions** | 25% | External APIs (15%), Internal interfaces (5%), Data schemas (5%) |
| **Implementation Specs** | 25% | Behavior sections (15%), Performance/security targets (5%), Dependencies (5%) |
| **Code Generation Readiness** | 25% | Machine-readable (15%), TASKS-ready metadata (5%), Validation schemas (5%) |

**Quality Gate**: Score ≥90% required before TASKS generation.

### Cross-Document Validation Loop (Include in Plan)

Plans MUST include this mandatory validation workflow:

```
VALIDATION LOOP:
1. Run: python scripts/validate_cross_document.py --document {doc_path} --auto-fix
2. IF errors fixed: GOTO step 1 (re-validate)
3. IF warnings fixed: GOTO step 1 (re-validate)
4. IF unfixable issues: Log for manual review, continue
5. IF clean: Mark VALIDATED, proceed to next artifact
```

**Validation Error Codes**:

| Code | Description | Severity |
|------|-------------|----------|
| XDOC-001 | Referenced requirement ID not found | ERROR |
| XDOC-002 | Missing cumulative tag | ERROR |
| XDOC-003 | Upstream document not found | ERROR |
| XDOC-006 | Tag format invalid | ERROR |
| XDOC-007 | Gap in cumulative tag chain | ERROR |
| XDOC-009 | Missing traceability section | ERROR |

### Threshold Registry Format (Include in Plan)

Plans MUST show the `threshold_references` section format:

```yaml
threshold_references:
  registry_document: "PRD-NN"
  keys_used:
    - perf.api.p95_latency
    - timeout.request.sync
    - limit.api.requests_per_second
    - retry.max_attempts
```

**Requirement**: No hardcoded performance/timeout values. All quantitative values MUST use `@threshold` references.

### Common Mistakes to Avoid (Link in Plan)

Plans MUST reference SPEC_MVP_CREATION_RULES.md Section 12 and include this summary:

| Mistake | Correct Approach |
|---------|------------------|
| Assumed REQ counts/ranges | Verify actual filesystem inventory |
| Wrong REQ path format | Check flat vs nested structure |
| Hardcoded performance values | Use `@threshold: PRD.NN.key` references |
| Missing `req_implementations` | Required for every upstream REQ |
| REQ in `downstream_artifacts` | REQ is UPSTREAM - use `upstream_sources.atomic_requirements` |
| File size > 20,000 tokens | Warning threshold; consider splitting |
| Status/score mismatch | Match status to TASKS-ready score threshold |

### Plan Validation Checklist

Before finalizing a SPEC Generation Plan, verify:

- [ ] REQ inventory verified via filesystem scan
- [ ] REQ path format matches actual project structure
- [ ] SPEC-00_index.md role documented
- [ ] TASKS-ready scoring criteria (4×25%) included
- [ ] Cross-document validation loop documented
- [ ] Threshold registry format shown
- [ ] Common mistakes section referenced
- [ ] File size limit (20,000 tokens) documented
- [ ] All REQ → SPEC mappings use verified ranges
