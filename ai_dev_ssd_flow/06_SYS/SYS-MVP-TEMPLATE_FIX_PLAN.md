# SYS-MVP-TEMPLATE Fix Plan

**Created**: 2026-02-26
**Status**: Pending
**Version**: 1.0
**Last Updated**: 2026-02-26
**Target Files**:
- `SYS-MVP-TEMPLATE.md` (primary)
- `SYS-MVP-TEMPLATE.yaml` (autopilot)
- `SYS_MVP_VALIDATION_RULES.md`
- `SYS_MVP_SCHEMA.yaml`
- `SYS_MVP_CREATION_RULES.md`
- `SYS_MVP_QUALITY_GATE_VALIDATION.md`
- `README.md`

## Overview

Fix identified gaps in `/opt/data/docs_flow_framework/ai_dev_ssd_flow/06_SYS/` documents and align template, validation rules, schema, and skills to a consistent **15-section** MVP structure (Section 1: Document Control through Section 15: Change History).

## Target Files

| File | Type | Priority |
|------|------|----------|
| `SYS-MVP-TEMPLATE.md` | MD Template (human workflow) | P1 |
| `SYS_MVP_VALIDATION_RULES.md` | Validation Rules | P1 |
| `SYS_MVP_SCHEMA.yaml` | Schema Definition | P1 |
| `SYS_MVP_CREATION_RULES.md` | Creation Rules | P1 |
| `SYS-MVP-TEMPLATE.yaml` | YAML Template (autopilot) | P1 |
| `SYS_MVP_QUALITY_GATE_VALIDATION.md` | Quality Gate Rules | P2 |
| `README.md` | Layer Documentation | P2 |
| `doc-sys*/SKILL.md` | Skills (5 files) | P2 |
| `doc-sys_quickref.md` | Quick Reference | P2 |

## Reference Files

- `ADR-MVP-TEMPLATE_FIX_PLAN.md` (for alignment reference - 11 sections)
- `PRD-MVP-TEMPLATE_FIX_PLAN.md` (for alignment reference - 21 sections)
- `ID_NAMING_STANDARDS.md` (for element ID format)

---

## Gap Summary

| # | Gap | Severity | Location | Phase |
|---|-----|----------|----------|-------|
| 1 | YAML template extremely minimal (4 sections vs 15 in MD) | Critical | SYS-MVP-TEMPLATE.yaml | 4 |
| 2 | YAML template lacks schema_version/total_sections metadata | High | SYS-MVP-TEMPLATE.yaml | 4 |
| 3 | doc-sys_quickref.md has wrong path (`docs/SYS/` → `docs/06_SYS/`) | Medium | doc-sys_quickref.md:30 | 5 |
| 4 | Validation Rules missing explicit section list in CHECK 2 | Medium | SYS_MVP_VALIDATION_RULES.md | 3 |
| 5 | MD template missing version metadata (total_sections) | Low | SYS-MVP-TEMPLATE.md | 1 |
| 6 | No YAML ↔ MD sync verification step defined | Medium | Fix Plan Phase 6 | 6 |
| 7 | README doesn't explicitly state "15 sections" | Low | README.md | 3 |
| 8 | Skills don't explicitly state "15 sections" count | Low | doc-sys/SKILL.md | 5 |
| 9 | doc-sys-validator says "15 sections" but uses FR-NNN (legacy) | Medium | doc-sys-validator/SKILL.md:115 | 5 |
| 10 | Missing template footer with version info | Low | SYS-MVP-TEMPLATE.md | 1 |
| 11 | Quality Gate validation CORPUS-10 has inconsistent thresholds | Low | SYS_MVP_QUALITY_GATE_VALIDATION.md:227-232 | 3 |
| 12 | Creation Rules mentions "5-part structure" without section count | Medium | SYS_MVP_CREATION_RULES.md:75-96 | 3 |

---

## Phase 0: Pre-Implementation

