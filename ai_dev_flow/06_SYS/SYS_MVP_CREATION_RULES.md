---
title: "SYS MVP Creation Rules"
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

 **Document Role**: This is a **CREATION HELPER** derived from `SYS-MVP-TEMPLATE.md`.
 **Authority**: `SYS-MVP-TEMPLATE.md` is the single source of truth for SYS structure
 **Validation**: Use `SYS_VALIDATION_RULES.md` after SYS creation/changes

# SYS Creation Rules

**SYS-MVP-TEMPLATE.md is the standard template for all SYS documents.**

| Template | File | When to Use |
|----------|------|-------------|
| **Standard (MVP)** | `SYS-MVP-TEMPLATE.md` | All SYS documents (default and recommended) |

**Note**: Previous framework versions included a separate full template. The current SYS-MVP-TEMPLATE.md is the primary standard and should be used for all SYS work.

## Index-Only Generation Workflow

Maintain `SYS-00_index.md` as the authoritative source of planned and active SYS files (mark planned items with Status: Planned).
Generators use: `SYS-00_index.md` + standard template profile (`mvp`).

Path conventions: Examples below use a portable `docs/` root for new projects. In this repository, artifact folders live at the ai_dev_flow root without the `docs/` prefix. When running commands here, drop the `docs/` prefix. See README → "Using This Repo" for path mapping.

**Version**: 1.2
**Date**: 2025-11-19
**Last Updated**: 2025-11-30


**Source**: Derived from SYS-MVP-TEMPLATE.md and ADR decisions
**Purpose**: Complete reference for creating SYS documents according to AI Dev Flow SDD framework
**Changes**: Added Threshold Registry Integration section (v1.2). Previous: Status/Score mapping, common mistakes section (v1.1)


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

- **Location**: `docs/06_SYS/` within project docs directory
- **Naming**: `SYS-NN_descriptive_system_name.md` (NN = 3-digit sequential)
- **Structure**: One primary SYS file per architectural subsystem

---

## 2. Document Structure (Required sections)

SYS documents follow a comprehensive structure translating ADR decisions into system requirements:

#### **Part 1: System Definition**
- Document Control, Executive Summary, Scope

#### **Part 2: System Requirements**
- Functional Requirements, Quality Attributes

#### **Part 3: System Specification**
- Interface Specifications, Data Management Requirements, Testing and Validation Requirements

#### **Part 4: System Operations**
- Deployment and Operations Requirements, Compliance and Regulatory Requirements

#### **Part 5: Validation and Control**
- Acceptance Criteria, Risk Assessment, Traceability, Implementation Notes

---

## 3. Document Control Requirements

**Required Fields** (8 mandatory):
- Status, Version, Date Created/Last Updated, Author, Reviewers, Owner, Priority
- REQ-Ready Score

**Format**:
```markdown
| Item | Details |
|------|---------|
| **REQ-Ready Score** | ✅ 95% (Target: ≥90%) |
```

> **Note**: SYS templates include REQ-Ready Score (mandatory for Layer 7 progression). EARS-Ready Score is optional and informational when present.

### Status and REQ-Ready Score Mapping

| REQ-Ready Score | Required Status | Notes |
|-----------------|-----------------|-------|
| ≥90% | Approved | Meets SYS-MVP standard |
| 75-89% | In Review | Needs refinement before approval |
| <75% | Draft | Early development |

---

## 4. ID and Naming Standards

- **Filename**: `SYS-NN_descriptive_system_name.md`
- **H1**: `# SYS-NN: [System Name/Component Name]`
- **Requirement IDs**: SYS-NN-P-N (Performance), SYS-NN-R-N (Reliability), etc.

### 4.1 Element ID Format (MANDATORY)

**Pattern**: `SYS.{DOC_NUM}.{ELEM_TYPE}.{SEQ}` (4 segments, dot-separated)

| Element Type | Code | Example |
|--------------|------|---------|
| Functional Requirement | 01 | SYS.02.01.01 |
| Quality Attribute | 02 | SYS.02.02.01 |
| Use Case | 11 | SYS.02.11.01 |
| System Requirement | 26 | SYS.02.26.01 |

