# Implementation Plan - Fix Documentation Inconsistencies

**Created**: 2025-11-14 07:06:16 EST
**Status**: Ready for Implementation
**Plan Type**: Documentation Quality Assurance

## Objective

Correct all identified documentation reference errors, path inconsistencies, and terminology issues across the docs_flow_framework repository to ensure consistent 16-layer architecture documentation and accurate file references.

## Context

### Analysis Summary

Comprehensive documentation review completed on 2025-11-14 identified **11 categories of issues** across 100+ files in the docs_flow_framework repository:

- **1 High Priority Issue**: Architecture layer terminology confusion (10-layer vs 16-layer references)
- **4 Medium Priority Issues**: Obsolete path references, documentation clarity, broken links, multi-project guide corrections
- **6 Low Priority Issues**: Legacy naming conventions, file extensions, minor inconsistencies

### Key Findings

1. **Architecture Terminology Confusion**: Multiple files still reference "10-layer architecture" when framework is v2.0 with 16-layer architecture (13 documentation artifacts + 3 execution layers)

2. **Obsolete Path References**: 16 files reference non-existent `docs_templates/` directory path that should be `ai_dev_flow/`

3. **Multi-Project Setup Guide**: Misleading Quick Start section suggesting setup script creates docs/ folders when it only creates symlinks

4. **Template Extension Inconsistencies**: References to "BDD-TEMPLATE.md" when actual file is "BDD-TEMPLATE.feature"

### Important Constraints

- Must maintain accuracy of Phase 3 completion claims (verified as accurate)
- Must not alter working validation scripts or tooling
- Must preserve historical migration notes (CONTRACTS → CTR, TASKS_PLANS → IPLAN)
- All paths must be verified before changes
- Documentation must remain under 100,000 token limit per file

## Task List

### Completed ✅

- [x] Comprehensive documentation analysis
- [x] Cross-reference validation
- [x] Naming convention consistency check
- [x] Template reference validation
- [x] Identification and categorization of all inconsistencies

### Pending Implementation

- [ ] **Phase 1**: Fix architecture layer terminology (High Priority)
  - [ ] Update ai_dev_flow/PROJECT_SETUP_GUIDE.md (3 locations)
  - [ ] Update ai_dev_flow/AI_ASSISTANT_RULES.md
  - [ ] Update .claude/skills/project-init/SKILL.md

- [ ] **Phase 2**: Correct obsolete path references (Medium Priority)
  - [ ] Run automated search-replace for docs_templates/ references
  - [ ] Verify all 16 affected files updated correctly
  - [ ] Validate no broken references introduced

- [ ] **Phase 3**: Update multi-project setup guide (Medium Priority)
  - [ ] Clarify MULTI_PROJECT_SETUP_GUIDE.md Quick Start section
  - [ ] Document setup script vs project-init skill responsibilities

- [ ] **Phase 4**: Template reference corrections (Low Priority)
  - [ ] Update BDD-TEMPLATE.md → BDD-TEMPLATE.feature references

- [ ] **Phase 5**: Script path standardization (Low Priority)
  - [ ] Standardize all script references to repository root-relative paths

- [ ] **Phase 6**: Validation and verification
  - [ ] Run markdown link checker
  - [ ] Verify template file existence
  - [ ] Validate @tag format consistency
  - [ ] Confirm layer numbering alignment

## Implementation Guide

### Prerequisites

**Required Access**:

- Write access to `/opt/data/docs_flow_framework/`
- Git repository in clean state (verified: modified files in .claude/skills/ and guides)

**Required Tools**:

- sed (for automated search-replace)
- find (for file traversal)
- markdown link checker (optional but recommended)
- git (for version control)

**Backup Strategy**:

- Create git commit before each phase
- Use git branches for each major change category
- Maintain rollback capability

### Execution Steps

#### Phase 1: Architecture Terminology Fixes (High Priority)

**File 1**: `ai_dev_flow/PROJECT_SETUP_GUIDE.md`

