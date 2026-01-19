---
title: "EARS MVP Creation Rules"
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

# =============================================================================
# 📋 Document Role: Guides creation of EARS-MVP-TEMPLATE.md (default)
# - Authority: EARS-MVP-TEMPLATE.md is the primary standard for EARS structure; full template is archived
# - Purpose: AI guidance for document creation (derived from MVP template)
# - On conflict: Defer to EARS-MVP-TEMPLATE.md
# =============================================================================
---
title: "EARS MVP Creation Rules"
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

> **📋 Document Role**: This is a **CREATION HELPER** for EARS-MVP-TEMPLATE.md (default).
> - **Authority**: `EARS-MVP-TEMPLATE.md` is the primary standard for EARS structure; full template archived
> - **Schema**: `EARS_MVP_SCHEMA.yaml` defines machine-readable validation rules
> - **Validation**: Use `EARS_MVP_VALIDATION_RULES.md` or `03_EARS/scripts/validate_ears.py`

# EARS Creation Rules

## Template Selection (MVP Default)

**MVP templates are the framework default.**

| Template | File | When to Use |
|----------|------|-------------|
| **MVP (DEFAULT)** | `EARS-MVP-TEMPLATE.md` | All EARS |

## Index-Only Generation Workflow

- Maintain `EARS-00_index.md` as the authoritative source of planned and active EARS documents (mark planned items with Status: Planned).
- Generators use: `EARS-00_index.md` + selected template profile (MVP by default; full when explicitly requested in settings or prompt).

> Path conventions: Examples below use a portable `docs/` root for new projects. In this repository, artifact folders live at the ai_dev_flow root (no `docs/` prefix). When running commands here, drop the `docs/` prefix. See README → "Using This Repo" for path mapping.

**Version**: 1.1
**Date**: 2025-11-19
**Last Updated**: 2025-11-30
**Source**: Extracted from EARS-MVP-TEMPLATE.md, PRD requirements, and behavioral specification patterns (full template archived)
**Purpose**: Complete reference for creating EARS files according to doc-flow SDD framework
**Changes**: Merged EARS_STYLE_GUIDE.md content - added Status/BDD-Score mapping, code block formatting, traceability format details, and extended common mistakes table

---

## Do Not (Guardrails)

- Do not reference numeric downstream artifacts (no `BDD-##`, `ADR-##`, `REQ-##`, `SPEC-##`, or `SYS-##`). Use generic names: `BDD`, `ADR`, `REQ`, `SPEC`, `SYS` until those artifacts exist.
- In the Document Control table, “Source Document” must contain exactly one canonical `@prd: PRD.NN.EE.SS` value. Do not include ranges (e.g., `@prd: ... - @prd: ...`) or multiple `@prd` values. List additional IDs in an “Upstream Sources” subsection or within per-requirement traceability.
- Keep `architecture_approaches` as an array using allowed values: `[ai-agent-based]`, `[traditional-8layer]`, or `[ai-agent-based, traditional-8layer]`. Do not use `ai-agent-primary` in this field.

## Table of Contents

