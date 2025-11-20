# EARS Creation Rules

**Version**: 1.0
**Date**: 2025-11-19
**Last Updated**: 2025-11-19
**Source**: Extracted from EARS-TEMPLATE.md, PRD requirements, and behavioral specification patterns
**Purpose**: Complete reference for creating EARS files according to doc-flow SDD framework
**Changes**: Added BDD-ready scoring system for EARS documents

---

## Table of Contents

1. [File Organization and Directory Structure](#1-file-organization-and-directory-structure)
2. [Document Structure (Required Sections)](#2-document-structure-required-sections)
3. [Document Control Requirements](#3-document-control-requirements)
4. [ID and Naming Standards](#4-id-and-naming-standards)
5. [EARS Syntax Patterns](#5-ears-syntax-patterns)
6. [Quality Attributes (NFRs)](#6-quality-attributes-nfrs)
7. [BDD Relationship Guidelines](#7-bdd-relationship-guidelines)
8. [BDD-Ready Scoring System](#8-bdd-ready-scoring-system)
9. [Traceability Requirements](#9-traceability-requirements)
10. [Precision and Measurability](#10-precision-and-measurability)
11. [Quality Gates](#11-quality-gates)
12. [Additional Requirements](#12-additional-requirements)

---

## 1. File Organization and Directory Structure

- **Location**: `docs/EARS/` within project docs directory
- **Naming**: `EARS-NNN_descriptive_title.md` (NNN = 3-digit sequential number)
- **Subdocuments**: For complex systems: `EARS-NNN-YY_additional_detail.md`

---

## 2. Document Structure (Required Sections)

EARS documents require specific structural elements for behavioral specification:

#### Required Sections:
1. **Document Control** - Metadata with BDD-Ready Score
2. **Purpose and Context** - Business and technical objectives
3. **Requirements** - Event-Driven, State-Driven, Unwanted Behavior, Ubiquitous
4. **Non-Functional Requirements** - Performance, Security, Reliability, etc.
5. **Guidelines for Writing EARS Statements** - Precision and measurability rules
6. **Quality Checklist** - Completeness validation
7. **Traceability** - Upstream/downstream artifacts
8. **References** - Internal/external documentation

---

## 3. Document Control Requirements

**Required Fields** (6 mandatory):
- Project Name
- Status: Draft/In Review/Approved/Implemented
- Version: Semantic versioning
- Date Created/Last Updated
- Author and Priority
- BDD-Ready Score: Format `✅ NN% (Target: ≥90%)`

**Template**:
```markdown
| Item | Details |
|------|---------|
| **Status** | Draft / In Review / Approved / Implemented |
| **Version** | [e.g., 1.0.0] |
| **BDD-Ready Score** | ✅ 95% (Target: ≥90%) |
```

---

## 4. ID and Naming Standards

- **Filename**: `EARS-NNN_descriptive_title.md`
- **H1**: `# EARS-NNN: [Short Descriptive Title]`
- **Statement IDs**: Event-NNN, State-NNN, Unwanted-NNN, Ubiquitous-NNN

---

## 5. EARS Syntax Patterns

### Event-Driven Requirements
**WHEN** [triggering condition] **THE** [system] **SHALL** [response] **WITHIN** [constraint]

### State-Driven Requirements
**WHILE** [system state] **THE** [system] **SHALL** [behavior] **WITHIN** [constraint]

### Unwanted Behavior Requirements
**IF** [error/problem] **THE** [system] **SHALL** [prevention/workaround] **WITHIN** [constraint]

### Ubiquitous Requirements
**THE** [system] **SHALL** [system-wide requirement] **WITHIN** [architectural boundary]

---

## 6. Quality Attributes (NFRs)

**Performance**: Quantified latency, throughput, response time constraints
**Security**: Authentication, authorization, encryption standards
**Reliability**: Availability SLAs, fault tolerance, recovery objectives
**Scalability**: Concurrent users, data volumes, growth projections
**Observability**: Logging, monitoring, tracing, alerting requirements
**Compliance**: Regulatory, audit, privacy requirements

---

## 7. BDD Relationship Guidelines

**CRITICAL**: EARS must enable direct translation to BDD scenarios
- Each EARS statement → Multiple BDD scenarios (success path + error cases)
- Atomic statements required for testability
- Clear Given-When-Then mapping
- Observable verification methods

---

## 8. BDD-Ready Scoring System ⭐ NEW

### Overview
BDD-ready scoring measures EARS maturity and readiness for progression to Behavior-Driven Development (BDD) phase.

**Format**: `✅ NN% (Target: ≥90%)`
**Location**: Document Control table
**Validation**: Enforced before BDD creation

### Scoring Criteria

**Requirements Clarity (40%)**:
- EARS statements follow precise WHEN-THE-SHALL-WITHIN syntax: 20%
- Each statement defines one testable concept (atomicity): 15%
- All timing/constraint clauses are quantifiable: 5%

**Testability (35%)**:
- BDD translation possible for each statement: 15%
- Observable verification methods defined: 10%
- Edge cases and error conditions specified: 10%

**NFR Completeness (15%)**:
- Performance targets quantifiable with percentiles: 5%
- Security/compliance requirements complete: 5%
- Reliability/scalability targets measurable: 5%

**Strategic Alignment (10%)**:
- Links to business objectives traceable: 5%
- Implementation paths documented: 5%

### Quality Gate Enforcement
- Score <90% prevents BDD artifact creation
- Format validation requires ✅ emoji and percentage
- Threshold enforcement at pre-commit

---

## 9. Traceability Requirements (MANDATORY - Layer 3)

**Upstream Tags Required**:
```markdown
@brd: BRD-NNN:REQUIREMENT-ID
@prd: PRD-NNN:REQUIREMENT-ID
```

**Downstream Linkages**:
- REQ and SPEC artifacts
- BDD feature files
- Code implementation paths

---

## 10. Precision and Measurability

- Replace subjective terms with quantitative measures
- Define exact thresholds and time constraints
- Specify percentile requirements (p95, p99)
- Include verification methods

---

## 11. Quality Gates (Pre-Commit Validation)

- EARS syntax validation
- BDD translation verification
- Atomicity checks
- Traceability completeness

---

## 12. Additional Requirements

- Business language focused on system behavior
- Direct mapping to BDD scenarios
- Observable success/failure criteria
- Comprehensive error condition handling

---

**Framework Compliance**: 100% doc_flow SDD framework (Layer 3)
**Integration**: Enforces EARS → BDD progression quality gates
