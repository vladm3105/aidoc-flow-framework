---
title: "ADR MVP Validation Rules"
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

# =============================================================================
#  Document Role: Validates ADR-MVP-TEMPLATE.md (default)
# - Authority: ADR-MVP-TEMPLATE.md is the primary standard for ADR structure
# - Purpose: AI checklist after document creation (derived from MVP template)
# - Scope: Includes all rules from ADR_MVP_CREATION_RULES.md plus validation extensions
# - On conflict: Defer to ADR-MVP-TEMPLATE.md
# =============================================================================
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

> ** Document Role**: This is the **POST-CREATION VALIDATOR** for ADR documents.
> - Apply these rules after ADR creation or modification
> - **Authority**: Validates compliance with `ADR-MVP-TEMPLATE.md` (primary standard; full template archived)
> - **Scope**: Use for quality gates before committing ADR changes

# ADR Validation Rules Reference

## MVP Validation Profile (DEFAULT)

**MVP validation is the framework default.** Full validation is applied only when explicitly triggered or when using full templates.

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
| ADR structure (Status/Context/Decision) | Error | Error |
| Traceability tags (@brd, @prd, etc.) | Error | Error |
| Extended sections (Consequences, Alternatives) | **Warning** | Error |
| SYS-Ready Score threshold | 70/100 | 90/100 |
| Architecture documentation depth | **Warning** | Error |

### Usage

```bash
# MVP validation (default)
python3 ai_dev_flow/05_ADR/scripts/validate_adr.py --path ai_dev_flow/05_ADR --profile mvp

# Full validation (explicit)
python3 ai_dev_flow/05_ADR/scripts/validate_adr.py --path ai_dev_flow/05_ADR --profile full
```
### Cross-Linking Tags (AI-Friendly)

Use same-layer cross-links to document ADR relationships:
- `@depends: ADR-NN` — hard prerequisite ADR(s) that must be satisfied first.
- `@discoverability: ADR-NN (short rationale); ADR-NN (short rationale)` — related ADRs with brief reasons to aid AI search and ranking.

Validation handling: Info-level (non-blocking). Reported for visibility only.
---

> Path conventions: Examples below use a portable `docs/` root for new projects. In this repository, artifact folders live at the ai_dev_flow root (no `docs/` prefix). When running commands here, drop the `docs/` prefix. See README → "Using This Repo" for path mapping.

**Version**: 1.1.0
**Date**: 2025-11-19T00:00:00
**Last Updated**: 2025-12-12T00:00:00
**Purpose**: Complete validation rules for ADR documents
**Script**: `python 05_ADR/scripts/validate_adr.py`
**Primary Template**: `ADR-MVP-TEMPLATE.md` (full template archived)
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

Note: Some examples in this document show a portable `docs/` root. In this repository, artifact folders live at the ai_dev_flow root without the `docs/` prefix; see README → “Using This Repo” for path mapping.

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

### Reserved ID Exemption (ADR-00_*)

**Scope**: Documents with reserved ID `000` are FULLY EXEMPT from validation.

**Pattern**: `ADR-00_*.md`

**Document Types**:
- Index documents (`ADR-00_index.md`)
- Traceability matrix templates (`ADR-00_TRACEABILITY_MATRIX-TEMPLATE.md`)
- Glossaries, registries, checklists

**Rationale**: Reserved ID 000 documents are framework infrastructure (indexes, templates, reference materials), not project artifacts requiring traceability or quality gates.

**Validation Behavior**: Skip all checks when filename matches `ADR-00_*` pattern.

---

## Validation Checks

### CHECK 1: Required Document Control Fields

**Type**: Error (blocking)

**Required Fields**:
- Project Name, Document Version, Date, Document Owner, Prepared By, Status, SYS-Ready Score

### CHECK 2: ADR Structure Completeness

**Type**: Error (blocking)

**Required sections**: Status, Context, Decision, Consequences, Architecture Flow, Alternatives Considered

### CHECK 3: SYS-Ready Score Validation  NEW

**Purpose**: Validate SYS-ready score format and threshold
**Type**: Error (blocking) - Standard ADR only

**Valid Examples**: `[PASS] 95% (Target: ≥90%)`

