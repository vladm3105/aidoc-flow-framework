# Implementation Plan - PRD Files Alignment for 19-Section Structure

**Created**: 2025-11-26 14:21:40 EST
**Status**: Ready for Implementation
**Source Work Plan**: `/opt/data/docs_flow_framework/work_plans/align-prd-files-consistency-implementation_20251126_120500.md`

## Objective

Establish complete consistency across PRD documentation files by:
1. Creating comprehensive validation rules (~450 lines)
2. Adding missing sections and implementing explicit numbering (19 sections: 0-18)
3. Enforcing dual scoring requirements (SYS-Ready + EARS-Ready ≥95%)
4. Clarifying User Stories scope (PRD-level definitions vs EARS/BDD details)
5. Making Customer-Facing Content mandatory

## Context

### Critical Decision Made

**Section Count Resolution**: Original work plan specified sections 0-16 (17 total), but PRD-TEMPLATE.md currently has 19 sections. **Decision: Use 19 sections (0-18)** to match current reality and keep Traceability and References sections.

### Current State Analysis

**PRD_VALIDATION_RULES.md**:
- Current: 14 lines (YAML only, completely empty)
- Target: ~450 lines with 5 comprehensive validation sections
- Gap: Missing all validation content

**PRD_CREATION_RULES.md**:
- Current: 329 lines with sections 1-16 listed
- Missing: Section 0 (Document Control), Section 6 (User Stories), Section 8 (Customer-Facing Content)
- Issue: Duplicate Section 10 (Traceability + Business Objectives)
- Target: ~470 lines with sections 0-18 properly sequenced

**PRD-TEMPLATE.md**:
- Current: 837 lines with all sections present but NO numbering
- Has User Stories (line 246) and Customer-Facing Content (line 358)
- Has dual scoring in Document Control (lines 37-38) ✅
- Target: ~868 lines with explicit section numbers 0-18

### Consistency Gaps Identified

| Metric | Current | Target |
|--------|---------|--------|
| Section numbering consistency | 0% | 100% |
| Dual scoring presence | 66% | 100% |
| User Stories scope alignment | 33% | 100% |
| Customer-Facing Content mandatory | 33% | 100% |
| Overall consistency | ~60% | 100% |

### Key Constraints

**Language Requirements** (from CLAUDE.md):
- Use objective, factual language only
- No promotional content or subjective claims
- Imperative verb forms for procedures
- Measurable validation criteria only

**Layer Separation** (SDD Framework):
- **PRD (Layer 2)**: User role definitions, high-level story titles, product capabilities
- **EARS (Layer 3)**: Detailed behavioral scenarios with technical specifications
- **BDD (Layer 4)**: Test cases with Given-When-Then acceptance criteria

## Task List

### Phase 1: Create PRD_VALIDATION_RULES.md Content
- [ ] Section 1: Overview (~80 lines)
  - Validation philosophy (product-centric focus)
  - PRD differentiators (vs BRD and SYS/EARS)
  - Measurable outcomes emphasis
- [ ] Section 2: Document Control Validation (~100 lines)
  - Dual scoring requirements validation
  - Metadata completeness checks
  - Threshold enforcement (≥90% for both scores)
- [ ] Section 3: Section-by-Section Validation (~180 lines)
  - Validation criteria for all 19 sections (0-18)
  - User Stories scope validation (definitions only)
  - Customer-Facing Content completeness (MANDATORY)
  - Architecture Decision Requirements (no ADR-XXX references)
- [ ] Section 4: Quality Gates (~50 lines)
  - Pre-commit checklist
  - Both scores at ≥90%
  - All 19 sections present
- [ ] Section 5: Common Issues & Troubleshooting (~40 lines)
  - Common validation errors
  - Root causes and fixes

### Phase 2: Update PRD_CREATION_RULES.md
- [ ] Fix duplicate Section 10 (lines 250, 271)
  - Renumber second "Section 10" to "Section 11"
- [ ] Insert Section 0: Document Control (~30 lines)
  - Insert after line 43, before Section 1
  - Include dual scoring requirements table
- [ ] Update Section 2 list (lines 60-75)
  - Expand from 16 to 19 sections
  - Add Section 0, Section 6, Section 8
- [ ] Insert Section 6: User Stories & User Roles (~50 lines)
  - Insert after Section 5 (Product Requirements Principles)
  - Include scope clarification note (PRD vs EARS/BDD)
