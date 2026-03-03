---
title: "EARS MVP Validation Rules"
tags:
  - validation-rules
  - layer-3-artifact
  - shared-architecture
custom_fields:
  document_type: validation-rules
  artifact_type: EARS
  layer: 3
  priority: shared
  development_status: active
---

# =============================================================================
#  Document Role: Validates EARS-MVP-TEMPLATE.md (default)
# - Authority: EARS-MVP-TEMPLATE.md is the standard for EARS structure (MVP → PROD → NEW MVP lifecycle)
# - Purpose: AI checklist after document creation (derived from MVP template)
# - Scope: Includes all rules from EARS_CREATION_RULES.md plus validation extensions
# - On conflict: Defer to EARS-MVP-TEMPLATE.md
# =============================================================================

> **Document Role**: This is the **POST-CREATION VALIDATOR** for EARS documents.
> - Apply these rules after EARS creation or modification
> - **Authority**: Validates compliance with `EARS-MVP-TEMPLATE.md` (standard template)
> - **Scope**: Use for quality gates before committing EARS changes

# EARS Validation Rules Reference

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
| EARS syntax (WHEN-THE-SHALL) | Error | Error |
| Traceability tags (@brd, @prd) | Error | Error |
| Document Control fields | Error | Error |
| Extended quality attributes | **Warning** | Error |
| BDD-Ready Score threshold | 70/100 | 90/100 |
| BDD-Ready score presence/format | Error (blocking) | Error (blocking) |
| Timing constraints (WITHIN) | **Warning** | Error |

### Usage

```bash
# MVP validation (default profile)
python3 ai_dev_flow/03_EARS/scripts/validate_ears.py --path ai_dev_flow/03_EARS

# Full profile (set in document frontmatter)
# custom_fields:
#   template_profile: full
```

### Cross-Linking Tags (AI-Friendly)

Use same-layer cross-links to document EARS relationships:
- `@depends: EARS-NN` — hard prerequisite EARS document(s) that must be satisfied first.
- `@discoverability: EARS-NN (short rationale)` — related EARS documents with brief reasons to aid AI search and ranking.

Validation handling: Info-level (non-blocking). Reported for visibility only.

---

> Path conventions: Examples below use a portable `docs/` root for new projects. In this repository, artifact folders live at the ai_dev_flow root (no `docs/` prefix). When running commands here, drop the `docs/` prefix. See README → "Using This Repo" for path mapping.

**Version**: 2.0
**Date**: 2025-11-29T00:00:00
**Last Updated**: 2025-11-29T00:00:00
**Purpose**: Complete validation rules for EARS documents
**Script**: `03_EARS/scripts/validate_ears.py`
**Primary Template**: `EARS-MVP-TEMPLATE.md` (standard template)
**Framework**: AI Dev Flow SDD (100% compliant)
**Changes**: v2.0 - Added requirement ID, table syntax, custom_fields, traceability format checks

---

## Table of Contents

