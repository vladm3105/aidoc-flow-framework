# Feature-Level Traceability Tags: Gap Analysis Report

**Date**: 2025-12-01
**Status**: COMPLETE
**Scope**: Internal feature/requirement ID formats across SDD framework
**Output**: Consolidated recommendations for fixing inconsistencies

---

## Executive Summary

The audit identified **4 critical inconsistencies** in how feature-level IDs are defined and used across the 16-layer SDD framework. These inconsistencies create confusion for document authors and prevent effective automated validation.

### Core Problem

The framework has **two competing paradigms** for internal feature IDs:

| Paradigm | Format | Where Defined | Example |
|----------|--------|---------------|---------|
| **Simple Numeric** | `001`, `002`, `003` | `ID_NAMING_STANDARDS.md` lines 360-381 | `### 001: Feature Name` |
| **Prefixed Compound** | `FR-NNN-NN`, `BO-NNN`, `NFR-NNN` | Various SCHEMA and TEMPLATE files | `FR-022-015`, `BO-001`, `NFR-PERF-001` |

**Both paradigms are valid**, but the framework lacks clear guidance on:
1. Which format to use in which context
2. How to reference features across layers
3. How prefixed formats map between layers

---

## Gap Analysis by Document Type

### Layer 1: BRD (Business Requirements Document)

| Element | Current State | Gap | Severity |
|---------|--------------|-----|----------|
| **Business Objectives** | `BO-NNN` in templates | No schema validation | MEDIUM |
| **Functional Requirements** | `FR-XXX` placeholder | Format undefined | LOW |
| **NFRs** | `NFR-001` through `NFR-046` | Simple format conflicts with EARS categorical | HIGH |

**Files Affected**:
- `BRD-TEMPLATE.md` lines 125-127, 655-748
- `BRD_CREATION_RULES.md` line 1338

### Layer 2: PRD (Product Requirements Document)

| Element | Current State | Gap | Severity |
|---------|--------------|-----|----------|
| **Feature IDs** | Schema: `FR-\d{3}-\d{2,3}` | Conflicts with ID_NAMING_STANDARDS simple format | CRITICAL |
| **User Stories** | `US-NNN` in template | No schema definition | MEDIUM |
| **Cross-Reference** | `@prd: PRD-022:005` | Unclear if `005` is simple or `FR-022-005` | HIGH |

**Files Affected**:
- `PRD_SCHEMA.yaml` lines 151-159
- `PRD_CREATION_RULES.md` lines 797-873 (section 20)
- `PRD-TEMPLATE.md` lines 369-392

### Layer 3: EARS (Easy Approach to Requirements Syntax)

| Element | Current State | Gap | Severity |
|---------|--------------|-----|----------|
| **Statement Types** | `EVENT-`, `STATE-`, `UB-` in TRACEABILITY.md | Not in EARS_SCHEMA.yaml | MEDIUM |
| **NFR Categories** | `NFR-PERF-NNN`, `NFR-SEC-NNN` in template | Conflicts with BRD simple NFR | HIGH |
| **Traceability Tag** | `@prd: PRD-NNN:NNN` in schema | Consistent with standard | OK |

**Files Affected**:
- `EARS_SCHEMA.yaml` lines 146-168 (pattern types only, no ID format)
- `EARS-TEMPLATE.md` lines 142-155
- `TRACEABILITY.md` lines 463-464, 476-491

### Layer 6: SYS (System Requirements)

| Element | Current State | Gap | Severity |
|---------|--------------|-----|----------|
| **Functional Requirements** | Schema: `FR-\d{3}` (3-digit only) | Conflicts with PRD `FR-\d{3}-\d{2,3}` | CRITICAL |
| **NFR Categories** | Schema defines 6 prefixes | Conflicts with BRD simple format | HIGH |

**Files Affected**:
- `SYS_SCHEMA.yaml` lines 203-266

---

## Critical Conflicts Requiring Resolution

### Conflict 1: FR Format Mismatch (CRITICAL)

```
PRD_SCHEMA.yaml:  pattern: "^FR-\\d{3}-\\d{2,3}$"  → FR-001-001, FR-022-15
SYS_SCHEMA.yaml:  pattern: "^FR-\\d{3}$"           → FR-001, FR-042
```

**Impact**: Cannot create consistent cross-layer FR references
**Root Cause**: PRD embeds document number in FR ID; SYS uses standalone sequence

### Conflict 2: Simple vs Prefixed Internal IDs (CRITICAL)

