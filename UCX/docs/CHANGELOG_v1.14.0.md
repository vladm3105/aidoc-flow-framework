# UCX v1.14.0 - Prompt Inspection Toolset

**Release Date**: 2026-03-13

## Overview

This release introduces the **Prompt Inspection Toolset** for pre-LLM analysis of generated prompts. Large documents (150K+ chars) merged into 40-50K token prompts are impossible to review manually. This toolset provides CLI and API interfaces to inspect, validate, and debug prompts before running expensive LLM reviews.

## Problem Statement

Documents like BRD-01 with 19 sections and 161K characters get merged into persona-filtered prompts of 15-40K tokens each. Without inspection tools:
- Token budgets are opaque until LLM complains
- Section inclusion decisions are invisible
- Format instruction positioning is unclear
- Debug cycle requires full LLM execution

## Solution

The prompt inspection toolset provides five commands to analyze prompts **without** LLM execution:

| Command | Purpose |
|---------|---------|
| `ucx prompt tokens` | Analyze token usage per persona |
| `ucx prompt sections` | Show section inclusion matrix |
| `ucx prompt inspect` | Inspect generated prompt structure |
| `ucx prompt check` | Validate document for prompt generation |
| `ucx prompt generate` | Generate prompts with metadata |

## New CLI Commands

### `ucx prompt tokens`

Analyze token usage per persona with budget tracking.

```bash
# All personas
ucx prompt tokens brd docs/01_BRD/BRD-01/

# Specific personas
ucx prompt tokens brd docs/01_BRD/BRD-01/ -p architect -p auditor

# Custom budget
ucx prompt tokens brd docs/01_BRD/BRD-01/ --budget 50000

# JSON output
ucx prompt tokens brd docs/01_BRD/BRD-01/ --json
```

**Sample output:**

```
TOKEN ANALYSIS
============================================================

Document: docs/01_BRD/BRD-01_platform_architecture
Type: BRD
Method: chars

Document:
  Characters: 161,254
  Tokens: 40,307

Per-Persona Breakdown:
------------------------------------------------------------
Persona              Sections      Doc  Instr    Total   Budget
------------------------------------------------------------
architect                   7   12,903  3,500   16,403   70,000
auditor                    12   33,939  4,000   37,939   60,000
...

Context Engineering Savings:
  Without CE: 80,614 tokens
  With CE: 54,342 tokens
  Savings: 26,272 tokens (33%)
```

### `ucx prompt sections`

Show which sections are included for each persona.

```bash
# ASCII table
ucx prompt sections brd docs/01_BRD/BRD-01/

# CSV export
ucx prompt sections brd docs/01_BRD/BRD-01/ --csv > matrix.csv

# JSON export
ucx prompt sections brd docs/01_BRD/BRD-01/ --json
```

**Legend:**
- `FULL` - Required section (full content included)
- `OPT` - Optional section (included if space allows)
- `IDX` - Index-only (title/summary only)
- `-` - Skipped (not included)

### `ucx prompt inspect`

Inspect a generated prompt file for structure and issues.

```bash
ucx prompt inspect tmp/prompts/prompt_architect.txt
ucx prompt inspect tmp/prompts/prompt_architect.txt --json
```

**Detects:**
- Prompt structure (system instructions, persona, document content, format)
- Token counts and largest sections
- Format instruction positioning (should be at END)
- Priority markers presence
- Potential attention issues

### `ucx prompt check`

Validate document is ready for prompt generation.

```bash
# Basic check
ucx prompt check brd docs/01_BRD/BRD-01/

# Strict mode (exit 1 if budget exceeded)
ucx prompt check brd docs/01_BRD/BRD-01/ --strict

# JSON output for CI/CD
ucx prompt check brd docs/01_BRD/BRD-01/ --json
```

**Exit codes:**
- `0` - All checks passed
- `1` - Errors detected

### `ucx prompt generate`

Generate prompts for all or specific personas.

```bash
# Generate all
ucx prompt generate brd docs/01_BRD/BRD-01/

# Specific personas
ucx prompt generate brd docs/01_BRD/BRD-01/ -p architect -p auditor

# Custom output directory
ucx prompt generate brd docs/01_BRD/BRD-01/ -o tmp/prompts/

# Without metadata files
ucx prompt generate brd docs/01_BRD/BRD-01/ --no-metadata
```

**Output files:**
- `prompt_{persona}.txt` - Prompt content
- `prompt_{persona}.meta.json` - Metadata for inspection

**Default output directory:** `.ucx_review_session/` (consistent with UCX review session storage)

## New API

The `UCPromptPhase` class provides programmatic access to all inspection features.

