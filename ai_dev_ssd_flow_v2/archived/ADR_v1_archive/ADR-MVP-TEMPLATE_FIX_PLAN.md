# ADR-MVP-TEMPLATE Fix Plan

**Created**: 2026-02-26
**Status**: Pending
**Version**: 1.2
**Last Updated**: 2026-02-26
**Target Files**:
- `ADR-MVP-TEMPLATE.md` (primary)
- `ADR-MVP-TEMPLATE.yaml` (autopilot)
- `ADR_MVP_VALIDATION_RULES.md`
- `ADR_MVP_SCHEMA.yaml`
- `ADR_MVP_CREATION_RULES.md`
- `ADR_MVP_QUALITY_GATE_VALIDATION.md`
- `README.md`

## Overview

Fix identified gaps in `/opt/data/docs_flow_framework/ucx_flow_v3/05_ADR/` documents and align template, validation rules, schema, and skills to a consistent **11-section** MVP structure (Section 1: Document Control through Section 11: MVP Lifecycle).

## Target Files

| File | Type | Priority |
|------|------|----------|
| `ADR-MVP-TEMPLATE.md` | MD Template (human workflow) | P1 |
| `ADR_MVP_VALIDATION_RULES.md` | Validation Rules | P1 |
| `ADR_MVP_SCHEMA.yaml` | Schema Definition | P1 |
| `ADR_MVP_CREATION_RULES.md` | Creation Rules | P1 |
| `ADR-MVP-TEMPLATE.yaml` | YAML Template (autopilot) | P1 |
| `ADR_MVP_QUALITY_GATE_VALIDATION.md` | Quality Gate Rules | P2 |
| `README.md` | Layer Documentation | P2 |
| `doc-adr*/SKILL.md` | Skills (5 files) | P2 |

## Reference Files

- `PRD-MVP-TEMPLATE_FIX_PLAN.md` (for alignment reference - example format)
- `EARS-MVP-TEMPLATE_FIX_PLAN.md` (for alignment reference - 6 sections)
- `ID_NAMING_STANDARDS.md` (for element ID format)

---

## Gap Summary

| # | Gap | Severity | Location | Phase |
|---|-----|----------|----------|-------|
| 1 | Duplicate YAML frontmatter in template | Critical | ADR-MVP-TEMPLATE.md lines 1-19, 39-61 | 1 |
| 2 | Duplicate YAML frontmatter in validation rules | Critical | ADR_MVP_VALIDATION_RULES.md lines 1-13, 22-33 | 1 |
| 3 | Duplicate YAML frontmatter in creation rules | Critical | ADR_MVP_CREATION_RULES.md lines 1-14, 22-34 | 1 |
| 4 | Section count mismatch (template=11, schema=15, skill=17, quality_gate=16) | Critical | All files | 2 |
| 5 | ~~Missing Section 2: Position in Development Workflow~~ | ~~High~~ | N/A - Schema alignment | - |
| 6 | ~~Missing Section 4: Status~~ | ~~High~~ | N/A - Schema alignment | - |
| 7 | ~~Missing Section 7: Requirements Satisfied~~ | ~~High~~ | N/A - Schema alignment | - |
| 8 | ~~Missing Section 11: Impact Analysis~~ | ~~High~~ | N/A - Schema alignment | - |
| 9 | Schema sections don't match template (15 vs 11) | Critical | ADR_MVP_SCHEMA.yaml | 2 |
| 10 | Schema has 10 required + 5 optional sections (15 total) | Critical | ADR_MVP_SCHEMA.yaml | 2 |
| 11 | doc-adr skill says "17 Sections Total" | High | doc-adr/SKILL.md:87 | 5 |
| 12 | Quality Gate Section 3.2 lists 16 sections | High | ADR_MVP_QUALITY_GATE_VALIDATION.md | 4 |
| 13 | Creation Rules says "4-part structure" without section count | Medium | ADR_MVP_CREATION_RULES.md | 4 |
| 14 | YAML template structure differs from MD template | High | ADR-MVP-TEMPLATE.yaml | 4.5 |
| 15 | doc-adr-validator doesn't specify section count | Medium | doc-adr-validator/SKILL.md | 5 |
| 16 | Missing version metadata in template | Medium | ADR-MVP-TEMPLATE.md | 6 |
| 17 | AI_CONTEXT comment inside duplicate frontmatter | Medium | ADR-MVP-TEMPLATE.md:27-38 | 1 |
| 18 | **No YAML ↔ MD sync verification step** | Medium | Fix Plan Phase 7 | 7 |
| 19 | README Section count references unspecified | Medium | README.md | 4 |
| 20 | CHECK 2 in validation rules doesn't list required sections | High | ADR_MVP_VALIDATION_RULES.md:176 | 4 |
| 21 | **doc-adr_quickref.md not in target files** | Medium | .claude/skills/doc-adr_quickref.md | 5 |
| 22 | **doc-adr_quickref.md has wrong path** (`docs/ADR/` → `docs/05_ADR/`) | Medium | doc-adr_quickref.md:30 | 5 |
| 23 | **Rollback plan missing 2 files** | Low | Phase 0.3 | 0 |
| 24 | **BDD not in downstream impact** (cumulative tagging) | Medium | Phase 0.4 | 0 |
| 25 | **Example ADR files not checked** | Low | 05_ADR/examples/ | 4 |