1. [File Organization and Directory Structure](#1-file-organization-and-directory-structure)
2. [Document Structure (Required sections)](#2-document-structure-required-sections)
3. [Document Control Requirements](#3-document-control-requirements)
4. [ID and Naming Standards](#4-id-and-naming-standards)
5. [EARS Syntax Patterns](#5-ears-syntax-patterns)
6. [Quality Attributes](#6-quality-attributes)
7. [BDD Relationship Guidelines](#7-bdd-relationship-guidelines)
8. [BDD-Ready Scoring System](#8-bdd-ready-scoring-system)
9. [Traceability Requirements](#9-traceability-requirements)
10. [Precision and Measurability](#10-precision-and-measurability)
11. [Quality Gates](#11-quality-gates)
12. [Additional Requirements](#12-additional-requirements)

---

## 1. File Organization and Directory Structure

- Note: Some examples in this document show a portable `docs/` root. In this repository, artifact folders live at the ai_dev_flow root without the `docs/` prefix; see README → “Using This Repo” for path mapping.
- **Location**: `docs/03_EARS/` within project docs directory
- **Naming**: `EARS-NN_descriptive_title.md` (NN = 2-digit minimum, expand when needed)
- **Subdocuments**: For complex systems: `EARS-NN-YY_additional_detail.md`

---

## 2. Document Structure (Required sections)

EARS documents require specific structural elements for behavioral specification:

#### Required sections:
1. **Document Control** - Metadata with BDD-Ready Score
2. **Purpose and Context** - Business and technical objectives
3. **Requirements** - Event-Driven, State-Driven, Unwanted Behavior, Ubiquitous
4. **Quality Attributes** - Performance, security, Reliability, etc.
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

- **Filename**: `EARS-NN_descriptive_title.md`
- **H1**: `# EARS-NN: [Short Descriptive Title]`
- **Statement IDs**: `EARS.{DocNum}.25.{Seq}` format (e.g., `EARS.06.25.01`, `EARS.06.25.02`)
  - Unified Element ID format: TYPE.NN.TT.SS (DOC_NUM.ELEM_TYPE.SEQ)
  - Element type 25 = EARS Statement
  - Sequential numbering within document (01, 02, 03...)

### 4.1 Element ID Format (MANDATORY)

**Pattern**: `EARS.{DOC_NUM}.{ELEM_TYPE}.{SEQ}` (4 segments, dot-separated)

| Element Type | Code | Example |
|--------------|------|---------|
| EARS Statement | 25 | EARS.02.25.01 |

> ⚠️ **REMOVED PATTERNS** - Do NOT use:
> - Category prefixes: `E-XXX`, `S-XXX`, `U-XXX`, `UB-XXX`, `EVENT-XXX`, `STATE-XXX`, `UNWANTED-XXX`, `UBIQ-XXX`
> - 3-segment format: `EARS.NN.EE`
>
> **Reference**: [ID_NAMING_STANDARDS.md — Cross-Reference Link Format](../ID_NAMING_STANDARDS.md#cross-reference-link-format-mandatory)

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
**EARS.01.25.01: Requirement Name**
```
WHEN [condition],
THE [component] SHALL [action]
WITHIN [constraint].
```
**Traceability**: @brd: BRD.01.01.01 | @prd: PRD.01.07.01
````

---

## 6. Quality Attributes

### Quality Attribute Format

EARS documents use unified sequential numbering for all requirements including quality attributes:

| Category | Keywords for Detection |
|----------|------------------------|
| Performance | latency, throughput, response time, p95, p99 |
| Reliability | availability, MTBF, MTTR, fault tolerance, recovery |
| Scalability | concurrent users, data volumes, horizontal scaling |
| Security | authentication, authorization, encryption, RBAC |
| Observability | logging, monitoring, tracing, alerting, metrics |
| Maintainability | code coverage, deployment, CI/CD, documentation |

### Quality Attribute Inheritance

When formalizing quality attributes from 01_BRD/PRD:
- **Use sequential numbering**: All requirements numbered sequentially (01, 02, 03...)
- **Add EARS formalization**: Apply WHEN-THE-SHALL-WITHIN syntax
- **Maintain traceability**: `@brd: BRD.17.01.15`

### Quality Attribute Categories

**Performance**: Quantified latency, throughput, response time constraints
**Security**: Authentication, authorization, encryption standards
**Reliability**: Availability SLAs, fault tolerance, recovery objectives
**Scalability**: Concurrent users, data volumes, growth projections
**Observability**: Logging, monitoring, tracing, alerting requirements
**Maintainability**: Code coverage, deployment, documentation standards

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

**Quality Attribute Completeness (15%)**:
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

### Standard Format

```markdown
**Traceability**: @brd: BRD.NN.01.SS | @prd: PRD.NN.EE.SS | @threshold: PRD.035.category.key
```

### Required Tags

| Tag | Format | When Required |
|-----|--------|---------------|
| @brd | BRD.NN.01.SS | Always |
| @prd | PRD.NN.EE.SS | Always |
| @threshold | PRD.035.category.key | When referencing timing/limits |
| @entity | PRD.004.EntityName | When referencing data entities |
| @ctr | CTR-NN | When referencing API contracts |

### Do NOT Use

- Block quote format: `> **Tags**:`
- Comma separators: `@prd: ..., @threshold: ...`
- Trailing commas: `@prd: PRD.19.07.02, |`

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

**Framework Compliance**: 100% AI Dev Flow SDD framework (Layer 3)
**Integration**: Enforces EARS → BDD progression quality gates


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
| @brd | Yes/No | BRD-NN or null | Reference/Create/Skip |
| @prd | Yes/No | PRD-NN or null | Reference/Create/Skip |
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
| Related | EARS-NN | [Related EARS title] | Shared domain context |
| Depends | EARS-NN | [Prerequisite EARS title] | Must complete before this |

**Tags**:
```markdown
@related-ears: EARS-NN
@depends-ears: EARS-NN
```

---

## 14. Batch Creation Checkpoint Rules

When creating multiple EARS documents in a session, follow these checkpoint rules to prevent inconsistencies:

### Pre-Batch Verification

**Before starting batch creation:**
1. Read `EARS_MVP_SCHEMA.yaml` to understand current metadata requirements
2. Verify tag standards: `ears` (not `ears-requirements`, `ears-formal-requirements`, etc.)
3. Verify document_type: `ears` (not `engineering-requirements`)
4. Verify architecture format: `architecture_approaches: [value]` (array, not singular)

### Every 5-Document Checkpoint

**After creating every 5 EARS documents:**
1. Run validation: `python 03_EARS/scripts/validate_ears.py --path docs/EARS`
2. Check for:
   - Tag consistency (all use `ears`)
   - document_type consistency (all use `ears`)
   - Source Document format (`@prd: PRD.NN.EE.SS`)
   - Section numbering (sequential)
3. Fix any errors before continuing

### End-of-Session Validation

**Before ending session:**
1. Run full validation: `python 03_EARS/scripts/validate_ears.py`
2. Verify 0 errors (warnings acceptable)
3. Update EARS-00_index.md if document counts changed
4. Document any issues in session notes

### Common Batch Errors to Avoid

| Error Pattern | Correct Format |
|---------------|----------------|
| `ears-requirements` | `ears` |
| `ears-formal-requirements` | `ears` |
| `ears-NN` | `ears` |
| `document_type: engineering-requirements` | `document_type: ears` |
| `architecture_approach: value` | `architecture_approaches: [value]` |
| `Source Document: PRD-NN` | `Source Document: @prd: PRD.NN.EE.SS` |
| `> **Tags**: @prd: ...` | `**Traceability**: @prd: ...` |
| `@prd: PRD.01.07.01, @threshold: ...` | `@prd: PRD.01.07.01 \| @threshold: ...` |
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

## 15. Cross-Document Validation (MANDATORY)

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
python scripts/validate_cross_document.py --document docs/03_EARS/EARS-NN_slug.md --auto-fix

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

**Blocking**: YES - Cannot proceed to BDD creation until Phase 1 validation passes with 0 errors.

---

## 16. Requirement Counting and total_requirements Field

### Overview

The `total_requirements` field in EARS index documents (EARS-00_index.md) tracks the aggregate count of EARS statements across all EARS documents in a project.

### What Counts as a Requirement

Each unique EARS statement ID counts as one requirement:

| Element | Counts As | Example |
|---------|-----------|---------|
| `EARS.NN.25.SS` statement | 1 requirement | `EARS.04.25.001` = 1 |
| Duplicate mapping to objectives | Count once | Same ID mapped to 3 objectives = 1 |
| Requirement in multiple sections | Count once | Same ID in overview + detail = 1 |

### Calculation Rules

1. **Per-Document Count**: Count unique `EARS.NN.25.SS` IDs in each EARS-NN document
2. **Index Total**: Sum of all individual document counts
3. **Business Objectives Mapping**: Requirements mapped to multiple objectives count ONCE (by unique ID)
4. **Deprecated Requirements**: Do NOT count deprecated/removed requirements

### Index Document Format

```markdown
## Document Statistics

| Document | Requirements | Status |
|----------|-------------|--------|
| EARS-01 | 45 | Approved |
| EARS-02 | 38 | Approved |
| EARS-03 | 52 | In Review |
| **Total** | **135** | - |
```

### Clarifying Notes

Add clarifying notes when counts require explanation:

```markdown
**Note**: Some requirements are mapped to multiple business objectives in Section 6.
The total counts each requirement once by unique EARS ID, not by mapping.
```

### Validation

Run `python 03_EARS/scripts/validate_ears.py --check-counts` to verify:
- Individual document counts match actual EARS statement count
- Index total equals sum of individual counts
- No duplicate EARS IDs across documents

---

## 17. Adding New Requirement Categories

### When to Create a New Category

Create a new EARS document (not category prefix) when:

1. **Domain boundary**: New functional area not covered by existing documents
2. **Scale threshold**: Existing document exceeds 100 requirements
3. **Ownership change**: Different team/stakeholder owns requirements
4. **Lifecycle difference**: Requirements have different approval/release cycles

### Process for Adding New EARS Documents

**Step 1: Reserve Document Number**

```bash
# Check existing EARS documents
ls -la docs/03_EARS/EARS-*.md | tail -5

# Reserve next sequential number
# If last is EARS-19, next is EARS-20
```

**Step 2: Create Document from Template**

```bash
cp docs/03_EARS/EARS-MVP-TEMPLATE.md docs/03_EARS/EARS-20_new_category_name.md
```

**Step 3: Update Schema (if new element types needed)**

If the new category introduces new element types beyond `EARS.NN.25.SS`:

1. Document in `EARS_MVP_SCHEMA.yaml` under `element_types`
2. Add validation rules to `03_EARS/scripts/validate_ears.py`
3. Update `ID_NAMING_STANDARDS.md` element type table

**Step 4: Update Index Document**

Add entry to `EARS-00_index.md`:

```markdown
| EARS-20 | [New Category Name] | 0 | Draft | [link] |
```

**Step 5: Notify Downstream Consumers**

Downstream artifacts may need updates:

| Artifact | Action Required |
|----------|-----------------|
| BDD | May need new feature files |
| ADR | May need architectural decisions |
| REQ | May derive atomic requirements |
| SPEC | May need technical specifications |

### Category Naming Guidelines

| Good Names | Avoid |
|------------|-------|
| `EARS-20_mcp_tool_requirements` | `EARS-20_misc` |
| `EARS-21_authentication_flows` | `EARS-21_new_stuff` |
| `EARS-22_data_pipeline_events` | `EARS-22_category_a` |

### Validation After Adding

```bash
# Validate new document
python 03_EARS/scripts/validate_ears.py --document docs/03_EARS/EARS-20_new_category.md

# Validate index counts
python 03_EARS/scripts/validate_ears.py --check-counts

# Validate cross-document consistency
python scripts/validate_cross_document.py --layer EARS
```