> ⚠️ **REMOVED PATTERNS** - Do NOT use:
> - `FR-XXX` → Use `SYS.NN.01.SS`
> - `QA-XXX` → Use `SYS.NN.02.SS`
>
> **Reference**: [ID_NAMING_STANDARDS.md — Cross-Reference Link Format](../ID_NAMING_STANDARDS.md#cross-reference-link-format-mandatory)

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
**Validation**: Enforced before REQ creation (single standard profile)

### Scoring Criteria

**Requirements Decomposition Clarity (35%)**:
- System boundaries clearly defined with acceptance/failure scopes: 15%
- Functional requirements broken down to implementable capabilities: 10%
- Requirement dependencies and prerequisites identified: 5%
- System responsibilities aligned with ADR architectural decisions: 5%

**Quality Attributes Quantification (30%)**:
- Performance requirements quantified with percentiles and thresholds: 15%
- Reliability requirements specified with uptime/SLA targets: 5%
- Security requirements defined with compliance framework references: 5%
- Scalability requirements quantified for resource and capacity growth: 5%

**Interface Specifications (20%)**:
- External API contracts defined (reference CTR creation guidelines): 10%
- Internal module interfaces specified with contract requirements: 5%
- Data exchange protocols and schemas documented: 5%

**Implementation Readiness (15%)**:
- Testing requirements specified for all functional and quality attribute categories: 5%
- Deployment and operational requirements documented: 5%
- Monitoring and observability requirements quantified: 5%

### Quality Gate Enforcement
- Score below 90% prevents REQ artifact creation
- Format validation requires ✅ emoji and percentage
- Threshold enforcement at pre-commit uses the standard SYS profile

---

## 8. Traceability Requirements (MANDATORY - Layer 6)

**Complete Upstream Tag Chain**:
```markdown
@brd: BRD.NN.EE.SS
@prd: PRD.NN.EE.SS
@ears: EARS.NN.EE.SS
@bdd: BDD.NN.EE.SS
@adr: ADR-NN
```

**Layer 6 Requirements**: SYS must reference ALL upstream artifacts

**Downstream Linkages**:
- REQ artifacts must respect SYS system boundaries and quality attribute constraints
- SPEC implementations must satisfy SYS interface specifications
- CTR contracts must exactly match SYS API requirements

---

## 9. Quality Attributes

**Technical Accuracy**: All requirements must be implementable within ADR architectural boundaries

**Business Alignment**: System capabilities must support business objectives from 01_BRD/PRD

**Interface Compliance**: API and integration requirements must be contractually complete

**Operational Viability**: Deployment, monitoring, and operational requirements must be production-ready

**Testability**: All functional and quality attribute requirements must have measurable acceptance criteria

---

## 10. Quality Gates (Pre-Commit Validation)

- SYS completeness and ADR alignment validation
- REQ-ready score verification (Target: ≥90%)
- Quality attribute quantification and measurability checks
- Interface specification completeness

---

## 11. Additional Requirements

- System boundaries must prevent requirement bleed between components
- Quality attributes must be prioritized and quantified with measurable thresholds
- Security and compliance requirements must reference specific standards
- Performance and scalability targets must be justified with business needs

---

## Downstream Creation Guidelines

### Creating REQ from SYS

SYS documents establish system requirements that must be decomposed into atomic REQ documents:

**REQ Decomposition Rules**:
1. Each SYS functional requirement → 3-7 atomic REQ files
2. Each SYS quality attribute category → 2-4 atomic REQ files per category
3. Each SYS interface → 1-3 atomic REQ files per interface

**REQ Validation Against SYS**:
- All REQ capabilities must fit within SYS system boundaries
- All REQ acceptance criteria must satisfy SYS exit criteria
- All REQ quality attribute targets must meet or exceed SYS quality thresholds

**Interface CTR Creation**:
- When SYS specifies external API contracts, create CTR documents
- CTR requirements must exactly match SYS interface specifications
- CTR validation blocks SYS creation if interfaces remain unspecified

---

**Framework Compliance**: 100% AI Dev Flow SDD framework (Layer 6)
**Integration**: Enforces SYS → Requirements Layer (REQ) progression quality gates

---

## 12. Common Mistakes to Avoid

| Mistake | Correct |
|---------|---------|
| `Status: Approved` (with score below threshold) | Match status to score threshold (Target: ≥90%) |
| Quality attributes without percentiles | Use p50/p95/p99 for performance targets |
| Missing criticality level | Specify Mission-Critical/Business-Critical/Operational |
| Interface specs without CTR reference | Create CTR for external APIs |
| Requirements without acceptance criteria | Include measurable acceptance criteria for all requirements |
| Missing ADR alignment verification | Verify all requirements fit within ADR architectural boundaries |
| `response time < 200ms` (hardcoded) | `response time < @threshold: PRD.NN.perf.api.p95_latency` |
| `timeout: 5000` (magic number) | `timeout: @threshold: PRD.NN.timeout.default` |
| `uptime: 99.9%` (hardcoded SLA) | `uptime: @threshold: PRD.NN.sla.uptime.target` |

---

## 13. Upstream Artifact Verification Process

### Before Creating This Document

**Step 1: Inventory Existing Upstream Artifacts**

```bash
# List existing upstream artifacts for this layer
ls -la docs/01_BRD/    # Layer 1
ls -la docs/02_PRD/    # Layer 2
ls -la docs/03_EARS/   # Layer 3
ls -la docs/04_BDD/    # Layer 4
ls -la docs/05_ADR/    # Layer 5
ls -la docs/06_SYS/    # Layer 6
ls -la docs/07_REQ/    # Layer 7
# ... continue for applicable layers
```

**Step 2: Map Existing Documents to Traceability Tags**

| Tag | Required for This Layer | Existing Document | Action |
|-----|------------------------|-------------------|--------|
| @brd | Yes/No | BRD-01 or null | Reference/Create/Skip |
| @prd | Yes/No | PRD-01 or null | Reference/Create/Skip |
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
| Related | SYS-NN | [Related SYS title] | Shared system context |
| Depends | SYS-NN | [Prerequisite SYS title] | Must complete before this |

**Tags**:
```markdown
@related-sys: SYS-NN
@depends-sys: SYS-NN
```

---

## 14. Threshold Registry Integration

**Purpose**: Prevent magic numbers by referencing centralized threshold registry.

### When @threshold Tag is Required

Use `@threshold` for ALL quantitative values that are:
- Business-critical (compliance limits, SLAs)
- Configurable (timeout values, rate limits)
- Shared across documents (performance targets)
- Quality attribute-related (p50/p95/p99 latencies, uptime percentages)

### @threshold Tag Format

```markdown
@threshold: PRD.NN.category.subcategory.key
```

**Examples**:
- `@threshold: PRD.035.perf.api.p95_latency`
- `@threshold: PRD.035.timeout.circuit_breaker.threshold`
- `@threshold: PRD.035.sla.uptime.target`
- `@threshold: PRD.035.resource.memory.max_heap`

### SYS-Specific Threshold Categories

| Category | SYS Usage | Example Key |
|----------|-----------|-------------|
| `perf.*` | Performance requirements | `perf.api.p95_latency` |
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
- `p95 latency: @threshold: PRD.NN.perf.api.p95_latency`
- `uptime: @threshold: PRD.NN.sla.uptime.target`
- `memory limit: @threshold: PRD.NN.resource.memory.max_heap`
- `circuit breaker threshold: @threshold: PRD.NN.timeout.circuit_breaker.threshold`

### Traceability Requirements Update

Add `@threshold` to Required Tags table in Traceability section:

| Tag | Format | When Required |
|-----|--------|---------------|
| @threshold | PRD-NN:category.key | When referencing SLAs, timing, limits, or configurable values |

### Validation

Run `detect_magic_numbers.py` to verify:
1. No hardcoded quantitative values in quality attribute sections
2. All `@threshold` references resolve to valid registry keys
3. All SLA targets use threshold references

---

## 15. Cross-Document Validation (MANDATORY)

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
python scripts/validate_cross_document.py --document docs/06_SYS/SYS-NN_slug.md --auto-fix

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
| Invalid tag format | Correct to TYPE.NN.TT.SS or TYPE-NN format |
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