### 0.1 Backup All Files

```bash
# Create backup directory
mkdir -p /opt/data/docs_flow_framework/ai_dev_ssd_flow/06_SYS/.backup_2026-02-26

# Backup templates and rules
cd /opt/data/docs_flow_framework/ai_dev_ssd_flow/06_SYS
cp SYS-MVP-TEMPLATE.md .backup_2026-02-26/
cp SYS-MVP-TEMPLATE.yaml .backup_2026-02-26/
cp SYS_MVP_VALIDATION_RULES.md .backup_2026-02-26/
cp SYS_MVP_CREATION_RULES.md .backup_2026-02-26/
cp SYS_MVP_QUALITY_GATE_VALIDATION.md .backup_2026-02-26/
cp SYS_MVP_SCHEMA.yaml .backup_2026-02-26/
cp README.md .backup_2026-02-26/

# Backup skills
cp -r /opt/data/docs_flow_framework/.claude/skills/doc-sys* .backup_2026-02-26/
```

### 0.2 Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Existing SYS docs reference old section numbers | Low | Medium | Section numbers already correct (1-15) |
| Autopilot fails with new YAML structure | Medium | High | Update YAML template comprehensively in Phase 4 |
| Skills produce invalid output | Low | Medium | Update all skills in Phase 5 |
| Validation rules mismatch | Low | Medium | Verify CHECK numbers align |

### 0.3 Rollback Plan

**If issues occur during implementation:**

1. **Immediate Rollback**:
   ```bash
   cd /opt/data/docs_flow_framework/ai_dev_ssd_flow/06_SYS
   # Restore all files
   cp .backup_2026-02-26/SYS-MVP-TEMPLATE.md ./
   cp .backup_2026-02-26/SYS-MVP-TEMPLATE.yaml ./
   cp .backup_2026-02-26/SYS_MVP_VALIDATION_RULES.md ./
   cp .backup_2026-02-26/SYS_MVP_CREATION_RULES.md ./
   cp .backup_2026-02-26/SYS_MVP_QUALITY_GATE_VALIDATION.md ./
   cp .backup_2026-02-26/SYS_MVP_SCHEMA.yaml ./
   cp .backup_2026-02-26/README.md ./

   # Restore skills
   cp -r .backup_2026-02-26/doc-sys* /opt/data/docs_flow_framework/.claude/skills/
   ```

2. **Partial Rollback**: Revert only affected files from backup

3. **Post-Rollback**: Re-run validators to confirm restored state

### 0.4 Downstream Impact Analysis

| Downstream Artifact | Impact | Action Required |
|--------------------|--------|-----------------|
| Existing SYS documents | Section numbers unchanged (1-15 already correct) | No migration needed |
| REQ templates | Reference SYS sections | Verify REQ-MVP-TEMPLATE references |
| Validation scripts | CHECK numbers reference sections | Verify SYS_MVP_VALIDATION_RULES.md |
| Autopilot workflows | Generate from YAML template | Update YAML template (Phase 4) |
| doc-sys-reviewer | Check section completeness | Verify 15-section check |
| doc-sys-fixer | Fix phases reference sections | Verify section creation logic |
| Quality Gate validation | Corpus-level checks | Verify SYS_MVP_QUALITY_GATE_VALIDATION.md |

### 0.5 Decision: Target Section Count

**Analysis**:
- Current MD template: 15 sections (Section 1: Document Control through Section 15: Change History)
- YAML Schema: 15 sections (Title + 15 required sections) - **ALIGNED**
- YAML Template: 4 sections only - **MISALIGNED** (needs expansion)
- doc-sys-validator skill: 15 sections - **ALIGNED**

