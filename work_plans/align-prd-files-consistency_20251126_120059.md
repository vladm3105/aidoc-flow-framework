# Implementation Plan - Align PRD Template and Rules Files for Consistency

**Created**: 2025-11-26 12:00:59 EST
**Status**: Ready for Implementation
**Project**: docs_flow_framework

## Objective

Resolve inconsistencies between PRD-TEMPLATE.md, PRD_CREATION_RULES.md, and PRD_VALIDATION_RULES.md to establish comprehensive, aligned documentation framework for Product Requirements Documents.

## Context

### Analysis Findings

**Critical Issues Identified**:
1. **PRD_VALIDATION_RULES.md is empty** (14 lines YAML only, no validation content)
2. **Scoring ambiguity**: Template shows both SYS-Ready and EARS-Ready scores, but creation rules unclear about requirements
3. **Section numbering mismatch**: Template uses unnumbered sections, creation rules reference numbered sections
4. **Missing sections in rules**: User Stories & User Roles, Customer-Facing Content & Messaging exist in template but not in creation rules

**User Decisions**:
- Validation structure: Define PRD-appropriate comprehensive validation (not copy BRD structure)
- Scoring: **Both SYS-Ready and EARS-Ready scores required** (95% targets)
- Section numbering: **Document Control as Section 0, then numbered sections 1-16**
- User Stories: **Mandatory** - definitions only (detailed behavior in EARS/BDD)
- Customer-Facing Content: **Mandatory** - full section required

### Files to Modify

1. `/opt/data/docs_flow_framework/ai_dev_flow/PRD/PRD_VALIDATION_RULES.md` (CREATE content)
2. `/opt/data/docs_flow_framework/ai_dev_flow/PRD/PRD_CREATION_RULES.md` (UPDATE)
3. `/opt/data/docs_flow_framework/ai_dev_flow/PRD/PRD-TEMPLATE.md` (UPDATE)

## Task List

### Phase 1: Create PRD_VALIDATION_RULES.md Content
- [ ] Design PRD-specific validation structure (~400-500 lines)
- [ ] Section 1: Overview (purpose, scope, validation approach)
- [ ] Section 2: Document Control Validation
  - [ ] YAML frontmatter requirements
  - [ ] Dual scoring validation (SYS-Ready + EARS-Ready both at 95%)
  - [ ] Version control fields
- [ ] Section 3: Section-by-Section Validation (Sections 0-16)
  - [ ] Section 0: Document Control
  - [ ] Section 1: Executive Summary
  - [ ] Section 2: Product Vision & Goals
  - [ ] Section 3: Market Context & User Needs
  - [ ] Section 4: Success Metrics & KPIs
  - [ ] Section 5: Scope & Requirements
  - [ ] Section 6: User Stories & User Roles (MANDATORY - definitions only)
  - [ ] Section 7: Functional Requirements
  - [ ] Section 8: Customer-Facing Content & Messaging (MANDATORY)
  - [ ] Section 9: Acceptance Criteria
  - [ ] Section 10: Non-Functional Requirements
  - [ ] Section 11: Constraints & Assumptions
  - [ ] Section 12: Dependencies
  - [ ] Section 13: Risk Assessment
  - [ ] Section 14: Timeline & Milestones
  - [ ] Section 15: Downstream Artifacts (Architecture Decision Requirements)
  - [ ] Section 16: Traceability
- [ ] Section 4: Quality Gates (pre-commit validation checklist)
- [ ] Section 5: Common Issues & Troubleshooting
- [ ] Add PRD-specific differentiators from BRD validation

### Phase 2: Update PRD_CREATION_RULES.md
- [ ] Update Required Sections list (lines 58-75)
  - [ ] Add Section 0: Document Control
  - [ ] Insert Section 6: User Stories & User Roles
  - [ ] Insert Section 8: Customer-Facing Content & Messaging
  - [ ] Renumber all subsequent sections (Acceptance Criteria → 9, etc.)
  - [ ] Update final section to 16: Traceability
- [ ] Update Document Control section (lines 78-113)
  - [ ] Change position to "Section 0, at the very top"
  - [ ] Explicitly require both SYS-Ready and EARS-Ready scores at 95%
- [ ] Add User Stories section specification
  - [ ] Purpose: Define roles and high-level stories
  - [ ] Scope: Definitions only (detailed behavior in EARS/BDD)
  - [ ] Required content: role definitions, story titles, prioritization
  - [ ] Validation: Stories must map to Functional Requirements
- [ ] Add Customer-Facing Content section specification
  - [ ] Purpose: Customer communication strategy
  - [ ] Required content: positioning, messaging, feature descriptions, UI content
  - [ ] Validation: Align with Product Vision (Section 2)
- [ ] Update all section number references throughout document
- [ ] Update Quick Reference (lines 308-322) with new section count

