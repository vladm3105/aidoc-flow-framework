# Implementation Plan - Framework Consistency Audit Remediation

**Created**: 2025-12-01 19:21:47 EST
**Status**: COMPLETED
**Completed**: 2025-12-01 19:30 EST
**Source Plan**: `/home/ya/.claude/plans/vectorized-purring-avalanche.md`

## Objective

Fix all inconsistencies, errors, and issues identified during the comprehensive audit of the docs_flow_framework following significant changes (cross-document validation system implementation). **47 distinct issues** across 8 categories require remediation.

## Context

### Audit Summary
Three parallel Explore agents audited the entire framework and identified:

| Category | Issue Count | Severity | Files Affected |
|----------|-------------|----------|----------------|
| **1. Corrupted/Garbled Text** | 1 | HIGH | 1 file |
| **2. Placeholder Text Not Replaced** | 99 occurrences | MEDIUM | 16 files |
| **3. Metadata Inconsistencies** | 7 | MEDIUM-HIGH | 7 files |
| **4. Section Numbering Gaps** | 4 files | HIGH | 4 files |
| **5. Missing Table of Contents** | 5 files | HIGH | 5 files |
| **6. Missing YAML Frontmatter** | 2 files | MEDIUM | 2 files |
| **7. Layer Conflict (ICON/TASKS)** | 1 | MEDIUM | 2 files |
| **8. TODO/TBD Items** | 72 files | LOW | 72 files |

### User Decisions
1. **Placeholders**: Replace with context-appropriate generic text, review carefully, add notes where needed
2. **Layer conflict**: Assign ICON Layer 11.5 (between TASKS 11 and IPLAN 12), ICON is optional for small projects
3. **Section numbering**: Renumber continuously (no gaps)

## Task List

