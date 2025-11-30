---
title: "EARS-NNN: [Descriptive Title]"
tags:
  - ears
  - layer-3-artifact
  - shared-architecture  # OR ai-agent-primary for EARS-022-029
custom_fields:
  document_type: ears
  artifact_type: EARS
  layer: 3
  architecture_approaches: [ai-agent-based, traditional-8layer]  # ARRAY format required
  priority: shared  # OR primary for AI agents
  development_status: active  # active | draft | in-review | reserved | deprecated
  agent_id: AGENT-NNN  # ONLY for AI agent documents (EARS-022 to EARS-029)
  schema_reference: "EARS_SCHEMA.yaml"
  schema_version: "1.0"
---

> **📋 Document Authority**: This is the **PRIMARY STANDARD** for EARS structure.
> - **Schema**: `EARS_SCHEMA.yaml v1.0` - Validation rules
> - **Creation Rules**: `EARS_CREATION_RULES.md` - Usage guidance
> - **Validation Rules**: `EARS_VALIDATION_RULES.md` - Post-creation checks

# EARS-NNN: [Descriptive Title]

## Document Control

| Item | Details |
|------|---------|
| **Status** | Draft |
| **Version** | 1.0.0 |
| **Date Created** | YYYY-MM-DD |
| **Last Updated** | YYYY-MM-DD |
| **Author** | BeeLocal Engineering Team |
| **Priority** | High |
| **Source Document** | @prd: PRD-NNN |
| **BDD-Ready Score** | XX% (Target: ≥90%) |

## 1. Purpose and Context

### 1.1 Document Purpose
This EARS document translates PRD-NNN ([Feature Name]) high-level business and product requirements into precise, atomic, testable engineering requirements using structured EARS syntax patterns.

### 1.2 Scope
This document covers [list of features/capabilities] derived from PRD-NNN. It defines behavioral requirements using WHEN-THE-SHALL-WITHIN syntax.

### 1.3 Intended Audience
- Solution Architects designing [domain] architecture
- Engineering teams implementing [components]
- QA engineers creating test scenarios
- AI code generation tools consuming structured requirements

---

## 2. EARS in Development Workflow

