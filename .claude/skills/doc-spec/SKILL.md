---
title: "doc-spec: Create Technical Specifications (Layer 10)"
name: doc-spec
description: Create Technical Specifications (SPEC) - Layer 10 artifact using YAML format for implementation-ready specifications
tags:
  - sdd-workflow
  - layer-10-artifact
  - shared-architecture
custom_fields:
  layer: 10
  artifact_type: SPEC
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  skill_category: core-workflow
  upstream_artifacts: [REQ,IMPL,CTR]
  downstream_artifacts: [TASKS]
---

# doc-spec

## Purpose

Create **Technical Specifications (SPEC)** - Layer 10 artifact in the SDD workflow that defines implementation-ready specifications in YAML format, providing complete technical details for code generation.

**Layer**: 10

**Upstream**: BRD (Layer 1), PRD (Layer 2), EARS (Layer 3), BDD (Layer 4), ADR (Layer 5), SYS (Layer 6), REQ (Layer 7), IMPL (Layer 8), CTR (Layer 9)

**Downstream Artifacts**: TASKS (Layer 11), IPLAN (Layer 12), Code (Layer 13)

## Prerequisites

### Upstream Artifact Verification (CRITICAL)

**Before creating this document, you MUST:**

1. **List existing upstream artifacts**:
   ```bash
   ls docs/BRD/ docs/PRD/ docs/EARS/ docs/BDD/ docs/ADR/ docs/SYS/ docs/REQ/ 2>/dev/null
   ```

2. **Reference only existing documents** in traceability tags
3. **Use `null`** only when upstream artifact type genuinely doesn't exist
4. **NEVER use placeholders** like `BRD-XXX` or `TBD`
5. **Do NOT create missing upstream artifacts** - skip functionality instead


Before creating SPEC, read:

1. **Shared Standards**: `.claude/skills/doc-flow/SHARED_CONTENT.md`
2. **Upstream REQ**: Read atomic requirements (PRIMARY SOURCE)
3. **Upstream CTR**: Read contracts if Layer 9 created
4. **Template**: `ai_dev_flow/SPEC/SPEC-TEMPLATE.yaml`
5. **Creation Rules**: `ai_dev_flow/SPEC/SPEC_CREATION_RULES.md`
6. **Validation Rules**: `ai_dev_flow/SPEC/SPEC_VALIDATION_RULES.md`
7. **Validation Script**: `./ai_dev_flow/scripts/validate_spec_template.sh` (under development - use template for manual validation until available)

## When to Use This Skill

Use `doc-spec` when:
- Have completed BRD through REQ (Layers 1-7)
- Ready to create implementation-ready specifications
- Preparing for code generation or implementation
- Need complete technical details in structured format
- You are at Layer 10 of the SDD workflow

## SPEC-Specific Guidance

### 1. YAML Format (MANDATORY)

**Format**: Pure YAML (not markdown)