**Current Template Structure** (verified from SYS-MVP-TEMPLATE.md):
```
## 1. Document Control     (line 41)
## 2. Executive Summary    (line 56)
## 3. Scope                (line 75)
## 4. Functional Requirements (line 116)
## 5. Quality Attributes   (line 242)
## 6. Interface Specifications (line 361)
## 7. Data Management Requirements (line 391)
## 8. Testing and Validation Requirements (line 424)
## 9. Deployment and Operations Requirements (line 462)
## 10. Compliance and Regulatory Requirements (line 670)
## 11. Acceptance Criteria (line 698)
## 12. Risk Assessment     (line 721)
## 13. Traceability        (line 762)
## 14. Implementation Notes (line 1105)
## 15. Change History      (line 1179)
```

**Decision**: Keep current **15-section** structure. MD template is already correct. Align YAML template and skills TO the MD template.

| Section | Title |
|---------|-------|
| 1 | Document Control |
| 2 | Executive Summary |
| 3 | Scope |
| 4 | Functional Requirements |
| 5 | Quality Attributes |
| 6 | Interface Specifications |
| 7 | Data Management Requirements |
| 8 | Testing and Validation Requirements |
| 9 | Deployment and Operations Requirements |
| 10 | Compliance and Regulatory Requirements |
| 11 | Acceptance Criteria |
| 12 | Risk Assessment |
| 13 | Traceability |
| 14 | Implementation Notes |
| 15 | Change History |

**Rationale**:
- MD template is the primary source of truth (per authority hierarchy)
- 15-section structure is comprehensive for system requirements
- **No renumbering needed** - MD template already has correct 1-15 numbering
- Update YAML template and skills to match MD template

---

## Phase 1: MD Template Minor Fixes

### 1.1 Update Frontmatter Metadata

**File**: `SYS-MVP-TEMPLATE.md`

Update YAML frontmatter to add total_sections and schema_version:

```yaml
---
title: "SYS-MVP-TEMPLATE: System Requirements"
tags:
  - sys-template
  - mvp-template
  - layer-6-artifact
  - document-template
  - shared-architecture
custom_fields:
  document_type: template
  artifact_type: SYS
  layer: 6
  template_variant: mvp
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  schema_version: "2.1"          # Updated
  last_updated: "2026-02-26"     # Added
  total_sections: 15             # Added (Sections 1-15)
---
```

### 1.2 Add Template Footer

**File**: `SYS-MVP-TEMPLATE.md`

Add after Section 15 (Change History):

```markdown
---

**Document Version**: 1.0
**Template Version**: 2.1 (MVP - 15 sections)
**Last Updated**: 2026-02-26
**Maintained By**: [Systems Architecture Team]

---

> **MVP Template Notes**:
> - This is the standard SYS template (15 sections: 1-15)
> - Single file - no sectioning per user requirement
> - Focus on system requirements + quality attributes
> - Maintains ai_dev_flow framework compliance
> - **Lifecycle**: MVP → PROD → NEW MVP (no separate "full SYS" template)
```

---

## Phase 2: Schema Verification

### 2.1 Verify Schema Section Count

**File**: `SYS_MVP_SCHEMA.yaml`

Verify `required_sections` has exactly 16 entries (Title H1 + 15 numbered sections):

**Current State** (lines 121-186): Lists Title + Sections 1-15 - **CORRECT**

**No changes needed** for schema - already aligned with MD template.

---

## Phase 3: Update Supporting Documents

### 3.1 Update Validation Rules Section List

**File**: `SYS_MVP_VALIDATION_RULES.md`

Add explicit 15-section list under CHECK 2 (around line 138):

