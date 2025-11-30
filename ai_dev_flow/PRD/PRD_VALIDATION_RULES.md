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

> **📋 Document Role**: This is the **POST-CREATION VALIDATOR** for PRD documents.
> - Apply these rules after PRD creation or modification
> - **Authority**: Validates compliance with `PRD-TEMPLATE.md` (the primary standard)
> - **Scope**: Use for quality gates before committing PRD changes

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
3. [section-by-section Validation](#section-by-section-validation)
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

**Required Fields** (11 mandatory + 4 optional):

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
| Priority | High / Medium / Low | OPTIONAL |
| Target Release | Release version/Quarter | OPTIONAL |
| Estimated Effort | Story Points or Person-Months | OPTIONAL |

**Note**: Optional fields are recommended but not validation-blocking. Document Revision History table is also optional but recommended.

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
1. Review scoring criteria in PRD_CREATION_RULES.md section 8 (SYS-Ready) and section 9 (EARS-Ready)
2. Address gaps in completeness, technical readiness, or traceability
3. Update Document Control score after improvements
4. Re-validate before commit

**Scoring Calculation Reference**:
- **SYS-Ready**: Product Requirements Completeness (40%), Technical Readiness (30%), Business Alignment (20%), Traceability (10%)
- **EARS-Ready**: Business Requirements Clarity (40%), Requirements Maturity (35%), EARS Translation Readiness (20%), Strategic Alignment (5%)

---

## 3. section-by-section Validation

### CHECK 4: section Numbering Validation

**Purpose**: Verify all 19 sections (0-18) are numbered explicitly
**Type**: Error (blocking)

**Required section Numbers**:
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
❌ MISSING NUMBER: section header must be "## 0. Document Control"
❌ INCORRECT NUMBER: Found "## Document Control", expected "## 0. Document Control"
❌ DUPLICATE NUMBER: section number 6 appears twice
```

**Resolution Steps**:
1. Add explicit section number to each header
2. Use format: `## N. section Title`
3. Verify sequential numbering (0-18)
4. Check for duplicates or skipped numbers

### CHECK 5: Mandatory sections Presence

**Purpose**: Verify all 19 sections exist in document
**Type**: Error (blocking)

**All sections MANDATORY**: Every PRD must contain all 19 sections (0-18) with substantive content, not placeholders.

**Error Messages**:
```
❌ MISSING regulatoryTION: ## 6. User Stories & User Roles
❌ MISSING regulatoryTION: ## 8. Customer-Facing Content & Messaging (MANDATORY)
```

**Resolution Steps**:
1. Add missing section with correct header format
2. Populate with substantive content (not "TBD" or "TODO")
3. Follow section-specific requirements from PRD-TEMPLATE.md

### CHECK 6: section Title Consistency

**Purpose**: Verify section titles match template exactly
**Type**: Warning (recommended fix)

**Title Matching Rules**:
- section titles must match PRD-TEMPLATE.md character-for-character
- Capitalization must be identical
- Special markers like (MANDATORY) must be included where specified

**Error Messages**:
```
⚠️ WARNING: section 8 title should be "Customer-Facing Content & Messaging (MANDATORY)"
⚠️ WARNING: section 3 title should use "&" not "and"
```

**Resolution Steps**:
1. Copy exact title from PRD-TEMPLATE.md
2. Preserve capitalization and punctuation
3. Include (MANDATORY) marker for section 8

### CHECK 7: User Stories Scope Validation (section 7)

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
1. **Scope Note Present**: section 7 must include layer separation explanation
2. **Role Definitions**: User personas with characteristics and needs
3. **Story Summaries**: High-level capability descriptions
4. **No Technical Details**: No EARS/BDD/SYS-level content

**Error Messages**:
```
❌ SCOPE VIOLATION: section 7 contains WHEN-THE-SHALL format (belongs in EARS)
❌ SCOPE VIOLATION: section 7 contains Given-When-Then scenarios (belongs in BDD)
❌ MISSING: section 7 scope note explaining layer separation
```

**Resolution Steps**:
1. Add scope note from PRD-TEMPLATE.md
2. Move EARS-level content to placeholder for future EARS document
3. Move BDD-level content to placeholder for future BDD tests
4. Keep only PRD-level role definitions and story summaries

### CHECK 8: Customer-Facing Content Mandatory (section 9)

> **Note**: CHECK numbers are sequential validation steps; they do not correspond to PRD section numbers.

**Purpose**: Enforce section 9 as blocking requirement
**Type**: Error (blocking)

**Requirements**:
- section 9 header must include (MANDATORY) designation
- section must contain substantive content (not placeholders)
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
❌ BLOCKING ERROR: section 9 (Customer-Facing Content) is missing
❌ BLOCKING ERROR: section 9 header missing (MANDATORY) designation
❌ BLOCKING ERROR: section 9 contains only placeholder text
```

**Resolution Steps**:
1. Add section 9 if missing
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
@brd: BRD-NNN:NNN
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
3. Populate Traceability section (section 17)

### Per-section Validation Criteria

**section 0 - Document Control**:
- 11 required fields present (See CHECK 1)
- Dual scoring with ≥90% thresholds (See CHECK 2-3)
- Document Revision History table with at least one entry

**section 1 - Executive Summary**:
- 2-3 sentence overview
- Business Value Proposition subsection
- Timeline subsection with 5 phases

**section 2 - Problem Statement**:
- Current State, Business Impact, Root Cause Analysis, Opportunity Assessment subsections
- Quantified business impact metrics
- Clear problem articulation

**section 3 - Target Audience & User Personas**:
- Primary Users, secondary Users, Business Stakeholders subsections
- At least 2 user personas with demographics, goals, pain points

**section 4 - Success Metrics (KPIs)**:
- Primary KPIs, secondary KPIs, Success Criteria by Phase subsections
- At least 3 measurable KPIs
- Baseline and target values specified

**section 5 - Goals & Objectives**:
- Primary Business Goals, secondary Objectives, Stretch Goals subsections
- SMART criteria applied (Specific, Measurable, Achievable, Relevant, Time-bound)

**section 6 - Scope & Requirements**:
- In Scope, Out of Scope, Dependencies, Assumptions subsections
- Clear boundary definitions

**section 7 - User Stories & User Roles**:
- Layer Separation scope note present (See CHECK 7)
- User role definitions
- Story summaries (not EARS/BDD-level detail)

**section 8 - Functional Requirements**:
- User Journey Mapping, Capability Requirements subsections
- Requirements numbered (FR-001, FR-002, etc.)
- Each requirement testable

**section 9 - Customer-Facing Content & Messaging**:
- (MANDATORY) designation in header (See CHECK 8)
- Substantive content addressing customer-visible materials
- At least 3 content categories covered

**section 10 - Acceptance Criteria**:
- Business Acceptance, Technical Acceptance, Quality Assurance subsections
- Criteria verifiable by business stakeholders

**section 11 - Constraints & Assumptions**:
- Business Constraints, Technical Constraints, External Constraints, Key Assumptions subsections
- Each assumption identified with validation plan

**section 12 - Risk Assessment**:
- High-Risk Items, Risk Mitigation Plan subsections
- Risks categorized by severity and likelihood

**section 13 - Success Definition**:
- Go-Live Criteria, Post-Launch Validation, Measurement Timeline subsections
- Specific success thresholds

**section 14 - Stakeholders & Communication**:
- Core Team, Stakeholders, Communication Plan subsections
- RACI matrix or equivalent

**section 15 - Implementation Approach**:
- Development Phases, Testing Strategy subsections
- High-level timeline

**section 16 - Budget & Resources**:
- Development Budget, Operational Budget, Resource Requirements subsections
- Cost estimates with justification

**section 17 - Traceability**:
- Upstream Sources, Downstream Artifacts, Traceability Tags, Validation Evidence subsections
- @brd tag present (See CHECK 10)

**section 18 - References**:
- Internal Documentation, External Standards, Domain References, Technology References subsections
- All references valid and accessible

---

## 4. Quality Gates

### Pre-Commit Checklist

**Before committing PRD to repository, verify**:

- [ ] **All 19 sections present** (0-18) with substantive content
- [ ] **section numbering explicit** (## N. Title format)
- [ ] **Dual scoring ≥90%** (SYS-Ready and EARS-Ready)
- [ ] **Customer-Facing Content (section 9)** populated with (MANDATORY) designation
- [ ] **User Stories (section 7)** include scope note, stay within PRD layer
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
| section Completeness | 100% | 100% | Yes |
| Traceability Links | 80% | 100% | No |
| User Story Scope Compliance | 100% | 100% | Yes |
| Customer-Facing Content | Present | Comprehensive | Yes |

### Progression Criteria

**When to Advance to EARS/SYS**:
- ✅ Both SYS-Ready and EARS-Ready scores ≥90%
- ✅ All 19 sections complete with substantive content
- ✅ section 9 (Customer-Facing Content) populated
- ✅ section 7 (User Stories) within PRD scope
- ✅ @brd upstream reference valid
- ✅ No blocking validation errors

**Blocking Conditions**:
- ❌ Either score <90%
- ❌ Missing mandatory sections
- ❌ section 9 missing or placeholder-only
- ❌ section 7 contains EARS/BDD-level detail
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
2. Calculate scores using criteria in PRD_CREATION_RULES.md sections 8-9
3. Ensure both scores ≥90% before commit

### Issue 2: section Numbering Inconsistencies

**Symptoms**:
```
❌ MISSING NUMBER: Found "## Document Control", expected "## 0. Document Control"
❌ DUPLICATE NUMBER: section number 6 appears twice
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
❌ SCOPE VIOLATION: section 7 contains WHEN-THE-SHALL format (belongs in EARS)
❌ SCOPE VIOLATION: section 7 contains Given-When-Then scenarios (belongs in BDD)
```

**Root Cause**: Mixing PRD-level requirements with EARS/BDD-level technical details

**Fix**:
1. Add scope note from PRD-TEMPLATE.md to section 7
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
❌ BLOCKING ERROR: section 9 (Customer-Facing Content) is missing
❌ BLOCKING ERROR: section 9 contains only placeholder text
```

**Root Cause**: section 9 treated as optional or overlooked as new mandatory requirement

**Fix**:
1. Add section 9 header with (MANDATORY) designation:
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
2. Add topics to "Architecture Decision Requirements" table in section 17:
   ```markdown
   | Topic Area | Decision Needed | Business Driver |
   |------------|-----------------|-----------------|
   | [Topic] | [Description] | [PRD reference] |
   ```
3. Describe architectural decision topics without assuming ADR already exists
4. Reference workflow: BRD → PRD → ADR → SYS/EARS

---

## 6. Additional Validation Checks

### CHECK 11: EARS Enhancement Appendix Validation (Section 19)

**Purpose**: Verify Section 19 (EARS Enhancement Appendix) is complete and EARS-Ready
**Type**: Error (blocking for EARS progression)

**Requirements**:
- Section 19 must exist with all 5 subsections (19.1-19.5)
- Timing Profile Matrix (19.1) must have at least 3 operations with p50/p95/p99
- Boundary Value Matrix (19.2) must have at least 3 thresholds with explicit operators
- State Transition Diagram (19.3) must include error state transitions
- Fallback Path Documentation (19.4) must cover all external dependencies
- EARS-Ready Checklist (19.5) must be completed

**Validation Rules**:

| Subsection | Minimum Content | Validation |
|------------|-----------------|------------|
| 19.1 Timing Profiles | 3+ operations | Each row has p50, p95, p99 values |
| 19.2 Boundary Values | 3+ thresholds | Each row has ≥/>/≤/< operator |
| 19.3 State Diagram | Mermaid diagram | Contains error states (Failed, Timeout) |
| 19.4 Fallback Paths | All dependencies | Each row has Fallback Behavior column |
| 19.5 Checklist | Complete | All checkboxes addressed |

**Error Messages**:
```
❌ MISSING SECTION: ## 19. EARS Enhancement Appendix
❌ INCOMPLETE: Section 19.1 requires at least 3 operations with timing profiles
❌ INCOMPLETE: Section 19.2 requires explicit boundary operators (≥, >, ≤, <)
❌ INCOMPLETE: Section 19.3 state diagram missing error transitions
❌ INCOMPLETE: Section 19.4 missing fallback documentation for external dependencies
```

**Resolution Steps**:
1. Add Section 19 from PRD-TEMPLATE.md
2. Complete timing profile matrix with p50/p95/p99 for all operations
3. Specify boundary operators for all threshold values
4. Add error state transitions to state diagram
5. Document fallback behavior for each external dependency

---

### CHECK 12: Bidirectional Reference Validation

**Purpose**: Verify all cross-PRD references are bidirectional (A→B implies B→A)
**Type**: Warning (recommended fix before commit)

**Requirements**:
- Every `@prd: PRD-XXX` reference must have reciprocal reference in target document
- No placeholder IDs (PRD-XXX, TBD, undefined)
- Referenced documents must exist
- Tag format required (not prose references like "see PRD-022")

**Validation Algorithm**:
```
1. Extract all @prd: tags from this document → Set A
2. For each referenced PRD in Set A:
   a. Verify target file exists
   b. Extract @prd: tags from target → Set B
   c. Verify this PRD is in Set B (reciprocal)
3. Report missing reciprocal references
```

**Error Messages**:
```
⚠️ WARNING: @prd: PRD-022 reference found, but PRD-022 does not reference this document
⚠️ WARNING: Found placeholder ID "PRD-XXX" - replace with actual ID or null
⚠️ WARNING: @prd: PRD-099 references non-existent document
⚠️ WARNING: Prose reference "see PRD-016" should use tag format @prd: PRD-016
```

**Resolution Steps**:
1. For missing reciprocal: Add `@prd: [this-PRD]` to referenced document
2. For placeholder: Replace with actual PRD ID or use `null`
3. For non-existent: Remove reference or create target document
4. For prose: Convert to `@prd: PRD-NNN` format

**Reciprocal Reference Table** (add to document if missing):
```markdown
| This PRD | References | Relationship | Reciprocal Status |
|----------|------------|--------------|-------------------|
| PRD-NNN | @prd: PRD-XXX | Primary/Fallback | ✅/❌ |
```

---

### CHECK 13: Feature ID Format Validation

**Purpose**: Verify all Feature IDs follow the standard format `FR-{PRD#}-{sequence}`
**Type**: Warning (recommended fix)

**Valid Format**: `FR-NNN-NNN` (e.g., FR-001-001, FR-022-015)

**Validation Regex**: `^FR-\d{3}-\d{3}$`

**Invalid Patterns to Detect**:

| Pattern | Issue | Fix |
|---------|-------|-----|
| `FR-001` | Missing sequence | `FR-001-001` |
| `FR-AGENT-001` | Non-standard prefix | `FR-022-001` |
| `Feature 3.1` | Text format | `FR-025-003` |
| `F-001-001` | Wrong prefix | `FR-001-001` |
| `FR-1-1` | Not zero-padded | `FR-001-001` |

**Error Messages**:
```
⚠️ WARNING: Invalid Feature ID "FR-001" found - missing sequence number
⚠️ WARNING: Non-standard Feature ID "FR-AGENT-001" - use FR-022-001 format
⚠️ WARNING: Text format "Feature 3.1" detected - convert to FR-NNN-NNN
```

**Resolution Steps**:
1. Identify PRD number (e.g., PRD-022 → 022)
2. Convert to standard format: `FR-{PRD#}-{sequence}`
3. Update all references to the Feature ID
4. Run validation again to confirm

---

### CHECK 14: Threshold Registry Compliance

**Purpose**: Verify numeric thresholds reference centralized registry where applicable
**Type**: Warning (recommended for new PRDs, required for high-risk PRDs)

**Requirements**:
- Numeric thresholds shared across 2+ PRDs must reference Threshold Registry
- Use format: `@prd: PRD-XXX:{category}.{key}`
- No "magic numbers" for common thresholds (KYC limits, risk scores, timeouts)

**Threshold Categories Requiring Registry Reference**:

| Category | Example Thresholds | Registry Key Pattern |
|----------|-------------------|---------------------|
| KYC/KYB Limits | Daily limits, monthly limits | `kyc.l1.daily`, `kyb.l2.monthly` |
| Risk Scores | Low/Medium/High boundaries | `risk.low.max`, `risk.high.min` |
| Performance | p50/p95/p99 targets | `perf.api.standard.p95` |
| Timeouts | API, session, job timeouts | `timeout.partner.bridge` |
| Rate Limits | API, transaction frequency | `rate.api.user.standard` |

**Validation Rules**:
1. Scan document for numeric threshold patterns
2. Check if pattern matches known threshold category
3. Verify registry reference exists if category requires it

**Error Messages**:
```
⚠️ WARNING: Hardcoded KYC limit "$1,000" found - reference @prd: PRD-035:kyc.l1.daily
⚠️ WARNING: Risk score threshold "75" found - reference @prd: PRD-035:risk.high.min
⚠️ WARNING: Timeout value "30s" found - reference @prd: PRD-035:timeout.partner.bridge
```

**Resolution Steps**:
1. Identify threshold category (KYC, risk, performance, timeout, rate)
2. Look up key in Threshold Registry (PRD-035 or project-specific)
3. Add reference: `(per @prd: PRD-035:{category}.{key})`
4. If threshold doesn't exist in registry: Add to registry first

**Example Fix**:
```markdown
# Before (non-compliant)
Transaction limit: $1,000 USD

# After (compliant)
Transaction limit: $1,000 USD (per @prd: PRD-035:kyc.l1.daily)
```

---

## 7. Validation Summary Table

| Check | Type | Purpose | Blocking |
|-------|------|---------|----------|
| CHECK 1 | Required Fields | Document Control completeness | Yes |
| CHECK 2 | Dual Scoring Format | SYS-Ready + EARS-Ready format | Yes |
| CHECK 3 | Threshold Enforcement | ≥90% scores required | Yes |
| CHECK 4 | Section Numbering | Explicit 0-19 numbering | Yes |
| CHECK 5 | Mandatory Sections | All 20 sections present | Yes |
| CHECK 6 | Section Title Consistency | Match template titles | No |
| CHECK 7 | User Stories Scope | PRD-level only (no EARS/BDD) | Yes |
| CHECK 8 | Customer-Facing Content | Section 9 mandatory | Yes |
| CHECK 9 | No ADR Forward References | Topics only, no ADR-XXX | Yes |
| CHECK 10 | Traceability Tags | @brd upstream tag | No |
| CHECK 11 | EARS Enhancement Appendix | Section 19 complete | Yes (for EARS) |
| CHECK 12 | Bidirectional References | A→B implies B→A | No |
| CHECK 13 | Feature ID Format | FR-NNN-NNN format | No |
| CHECK 14 | Threshold Registry | Registry references | No |

---

**Framework Compliance**: 100% doc_flow SDD framework aligned (Layer 2 - Product Requirements)
**Maintained By**: Product Management Team, SDD Framework Team
**Review Frequency**: Updated with template and validation rule enhancements

---