**Structure**:
```yaml
# SPEC-NNN: [Specification Title]

metadata:
  spec_id: SPEC-001
  title: "Order Validation Service Specification"
  version: "1.0.0"
  created_date: "2025-01-15"
  updated_date: "2025-01-15"
  status: "approved"
  owner: "team-backend"

cumulative_tags:
  brd: ["BRD-001:section-3"]
  prd: ["PRD-001:feature-2"]
  ears: ["EARS-001:E01"]
  bdd: ["BDD-001:scenario-validation"]
  adr: ["ADR-033", "ADR-045"]
  sys: ["SYS-001:FR-001"]
  req: ["REQ-risk-limits-001"]
  impl: ["IMPL-001:technical-approach"]  # optional
  contracts: ["CTR-001"]  # optional

overview:
  purpose: "Define trade order validation service implementation"
  scope: "Validate trade orders against position limits and business rules"
  requirements:
    - "REQ-risk-limits-001"
    - "REQ-risk-limits-002"

architecture:
  pattern: "layered"
  layers:
    - name: "controller"
      technology: "FastAPI"
      description: "REST API endpoint handlers"
    - name: "service"
      technology: "Python"
      description: "Business logic and validation"
    - name: "repository"
      technology: "SQLAlchemy"
      description: "Database access layer"

interfaces:
  api_endpoints:
    - endpoint: "/api/v1/trades/validate"
      method: "POST"
      contract_ref: "CTR-001"
      authentication: "Bearer token"
      rate_limit: 100
      rate_limit_window: "1min"

  data_models:
    - model: "TradeOrderRequest"
      schema_ref: "CTR-001#/components/schemas/TradeOrderRequest"
    - model: "ValidationResponse"
      schema_ref: "CTR-001#/components/schemas/ValidationResponse"

implementation:
  modules:
    - name: "controllers/trade_validation_controller.py"
      purpose: "API endpoint handlers"
      dependencies: ["services/trade_validator.py"]

    - name: "services/trade_validator.py"
      purpose: "Business logic and validation"
      dependencies:
        - "repositories/position_repository.py"
        - "models/trade_order.py"

    - name: "repositories/position_repository.py"
      purpose: "Database access for positions"
      dependencies: ["database/connection.py"]

  functions:
    - name: "validate_trade_order"
      module: "services/trade_validator.py"
      signature: "async def validate_trade_order(order: TradeOrderRequest) -> ValidationResponse"
      purpose: "Validate trade order against all rules"
      algorithm:
        - "1. Validate symbol exists"
        - "2. Check quantity is positive"
        - "3. Validate price within range"
        - "4. Check position limits"
        - "5. Return validation result"

error_handling:
  error_codes:
    - code: "INVALID_SYMBOL"
      http_status: 400
      message: "Symbol not found in approved list"
      recovery: "user_correction"

    - code: "LIMIT_EXCEEDED"
      http_status: 403
      message: "Position limit exceeded"
      recovery: "reduce_position"

configuration:
  environment_variables:
    - name: "MAX_POSITION_DELTA"
      type: "float"
      default: "0.50"
      required: true

  feature_flags:
    - name: "enable_strict_validation"
      default: false
      description: "Enable enhanced validation rules"

testing:
  unit_tests:
    - test: "test_validate_valid_order"
      module: "tests/unit/test_trade_validator.py"
      coverage_target: 95

  integration_tests:
    - test: "test_validation_endpoint"
      module: "tests/integration/test_trade_api.py"

  performance_tests:
    - test: "test_validation_latency"
      target: "P95 < 50ms"

deployment:
  container:
    image: "trade-validator:1.0.0"
    base: "python:3.11-slim"

  resources:
    cpu: "1000m"
    memory: "512Mi"

  scaling:
    min_replicas: 2
    max_replicas: 10
    target_cpu: 70

monitoring:
  metrics:
    - name: "validation_latency_ms"
      type: "histogram"
      labels: ["endpoint", "status"]

    - name: "validation_errors_total"
      type: "counter"
      labels: ["error_code"]

  alerts:
    - alert: "HighValidationLatency"
      condition: "P95 > 100ms"
      severity: "warning"

traceability:
  upstream_sources:
    - artifact: "BRD-001"
      sections: ["section-3"]
    - artifact: "PRD-001"
      sections: ["feature-2"]
    - artifact: "REQ-risk-limits-001"
      sections: ["all"]

  downstream_artifacts:
    - "TASKS-001"
    - "IPLAN-001"
    - "Code: src/services/trade_validator.py"
```

### 2. Required Top-Level Sections

**MANDATORY Sections**:
1. **metadata**: Spec ID, title, version, dates, status, owner
2. **cumulative_tags**: All upstream tags (8-10 tags depending on layers)
3. **overview**: Purpose, scope, requirements
4. **architecture**: Pattern, layers, technologies
5. **interfaces**: API endpoints, data models
6. **implementation**: Modules, functions, algorithms
7. **error_handling**: Error codes, HTTP status, recovery
8. **configuration**: Environment variables, feature flags
9. **testing**: Unit, integration, performance tests
10. **deployment**: Container, resources, scaling
11. **monitoring**: Metrics, alerts, logging
12. **traceability**: Upstream sources, downstream artifacts

### 3. cumulative_tags Field (NEW)

**CRITICAL**: SPEC must include cumulative_tags section with ALL upstream tags

**Format**:
```yaml
cumulative_tags:
  brd: ["BRD-001:section-3", "BRD-001:success-criteria"]
  prd: ["PRD-001:feature-2", "PRD-001:kpi-performance"]
  ears: ["EARS-001:E01", "EARS-001:S02"]
  bdd: ["BDD-001:scenario-validation"]
  adr: ["ADR-033", "ADR-045"]
  sys: ["SYS-001:FR-001", "SYS-001:NFR-001"]
  req: ["REQ-risk-limits-001"]
  impl: ["IMPL-001:technical-approach"]  # optional - omit if Layer 8 skipped
  contracts: ["CTR-001"]  # optional - omit if Layer 9 skipped
```