```
ID_NAMING_STANDARDS.md:  "001", "002", "003" (simple numeric)
PRD_SCHEMA.yaml:         "FR-NNN-NN" (prefixed compound)
```

**Impact**: Document authors don't know which format to use
**Root Cause**: ID_NAMING_STANDARDS was updated but schemas weren't aligned

### Conflict 3: NFR Format Inconsistency (HIGH)

```
BRD-TEMPLATE.md:   NFR-001 through NFR-046 (simple)
SYS_SCHEMA.yaml:   NFR-P, NFR-R, NFR-S, NFR-SEC, NFR-O, NFR-M (categorical prefixes)
EARS-TEMPLATE.md:  NFR-PERF-001, NFR-SEC-001 (categorical full)
```

**Impact**: Cannot trace NFRs from BRD→EARS→SYS consistently
**Root Cause**: Each layer independently defined NFR format

### Conflict 4: Cross-Reference Ambiguity (HIGH)

```
ID_NAMING_STANDARDS.md: "@brd: BRD-017:001"  → What is "001"?
                        Is it simple numeric OR FR-017-001 shortened?
```

**Impact**: Validation scripts cannot determine correct format
**Root Cause**: Cross-reference format defined but internal ID format ambiguous

---

## Proposed Resolution: Unified Feature ID Standard

### Design Principles

1. **Document context provides namespace** - No need to embed document ID in feature ID
2. **Simple numeric for internal use** - `001`, `002`, `003` within documents
3. **Prefixes for semantic categorization** - `BO-`, `FR-`, `NFR-`, `US-` indicate type
4. **Cross-reference combines both** - `@type: DOC-NNN:NNN` or `@type: DOC-NNN:PREFIX-NNN`

### Recommended Standard

| Document Type | Internal Feature ID | Cross-Reference Format | Notes |
|---------------|---------------------|------------------------|-------|
| **BRD** | `BO-NNN`, `FR-NNN`, `NFR-NNN` | `@brd: BRD-017:BO-001` | Semantic prefixes retained |
| **PRD** | `NNN` (simple) or `FR-NNN` | `@prd: PRD-022:001` or `@prd: PRD-022:FR-001` | Choice: simple OR prefixed |
| **EARS** | `NNN` (simple) | `@ears: EARS-012:001` | Statement types (EVENT/STATE/UB) are metadata, not IDs |
| **SYS** | `FR-NNN`, `NFR-NNN` | `@sys: SYS-008:FR-001` | Prefixes indicate type |
| **REQ** | `NNN` (simple) | `@req: REQ-045:001` | Already consistent |

### NFR Standardization

**Recommendation**: Use categorical prefixes consistently across ALL layers

| Category | Prefix | BRD Example | EARS Example | SYS Example |
|----------|--------|-------------|--------------|-------------|
| Performance | `NFR-PERF-` | NFR-PERF-001 | NFR-PERF-001 | NFR-PERF-001 |
| Reliability | `NFR-REL-` | NFR-REL-001 | NFR-REL-001 | NFR-REL-001 |
| Scalability | `NFR-SCAL-` | NFR-SCAL-001 | NFR-SCAL-001 | NFR-SCAL-001 |
| Security | `NFR-SEC-` | NFR-SEC-001 | NFR-SEC-001 | NFR-SEC-001 |
| Observability | `NFR-OBS-` | NFR-OBS-001 | NFR-OBS-001 | NFR-OBS-001 |
| Maintainability | `NFR-MAINT-` | NFR-MAINT-001 | NFR-MAINT-001 | NFR-MAINT-001 |

**Rationale**: Consistent prefixes enable automated NFR tracing across layers.

---

## Files Requiring Updates

### Priority 1: Schema Files (Authoritative)

| File | Change Required | Lines |
|------|-----------------|-------|
| `PRD_SCHEMA.yaml` | Remove compound FR pattern OR document as optional | 151-159 |
| `SYS_SCHEMA.yaml` | Align FR pattern with decision | 203-212 |
| `SYS_SCHEMA.yaml` | Standardize NFR category prefixes | 220-266 |

### Priority 2: Naming Standards (Prescriptive)

| File | Change Required | Lines |
|------|-----------------|-------|
| `ID_NAMING_STANDARDS.md` | Add section clarifying prefixed vs simple | 360-381 |
| `ID_NAMING_STANDARDS.md` | Add NFR categorical prefix standard | NEW |
| `ID_NAMING_STANDARDS.md` | Add decision flowchart | NEW |

