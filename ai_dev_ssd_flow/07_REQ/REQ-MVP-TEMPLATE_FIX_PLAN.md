# REQ-MVP-TEMPLATE Fix Plan

**Created**: 2026-02-26
**Status**: Completed
**Version**: 1.1
**Last Updated**: 2026-02-26
**Target Files**:
- `REQ-MVP-TEMPLATE.md` (primary)
- `REQ-MVP-TEMPLATE.yaml` (autopilot)
- `REQ_MVP_VALIDATION_RULES.md`
- `REQ_MVP_SCHEMA.yaml`
- `REQ_MVP_CREATION_RULES.md`
- `REQ_MVP_QUALITY_GATE_VALIDATION.md`
- `README.md`

## Overview

Fix identified gaps in `/opt/data/docs_flow_framework/ai_dev_ssd_flow/07_REQ/` documents and align template, validation rules, schema, and skills to a consistent **11-section** MVP structure (Section 1: Document Control through Section 11: Implementation Notes).

**Key Issue**: The MD template has `## 13. MVP Lifecycle` which creates a numbering gap (no Section 12) and contradicts the stated "11 sections" in multiple places. The YAML template correctly has only 11 sections (no Section 13).

## Target Files

| File | Type | Priority |
|------|------|----------|
| `REQ-MVP-TEMPLATE.md` | MD Template (human workflow) | P1 |
| `REQ_MVP_VALIDATION_RULES.md` | Validation Rules | P1 |
| `REQ_MVP_SCHEMA.yaml` | Schema Definition | P1 |
| `REQ_MVP_CREATION_RULES.md` | Creation Rules | P1 |
| `REQ-MVP-TEMPLATE.yaml` | YAML Template (autopilot) | P1 |
| `REQ_MVP_QUALITY_GATE_VALIDATION.md` | Quality Gate Rules | P2 |
| `README.md` | Layer Documentation | P2 |
| `doc-req*/SKILL.md` | Skills (5 files) | P2 |

## Reference Files

- `ADR-MVP-TEMPLATE_FIX_PLAN.md` (for alignment reference - 11-section format)
- `PRD-MVP-TEMPLATE_FIX_PLAN.md` (for alignment reference - 21-section format)
- `ID_NAMING_STANDARDS.md` (for element ID format: `REQ.NN.TT.SS`)

---

## Gap Summary

| # | Gap | Severity | Location | Phase |
|---|-----|----------|----------|-------|
| 1 | Section 13 (MVP Lifecycle) exists in MD template but NOT in YAML template | Critical | REQ-MVP-TEMPLATE.md:482 vs YAML (no Section 13) | 2 |
| 2 | Section numbering jump: 1-11 then jumps to 13 (no Section 12) | Critical | REQ-MVP-TEMPLATE.md:482 | 2 |
| 3 | MD template line 36 says "11 sections" but has 12 section headers | Critical | REQ-MVP-TEMPLATE.md:36 | 2 |
| 4 | MD template line 478 says "Change History omitted for 11-section" but Section 13 exists | Critical | REQ-MVP-TEMPLATE.md:478 | 2 |
| 5 | Template footer says "12 sections" contradicting "11 sections" elsewhere | Critical | REQ-MVP-TEMPLATE.md:521 | 3 |
| 6 | YAML template line 413 says "11 mandatory sections" - CORRECT | Info | REQ-MVP-TEMPLATE.yaml:413 | - |
| 7 | Validation rules CHECK 11 validates Change History (Section 12) - but template omits it | High | REQ_MVP_VALIDATION_RULES.md:459-486 | 4 |
| 8 | Schema defines optional sections as "## 12. Appendix A" and "## 13. Appendix B" - conflicts with template's "## 13. MVP Lifecycle" | High | REQ_MVP_SCHEMA.yaml:245-253 | 4 |
| 9 | Creation rules TOC line 58 says "12 sections" but line 138 says "11 sections" | High | REQ_MVP_CREATION_RULES.md:58, 138 | 4 |
| 10 | doc-req skill says "12 Required Sections" - misaligned with MVP 11-section | High | doc-req/SKILL.md:85 | 5 |
| 11 | doc-req-validator says "Required Sections (12 sections)" | High | doc-req-validator/SKILL.md:109 | 5 |
| 12 | doc-req_quickref.md has wrong path (`docs/REQ/` → `docs/07_REQ/`) | Medium | doc-req_quickref.md:30 | 5 |

