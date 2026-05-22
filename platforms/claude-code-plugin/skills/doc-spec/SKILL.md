---
name: doc-spec
description: Create Technical Specifications (SPEC) - Layer 6 artifact using YAML format for implementation-ready specifications
metadata:
  tags:
    - sdd-workflow
    - layer-6-artifact
    - shared-architecture
  custom_fields:
    layer: 6
    artifact_type: SPEC
    architecture_approaches: [ai-agent-based, traditional-8layer]
    priority: shared
    development_status: active
    skill_category: core-workflow
    upstream_artifacts: [BRD, PRD, EARS, BDD, ADR]
    downstream_artifacts: [TDD, IPLAN, Code]
    version: "2.0"
    last_updated: "2026-05-22"
  versioning_policy: "tracks SPEC-TEMPLATE schema_version"
---

# doc-spec

## Purpose

Create **Technical Specifications (SPEC)** - Layer 6 artifact in the SDD workflow that defines implementation-ready specifications in YAML format, providing complete technical details for the downstream test and implementation layers.

**Layer**: 6

**Upstream**: BRD (Layer 1), PRD (Layer 2), EARS (Layer 3), BDD (Layer 4), ADR (Layer 5)

**Downstream Artifacts**: TDD (Layer 7), IPLAN (Layer 8), Code

## Prerequisites

### Upstream Artifact Verification (CRITICAL)

**Before creating this document, you MUST:**

1. **List existing upstream artifacts**:
   ```bash
   ls docs/01_BRD/ docs/02_PRD/ docs/03_EARS/ docs/04_BDD/ docs/05_ADR/ 2>/dev/null
   ```

2. **Reference only existing documents** in traceability tags
3. **Use `null`** only when upstream artifact type genuinely doesn't exist
4. **NEVER use placeholders** like `BRD-XXX` or `TBD`
5. **Do NOT create missing upstream artifacts** - skip functionality instead


Before creating SPEC, read:

1. **Shared Standards**: `../doc-flow/SHARED_CONTENT.md`
2. **Upstream ADR**: Read architecture decisions (PRIMARY SOURCE)
3. **Upstream BDD/EARS**: Read acceptance scenarios and formal requirements
4. **Template**: `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`
5. **SPEC README**: `framework/layers/06_SPEC/README.md`
6. **ID & Tag Standards**: `framework/governance/ID_NAMING_STANDARDS.md`

## Reserved ID Exemption (SPEC-00_*)

**Scope**: Documents with reserved ID `00` are FULLY EXEMPT from validation.

**Pattern**: `SPEC-00_*.md`, `SPEC-00_*.yaml`

**Document Types**:
- Index documents (`SPEC-00_index.md`)
- Traceability matrix templates (`SPEC-00_TRACEABILITY_MATRIX-TEMPLATE.md`)
- Glossaries, registries, checklists

**Rationale**: Reserved ID 00 documents are framework infrastructure (indexes, templates, reference materials), not project artifacts requiring traceability or quality gates.

**Validation Behavior**: Skip all checks when filename matches `SPEC-00_*` pattern.

## When to Use This Skill

Use `doc-spec` when:
- Have completed BRD through ADR (Layers 1-5)
- Ready to create implementation-ready specifications
- Preparing for downstream test definitions and implementation planning
- Need complete technical details in structured format
- You are at Layer 6 of the SDD workflow

## SPEC-Specific Guidance

### 1. YAML Format (MANDATORY)

**Format**: Pure YAML (not markdown)

