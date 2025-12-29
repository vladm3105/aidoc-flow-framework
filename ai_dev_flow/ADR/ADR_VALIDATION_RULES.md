# =============================================================================
# 📋 Document Role: This is a DERIVATIVE of ADR-TEMPLATE.md
# - Authority: ADR-TEMPLATE.md is the single source of truth for ADR structure
# - Purpose: AI checklist after document creation (derived from template)
# - Scope: Includes all rules from ADR_CREATION_RULES.md plus validation extensions
# - On conflict: Defer to ADR-TEMPLATE.md
# =============================================================================
---
title: "ADR Validation Rules Reference"
tags:
  - validation-rules
  - layer-5-artifact
  - shared-architecture
custom_fields:
  document_type: validation-rules
  artifact_type: ADR
  layer: 5
  priority: shared
  development_status: active
---

> **📋 Document Role**: This is the **POST-CREATION VALIDATOR** for ADR documents.
> - Apply these rules after ADR creation or modification
> - **Authority**: Validates compliance with `ADR-TEMPLATE.md` (the primary standard)
> - **Scope**: Use for quality gates before committing ADR changes

# ADR Validation Rules Reference

**Version**: 1.1.0
**Date**: 2025-11-19
**Last Updated**: 2025-12-12
**Purpose**: Complete validation rules for ADR documents
**Script**: `python scripts/validate_adr.py`
**Primary Template**: `ADR-TEMPLATE.md`
**Framework**: AI Dev Flow SDD (100% compliant)
**Changes**: Added ADR-REF as second document category with reduced validation; Updated CHECK 3 and CHECK 4 for reference documents

---

## Table of Contents

