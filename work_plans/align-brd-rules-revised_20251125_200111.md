# Implementation Plan - Align BRD Rules Documents with Template (Revised)

**Created**: 2025-11-25 20:01:11 EST
**Status**: Ready for Implementation
**Original Plan**: align-brd-rules-with-template_20251125_195137.md

## Objective

Update BRD_CREATION_RULES.md and BRD_VALIDATION_RULES.md to achieve 100% alignment with BRD-TEMPLATE.md by addressing verified gaps, adding missing sections, and resolving consistency issues.

## Context

### Analysis Phase Completed

Performed comprehensive analysis using Plan agent comparing three BRD framework documents:
- **BRD-TEMPLATE.md** (authoritative template, 2,837 lines, 19 numbered sections)
- **BRD_CREATION_RULES.md** (creation guidelines)
- **BRD_VALIDATION_RULES.md** (validation checklist, currently 18 CHECKs)

### Key Findings from Analysis

**Document Structure Verified**:
- Template has 19 numbered sections (Sections 1-19)
- All 19 sections are mandatory (no optional sections in main numbering)
- Appendices B and C are supplementary (outside main section numbering)
- Workflow diagram sections 3.5.4-3.5.5 exist but are unstaged in git

**BRD_CREATION_RULES.md Gaps (Verified)**:
1. Document Control field count: 6 listed (should be 7, missing PRD-Ready Score)
2. Executive Summary: EXISTS at Section 2.2 lines 76-110 but needs verification for completeness
3. Section 5 (User Stories): Entirely missing from creation rules
4. Sections 3.5.4-3.5.5 (Workflow Diagrams): Not documented
5. Section 15.5 (Approval and Sign-off): Not documented
6. Section 17 (Traceability): Present but incomplete, needs enhancement
7. Section count claim: States "17 Required Sections" (should be 19)

**BRD_VALIDATION_RULES.md Gaps (Verified)**:
1. CHECK 1: Lists sections 1-16 only (missing 17-19)
2. No CHECK for Executive Summary structure validation
3. No CHECK for User Stories section (Section 5)
4. No CHECK for Workflow Diagrams (Sections 3.5.4-3.5.5)
5. No CHECK for Traceability Matrix completeness
6. No CHECK for Approval section (Section 15.5)
7. Glossary validation doesn't verify subsections 18.1-18.6

### User Decisions Incorporated

**Decision 1 - Executive Summary (Task 1.2)**:
- Action: Verify and enhance existing Section 2.2
- Rationale: Content exists at lines 76-110 but needs verification against template's 6 quantitative elements

**Decision 2 - Template State**:
- Action: Commit BRD-TEMPLATE.md unstaged changes first
- Rationale: Workflow sections 3.5.4-3.5.5 exist but unstaged; need stable reference before updating rules

**Decision 3 - Section Count**:
- Action: All 19 sections mandatory
- Clarification: Sections 1-19 are required, Appendices B and C are supplementary

**Decision 4 - Executive Summary Validation (Task 2.2)**:
- Action: Enhance existing CHECK rather than create standalone
- Rationale: Executive Summary is part of Section 1, should be validated within Section 1 CHECK

### Constraints

- Maintain objective, factual language (per CLAUDE.md standards)
- No promotional content or subjective claims
- Follow existing document structure and formatting
- Preserve all existing correct content
- No cascading renumbering required (template already numbered correctly)

## Task List

### Phase 0: Pre-Implementation Setup

- [ ] **0.1** Commit BRD-TEMPLATE.md unstaged changes
  - Stage workflow diagram sections 3.5.4-3.5.5
  - Commit with message: "docs: add workflow diagram sections to BRD template"
  - Ensures stable reference for rules updates
  - Verification: `git status` shows no unstaged changes to BRD-TEMPLATE.md

- [ ] **0.2** Verify Executive Summary completeness in BRD_CREATION_RULES.md
  - Review Section 2.2 (lines 76-110)
  - Compare against template's 6 quantitative elements:
    1. Problem statement with market data
    2. Proposed solution overview
    3. Expected business outcomes (quantified)
    4. Target user segments (sized)
    5. Implementation timeline
    6. Investment required
  - Enhance if missing any elements
  - Mark as complete if all 6 elements present
  - Location: `ai_dev_flow/BRD/BRD_CREATION_RULES.md` Section 2.2