- [ ] Insert Section 8: Customer-Facing Content (~60 lines)
  - Insert after Section 7 (was Section 6)
  - Mark as MANDATORY
- [ ] Renumber subsequent sections
  - Section 6→7 (Architecture Decision Requirements)
  - Section 7→9 (ADR Relationship Guidelines)
  - Section 8→10 (SYS-Ready Scoring)
  - Section 9→11 (EARS-Ready Scoring)
  - Section 10→12 (Traceability)
  - Section 10→13 (Business Objectives - was duplicate)
  - Section 11→14 (Quality Gates)
  - Section 12→15 (Additional Requirements)
- [ ] Update Table of Contents (lines 28-42)
  - Add new sections 0, 6, 8
  - Update all section numbers
- [ ] Update Quick Reference (lines 308-329)
  - Add critical requirements summary
  - Emphasize dual scoring and 19-section structure

### Phase 3: Update PRD-TEMPLATE.md
- [ ] Add section numbers to all headers (19 total)
  - Line 24: `## Document Control` → `## 0. Document Control`
  - Line 40: `## Executive Summary` → `## 1. Executive Summary`
  - Line 58: `## Problem Statement` → `## 2. Problem Statement`
  - Line 95: `## Target Audience & User Personas` → `## 3. Target Audience & User Personas`
  - Line 121: `## Success Metrics (KPIs)` → `## 4. Success Metrics (KPIs)`
  - Line 156: `## Goals & Objectives` → `## 5. Goals & Objectives`
  - Line 246: `## User Stories & User Roles` → `## 6. User Stories & User Roles`
  - Line 180: `## Scope & Requirements` → `## 7. Scope & Requirements`
  - Line 358: `## Customer-Facing Content & Messaging` → `## 8. Customer-Facing Content & Messaging (MANDATORY)`
  - Line 324: `## Functional Requirements` → `## 9. Functional Requirements`
  - Line 428: `## Acceptance Criteria` → `## 10. Acceptance Criteria`
  - Line 483: `## Constraints & Assumptions` → `## 11. Constraints & Assumptions`
  - Line 521: `## Risk Assessment` → `## 12. Risk Assessment`
  - Line 547: `## Success Definition` → `## 13. Success Definition`
  - Line 576: `## Stakeholders & Communication` → `## 14. Stakeholders & Communication`
  - Line 601: `## Implementation Approach` → `## 15. Implementation Approach`
  - Line 635: `## Budget & Resources` → `## 16. Budget & Resources`
  - Line 654: `## Traceability` → `## 17. Traceability`
  - Line 798: `## References` → `## 18. References`
- [ ] Add User Stories scope note (after line 246)
  - Layer separation explanation
  - PRD scope: definitions only
  - EARS/BDD scope: behavioral details
- [ ] Add Customer-Facing Content MANDATORY designation (line 358)
  - Add (MANDATORY) to header
  - Add purpose statement
- [ ] Verify Document Control dual scoring (lines 37-38)
  - Already correct ✅

### Phase 4: Cross-File Validation
- [ ] Section numbering consistency (0-18)
  - Verify all 3 files reference sections 0-18
  - Verify section titles match exactly
- [ ] Dual scoring presence (95% targets)
  - Verify PRD_VALIDATION_RULES.md enforces both scores
  - Verify PRD_CREATION_RULES.md documents both scores
  - Verify PRD-TEMPLATE.md has both scores
- [ ] User Stories scope alignment
  - Verify PRD_VALIDATION_RULES.md validates scope note
  - Verify PRD_CREATION_RULES.md defines layer separation
  - Verify PRD-TEMPLATE.md includes scope note
- [ ] Customer-Facing Content mandatory status
  - Verify PRD_VALIDATION_RULES.md enforces as ERROR
  - Verify PRD_CREATION_RULES.md marks as MANDATORY
  - Verify PRD-TEMPLATE.md shows (MANDATORY)
- [ ] YAML frontmatter validation
  - Update PRD_VALIDATION_RULES.md title
  - Verify artifact_type: PRD in all files
  - Verify layer: 2 in all files

### Phase 5: Documentation & Commit
- [ ] Create completion report
  - Document consistency metrics (target: 100%)
  - File statistics (line counts before/after)
