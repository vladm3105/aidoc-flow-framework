# EARS-MVP-TEMPLATE Fix Plan

**Created**: 2026-02-26
**Status**: Complete (Phase 0-7 Executed)
**Version**: 1.2
**Last Updated**: 2026-02-26
**Execution Date**: 2026-02-26
**Target Files**:
- `EARS-MVP-TEMPLATE.md` (primary)
- `EARS-MVP-TEMPLATE.yaml` (autopilot)
- `EARS_MVP_VALIDATION_RULES.md`
- `EARS_MVP_SCHEMA.yaml`
- `EARS_MVP_CREATION_RULES.md`
- `EARS_MVP_QUALITY_GATE_VALIDATION.md`
- `README.md`

## Overview

Fix identified gaps in `/opt/data/docs_flow_framework/ai_dev_ssd_flow/03_EARS/` documents and align template, validation rules, schema, and skills to a consistent **6-section** MVP structure.

## Target Files

| File | Type | Priority |
|------|------|----------|
| `EARS-MVP-TEMPLATE.md` | MD Template (human workflow) | P1 |
| `EARS_MVP_VALIDATION_RULES.md` | Validation Rules | P1 |
| `EARS_MVP_SCHEMA.yaml` | Schema Definition | P1 |
| `EARS_MVP_CREATION_RULES.md` | Creation Rules | P1 |
| `EARS-MVP-TEMPLATE.yaml` | YAML Template (autopilot) | P1 |
| `EARS_MVP_QUALITY_GATE_VALIDATION.md` | Quality Gate Rules | P2 |
| `README.md` | Layer Documentation | P2 |
| `doc-ears*/SKILL.md` | Skills (5 files) | P2 |
| `doc-ears_quickref.md` | Quick Reference | P2 |

## Reference Files

- `PRD-MVP-TEMPLATE_FIX_PLAN.md` (for alignment reference - example format)
- `ID_NAMING_STANDARDS.md` (for element ID format)

---

## Gap Summary

| # | Gap | Severity | Location | Phase |
|---|-----|----------|----------|-------|
| 1 | Duplicate YAML frontmatter in template | Critical | EARS-MVP-TEMPLATE.md lines 1-18, 40-61 | 1 |
| 2 | Duplicate YAML frontmatter in validation rules | Critical | EARS_MVP_VALIDATION_RULES.md lines 1-13, 22-34 | 1 |
| 3 | Duplicate YAML frontmatter in creation rules | Critical | EARS_MVP_CREATION_RULES.md lines 1-13, 22-33 | 1 |
| 4 | Template has only 2 sections, expected 6 | Critical | EARS-MVP-TEMPLATE.md | 2-3 |
| 5 | Section count mismatch (template=2, schema=5, creation=8, validator=10) | Critical | All files | 2 |
| 6 | Missing Section 1: Purpose and Context | High | EARS-MVP-TEMPLATE.md | 3 |
| 7 | Missing Section 2: Development Workflow | High | EARS-MVP-TEMPLATE.md | 3 |
| 8 | Current Section 2 labeled "Requirements Logic" should be Section 3 | Critical | EARS-MVP-TEMPLATE.md | 3 |
| 9 | Missing Section 4: Quality Attributes | High | EARS-MVP-TEMPLATE.md | 3 |
| 10 | Missing Section 5: Traceability | High | EARS-MVP-TEMPLATE.md | 3 |
| 11 | Missing Section 6: References | Medium | EARS-MVP-TEMPLATE.md | 3 |
| 12 | Validator expects 10 sections, inconsistent with other files | Critical | doc-ears-validator/SKILL.md | 5 |
| 13 | Path references inconsistent (EARS_SCHEMA vs EARS_MVP_SCHEMA) | Medium | Multiple skills | 5 |
| 14 | doc-ears skill references 6 sections correctly | Info | doc-ears/SKILL.md | - |
| 15 | Missing version metadata in template | Medium | EARS-MVP-TEMPLATE.md | 6 |
| 16 | Creation Rules lists 8 sections, should be 6 | High | EARS_MVP_CREATION_RULES.md | 4 |
| 17 | Template missing Document Control table format | High | EARS-MVP-TEMPLATE.md | 3 |
| 18 | Missing Ubiquitous requirements subsection in Section 3 | Medium | EARS-MVP-TEMPLATE.md | 3 |
| 19 | **No YAML ↔ MD sync verification step** | Medium | Fix Plan Phase 7 | 7 |
| 20 | Schema required_sections incomplete | High | EARS_MVP_SCHEMA.yaml | 2 |
| 21 | Quality Gate CORPUS-11/13 reference section structure | Medium | EARS_MVP_QUALITY_GATE_VALIDATION.md | 4 |
| 22 | Scripts path references inconsistent (scripts/ folder) | Medium | Multiple files | 5 |
| 23 | FIXES_SUMMARY.md outdated | Low | FIXES_SUMMARY.md | 6 |
| 24 | Example files need 6-section alignment | Medium | examples/EARS-01_*.md, EARS-02_*.md | 4 |
| 25 | doc-ears-reviewer Check #6 Section Completeness wrong sections | High | doc-ears-reviewer/SKILL.md | 5 |
| 26 | doc-ears-fixer phases reference wrong sections | High | doc-ears-fixer/SKILL.md | 5 |
| 27 | Quality Gate file size triggers (20k tokens) not in template | Low | EARS_MVP_QUALITY_GATE_VALIDATION.md | 4 |
| 28 | BDD-Ready Score calculation not aligned with 6-section structure | Medium | Multiple skills | 5 |
| 29 | Index file template reference may need update | Low | EARS-00_index.md | 4 |
| 30 | doc-ears SKILL.md line 54 references wrong schema filename | Medium | doc-ears/SKILL.md:54 | 5 |
| 31 | Traceability Matrix template section references | Low | EARS-00_TRACEABILITY_MATRIX-TEMPLATE.md | 4 |
| 32 | AI_CONTEXT comment in template references wrong section count | Low | EARS-MVP-TEMPLATE.md:29-37 | 1 |

