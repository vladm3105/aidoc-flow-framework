# Implementation Plan - BRD/PRD Template Refactoring & Layer Separation

**Created**: 2025-11-26 09:08:09 EST
**Status**: Ready for Implementation
**Project**: docs_flow_framework
**Location**: `/opt/data/docs_flow_framework/`

## Objective

Refactor BRD and PRD templates to enforce proper Layer 1 (business) vs Layer 2 (product) separation, reduce BRD token count by 39% (24.5K→15K tokens), eliminate project-specific document IDs, and align creation/validation rules with updated template structure.

## Context

### Problem Statement
1. **BRD template approaching token limits** (~24,469 tokens) and mixing business (Layer 1) with product (Layer 2) content
2. **Missing creation/validation rules** for Sections 4 (Stakeholders), 5 (User Stories), 17 (Traceability), and Appendices K-O
3. **Hardcoded document IDs** (BRD-001, FR-001, etc.) creating project-specific coupling
4. **Inconsistent section counts** between CREATION_RULES (17 sections) and VALIDATION_RULES (19 sections)

### User Requirements (from conversation)
1. Move User Stories and Stakeholder Stories to PRD (high-level in BRD only)
2. Remove specific document IDs (BRD-001, BRD-015) - use generalized placeholders
3. FR/NFR defined at high level in BRD, detailed in PRD
4. Move product-related appendices to PRD (e.g., Appendix N: Customer Communication Templates)
5. Add stakeholder analysis and user story creation rules to PRD/EARS/BDD

### Key Decisions
- **Layer Separation**: BRD = business objectives/capabilities, PRD = user personas/stories/roles
- **Token Budget**: Keep all templates under 50,000 tokens (BRD target: ~15K)
- **Teaching Materials**: Extract to separate reference guides (FR_EXAMPLES_GUIDE.md)
- **ID Generalization**: Use BRD-NNN, FR-NNN patterns instead of specific numbers

### Analysis Summary
- Current BRD: 18,352 words, ~24,469 tokens
- Current PRD: 3,389 words, ~4,518 tokens
- Projected BRD: ~15,000 tokens (-39%)
- Projected PRD: ~7,500 tokens (+66%, still well within limits)

## Gap Analysis: Missing Rules

### Critical Gaps (4 areas)
1. **Section 4 (Stakeholders)**: NO creation guidance, NO validation
2. **Section 5 (User Stories)**: Minimal creation guidance, limited validation
3. **Section 17 (Traceability)**: NO creation guidance for Health Score calculation
4. **Appendices K-O**: NO creation or validation rules for specialized appendices

### High-Priority Gaps (4 areas)
- Technology Prerequisites (3.6): Missing methodology for platform-inherited conditions
- Mandatory Conditions (3.7): No guidance on distinguishing mandatory vs optional
- Business Objectives: Missing SMART criteria writing methodology
- Appendix Validation: No checks for required appendices by BRD type

### Structural Issues
- **Inconsistency**: CREATION_RULES references 17 sections, but template has 19
- **Misalignment**: Executive Summary pattern (3 paragraphs) vs validation (6 elements)

## Task List

### Phase 1: Content Redistribution - User Stories & Stakeholders
- [ ] Move BRD Section 5 (User Stories) → PRD Section 3.4-3.5
  - [ ] Extract BRD Sections 5.1-5.5 (User Story Format, Primary Stories, Operational Stories, Summary, BO Mapping)
  - [ ] Insert into PRD Section 3 "Target Audience & User Personas"
  - [ ] Create PRD subsections: 3.4 User Stories, 3.5 User Story to Feature Mapping
  - [ ] Update user story guidance: derive from business objectives (BRD) + user personas (PRD)
  - [ ] Add cross-reference: `@brd: BRD-NNN:BO-XXX` for traceability
- [ ] Move BRD Section 6.4 (User Roles & Permissions) → PRD Section 5.4
  - [ ] Extract role definition table from BRD
  - [ ] Insert into PRD Section 5 "Functional Requirements" as subsection 5.4
- [ ] Refactor BRD Section 4 (Stakeholders)
  - [ ] Simplify to high-level stakeholder groups only (remove detailed personas)
  - [ ] Rename: "Section 4: Stakeholder Groups & Business Impact"
  - [ ] Keep stakeholder analysis table (business-level concern)
- [ ] **Token Impact**: BRD -1,500 tokens, PRD +1,200 tokens

### Phase 2: Appendix Reorganization - Teaching Materials
- [ ] Extract Appendix C (FR Examples) → New Reference Guide
  - [ ] Create: `ai_dev_flow/BRD/FR_EXAMPLES_GUIDE.md`
  - [ ] Content: 5 detailed FR examples (Simple, Complex, Multi-Partner, Regulatory, AI/ML)
  - [ ] Update BRD Appendix C to single-line reference link