### Phase 1: Update BRD_CREATION_RULES.md

- [ ] **1.1** Fix Document Control (Section 3)
  - Update field count from 6 to 7 fields
  - Add PRD-Ready Score field with calculation criteria
  - Match format from BRD_VALIDATION_RULES.md CHECK 2 (lines 104-111)
  - Location: `ai_dev_flow/BRD/BRD_CREATION_RULES.md` lines 115-146
  - Verification: Count of fields listed = 7, PRD-Ready Score documented

- [ ] **1.3** Add User Stories Section (New Section 5)
  - Create complete Section 5: User Stories Requirements
  - Include standard format: "As a [persona], I want to [action], so that [benefit]"
  - Add persona categorization guidance (Primary/Secondary/Edge Case)
  - Add acceptance criteria requirements
  - Add priority/complexity ratings guidance
  - Reference template Section 5 (lines 453-515) for structure
  - Location: Insert after Section 4 in creation rules
  - Note: NO renumbering of subsequent sections needed
  - Verification: Section 5 header exists, includes 5 required subsections

- [ ] **1.4** Add Workflow Diagram Requirements (Sections 3.5.4-3.5.5)
  - Add subsection 3.5.4: User Workflow Diagrams
  - Add subsection 3.5.5: System Workflow Diagrams
  - Include Mermaid syntax requirements and examples
  - Specify mandatory workflow types (happy path, error handling, edge cases)
  - Reference template lines 173-257 for content
  - Location: Within Section 3.5 (Business Context) in creation rules
  - Verification: Subsections 3.5.4 and 3.5.5 present with Mermaid examples

- [ ] **1.5** Add Approval Process Section (Section 15.5)
  - Add subsection 15.5: Approval and Sign-off
  - Include approval workflow requirements
  - Add stakeholder sign-off checklist
  - Specify approval criteria and decision points
  - Reference template lines 1577-1625 for content
  - Location: Within Section 15 (Appendices) in creation rules
  - Verification: Subsection 15.5 header exists with approval workflow

- [ ] **1.6** Enhance Traceability Requirements (Section 17)
  - Expand Section 17 with full traceability matrix requirements
  - Add bidirectional linking guidance (Business Objectives ↔ FRs ↔ Technical Specs)
  - Include coverage verification requirements
  - Add orphan detection guidance
  - Reference template lines 1673-1745 for comprehensive structure
  - Location: Update existing Section 17 in creation rules
  - Verification: Section 17 includes subsections 17.1-17.4 documentation

- [ ] **1.7** Fix Section Count Discrepancy
  - Update "17 Required Sections" to "19 Required Sections"
  - Clarify: All 19 numbered sections (1-19) are mandatory
  - Note: Appendices B and C are supplementary (outside main numbering)
  - Location: Introduction/Overview section in creation rules
  - Verification: Document states "19 Required Sections" or "19 mandatory sections"

### Phase 2: Update BRD_VALIDATION_RULES.md

- [ ] **2.1** Update CHECK 1: Section Completeness
  - Update section count: "19 required sections (1-19)"
  - Expand section list to include all 19 sections
  - Add note: "Appendices B and C are supplementary"
  - Location: `ai_dev_flow/BRD/BRD_VALIDATION_RULES.md` CHECK 1
  - Verification: CHECK 1 lists sections 1-19, clarifies mandatory status

- [ ] **2.2** Enhance Existing Section 1 CHECK for Executive Summary
  - Locate existing CHECK that validates Section 1 (Introduction)
  - Add Executive Summary structure verification criteria
  - Verify 6 required quantitative elements present:
    1. Problem statement with market data
    2. Proposed solution overview
    3. Expected business outcomes (quantified)
    4. Target user segments (sized)
    5. Implementation timeline
    6. Investment required
  - Add sub-validation: Market data includes sources and dates
  - Add sub-validation: Business outcomes are measurable
  - Location: Update existing Section 1 CHECK (not new CHECK)
  - Verification: Section 1 CHECK includes Executive Summary validation criteria

