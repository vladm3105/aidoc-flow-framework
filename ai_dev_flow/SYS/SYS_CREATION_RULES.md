# =============================================================================
# 📋 Document Role: This is a DERIVATIVE of SYS-TEMPLATE.md
# - Authority: SYS-TEMPLATE.md is the single source of truth for SYS structure
# - Purpose: AI guidance for document creation (derived from template)
# - On conflict: Defer to SYS-TEMPLATE.md
# =============================================================================
---
title: "SYS Creation Rules"
tags:
  - creation-rules
  - layer-6-artifact
  - shared-architecture
custom_fields:
  document_type: creation-rules
  artifact_type: SYS
  layer: 6
  priority: shared
  development_status: active
---

> **📋 Document Role**: This is a **CREATION HELPER** for SYS-TEMPLATE.md.
> - **Authority**: `SYS-TEMPLATE.md` is the single source of truth for SYS structure
> - **Validation**: Use `SYS_VALIDATION_RULES.md` after SYS creation/changes

# SYS Creation Rules

**Version**: 1.2
**Date**: 2025-11-19
**Last Updated**: 2025-11-30
**Source**: Derived from SYS-TEMPLATE.md and ADR decisions
**Purpose**: Complete reference for creating SYS documents according to doc_flow SDD framework
**Changes**: Added Threshold Registry Integration section (v1.2). Previous: Status/Score mapping, common mistakes section (v1.1)

---

## Table of Contents

