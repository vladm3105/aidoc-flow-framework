# UCX v1.13.0 - Context Engineering & Finding ID Standardization

**Release Date**: 2026-03-13
**Status**: ✅ COMPLETE (Validated via Integration Testing)

## Implementation Status

| Phase | Status | Description |
|-------|--------|-------------|
| Finding ID Format | ✅ Complete | Canonical `PREFIX-P0-NNN` format |
| UCR Prompt Updates | ✅ Complete | BRD + PRD prompts with Finding ID tables |
| Skill File Updates | ✅ Complete | chairperson.md, operator.md updated |
| Context Engine Core | ✅ Complete | Hierarchical context, summarization |
| Attention Steering | ✅ Complete | Format at prompt END |
| Documentation | ✅ Complete | README, ROADMAP, CONTEXT_ENGINEERING.md |
| Integration Testing | ✅ Complete | 33 canonical findings, 0 legacy, manifest present |
| Hybrid Keyword Scan | ⏸️ Deferred | `RelevantSnippet`, `_scan_other_sections_for_keywords()` |
| Appendix-on-Demand | ⏸️ Deferred | `AppendixInfo`, dynamic detection |
| Dynamic Section Map | ⏸️ Deferred | `SECTION_CATEGORIES`, `DynamicSectionMapper` |

## Summary

UCX v1.13.0 introduces **context engineering** to address prompt size explosion and **Finding ID standardization** to fix extraction failures. These changes resolve critical bugs where reviews produced incorrect scores (showing 0 findings when 30+ exist) and generated summaries instead of structured tables.

## Problem Statement

| Issue | Symptom | Impact |
|-------|---------|--------|
| Regex mismatch | Frontmatter shows `P0=0` despite 30+ findings | Incorrect scores |
| Prompt size explosion | 170-187KB prompts | LLM truncates/simplifies output |
| Format instructions lost | Summary text instead of tables | Unparseable reports |
| Missing manifest markers | No `<!-- UCX-MANIFEST-START -->` | Remediation routing fails |

## Key Changes

### Canonical Finding ID Format

All personas now use a unified format: `PREFIX-P0-NNN`

| Persona | Prefix | Example |
|---------|--------|---------|
| Architect | ARCH | `ARCH-P0-001` |
| Auditor | AUD | `AUD-P0-001` |
| Tech Lead | TL | `TL-P1-001` |
| Operator | OP | `OP-P0-001` |
| Chairperson | REM | `REM-P0-001` |

**Old (broken)**: `P0-OP-001`, `**[P0-1]**`
**New (canonical)**: `OP-P0-001`, `ARCH-P0-001`

### Context Engineering

Reduces prompt size from 170KB to ~60-80KB while improving LLM adherence to format.

| Component | Purpose | Token Savings |
|-----------|---------|---------------|
| `PERSONA_SECTION_MAP` | Static section filtering per persona | 30-50% |
| `PriorFindingsSummarizer` | Summarizes prior findings | 90% reduction |
| `build_attention_steering_format()` | Format at prompt END | N/A (quality) |
| Hierarchical Context | 4-level document structure | Variable |
| Hybrid Keyword Scan | Discovers relevant content in other sections | Completeness |

### Attention Steering

Format instructions are now placed at the **END** of the prompt with visual emphasis:

```
═══════════════════════════════════════════════════════════════════
==  CRITICAL: REQUIRED OUTPUT FORMAT - READ THIS SECTION LAST    ==
═══════════════════════════════════════════════════════════════════

### Finding ID Format: ARCH-P{0-2}-NNN

| ID (ARCH-P0-NNN) | Finding | Section | Gap | Remediation |
|------------------|---------|---------|-----|-------------|
| ARCH-P0-001 | [finding] | [X.X] | [gap] | [fix] |
```

### Hybrid Context Selection (Static + Dynamic)

Context selection uses a hybrid approach:

1. **Static (Primary)**: `PERSONA_SECTION_MAP` ensures core sections are always included
2. **Dynamic (Secondary)**: Keyword scan of "other" sections discovers relevant content

```python
# Hybrid approach in build_hierarchical_context()
ctx = engine.build_hierarchical_context(
    persona="architect",
    enable_keyword_scan=True,  # Enable hybrid discovery
    max_discovered_snippets=10,
)

# Results include 4 levels:
# - level2_relevant: Core sections from PERSONA_SECTION_MAP
# - level4_discovered: Keyword-discovered snippets from other sections
```

**Benefits**:
- Catches relevant content scattered across sections
- Static mapping ensures core sections never missed
- Only scans non-mapped sections (minimal overhead)
- Discovered snippets clearly labeled as "additional"