```markdown
### CHECK 2: ADR Compliance Validation

**Purpose**: Ensure SYS requirements are implementable within ADR architectural boundaries
**Type**: Error (blocking)

**Required Sections (MVP Template - 15 Sections)**:

| Section | Title | Required |
|---------|-------|----------|
| 1 | Document Control | MANDATORY |
| 2 | Executive Summary | MANDATORY |
| 3 | Scope | MANDATORY |
| 4 | Functional Requirements | MANDATORY |
| 5 | Quality Attributes | MANDATORY |
| 6 | Interface Specifications | MANDATORY |
| 7 | Data Management Requirements | MANDATORY |
| 8 | Testing and Validation Requirements | MANDATORY |
| 9 | Deployment and Operations Requirements | MANDATORY |
| 10 | Compliance and Regulatory Requirements | MANDATORY |
| 11 | Acceptance Criteria | MANDATORY |
| 12 | Risk Assessment | MANDATORY |
| 13 | Traceability | MANDATORY |
| 14 | Implementation Notes | MANDATORY |
| 15 | Change History | MANDATORY |
```

### 3.2 Update Creation Rules Section List

**File**: `SYS_MVP_CREATION_RULES.md`

Update Section 2 (line ~73) to explicitly state section count:

```markdown
## 2. Document Structure (Required sections)

SYS documents follow a comprehensive **15-section** MVP structure organized into 5 parts:

#### Required Sections (numbered 1-15):

| # | Section | Part | Purpose |
|---|---------|------|---------|
| 1 | Document Control | 1 | Metadata with REQ-Ready Score |
| 2 | Executive Summary | 1 | System overview and context |
| 3 | Scope | 1 | System boundaries and inclusions/exclusions |
| 4 | Functional Requirements | 2 | SYS.NN.01.SS format requirements |
| 5 | Quality Attributes | 2 | Performance, reliability, security, etc. |
| 6 | Interface Specifications | 3 | External and internal interfaces |
| 7 | Data Management Requirements | 3 | Data model, storage, migration |
| 8 | Testing and Validation Requirements | 3 | Test strategy, coverage targets |
| 9 | Deployment and Operations Requirements | 4 | Infrastructure, scripts, Ansible, observability |
| 10 | Compliance and Regulatory Requirements | 4 | Regulatory, security, audit |
| 11 | Acceptance Criteria | 5 | Functional, performance, security criteria |
| 12 | Risk Assessment | 5 | Technical risks, mitigation |
| 13 | Traceability | 5 | Upstream sources, downstream artifacts |
| 14 | Implementation Notes | 5 | Technical guidance, dependencies |
| 15 | Change History | 5 | Version history table |
```

### 3.3 Update Quality Gate Thresholds

**File**: `SYS_MVP_QUALITY_GATE_VALIDATION.md`

Fix inconsistent thresholds in CORPUS-10 (lines 227-232):

```markdown
**Thresholds**:
| Metric | Warning | Error |
|--------|---------|-------|
| Lines | 800 | 1,200 |
| Tokens | 15,000 | 20,000 |
```

### 3.4 Update README.md Section Count

**File**: `README.md`

Update to explicitly state 15 sections (around line 29):

```markdown
## Available Templates

**SYS-MVP-TEMPLATE.md** (default) - Streamlined MVP version in a single file (15 sections)
- Focused on 5-10 core system capabilities
- Comprehensive 15-section structure (Document Control through Change History)
- Maintains framework compliance while reducing documentation overhead
- Ideal for MVPs with focused system scope
```

---

## Phase 4: Update YAML Template

**File**: `SYS-MVP-TEMPLATE.yaml`

The YAML template currently has only 4 sections. Expand to match MD template's 15-section structure:

### 4.1 Update YAML Template Structure