- [ ] Extract Appendix B (Content Exclusions) → EARS Guidelines
  - [ ] Move to EARS-TEMPLATE.md Section 5.6 "Business vs Technical Requirements Boundary"
  - [ ] Add quick self-check questions to BDD-TEMPLATE.feature header
- [ ] **Token Impact**: BRD -7,500 tokens (largest savings!)

### Phase 3: Product Appendices Relocation
- [ ] Move Appendix E (Data Requirements) → PRD Section 7 "Data Requirements & Mapping"
- [ ] Move Appendix F (UI Mockups) → PRD Section 8 "UI/UX Design References"
- [ ] Move Appendix N (Customer Communication Templates) → PRD Section 9 "Customer-Facing Content"
- [ ] Keep Business Appendices in BRD:
  - [ ] Verify Appendix A, D, H, I, J remain in BRD
  - [ ] Verify Appendix K (Fee Schedule), L (Partner SLA), M (Regulatory Matrix), O (Business Metrics) remain
- [ ] **Token Impact**: BRD -1,500 tokens, PRD +1,500 tokens

### Phase 4: Document ID Generalization
- [ ] Generalize BRD Template ID References
  - [ ] Replace `BRD-001` → `[Platform_BRD-001]` or `BRD-NNN` in instructional text
  - [ ] Replace `FR-001, FR-002, FR-003` → `FR-NNN` in template sections
  - [ ] Replace `US-001, US-002` → `US-NNN`
  - [ ] Keep specific IDs in FR_EXAMPLES_GUIDE.md only (teaching examples)
- [ ] Generalize PRD Template (already uses BRD-NNN, PRD-NNN - verify consistency)
- [ ] Update EARS/BDD Templates
  - [ ] Use `@brd: BRD-NNN:FR-NNN` pattern
  - [ ] Use `@prd: PRD-NNN:FR-NNN` pattern
- [ ] Document ID Conventions
  - [ ] Update `ID_NAMING_STANDARDS.md` with generic placeholder patterns
  - [ ] Document semantic category labels ([Platform_BRD], [Feature_BRD])
- [ ] **Token Impact**: Neutral (same content, better portability)

### Phase 5: Creation & Validation Rules Updates
- [ ] Update BRD_CREATION_RULES.md
  - [ ] Add Section 4 guidance: Stakeholder Groups (simplified, business-level only)
  - [ ] Remove Section 5 guidance (User Stories moved to PRD)
  - [ ] Add Appendix K-M creation guidance (Fee Schedule, Partner SLA, Regulatory Matrix)
  - [ ] Update section count: "19 Sections" → "18 Sections"
  - [ ] Fix Executive Summary alignment (reconcile 3-paragraph pattern with 6 elements)
- [ ] Update BRD_VALIDATION_RULES.md
  - [ ] Update CHECK 1: Validate 18 sections (not 19)
  - [ ] Remove CHECK 20: User Stories validation (moved to PRD)
  - [ ] Remove CHECK 21: User Roles validation (moved to PRD)
  - [ ] Add CHECK 25-27: Specialized appendix validation by BRD type
  - [ ] Update CHECK references to generalized IDs
- [ ] Create/Update PRD_CREATION_RULES.md
  - [ ] Add Section 3.4-3.5: User Stories creation guidance
    - [ ] User story derivation from business objectives
    - [ ] Story ID numbering (US-001+)
    - [ ] FR linkage methodology
    - [ ] Business objective mapping process
  - [ ] Add Section 5.4: User Roles & Permissions guidance
    - [ ] Role identification methodology
    - [ ] Permission matrix construction
  - [ ] Add Stakeholder Analysis guidance:
    - [ ] Stakeholder identification methodology
    - [ ] Interest/Influence level criteria (High/Med/Low)
    - [ ] Engagement strategy patterns
- [ ] Create/Update PRD_VALIDATION_RULES.md
  - [ ] Add CHECK for User Stories format (US-NNN pattern)
  - [ ] Add CHECK for User Story to FR traceability
  - [ ] Add CHECK for User Roles table completeness

### Phase 6: SDD Guide & Cross-References Update
- [ ] Update SPEC_DRIVEN_DEVELOPMENT_GUIDE.md
  - [ ] Section "Layer 1 (BRD)": Clarify business-level FRs, stakeholder groups (NOT user stories/roles)
  - [ ] Section "Layer 2 (PRD)": Expand to include user stories, user roles, product features
  - [ ] Section "Principles - Complete Traceability": Add note on user story derivation (BO→US→FR)
  - [ ] Update token limit guidance: "BRD optimized to ~15K tokens through modular appendices"