### Phase 3: Update PRD-TEMPLATE.md
- [ ] Add explicit section numbering to all headings
  - [ ] Line 24: `## 0. Document Control`
  - [ ] Line 42: `## 1. Executive Summary`
  - [ ] Continue through `## 16. Traceability`
- [ ] Verify Document Control table (lines 26-38)
  - [ ] Confirm `| SYS-Ready Score | 95% |` present
  - [ ] Confirm `| EARS-Ready Score | 95% |` present
- [ ] Add User Stories section note (lines 245-321)
  - [ ] Add callout: "**Purpose**: Define user roles and high-level stories. Detailed behavioral scenarios will be specified in EARS and BDD artifacts."
- [ ] Update any references to section count (15 → 17 sections)

### Phase 4: Cross-Validation
- [ ] Verify all three files aligned on section numbering (0-16)
- [ ] Verify dual scoring requirements consistent across files
- [ ] Verify User Stories scope (definitions only) consistent
- [ ] Verify Customer-Facing Content mandatory in all files
- [ ] Verify all section references updated
- [ ] Run validation script if exists: `./scripts/validate_prd_template.sh`

### Phase 5: Optional Enhancement
- [ ] Create validation script: `scripts/validate_prd_template.sh`
  - [ ] Check YAML frontmatter present
  - [ ] Check section numbering 0-16 sequential
  - [ ] Check Document Control has both scores
  - [ ] Check all required sections present
  - [ ] Check traceability tags format valid
  - [ ] Check no ADR number references in Section 15

## Implementation Guide