```yaml
# =============================================================================
#  Document Authority: PRIMARY STANDARD for Autopilot Workflow
# - Purpose: AI-consumable template for automated SYS artifact generation
# - Validation: Validated by SYS_MVP_SCHEMA.yaml (shared with MD template)
# - Human Reference: See SYS-MVP-TEMPLATE.md for narrative explanations
# =============================================================================

# Template metadata
schema_version: "2.1"
artifact_type: SYS
layer: 6
total_sections: 15
last_updated: "2026-02-26"

id: SYS-NN
summary: "[Single-sentence description: System requirements defining boundaries, functionality, and non-functional requirements]"

# =============================================================================
# Document Control
# =============================================================================

document_control:
  status: "Draft"  # Draft, Review, Approved, Implemented, Deprecated
  version: "1.0"
  date_created: "YYYY-MM-DD"
  last_updated: "YYYY-MM-DD"
  author: "[Primary Author]"
  reviewers: "[Reviewer Names]"
  owner: "[Team/Person]"
  priority: "High"  # High, Medium, Low
  ears_ready_score: "[PASS] 95% (Target: ≥90%)"
  req_ready_score: "[PASS] 95% (Target: ≥90%)"
  source_document: "@prd: PRD.NN.EE.SS"

# =============================================================================
# Sections (15 total)
# =============================================================================

sections:
  - number: 1
    title: "Document Control"
    required: true
    description: "Metadata table with REQ-Ready Score"

  - number: 2
    title: "Executive Summary"
    required: true
    subsections:
      - "2.1 System Context"
      - "2.2 Business Value"

  - number: 3
    title: "Scope"
    required: true
    subsections:
      - "3.1 System Boundaries"
      - "3.2 Acceptance Scope"
      - "3.3 Environmental Assumptions"

  - number: 4
    title: "Functional Requirements"
    required: true
    subsections:
      - "4.1 Core System Behaviors"
      - "4.2 Data Processing Requirements"
      - "4.3 Error Handling Requirements"
      - "4.4 Integration Requirements"
      - "4.5 External Dependencies"

  - number: 5
    title: "Quality Attributes"
    required: true
    subsections:
      - "5.1 Performance Requirements"
      - "5.2 Reliability Requirements"
      - "5.3 Scalability Requirements"
      - "5.4 Security Requirements"
      - "5.5 Observability Requirements"
      - "5.6 Maintainability Requirements"

  - number: 6
    title: "Interface Specifications"
    required: true
    subsections:
      - "6.1 External Interfaces"
      - "6.2 Internal Interfaces"

  - number: 7
    title: "Data Management Requirements"
    required: true
    subsections:
      - "7.1 Data Model Requirements"
      - "7.2 Data Lifecycle Management"

  - number: 8
    title: "Testing and Validation Requirements"
    required: true
    subsections:
      - "8.1 Functional Testing Requirements"
      - "8.2 Quality Attribute Testing Requirements"

  - number: 9
    title: "Deployment and Operations Requirements"
    required: true
    subsections:
      - "9.1 Deployment Requirements"
      - "9.2 Operational Requirements"

  - number: 10
    title: "Compliance and Regulatory Requirements"
    required: true
    subsections:
      - "10.1 Business Compliance"
      - "10.2 Security Compliance"

  - number: 11
    title: "Acceptance Criteria"
    required: true
    subsections:
      - "11.1 System Capability Validation"

  - number: 12
    title: "Risk Assessment"
    required: true
    subsections:
      - "12.1 Technical Implementation Risks"
      - "12.2 Business Risks"
      - "12.3 Risk Mitigation Strategies"

  - number: 13
    title: "Traceability"
    required: true
    subsections:
      - "13.1 Upstream Sources"
      - "13.2 Downstream Artifacts"
      - "13.3 BDD Mapping"
      - "13.4 Code Implementation Paths"
      - "13.5 Document Links and Cross-References"
      - "13.6 Validation Evidence"
      - "13.7 Cross-Reference Validation"
      - "13.8 Same-Type References"
      - "13.9 Traceability Tags"
      - "13.10 Thresholds Referenced"

  - number: 14
    title: "Implementation Notes"
    required: true
    subsections:
      - "14.1 Design Considerations"
      - "14.2 Performance Considerations"
      - "14.3 Monitoring and Troubleshooting Strategy"
      - "14.4 Security Implementation Guidance"
      - "14.5 Deployment Strategy Guidance"

  - number: 15
    title: "Change History"
    required: true
    description: "Version history table"

# =============================================================================
# Traceability
# =============================================================================

traceability:
  upstream_references:
    brd: "@brd: BRD.NN.EE.SS"
    prd: "@prd: PRD.NN.EE.SS"
    ears: "@ears: EARS.NN.EE.SS"
    bdd: "@bdd: BDD.NN.EE.SS"
    adr: "@adr: ADR-NN"

  downstream_artifacts:
    req: "REQ"
    spec: "SPEC"
    tasks: "TASKS"

  tags:
    - "@sys: SYS.NN.EE.SS"
    - "@brd: BRD.NN.EE.SS"
    - "@prd: PRD.NN.EE.SS"
    - "@ears: EARS.NN.EE.SS"
    - "@bdd: BDD.NN.EE.SS"
    - "@adr: ADR-NN"

  cross_links:
    depends:
      - "@depends: SYS-NN"
    discoverability:
      - "@discoverability: SYS-NN (short rationale)"

# =============================================================================
# Template Metadata
# =============================================================================

# Template Reference: SYS-MVP-TEMPLATE.md (for narrative explanations)
# Schema: SYS_MVP_SCHEMA.yaml (for validation rules)
# Creation Rules: SYS_MVP_CREATION_RULES.md (for guidance)
# Validation Rules: SYS_MVP_VALIDATION_RULES.md (for checklist)

# MVP Profile Notes:
# - 15 sections: Document Control through Change History
# - 5-part organization: Definition, Requirements, Specification, Operations, Validation
# - Quality attributes cover performance, reliability, scalability, security, observability, maintainability

# =============================================================================
```