```bash
# Line 82: Update layer count
OLD: "Core 10-layer directory structure (ALL PROJECTS)"
NEW: "Core 16-layer architecture (13 documentation artifacts + 3 execution layers)"

# Line 103: Update directory verification
OLD: "Verify 11 directories created"
NEW: "Verify 13 artifact directories created (BRD through IPLAN)"

# Line 232: Clarify workflow description
ADD CLARIFICATION: "16-layer architecture: BRD → PRD → EARS → BDD → ADR → SYS → REQ → [IMPL] → [CTR] → SPEC → TASKS → IPLAN → Code → Tests → Deployment (brackets indicate optional layers)"
```

**File 2**: `ai_dev_flow/AI_ASSISTANT_RULES.md`

```bash
# Replace all instances
SEARCH: "10-layer workflow"
REPLACE: "16-layer architecture"
```

**File 3**: `.claude/skills/project-init/SKILL.md`

```bash
# Line 37
OLD: "Follow 10-layer workflow"
NEW: "Follow 16-layer architecture (13 documentation artifacts + 3 execution layers)"
```

**Verification Phase 1**:

```bash
# Confirm no remaining "10-layer" references
grep -r "10-layer" --include="*.md" ai_dev_flow/ .claude/
# Should return: no results (or only historical notes clearly marked)
```

#### Phase 2: Path Reference Corrections (Medium Priority)

**Automated Search-Replace**:

```bash
# Navigate to repository root
cd /opt/data/docs_flow_framework/

# Pattern 1: ai_dev_flow → ai_dev_flow
find . -name "*.md" -type f -exec sed -i 's|ai_dev_flow|ai_dev_flow|g' {} +

# Pattern 2: /ai_dev_flow → /ai_dev_flow
find . -name "*.md" -type f -exec sed -i 's|/ai_dev_flow|/ai_dev_flow|g' {} +

# Pattern 3: docs_templates/ (standalone) → ai_dev_flow/
find . -name "*.md" -type f -exec sed -i 's|docs_templates/|ai_dev_flow/|g' {} +
```

**Affected Files** (16 total):

1. `.claude/skills/project-init/SKILL.md`
2. `ai_dev_flow/PROJECT_SETUP_GUIDE.md`
3. `ai_dev_flow/AI_ASSISTANT_RULES.md`
4. `ai_dev_flow/README.md`
5. `ai_dev_flow/IMPL/README.md`
6. `ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md`
7. `ai_dev_flow/TRACEABILITY.md`
8. `ai_dev_flow/SPEC/SPEC-TEMPLATE.yaml`
9. `ai_dev_flow/DOMAIN_ADAPTATION_GUIDE.md`
10. `ai_dev_flow/TASKS/TASKS-000_index.md`
11. `ai_dev_flow/CONTRACT_DECISION_QUESTIONNAIRE.md`
12. `ai_dev_flow/QUICK_REFERENCE.md`
13. `ai_dev_flow/IMPL/IMPL-000_index.md`
14. `ai_dev_flow/scripts/make_framework_generic.py`
15. `.clinerules/doc-flow.md`
16. `work_plans/align-skills-with-framework_20251113_165924.md`

**Verification Phase 2**:

```bash
# Confirm no remaining docs_templates/ references
grep -r "docs_templates" --include="*.md" --include="*.py" --include="*.yaml"
# Should return: no results

# Verify ai_dev_flow/ paths are correct
ls -la /opt/data/docs_flow_framework/ai_dev_flow/
# Should show: directories exist, no docs_templates/ subdirectory
```

#### Phase 3: Multi-Project Setup Guide Clarification

**File**: `MULTI_PROJECT_SETUP_GUIDE.md`

**Changes Required**:

```markdown
# Lines 23-26 (Quick Start section)
CURRENT:
```bash
# ✓ Creates .claude/custom_skills/, custom_commands/, custom_agents/
# ✓ Symlinks .claude/skills/ → framework
```

UPDATE TO:

```bash
# ✓ Creates .claude/custom_skills/, custom_commands/, custom_agents/
# ✓ Symlinks .claude/skills/ → framework
# ⚠ Does NOT create docs/ or work_plans/ (use `/skill project-init` for full structure)
```

ADD NEW SECTION (after line 60):

```markdown
### Setup Script vs Project-Init Skill

