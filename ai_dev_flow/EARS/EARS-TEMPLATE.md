# =============================================================================
# 📋 Document Authority: This is the PRIMARY STANDARD for EARS structure.
# All other documents (Schema, Creation Rules, Validation Rules) DERIVE from this template.
# - In case of conflict, this template is the single source of truth
# - Schema: EARS_SCHEMA.yaml - Machine-readable validation (derivative)
# - Creation Rules: EARS_CREATION_RULES.md - AI guidance for document creation (derivative)
# - Validation Rules: EARS_VALIDATION_RULES.md - AI checklist after document creation (derivative)
#   NOTE: VALIDATION_RULES includes all CREATION_RULES and may be extended for validation
# =============================================================================
---
title: "EARS-NN: [Descriptive Title]"
tags:
  - ears
  - layer-3-artifact
  - shared-architecture  # OR ai-agent-primary for EARS.022-029
custom_fields:
  document_type: ears
  artifact_type: EARS
  layer: 3
  architecture_approaches: [ai-agent-based, traditional-8layer]  # ARRAY format required
  priority: shared  # OR primary for AI agents
  development_status: active  # active | draft | in-review | reserved | deprecated
  agent_id: AGENT-NN  # ONLY for AI agent documents (EARS.022 to EARS.029)
  schema_reference: "EARS_SCHEMA.yaml"
  schema_version: "1.0"
---

> Reference Template — For learning and small docs only. Real EARS suites should be split per `../DOCUMENT_SPLITTING_RULES.md` using:
> - `EARS-SECTION-0-TEMPLATE.md` to create `EARS-{NN}.0_index.md`
> - `EARS-SECTION-TEMPLATE.md` to create `EARS-{NN}.{S}_{slug}.md`

> **📋 Document Authority**: This is the **PRIMARY STANDARD** for EARS structure.
> - **Schema**: `EARS_SCHEMA.yaml v1.0` - Validation rules
> - **Creation Rules**: `EARS_CREATION_RULES.md` - Usage guidance
> - **Validation Rules**: `EARS_VALIDATION_RULES.md` - Post-creation checks

# EARS-NN: [Descriptive Title]

## Document Control

| Item | Details |
|------|---------|
| **Status** | Draft |
| **Version** | 1.0.0 |
| **Date Created** | YYYY-MM-DD |
| **Last Updated** | YYYY-MM-DD |
| **Author** | Project Engineering Team |
| **Priority** | High |
| **Source Document** | @prd: PRD.NN.EE.SS |
| **BDD-Ready Score** | XX% (Target: ≥90%) |

## 1. Purpose and Context

### 1.1 Document Purpose
This EARS document translates PRD-NN ([Feature Name]) high-level business and product requirements into precise, atomic, testable engineering requirements using structured EARS syntax patterns.

### 1.2 Scope
This document covers [list of features/capabilities] derived from PRD-NN. It defines behavioral requirements using WHEN-THE-SHALL-WITHIN syntax.

### 1.3 Intended Audience
- Solution Architects designing [domain] architecture
- Engineering teams implementing [components]
- QA engineers creating test scenarios
- AI code generation tools consuming structured requirements

---

## 2. EARS in Development Workflow

