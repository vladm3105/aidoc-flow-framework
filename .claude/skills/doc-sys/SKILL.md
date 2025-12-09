---
title: "doc-sys: Create System Requirements (Layer 6)"
name: doc-sys
description: Create System Requirements (SYS) - Layer 6 artifact defining functional and non-functional system requirements
tags:
  - sdd-workflow
  - layer-6-artifact
  - shared-architecture
custom_fields:
  layer: 6
  artifact_type: SYS
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  skill_category: core-workflow
  upstream_artifacts: [ADR,BDD]
  downstream_artifacts: [REQ]
---

# doc-sys

## Purpose

Create **System Requirements (SYS)** documents - Layer 6 artifact in the SDD workflow that defines technical system requirements including functional capabilities and non-functional qualities.

**Layer**: 6

**Upstream**: BRD (Layer 1), PRD (Layer 2), EARS (Layer 3), BDD (Layer 4), ADR (Layer 5)

**Downstream Artifacts**: REQ (Layer 7), Code (Layer 13)

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


Before creating SYS, read:

1. **Shared Standards**: `.claude/skills/doc-flow/SHARED_CONTENT.md`
2. **Upstream ADR**: Read architecture decisions constraining system
3. **Template**: `ai_dev_flow/SYS/SYS-TEMPLATE.md`
4. **Creation Rules**: `ai_dev_flow/SYS/SYS_CREATION_RULES.md`
5. **Validation Rules**: `ai_dev_flow/SYS/SYS_VALIDATION_RULES.md`

## When to Use This Skill

Use `doc-sys` when:
- Have completed BRD through ADR (Layers 1-5)
- Need to define system-level technical requirements
- Translating architecture decisions into requirements
- Specifying functional and non-functional system behavior
- You are at Layer 6 of the SDD workflow

## SYS-Specific Guidance

### 1. Required Sections

**Document Control** (MANDATORY - First section before all numbered sections)

**Core Sections**:
1. **Introduction**: System overview and scope
2. **Functional Requirements**: What system must do
3. **Non-Functional Requirements**: Quality attributes
4. **System Flows**: Interaction diagrams and workflows
5. **Technical Constraints**: ADR-imposed limitations
6. **Traceability**: Section 7 format

### 2. Functional Requirements

**Format**: Numbered functional requirements

```markdown
## Functional Requirements

### FR-001: Trade Order Validation
**Description**: System SHALL validate all trade orders before submission
**Input**: Trade order (symbol, quantity, price, account)
**Processing**:
- Validate symbol exists and is tradeable
- Validate quantity is positive integer
- Validate price within reasonable range
- Validate account has sufficient buying power
**Output**: Validation result (pass/fail) with error details
**Source**: EARS.001.001, ADR-033
**Verification**: BDD.001.001
```

### 3. Non-Functional Requirements

**NFR 900-Series Standard** (MANDATORY):

NFRs use unified 900-series numbering within SYS documents for automated categorization:

| Category | Series Range | Example | Keywords for AI Detection |
|----------|-------------|---------|---------------------------|
| Performance | 901-920 | `SYS.001.901` | latency, response time, throughput, p95, TPS |
| Reliability | 921-940 | `SYS.001.921` | uptime, availability, MTBF, MTTR, failover |
| Scalability | 941-960 | `SYS.001.941` | concurrent users, horizontal scaling, capacity |
| Security | 961-980 | `SYS.001.961` | authentication, authorization, encryption, RBAC |
| Observability | 981-990 | `SYS.001.981` | logging, monitoring, alerting, metrics, tracing |
| Maintainability | 991-999 | `SYS.001.991` | code coverage, deployment, CI/CD, documentation |

**Cross-Layer Consistency**: Use unified `TYPE.NNN.9XX` format across all layers.

**Cross-Reference Format**: `@sys: SYS.001.901` (not `SYS-001:NFR-PERF-001`)

**Format**:
```markdown
## Non-Functional Requirements

### SYS.001.901: Order Validation Performance
**Category**: Performance (901-920)
**Requirement**: Order validation SHALL complete within 50ms at P95
**Measurement**: P50 <25ms, P95 <50ms, P99 <100ms
**Rationale**: User experience requires sub-second feedback per PRD-001
**Source**: PRD.001.901, EARS.001.901
**Verification**: Performance benchmarks, load testing
**Traceability**: @brd: BRD.001.901 | @prd: PRD.001.901

### SYS.001.921: System Availability
**Category**: Reliability (921-940)
**Requirement**: System SHALL maintain 99.9% uptime during market hours
**Measurement**: Monthly uptime >99.9% (43.2 minutes downtime max)
**Rationale**: Trading system criticality requires high availability
**Source**: BRD.001.921
**Verification**: Uptime monitoring, incident tracking
**Traceability**: @brd: BRD.001.921
```

