---
title: "PRD Validation Rules Reference"
tags:
  - validation-rules
  - layer-2-artifact
  - shared-architecture
custom_fields:
  document_type: validation-rules
  artifact_type: PRD
  layer: 2
  priority: shared
  development_status: active
---

# PRD Validation Rules Reference

**Version**: 1.0.0
**Date**: 2025-11-26
**Last Updated**: 2025-11-26
**Purpose**: Complete validation rules for PRD documents
**Script**: `scripts/validate_prd_template.sh`
**Primary Template**: `PRD-TEMPLATE.md`
**Framework**: doc_flow SDD (100% compliant)

---

## Table of Contents

1. [Overview](#overview)
2. [Document Control Validation](#document-control-validation)
3. [Section-by-Section Validation](#section-by-section-validation)
4. [Quality Gates](#quality-gates)
5. [Common Issues](#common-issues)

---

## 1. Overview

The PRD validation framework ensures Product Requirements Documents comply with SDD Layer 2 standards, focusing on product-centric requirements that translate business objectives into measurable features.

### Validation Philosophy

**Product-Centric Focus**: PRD validation emphasizes product features, user needs, and business value over technical implementation details. Requirements must be measurable, testable by business stakeholders, and implementation-agnostic.

### PRD vs BRD Distinctions

| Aspect | BRD (Layer 1) | PRD (Layer 2) |
|--------|---------------|---------------|
| Focus | Business objectives, strategy | Product features, user requirements |
| Audience | Executives, business stakeholders | Product managers, development teams |
| Scope | Why build this | What to build |
| Metrics | Business KPIs, ROI | Product KPIs, user metrics |
| Acceptance | Strategic alignment | Feature completeness |

### PRD vs SYS/EARS Distinctions

| Aspect | PRD (Layer 2) | SYS (Layer 6) | EARS (Layer 3) |
|--------|---------------|---------------|----------------|
| Focus | Product requirements | System requirements | Engineering requirements |
| Level | User capabilities | System capabilities | Technical specifications |
| Format | User stories, features | Functional/non-functional | WHEN-THE-SHALL-WITHIN |
| Detail | What product does | How system delivers | Precise technical behavior |

### Measurable Outcomes Emphasis

All PRD requirements must include:
- **Quantifiable Success Metrics**: Specific, measurable KPIs
- **Acceptance Criteria**: Business stakeholder-verifiable conditions
- **User Impact**: Clear benefit to target users
- **Business Value**: ROI or strategic alignment justification

### Layer 2 Positioning in SDD Framework

**Upstream**: Inherits business objectives from BRD (Layer 1)
**Downstream**: Informs SYS (Layer 6), EARS (Layer 3), BDD (Layer 4), REQ (Layer 7)
**Parallel**: May reference ADR topics (Layer 5) but NOT specific ADR numbers
**Quality Gates**: ≥90% SYS-Ready and EARS-Ready scores required for progression

---

## 2. Document Control Validation

### CHECK 1: Required Fields Validation

**Purpose**: Verify all 11 mandatory Document Control fields exist
**Type**: Error (blocking)

**Required Fields**:

| Field | Format | Requirement |
|-------|--------|-------------|
| Document ID | PRD-XXX in H1 header | MANDATORY |
| Version | Semantic versioning (X.Y.Z) | MANDATORY |
| Status | Draft/Review/Approved/Implemented | MANDATORY |
| Author | Product Manager/Owner Name | MANDATORY |
| Reviewer | Technical reviewer name | MANDATORY |
| Approver | Final approver name | MANDATORY |
| Created Date | YYYY-MM-DD | MANDATORY |
| Last Updated | YYYY-MM-DD | MANDATORY |
| BRD Reference | @brd: BRD-XXX tag | MANDATORY |
| SYS-Ready Score | ✅ XX% (Target: ≥90%) | MANDATORY |
| EARS-Ready Score | ✅ XX% (Target: ≥90%) | MANDATORY |

**Error Messages**:
```
❌ MISSING FIELD: SYS-Ready Score
❌ MISSING FIELD: EARS-Ready Score
❌ INVALID FORMAT: Version must use semantic versioning (X.Y.Z)
```

**Resolution Steps**:
1. Add missing field to Document Control table
2. Use exact field names as specified
3. Follow format requirements for each field
4. Include both scoring fields with ✅ emoji

### CHECK 2: Dual Scoring Format Validation

**Purpose**: Verify both SYS-Ready and EARS-Ready scores follow standard format
**Type**: Error (blocking)

**Requirements**:
- Both scores must be present in Document Control table
- Both must use ✅ emoji prefix
- Both must show percentage (XX%)
- Both must include target threshold in parentheses: (Target: ≥90%)

**Valid Format Example**:
```markdown
| **SYS-Ready Score** | ✅ 95% (Target: ≥90%) |
| **EARS-Ready Score** | ✅ 95% (Target: ≥90%) |
```

**Invalid Formats**:
```markdown
❌ | **SYS-Ready Score** | 95% |           # Missing emoji and target
❌ | **SYS-Ready Score** | ✅ 95 |           # Missing percentage symbol
❌ | **SYS-Ready Score** | ✅ 95% |          # Missing target threshold
❌ | **EARS-Ready Score** | N/A |            # Score must be numeric
```

**Error Messages**:
```
❌ INVALID FORMAT: SYS-Ready Score must include ✅ emoji
❌ INVALID FORMAT: EARS-Ready Score missing target threshold
❌ INVALID FORMAT: Score must be percentage (XX%)
```

**Resolution Steps**:
1. Add ✅ emoji before percentage
2. Include percentage symbol after number
3. Add target threshold: (Target: ≥90%)
4. Verify both scores follow identical format

### CHECK 3: Threshold Enforcement

**Purpose**: Ensure PRD meets minimum quality thresholds for downstream progression
**Type**: Error (blocking)

**Requirements**:
- **SYS-Ready Score ≥90%**: Blocks progression to SYS creation if not met
- **EARS-Ready Score ≥90%**: Blocks progression to EARS creation if not met

**Error Messages**:
```
❌ BLOCKING ERROR: SYS-Ready Score is 85% (minimum: 90%)
❌ BLOCKING ERROR: EARS-Ready Score is 88% (minimum: 90%)
```

**Resolution Steps**:
1. Review scoring criteria in PRD_CREATION_RULES.md Section 8 (SYS-Ready) and Section 9 (EARS-Ready)
2. Address gaps in completeness, technical readiness, or traceability
3. Update Document Control score after improvements
4. Re-validate before commit

**Scoring Calculation Reference**:
- **SYS-Ready**: Product Requirements Completeness (40%), Technical Readiness (30%), Business Alignment (20%), Traceability (10%)
- **EARS-Ready**: Business Requirements Clarity (40%), Requirements Maturity (35%), EARS Translation Readiness (20%), Strategic Alignment (5%)

---

## 3. Section-by-Section Validation

### CHECK 4: Section Numbering Validation

**Purpose**: Verify all 19 sections (0-18) are numbered explicitly
**Type**: Error (blocking)

**Required Section Numbers**:
```markdown
## 0. Document Control
## 1. Executive Summary
## 2. Problem Statement
## 3. Target Audience & User Personas
## 4. Success Metrics (KPIs)
## 5. Goals & Objectives
## 6. Scope & Requirements
## 7. User Stories & User Roles
## 8. Functional Requirements
## 9. Customer-Facing Content & Messaging (MANDATORY)
## 10. Acceptance Criteria
## 11. Constraints & Assumptions
## 12. Risk Assessment
## 13. Success Definition
## 14. Stakeholders & Communication
## 15. Implementation Approach
## 16. Budget & Resources
## 17. Traceability
## 18. References
```

**Error Messages**:
```
❌ MISSING NUMBER: Section header must be "## 0. Document Control"
❌ INCORRECT NUMBER: Found "## Document Control", expected "## 0. Document Control"
❌ DUPLICATE NUMBER: Section number 6 appears twice
```

**Resolution Steps**:
1. Add explicit section number to each header
2. Use format: `## N. Section Title`
3. Verify sequential numbering (0-18)
4. Check for duplicates or skipped numbers

### CHECK 5: Mandatory Sections Presence

**Purpose**: Verify all 19 sections exist in document
**Type**: Error (blocking)

**All Sections MANDATORY**: Every PRD must contain all 19 sections (0-18) with substantive content, not placeholders.

**Error Messages**:
```
❌ MISSING SECTION: ## 6. User Stories & User Roles
❌ MISSING SECTION: ## 8. Customer-Facing Content & Messaging (MANDATORY)
```

**Resolution Steps**:
1. Add missing section with correct header format
2. Populate with substantive content (not "TBD" or "TODO")
3. Follow section-specific requirements from PRD-TEMPLATE.md

### CHECK 6: Section Title Consistency

**Purpose**: Verify section titles match template exactly
**Type**: Warning (recommended fix)

**Title Matching Rules**:
- Section titles must match PRD-TEMPLATE.md character-for-character
- Capitalization must be identical
- Special markers like (MANDATORY) must be included where specified

**Error Messages**:
```
⚠️ WARNING: Section 8 title should be "Customer-Facing Content & Messaging (MANDATORY)"
⚠️ WARNING: Section 3 title should use "&" not "and"
```

**Resolution Steps**:
1. Copy exact title from PRD-TEMPLATE.md
2. Preserve capitalization and punctuation
3. Include (MANDATORY) marker for Section 8

### CHECK 7: User Stories Scope Validation (Section 7)

**Purpose**: Ensure PRD-level user stories stay within Layer 2 scope
**Type**: Error (blocking)

**Layer Separation Requirements**:

**✅ PRD-Level Content (Layer 2)**:
- User role definitions (personas)
- Story titles: "As a [role], I want [capability] so that [benefit]"
- Story summaries (2-3 sentences max)
- Product-level acceptance criteria (what, not how)

**❌ NOT PRD-Level (belongs in downstream layers)**:
- EARS-level specifications (WHEN-THE-SHALL-WITHIN format) → Layer 3
- BDD-level test scenarios (Given-When-Then) → Layer 4
- Technical implementation details → Layer 6/7
- System architecture decisions → ADR (Layer 5)

**Required Elements**:
1. **Scope Note Present**: Section 6 must include layer separation explanation
2. **Role Definitions**: User personas with characteristics and needs
3. **Story Summaries**: High-level capability descriptions
4. **No Technical Details**: No EARS/BDD/SYS-level content

**Error Messages**:
```
❌ SCOPE VIOLATION: Section 7 contains WHEN-THE-SHALL format (belongs in EARS)
❌ SCOPE VIOLATION: Section 7 contains Given-When-Then scenarios (belongs in BDD)
❌ MISSING: Section 7 scope note explaining layer separation
```

**Resolution Steps**:
1. Add scope note from PRD-TEMPLATE.md
2. Move EARS-level content to placeholder for future EARS document
3. Move BDD-level content to placeholder for future BDD tests
4. Keep only PRD-level role definitions and story summaries

### CHECK 8: Customer-Facing Content Mandatory (Section 9)

**Purpose**: Enforce Section 9 as blocking requirement
**Type**: Error (blocking)

**Requirements**:
- Section 9 header must include (MANDATORY) designation
- Section must contain substantive content (not placeholders)
- Content must address customer-visible materials

**Required Content Categories**:
- Product positioning statements
- Key messaging themes
- Feature descriptions for marketing
- User-facing documentation requirements
- Help text and tooltips
- Error messages (user-visible)
- Success confirmations
- Onboarding content
- Release notes template

**Error Messages**:
```
❌ BLOCKING ERROR: Section 9 (Customer-Facing Content) is missing
❌ BLOCKING ERROR: Section 9 header missing (MANDATORY) designation
❌ BLOCKING ERROR: Section 9 contains only placeholder text
```

**Resolution Steps**:
1. Add Section 9 if missing
2. Include (MANDATORY) in header
3. Populate with substantive customer-facing content
4. Address at least 3 content categories from required list

### CHECK 9: No ADR Forward References

**Purpose**: Prevent broken references to non-existent ADRs
**Type**: Error (blocking)

**Rule**: PRDs are created BEFORE ADRs in SDD workflow. Never reference specific ADR numbers (ADR-012, ADR-033, etc.).

**✅ ALLOWED**:
```markdown
#### Architecture Decision Requirements

| Topic Area | Decision Needed | Business Driver |
|------------|-----------------|-----------------|
| Data Storage | Select between SQL and NoSQL | High-volume transaction requirements |
| API Protocol | REST vs GraphQL | Client flexibility requirements |
```

**❌ NOT ALLOWED**:
```markdown
This requirement is based on ADR-012 (Database Selection)  ← BLOCKING ERROR
See ADR-033 for API design decisions                       ← BLOCKING ERROR
```

**Error Messages**:
```
❌ BLOCKING ERROR: Found ADR-012 reference (PRDs created before ADRs)
❌ BLOCKING ERROR: Remove ADR-XXX references, use topic names only
```

**Resolution Steps**:
1. Remove specific ADR-XXX references
2. Add topics to "Architecture Decision Requirements" table
3. Describe decision needed without referencing non-existent ADR

### CHECK 10: Traceability Tags Cumulative Hierarchy

**Purpose**: Verify proper upstream/downstream linkage
**Type**: Warning (recommended fix)

**Layer 2 Traceability Requirements**:

**Upstream Tags** (MANDATORY):
```markdown
@brd: BRD-XXX:REQUIREMENT-ID
```

**Downstream Tags** (Optional but recommended):
```markdown
@sys: SYS-XXX (planned)
@ears: EARS-XXX (planned)
@bdd: BDD-XXX (planned)
@req: REQ-XXX (planned)
```

**Error Messages**:
```
⚠️ WARNING: Missing @brd upstream reference
⚠️ WARNING: Traceability section incomplete
```

**Resolution Steps**:
1. Add @brd tag referencing source BRD requirement
2. Add planned downstream artifact tags (optional)
3. Populate Traceability section (Section 17)

### Per-Section Validation Criteria

**Section 0 - Document Control**:
- 11 required fields present (See CHECK 1)
- Dual scoring with ≥90% thresholds (See CHECK 2-3)
- Document Revision History table with at least one entry

**Section 1 - Executive Summary**:
- 2-3 sentence overview
- Business Value Proposition subsection
- Timeline subsection with 5 phases

**Section 2 - Problem Statement**:
- Current State, Business Impact, Root Cause Analysis, Opportunity Assessment subsections
- Quantified business impact metrics
- Clear problem articulation

**Section 3 - Target Audience & User Personas**:
- Primary Users, Secondary Users, Business Stakeholders subsections
- At least 2 user personas with demographics, goals, pain points

**Section 4 - Success Metrics (KPIs)**:
- Primary KPIs, Secondary KPIs, Success Criteria by Phase subsections
- At least 3 measurable KPIs
- Baseline and target values specified

**Section 5 - Goals & Objectives**:
- Primary Business Goals, Secondary Objectives, Stretch Goals subsections
- SMART criteria applied (Specific, Measurable, Achievable, Relevant, Time-bound)

**Section 6 - Scope & Requirements**:
- In Scope, Out of Scope, Dependencies, Assumptions subsections
- Clear boundary definitions

**Section 7 - User Stories & User Roles**:
- Layer Separation scope note present (See CHECK 7)
- User role definitions
- Story summaries (not EARS/BDD-level detail)

**Section 8 - Functional Requirements**:
- User Journey Mapping, Capability Requirements subsections
- Requirements numbered (FR-001, FR-002, etc.)
- Each requirement testable

**Section 9 - Customer-Facing Content & Messaging**:
- (MANDATORY) designation in header (See CHECK 8)
- Substantive content addressing customer-visible materials
- At least 3 content categories covered

**Section 10 - Acceptance Criteria**:
- Business Acceptance, Technical Acceptance, Quality Assurance subsections
- Criteria verifiable by business stakeholders

**Section 11 - Constraints & Assumptions**:
- Business Constraints, Technical Constraints, External Constraints, Key Assumptions subsections
- Each assumption identified with validation plan

**Section 12 - Risk Assessment**:
- High-Risk Items, Risk Mitigation Plan subsections
- Risks categorized by severity and likelihood

**Section 13 - Success Definition**:
- Go-Live Criteria, Post-Launch Validation, Measurement Timeline subsections
- Specific success thresholds

**Section 14 - Stakeholders & Communication**:
- Core Team, Stakeholders, Communication Plan subsections
- RACI matrix or equivalent

**Section 15 - Implementation Approach**:
- Development Phases, Testing Strategy subsections
- High-level timeline

**Section 16 - Budget & Resources**:
- Development Budget, Operational Budget, Resource Requirements subsections
- Cost estimates with justification

**Section 17 - Traceability**:
- Upstream Sources, Downstream Artifacts, Traceability Tags, Validation Evidence subsections
- @brd tag present (See CHECK 10)

**Section 18 - References**:
- Internal Documentation, External Standards, Domain References, Technology References subsections
- All references valid and accessible

---

## 4. Quality Gates

### Pre-Commit Checklist

**Before committing PRD to repository, verify**:

- [ ] **All 19 sections present** (0-18) with substantive content
- [ ] **Section numbering explicit** (## N. Title format)
- [ ] **Dual scoring ≥90%** (SYS-Ready and EARS-Ready)
- [ ] **Customer-Facing Content (Section 9)** populated with (MANDATORY) designation
- [ ] **User Stories (Section 7)** include scope note, stay within PRD layer
- [ ] **No ADR-XXX forward references** (use topics only)
- [ ] **@brd upstream tag** present in Traceability section
- [ ] **Document Control** has all 11 required fields
- [ ] **YAML frontmatter** valid syntax
- [ ] **Run validation script**: `./scripts/validate_prd_template.sh [filename]`

### Validation Script Commands

```bash
# Validate single PRD
./scripts/validate_prd_template.sh docs/PRD/PRD-001_product_name.md

# Validate all PRDs
find docs/PRD -name "PRD-*.md" -exec ./scripts/validate_prd_template.sh {} \;

# Check YAML frontmatter
python3 -c "import yaml; yaml.safe_load(open('docs/PRD/PRD-001_product_name.md').read().split('---')[1])"
```

### Quality Thresholds Table

| Metric | Minimum | Target | Blocking |
|--------|---------|--------|----------|
| SYS-Ready Score | 90% | 95% | Yes |
| EARS-Ready Score | 90% | 95% | Yes |
| Section Completeness | 100% | 100% | Yes |
| Traceability Links | 80% | 100% | No |
| User Story Scope Compliance | 100% | 100% | Yes |
| Customer-Facing Content | Present | Comprehensive | Yes |

### Progression Criteria

**When to Advance to EARS/SYS**:
- ✅ Both SYS-Ready and EARS-Ready scores ≥90%
- ✅ All 19 sections complete with substantive content
- ✅ Section 9 (Customer-Facing Content) populated
- ✅ Section 7 (User Stories) within PRD scope
- ✅ @brd upstream reference valid
- ✅ No blocking validation errors

**Blocking Conditions**:
- ❌ Either score <90%
- ❌ Missing mandatory sections
- ❌ Section 9 missing or placeholder-only
- ❌ Section 7 contains EARS/BDD-level detail
- ❌ ADR-XXX forward references present
- ❌ Missing Document Control fields

---

## 5. Common Issues

### Issue 1: Missing Dual Scores

**Symptoms**:
```
❌ MISSING FIELD: SYS-Ready Score
❌ MISSING FIELD: EARS-Ready Score
```

**Root Cause**: Document Control table incomplete or using old template format

**Fix**:
1. Add both scoring rows to Document Control table:
   ```markdown
   | **SYS-Ready Score** | ✅ 95% (Target: ≥90%) |
   | **EARS-Ready Score** | ✅ 95% (Target: ≥90%) |
   ```
2. Calculate scores using criteria in PRD_CREATION_RULES.md Sections 8-9
3. Ensure both scores ≥90% before commit

### Issue 2: Section Numbering Inconsistencies

**Symptoms**:
```
❌ MISSING NUMBER: Found "## Document Control", expected "## 0. Document Control"
❌ DUPLICATE NUMBER: Section number 6 appears twice
```

**Root Cause**: Manual editing without systematic renumbering or old template format

**Fix**:
1. Use find/replace to add numbers to all headers:
   ```
   ## Document Control → ## 0. Document Control
   ## Executive Summary → ## 1. Executive Summary
   ```
2. Verify sequential numbering 0-18 with no gaps
3. Check for duplicate section numbers
4. Compare with PRD-TEMPLATE.md for correct sequence

### Issue 3: User Stories Scope Violations

**Symptoms**:
```
❌ SCOPE VIOLATION: Section 7 contains WHEN-THE-SHALL format (belongs in EARS)
❌ SCOPE VIOLATION: Section 7 contains Given-When-Then scenarios (belongs in BDD)
```

**Root Cause**: Mixing PRD-level requirements with EARS/BDD-level technical details

**Fix**:
1. Add scope note from PRD-TEMPLATE.md to Section 7
2. Keep only PRD-level content:
   - User role definitions (who they are)
   - Story titles and summaries (what they need)
   - Product-level acceptance criteria
3. Move EARS-level content to notes for future EARS document
4. Move BDD-level scenarios to notes for future BDD tests
5. Focus on WHAT product delivers, not HOW system implements

### Issue 4: Customer-Facing Content Omissions

**Symptoms**:
```
❌ BLOCKING ERROR: Section 9 (Customer-Facing Content) is missing
❌ BLOCKING ERROR: Section 9 contains only placeholder text
```

**Root Cause**: Section 9 treated as optional or overlooked as new mandatory requirement

**Fix**:
1. Add Section 9 header with (MANDATORY) designation:
   ```markdown
   ## 9. Customer-Facing Content & Messaging (MANDATORY)
   ```
2. Populate with substantive content (minimum 3 categories):
   - Product positioning statements
   - Key messaging themes
   - User-facing documentation requirements
   - Help text, error messages, success confirmations
3. Avoid placeholders like "TBD" or "TODO"
4. Ensure content addresses customer-visible materials

### Issue 5: ADR Forward References

**Symptoms**:
```
❌ BLOCKING ERROR: Found ADR-012 reference (PRDs created before ADRs)
❌ BLOCKING ERROR: Remove ADR-XXX references, use topic names only
```

**Root Cause**: Misunderstanding SDD workflow order (PRD created before ADR)

**Fix**:
1. Remove all ADR-XXX specific references
2. Add topics to "Architecture Decision Requirements" table in Section 17:
   ```markdown
   | Topic Area | Decision Needed | Business Driver |
   |------------|-----------------|-----------------|
   | [Topic] | [Description] | [PRD reference] |
   ```
3. Describe architectural decision topics without assuming ADR already exists
4. Reference workflow: BRD → PRD → ADR → SYS/EARS

---

**Framework Compliance**: 100% doc_flow SDD framework aligned (Layer 2 - Product Requirements)
**Maintained By**: Product Management Team, SDD Framework Team
**Review Frequency**: Updated with template and validation rule enhancements

---
