---
name: "doc-req: Create Atomic Requirements (Layer 7)"
name: doc-req
description: Create Atomic Requirements (REQ) - Layer 7 artifact using REQ v3.0 format with 12 sections and SPEC-readiness scoring
tags:
  - sdd-workflow
  - layer-7-artifact
  - shared-architecture
custom_fields:
  layer: 7
  artifact_type: REQ
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  skill_category: core-workflow
  upstream_artifacts: [BRD,PRD,EARS,BDD,ADR,SYS]
  downstream_artifacts: [IMPL,CTR,SPEC]
---

# doc-req

## Purpose

Create **Atomic Requirements (REQ)** documents - Layer 7 artifact in the SDD workflow that decomposes system requirements into atomic, implementation-ready requirements using REQ v3.0 format.

**Layer**: 7

**Upstream**: BRD (Layer 1), PRD (Layer 2), EARS (Layer 3), BDD (Layer 4), ADR (Layer 5), SYS (Layer 6)

**Downstream Artifacts**: IMPL (Layer 8), CTR (Layer 9), SPEC (Layer 10), Code (Layer 13)

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


Before creating REQ, read:

1. **Shared Standards**: `.claude/skills/doc-flow/SHARED_CONTENT.md`
2. **Upstream SYS**: Read system requirements driving this REQ
3. **Template**: `ai_dev_flow/REQ/REQ-TEMPLATE.md`
4. **Creation Rules**: `ai_dev_flow/REQ/REQ_CREATION_RULES.md`
5. **Validation Rules**: `ai_dev_flow/REQ/REQ_VALIDATION_RULES.md`
6. **Validation Script**: `./ai_dev_flow/scripts/validate_req_template.sh`

## When to Use This Skill

Use `doc-req` when:
- Have completed BRD through SYS (Layers 1-6)
- Need to decompose system requirements into atomic units
- Preparing for implementation (Layer 8+)
- Achieving ≥90% SPEC-readiness score
- You are at Layer 7 of the SDD workflow

## REQ-Specific Guidance

### 1. REQ v3.0 Format (12 Required Sections)

**CRITICAL**: REQ v3.0 expanded from 7 to 12 sections

**Document Control** (MANDATORY - First section before all numbered sections)

**Core Sections**:
1. **Requirement Overview**: ID, description, priority, source, rationale
2. **Acceptance Criteria**: Testable conditions for completion
3. **Interface Specifications**: APIs, data contracts, integration points
4. **Data Schemas**: Data models, validation rules, constraints
5. **Error Handling Specifications**: Error conditions, recovery procedures
6. **Configuration Specifications**: Settings, parameters, environment variables
7. **Quality Attributes**: Performance, security, scalability constraints
8. **Dependencies**: Upstream/downstream requirements, external systems
9. **Implementation Guidance**: Technical approach, patterns, libraries
10. **Testing Strategy**: Unit, integration, e2e test requirements
11. **Verification Methods**: How to validate requirement is met
12. **Traceability**: Section 7 format with cumulative tags

### 2. SPEC-Ready Score Field

**MANDATORY**: Each REQ must calculate SPEC-readiness score

**Formula**:
```
SPEC-Ready Score = (Completed Sections / 12) × 100%
```

**Quality Gate**: ≥90% required for Layer transition

**Example**:
```markdown
## SPEC-Ready Score

**Current Score**: 11/12 sections = 91.7% ✓ (≥90% threshold met)

**Section Status**:
- [✓] 1. Requirement Overview
- [✓] 2. Acceptance Criteria
- [✓] 3. Interface Specifications
- [✓] 4. Data Schemas
- [✓] 5. Error Handling Specifications
- [✓] 6. Configuration Specifications
- [✓] 7. Quality Attributes
- [✓] 8. Dependencies
- [✓] 9. Implementation Guidance
- [✓] 10. Testing Strategy
- [✓] 11. Verification Methods
- [✗] 12. Traceability (In Progress)

**Readiness**: READY for SPEC creation ✓
```

### 3. Domain/Subdomain Organization

**Format**: `REQ-domain-subdomain-NNN`

**Example**: `REQ-risk-limits-001`, `REQ-api-auth-001`

**Benefits**:
- Groups related requirements
- Improves traceability
- Facilitates parallel development

### 4. New Sections in REQ v3.0

**Section 3: Interface Specifications**
```markdown
## Interface Specifications

### API Endpoints
**Endpoint**: POST /api/v1/trades/validate
**Method**: POST
**Request Schema**: TradeOrderRequest
**Response Schema**: ValidationResponse
**Authentication**: Bearer token required
**Rate Limit**: 100 requests/minute

### Data Contracts
**Input**: Trade order (symbol, quantity, price, account)
**Output**: Validation result (pass/fail, error details)
**Contract**: See CTR-001_trade_validation.yaml
```