**Error Message**: `[FAIL] MISSING: SYS-Ready Score with [PASS] emoji and percentage`

**ADR-REF Exemption**: ADR-REF documents are EXEMPT from SYS-Ready Score requirements. Reference documents use free format with no scores.

**Info Message** (for ADR-REF):
```
ℹ  INFO: ADR-REF document detected - SYS-Ready Score NOT REQUIRED
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
ℹ  INFO: ADR-REF document detected - applying reduced validation
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

### CHECK 8: Universal Splitting Trigger (Size/Cardinality)  NEW
**Purpose**: Enforce Nested Directory Pattern when triggers are met.
**Type**: Error (blocking)

**Triggers**:
1. **Size**: File > 20,000 tokens.
2. **Cardinality**: More than 1 file for this ID.

**Action**: Move to `05_ADR/ADR-{PRD_ID}_{Slug}/` folder.

**Error Message**: `[FAIL] ERROR: ADR-NN triggers nested folder rule (>20,000 tokens or >1 file). Move to 05_ADR/ADR-NN_{Slug}/`

### CHECK 9: Element ID Format Compliance  NEW


**Purpose**: Verify element IDs use unified 4-segment format, flag removed patterns.
**Type**: Error

| Check | Pattern | Result |
|-------|---------|--------|
| Valid format | `### ADR.NN.TT.SS:` | [PASS] Pass |
| Removed pattern | `### DEC-XXX` | [FAIL] Fail - use ADR.NN.10.SS |
| Removed pattern | `### ALT-XXX` | [FAIL] Fail - use ADR.NN.12.SS |
| Removed pattern | `### CON-XXX` | [FAIL] Fail - use ADR.NN.13.SS |

**Regex**: `^###\s+ADR\.[0-9]{2,}\.[0-9]{2,}\.[0-9]{2,}:\s+.+$`

**Common Element Types for ADR**:
| Element Type | Code | Example |
|--------------|------|---------|
| Decision | 10 | ADR.02.10.01 |
| Alternative | 12 | ADR.02.12.01 |
| Consequence | 13 | ADR.02.13.01 |

**Fix**: Replace `### DEC-01: Decision` with `### ADR.02.10.01: Decision`

**Reference**: ADR_CREATION_RULES.md Section 4.1, [ID_NAMING_STANDARDS.md — Cross-Reference Link Format](../ID_NAMING_STANDARDS.md#cross-reference-link-format-mandatory)

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
python 05_ADR/scripts/validate_adr.py docs/05_ADR/ADR-01_architecture_decision/ADR-01.0_architecture_decision_index.md

# Validate all ADR files (section-based structure)
find docs/ADR -type f -name "ADR-*.md" -exec python 05_ADR/scripts/validate_adr.py {} \;

# Validate monolithic ADR (optional for <25KB)
python 05_ADR/scripts/validate_adr.py docs/05_ADR/ADR-01_architecture_decision.md
```

### SYS-Ready Scoring Criteria  NEW

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

All diagrams MUST use Mermaid syntax. Text-based diagrams (ASCII art, box drawings) are prohibited. Directory tree structures (`  `) are exempted.

**Central Authority**: `ai_dev_flow/DIAGRAM_STANDARDS.md`
**Diagram Skill**: `mermaid-gen` skill

---

## Common Mistakes

### Mistake #1: Incomplete Decision Process
```
[FAIL] Missing alternatives considered section
[PASS] Document evaluated alternatives with rejection rationale
```

### Mistake #2: Vague Architecture Documentation
```
[FAIL] "Use microservices architecture"
[PASS] "Use event-driven microservices with CQRS pattern for order processing, deployed on Kubernetes with Istio service mesh"
```

### Mistake #3: SYS-Ready Score Format
```
[FAIL] SYS-Ready Score: 95%
[PASS] SYS-Ready Score: [PASS] 95% (Target: ≥90%)
```

### Mistake #4: Missing Traceability Tags
```
[FAIL] @brd: BRD-01
[PASS] @brd: BRD.01.01.30, BRD.01.01.06
```

---

**Maintained By**: Architecture Team, Quality Assurance Team
**Review Frequency**: Updated with ADR template enhancements