**DEFINITIVE DECISION**: Keep **11-section** MVP structure (matching YAML template, schema, and validation rules).

**Resolution**: Remove Section 13 (MVP Lifecycle) from MD template OR merge its content into Section 11 (Implementation Notes) as subsection 11.4.

**Rationale**:
- YAML template has 11 sections (correct, authoritative for autopilot)
- Schema line 458 says "All 11 MVP sections must be present"
- Schema line 298 says "Core MVP has 11 mandatory sections (1–11); 12–13 are optional appendices"
- Validation rules line 47 says "Required sections (11 total)"
- The "MVP Lifecycle" content is guidance, not a core requirement section

---

## Phase 0: Pre-Implementation

### 0.1 Backup All Files

```bash
# Create backup directory
mkdir -p /opt/data/docs_flow_framework/ai_dev_ssd_flow/07_REQ/.backup_2026-02-26

# Backup templates and rules
cp REQ-MVP-TEMPLATE.md .backup_2026-02-26/
cp REQ-MVP-TEMPLATE.yaml .backup_2026-02-26/
cp REQ_MVP_VALIDATION_RULES.md .backup_2026-02-26/
cp REQ_MVP_CREATION_RULES.md .backup_2026-02-26/
cp REQ_MVP_QUALITY_GATE_VALIDATION.md .backup_2026-02-26/
cp REQ_MVP_SCHEMA.yaml .backup_2026-02-26/
cp README.md .backup_2026-02-26/

# Backup skills
cp -r /opt/data/docs_flow_framework/.claude/skills/doc-req* .backup_2026-02-26/
```

### 0.2 Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Existing REQs reference old section numbers | Medium | High | Document migration guide |
| Autopilot fails with new structure | Medium | High | Update YAML template in Phase 4.5 |
| Skills produce invalid output | Medium | Medium | Update all skills in Phase 5 |
| Validation rules mismatch | Low | Medium | Verify CHECK numbers align |
| Cross-document links break | Low | Low | Update references in Phase 4 |

### 0.3 Rollback Plan

**If issues occur during implementation:**

1. **Immediate Rollback**:
   ```bash
   # Restore all files
   cp .backup_2026-02-26/REQ-MVP-TEMPLATE.md ./
   cp .backup_2026-02-26/REQ-MVP-TEMPLATE.yaml ./
   cp .backup_2026-02-26/REQ_MVP_VALIDATION_RULES.md ./
   cp .backup_2026-02-26/REQ_MVP_CREATION_RULES.md ./
   cp .backup_2026-02-26/REQ_MVP_QUALITY_GATE_VALIDATION.md ./
   cp .backup_2026-02-26/REQ_MVP_SCHEMA.yaml ./
   cp .backup_2026-02-26/README.md ./

   # Restore skills
   cp -r .backup_2026-02-26/doc-req* /opt/data/docs_flow_framework/.claude/skills/
   ```

2. **Partial Rollback**: Revert only affected files from backup

3. **Post-Rollback**: Re-run validators to confirm restored state

### 0.4 Downstream Impact Analysis

| Downstream Artifact | Impact | Action Required |
|--------------------|--------|-----------------|
| Existing REQ documents | Section 13 merged into 11.4 | Migration guide provided |
| SPEC templates | Reference REQ sections | Verify SPEC-MVP-TEMPLATE references |
| CTR templates | Reference REQ traceability | Verify CTR references to REQ sections |
| Validation scripts | CHECK numbers reference sections | Verify REQ_MVP_VALIDATION_RULES.md |
| Autopilot workflows | Generate from YAML template | No change (YAML already correct) |
| doc-req-reviewer | Check section completeness | Verify 11-section check |
| doc-req-fixer | Fix phases reference sections | Verify section creation logic |
| Quality Gate validation | Corpus-level checks | Verify REQ_MVP_QUALITY_GATE_VALIDATION.md |

### 0.5 Decision: Target Section Count