---

## Phase 0: Pre-Implementation

### 0.1 Backup All Files

```bash
# Create backup directory
mkdir -p /opt/data/docs_flow_framework/ai_dev_ssd_flow/03_EARS/.backup_2026-02-26

# Backup templates and rules
cp EARS-MVP-TEMPLATE.md .backup_2026-02-26/
cp EARS-MVP-TEMPLATE.yaml .backup_2026-02-26/
cp EARS_MVP_VALIDATION_RULES.md .backup_2026-02-26/
cp EARS_MVP_CREATION_RULES.md .backup_2026-02-26/
cp EARS_MVP_QUALITY_GATE_VALIDATION.md .backup_2026-02-26/
cp EARS_MVP_SCHEMA.yaml .backup_2026-02-26/
cp README.md .backup_2026-02-26/

# Backup skills
cp -r /opt/data/docs_flow_framework/.claude/skills/doc-ears* .backup_2026-02-26/
```

### 0.2 Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Existing EARS reference old section numbers | Medium | High | Document migration guide |
| Autopilot fails with new structure | Medium | High | Update YAML template in Phase 4.5 |
| Skills produce invalid output | Medium | Medium | Update all skills in Phase 5 |
| Validation rules mismatch | Low | Medium | Verify CHECK numbers align |
| Cross-document links break | Low | Low | Update references in Phase 4 |

### 0.3 Rollback Plan

**If issues occur during implementation:**

1. **Immediate Rollback**:
   ```bash
   # Restore all files
   cp .backup_2026-02-26/EARS-MVP-TEMPLATE.md ./
   cp .backup_2026-02-26/EARS-MVP-TEMPLATE.yaml ./
   cp .backup_2026-02-26/EARS_MVP_VALIDATION_RULES.md ./
   cp .backup_2026-02-26/EARS_MVP_SCHEMA.yaml ./
   cp .backup_2026-02-26/README.md ./

   # Restore skills
   cp -r .backup_2026-02-26/doc-ears* /opt/data/docs_flow_framework/.claude/skills/
   ```

2. **Partial Rollback**: Revert only affected files from backup