**Section 4: Data Schemas**
```markdown
## Data Schemas

### TradeOrderRequest
```yaml
TradeOrderRequest:
  type: object
  required: [symbol, quantity, price, account_id]
  properties:
    symbol:
      type: string
      pattern: ^[A-Z]{1,5}$
    quantity:
      type: integer
      minimum: 1
      maximum: 10000
    price:
      type: number
      minimum: 0.01
```

**Validation Rules**:
- Symbol must be valid ticker from approved list
- Quantity must be positive integer
- Price must be within 10% of last traded price
```

**Section 5: Error Handling Specifications**
```markdown
## Error Handling Specifications

### Error Conditions
| Error Code | Condition | HTTP Status | Recovery |
|------------|-----------|-------------|----------|
| INVALID_SYMBOL | Symbol not found | 400 | User correction |
| INSUFFICIENT_FUNDS | Account balance too low | 403 | Add funds |
| LIMIT_EXCEEDED | Position limit breached | 403 | Reduce position |
| SYSTEM_ERROR | Internal error | 500 | Retry with backoff |

### Error Response Format
```json
{
  "error_code": "LIMIT_EXCEEDED",
  "message": "Position limit exceeded: current=0.55, limit=0.50",
  "details": {"delta": 0.55, "limit": 0.50}
}
```
```

**Section 6: Configuration Specifications**
```markdown
## Configuration Specifications

### Environment Variables
| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| MAX_POSITION_DELTA | float | 0.50 | Maximum portfolio delta |
| VALIDATION_TIMEOUT_MS | int | 50 | Validation timeout |
| RETRY_ATTEMPTS | int | 3 | Number of retry attempts |

### Feature Flags
- `enable_strict_validation`: Enable enhanced validation rules
- `log_rejected_trades`: Log all rejected trades for audit
```

**Section 7: Quality Attributes**

Document quality constraints (performance, security, scalability, etc.) using sequential numbering.

```markdown
## Quality Attributes

### 007: Validation Latency
- P95 latency <50ms for validation
- Throughput: 1000 validations/second
- Memory usage <100MB per instance
- **Traceability**: @sys: SYS.001.007

### 008: Input Validation Security
- Validate all inputs against schema
- Sanitize error messages (no sensitive data)
- Audit log all validation attempts
- **Traceability**: @sys: SYS.001.008

### 009: Horizontal Scaling
- Horizontal scaling support
- Stateless validation (no session required)
- **Traceability**: @sys: SYS.001.009
```

**Note**: All requirements use sequential numbering. Use folder structure, tags, or document sections for categorization if needed.

## Tag Format Convention (By Design)

The SDD framework uses two distinct notation systems for cross-references:

| Notation | Format       | Artifacts                               | Purpose                                                             |
|----------|--------------|----------------------------------------|---------------------------------------------------------------------|
| Dash     | TYPE-NNN     | ADR, SPEC, CTR, IPLAN, ICON            | Technical artifacts - references to files/documents                 |
| Dot      | TYPE.NNN.NNN | BRD, PRD, EARS, BDD, SYS, REQ, IMPL, TASKS | Hierarchical artifacts - references to features inside documents |

**Key Distinction**:
- `@adr: ADR-033` → Points to the document `ADR-033_risk_limit_enforcement.md`
- `@brd: BRD.017.001` → Points to feature 001 inside document `BRD-017.md`

## Unified Feature ID Format (MANDATORY)

**For hierarchical requirements (BRD, PRD, EARS, BDD, SYS, REQ)**:
- **Always use**: `TYPE.NNN.NNN` (dot separator)
- **Never use**: `TYPE-NNN:NNN` (colon separator - DEPRECATED)

Examples:
- `@brd: BRD.017.001` ✅
- `@brd: BRD-017:001` ❌


## Cumulative Tagging Requirements

**Layer 7 (REQ)**: Must include tags from Layers 1-6 (BRD, PRD, EARS, BDD, ADR, SYS)

**Tag Count**: 6 tags (@brd, @prd, @ears, @bdd, @adr, @sys)