**Analysis**:
- MD template line 36: "11 sections required"
- MD template line 478: "Change History section intentionally omitted for MVP (11 sections)"
- MD template line 521 (footer): "12 sections" - **INCORRECT**
- YAML template line 413: "11 mandatory sections" - **CORRECT**
- Schema (REQ_MVP_SCHEMA.yaml line 458): "All 11 MVP sections must be present" - **CORRECT**
- Schema (REQ_MVP_SCHEMA.yaml line 298): "Core MVP has 11 mandatory sections (1–11)" - **CORRECT**
- Validation rules (REQ_MVP_VALIDATION_RULES.md line 47): "Required sections (11 total)" - **CORRECT**
- doc-req skill line 85: "12 Required Sections" - **MISALIGNED**
- doc-req-validator skill line 109: "12 sections" - **MISALIGNED**

**Actual MD Template Section Headers** (verified):
```
## 1. Document Control
## 2. Requirement Description
## 3. Functional Specification
## 4. Interface Definition
## 5. Error Handling
## 6. Quality Attributes
## 7. Configuration
## 8. Testing Requirements
## 9. Acceptance Criteria
## 10. Traceability
## 11. Implementation Notes
## 13. MVP Lifecycle      ← EXTRA: Not in YAML template, breaks numbering
```

**YAML Template Sections** (authoritative for autopilot):
```
section_1: document_control
section_2: requirement_description (mapped to section_1_description)
section_3: functional_specification
section_4: interface_definition
section_5: error_handling
section_6: quality_attributes
section_7: configuration
section_8: testing_requirements
section_9: acceptance_criteria
section_10: traceability
section_11: implementation_notes
(NO Section 12 or 13)
```

**DECISION**: Keep **11-section** MVP structure (matching YAML template, schema, validation rules)

**Action**: Remove `## 13. MVP Lifecycle` from MD template OR merge into Section 11 as subsection `### 11.4 MVP Lifecycle`

| Section | Title (Canonical) |
|---------|-------------------|
| 1 | Document Control |
| 2 | Requirement Description |
| 3 | Functional Specification |
| 4 | Interface Definition |
| 5 | Error Handling |
| 6 | Quality Attributes |
| 7 | Configuration |
| 8 | Testing Requirements |
| 9 | Acceptance Criteria |
| 10 | Traceability |
| 11 | Implementation Notes |

**Recommended Resolution**: Merge MVP Lifecycle content into Section 11 (Implementation Notes) as subsection 11.4. This:
- Preserves valuable lifecycle guidance
- Maintains 11-section structure
- Aligns MD template with YAML template
- Removes the Section 13 numbering anomaly

---

## Phase 1: Critical Structural Analysis

### 1.1 Section Count Verification

**Current MD Template Sections** (verified actual headers):

```markdown
## 1. Document Control
## 2. Requirement Description
## 3. Functional Specification
## 4. Interface Definition
## 5. Error Handling
## 6. Quality Attributes
## 7. Configuration
## 8. Testing Requirements
## 9. Acceptance Criteria
## 10. Traceability
## 11. Implementation Notes
## 13. MVP Lifecycle        ← EXTRA (not in YAML template)
```

**Count**: 12 section headers (1-11 + 13, missing 12)

**Issue**: Section 13 exists but:
- YAML template has only 11 sections (no Section 13)
- Schema says "11 MVP sections" (Sections 12-13 are optional appendices)
- Numbering jumps from 11 to 13

### 1.2 Resolution Options

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| A | Merge Section 13 content into Section 11.4 (subsection) | Preserves content, maintains 11 sections, aligns with YAML | Minor structural change |
| B | Remove Section 13 entirely | Simplest fix, perfect 11-section match | Loses lifecycle guidance |
| C | Renumber 13→12, update to 12 sections | Consistent numbering | Contradicts schema/validation/YAML |

**Recommended**: **Option A** - Merge MVP Lifecycle into Section 11 (Implementation Notes) as subsection `### 11.4 MVP Lifecycle`. This:
- Preserves valuable lifecycle guidance
- Maintains strict 11-section MVP structure
- Aligns MD with YAML template (authoritative for autopilot)
- Matches schema, validation rules, and creation rules

---

## Phase 2: Template Section Restructuring

### 2.1 Merge Section 13 into Section 11

**File**: `REQ-MVP-TEMPLATE.md`

