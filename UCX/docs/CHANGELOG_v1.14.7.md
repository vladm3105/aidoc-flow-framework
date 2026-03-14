# UCX v1.14.7 - One-Turn Attention Steering Fix

**Release Date**: 2026-03-14

## Overview

This release fixes the attention steering issue in one-turn review mode by restructuring prompts to place format instructions at the END after document content.

## Changes

### Attention Steering Fix

**Problem**: One-turn prompts had format instructions placed BEFORE the document content, which degraded LLM attention to output requirements by the time it finished processing.

**Solution**: Split format instructions into a separate file that gets appended AFTER the document content.

| Aspect | Before | After |
|--------|--------|-------|
| Format Instructions Position | START (before document) | END (after document) |
| Inspection Result | ⚠ Format instructions at START | ✓ Format instructions at END |
| Attention to Output Format | Degraded | Optimal |

### Files Changed

| File | Changes |
|------|---------|
| `ucx/api/review.py` | Added `_load_format_instructions()` method, updated `_build_review_prompt()` |
| `docs/UCX/review/UCR_FORMAT_BRD_PROJECT.md` | **New** - Extracted format instructions |
| `docs/UCX/review/UCR_PROMPT_BRD_PROJECT.md` | Removed embedded format instructions |

### API Changes

New method in `UCRPhase`:
```python
def _load_format_instructions(self, doc_type: DocType) -> str:
    """
    Load format instructions for document type (v1.14.7).

    Format instructions are appended AFTER the document content for
    better attention steering - LLMs pay more attention to content
    at the end of prompts.

    Search order (project-specific only):
    1. {project_dir}/docs/UCX/review/UCR_FORMAT_{TYPE}_PROJECT.md
    2. {project_dir}/docs/UCX/review/UCR_FORMAT_{TYPE}.md
    """
```

### Prompt Structure Comparison

**Before (v1.14.6):**
```
[System Instructions]
[Output Requirements]        ← Format instructions BEFORE document
[Persona Reviews]
[Required Output Format]     ← More format instructions BEFORE document
[Document Content]           ← Document at END
```

**After (v1.14.7):**
```
[System Instructions]
[Persona Reviews]
[Document Content]
[Format Instructions]        ← Format instructions at END (optimal)
```

## Migration

**For Projects Using One-Turn Review:**

1. Create `docs/UCX/review/UCR_FORMAT_BRD_PROJECT.md` with format instructions:
   - Output Requirements (priority classification, category tagging, finding ID format)
   - Required Output Format (YAML frontmatter, section templates)
   - Remediation Findings Manifest template

2. Remove format sections from `UCR_PROMPT_BRD_PROJECT.md`:
   - Remove "## Output Requirements" section
   - Remove "## REQUIRED OUTPUT FORMAT" section
   - Keep only domain context, persona reviews, and document placeholder

3. The UCX API will automatically load and append format instructions after document content.

## Verification

```bash
# Generate one-turn prompt
ucx prompt generate brd docs/01_BRD/BRD-01/ -o tmp/

# Inspect prompt structure
ucx prompt inspect tmp/prompt_architect.txt
# Should show: ✓ Format instructions at END
```

## Token Impact

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Total Tokens | ~59,572 | ~60,588 | +1,016 |
| Format Instructions | 11,901 (at start) | 2,270 (at end) | -9,631 |
| Document Content | 40,507 | 40,566 | +59 |

The slight increase in total tokens is due to the format file header and attention steering note.

## References

- [UNIFIED_CONTEXT_REVIEW.md](UNIFIED_CONTEXT_REVIEW.md) - Review modes documentation
- [CHANGELOG_v1.14.6.md](CHANGELOG_v1.14.6.md) - Session directory rename

---

*UCX v1.14.7 - 2026-03-14*