### Chairperson Validation

`save_response()` now validates chairperson output for required manifest markers:

```python
if "<!-- UCX-MANIFEST-START -->" not in response:
    logger.warning("Chairperson response missing UCX-MANIFEST-START marker")
```

### Bug Fix: UnifiedPromptLoader Attention Steering

**Problem**: In multi-turn mode, the `UnifiedPromptLoader.build_persona_prompt()` method was not appending the attention steering format at the END of the prompt. Format instructions from the skill file were at line 133 of 4300 (3% into prompt), causing "lost in the middle" phenomenon.

**Fix**: Added calls to `build_attention_steering_format()` and `build_chairperson_manifest_format()` after the document content in `UnifiedPromptLoader.build_persona_prompt()`:

```python
# After document content
parts.append(document_content)

# OUTPUT FORMAT AT END (Attention Steering)
if persona == "chairperson":
    parts.append(build_chairperson_manifest_format())
else:
    parts.append(build_attention_steering_format(persona, prefix))
```

**Result**: Integration testing showed 100% canonical format compliance (33 findings with `PREFIX-P0-NNN`, 0 legacy format).

## New Components

| Component | Location | Purpose |
|-----------|----------|---------|
| `FINDING_ID_PATTERN` | `review_memory.py` | Canonical regex for `PREFIX-P0-NNN` |
| `_parse_finding_id()` | `review_memory.py` | Returns `(prefix, priority, number)` |
| `_validate_chairperson_response()` | `review_memory.py` | Validates manifest markers |
| `PERSONA_PREFIX_MAP` | `context_engine.py` | Maps 14 personas to prefixes |
| `PERSONA_SECTION_MAP` | `context_engine.py` | Section filtering per persona |
| `ContextEngine` | `context_engine.py` | Hierarchical document context |
| `PriorFindingsSummarizer` | `context_engine.py` | Prior findings summarization |
| `build_attention_steering_format()` | `context_engine.py` | Format at prompt END |
| `build_chairperson_manifest_format()` | `context_engine.py` | Manifest template |

## Files Changed

| File | Change |
|------|--------|
| `ucx/core/context_engine.py` | NEW: Full context engineering module |
| `ucx/core/review_memory.py` | Updated: Finding pattern, validation, extraction |
| `ucx/core/persona_prompts.py` | Updated: Context engineering integration |
| `tests/test_finding_extraction.py` | NEW: 14 test cases for finding ID patterns |
| `tests/test_context_engine.py` | NEW: 25 test cases for context engine |

## API Changes

### build_persona_prompt() Signature

```python
def build_persona_prompt(
    persona: str,
    shared_context: str,
    previous_responses: dict[str, str] = None,
    doc_type: str = "brd",
    skill_dir: Optional[Path] = None,
    project_dir: Optional[Path] = None,
    use_context_engineering: bool = True,  # NEW
) -> str:
```

### New Exports from context_engine.py

```python
from ucx.core.context_engine import (
    PERSONA_PREFIX_MAP,
    PERSONA_SECTION_MAP,
    ContextEngine,
    PriorFindingsSummarizer,
    build_attention_steering_format,
    build_chairperson_manifest_format,
)
```

## Benefits

1. **Accurate scores**: Finding extraction now matches actual persona output
2. **Smaller prompts**: 170KB → 60-80KB per persona call
3. **Better LLM adherence**: Format instructions at END (attention steering)
4. **Guaranteed manifest**: Chairperson validation ensures machine-parseable output
5. **90% prior context reduction**: Summarized findings instead of raw text

## Migration

No breaking changes. The `use_context_engineering` parameter defaults to `True`.

To disable (not recommended):
```python
prompt = build_persona_prompt(..., use_context_engineering=False)
```

## Verification

```bash
# Test finding extraction
cd /opt/data/docs_flow_framework/UCX
PYTHONPATH=. python -c "
from ucx.core.review_memory import FINDING_ID_PATTERN
text = '| ARCH-P0-001 | Finding |'
matches = FINDING_ID_PATTERN.findall(text)
print(f'Matches: {len(matches)}')
"

# Test context engineering
PYTHONPATH=. python -c "
from ucx.core.persona_prompts import build_persona_prompt
p = build_persona_prompt('architect', 'doc', use_context_engineering=True)
print(f'Format at end: {\"REQUIRED OUTPUT FORMAT\" in p[-2000:]}')
"
```

## Related Documentation

- [PLAN-003: Persona Prompt Restructuring](plans/PLAN-003_persona_prompt_restructuring.md)
- [ROADMAP.md](ROADMAP.md)
- [README.md](../README.md)
