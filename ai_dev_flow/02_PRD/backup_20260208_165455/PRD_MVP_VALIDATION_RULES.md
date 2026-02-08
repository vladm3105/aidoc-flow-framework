---
title: "PRD MVP Validation Rules"
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

# =============================================================================
# 📋 Document Role: Validates PRD-MVP-TEMPLATE.md (default)
# - Authority: PRD-MVP-TEMPLATE.md is the primary standard for PRD structure; full template is archived
# - Purpose: AI checklist after document creation (derived from MVP template)
# - Scope: Includes all rules from PRD_CREATION_RULES.md plus validation extensions
# - On conflict: Defer to PRD-MVP-TEMPLATE.md
# =============================================================================
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
> - **Authority**: Validates compliance with `PRD-MVP-TEMPLATE.md` (primary standard; full template archived)
> - **Scope**: Use for quality gates before committing PRD changes

# PRD Validation Rules Reference

## MVP Validation Profile (DEFAULT)

**MVP validation is the framework default.** Full validation is applied only when explicitly triggered or when using full templates.

### MVP Detection

| Detection Method | Pattern | Result |
|------------------|---------|--------|
| Filename | `*-MVP-*.md` | MVP profile |
| Frontmatter | `template_profile: mvp` | MVP profile |
| Default (no markers) | — | MVP profile |
| Frontmatter | `template_profile: full` or `enterprise` | Full profile |

### Validation Differences

| Check Category | MVP Profile | Full Profile |
|----------------|-------------|--------------|
| Required sections (core) | Error | Error |
| Traceability tags (@brd) | Error | Error |
| Document Control fields | Error | Error |
| Extended sections (16-21) | **Warning** | Error |
| SYS-Ready Score threshold | 70/100 | 90/100 |
| EARS-Ready Score threshold | 70/100 | 90/100 |
| Customer Messaging | **Skip** | Required |

### Usage

```bash
# MVP validation (default)
python3 ai_dev_flow/02_PRD/scripts/validate_prd.py ai_dev_flow/02_PRD --profile mvp

# Full validation (explicit)
python3 ai_dev_flow/02_PRD/scripts/validate_prd.py ai_dev_flow/02_PRD --profile full
```

### Cross-Linking Tags (AI-Friendly)

Use same-layer cross-links to document PRD relationships in a machine-parseable way:
- `@depends: PRD-NN` — hard prerequisite PRD(s) that must be satisfied first.
- `@discoverability: PRD-NN (short rationale); PRD-NN (short rationale)` — related PRDs with brief reasons to aid AI search and ranking.

Validation handling: Recognized as info-level (non-blocking). Reported for visibility only.

---

> Path conventions: Examples below use a portable `docs/` root for new projects. In this repository, artifact folders live at the ai_dev_flow root (no `docs/` prefix). When running commands here, drop the `docs/` prefix. See README → "Using This Repo" for path mapping.

**Version**: 1.0.0
**Date**: 2025-11-26
**Last Updated**: 2025-11-26
**Purpose**: Complete validation rules for PRD documents
**Script**: `python 02_PRD/scripts/validate_prd.py`
**Primary Template**: `PRD-MVP-TEMPLATE.md` (full template archived)
**Framework**: AI Dev Flow SDD (100% compliant)

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

### PRD vs 06_SYS/EARS Distinctions

| Aspect | PRD (Layer 2) | SYS (Layer 6) | EARS (Layer 3) |
|--------|---------------|---------------|----------------|
| Focus | Product requirements | System requirements | Engineering requirements |
| Level | User capabilities | System capabilities | Technical specifications |
| Format | User stories, features | Functional/quality attributes | WHEN-THE-SHALL-WITHIN |
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

### Reserved ID Exemption (PRD-00_*)

**Scope**: Documents with reserved ID `000` are FULLY EXEMPT from validation.

**Pattern**: `PRD-00_*.md`

**Document Types**:
- Index documents (`PRD-00_index.md`)
- Traceability matrix templates (`PRD-00_TRACEABILITY_MATRIX-TEMPLATE.md`)
- Threshold registries (`PRD-00_threshold_registry_template.md`)
- Glossaries, checklists

**Rationale**: Reserved ID 000 documents are framework infrastructure (indexes, templates, reference materials), not project artifacts requiring traceability or quality gates.