- [ ] **2.3** Add CHECK 19: User Stories Section
  - Verify Section 5 exists and follows standard format
  - Check all personas are categorized (Primary/Secondary/Edge Case)
  - Validate acceptance criteria present for each story
  - Verify priority and complexity ratings assigned
  - Ensure traceability to functional requirements
  - Location: After current CHECK 18 in validation rules
  - Verification: CHECK 19 header exists, validates Section 5 completeness

- [ ] **2.4** Add CHECK 20: Workflow Diagrams
  - Verify Section 3.5.4 (User Workflows) present
  - Verify Section 3.5.5 (System Workflows) present
  - Check Mermaid syntax correctness
  - Validate coverage: happy path + error handling + edge cases
  - Location: After CHECK 19 in validation rules
  - Verification: CHECK 20 header exists, validates both workflow subsections

- [ ] **2.5** Add CHECK 21: Traceability Matrix
  - Verify Section 17 contains complete matrix with subsections 17.1-17.4
  - Check bidirectional links: Business Objectives → FRs → Technical Specs
  - Validate no orphaned requirements
  - Verify coverage metrics calculated
  - Location: After CHECK 20 in validation rules
  - Verification: CHECK 21 header exists, validates traceability completeness

- [ ] **2.6** Add CHECK 22: Approval Section
  - Verify Section 15.5 present
  - Check stakeholder sign-off table complete
  - Validate approval criteria documented
  - Verify decision points clearly marked
  - Location: After CHECK 21 in validation rules
  - Verification: CHECK 22 header exists, validates Section 15.5

- [ ] **2.7** Enhance Glossary Validation (Update Existing Glossary CHECK)
  - Locate existing glossary validation CHECK
  - Update to verify subsections 18.1-18.6:
    - 18.1 Business Terms
    - 18.2 Technical Terms
    - 18.3 Domain-Specific Terms
    - 18.4 Acronyms
    - 18.5 Cross-References
    - 18.6 External Standards
  - Location: Update existing CHECK that validates Section 18
  - Verification: Glossary CHECK includes subsection validation

### Phase 3: Consistency Verification

- [ ] **3.1** Cross-Reference Alignment
  - Verify all 19 template sections referenced in creation rules
  - Verify all creation rules have corresponding validation checks
  - Ensure consistent terminology across all three documents
  - Create verification checklist comparing section references
  - Verification: No orphaned sections, consistent term usage

- [ ] **3.2** Field Count Verification
  - Document Control: 7 fields (including PRD-Ready Score) across all docs
  - Section Count: 19 sections consistently referenced
  - Glossary Subsections: 6 subsections (18.1-18.6) documented
  - Verification: All three documents show matching counts

- [ ] **3.3** Final Validation Commands
  - Run section count verification
  - Run CHECK count verification
  - Run PRD-Ready Score cross-reference check
  - Run section count consistency check
  - Verification: All commands show expected results (see Implementation Guide)

## Implementation Guide

### Prerequisites

**Files to Modify**:
- `/opt/data/docs_flow_framework/ai_dev_flow/BRD/BRD-TEMPLATE.md` (commit unstaged changes)
- `/opt/data/docs_flow_framework/ai_dev_flow/BRD/BRD_CREATION_RULES.md`
- `/opt/data/docs_flow_framework/ai_dev_flow/BRD/BRD_VALIDATION_RULES.md`

**Reference Sources**:
- BRD-TEMPLATE.md is authoritative source for all content
- Current CHECK count in validation rules: 18
- Expected final CHECK count: 22 (18 existing + 4 new, 2 enhanced)

**Required Tools**:
- Read tool (examine current file state)
- Edit tool (make targeted updates)
- Bash tool (git operations, verification commands)

### Execution Steps

#### Step 1: Pre-Implementation Setup (Tasks 0.1-0.2)

