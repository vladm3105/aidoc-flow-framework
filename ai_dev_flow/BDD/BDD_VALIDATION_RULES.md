# =============================================================================
# 📋 Document Role: This is a DERIVATIVE of BDD-TEMPLATE.feature
# - Authority: BDD-TEMPLATE.feature is the single source of truth for BDD structure
# - Purpose: AI checklist after document creation (derived from template)
# - Scope: Includes all rules from BDD_CREATION_RULES.md plus validation extensions
# - On conflict: Defer to BDD-TEMPLATE.feature
# =============================================================================
---
title: "BDD Validation Rules Reference"
tags:
  - validation-rules
  - layer-4-artifact
  - shared-architecture
custom_fields:
  document_type: validation-rules
  artifact_type: BDD
  layer: 4
  priority: shared
  development_status: active
---

> **📋 Document Role**: VALIDATION CHECKLIST for BDD documents (DERIVATIVE).
> - **Authority**: Validates compliance with `BDD-TEMPLATE.feature` (PRIMARY STANDARD)
> - **Purpose**: Post-creation quality gate checks
> - **Scope**: Use for quality gates before committing BDD changes
> - **Conflict Resolution**: If this conflicts with Template, update this document

# BDD Validation Rules Reference

**Version**: 1.0
**Date**: 2025-11-19
**Last Updated**: 2025-11-19
**Purpose**: Complete validation rules for BDD feature files
**Script**: `scripts/validate_bdd_template.sh`
**Primary Template**: `BDD-TEMPLATE.feature`
**Framework**: doc_flow SDD (100% compliant)
**Changes**: Added ADR-ready scoring validation system

---

## Table of Contents