**Validation Behavior**: Skip all checks when filename matches `PRD-00_*` pattern.

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
| BRD Reference | @brd: BRD.NN.EE.SS tag | MANDATORY |
| SYS-Ready Score | ✅ XX% (Target: ≥90%) | MANDATORY |
| EARS-Ready Score | ✅ XX% (Target: ≥90%) | MANDATORY |
| Priority | High / Medium / Low | OPTIONAL |
| Target Release | Release version/Quarter | OPTIONAL |
| Estimated Effort | Story Points or Person-Months | OPTIONAL |

**Note**: Optional fields (Priority, Target Release, Estimated Effort) are recommended but not validation-blocking. Document Revision History table is recommended but optional for Draft status; required for Review/Approved status.

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

**Purpose**: Verify all 21 sections (1-21) are numbered explicitly
**Type**: Error (blocking)

**Required section Numbers**:
```markdown
## 1. Document Control
## 2. Executive Summary
## 3. Problem Statement
## 4. Target Audience & User Personas
## 5. Success Metrics (KPIs)
## 6. Goals & Objectives
## 7. Scope & Requirements
## 8. User Stories & User Roles
## 9. Functional Requirements
## 10. Customer-Facing Content & Messaging (MANDATORY)
## 11. Acceptance Criteria
## 12. Constraints & Assumptions
## 13. Risk Assessment
## 14. Success Definition
## 15. Stakeholders & Communication
## 16. Implementation Approach
## 17. Budget & Resources
## 18. Traceability
## 19. References
## 20. EARS Enhancement Appendix
## 21. Quality Assurance & Testing Strategy
```

**Error Messages**:
```
❌ MISSING NUMBER: section header must be "## 1. Document Control"
❌ INCORRECT NUMBER: Found "## Document Control", expected "## 1. Document Control"
❌ DUPLICATE NUMBER: section number 6 appears twice
```

**Resolution Steps**:
1. Add explicit section number to each header
2. Use format: `## N. section Title`
3. Verify sequential numbering (1-21)
4. Check for duplicates or skipped numbers

### CHECK 5: Mandatory sections Presence

**Purpose**: Verify all 21 sections exist in document
**Type**: Error (blocking)

**All sections MANDATORY**: Every PRD must contain all 21 sections (1-21) with substantive content, not placeholders.

**Error Messages**:
```
❌ MISSING SECTION: ## 8. User Stories & User Roles
❌ MISSING SECTION: ## 10. Customer-Facing Content & Messaging (MANDATORY)
```

**Resolution Steps**:
1. Add missing section with correct header format
2. Populate with substantive content (not "TBD" or "TODO")
3. Follow section-specific requirements from PRD-MVP-TEMPLATE.md (full template archived)

### CHECK 6: section Title Consistency

**Purpose**: Verify section titles match template exactly
**Type**: Warning (recommended fix)

**Title Matching Rules**:
- section titles must match PRD-MVP-TEMPLATE.md character-for-character (full template archived)
- Capitalization must be identical
- Special markers like (MANDATORY) must be included where specified

**Error Messages**:
```
⚠️ WARNING: section 8 title should be "Customer-Facing Content & Messaging (MANDATORY)"
⚠️ WARNING: section 3 title should use "&" not "and"
```

**Resolution Steps**:
1. Copy exact title from PRD-MVP-TEMPLATE.md
2. Preserve capitalization and punctuation
3. Include (MANDATORY) marker for section 8

### CHECK 7: User Stories Scope Validation (section 8)

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
1. **Scope Note Present**: section 8 must include layer separation explanation
2. **Role Definitions**: User personas with characteristics and needs
3. **Story Summaries**: High-level capability descriptions
4. **No Technical Details**: No 03_EARS/04_BDD/SYS-level content

**Error Messages**:
```
❌ SCOPE VIOLATION: section 8 contains WHEN-THE-SHALL format (belongs in EARS)
❌ SCOPE VIOLATION: section 8 contains Given-When-Then scenarios (belongs in BDD)
❌ MISSING: section 8 scope note explaining layer separation
```

**Resolution Steps**:
1. Add scope note from PRD-MVP-TEMPLATE.md (full template archived)
2. Move EARS-level content to placeholder for future EARS document
3. Move BDD-level content to placeholder for future BDD tests
4. Keep only PRD-level role definitions and story summaries

### CHECK 8: Customer-Facing Content Mandatory (section 10)

> **Note**: CHECK numbers are sequential validation steps; they do not correspond to PRD section numbers.

**Purpose**: Enforce section 10 as blocking requirement
**Type**: Error (blocking)