**Note on Gaps #5-8**: These were initially identified as "missing sections" based on schema comparison, but the decision is to align schema TO template (11 sections), not add sections to template. These gaps are resolved by updating the schema, not the template.

---

## Phase 0: Pre-Implementation

### 0.1 Backup All Files

```bash
# Create backup directory
mkdir -p /opt/data/docs_flow_framework/ucx_flow_v3/05_ADR/.backup_2026-02-26

# Backup templates and rules
cp ADR-MVP-TEMPLATE.md .backup_2026-02-26/
cp ADR-MVP-TEMPLATE.yaml .backup_2026-02-26/
cp ADR_MVP_VALIDATION_RULES.md .backup_2026-02-26/
cp ADR_MVP_CREATION_RULES.md .backup_2026-02-26/
cp ADR_MVP_QUALITY_GATE_VALIDATION.md .backup_2026-02-26/
cp ADR_MVP_SCHEMA.yaml .backup_2026-02-26/
cp README.md .backup_2026-02-26/

# Backup skills
cp -r /opt/data/docs_flow_framework/.claude/skills/doc-adr* .backup_2026-02-26/
```

### 0.2 Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Existing ADRs reference old section numbers | Medium | High | Document migration guide |
| Autopilot fails with new structure | Medium | High | Update YAML template in Phase 4.5 |
| Skills produce invalid output | Medium | Medium | Update all skills in Phase 5 |
| Validation rules mismatch | Low | Medium | Verify CHECK numbers align |
| Cross-document links break | Low | Low | Update references in Phase 4 |

### 0.3 Rollback Plan

**If issues occur during implementation:**

1. **Immediate Rollback**:
   ```bash
   # Restore all files
   cp .backup_2026-02-26/ADR-MVP-TEMPLATE.md ./
   cp .backup_2026-02-26/ADR-MVP-TEMPLATE.yaml ./
   cp .backup_2026-02-26/ADR_MVP_VALIDATION_RULES.md ./
   cp .backup_2026-02-26/ADR_MVP_CREATION_RULES.md ./
   cp .backup_2026-02-26/ADR_MVP_QUALITY_GATE_VALIDATION.md ./
   cp .backup_2026-02-26/ADR_MVP_SCHEMA.yaml ./
   cp .backup_2026-02-26/README.md ./

   # Restore skills
   cp -r .backup_2026-02-26/doc-adr* /opt/data/docs_flow_framework/.claude/skills/
   ```

2. **Partial Rollback**: Revert only affected files from backup

3. **Post-Rollback**: Re-run validators to confirm restored state

### 0.4 Downstream Impact Analysis

| Downstream Artifact | Impact | Action Required |
|--------------------|--------|-----------------|
| Existing ADR documents | Section numbers unchanged (1-11 already correct) | No migration needed |
| SYS templates | Reference ADR sections | Verify SYS-MVP-TEMPLATE references |
| BDD templates | Cumulative tagging (@brd, @prd, @ears, @bdd, @adr) | Verify BDD references to ADR sections |
| Validation scripts | CHECK numbers reference sections | Verify ADR_MVP_VALIDATION_RULES.md |
| Autopilot workflows | Generate from YAML template | Update YAML template (Phase 4.5) |
| doc-adr-reviewer | Check section completeness | Verify 11-section check |
| doc-adr-fixer | Fix phases reference sections | Verify section creation logic |
| Quality Gate validation | Corpus-level checks | Verify ADR_MVP_QUALITY_GATE_VALIDATION.md |