- [ ] Update Template Cross-References
  - [ ] BRD Section 1.4: Add note "User stories defined in downstream PRD"
  - [ ] PRD Section 3.4: Add note "Derived from Business Objectives in upstream BRD-NNN"
  - [ ] EARS Section 7: Update traceability pattern to include user stories
  - [ ] BDD header: Update cumulative tags to include `@user-story: US-NNN`
- [ ] Create Migration Guide (optional)
  - [ ] Document: `TEMPLATE_MIGRATION_GUIDE.md`
  - [ ] Content: How to convert old BRDs (with user stories) to new structure
  - [ ] Mapping table: Old Section → New Template Location

### Validation (After Each Phase)
- [ ] Run markdown linter on modified templates
- [ ] Verify YAML frontmatter validity
- [ ] Check all cross-references resolve
- [ ] Validate token counts using Read tool
- [ ] Test template with sample BRD/PRD creation
- [ ] Update METADATA_TAGGING_GUIDE.md if needed

## Implementation Guide

### Prerequisites
- Access to: `/opt/data/docs_flow_framework/ai_dev_flow/`
- Files to modify:
  - `BRD/BRD-TEMPLATE.md`
  - `BRD/BRD_CREATION_RULES.md`
  - `BRD/BRD_VALIDATION_RULES.md`
  - `PRD/PRD-TEMPLATE.md`
  - `PRD/PRD_CREATION_RULES.md` (may need to create)
  - `PRD/PRD_VALIDATION_RULES.md` (may need to create)
  - `EARS/EARS-TEMPLATE.md`
  - `BDD/BDD-TEMPLATE.feature`
  - `SPEC_DRIVEN_DEVELOPMENT_GUIDE.md`
  - `ID_NAMING_STANDARDS.md`
- New files to create:
  - `BRD/FR_EXAMPLES_GUIDE.md`
  - `TEMPLATE_MIGRATION_GUIDE.md` (optional)

### Execution Steps (Recommended Order)

#### PHASE 2 FIRST (Largest Token Savings, Minimal Dependencies)
1. Extract Appendix C to `BRD/FR_EXAMPLES_GUIDE.md`
2. Extract Appendix B to `EARS-TEMPLATE.md` Section 5.6
3. Update BRD Appendices B & C to reference links
4. **Verify**: BRD token count reduced by ~7,500 tokens

#### PHASE 1 SECOND (Move User Stories - Requires PRD Updates)
5. Create PRD Sections 3.4-3.5 (User Stories)
6. Extract BRD Section 5 content to PRD
7. Create PRD Section 5.4 (User Roles)
8. Extract BRD Section 6.4 content to PRD
9. Simplify BRD Section 4 (Stakeholders)
10. **Verify**: Cross-references between BRD/PRD work correctly

#### PHASE 3 THIRD (Move Product Appendices)
11. Create PRD Sections 7, 8, 9 for relocated appendices
12. Move BRD Appendices E, F, N to PRD
13. **Verify**: All appendix cross-references updated

#### PHASE 4 FOURTH (Generalize IDs)
14. Find/replace specific IDs in BRD template
15. Find/replace specific IDs in PRD template
16. Update EARS/BDD traceability patterns
17. Update `ID_NAMING_STANDARDS.md`
18. **Verify**: No project-specific IDs remain in templates

#### PHASE 5 FIFTH (Update Rules)
19. Update BRD_CREATION_RULES.md (remove Section 5, update Section 4, add appendix guidance)
20. Update BRD_VALIDATION_RULES.md (remove CHECKs 20-21, add CHECKs 25-27, update CHECK 1)
21. Create/update PRD_CREATION_RULES.md (add user story + role guidance)
22. Create/update PRD_VALIDATION_RULES.md (add user story + role checks)
23. **Verify**: Rules align with updated template structure

#### PHASE 6 LAST (Update SDD Guide)
24. Update SPEC_DRIVEN_DEVELOPMENT_GUIDE.md Layer descriptions
25. Update all template cross-references
26. Create TEMPLATE_MIGRATION_GUIDE.md (optional)
27. **Verify**: All documentation consistent

### Verification Checklist

#### Token Count Verification
```bash
# Check BRD token count (target: ~15,000 tokens)
wc -w /opt/data/docs_flow_framework/ai_dev_flow/BRD/BRD-TEMPLATE.md

# Check PRD token count (target: ~7,500 tokens)
wc -w /opt/data/docs_flow_framework/ai_dev_flow/PRD/PRD-TEMPLATE.md
```

