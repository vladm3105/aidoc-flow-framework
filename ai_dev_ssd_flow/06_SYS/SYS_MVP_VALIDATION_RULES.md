---
title: "SYS MVP Validation Rules"
tags:
  - validation-rules
  - layer-6-artifact
  - shared-architecture
custom_fields:
  document_type: validation-rules
  artifact_type: SYS
  layer: 6
  priority: shared
  development_status: active
---

# =============================================================================
#  Document Role: Validates SYS-MVP-TEMPLATE.md (default)
# - Authority: SYS-MVP-TEMPLATE.md is the standard for SYS structure (MVP → PROD → NEW MVP lifecycle)
# - Purpose: AI checklist after document creation (derived from MVP template)
# - Scope: Includes all rules from SYS_CREATION_RULES.md plus validation extensions
# - On conflict: Defer to SYS-MVP-TEMPLATE.md
# =============================================================================

** Document Role**: This is the **POST-CREATION VALIDATOR** for SYS documents.
 Apply these rules after SYS creation or modification
 **Authority**: Validates compliance with `SYS-MVP-TEMPLATE.md` (standard template)
 **Scope**: Use for quality gates before committing SYS changes

# SYS Validation Rules Reference

## MVP Validation Profile (DEFAULT)

**MVP validation is the framework default.** Full validation is applied only when explicitly triggered or when using enterprise profile.

### MVP Detection

| Detection Method | Pattern | Result |
|------------------|---------|--------|
| Filename | `*-MVP-*.md` | MVP profile |
| Frontmatter | `template_profile: mvp` | MVP profile |
| Default (no markers) | — | MVP profile |
| Frontmatter | `template_profile: full` or `enterprise` | Full profile |

### Validation Differences

| Check Category | MVP Profile | Full Profile |
|----------------|-------------|--------------|
| Document Control fields | Error | Error |
| ADR compliance validation | Error | Error |
| Traceability tags (@brd, @prd, etc.) | Error | Error |
| Quality attribute quantification | **Warning** | Error |
| REQ-Ready Score threshold | 85/100 | 90/100 |
| Interface specifications depth | **Warning** | Error |

### Usage

```bash
# MVP validation (default)
python3 ai_dev_flow/06_SYS/scripts/validate_sys.py --path ai_dev_flow/06_SYS --profile mvp

# Full validation (explicit)
python3 ai_dev_flow/06_SYS/scripts/validate_sys.py --path ai_dev_flow/06_SYS --profile full
```

### Cross-Linking Tags (AI-Friendly)

Use same-layer cross-links to document SYS relationships:
- `@depends: SYS-NN` — hard prerequisite SYS documents that must be satisfied first.
- `@discoverability: SYS-NN (short rationale); SYS-NN (short rationale)` — related SYS documents with brief reasons to aid AI search and ranking.

Validation handling: Info-level (non-blocking). Reported for visibility only.



Path conventions: Examples below use a portable `docs/` root for new projects. In this repository, artifact folders live at the ai_dev_flow root (no `docs/` prefix). When running commands here, drop the `docs/` prefix. See README → "Using This Repo" for path mapping.

**Version**: 1.1
**Date**: 2025-11-19T00:00:00
**Last Updated**: 2026-01-19T00:00:00
**Purpose**: Complete validation rules for SYS documents
**Script**: `python 06_SYS/scripts/validate_sys.py`
**Primary Template**: `SYS-MVP-TEMPLATE.md` (standard template)
**Framework**: AI Dev Flow SDD (100% compliant)
**Changes**: Added deployment requirements validation (CHECK 10), architectural correction from REQ to SYS layer

---

## Table of Contents