### Completed
- [x] Framework audit completed
- [x] Plan approved by user
- [x] Fix corrupted text in PROJECT_SETUP_GUIDE.md (already fixed - verified correct)
- [x] Remove duplicate custom_fields in BDD_CREATION_RULES.md (not duplicates - were code examples)
- [x] Fix section numbering in CTR_CREATION_RULES.md (already correct - sections 1-10 continuous)
- [x] Fix section numbering in IMPL_CREATION_RULES.md (fixed: ## 10 → 13, ## 11 → 14, updated ToC)
- [x] Fix section numbering in IPLAN_CREATION_RULES.md (already correct - sections 1-16 continuous)
- [x] Fix section numbering in TASKS_CREATION_RULES.md (already correct - sections 1-14)
- [x] Add ToC to 5 CREATION_RULES files (all already have ToC - updated IMPL ToC)
- [x] Fix document_type metadata in 5 files (all already have `creation-rules` format)
- [x] Add YAML frontmatter to 2 BDD files (already present in both)
- [x] Update ICON layer to 11.5 (already 11.5, fixed "## N." → "## 10.", "## 15." → "## 13.", updated ToC)
- [x] Review and replace placeholders in key files (priority files cleaned, 99→8 remaining are template syntax)
- [x] Run validation scripts (validate_metadata.py: PASSED, validate_cross_document.py: PASSED)

### Pending
(None - all tasks completed)

### Notes
- Section numbering fix: Cross-Document Validation sections jumped from 9 to 13/14/15 - renumber to continuous 10, 11, 12 etc.
- ICON layer: Change from 11 to 11.5 to resolve conflict with TASKS

## Implementation Guide

### Prerequisites
- Access to `/opt/data/docs_flow_framework/ai_dev_flow/`
- Read the detailed plan at `/home/ya/.claude/plans/vectorized-purring-avalanche.md`

### Phase 1: Critical Fixes (HIGH Priority)

**1.1 Fix Corrupted Text**
```
File: ai_dev_flow/PROJECT_SETUP_GUIDE.md:69
Change: "REQUIRED regulatoryOND" → "REQUIRED SECOND"
```

**1.2 Remove Duplicate YAML Blocks**
```
File: ai_dev_flow/BDD/BDD_CREATION_RULES.md
Action: Remove duplicate custom_fields blocks at lines 81 and 109
Keep only the first block at line 13
```

**1.3 Fix Section Numbering (4 files)**
Files to fix:
- `ai_dev_flow/CTR/CTR_CREATION_RULES.md` - Sections 1-9, then jumps to 14
- `ai_dev_flow/IMPL/IMPL_CREATION_RULES.md` - Sections 1-9, 13, 14
- `ai_dev_flow/IPLAN/IPLAN_CREATION_RULES.md` - Sections 1-9, 13, 14, 15
- `ai_dev_flow/TASKS/TASKS_CREATION_RULES.md` - Sections 1-9, 13, 14, 15

Action: Renumber all sections to be continuous (1, 2, 3... with no gaps)

**1.4 Add Table of Contents (5 files)**
Files:
- `ai_dev_flow/CTR/CTR_CREATION_RULES.md`
- `ai_dev_flow/IMPL/IMPL_CREATION_RULES.md`
- `ai_dev_flow/IPLAN/IPLAN_CREATION_RULES.md`
- `ai_dev_flow/TASKS/TASKS_CREATION_RULES.md`
- `ai_dev_flow/ICON/ICON_CREATION_RULES.md`

### Phase 2: Metadata Standardization (MEDIUM Priority)

**2.1 Fix document_type Field (5 files)**
```yaml
# Change from:
document_type: creation_rules  # or "guide"
# To:
document_type: creation-rules
```

Files:
- `ai_dev_flow/CTR/CTR_CREATION_RULES.md`
- `ai_dev_flow/IMPL/IMPL_CREATION_RULES.md`
- `ai_dev_flow/IPLAN/IPLAN_CREATION_RULES.md`
- `ai_dev_flow/TASKS/TASKS_CREATION_RULES.md`
- `ai_dev_flow/ICON/ICON_CREATION_RULES.md`

**2.2 Add YAML Frontmatter (2 files)**
- `ai_dev_flow/BDD/BDD_AI_AGENT_EXTENSION.md`
- `ai_dev_flow/BDD/BDD_PRE_GENERATION_CHECKLIST.md`

**2.3 Update ICON Layer**
```yaml
# In ICON_CREATION_RULES.md:
layer: 11.5  # Changed from 11 to resolve conflict with TASKS
```

### Phase 3: Content Cleanup (LOW-MEDIUM Priority)

**3.1 Replace Placeholder Text (99 occurrences, 16 files)**
Replace all `[RESOURCE_INSTANCE - e.g., ...]` placeholders with context-appropriate descriptive text.

Priority files:
1. `ai_dev_flow/IMPL/README.md`
2. `ai_dev_flow/IMPL/IMPL-TEMPLATE.md`
3. `ai_dev_flow/BRD/README.md`
4. `ai_dev_flow/BDD/README.md`

### Verification

After remediation, run:
```bash
# Validate all metadata
python scripts/validate_metadata.py

# Validate all documentation paths
python scripts/validate_documentation_paths.py --strict

# Validate cross-document references
python scripts/validate_cross_document.py --full --auto-fix
```

### Success Criteria
1. Zero corrupted/garbled text
2. All *_CREATION_RULES.md files have continuous section numbering
3. All *_CREATION_RULES.md files have Table of Contents
4. All metadata uses `document_type: creation-rules` (hyphen format)
5. No duplicate YAML blocks in any file
6. All markdown files have YAML frontmatter
7. Layer 11.5 assigned to ICON (conflict resolved)
8. Placeholder text reduced by 90%+

## References

- Detailed Plan: `/home/ya/.claude/plans/vectorized-purring-avalanche.md`
- Framework Root: `/opt/data/docs_flow_framework/ai_dev_flow/`
- Key Files:
  - `ai_dev_flow/PROJECT_SETUP_GUIDE.md`
  - `ai_dev_flow/BDD/BDD_CREATION_RULES.md`
  - `ai_dev_flow/CTR/CTR_CREATION_RULES.md`
  - `ai_dev_flow/IMPL/IMPL_CREATION_RULES.md`
  - `ai_dev_flow/IPLAN/IPLAN_CREATION_RULES.md`
  - `ai_dev_flow/TASKS/TASKS_CREATION_RULES.md`
  - `ai_dev_flow/ICON/ICON_CREATION_RULES.md`

## Files Modified Priority Order

| # | File | Actions | Priority |
|---|------|---------|----------|
| 1 | `ai_dev_flow/PROJECT_SETUP_GUIDE.md` | Fix corrupted text | CRITICAL |
| 2 | `ai_dev_flow/BDD/BDD_CREATION_RULES.md` | Remove duplicate custom_fields | HIGH |
| 3 | `ai_dev_flow/CTR/CTR_CREATION_RULES.md` | Fix numbering, add ToC, fix metadata | HIGH |
| 4 | `ai_dev_flow/IMPL/IMPL_CREATION_RULES.md` | Fix numbering, add ToC, fix metadata | HIGH |
| 5 | `ai_dev_flow/IPLAN/IPLAN_CREATION_RULES.md` | Fix numbering, add ToC, fix metadata | HIGH |
| 6 | `ai_dev_flow/TASKS/TASKS_CREATION_RULES.md` | Fix numbering, add ToC, fix metadata | HIGH |
| 7 | `ai_dev_flow/ICON/ICON_CREATION_RULES.md` | Fix metadata, add ToC, update layer | HIGH |
| 8 | `ai_dev_flow/BDD/BDD_AI_AGENT_EXTENSION.md` | Add YAML frontmatter | MEDIUM |
| 9 | `ai_dev_flow/BDD/BDD_PRE_GENERATION_CHECKLIST.md` | Add YAML frontmatter | MEDIUM |
| 10+ | 16 files with placeholders | Replace placeholders | LOW |