**Requirements**:
- section 10 header must include (MANDATORY) designation
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
❌ BLOCKING ERROR: section 10 (Customer-Facing Content) is missing
❌ BLOCKING ERROR: section 10 header missing (MANDATORY) designation
❌ BLOCKING ERROR: section 10 contains only placeholder text
```

**Resolution Steps**:
1. Add section 10 if missing
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
@brd: BRD.NN.EE.SS
```

**Downstream Tags** (Optional but recommended):
```markdown
@sys: SYS.NN.EE.SS (planned)
@ears: EARS.NN.EE.SS (planned)
@bdd: BDD.NN.EE.SS (planned)
@req: REQ.NN.EE.SS (planned)
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

**section 1 - Document Control**:
- 11 required fields present (See CHECK 1)
- Dual scoring with ≥90% thresholds (See CHECK 2-3)
- Document Revision History table with at least one initial entry (required for Review/Approved status)

**section 2 - Executive Summary**:
- 2-3 sentence overview
- Business Value Proposition subsection
- Timeline subsection with 5 phases

**section 3 - Problem Statement**:
- Current State, Business Impact, Root Cause Analysis, Opportunity Assessment subsections
- Quantified business impact metrics
- Clear problem articulation

**section 4 - Target Audience & User Personas**:
- Primary Users, secondary Users, Business Stakeholders subsections
- At least 2 user personas with demographics, goals, pain points

**section 5 - Success Metrics (KPIs)**:
- Primary KPIs, secondary KPIs, Success Criteria by Phase subsections
- At least 3 measurable KPIs
- Baseline and target values specified

**section 6 - Goals & Objectives**:
- Primary Business Goals, secondary Objectives, Stretch Goals subsections
- SMART criteria applied (Specific, Measurable, Achievable, Relevant, Time-bound)

**section 7 - Scope & Requirements**:
- In Scope, Out of Scope, Dependencies, Assumptions subsections
- Clear boundary definitions

**section 8 - User Stories & User Roles**:
- Layer Separation scope note present (See CHECK 7)
- User role definitions
- Story summaries (not 03_EARS/BDD-level detail)

**section 9 - Functional Requirements**:
- User Journey Mapping, Capability Requirements subsections
- Requirements use unified format (PRD.NN.EE.SS)
- Each requirement testable

**section 10 - Customer-Facing Content & Messaging**:
- (MANDATORY) designation in header (See CHECK 8)
- Substantive content addressing customer-visible materials
- At least 3 content categories covered

**section 11 - Acceptance Criteria**:
- Business Acceptance, Technical Acceptance, Quality Assurance subsections
- Criteria verifiable by business stakeholders

**section 12 - Constraints & Assumptions**:
- Business Constraints, Technical Constraints, External Constraints, Key Assumptions subsections
- Each assumption identified with validation plan

**section 13 - Risk Assessment**:
- High-Risk Items, Risk Mitigation Plan subsections
- Risks categorized by severity and likelihood

**section 14 - Success Definition**:
- Go-Live Criteria, Post-Launch Validation, Measurement Timeline subsections
- Specific success thresholds

**section 15 - Stakeholders & Communication**:
- Core Team, Stakeholders, Communication Plan subsections
- RACI matrix or equivalent

**section 16 - Implementation Approach**:
- Development Phases, Testing Strategy subsections
- High-level timeline

**section 17 - Budget & Resources**:
- Development Budget, Operational Budget, Resource Requirements subsections
- Cost estimates with justification

**section 18 - Traceability**:
- Upstream Sources, Downstream Artifacts, Traceability Tags, Validation Evidence subsections
- @brd tag present (See CHECK 10)

**section 19 - References**:
- Internal Documentation, External Standards, Domain References, Technology References subsections
- All references valid and accessible

**section 20 - EARS Enhancement Appendix**:
- Timing Profile Matrix (20.1) with p50/p95/p99 values
- Boundary Value Matrix (20.2) with explicit operators
- State Transition Diagram (20.3) with error states
- Fallback Path Documentation (20.4) for external dependencies
- EARS-Ready Checklist (20.5) completed

---

## 4. Quality Gates

### Pre-Commit Checklist

**Before committing PRD to repository, verify**:

- [ ] **All 21 sections present** (1-21) with substantive content
- [ ] **section numbering explicit** (## N. Title format)
- [ ] **Dual scoring ≥90%** (SYS-Ready and EARS-Ready)
- [ ] **Customer-Facing Content (section 10)** populated with (MANDATORY) designation
- [ ] **User Stories (section 8)** include scope note, stay within PRD layer
- [ ] **No ADR-XXX forward references** (use topics only)
- [ ] **@brd upstream tag** present in Traceability section
- [ ] **Document Control** has all 11 required fields
- [ ] **YAML frontmatter** valid syntax
- [ ] **Run validation script**: `python 02_PRD/scripts/validate_prd.py [filename]`

### Validation Script Commands

```bash
# Validate single PRD (nested folder structure - DEFAULT)
python 02_PRD/scripts/validate_prd.py docs/02_PRD/PRD-01_product_name/PRD-01.0_product_name_index.md

