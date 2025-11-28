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

**Version**: 1.0
**Date**: 2025-11-19
**Last Updated**: 2025-11-19
**Source**: Derived from SYS-TEMPLATE.md and ADR decisions
**Purpose**: Complete reference for creating SYS documents according to doc_flow SDD framework
**Changes**: Added REQ-ready scoring system for SYS documents

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
@brd: BRD-NNN:REQUIREMENT-ID
@prd: PRD-NNN:REQUIREMENT-ID
@ears: EARS-NNN:STATEMENT-ID
@bdd: BDD-NNN:SCENARIO-ID
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


## 12. Upstream Artifact Verification Process

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