---

## Phase 5: Update doc-sys* Skills

### 5.1 Target Skill Files

| Skill | File Path | Update Scope |
|-------|-----------|--------------|
| doc-sys | `.claude/skills/doc-sys/SKILL.md` | Add explicit "15 sections" statement |
| doc-sys_quickref | `.claude/skills/doc-sys_quickref.md` | Fix path `docs/SYS/` → `docs/06_SYS/` |
| doc-sys-validator | `.claude/skills/doc-sys-validator/SKILL.md` | Fix FR-NNN to SYS.NN.01.SS |
| doc-sys-reviewer | `.claude/skills/doc-sys-reviewer/SKILL.md` | Verify section references |
| doc-sys-fixer | `.claude/skills/doc-sys-fixer/SKILL.md` | Verify fix patterns |
| doc-sys-autopilot | `.claude/skills/doc-sys-autopilot/SKILL.md` | Verify generation logic |

### 5.2 doc-sys/SKILL.md Fixes

**Line 79**: Add explicit section count:

```markdown
# Before:
### 1. Five-Part SYS Document Structure

# After:
### 1. SYS MVP Structure (15 Sections Total)

**MVP Template**: See `ai_dev_flow/06_SYS/SYS-MVP-TEMPLATE.md` for complete 15-section structure.
```

### 5.3 doc-sys_quickref.md Fixes

**Path correction** (line 30):
```markdown
# Before:
docs/SYS/SYS-NNN_{descriptive_name}.md

# After:
docs/06_SYS/SYS-NN_{descriptive_name}/SYS-NN_{descriptive_name}.md
```

**Template path correction** (line 76):
```markdown
# Before:
ai_dev_flow/06_SYS/SYS-MVP-TEMPLATE.md

# After (no change needed - already correct):
ai_dev_flow/06_SYS/SYS-MVP-TEMPLATE.md
```

### 5.4 doc-sys-validator/SKILL.md Fixes

**Line 115**: Fix FR-NNN to unified format:
```markdown
# Before:
- Section 4: Functional Requirements (FR-NNN format)

# After:
- Section 4: Functional Requirements (SYS.NN.01.SS format)
```