# Validate all PRDs (section-based structure)
find docs/PRD -type f -name "PRD-*.md" -exec python 02_PRD/scripts/validate_prd.py {} \;

# Validate monolithic PRD (optional for <25KB)
python 02_PRD/scripts/validate_prd.py docs/02_PRD/PRD-01_product_name.md

# Check YAML frontmatter (nested structure)
python3 -c "import yaml; yaml.safe_load(open('docs/02_PRD/PRD-01_product_name/PRD-01.0_product_name_index.md').read().split('---')[1])"
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

**When to Advance to 03_EARS/SYS**:
- ✅ Both SYS-Ready and EARS-Ready scores ≥90%
- ✅ All 21 sections complete with substantive content
- ✅ section 10 (Customer-Facing Content) populated
- ✅ section 8 (User Stories) within PRD scope
- ✅ @brd upstream reference valid
- ✅ No blocking validation errors

**Blocking Conditions**:
- ❌ Either score <90%
- ❌ Missing mandatory sections
- ❌ section 10 missing or placeholder-only
- ❌ section 8 contains 03_EARS/BDD-level detail
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
❌ MISSING NUMBER: Found "## Document Control", expected "## 1. Document Control"
❌ DUPLICATE NUMBER: section number 6 appears twice
```

**Root Cause**: Manual editing without systematic renumbering or old template format

**Fix**:
1. Use find/replace to add numbers to all headers:
   ```
   ## Document Control → ## 1. Document Control
   ## Executive Summary → ## 2. Executive Summary
   ```
2. Verify sequential numbering 1-21 with no gaps
3. Check for duplicate section numbers
4. Compare with PRD-MVP-TEMPLATE.md for correct sequence (full template archived)

### Issue 3: User Stories Scope Violations

**Symptoms**:
```
❌ SCOPE VIOLATION: section 8 contains WHEN-THE-SHALL format (belongs in EARS)
❌ SCOPE VIOLATION: section 8 contains Given-When-Then scenarios (belongs in BDD)
```

**Root Cause**: Mixing PRD-level requirements with 03_EARS/BDD-level technical details

**Fix**:
1. Add scope note from PRD-MVP-TEMPLATE.md to section 8 (full template archived)
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
❌ BLOCKING ERROR: section 10 (Customer-Facing Content) is missing
❌ BLOCKING ERROR: section 10 contains only placeholder text
```

**Root Cause**: section 10 treated as optional or overlooked as new mandatory requirement

