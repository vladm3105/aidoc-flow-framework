---
title: "EARS Validation Rules Reference"
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

> **📋 Document Role**: This is the **POST-CREATION VALIDATOR** for EARS documents.
> - Apply these rules after EARS creation or modification
> - **Authority**: Validates compliance with `EARS-TEMPLATE.md` (the primary standard)
> - **Scope**: Use for quality gates before committing EARS changes

# EARS Validation Rules Reference

**Version**: 1.0
**Date**: 2025-11-19
**Last Updated**: 2025-11-19
**Purpose**: Complete validation rules for EARS documents
**Script**: `scripts/validate_ears_template.sh`
**Primary Template**: `EARS-TEMPLATE.md`
**Framework**: doc_flow SDD (100% compliant)
**Changes**: Added BDD-ready scoring validation system

---

## Table of Contents

1. [Overview](#overview)
2. [Validation Checks](#validation-checks)
3. [Error Fix Guide](#error-fix-guide)
4. [Quick Reference](#quick-reference)
5. [Common Mistakes](#common-mistakes)

---

## Overview

The EARS validation script performs checks ensuring EARS documents enable direct BDD translation and meet SDD quality standards.

### Validation Tiers

| Tier | Type | Exit Code | Description |
|------|------|-----------|-------------|
| **Tier 1** | Errors | 1 | Blocking issues - must fix before commit |
| **Tier 2** | Warnings | 0 | Quality issues - recommended to fix |
| **Tier 3** | Info | 0 | Informational - no action required |

---

## Validation Checks

### CHECK 1: Required sections

**Type**: Error (blocking)

**Required sections**:
- Document Control, Purpose and Context, Requirements (all 4 types), Non-Functional Requirements, Guidelines, Quality Checklist, Traceability, References

### CHECK 2: Document Control Fields

**Type**: Error (blocking)

**Required Fields**:
- Status, Version, BDD-Ready Score (format: `✅ NN% (Target: ≥90%)`)

### CHECK 3: EARS Syntax Compliance

**Purpose**: Verify all statements follow WHEN-THE-SHALL-WITHIN patterns
**Type**: Error (blocking)

**Requirements**:
- Event-Driven: WHEN [condition] THE [system] SHALL [response] WITHIN [constraint]
- State-Driven: WHILE [state] THE [system] SHALL [behavior] WITHIN [constraint]
- Unwanted: IF [condition] THE [system] SHALL [prevention] WITHIN [constraint]
- Ubiquitous: THE [system] SHALL [requirement] WITHIN [constraint]

### CHECK 4: BDD-Ready Score Validation ⭐ NEW

**Purpose**: Validate BDD-ready score format and threshold
**Type**: Error (blocking)

**Valid Examples**: `✅ 95% (Target: ≥90%)`

**Error Message**: `❌ MISSING: BDD-Ready Score with ✅ emoji and percentage`

### CHECK 5: Atomic Requirements

**Purpose**: Ensure one concept per statement
**Type**: Warning

**Errors**: Statements with multiple "and" clauses

### CHECK 6: Measurable Constraints

**Purpose**: Verify all WITHIN clauses are quantifiable
**Type**: Warning

**Requirements**: No subjective terms, specific time/measurement values

### CHECK 7: BDD Translation Readiness

**Purpose**: Verify statements can be converted to BDD scenarios
**Type**: Warning

**Requirements**: Clear Given-When-Then equivalency

---

## Error Fix Guide

### Quick Fix Matrix

| Error Check | Quick Fix |
|-------------|-----------|
| **CHECK 1** | Add missing section headers |
| **CHECK 3** | Reformat statements to follow EARS syntax |
| **CHECK 4** | Add properly formatted BDD-Ready Score |
| **CHECK 5** | Split compound statements |

---

## Quick Reference

### Pre-Commit Validation

```bash
# Validate single EARS file
./scripts/validate_ears_template.sh docs/EARS/EARS-001_system_requirements.md

# Validate all EARS files
find docs/EARS -name "EARS-*.md" -exec ./scripts/validate_ears_template.sh {} \;
```

### BDD-Ready Scoring Criteria ⭐ NEW

**Requirements Clarity (40%)**:
- EARS syntax compliance: 20%
- Atomic statement structure: 15%
- Quantifiable constraints: 5%

**Testability (35%)**:
- BDD translation possible: 15%
- Observable verification: 10%
- Edge case coverage: 10%

**NFR Completeness (15%)**:
- Performance with percentiles: 5%
- security/compliance: 5%
- Reliability/scalability: 5%

**Strategic Alignment (10%)**:
- Business objective linkage: 5%
- Implementation paths: 5%

### Validation Tiers Summary

| Tier | Type | Checks | Action |
|------|------|--------|--------|
| **Tier 1** | Error | 1-4 | Must fix before commit |
| **Tier 2** | Warning | 5-7 | Recommended to fix |
| **Tier 3** | Info | - | No action required |

---

## Common Mistakes

### Mistake #1: Subject Syntax
```
❌ The system shall respond quickly.
✅ THE System SHALL respond WITHIN 50ms at p95 latency.
```

### Mistake #2: Compound Requirements
```
❌ WHEN data arrives THE system SHALL validate and process data.
✅ [Split into separate Event-001 and Event-002 statements]
```

### Mistake #3: BDD-Ready Score Format
```
❌ BDD-Ready Score: 95%
✅ BDD-Ready Score: ✅ 95% (Target: ≥90%)
```

---

**Maintained By**: Engineering Team, QA Team
**Review Frequency**: Updated with EARS template enhancements
