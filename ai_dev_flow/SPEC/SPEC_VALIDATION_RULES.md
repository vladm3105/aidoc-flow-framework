# =============================================================================
# 📋 Document Role: This is a DERIVATIVE of SPEC-TEMPLATE.md / SPEC-TEMPLATE.yaml
# - Authority: SPEC-TEMPLATE files are the single source of truth for SPEC structure
# - Purpose: AI checklist after document creation (derived from template)
# - Scope: Includes all rules from SPEC_CREATION_RULES.md plus validation extensions
# - On conflict: Defer to SPEC-TEMPLATE.md / SPEC-TEMPLATE.yaml
# =============================================================================
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

> **📋 Document Role**: This is the **POST-CREATION VALIDATOR** for SPEC documents.
> - Apply these rules after SPEC creation or modification
> - **Authority**: Validates compliance with `SPEC-TEMPLATE.yaml` (the primary standard)
> - **Scope**: Use for quality gates before committing SPEC changes

# SPEC Validation Rules Reference

**Version**: 1.0
**Date**: 2025-11-19
**Last Updated**: 2025-11-19
**Purpose**: Complete validation rules for SPEC YAML files
**Script**: `python scripts/validate_spec.py`
**Primary Template**: `SPEC-TEMPLATE.yaml`
**Framework**: AI Dev Flow SDD (100% compliant)
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

### Reserved ID Exemption (SPEC-000_*)

**Scope**: Documents with reserved ID `000` are FULLY EXEMPT from validation.

**Pattern**: `SPEC-000_*.md` or `SPEC-000_*.yaml`

**Document Types**:
- Index documents (`SPEC-000_index.md`)
- Traceability matrix templates (`SPEC-000_TRACEABILITY_MATRIX-TEMPLATE.md`)
- Glossaries, registries, checklists

**Rationale**: Reserved ID 000 documents are framework infrastructure (indexes, templates, reference materials), not project artifacts requiring traceability or quality gates.

**Validation Behavior**: Skip all checks when filename matches `SPEC-000_*` pattern.

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
  brd: "BRD.NN.EE.SS"         # Unified dot notation for sub-ID references
  prd: "PRD.NN.EE.SS"         # Unified dot notation for sub-ID references
  ears: "EARS.NN.EE.SS"       # Unified dot notation
  bdd: "BDD.NN.EE.SS"         # Unified dot notation for sub-ID references
  adr: "ADR-NN"             # Document-level reference (no sub-ID)
  sys: "SYS.NN.EE.SS"         # Unified dot notation for sub-ID references
  req: "REQ.NN.EE.SS"         # Unified dot notation for sub-ID references
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

### CHECK 8: Element ID Format Compliance ⭐ NEW

**Purpose**: Verify element IDs use unified 4-segment format, flag removed patterns.
**Type**: Error

| Check | Pattern | Result |
|-------|---------|--------|
| Valid format | `SPEC.NN.TT.SS:` | ✅ Pass |
| Removed pattern | `STEP-XXX` | ❌ Fail - use SPEC.NN.15.SS |
| Removed pattern | `IF-XXX` | ❌ Fail - use SPEC.NN.16.SS |
| Removed pattern | `DM-XXX` | ❌ Fail - use SPEC.NN.17.SS |
| Removed pattern | `VR-XXX` | ❌ Fail - use SPEC.NN.21.SS |

**Regex**: `^###?\s+SPEC\.[0-9]{2,}\.[0-9]{2,}\.[0-9]{2,}:\s+.+$`

**Common Element Types for SPEC**:
| Element Type | Code | Example |
|--------------|------|---------|
| Step | 15 | SPEC.02.15.01 |
| Interface | 16 | SPEC.02.16.01 |
| Data Model | 17 | SPEC.02.17.01 |
| Validation Rule | 21 | SPEC.02.21.01 |
| Specification Element | 28 | SPEC.02.28.01 |

**Fix**: Replace `IF-01: Interface` with `SPEC.02.16.01: Interface`

**Reference**: SPEC_CREATION_RULES.md Section 4.1, ID_NAMING_STANDARDS.md lines 783-793

---

## Error Fix Guide

### Quick Fix Matrix

| Error Check | Quick Fix |
|-------------|-----------|
| **CHECK 1** | Fix YAML syntax (indentation, quotes, colons) |
| **CHECK 2** | Add missing metadata fields |
| **CHECK 3** | Add properly formatted TASKS-ready score |
| **CHECK 4** | Complete traceability tag chain |
| **CHECK 8** | Replace legacy element IDs (STEP-XXX, IF-XXX, DM-XXX) with unified format `SPEC.NN.TT.SS` |

---

## Quick Reference

### Pre-Commit Validation

```bash
# Validate single SPEC YAML file
python scripts/validate_spec.py docs/SPEC/SPEC-01_component_spec/SPEC-01_component_spec.yaml

# Validate all SPEC files
find docs/SPEC -name "SPEC-*.yaml" -exec python scripts/validate_spec.py {} \;
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
    brd: "BRD-NN"
✅ cumulative_tags:
    brd: "BRD.01.01.30"
    prd: "PRD.03.01.02"
    ears: "EARS.01.24.03"
    bdd: "BDD.03.13.01"
    adr: "ADR-NN"
    sys: "SYS.01.25.01"
    req: "REQ.02.26.05"
```

### Mistake #4: CTR Contract Mismatch
```
❌ # CTR-NN references interface that doesn't exist
✅ # Verified CTR-01_api_contract.md exists and matches API spec
```

---

**Maintained By**: Architecture Team, Engineering Team
**Review Frequency**: Updated with SPEC template enhancements