### Priority 3: Creation Rules (Guidance)

| File | Change Required | Lines |
|------|-----------------|-------|
| `PRD_CREATION_RULES.md` | Update section 20 to align with standard | 797-873 |
| `BRD_CREATION_RULES.md` | Add BO/NFR format rules | ~1338 |
| `EARS_CREATION_RULES.md` | Clarify statement type IDs vs semantic labels | NEW |

### Priority 4: Templates (Examples)

| File | Change Required | Lines |
|------|-----------------|-------|
| `BRD-TEMPLATE.md` | Update NFR examples to categorical | 655-748 |
| `PRD-TEMPLATE.md` | Align feature ID examples | 369-392 |
| `EARS-TEMPLATE.md` | Verify NFR examples use standard prefixes | 142-155 |

### Priority 5: Traceability Docs (Reference)

| File | Change Required | Lines |
|------|-----------------|-------|
| `TRACEABILITY.md` | Update examples to use standard format | 463-491 |
| `COMPLETE_TAGGING_EXAMPLE.md` | Ensure all examples consistent | Throughout |

---

## Implementation Plan

### Phase 1: Decision (Before Any Changes)

**Question 1**: Should PRD use compound `FR-NNN-NN` or simple `NNN`?

| Option | Pros | Cons |
|--------|------|------|
| **Compound** `FR-022-015` | Self-documenting, globally unique | Redundant (doc context provides namespace) |
| **Simple** `001` | Cleaner, matches ID_NAMING_STANDARDS | Requires document context for uniqueness |

**Recommendation**: **Simple `NNN`** - aligns with ID_NAMING_STANDARDS principle that document context provides namespace.

**Question 2**: Should NFRs use categorical prefixes everywhere?

| Option | Pros | Cons |
|--------|------|------|
| **Categorical** `NFR-PERF-001` | Clear categorization, traceable | More verbose |
| **Simple** `NFR-001` | Shorter | Loses category information |

**Recommendation**: **Categorical** - enables automated categorization and cross-layer tracing.

### Phase 2: Schema Updates

1. Update `PRD_SCHEMA.yaml` - Change pattern to allow simple OR remove compound requirement
2. Update `SYS_SCHEMA.yaml` - Standardize NFR prefixes to full categorical format
3. Add `BRD_SCHEMA.yaml` section for BO format validation

### Phase 3: Documentation Updates

1. Update `ID_NAMING_STANDARDS.md` with:
   - Decision flowchart: "When to use prefixed vs simple"
   - NFR categorical prefix standard table
   - Cross-reference format clarification

2. Update `PRD_CREATION_RULES.md` section 20 to align with new standard

3. Update templates with consistent examples

### Phase 4: Validation

1. Run existing validation scripts
2. Create new validation for NFR categorical prefixes
3. Update `FEATURE_ID_AUDIT_REPORT.md` with resolution status

---

## Success Criteria

| Metric | Target | Validation Method |
|--------|--------|-------------------|
| Schema consistency | 100% aligned patterns | Manual review |
| ID_NAMING_STANDARDS complete | All formats documented | Checklist |
| Template examples consistent | All use standard format | grep validation |
| Cross-reference format clear | Unambiguous interpretation | Manual review |
| Validation scripts pass | No false positives | Automated test |

---

## Appendix: Current vs Proposed Formats

### Current State (Inconsistent)

```
BRD:  BO-001, FR-001, NFR-001 (no schema)
PRD:  FR-022-015 (schema), US-001 (template only)
EARS: EVENT-001 (conceptual), NFR-PERF-001 (template)
SYS:  FR-001 (schema), NFR-P/R/S/SEC/O/M (schema categories)
REQ:  001 (consistent)
```

### Proposed State (Unified)

```
BRD:  BO-NNN, FR-NNN, NFR-PERF-NNN (categorical)  → @brd: BRD-017:BO-001
PRD:  NNN (simple)                                 → @prd: PRD-022:001
EARS: NNN (simple)                                 → @ears: EARS-012:001
SYS:  FR-NNN, NFR-PERF-NNN (categorical)          → @sys: SYS-008:FR-001
REQ:  NNN (simple)                                 → @req: REQ-045:001
```

---

**Report Status**: COMPLETE
**Next Action**: User approval of recommendations before implementing fixes
**Estimated Fix Effort**: 2-3 hours for all Priority 1-3 changes