**Lines 143-146**: Fix FR-ID reference:
```markdown
# Before:
**Functional Requirement Format:**
- Pattern: `FR-NNN`
- Table columns: FR-ID, Requirement, Priority, Source, Verification Method

# After:
**Functional Requirement Format:**
- Pattern: `SYS.NN.01.SS` (unified 4-segment format)
- Table columns: SYS ID, Requirement, Priority, Source, Verification Method
```

---

## Phase 6: Testing & Validation

### 6.1 Template Validation

| Test | Command/Action | Expected Result |
|------|----------------|-----------------|
| Syntax check | Open in markdown viewer | Renders without errors |
| Section count | Count `## N.` headers | 15 sections (1-15) |
| Duplicate check | Search for duplicate headers | 0 duplicates |
| Frontmatter | Validate YAML | Single valid block |

### 6.2 Schema Validation

```bash
# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('SYS_MVP_SCHEMA.yaml').read())"

# Check for duplicates
grep -n "required_sections:" SYS_MVP_SCHEMA.yaml
# Expected: 1 occurrence

# Count required sections
grep -c "pattern:" SYS_MVP_SCHEMA.yaml
# Expected: 16 (Title + 15 sections)
```

### 6.3 Skill Testing

| Skill | Test Action | Expected Result |
|-------|-------------|-----------------|
| doc-sys | Create test SYS | 15-section SYS generated |
| doc-sys-validator | Validate test SYS | Pass all checks |
| doc-sys-autopilot | Generate SYS from YAML | Valid 15-section output |

### 6.4 YAML ↔ MD Template Sync Verification

**Purpose**: Ensure MD template and YAML template are aligned after changes.

| Check | MD Template | YAML Template | Expected |
|-------|-------------|---------------|----------|
| Total sections | Count `## N.` headers | Count `sections:` entries | 15 each |
| Section titles | Extract from headers | Extract from `title:` | Match exactly |
| Subsections | Count `### N.N` headers | Count `subsections:` | Match |
| Schema version | `custom_fields.schema_version` | `schema_version:` | Match |

**Verification Command**:
```bash
# Count sections in MD template
grep -c "^## [0-9]" SYS-MVP-TEMPLATE.md
# Expected: 15

# Count sections in YAML template
grep -c "number:" SYS-MVP-TEMPLATE.yaml
# Expected: 15

# Verify section titles match
diff <(grep "^## [0-9]" SYS-MVP-TEMPLATE.md | sed 's/## [0-9]*\. //') \
     <(grep "title:" SYS-MVP-TEMPLATE.yaml | head -15 | sed 's/.*title: "//;s/"$//')
# Expected: No output (files match)
```

---

## Execution Order

| Step | Phase | Action | Dependencies |
|------|-------|--------|--------------|
| 1 | 0 | Create backups | None |
| 2 | 1 | Update MD template metadata | Backup complete |
| 3 | 1 | Add template footer | Step 2 |
| 4 | 2 | Verify schema (no changes expected) | Step 3 |
| 5 | 3 | Update Validation Rules (15 sections list) | Step 4 |
| 6 | 3 | Update Creation Rules (15 sections) | Step 5 |
| 7 | 3 | Update Quality Gate thresholds | Step 6 |
| 8 | 3 | Update README.md (15 sections) | Step 7 |
| 9 | 4 | Expand YAML template (15 sections) | Step 8 |
| 10 | 5 | Update doc-sys/SKILL.md | Step 9 |
| 11 | 5 | Update doc-sys_quickref.md (paths) | Step 10 |
| 12 | 5 | Update doc-sys-validator/SKILL.md | Step 11 |
| 13 | 5 | Update remaining skills (3 files) | Step 12 |
| 14 | 6 | Run all tests | Step 13 |

**Note**: No MD template section renumbering needed - template already has correct 1-15 numbering.

---

## Verification Checklist

### MD Template Verification
- [ ] Single YAML frontmatter block at top
- [ ] Section 1 is Document Control (uses table format)
- [ ] 15 numbered sections exist (1-15)
- [ ] No duplicate section numbers
- [ ] Section 13 has Traceability with cumulative tags
- [ ] Section 15 has Change History
- [ ] Version metadata updated (schema_version: 2.1, total_sections: 15)
- [ ] Template footer added

