# =============================================================================
# 📋 Document Role: This is a DERIVATIVE of BDD-TEMPLATE.feature
# - Authority: BDD-TEMPLATE.feature is the single source of truth for BDD structure
# - Purpose: AI guidance for document creation (derived from template)
# - On conflict: Defer to BDD-TEMPLATE.feature
# =============================================================================
---
title: "BDD Creation Rules"
tags:
  - creation-rules
  - layer-4-artifact
  - shared-architecture
custom_fields:
  document_type: creation-rules
  artifact_type: BDD
  layer: 4
  priority: shared
  development_status: active
---

> **📋 Document Role**: CREATION GUIDANCE for BDD documents (DERIVATIVE).
> - **Authority**: `BDD-TEMPLATE.feature` is the PRIMARY STANDARD (single source of truth)
> - **Purpose**: Human-readable explanation of Template structure
> - **Scope**: Does NOT define new rules - only explains Template
> - **Conflict Resolution**: If this conflicts with Template, update this document
> - **Validation**: Use `BDD_VALIDATION_RULES.md` after BDD creation/changes

# BDD Creation Rules

**Version**: 1.2
**Date**: 2025-11-19
**Last Updated**: 2025-11-30
**Source**: Derived from BDD-TEMPLATE.feature, EARS requirements, and Gherkin best practices
**Purpose**: Complete reference for creating BDD feature files according to doc_flow SDD framework
**Changes**: Added Threshold Registry Integration section (v1.2). Previous: Status/Score mapping, common mistakes section (v1.1)

---

## Table of Contents

