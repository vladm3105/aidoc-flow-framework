---
title: "SPEC MVP Validation Rules"
tags:
  - validation-rules
  - layer-9-artifact
  - shared-architecture
custom_fields:
  document_type: validation-rules
  artifact_type: SPEC
  layer: 9
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

### CHECK 1b: Flat YAML Structure ⭐ NEW

**Purpose**: Ensure SPEC uses flat structure with top-level keys (not nested under `spec_document` or similar wrapper)
**Type**: Error (blocking)

**Requirements**:
- SPEC content must be at root level (flat structure)
- Top-level keys must include: `metadata`, `traceability`, `req_implementations`
- NO wrapper keys like `spec_document`, `spec`, `document`, or `specification`

**Valid Structure (Flat)**:
```yaml
id: component_name
summary: Component description
metadata:
  version: "1.0.0"
  status: "draft"
traceability:
  upstream_sources: ...
req_implementations: ...
architecture: ...
interfaces: ...
```

**Invalid Structure (Nested)**:
```yaml
spec_document:  # ❌ WRONG - wrapper key not allowed
  metadata:
    version: "1.0.0"
  traceability: ...
```

**Validation Logic**:
1. Parse YAML and get top-level keys
2. If `spec_document`, `spec`, `document`, or `specification` is a top-level key → Error
3. Verify `metadata` or `traceability` exists at root level

**Error Message**: `❌ SPEC-E001b: Invalid nested structure - SPEC must use flat YAML structure (no spec_document wrapper)`

**Rationale**: Flat structure ensures consistent parsing across all SPEC files and enables uniform TASKS code generation. Nested structures break tooling expectations and create inconsistent validation paths.

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
  adr: "ADR-NN"               # Document-level reference (no sub-ID, or null if absent)
  sys: "SYS.NN.EE.SS"         # Unified dot notation for sub-ID references (or null if absent)
  req: "REQ.NN.EE.SS"         # Unified dot notation for sub-ID references (or null if absent)
  ctr: "CTR-NN"               # API Contract reference (or null if CTR file does not exist)
  threshold: "PRD-NN"         # Threshold registry document reference (or null if registry not applicable)
```

### CHECK 5b: CTR Contract Validation (Conditional) ⭐ NEW

**Purpose**: Verify CTR reference when corresponding CTR file exists
**Type**: Warning (non-blocking, but recommended)

**Validation Logic**:
1. Extract SPEC number from filename (e.g., SPEC-01 → 01)
2. Check if `docs/08_CTR/CTR-01_*.yaml` exists
3. If CTR exists AND `cumulative_tags.ctr` is `null` → Warning
4. If CTR does not exist AND `cumulative_tags.ctr` is not `null` → Error (invalid reference)

**Warning Message**: `⚠️ SPEC-W012: CTR-NN exists but cumulative_tags.ctr is null - should reference CTR-NN`
**Error Message**: `❌ SPEC-E012: cumulative_tags.ctr references CTR-NN but file does not exist`

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
- Markdown files: 500 lines soft limit (target: 300-500 lines)
- YAML files: 1000 lines HARD limit (Universal Trigger)

**Warning Messages**:
- `SPEC-W010`: Markdown file exceeds 500 lines
- `SPEC-E011`: YAML file exceeds 1000 lines (MUST SPLIT)

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
| **CHECK 1b** | Remove `spec_document` wrapper - move all nested content to root level |
| **CHECK 2** | Add missing metadata fields |
| **CHECK 3** | Add properly formatted TASKS-ready score |
| **CHECK 4** | Replace raw quantitative values with `@threshold: PRD.NN.*` and add `threshold_references` registry + keys |
| **CHECK 5** | Complete traceability tag chain; use `null` only when an upstream artifact type does not exist |
| **CHECK 5b** | If CTR-NN exists in `docs/08_CTR/`, add `ctr: "CTR-NN"` to cumulative_tags |
| **CHECK 9** | Reduce file size or accept warning (non-blocking) |
| **CHECK 10** | Replace legacy element IDs (STEP-XXX, IF-XXX, DM-XXX) with unified format `SPEC.NN.TT.SS` |

---

## Quick Reference

### Pre-Commit Validation

```bash
# Validate single SPEC YAML file
python scripts/validate_spec.py docs/09_SPEC/SPEC-01_component_spec/SPEC-01_component_spec.yaml

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
| **Tier 1** | Error | 1, 1b, 2-5, 10 | Must fix before commit |
| **Tier 2** | Warning | 5b, 6-9 | Recommended to fix |
| **Tier 3** | Info | - | No action required |

**Note**: CHECK 5b (CTR validation) is a Warning - missing CTR reference won't block commit but should be addressed.

---

## Common Mistakes

### Mistake #1: Invalid YAML Syntax
```
❌ version: '1.0.0  # Missing closing quote
✅ version: "1.0.0"  # Proper quotes
```

### Mistake #1b: Nested Structure (spec_document wrapper)
```yaml
❌ # WRONG - nested under spec_document wrapper
spec_document:
  metadata:
    version: "1.0.0"
  traceability: ...
  req_implementations: ...

✅ # CORRECT - flat structure at root level
metadata:
  version: "1.0.0"
traceability: ...
req_implementations: ...
```

**Fix**: Move all content from under `spec_document:` to the root level. Remove the `spec_document:` key entirely and dedent all nested content by one level.

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
    ctr: "CTR-01"             # reference if CTR file exists, null otherwise
    threshold: "PRD-03"       # use null only when thresholds not applicable
```

### Mistake #4: Missing CTR Reference When CTR Exists
```
❌ # CTR-01_iam.yaml exists in docs/08_CTR/ but SPEC-01 has:
cumulative_tags:
    ctr: null  # WRONG - CTR file exists

✅ # Check for CTR file first, then reference it:
cumulative_tags:
    ctr: "CTR-01"  # Reference the existing CTR contract
```

### Mistake #5: CTR Contract Mismatch
```
❌ # CTR-NN references interface that doesn't exist
✅ # Verified CTR-01_iam.yaml exists and matches API spec
```

---

**Maintained By**: Architecture Team, Engineering Team
**Review Frequency**: Updated with SPEC template enhancements