1. [File Organization and Directory Structure](#1-file-organization-and-directory-structure)
2. [Document Structure (Required sections)](#2-document-structure-required-sections)
3. [Document Control Requirements](#3-document-control-requirements)
4. [ID and Naming Standards](#4-id-and-naming-standards)
5. [System Component Categorization](#5-system-component-categorization)
6. [ADR Relationship Guidelines](#6-adr-relationship-guidelines)
7. [REQ-Ready Scoring System](#7-req-ready-scoring-system)
8. [Traceability Requirements](#8-traceability-requirements)
9. [Quality Attributes](#9-quality-attributes)
10. [Quality Gates](#10-quality-gates)
11. [Additional Requirements](#11-additional-requirements)
12. [Common Mistakes to Avoid](#12-common-mistakes-to-avoid)
13. [Upstream Artifact Verification Process](#13-upstream-artifact-verification-process)
14. [Threshold Registry Integration](#14-threshold-registry-integration)

---

## 1. File Organization and Directory Structure

- **Location**: `docs/SYS/` within project docs directory
- **Naming**: `SYS-NNN_descriptive_system_name.md` (NNN = 3-digit sequential)
- **Structure**: One primary SYS file per architectural subsystem

---

## 2. Document Structure (Required sections)

SYS documents follow a comprehensive structure translating ADR decisions into system requirements:

#### **Part 1: System Definition**
- Document Control, Executive Summary, Scope

#### **Part 2: System Requirements**
- Functional Requirements, Non-Functional Requirements

#### **Part 3: System Specification**
- Interface Specifications, Data Management Requirements, Testing and Validation Requirements

#### **Part 4: System Operations**
- Deployment and Operations Requirements, Compliance and Regulatory Requirements

#### **Part 5: Validation and Control**
- Acceptance Criteria, Risk Assessment, Traceability, Implementation Notes

---

## 3. Document Control Requirements

**Required Fields** (9 mandatory):
- Status, Version, Date Created/Last Updated, Author, Reviewers, Owner, Priority
- EARS-Ready Score (⭐ NEW)
- REQ-Ready Score (⭐ NEW)

**Format**:
```markdown
| Item | Details |
|------|---------|
| **EARS-Ready Score** | ✅ 95% (Target: ≥90%) |
| **REQ-Ready Score** | ✅ 95% (Target: ≥90%) |
```

### Status and REQ-Ready Score Mapping

| REQ-Ready Score | Required Status |
|-----------------|-----------------|
| >= 90% | Approved |
| 70-89% | In Review |
| < 70% | Draft |

---

## 4. ID and Naming Standards

- **Filename**: `SYS-NNN_descriptive_system_name.md`
- **H1**: `# SYS-NNN: [System Name/Component Name]`
- **Requirement IDs**: SYS-NNN-P-N (Performance), SYS-NNN-R-N (Reliability), etc.

---

## 5. System Component Categorization

**System Types**:
- **API Services**: REST, GraphQL, or other API interfaces
- **Data Processing**: ETL, stream processing, batch processing systems
- **Integration Services**: Adapters, connectors, proxy services
- **Supporting Services**: Caching, messaging, configuration services
- **Infrastructure Components**: Load balancers, gateways, monitoring systems

**Criticality Levels**:
- **Mission-Critical**: Revenue-generating systems with <1 hour downtime SLA
- **Business-Critical**: Core operational systems with <4 hour downtime SLA
- **Operational Support**: Back-office systems with <24 hour downtime SLA

---

## 6. ADR Relationship Guidelines

**ADR → SYS Translation**:
- ADRs define architectural patterns and technology choices
- SYS documents specify operational and quantitative requirements
- SYS requirements must be implementable within ADR architectural boundaries

**ADR Implementation Requirements**:
- Technology selections from ADRs must be specified with versions and configurations
- Architectural patterns from ADRs must be translated into concrete system behaviors
- Performance and scalability targets from ADRs must be quantified in SYS

---

## 7. REQ-Ready Scoring System ⭐ NEW

### Overview
REQ-ready scoring measures SYS maturity and readiness for progression to Requirements (REQ) decomposition.

**Format**: `✅ NN% (Target: ≥90%)`
**Location**: Document Control table
**Validation**: Enforced before REQ creation

### Scoring Criteria

**Requirements Decomposition Clarity (35%)**:
- System boundaries clearly defined with acceptance/failure scopes: 15%
- Functional requirements broken down to implementable capabilities: 10%
- Requirement dependencies and prerequisites identified: 5%
- System responsibilities aligned with ADR architectural decisions: 5%

**NFR Quantification (30%)**:
- Performance NFRs quantified with percentiles and thresholds: 15%
- Reliability NFRs specified with uptime/SLA targets: 5%
- security NFRs defined with compliance framework references: 5%
- Scalability NFRs quantified for resource and capacity growth: 5%

**Interface Specifications (20%)**:
- External API contracts defined (reference CTR creation guidelines): 10%
- Internal module interfaces specified with contract requirements: 5%
- Data exchange protocols and schemas documented: 5%

**Implementation Readiness (15%)**:
- Testing requirements specified for all functional and NFR categories: 5%
- Deployment and operational requirements documented: 5%
- Monitoring and observability requirements quantified: 5%

### Quality Gate Enforcement
- Score <90% prevents REQ artifact creation
- Format validation requires ✅ emoji and percentage
- Threshold enforcement at pre-commit

---

## 8. Traceability Requirements (MANDATORY - Layer 6)

**Complete Upstream Tag Chain**:
```markdown
@brd: BRD-NNN:NNN
@prd: PRD-NNN:NNN
@ears: EARS-NNN:NNN
@bdd: BDD-NNN:NNN
@adr: ADR-NNN
```

**Layer 6 Requirements**: SYS must reference ALL upstream artifacts

**Downstream Linkages**:
- REQ artifacts must respect SYS system boundaries and NFR constraints
- SPEC implementations must satisfy SYS interface specifications
- CTR contracts must exactly match SYS API requirements

---

## 9. Quality Attributes

**Technical Accuracy**: All requirements must be implementable within ADR architectural boundaries

**Business Alignment**: System capabilities must support business objectives from BRD/PRD

**Interface Compliance**: API and integration requirements must be contractually complete

**Operational Viability**: Deployment, monitoring, and operational requirements must be production-ready

**Testability**: All functional and NFR requirements must have measurable acceptance criteria

---

## 10. Quality Gates (Pre-Commit Validation)

- SYS completeness and ADR alignment validation
- REQ-ready score verification ≥90%
- NFR quantification and measurability checks
- Interface specification completeness

---

## 11. Additional Requirements

- System boundaries must prevent requirement bleed between components
- NFRs must be prioritized and quantified with measurable thresholds
- security and compliance requirements must reference specific standards
- Performance and scalability targets must be justified with business needs

---

## Downstream Creation Guidelines

### Creating REQ from SYS

SYS documents establish system requirements that must be decomposed into atomic REQ documents:

**REQ Decomposition Rules**:
1. Each SYS functional requirement → 3-7 atomic REQ files
2. Each SYS NFR category → 2-4 atomic REQ files per category
3. Each SYS interface → 1-3 atomic REQ files per interface

**REQ Validation Against SYS**:
- All REQ capabilities must fit within SYS system boundaries
- All REQ acceptance criteria must satisfy SYS exit criteria
- All REQ NFR targets must meet or exceed SYS NFR thresholds

**Interface CTR Creation**:
- When SYS specifies external API contracts, create CTR documents
- CTR requirements must exactly match SYS interface specifications
- CTR validation blocks SYS creation if interfaces remain unspecified

---

**Framework Compliance**: 100% doc_flow SDD framework (Layer 6)
**Integration**: Enforces SYS → Requirements Layer (REQ) progression quality gates

---

## 12. Common Mistakes to Avoid

| Mistake | Correct |
|---------|---------|
| `Status: Approved` (with <90% REQ-Ready score) | Match status to score threshold |
| NFRs without percentiles | Use p50/p95/p99 for performance targets |
| Missing criticality level | Specify Mission-Critical/Business-Critical/Operational |
| Interface specs without CTR reference | Create CTR for external APIs |
| Requirements without acceptance criteria | Include measurable acceptance criteria for all requirements |
| Missing ADR alignment verification | Verify all requirements fit within ADR architectural boundaries |
| `response time < 200ms` (hardcoded) | `response time < @threshold: PRD-NNN:perf.api.p95_latency` |
| `timeout: 5000` (magic number) | `timeout: @threshold: PRD-NNN:timeout.default` |
| `uptime: 99.9%` (hardcoded SLA) | `uptime: @threshold: PRD-NNN:sla.uptime.target` |

---

## 13. Upstream Artifact Verification Process

### Before Creating This Document

**Step 1: Inventory Existing Upstream Artifacts**

```bash
# List existing upstream artifacts for this layer
ls -la docs/BRD/    # Layer 1
ls -la docs/PRD/    # Layer 2
ls -la docs/EARS/   # Layer 3
ls -la docs/BDD/    # Layer 4
ls -la docs/ADR/    # Layer 5
ls -la docs/SYS/    # Layer 6
ls -la docs/REQ/    # Layer 7
# ... continue for applicable layers
```

**Step 2: Map Existing Documents to Traceability Tags**

| Tag | Required for This Layer | Existing Document | Action |
|-----|------------------------|-------------------|--------|
| @brd | Yes/No | BRD-001 or null | Reference/Create/Skip |
| @prd | Yes/No | PRD-001 or null | Reference/Create/Skip |
| ... | ... | ... | ... |

**Step 3: Decision Rules**

| Situation | Action |
|-----------|--------|
| Upstream exists | Reference with exact document ID |
| Upstream required but missing | Skip that functionality - do NOT implement |
| Upstream optional and missing | Use `null` in traceability tag |
| Upstream not applicable | Omit tag entirely |

### Traceability Tag Rules

- **NEVER** use placeholder IDs like `BRD-XXX` or `TBD`
- **NEVER** reference documents that don't exist
- **ALWAYS** verify document exists before adding reference
- **USE** `null` only when artifact type is genuinely not applicable

### Same-Type References (Conditional)

Include ONLY if relationships exist between SYS documents sharing system context or implementation dependencies.

| Relationship | Document ID | Document Title | Purpose |
|--------------|-------------|----------------|---------|
| Related | SYS-NNN | [Related SYS title] | Shared system context |
| Depends | SYS-NNN | [Prerequisite SYS title] | Must complete before this |

**Tags**:
```markdown
@related-sys: SYS-NNN
@depends-sys: SYS-NNN
```

---

## 14. Threshold Registry Integration

**Purpose**: Prevent magic numbers by referencing centralized threshold registry.

### When @threshold Tag is Required

Use `@threshold` for ALL quantitative values that are:
- Business-critical (compliance limits, SLAs)
- Configurable (timeout values, rate limits)
- Shared across documents (performance targets)
- NFR-related (p50/p95/p99 latencies, uptime percentages)

### @threshold Tag Format

```markdown
@threshold: PRD-NNN:category.subcategory.key
```

**Examples**:
- `@threshold: PRD-035:perf.api.p95_latency`
- `@threshold: PRD-035:timeout.circuit_breaker.threshold`
- `@threshold: PRD-035:sla.uptime.target`
- `@threshold: PRD-035:resource.memory.max_heap`

### SYS-Specific Threshold Categories

| Category | SYS Usage | Example Key |
|----------|-----------|-------------|
| `perf.*` | NFR performance requirements | `perf.api.p95_latency` |
| `sla.*` | Uptime and availability targets | `sla.uptime.target` |
| `timeout.*` | Circuit breaker, connection timeouts | `timeout.circuit_breaker.threshold` |
| `resource.*` | Memory, CPU, storage limits | `resource.memory.max_heap` |
| `limit.*` | Rate limits, connection limits | `limit.connection.max_total` |

### Magic Number Detection

**Invalid (hardcoded values)**:
- `p95 latency: 200ms`
- `uptime: 99.9%`
- `memory limit: 4GB`
- `circuit breaker threshold: 5 failures`

**Valid (registry references)**:
- `p95 latency: @threshold: PRD-NNN:perf.api.p95_latency`
- `uptime: @threshold: PRD-NNN:sla.uptime.target`
- `memory limit: @threshold: PRD-NNN:resource.memory.max_heap`
- `circuit breaker threshold: @threshold: PRD-NNN:timeout.circuit_breaker.threshold`

### Traceability Requirements Update

Add `@threshold` to Required Tags table in Traceability section:

| Tag | Format | When Required |
|-----|--------|---------------|
| @threshold | PRD-NNN:category.key | When referencing NFRs, SLAs, timing, limits, or configurable values |

### Validation

Run `detect_magic_numbers.py` to verify:
1. No hardcoded quantitative values in NFR sections
2. All `@threshold` references resolve to valid registry keys
3. All SLA targets use threshold references

---

## 14. Cross-Document Validation (MANDATORY)

**CRITICAL**: Execute cross-document validation IMMEDIATELY after creating any SYS document. Do NOT proceed to downstream artifacts until validation passes.

### Automatic Validation Loop

```
LOOP:
  1. Run: python scripts/validate_cross_document.py --document {doc_path} --auto-fix
  2. IF errors fixed: GOTO LOOP (re-validate)
  3. IF warnings fixed: GOTO LOOP (re-validate)
  4. IF unfixable issues: Log for manual review, continue
  5. IF clean: Mark VALIDATED, proceed to next layer
```

### Validation Command

```bash
# Per-document validation (Phase 1)
python scripts/validate_cross_document.py --document docs/SYS/SYS-NNN_slug.md --auto-fix

# Layer validation (Phase 2) - run when all SYS documents complete
python scripts/validate_cross_document.py --layer SYS --auto-fix
```

### Layer-Specific Upstream Requirements

| This Layer | Required Upstream Tags | Tag Count |
|------------|------------------------|-----------|
| SYS (Layer 6) | @brd, @prd, @ears, @bdd, @adr | 5 |

### Auto-Fix Actions (No Confirmation Required)

| Issue | Fix Action |
|-------|------------|
| Missing @brd/@prd/@ears/@bdd/@adr tag | Add with upstream document reference |
| Invalid tag format | Correct to TYPE-NNN:section format |
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

**Blocking**: YES - Cannot proceed to REQ creation until Phase 1 validation passes with 0 errors.
