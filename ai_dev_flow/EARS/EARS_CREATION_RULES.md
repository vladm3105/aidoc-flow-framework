# =============================================================================
# 📋 Document Role: This is a DERIVATIVE of EARS-TEMPLATE.md
# - Authority: EARS-TEMPLATE.md is the single source of truth for EARS structure
# - Purpose: AI guidance for document creation (derived from template)
# - On conflict: Defer to EARS-TEMPLATE.md
# =============================================================================
---
title: "EARS Creation Rules"
tags:
  - creation-rules
  - layer-3-artifact
  - shared-architecture
custom_fields:
  document_type: creation-rules
  artifact_type: EARS
  layer: 3
  priority: shared
  development_status: active
---

> **📋 Document Role**: This is a **CREATION HELPER** for EARS-TEMPLATE.md.
> - **Authority**: `EARS-TEMPLATE.md` is the single source of truth for EARS structure
> - **Schema**: `EARS_SCHEMA.yaml` defines machine-readable validation rules
> - **Validation**: Use `EARS_VALIDATION_RULES.md` or `scripts/validate_ears.py`

# EARS Creation Rules

**Version**: 1.1
**Date**: 2025-11-19
**Last Updated**: 2025-11-30
**Source**: Extracted from EARS-TEMPLATE.md, PRD requirements, and behavioral specification patterns
**Purpose**: Complete reference for creating EARS files according to doc-flow SDD framework
**Changes**: Merged EARS_STYLE_GUIDE.md content - added Status/BDD-Score mapping, code block formatting, traceability format details, and extended common mistakes table

---

## Table of Contents