**Format**:
```markdown
## Traceability

**Required Tags** (Cumulative Tagging Hierarchy - Layer 7):
```markdown
@brd: BRD.001.003
@prd: PRD.001.002
@ears: EARS.001.001
@bdd: BDD.001.001
@adr: ADR-033, ADR-045
@sys: SYS.001.001, SYS.001.901
```

**Upstream Sources**:
- [BRD-001](../BRD/BRD-001_platform.md#BRD-001)
- [PRD-001](../PRD/PRD-001_integration.md#PRD-001)
- [EARS-001](../EARS/EARS-001_risk.md#EARS-001)
- [BDD-001](../BDD/BDD-001_limits.feature)
- [ADR-033](../ADR/ADR-033_database.md#ADR-033)
- [SYS-001](../SYS/SYS-001_order.md#SYS-001)

**Downstream Artifacts**:
- IMPL-NNN (to be created) - Implementation approach
- CTR-NNN (to be created) - Data contracts
- SPEC-NNN (to be created) - Technical specifications
```

## Upstream/Downstream Artifacts

**Upstream Sources**:
- **BRD** (Layer 1) - Business requirements
- **PRD** (Layer 2) - Product features
- **EARS** (Layer 3) - Formal requirements
- **BDD** (Layer 4) - Test scenarios
- **ADR** (Layer 5) - Architecture decisions
- **SYS** (Layer 6) - System requirements (PRIMARY SOURCE)

**Downstream Artifacts**:
- **IMPL** (Layer 8) - Implementation approach (optional)
- **CTR** (Layer 9) - Data contracts (optional)
- **SPEC** (Layer 10) - Technical specifications
- **Code** (Layer 13) - Implementation

**Same-Type Document Relationships** (conditional):
- `@related-req: REQ-NNN` - REQs sharing domain context
- `@depends-req: REQ-NNN` - REQ that must be implemented first

## Creation Process

### Step 1: Read Upstream Artifacts

Especially focus on SYS (Layer 6) - system requirements to decompose.

### Step 2: Reserve ID Number

Check `ai_dev_flow/REQ/` for next available ID number.

**Domain-based naming**: `REQ-domain-subdomain-NNN`

### Step 3: Create REQ File

**Location**: `docs/REQ/REQ-{domain}-{subdomain}-NNN_{slug}.md` (flat structure, domain in filename)

**Example**: `docs/REQ/REQ-risk-limits-001_position_validation.md`

### Step 4: Fill Document Control Section

Complete metadata and Document Revision History table.

### Step 5: Complete All 12 Required Sections

**Critical**: REQ v3.0 requires all 12 sections for ≥90% SPEC-readiness

1. **Requirement Overview**: Atomic requirement description
2. **Acceptance Criteria**: Testable conditions
3. **Interface Specifications**: APIs, endpoints, contracts
4. **Data Schemas**: Models, validation, constraints
5. **Error Handling Specifications**: Error codes, recovery
6. **Configuration Specifications**: Settings, feature flags
7. **Quality Attributes**: Performance, security, scalability
8. **Dependencies**: Other requirements, systems
9. **Implementation Guidance**: Technical approach
10. **Testing Strategy**: Test requirements
11. **Verification Methods**: Validation approach
12. **Traceability**: Cumulative tags (6 tags)

### Step 6: Calculate SPEC-Ready Score

Count completed sections and calculate percentage.

**Quality Gate**: Must achieve ≥90% (11/12 sections minimum)

### Step 7: Add Cumulative Tags

Include all 6 upstream tags (@brd through @sys).

### Step 8: Create/Update Traceability Matrix

**MANDATORY**: Update `ai_dev_flow/REQ/REQ-000_TRACEABILITY_MATRIX-TEMPLATE.md`

### Step 9: Validate REQ

```bash
./ai_dev_flow/scripts/validate_req_template.sh ai_dev_flow/REQ/REQ-risk-limits-001_*.md

python ai_dev_flow/scripts/validate_tags_against_docs.py --artifact REQ-risk-limits-001 --expected-layers brd,prd,ears,bdd,adr,sys --strict
```

### Step 10: Commit Changes

Commit REQ file and traceability matrix.

## Validation

### Automated Validation

```bash
# Quality gates
./scripts/validate_quality_gates.sh ai_dev_flow/REQ/REQ-risk-limits-001_*.md

# REQ template validation (12 sections)
./ai_dev_flow/scripts/validate_req_template.sh ai_dev_flow/REQ/REQ-risk-limits-001_*.md

# Cumulative tagging
python ai_dev_flow/scripts/validate_tags_against_docs.py \
  --artifact REQ-risk-limits-001 \
  --expected-layers brd,prd,ears,bdd,adr,sys \
  --strict

# SPEC-readiness score check
python ai_dev_flow/scripts/validate_req_spec_readiness.py ai_dev_flow/REQ/REQ-risk-limits-001_*.md
```

### Manual Checklist

