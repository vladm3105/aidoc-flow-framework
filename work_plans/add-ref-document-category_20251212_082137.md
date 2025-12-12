# Implementation Plan - Add REFERENCE (REF) Document Category

**Created**: 2025-12-12 08:21:37 EST
**Status**: Ready for Implementation

## Objective

Add a new **REFERENCE (REF)** document category to the SDD framework for supplementary documentation that doesn't participate in the formal traceability chain.

**Format**: `{TYPE}-REF-NNN_{slug}.md` (e.g., `BRD-REF-001_project_overview.md`)

## Context

### Key Requirements (from user discussion)

| Aspect | Specification |
|--------|---------------|
| **Naming** | `{TYPE}-REF-NNN_{slug}.md` |
| **Numbering** | Independent per TYPE (BRD-REF-001, PRD-REF-001, etc.) |
| **Mandatory Sections** | 4 only: Metadata, Document Control, Revision History, Introduction |
| **Traceability** | Optional (encouraged but not required) |
| **Validation** | Minimal (non-blocking) |
| **Similar to** | `{TYPE}-000` documents (both exempted from full validation) |

### Use Cases
- General project descriptions from business perspective
- Infrastructure requirements
- Strategic vision descriptions
- Dictionary/reference material

### User Decisions
- REF Numbering: Independent per TYPE (each TYPE has its own REF sequence)
- Template: Shared REF-TEMPLATE.md in central location
- Traceability: Encouraged but not required (include simplified optional section)

## Task List

### Pending

- [ ] Step 1: Create REF-TEMPLATE.md (HIGH priority)
- [ ] Step 2: Update ID_NAMING_STANDARDS.md (HIGH priority)
- [ ] Step 3: Update validation scripts (HIGH priority)
- [ ] Step 4: Create doc-ref skill (HIGH priority)
- [ ] Step 5: Update doc-flow/SKILL.md (MEDIUM priority)
- [ ] Step 6: Update doc-validator/SKILL.md (MEDIUM priority)
- [ ] Step 7: Update all 12 doc-{type} skills (LOW priority)
- [ ] Step 8: Update SPEC_DRIVEN_DEVELOPMENT_GUIDE.md (LOW priority)

## Implementation Guide

### Prerequisites

- Access to `/opt/data/docs_flow_framework/` directory
- Understanding of SDD framework structure
- Familiarity with YAML frontmatter format

### Execution Steps

#### Step 1: Create REF-TEMPLATE.md

**Location**: `/opt/data/docs_flow_framework/ai_dev_flow/REF-TEMPLATE.md`

Template with 4 mandatory sections:
1. YAML frontmatter (metadata)
2. Document Control table
3. Document Revision History table
4. Introduction section
5. [Optional] Related Documents section

#### Step 2: Update ID_NAMING_STANDARDS.md

**File**: `/opt/data/docs_flow_framework/ai_dev_flow/ID_NAMING_STANDARDS.md`

Add after line 41 (Scope section):
```markdown
  - `REF/` - Reference Documents (supplementary, non-workflow documentation)
```

Add new section (after line 221):
```markdown
- Reference Documents (REF)
  - H1 ID: `{TYPE}-REF-NNN` (e.g., `# BRD-REF-001: Project Overview`)
  - Filename: `{TYPE}-REF-NNN_{slug}.md`
  - Numbering: Independent sequence per parent TYPE
  - Traceability: Optional
  - Use cases: Project overviews, infrastructure requirements, strategic vision, dictionaries
```

Add regex (after line 310):
```
  - REF H1 ID: `^#\s+[A-Z]{2,5}-REF-\d{3,4}:.+$`
  - REF filename: `[A-Z]{2,5}-REF-\d{3,4}_.+\.md$`