\`\`\`
BRD-NNN (Business Requirements)
        ↓
PRD-NNN (Product Requirements)
        ↓
EARS-NNN (Formal Requirements) ← You are here
        ↓
BDD-NNN (Behavior-Driven Development)
        ↓
ADR-NNN (Architecture Decisions)
        ↓
REQ-NNN (Atomic Requirements)
        ↓
SPEC-NNN (Technical Specifications)
        ↓
Code Implementation
\`\`\`

---

## 3. Requirements

### 3.1 Event-Driven Requirements

**EARS-NNN-001: [Requirement Name]**
\`\`\`
WHEN [trigger condition],
THE [system component] SHALL [action 1],
[action 2],
and [action 3]
WITHIN [timing constraint] (@threshold: PRD-035:category.key).
\`\`\`
**Traceability**: @brd: BRD-NNN:NNN | @prd: PRD-NNN:NNN | @threshold: PRD-035:timing.key | @entity: PRD-004:EntityName

### 3.2 State-Driven Requirements

**EARS-NNN-101: [Requirement Name]**
\`\`\`
WHILE [state condition],
THE [system component] SHALL [continuous behavior 1],
[continuous behavior 2],
and [continuous behavior 3]
WITHIN [operational context].
\`\`\`
**Traceability**: @brd: BRD-NNN:NNN | @prd: PRD-NNN:NNN | @entity: PRD-004:EntityName

### 3.3 Unwanted Behavior Requirements

**EARS-NNN-201: [Requirement Name]**
\`\`\`
IF [error condition],
THE [system component] SHALL [prevention/recovery action 1],
[prevention/recovery action 2],
and [prevention/recovery action 3]
WITHIN [timing constraint].
\`\`\`
**Traceability**: @brd: BRD-NNN:NNN | @prd: PRD-NNN:NNN | @threshold: PRD-035:error.key

### 3.4 Ubiquitous Requirements

**EARS-NNN-401: [Requirement Name]**
\`\`\`
THE [system component] SHALL [universal behavior]
for [scope/context]
WITHIN [operational boundary].
\`\`\`
**Traceability**: @brd: BRD-NNN:NNN | @prd: PRD-NNN:NNN

---

## 4. Non-Functional Requirements (NFRs)

### 4.1 Performance Requirements

| NFR ID | Requirement Statement | Metric | Target | Priority | Measurement Method |
|--------|----------------------|--------|--------|----------|-------------------|
| NFR-PERF-001 | THE [component] SHALL complete [operation] | Latency | p95 < XXXms | High | [method] |
| NFR-PERF-002 | THE [component] SHALL process [workload] | Throughput | XXX/s | Medium | [method] |

### 4.2 Security Requirements

| NFR ID | Requirement Statement | Standard/Framework | Priority | Validation Method |
|--------|----------------------|-------------------|----------|-------------------|
| NFR-SEC-001 | THE [component] SHALL [security requirement] | [standard] | High | [method] |

### 4.3 Reliability Requirements

| NFR ID | Requirement Statement | Target | Priority | Measurement Period |
|--------|----------------------|--------|----------|-------------------|
| NFR-REL-001 | THE [component] SHALL maintain uptime | 99.9% | High | Monthly |

---

## 5. Traceability

### 5.1 Upstream Sources

| Source Type | Document ID | Document Title | Relevant Sections | Relationship |
|-------------|-------------|----------------|-------------------|--------------|
| BRD | BRD-NNN | [Title] | Sections X.X | Business objectives |
| PRD | PRD-NNN | [Title] | Section X.X | Product features |
| Threshold Registry | PRD-035 | Platform Threshold Registry | Sections X.X | Timing thresholds |
| Entity Definitions | PRD-004 | Data Model & Ledger | Section 1.3 | Entity definitions |

### 5.2 Downstream Artifacts

| Target | Document ID | Status | Relationship |
|--------|-------------|--------|--------------|
| BDD | BDD-NNN | Planned | Test scenarios |
| REQ | REQ-NNN | Planned | Atomic requirements |
| SPEC | SPEC-NNN | Planned | Technical specifications |

### 5.3 Traceability Tags

**Required Tags**:
\`\`\`markdown
@brd: BRD-NNN:NNN
@prd: PRD-NNN:NNN
@threshold: PRD-035:category.key
@entity: PRD-004:EntityName
@ctr: CTR-NNN (if applicable)
\`\`\`

---

## 6. References

### 6.1 Internal Documentation

- [EARS Style Guide](EARS_STYLE_GUIDE.md)
- [PRD-NNN](../PRD/PRD-NNN_name.md) - Source product requirements
- [PRD-035](../PRD/PRD-035_platform_threshold_registry.md) - Platform threshold registry
- [PRD-004](../PRD/PRD-004_data_model_ledger_double_entry_accounting.md) - Entity definitions

### 6.2 External Standards

- **EARS Notation**: Mavin, A. et al. (2009). "Easy Approach to Requirements Syntax (EARS)."
- **ISO/IEC/IEEE 29148:2018**: Systems and software engineering — Requirements engineering
- **RFC 2119**: Key words for use in RFCs to Indicate Requirement Levels (SHALL, SHOULD, MAY)

---

## Requirement ID Naming Convention

| Category | ID Range | Pattern | Example |
|----------|----------|---------|---------|
| Event-Driven | 001-099 | EARS-NNN-0XX | EARS-001-001 |
| State-Driven | 101-199 | EARS-NNN-1XX | EARS-001-101 |
| Unwanted Behavior | 201-299 | EARS-NNN-2XX | EARS-001-201 |
| Ubiquitous | 401-499 | EARS-NNN-4XX | EARS-001-401 |

---

**Document Version**: 1.0.0
**Template Version**: 3.0
**Last Reviewed**: YYYY-MM-DD
**Next Review**: YYYY-MM-DD (quarterly review)
**Maintained By**: BeeLocal Engineering Team