### 0.5 Decision: Target Section Count

**Analysis**:
- Current MD template: 11 sections (Section 1: Document Control through Section 11: MVP Lifecycle)
- YAML Schema: 15 sections (10 required + 5 optional) - **MISALIGNED**
- doc-adr skill: 17 sections (4-part structure) - **MISALIGNED**
- Quality Gate: 16 sections - **MISALIGNED**

**Current Template Structure** (verified from ADR-MVP-TEMPLATE.md):
```
## 1. Document Control     (line 72)
## 2. Context              (line 85)
## 3. Decision             (line 114)
## 4. Alternatives Considered (line 145)
## 5. Consequences         (line 199)
## 6. Architecture Flow    (line 228)
## 7. Implementation Assessment (line 260)
## 8. Verification         (line 290)
## 9. Traceability         (line 307)
## 10. Related Decisions   (line 343)
## 11. MVP Lifecycle       (line 353)
```

**Decision**: Keep current **11-section** structure. Align schema, skills, and quality gate TO the template (not vice versa):

| Section | Title |
|---------|-------|
| 1 | Document Control |
| 2 | Context |
| 3 | Decision |
| 4 | Alternatives Considered |
| 5 | Consequences |
| 6 | Architecture Flow |
| 7 | Implementation Assessment |
| 8 | Verification |
| 9 | Traceability |
| 10 | Related Decisions |
| 11 | MVP Lifecycle |

**Rationale**:
- Template is the primary source of truth (per authority hierarchy)
- 11-section structure is appropriate for MVP decisions
- **No renumbering needed** - template already has correct 1-11 numbering
- Update schema, skills, and quality gate to match template

---

## Phase 1: Critical Structural Fixes

### 1.1 Remove Duplicate YAML Frontmatter in Template

**File**: `ADR-MVP-TEMPLATE.md`

**Current State**:
- Lines 1-19: First (correct) YAML frontmatter
- Lines 27-38: AI_CONTEXT HTML comment block (KEEP)
- Lines 39-61: Second (duplicate) YAML frontmatter

**Action**: Delete lines 39-61 (second frontmatter block)

**Keep**: Lines 1-19 (first frontmatter) and lines 27-38 (AI_CONTEXT)

### 1.2 Remove Duplicate YAML Frontmatter in Validation Rules

**File**: `ADR_MVP_VALIDATION_RULES.md`

**Current State**:
- Lines 1-13: First YAML frontmatter (valid)
- Lines 22-33: Second YAML frontmatter (duplicate)

**Action**: Delete lines 22-33 (second frontmatter block)

### 1.3 Remove Duplicate YAML Frontmatter in Creation Rules

**File**: `ADR_MVP_CREATION_RULES.md`

**Current State**:
- Lines 1-14: First YAML frontmatter (valid)
- Lines 22-34: Second YAML frontmatter (duplicate)

**Action**: Delete lines 22-34 (second frontmatter block)

---

## Phase 2: Align Supporting Files to 11-Section Structure

### 2.1 Target Section Mapping

Based on current MD template (source of truth for MVP structure):

| Template Section | Schema Section | Alignment Action |
|------------------|----------------|------------------|
| 1. Document Control | Title + Document Control | Keep |
| 2. Context | 4. Context | Renumber to 2 |
| 3. Decision | 5. Decision | Renumber to 3 |
| 4. Alternatives Considered | 11. Alternatives (optional) | Make required, renumber to 4 |
| 5. Consequences | 7. Consequences | Renumber to 5 |
| 6. Architecture Flow | 8. Architecture Flow | Renumber to 6 |
| 7. Implementation Assessment | 9. Implementation Assessment | Renumber to 7 |
| 8. Verification | N/A | Add to schema |
| 9. Traceability | 14. Traceability (optional) | Make required, renumber to 9 |
| 10. Related Decisions | N/A | Add to schema |
| 11. MVP Lifecycle | N/A | Add to schema |

### 2.2 Schema Sections to Remove/Modify

The schema has sections NOT in template that should be removed or consolidated:

| Schema Section | Action |
|----------------|--------|
| 2. Position in Development Workflow | Remove (covered in README) |
| 3. Status | Remove (status in Document Control) |
| 6. Requirements Satisfied | Remove (covered in Traceability) |
| 10. Impact Analysis | Remove (covered in Consequences) |
| 12. Security Considerations (optional) | Remove (covered in Consequences) |
| 13. Operational Considerations (optional) | Remove (covered in Implementation) |
| 15. References (optional) | Remove (covered in Traceability) |

### 2.3 No Template Renumbering Required

**CORRECTION**: The template already has correct section numbering (1-11). No renumbering is needed.

The previous analysis incorrectly stated sections start at 2. Verified template structure:
- `## 1. Document Control` ✓
- `## 2. Context` ✓
- Through `## 11. MVP Lifecycle` ✓

---

## Phase 3: Template Minor Fixes

**Note**: No section renumbering required. Template already has correct 1-11 structure.

### 3.1 Remove Duplicate YAML Frontmatter

**File**: `ADR-MVP-TEMPLATE.md`

Delete lines 39-61 (second YAML frontmatter block). Keep:
- Lines 1-19: Valid YAML frontmatter
- Lines 27-38: AI_CONTEXT HTML comment block

### 3.2 Update Frontmatter Metadata

Add `total_sections` and update `schema_version`:

```yaml
custom_fields:
  # ... existing fields ...
  schema_version: "1.1"          # Updated from 1.0
  last_updated: "2026-02-26"     # Added
  total_sections: 11             # Added
```

### 3.3 Verify Document Control Table

Ensure Document Control table has all required fields:

| Item | Details |
|------|---------|
| **Status** | Proposed / Accepted / Deprecated / Superseded |
| **Date** | YYYY-MM-DDTHH:MM:SS |
| **Decision Makers** | [Names/Roles] |
| **Author** | [Architect/Lead Name] |
| **Version** | 1.0 |
| **SYS-Ready Score** | [Score]/100 (Target: ≥90) |

### 3.4 Add Template Footer

Add document footer:

```markdown
---

**Document Version**: 1.0
**Template Version**: 1.1 (MVP - 11 sections)
**Last Updated**: 2026-02-26
**Maintained By**: [Architecture Team]

---

> **MVP Template Notes**:
> - This is the standard ADR template (11 sections: 1-11)
> - Single file - no sectioning per user requirement
> - Focus on decision + rationale + alternatives
> - Maintains ucx_flow_v3 framework compliance
> - **Lifecycle**: MVP → PROD → NEW MVP (no separate "full ADR" template)
```

---

## Phase 4: Update Supporting Documents

### 4.1 Update Validation Rules Section List

**File**: `ADR_MVP_VALIDATION_RULES.md`

Update CHECK 2 to list required sections:

```markdown
### CHECK 2: ADR Structure Completeness

**Type**: Error (blocking)

**Required Sections (MVP Template - 11 Sections)**:

| Section | Title | Required |
|---------|-------|----------|
| 1 | Document Control | MANDATORY |
| 2 | Context | MANDATORY |
| 3 | Decision | MANDATORY |
| 4 | Alternatives Considered | MANDATORY |
| 5 | Consequences | MANDATORY |
| 6 | Architecture Flow | MANDATORY |
| 7 | Implementation Assessment | MANDATORY |
| 8 | Verification | MANDATORY |
| 9 | Traceability | MANDATORY |
| 10 | Related Decisions | MANDATORY |
| 11 | MVP Lifecycle | MANDATORY |
```

### 4.2 Update Schema Required Sections

**File**: `ADR_MVP_SCHEMA.yaml`

Update `required_sections` to match 11-section structure (align TO template):