```

#### Step 3: Update Validation Scripts

**validate_artifact.py** (`/opt/data/docs_flow_framework/ai_dev_flow/scripts/validate_artifact.py`):
- Add to ARTIFACT_PATTERNS: `"REF": r"^[A-Z]{2,5}-REF-\d{3}"`

**validate_requirement_ids.py** (`/opt/data/docs_flow_framework/ai_dev_flow/scripts/validate_requirement_ids.py`):
- Add exemption: `if "-REF-" in req_file.name: continue`

#### Step 4: Create doc-ref Skill

**Location**: `/opt/data/docs_flow_framework/.claude/skills/doc-ref/SKILL.md`

Skill for creating REF documents with:
- Purpose and when to use
- Naming convention documentation
- Minimal validation rules
- Creation process

#### Step 5: Update doc-flow/SKILL.md

**File**: `/opt/data/docs_flow_framework/.claude/skills/doc-flow/SKILL.md`

- Add REF to `downstream_artifacts` in frontmatter
- Add REF to skill selection decision tree
- Add REF row to layer descriptions table

#### Step 6: Update doc-validator/SKILL.md

**File**: `/opt/data/docs_flow_framework/.claude/skills/doc-validator/SKILL.md`

Add REF validation rules:
- Minimal validation (non-blocking)
- Required: Document Control, Revision History, Introduction, H1 ID match
- Exempted: Cumulative tags, traceability, quality gates

#### Step 7: Update All 12 doc-{type} Skills

Add to each skill's SKILL.md:
```markdown
## Reference Documents

For supplementary documentation related to {TYPE} artifacts:
- Format: `{TYPE}-REF-NNN_{slug}.md`
- Use `doc-ref` skill
- Minimal validation (non-blocking)
```

**Files**:
- `/opt/data/docs_flow_framework/.claude/skills/doc-brd/SKILL.md`
- `/opt/data/docs_flow_framework/.claude/skills/doc-prd/SKILL.md`
- `/opt/data/docs_flow_framework/.claude/skills/doc-ears/SKILL.md`
- `/opt/data/docs_flow_framework/.claude/skills/doc-bdd/SKILL.md`
- `/opt/data/docs_flow_framework/.claude/skills/doc-adr/SKILL.md`
- `/opt/data/docs_flow_framework/.claude/skills/doc-sys/SKILL.md`
- `/opt/data/docs_flow_framework/.claude/skills/doc-req/SKILL.md`
- `/opt/data/docs_flow_framework/.claude/skills/doc-impl/SKILL.md`
- `/opt/data/docs_flow_framework/.claude/skills/doc-ctr/SKILL.md`
- `/opt/data/docs_flow_framework/.claude/skills/doc-spec/SKILL.md`
- `/opt/data/docs_flow_framework/.claude/skills/doc-tasks/SKILL.md`
- `/opt/data/docs_flow_framework/.claude/skills/doc-iplan/SKILL.md`

#### Step 8: Update SPEC_DRIVEN_DEVELOPMENT_GUIDE.md

**File**: `/opt/data/docs_flow_framework/ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md`

Add section documenting:
- REF document purpose
- Naming convention
- Use cases
- Template location

### Verification

After implementation, verify:
- [ ] REF-TEMPLATE.md exists with 4 mandatory sections
- [ ] `{TYPE}-REF-NNN` pattern validates correctly
- [ ] REF documents skip traceability validation
- [ ] doc-ref skill accessible via Skill tool
- [ ] All 14 doc-* skills reference REF documents

## References

### Related Files
- `/opt/data/docs_flow_framework/ai_dev_flow/ID_NAMING_STANDARDS.md` - Core naming standards
- `/opt/data/docs_flow_framework/ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md` - Main SDD guide
- `/opt/data/docs_flow_framework/.claude/skills/doc-flow/SKILL.md` - Workflow orchestrator

### Documentation
- Plan file: `/home/ya/.claude/plans/jiggly-brewing-grove.md`
- Work plans directory: `/opt/data/docs_flow_framework/work_plans/`