```python
from ucx.prompts import UCPromptPhase
from pathlib import Path

api = UCPromptPhase()

# Analyze tokens
result = api.tokens(Path("docs/01_BRD/BRD-01/"), "brd")
print(f"Total tokens: {result.total_all_personas:,}")
print(f"Budget exceeded: {result.budget_exceeded}")

# Build section matrix
matrix = api.sections(Path("docs/01_BRD/BRD-01/"), "brd")
print(matrix.to_table())
print(matrix.to_csv())

# Check document
check = api.check(Path("docs/01_BRD/BRD-01/"), "brd", strict=True)
if not check.passed:
    for error in check.errors:
        print(f"Error: {error}")

# Generate prompts
result = api.generate(Path("docs/01_BRD/BRD-01/"), "brd", output_dir=Path("tmp/prompts"))
for prompt in result.prompts:
    print(f"{prompt.persona}: {prompt.token_estimate:,} tokens")
```

## New Module Structure

```
ucx/prompts/
├── __init__.py      # Package exports
├── models.py        # Data classes
├── exceptions.py    # Custom exceptions
├── document.py      # DocumentLoader
├── inspector.py     # PromptInspector
├── analyzer.py      # TokenAnalyzer
├── mapper.py        # SectionMapper
└── api.py           # UCPromptPhase
```

### Data Classes

| Class | Purpose |
|-------|---------|
| `PromptSection` | Section within prompt structure |
| `InspectionResult` | Result of prompt inspection |
| `PersonaTokens` | Token breakdown for one persona |
| `TokenAnalysis` | Token analysis across all personas |
| `SectionMatrix` | Section inclusion matrix |
| `CheckResult` | Validation check result |
| `GeneratedPrompt` | Result of generating one prompt |
| `GenerationResult` | Result of generating all prompts |
| `PromptMetadata` | Metadata stored in .meta.json |

### Exception Hierarchy

```
PromptInspectionError (base)
├── DocumentNotFoundError
├── InvalidDocumentTypeError
├── PromptFileNotFoundError
├── MetadataNotFoundError
├── PersonaNotFoundError
├── TokenBudgetExceededError
├── ConfigurationError
└── PromptGenerationError
```

## Metadata Files

Generated prompts include `.meta.json` files with inspection data:

```json
{
  "persona": "architect",
  "generated_at": "2026-03-13T10:30:00",
  "doc_path": "docs/01_BRD/BRD-01_platform_architecture",
  "doc_type": "brd",
  "sections": {
    "included": ["BRD-01.3", "BRD-01.6", "BRD-01.7"],
    "skipped": ["BRD-01.14", "BRD-01.15"],
    "index_only": ["BRD-01.18"]
  },
  "tokens": {
    "total": 16403,
    "document": 12903,
    "instructions": 3500
  },
  "structure": {
    "system_instructions": {"start": 1, "end": 10, "tokens": 500},
    "document_content": {"start": 11, "end": 200, "tokens": 12903},
    "format_instructions": {"start": 201, "end": 210, "tokens": 500}
  }
}
```

## Integration with Existing Commands

The prompt toolset integrates with existing UCX commands:

```bash
# Check before review
ucx prompt check brd docs/01_BRD/BRD-01/ --strict && \
ucx review brd docs/01_BRD/BRD-01/

# Analyze after generation
ucx prompt generate brd docs/01_BRD/BRD-01/ -o tmp/prompts/
ucx prompt inspect tmp/prompts/prompt_architect.txt
```

## Backward Compatibility

- No breaking changes to existing commands
- `ucx prompt` is a new command group
- All existing `ucx review`, `ucx validate` commands work unchanged
- Uses existing `DynamicSectionMapper` from context engine

## Dependencies

No new external dependencies. Uses:
- `click` for CLI (existing)
- `rich` for formatting (existing)
- `pathlib` for paths (stdlib)

## Code Review

**Review Date**: 2026-03-13
**Status**: Passed with fixes applied

| Priority | Found | Fixed |
|----------|-------|-------|
| P0 Critical | 0 | - |
| P1 High | 4 | 4 |
| P2 Medium | 8 | 3 |

**P1 Fixes Applied:**
- Added specific exception handling + logging for file read failures
- Added output format validation with `ConfigurationError` for invalid formats
- Added `doc_type` parameter to TokenAnalyzer and SectionMapper constructors
- Fixed type annotation `any` → `Any` in document.py

**Deferred (Low Risk):**
- Unit test coverage (P2-007) - should add before production use

## References

- [PLAN-005: Prompt Engineering Toolset](plans/PLAN-005_prompt_engineering_toolset.md)
- [CONTEXT_ENGINEERING.md](CONTEXT_ENGINEERING.md)
- [ROADMAP.md](ROADMAP.md)

---

*UCX v1.14.0 - 2026-03-13*