**Action**: Convert `## 13. MVP Lifecycle` to subsection `### 11.4 MVP Lifecycle`

**Current** (line 482):
```markdown
## 13. MVP Lifecycle (MVP → PROD → NEW MVP)
```

**Change To**:
```markdown
### 11.4 MVP Lifecycle (MVP → PROD → NEW MVP)
```

**Subsection renumbering**:
- `### 13.1 Lifecycle Phases` → `### 11.4.1 Lifecycle Phases`
- `### 13.2 When to Create a New REQ` → `### 11.4.2 When to Create a New REQ`
- `### 13.3 Cross-REQ Traceability` → `### 11.4.3 Cross-REQ Traceability`

### 2.2 Remove Section 13 Header

Delete the `## 13. MVP Lifecycle` line entirely (keep content, change hierarchy).

### 2.3 Update Footer to Match 11 Sections

**File**: `REQ-MVP-TEMPLATE.md`

**Location**: Around line 521

**Current**:
```markdown
> - 12 sections - this is the standard REQ template structure
```

**Change To**:
```markdown
> - 11 sections - this is the standard REQ MVP template structure
```

### 2.4 Verify Line 36 Statement (No Change Needed)

**Location**: Line 36

**Current** (CORRECT):
```markdown
11 sections required
```

**Action**: No change needed - this is already correct.

### 2.5 Verify Line 478 Statement (No Change Needed)

**Location**: Line 478

**Current** (CORRECT):
```markdown
Change History section is intentionally omitted for MVP to keep 11-section structure
```

**Action**: No change needed - this is already correct.

---

## Phase 3: Template Minor Fixes

### 3.1 Verify Frontmatter Metadata

Verify existing metadata (no changes needed to section count):

```yaml
custom_fields:
  # ... existing fields ...
  schema_version: "1.1"          # Current value
  # Note: total_sections not present - no need to add
```

**Action**: No change needed to frontmatter.

### 3.2 Update Template Footer

Change footer to say 11 sections:

**Current** (line 521):
```markdown
> - 12 sections - this is the standard REQ template structure
```

**Change To**:
```markdown
> - 11 sections - this is the standard REQ MVP template structure
```

### 3.3 Verify Footer Content

Ensure footer accurately reflects structure:

```markdown
---

**Document Version**: 0.1.0
**Template Version**: 1.0 (MVP)
**Last Updated**: 2026-02-26

---

> **MVP Template Notes**:
> - 11 sections - this is the standard REQ MVP template structure
> - Single file - no document splitting required
> - Focus on SPEC-ready, atomic requirements
> - All 6 upstream traceability tags required (Layer 7)
> - SPEC-Ready/CTR-Ready thresholds: ≥90%
> - Uses `@threshold` tags for quantitative values
> - **Lifecycle**: MVP → PROD → NEW MVP (no separate "full REQ" template)
```

---

## Phase 4: Update Supporting Documents

### 4.1 Verify Validation Rules Section List (No Change Needed)

**File**: `REQ_MVP_VALIDATION_RULES.md`

**Current** (line 47): "Required sections (11 total)" - **CORRECT**

**Current section list (lines 138-150)** - **CORRECT**:

```markdown
## 1. Document Control
## 2. Requirement Description
## 3. Functional Specification
## 4. Interface Definition
## 5. Error Handling
## 6. Quality Attributes
## 7. Configuration
## 8. Testing Requirements
## 9. Acceptance Criteria
## 10. Traceability
## 11. Implementation Notes
```

**Action**: No change needed - validation rules already list correct 11 sections.

### 4.1b Update CHECK 11 (Change History Validation)

**File**: `REQ_MVP_VALIDATION_RULES.md`

**Issue**: CHECK 11 (lines 459-486) validates Change History section, but template explicitly omits it.

**Current** (line 459-486):
```markdown
### CHECK 11: Change History
**Purpose**: Verify change history table exists and matches version
```

**Action Options**:
1. **Mark as Info-only**: Change CHECK 11 from Error to Info for MVP profile
2. **Skip for MVP**: Add "MVP Profile: Skip this check" note
3. **Remove CHECK 11**: Delete entirely since Change History is omitted