**Task 0.1 - Commit Template Changes**:
```bash
cd /opt/data/docs_flow_framework
git add ai_dev_flow/BRD/BRD-TEMPLATE.md
git commit -m "docs: add workflow diagram sections to BRD template

- Add Section 3.5.4: User Workflow Diagrams
- Add Section 3.5.5: System Workflow Diagrams
- Includes Mermaid syntax examples and requirements

Prepares stable template reference for rules alignment."
```

**Task 0.2 - Verify Executive Summary**:
1. Read BRD_CREATION_RULES.md Section 2.2 (lines 76-110)
2. Compare against template's 6 quantitative elements
3. If all 6 elements present → Mark task complete, proceed to Phase 1
4. If elements missing → Enhance Section 2.2 using template reference
5. Verify: Count documented elements, should equal 6

#### Step 2: Update BRD_CREATION_RULES.md (Tasks 1.1, 1.3-1.7)

**Insertion Order** (to minimize renumbering):
1. Task 1.4 (subsections within existing 3.5)
2. Task 1.5 (subsection within existing 15)
3. Task 1.6 (enhance existing Section 17)
4. Task 1.3 (add Section 5, but template already numbered correctly)
5. Task 1.1 (update existing Section 3)
6. Task 1.7 (update introduction/overview)

**For Each Task**:
1. Read current state of BRD_CREATION_RULES.md
2. Locate insertion point using section headers
3. Extract relevant content from BRD-TEMPLATE.md at specified lines
4. Adapt content to creation rules format (imperative guidance)
5. Use Edit tool to insert/update content
6. Verify section numbering remains consistent
7. Verify inserted content matches template structure

**Example Edit Pattern**:
```markdown
# Before editing
## 3.5 Business Context
[existing content]

## 4. Next Section

# After Task 1.4
## 3.5 Business Context
[existing content]

### 3.5.4 User Workflow Diagrams
[new content from template]

### 3.5.5 System Workflow Diagrams
[new content from template]

## 4. Next Section
```

#### Step 3: Update BRD_VALIDATION_RULES.md (Tasks 2.1-2.7)

**Update Order**:
1. Task 2.1 (update existing CHECK 1)
2. Task 2.2 (enhance existing Section 1 CHECK)
3. Task 2.7 (enhance existing glossary CHECK)
4. Tasks 2.3-2.6 (add new CHECKs 19-22 in sequence)

**For Each New CHECK** (Tasks 2.3-2.6):
1. Read current state of BRD_VALIDATION_RULES.md
2. Locate insertion point after last CHECK
3. Create new CHECK with incremental number
4. Include validation criteria from template
5. Use Edit tool to add new CHECK
6. Verify CHECK numbering is sequential

**For Enhanced CHECKs** (Tasks 2.1, 2.2, 2.7):
1. Locate existing CHECK by section reference
2. Add new validation criteria to existing CHECK
3. Preserve existing validation points
4. Use Edit tool to update CHECK content
5. Verify enhanced CHECK maintains structure

**CHECK Numbering**:
- Current: CHECKs 1-18
- After updates: CHECKs 1-22
- CHECKs 1, 2 (Section 1), and glossary CHECK: Enhanced
- CHECKs 19-22: New additions

#### Step 4: Consistency Verification (Tasks 3.1-3.3)

**Task 3.1 - Cross-Reference Alignment**:
1. Read all three files (template + both rules)
2. Extract section numbers from template (1-19)
3. Verify each section referenced in creation rules
4. Verify each creation rule has corresponding CHECK
5. Compare terminology (e.g., "Functional Requirements" vs "FRs")
6. Document any remaining discrepancies

**Task 3.2 - Field Count Verification**:
```bash
# Verify Document Control field count
grep -A 20 "Document Control" ai_dev_flow/BRD/BRD_CREATION_RULES.md | grep -E "^\s*[0-9]+\." | wc -l
# Expected: 7

# Verify section count references
grep -i "required sections\|mandatory sections" ai_dev_flow/BRD/BRD_CREATION_RULES.md
# Expected: "19 required sections" or similar

# Verify glossary subsections
grep "^### 18\.[0-9]" ai_dev_flow/BRD/BRD-TEMPLATE.md | wc -l
# Expected: 6
```