- [ ] Stage changes
  - `git add ai_dev_flow/PRD/PRD_VALIDATION_RULES.md`
  - `git add ai_dev_flow/PRD/PRD_CREATION_RULES.md`
  - `git add ai_dev_flow/PRD/PRD-TEMPLATE.md`
- [ ] Create git commit with comprehensive message
- [ ] Update source work plan status

## Implementation Guide

### Prerequisites

**Required Access**:
- `/opt/data/docs_flow_framework/ai_dev_flow/PRD/` directory (write access)
- Git repository with write permissions

**Reference Documents to Read**:
1. `/opt/data/docs_flow_framework/ai_dev_flow/BRD/BRD_VALIDATION_RULES.md` (1,531 lines - structure pattern)
2. `/opt/data/docs_flow_framework/ai_dev_flow/BRD/BRD-TEMPLATE.md` (Document Control structure)
3. Current PRD files (already analyzed)

### Execution Steps

#### Phase 1: Create PRD_VALIDATION_RULES.md (~450 lines)

**Step 1.1**: Read reference document
```bash
# Read BRD validation rules for structure pattern
cat ai_dev_flow/BRD/BRD_VALIDATION_RULES.md
```

**Step 1.2**: Create Section 1 (Overview)
- Lines 15-94: ~80 lines
- Content: Validation philosophy, PRD differentiators, measurable outcomes
- Pattern: Model after BRD_VALIDATION_RULES.md overview section

**Step 1.3**: Create Section 2 (Document Control Validation)
- Lines 95-194: ~100 lines
- Content: 11 required fields, dual scoring format validation, threshold enforcement
- Include CHECK 1, CHECK 2, CHECK 3 with error messages and fixes

**Step 1.4**: Create Section 3 (Section-by-Section Validation)
- Lines 195-374: ~180 lines
- Content: Validation for all 19 sections (0-18)
- Special focus: Section 6 (User Stories scope), Section 8 (Customer-Facing mandatory)
- Include CHECK 4, CHECK 5, CHECK 6, CHECK 7

**Step 1.5**: Create Section 4 (Quality Gates)
- Lines 375-424: ~50 lines
- Content: Pre-commit checklist, validation script commands, quality thresholds table

**Step 1.6**: Create Section 5 (Common Issues)
- Lines 425-464: ~40 lines
- Content: Top 5 common issues with symptoms, causes, and fixes

**Verification**: File should be ~450 lines with 5 major sections

---

#### Phase 2: Update PRD_CREATION_RULES.md (+141 lines)

**Step 2.1**: Read current file
```bash
cat ai_dev_flow/PRD/PRD_CREATION_RULES.md
```

**Step 2.2**: Fix duplicate Section 10
- Line 271: Change `## 10. Business Objectives` → `## 11. Business Objectives`

**Step 2.3**: Insert Section 0 (Document Control)
- Insert after line 43 (after `---`)
- Insert before line 44 (before `## 1. File Organization`)
- Content: ~30 lines with dual scoring table and requirements

**Step 2.4**: Update Section 2 list (Required Sections)
- Lines 60-75: Replace with 19-section list
- Add Section 0, Section 6, Section 8
- Include brief descriptions for each

**Step 2.5**: Insert Section 6 (User Stories & User Roles)
- Insert after Section 5 (~line 135)
- Content: ~50 lines with scope note

**Step 2.6**: Insert Section 8 (Customer-Facing Content)
- Insert after new Section 7 (~line 325)
- Content: ~60 lines, marked MANDATORY

**Step 2.7**: Renumber sections
- Update 8 section headers (6→7, 7→9, 8→10, 9→11, 10→12, 10→13, 11→14, 12→15)

**Step 2.8**: Update Table of Contents (lines 28-42)
- Add Sections 0, 6, 8
- Update all section numbers

**Step 2.9**: Update Quick Reference (lines 308-329)
- Add critical requirements summary
- Emphasize 19-section structure and dual scoring

**Verification**: File should be ~470 lines with sections 0-15 (plus unnumbered sections)

---

#### Phase 3: Update PRD-TEMPLATE.md (+31 lines)

**Step 3.1**: Read current file
```bash
cat ai_dev_flow/PRD/PRD-TEMPLATE.md
```

**Step 3.2**: Add section numbers to all 19 headers
- Use Edit tool to add numbers: `## 0.`, `## 1.`, ... `## 18.`
- 19 edits total (one per section)

**Step 3.3**: Add User Stories scope note
- Insert after line 246 (Section 6 header)
- Content: Layer separation note (PRD vs EARS/BDD)