**Fix**:
1. Add section 10 header with (MANDATORY) designation:
   ```markdown
   ## 10. Customer-Facing Content & Messaging (MANDATORY)
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
2. Add topics to "Architecture Decision Requirements" table in section 15:
   ```markdown
   | Topic Area | Decision Needed | Business Driver |
   |------------|-----------------|-----------------|
   | [Topic] | [Description] | [PRD reference] |
   ```
3. Describe architectural decision topics without assuming ADR already exists
4. Reference workflow: BRD → PRD → EARS → BDD → ADR → SYS → REQ

---

## 6. Additional Validation Checks

### CHECK 11: EARS Enhancement Appendix Validation (Section 20)

**Purpose**: Verify Section 20 (EARS Enhancement Appendix) is complete and EARS-Ready
**Type**: Error (blocking for EARS progression)

**Requirements**:
- Section 20 must exist with all 5 subsections (20.1-20.5)
- Timing Profile Matrix (20.1) must have at least 3 operations with p50/p95/p99
- Boundary Value Matrix (20.2) must have at least 3 thresholds with explicit operators
- State Transition Diagram (20.3) must include error state transitions
- Fallback Path Documentation (20.4) must cover all external dependencies
- EARS-Ready Checklist (20.5) must be completed

**Validation Rules**:

| Subsection | Minimum Content | Validation |
|------------|-----------------|------------|
| 20.1 Timing Profiles | 3+ operations | Each row has p50, p95, p99 values |
| 20.2 Boundary Values | 3+ thresholds | Each row has ≥/>/≤/< operator |
| 20.3 State Diagram | Mermaid diagram | Contains error states (Failed, Timeout) |
| 20.4 Fallback Paths | All dependencies | Each row has Fallback Behavior column |
| 20.5 Checklist | Complete | All checkboxes addressed |

**Error Messages**:
```
❌ MISSING SECTION: ## 20. EARS Enhancement Appendix
❌ INCOMPLETE: Section 20.1 requires at least 3 operations with timing profiles
❌ INCOMPLETE: Section 20.2 requires explicit boundary operators (≥, >, ≤, <)
❌ INCOMPLETE: Section 20.3 state diagram missing error transitions
❌ INCOMPLETE: Section 20.4 missing fallback documentation for external dependencies
```

**Resolution Steps**:
1. Add Section 20 from PRD-MVP-TEMPLATE.md
2. Complete timing profile matrix with p50/p95/p99 for all operations
3. Specify boundary operators for all threshold values
4. Add error state transitions to state diagram
5. Document fallback behavior for each external dependency

---

### CHECK 12: Bidirectional Reference Validation

**Purpose**: Verify all cross-PRD references are bidirectional (A→B implies B→A)
**Type**: Warning (recommended fix before commit)

**Requirements**:
- Every `@prd: PRD.NN.EE.SS` reference must have reciprocal reference in target document
- No placeholder IDs (PRD.XXX.XXX, TBD, undefined)
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
⚠️ WARNING: @prd: PRD.22.01.01 reference found, but PRD-022 does not reference this document
⚠️ WARNING: Found placeholder ID "PRD.NN.EE.SS" - replace with actual ID or null
⚠️ WARNING: @prd: PRD.99.01.01 references non-existent document
⚠️ WARNING: Prose reference "see PRD-NN" should use tag format @prd: PRD.NN.NN.NN
```

**Resolution Steps**:
1. For missing reciprocal: Add `@prd: [this-PRD]` to referenced document
2. For placeholder: Replace with actual PRD ID or use `null`
3. For non-existent: Remove reference or create target document
4. For prose: Convert to `@prd: PRD.NN.EE.SS` format

**Reciprocal Reference Table** (add to document if missing):
```markdown
| This PRD | References | Relationship | Reciprocal Status |
|----------|------------|--------------|-------------------|
| PRD-NN | @prd: PRD.NN.EE.SS | Primary/Fallback | ✅/❌ |
```

---

### CHECK 13: Feature ID Format Validation

**Purpose**: Verify all Feature IDs follow the unified format `PRD.NN.EE.SS`
**Type**: Warning (recommended fix)

**Valid Format**: `PRD.NN.EE.SS` (e.g., PRD.22.01.01, PRD.22.01.15)

**Validation Regex**: `^PRD\.\d{2,9}\.\d{2,9}\.\d{2,9}$`

**Invalid Patterns to Detect**:

| Pattern | Issue | Fix |
|---------|-------|-----|
| `Feature-001` | Deprecated format | `PRD.NN.01.01` |
| `FR-AGENT-001` | Non-standard prefix | `PRD.NN.01.01` |
| `Feature 3.1` | Text format | `PRD.NN.01.03` |
| `F-01` | Deprecated F- format | `PRD.NN.01.01` |
| `PRD.1.1.1` | Not zero-padded | `PRD.01.01.01` |

**Error Messages**:
```
⚠️ WARNING: Deprecated Feature ID "Feature-001" found - use PRD.NN.TT.SS format
⚠️ WARNING: Non-standard Feature ID "FR-AGENT-001" - use PRD.NN.EE.SS format
⚠️ WARNING: Text format "Feature 3.1" detected - convert to PRD.NN.EE.SS
```

**Resolution Steps**:
1. Identify PRD number (e.g., PRD-022 → 022)
2. Convert to unified format: `PRD.{PRD#}.{sequence}`
3. Update all references to the Feature ID
4. Run validation again to confirm

---

### CHECK 14: Threshold Registry Compliance

**Purpose**: Verify numeric thresholds reference centralized registry where applicable
**Type**: Warning (recommended for new PRDs, required for high-risk PRDs)

**Requirements**:
- Numeric thresholds shared across 2+ PRDs must reference Threshold Registry
- Use format: `@prd: PRD.NN.EE.SS` with `@threshold: PRD.NN.{category}.{key}`
- No "magic numbers" for common thresholds (quota limits, risk scores, timeouts)