**Structure**:
```yaml
# SPEC-NN: [Specification Title]

metadata:
  spec_id: SPEC-01
  title: "Order Validation Service Specification"
  version: "1.0.0"
  created_date: "2025-01-15T00:00:00"
  updated_date: "2025-01-15T00:00:00"
  status: "approved"
  owner: "team-backend"
  tdd_ready_score: "✅ 95% (Target: ≥90%)"

cumulative_tags:
  brd: ["BRD.01.01.0a13"]
  prd: ["PRD.01.07.1dbc"]
  ears: ["EARS.01.03.5e2a"]
  bdd: ["BDD.01.14.8f4c"]
  adr: ["ADR-03", "ADR-04"]

overview:
  purpose: "Define trade order validation service implementation"
  scope: "Validate trade orders against position limits and business rules"
  requirements:
    - "EARS.01.03.5e2a"
    - "EARS.01.03.5e2b"

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
      authentication: "Bearer token"
      rate_limit: "@threshold: PRD.NN.limit.api.requests_per_second"
      rate_limit_window: "1min"

  data_models:
    - model: "TradeOrderRequest"
      description: "Inbound trade order payload"
    - model: "ValidationResponse"
      description: "Validation result payload"

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
    - artifact: "BRD-01"
      sections: ["section-3"]
    - artifact: "PRD-01"
      sections: ["feature-2"]
    - artifact: "ADR-03"
      sections: ["all"]

  downstream_artifacts:
    - "TDD-01"
    - "IPLAN-01"
    - "Code: src/services/trade_validator.py"
```

### 2. Element ID Format (MANDATORY)

**Document-level ID**: `SPEC-NN` (dash notation, two-digit number) per `framework/governance/ID_NAMING_STANDARDS.md`.

| ID kind | Format | Example |
|---------|--------|---------|
| Document reference | `SPEC-NN` | `SPEC-01` |
| Upstream element reference | `TYPE.NN.SS.xxxx` (4-segment) | `BRD.01.07.a7f3` |
| Upstream document reference | `TYPE-NN` | `ADR-03` |

> **REMOVED PATTERNS** - Do NOT use legacy formats:
> - `STEP-XXX`, `IF-XXX`, `INT-XXX`, `DM-XXX`, `MODEL-XXX`, `VR-XXX` - element-level code labels are not used
> - 3-digit `SPEC-NNN` (e.g. `SPEC-001`) - use two-digit `SPEC-NN`
> - Numeric element-type-code tables (15/16/17/21/28) - the 8-layer model has no such codes

**Reference**: `framework/governance/ID_NAMING_STANDARDS.md`

### 3. Required Top-Level Sections

**MANDATORY Sections**:
1. **metadata**: Spec ID, title, version, dates, status, owner, tdd_ready_score
2. **cumulative_tags**: All upstream tags (BRD, PRD, EARS, BDD, ADR)
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

### 4. TDD-Ready Scoring System

**Purpose**: Measures SPEC maturity and readiness for progression to TDD test case definitions.

**Format in Metadata**:
```yaml
metadata:
  tdd_ready_score: "✅ 95% (Target: ≥90%)"
```

**Status and TDD-Ready Score Mapping**:

| TDD-Ready Score | Required Status |
|-------------------|-----------------|
| ≥90% | approved |
| 70-89% | in_review |
| <70% | draft |

**Scoring Criteria**:
- **YAML Completeness (25%)**: All metadata fields, traceability chain, all sections populated
- **Interface Definitions (25%)**: External APIs, internal interfaces, data schemas
- **Implementation Specifications (25%)**: Behavior enables code generation, performance/security quantifiable
- **Code Generation Readiness (25%)**: Machine-readable fields, TDD-ready metadata

**Quality Gate**: Score <90% prevents TDD artifact creation.

### 5. Threshold Registry Integration

**Purpose**: Prevent magic numbers by referencing centralized threshold registry.

**When @threshold Tag is Required**: Use for ALL quantitative values that are:
- Performance configurations (latencies, throughput, IOPS)
- Timeout configurations (connection, read, write timeouts)
- Rate limiting values (requests per second, burst limits)
- Resource limits (memory, CPU, storage)
- Circuit breaker configurations

**@threshold Tag Format in YAML**:
```yaml
# String value format
performance:
  p95_latency_ms: "@threshold: PRD.NN.perf.api.p95_latency"

# Comment format for documentation
timeout:
  request_ms: 5000  # @threshold: PRD.NN.timeout.request.sync
```

**Invalid (hardcoded values)**:
```yaml
performance:
  p95_latency_ms: 200
timeout:
  request_ms: 5000
rate_limit:
  requests_per_second: 100
```