3. **Post-Rollback**: Re-run validators to confirm restored state

### 0.4 Downstream Impact Analysis

| Downstream Artifact | Impact | Action Required |
|--------------------|--------|-----------------|
| Existing EARS documents | Section numbers changed | Add migration note to plan |
| BDD templates | Reference EARS sections | Verify BDD-MVP-TEMPLATE references |
| Validation scripts | CHECK numbers reference sections | Verify EARS_MVP_VALIDATION_RULES.md |
| Autopilot workflows | Generate from YAML template | Update YAML template (Phase 4.5) |
| doc-ears-reviewer | Check section completeness | Verify 6-section check |
| doc-ears-fixer | Fix phases reference sections | Verify section creation logic |
| Quality Gate validation | Corpus-level checks | Verify EARS_MVP_QUALITY_GATE_VALIDATION.md |

### 0.5 Decision: Target Section Count

**Analysis**:
- Current MD template: 2 sections (incomplete)
- YAML template: 4 sections
- Schema: 5 sections
- Creation rules: 8 sections
- Validator skill: 10 sections
- doc-ears skill: 6 sections

**Decision**: Align to **6 sections** as per doc-ears skill (most reasonable MVP structure):

1. Document Control (unnumbered)
2. Section 1: Purpose and Context
3. Section 2: Development Workflow
4. Section 3: Requirements (Event-Driven, State-Driven, Unwanted Behavior, Ubiquitous)
5. Section 4: Quality Attributes
6. Section 5: Traceability
7. Section 6: References

---

## Phase 1: Critical Structural Fixes

### 1.1 Remove Duplicate YAML Frontmatter in Template

**File**: `EARS-MVP-TEMPLATE.md`

**Current State**:
- Lines 1-18: First (correct) YAML frontmatter
- Lines 28-38: AI_CONTEXT HTML comment block
- Lines 39-61: Second (duplicate) YAML frontmatter

**Action**: Delete lines 39-61 (second frontmatter block)

**Keep**: Lines 1-18 (first frontmatter) and lines 28-38 (AI_CONTEXT)

### 1.2 Remove Duplicate YAML Frontmatter in Validation Rules

**File**: `EARS_MVP_VALIDATION_RULES.md`

**Current State**:
- Lines 1-13: First YAML frontmatter (valid)
- Lines 22-34: Second YAML frontmatter (duplicate)

**Action**: Delete lines 22-34 (second frontmatter block)

### 1.3 Remove Duplicate YAML Frontmatter in Creation Rules

**File**: `EARS_MVP_CREATION_RULES.md`

**Current State**:
- Lines 1-13: First YAML frontmatter (valid)
- Lines 22-33: Second YAML frontmatter (duplicate)

**Action**: Delete lines 22-33 (second frontmatter block)

---

## Phase 2: Define Target 6-Section Structure

### 2.1 Target Section Mapping

Based on doc-ears skill (source of truth for MVP structure):

| # | Section Title | Validation | Schema | Template Status |
|---|--------------|------------|--------|-----------------|
| - | Document Control | Required | Required | EXISTS (but needs table format) |
| 1 | Purpose and Context | Required | Required | **MISSING** |
| 2 | EARS in Development Workflow | Required | Required | **MISSING** |
| 3 | Requirements | Required | Required | EXISTS as "2. Requirements Logic" (renumber) |
| 4 | Quality Attributes | Required | Required | **MISSING** |
| 5 | Traceability | Required | Required | **MISSING** |
| 6 | References | Required | Required | **MISSING** |

### 2.2 Requirements Subsections (Section 3)

Section 3 must include all 4 EARS requirement types:

| Subsection | Pattern | Status |
|------------|---------|--------|
| 3.1 Event-Driven | WHEN-THE-SHALL-WITHIN | EXISTS (as 2.1) |
| 3.2 State-Driven | WHILE-THE-SHALL-WITHIN | EXISTS (as 2.3) |
| 3.3 Unwanted Behavior | IF-THE-SHALL-WITHIN | EXISTS (as 2.2) |
| 3.4 Ubiquitous | THE-SHALL | **MISSING** |

