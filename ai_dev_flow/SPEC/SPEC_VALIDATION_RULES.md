---
title: "SPEC Validation Rules Reference"
tags:
  - validation-rules
  - layer-10-artifact
  - shared-architecture
custom_fields:
  document_type: validation-rules
  artifact_type: SPEC
  layer: 10
  priority: shared
  development_status: active
---

# SPEC Validation Rules Reference

**Version**: 1.0
**Date**: 2025-11-19
**Last Updated**: 2025-11-19
**Purpose**: Complete validation rules for SPEC YAML files
**Script**: `scripts/validate_spec_template.sh`
**Primary Template**: `SPEC-TEMPLATE.yaml`
**Framework**: doc_flow SDD (100% compliant)
**Changes**: Added TASKS-ready scoring validation system

---

## Table of Contents

1. [Overview](#overview)
2. [Validation Checks](#validation-checks)
3. [Error Fix Guide](#error-fix-guide)
4. [Quick Reference](#quick-reference)
5. [Common Mistakes](#common-mistakes)

---

## Overview

The SPEC validation script ensures YAML specification files meet quality standards for TASKS implementation planning.

### Validation Tiers

| Tier | Type | Exit Code | Description |
|------|------|-----------|-------------|
| **Tier 1** | Errors | 1 | Blocking issues - must fix before commit |
| **Tier 2** | Warnings | 0 | Quality issues - recommended to fix |
| **Tier 3** | Info | 0 | Informational - no action required |

---

## Validation Checks

### CHECK 1: YAML Syntax Validation

**Purpose**: Ensure file is valid YAML that can be parsed
**Type**: Error (blocking)

**Requirements**:
- Valid YAML syntax
- Proper indentation
- Correct data types (strings, numbers, booleans, arrays, objects)

### CHECK 2: Required Metadata Fields

**Type**: Error (blocking)

**Required Fields**:
- metadata.version, metadata.status, metadata.created_date
- metadata.task_ready_score with `✅ NN% (Target: ≥90%)` format

### CHECK 3: TASKS-Ready Score Validation ⭐ NEW

**Purpose**: Validate TASKS-ready score format and threshold
**Type**: Error (blocking)

**Valid Examples**: `✅ 95% (Target: ≥90%)`

**Error Message**: `❌ MISSING: TASKS-ready score with ✅ emoji and percentage`

### CHECK 4: Complete Traceability Chain

**Purpose**: Verify all upstream artifacts referenced
**Type**: Error (blocking)

**Required Tag Chain**:
```yaml
cumulative_tags:
  brd: "BRD-NNN:REQUIREMENT-ID"
  prd: "PRD-NNN:REQUIREMENT-ID"
  ears: "EARS-NNN:STATEMENT-ID"
  bdd: "BDD-NNN:SCENARIO-ID"
  adr: "ADR-NNN"
  sys: "SYS-NNN:SECTION-ID"
  req: "REQ-NNN:REQUIREMENT-ID"
```

### CHECK 5: Interface Specifications

**Purpose**: Verify CTR contract references are valid
**Type**: Warning

**Requirements**:
- External API contracts reference CTR files
- Contract references are resolvable
- CTR files exist and match interface definitions

### CHECK 6: Implementation Readiness

**Purpose**: Ensure SPEC enables code generation
**Type**: Warning

**Requirements**:
- All specification sections machine-readable
- Implementation paths and dependencies specified
- Configuration schemas valid

### CHECK 7: Code Generation Compatibility

**Purpose**: Verify SCHEMA sections enable TASKS creation
**Type**: Warning

**Requirements**:
- Interface method signatures parseable
- Data schemas compatible with target languages
- Error handling specifications complete

---

## Error Fix Guide

### Quick Fix Matrix

| Error Check | Quick Fix |
|-------------|-----------|
| **CHECK 1** | Fix YAML syntax (indentation, quotes, colons) |
| **CHECK 2** | Add missing metadata fields |
| **CHECK 3** | Add properly formatted TASKS-ready score |
| **CHECK 4** | Complete traceability tag chain |

---

## Quick Reference

### Pre-Commit Validation

```bash
# Validate single SPEC YAML file
./scripts/validate_spec_template.sh docs/SPEC/SPEC-001_component_spec.yaml

# Validate all SPEC files
find docs/SPEC -name "SPEC-*.yaml" -exec ./scripts/validate_spec_template.sh {} \;
```

### TASKS-Ready Scoring Criteria ⭐ NEW

**YAML Completeness (25%)**:
- Metadata fields complete: 10%
- Traceability chain valid: 10%
- All spec sections populated: 5%

**Interface Definitions (25%)**:
- External APIs with CTR contracts: 15%
- Internal interfaces documented: 5%
- Data schemas/types defined: 5%

**Implementation Specifications (25%)**:
- Behavior enables code generation: 15%
- Performance/security quantifiable: 5%
- Dependencies/configuration specified: 5%

**Code Generation Readiness (25%)**:
- Machine-readable fields: 15%
- TASKS-ready metadata included: 5%
- Validation schemas complete: 5%

### Validation Tiers Summary

| Tier | Type | Checks | Action |
|------|------|--------|--------|
| **Tier 1** | Error | 1-4 | Must fix before commit |
| **Tier 2** | Warning | 5-7 | Recommended to fix |
| **Tier 3** | Info | - | No action required |

---

## Common Mistakes

### Mistake #1: Invalid YAML Syntax
```
❌ version: '1.0.0  # Missing closing quote
✅ version: "1.0.0"  # Proper quotes
```

### Mistake #2: Missing TASKS-Ready Score
```
❌ metadata:
    version: "1.0.0"
    status: "draft"
✅ metadata:
    version: "1.0.0"
    status: "draft"
    task_ready_score: "✅ 95% (Target: ≥90%)"
```

### Mistake #3: Incomplete Traceability
```
❌ cumulative_tags:
    brd: "BRD-001"
✅ cumulative_tags:
    brd: "BRD-001:FR-030"
    prd: "PRD-003:FEATURE-002"
    ears: "EARS-001:EVENT-003"
    bdd: "BDD-003:scenario-realtime-quote"
    adr: "ADR-033"
    sys: "SYS-001:PERFORMANCE-001"
    req: "REQ-002:IMPLEMENTATION-005"
```

### Mistake #4: CTR Contract Mismatch
```
❌ # CTR-NNN references interface that doesn't exist
✅ # Verified CTR-001_api_contract.md exists and matches API spec
```

---

**Maintained By**: Architecture Team, Engineering Team
**Review Frequency**: Updated with SPEC template enhancements
