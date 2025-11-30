# Implementation Plan - Framework 100% Readiness

**Created**: 2025-11-30 16:39:28 EST
**Status**: Ready for Implementation

## Objective

Make the docs_flow_framework 100% ready for new projects by fixing all identified issues from the readiness assessment.

## Context

Framework review identified several issues preventing 100% validation compliance:
- 22 metadata errors from obsolete backup folder
- 4 skills with relative paths instead of `{project_root}` placeholders
- 79 unknown tags not in taxonomy
- 30 broken example links in documentation
- 1 file missing YAML frontmatter

## Task List

### Pending
- [ ] Task 1: Delete backup folder `.claude/skills.backup_20251114_152704/`
- [ ] Task 2: Fix relative paths in 4 skills (context-analyzer, quality-advisor, skill-recommender, workflow-optimizer)
- [ ] Task 3: Expand tag taxonomy in `scripts/validate_metadata.py` (~30 new tags)
- [ ] Task 4: Fix broken example links in 4 files (convert to code blocks/placeholders)
- [ ] Task 5: Add YAML frontmatter to `.claude/commands/save-plan.md`
- [ ] Task 6: Run all validators to confirm 100% compliance

### Notes
- `.clinerules/doc-flow.md` excluded from fixes per user request
- All 30 broken links are intentional examples/placeholders - fix by wrapping in code blocks

## Implementation Guide

### Prerequisites
- Working directory: `/opt/data/docs_flow_framework`
- Python 3 for validation scripts

### Execution Steps

**Task 1: Delete Backup Folder**
```bash
rm -rf .claude/skills.backup_20251114_152704/
```

**Task 2: Fix Skill Paths** (4 files)
Files:
- `.claude/skills/context-analyzer/SKILL.md` (lines 445-446)
- `.claude/skills/quality-advisor/SKILL.md` (lines 422-423)
- `.claude/skills/skill-recommender/SKILL.md` (lines 290-291)
- `.claude/skills/workflow-optimizer/SKILL.md` (lines 489-490)

Change: `../../../ai_dev_flow/` → `{project_root}/ai_dev_flow/`

**Task 3: Expand Tag Taxonomy**
File: `scripts/validate_metadata.py` (VALID_TAGS set, lines 21-71)

Add tags:
```python
# Template tags - artifact-specific (12)
'adr-template', 'bdd-template', 'brd-template', 'ctr-template',
'ears-template', 'impl-template', 'iplan-template', 'prd-template',
'req-template', 'spec-template', 'sys-template', 'tasks-template',

# Template tags - generic (2)
'document-template', 'traceability-matrix-template',

# Reference/guide tags (5)
'reference-document', 'quick-reference', 'traceability-guide',
'metadata-guide', 'supporting-document',

# ICON/contract tags (5)
'implementation-contract', 'contract-index', 'contract-template',
'decision-criteria', 'troubleshooting',

# Index/directory tags (2)
'directory-overview', 'brd-glossary',

# Feature variant tags (2)
'feature-prd', 'architecture-adr',

# Checklist tags (2)
'tasks-checklist', 'ears',
```

**Task 4: Fix Broken Links** (4 files)
Files:
- `ai_dev_flow/AI_ASSISTANT_RULES.md` (6 links)
- `ai_dev_flow/FINANCIAL_DOMAIN_CONFIG.md` (6 links)
- `ai_dev_flow/QUICK_REFERENCE.md` (4 links)
- `ai_dev_flow/TRACEABILITY.md` (14 links)

Change pattern:
- Convert markdown links to inline code: `[BRD-001](../path)` → `` `@brd: BRD-001` ``
- Wrap template patterns in code blocks: `../BRD/BRD-NNN_...md` → `` `../BRD/BRD-NNN_...md` ``

**Task 5: Add Frontmatter**
File: `.claude/commands/save-plan.md`
```yaml
---
title: "Save Plan Command"
tags:
  - utility
---
```

### Verification

Run validators after each task:
```bash
# After Task 1
python3 scripts/validate_metadata.py  # Errors: 22 → 2

# After Task 2
python3 scripts/validate_skill_paths.py  # Failures: 4 → 0

# After Task 3
python3 scripts/validate_metadata.py  # Warnings: 79 → 0

# After Task 4
python3 ai_dev_flow/scripts/validate_links.py --docs-dir ai_dev_flow/  # Broken: 30 → 0

# After Task 5
python3 scripts/validate_metadata.py  # Errors: 2 → 1

# Final
python3 scripts/skills_compliance_report.py  # Should show 100%
```

## Expected Final Results

| Validator | Before | After |
|-----------|--------|-------|
| `validate_metadata.py` errors | 22 | 1* |
| `validate_metadata.py` warnings | 79 | 0 |
| `validate_skill_paths.py` failures | 4 | 0 |
| `validate_links.py` broken links | 30 | 0 |
| `skills_compliance_report.py` | 97.6% | 100% |

*1 remaining error is `.clinerules/doc-flow.md` (excluded per user request)

## References

- Plan file: `/home/ya/.claude/plans/glimmering-humming-hoare.md`
- Tag taxonomy: `scripts/validate_metadata.py`
- Skills directory: `.claude/skills/`
- Documentation: `ai_dev_flow/`
