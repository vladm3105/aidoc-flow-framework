# =============================================================================
# 📋 Document Role: This is a DERIVATIVE of ADR-TEMPLATE.md
# - Authority: ADR-TEMPLATE.md is the single source of truth for ADR structure
# - Purpose: AI guidance for document creation (derived from template)
# - On conflict: Defer to ADR-TEMPLATE.md
# =============================================================================
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

> **📋 Document Role**: This is a **CREATION HELPER** for ADR-TEMPLATE.md.
> - **Authority**: `ADR-TEMPLATE.md` is the single source of truth for ADR structure
> - **Validation**: Use `ADR_VALIDATION_RULES.md` after ADR creation/changes

# ADR Creation Rules

**Version**: 1.1
**Date**: 2025-11-19
**Last Updated**: 2025-11-30
**Source**: Derived from ADR-TEMPLATE.md and SPEC_DRIVEN_DEVELOPMENT_GUIDE.md
**Purpose**: Complete reference for creating ADR documents according to doc_flow SDD framework
**Changes**: Added Status/Score mapping table, new common mistakes section. Previous: SYS-ready scoring system

---

## Table of Contents

1. [File Organization and Directory Structure](#1-file-organization-and-directory-structure)
2. [Document Structure (Required sections)](#2-document-structure-required-sections)
3. [Document Control Requirements](#3-document-control-requirements)
4. [ID and Naming Standards](#4-id-and-naming-standards)
5. [ADR Decision Categories](#5-adr-decision-categories)
6. [SYS Relationship Guidelines](#6-sys-relationship-guidelines)
7. [SYS-Ready Scoring System](#7-sys-ready-scoring-system)
8. [Traceability Requirements](#8-traceability-requirements)
9. [Quality Attributes](#9-quality-attributes)
10. [Quality Gates](#10-quality-gates)
11. [Additional Requirements](#11-additional-requirements)
12. [Common Mistakes to Avoid](#12-common-mistakes-to-avoid)
13. [Upstream Artifact Verification Process](#13-upstream-artifact-verification-process)

---

## 1. File Organization and Directory Structure

- **Location**: `docs/ADR/` within project docs directory
- **Naming**: `ADR-NNN_descriptive_architecture_decision.md` (NNN = 3-digit sequential)
- **Structure**: One primary ADR file per architecture decision

---

## 2. Document Structure (Required sections)

ADR documents follow a comprehensive 4-part structure:

#### **Part 1: Decision Context and Requirements**
- Status, Context, Decision, Requirements Satisfied

#### **Part 2: Impact Analysis and Architecture**
- Consequences, Architecture Flow, Implementation Assessment, Impact Analysis

#### **Part 3: Implementation and Operations**
- security, Related Decisions, Implementation Notes

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

### Status and SYS-Ready Score Mapping

| SYS-Ready Score | Required Status |
|-----------------|-----------------|
| >= 90% | Accepted |
| 70-89% | Proposed |
| < 70% | Draft |

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
- security and compliance approaches
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
@brd: BRD-NNN:NNN
@prd: PRD-NNN:NNN
@ears: EARS-NNN:NNN
@bdd: BDD-NNN:NNN
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

**security Compliance**: security architecture meets regulatory requirements

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

---

## 12. Common Mistakes to Avoid

| Mistake | Correct |
|---------|---------|
| `Status: Accepted` (with <90% SYS-Ready score) | Match status to score threshold |
| Missing Consequences section | Document positive AND negative consequences |
| Alternatives without evaluation | Include trade-off analysis for each option |
| `@sys: SYS-NNN` (referencing downstream) | ADR should not reference downstream SYS |
| Decision without context | Provide problem statement and constraints |
| Missing architecture diagrams | Include Mermaid diagrams for architecture flow |

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

Include ONLY if relationships exist between ADRs sharing architectural context or implementation dependencies.

| Relationship | Document ID | Document Title | Purpose |
|--------------|-------------|----------------|---------|
| Related | ADR-NNN | [Related ADR title] | Shared architectural context |
| Depends | ADR-NNN | [Prerequisite ADR title] | Must complete before this |

**Tags**:
```markdown
@related-adr: ADR-NNN
@depends-adr: ADR-NNN
```
