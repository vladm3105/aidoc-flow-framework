# UCX v1.14.2 - Enhanced Skill Extraction

**Release Date**: 2026-03-13

## Overview

This release enhances the skill extraction logic to capture more domain-specific context from skill manifests, significantly improving instruction quality for persona-based reviews.

## Problem Statement

Skill files contain rich domain knowledge, but only a subset was being extracted:

| Skill Section | Before v1.14.2 | After v1.14.2 |
|---------------|----------------|---------------|
| Role | ✓ Extracted | ✓ Extracted |
| Review Focus | ✓ Extracted | ✓ Extracted |
| Anti-Patterns | ✓ Extracted | ✓ Extracted |
| Business Processes | ✗ Missing | ✓ Extracted |
| Stakeholders | ✗ Missing | ✓ Extracted |
| Domain Requirements | ✗ Missing | ✓ Extracted |
| Review Questions | ✗ Missing | ✓ Extracted |
| Analysis Checklist | ✗ Missing | ✓ Extracted |
| Quality Framework (5 C's) | ✗ Missing | ✓ Extracted |

**Impact**: ~60% of skill content was not being used in generated prompts.

## Solution

Enhanced `_load_system_instructions()` in `ucx/prompts/api.py` with additional regex patterns:

```python
# New extraction patterns added
- ^##\s+.*Business Process.*?\n
- ^##\s+.*Stakeholders.*?\n
- ^##\s+.*(?:Corridor|Domain).*?Requirements.*?\n
- ^##\s+Review Questions.*?\n
- ^##\s+Analysis Checklist.*?\n
- ^##\s+The 5\s*['"]?C['"]?s.*?\n
```

## Before/After Comparison

### Business Analyst Prompt

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Total tokens | 18,099 | 18,633 | +534 tokens |
| Instruction tokens | 372 | 906 | +143% |
| Instruction ratio | 2.1% | 4.9% | +133% |

### Extracted Content

**Before (v1.14.1)**:
```
**Role**: Business Analyst responsible for BeeLocal...
**Review Focus**: (5 bullet points)
**Anti-Patterns to Flag**: (3 patterns)
```

**After (v1.14.2)**:
```
**Role**: Business Analyst responsible for BeeLocal...
**Review Focus**: (5 bullet points)
**Anti-Patterns to Flag**: (3 patterns)
**Business Processes**: (6-step remittance flow + stakeholder table)
**Review Questions**: (5 questions)
**Analysis Checklist**: (7 checklist items)
**Quality Framework (5 C's)**: (Clear, Complete, Consistent, Correct, Confirmable)
```

## Files Changed

| File | Changes |
|------|---------|
| `ucx/prompts/api.py` | Added 6 new section extraction patterns in `_load_system_instructions()` |

## Skill File Conventions

To maximize extraction, skill files should use these section headers:

| Section | Header Pattern | Purpose |
|---------|----------------|---------|
| Business Processes | `## ... Business Process...` | Domain-specific workflows |
| Stakeholders | `## ... Stakeholders...` | Key actors and concerns |
| Domain Requirements | `## ... Corridor/Domain ... Requirements...` | Domain constraints |
| Review Questions | `## Review Questions` | Actionable review prompts |
| Analysis Checklist | `## Analysis Checklist` | Verification items |
| Quality Framework | `## The 5 'C's...` | Quality criteria framework |

## Verification

```bash
# Generate prompt and check instruction ratio
cd /opt/data/b-local/b-local-docs
source .envrc
ucx prompt generate brd docs/01_BRD/BRD-01_platform_architecture/ -p business_analyst

# Check token distribution
cat docs/01_BRD/BRD-01_platform_architecture/.doc_review_memory/prompt_business_analyst.meta.json | jq '.tokens'
# {
#   "total": 18633,
#   "document": 17727,
#   "instructions": 906
# }

# Verify new sections present
grep -c "Business Processes\|Review Questions\|Analysis Checklist\|Quality Framework" \
  docs/01_BRD/BRD-01_platform_architecture/.doc_review_memory/prompt_business_analyst.txt
# Expected: 4
```

## Backward Compatibility

- No breaking changes
- Existing skill files work without modification
- New sections are extracted only if present in skill files
- Prompts with minimal skill files continue to work

## References

- [PLAN-005: Prompt Engineering Toolset](plans/PLAN-005_prompt_engineering_toolset.md)
- [CHANGELOG_v1.14.1](CHANGELOG_v1.14.1.md) - Content preprocessing
- [CHANGELOG_v1.14.0](CHANGELOG_v1.14.0.md) - Prompt inspection toolset

---

*UCX v1.14.2 - 2026-03-13*