### Validation Rules Verification
- [ ] Section structure includes 15-section table
- [ ] CHECK numbers reference correct sections
- [ ] No duplicate CHECK numbers

### Creation Rules Verification
- [ ] Section structure explicitly states "15 sections"
- [ ] 5-part organization documented
- [ ] Required sections list updated

### Schema Verification
- [ ] required_sections has 16 entries (Title + 15 sections)
- [ ] Section patterns match template headers (## 1. through ## 15.)
- [ ] Matches validation rules

### YAML Template Verification
- [ ] Section structure matches MD template
- [ ] All 15 sections defined with subsections
- [ ] Metadata updated (total_sections: 15)
- [ ] schema_version: 2.1

### Skill Files Verification
- [ ] doc-sys/SKILL.md explicitly says "15 sections"
- [ ] doc-sys_quickref.md path fixed (`docs/SYS/` → `docs/06_SYS/`)
- [ ] doc-sys-validator/SKILL.md FR-NNN fixed to SYS.NN.01.SS
- [ ] doc-sys-reviewer/SKILL.md section references updated
- [ ] doc-sys-fixer/SKILL.md fix patterns updated
- [ ] doc-sys-autopilot/SKILL.md generation logic verified

### README Verification
- [ ] Section count updated to explicit "15 sections"
- [ ] Section reference consistent

### Quality Gate Verification
- [ ] CORPUS-10 thresholds consistent
- [ ] All CORPUS checks reference correct sections

---

## Estimated Changes

| Metric | Count |
|--------|-------|
| MD Template lines modified | ~30 (metadata + footer) |
| YAML Template lines added | ~200 (expand from 4 to 15 sections) |
| Validation Rules fixes | ~30 lines added (section table) |
| Creation Rules fixes | ~30 lines modified |
| Quality Gate fixes | ~10 lines |
| README updates | ~10 lines |
| Skill files to update | 6 |
| Total sections after fix | 15 (Sections 1-15) |

---

## Migration Guide for Existing SYS Documents

**GOOD NEWS**: No section renumbering required for existing SYS documents!

The MD template already uses correct 1-15 section numbering. Migration only needed if existing SYS documents:
- Were created with non-standard section numbers
- Are missing required sections
- Use legacy element ID formats (FR-XXX, QA-XXX)

### Migration Steps (if needed)

1. **Check section structure**: Verify Sections 1-15 exist with correct titles
2. **Fix element IDs**: Replace legacy FR-XXX/QA-XXX with SYS.NN.01.SS/SYS.NN.02.SS
3. **Add missing sections**: Add any missing sections per template
4. **Fix traceability**: Ensure Section 13 has cumulative @brd, @prd, @ears, @bdd, @adr tags
5. **Validate**: Run `doc-sys-validator` on updated document

### Canonical Section Structure (Reference)

| Section | Title |
|---------|-------|
| 1 | Document Control |
| 2 | Executive Summary |
| 3 | Scope |
| 4 | Functional Requirements |
| 5 | Quality Attributes |
| 6 | Interface Specifications |
| 7 | Data Management Requirements |
| 8 | Testing and Validation Requirements |
| 9 | Deployment and Operations Requirements |
| 10 | Compliance and Regulatory Requirements |
| 11 | Acceptance Criteria |
| 12 | Risk Assessment |
| 13 | Traceability |
| 14 | Implementation Notes |
| 15 | Change History |

---

## Related Files to Update (Post-Implementation)

After fixing the template and skills, verify these files:

| File | Update Needed | Priority |
|------|---------------|----------|
| `REQ-MVP-TEMPLATE.md` | SYS section references | P3 |
| Existing SYS documents | Migration to unified element IDs | P3 |

---

**End of Plan**
