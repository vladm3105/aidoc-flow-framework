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

**Purpose**: Verify complete tag chain
**Type**: Error (blocking)

**Required Tags**:
```gherkin
@brd: BRD-NNN:REQUIREMENT-ID
@prd: PRD-NNN:REQUIREMENT-ID
@ears: EARS-NNN:STATEMENT-ID
```

### CHECK 5: Scenario Coverage Completeness

**Purpose**: Ensure comprehensive test coverage
**Type**: Warning

**Requirements**:
- Primary success scenarios present
- Error conditions covered
- Edge cases included
- Non-functional scenarios specified

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

## Error Fix Guide

### Quick Fix Matrix

| Error Check | Quick Fix |
|-------------|-----------|
| **CHECK 1** | Add missing Document Control fields |
| **CHECK 2** | Fix Gherkin syntax (Given/When/Then structure) |
| **CHECK 3** | Add properly formatted ADR-Ready Score |
| **CHECK 4** | Complete traceability tag chain |

---

## Quick Reference

### Pre-Commit Validation

```bash
# Validate single BDD feature file
./scripts/validate_bdd_template.sh docs/BDD/BDD-001_feature_scenarios.feature

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
- Performance/security/scalability NFRs: 15%
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

### Mistake #1: Incomplete Traceability Tags
```
❌ @brd: BRD-001
✅ @brd: BRD-001:FR-030
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
✅ Include @negative @edge_case @non_functional scenarios
```

---

**Maintained By**: QA Team, Engineering Team
**Review Frequency**: Updated with BDD template enhancements
