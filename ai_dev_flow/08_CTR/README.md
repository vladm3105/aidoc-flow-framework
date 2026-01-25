---
title: "API Contracts (CTR) - README"
tags:
  - index-document
  - layer-9-artifact
  - shared-architecture
custom_fields:
  document_type: readme
  artifact_type: CTR
  layer: 9
  priority: shared
---

# API Contracts (CTR) - README

## Generation Rules

- Index-only: maintain `CTR-00_index.md` as the authoritative plan and registry (mark planned items with Status: Planned).
- Templates: default to the MVP template; use the full (sectioned) template only when explicitly set in project settings or clearly requested in the prompt.
- Inputs used for generation: `CTR-00_index.md` + selected template profile; no skeletons are used.
- Example index: `ai_dev_flow/tmp/SYS-00_index.md`.

## 1. Purpose

API Contracts (CTR) define precise interface specifications between components using a **Design by Contract** approach. Contracts establish formal agreements on:
- Request/response schemas (structure, types, constraints)
- Error codes and failure modes
- Quality attributes (latency, throughput, idempotency)
- Versioning policies and compatibility rules

Contracts enable parallel development by allowing providers and consumers to implement independently against the same specification, reducing integration time and defects.


## 2. Position in Document Workflow

**⚠️ See [../index.md](../index.md#traceability-flow) for the authoritative workflow visualization.**

**⚠️ See for the full document flow: [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](../SPEC_DRIVEN_DEVELOPMENT_GUIDE.md)**

> **Note on Diagram Labels**: The above flowchart shows the sequential workflow. For formal layer numbers used in cumulative tagging, always reference the 14-layer architecture (Layers 0-13) defined in README.md. Diagram groupings are for visual clarity only.

**When to Create Contracts**: After atomic requirements (REQ) define WHAT components must do, create contracts to specify HOW components communicate. Contracts precede technical specifications (SPEC) to establish interface agreements before implementation.

**Workflow Summary**:
- **REQ** defines functional requirements (what must happen)
- **CTR** defines interface contracts (how components communicate)
- **SPEC** defines implementation details (how requirements + contracts are realized)

## 3. Dual-File Structure


### 3.1 Markdown File (.md)
**Purpose**: Human-readable documentation
**Contains**:
- Context: Problem statement, background, driving forces
- Contract definition: Parties, communication patterns
- Requirements satisfied: Traceability to 07_REQ/ADR
- Error handling: Error codes, failure modes, recovery strategies
- Quality attributes: Performance, security, reliability targets
- Versioning strategy: Compatibility rules, deprecation policy
- Examples: Request/response samples, edge cases
- Traceability: Upstream sources, SPEC requirements (not specific IDs)

**Audience**: Developers, architects, product managers

### 3.2 YAML File (.yaml)
**Purpose**: Machine-readable schema
**Contains**:
- Contract metadata: ID, version, service type
- Traceability references: Upstream 07_REQ/ADR IDs
- Request/response schemas: JSON Schema format
- Error codes: Code, HTTP status, description, retry safety
- Quality attributes: Latency, throughput, timeouts
- Versioning metadata: Breaking changes, compatibility flags
- security requirements: Authentication, authorization, encryption

**Audience**: Code generators, schema validators, contract test frameworks

### 3.3 Why Both Formats?

| Aspect | Markdown (.md) | YAML (.yaml) |
|--------|---------------|--------------|
| **Readability** | High - formatted prose | Low - structured data |
| **Context** | Rich - rationale, alternatives | Minimal - schemas only |
| **Tooling** | Limited - documentation only | Extensive - validation, codegen |
| **Validation** | Manual - human review | Automated - schema validation |
| **Traceability** | Detailed - links to all artifacts | Minimal - ID references only |
| **Examples** | Rich - multiple scenarios | Basic - schema structure |

**Best Practice**: Markdown provides context and rationale, YAML enables automation. Both must be synchronized (same CTR-NN, same schema structure).

## Layer Scripts

This layer includes a dedicated `scripts/` directory containing validation and utility scripts specific to this document type.

- **Location**: `08_CTR/scripts/`
- **Primary Validator**: `validate_ctr_quality_score.sh`
- **Usage**: Run scripts directly or usage via `validate_all.py`.

## 4. File Naming Convention

### 4.1 Format
```
CTR-NN_descriptive_slug.md
CTR-NN_descriptive_slug.yaml
```

- **CTR**: Constant prefix (API Contracts)
- **NNN**: 2+ digit sequence number (01, 02, 015)
- **Slug**: snake_case descriptive title (lowercase, underscores)
- **Extension**: .md for documentation, .yaml for schema

### 4.2 Examples
```
CTR-01_data_validation.md
CTR-01_data_validation.yaml

CTR-010_service_orchestrator_api.md
CTR-010_service_orchestrator_api.yaml

CTR-025_pubsub_trade_event_schema.md
CTR-025_pubsub_trade_event_schema.yaml
```

### 4.3 Rules
- Both files MUST exist for each contract (paired creation)
- Both files MUST use identical CTR-NN and slug
- H1 header in .md MUST match: `# CTR-NN: [Title]`
- `contract_id` in .yaml MUST be lowercase_snake_case version of slug

## 5. Organization by Service Type

### 5.1 Recommendation
Organize contracts in subdirectories by service type for better document management and SPEC alignment.

### 5.2 Directory Structure Example
```
`08_CTR/
├── agents/              # Agent-to-agent communication contracts
│   ├── CTR-01_service_orchestrator_api.md
│   ├── CTR-01_service_orchestrator_api.yaml
│   ├── CTR-02_item_selection_interface.md
│   └── CTR-02_item_selection_interface.yaml
├── mcp/                 # MCP server contracts
│   ├── CTR-010_risk_validator_mcp.md
│   ├── CTR-010_risk_validator_mcp.yaml
│   ├── CTR-011_greeks_calculator_mcp.md
│   └── CTR-011_greeks_calculator_mcp.yaml
├── infra/               # Infrastructure service contracts
│   ├── CTR-020_pubsub_message_schema.md
│   ├── CTR-020_pubsub_message_schema.yaml
│   ├── CTR-021_cloud_sql_data_model.md
│   └── CTR-021_cloud_sql_data_model.yaml
└── shared/              # Cross-cutting contracts (optional)
    ├── CTR-100_common_data_types.md
    └── CTR-100_common_data_types.yaml
```

### 5.3 Service Type Definitions

| Service Type | Purpose | Examples |
|--------------|---------|----------|
| **agents/** | Agent-to-agent communication | [ORCHESTRATION_COMPONENT] API, Strategy Agent interfaces |
| **mcp/** | MCP server contracts | Risk Validator MCP, [METRICS - e.g., performance indicators, quality scores] Calculator MCP, [EXTERNAL_DATA - e.g., customer data, sensor readings] MCP |
| **infra/** | Infrastructure services | Pub/Sub schemas, database models, Cloud Run endpoints |
| **shared/** | Cross-cutting contracts | Common data types, error code standards, auth patterns |

### 5.4 Benefits of Organization

#### Better Document Management
- **Scalability**: Supports management of 50+ contracts across multiple teams
- **Discovery**: Find contracts by service type (e.g., "show me all MCP contracts")
- **Ownership**: Clear responsibility (agent team owns `agents/`, infra team owns `infra/`)

#### SPEC Compatibility
- **Alignment**: Directory structure mirrors SPEC organization
  - `08_CTR/agents/CTR-NN` → `09_SPEC/agents/SPEC-NN`
  - `08_CTR/mcp/CTR-NN` → `09_SPEC/mcp/SPEC-NN`
- **Traceability**: Enables tracing CTR → SPEC relationships
- **Navigation**: Consistent paths across contract and implementation docs

#### Team Collaboration
- **Clear Boundaries**: Each team manages their service type directory
- **Parallel Development**: Teams work independently in their directories
- **Code Owners**: CODEOWNERS file can assign review permissions by directory

### 5.5 When to Use Subdirectories

| Project Size | Organization | Rationale |
|--------------|--------------|-----------|
| **<10 contracts** | Flat directory | Simple, no navigation overhead |
| **10-30 contracts** | Optional subdirectories | Consider if multiple service types exist |
| **30+ contracts** | **Use subdirectories** | Mandatory for maintainability |
| **Multiple teams** | **Use subdirectories** | Clear ownership and responsibility |

**Recommendation**: Start flat, migrate to subdirectories when you have 3+ contracts per service type.

## 6. SPEC-Readiness & Data Model Patterns

### 6.1 SPEC-Readiness Scoring

Before generating SPEC documents from CTR contracts, validate readiness using the `validate_ctr_spec_readiness.py` script. The validator scores CTR files on 10 dimensions (0-100 points):

| Criterion | Requirement | Points |
|-----------|-------------|--------|
| API Specification | Endpoint/method documentation | 10 |
| Data Models | Pydantic OR JSON Schema | 10 |
| Error Handling | Exception catalog with HTTP codes | 10 |
| Versioning | Version policy and breaking changes | 10 |
| Testing | Contract test strategy | 10 |
| Endpoints | GET/POST/PUT/DELETE documented | 10 |
| OpenAPI/Schema | OpenAPI or JSON Schema reference | 10 |
| Type Annotations | 3+ `param: Type -> ReturnType` examples | 10 |
| Error Recovery | 2+ recovery strategies (retry, backoff, circuit breaker, timeout) | 10 |
| Concrete Examples | 10+ real domain instances (IDs, dates, symbols) | 10 |

**Target**: ≥90 points for SPEC generation readiness.

**Usage**:
```bash
python scripts/validate_ctr_spec_readiness.py --directory docs/08_CTR --min-score 90
```

### 6.2 Pydantic Model Pattern

Include Pydantic models with Literal types, Field validators, and concrete examples:

```python
from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime

class OrderRequest(BaseModel):
    """Contract request model with examples and constraints"""
    trace_id: str = Field(..., example="trace_ord_123")
    order_id: str = Field(..., example="ord_456")
    symbol: str = Field(..., example="TSLA")
    action: Literal["BUY", "SELL"] = Field(default="BUY", example="BUY")
    quantity: int = Field(..., example=10, gt=0)
    limit_price: float = Field(optional=True, example=150.50, gt=0)
    order_type: Literal["MKT", "LMT", "STP", "STP_LMT"] = "MKT"
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class OrderResponse(BaseModel):
    """Contract response model"""
    trace_id: str
    order_id: str
    status: Literal["accepted", "rejected", "pending"]
    filled_quantity: int = 0
    avg_price: float = Field(optional=True, example=150.25)
    error_code: Literal[None, "INVALID_SYMBOL", "INSUFFICIENT_FUNDS", "RATE_LIMITED"] = None
    message: str = Field(optional=True, example="Order accepted")
```

### 6.3 Type-Annotated Usage Examples

Provide typed function examples showing contract usage:

```python
def validate_order(order: OrderRequest) -> bool:
    """Validate order before submission"""
    return order.quantity > 0 and order.limit_price > 0

def route_order(order: OrderRequest, broker: str) -> str:
    """Route order to broker endpoint"""
    return f"{broker}:{order.symbol}:{order.action}:{order.order_id}"

def format_response(order: OrderRequest, status: str) -> dict[str, object]:
    """Format order response with tracing"""
    return {
        "trace_id": order.trace_id,
        "order_id": order.order_id,
        "status": status,
        "timestamp": datetime.utcnow().isoformat()
    }

async def submit_order(order: OrderRequest, client: BrokerClient) -> OrderResponse:
    """Submit order with error recovery"""
    for attempt in range(3):
        try:
            response = await client.submit(order.model_dump())
            return OrderResponse(**response)
        except RateLimitError:
            if attempt < 2:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                continue
            raise
```

### 6.4 Concrete Domain Examples

Include realistic examples with domain-specific data:

| Aspect | Example | Guidance |
|--------|---------|----------|
| Symbols | `TSLA`, `GOOGL`, `SPY` | Use real trading symbols |
| IDs | `ord_789`, `user_456`, `acct_123` | Prefix with entity type |
| Dates | `2026-01-25T14:30:00Z` | ISO 8601 format |
| Prices | `150.50`, `0.01` | Real market values |
| Quantities | `10`, `100`, `1` | Domain-specific minimums |
| Account IDs | `DU123456`, `U789012` | Real IB account format |

---

## 7. Quality Gates

Before marking a contract as "Active", ensure:

- [ ] **Dual Files Exist**: Both .md and .yaml files created with matching CTR-NN_slug
- [ ] **Schema Valid**: YAML passes schema validation (yamllint, JSON Schema validator)
- [ ] **Traceability Complete**: All upstream 07_REQ/ADR referenced, SPEC requirements defined in Section 11.3
- [ ] **Error Handling Defined**: All error codes documented with retry strategies
- [ ] **Examples Present**: At least 3 examples (success, error, edge case)
- [ ] **Quality Attributes**: Performance, security, reliability targets specified
- [ ] **Versioning Policy**: Semantic versioning rules and deprecation policy documented
- [ ] **Stakeholder Approval**: Provider and consumer teams reviewed and approved
- [ ] **Contract Tests Planned**: Test strategy for validating implementation compliance
- [ ] **Index Updated**: CTR-00_index.md updated with new contract metadata

## 8. Writing Guidelines

### 7.1 Request/Response Schema Design

**Principles**:
- **Minimal**: Include only data required for operation (avoid over-specification)
- **Explicit**: All fields have clear descriptions and constraints
- **Versioned**: Support evolution through optional fields and semantic versioning
- **Validated**: Use JSON Schema constraints (type, required, minimum, maximum, pattern)

**Best Practices**:
```yaml
# Good: Clear constraints
field_name:
  type: integer
  minimum: 0
  maximum: 100
  description: "Percentage value between 0 and 100"

# Bad: No constraints
field_name:
  type: integer
  description: "Some number"
```

### 7.2 Error Handling Patterns

**Error Code Structure**:
- **Naming**: UPPER_SNAKE_CASE (INVALID_INPUT, RATE_LIMITED)
- **HTTP Status**: Match semantic meaning (400 client error, 500 server error)
- **Retry Safety**: Specify if safe to retry (idempotent operations: yes, mutations: no)

**Error Response Format**:
```json
{
  "error_code": "INVALID_INPUT",
  "error_message": "Human-readable description",
  "field_errors": [
    {"field": "[METRIC_1 - e.g., error rate, response time]", "error": "must be >= 0"}
  ],
  "timestamp": "2025-11-02T14:30:00Z",
  "request_id": "uuid"
}
```

### 7.3 Idempotency Considerations

**Idempotent Operations** (safe to retry):
- Validation endpoints (read-only)
- GET requests (retrieval)
- Calculations (deterministic)

**Non-Idempotent Operations** (not safe to retry):
- [OPERATION_EXECUTION - e.g., order processing, task execution] (creates side effects)
- State mutations (resource updates)
- Resource creation (may duplicate)

**Contract Specification**:
```yaml
endpoints:
  - name: validatePosition
    idempotent: true  # Same input always produces same output
    retry_safe: true  # Safe to retry on failure
```

### 7.4 Async vs Sync Contracts

| Pattern | When to Use | Latency | Complexity |
|---------|-------------|---------|------------|
| **Synchronous** | Request-response, immediate result needed | Low (<100ms) | Low |
| **Asynchronous** | Long-running operations, fire-and-forget | High (100ms-seconds) | Medium |
| **Event-Driven** | Pub/sub, multiple consumers, decoupling | High (seconds) | High |

**Synchronous Contract**:
```yaml
endpoints:
  - name: validatePosition
    synchronous: true
    request_schema: {...}
    response_schema: {...}
```

**Asynchronous Contract**:
```yaml
events:
  - name: PositionValidated
    async: true
    message_schema: {...}
    delivery_guarantee: at_least_once
```

## 9. Common Patterns

### 8.1 Synchronous Request/Response
**Use Case**: Immediate validation, calculations, queries
**Example**: Risk validation, [METRICS - e.g., performance indicators, quality scores] calculation, resource collection state query

**Schema Pattern**:
```yaml
endpoints:
  - name: operation_name
    synchronous: true
    request_schema:
      type: object
      required: [input_field]
      properties:
        input_field: {type: string}
    response_schema:
      type: object
      required: [status, result]
      properties:
        status: {type: string, enum: [success, error]}
        result: {type: object}
```

### 8.2 Asynchronous Message Contracts
**Use Case**: Event notification, fire-and-forget, pub/sub
**Example**: [OPERATION_EXECUTION - e.g., order processing, task execution] events, resource collection rebalancing triggers

**Schema Pattern**:
```yaml
events:
  - name: TradeExecuted
    async: true
    message_schema:
      type: object
      required: [event_id, timestamp, payload]
      properties:
        event_id: {type: string, format: uuid}
        timestamp: {type: string, format: date-time}
        payload:
          type: object
          properties:
            symbol: {type: string}
            [METRIC_1 - e.g., error rate, response time]: {type: number}
```

### 8.3 Pagination Patterns
**Use Case**: Large result sets, incremental data retrieval
**Example**: List all positions, historical trade log

**Schema Pattern**:
```yaml
request_schema:
  properties:
    page: {type: integer, minimum: 1, default: 1}
    page_size: {type: integer, minimum: 1, maximum: 100, default: 20}
    cursor: {type: string, description: "Opaque pagination cursor"}

response_schema:
  properties:
    items: {type: array, items: {type: object}}
    page_info:
      type: object
      properties:
        has_next_page: {type: boolean}
        next_cursor: {type: string}
        total_count: {type: integer}
```

### 8.4 Bulk Operations
**Use Case**: Batch validation, bulk updates, resource collection rebalancing
**Example**: Validate 100 positions, update 50 stop-losses

**Schema Pattern**:
```yaml
request_schema:
  properties:
    operations:
      type: array
      minItems: 1
      maxItems: 100
      items:
        type: object
        properties:
          id: {type: string}
          operation: {type: string, enum: [create, update, delete]}
          data: {type: object}

response_schema:
  properties:
    results:
      type: array
      items:
        type: object
        properties:
          id: {type: string}
          status: {type: string, enum: [success, error]}
          result: {type: object}
```

## 10. Traceability Requirements

### 9.1 Upstream Traceability (REQUIRED)

> **Traceability Rule**: Upstream traceability is REQUIRED for CTR documents. All CTR contracts MUST reference existing BRD through REQ documents.

Contracts MUST reference:
- **REQ**: Atomic requirements defining interface needs
- **ADR**: Architecture decisions justifying interface design
- **SYS**: System requirements specifying integration patterns

**Format** (in .md Traceability section):
```markdown
### Upstream Sources
| Source Type | Document ID | Document Title | Relevant sections | Relationship |
|-------------|-------------|----------------|-------------------|--------------|
| REQ | [REQ-03](../07_REQ/.../REQ-03.md) | [RESOURCE_LIMIT - e.g., request quota, concurrent sessions] Enforcement | section 3.1 | Interface requirement |
```

**Format** (in .yaml metadata):
```yaml
upstream_requirements:
  - REQ-03
upstream_adrs:
```

### 9.2 SPEC Implementation Requirements

> **Rule**: Do NOT reference specific SPEC-XX IDs during CTR creation. Instead, specify what SPEC files must implement.

**Required in Section 11.3 (SPEC Requirements)**:
- **Provider Requirements**: Interface methods, quality attributes, error handling
- **Consumer Requirements**: How to call contract, error handling, retry strategies  
- **Validation Requirements**: Contract testing approach, schema validation

**Format** (in .md Traceability section):
```markdown
### SPEC Requirements

**Provider SPEC Requirements**:
- Must implement all interface methods from Section 4
- Must satisfy quality attributes from Section 6
- Must handle all error scenarios from Section 5

**Consumer SPEC Requirements**:
- Must call provider using exact interface from Section 4
- Must handle all error codes from Section 5.1
- Must reference this CTR using `@ctr: CTR-NN` tags
```

### 9.3 Cross-Reference Format
```markdown
# In markdown files
[CTR-01](../08_CTR/CTR-01_data_validation.md#CTR-01)
[CTR-01 Schema](../08_CTR/CTR-01_data_validation.yaml)

# If using subdirectories
[CTR-01](../08_CTR/agents/CTR-01_service_orchestrator_api.md)
```

## 11. Integration with Workflow

### 10.1 How SPEC Files Reference Contracts

**SPEC YAML Structure**:
```yaml
component_name: risk_validation_service
component_type: service

# Contract reference
interface:
  contract_ref: CTR-01_data_validation
  contract_version: "1.0.0"
  role: provider  # or consumer

  # Implementation details
  request_validation: schema_validation_middleware
  response_formatting: json_serializer
  error_handling: standard_error_handler
```

**SPEC Markdown section**:
```markdown
## Interface Contract

This service implements **[CTR-01: resource Risk Validation](../08_CTR/CTR-01_data_validation.md)** as the provider.

**Contract Compliance**:
- Request validation: JSON Schema validation against CTR-01.yaml
- Response formatting: Matches CTR-01 response_schema
- Error codes: Implements all CTR-01 error codes (INVALID_INPUT, RATE_LIMITED, etc.)
```

### 10.2 How to Validate Implementation Against Contract

**Contract Tests** (Provider Side):
```python
# tests/08_CTR/risk_validation/test_provider_contract.py
import pact
from src.services.risk_validation_service import validate_position

def test_validatePosition_success(pact_provider):
    """Provider satisfies CTR-01 success scenario"""
    request = load_contract_example("CTR-01", "example_1_request")
    response = validate_position(request)

    assert_schema_valid(response, "CTR-01", "response_schema")
    assert response["is_valid"] == True
    assert "decision_id" in response
```

**Contract Tests** (Consumer Side):
```python
# tests/08_CTR/risk_validation/test_consumer_contract.py
import pact
from src.agents.service_orchestrator.risk_validator_client import RiskValidatorClient

def test_consumer_expects_ctr001_schema(pact_consumer):
    """Consumer expects CTR-01 response schema"""
    pact_consumer.expect_request(
        method="POST",
        path="/validate",
        body={"resource": {...}}
    ).will_respond_with(
        status=200,
        body=matches_schema("CTR-01", "response_schema")
    )

    client = RiskValidatorClient()
    result = client.validate_position(resource)
    assert result.is_valid is not None
```

## 12. Benefits

### 11.1 Enables Parallel Development
- **Independent Work**: Provider and consumer teams code simultaneously
- **Clear Interface**: Contract defines boundary, no ambiguity
- **No Blocking**: Teams don't wait for each other to finish

**Example**: Risk Validation Service team implements provider while 11 agent teams implement consumers, all referencing CTR-01.

### 11.2 Early Validation
- **Schema Validation**: Catch type errors before coding (JSON Schema)
- **Mock Testing**: Create test stubs from contract for TDD
- **Contract Testing**: Validate implementation compliance pre-integration

**Cost Savings**: Fix interface issues in design phase (hours) vs production (weeks).

### 11.3 Prevents Implementation Drift
- **Immutable Boundary**: Contract defines interface, implementation cannot deviate
- **Version Control**: Breaking changes require new major version
- **Contract Tests**: CI/CD enforces contract compliance

**Example**: Agent team cannot add undocumented field to request without updating CTR, which triggers provider team review.

### 11.4 Supports Contract Testing
- **Pact**: Consumer-driven contract testing framework
- **Spring Cloud Contract**: JVM-based contract testing
- **Custom**: Roll your own with JSON Schema validation

**CI/CD Integration**: Contract tests run on every PR, catch violations immediately.

## 13. Avoiding Pitfalls

### 12.1 Breaking Changes Without Version Bumps
**Problem**: Changing request schema without updating major version
**Impact**: Consumers break silently, production outages
**Solution**: Semantic versioning discipline, contract tests catch violations

### 12.2 Missing Error Handling
**Problem**: Contract defines only happy path, not error scenarios
**Impact**: Consumers don't know how to handle failures
**Solution**: Document all error codes, failure modes, retry strategies

### 12.3 Unclear Idempotency Guarantees
**Problem**: Contract doesn't specify if operation is idempotent
**Impact**: Consumers don't know if retry is safe, duplicate operations possible
**Solution**: Explicitly specify `idempotent: true|false` and `retry_safe: true|false`

### 12.4 Over-Specifying Implementation Details
**Problem**: Contract dictates internal implementation (e.g., "use Redis for caching")
**Impact**: Limits provider flexibility, unnecessary coupling
**Solution**: Specify interface behavior only (what), not implementation (how)

**Good Contract**:
```yaml
# Specifies behavior only
max_latency_ms: 100
idempotent: true
```

**Bad Contract**:
```yaml
# Specifies implementation details
caching_strategy: redis
database: postgresql
retry_library: tenacity
```

## 13. Tools

### 13.1 YAML Validators
```bash
# yamllint - YAML syntax validation
yamllint 08_CTR/CTR-01_data_validation.yaml
check-jsonschema --schemafile 08_CTR/CTR-01_data_validation.yaml
spectral lint 08_CTR/CTR-01_data_validation.yaml

```

### 13.3 Contract Testing Tools
- **Pact**: https://docs.pact.io/ - Consumer-driven contract testing
- **Spring Cloud Contract**: https://spring.io/projects/spring-cloud-contract - JVM contract testing
- **Dredd**: https://dredd.org/ - API contract validator

### 13.4 Schema Validators
```python
# Python: jsonschema library
from jsonschema import validate, ValidationError
import yaml

with open("CTR-01_data_validation.yaml") as f:
    contract = yaml.safe_load(f)
    schema = contract["endpoints"][0]["request_schema"]

try:
    validate(instance=request_data, schema=schema)
except ValidationError as e:
    print(f"Invalid request: {e.message}")
```

## 14. Examples

### 14.1 Template Files
- **[CTR-MVP-TEMPLATE.md](./CTR-MVP-TEMPLATE.md)**: 12-section markdown template (primary standard)
- **[CTR_MVP_SCHEMA.yaml](./CTR_MVP_SCHEMA.yaml)**: Validation schema defining 12-section structure and OpenAPI 3.x requirements

### 14.2 Example Scenarios

**Scenario 1: Synchronous Validation Endpoint**
- Use Case: Validate resource before [OPERATION_EXECUTION - e.g., order processing, task execution]
- Pattern: Request/response, <100ms latency
- Template section: Synchronous Request/Response

**Scenario 2: Asynchronous Event Schema**
- Use Case: Notify agents when resource collection rebalances
- Pattern: Pub/Sub, fire-and-forget
- Template section: Asynchronous Message Contracts

**Scenario 3: Paginated List Endpoint**
- Use Case: Retrieve all open positions
- Pattern: Cursor-based pagination
- Template section: Pagination Patterns

---

## Quick Reference

| Task | Location |
|------|----------|
| **Copy template** | CTR-MVP-TEMPLATE.md (structure) + OpenAPI 3.x YAML |
| **Reserve ID** | CTR-00_index.md (check next available) |
| **Naming format** | CTR-NN_snake_case_slug.md + .yaml |
| **Organize by type** | Optional: 08_CTR/{agents,mcp,infra}/ |
| **Link traceability** | 07_REQ/ADR (upstream), define SPEC requirements |

| **Contract tests** | Pact, Spring Cloud Contract, custom validators |
| **Update index** | Add entry to CTR-00_index.md |

---

**README Version**: 1.0
**Last Updated**: YYYY-MM-DD
**Next Review**: YYYY-MM-DD (recommend quarterly for active documentation)
## File Size Limits

- **Target**: <15,000 tokens per file
- **Maximum**: 20,000 tokens (Error limit)
- **YAML Exception**: If a contract approaches/exceeds limits, split content logically (e.g., separate endpoints/schemas) and maintain dual-file `.md` + `.yaml` structure (prefer monolithic YAML where logical).

## Document Splitting Standard

CTR uses a dual-file structure per contract (`.md` + `.yaml`):
- Prefer keeping each contract monolithic (pairs) unless extremely large
- If splitting is necessary, split by endpoint groups or modules, keeping pairs consistent (`CTR-XX_group.md` with `CTR-XX_group.yaml`)
- Update indexes and cross-references; validate and lint
