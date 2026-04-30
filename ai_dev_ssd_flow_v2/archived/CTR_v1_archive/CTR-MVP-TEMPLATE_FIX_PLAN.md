# CTR-MVP-TEMPLATE Fix Plan

**Created**: 2026-02-26
**Status**: Pending
**Version**: 1.3
**Last Updated**: 2026-02-26
**Target Files**:
- `CTR-MVP-TEMPLATE.md` (primary)
- `CTR-MVP-TEMPLATE.yaml` (autopilot)
- `CTR_MVP_VALIDATION_RULES.md`
- `CTR_MVP_SCHEMA.yaml`
- `CTR_MVP_CREATION_RULES.md`
- `CTR_MVP_QUALITY_GATE_VALIDATION.md`
- `README.md`

## Overview

Fix identified gaps in `/opt/data/docs_flow_framework/ucx_flow_v3/08_CTR/` documents and align template, validation rules, schema, and skills to a consistent **12-section** MVP structure with 2 optional lettered appendices (A, B).

## Target Files

| File | Type | Priority |
|------|------|----------|
| `CTR-MVP-TEMPLATE.md` | MD Template (human workflow) | P1 |
| `CTR_MVP_VALIDATION_RULES.md` | Validation Rules | P1 |
| `CTR_MVP_SCHEMA.yaml` | Schema Definition | P1 |
| `CTR_MVP_CREATION_RULES.md` | Creation Rules | P1 |
| `CTR-MVP-TEMPLATE.yaml` | YAML Template (autopilot) | P1 |
| `CTR_MVP_QUALITY_GATE_VALIDATION.md` | Quality Gate Rules | P2 |
| `README.md` | Layer Documentation | P2 |
| `doc-ctr*/SKILL.md` | Skills (5 files) | P2 |

## Reference Files

- `ADR-MVP-TEMPLATE_FIX_PLAN.md` (for alignment reference - 11 sections)
- `PRD-MVP-TEMPLATE_FIX_PLAN.md` (for alignment reference - 21 sections)
- `/opt/data/docs_flow_framework/ucx_flow_v3/ID_NAMING_STANDARDS.md` (for element ID format and type codes - **AUTHORITATIVE SOURCE**)

## Element Type Code Reference (from `ucx_flow_v3/ID_NAMING_STANDARDS.md`)

**Source**: `/opt/data/docs_flow_framework/ucx_flow_v3/ID_NAMING_STANDARDS.md`

**Authoritative CTR Element Type Codes** (per `ucx_flow_v3/ID_NAMING_STANDARDS.md` lines 1259-1263):

| Code | Element Type | Artifact Types |
|------|--------------|----------------|
| 16 | Interface | SPEC, CTR |
| 17 | Data Model | SPEC, CTR |
| 20 | Contract Clause | CTR |

**IMPORTANT**: The codes 28, 29 used in doc-ctr-fixer and doc-ctr-reviewer are **NOT VALID** per `ucx_flow_v3/ID_NAMING_STANDARDS.md`. These must be corrected to 16, 17, 20.

---

## Gap Summary