### 4. System Flows

**Use Mermaid diagrams** (per documentation standards - no Python code):

```markdown
## System Flows

### Flow 1: Trade Order Submission

```mermaid
sequenceDiagram
    participant User
    participant API
    participant Validator
    participant RiskEngine
    participant Broker

    User->>API: Submit trade order
    API->>Validator: Validate order
    Validator->>RiskEngine: Check position limits
    RiskEngine-->>Validator: Limit check result
    Validator-->>API: Validation result
    alt Order Valid
        API->>Broker: Submit to broker
        Broker-->>API: Confirmation
        API-->>User: Order accepted
    else Order Invalid
        API-->>User: Rejection with reason
    end
```
```

### 5. Technical Constraints

**From ADR decisions**:

```markdown
## Technical Constraints

### TC-001: Database Technology
**Constraint**: System MUST use PostgreSQL per ADR-033
**Impact**: All data models use PostgreSQL-specific features
**Verification**: Architecture review, code inspection

### TC-002: API Protocol
**Constraint**: External APIs MUST use REST per ADR-045
**Impact**: No GraphQL or gRPC for external interfaces
**Verification**: API design review, contract validation
```

## Unified Feature ID Format (MANDATORY)

**Always use**: `TYPE.NNN.NNN` (dot separator)
**Never use**: `TYPE-NNN:NNN` (colon separator - DEPRECATED)

Examples:
- `@brd: BRD.017.001` ✅
- `@brd: BRD-017:001` ❌

NFRs use 900-series: `SYS.008.901` (not `NFR-PERF-001`)

## Cumulative Tagging Requirements

**Layer 6 (SYS)**: Must include tags from Layers 1-5 (BRD, PRD, EARS, BDD, ADR)

**Tag Count**: 5 tags (@brd, @prd, @ears, @bdd, @adr)

**Format**:
```markdown
## Traceability

**Required Tags** (Cumulative Tagging Hierarchy - Layer 6):
```markdown
@brd: BRD.001.003
@prd: PRD.001.002, PRD.001.015
@ears: EARS.001.001, EARS.001.002
@bdd: BDD.001.001
@adr: ADR.033, ADR.045
```

**Upstream Sources**:
- [BRD-001](../BRD/BRD-001_platform.md#BRD-001)
- [PRD-001](../PRD/PRD-001_integration.md#PRD-001)
- [EARS-001](../EARS/EARS-001_risk.md#EARS-001)
- [BDD-001](../BDD/BDD-001_limits.feature)
- [ADR-033](../ADR/ADR-033_database.md#ADR-033)

**Downstream Artifacts**:
- REQ-NNN (to be created) - Atomic requirements
```

## Upstream/Downstream Artifacts

**Upstream Sources**:
- **BRD** (Layer 1) - Business requirements
- **PRD** (Layer 2) - Product features
- **EARS** (Layer 3) - Formal requirements
- **BDD** (Layer 4) - Test scenarios
- **ADR** (Layer 5) - Architecture decisions (CRITICAL - defines constraints)

**Downstream Artifacts**:
- **REQ** (Layer 7) - Atomic requirements decomposed from SYS
- **Code** (Layer 13) - Implementation of system requirements

**Same-Type Document Relationships** (conditional):
- `@related-sys: SYS-NNN` - SYS documents sharing system context
- `@depends-sys: SYS-NNN` - SYS that must be implemented first

## Creation Process

### Step 1: Read Upstream Artifacts

Especially focus on ADR (Layer 5) - architecture decisions constrain system requirements.

### Step 2: Reserve ID Number

Check `ai_dev_flow/SYS/` for next available ID number.

### Step 3: Create SYS File

**Location**: `docs/SYS/SYS-NNN_{slug}.md` (template available at `ai_dev_flow/SYS/`)

**Example**: `docs/SYS/SYS-001_order_management.md`

### Step 4: Fill Document Control Section

Complete metadata and Document Revision History table.

### Step 5: Define Functional Requirements