**Valid (registry references)**:
```yaml
performance:
  p95_latency_ms: "@threshold: PRD.NN.perf.api.p95_latency"
timeout:
  request_ms: "@threshold: PRD.NN.timeout.request.sync"
rate_limit:
  requests_per_second: "@threshold: PRD.NN.limit.api.requests_per_second"
```

### 6. cumulative_tags Field (CRITICAL)

**CRITICAL**: SPEC must include cumulative_tags section with ALL upstream tags

**Upstream tags (Layer 6 cumulative chain)**:
| Tag | Artifact | Reference form |
|-----|----------|----------------|
| brd | BRD | element `BRD.NN.SS.xxxx` |
| prd | PRD | element `PRD.NN.SS.xxxx` |
| ears | EARS | element `EARS.NN.SS.xxxx` |
| bdd | BDD | element `BDD.NN.SS.xxxx` |
| adr | ADR | document `ADR-NN` |

**Format**:
```yaml
cumulative_tags:
  brd: ["BRD.01.01.0a13", "BRD.01.01.0c2f"]
  prd: ["PRD.01.07.1dbc", "PRD.01.07.4e91"]
  ears: ["EARS.01.03.5e2a", "EARS.01.03.5e2b"]
  bdd: ["BDD.01.14.8f4c"]
  adr: ["ADR-03", "ADR-04"]
```

**Tag Count**: 5 upstream tag families (@brd, @prd, @ears, @bdd, @adr)

### 7. Interface and Schema References

**Purpose**: Define component interfaces and data models directly within the SPEC (the SPEC is the component contract at C4-L3).

**Format**:
```yaml
interfaces:
  api_endpoints:
    - endpoint: "/api/v1/trades/validate"
      method: "POST"
      authentication: "Bearer token"

  data_models:
    - model: "TradeOrderRequest"
      schema_ref: "#/components/schemas/TradeOrderRequest"
```

### 8. Implementation Readiness

**100% Implementation-Ready**: SPEC must contain ALL information needed to define tests and write code

**Checklist**:
- [ ] All modules identified with file paths
- [ ] All functions identified with signatures
- [ ] All algorithms documented step-by-step
- [ ] All data models defined with schemas
- [ ] All error codes defined
- [ ] All configuration specified
- [ ] All tests specified
- [ ] Deployment requirements complete

## Tag Format Convention (By Design)

The SDD framework uses two distinct notation systems for cross-references:

| Notation | Format        | Artifacts                               | Purpose                                                             |
|----------|---------------|----------------------------------------|---------------------------------------------------------------------|
| Dash     | TYPE-NN      | ADR, SPEC, IPLAN            | Technical artifacts - references to files/documents                 |
| Dot      | TYPE.NN.SS.xxxx | BRD, PRD, EARS, BDD, TDD | Hierarchical artifacts - references to elements inside documents |

**Key Distinction**:
- `@adr: ADR-03` → Points to the document `ADR-03_risk_limit_enforcement.yaml`
- `@brd: BRD.01.07.a7f3` → Points to element in section 07 inside document `BRD-01`

## Unified Element ID Format (MANDATORY)

**For hierarchical references (BRD, PRD, EARS, BDD, TDD)**:
- **Always use**: `TYPE.NN.SS.xxxx` (dot separator, 4-segment standard)
- **Never use**: `TYPE-NN:NNN` (colon separator - DEPRECATED)
- **Never use**: `TYPE.NN.xxxx` (old 3-segment format - DEPRECATED)

Examples:
- `@brd: BRD.01.07.a7f3` ✅
- `@brd: BRD.017.001` ❌ (old format)

**For document-level references (SPEC, ADR, IPLAN)**: use `TYPE-NN` (e.g. `SPEC-01`, `ADR-03`).

## Validation

The framework is spec-only — there are no validation scripts to run. This skill
*is* the validator: apply the declarative checklist below, using
`framework/layers/06_SPEC/README.md` and `framework/governance/` as authority.

### Validation Checks

#### Tier 1: Errors (Blocking)