1. [Overview](#overview)
2. [Validation Checks](#validation-checks)
3. [Error Fix Guide](#error-fix-guide)
4. [Quick Reference](#quick-reference)
5. [Common Mistakes](#common-mistakes)

---

## Overview

Note: Some examples in this document show a portable `docs/` root. In this repository, artifact folders live at the ai_dev_flow root without the `docs/` prefix; see README → “Using This Repo” for path mapping.

The SYS validation script ensures system requirements meet quality standards for REQ progression and implement ADR architectural decisions.

### Validation Tiers

| Tier | Type | Exit Code | Description |
|------|------|-----------|-------------|
| **Tier 1** | Errors | 1 | Blocking issues - must fix before commit |
| **Tier 2** | Warnings | 0 | Quality issues - recommended to fix |
| **Tier 3** | Info | 0 | Informational - no action required |

### Reserved ID Exemption (SYS-00_*)

**Scope**: Documents with reserved ID `000` are FULLY EXEMPT from validation.

**Pattern**: `SYS-00_*.md`

**Document Types**:
- Index documents (`SYS-00_index.md`)
- Traceability matrix templates (`SYS-00_TRACEABILITY_MATRIX-TEMPLATE.md`)
- Glossaries, registries, checklists

**Rationale**: Reserved ID 000 documents are framework infrastructure (indexes, templates, reference materials), not project artifacts requiring traceability or quality gates.

**Validation Behavior**: Skip all checks when filename matches `SYS-00_*` pattern.

---

## Validation Checks

### CHECK 1: Required Document Control Fields

**Type**: Error (blocking)

**Required Fields**:
- Status, Version, Date Created/Last Updated, Author, Reviewers, Owner, Priority
- REQ-Ready Score

### CHECK 2: ADR Compliance Validation

**Purpose**: Ensure SYS requirements are implementable within ADR architectural boundaries
**Type**: Error (blocking)

**Required Sections (MVP Template - 15 Sections)**:

| Section | Title | Required |
|---------|-------|----------|
| 1 | Document Control | MANDATORY |
| 2 | Executive Summary | MANDATORY |
| 3 | Scope | MANDATORY |
| 4 | Functional Requirements | MANDATORY |
| 5 | Quality Attributes | MANDATORY |
| 6 | Interface Specifications | MANDATORY |
| 7 | Data Management Requirements | MANDATORY |
| 8 | Testing and Validation Requirements | MANDATORY |
| 9 | Deployment and Operations Requirements | MANDATORY |
| 10 | Compliance and Regulatory Requirements | MANDATORY |
| 11 | Acceptance Criteria | MANDATORY |
| 12 | Risk Assessment | MANDATORY |
| 13 | Traceability | MANDATORY |
| 14 | Implementation Notes | MANDATORY |
| 15 | Change History | MANDATORY |

**Requirements**:
- Technology selections match ADR decisions
- Architectural patterns align with ADR specifications
- Performance targets meet ADR scalability requirements

### CHECK 3: REQ-Ready Score Validation  NEW

**Purpose**: Validate REQ-ready score format and threshold
**Type**: Error (blocking)

**Valid Examples**: `[PASS] 95% (Target: ≥90%)`

**Error Message**: `[FAIL] MISSING: REQ-Ready Score with [PASS] emoji and percentage`

### CHECK 4: Quality Attribute Quantification

**Purpose**: Verify all quality attributes are measurable
**Type**: Error (blocking)

**Requirements**:
- Performance quality attributes include percentiles and thresholds
- Reliability quality attributes specify uptime/SLA targets
- Security/compliance quality attributes reference specific standards

### CHECK 5: System Boundaries

**Purpose**: Validate system boundaries prevent requirement bleed
**Type**: Warning

**Requirements**:
- Included capabilities clearly defined
- Excluded capabilities explicitly documented
- Acceptance/failure scopes specified

### CHECK 6: Interface Specifications

**Purpose**: Ensure interface contracts are CTR-ready
**Type**: Warning

**Requirements**:
- External APIs defined with contract details
- Internal interfaces specified with data formats
- Data exchange protocols documented

### CHECK 7: Upstream Traceability

**Purpose**: Verify complete traceability to requirements source
**Type**: Warning

**Required Tags**:
```markdown
@brd: BRD.NN.EE.SS
@prd: PRD.NN.EE.SS
@ears: EARS.NN.EE.SS
@bdd: BDD.NN.EE.SS
@adr: ADR-NN
```

---

### CHECK 8: Universal Splitting Trigger (Size/Cardinality)  NEW
**Purpose**: Enforce Nested Directory Pattern when triggers are met.
**Type**: Error (blocking)

**Triggers**:
1. **Size**: File > 20,000 tokens.
2. **Cardinality**: More than 1 file for this ID.

**Action**: Move to `06_SYS/SYS-{PRD_ID}_{Slug}/` folder.

**Error Message**: `[FAIL] ERROR: SYS-NN triggers nested folder rule (>20,000 tokens or >1 file). Move to 06_SYS/SYS-NN_{Slug}/`

### CHECK 9: Element ID Format Compliance  NEW


**Purpose**: Verify element IDs use unified 4-segment format, flag removed patterns.
**Type**: Error

| Check | Pattern | Result |
|-------|---------|--------|
| Valid format | `### SYS.NN.TT.SS:` | [PASS] Pass |
| Removed pattern | `### FR-XXX` | [FAIL] Fail - use SYS.NN.01.SS |
| Removed pattern | `### QA-XXX` | [FAIL] Fail - use SYS.NN.02.SS |
| Removed pattern | `### UC-XXX` | [FAIL] Fail - use SYS.NN.11.SS |
| Removed pattern | `### SR-XXX` | [FAIL] Fail - use SYS.NN.26.SS |

**Regex**: `^###\s+SYS\.[0-9]{2,}\.[0-9]{2,}\.[0-9]{2,}:\s+.+$`

**Common Element Types for SYS**:
| Element Type | Code | Example |
|--------------|------|---------|
| Functional Requirement | 01 | SYS.02.01.01 |
| Quality Attribute | 02 | SYS.02.02.01 |
| Risk | 07 | SYS.02.07.01 |
| Use Case | 11 | SYS.02.11.01 |
| System Requirement | 26 | SYS.02.26.01 |

**Fix**: Replace `### SR-01: System Requirement` with `### SYS.02.26.01: System Requirement`

**Reference**: SYS_CREATION_RULES.md Section 4.1, [ID_NAMING_STANDARDS.md — Cross-Reference Link Format](../ID_NAMING_STANDARDS.md#cross-reference-link-format-mandatory)

---

### CHECK 10: Deployment Requirements Completeness  NEW

**Purpose**: Verify Section 9.1 Deployment Requirements includes all required subsections with either details or appropriate NA markings.
**Type**: Warning

**Required Subsections** (9.1.1-9.1.8):
- Infrastructure Requirements
- Environment Configuration
- Deployment Scripts Requirements
- Ansible Playbook Requirements
- Observability Requirements
- Security Requirements
- Cost Constraints
- Deployment Automation Requirements

**Validation Options**:
1. All 8 subsections present with detailed tables → PASS
2. All 8 subsections present with "Not Applicable" + rationale → PASS
3. Mixed case (some Required with details, some NA with rationale) → PASS
4. Missing subsections → FAIL
5. Empty subsections without "Not Applicable" marker → FAIL

**Validation Requirements**:
1. All 8 subsection headings must be present
2. Each subsection must have "Applicability" marker (Required | Not Applicable)
3. If marked "Not Applicable", must include rationale
4. Accept detailed tables OR "Not Applicable" + brief rationale
5. No minimum length requirement for rationale, but must be present

**Architectural Principle**: Deployment infrastructure is a **system-level concern**, not an atomic requirement. When no infrastructure changes are needed, mark subsections as NA rather than omitting them.

**Error Messages**:
- Missing: `[FAIL] ERROR: Section 9.1 missing subsection [9.1.x]`
- Empty without NA: `[WARN] WARNING: Subsection [9.1.x] present but empty. Mark as NA with rationale or provide details.`
- NA without rationale: `[WARN] WARNING: Subsection [9.1.x] marked Not Applicable but missing rationale. AI requires rationale for assistance.`

---

### CHECK 11: Operational Requirements Completeness  NEW

**Purpose**: Verify Section 9.2 Operational Requirements includes all required subsections with either details or appropriate NA markings.
**Type**: Warning

**Required Subsections** (9.2.1-9.2.3):
- Monitoring and Alerting
- Backup and Recovery
- Maintenance Procedures

**Validation Options**:
1. All 3 subsections present with details → PASS
2. All 3 subsections present with "Not Applicable" + rationale → PASS
3. Mixed case (some Required with details, some NA with rationale) → PASS
4. Missing subsections → FAIL
5. Empty subsections without "Not Applicable" marker → FAIL

**Validation Requirements**:
1. All 3 subsection headings must be present
2. Each subsection must have "Applicability" marker (Required | Not Applicable)
3. If marked "Not Applicable", must include rationale
4. Accept detailed requirements OR "Not Applicable" + brief rationale
5. No minimum length requirement for rationale, but must be present

**Architectural Principle**: Operational requirements are **system-level concerns**, not atomic requirements. When no operational changes are needed, mark subsections as NA rather than omitting them.

**Error Messages**:
- Missing: `[FAIL] ERROR: Section 9.2 missing subsection [9.2.x]`
- Empty without NA: `[WARN] WARNING: Subsection [9.2.x] present but empty. Mark as NA with rationale or provide details.`
- NA without rationale: `[WARN] WARNING: Subsection [9.2.x] marked Not Applicable but missing rationale. AI requires rationale for assistance.`

---

## Error Fix Guide

### Quick Fix Matrix

| Error Check | Quick Fix |
|-------------|-----------|
| **CHECK 1** | Add missing Document Control fields |
| **CHECK 2** | Align SYS requirements with ADR decisions |
| **CHECK 3** | Add properly formatted REQ-Ready Score |
| **CHECK 4** | Quantify all quality attributes with measurable thresholds |
| **CHECK 9** | Replace legacy element IDs (FR-XXX, QA-XXX, SR-XXX) with unified format `SYS.NN.TT.SS` |
| **CHECK 10** | Add missing Section 9.1 subsections or mark as NA with rationale |
| **CHECK 11** | Add missing Section 9.2 subsections or mark as NA with rationale |

---

## Quick Reference

### Pre-Commit Validation

```bash
# Validate single SYS document
python 06_SYS/scripts/validate_sys.py docs/06_SYS/SYS-01_system_requirements.md

# Validate all SYS files
find docs/SYS -name "SYS-*.md" -exec python 06_SYS/scripts/validate_sys.py {} \;
```

### REQ-Ready Scoring Criteria  NEW

**Requirements Decomposition Clarity (35%)**:
- System boundaries with acceptance/failure scopes: 15%
- Functional requirements broken to implementable capabilities: 10%
- Dependencies and prerequisites identified: 5%
- ADR architectural alignment: 5%

**Quality Attribute Quantification (30%)**:
- Performance with percentiles and thresholds: 15%
- Reliability with uptime/SLA targets: 5%
- security with compliance framework references: 5%
- Scalability quantified for growth: 5%

**Interface Specifications (20%)**:
- External API contracts (CTR-ready): 10%
- Internal module interfaces specified: 5%
- Data exchange protocols documented: 5%

**Implementation Readiness (15%)**:
- Testing requirements for all categories: 5%
- Deployment and operational requirements: 5%
- Monitoring and observability quantified: 5%

### Validation Tiers Summary

| Tier | Type | Checks | Action |
|------|------|--------|--------|
| **Tier 1** | Error | 1-4, 8-9 | Must fix before commit |
| **Tier 2** | Warning | 5-7, 10 | Recommended to fix |
| **Tier 3** | Info | - | No action required |

---

## Common Mistakes

### Mistake #1: ADR Non-Compliance
```
[FAIL] SYS specifies MongoDB when ADR selected PostgreSQL
[PASS] Align SYS technology selections with ADR decisions
```

### Mistake #2: Unquantified Quality Attributes
```
[FAIL] System shall be highly available
[PASS] System shall maintain 99.9% uptime during business hours
```

### Mistake #3: REQ-Ready Score Format
```
[FAIL] REQ-Ready Score: 95%
[PASS] REQ-Ready Score: [PASS] 95% (Target: ≥90%)
```

### Mistake #4: Incomplete Traceability
```
[FAIL] @brd: BRD-01
[PASS] @brd: BRD.01.01.30, @prd: PRD.03.01.02
```

---

**Maintained By**: Systems Architecture Team, Requirements Engineering Team
## Functional Requirements

---

## DEPRECATED: Template+Schema migration (2026-03-24)

This file is deprecated and retained for backward compatibility only.

Active references for MCP and framework tooling must use:
- `*-MVP-TEMPLATE.*`
- `*_MVP_SCHEMA.yaml`

Do not add new dependencies on this file.