For each capability:
- Number as FR-NNN
- Specify inputs, processing, outputs
- Reference upstream EARS/PRD
- Link to BDD verification

### Step 6: Define Non-Functional Requirements

For each quality attribute:
- Number as NFR-NNN
- Specify measurable criteria
- Define verification method
- Reference upstream KPIs

### Step 7: Create System Flows

Use Mermaid diagrams (not Python code) to visualize:
- Sequence diagrams for interactions
- Flowcharts for logic
- State diagrams for workflows

### Step 8: Document Technical Constraints

From ADR decisions:
- List each constraint
- Explain impact
- Define verification

### Step 9: Add Cumulative Tags

Include all 5 upstream tags (@brd, @prd, @ears, @bdd, @adr).

### Step 10: Create/Update Traceability Matrix

**MANDATORY**: Update `ai_dev_flow/SYS/SYS-000_TRACEABILITY_MATRIX.md`

### Step 11: Validate SYS

```bash
./ai_dev_flow/scripts/validate_sys_template.sh ai_dev_flow/SYS/SYS-001_*.md

python ai_dev_flow/scripts/validate_tags_against_docs.py --artifact SYS-001 --expected-layers brd,prd,ears,bdd,adr --strict
```

### Step 12: Commit Changes

Commit SYS file and traceability matrix.

## Validation

### Automated Validation

```bash
# Quality gates
./scripts/validate_quality_gates.sh ai_dev_flow/SYS/SYS-001_order.md

# Cumulative tagging
python ai_dev_flow/scripts/validate_tags_against_docs.py \
  --artifact SYS-001 \
  --expected-layers brd,prd,ears,bdd,adr \
  --strict
```

### Manual Checklist

- [ ] Document Control section at top
- [ ] Functional requirements numbered (FR-NNN)
- [ ] Non-functional requirements categorized (NFR-NNN)
- [ ] Each requirement has measurable criteria
- [ ] System flows use Mermaid diagrams
- [ ] Technical constraints from ADR documented
- [ ] Cumulative tags: @brd, @prd, @ears, @bdd, @adr included
- [ ] Each requirement references upstream source
- [ ] Verification method specified for each requirement
- [ ] Traceability matrix updated

## Common Pitfalls

1. **Vague NFRs**: Must be measurable (not "fast" but "P95 <50ms")
2. **Missing ADR constraints**: System requirements must respect ADR decisions
3. **Python code in diagrams**: Use Mermaid, not code blocks
4. **Missing cumulative tags**: Layer 6 must include all 5 upstream tags
5. **No verification method**: Each requirement needs test approach

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
python scripts/validate_cross_document.py --document docs/SYS/SYS-NNN_slug.md --auto-fix

# Layer validation (Phase 2) - run when all SYS documents complete
python scripts/validate_cross_document.py --layer SYS --auto-fix
```

### Layer-Specific Upstream Requirements

| This Layer | Required Upstream Tags | Count |
|------------|------------------------|-------|
| SYS (Layer 6) | @brd, @prd, @ears, @bdd, @adr | 5 tags |

### Auto-Fix Actions (No Confirmation Required)

| Issue | Fix Action |
|-------|------------|
| Missing @brd/@prd/@ears/@bdd/@adr tag | Add with upstream document reference |
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

After creating SYS, use:

**`doc-req`** - Create Atomic Requirements (Layer 7)

The REQ will:
- Decompose SYS into atomic requirements
- Include all 6 upstream tags (@brd through @sys)
- Use REQ v3.0 format (12 sections)
- Achieve ≥90% SPEC-readiness

## Related Resources

- **SYS Creation Rules**: `ai_dev_flow/SYS/SYS_CREATION_RULES.md`
- **SYS Validation Rules**: `ai_dev_flow/SYS/SYS_VALIDATION_RULES.md`
- **SYS README**: `ai_dev_flow/SYS/README.md`
- **Shared Standards**: `.claude/skills/doc-flow/SHARED_CONTENT.md`

## Quick Reference

**SYS Purpose**: Define system-level technical requirements

**Layer**: 6

**Tags Required**: @brd, @prd, @ears, @bdd, @adr (5 tags)

**Key Sections**:
- Functional Requirements (FR-NNN)
- Non-Functional Requirements (NFR-NNN with categories)
- System Flows (Mermaid diagrams)
- Technical Constraints (from ADR)

**Next**: doc-req