1. [Overview](#overview)
2. [Validation Checks](#validation-checks)
3. [Error Fix Guide](#error-fix-guide)
4. [Quick Reference](#quick-reference)
5. [Common Mistakes](#common-mistakes)

---

## Overview

The BDD validation script ensures feature files meet quality standards for ADR progression and automated test execution.

### Validation Tiers

| Tier | Type | Exit Code | Description |
|------|------|-----------|-------------|
| **Tier 1** | Errors | 1 | Blocking issues - must fix before commit |
| **Tier 2** | Warnings | 0 | Quality issues - recommended to fix |
| **Tier 3** | Info | 0 | Informational - no action required |

### Reserved ID Exemption (BDD-000_*)

**Scope**: Documents with reserved ID `000` are FULLY EXEMPT from validation.

**Pattern**: `BDD-000_*.md` or `BDD-000_*.feature`

**Document Types**:
- Index documents (`BDD-000_index.md`)
- Traceability matrix templates (`BDD-000_TRACEABILITY_MATRIX-TEMPLATE.md`)
- Glossaries, registries, checklists

**Rationale**: Reserved ID 000 documents are framework infrastructure (indexes, templates, reference materials), not project artifacts requiring traceability or quality gates.

**Validation Behavior**: Skip all checks when filename matches `BDD-000_*` pattern.

---

## Validation Checks

### CHECK 1: Required Document Control Fields

**Type**: Error (blocking)

**Required Fields**:
- Project Name, Document Version, Date, Document Owner, Prepared By, Status, ADR-Ready Score

### CHECK 2: Gherkin Syntax Compliance

**Type**: Error (blocking)

**Requirements**:
- Feature declaration with As a/I want/So that
- Background keyword where applicable
- Valid Given/When/Then structure
- Proper tag format (@scenario_name)

### CHECK 3: ADR-Ready Score Validation ⭐ NEW

**Purpose**: Validate ADR-ready score format and threshold
**Type**: Error (blocking)

**Valid Examples**: `✅ 95% (Target: ≥90%)`

**Error Message**: `❌ MISSING: ADR-Ready Score with ✅ emoji and percentage`

### CHECK 4: Upstream Traceability Tags

**Purpose**: Verify complete tag chain per BDD-TEMPLATE.feature
**Type**: Error (blocking)

**Required Tags** (ALL MANDATORY):
```gherkin
@brd: BRD.NN.EE.SS    # REQUIRED - business requirements
@prd: PRD.NN.EE.SS    # REQUIRED - product requirements
@ears: EARS.NN.EE.SS  # REQUIRED - engineering requirements
```

**Format**: Extended format with requirement ID suffix (`:NN`) is REQUIRED.

### CHECK 4.1: Tag Placement Validation ⭐ NEW

**Purpose**: Verify tags are Gherkin-native, not in comments
**Type**: Error (blocking)

**Validation Rule**: Tags MUST appear as Gherkin-native tags on separate lines before `Feature:` keyword, NOT inside comment blocks.

**❌ INVALID** (comment-based tags - frameworks cannot parse):
```gherkin
# @brd: BRD.01.01.01
# @prd: PRD.01.01.01
Feature: My Feature
```

**✅ VALID** (Gherkin-native tags):
```gherkin
@brd:BRD.01.01.01
@prd:PRD.01.01.01
@ears:EARS.01.24.01
Feature: My Feature
```

**Detection Pattern**:
```bash
# Detect comment-based tags (invalid)
grep -n "^#.*@brd:" docs/BDD/*.feature
grep -n "^#.*@prd:" docs/BDD/*.feature
grep -n "^#.*@ears:" docs/BDD/*.feature
```

**Error Message**: `❌ INVALID: Tags found in comments. Move to Gherkin-native format before Feature: keyword`

### CHECK 5: Scenario Coverage Completeness

**Purpose**: Ensure comprehensive test coverage
**Type**: Warning

**Requirements**:
- Primary success scenarios present
- Error conditions covered
- Edge cases included
- Quality attribute scenarios specified

### CHECK 6: BDD Syntax Validation

**Purpose**: Verify Gherkin best practices
**Type**: Warning

**Requirements**:
- Active voice in step definitions
- Observable outcomes in Then steps
- No subjective language (fast, reliable, etc.)
- Data-driven Examples tables for parametric testing

### CHECK 7: ADR Readiness Assessment

**Purpose**: Verify architectural requirements clarity
**Type**: Warning

**Requirements**:
- Performance targets quantifiable
- security scenarios included
- Integration points specified
- Scalability requirements defined

---

### CHECK 8: Element ID Format Compliance ⭐ NEW

**Purpose**: Verify element IDs use unified 4-segment format, flag removed patterns.
**Type**: Error

| Check | Pattern | Result |
|-------|---------|--------|
| Valid format | `BDD.NN.TT.SS:` | ✅ Pass |
| Removed pattern | `TS-XXX` | ❌ Fail - use BDD.NN.14.SS |
| Removed pattern | `Scenario-XXX` | ❌ Fail - use BDD.NN.14.SS |
| Removed pattern | `STEP-XXX` | ❌ Fail - use BDD.NN.15.SS |

**Regex**: `^###?\s+BDD\.[0-9]{2,}\.[0-9]{2,}\.[0-9]{2,}:\s+.+$`

**Common Element Types for BDD**:
| Element Type | Code | Example |
|--------------|------|---------|
| Test Scenario | 14 | BDD.02.14.01 |
| Step | 15 | BDD.02.15.01 |

**Fix**: Replace `Scenario: TS-01` with `Scenario: BDD.02.14.01`

**Reference**: BDD_CREATION_RULES.md Section 4.1, ID_NAMING_STANDARDS.md lines 783-793

---

## Error Fix Guide

### Quick Fix Matrix

| Error Check | Quick Fix |
|-------------|-----------|
| **CHECK 1** | Add missing Document Control fields |
| **CHECK 2** | Fix Gherkin syntax (Given/When/Then structure) |
| **CHECK 3** | Add properly formatted ADR-Ready Score |
| **CHECK 4** | Complete traceability tag chain |
| **CHECK 8** | Replace legacy element IDs (TS-XXX, Scenario-XXX) with unified format `BDD.NN.TT.SS` |

---

## Quick Reference

### Pre-Commit Validation

```bash
# Validate single BDD feature file
./scripts/validate_bdd_template.sh docs/BDD/BDD-01_feature_scenarios.feature

# Validate all BDD files
find docs/BDD -name "BDD-*.feature" -exec ./scripts/validate_bdd_template.sh {} \;
```

### ADR-Ready Scoring Criteria ⭐ NEW

**Scenario Completeness (35%)**:
- All EARS statements translated to BDD: 15%
- Comprehensive coverage (success/error/edge): 15%
- Observable verifications specified: 5%

**Testability (30%)**:
- Scenarios are automatable: 15%
- Data-driven Examples tables used: 10%
- Performance benchmarks quantifiable: 5%

**Architecture Requirements (25%)**:
- Performance/security/scalability quality attributes: 15%
- Integration points defined: 10%

**Business Validation (10%)**:
- Business acceptance criteria: 5%
- Measurable success outcomes: 5%

### Validation Tiers Summary

| Tier | Type | Checks | Action |
|------|------|--------|--------|
| **Tier 1** | Error | 1-4 | Must fix before commit |
| **Tier 2** | Warning | 5-7 | Recommended to fix |
| **Tier 3** | Info | - | No action required |

---

## Common Mistakes

### Mistake #1: Incomplete Traceability Tags (ALL THREE ARE REQUIRED)
```
❌ @brd: BRD-01           (missing element ID suffix)
✅ @brd: BRD.01.01.30       (correct 4-segment element ID format)
❌ Missing @brd tag        (ALL three tags are MANDATORY)
✅ @brd: BRD.01.01.30
   @prd: PRD.01.01.02
   @ears: EARS.01.24.03
```

### Mistake #2: Subjective Language
```
❌ Given the system is running fast
✅ Given response time is under 500ms
```

### Mistake #3: ADR-Ready Score Format
```
❌ ADR-Ready Score: 95%
✅ ADR-Ready Score: ✅ 95% (Target: ≥90%)
```

### Mistake #4: Missing Scenario Types
```
❌ Only success scenarios included
✅ Include @negative @edge_case @quality_attribute scenarios
```

---

**Maintained By**: QA Team, Engineering Team
**Review Frequency**: Updated with BDD template enhancements