| # | Gap | Severity | Location | Phase |
|---|-----|----------|----------|-------|
| 1 | **PART markers in template create non-standard structure** | Critical | CTR-MVP-TEMPLATE.md lines 65, 173, 238, 354 | 2 |
| 2 | **Duplicate section numbers** (## 2. appears twice, ## 5. appears twice, etc.) | Critical | CTR-MVP-TEMPLATE.md | 2 |
| 3 | **Section count mismatch**: Template has mixed structure, Validation=12, Schema=12, doc-ctr=7, doc-ctr-validator=20 | Critical | All files | 2 |
| 4 | **Wrong layer tag in Validation Rules** (`layer-9-artifact` should be `layer-8-artifact`) | Critical | CTR_MVP_VALIDATION_RULES.md:5, 108 | 1 |
| 5 | **Wrong layer tag in Schema** (`layer-9-artifact` should be `layer-8-artifact`) | Critical | CTR_MVP_SCHEMA.yaml:108 | 1 |
| 6 | **doc-ctr skill references wrong template** (`CTR-TEMPLATE.md` vs `CTR-MVP-TEMPLATE.md`) | High | doc-ctr/SKILL.md:52,751,752 | 5 |
| 7 | **doc-ctr skill says "7 sections"** | High | doc-ctr/SKILL.md:125-133 | 5 |
| 8 | **doc-ctr-validator says "20 sections in 5 Parts"** | Critical | doc-ctr-validator/SKILL.md:119-151 | 5 |
| 9 | **Schema has `layer: 9` in custom_fields** (should be 8) | Medium | CTR_MVP_SCHEMA.yaml:99 | 1 |
| 10 | **Creation Rules says "12-Section Structure"** but has different section list | High | CTR_MVP_CREATION_RULES.md:157-175 | 4 |
| 11 | **Quality Gate references "12 sections"** (Section 4 header says "12-Section Format") | Medium | CTR_MVP_VALIDATION_RULES.md:143 | 4 |
| 12 | **Template has Appendix sections numbered 13 and 14** instead of using lettered appendices | Medium | CTR-MVP-TEMPLATE.md:559, 590 | 2 |
| 13 | **README references "12-section structure"** | Medium | README.md:746-747 | 4 |
| 14 | **Missing version metadata in frontmatter** | Low | CTR-MVP-TEMPLATE.md | 6 |
| 15 | **No YAML ↔ MD sync verification step** in validation rules | Medium | Fix Plan Phase 7 | 7 |
| 16 | **doc-ctr-autopilot references inconsistent section structure** | Medium | doc-ctr-autopilot/SKILL.md | 5 |
| 17 | **Validation Rules CHECK 8 says "1-20 sections"** | High | CTR_MVP_VALIDATION_RULES.md (error codes) | 4 |
| 18 | **Element type code inconsistency across skills** (doc-ctr uses 16, 17, 20; doc-ctr-reviewer/fixer use 28, 29) | High | doc-ctr*/SKILL.md | 5 |
| 19 | **doc-ctr-reviewer "12/12" reference** needs verification | Medium | doc-ctr-reviewer/SKILL.md:110 | 5 |
| 20 | **doc-ctr-fixer uses CTR-NN-TYPE-SS pattern** (differs from standard CTR-NN) | High | doc-ctr-fixer/SKILL.md:319-349 | 5 |
| 21 | **doc-ctr-reviewer element type codes 28, 29** (inconsistent with other skills) | High | doc-ctr-reviewer/SKILL.md:257-258 | 5 |
| 22 | **Wrong directory path in skills**: `ucx_flow_v3/` should be `ucx_flow_v3/` | Critical | doc-ctr/SKILL.md, doc-ctr-validator/SKILL.md, doc-ctr-autopilot/SKILL.md | 5 |

---

## Phase 0: Pre-Implementation

### 0.1 Backup All Files

```bash
# Create backup directory
mkdir -p /opt/data/docs_flow_framework/ucx_flow_v3/08_CTR/.backup_2026-02-26

# Backup templates and rules
cd /opt/data/docs_flow_framework/ucx_flow_v3/08_CTR
cp CTR-MVP-TEMPLATE.md .backup_2026-02-26/
cp CTR-MVP-TEMPLATE.yaml .backup_2026-02-26/
cp CTR_MVP_VALIDATION_RULES.md .backup_2026-02-26/
cp CTR_MVP_CREATION_RULES.md .backup_2026-02-26/
cp CTR_MVP_QUALITY_GATE_VALIDATION.md .backup_2026-02-26/
cp CTR_MVP_SCHEMA.yaml .backup_2026-02-26/
cp README.md .backup_2026-02-26/

# Backup skills
cp -r /opt/data/docs_flow_framework/.claude/skills/doc-ctr* .backup_2026-02-26/
```

### 0.2 Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Existing CTRs reference old section numbers | Medium | High | Document migration guide |
| Autopilot fails with new structure | Medium | High | Update YAML template in Phase 4.5 |
| Skills produce invalid output | Medium | Medium | Update all skills in Phase 5 |
| Validation rules mismatch | Low | Medium | Verify CHECK numbers align |
| Cross-document links break | Low | Low | Update references in Phase 4 |

### 0.3 Rollback Plan

**If issues occur during implementation:**

1. **Immediate Rollback**:
   ```bash
   cd /opt/data/docs_flow_framework/ucx_flow_v3/08_CTR
   cp .backup_2026-02-26/CTR-MVP-TEMPLATE.md ./
   cp .backup_2026-02-26/CTR-MVP-TEMPLATE.yaml ./
   cp .backup_2026-02-26/CTR_MVP_VALIDATION_RULES.md ./
   cp .backup_2026-02-26/CTR_MVP_CREATION_RULES.md ./
   cp .backup_2026-02-26/CTR_MVP_QUALITY_GATE_VALIDATION.md ./
   cp .backup_2026-02-26/CTR_MVP_SCHEMA.yaml ./
   cp .backup_2026-02-26/README.md ./

   # Restore skills
   cp -r .backup_2026-02-26/doc-ctr* /opt/data/docs_flow_framework/.claude/skills/
   ```

2. **Partial Rollback**: Revert only affected files from backup

3. **Post-Rollback**: Re-run validators to confirm restored state

### 0.4 Downstream Impact Analysis

| Downstream Artifact | Impact | Action Required |
|--------------------|--------|-----------------|
| Existing CTR documents | Section numbers may change | Document migration guide |
| SPEC templates | Reference CTR sections | Verify SPEC-MVP-TEMPLATE references |
| Validation scripts | CHECK numbers reference sections | Verify CTR_MVP_VALIDATION_RULES.md |
| Autopilot workflows | Generate from YAML template | Update YAML template (Phase 4.5) |
| doc-ctr-reviewer | Check section completeness | Verify section check logic |
| doc-ctr-fixer | Fix phases reference sections | Verify section creation logic |
| Quality Gate validation | Corpus-level checks | Verify CTR_MVP_QUALITY_GATE_VALIDATION.md |

### 0.5 Decision: Target Section Count

**Analysis**:
- Current MD template: Mixed structure with PART markers and duplicate section numbers
- Validation Rules: 12 sections
- Schema: 12 sections (Title + 12 numbered)
- doc-ctr skill: 7 sections (WRONG)
- doc-ctr-validator: 20 sections in 5 Parts (INCONSISTENT)
- Quality Gate: 12 sections

**Decision**: Standardize to **12 numbered sections** (1-12) plus 2 optional lettered appendices (A, B) based on current template content analysis:

| Section | Title |
|---------|-------|
| 1 | Document Control |
| 2 | Context |
| 3 | Contract Definition |
| 4 | Requirements Satisfied |
| 5 | Interface Definition |
| 6 | Error Handling |
| 7 | Quality Attributes |
| 8 | Versioning Strategy |
| 9 | Examples |
| 10 | Verification |
| 11 | Traceability |
| 12 | References |
| Appendix A | Alternatives Considered |
| Appendix B | Implementation Notes |

**Rationale**:
- 12 numbered sections align with current template content (excluding PART markers)
- Appendices moved to lettered format per ADR/PRD conventions
- Template is primary source of truth
- Remove PART markers as they cause duplicate section numbers

---

## Phase 1: Critical Metadata Fixes

### 1.1 Fix Layer Tag in Validation Rules

**File**: `CTR_MVP_VALIDATION_RULES.md`

**Line 5**: Change `layer-9-artifact` to `layer-8-artifact`:
```yaml
# Before:
tags:
  - validation-rules
  - layer-9-artifact

# After:
tags:
  - validation-rules
  - layer-8-artifact
```

**Line 108**: Update required_tags:
```yaml
# Before:
required_tags:
  - ctr
  - layer-9-artifact

# After:
required_tags:
  - ctr
  - layer-8-artifact
```

### 1.2 Fix Layer Tag in Schema

**File**: `CTR_MVP_SCHEMA.yaml`

**Line 108** (in required_tags):
```yaml
# Before:
required_tags:
  - ctr
  - layer-9-artifact

# After:
required_tags:
  - ctr
  - layer-8-artifact
```

**Line 99** (in custom_fields validation - if present):
Ensure `layer: 8` is the only valid value.

---

## Phase 2: Template Structure Fixes

### 2.1 Target Section Structure

Restructure MD template to remove PART markers and fix duplicate section numbers:

**Current Problem Structure**:
```markdown
## 1. Document Control
## 2. PART 1: Contract Context and Requirements  ← REMOVE
## 2. Context                                     ← DUPLICATE #2
## 3. Contract Definition
## 4. Requirements Satisfied
## 5. PART 2: Interface Specification and Schema ← REMOVE
## 5. Interface Definition                       ← DUPLICATE #5
## 6. Error Handling
## 7. PART 3: Quality Attributes and Operations  ← REMOVE
## 7. Quality Attributes                         ← DUPLICATE #7
## 8. Versioning Strategy
## 9. Examples
## 10. PART 4: Testing and Traceability          ← REMOVE
## 10. Verification                              ← DUPLICATE #10
## 11. Traceability
## 12. References
## 13. Appendix A: Alternatives Considered       ← RENUMBER
## 14. Appendix B: Implementation Notes          ← RENUMBER
```

**Target Structure**:
```markdown
## 1. Document Control
## 2. Context
## 3. Contract Definition
## 4. Requirements Satisfied
## 5. Interface Definition
## 6. Error Handling
## 7. Quality Attributes
## 8. Versioning Strategy
## 9. Examples
## 10. Verification
## 11. Traceability
## 12. References
## Appendix A: Alternatives Considered
## Appendix B: Implementation Notes
```

### 2.2 Remove PART Markers

**File**: `CTR-MVP-TEMPLATE.md`

Delete the following lines entirely:
- Line ~65: `## 2. PART 1: Contract Context and Requirements`
- Line ~173: `## 5. PART 2: Interface Specification and Schema`
- Line ~238: `## 7. PART 3: Quality Attributes and Operations`
- Line ~354: `## 10. PART 4: Testing and Traceability`

### 2.3 Fix Duplicate Section Numbers

After removing PART markers, renumber sections sequentially:

| Line | Before | After |
|------|--------|-------|
| ~67 | `## 2. Context` | Keep as `## 2. Context` |
| ~112 | `## 3. Contract Definition` | Keep |
| ~136 | `## 4. Requirements Satisfied` | Keep |
| ~175 | `## 5. Interface Definition` | Keep (was duplicate after PART) |
| ~211 | `## 6. Error Handling` | Keep |
| ~240 | `## 7. Quality Attributes` | Keep (was duplicate after PART) |
| ~273 | `## 8. Versioning Strategy` | Keep |
| ~298 | `## 9. Examples` | Keep |
| ~356 | `## 10. Verification` | Keep (was duplicate after PART) |
| ~424 | `## 11. Traceability` | Keep |
| ~521 | `## 12. References` | Keep |
| ~559 | `## 13. Appendix A` | Change to `## Appendix A` |
| ~590 | `## 14. Appendix B` | Change to `## Appendix B` |

### 2.4 Convert Numbered Appendices to Lettered

**Before**:
```markdown
## 13. Appendix A: Alternatives Considered
## 14. Appendix B: Implementation Notes
```

**After**:
```markdown
## Appendix A: Alternatives Considered
## Appendix B: Implementation Notes
```

---

## Phase 3: Template Content Verification

### 3.1 Verify Document Control Table

Ensure Document Control table has all required fields:

| Item | Details |
|------|---------|
| **Project Name** | [Enter project name] |
| **Document Version** | [e.g., 1.0] |
| **Date** | YYYY-MM-DDTHH:MM:SS |
| **Document Owner** | [Name and title] |
| **Prepared By** | [API Designer/Architect name] |
| **Status** | Draft / In Review / Approved |
| **SPEC-Ready Score** | [Score]/100 (Target: ≥90/100) |

### 3.2 Update Frontmatter Metadata

Add `total_sections` and update `schema_version`:

```yaml
custom_fields:
  document_type: template
  artifact_type: CTR
  layer: 8
  template_variant: mvp
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  schema_version: "1.1"          # Updated from 1.0
  last_updated: "2026-02-26"     # Added
  total_sections: 12             # Added (Sections 1-12 + 2 Appendices)
```

### 3.3 Add Template Footer

Add document footer:

```markdown
---

**Document Version**: 1.0
**Template Version**: 1.1 (MVP - 12 sections + 2 appendices)
**Last Updated**: 2026-02-26
**Maintained By**: [Architecture Team]

---

> **MVP Template Notes**:
> - This is the standard CTR template (12 numbered sections + 2 appendices)
> - Dual-file format: .md + .yaml
> - Focus on API contracts, data schemas, interface specifications
> - Maintains ucx_flow_v3 framework compliance
> - **Lifecycle**: MVP → PROD → NEW MVP (no separate "full CTR" template)
```

---

## Phase 4: Update Supporting Documents

### 4.1 Update Validation Rules Section List

**File**: `CTR_MVP_VALIDATION_RULES.md`

Update Section 4 header and table:

```markdown
## 4. Section Structure Validation (12-Section Format + 2 Appendices)

### Required Sections (Markdown)

| Section | Required | Validation | Notes |
|---------|----------|------------|-------|
| 1. Document Control | Yes | Contract ID, version, status defined | - |
| 2. Context | Yes | Problem statement, background, constraints | - |
| 3. Contract Definition | Yes | Interface overview, parties, pattern | - |
| 4. Requirements Satisfied | Yes | Upstream requirements linked | - |
| 5. Interface Definition | Yes | At least one endpoint/schema | - |
| 6. Error Handling | Yes | Error codes documented | - |
| 7. Quality Attributes | Yes | Performance, security defined | - |
| 8. Versioning Strategy | Yes | Strategy documented | - |
| 9. Examples | Yes | At least one request/response | - |
| 10. Verification | Yes | Testing criteria defined | - |
| 11. Traceability | Yes | Valid tag format | - |
| 12. References | Yes | Internal/external links | - |

**Optional Appendices**: Appendix A (Alternatives Considered), Appendix B (Implementation Notes)
```

### 4.2 Update Schema Required Sections

**File**: `CTR_MVP_SCHEMA.yaml`

Update `required_sections` to match 12-section structure:

```yaml
structure:
  required_sections:
    - pattern: "^# CTR-\\d{2,}:"
      name: "Title (H1)"
      description: "Single H1 with format CTR-NN: Title"

    - pattern: "^## 1\\. Document Control$"
      name: "Document Control"
      description: "Section 1 with metadata table"

    - pattern: "^## 2\\. Context$"
      name: "Context"
      description: "Section 2 with Problem Statement, Background, Constraints"

    - pattern: "^## 3\\. Contract Definition$"
      name: "Contract Definition"
      description: "Section 3 with Interface Overview, Parties, Communication Pattern"

    - pattern: "^## 4\\. Requirements Satisfied$"
      name: "Requirements Satisfied"
      description: "Section 4 with upstream requirements links"

    - pattern: "^## 5\\. Interface Definition$"
      name: "Interface Definition"
      description: "Section 5 with Schema Reference, Endpoints"

    - pattern: "^## 6\\. Error Handling$"
      name: "Error Handling"
      description: "Section 6 with Error Codes, Failure Modes"

    - pattern: "^## 7\\. Quality Attributes$"
      name: "Quality Attributes"
      description: "Section 7 with Performance, Reliability, Security"

    - pattern: "^## 8\\. Versioning Strategy$"
      name: "Versioning Strategy"
      description: "Section 8 with Version Policy, Compatibility"

    - pattern: "^## 9\\. Examples$"
      name: "Examples"
      description: "Section 9 with Request/Response examples"

    - pattern: "^## 10\\. Verification$"
      name: "Verification"
      description: "Section 10 with Contract Testing, BDD Scenarios"

    - pattern: "^## 11\\. Traceability$"
      name: "Traceability"
      description: "Section 11 with Upstream Sources, Downstream Artifacts"

    - pattern: "^## 12\\. References$"
      name: "References"
      description: "Section 12 with Internal and External Links"

  optional_sections:
    - pattern: "^## Appendix A"
      name: "Appendix A: Alternatives Considered"
      description: "Optional - rejected alternative approaches"

    - pattern: "^## Appendix B"
      name: "Appendix B: Implementation Notes"
      description: "Optional - Development Phases, Code Locations"

  section_numbering:
    start: 1
    end: 12
    format: "## N. Section Title"
    subsection_format: "### N.N Subsection Title"
    no_duplicate_numbers: true
    appendices: ["Appendix A", "Appendix B"]
```

### 4.3 Update Creation Rules Section List

**File**: `CTR_MVP_CREATION_RULES.md`

Update Section 3 to specify 12-section structure:

```markdown
## 3. Required Sections (Markdown)

### 3.3 Mandatory Sections (12-Section Structure)

CTR documents follow a streamlined **12-section** MVP structure:

| # | Section | Purpose |
|---|---------|---------|
| 1 | Document Control | Contract metadata, status, version |
| 2 | Context | Business problem, constraints, trade-offs |
| 3 | Contract Definition | Format, naming conventions, parties |
| 4 | Requirements Satisfied | Upstream requirements this contract addresses |
| 5 | Interface Definition | Schema reference, endpoints, data models |
| 6 | Error Handling | Error codes and response formats |
| 7 | Quality Attributes | Performance, security, reliability |
| 8 | Versioning Strategy | Version policy, backwards compatibility |
| 9 | Examples | Request/response examples |
| 10 | Verification | Contract testing, BDD scenarios |
| 11 | Traceability | Upstream/downstream artifacts, tags |
| 12 | References | Internal/external links |

**Optional Appendices**:
- **Appendix A**: Alternatives Considered
- **Appendix B**: Implementation Notes
```

### 4.4 Update Quality Gate Validation

**File**: `CTR_MVP_QUALITY_GATE_VALIDATION.md`

Update section references and error codes:

```markdown
## Error Codes (Blocking)

| Code | Description | Check |
|------|-------------|-------|
| CORPUS-E001 | Placeholder text for existing document | CORPUS-01 |
| CORPUS-E002 | Premature downstream reference | CORPUS-02 |
| CORPUS-E004 | Duplicate contract ID | CORPUS-08 |
| CORPUS-E005 | File exceeds size limits | CORPUS-10 |
| CORPUS-E011 | Missing paired .yaml file | CORPUS-11 |
| CORPUS-E012 | Missing paired .md file | CORPUS-11 |
| CORPUS-E013 | Version mismatch between files | CORPUS-11 |
| CORPUS-E014 | Invalid YAML syntax | CORPUS-12 |
| CORPUS-E015 | Section structure not 1-12 | NEW |
```

### 4.5 Update README.md

**File**: `README.md`

Update section references throughout:

- Line ~746-747: Update "12-section structure" mentions to clarify "12 numbered sections + 2 optional appendices"
- Update any section number references

---

## Phase 4.6: Update YAML Template

**File**: `CTR-MVP-TEMPLATE.yaml`

The YAML template currently has a different structure. Sync with MD template (12 sections + 2 appendices):

### 4.6.1 Add Section Structure Metadata

```yaml
# Template metadata
schema_version: "1.1"
artifact_type: CTR
layer: 8
total_sections: 12
appendices: ["A", "B"]
last_updated: "2026-02-26"

sections:
  - number: 1
    title: "Document Control"
    required: true
    description: "Metadata with SPEC-Ready Score"
  - number: 2
    title: "Context"
    required: true
    subsections:
      - "2.1 Interface Problem Statement"
      - "2.2 Background"
      - "2.3 Driving Forces"
      - "2.4 Constraints"
      - "2.5 Trade-offs"
  - number: 3
    title: "Contract Definition"
    required: true
    subsections:
      - "3.1 Interface Overview"
      - "3.2 Parties"
      - "3.3 Communication Pattern"
  - number: 4
    title: "Requirements Satisfied"
    required: true
    subsections:
      - "4.1 Primary Requirements"
      - "4.2 Source Business Logic"
      - "4.3 Quality Attributes"
      - "4.4 Thresholds Referenced"
  - number: 5
    title: "Interface Definition"
    required: true
    subsections:
      - "5.1 Schema Reference"
      - "5.2 Endpoints / Functions / Messages"
  - number: 6
    title: "Error Handling"
    required: true
    subsections:
      - "6.1 Error Codes"
      - "6.2 Failure Modes & Recovery"
  - number: 7
    title: "Quality Attributes"
    required: true
    subsections:
      - "7.1 Performance Targets"
      - "7.2 Reliability Requirements"
      - "7.3 Security Requirements"
      - "7.4 Observability"
  - number: 8
    title: "Versioning Strategy"
    required: true
    subsections:
      - "8.1 Version Policy"
      - "8.2 Compatibility Rules"
      - "8.3 Deprecation Policy"
  - number: 9
    title: "Examples"
    required: true
    subsections:
      - "9.1 Success Response"
      - "9.2 Validation Failure"
      - "9.3 Error Response"
  - number: 10
    title: "Verification"
    required: true
    subsections:
      - "10.1 Contract Testing"
      - "10.2 BDD Scenarios"
      - "10.3 Specification Impact"
      - "10.4 Validation Criteria"
      - "10.5 Impact Analysis"
      - "10.6 Migration Strategy"
  - number: 11
    title: "Traceability"
    required: true
    subsections:
      - "11.1 Related Contracts"
      - "11.2 Upstream Sources"
      - "11.3 SPEC Requirements"
      - "11.4 Document Links"
      - "11.5 Same-Type References"
      - "11.6 Traceability Tags"
  - number: 12
    title: "References"
    required: true
    subsections:
      - "12.1 Internal Links"
      - "12.2 External Links"
      - "12.3 Additional Context"

appendices:
  - id: "A"
    title: "Alternatives Considered"
    required: false
  - id: "B"
    title: "Implementation Notes"
    required: false
```

---

## Phase 5: Update doc-ctr* Skills

### 5.1 Target Skill Files

| Skill | File Path | Update Scope |
|-------|-----------|--------------|
| doc-ctr | `.claude/skills/doc-ctr/SKILL.md` | Fix template references, section count (7→12) |
| doc-ctr-validator | `.claude/skills/doc-ctr-validator/SKILL.md` | **CRITICAL**: Fix "20 sections in 5 Parts" to "12 sections" |
| doc-ctr-reviewer | `.claude/skills/doc-ctr-reviewer/SKILL.md` | **HIGH**: Fix element type codes (28,29→16,17,20) |
| doc-ctr-fixer | `.claude/skills/doc-ctr-fixer/SKILL.md` | **HIGH**: Fix element type codes (28,29→16,17,20), regex patterns |
| doc-ctr-autopilot | `.claude/skills/doc-ctr-autopilot/SKILL.md` | Section references update |

### 5.2 doc-ctr/SKILL.md Fixes

**CRITICAL: Fix directory path** (throughout file):
```markdown
# Before:
ucx_flow_v3/08_CTR/

# After:
ucx_flow_v3/08_CTR/
```

**Lines 52-55**: Update template references:

```markdown
# Before:
2. **Template**: `ucx_flow_v3/08_CTR/CTR-TEMPLATE.md` and `CTR-TEMPLATE.yaml`
3. **Creation Rules**: `ucx_flow_v3/08_CTR/CTR_CREATION_RULES.md`
4. **Validation Rules**: `ucx_flow_v3/08_CTR/CTR_VALIDATION_RULES.md`

# After:
2. **Template**: `ucx_flow_v3/08_CTR/CTR-MVP-TEMPLATE.md` and `CTR-MVP-TEMPLATE.yaml`
3. **Creation Rules**: `ucx_flow_v3/08_CTR/CTR_MVP_CREATION_RULES.md`
4. **Validation Rules**: `ucx_flow_v3/08_CTR/CTR_MVP_VALIDATION_RULES.md`
```

**Lines 125-133**: Update section list to 12 sections:

```markdown
# Before:
**Core Sections**:
1. **Contract Overview**: Purpose, scope, version
2. **Business Context**: Why this contract exists (link to REQ)
3. **Contract Definition**: Reference to YAML file
4. **Usage Examples**: Request/response examples
5. **Validation Rules**: Schema validation, business rules
6. **Error Handling**: Error codes and responses
7. **Traceability**: Section 7 format with cumulative tags

# After:
**Required Sections (12 Sections)**:

| # | Section | Purpose |
|---|---------|---------|
| 1 | Document Control | Metadata, SPEC-Ready Score |
| 2 | Context | Problem statement, constraints, trade-offs |
| 3 | Contract Definition | Interface overview, parties, pattern |
| 4 | Requirements Satisfied | Upstream requirements linked |
| 5 | Interface Definition | Schema reference, endpoints |
| 6 | Error Handling | Error codes, failure modes |
| 7 | Quality Attributes | Performance, security, reliability |
| 8 | Versioning Strategy | Version policy, compatibility |
| 9 | Examples | Request/response pairs |
| 10 | Verification | Contract testing, BDD refs |
| 11 | Traceability | Upstream/downstream, tags |
| 12 | References | Internal/external links |

**Optional Appendices**:
- Appendix A: Alternatives Considered
- Appendix B: Implementation Notes
```

**Lines 751-754**: Update Related Resources:

```markdown
# Before:
- **Template**: `ucx_flow_v3/08_CTR/CTR-TEMPLATE.md` (primary authority)
- **Schema Template**: `ucx_flow_v3/08_CTR/CTR-TEMPLATE.yaml` (machine-readable)
- **CTR Creation Rules**: `ucx_flow_v3/08_CTR/CTR_CREATION_RULES.md`
- **CTR Validation Rules**: `ucx_flow_v3/08_CTR/CTR_VALIDATION_RULES.md`

# After:
- **Template**: `ucx_flow_v3/08_CTR/CTR-MVP-TEMPLATE.md` (primary authority)
- **Schema Template**: `ucx_flow_v3/08_CTR/CTR-MVP-TEMPLATE.yaml` (machine-readable)
- **CTR Creation Rules**: `ucx_flow_v3/08_CTR/CTR_MVP_CREATION_RULES.md`
- **CTR Validation Rules**: `ucx_flow_v3/08_CTR/CTR_MVP_VALIDATION_RULES.md`
- **CTR README**: `ucx_flow_v3/08_CTR/README.md`
```

### 5.3 doc-ctr-validator/SKILL.md Fixes (CRITICAL)

**Lines 119-151**: Replace "20 sections in 5 Parts" with 12-section structure:

```markdown
### 2. Structure Validation (12 Required Sections + 2 Optional Appendices)

**Required Sections (MVP Template)**:

| Section | Title | Required |
|---------|-------|----------|
| 1 | Document Control | MANDATORY |
| 2 | Context | MANDATORY |
| 3 | Contract Definition | MANDATORY |
| 4 | Requirements Satisfied | MANDATORY |
| 5 | Interface Definition | MANDATORY |
| 6 | Error Handling | MANDATORY |
| 7 | Quality Attributes | MANDATORY |
| 8 | Versioning Strategy | MANDATORY |
| 9 | Examples | MANDATORY |
| 10 | Verification | MANDATORY |
| 11 | Traceability | MANDATORY |
| 12 | References | MANDATORY |

**Optional Appendices**:
| Section | Title | Required |
|---------|-------|----------|
| Appendix A | Alternatives Considered | OPTIONAL |
| Appendix B | Implementation Notes | OPTIONAL |

**Document Control Required Fields:**
- Project Name
- Document Version
- Date
- Document Owner
- Prepared By
- Status
- SPEC-Ready Score
```

**Update Error Code CTR-E008**:

```markdown
# Before:
| CTR-E008 | error | Section numbering not sequential (1-20) |

# After:
| CTR-E008 | error | Section numbering not sequential (1-12) |
```

### 5.4 doc-ctr-reviewer/SKILL.md Fixes

**Line 110**: Verify "12/12" section reference is correct (it is):

```markdown
### 0. Structure Compliance (12/12) - BLOCKING
```

**Lines 257-258** (if present): Fix element type codes to match `ucx_flow_v3/ID_NAMING_STANDARDS.md`:

```markdown
# Before (INCORRECT):
| 28 | Contract Interface | API endpoints |
| 29 | Contract Event | Event definitions |

# After (CORRECT - per `ucx_flow_v3/ID_NAMING_STANDARDS.md`):
| 16 | Interface | API endpoints, service interfaces |
| 17 | Data Model | Schema definitions, data structures |
| 20 | Contract Clause | Contract terms, SLA definitions |
```

**Section structure references**: Ensure all references to section structure say "12 sections + 2 appendices".

---

### 5.5 doc-ctr-fixer/SKILL.md Fixes (CRITICAL)

**Lines 319-349**: Fix element type codes to match `ucx_flow_v3/ID_NAMING_STANDARDS.md`:

```markdown
# Before (INCORRECT):
| Invalid Code | Valid Code | Element Type |
|--------------|------------|--------------|
| 01 | 28 | Contract Interface |
| 02 | 29 | Contract Event |

**Valid CTR Type Codes**:
| Code | Element Type | Description |
|------|--------------|-------------|
| 28 | Contract Interface | API endpoints |
| 29 | Contract Event | Event definitions |

# After (CORRECT - per `ucx_flow_v3/ID_NAMING_STANDARDS.md`):
| Invalid Code | Valid Code | Element Type |
|--------------|------------|--------------|
| 28 | 16 | Interface |
| 29 | 17 | Data Model |
| Any API | 16 | Interface |
| Any Schema | 17 | Data Model |

**Valid CTR Type Codes**:
| Code | Element Type | Description |
|------|--------------|-------------|
| 16 | Interface | API endpoints, service interfaces |
| 17 | Data Model | Schema definitions, data structures |
| 20 | Contract Clause | Contract terms, SLA definitions |
```

**Update regex patterns** (line 343):

```python
# Before:
invalid_ctr_type = r'CTR\.(\d{2})\.(?!28|29)(\d{2})\.(\d{2})'

# After:
invalid_ctr_type = r'CTR\.(\d{2})\.(?!16|17|20)(\d{2})\.(\d{2})'
```

**Update legacy pattern conversions** (lines 320-323):

```markdown
# Before:
| `API-XXX` | Legacy pattern | `CTR.NN.28.SS` |
| `EVT-XXX` | Legacy pattern | `CTR.NN.29.SS` |
| `SCHEMA-XXX` | Legacy pattern | `CTR.NN.28.SS` |

# After:
| `API-XXX` | Legacy pattern | `CTR.NN.16.SS` |
| `INT-XXX` | Legacy pattern | `CTR.NN.16.SS` |
| `MODEL-XXX` | Legacy pattern | `CTR.NN.17.SS` |
| `SCHEMA-XXX` | Legacy pattern | `CTR.NN.17.SS` |
| `CLAUSE-XXX` | Legacy pattern | `CTR.NN.20.SS` |
```

---

### 5.6 doc-ctr-autopilot/SKILL.md Fixes

Update any references to section counts or PART structures.

---

## Phase 6: Minor Fixes and Metadata

### 6.1 Update Version Metadata in Template

Update YAML frontmatter in `CTR-MVP-TEMPLATE.md`:

```yaml
---
title: "CTR-TEMPLATE: Contract Specification"
tags:
  - ctr-template
  - layer-8-artifact
  - shared-architecture
  - document-template
custom_fields:
  document_type: template
  artifact_type: CTR
  layer: 8
  template_variant: mvp
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  complexity: 1
  template_for: contract-specification
  schema_reference: "CTR_MVP_SCHEMA.yaml"
  schema_version: "1.1"          # Updated from 1.0
  last_updated: "2026-02-26"     # Added
  total_sections: 12             # Added
---
```

---

## Phase 7: Testing & Validation

### 7.1 Template Validation

| Test | Command/Action | Expected Result |
|------|----------------|-----------------|
| Syntax check | Open in markdown viewer | Renders without errors |
| Section count | Count `## N.` headers | 12 numbered sections + 2 appendices |
| Duplicate check | Search for duplicate headers | 0 duplicates |
| PART markers | Search for `PART` | 0 occurrences |
| Frontmatter | Validate YAML | Single valid block |

### 7.2 Schema Validation

```bash
# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('CTR_MVP_SCHEMA.yaml').read())"

# Check for duplicates
grep -n "required_sections:" CTR_MVP_SCHEMA.yaml
# Expected: 1 occurrence
```

### 7.3 Skill Testing

| Skill | Test Action | Expected Result |
|-------|-------------|-----------------|
| doc-ctr | Create test CTR | 12-section CTR generated |
| doc-ctr-validator | Validate test CTR | Pass all checks |
| doc-ctr-autopilot | Generate CTR from YAML | Valid 12-section output |

### 7.4 YAML ↔ MD Template Sync Verification

**Purpose**: Ensure MD template and YAML template are aligned after changes.

| Check | MD Template | YAML Template | Expected |
|-------|-------------|---------------|----------|
| Total sections | Count `## N.` headers | Count `sections:` entries | 12 each |
| Section titles | Extract from headers | Extract from `title:` | Match exactly |
| Subsections | Count `### N.N` headers | Count `subsections:` | Match |
| Schema version | `custom_fields.schema_version` | `schema_version:` | Match |

**Verification Command**:
```bash
# Count sections in MD template
grep -c "^## [0-9]" CTR-MVP-TEMPLATE.md
# Expected: 12

# Count appendices
grep -c "^## Appendix" CTR-MVP-TEMPLATE.md
# Expected: 2

# Verify no PART markers
grep "PART [0-9]" CTR-MVP-TEMPLATE.md
# Expected: 0 matches
```

---

## Execution Order

| Step | Phase | Action | Dependencies |
|------|-------|--------|--------------|
| 1 | 0 | Create backups | None |
| 2 | 1.1 | Fix layer tag in Validation Rules | Backup complete |
| 3 | 1.2 | Fix layer tag in Schema | Step 2 |
| 4 | 2.2 | Remove PART markers from template | Step 3 |
| 5 | 2.3 | Fix duplicate section numbers | Step 4 |
| 6 | 2.4 | Convert numbered appendices to lettered | Step 5 |
| 7 | 3 | Verify template content, add footer/metadata | Step 6 |
| 8 | 4.1 | Update Validation Rules (12 sections) | Step 7 |
| 9 | 4.2 | Update Schema (align to template) | Step 8 |
| 10 | 4.3 | Update Creation Rules | Step 9 |
| 11 | 4.4 | Update Quality Gate | Step 10 |
| 12 | 4.5 | Update README.md | Step 11 |
| 13 | 4.6 | Update YAML template | Step 12 |
| 14 | 5 | Update all skills (5 files) | Step 13 |
| 15 | 6 | Update version metadata | Step 14 |
| 16 | 7 | Run all tests | Step 15 |

---

## Verification Checklist

### Template Verification
- [ ] Single YAML frontmatter block at top
- [ ] No PART markers (`## N. PART X:`)
- [ ] 12 numbered sections exist (1-12)
- [ ] No duplicate section numbers
- [ ] 2 lettered appendices (Appendix A, Appendix B)
- [ ] Section 2 is Context (not PART 1)
- [ ] Section 5 is Interface Definition (not PART 2)
- [ ] Section 7 is Quality Attributes (not PART 3)
- [ ] Section 10 is Verification (not PART 4)
- [ ] Section 11 has Traceability with cumulative tags
- [ ] Version metadata updated (schema_version: 1.1, total_sections: 12)

### Validation Rules Verification
- [ ] Layer tag is `layer-8-artifact` (not layer-9)
- [ ] Section structure specifies 12 sections
- [ ] Error code CTR-E008 references "1-12" (not "1-20")
- [ ] No duplicate frontmatter blocks

### Creation Rules Verification
- [ ] Section structure matches template (12 sections)
- [ ] Appendices listed as lettered (A, B) not numbered (13, 14)

### Schema Verification
- [ ] required_sections has 13 entries (Title + 12 sections)
- [ ] optional_sections has 2 entries (Appendix A, B)
- [ ] Layer tag is `layer-8-artifact`
- [ ] section_numbering.end: 12

### YAML Template Verification
- [ ] Section structure matches MD template
- [ ] All 12 sections defined with subsections
- [ ] Appendices A and B defined
- [ ] Metadata updated (total_sections: 12)

### Skill Files Verification
- [ ] doc-ctr/SKILL.md uses `ucx_flow_v3/08_CTR/` path (not `ucx_flow_v3/08_CTR/`)
- [ ] doc-ctr/SKILL.md references CTR-MVP-TEMPLATE.md (not CTR-TEMPLATE.md)
- [ ] doc-ctr/SKILL.md lists 12 sections
- [ ] doc-ctr-validator/SKILL.md says "12 sections" (not "20 sections in 5 Parts")
- [ ] doc-ctr-validator/SKILL.md error code CTR-E008 references "1-12"
- [ ] doc-ctr-autopilot/SKILL.md section references updated
- [ ] All skills reference Layer 8 (not Layer 9)
- [ ] doc-ctr-reviewer/SKILL.md uses correct element type codes (16, 17, 20)
- [ ] doc-ctr-fixer/SKILL.md uses correct element type codes (16, 17, 20)
- [ ] All skills align with `/opt/data/docs_flow_framework/ucx_flow_v3/ID_NAMING_STANDARDS.md` for type codes

### README Verification
- [ ] Section references updated to 12 sections
- [ ] Layer 8 references consistent

### Quality Gate Verification
- [ ] Section references updated
- [ ] CORPUS-11 check references correct sections

---

## Estimated Changes

| Metric | Count |
|--------|-------|
| MD Template lines removed | ~15 (PART markers + duplicates) |
| MD Template lines modified | ~20 (appendix renumbering, metadata) |
| Validation Rules fixes | ~40 lines modified |
| Creation Rules fixes | ~30 lines modified |
| Schema fixes | ~60 lines modified |
| YAML Template updates | ~100 lines |
| README updates | ~20 lines |
| Quality Gate updates | ~15 lines |
| Skill files to update | 5 |
| Total sections after fix | 12 + 2 appendices |

---

## Migration Guide for Existing CTRs

### Migration Steps

1. **Remove PART markers**: Delete any `## N. PART X:` headers
2. **Fix duplicate sections**: Ensure no duplicate section numbers
3. **Renumber appendices**: Change `## 13. Appendix A` to `## Appendix A`
4. **Verify section structure**: Ensure Sections 1-12 exist with correct titles
5. **Update traceability**: Ensure Section 11 has cumulative tags (@brd through @req)
6. **Validate**: Run `doc-ctr-validator` on updated document

### Canonical Section Structure (Reference)

| Section | Title |
|---------|-------|
| 1 | Document Control |
| 2 | Context |
| 3 | Contract Definition |
| 4 | Requirements Satisfied |
| 5 | Interface Definition |
| 6 | Error Handling |
| 7 | Quality Attributes |
| 8 | Versioning Strategy |
| 9 | Examples |
| 10 | Verification |
| 11 | Traceability |
| 12 | References |
| Appendix A | Alternatives Considered |
| Appendix B | Implementation Notes |

---

## Related Files to Update (Post-Implementation)

After fixing the template and skills, verify these files:

| File | Update Needed | Priority |
|------|---------------|----------|
| `SPEC-MVP-TEMPLATE.md` | CTR section references | P3 |
| Existing CTR documents | Migration to new structure | P3 |
| Example CTR files | Update to 12-section structure | P3 |

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.3 | 2026-02-26 | Added gap #22 (wrong directory path `ucx_flow_v3` → `ucx_flow_v3`); Fixed all path references in Phase 5.2; Added path verification to checklist |
| 1.2 | 2026-02-26 | Updated all ID_NAMING_STANDARDS.md references to use full path (`ucx_flow_v3/ID_NAMING_STANDARDS.md`) |
| 1.1 | 2026-02-26 | Gap review update: Fixed section count inconsistency (14→12); Added gaps #18-21 for element type codes; Added detailed fixes for doc-ctr-reviewer (5.4) and doc-ctr-fixer (5.5); Added Element Type Code Reference section; Updated verification checklist for type codes |
| 1.0 | 2026-02-26 | Initial fix plan with 17 identified gaps |

---

**End of Plan**