**Task 3.3 - Final Validation**:
```bash
# Section reference count
echo "=== Section References in Creation Rules ==="
grep -n "Section [0-9]" ai_dev_flow/BRD/BRD_CREATION_RULES.md | wc -l

# CHECK count
echo "=== Total CHECKs in Validation Rules ==="
grep -n "^## CHECK [0-9]" ai_dev_flow/BRD/BRD_VALIDATION_RULES.md | wc -l
# Expected: 22

# PRD-Ready Score mentions
echo "=== PRD-Ready Score Cross-References ==="
grep -i "prd-ready" ai_dev_flow/BRD/BRD_CREATION_RULES.md | wc -l
grep -i "prd-ready" ai_dev_flow/BRD/BRD_VALIDATION_RULES.md | wc -l
# Expected: At least 1 in each file

# Section count consistency
echo "=== Section Count References ==="
grep -i "17 required\|19 sections\|19 required\|mandatory" ai_dev_flow/BRD/BRD_CREATION_RULES.md
grep -i "17 required\|19 sections\|19 required\|mandatory" ai_dev_flow/BRD/BRD_VALIDATION_RULES.md
# Expected: Both should reference "19 sections" or "19 required"

# Final summary
echo "=== Final Document Statistics ==="
echo "BRD-TEMPLATE.md sections: $(grep '^## [0-9]' ai_dev_flow/BRD/BRD-TEMPLATE.md | wc -l)"
echo "BRD_CREATION_RULES.md documented sections: $(grep '^### Section [0-9]' ai_dev_flow/BRD/BRD_CREATION_RULES.md | wc -l)"
echo "BRD_VALIDATION_RULES.md CHECKs: $(grep '^## CHECK' ai_dev_flow/BRD/BRD_VALIDATION_RULES.md | wc -l)"
```

### Verification Checklist

**After Phase 0**:
- [ ] BRD-TEMPLATE.md unstaged changes committed
- [ ] Git status shows clean working directory for template
- [ ] Executive Summary in creation rules verified (6 elements) or enhanced

**After Phase 1**:
- [ ] Document Control shows 7 fields including PRD-Ready Score
- [ ] Executive Summary requirements complete (6 quantitative elements)
- [ ] User Stories section (Section 5) fully documented
- [ ] Workflow diagrams sections 3.5.4-3.5.5 present with Mermaid examples
- [ ] Approval section 15.5 documented with workflow
- [ ] Traceability section 17 includes subsections 17.1-17.4
- [ ] Section count updated to "19 required sections"
- [ ] All 19 template sections referenced in creation rules

**After Phase 2**:
- [ ] CHECK 1 lists all 19 sections
- [ ] Section 1 CHECK validates Executive Summary structure
- [ ] CHECK 19 validates User Stories section
- [ ] CHECK 20 validates Workflow Diagrams
- [ ] CHECK 21 validates Traceability Matrix
- [ ] CHECK 22 validates Approval section
- [ ] Glossary CHECK validates subsections 18.1-18.6
- [ ] Total CHECK count = 22

**After Phase 3**:
- [ ] No orphaned sections (all template sections in creation rules)
- [ ] No orphaned rules (all creation rules have validation checks)
- [ ] Consistent terminology across all three documents
- [ ] Field counts match: Document Control = 7 fields in all docs
- [ ] Section counts match: 19 sections in all docs
- [ ] PRD-Ready Score referenced in both rules documents
- [ ] All verification commands return expected results

### Expected Outcomes

**BRD_CREATION_RULES.md Changes**:
- 6 sections/subsections enhanced or added:
  - Section 3: Document Control (enhanced, 6→7 fields)
  - Section 2.2: Executive Summary (verified/enhanced)
  - Section 5: User Stories (added)
  - Sections 3.5.4-3.5.5: Workflow Diagrams (added)
  - Section 15.5: Approval (added)
  - Section 17: Traceability (enhanced)
- Introduction updated: 17→19 required sections
- 100% coverage of template structure