1. [File Organization and Directory Structure](#1-file-organization-and-directory-structure)
2. [Document Structure (Required sections)](#2-document-structure-required-sections)
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

## 2. Document Structure (Required sections)

EARS documents require specific structural elements for behavioral specification:

#### Required sections:
1. **Document Control** - Metadata with BDD-Ready Score
2. **Purpose and Context** - Business and technical objectives
3. **Requirements** - Event-Driven, State-Driven, Unwanted Behavior, Ubiquitous
4. **Non-Functional Requirements** - Performance, security, Reliability, etc.
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

### Status and BDD-Ready Score Mapping

| BDD-Ready Score | Required Status |
|-----------------|-----------------|
| >= 90% | Approved |
| 70-89% | In Review |
| < 70% | Draft |

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
- **Statement IDs**: `EARS-{DocID}-{Num}` format (e.g., `EARS-006-001`, `EARS-006-002`)
  - Sequential numbering within document (001, 002, 003...)
  - ❌ **DEPRECATED**: Do NOT use category prefixes (E, S, U, UB, EVENT, STATE, UNWANTED, UBIQ)

---

## 5. EARS Syntax Patterns

### Event-Driven Requirements
**WHEN** [triggering condition] **THE** [system] **SHALL** [response] **WITHIN** [constraint]

```
WHEN [trigger condition],
THE [system component] SHALL [action 1],
[action 2],
and [action 3]
WITHIN [timing constraint].
```

### State-Driven Requirements
**WHILE** [system state] **THE** [system] **SHALL** [behavior] **WITHIN** [constraint]

```
WHILE [state condition],
THE [system component] SHALL [continuous behavior]
WITHIN [operational context].
```

### Unwanted Behavior Requirements
**IF** [error/problem] **THE** [system] **SHALL** [prevention/workaround] **WITHIN** [constraint]

```
IF [error condition],
THE [system component] SHALL [prevention/recovery action]
WITHIN [timing constraint].
```

### Ubiquitous Requirements
**THE** [system] **SHALL** [system-wide requirement] **WITHIN** [architectural boundary]

```
THE [system component] SHALL [universal behavior]
for [scope/context].
```

### Code Block Formatting

Always use triple backticks for EARS statements:

````markdown
**EARS-001-001: Requirement Name**
```
WHEN [condition],
THE [component] SHALL [action]
WITHIN [constraint].
```
**Traceability**: @brd: BRD-001:001 | @prd: PRD-001:001
````

---

## 6. Quality Attributes (NFRs)

### NFR Categorical Format

EARS documents inherit NFR IDs from upstream BRD/PRD documents using categorical prefixes:

| Category | Prefix | Keywords for Detection |
|----------|--------|------------------------|
| Performance | `NFR-PERF-` | latency, throughput, response time, p95, p99 |
| Security | `NFR-SEC-` | authentication, authorization, encryption, RBAC |
| Reliability | `NFR-REL-` | availability, MTBF, MTTR, fault tolerance, recovery |
| Scalability | `NFR-SCAL-` | concurrent users, data volumes, horizontal scaling |
| Observability | `NFR-OBS-` | logging, monitoring, tracing, alerting, metrics |
| Maintainability | `NFR-MAINT-` | code coverage, deployment, CI/CD, documentation |

### NFR Inheritance

When formalizing NFRs from BRD/PRD:
- **Inherit the same NFR ID**: If BRD defines `NFR-PERF-001`, EARS uses `NFR-PERF-001`
- **Add EARS formalization**: Apply WHEN-THE-SHALL-WITHIN syntax
- **Maintain traceability**: `@brd: BRD-017:NFR-PERF-001`

### NFR Quality Attributes

**Performance** (`NFR-PERF-`): Quantified latency, throughput, response time constraints
**Security** (`NFR-SEC-`): Authentication, authorization, encryption standards
**Reliability** (`NFR-REL-`): Availability SLAs, fault tolerance, recovery objectives
**Scalability** (`NFR-SCAL-`): Concurrent users, data volumes, growth projections
**Observability** (`NFR-OBS-`): Logging, monitoring, tracing, alerting requirements
**Maintainability** (`NFR-MAINT-`): Code coverage, deployment, documentation standards

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
- security/compliance requirements complete: 5%
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

### Standard Format

```markdown
**Traceability**: @brd: BRD-NNN:NNN | @prd: PRD-NNN:NNN | @threshold: PRD-035:category.key
```

### Required Tags

| Tag | Format | When Required |
|-----|--------|---------------|
| @brd | BRD-NNN:NNN | Always |
| @prd | PRD-NNN:NNN | Always |
| @threshold | PRD-035:category.key | When referencing timing/limits |
| @entity | PRD-004:EntityName | When referencing data entities |
| @ctr | CTR-NNN:section | When referencing API contracts |

### Do NOT Use

- Block quote format: `> **Tags**:`
- Comma separators: `@prd: ..., @threshold: ...`
- Trailing commas: `@prd: PRD-019:002, |`

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

Include ONLY if relationships exist between EARS documents sharing domain context or implementation dependencies.

| Relationship | Document ID | Document Title | Purpose |
|--------------|-------------|----------------|---------|
| Related | EARS-NNN | [Related EARS title] | Shared domain context |
| Depends | EARS-NNN | [Prerequisite EARS title] | Must complete before this |

**Tags**:
```markdown
@related-ears: EARS-NNN
@depends-ears: EARS-NNN
```

---

## 14. Batch Creation Checkpoint Rules

When creating multiple EARS documents in a session, follow these checkpoint rules to prevent inconsistencies:

### Pre-Batch Verification

**Before starting batch creation:**
1. Read `EARS_SCHEMA.yaml` to understand current metadata requirements
2. Verify tag standards: `ears` (not `ears-requirements`, `ears-formal-requirements`, etc.)
3. Verify document_type: `ears` (not `engineering-requirements`)
4. Verify architecture format: `architecture_approaches: [value]` (array, not singular)

### Every 5-Document Checkpoint

**After creating every 5 EARS documents:**
1. Run validation: `python scripts/validate_ears.py --path docs/EARS`
2. Check for:
   - Tag consistency (all use `ears`)
   - document_type consistency (all use `ears`)
   - Source Document format (`@prd: PRD-NNN`)
   - Section numbering (sequential)
3. Fix any errors before continuing

### End-of-Session Validation

**Before ending session:**
1. Run full validation: `python scripts/validate_ears.py`
2. Verify 0 errors (warnings acceptable)
3. Update EARS-000_index.md if document counts changed
4. Document any issues in session notes

### Common Batch Errors to Avoid

| Error Pattern | Correct Format |
|---------------|----------------|
| `ears-requirements` | `ears` |
| `ears-formal-requirements` | `ears` |
| `ears-NNN` | `ears` |
| `document_type: engineering-requirements` | `document_type: ears` |
| `architecture_approach: value` | `architecture_approaches: [value]` |
| `Source Document: PRD-NNN` | `Source Document: @prd: PRD-NNN` |
| `> **Tags**: @prd: ...` | `**Traceability**: @prd: ...` |
| `@prd: PRD-001, @threshold: ...` | `@prd: PRD-001 \| @threshold: ...` |
| `Status: Approved` (with 50% BDD score) | `Status: Draft` |

### Session Summary Template

```markdown
## EARS Batch Session Summary

- **Documents Created**: N
- **Validation Status**: ✅ Pass / ❌ Fail
- **Errors Found**: N
- **Errors Fixed**: N
- **Index Updated**: Yes/No
```

---

## 13. Cross-Document Validation (MANDATORY)

**CRITICAL**: Execute cross-document validation IMMEDIATELY after creating any EARS document. Do NOT proceed to downstream artifacts until validation passes.

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
python scripts/validate_cross_document.py --document docs/EARS/EARS-NNN_slug.md --auto-fix

# Layer validation (Phase 2) - run when all EARS documents complete
python scripts/validate_cross_document.py --layer EARS --auto-fix
```

### Layer-Specific Upstream Requirements

| This Layer | Required Upstream Tags | Tag Count |
|------------|------------------------|-----------|
| EARS (Layer 3) | @brd, @prd | 2 |

### Auto-Fix Actions (No Confirmation Required)

| Issue | Fix Action |
|-------|------------|
| Missing @brd/@prd tag | Add with upstream document reference |
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

**Blocking**: YES - Cannot proceed to BDD creation until Phase 1 validation passes with 0 errors.