---

## Phase 3: Add Missing Sections to Template

### 3.1 Fix Document Control Section

Replace current Document Control with table format:

```markdown
## Document Control

| Item | Details |
|------|---------|
| **Version** | 0.1.0 |
| **Status** | Draft / Review / Approved |
| **Date Created** | YYYY-MM-DD |
| **Last Updated** | YYYY-MM-DD |
| **Author** | [Author Name] |
| **Priority** | Critical (P1) / High (P2) / Medium (P3) / Low (P4) |
| **Source Document** | @prd: PRD.NN.EE.SS |
| **BDD-Ready Score** | NN% (Target: ≥90%) |
```

### 3.2 Add Section 1: Purpose and Context

Insert after Document Control:

```markdown
## 1. Purpose and Context

### 1.1 Document Purpose

[Purpose statement: Convert PRD features into formal EARS statements
using WHEN-THE-SHALL-WITHIN format for clarity and unambiguousness.
Provide precise timing and performance specifications for each requirement.]

### 1.2 Scope

[Scope description: Define the boundaries of these formal requirements.
Include which PRD features are mapped and which are out of scope.
Specify the system components and interfaces covered.]

### 1.3 Intended Audience

[Target audience: System architects, developers, QA engineers,
and business analysts who need precise requirements specifications.]
```

### 3.3 Add Section 2: EARS in Development Workflow

Insert after Section 1:

```markdown
## 2. EARS in Development Workflow

### 2.1 Workflow Position

```
BRD → PRD → **EARS** → BDD → ADR → SYS → REQ → SPEC → TASKS
```

### 2.2 Role in Specification-Driven Development

EARS documents serve as the translation layer between product requirements (PRD)
and behavioral test specifications (BDD). Each EARS statement must be:

1. **Testable**: Can be translated directly to BDD Given-When-Then scenarios
2. **Measurable**: Contains quantifiable constraints with @threshold references
3. **Traceable**: Links to upstream PRD and downstream BDD artifacts
4. **Atomic**: Defines one testable concept per statement
```

### 3.4 Restructure Section 3: Requirements

Rename current "2. Requirements Logic" to "3. Requirements" and add Ubiquitous subsection:

```markdown
## 3. Requirements

### 3.1 Event-Driven Requirements (WHEN-THE-SHALL-WITHIN)

**EARS.NN.25.001: [Requirement Name]**
```
WHEN [trigger condition],
THE [system component] SHALL [response action]
WITHIN [timing constraint] (@threshold: PRD.NN.category.key).
```
**Traceability**: @brd: BRD.NN.EE.SS | @prd: PRD.NN.EE.SS

### 3.2 State-Driven Requirements (WHILE-THE-SHALL-WITHIN)

**EARS.NN.25.101: [State Behavior]**
```
WHILE [state condition],
THE [system component] SHALL [continuous behavior]
WITHIN [operational context].
```
**Traceability**: @brd: BRD.NN.EE.SS | @prd: PRD.NN.EE.SS

### 3.3 Unwanted Behavior Requirements (IF-THE-SHALL-WITHIN)

**EARS.NN.25.201: [Error Scenario]**
```
IF [error condition],
THE [system component] SHALL [recovery action]
WITHIN [timing constraint].
```
**Traceability**: @brd: BRD.NN.EE.SS | @prd: PRD.NN.EE.SS

### 3.4 Ubiquitous Requirements (THE-SHALL)

**EARS.NN.25.401: [System-Wide Requirement]**
```
THE [system component] SHALL [universal behavior]
for [scope/context].
```
**Traceability**: @brd: BRD.NN.EE.SS | @prd: PRD.NN.EE.SS
```

### 3.5 Add Section 4: Quality Attributes

Insert after Section 3:

```markdown
## 4. Quality Attributes

### 4.1 Performance Requirements

| QA ID | Requirement Statement | Metric | Target | Priority | Measurement Method |
|-------|----------------------|--------|--------|----------|-------------------|
| EARS.NN.02.01 | THE [component] SHALL complete [operation] | Latency | p95 < NNms | High | Load test |
| EARS.NN.02.02 | THE [component] SHALL process [workload] | Throughput | NN/s | Medium | Performance test |

### 4.2 Security Requirements

| QA ID | Requirement Statement | Control | Compliance | Priority |
|-------|----------------------|---------|------------|----------|
| EARS.NN.03.01 | THE [component] SHALL authenticate using [method] | Authentication | [standard] | High |

### 4.3 Reliability Requirements

| QA ID | Requirement Statement | Metric | Target | Priority |
|-------|----------------------|--------|--------|----------|
| EARS.NN.04.01 | THE [component] SHALL maintain availability | Uptime | 99.9% | High |
```

### 3.6 Add Section 5: Traceability

Insert after Section 4:

```markdown
## 5. Traceability

### 5.1 Upstream Sources

| Tag | Document | Section |
|-----|----------|---------|
| @brd | BRD.NN.EE.SS | [Section reference] |
| @prd | PRD.NN.EE.SS | [Section reference] |

### 5.2 Downstream Artifacts

| Artifact | Purpose | Status |
|----------|---------|--------|
| BDD | Behavioral test scenarios | Pending |
| ADR | Architecture decisions | Pending |
| SYS | System requirements | Pending |

### 5.3 Traceability Tags

**Required Tags** (Cumulative Tagging Hierarchy - Layer 3):
```markdown
@brd: BRD.NN.EE.SS
@prd: PRD.NN.EE.SS
```

### 5.4 Threshold References

| Threshold ID | Category | Value | Source |
|--------------|----------|-------|--------|
| @threshold: PRD.NN.timeout.category.key | Timing | NNms | PRD Section 20.1 |
| @threshold: PRD.NN.perf.category.key | Performance | NN/s | PRD Section 14 |
```

### 3.7 Add Section 6: References

Insert after Section 5:

```markdown
## 6. References

### 6.1 Internal Documentation

| Document | Location | Purpose |
|----------|----------|---------|
| BRD-NN | `../01_BRD/BRD-NN_*.md` | Business requirements source |
| PRD-NN | `../02_PRD/PRD-NN_*.md` | Product requirements source |

### 6.2 External Standards

| Standard | Organization | Relevance |
|----------|--------------|-----------|
| EARS Syntax | Alistair Mavin et al. | Requirement specification format |

### 6.3 Framework References

| Reference | Type | Notes |
|-----------|------|-------|
| ID_NAMING_STANDARDS.md | Framework Guide | Element ID format |
| THRESHOLD_NAMING_RULES.md | Framework Guide | @threshold tag format |
```

### 3.8 Add Template Footer

Add document footer:

```markdown
---

**Document Version**: 0.1.0
**Template Version**: 1.1 (MVP - 6 sections)
**Last Updated**: 2026-02-26
**Maintained By**: [Requirements Engineer]

---

> **MVP Template Notes**:
> - This is the standard EARS template (6 sections)
> - Single file - no sectioning per user requirement
> - Maintains ai_dev_flow framework compliance
> - **Lifecycle**: MVP → PROD → NEW MVP (no separate "full EARS" template)
```

---

## Phase 4: Update Supporting Documents

### 4.1 Update Creation Rules Section List

**File**: `EARS_MVP_CREATION_RULES.md`

Change from 8 sections to 6 sections:

```markdown
## 2. Document Structure (Required sections)

EARS documents require specific structural elements for behavioral specification:

#### Required sections:
1. **Document Control** - Metadata with BDD-Ready Score (unnumbered)
2. **Section 1: Purpose and Context** - Business and technical objectives
3. **Section 2: Development Workflow** - SDD position and EARS role
4. **Section 3: Requirements** - Event-Driven, State-Driven, Unwanted Behavior, Ubiquitous
5. **Section 4: Quality Attributes** - Performance, Security, Reliability
6. **Section 5: Traceability** - Upstream sources, downstream artifacts, tags
7. **Section 6: References** - Internal and external documentation
```

### 4.2 Update Schema Required Sections

**File**: `EARS_MVP_SCHEMA.yaml`

Update `required_sections` to match 6-section structure:

```yaml
structure:
  required_sections:
    - pattern: "^# EARS-\\d{2,}:"
      name: "Title (H1)"
      description: "Single H1 with format EARS-NN: Title"

    - pattern: "^## Document Control$"
      name: "Document Control"
      description: "Contains metadata table with Source Document"

    - pattern: "^## 1\\. Purpose and Context$"
      name: "Purpose and Context"
      description: "Section 1 with Purpose, Scope, Audience subsections"

    - pattern: "^## 2\\. EARS in Development Workflow$"
      name: "Development Workflow"
      description: "Section 2 with workflow diagram"

    - pattern: "^## 3\\. Requirements$"
      name: "Requirements"
      description: "Section 3 with Event-Driven, State-Driven, Unwanted Behavior, Ubiquitous"

    - pattern: "^## 4\\. Quality Attributes$"
      name: "Quality Attributes"
      description: "Section 4 with Performance, Security, Reliability"

    - pattern: "^## 5\\. Traceability$"
      name: "Traceability"
      description: "Section 5 with upstream sources, downstream artifacts, tags"

    - pattern: "^## 6\\. References$"
      name: "References"
      description: "Section 6 with internal and external documentation"
```

### 4.3 Update README.md

- Update section count from unspecified to 6
- Update section reference table
- Remove any references to 10-section structure

---

## Phase 4.5: Update YAML Template

**File**: `EARS-MVP-TEMPLATE.yaml`

The YAML template currently has 4 sections. Sync with MD template (6 sections):

### 4.5.1 Add Section Structure

```yaml
sections:
  - number: 0
    title: "Document Control"
    required: true
    unnumbered: true
  - number: 1
    title: "Purpose and Context"
    required: true
    subsections:
      - "1.1 Document Purpose"
      - "1.2 Scope"
      - "1.3 Intended Audience"
  - number: 2
    title: "EARS in Development Workflow"
    required: true
    subsections:
      - "2.1 Workflow Position"
      - "2.2 Role in Specification-Driven Development"
  - number: 3
    title: "Requirements"
    required: true
    subsections:
      - "3.1 Event-Driven Requirements"
      - "3.2 State-Driven Requirements"
      - "3.3 Unwanted Behavior Requirements"
      - "3.4 Ubiquitous Requirements"
  - number: 4
    title: "Quality Attributes"
    required: true
    subsections:
      - "4.1 Performance Requirements"
      - "4.2 Security Requirements"
      - "4.3 Reliability Requirements"
  - number: 5
    title: "Traceability"
    required: true
    subsections:
      - "5.1 Upstream Sources"
      - "5.2 Downstream Artifacts"
      - "5.3 Traceability Tags"
      - "5.4 Threshold References"
  - number: 6
    title: "References"
    required: true
    subsections:
      - "6.1 Internal Documentation"
      - "6.2 External Standards"
      - "6.3 Framework References"
```

### 4.5.2 Update Metadata

```yaml
schema_version: "1.1"
last_updated: "2026-02-26"
total_sections: 6
```

---

## Phase 5: Update doc-ears* Skills

### 5.1 Target Skill Files

| Skill | File Path | Update Scope |
|-------|-----------|--------------|
| doc-ears | `.claude/skills/doc-ears/SKILL.md` | Already has 6 sections - verify consistency |
| doc-ears-validator | `.claude/skills/doc-ears-validator/SKILL.md` | **CRITICAL**: Says 10 sections, should be 6 |
| doc-ears-reviewer | `.claude/skills/doc-ears-reviewer/SKILL.md` | Review criteria update |
| doc-ears-fixer | `.claude/skills/doc-ears-fixer/SKILL.md` | Fix patterns update |
| doc-ears-autopilot | `.claude/skills/doc-ears-autopilot/SKILL.md` | Verify section references |
| doc-ears_quickref | `.claude/skills/doc-ears_quickref.md` | Fix paths, section count |

### 5.2 doc-ears-validator/SKILL.md Fixes (CRITICAL)

**Lines 107-120**: Replace 10-section list with 6-section list:

```markdown
### 2. Structure Validation

**Required Sections:**
- Title (H1): `# EARS-NN: Title`
- Document Control (unnumbered)
- Section 1: Purpose and Context
- Section 2: EARS in Development Workflow
- Section 3: Requirements (with 4 subsections)
- Section 4: Quality Attributes
- Section 5: Traceability
- Section 6: References
```

### 5.3 doc-ears_quickref.md Fixes

- Update path `docs/EARS/` to `docs/03_EARS/`
- Update section count reference
- Update template location

---

## Phase 6: Minor Fixes and Metadata

### 6.1 Update Version Metadata in Template

Update YAML frontmatter in `EARS-MVP-TEMPLATE.md`:

```yaml
---
title: "EARS-MVP-TEMPLATE: EARS Requirements (MVP)"
tags:
  - ears-template
  - mvp-template
  - layer-3-artifact
  - document-template
  - shared-architecture
custom_fields:
  document_type: template
  artifact_type: EARS
  layer: 3
  template_variant: mvp
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  schema_version: "1.1"          # Updated from 1.0
  last_updated: "2026-02-26"     # Added
  total_sections: 6              # Added
---
```

---

## Phase 7: Testing & Validation

### 7.1 Template Validation

| Test | Command/Action | Expected Result |
|------|----------------|-----------------|
| Syntax check | Open in markdown viewer | Renders without errors |
| Section count | Count `## N.` headers | 6 sections + Document Control |
| Duplicate check | Search for duplicate headers | 0 duplicates |
| Frontmatter | Validate YAML | Single valid block |

### 7.2 Schema Validation

```bash
# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('EARS_MVP_SCHEMA.yaml').read())"

# Check for duplicates
grep -n "required_sections:" EARS_MVP_SCHEMA.yaml
# Expected: 1 occurrence
```

### 7.3 Skill Testing

| Skill | Test Action | Expected Result |
|-------|-------------|-----------------|
| doc-ears | Create test EARS | 6-section EARS generated |
| doc-ears-validator | Validate test EARS | Pass all checks |
| doc-ears-autopilot | Generate EARS from YAML | Valid 6-section output |

### 7.4 YAML ↔ MD Template Sync Verification

**Purpose**: Ensure MD template and YAML template are aligned after changes.

| Check | MD Template | YAML Template | Expected |
|-------|-------------|---------------|----------|
| Total sections | Count `## N.` headers | Count `sections:` entries | 6 each |
| Section titles | Extract from headers | Extract from `title:` | Match exactly |
| Subsections | Count `### N.N` headers | Count `subsections:` | Match |
| Schema version | `custom_fields.schema_version` | `schema_version:` | Match |