**BRD_VALIDATION_RULES.md Changes**:
- 3 existing CHECKs enhanced:
  - CHECK 1: Section completeness (17→19 sections)
  - Section 1 CHECK: Executive Summary validation added
  - Glossary CHECK: Subsection validation (18.1-18.6) added
- 4 new CHECKs added:
  - CHECK 19: User Stories
  - CHECK 20: Workflow Diagrams
  - CHECK 21: Traceability Matrix
  - CHECK 22: Approval Section
- Total validation coverage: 22 checks
- 100% coverage of template requirements

**Consistency Achieved**:
- Zero discrepancies between template and rules
- All terminology aligned
- All field/section counts accurate and consistent
- Bidirectional traceability: Template ↔ Creation Rules ↔ Validation Rules

## References

### Primary Files

**Authoritative Source**:
- `/opt/data/docs_flow_framework/ai_dev_flow/BRD/BRD-TEMPLATE.md` (2,837 lines)

**Files to Update**:
- `/opt/data/docs_flow_framework/ai_dev_flow/BRD/BRD_CREATION_RULES.md`
- `/opt/data/docs_flow_framework/ai_dev_flow/BRD/BRD_VALIDATION_RULES.md`

### Template Section Line References

**Sections Requiring Documentation**:
- Lines 20-40: Document Control (7 fields including PRD-Ready Score)
- Lines 76-111: Executive Summary (6 quantitative elements)
- Lines 173-210: Section 3.5.4 User Workflow Diagrams (unstaged)
- Lines 211-257: Section 3.5.5 System Workflow Diagrams (unstaged)
- Lines 453-515: Section 5 User Stories (complete structure)
- Lines 1577-1625: Section 15.5 Approval and Sign-off
- Lines 1673-1745: Section 17 Traceability (subsections 17.1-17.4)
- Lines 1751-1831: Section 18 Glossary (subsections 18.1-18.6)
- Lines 1846-2076: Appendix B (supplementary)
- Lines 2078-2499: Appendix C (supplementary)

### Gap Analysis Summary

**Original Work Plan Identified**:
- 11 gaps in BRD_CREATION_RULES.md
- 6 gaps in BRD_VALIDATION_RULES.md
- 3 consistency issues
- Total: 20 discrete issues

**Verified Gaps** (after analysis):
- 6 confirmed gaps in BRD_CREATION_RULES.md (Task 0.2 may reduce to 5)
- 6 confirmed gaps in BRD_VALIDATION_RULES.md
- 3 confirmed consistency issues
- Total: 15 discrete issues to resolve

**Adjustments from Original Plan**:
- Executive Summary documentation exists (Task 1.2 → Task 0.2 verification)
- Section 1 CHECK enhancement instead of new CHECK (Task 2.2 modified)
- Template unstaged changes need commit first (Task 0.1 added)
- Section count clarified as 19 (not 17+2 optional)

### Standards and Guidelines

**Language Requirements** (CLAUDE.md):
- Objective, factual language only
- No promotional content or subjective claims
- Document implementation complexity (scale 1-5)
- Include resource requirements and constraints
- No time estimates or performance claims

**Documentation Standards**:
- Maximum 100,000 tokens per file (all files well under limit)
- Use tabular format for parameter specifications
- Employ bullet points for configuration options
- Imperative verb forms for procedures

### Related Documentation

**Project Configuration**:
- Work Plans Directory: `/opt/data/docs_flow_framework/work_plans/`
- Active Project: docs_flow_framework
- Git repository: Yes

**Standards References**:
- ID Naming Standards: `/opt/data/docs_flow_framework/ai_dev_flow/ID_NAMING_STANDARDS.md`
- Metadata Guide: `/opt/data/docs_flow_framework/ai_dev_flow/METADATA_TAGGING_GUIDE.md`
- SDD Guide: `/opt/data/docs_flow_framework/ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md`

---

## Implementation Instructions

To continue implementation in a new context:

1. Open new Claude Code session
2. Run: `cat /opt/data/docs_flow_framework/work_plans/align-brd-rules-revised_20251125_200111.md`
3. Say: "Implement this plan"

The plan includes detailed step-by-step execution instructions, verification commands, and expected outcomes for each phase.
