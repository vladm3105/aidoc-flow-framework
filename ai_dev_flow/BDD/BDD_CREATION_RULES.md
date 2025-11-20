# BDD Creation Rules

**Version**: 1.0
**Date**: 2025-11-19
**Last Updated**: 2025-11-19
**Source**: Derived from BDD-TEMPLATE.feature, EARS requirements, and Gherkin best practices
**Purpose**: Complete reference for creating BDD feature files according to doc_flow SDD framework
**Changes**: Added ADR-ready scoring system for BDD documents

---

## Table of Contents

1. [File Organization and Directory Structure](#1-file-organization-and-directory-structure)
2. [Document Structure (Gherkin Syntax)](#2-document-structure-gherkin-syntax)
3. [Document Control Requirements](#3-document-control-requirements)
4. [Feature File Standards](#4-feature-file-standards)
5. [Scenario Types and Structure](#5-scenario-types-and-structure)
6. [ADR Relationship Guidelines](#6-adr-relationship-guidelines)
7. [ADR-Ready Scoring System](#7-adr-ready-scoring-system)
8. [Traceability Requirements](#8-traceability-requirements)
9. [Quality Attributes](#9-quality-attributes)
10. [Quality Gates](#10-quality-gates)
11. [Additional Requirements](#11-additional-requirements)

---

## 1. File Organization and Directory Structure

- **Location**: `docs/BDD/` within project docs directory
- **Naming**: `BDD-NNN_descriptive_scenarios.feature` (NNN = 3-digit sequential)
- **Structure**: One primary feature file per EARS requirement set

---

## 2. Document Structure (Gherkin Syntax)

**Required Structure for BDD Feature Files**:

```gherkin
# Header with traceability and control metadata
## Document Control | metadata table |
@brd: BRD-NNN:REQUIREMENT-ID
@prd: PRD-NNN:REQUIREMENT-ID
@ears: EARS-NNN:STATEMENT-ID

Feature: [Business Capability Title]
  As a [stakeholder role]
  I want [specific capability]
  So that [business benefit]

  Background: [Common context for all scenarios]

  @positive @functional @acceptance
  Scenario: [Primary success path]
    Given [initial context]
    When [primary action]
    Then [expected outcome]

  @negative @error_handling
  Scenario: [Error condition handling]
    Given [error precondition]
    When [invalid action]
    Then [error response]
```

---

## 3. Document Control Requirements

**Location**: Header comment section at top of .feature file

**Required Fields** (6 mandatory):
- Project Name
- Document Version
- Date
- Document Owner
- Prepared By
- Status
- ADR-Ready Score (⭐ NEW)

**Format**:
```gherkin
## Document Control

| Item | Details |
|------|---------|
| **Project Name** | [Trading Platform v2.0] |
| **ADR-Ready Score** | ✅ 95% (Target: ≥90%) |
```

---

## 4. Feature File Standards

**Filename**: `BDD-NNN_descriptive_requirements.feature`

**Feature Declaration**:
- Business-focused title
- User role (As a...)
- Specific capability (I want...)
- Business benefit (So that...)

**Required Tags**:
- `@brd: BRD-NNN:ID` - Business requirements upstream
- `@prd: PRD-NNN:ID` - Product requirements upstream
- `@ears: EARS-NNN:ID` - Engineering requirements upstream

---

## 5. Scenario Types and Structure

**5.1 Success Path Scenarios** (@positive):
- Primary business functionality
- Expected successful outcomes
- Measurable business value

**5.2 Error Path Scenarios** (@negative):
- Invalid inputs and error conditions
- Graceful error handling
- Security boundary validation

**5.3 Edge Case Scenarios** (@boundary @edge_case):
- Boundary conditions and limits
- Performance boundaries
- Concurrent operations

**5.4 Alternative Path Scenarios** (@alternative):
- Optional parameters and configurations
- Alternative workflows and outcomes

**5.5 Non-Functional Scenarios** (@non_functional):
- Performance, security, reliability testing

---

## 6. ADR Relationship Guidelines

**EARS → BDD → ADR Workflow**:
- BDD scenarios provide concrete test cases that drive architectural decisions
- ADR processes evaluate technical alternatives against BDD requirements
- Failed BDD scenarios may necessitate ADR changes

**ADR Impact Analysis**:
- BDD scenarios define the "what" that ADRs must enable
- Architecture selection must support all BDD scenario outcomes
- Performance targets in BDD scenarios drive scaling decisions

---

## 7. ADR-Ready Scoring System ⭐ NEW

### Overview
ADR-ready scoring measures BDD maturity and readiness for progression to Architecture Decision Records (ADR) phase.

**Format**: `✅ NN% (Target: ≥90%)`
**Location**: Document Control table
**Validation**: Enforced before ADR creation

### Scoring Criteria

**Scenario Completeness (35%)**:
- All EARS statements translated to BDD scenarios: 15%
- Comprehensive coverage (success/error/edge cases): 15%
- Observable verification methods specified: 5%

**Testability (30%)**:
- Scenarios are automatable: 15%
- Data-driven scenarios use Examples tables: 10%
- Performance benchmarks quantifiable: 5%

**Architecture Requirements Clarity (25%)**:
- Performance, security, scalability NFRs specified: 15%
- Integration points and external dependencies defined: 10%

**Business Validation (10%)**:
- Business acceptance criteria traceable: 5%
- Measurable success outcomes defined: 5%

### Quality Gate Enforcement
- Score <90% prevents ADR artifact creation
- Format validation requires ✅ emoji and percentage
- Threshold enforcement at pre-commit

---

## 8. Traceability Requirements (MANDATORY - Layer 4)

**Upstream Tag Chain Required**:
```gherkin
@brd: BRD-NNN:REQUIREMENT-ID
@prd: PRD-NNN:REQUIREMENT-ID
@ears: EARS-NNN:STATEMENT-ID
```

**Layer 4 Requirements**: BDD must reference ALL upstream artifacts (BRD + PRD + EARS)

**Downstream Linkages**:
- ADR decisions must satisfy BDD scenarios
- Code implementation must pass BDD tests
- Specification artifacts must align with BDD acceptance criteria

---

## 9. Quality Attributes

**Automated Execution**: All scenarios must be executable by test automation frameworks

**Performance Validation**: Response time and throughput benchmarks included

**Security Testing**: Authentication, authorization, and data protection scenarios

**Reliability Validation**: Error handling and resilience scenarios

**Scalability Testing**: Boundary conditions and load scenarios

---

## 10. Quality Gates (Pre-Commit Validation)

- BDD syntax validation
- ADR-ready score verification (≥90%)
- Scenario coverage completeness
- Traceability chain validation

---

## 11. Additional Requirements

- Business language in scenario descriptions
- Observable pass/fail criteria
- Integration with CI/CD pipelines
- Regular test execution and regression prevention

---

**Framework Compliance**: 100% doc_flow SDD framework (Layer 4)
