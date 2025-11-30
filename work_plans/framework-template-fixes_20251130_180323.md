# Implementation Plan - Framework Template Fixes

**Created**: 2025-11-30 18:03:23 EST
**Status**: Ready for Implementation
**Framework Version**: v2.2

## Objective

Fix identified inconsistencies in the docs_flow_framework templates to achieve 100% readiness for new projects. Currently at 95% readiness with 4 fixes needed.

## Context

A comprehensive framework assessment was conducted reviewing:
- All 13 SDD layer templates
- 24 validation scripts
- 22 skills
- Template consistency across artifacts

**Overall Verdict**: Framework is PRODUCTION-READY but has minor documentation inconsistencies that should be fixed.

## Task List

### Pending
- [ ] Fix 1: CTR layer number (6→9) in CTR-TEMPLATE.md:69
- [ ] Fix 2: Remove duplicate authority block in BDD-TEMPLATE.feature:41-51
- [ ] Fix 3: Add ICON workflow position clarification in ICON-TEMPLATE.md
- [ ] Fix 4: Align version number in ai_dev_flow/README.md (2.0→2.2)

### Not Required
- [x] Fix 5: BRD authority blockquote - ALREADY PRESENT (lines 29-32)

## Implementation Guide

### Prerequisites
- Access to `/opt/data/docs_flow_framework/ai_dev_flow/`
- No dependencies between fixes (can be done in any order)

### Execution Steps

#### Fix 1: CTR Layer Number
**File**: `/opt/data/docs_flow_framework/ai_dev_flow/CTR/CTR-TEMPLATE.md`
**Line**: 69
**Change**:
```
OLD: **CTR (API Contracts)** ← YOU ARE HERE (Layer 6 - Interface Layer)
NEW: **CTR (API Contracts)** ← YOU ARE HERE (Layer 9 - Interface Layer)
```

#### Fix 2: BDD Duplicate Authority Block
**File**: `/opt/data/docs_flow_framework/ai_dev_flow/BDD/BDD-TEMPLATE.feature`
**Action**: Remove lines 41-51 (duplicate authority block)
```
DELETE LINES 41-51:
# =============================================================================
# 📋 DOCUMENT AUTHORITY: PRIMARY STANDARD for BDD structure
# =============================================================================
# This template is the SINGLE SOURCE OF TRUTH for BDD artifact structure.
# All other documents DERIVE from this template:
#   - BDD_SCHEMA.yaml (DERIVATIVE - machine-readable validation rules)
#   - BDD_CREATION_RULES.md (DERIVATIVE - human-readable creation guidance)
#   - BDD_VALIDATION_RULES.md (DERIVATIVE - post-creation validation checklist)
#
# CONFLICT RESOLUTION: When any document conflicts with this template,
# this template wins. Update the conflicting document to match.
# =============================================================================
```

#### Fix 3: ICON Workflow Position Clarification
**File**: `/opt/data/docs_flow_framework/ai_dev_flow/ICON/ICON-TEMPLATE.md`
**Action**: Add new section after "## 1. Pre-Creation Checklist" (after line 62)
```markdown
## 1.1 ICON Workflow Position

**ICON (Layer 11)** ← Creates integration contracts **parallel after TASKS**
- **Input**: TASKS (code generation specifications)
- **Output**: Type-safe contracts for IPLAN source code implementation
- **Purpose**: Enable parallel development by defining stable interfaces

```
TASKS (Layer 11) ──┬──> ICON (Layer 11, parallel)
                   │         │
                   │         ▼
                   └──> IPLAN (Layer 12) uses ICON contracts
```
```

#### Fix 4: Version Alignment
**File**: `/opt/data/docs_flow_framework/ai_dev_flow/README.md`
**Line**: 17
**Change**:
```
OLD: **Version**: 2.0 | **Last Updated**: 2025-11-13
NEW: **Version**: 2.2 | **Last Updated**: 2025-11-30
```

### Verification

After fixes, run:
```bash
# Verify CTR fix
grep -n "Layer 9" /opt/data/docs_flow_framework/ai_dev_flow/CTR/CTR-TEMPLATE.md

# Verify BDD fix (should not find duplicate)
grep -n "PRIMARY STANDARD for BDD" /opt/data/docs_flow_framework/ai_dev_flow/BDD/BDD-TEMPLATE.feature | wc -l
# Expected: 1 (not 2)

# Verify ICON fix
grep -n "Workflow Position" /opt/data/docs_flow_framework/ai_dev_flow/ICON/ICON-TEMPLATE.md

# Verify version alignment
grep "Version.*2.2" /opt/data/docs_flow_framework/ai_dev_flow/README.md
```

## References

- **Plan file**: `/home/ya/.claude/plans/generic-frolicking-toast.md`
- **Framework root**: `/opt/data/docs_flow_framework/`
- **Templates**: `/opt/data/docs_flow_framework/ai_dev_flow/`

## Assessment Summary

| Category | Status |
|----------|--------|
| Templates (13 layers) | ✅ Complete |
| Validation scripts (24) | ✅ Comprehensive |
| Skills (22) | ✅ Ready |
| Template consistency | 95% → 100% after fixes |