**Tag Count**: 7-9 tags (minimum 7 if IMPL/CTR skipped, 9 if both included)

### 4. contract_ref Field

**Purpose**: Link SPEC to CTR (if Layer 9 created)

**Format**:
```yaml
interfaces:
  api_endpoints:
    - endpoint: "/api/v1/trades/validate"
      method: "POST"
      contract_ref: "CTR-001"  # Link to contract
      contract_path: "#/paths/~1api~1v1~1trades~1validate/post"  # JSON Pointer

  data_models:
    - model: "TradeOrderRequest"
      schema_ref: "CTR-001#/components/schemas/TradeOrderRequest"
```

### 5. Implementation Readiness

**100% Implementation-Ready**: SPEC must contain ALL information needed to write code

**Checklist**:
- [ ] All modules identified with file paths
- [ ] All functions identified with signatures
- [ ] All algorithms documented step-by-step
- [ ] All data models linked to schemas
- [ ] All error codes defined
- [ ] All configuration specified
- [ ] All tests specified
- [ ] Deployment requirements complete

## Cumulative Tagging Requirements

**Layer 10 (SPEC)**: Must include tags from Layers 1-9

**Tag Count**: 7-9 tags (minimum 7, maximum 9)

**Minimum (IMPL and CTR skipped)**:
```yaml
cumulative_tags:
  brd: ["BRD-001:section-3"]
  prd: ["PRD-001:feature-2"]
  ears: ["EARS-001:E01"]
  bdd: ["BDD-001:scenario-validation"]
  adr: ["ADR-033", "ADR-045"]
  sys: ["SYS-001:FR-001"]
  req: ["REQ-risk-limits-001"]
```

**Maximum (IMPL and CTR included)**:
```yaml
cumulative_tags:
  brd: ["BRD-001:section-3"]
  prd: ["PRD-001:feature-2"]
  ears: ["EARS-001:E01"]
  bdd: ["BDD-001:scenario-validation"]
  adr: ["ADR-033", "ADR-045"]
  sys: ["SYS-001:FR-001"]
  req: ["REQ-risk-limits-001"]
  impl: ["IMPL-001:technical-approach"]
  contracts: ["CTR-001"]
```

## Upstream/Downstream Artifacts

**Upstream Sources**:
- **BRD** (Layer 1) - Business requirements
- **PRD** (Layer 2) - Product features
- **EARS** (Layer 3) - Formal requirements
- **BDD** (Layer 4) - Test scenarios
- **ADR** (Layer 5) - Architecture decisions
- **SYS** (Layer 6) - System requirements
- **REQ** (Layer 7) - Atomic requirements (PRIMARY SOURCE)
- **IMPL** (Layer 8) - Implementation approach (optional)
- **CTR** (Layer 9) - Data contracts (optional)

**Downstream Artifacts**:
- **TASKS** (Layer 11) - Task breakdown
- **IPLAN** (Layer 12) - Implementation plans
- **Code** (Layer 13) - Implementation

**Same-Type Document Relationships** (conditional):
- `@related-spec: SPEC-NNN` - SPECs sharing implementation context
- `@depends-spec: SPEC-NNN` - SPEC that must be implemented first

## Creation Process

### Step 1: Read Upstream Artifacts

Focus on REQ (Layer 7) and optionally CTR (Layer 9).

### Step 2: Reserve ID Number

Check `ai_dev_flow/SPEC/` for next available ID number.

### Step 3: Create SPEC File

**File naming**: `ai_dev_flow/SPEC/SPEC-NNN_{slug}.yaml`

**Example**: `ai_dev_flow/SPEC/SPEC-001_trade_validation.yaml`

**IMPORTANT**: Pure YAML format (NOT markdown)

### Step 4: Fill Metadata Section

Complete spec_id, title, version, dates, status, owner.

### Step 5: Add Cumulative Tags

Include all 7-9 upstream tags (brd through req/impl/contracts).

### Step 6: Define Overview

Purpose, scope, and requirements list.

### Step 7: Specify Architecture

Pattern, layers, and technologies (reference ADR decisions).

### Step 8: Define Interfaces

API endpoints (with contract_ref), data models (with schema_ref).

### Step 9: Document Implementation

