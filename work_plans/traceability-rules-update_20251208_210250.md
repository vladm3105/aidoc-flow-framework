# Implementation Plan - Traceability Rules Update

**Created**: 2025-12-08 21:02:50 EST
**Status**: Ready for Implementation

## Objective

Update the docs_flow_framework to clearly define and enforce traceability rules:
1. **Upstream Traceability** - REQUIRED for all documents except BRD
2. **Downstream Traceability** - OPTIONAL, only to existing documents
3. **No-TBD Rule** - Strictly enforced (no placeholders in actual documents)
4. **BRD Exception** - BRD may have OPTIONAL upstream only to other BRDs or business description documents, may have downstream

## Context

### Current State
The framework already has:
- Strong No-TBD rule in TRACEABILITY.md (lines 92-96)
- Upstream artifact verification warnings in all templates
- Both upstream AND downstream sections in traceability matrices

### Key Decision
Downstream Traceability sections will be **kept but marked as OPTIONAL** (only for existing documents).

### Traceability Rules to Document

| Rule | Description |
|------|-------------|
| **Upstream Required** | All documents MUST reference existing upstream documents (except BRD) |
| **Downstream Optional** | Documents MAY reference existing downstream documents |
| **No-TBD Strict** | NEVER use placeholder IDs (TBD, XXX, NNN) in actual documents |
| **Existing Only** | Both upstream and downstream links MUST reference existing documents |
| **BRD Exception** | BRD is the root - may have OPTIONAL upstream only to other BRDs or business description documents, may have downstream |

## Task List

### Pending

- [ ] Update TRACEABILITY.md - Add explicit "Traceability Rules" section near top
- [ ] Update validation script - Change downstream check from required to optional
- [ ] Update 13 traceability matrix templates - Add REQUIRED/OPTIONAL labels to sections
- [ ] Update README files - Clarify rules per artifact type
- [ ] Update skills files - Ensure consistent messaging

## Implementation Guide

### Prerequisites
- Access to `/opt/data/docs_flow_framework/`
- Understanding of SDD 16-layer workflow

### Execution Steps

#### Step 1: Update Core Documentation (TRACEABILITY.md)
**File**: `/opt/data/docs_flow_framework/ai_dev_flow/TRACEABILITY.md`

Add a new "Traceability Rules" section after the "Core Principle" section with the rules table above.

#### Step 2: Update Validation Script
**File**: `/opt/data/docs_flow_framework/ai_dev_flow/scripts/validate_traceability_matrix_enforcement.py`

Change lines 83-86 to make downstream check a warning (optional) instead of required.

#### Step 3: Update 13 Traceability Matrix Templates

Add REQUIRED/OPTIONAL labels to section headers:

| File | Upstream Section | Downstream Section |
|------|-----------------|-------------------|
| `ai_dev_flow/BRD/BRD-000_TRACEABILITY_MATRIX-TEMPLATE.md` | OPTIONAL (to other BRDs) | OPTIONAL |
| `ai_dev_flow/PRD/PRD-000_TRACEABILITY_MATRIX-TEMPLATE.md` | REQUIRED | OPTIONAL |
| `ai_dev_flow/EARS/EARS-000_TRACEABILITY_MATRIX-TEMPLATE.md` | REQUIRED | OPTIONAL |
| `ai_dev_flow/BDD/BDD-000_TRACEABILITY_MATRIX-TEMPLATE.md` | REQUIRED | OPTIONAL |
| `ai_dev_flow/ADR/ADR-000_TRACEABILITY_MATRIX-TEMPLATE.md` | REQUIRED | OPTIONAL |
| `ai_dev_flow/SYS/SYS-000_TRACEABILITY_MATRIX-TEMPLATE.md` | REQUIRED | OPTIONAL |
| `ai_dev_flow/REQ/REQ-000_TRACEABILITY_MATRIX-TEMPLATE.md` | REQUIRED | OPTIONAL |
| `ai_dev_flow/IMPL/IMPL-000_TRACEABILITY_MATRIX-TEMPLATE.md` | REQUIRED | OPTIONAL |
| `ai_dev_flow/CTR/CTR-000_TRACEABILITY_MATRIX-TEMPLATE.md` | REQUIRED | OPTIONAL |
| `ai_dev_flow/SPEC/SPEC-000_TRACEABILITY_MATRIX-TEMPLATE.md` | REQUIRED | OPTIONAL |
| `ai_dev_flow/TASKS/TASKS-000_TRACEABILITY_MATRIX-TEMPLATE.md` | REQUIRED | OPTIONAL |
| `ai_dev_flow/IPLAN/IPLAN-000_TRACEABILITY_MATRIX-TEMPLATE.md` | REQUIRED | OPTIONAL |
| `ai_dev_flow/ICON/ICON-000_TRACEABILITY_MATRIX-TEMPLATE.md` | REQUIRED | OPTIONAL |

#### Step 4: Update README/Guide Files

| File | Change |
|------|--------|
| `ai_dev_flow/BRD/README.md` | Clarify BRD upstream is OPTIONAL (to other BRDs), downstream OPTIONAL |
| `ai_dev_flow/PRD/README.md` | Clarify upstream REQUIRED, downstream OPTIONAL |
| `ai_dev_flow/CTR/README.md` | Update section 9.2 Downstream Traceability as OPTIONAL |
| `ai_dev_flow/QUICK_REFERENCE.md` | Update traceability quick reference |
| `ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md` | Update traceability section description |

#### Step 5: Update Skills Files

| File | Change |
|------|--------|
| `.claude/skills/trace-check/SKILL.md` | Update validation rules |
| `.claude/skills/doc-flow/SHARED_CONTENT.md` | Update traceability description |
| `.claude/agents/requirements-analyst.md` | Update traceability matrix framework |

### Verification
- Validate no "TBD" or placeholder IDs remain in templates
- Run validation script to confirm it passes with optional downstream
- Check all templates have correct REQUIRED/OPTIONAL labels

## References

- Core traceability guide: `/opt/data/docs_flow_framework/ai_dev_flow/TRACEABILITY.md`
- Validation script: `/opt/data/docs_flow_framework/ai_dev_flow/scripts/validate_traceability_matrix_enforcement.py`
- Plan file: `/home/ya/.claude/plans/composed-swinging-treasure.md`