**Verification Command**:
```bash
# Count sections in MD template
grep -c "^## [0-9]" EARS-MVP-TEMPLATE.md
# Expected: 6

# Count sections in YAML template
grep -c "number:" EARS-MVP-TEMPLATE.yaml
# Expected: 7 (including Document Control as 0)

# Verify section titles match
diff <(grep "^## [0-9]" EARS-MVP-TEMPLATE.md | sed 's/## [0-9]*\. //') \
     <(grep "title:" EARS-MVP-TEMPLATE.yaml | grep -v "Document Control" | sed 's/.*title: "//;s/"$//')
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
| 5 | 3 | Add Document Control table format | Step 4 |
| 6 | 3 | Add Section 1 (Purpose and Context) | Step 5 |
| 7 | 3 | Add Section 2 (Development Workflow) | Step 6 |
| 8 | 3 | Restructure Section 3 (Requirements) | Step 7 |
| 9 | 3 | Add Section 4 (Quality Attributes) | Step 8 |
| 10 | 3 | Add Section 5 (Traceability) | Step 9 |
| 11 | 3 | Add Section 6 (References) | Step 10 |
| 12 | 3 | Add template footer | Step 11 |
| 13 | 4 | Update Creation Rules | Step 12 |
| 14 | 4 | Update Schema | Step 13 |
| 15 | 4 | Update README.md | Step 14 |
| 16 | 4.5 | Update YAML template | Step 15 |
| 17 | 5 | Update all skills | Step 16 |
| 18 | 6 | Update version metadata | Step 17 |
| 19 | 7 | Run all tests | Step 18 |

---

## Verification Checklist

### Template Verification
- [x] Single YAML frontmatter block at top
- [x] Document Control uses table format
- [x] 6 numbered sections exist (1-6)
- [x] No duplicate section numbers
- [x] Section 3 has 4 subsections (Event, State, Unwanted, Ubiquitous)
- [x] Section 4 has Quality Attributes tables
- [x] Section 5 has Traceability with @brd, @prd tags
- [x] Section 6 has References
- [x] Version metadata updated (schema_version: 1.1)

### Validation Rules Verification
- [x] Single YAML frontmatter block
- [x] Section structure matches template (6 sections)
- [ ] CHECK numbers reference correct sections (needs manual verification)
- [x] No duplicate frontmatter blocks

### Creation Rules Verification
- [x] Single YAML frontmatter block (duplicate removed)
- [x] Section structure matches template (6 sections)
- [x] Required sections list updated

### Schema Verification
- [x] required_sections has 8 entries (Title + Document Control + 6 sections)
- [x] Section patterns match template headers
- [x] Matches validation rules

### YAML Template Verification
- [x] Section structure matches MD template
- [x] All 6 sections defined with subsections
- [x] Metadata updated

### Skill Files Verification
- [x] doc-ears/SKILL.md consistent (already 6 sections)
- [x] doc-ears-validator/SKILL.md updated from 10 to 6 sections
- [x] doc-ears-reviewer/SKILL.md section references updated (generic, acceptable)
- [x] doc-ears-fixer/SKILL.md fix patterns updated (no hard-coded section numbers found)
- [x] doc-ears-autopilot/SKILL.md generation logic verified (uses PRD sections, not EARS sections)
- [x] doc-ears_quickref.md paths and counts updated

### README Verification
- [x] Section count updated to 6
- [x] Section reference table updated

---

## Estimated Changes

| Metric | Count |
|--------|-------|
| MD Template lines added | ~200 |
| MD Template lines modified | ~50 |
| MD Template lines removed | ~40 |
| Validation Rules fixes | ~15 lines removed |
| Creation Rules fixes | ~15 lines removed, ~20 modified |
| Schema fixes | ~30 lines modified |
| YAML Template updates | ~80 lines |
| README updates | ~20 lines |
| Skill files to update | 5 |
| Total sections after fix | 6 + Document Control |

---

## Migration Guide for Existing EARS

If existing EARS documents need updating:

1. **Identify affected documents**: Search for EARS using old section numbers
2. **Section restructuring**: Apply mapping from Phase 2 table
3. **Add missing sections**: Insert Sections 1, 2, 4, 5, 6
4. **Rename Section 2 to 3**: "Requirements Logic" → "Requirements"
5. **Add Ubiquitous subsection**: Create Section 3.4
6. **Update traceability**: Ensure Section 5 format with subsections
7. **Add Document Control table**: Convert to table format if needed
8. **Validate**: Run validator on updated document

### Section Migration Mapping

| Old Structure | New Location |
|---------------|--------------|
| Document Control (list) | Document Control (table) |
| 2. Requirements Logic | 3. Requirements |
| 2.1 Event-Driven | 3.1 Event-Driven |
| 2.2 Unwanted Behavior | 3.3 Unwanted Behavior |
| 2.3 State-Driven | 3.2 State-Driven |
| (none) | 1. Purpose and Context |
| (none) | 2. Development Workflow |
| (none) | 3.4 Ubiquitous |
| (none) | 4. Quality Attributes |
| (none) | 5. Traceability |
| (none) | 6. References |

---

## Related Files to Update (Post-Implementation)

After fixing the template and skills, verify these files:

| File | Update Needed | Priority |
|------|---------------|----------|
| `BDD-MVP-TEMPLATE.feature` | EARS section references | P3 |
| `ADR-MVP-TEMPLATE.md` | EARS section references | P3 |
| Existing EARS documents | Migration to new structure | P3 |

---

**End of Plan**