Modules (file paths), functions (signatures), algorithms (step-by-step).

### Step 10: Specify Error Handling

Error codes, HTTP status, messages, recovery procedures.

### Step 11: Define Configuration

Environment variables, feature flags, defaults.

### Step 12: Specify Testing

Unit tests, integration tests, performance tests with targets.

### Step 13: Define Deployment

Container, resources, scaling, environment.

### Step 14: Add Monitoring

Metrics, alerts, logging requirements.

### Step 15: Add Traceability

Upstream sources and downstream artifacts.

### Step 16: Create/Update Traceability Matrix

**MANDATORY**: Update `ai_dev_flow/SPEC/SPEC-000_TRACEABILITY_MATRIX.md`

### Step 17: Validate SPEC

```bash
# YAML validation
yamllint ai_dev_flow/SPEC/SPEC-001_*.yaml

# Schema validation
python ai_dev_flow/scripts/validate_spec_schema.py ai_dev_flow/SPEC/SPEC-001_*.yaml

# Cumulative tagging
python ai_dev_flow/scripts/validate_tags_against_docs.py --artifact SPEC-001 --expected-layers brd,prd,ears,bdd,adr,sys,req,impl,contracts --strict

# Implementation readiness check
python ai_dev_flow/scripts/check_implementation_readiness.py ai_dev_flow/SPEC/SPEC-001_*.yaml
```

### Step 18: Commit Changes

Commit SPEC file and traceability matrix.

## Validation

### Automated Validation

```bash
# YAML validation
yamllint ai_dev_flow/SPEC/SPEC-001_*.yaml

# Schema validation
python ai_dev_flow/scripts/validate_spec_schema.py ai_dev_flow/SPEC/SPEC-001_*.yaml

# Cumulative tagging
python ai_dev_flow/scripts/validate_tags_against_docs.py \
  --artifact SPEC-001 \
  --expected-layers brd,prd,ears,bdd,adr,sys,req,impl,contracts \
  --strict

# Implementation readiness
python ai_dev_flow/scripts/check_implementation_readiness.py ai_dev_flow/SPEC/SPEC-001_*.yaml
```

### Manual Checklist

- [ ] Pure YAML format (not markdown)
- [ ] Metadata section complete
- [ ] cumulative_tags section with 7-9 upstream tags
- [ ] Overview defines purpose and scope
- [ ] Architecture references ADR decisions
- [ ] Interfaces link to CTR (if Layer 9 created)
- [ ] Implementation specifies modules with file paths
- [ ] Functions have signatures and algorithms
- [ ] Error handling complete
- [ ] Configuration specified
- [ ] Testing requirements defined
- [ ] Deployment requirements complete
- [ ] Monitoring specified
- [ ] Traceability links to upstream/downstream
- [ ] 100% implementation-ready

## Common Pitfalls

1. **Markdown format**: SPEC must be pure YAML, not markdown
2. **Missing cumulative_tags**: Must include all 7-9 upstream tags
3. **No contract_ref**: Must link to CTR if Layer 9 created
4. **Vague implementation**: Must specify exact file paths and signatures
5. **Missing algorithms**: Functions need step-by-step algorithms
6. **Incomplete**: Must be 100% implementation-ready

## Next Skill

After creating SPEC, use:

**`doc-tasks`** - Create Task Breakdown (Layer 11)

The TASKS will:
- Reference this SPEC as upstream source
- Include all 8-10 upstream tags
- Break SPEC into actionable tasks
- Provide AI-structured TODO format

## Related Resources

- **SPEC Creation Rules**: `ai_dev_flow/SPEC/SPEC_CREATION_RULES.md`
- **SPEC Validation Rules**: `ai_dev_flow/SPEC/SPEC_VALIDATION_RULES.md`
- **SPEC README**: `ai_dev_flow/SPEC/README.md`
- **Shared Standards**: `.claude/skills/doc-flow/SHARED_CONTENT.md`

## Quick Reference

**SPEC Purpose**: Implementation-ready technical specifications

**Layer**: 10

**Tags Required**: @brd through @req/impl/contracts (7-9 tags)

**Format**: Pure YAML (not markdown)

**Key Features**:
- cumulative_tags section (NEW)
- contract_ref field (links to CTR)
- schema_ref field (links to data models)
- 100% implementation-ready
- All modules, functions, algorithms specified

**Quality Gate**: Must be 100% implementation-ready

**Next**: doc-tasks