1. [Overview](#overview)
2. [Validation Checks](#validation-checks)
3. [Error Fix Guide](#error-fix-guide)
4. [Quick Reference](#quick-reference)
5. [Common Mistakes](#common-mistakes)

---

## Overview

The EARS validation script performs comprehensive checks ensuring EARS documents enable direct BDD translation and meet SDD quality standards.

### Validation Tiers

| Tier | Type | Exit Code | Description |
|------|------|-----------|-------------|
| **Tier 1** | Errors (E###) | 1 | Blocking issues - must fix before commit |
| **Tier 2** | Warnings (W###) | 0 | Quality issues - recommended to fix |

Note: `W020` and `W021` are enforced as blocking in the validator for unified layer-gate behavior.

### Reserved ID Exemption (EARS-00_*)

**Scope**: Documents with reserved ID `000` are FULLY EXEMPT from validation.

**Pattern**: `EARS-00_*.md`

**Document Types**:
- Index documents (`EARS-00_index.md`)
- Traceability matrix templates (`EARS-00_TRACEABILITY_MATRIX-TEMPLATE.md`)
- Glossaries, registries, checklists

**Rationale**: Reserved ID 000 documents are framework infrastructure (indexes, templates, reference materials), not project artifacts requiring traceability or quality gates.

**Validation Behavior**: Skip all checks when filename matches `EARS-00_*` pattern.

### Rule Categories

| Category | Rule Range | Description |
|----------|------------|-------------|
| Frontmatter | E001 | YAML parsing |
| Metadata/Tags | E002-E008 | Required tags, custom_fields |
| Structure | E010-E013 | Sections, numbering, Document Control |
| Table Syntax | E020 | Markdown table formatting |
| Requirement IDs | E030 | EARS-XXX-NN format |
| Traceability | E040-E041 | @prd: prefix, pipe separators |
| EARS Syntax | W010-W012 | SHALL patterns, atomicity |
| BDD-Ready | W020-W021, E052, E053 | Score format, status alignment, threshold gating |
| Misc | W001 | Multiple H1 |

---

## Validation Checks

### E001: YAML Frontmatter

**Type**: Error (blocking)

**Check**: Valid YAML frontmatter exists between `---` delimiters

**Fix**: Ensure file starts with valid YAML block

---

### E002: Required Tags

**Type**: Error (blocking)

**Required Tags**:
- `ears`
- `layer-3-artifact`

**Fix**: Add missing tags to frontmatter

---

### E003: Forbidden Tag Patterns

**Type**: Error (blocking)

**Forbidden Patterns**:
- `ears-requirements`
- `ears-formal-requirements`
- `ears-document`
- `ears-NN` (e.g., `ears-030`)

**Fix**: Replace with `ears`

---

### E004: Missing custom_fields

**Type**: Error (blocking)

**Check**: `custom_fields` section exists in frontmatter

**Fix**: Add complete custom_fields section

---

### E005: document_type Value

**Type**: Error (blocking)

**Required**: `document_type: ears-document` (preferred) or `document_type: ears` (legacy compatibility)

**Fix**: Set `document_type: ears-document` in custom_fields for generated instances

---

### E006: artifact_type Value

**Type**: Error (blocking)

**Required**: `artifact_type: EARS`

**Fix**: Add or correct artifact_type in custom_fields

---

### E007: layer Value

**Type**: Error (blocking)

**Required**: `layer: 3`

**Fix**: Add or correct layer in custom_fields

---

### E008: architecture_approaches Format

**Type**: Error (blocking)

**Check**: Must use `architecture_approaches` (plural) with array format

**Invalid**:
```yaml
architecture_approach: ai-agent-based  # WRONG - singular, string
```

**Valid**:
```yaml
architecture_approaches: [ai-agent-based]  # CORRECT - plural, array
```

---

### E010: Required Sections

**Type**: Error (blocking)

**Required Sections (6-Section MVP Structure)**:
- Document Control (unnumbered)
- Section 1: Purpose and Context
- Section 2: EARS in Development Workflow
- Section 3: Requirements
- Section 4: Quality Attributes
- Section 5: Traceability
- Section 6: References

**Fix**: Add missing sections per EARS-MVP-TEMPLATE.md

---

### E011: Section Numbering Start

**Type**: Error (blocking)

**Check**: Section numbering does NOT start with 0

**Invalid**: `## 0. Document Control`

**Valid**: `## Document Control` or `## 1. Purpose`

---

### E012: Duplicate Section Numbers

**Type**: Error (blocking)

**Check**: No duplicate section numbers

**Fix**: Renumber sections sequentially

---

### E013: Document Control Format

**Type**: Error (blocking)

**Check**: Document Control uses table format, not list format

**Invalid**:
```markdown
## 0. Document Control

**Document Metadata**
- **Document ID**: EARS-NN
- **Version**: 1.0
```

**Valid**:
```markdown
## Document Control

| Item | Details |
|------|---------|
| **Status** | Active |
| **Version** | 1.0.0 |
```

---

### E020: Table Syntax

**Type**: Error (blocking)

**Check**: No malformed table separators (trailing `| |`)

**Invalid**:
```markdown
|------|---------| |
```

**Valid**:
```markdown
|------|---------|
```

---

### E030: Requirement ID Format  ENHANCED

**Type**: Error (blocking)

**Check**: Requirement headings use unified 4-segment format `#### EARS.NN.TT.SS: Title`

**Pattern**: `EARS.{DOC_NUM}.{ELEM_TYPE}.{SEQ}` (4 segments, dot-separated)

**Regex**: `^####\s+EARS\.[0-9]{2,}\.[0-9]{2,}\.[0-9]{2,}:\s+.+$`

| Check | Pattern | Result |
|-------|---------|--------|
| Valid format | `#### EARS.NN.25.SS:` | [PASS] Pass |
| Removed pattern | `#### Event-XXX` | [FAIL] Fail - use EARS.NN.25.SS |
| Removed pattern | `#### State-XXX` | [FAIL] Fail - use EARS.NN.25.SS |
| Removed pattern | `#### EARS-NN-XXX` | [FAIL] Fail - use EARS.NN.25.SS |

**Common Element Types for EARS**:
| Element Type | Code | Example |
|--------------|------|---------|
| EARS Statement | 25 | EARS.06.25.01 |
| Performance Quality Attribute | 02 | EARS.06.02.01 |
| Security Quality Attribute | 03 | EARS.06.03.01 |
| Reliability Quality Attribute | 04 | EARS.06.04.01 |

**Section-to-Element-Type Mapping**:

| Section | Required Code | ID Pattern |
|---------|---------------|------------|
| Section 3 (Requirements) | 25 | `EARS.NN.25.SS` |
| Section 4.1 (Performance) | 02 | `EARS.NN.02.SS` |
| Section 4.2 (Security) | 03 | `EARS.NN.03.SS` |
| Section 4.3 (Reliability) | 04 | `EARS.NN.04.SS` |

> [WARN] **REMOVED PATTERNS** - Do NOT use:
> - `Event-XXX` → Use `EARS.NN.25.SS`
> - `State-XXX` → Use `EARS.NN.25.SS`
> - `EARS-NN-XXX` → Use `EARS.NN.25.SS`
>
> **Reference**: [ID_NAMING_STANDARDS.md — Cross-Reference Link Format](../ID_NAMING_STANDARDS.md#cross-reference-link-format-mandatory)

**Invalid**:
```markdown
#### Event-001: L1 Verification Submission
#### State-001: Pending Status
```

**Valid**:
```markdown
#### EARS.06.25.01: L1 Verification Submission
#### EARS.06.25.02: Pending Status
```

**Fix**: Replace non-standard formats (e.g., `Event-001`, `EARS-06-001`) with `#### EARS.06.25.01: ...`

---

### E040: Source Document @prd: Prefix

**Type**: Error (blocking)

**Check**: Source Document field uses `@prd:` prefix

**Invalid**:
```markdown
| **Source Document** | PRD-01 |
```

**Valid**:
```markdown
| **Source Document** | @prd: PRD.01.01.01 |
```

---

### E044: Source Document Single @prd (No Ranges)

**Type**: Error (blocking)

**Check**: Document Control “Source Document” contains exactly one `@prd: PRD.NN.EE.SS` reference. No ranges (e.g., `@prd: ... - @prd: ...`) and no multiple `@prd` values.

**Invalid**:
```markdown
| **Source Document** | @prd: PRD.12.19.01 - @prd: PRD.12.19.57 |
```

**Valid**:
```markdown
| **Source Document** | @prd: PRD.12.19.01 |
```

**Fix**: Provide one canonical `@prd` in the table; list additional IDs in an Upstream Sources subsection or per-requirement traceability.

---

### E045: No Numeric Downstream References

**Type**: Error (blocking)

**Check**: Document contains no numeric downstream references of the form `BDD-##`, `ADR-##`, `REQ-##`, `SPEC-##`, `SYS-##`.

**Invalid**:
```markdown
Downstream: BDD-NN, ADR-NN
```

**Valid**:
```markdown
Downstream: BDD, ADR, SYS
```

**Fix**: Use generic downstream names until those artifacts exist; add numeric IDs only after creation.

---

### E041: Traceability Tag Separators

**Type**: Error (blocking)

**Check**: Multiple traceability tags separated by pipes (for inline format)

**Note**: Both inline pipe format and list format are valid traceability formats.

**Invalid** (inline without pipes):
```markdown
**Traceability**: @brd: BRD.02.01.10 @prd: PRD.02.01.01
```

**Valid** (inline with pipes):
```markdown
**Traceability**: @brd: BRD.02.01.10 | @prd: PRD.02.01.01
```

**Valid** (list format):
```markdown
**Traceability**:
- @brd: BRD.02.01.10
- @prd: PRD.02.01.01
- @threshold: PRD.035.timeout.partner.bridge
```

---

### E042: Requirement ID Uniqueness

**Type**: Error (blocking)

**Check**: Each requirement ID must be unique within the document

**Invalid**:
```markdown
#### EARS.02.25.01: First Requirement
...
#### EARS.02.25.01: Different Requirement  ← DUPLICATE ID
```

**Valid**:
```markdown
#### EARS.02.25.02: Second Requirement  ← UNIQUE ID
```

**Fix**: Renumber duplicate IDs sequentially

---

### E050: Universal Splitting Trigger (Size/Cardinality)  NEW

**Purpose**: Enforce Nested Directory Pattern when triggers are met.
**Type**: Error (blocking)

**Triggers**:
1. **Size**: File > 20,000 tokens.
2. **Cardinality**: More than 1 file for this ID.

**Action**: Move to `04_EARS/EARS-{PRD_ID}_{Slug}/` folder.

**Error Message**: `[FAIL] ERROR: EARS-NN triggers nested folder rule (>20,000 tokens or >1 file). Move to 04_EARS/EARS-NN_{Slug}/`

---

### E043: @brd Tag in Traceability

**Type**: Warning

**Check**: Traceability section includes `@brd: BRD.NN.EE.SS` reference

**Rationale**: EARS (Layer 3) should trace back to BRD (Layer 1) via PRD (Layer 2)

**Valid format**:
```markdown
@brd: BRD.02.01.10
```

**Fix**: Add @brd tag to traceability section referencing source BRD

---

### W001: Multiple H1 Headings

**Type**: Warning

**Check**: Only one H1 (`#`) heading per document

---

### W010: EARS SHALL Statements

**Type**: Warning

**Check**: Document contains EARS `SHALL` statements

---

### W011: Atomic Requirements

**Type**: Warning

**Check**: Requirements don't have multiple `and` clauses

**Recommend**: Split compound requirements

---

### W012: Measurable Constraints

**Type**: Warning

**Check**: `WITHIN` clauses have numeric/measurable values

---

### W020: BDD-Ready Score Missing

**Type**: Error (blocking)

**Check**: Document Control contains BDD-Ready Score

---

### W021: BDD-Ready Score Format

**Type**: Error (blocking)

**Required Format**: `[PASS] NN% (Target: ≥90%)`

---

### E053: BDD-Ready Score Below Profile Threshold

**Type**: Error (blocking)

**Check**: Score must meet profile threshold

**Thresholds**:
- `mvp`: ≥70%
- `standard`/`full`/`enterprise`: ≥90%

---

## Error Fix Guide

### Quick Fix Matrix

| Rule | Quick Fix |
|------|-----------|
| E002 | Add `- ears` and `- layer-3-artifact` to tags |
| E003 | Replace forbidden tag with `ears` |
| E006 | Add `artifact_type: EARS` to custom_fields |
| E007 | Add `layer: 3` to custom_fields |
| E008 | Change `architecture_approach:` to `architecture_approaches: [value]` |
| E011/E013 | Change `## 0. Document Control` to `## Document Control`, use table format |
| E020 | Remove trailing `\| \|` from table separator |
| E030 | Change `#### Event-N:` to `#### EARS.NN.25.SS:` |
| E040 | Change `PRD-NN` to `@prd: PRD.NN.EE.SS` |
| E041 | Add `\|` between traceability tags |

---

## Quick Reference

### Run Validation

```bash
# Validate all EARS files
python3 03_EARS/scripts/validate_ears.py

# Validate single file
python3 03_EARS/scripts/validate_ears.py --path 03_EARS/EARS-006.md

# Show fix suggestions
python3 03_EARS/scripts/validate_ears.py --fix-suggestions

# Summary only (counts by rule)
python3 03_EARS/scripts/validate_ears.py --summary-only
```

### Pre-Commit Checklist

- [ ] Run `python3 03_EARS/scripts/validate_ears.py` - 0 errors
- [ ] All files have `tags: ears, layer-3-artifact`
- [ ] All files have `custom_fields` with document_type, artifact_type, layer
- [ ] All requirement IDs use `EARS.NN.25.SS:` format
- [ ] No malformed table syntax
- [ ] Document Control uses table format (not list)

---

## Common Mistakes

### Mistake #1: Wrong Tag Format
```
[FAIL] tags: ears-030, ears-requirements
[PASS] tags: ears, layer-3-artifact
```

### Mistake #2: Singular architecture_approach
```
[FAIL] architecture_approach: ai-agent-based
[PASS] architecture_approaches: [ai-agent-based]
```

### Mistake #3: Non-Standard Requirement IDs
```
[FAIL] #### Event-001: L1 Verification Submission
[PASS] #### EARS.06.25.01: L1 Verification Submission
```

### Mistake #4: List-Style Document Control
```
[FAIL] ## 0. Document Control
   **Document Metadata**
   - **Version**: 1.0

[PASS] ## Document Control
   | Item | Details |
   |------|---------|
   | **Version** | 1.0.0 |
```

### Mistake #5: Missing Traceability Separators
```
[FAIL] **Traceability**: @brd: X @prd: Y @threshold: Z
[PASS] **Traceability**: @brd: X | @prd: Y | @threshold: Z
```

### Mistake #6: Table Separator Typo
```
[FAIL] |------|---------| |
[PASS] |------|---------|
```

---

**Maintained By**: Engineering Team
**Review Frequency**: Updated with EARS template enhancements
**Script Location**: `03_EARS/scripts/validate_ears.py`