**Recommended**: Add MVP exception note:
```markdown
### CHECK 11: Change History

**Purpose**: Verify change history table exists and matches version
**Type**: Warning (non-blocking for MVP - Change History intentionally omitted)
**MVP Note**: This check is skipped for MVP template documents.
```

### 4.2 Verify Schema Required Sections (No Change Needed)

**File**: `REQ_MVP_SCHEMA.yaml`

**Current** (lines 169-243): `mvp_sections` has 11 entries (Title + Sections 1-11) - **CORRECT**

**Current** (line 458): "All 11 MVP sections must be present" - **CORRECT**

**Current** (line 298): "Core MVP has 11 mandatory sections (1–11); 12–13 are optional appendices" - **CORRECT**

**Action**: No change needed - schema already defines correct 11-section structure.

**Note on Optional Sections** (lines 245-253):
Schema defines `## 12. Appendix A` and `## 13. Appendix B` as optional. These are distinct from the erroneous `## 13. MVP Lifecycle` in the MD template.

### 4.3 Update Creation Rules Section List

**File**: `REQ_MVP_CREATION_RULES.md`

**Fix 1** (line 58 - TOC entry): Change "12 Required sections" to "11 Required sections"

**Current**:
```markdown
2. [Document Structure (12 Required sections)](#2-document-structure-12-required-sections)
```

**Change To**:
```markdown
2. [Document Structure (11 Required sections)](#2-document-structure-11-required-sections)
```

**Fix 2** (line 138 - Section header): Already correct "11 Required sections — MVP"

**Verify section list (lines 142-156)** - Already correct:

```markdown
## 2. Document Structure (11 Required sections — MVP)

REQ documents follow a streamlined **11-section** MVP structure:

| # | Section | Purpose |
|---|---------|---------|
| 1 | Document Control | Metadata with SPEC-Ready Score |
| 2 | Requirement Description | Atomic requirement + context + scenario |
| 3 | Functional Specification | Core capabilities + business rules + I/O |
| 4 | Interface Definition | API contract + schemas/DTOs |
| 5 | Error Handling | Exception catalog + recovery strategies |
| 6 | Quality Attributes | Performance/security/reliability targets |
| 7 | Configuration | Parameters, feature flags, validation |
| 8 | Testing Requirements | Unit, Integration, BDD scenarios |
| 9 | Acceptance Criteria | ≥3 measurable criteria (MVP) |
| 10 | Traceability | Upstream chain, downstream artifacts, tags |
| 11 | Implementation Notes | Technical approach, code locations, dependencies |
```

**Action**: Only fix TOC entry (line 58) to match section header (line 138).

### 4.4 Update Quality Gate Section List

**File**: `REQ_MVP_QUALITY_GATE_VALIDATION.md`

Verify Section 3.2 (or relevant CHECK) reflects 11-section structure:

```markdown
### 3.2 Required Document Structure (Per Template)

| # | Section | Required |
|---|---------|----------|
| 0 | **YAML Frontmatter** | YES - title, tags, custom_fields |
| 1 | **Section 1: Document Control** | YES |
| 2 | **Section 2: Requirement Description** | YES |
| 3 | **Section 3: Functional Specification** | YES |
| 4 | **Section 4: Interface Definition** | YES |
| 5 | **Section 5: Error Handling** | YES |
| 6 | **Section 6: Quality Attributes** | YES |
| 7 | **Section 7: Configuration** | YES |
| 8 | **Section 8: Testing Requirements** | YES |
| 9 | **Section 9: Acceptance Criteria** | YES |
| 10 | **Section 10: Traceability** | YES |
| 11 | **Section 11: Implementation Notes** | YES |
```

**Action**: Verify Quality Gate matches this 11-section structure. Update if necessary.

### 4.5 Verify README.md

- Verify section count says 11 (not 12)
- Verify section reference table matches template (Sections 1-11)
- Ensure REQ MVP format documentation is accurate

---

## Phase 4.6: Verify YAML Template (No Change Needed)

**File**: `REQ-MVP-TEMPLATE.yaml`

The YAML template is **already correct** with 11 sections. The MD template needs to align to YAML, not vice versa.

### 4.6.1 Current YAML Structure (CORRECT)