1. [Overview](#overview)
2. [Validation Checks](#validation-checks)
3. [Error Fix Guide](#error-fix-guide)
4. [Quick Reference](#quick-reference)
5. [Common Mistakes](#common-mistakes)

---

## Overview

Note: Some examples in this guide show a portable `docs/` root. In this repository, artifact folders live at the ai_dev_flow root without the `docs/` prefix; see README → “Using This Repo” for path mapping.

The ADR validation script ensures architecture decisions follow quality standards for SYS progression and meet SDD quality gates.

### ADR Document Categories

| Category | Filename Pattern | Validation Level | Description |
|----------|------------------|------------------|-------------|
| **Standard ADR** | `ADR-NN_{decision_topic}.md` | Full (7 checks) | Architecture decision records |
| **ADR-REF** | `ADR-REF-NN_{slug}.md` | Reduced (4 checks) | Supplementary reference documents |

### ADR-REF Reduced Validation

**Purpose**: ADR-REF documents are reference targets that other documents link to. They provide supporting information, context, or external references in free format with business-oriented descriptions. They do not define formal architecture decisions.

**Applicable Checks** (4 total):
- CHECK 1 (partial): Document Control Fields (required)
- Document Revision History (required)
- Status/Context sections only (required)
- H1 ID match with filename (required)

**Exempted Checks** (NO SCORES):
- SYS-Ready Score: NOT APPLICABLE (REF documents use free format, no scores)
- CHECK 4: Cumulative traceability tags NOT REQUIRED (@brd, @prd, @ears, @bdd)
- CHECK 5-7: Decision quality, architecture documentation, implementation readiness (exempt)
- All quality gates and downstream readiness metrics: EXEMPT

**Reference**: See `REF-TEMPLATE.md` for ADR-REF document structure and requirements.

### Validation Tiers

| Tier | Type | Exit Code | Description |
|------|------|-----------|-------------|
| **Tier 1** | Errors | 1 | Blocking issues - must fix before commit |
| **Tier 2** | Warnings | 0 | Quality issues - recommended to fix |
| **Tier 3** | Info | 0 | Informational - no action required |

### Reserved ID Exemption (ADR-000_*)

**Scope**: Documents with reserved ID `000` are FULLY EXEMPT from validation.

**Pattern**: `ADR-000_*.md`

**Document Types**:
- Index documents (`ADR-000_index.md`)
- Traceability matrix templates (`ADR-000_TRACEABILITY_MATRIX-TEMPLATE.md`)
- Glossaries, registries, checklists

**Rationale**: Reserved ID 000 documents are framework infrastructure (indexes, templates, reference materials), not project artifacts requiring traceability or quality gates.

**Validation Behavior**: Skip all checks when filename matches `ADR-000_*` pattern.

---

## Validation Checks

### CHECK 1: Required Document Control Fields

**Type**: Error (blocking)

**Required Fields**:
- Project Name, Document Version, Date, Document Owner, Prepared By, Status, SYS-Ready Score

### CHECK 2: ADR Structure Completeness

**Type**: Error (blocking)

**Required sections**: Status, Context, Decision, Consequences, Architecture Flow, Alternatives Considered

### CHECK 3: SYS-Ready Score Validation ⭐ NEW

**Purpose**: Validate SYS-ready score format and threshold
**Type**: Error (blocking) - Standard ADR only

**Valid Examples**: `✅ 95% (Target: ≥90%)`

**Error Message**: `❌ MISSING: SYS-Ready Score with ✅ emoji and percentage`

**ADR-REF Exemption**: ADR-REF documents are EXEMPT from SYS-Ready Score requirements. Reference documents use free format with no scores.

**Info Message** (for ADR-REF):
```
ℹ️  INFO: ADR-REF document detected - SYS-Ready Score NOT REQUIRED
         REF documents use free format with no downstream quality gates
```

### CHECK 4: Upstream Traceability Tags

**Purpose**: Verify complete tag chain through BDD layer
**Type**: Error (blocking) - Standard ADR only

**Required Tags** (Standard ADR):
```markdown
@brd: BRD.NN.EE.SS
@prd: PRD.NN.EE.SS
@ears: EARS.NN.EE.SS
@bdd: BDD.NN.EE.SS
```

**ADR-REF Exemption**: ADR-REF documents are EXEMPT from cumulative traceability tag requirements. Reference documents serve as citation targets for other documents.

**Info Message** (for ADR-REF):
```
ℹ️  INFO: ADR-REF document detected - applying reduced validation
         Checks 3-7 exempt for reference documents
         Validating: Document Control, Revision History, Status/Context, H1 ID match
```

### CHECK 5: Decision Quality Assessment

**Purpose**: Ensure decision rationale is comprehensive
**Type**: Warning

**Requirements**:
- Context clearly establishes the problem
- Decision explains chosen solution
- Consequences cover positive and negative outcomes
- Alternatives considered with rejection rationale

### CHECK 6: Architecture Documentation

**Purpose**: Verify technical architecture is well-defined
**Type**: Warning

**Requirements**:
- Architecture flow includes Mermaid diagram
- Component responsibilities specified
- Impact analysis covers affected systems

### CHECK 7: Implementation Readiness

**Purpose**: Assess practical implementability
**Type**: Warning

**Requirements**:
- Complexity assessment provided
- Resource estimates documented
- Migration and rollback strategies included

---

### CHECK 8: Element ID Format Compliance ⭐ NEW

**Purpose**: Verify element IDs use unified 4-segment format, flag removed patterns.
**Type**: Error

| Check | Pattern | Result |
|-------|---------|--------|
| Valid format | `### ADR.NN.TT.SS:` | ✅ Pass |
| Removed pattern | `### DEC-XXX` | ❌ Fail - use ADR.NN.10.SS |
| Removed pattern | `### ALT-XXX` | ❌ Fail - use ADR.NN.12.SS |
| Removed pattern | `### CON-XXX` | ❌ Fail - use ADR.NN.13.SS |

**Regex**: `^###\s+ADR\.[0-9]{2,}\.[0-9]{2,}\.[0-9]{2,}:\s+.+$`

**Common Element Types for ADR**:
| Element Type | Code | Example |
|--------------|------|---------|
| Decision | 10 | ADR.02.10.01 |
| Alternative | 12 | ADR.02.12.01 |
| Consequence | 13 | ADR.02.13.01 |

**Fix**: Replace `### DEC-01: Decision` with `### ADR.02.10.01: Decision`

**Reference**: ADR_CREATION_RULES.md Section 4.1, ID_NAMING_STANDARDS.md lines 783-793

---

## Error Fix Guide

### Quick Fix Matrix

| Error Check | Quick Fix |
|-------------|-----------|
| **CHECK 1** | Add missing Document Control fields |
| **CHECK 2** | Add required ADR structure sections (Standard ADR only) |
| **CHECK 3** | Add properly formatted SYS-Ready Score (Standard ADR only; ADR-REF exempt) |
| **CHECK 4** | Complete traceability tag chain (Standard ADR only; ADR-REF exempt) |
| **CHECK 8** | Replace legacy element IDs (DEC-XXX, ALT-XXX, CON-XXX) with unified format `ADR.NN.TT.SS` |

**ADR-REF Quick Fix**:
- Ensure filename matches `ADR-REF-NN_{slug}.md` pattern
- Add Document Control fields (Project Name, Version, Date, Owner, Prepared By, Status)
- Add Document Revision History table
- Add Status and Context sections
- Verify H1 ID matches filename

---

## Quick Reference

### Pre-Commit Validation

```bash
# Validate single ADR document (nested folder structure)
python scripts/validate_adr.py docs/ADR/ADR-01_architecture_decision/ADR-01.0_architecture_decision_index.md

# Validate all ADR files (section-based structure)
find docs/ADR -type f -name "ADR-*.md" -exec python scripts/validate_adr.py {} \;

# Validate monolithic ADR (optional for <25KB)
python scripts/validate_adr.py docs/ADR/ADR-01_architecture_decision.md
```

### SYS-Ready Scoring Criteria ⭐ NEW

**Decision Completeness (30%)**:
- Complete decision process (Context/Decision/Consequences/Alternatives): 15%
- Requirements mapping and traceability: 10%
- Impact analysis (positive/negative consequences): 5%

**Architecture Clarity (35%)**:
- Architecture flow with Mermaid diagrams: 15%
- Component responsibilities defined: 10%
- Cross-cutting concerns addressed: 10%

**Implementation Readiness (20%)**:
- Complexity and resource estimates: 10%
- Dependencies identified: 5%
- Rollback/migration strategies: 5%

**Verification Approach (15%)**:
- Testing strategy alignment: 5%
- Success metrics and validation criteria: 5%
- Operational readiness assessment: 5%

### Validation Tiers Summary

| Tier | Type | Checks | Action |
|------|------|--------|--------|
| **Tier 1** | Error | 1-4 | Must fix before commit |
| **Tier 2** | Warning | 5-7 | Recommended to fix |
| **Tier 3** | Info | - | No action required |

---

## Diagram Standards

All diagrams MUST use Mermaid syntax. Text-based diagrams (ASCII art, box drawings) are prohibited. Directory tree structures (`├── └── │`) are exempted.

**Central Authority**: `ai_dev_flow/DIAGRAM_STANDARDS.md`
**Diagram Skill**: `mermaid-gen` skill

---

## Common Mistakes

### Mistake #1: Incomplete Decision Process
```
❌ Missing alternatives considered section
✅ Document evaluated alternatives with rejection rationale
```

### Mistake #2: Vague Architecture Documentation
```
❌ "Use microservices architecture"
✅ "Use event-driven microservices with CQRS pattern for order processing, deployed on Kubernetes with Istio service mesh"
```

### Mistake #3: SYS-Ready Score Format
```
❌ SYS-Ready Score: 95%
✅ SYS-Ready Score: ✅ 95% (Target: ≥90%)
```

### Mistake #4: Missing Traceability Tags
```
❌ @brd: BRD-01
✅ @brd: BRD.01.01.30, BRD.01.01.06
```

---

**Maintained By**: Architecture Team, Quality Assurance Team
**Review Frequency**: Updated with ADR template enhancements