\`\`\`
BRD-NN (Business Requirements)
        ↓
PRD-NN (Product Requirements)
        ↓
EARS-NN (Engineering Requirements) ← You are here
        ↓
BDD-NN (Behavior-Driven Development)
        ↓
ADR-NN (Architecture Decisions)
        ↓
REQ-NN (Atomic Requirements)
        ↓
SPEC-NN (Technical Specifications)
        ↓
Code Implementation
\`\`\`

---

## 3. Requirements

### 3.1 Event-Driven Requirements

**EARS-NN-01: [Requirement Name]**
\`\`\`
WHEN [trigger condition],
THE [system component] SHALL [action 1],
[action 2],
and [action 3]
WITHIN [timing constraint] (@threshold: PRD.035.category.key).
\`\`\`
**Traceability**: @brd: BRD.NN.EE.SS | @prd: PRD.NN.EE.SS | @threshold: PRD.035.timing.key | @entity: PRD.004.EntityName

### 3.2 State-Driven Requirements

**EARS-NN-101: [Requirement Name]**
\`\`\`
WHILE [state condition],
THE [system component] SHALL [continuous behavior 1],
[continuous behavior 2],
and [continuous behavior 3]
WITHIN [operational context].
\`\`\`
**Traceability**: @brd: BRD.NN.EE.SS | @prd: PRD.NN.EE.SS | @entity: PRD.004.EntityName

### 3.3 Unwanted Behavior Requirements

**EARS-NN-201: [Requirement Name]**
\`\`\`
IF [error condition],
THE [system component] SHALL [prevention/recovery action 1],
[prevention/recovery action 2],
and [prevention/recovery action 3]
WITHIN [timing constraint].
\`\`\`
**Traceability**: @brd: BRD.NN.EE.SS | @prd: PRD.NN.EE.SS | @threshold: PRD.035.error.key

### 3.4 Ubiquitous Requirements

**EARS-NN-401: [Requirement Name]**
\`\`\`
THE [system component] SHALL [universal behavior]
for [scope/context]
WITHIN [operational boundary].
\`\`\`
**Traceability**: @brd: BRD.NN.EE.SS | @prd: PRD.NN.EE.SS

---

## 4. Quality Attributes

### 4.1 Performance Requirements

| QA ID | Requirement Statement | Metric | Target | Priority | Measurement Method |
|-------|----------------------|--------|--------|----------|-------------------|
| EARS.NN.02.01 | THE [component] SHALL complete [operation] | Latency | p95 < NNms | High | [method] |
| EARS.NN.02.02 | THE [component] SHALL process [workload] | Throughput | NN/s | Medium | [method] |

### 4.2 Security Requirements

| QA ID | Requirement Statement | Standard/Framework | Priority | Validation Method |
|-------|----------------------|-------------------|----------|-------------------|
| EARS.NN.02.03 | THE [component] SHALL [security requirement] | [standard] | High | [method] |

### 4.3 Reliability Requirements

| QA ID | Requirement Statement | Target | Priority | Measurement Period |
|-------|----------------------|--------|----------|-------------------|
| EARS.NN.02.04 | THE [component] SHALL maintain uptime | 99.9% | High | Monthly |

---

## 5. Traceability

### 5.1 Upstream Sources

| Source Type | Document ID | Document Title | Relevant Sections | Relationship |
|-------------|-------------|----------------|-------------------|--------------|
| BRD | BRD-NN | [Title] | Sections X.X | Business objectives |
| PRD | PRD-NN | [Title] | Section X.X | Product features |
| Threshold Registry | PRD-NN | Platform Threshold Registry | Sections X.X | Timing thresholds |
| Entity Definitions | PRD-004 | Data Model & Ledger | Section 1.3 | Entity definitions |

### 5.2 Downstream Artifacts

> Note: Use generic downstream names; do not reference numeric IDs until the artifacts exist.

| Target | Document ID | Status | Relationship |
|--------|-------------|--------|--------------|
| BDD | (TBD) | Planned | Test scenarios |
| REQ | (TBD) | Planned | Atomic requirements |
| SPEC | (TBD) | Planned | Technical specifications |

### 5.3 Traceability Tags

**Required Tags**:
\`\`\`markdown
@brd: BRD.NN.EE.SS
@prd: PRD.NN.EE.SS
@threshold: PRD.035.category.key
@entity: PRD.004.EntityName
@ctr: CTR-NN (if applicable)
\`\`\`

### 5.4 Thresholds Referenced

**Purpose**: EARS documents REFERENCE thresholds defined in PRD threshold registry. All quantitative values in EARS requirements must use `@threshold:` tags to ensure single source of truth.

**Threshold Naming Convention**: `@threshold: PRD.NN.category.subcategory.key`

**Format Reference**: See `THRESHOLD_NAMING_RULES.md` for complete naming standards.

**Thresholds Used in This Document**:
\`\`\`yaml
# Thresholds referenced from PRD threshold registry
# Format: @threshold: PRD.NN.category.subcategory.key

timing:
  # Timing constraints for WITHIN clauses
  - "@threshold: PRD.NN.timeout.request.sync"        # Synchronous operation timeout
  - "@threshold: PRD.NN.timeout.request.async"       # Asynchronous operation timeout
  - "@threshold: PRD.NN.timeout.connection.default"  # Connection establishment timeout

performance:
  # Performance targets for quality attributes
  - "@threshold: PRD.NN.perf.api.p95_latency"        # API response time target
  - "@threshold: PRD.NN.perf.batch.max_duration"    # Batch processing limit

limits:
  # Capacity and rate limits
  - "@threshold: PRD.NN.limit.api.requests_per_second"  # Rate limiting
  - "@threshold: PRD.NN.limit.batch.size"              # Batch size limits

error:
  # Error handling thresholds
  - "@threshold: PRD.NN.sla.error_rate.target"      # Acceptable error rate
  - "@threshold: PRD.NN.retry.max_attempts"         # Retry policy
\`\`\`

**Example Usage in Requirements**:
\`\`\`
WHEN [trigger condition],
THE [system component] SHALL [action]
WITHIN @threshold: PRD.NN.timeout.request.sync.
\`\`\`

**Reference**: See [THRESHOLD_NAMING_RULES.md](../THRESHOLD_NAMING_RULES.md) for naming conventions.

---

## 6. References

### 6.1 Internal Documentation

- EARS Style Guide (EARS_STYLE_GUIDE.md)
- PRD-NN (../PRD/PRD-NN_name.md) - Source product requirements (example)
- PRD-NN (../PRD/PRD-NN_platform_threshold_registry.md) - Platform threshold registry (example)
- PRD-004 (../PRD/PRD-004_data_model_ledger_double_entry_accounting.md) - Entity definitions (example)

### 6.2 External Standards

- EARS-inspired structured patterns: Mavin, A. et al. (2009). "Easy Approach to Requirements Syntax (EARS)." (In this framework, EARS stands for Event-Action-Response-State — Engineering Requirements.)
- **ISO/IEC/IEEE 29148:2018**: Systems and software engineering — Requirements engineering
- **RFC 2119**: Key words for use in RFCs to Indicate Requirement Levels (SHALL, SHOULD, MAY)

---

## Requirement ID Naming Convention

| Category | ID Range | Pattern | Example |
|----------|----------|---------|---------|
| Event-Driven | 001-099 | EARS.NN.25.0SS | EARS.01.25.001 |
| State-Driven | 101-199 | EARS.NN.25.1SS | EARS.01.25.101 |
| Unwanted Behavior | 201-299 | EARS.NN.25.2SS | EARS.01.25.201 |
| Ubiquitous | 401-499 | EARS.NN.25.4SS | EARS.01.25.401 |

---

**Document Version**: 1.0.0
**Template Version**: 3.0
**Last Reviewed**: YYYY-MM-DD
**Next Review**: YYYY-MM-DD (quarterly review)
**Maintained By**: Project Engineering Team
## File Size Limits

- Target: 300–500 lines per file
- Maximum: 600 lines per file (absolute)
- If this document approaches/exceeds limits, split into `EARS-{NN}.{S}_{slug}.md` section files using `EARS-SECTION-TEMPLATE.md` and update `EARS-{NN}.0_index.md`.

## Document Splitting Standard

Split EARS when sections become large or cover distinct capability areas:
- Add/update `EARS-{NN}.0_index.md` with sections and descriptions
- Create section files from `EARS-SECTION-TEMPLATE.md` (`EARS-{NN}.{S}_{slug}.md`)
- Maintain Prev/Next links, consistent YAML frontmatter, and update traceability
- Re-run validators and lints