```yaml
# Line 413: "11 mandatory sections; Change History removed for MVP"

section_1: document_control
section_2: requirement_description (via section_1_description)
section_3: functional_specification
section_4: interface_definition
section_5: error_handling
section_6: quality_attributes
section_7: configuration
section_8: testing_requirements
section_9: acceptance_criteria
section_10: traceability
section_11: implementation_notes
```

**Action**: No change needed - YAML template already has correct 11-section structure.

---

## Phase 5: Update doc-req* Skills

### 5.1 Target Skill Files

| Skill | File Path | Update Scope |
|-------|-----------|--------------|
| doc-req | `.claude/skills/doc-req/SKILL.md` | Line 85: Change "12 Required Sections" → "11 Required Sections" |
| doc-req_quickref | `.claude/skills/doc-req_quickref.md` | Fix path `docs/REQ/` → `docs/07_REQ/`, change section count 12→11 |
| doc-req-validator | `.claude/skills/doc-req-validator/SKILL.md` | Line 109: Change "12 sections" → "11 sections" |
| doc-req-reviewer | `.claude/skills/doc-req-reviewer/SKILL.md` | Update review criteria for 11 sections |
| doc-req-fixer | `.claude/skills/doc-req-fixer/SKILL.md` | Update fix patterns for 11 sections |
| doc-req-autopilot | `.claude/skills/doc-req-autopilot/SKILL.md` | Verify section references produce 11 sections |

### 5.2 doc-req/SKILL.md Fixes

**Line 85**: Change "12 Required Sections" to "11 Required Sections":

```markdown
### 1. REQ MVP Format (11 Required Sections)

| # | Section | Purpose |
|---|---------|---------|
| 1 | Document Control | Metadata, SPEC-Ready Score |
| 2 | Requirement Description | Atomic requirement + context + scenario |
| 3 | Functional Specification | Core capabilities + business rules + I/O |
| 4 | Interface Definition | API contract + schemas/DTOs |
| 5 | Error Handling | Exception catalog + recovery strategies |
| 6 | Quality Attributes | Performance/security/reliability targets |
| 7 | Configuration | Parameters, feature flags, validation |
| 8 | Testing Requirements | Unit, Integration, BDD scenarios |
| 9 | Acceptance Criteria | ≥3 measurable criteria (MVP) |
| 10 | Traceability | Upstream chain, downstream artifacts, tags |
| 11 | Implementation Notes | Technical approach, code locations, dependencies |
```

### 5.3 doc-req_quickref.md Fixes

**Path correction** (line ~30):
```markdown
# Before:
- Template: `docs/REQ/REQ-MVP-TEMPLATE.md`

# After:
- Template: `docs/07_REQ/REQ-MVP-TEMPLATE.md`
```

**Section count update** (line ~33):
```markdown
# Before:
## REQ v3.0 Format (12 Sections)

# After:
## REQ MVP Format (11 Sections)
```

### 5.4 doc-req-validator/SKILL.md Fixes

**Line 109**: Change "Required Sections (12 sections)" to "Required Sections (11 sections)"

Update section list to match template's 11 sections.

### 5.5 doc-req-reviewer/SKILL.md Fixes

Update review criteria to reference 11 sections (Sections 1-11).

### 5.6 doc-req-fixer/SKILL.md Fixes

Update fix patterns for 11-section structure (no Section 12 or 13).

### 5.7 doc-req-autopilot/SKILL.md Fixes

Verify generation logic produces 11 sections (matching YAML template).

---

## Phase 6: Minor Fixes and Metadata

### 6.1 Verify Version Metadata in Template

Verify YAML frontmatter in `REQ-MVP-TEMPLATE.md` is correct:

```yaml
---
title: "REQ-MVP-TEMPLATE: Requirements Document (MVP)"
tags:
  - req-template
  - mvp-template
  - layer-7-artifact
  - document-template
  - shared-architecture
custom_fields:
  document_type: template
  artifact_type: REQ
  layer: 7
  template_profile: mvp
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  schema_version: "1.1"          # Current value - no change needed
  # Note: total_sections field not present - no need to add
---
```

**Action**: No changes needed to frontmatter - existing metadata is correct.

---

## Phase 7: Testing & Validation

### 7.1 Template Validation