#### Markdown Linting
```bash
cd /opt/data/docs_flow_framework/ai_dev_flow
npx markdownlint-cli2 BRD/BRD-TEMPLATE.md
npx markdownlint-cli2 PRD/PRD-TEMPLATE.md
npx markdownlint-cli2 EARS/EARS-TEMPLATE.md
```

#### Cross-Reference Validation
- [ ] All `[BRD-NNN]` references resolve
- [ ] All `[PRD-NNN]` references resolve
- [ ] All `@brd` tags use correct format
- [ ] All `@prd` tags use correct format

#### Content Verification
- [ ] No user stories in BRD template
- [ ] No user roles in BRD template
- [ ] User stories present in PRD template
- [ ] Stakeholder analysis simplified in BRD
- [ ] Product appendices moved to PRD
- [ ] Teaching materials extracted to separate guides

## Expected Outcomes

### Final Token Counts
| Template | Before | After | Change |
|----------|--------|-------|--------|
| **BRD-TEMPLATE.md** | ~24,469 | ~15,000 | -39% |
| **PRD-TEMPLATE.md** | ~4,518 | ~7,500 | +66% |
| **EARS-TEMPLATE.md** | ~6,409 | ~9,000 | +40% |
| **BDD-TEMPLATE.feature** | ~400 | ~600 | +50% |
| **FR_EXAMPLES_GUIDE.md** | 0 | ~5,000 | NEW |

### Layer Separation Compliance
- **BRD (Layer 1)**: Business objectives, stakeholder groups, business-level FRs/NFRs
- **PRD (Layer 2)**: User personas, user stories, user roles, product-level FRs/NFRs
- **EARS (Layer 3)**: Formal requirements with business/product boundary guidance
- **BDD (Layer 4)**: Test scenarios with full cumulative traceability

### ID Generalization
- No hardcoded document numbers (BRD-001, FR-001) in templates
- Generic placeholders (BRD-NNN, FR-NNN) used throughout
- Semantic labels ([Platform_BRD], [Feature_BRD]) for categorization

### Rules Alignment
- Creation rules match template structure (18 sections in BRD)
- Validation checks cover all template requirements
- PRD rules include user story and role guidance
- Stakeholder analysis methodology documented

## References

### Related Files
- `/opt/data/docs_flow_framework/ai_dev_flow/BRD/BRD-TEMPLATE.md`
- `/opt/data/docs_flow_framework/ai_dev_flow/BRD/BRD_CREATION_RULES.md`
- `/opt/data/docs_flow_framework/ai_dev_flow/BRD/BRD_VALIDATION_RULES.md`
- `/opt/data/docs_flow_framework/ai_dev_flow/PRD/PRD-TEMPLATE.md`
- `/opt/data/docs_flow_framework/ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md`
- `/opt/data/docs_flow_framework/ai_dev_flow/ID_NAMING_STANDARDS.md`

### Documentation
- METADATA_TAGGING_GUIDE.md
- TOOL_OPTIMIZATION_GUIDE.md
- Layer separation principles in SPEC_DRIVEN_DEVELOPMENT_GUIDE.md

### Previous Analysis
- Gap analysis output from Plan agent (72K tokens)
- Template structure analysis showing current sections and token counts
- Cross-reference pattern analysis

## Notes

### Critical Decisions Made
1. **User Stories = Layer 2 (PRD)**: User stories are product artifacts derived from business objectives, not business requirements themselves
2. **Teaching Materials = Separate Guides**: FR examples and content exclusion rules moved to standalone reference documents
3. **Stakeholder Analysis = Simplified in BRD**: Keep high-level stakeholder groups in BRD, detailed user personas in PRD
4. **ID Generalization Required**: Remove all project-specific document IDs to make templates portable

### Risk Mitigation
- Phase 2 first minimizes risk (extracting content to new files, not cross-template moves)
- Validate token counts after each phase
- Maintain git commits after each phase for rollback capability
- Test templates with sample documents before finalizing

### Estimated Effort
- Phase 1: 2-3 hours (complex content moves with traceability updates)
- Phase 2: 1-2 hours (extract to new files)
- Phase 3: 1 hour (straightforward appendix moves)
- Phase 4: 1 hour (find/replace with validation)
- Phase 5: 2-3 hours (rules require careful alignment)
- Phase 6: 1 hour (documentation updates)
- **Total**: 8-11 hours of focused work

### Success Metrics
- [ ] BRD token count ≤ 15,000 tokens
- [ ] PRD token count ≤ 10,000 tokens
- [ ] All templates ≤ 50,000 token limit
- [ ] Zero hardcoded document IDs in templates
- [ ] All creation/validation rules aligned with templates
- [ ] Layer 1/Layer 2 separation enforced
- [ ] All cross-references resolve correctly
- [ ] Markdown linting passes with no errors
