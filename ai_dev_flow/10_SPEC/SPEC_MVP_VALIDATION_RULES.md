---
title: "SPEC MVP Validation Rules"
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
> - **Authority**: Validates compliance with `SPEC-MVP-TEMPLATE.yaml` (MVP default profile; use full profile only when explicitly requested)
> - **Scope**: Use for quality gates before committing SPEC changes

# SPEC Validation Rules Reference

> Path conventions: Examples below use a portable `docs/` root for new projects. In this repository, artifact folders live at the ai_dev_flow root (no `docs/` prefix). When running commands here, drop the `docs/` prefix. See README → "Using This Repo" for path mapping.

**Version**: 1.2
**Date**: 2025-11-30
**Last Updated**: 2025-11-30
**Purpose**: Complete validation rules for SPEC YAML files
**Script**: `python scripts/validate_spec.py`
**Primary Template**: `SPEC-MVP-TEMPLATE.yaml`
**Framework**: AI Dev Flow SDD (100% compliant)
**Changes**: v1.2: Added file size warnings, removed document splitting requirement. v1.1: Relaxed method naming (dunder support), downgraded missing latency targets to Warning, added TASKS-ready scoring validation system

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

### Reserved ID Exemption (SPEC-00_*)

**Scope**: Documents with reserved ID `000` are FULLY EXEMPT from validation.

**Pattern**: `SPEC-00_*.md` or `SPEC-00_*.yaml`

**Document Types**:
- Index documents (`SPEC-00_index.md`)
- Traceability matrix templates (`SPEC-00_TRACEABILITY_MATRIX-TEMPLATE.md`)
- Glossaries, registries, checklists

**Rationale**: Reserved ID 000 documents are framework infrastructure (indexes, templates, reference materials), not project artifacts requiring traceability or quality gates.

**Validation Behavior**: Skip all checks when filename matches `SPEC-00_*` pattern.

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

### CHECK 4: Threshold Registry Compliance ⭐ NEW

**Purpose**: Enforce @threshold usage and registry traceability
**Type**: Error (blocking)

**Requirements**:
- All quantitative values (performance, timeouts, limits, resource caps) use `@threshold: PRD.NN.*`
- `threshold_references.registry_document` present (PRD ID) and `keys_used` lists all referenced keys
- No raw numeric literals in quantitative fields

### CHECK 5: Complete Traceability Chain

**Purpose**: Verify all upstream artifacts referenced while allowing `null` only when an upstream type truly does not exist
**Type**: Error (blocking)

**Required Tag Chain**:
```yaml
cumulative_tags:
  brd: "BRD.NN.EE.SS"         # Unified dot notation for sub-ID references (or null if absent)
  prd: "PRD.NN.EE.SS"         # Unified dot notation for sub-ID references (or null if absent)
  ears: "EARS.NN.EE.SS"       # Unified dot notation (or null if absent)
  bdd: "BDD.NN.EE.SS"         # Unified dot notation for sub-ID references (or null if absent)
  adr: "ADR-NN"             # Document-level reference (no sub-ID, or null if absent)
  sys: "SYS.NN.EE.SS"         # Unified dot notation for sub-ID references (or null if absent)
  req: "REQ.NN.EE.SS"         # Unified dot notation for sub-ID references (or null if absent)
  threshold: "PRD-NN"         # Threshold registry document reference (or null if registry not applicable)
```

### CHECK 6: Interface Specifications

**Purpose**: Verify CTR contract references are valid
**Type**: Warning

**Requirements**:
- External API contracts reference CTR files
- Contract references are resolvable
- CTR files exist and match interface definitions

### CHECK 7: Implementation Readiness

**Purpose**: Ensure SPEC enables code generation
**Type**: Warning

**Requirements**:
- All specification sections machine-readable
- Implementation paths and dependencies specified
- Configuration schemas valid

### CHECK 8: Code Generation Compatibility

**Purpose**: Verify SCHEMA sections enable TASKS creation
**Type**: Warning

**Requirements**:
- Interface method signatures parseable
- Data schemas compatible with target languages
- Error handling specifications complete

---

### CHECK 9: File Size Limits

**Purpose**: Warn when files exceed recommended size thresholds
**Type**: Warning

**Thresholds**:
- Markdown files: 600 lines maximum (target: 300-500 lines)
- YAML files: 1000 lines maximum

**Warning Messages**:
- `SPEC-W010`: Markdown file exceeds 600 lines
- `SPEC-W011`: YAML file exceeds 1000 lines

---

### CHECK 10: Element ID Format Compliance

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

**Reference**: SPEC_CREATION_RULES.md Section 4.1, [ID_NAMING_STANDARDS.md — Cross-Reference Link Format](../ID_NAMING_STANDARDS.md#cross-reference-link-format-mandatory)

---

## Error Fix Guide

### Quick Fix Matrix

| Error Check | Quick Fix |
|-------------|-----------|
| **CHECK 1** | Fix YAML syntax (indentation, quotes, colons) |
| **CHECK 2** | Add missing metadata fields |
| **CHECK 3** | Add properly formatted TASKS-ready score |
| **CHECK 4** | Replace raw quantitative values with `@threshold: PRD.NN.*` and add `threshold_references` registry + keys |
| **CHECK 5** | Complete traceability tag chain; use `null` only when an upstream artifact type does not exist |
| **CHECK 9** | Reduce file size or accept warning (non-blocking) |
| **CHECK 10** | Replace legacy element IDs (STEP-XXX, IF-XXX, DM-XXX) with unified format `SPEC.NN.TT.SS` |

---

## Quick Reference

### Pre-Commit Validation

```bash
# Validate single SPEC YAML file
python scripts/validate_spec.py docs/10_SPEC/SPEC-01_component_spec/SPEC-01_component_spec.yaml

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
| **Tier 1** | Error | 1-5, 10 | Must fix before commit |
| **Tier 2** | Warning | 6-9 | Recommended to fix |
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
    threshold: null  # missing registry reference despite thresholds in spec
✅ cumulative_tags:
    brd: "BRD.01.01.30"
    prd: "PRD.03.01.02"
    ears: "EARS.01.24.03"
    bdd: "BDD.03.13.01"
    adr: "ADR-NN"
    sys: "SYS.01.25.01"
    req: "REQ.02.26.05"
    threshold: "PRD-03"      # use null only when thresholds not applicable
```

### Mistake #4: CTR Contract Mismatch
```
❌ # CTR-NN references interface that doesn't exist
✅ # Verified CTR-01_api_contract.md exists and matches API spec
```

---

**Maintained By**: Architecture Team, Engineering Team
**Review Frequency**: Updated with SPEC template enhancements