| Test | Command/Action | Expected Result |
|------|----------------|-----------------|
| Syntax check | Open in markdown viewer | Renders without errors |
| Section count | Count `## N.` headers | 11 sections (1-11) |
| Duplicate check | Search for duplicate headers | 0 duplicates |
| Frontmatter | Validate YAML | Single valid block |
| Section 12/13 check | Search for "## 12" or "## 13" | 0 matches (merged into 11.4) |

### 7.2 Schema Validation

```bash
# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('REQ_MVP_SCHEMA.yaml').read())"

# Check section count in schema
grep -c "pattern:" REQ_MVP_SCHEMA.yaml | head -12
# Expected: 11 section patterns (plus Title H1)
```

### 7.3 Skill Testing

| Skill | Test Action | Expected Result |
|-------|-------------|-----------------|
| doc-req | Create test REQ | 11-section REQ generated |
| doc-req-validator | Validate test REQ | Pass all checks |
| doc-req-autopilot | Generate REQ from YAML | Valid 11-section output |

### 7.4 YAML ↔ MD Template Sync Verification

**Purpose**: Ensure MD template and YAML template are aligned after changes.

| Check | MD Template | YAML Template | Expected |
|-------|-------------|---------------|----------|
| Total sections | Count `## N.` headers | Count `section_N_*` entries | 11 each |
| Section titles | Extract from headers | Extract from keys | Match exactly |
| Schema version | `custom_fields.schema_version` | `schema_version:` | Match |

**Verification Command**:
```bash
# Count sections in MD template
grep -c "^## [0-9]" REQ-MVP-TEMPLATE.md
# Expected: 11

# Count sections in YAML template
grep -c "^section_[0-9]" REQ-MVP-TEMPLATE.yaml
# Expected: 11

# Verify no Section 12 or 13 as main sections
grep "^## 1[23]\." REQ-MVP-TEMPLATE.md
# Expected: No output (merged into subsection 11.4)
```

---

## Execution Order

| Step | Phase | Action | Dependencies |
|------|-------|--------|--------------|
| 1 | 0 | Create backups | None |
| 2 | 2.1-2.2 | Merge Section 13 into Section 11.4 | Backup complete |
| 3 | 2.3 | Update template footer (12→11 sections) | Step 2 |
| 4 | 3 | Verify template metadata | Step 3 |
| 5 | 4.1 | Verify Validation Rules (already 11 sections) | Step 4 |
| 6 | 4.1b | Update CHECK 11 (add MVP skip note) | Step 5 |
| 7 | 4.2 | Verify Schema (already 11 sections) | Step 6 |
| 8 | 4.3 | Fix Creation Rules TOC (12→11) | Step 7 |
| 9 | 4.4 | Verify Quality Gate (11 sections) | Step 8 |
| 10 | 4.5 | Update README.md (if needed) | Step 9 |
| 11 | 4.6 | Verify YAML template (already 11 sections) | Step 10 |
| 12 | 5 | Update all skills (6 files: 12→11 sections) | Step 11 |
| 13 | 6 | Verify version metadata | Step 12 |
| 14 | 7 | Run all tests | Step 13 |

---

## Verification Checklist

### Template Verification
- [ ] Single YAML frontmatter block at top
- [ ] Section 1 is Document Control
- [ ] 11 numbered sections exist (1-11)
- [ ] No duplicate section numbers
- [ ] No Section 12 or 13 as main sections (only subsections)
- [ ] Section 10 has Traceability with cumulative @brd, @prd, @ears, @bdd, @adr, @sys tags
- [ ] Section 11 (Implementation Notes) includes subsection 11.4 MVP Lifecycle
- [ ] Footer says "11 sections"
- [ ] Line 36 says "11 sections required"

### Validation Rules Verification
- [ ] Section structure matches template (11 sections)
- [ ] CHECK 2 lists 11 required sections (Document Control through Implementation Notes)
- [ ] Line 47 says "11 sections"
- [ ] CHECK 11 (Change History) marked as skipped for MVP

### Creation Rules Verification
- [ ] TOC line 58 says "11 Required sections" (not 12)
- [ ] Line 138 says "11 Required sections — MVP"
- [ ] No conflicting section counts