```yaml
structure:
  required_sections:
    - pattern: "^# ADR-\\d{2,}:"
      name: "Title (H1)"
      description: "Single H1 with format ADR-NN: Title"

    - pattern: "^## 1\\. Document Control$"
      name: "Document Control"
      description: "Section 1 - Contains metadata table with SYS-Ready Score"

    - pattern: "^## 2\\. Context$"
      name: "Context"
      description: "Section 2 with Problem Statement, Technical Context"

    - pattern: "^## 3\\. Decision$"
      name: "Decision"
      description: "Section 3 with Chosen Solution, Key Components, Implementation Approach"

    - pattern: "^## 4\\. Alternatives Considered$"
      name: "Alternatives Considered"
      description: "Section 4 with Options A, B, C evaluation"

    - pattern: "^## 5\\. Consequences$"
      name: "Consequences"
      description: "Section 5 with Positive Outcomes, Trade-offs, Cost Estimate"

    - pattern: "^## 6\\. Architecture Flow$"
      name: "Architecture Flow"
      description: "Section 6 with Mermaid diagram and Integration Points"

    - pattern: "^## 7\\. Implementation Assessment$"
      name: "Implementation Assessment"
      description: "Section 7 with Phases, Rollback Plan, Monitoring"

    - pattern: "^## 8\\. Verification$"
      name: "Verification"
      description: "Section 8 with Success Criteria, BDD Scenarios"

    - pattern: "^## 9\\. Traceability$"
      name: "Traceability"
      description: "Section 9 with upstream/downstream refs, tags, cross-links"

    - pattern: "^## 10\\. Related Decisions$"
      name: "Related Decisions"
      description: "Section 10 with dependency and supersession references"

    - pattern: "^## 11\\. MVP Lifecycle$"
      name: "MVP Lifecycle"
      description: "Section 11 with lifecycle phases and ADR iteration guidance"
```

### 4.3 Update Creation Rules Section List

**File**: `ADR_MVP_CREATION_RULES.md`

Update Section 2 to specify 11-section structure:

```markdown
## 2. Document Structure (Required sections)

ADR documents follow a streamlined **11-section** MVP structure:

#### Required sections (numbered 1-11):
| # | Section | Purpose |
|---|---------|---------|
| 1 | Document Control | Metadata with SYS-Ready Score |
| 2 | Context | Problem Statement, Technical Context |
| 3 | Decision | Chosen Solution, Key Components, Approach |
| 4 | Alternatives Considered | Options with pros/cons |
| 5 | Consequences | Positive/Negative Outcomes, Costs |
| 6 | Architecture Flow | Mermaid diagrams, Integration Points |
| 7 | Implementation Assessment | Phases, Rollback, Monitoring |
| 8 | Verification | Success Criteria, BDD Scenarios |
| 9 | Traceability | Upstream/Downstream, Tags, Cross-Links |
| 10 | Related Decisions | Dependencies, Supersessions |
| 11 | MVP Lifecycle | Iteration guidance |
```

### 4.4 Update Quality Gate Section 3.2

**File**: `ADR_MVP_QUALITY_GATE_VALIDATION.md`

Update Section 3.2 to match 11-section structure:

```markdown
### 3.2 Required Document Structure (Per Template)

| # | Section | Required |
|---|---------|----------|
| 0 | **YAML Frontmatter** | YES - title, tags, custom_fields |
| 1 | **Section 1: Document Control** | YES - Project, Version, Date, Owner, Status, SYS-Ready Score |
| 2 | **Section 2: Context** | YES - Problem statement and background |
| 3 | **Section 3: Decision** | YES - The architecture decision made |
| 4 | **Section 4: Alternatives Considered** | YES - Evaluated options |
| 5 | **Section 5: Consequences** | YES - Positive and negative outcomes |
| 6 | **Section 6: Architecture Flow** | YES - Mermaid diagrams |
| 7 | **Section 7: Implementation Assessment** | YES - Phases, rollback, monitoring |
| 8 | **Section 8: Verification** | YES - Success criteria, BDD refs |
| 9 | **Section 9: Traceability** | YES - Cumulative upstream tags |
| 10 | **Section 10: Related Decisions** | YES - Dependencies, supersessions |
| 11 | **Section 11: MVP Lifecycle** | YES - Iteration guidance |
```

### 4.5 Update README.md

- Update section count to 11
- Update section reference table to match template (Sections 1-11)
- Remove any references to 17-section structure

---

## Phase 4.6: Update YAML Template

**File**: `ADR-MVP-TEMPLATE.yaml`

The YAML template currently has a different structure. Sync with MD template (11 sections):

### 4.6.1 Update Section Structure