**Step 3.4**: Add Customer-Facing Content MANDATORY designation
- Line 358: Update header to include `(MANDATORY)`
- Add purpose statement

**Step 3.5**: Verify dual scoring
- Lines 37-38: Confirm both scores present (already correct)

**Verification**: File should be ~868 lines with all sections numbered 0-18

---

#### Phase 4: Cross-File Validation

**Step 4.1**: Create validation checklist
```bash
# Search for section references across all files
grep -n "## [0-9]" ai_dev_flow/PRD/PRD-TEMPLATE.md
grep -n "Section [0-9]" ai_dev_flow/PRD/PRD_CREATION_RULES.md
grep -n "Section [0-9]" ai_dev_flow/PRD/PRD_VALIDATION_RULES.md
```

**Step 4.2**: Verify section titles match
- Compare all 19 section titles across 3 files
- Ensure exact matches (case-sensitive)

**Step 4.3**: Verify dual scoring
- Search for "SYS-Ready Score" in all 3 files
- Search for "EARS-Ready Score" in all 3 files
- Verify format: `✅ NN% (Target: ≥90%)`

**Step 4.4**: Verify User Stories scope
- Check PRD_VALIDATION_RULES.md Section 3 validates scope note
- Check PRD_CREATION_RULES.md Section 6 defines layer separation
- Check PRD-TEMPLATE.md Section 6 includes scope note

**Step 4.5**: Verify Customer-Facing Content
- Check PRD_VALIDATION_RULES.md enforces as ERROR (blocking)
- Check PRD_CREATION_RULES.md marks as MANDATORY
- Check PRD-TEMPLATE.md shows (MANDATORY) in header

**Step 4.6**: Validate YAML frontmatter
```bash
# Check YAML syntax
head -15 ai_dev_flow/PRD/PRD_VALIDATION_RULES.md
head -15 ai_dev_flow/PRD/PRD_CREATION_RULES.md
head -15 ai_dev_flow/PRD/PRD-TEMPLATE.md
```

**Verification**: All validation checks pass at 100%

---

#### Phase 5: Documentation & Commit

**Step 5.1**: Create completion report
- File: `/opt/data/docs_flow_framework/work_plans/prd-files-alignment-complete_20251126_HHMMSS.md`
- Content: Consistency metrics, before/after statistics, validation results

**Step 5.2**: Stage changes
```bash
cd /opt/data/docs_flow_framework
git add ai_dev_flow/PRD/PRD_VALIDATION_RULES.md
git add ai_dev_flow/PRD/PRD_CREATION_RULES.md
git add ai_dev_flow/PRD/PRD-TEMPLATE.md
git status
```