**Threshold Categories Requiring Registry Reference**:

| Category | Example Thresholds | Registry Key Pattern |
|----------|-------------------|---------------------|
| Quota Limits | Daily limits, monthly limits | `quota.l1.daily`, `quota.l2.monthly` |
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
⚠️ WARNING: Hardcoded quota limit "$1,000" found - reference @threshold: PRD.035.quota.l1.daily
⚠️ WARNING: Risk score threshold "75" found - reference @threshold: PRD.035.risk.high.min
⚠️ WARNING: Timeout value "30s" found - reference @threshold: PRD.035.timeout.partner.bridge
```

**Resolution Steps**:
1. Identify threshold category (quota, risk, performance, timeout, rate)
2. Look up key in Threshold Registry (PRD-035 or project-specific)
3. Add reference: `(per @threshold: PRD.035.{category}.{key})`
4. If threshold doesn't exist in registry: Add to registry first

**Example Fix**:
```markdown
# Before (non-compliant)
Transaction limit: $1,000 USD

# After (compliant)
Transaction limit: $1,000 USD (per @threshold: PRD.035.kyc.l1.daily)
```

---

### CHECK 15: Element ID Format Compliance ⭐ NEW

**Purpose**: Verify element IDs use unified 4-segment format, flag removed patterns.
**Type**: Error

| Check | Pattern | Result |
|-------|---------|--------|
| Valid format | `### PRD.NN.TT.SS:` | ✅ Pass |
| Removed pattern | `### F-XXX` | ❌ Fail - use PRD.NN.09.SS |
| Removed pattern | `### US-XXX` | ❌ Fail - use PRD.NN.09.SS |
| Removed pattern | `### FR-XXX` | ❌ Fail - use PRD.NN.01.SS |
| Removed pattern | `### AC-XXX` | ❌ Fail - use PRD.NN.06.SS |

**Regex**: `^###\s+PRD\.[0-9]{2,}\.[0-9]{2,}\.[0-9]{2,}:\s+.+$`

**Common Element Types for PRD**:
| Element Type | Code | Example |
|--------------|------|---------|
| Functional Requirement | 01 | PRD.02.01.01 |
| Quality Attribute | 02 | PRD.02.02.01 |
| Acceptance Criteria | 06 | PRD.02.06.01 |
| User Story | 09 | PRD.02.09.01 |
| Use Case | 11 | PRD.02.11.01 |
| Feature Item | 22 | PRD.02.22.01 |

**Fix**: Replace `### US-01: User Story` with `### PRD.02.09.01: User Story`

**Reference**: PRD_CREATION_RULES.md Section 4.1, [ID_NAMING_STANDARDS.md — Cross-Reference Link Format](../ID_NAMING_STANDARDS.md#cross-reference-link-format-mandatory)

---

## 7. Validation Summary Table

| Check | Type | Purpose | Blocking |
|-------|------|---------|----------|
| CHECK 1 | Required Fields | Document Control completeness | Yes |
| CHECK 2 | Dual Scoring Format | SYS-Ready + EARS-Ready format | Yes |
| CHECK 3 | Threshold Enforcement | ≥90% scores required | Yes |
| CHECK 4 | Section Numbering | Explicit 1-21 numbering | Yes |
| CHECK 5 | Mandatory Sections | All 21 sections present | Yes |
| CHECK 6 | Section Title Consistency | Match template titles | No |
| CHECK 7 | User Stories Scope | PRD-level only (no 03_EARS/BDD) | Yes |
| CHECK 8 | Customer-Facing Content | Section 10 mandatory | Yes |
| CHECK 9 | No ADR Forward References | Topics only, no ADR-XXX | Yes |
| CHECK 10 | Traceability Tags | @brd upstream tag | No |
| CHECK 11 | EARS Enhancement Appendix | Section 20 complete | Yes (for EARS) |
| CHECK 12 | Bidirectional References | A→B implies B→A | No |
| CHECK 13 | Feature ID Format | PRD.NN.EE.SS format | No |
| CHECK 14 | Threshold Registry | Registry references | No |
| CHECK 15 | Element ID Format | Unified 4-segment format | Yes |

---

**Framework Compliance**: 100% AI Dev Flow SDD framework aligned (Layer 2 - Product Requirements)
**Maintained By**: Product Management Team, SDD Framework Team
**Review Frequency**: Updated with template and validation rule enhancements

---