```yaml
# Template metadata
schema_version: "1.1"
artifact_type: ADR
layer: 5
total_sections: 11
last_updated: "2026-02-26"

sections:
  - number: 1
    title: "Document Control"
    required: true
    description: "Metadata with SYS-Ready Score"
  - number: 2
    title: "Context"
    required: true
    subsections:
      - "2.1 Problem Statement"
      - "2.2 Technical Context"
  - number: 3
    title: "Decision"
    required: true
    subsections:
      - "3.1 Chosen Solution"
      - "3.2 Key Components"
      - "3.3 Implementation Approach"
  - number: 4
    title: "Alternatives Considered"
    required: true
    subsections:
      - "4.1 Option A"
      - "4.2 Option B"
      - "4.3 Option C (Optional)"
  - number: 5
    title: "Consequences"
    required: true
    subsections:
      - "5.1 Positive Outcomes"
      - "5.2 Trade-offs & Risks"
      - "5.3 Cost Estimate"
  - number: 6
    title: "Architecture Flow"
    required: true
    subsections:
      - "6.1 High-Level Flow"
      - "6.2 Key Integration Points"
  - number: 7
    title: "Implementation Assessment"
    required: true
    subsections:
      - "7.1 MVP Development Phases"
      - "7.2 Rollback Plan"
      - "7.3 Monitoring (MVP Baseline)"
  - number: 8
    title: "Verification"
    required: true
    subsections:
      - "8.1 Success Criteria"
      - "8.2 BDD Scenarios"
  - number: 9
    title: "Traceability"
    required: true
    subsections:
      - "9.1 Upstream References"
      - "9.2 Downstream Artifacts"
      - "9.3 Traceability Tags"
      - "9.4 Cross-Links (Same-Layer)"
  - number: 10
    title: "Related Decisions"
    required: true
  - number: 11
    title: "MVP Lifecycle"
    required: true
    subsections:
      - "11.1 Lifecycle Phases"
      - "11.2 When to Create a New ADR"
      - "11.3 Cross-ADR Traceability"
```

---

## Phase 5: Update doc-adr* Skills

### 5.1 Target Skill Files

| Skill | File Path | Update Scope |
|-------|-----------|--------------|
| doc-adr | `.claude/skills/doc-adr/SKILL.md` | **CRITICAL**: Line 87 says "17 Sections Total" - update to 11 |
| doc-adr_quickref | `.claude/skills/doc-adr_quickref.md` | Fix path `docs/ADR/` → `docs/05_ADR/`, update section count |
| doc-adr-validator | `.claude/skills/doc-adr-validator/SKILL.md` | Add 11-section list |
| doc-adr-reviewer | `.claude/skills/doc-adr-reviewer/SKILL.md` | Review criteria update |
| doc-adr-fixer | `.claude/skills/doc-adr-fixer/SKILL.md` | Fix patterns update |
| doc-adr-autopilot | `.claude/skills/doc-adr-autopilot/SKILL.md` | Verify section references |

### 5.2 doc-adr/SKILL.md Fixes (CRITICAL)

**Line 87**: Change "17 Sections Total" to "11 Sections Total":

```markdown
# Before:
### 1. Four-Part ADR Structure (17 Sections Total)

# After:
### 1. ADR MVP Structure (11 Sections Total)
```

**Lines 91-101**: Update section ranges:

```markdown
# Before:
**Part 1 - Decision Context and Requirements** (Sections 1-6):
**Part 2 - Impact Analysis and Architecture** (Sections 7-12):
**Part 3 - Implementation and Operations** (Sections 13-15):
**Part 4 - Traceability and Documentation** (Sections 16-17):

# After:
**Required Sections (11 Total)**:
| # | Section | Purpose |
|---|---------|---------|
| 1 | Document Control | Metadata, SYS-Ready Score |
| 2 | Context | Problem statement, technical context |
| 3 | Decision | Chosen solution, components, approach |
| 4 | Alternatives Considered | Options with pros/cons |
| 5 | Consequences | Positive/negative outcomes, costs |
| 6 | Architecture Flow | Mermaid diagrams, integrations |
| 7 | Implementation Assessment | Phases, rollback, monitoring |
| 8 | Verification | Success criteria, BDD refs |
| 9 | Traceability | Upstream/downstream, tags |
| 10 | Related Decisions | Dependencies, supersessions |
| 11 | MVP Lifecycle | Iteration guidance |
```

### 5.3 doc-adr_quickref.md Fixes

**Path correction** (line ~30):
```markdown
# Before:
- Template: `docs/ADR/ADR-MVP-TEMPLATE.md`

# After:
- Template: `docs/05_ADR/ADR-MVP-TEMPLATE.md`
```

**Section count update**: Change any "10 sections" or "17 sections" to "11 sections"

### 5.4 doc-adr-validator/SKILL.md Fixes

Add explicit 11-section structure validation:

```markdown
### 2. Structure Validation (MVP Template - 11 Sections)

**Required Sections**:

| Section | Title | Required |
|---------|-------|----------|
| 1 | Document Control | MANDATORY |
| 2 | Context | MANDATORY |
| 3 | Decision | MANDATORY |
| 4 | Alternatives Considered | MANDATORY |
| 5 | Consequences | MANDATORY |
| 6 | Architecture Flow | MANDATORY |
| 7 | Implementation Assessment | MANDATORY |
| 8 | Verification | MANDATORY |
| 9 | Traceability | MANDATORY |
| 10 | Related Decisions | MANDATORY |
| 11 | MVP Lifecycle | MANDATORY |
```

---

## Phase 6: Minor Fixes and Metadata

### 6.1 Update Version Metadata in Template

Update YAML frontmatter in `ADR-MVP-TEMPLATE.md`:

```yaml
---
title: "ADR-MVP-TEMPLATE: Architecture Decision Record (MVP)"
tags:
  - adr-template
  - mvp-template
  - layer-5-artifact
  - document-template
  - shared-architecture
custom_fields:
  document_type: template
  artifact_type: ADR
  layer: 5
  template_variant: mvp
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  schema_version: "1.1"          # Updated from 1.0
  last_updated: "2026-02-26"     # Added
  total_sections: 11             # Added (Sections 1-11)
---
```

---

## Phase 7: Testing & Validation

### 7.1 Template Validation

| Test | Command/Action | Expected Result |
|------|----------------|-----------------|
| Syntax check | Open in markdown viewer | Renders without errors |
| Section count | Count `## N.` headers | 11 sections (1-11) |
| Duplicate check | Search for duplicate headers | 0 duplicates |
| Frontmatter | Validate YAML | Single valid block |

### 7.2 Schema Validation

```bash
# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('ADR_MVP_SCHEMA.yaml').read())"

# Check for duplicates
grep -n "required_sections:" ADR_MVP_SCHEMA.yaml
# Expected: 1 occurrence
```

### 7.3 Skill Testing

| Skill | Test Action | Expected Result |
|-------|-------------|-----------------|
| doc-adr | Create test ADR | 11-section ADR generated |
| doc-adr-validator | Validate test ADR | Pass all checks |
| doc-adr-autopilot | Generate ADR from YAML | Valid 11-section output |

### 7.4 YAML ↔ MD Template Sync Verification

**Purpose**: Ensure MD template and YAML template are aligned after changes.

| Check | MD Template | YAML Template | Expected |
|-------|-------------|---------------|----------|
| Total sections | Count `## N.` headers | Count `sections:` entries | 11 each |
| Section titles | Extract from headers | Extract from `title:` | Match exactly |
| Subsections | Count `### N.N` headers | Count `subsections:` | Match |
| Schema version | `custom_fields.schema_version` | `schema_version:` | Match |

**Verification Command**:
```bash
# Count sections in MD template
grep -c "^## [0-9]" ADR-MVP-TEMPLATE.md
# Expected: 11

# Count sections in YAML template
grep -c "number:" ADR-MVP-TEMPLATE.yaml
# Expected: 11

# Verify section titles match
diff <(grep "^## [0-9]" ADR-MVP-TEMPLATE.md | sed 's/## [0-9]*\. //') \
     <(grep "title:" ADR-MVP-TEMPLATE.yaml | sed 's/.*title: "//;s/"$//')
# Expected: No output (files match)
```

---

## Execution Order

| Step | Phase | Action | Dependencies |
|------|-------|--------|--------------|
| 1 | 0 | Create backups | None |
| 2 | 1 | Fix duplicate YAML in template | Backup complete |
| 3 | 1 | Fix duplicate YAML in validation rules | Step 2 |
| 4 | 1 | Fix duplicate YAML in creation rules | Step 3 |
| 5 | 3 | Update template footer/metadata | Step 4 |
| 6 | 4.1 | Update Validation Rules (11 sections) | Step 5 |
| 7 | 4.2 | Update Schema (align to template) | Step 6 |
| 8 | 4.3 | Update Creation Rules | Step 7 |
| 9 | 4.4 | Update Quality Gate | Step 8 |
| 10 | 4.5 | Update README.md | Step 9 |
| 11 | 4.6 | Update YAML template (11 sections) | Step 10 |
| 12 | 5 | Update all skills (6 files) | Step 11 |
| 13 | 6 | Update version metadata | Step 12 |
| 14 | 7 | Run all tests | Step 13 |