| Check | Description |
|-------|-------------|
| CHECK 1 | YAML Syntax Validation (parseable) |
| CHECK 2 | Required Metadata Fields (version, status, tdd_ready_score) |
| CHECK 3 | TDD-Ready Score format (✅ emoji + percentage + target) |
| CHECK 4 | Complete Traceability Chain (cumulative_tags section) |
| CHECK 5 | Document ID Format (`SPEC-NN`) |

#### Tier 2: Warnings (Recommended)

| Check | Description |
|-------|-------------|
| CHECK 6 | Interface Specifications (endpoints + data models defined) |
| CHECK 7 | Implementation Readiness (code generation enabling) |
| CHECK 8 | Test Definition Compatibility (TDD creation) |

#### Tier 3: Info

| Check | Description |
|-------|-------------|
| CHECK 9 | Threshold Registry Integration (@threshold references) |
| CHECK 10 | Performance benchmarks defined |

### Quality Gates Enforced

- ✅ YAML syntax validation (parseable structure)
- ✅ Implementation-Ready score ≥90% for progression
- ✅ Required metadata fields (version, status, tdd_ready_score)
- ✅ TDD-Ready score format (✅ emoji + percentage)
- ✅ Complete traceability chain (5 upstream tag families: @brd through @adr)
- ✅ Document ID format (`SPEC-NN`)
- ✅ Interface specifications (endpoints + data models)
- ✅ Code generation compatibility
- ✅ Threshold registry integration (@threshold references)
- ✅ Performance benchmarks defined
- ✅ Concrete examples (pseudocode, API samples, model definitions)

## Upstream/Downstream Artifacts

**Upstream Sources**:
- **BRD** (Layer 1) - Business requirements
- **PRD** (Layer 2) - Product features
- **EARS** (Layer 3) - Formal requirements
- **BDD** (Layer 4) - Test scenarios
- **ADR** (Layer 5) - Architecture decisions (PRIMARY SOURCE)

**Downstream Artifacts**:
- **TDD** (Layer 7) - Test case definitions validating SPEC contracts
- **IPLAN** (Layer 8) - Implementation plan bridging TDD to Code
- **Code** - Implementation source code

**Same-Type Document Relationships** (conditional):
- `@related-spec: SPEC-NN` - SPECs sharing implementation context
- `@depends-spec: SPEC-NN` - SPEC that must be implemented first

## Creation Process

### Step 1: Read Upstream Artifacts

Focus on ADR (Layer 5) decisions and BDD/EARS acceptance criteria.

### Step 2: Reserve ID Number

Check `docs/06_SPEC/` for next available ID number (or create `docs/06_SPEC/` directory if first SPEC).

**ID Numbering Convention**: Start with 2 digits and expand only as needed.
- ✅ Correct: SPEC-01, SPEC-99, SPEC-102
- ❌ Incorrect: SPEC-001, SPEC-009 (extra leading zero not required)

### Step 3: Create SPEC File

**Nested Folder Rule (MANDATORY)**: ALL SPEC documents MUST use nested folders regardless of document size.

**File naming**: `docs/06_SPEC/SPEC-NN_{slug}/SPEC-NN_{slug}.yaml`

**Example**: `docs/06_SPEC/SPEC-01_trade_validation/SPEC-01_trade_validation.yaml`

**IMPORTANT**: Pure YAML format (NOT markdown)

**Note**: Templates and examples are in `framework/layers/06_SPEC/` while project-specific SPECs go in `docs/06_SPEC/`.

**CRITICAL**: Never create SPEC files directly in `docs/06_SPEC/` without a nested folder structure.

### Step 4: Fill Metadata Section

Complete spec_id, title, version, dates, status, owner, tdd_ready_score.

### Step 5: Add Cumulative Tags

Include all 5 upstream tag families (brd, prd, ears, bdd, adr).

### Step 6: Define Overview

Purpose, scope, and requirements list.

### Step 7: Specify Architecture

Pattern, layers, and technologies (reference ADR decisions).

### Step 8: Define Interfaces

API endpoints and data models with schema definitions.

### Step 9: Document Implementation

Modules (file paths), functions (signatures), algorithms (step-by-step).

### Step 10: Specify Error Handling