1. [File Organization and Directory Structure](#1-file-organization-and-directory-structure)
   1.1. [YAML Frontmatter Metadata](#11-yaml-frontmatter-metadata-required-for-md-files)
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
12. [Common Mistakes to Avoid](#12-common-mistakes-to-avoid)
13. [Upstream Artifact Verification Process](#13-upstream-artifact-verification-process)
14. [Threshold Registry Integration](#14-threshold-registry-integration)

---

## 1. File Organization and Directory Structure

- **Location**: `docs/BDD/` within project docs directory
- **Naming**: `BDD-NNN_descriptive_slug.md` or `BDD-NNN_descriptive_slug.feature` (NNN = 3-digit sequential)
- **Structure**: One primary feature file per EARS requirement set

---

## 1.1 YAML Frontmatter Metadata (Required for .md files)

All BDD markdown files MUST include YAML frontmatter metadata consistent with other SDD artifacts (BRD, PRD, EARS).

**Required YAML Frontmatter Structure**:

```yaml
---
title: "BDD-NNN: Feature Title"
tags:
  - bdd
  - layer-4-artifact
  - shared-architecture  # or ai-agent-primary for agent-based features
  - feature-specific-tag
custom_fields:
  document_type: bdd
  artifact_type: BDD
  layer: 4
  architecture_approaches: [ai-agent-based, traditional-8layer]  # or single approach
  priority: shared  # or primary/fallback
  development_status: active
  agent_id: AGENT-NNN  # Only for ai-agent-primary documents
  requirements_verified:
    - EARS-NNN
    - BRD-NNN
  traceability:
    upstream: [BRD-NNN, PRD-NNN, EARS-NNN]
    downstream: [ADR, SYS, REQ, SPEC, Code, Tests]
---
```

**Shared Architecture Example** (most BDD files):
```yaml
---
title: "BDD-008: Wallet Funding via ACH, Card, and PayPal"
tags:
  - bdd
  - layer-4-artifact
  - shared-architecture
  - wallet
  - funding
  - payments
custom_fields:
  document_type: bdd
  artifact_type: BDD
  layer: 4
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  requirements_verified:
    - EARS-008
    - BRD-008
  traceability:
    upstream: [BRD-008, PRD-008, EARS-008]
    downstream: [ADR, SYS, REQ, SPEC, Code, Tests]
---
```

**AI-Agent Primary Example** (agent-based features):
```yaml
---
title: "BDD-022: Fraud Detection Agent (ML-based Risk)"
tags:
  - bdd
  - layer-4-artifact
  - ai-agent-primary
  - recommended-approach
  - fraud-detection
  - ml-risk
custom_fields:
  document_type: bdd
  artifact_type: BDD
  layer: 4
  architecture_approach: ai-agent-based
  priority: primary
  development_status: active
  agent_id: AGENT-001
  requirements_verified:
    - EARS-022
    - BRD-022
  traceability:
    upstream: [BRD-022, PRD-022, EARS-022]
    downstream: [ADR, SYS, REQ, SPEC, Code, Tests]
---
```

**Key Differences from .feature files**:
- YAML frontmatter replaces comment-based header (`# ===...`)
- Traceability information moves to `custom_fields.traceability`
- Architecture classification uses standard tags (`shared-architecture`, `ai-agent-primary`)
- Agent ID included for AI-agent documents

---

## 2. Document Structure (Gherkin Syntax)

**Required Structure for BDD Feature Files**:

```gherkin
# Header with traceability and control metadata
## Document Control | metadata table |
@brd: BRD.NN.EE.SS
@prd: PRD.NN.EE.SS
@ears: EARS.NN.EE.SS

Feature: [Business Capability Title]
  As a [stakeholder role]
  I want [specific capability]
  So that [business benefit]

  Background: [Common context for all scenarios]

  @primary @functional @acceptance
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

**Required Document Control Fields (7 mandatory)**:
1. Project Name
2. Document Version
3. Date
4. Document Owner
5. Prepared By
6. Status
7. ADR-Ready Score (format: `✅ NN% (Target: ≥90%)`)

**Format**:
```gherkin
## Document Control

| Item | Details |
|------|---------|
| **Project Name** | [Service Platform v2.0] |
| **ADR-Ready Score** | ✅ 95% (Target: ≥90%) |
```

### Status and ADR-Ready Score Mapping

| ADR-Ready Score | Required Status |
|-----------------|-----------------|
| >= 90% | Approved |
| 70-89% | In Review |
| < 70% | Draft |

---

## 4. Feature File Standards

**Filename**: `BDD-NNN_descriptive_requirements.feature`

**Feature Declaration**:
- Business-focused title
- User role (As a...)
- Specific capability (I want...)
- Business benefit (So that...)

**Required Tags**:
- `@brd: BRD.NN.EE.SS` - Business requirements upstream (sub-ID dot notation)
- `@prd: PRD.NN.EE.SS` - Product requirements upstream (sub-ID dot notation)
- `@ears: EARS.NN.EE.SS` - Engineering requirements upstream (sub-ID dot notation)

---

## 5. Scenario Types and Structure

### Step Ordering Rule

**Step Ordering Rule**: Steps MUST follow this sequence:
1. **Given** (preconditions) - FIRST
2. **When** (actions) - SECOND
3. **Then** (outcomes) - THIRD
4. **And/But** (continuations) - After any step type

**Invalid Sequences**:
- `When` before `Given` ❌
- `Then` before `When` ❌
- `Then` before `Given` ❌

**Valid Sequences**:
- `Given → When → Then` ✅
- `Given → And → When → Then → And` ✅
- `Given → When → And → Then → And → But` ✅

---

**5.1 Success Path Scenarios** (@primary):
- Primary business functionality
- Expected successful outcomes
- Measurable business value

**5.2 Error Path Scenarios** (@negative):
- Invalid inputs and error conditions
- Graceful error handling
- security boundary validation

**5.3 Edge Case Scenarios** (@boundary @edge_case):
- Boundary conditions and limits
- Performance boundaries
- Concurrent operations

**5.4 Alternative Path Scenarios** (@alternative):
- Optional parameters and configurations
- Alternative workflows and outcomes

**5.5 Quality Attribute Scenarios** (@quality_attribute):
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

### ADR-Ready Score Format Specification

**Format**: `✅ NN% (Target: ≥90%)`

**Format Rules**:
- Must include checkmark emoji (✅) at start
- Percentage as integer (1-100)
- Target threshold in parentheses
- Example: `✅ 85% (Target: ≥90%)`

**Location**: Document Control table (mandatory field)
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
- Performance, security, scalability quality attributes specified: 15%
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

**Required Tags** (ALL are MANDATORY per BDD-TEMPLATE.feature):
```gherkin
@brd: BRD.NN.EE.SS    # MANDATORY - business requirements
@prd: PRD.NN.EE.SS    # MANDATORY - product requirements
@ears: EARS.NN.EE.SS  # MANDATORY - engineering requirements
```

**Format**: Extended format with requirement ID suffix (`:NNN`) is REQUIRED.

**Layer 4 Requirements**: BDD must reference ALL upstream artifacts (BRD + PRD + EARS)

**Downstream Linkages**:
- ADR decisions must satisfy BDD scenarios
- Code implementation must pass BDD tests
- Specification artifacts must align with BDD acceptance criteria

---

## 9. Quality Attributes

**Automated Execution**: All scenarios must be executable by test automation frameworks

**Performance Validation**: Response time and throughput benchmarks included

**security Testing**: Authentication, authorization, and data protection scenarios

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

---

## 12. Common Mistakes to Avoid

| Mistake | Correct |
|---------|---------|
| `Status: Approved` (with <90% ADR-Ready score) | `Status: In Review` or `Status: Draft` |
| Missing @ears traceability tag | `@ears: EARS.NN.EE.SS` |
| Scenario without tags | Add `@primary`, `@negative`, `@boundary` tags |
| `Given-When-Then` without concrete values | Use specific data in steps |
| Vague outcomes like "should work" | Observable verification: "response status code is 200" |
| Missing Background section | Add common preconditions to Background |
| `response time is less than 200ms` (hardcoded) | `response time is less than @threshold: PRD.NNN.perf.api.p95_latency` |
| `timeout after 5000ms` (magic number) | `timeout after @threshold: PRD.NNN.timeout.default` |
| `rate limit of 100 requests` (hardcoded) | `rate limit of @threshold: PRD.NNN.limit.api.requests_per_second` |

### 12.1 Critical Anti-Patterns (Visual Examples)

#### Anti-Pattern 1: Tags in Comments (BLOCKING)

**❌ WRONG** (Gherkin frameworks cannot parse comment-based tags):
```gherkin
# @brd: BRD.01.01.01
# @prd: PRD.01.01.01
# @ears: EARS.01.24.01
Feature: My Feature
```

**✅ CORRECT** (Gherkin-native tags before Feature):
```gherkin
@brd:BRD.01.01.01
@prd:PRD.01.01.01
@ears:EARS.01.24.01
Feature: My Feature
```

**Why this matters**: BDD test frameworks (Cucumber, Behave, pytest-bdd) use tags for filtering, reporting, and execution control. Comment-based tags are invisible to these tools.

#### Anti-Pattern 2: ADR-Ready Score Format (BLOCKING)

**❌ WRONG** (missing checkmark and ≥ symbol):
```markdown
| **ADR-Ready Score** | 75% (Target: 90%) |
```

**✅ CORRECT** (with checkmark and ≥ symbol):
```markdown
| **ADR-Ready Score** | ✅ 75% (Target: ≥90%) |
```

**Why this matters**: Automated validation scripts parse this exact format. Inconsistent formatting breaks dashboard reporting and quality gates.

#### Anti-Pattern 3: Hardcoded Magic Numbers (HIGH)

**❌ WRONG** (hardcoded values):
```gherkin
Then response time is less than 200ms
And timeout occurs after 5000ms
And rate limit is 100 requests per second
```

**✅ CORRECT** (threshold registry references):
```gherkin
Then response time is less than @threshold: PRD.035.perf.api.p95_latency
And timeout occurs after @threshold: PRD.035.timeout.default
And rate limit is @threshold: PRD.035.limit.api.requests_per_second
```

**Why this matters**: Hardcoded values become stale, are difficult to update consistently, and break traceability to requirements.

#### Anti-Pattern 4: Missing Scenario Categories (MEDIUM)

**❌ WRONG** (only success scenarios):
```gherkin
@primary @functional
Scenario: User logs in successfully
  Given valid credentials
  When user submits login
  Then user is authenticated
```

**✅ CORRECT** (all 8 categories represented):
```gherkin
# Include scenarios for: @primary, @alternative, @negative,
# @edge_case, @data_driven, @integration, @quality_attribute, @failure_recovery
```

**Why this matters**: Incomplete scenario coverage leads to untested edge cases and potential production failures.

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

Include ONLY if relationships exist between BDD features sharing domain context or implementation dependencies.

**Tags**:
```markdown
@related-bdd: BDD-NNN
@depends-bdd: BDD-NNN
```

---

## 14. Threshold Registry Integration

**Purpose**: Prevent magic numbers by referencing centralized threshold registry in BDD scenarios.

### When @threshold Tag is Required

Use `@threshold` for ALL quantitative values in BDD scenarios that are:
- Performance targets (response times, SLA validations)
- Timeout expectations (operation timeouts, circuit breaker tests)
- Rate limit validations (requests per second, concurrent users)
- Business-critical values (compliance thresholds, transaction limits)

### @threshold Tag Format in Gherkin

**Scenario Tag Format**:
```gherkin
@threshold: PRD.NNN.perf.api.p95_latency
Scenario: API responds within performance threshold
```

**Step Definition Format**:
```gherkin
Then the response time SHOULD be less than @threshold: PRD.NNN.perf.api.p95_latency
```

**Examples**:
- `@threshold: PRD.035.perf.api.p95_latency`
- `@threshold: PRD.035.sla.uptime.target`
- `@threshold: PRD.035.compliance.travel_rule.amount`

### BDD-Specific Threshold Categories

| Category | BDD Usage | Example Key |
|----------|-----------|-------------|
| `perf.*` | Performance scenario validation | `perf.api.p95_latency` |
| `sla.*` | SLA scenario validation | `sla.uptime.target` |
| `limit.*` | Rate limit scenario testing | `limit.api.requests_per_second` |
| `compliance.*` | Compliance boundary testing | `compliance.travel_rule.amount` |
| `timeout.*` | Timeout scenario validation | `timeout.request.sync` |

### Magic Number Detection

**Invalid (hardcoded values)**:
```gherkin
Scenario: API performance validation
  Given the system is under normal load
  When a client sends a request
  Then the response time SHOULD be less than 200ms
```

**Valid (registry references)**:
```gherkin
@threshold: PRD.NNN.perf.api.p95_latency
Scenario: API performance validation
  Given the system is under normal load
  When a client sends a request
  Then the response time SHOULD be less than @threshold: PRD.NNN.perf.api.p95_latency
```

### Examples Table Integration

Use threshold references in Examples tables for data-driven scenarios:

```gherkin
Scenario Outline: Transaction limit validation
  Given a user with role "<role>"
  When they attempt a transaction of <amount>
  Then the transaction SHOULD be <result>

  Examples:
    | role   | amount                                         | result   |
    | user   | @threshold: PRD.NNN.limit.transaction.max     | rejected |
    | admin  | @threshold: PRD.NNN.limit.transaction.max     | approved |
```

### Traceability Requirements Update

Add `@threshold` to Required Tags:

| Tag | Format | When Required |
|-----|--------|---------------|
| @threshold | PRD-NNN:category.key | When scenarios validate performance, SLA, limits, or compliance values |

### Validation

Run `detect_magic_numbers.py` to verify:
1. No hardcoded quantitative values in Then steps
2. No hardcoded values in performance scenarios
3. All `@threshold` references resolve to valid registry keys
4. All Examples tables use threshold references for numeric limits

---

## 15. Cross-Document Validation (MANDATORY)

**CRITICAL**: Execute cross-document validation IMMEDIATELY after creating any BDD document. Do NOT proceed to downstream artifacts until validation passes.

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
python scripts/validate_cross_document.py --document docs/BDD/BDD-NNN_slug.md --auto-fix

# Layer validation (Phase 2) - run when all BDD documents complete
python scripts/validate_cross_document.py --layer BDD --auto-fix
```

### Layer-Specific Upstream Requirements

| This Layer | Required Upstream Tags | Tag Count |
|------------|------------------------|-----------|
| BDD (Layer 4) | @brd, @prd, @ears | 3 |

### Auto-Fix Actions (No Confirmation Required)

| Issue | Fix Action |
|-------|------------|
| Missing @brd/@prd/@ears tag | Add with upstream document reference |
| Invalid tag format | Correct to TYPE.NN.EE.SS or TYPE-NNN format |
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

**Blocking**: YES - Cannot proceed to ADR creation until Phase 1 validation passes with 0 errors.