**Note**: No template section renumbering needed - template already has correct 1-11 numbering.

---

## Verification Checklist

### Template Verification
- [ ] Single YAML frontmatter block at top
- [ ] Section 1 is Document Control (uses table format)
- [ ] 11 numbered sections exist (1-11)
- [ ] No duplicate section numbers
- [ ] Section 2 is Context
- [ ] Section 9 has Traceability with @brd, @prd, @ears, @bdd tags
- [ ] Section 10 has Related Decisions
- [ ] Section 11 has MVP Lifecycle
- [ ] Version metadata updated (schema_version: 1.1, total_sections: 11)

### Validation Rules Verification
- [ ] Single YAML frontmatter block
- [ ] Section structure matches template (11 sections)
- [ ] CHECK 2 lists all 11 required sections
- [ ] No duplicate frontmatter blocks

### Creation Rules Verification
- [ ] Single YAML frontmatter block (duplicate removed)
- [ ] Section structure matches template (11 sections)
- [ ] Required sections list updated

### Schema Verification
- [ ] required_sections has 12 entries (Title + 11 sections)
- [ ] Section patterns match template headers (## 1. through ## 11.)
- [ ] Matches validation rules

### YAML Template Verification
- [ ] Section structure matches MD template
- [ ] All 11 sections defined with subsections
- [ ] Metadata updated (total_sections: 11)

### Skill Files Verification
- [ ] doc-adr/SKILL.md updated from 17 to 11 sections
- [ ] doc-adr_quickref.md path fixed (`docs/ADR/` → `docs/05_ADR/`)
- [ ] doc-adr-validator/SKILL.md section list added (11 sections)
- [ ] doc-adr-reviewer/SKILL.md section references updated
- [ ] doc-adr-fixer/SKILL.md fix patterns updated
- [ ] doc-adr-autopilot/SKILL.md generation logic verified

### README Verification
- [ ] Section count updated to 11
- [ ] Section reference table updated

### Quality Gate Verification
- [ ] Section 3.2 updated to 11-section structure
- [ ] CORPUS-11 check references correct sections

---

## Estimated Changes

| Metric | Count |
|--------|-------|
| MD Template lines modified | ~30 (metadata only, no renumbering) |
| MD Template lines removed | ~25 (duplicate frontmatter) |
| Validation Rules fixes | ~15 lines removed, ~30 added |
| Creation Rules fixes | ~15 lines removed, ~20 modified |
| Schema fixes | ~80 lines modified (align 15→11 sections) |
| YAML Template updates | ~100 lines |
| README updates | ~30 lines |
| Quality Gate updates | ~20 lines |
| Skill files to update | 6 (added doc-adr_quickref.md) |
| Total sections after fix | 11 (Sections 1-11) |

---

## Migration Guide for Existing ADRs

**GOOD NEWS**: No section renumbering required for existing ADRs!

The template already uses correct 1-11 section numbering. Migration only needed if existing ADRs:
- Were created with non-standard section numbers
- Are missing required sections
- Have duplicate YAML frontmatter

### Migration Steps (if needed)

1. **Check section structure**: Verify Sections 1-11 exist with correct titles
2. **Fix traceability**: Ensure Section 9 has cumulative @brd, @prd, @ears, @bdd tags
3. **Add missing sections**: Add any missing sections per template
4. **Remove duplicate frontmatter**: Keep only first YAML block (lines 1-N)
5. **Validate**: Run `doc-adr-validator` on updated document

### Canonical Section Structure (Reference)

| Section | Title |
|---------|-------|
| 1 | Document Control |
| 2 | Context |
| 3 | Decision |
| 4 | Alternatives Considered |
| 5 | Consequences |
| 6 | Architecture Flow |
| 7 | Implementation Assessment |
| 8 | Verification |
| 9 | Traceability |
| 10 | Related Decisions |
| 11 | MVP Lifecycle |

---

## Related Files to Update (Post-Implementation)

After fixing the template and skills, verify these files:

| File | Update Needed | Priority |
|------|---------------|----------|
| `SYS-MVP-TEMPLATE.md` | ADR section references | P3 |
| `REQ-MVP-TEMPLATE.md` | ADR section references | P3 |
| Existing ADR documents | Migration to new structure | P3 |

---

**End of Plan**