### Prerequisites
- Access to `/opt/data/docs_flow_framework/ai_dev_flow/PRD/` directory
- Read access to BRD_VALIDATION_RULES.md for reference patterns (but don't copy directly)
- Understanding of PRD vs BRD validation differences

### Key Principles

**PRD Validation Differentiators** (vs BRD):
- Product-centric validation (measurable outcomes, user impact)
- User story validation (role definition, scope boundaries for EARS/BDD)
- Customer messaging validation (clarity, consistency, brand alignment)
- Architecture decision requirements validation (ADR prompts, not ADR references)
- Focus on "what to build" not "why to build" (BRD covers "why")

**User Stories Scope**:
- PRD: Role definitions and high-level story titles only
- EARS/BDD: Detailed behavioral scenarios, acceptance criteria, test cases
- Rationale: Prevent duplication, maintain clear layer separation

**Customer-Facing Content Scope**:
- Required for all PRDs (product launch communication strategy)
- Includes: positioning, messaging pillars, feature descriptions, UI content
- Must align with Product Vision (Section 2)

### Execution Steps

#### Step 1: Create PRD_VALIDATION_RULES.md
1. Open `/opt/data/docs_flow_framework/ai_dev_flow/PRD/PRD_VALIDATION_RULES.md`
2. Keep existing YAML frontmatter (lines 1-14)
3. Add title: `title: "PRD Validation Rules"`
4. Add comprehensive validation content (~450 lines):
   - Section 1: Overview (validation philosophy for PRDs)
   - Section 2: Document Control Validation (dual scoring emphasis)
   - Section 3: Section-by-Section Validation (0-16 with PRD-specific criteria)
   - Section 4: Quality Gates (pre-commit checklist)
   - Section 5: Common Issues (FAQ and troubleshooting)

#### Step 2: Update PRD_CREATION_RULES.md
1. Open `/opt/data/docs_flow_framework/ai_dev_flow/PRD/PRD_CREATION_RULES.md`
2. Update lines 58-75 (Required Sections):
   - Insert Section 0: Document Control (before current Section 1)
   - Insert Section 6: User Stories & User Roles (after Scope & Requirements)
   - Insert Section 8: Customer-Facing Content & Messaging (after Functional Requirements)
   - Renumber subsequent sections (Acceptance Criteria → 9, Traceability → 16)
3. Update lines 78-113 (Document Control section):
   - Line 81: "Section 0, at the very top of the PRD"
   - Lines 86-91: Add both scoring requirements with 95% targets
4. Add User Stories specification (after line 113)
5. Add Customer-Facing Content specification (after Functional Requirements)
6. Update all section references throughout document
7. Update Quick Reference (lines 308-322)

#### Step 3: Update PRD-TEMPLATE.md
1. Open `/opt/data/docs_flow_framework/ai_dev_flow/PRD/PRD-TEMPLATE.md`
2. Add section numbers to all headings:
   - Line 24: `## 0. Document Control`
   - Line 42: `## 1. Executive Summary`
   - Continue pattern through `## 16. Traceability`
3. Verify Document Control table has both scores (lines 26-38)
4. Add User Stories scope note (around line 245):
   ```markdown
   > **Scope Note**: This section defines user roles and high-level user stories. Detailed behavioral scenarios, acceptance criteria, and test cases will be specified in downstream EARS and BDD artifacts to prevent duplication and maintain clear layer separation.
   ```
5. Update any "15 sections" references to "17 sections (0-16)"

#### Step 4: Cross-File Validation
1. Compare section lists across all three files
2. Verify numbering consistency (0-16)
3. Verify dual scoring requirements in all files
4. Verify User Stories scope description consistent
5. Verify Customer-Facing Content marked mandatory
6. Search for any orphaned section references

### Verification

**PRD_VALIDATION_RULES.md**:
- [ ] File has 400+ lines of content (not just YAML)
- [ ] Title field populated: `title: "PRD Validation Rules"`
- [ ] Section 2 explicitly requires both SYS-Ready and EARS-Ready scores
- [ ] Section 3 covers all 17 sections (0-16)
- [ ] Section 6 validation clarifies "definitions only" scope
- [ ] Section 8 validation marks Customer-Facing Content as mandatory
- [ ] PRD-specific validation criteria distinct from BRD

**PRD_CREATION_RULES.md**:
- [ ] Required sections list shows 17 sections (0-16) in order
- [ ] Section 0: Document Control listed first
- [ ] Section 6: User Stories & User Roles present with scope note
- [ ] Section 8: Customer-Facing Content & Messaging present
- [ ] Document Control section requires both scores at 95%
- [ ] All section number references updated
- [ ] Quick Reference updated

**PRD-TEMPLATE.md**:
- [ ] All section headings numbered (## 0. through ## 16.)
- [ ] Document Control is Section 0
- [ ] Traceability is Section 16
- [ ] Document Control table has both score rows
- [ ] User Stories section has scope note about EARS/BDD
- [ ] Section count references updated to 17

**Cross-File Alignment**:
- [ ] All three files agree on section numbering (0-16)
- [ ] All three files require both SYS-Ready and EARS-Ready scores
- [ ] All three files clarify User Stories scope (definitions only)
- [ ] All three files mark Customer-Facing Content as mandatory
- [ ] Section titles consistent across files

### Expected Outcomes

**File Sizes** (approximate):
- PRD_VALIDATION_RULES.md: ~450 lines (current: 14 lines)
- PRD_CREATION_RULES.md: ~470 lines (current: 330 lines, +140 lines)
- PRD-TEMPLATE.md: ~868 lines (current: 838 lines, +30 lines)

**Quality Improvements**:
- Complete validation framework for PRDs
- Eliminated scoring ambiguity (dual scoring required)
- Standardized section numbering across all files
- Clear layer separation (PRD definitions vs EARS/BDD details)
- Comprehensive coverage of all template sections in rules

**Consistency Metrics**:
- Section numbering alignment: 100% (0-16 in all files)
- Required sections alignment: 100% (17 sections in all files)
- Scoring requirements alignment: 100% (both scores at 95%)
- User Stories scope alignment: 100% (definitions only)
- Customer-Facing Content alignment: 100% (mandatory)

## References

### Related Files
- `/opt/data/docs_flow_framework/ai_dev_flow/PRD/PRD-TEMPLATE.md` (838 lines)
- `/opt/data/docs_flow_framework/ai_dev_flow/PRD/PRD_CREATION_RULES.md` (330 lines)
- `/opt/data/docs_flow_framework/ai_dev_flow/PRD/PRD_VALIDATION_RULES.md` (14 lines - empty)
- `/opt/data/docs_flow_framework/ai_dev_flow/BRD/BRD_VALIDATION_RULES.md` (reference only)

### Documentation
- `/opt/data/docs_flow_framework/ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md`
- `/opt/data/docs_flow_framework/ai_dev_flow/ID_NAMING_STANDARDS.md`
- `/opt/data/docs_flow_framework/ai_dev_flow/METADATA_TAGGING_GUIDE.md`

### Analysis Report
- Detailed inconsistency analysis completed 2025-11-26
- 3 critical issues, 5 moderate issues, 4 minor issues identified
- 5 strengths confirmed (ID standards, principles, ADR guidelines, traceability, document control core fields)

## Notes

### Critical Decisions
- **Validation structure**: PRD-appropriate (not BRD copy) - focus on product-centric validation
- **Dual scoring mandatory**: Both SYS-Ready and EARS-Ready at 95% targets
- **Section 0**: Document Control positioned as first section (before numbered sections 1-16)
- **User Stories scope**: Definitions only in PRD, detailed behavior in EARS/BDD
- **Customer-Facing Content**: Mandatory section for all PRDs

### Constraints
- Maximum file size: 100,000 tokens (400KB) per global rules
- No subjective language in validation rules
- Imperative verb forms for procedures
- Measurable validation criteria only

### Risk Mitigation
- Phase-based approach allows verification at each step
- Cross-validation phase catches alignment issues
- Reference to BRD validation for patterns (but not direct copy)
- Clear differentiation between PRD and BRD validation focus
