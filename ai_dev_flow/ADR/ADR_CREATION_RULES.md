---
title: "ADR Creation Rules"
tags:
  - creation-rules
  - layer-5-artifact
  - shared-architecture
custom_fields:
  document_type: creation-rules
  artifact_type: ADR
  layer: 5
  priority: shared
  development_status: active
---

# ADR Creation Rules

**Version**: 1.0
**Date**: 2025-11-19
**Last Updated**: 2025-11-19
**Source**: Derived from ADR-TEMPLATE.md and SPEC_DRIVEN_DEVELOPMENT_GUIDE.md
**Purpose**: Complete reference for creating ADR documents according to doc_flow SDD framework
**Changes**: Added SYS-ready scoring system for ADR documents

---

## Table of Contents

1. [File Organization and Directory Structure](#1-file-organization-and-directory-structure)
2. [Document Structure (Required Sections)](#2-document-structure-required-sections)
3. [Document Control Requirements](#3-document-control-requirements)
4. [ID and Naming Standards](#4-id-and-naming-standards)
5. [ADR Decision Categories](#5-adr-decision-categories)
6. [SYS Relationship Guidelines](#6-sys-relationship-guidelines)
7. [SYS-Ready Scoring System](#7-sys-ready-scoring-system)
8. [Traceability Requirements](#8-traceability-requirements)
9. [Quality Attributes](#9-quality-attributes)
10. [Quality Gates](#10-quality-gates)
11. [Additional Requirements](#11-additional-requirements)

---

## 1. File Organization and Directory Structure

- **Location**: `docs/ADR/` within project docs directory
- **Naming**: `ADR-NNN_descriptive_architecture_decision.md` (NNN = 3-digit sequential)
- **Structure**: One primary ADR file per architecture decision

---

## 2. Document Structure (Required Sections)

ADR documents follow a comprehensive 4-part structure:

#### **Part 1: Decision Context and Requirements**
- Status, Context, Decision, Requirements Satisfied

#### **Part 2: Impact Analysis and Architecture**
- Consequences, Architecture Flow, Implementation Assessment, Impact Analysis

#### **Part 3: Implementation and Operations**
- Security, Related Decisions, Implementation Notes

#### **Part 4: Traceability and Documentation**
- Traceability, References

---

## 3. Document Control Requirements

**Required Fields** (6 mandatory):
- Project Name
- Document Version
- Date
- Document Owner
- Prepared By
- Status
- SYS-Ready Score (⭐ NEW)

**Format**:
```markdown
| Item | Details |
|------|---------|
| **SYS-Ready Score** | ✅ 95% (Target: ≥90%) |
```

---

## 4. ID and Naming Standards

- **Filename**: `ADR-NNN_descriptive_architecture_decision.md`
- **H1**: `# ADR-NNN: [Architecture Decision Title]`
- **Status Tags**: Proposed, Accepted, Rejected, Superseded, Deprecated

---

## 5. ADR Decision Categories

**Technical Decisions**:
- Framework, library, or technology selection
- Architecture patterns and design principles
- Infrastructure and deployment models

**Quality Attribute Decisions**:
- Performance, scalability, and reliability requirements
- Security and compliance approaches
- Operational and monitoring strategies

**Integration Decisions**:
- Service interaction patterns
- Data flow and communication protocols
- External system integration approaches

---

## 6. SYS Relationship Guidelines

**ADR → SYS Workflow**:
- ADRs establish the "how" for architecture
- SYS documents translate ADRs into detailed system requirements
- SYS requirements must be implementable within ADR constraints

**SYS Impact Analysis**:
- ADR decisions may necessitate SYS requirement modifications
- Performance targets from ADRs drive SYS NFRs
- Integration patterns in ADRs define SYS interfaces

---

## 7. SYS-Ready Scoring System ⭐ NEW

### Overview
SYS-ready scoring measures ADR maturity and readiness for progression to System Requirements (SYS) phase.

**Format**: `✅ NN% (Target: ≥90%)`
**Location**: Document Control table
**Validation**: Enforced before SYS creation

### Scoring Criteria

**Decision Completeness (30%)**:
- ADR follows complete decision process (Context, Decision, Consequences, Alternatives): 15%
- Requirements mapping clear and traceable: 10%
- Impact analysis comprehensive (positive/negative consequences): 5%

**Architecture Clarity (35%)**:
- Architecture flow documented with Mermaid diagrams: 15%
- Component responsibilities clearly defined: 10%
- Cross-cutting concerns addressed (security, observability): 10%

**Implementation Readiness (20%)**:
- Complexity assessment and resource estimates provided: 10%
- Dependencies and requirements identified: 5%
- Rollback and migration strategies documented: 5%

**Verification Approach (15%)**:
- Testing strategy aligned with architecture: 5%
- Success metrics and validation criteria defined: 5%
- Operational readiness assessment complete: 5%

### Quality Gate Enforcement
- Score <90% prevents SYS artifact creation
- Format validation requires ✅ emoji and percentage
- Threshold enforcement at pre-commit

---

## 8. Traceability Requirements (MANDATORY - Layer 5)

**Complete Upstream Tag Chain**:
```markdown
@brd: BRD-NNN:REQUIREMENT-ID
@prd: PRD-NNN:REQUIREMENT-ID
@ears: EARS-NNN:STATEMENT-ID
@bdd: BDD-NNN:SCENARIO-ID
```

**Layer 5 Requirements**: ADR must reference ALL upstream artifacts

**Downstream Linkages**:
- SYS requirements must align with ADR architectural boundaries
- REQ artifacts must respect ADR constraints
- SPEC implementations must follow ADR patterns

---

## 9. Quality Attributes

**Decision Rationale**: Evidence-based with quantitative trade-off analysis

**Technical Validation**: Architecture must be verifiable through testing

**Business Alignment**: Technical decisions support business objectives

**Implementation Feasibility**: Architecture must be buildable with available resources

**Operational Viability**: Long-term maintenance and scaling considerations

**Security Compliance**: Security architecture meets regulatory requirements

---

## 10. Quality Gates (Pre-Commit Validation)

- ADR completeness and decision quality validation
- SYS-ready score verification ≥90%
- Architecture diagram validation
- Traceability chain completeness

---

## 11. Additional Requirements

- Business justification for all architectural trade-offs
- Quantitative metrics for performance and cost impacts
- Risk mitigation strategies with probability assessments
- Technical debt and maintenance cost projections

---

**Framework Compliance**: 100% doc_flow SDD framework (Layer 5)
**Integration**: Enforces ADR → SYS progression quality gates