**`setup_project_hybrid.sh`** (Lightweight):
- Creates `.claude/` directory structure
- Creates symlinks to framework skills/agents/commands
- Ideal for: Adding framework to existing projects

**`/skill project-init`** (Full Structure):
- Creates complete documentation structure (docs/)
- Creates work_plans/ directory
- Initializes all 13 artifact directories
- Ideal for: Starting new projects from scratch
```

**Verification Phase 3**:

```bash
# Read updated guide
cat MULTI_PROJECT_SETUP_GUIDE.md | grep -A 5 "Setup Script vs Project-Init Skill"
# Should show: new clarification section
```

#### Phase 4: Template Extension Corrections

**Search Pattern**:

```bash
# Find all references to BDD-TEMPLATE.md
grep -r "BDD-TEMPLATE\.md" --include="*.md"
```

**Replace With**: `BDD-TEMPLATE.feature`

**Manual Verification**:

```bash
# Confirm actual template file
ls -la ai_dev_flow/BDD/BDD-TEMPLATE.feature
# Should exist

ls -la ai_dev_flow/BDD/BDD-TEMPLATE.md
# Should NOT exist
```

#### Phase 5: Script Path Standardization

**Standardization Rule**:
All script references use repository root-relative paths:

```bash
# Standard format
python ai_dev_flow/scripts/script_name.py