- [ ] Document Control section at top
- [ ] All 12 required sections completed
- [ ] SPEC-Ready Score ≥90% (11/12 sections minimum)
- [ ] Section 3: Interface Specifications detailed
- [ ] Section 4: Data Schemas with validation rules
- [ ] Section 5: Error Handling Specifications complete
- [ ] Section 6: Configuration Specifications documented
- [ ] Section 7: Quality Attributes quantified
- [ ] Domain/subdomain organization used in ID
- [ ] Cumulative tags: @brd through @sys (6 tags) included
- [ ] Each requirement atomic (single responsibility)
- [ ] Acceptance criteria testable
- [ ] Traceability matrix updated

## Common Pitfalls

1. **Incomplete sections**: All 12 sections mandatory for SPEC-readiness
2. **Missing new sections**: Sections 3-7 are new in v3.0 - don't skip them
3. **Low SPEC-Ready Score**: Must achieve ≥90% (11/12 sections)
4. **Non-atomic requirements**: Each REQ must be single, testable unit
5. **Missing cumulative tags**: Layer 7 must include all 6 upstream tags
6. **Vague acceptance criteria**: Must be measurable and testable

## Post-Creation Validation (MANDATORY - NO CONFIRMATION)

**CRITICAL**: Execute this validation loop IMMEDIATELY after document creation. Do NOT proceed to next document until validation passes.

### Automatic Validation Loop

```
LOOP:
  1. Run: python scripts/validate_cross_document.py --document {doc_path} --auto-fix
  2. IF errors fixed: GOTO LOOP (re-validate)
  3. IF warnings fixed: GOTO LOOP (re-validate)
  4. IF unfixable issues: Log for manual review, continue
  5. IF clean: Mark VALIDATED, proceed
```

### Validation Command

```bash
# Per-document validation (Phase 1)
python ai_dev_flow/scripts/validate_cross_document.py --document docs/REQ/REQ-NNN_slug.md --auto-fix

# Layer validation (Phase 2) - run when all REQ documents complete
python ai_dev_flow/scripts/validate_cross_document.py --layer REQ --auto-fix
```

### Layer-Specific Upstream Requirements

| This Layer | Required Upstream Tags | Count |
|------------|------------------------|-------|
| REQ (Layer 7) | @brd, @prd, @ears, @bdd, @adr, @sys | 6 tags |

### Auto-Fix Actions (No Confirmation Required)

| Issue | Fix Action |
|-------|------------|
| Missing @brd/@prd/@ears/@bdd/@adr/@sys tag | Add with upstream document reference |
| Invalid tag format | Correct to TYPE.NNN.NNN format |
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

**Blocking**: YES - Cannot proceed to next document until Phase 1 validation passes with 0 errors.

---

## Next Skill

After creating REQ, use:

**`doc-spec`** (or optionally `doc-impl`/`doc-ctr` first) - Create Technical Specifications (Layer 10)

The SPEC will:
- Reference this REQ as upstream source
- Include all 7 upstream tags (@brd through @req)
- Use YAML format
- Define implementation contracts
- Achieve 100% implementation-readiness

## Reference Documents

REQ artifacts do not support REF documents. Reference documents are limited to **BRD and ADR types only** per the SDD framework.

For supplementary documentation needs, create:
- **BRD-REF**: Business context and domain glossaries
- **ADR-REF**: Technical reference guides and architecture summaries

## Related Resources

- **Template**: `ai_dev_flow/REQ/REQ-TEMPLATE.md` (primary authority)
- **REQ Creation Rules**: `ai_dev_flow/REQ/REQ_CREATION_RULES.md`
- **REQ Validation Rules**: `ai_dev_flow/REQ/REQ_VALIDATION_RULES.md`
- **REQ README**: `ai_dev_flow/REQ/README.md`
- **Shared Standards**: `.claude/skills/doc-flow/SHARED_CONTENT.md`

## Quick Reference

**REQ Purpose**: Atomic, implementation-ready requirements

**Layer**: 7

**Tags Required**: @brd, @prd, @ears, @bdd, @adr, @sys (6 tags)

**Format**: REQ v3.0 (12 sections)

**Quality Gate**: SPEC-Ready Score ≥90% (11/12 sections)

**Key Enhancements**:
- Section 3: Interface Specifications (NEW)
- Section 4: Data Schemas (NEW)
- Section 5: Error Handling Specifications (NEW)
- Section 6: Configuration Specifications (NEW)
- Section 7: Quality Attributes (NEW)
- SPEC-Ready Score calculation (NEW)
- Domain/subdomain organization (NEW)

**Next**: doc-spec (or optionally doc-impl/doc-ctr first)