**Step 5.3**: Create commit
```bash
git commit -m "$(cat <<'EOF'
docs: align PRD files for complete consistency (19 sections)

- Create PRD_VALIDATION_RULES.md with comprehensive validation criteria (~450 lines)
- Update PRD_CREATION_RULES.md with sections 0, 6, 8 and renumbering (329→470 lines)
- Update PRD-TEMPLATE.md with explicit section numbering 0-18 (837→868 lines)
- Establish dual scoring (SYS-Ready + EARS-Ready at 95%)
- Clarify User Stories scope (definitions only, EARS/BDD for details)
- Mark Customer-Facing Content as mandatory (Section 8)
- Fix duplicate Section 10 in PRD_CREATION_RULES.md
- Update section count from 0-16 to 0-18 (19 total sections)

Resolves inconsistencies identified in work plan.
Achieves 100% consistency across PRD documentation.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

**Step 5.4**: Verify commit
```bash
git log -1 --stat
git diff HEAD~1
```

**Verification**: Commit created successfully with all files

---

### Verification Checkpoints

**After Phase 1**:
- [ ] PRD_VALIDATION_RULES.md exists and is ~450 lines
- [ ] Contains 5 main sections (Overview, Document Control, Section-by-Section, Quality Gates, Common Issues)
- [ ] Product-centric validation criteria present
- [ ] Dual scoring requirements emphasized

**After Phase 2**:
- [ ] PRD_CREATION_RULES.md is ~470 lines
- [ ] Sections 0, 6, 8 present
- [ ] All sections numbered 0-15 (in creation rules structure)
- [ ] No duplicate section numbers
- [ ] Table of Contents updated
- [ ] Quick Reference updated

**After Phase 3**:
- [ ] PRD-TEMPLATE.md is ~868 lines
- [ ] All 19 section headers numbered 0-18
- [ ] User Stories scope note added
- [ ] Customer-Facing Content marked (MANDATORY)
- [ ] Document Control has both scores

**After Phase 4**:
- [ ] Section numbering 100% consistent (0-18)
- [ ] Dual scoring 100% present (95% targets)
- [ ] User Stories scope 100% aligned
- [ ] Customer-Facing Content 100% mandatory
- [ ] Section titles 100% matching
- [ ] YAML frontmatter valid

**After Phase 5**:
- [ ] Completion report created
- [ ] Git commit created with all 3 files
- [ ] All changes committed to repository
- [ ] Source work plan updated to "Completed" status

---

## Expected Outcomes

### File Statistics

| File | Current Lines | Target Lines | Change |
|------|---------------|--------------|--------|
| PRD_VALIDATION_RULES.md | 14 | 450 | +436 |
| PRD_CREATION_RULES.md | 329 | 470 | +141 |
| PRD-TEMPLATE.md | 837 | 868 | +31 |
| **Total** | **1,180** | **1,788** | **+608** |

### Consistency Metrics

| Metric | Before | After | Target |
|--------|--------|-------|--------|
| Section numbering consistency | 0% | 100% | 100% |
| Dual scoring presence | 66% | 100% | 100% |
| User Stories scope alignment | 33% | 100% | 100% |
| Customer-Facing Content mandatory | 33% | 100% | 100% |
| Section title matching | ~85% | 100% | 100% |
| **Overall Consistency** | **~60%** | **100%** | **100%** |

### Critical Requirements Achieved

All PRD files will enforce:
- ✅ 19 sections (0-18) with explicit numbering
- ✅ Dual scoring at 95% (SYS-Ready + EARS-Ready)
- ✅ User Stories scope note (PRD-level definitions only)
- ✅ Customer-Facing Content MANDATORY for all PRDs
- ✅ No ADR-XXX forward references (topics only)
- ✅ Complete section-by-section validation criteria
- ✅ Pre-commit quality gates

---

## References

### Files to Modify
- `/opt/data/docs_flow_framework/ai_dev_flow/PRD/PRD_VALIDATION_RULES.md`
- `/opt/data/docs_flow_framework/ai_dev_flow/PRD/PRD_CREATION_RULES.md`
- `/opt/data/docs_flow_framework/ai_dev_flow/PRD/PRD-TEMPLATE.md`

### Reference Documents (Read-Only)
- `/opt/data/docs_flow_framework/ai_dev_flow/BRD/BRD_VALIDATION_RULES.md` (structure pattern)
- `/opt/data/docs_flow_framework/ai_dev_flow/BRD/BRD-TEMPLATE.md` (Document Control structure)
- `/opt/data/docs_flow_framework/ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md` (SDD framework)

### Related Documentation
- `/opt/data/docs_flow_framework/ai_dev_flow/ID_NAMING_STANDARDS.md`
- `/opt/data/docs_flow_framework/ai_dev_flow/METADATA_TAGGING_GUIDE.md`

### Previous Work
- Source work plan: `/opt/data/docs_flow_framework/work_plans/align-prd-files-consistency_20251126_120059.md`
- Implementation work plan: `/opt/data/docs_flow_framework/work_plans/align-prd-files-consistency-implementation_20251126_120500.md`
- Related BRD alignment work completed previously

---

## Section Numbering Reference (0-18)

For quick reference during implementation:

| # | Section Title |
|---|---------------|
| 0 | Document Control |
| 1 | Executive Summary |
| 2 | Problem Statement |
| 3 | Target Audience & User Personas |
| 4 | Success Metrics (KPIs) |
| 5 | Goals & Objectives |
| 6 | User Stories & User Roles |
| 7 | Scope & Requirements |
| 8 | Customer-Facing Content & Messaging (MANDATORY) |
| 9 | Functional Requirements |
| 10 | Acceptance Criteria |
| 11 | Constraints & Assumptions |
| 12 | Risk Assessment |
| 13 | Success Definition |
| 14 | Stakeholders & Communication |
| 15 | Implementation Approach |
| 16 | Budget & Resources |
| 17 | Traceability |
| 18 | References |

---

**Plan Complete**: Ready for implementation execution in new context window.