# NOT
python scripts/script_name.py  # (ambiguous - depends on pwd)
```

**Files to Update**:

- README.md
- ai_dev_flow/README.md
- Any other files with script references

**Search Command**:

```bash
grep -r "python scripts/" --include="*.md"
grep -r "python3 scripts/" --include="*.md"
```

#### Phase 6: Validation and Verification

**1. Verify Template Files Exist**:

```bash
# Check all referenced templates
ls -la ai_dev_flow/*/\*-TEMPLATE.*

# Expected files:
# - ADR-TEMPLATE.md
# - BDD-TEMPLATE.feature (NOT .md)
# - BRD-TEMPLATE.md
# - CTR-000_TRACEABILITY_MATRIX-TEMPLATE.md
# - EARS-TEMPLATE.md
# - IMPL-TEMPLATE.md
# - IPLAN-000_TRACEABILITY_MATRIX-TEMPLATE.md
# - PRD-TEMPLATE.md
# - REQ-TEMPLATE.md
# - SPEC-TEMPLATE.yaml (NOT .md)
# - SYS-TEMPLATE.md
# - TASKS-TEMPLATE.md
# - TRACEABILITY_MATRIX_COMPLETE-TEMPLATE.md
```

**2. Check @tag Format Consistency**:

```bash
# Extract all @tags and verify format
grep -rh '@[a-z-]*:' --include="*.md" --include="*.py" --include="*.yaml" | sort -u

# Expected patterns:
# @adr: ADR-NNN
# @bdd: BDD-NNN
# @brd: BRD-NNN
# @ctr: CTR-NNN
# @ears: EARS-NNN
# @impl: IMPL-NNN
# @iplan: IPLAN-NNN
# @prd: PRD-NNN
# @req: REQ-NNN
# @spec: SPEC-NNN
# @sys: SYS-NNN
# @tasks: TASKS-NNN
# @impl-status: [complete|in-progress|blocked]
```

**3. Verify Layer Numbering**:

```bash
# Check TRACEABILITY.md for correct layer definitions
grep "Layer [0-9]" ai_dev_flow/TRACEABILITY.md

# Should show layers 0-15 correctly defined
```

**4. Markdown Link Validation** (Optional):

```bash
# Install markdown link checker if not present
npm install -g markdown-link-check

# Run on all markdown files
find . -name "*.md" -exec markdown-link-check {} \;
```

**5. Git Status Check**:

```bash
# Review all changes
git status
git diff

# Expected: ~25-30 files modified
```

### Verification Checklist

After each phase, verify:

**Phase 1 Verification**:

- [ ] No remaining "10-layer" references (except historical notes)
- [ ] All files correctly reference "16-layer architecture"
- [ ] Layer count descriptions include "(13 documentation artifacts + 3 execution layers)"

**Phase 2 Verification**:

- [ ] No remaining `docs_templates/` path references
- [ ] All paths reference `ai_dev_flow/` correctly
- [ ] No broken file references introduced

**Phase 3 Verification**:

- [ ] MULTI_PROJECT_SETUP_GUIDE.md clearly distinguishes setup script vs project-init
- [ ] Quick Start section no longer misleading
- [ ] New clarification section present and accurate

**Phase 4 Verification**:

- [ ] All BDD template references use `.feature` extension
- [ ] No references to non-existent `BDD-TEMPLATE.md`

**Phase 5 Verification**:

- [ ] All script paths use repository root-relative format
- [ ] No ambiguous `python scripts/` references remain

**Phase 6 Verification**:

- [ ] All referenced template files exist
- [ ] @tag formats consistent across framework
- [ ] Layer numbering (0-15) correctly documented
- [ ] No broken markdown links

## Implementation Complexity

**Overall Complexity**: 2/5 (Straightforward search-replace with verification)

**Resource Requirements**:

- CPU: Minimal (sed operations)
- Memory: < 100MB (file processing)
- Storage: No change (in-place updates)
- Time: 30-60 minutes for all phases

**Risk Assessment**:

- **Low Risk**: Primarily documentation changes
- **Failure Modes**:
  - Incorrect regex patterns breaking valid references
  - Over-broad search-replace affecting unintended files
  - Git merge conflicts if concurrent changes
- **Mitigation**: Phase-by-phase commits, verification after each phase

## References

### Related Files (Critical)

- `/opt/data/docs_flow_framework/ai_dev_flow/ID_NAMING_STANDARDS.md` - Naming conventions
- `/opt/data/docs_flow_framework/ai_dev_flow/TRACEABILITY.md` - Layer definitions
- `/opt/data/docs_flow_framework/README.md` - Framework overview
- `/opt/data/docs_flow_framework/MULTI_PROJECT_SETUP_GUIDE.md` - Setup documentation

### Analysis Report

- **Source**: Plan agent comprehensive analysis (2025-11-14)
- **Files Analyzed**: 100+
- **Issues Identified**: 11 categories
- **Priority Distribution**: 1 High, 4 Medium, 6 Low

### Previous Work

- Git commit 75267af: "Add IPLAN naming convention validator script"
- Git commit 8f0b5e2: "Update README.md to reflect v2.0 with cumulative tagging hierarchy"
- Git commit 7bc3560: "Phase 3 complete - Add cumulative tagging sections to all remaining matrix templates"

## Execution Order

1. **Phase 1** (High Priority): Architecture terminology - Complete first
2. **Phase 2** (Medium Priority): Path references - Automated, verify carefully
3. **Phase 3** (Medium Priority): Multi-project guide - Manual edit
4. **Phase 4** (Low Priority): Template extensions - Quick fix
5. **Phase 5** (Low Priority): Script paths - Standardization
6. **Phase 6** (Validation): Run all verification checks

## Success Criteria

✅ **Complete when**:

- All "10-layer" references updated to "16-layer architecture"
- All `docs_templates/` paths corrected to `ai_dev_flow/`
- MULTI_PROJECT_SETUP_GUIDE.md accurately describes script vs skill responsibilities
- All template references use correct file extensions
- All script paths standardized to repository root-relative format
- All verification checks pass
- Git repository shows clean diff with expected changes only

## Notes

- **Historical References**: CONTRACTS → CTR and TASKS_PLANS → IPLAN migration notes should be preserved as they document evolution
- **Phase 3 Status**: Analysis confirmed Phase 3 completion claims are accurate - no changes needed
- **Validation Scripts**: All existing validation scripts (extract_tags.py, etc.) remain functional - no modifications needed
- **Token Limits**: All documentation files remain under 100,000 token limit after changes
- **Git Strategy**: Commit after each phase for granular rollback capability

---

**Last Updated**: 2025-11-14 07:06:16 EST
**Repository**: /opt/data/docs_flow_framework/
**Git Branch**: main
**Total Files to Modify**: ~25-30 files