Error codes, HTTP status, messages, recovery procedures.

### Step 11: Define Configuration

Environment variables, feature flags, defaults. Use @threshold for quantitative values.

### Step 12: Specify Testing

Unit tests, integration tests, performance tests with targets.

### Step 13: Define Deployment

Container, resources, scaling, environment.

### Step 14: Add Monitoring

Metrics, alerts, logging requirements.

### Step 15: Add Traceability

Upstream sources and downstream artifacts.

### Step 16: Create/Update Traceability Matrix

**MANDATORY**: Create or update `docs/06_SPEC/SPEC-00_TRACEABILITY_MATRIX.md` (use the index template from `framework/layers/06_SPEC/SPEC-00_index.TEMPLATE.md`)

### Step 17: Validate SPEC

Apply the declarative validation checklist (above) and the Manual Checklist
(below). The plugin skill *is* the validator — confirm YAML parses, the
cumulative-tag chain is complete, and the document is implementation-ready.

### Step 18: Commit Changes

Commit SPEC file and traceability matrix.

## Manual Checklist

- [ ] Pure YAML format (not markdown)
- [ ] Metadata section complete with tdd_ready_score
- [ ] cumulative_tags section with 5 upstream tag families (@brd, @prd, @ears, @bdd, @adr)
- [ ] Overview defines purpose and scope
- [ ] Architecture references ADR decisions
- [ ] Interfaces define endpoints and data models
- [ ] Implementation specifies modules with file paths
- [ ] Functions have signatures and algorithms
- [ ] Error handling complete
- [ ] Configuration uses @threshold for quantitative values
- [ ] Testing requirements defined
- [ ] Deployment requirements complete
- [ ] Monitoring specified
- [ ] Traceability links to upstream/downstream
- [ ] 100% implementation-ready
- [ ] Document ID uses `SPEC-NN` format

### Diagram Standards
All diagrams MUST use Mermaid syntax. Text-based diagrams (ASCII art, box drawings) are prohibited.
See the `mermaid-gen` skill and `framework/governance/`.

## Common Pitfalls

1. **Markdown format**: SPEC must be pure YAML, not markdown
2. **Missing cumulative_tags**: Must include all 5 upstream tag families (@brd, @prd, @ears, @bdd, @adr)
3. **Skipped interfaces**: Must define component endpoints and data models
4. **Vague implementation**: Must specify exact file paths and signatures
5. **Missing algorithms**: Functions need step-by-step algorithms
6. **Incomplete**: Must be 100% implementation-ready
7. **Hardcoded values**: Use @threshold for performance/timeout/rate limits
8. **Wrong element IDs**: Use `SPEC-NN` (document) and 4-segment `TYPE.NN.SS.xxxx` (upstream elements), not legacy `STEP-XXX`, `IF-XXX`, `DM-XXX`
9. **Legacy upstream layers**: SPEC upstream is BRD, PRD, EARS, BDD, ADR only — never reference removed SYS/REQ/CTR layers

## Post-Creation Validation (MANDATORY - NO CONFIRMATION)

**CRITICAL**: Execute this validation loop IMMEDIATELY after document creation. Do NOT proceed to next document until validation passes.

### Automatic Validation Loop

```
LOOP:
  1. Apply the declarative validation checklist to {doc_path}
  2. IF errors found: fix, GOTO LOOP (re-validate)
  3. IF warnings found: fix where feasible, GOTO LOOP (re-validate)
  4. IF unfixable issues: Log for manual review, continue
  5. IF clean: Mark VALIDATED, proceed
```

### Layer-Specific Upstream Requirements

| This Layer | Required Upstream Tags | Count |
|------------|------------------------|-------|
| SPEC (Layer 6) | @brd, @prd, @ears, @bdd, @adr | 5 tag families |

### Auto-Fix Actions (No Confirmation Required)

| Issue | Fix Action |
|-------|------------|
| Missing upstream tag | Add with upstream document reference |
| Invalid tag format | Correct to `TYPE.NN.SS.xxxx` (4-segment) or `TYPE-NN` format |
| Broken link | Recalculate path from current location |
| Missing traceability section | Insert from template |