### Schema Verification
- [ ] mvp_sections has 11 entries (Sections 1-11)
- [ ] Section patterns match template headers (## 1. through ## 11.)
- [ ] Line 458 says "11 MVP sections"
- [ ] Line 298 says "11 mandatory sections"

### YAML Template Verification
- [ ] Section structure matches MD template (11 sections)
- [ ] All 11 sections defined (section_1 through section_11)
- [ ] Line 413 says "11 mandatory sections"
- [ ] No section_12 or section_13

### Skill Files Verification
- [ ] doc-req/SKILL.md section list has 11 entries
- [ ] doc-req_quickref.md path fixed (`docs/REQ/` → `docs/07_REQ/`)
- [ ] doc-req_quickref.md section count says 11
- [ ] doc-req-validator/SKILL.md section list has 11 entries
- [ ] doc-req-reviewer/SKILL.md section references updated for 11 sections
- [ ] doc-req-fixer/SKILL.md fix patterns updated for 11 sections
- [ ] doc-req-autopilot/SKILL.md generation logic produces 11 sections

### README Verification
- [ ] Section count says 11
- [ ] Section reference table matches template (Sections 1-11)

### Quality Gate Verification
- [ ] Section 3.2 lists 11-section structure
- [ ] All CORPUS checks reference correct 11-section structure

---

## Estimated Changes

| Metric | Count |
|--------|-------|
| MD Template: Section 13 merged into 11.4 | ~30 lines reorganized |
| MD Template: Footer updated | 1 line (12→11 sections) |
| Validation Rules: CHECK 11 updated | ~5 lines (add MVP skip note) |
| Creation Rules: TOC entry fixed | 1 line (12→11 in TOC) |
| Schema: No changes | 0 (already correct) |
| YAML Template: No changes | 0 (already correct) |
| README updates | ~10 lines (verify 11 sections) |
| Quality Gate updates | ~10 lines (verify structure) |
| Skill files to update | 6 (section counts 12→11, path fixes) |
| Total sections after fix | 11 (Sections 1-11) |

---

## Migration Guide for Existing REQs

**Migration Required**: Existing REQs with Section 13 need restructuring.

### Migration Steps

1. **Check section structure**: Verify Sections 1-11 exist with correct titles
2. **Merge Section 13 into Section 11**: If REQ has `## 13. MVP Lifecycle`:
   - Change `## 13. MVP Lifecycle` to `### 11.4 MVP Lifecycle`
   - Renumber subsections: `### 13.1` → `### 11.4.1`, etc.
3. **Fix traceability**: Ensure Section 10 has cumulative @brd, @prd, @ears, @bdd, @adr, @sys tags
4. **Add missing sections**: Add any missing sections per template
5. **Validate**: Run `doc-req-validator` on updated document

### Canonical Section Structure (Reference)

| Section | Title |
|---------|-------|
| 1 | Document Control |
| 2 | Requirement Description |
| 3 | Functional Specification |
| 4 | Interface Definition |
| 5 | Error Handling |
| 6 | Quality Attributes |
| 7 | Configuration |
| 8 | Testing Requirements |
| 9 | Acceptance Criteria |
| 10 | Traceability |
| 11 | Implementation Notes |

**Note**: MVP Lifecycle content is merged into Section 11 as subsection 11.4.

---

## Related Files to Update (Post-Implementation)

After fixing the template and skills, verify these files:

| File | Update Needed | Priority |
|------|---------------|----------|
| `SPEC-MVP-TEMPLATE.md` | REQ section references | P3 |
| `CTR-MVP-TEMPLATE.md` | REQ traceability references | P3 |
| Existing REQ documents | Migration: merge Section 13 into Section 11.4 | P3 |

---

## Summary of Key Corrections

| Item | Original Fix Plan | Corrected Fix Plan |
|------|-------------------|-------------------|
| Target structure | Inconsistent (11 vs 12) | **11 sections** (aligned with YAML, schema, validation) |
| Section 13 action | Renumber to 12 | **Merge into Section 11.4** |
| Section titles | Wrong titles listed | Correct titles from actual template |
| Schema changes | Add Section 12 | **No changes needed** (already correct) |
| YAML template | Update to 12 sections | **No changes needed** (already correct) |
| Validation rules | Update to 12 sections | **Add MVP skip note to CHECK 11** |

---

**End of Plan**