### Validation Codes Reference

| Code | Description | Severity |
|------|-------------|----------|
| XDOC-001 | Referenced requirement ID not found | ERROR |
| XDOC-002 | Missing cumulative tag | ERROR |
| XDOC-003 | Upstream document not found | ERROR |
| XDOC-006 | Tag format invalid | ERROR |
| XDOC-007 | Gap in cumulative tag chain | ERROR |
| XDOC-009 | Missing traceability section | ERROR |

### Quality Gate

**Blocking**: YES - Cannot proceed to next document until validation passes with 0 errors.

---

## Next Skill

After creating SPEC, use:

**`doc-tdd`** - Create Test-Driven Definitions (Layer 7)

The TDD will:
- Reference this SPEC as upstream source
- Include all 6 upstream tag families (@brd through @spec)
- Define test cases, inputs, expected outputs, and thresholds for the SPEC contracts

## Reference Documents

SPEC artifacts do not support REF documents. Reference documents are limited to **BRD and ADR types only** per the SDD framework.

For supplementary documentation needs, create:
- **BRD-REF**: Business context documentation
- **ADR-REF**: Technical reference guides (API quick references, implementation guides)

## Related Resources

- **Template**: `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml` (primary authority)
- **SPEC README**: `framework/layers/06_SPEC/README.md`
- **SPEC Index template**: `framework/layers/06_SPEC/SPEC-00_index.TEMPLATE.md`
- **ID & Tag Standards**: `framework/governance/ID_NAMING_STANDARDS.md`
- **Shared Standards**: `../doc-flow/SHARED_CONTENT.md`
- **doc-adr skill**: `../doc-adr/SKILL.md` (upstream architecture decisions)
- **doc-tdd skill**: `../doc-tdd/SKILL.md` (downstream test definitions)

## Quick Reference

**SPEC Purpose**: Implementation-ready technical specifications

**Layer**: 6

**Document ID Format**: `SPEC-NN` (dash notation)

**Upstream element refs**: 4-segment `TYPE.NN.SS.xxxx` (BRD, PRD, EARS, BDD); document-level `ADR-NN`

**Removed Patterns**: STEP-XXX, IF-XXX, INT-XXX, DM-XXX, MODEL-XXX, VR-XXX, 3-digit `SPEC-NNN`, numeric element-type codes

**Tags Required**: @brd, @prd, @ears, @bdd, @adr (5 tag families)

**Format**: Pure YAML (not markdown)

**Key Features**:
- cumulative_tags section (CRITICAL)
- interface and data-model definitions
- @threshold references for quantitative values
- 100% implementation-ready
- All modules, functions, algorithms specified

**TDD-Ready Score**: ≥90% required for "approved" status

**Quality Gate**: Must be 100% implementation-ready

**Next**: doc-tdd

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 2.0 | 2026-05-22 | **MAJOR**: Migrated to the 8-layer model. SPEC renumbered to Layer 6 (from its prior position); tag `layer-9-artifact` → `layer-6-artifact`. Upstream chain reduced to BRD, PRD, EARS, BDD, ADR (removed SYS/REQ/CTR); downstream rebuilt to TDD (L7), IPLAN (L8), Code. Element IDs are document-level `SPEC-NN` (dash) with 4-segment `TYPE.NN.SS.xxxx` upstream refs; removed legacy numeric element-type-code tables and 3-digit `SPEC-NNN`. Paths point at `framework/layers/06_SPEC/`; templates are `.yaml`. TASKS-Ready score renamed TDD-Ready; validation is now this skill's declarative checklist (framework is spec-only, no scripts). Next skill is `doc-tdd`. | System |
| 1.2.0 | 2026-02-27 | Normalized metadata schema; migrated canonical references; replaced stale validation examples; aligned commands to existing SPEC validators | System |
| 1.1.0 | 2026-02-08 | Updated layer assignment from 10 to 9 per LAYER_REGISTRY v1.6; updated downstream artifacts; removed IMPL from upstream; updated tag counts | System |
| 1.0.0 | 2025-01-15 | Initial skill definition | System |
