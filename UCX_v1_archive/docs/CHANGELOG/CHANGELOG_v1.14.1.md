# UCX v1.14.1 - Prompt Quality Improvements

**Release Date**: 2026-03-13

## Overview

This release improves the quality of generated prompts through content preprocessing, system instruction loading from skill manifests, and token optimization. These improvements complement the Prompt Inspection Toolset from v1.14.0.

## Problem Statement

Quality evaluation of generated prompts revealed content issues:

| Issue | Impact | Tokens Wasted |
|-------|--------|---------------|
| YAML frontmatter included | Non-essential metadata in prompts | ~175 tokens/prompt |
| HTML comments duplicated | Diagram requests repeated per section | ~245 tokens/prompt |
| Navigation breadcrumbs | Irrelevant for review context | ~35 tokens/prompt |
| Document metadata | Revision history, Document Control, etc. | Variable |
| Minimal system instructions | "You are the X reviewing..." only | Poor guidance |
| Alphabetical section ordering | BRD-01.11 sorted before BRD-01.5 | Confusion |

**Total waste**: ~455 tokens per prompt, ~5,000 tokens across 11 personas.

## Solution

### Content Preprocessing

Added preprocessing pipeline to strip non-essential content:

```python
# New patterns in ucx/prompts/document.py
FRONTMATTER_PATTERN = re.compile(r'^---\n.*?\n---\n', re.DOTALL)
HTML_COMMENT_PATTERN = re.compile(r'<!--.*?-->', re.DOTALL)
NAVIGATION_PATTERN = re.compile(r'^>\s*\*\*Navigation\*\*:.*$', re.MULTILINE)

# Document metadata patterns (low-value for review)
METADATA_PATTERNS = [
    # Document Revision History tables
    re.compile(r'###?\s*Document Revision History\s*\n.*?(?=\n---|\n##[^#]|\Z)', ...),
    # Document Control sections
    re.compile(r'##\s*Document Control\s*\n.*?(?=\n---|\n##[^#]|\Z)', ...),
    # Version/Date/Author tables
    re.compile(r'\|\s*Version\s*\|\s*Date\s*\|\s*Author\s*\|.*?(?=\n\n|\n---|\n##|\Z)', ...),
    # Quick Statistics sections
    re.compile(r'##\s*Quick Statistics\s*\n.*?(?=\n---|\n##[^#]|\Z)', ...),
    # Section Index tables
    re.compile(r'##\s*Section Index\s*\n.*?(?=\n---|\n##[^#]|\Z)', ...),
]

def preprocess_content(content: str,
                       strip_frontmatter: bool = True,
                       strip_comments: bool = True,
                       strip_navigation: bool = True,
                       strip_metadata: bool = True) -> str:
    """Preprocess section content by removing non-essential artifacts."""
```

### System Instructions from Skill Manifests

Added `_load_system_instructions()` to load persona knowledge from skill files:

```python
# Search order for skill manifests
1. Project: {project}/.ucx/skills/{persona}.md
2. Framework: /UCX/skills/{persona}.md

# Sections extracted from skill manifest
- Role description
- Review focus areas
- Quality criteria
- Finding categories
- Anti-patterns to detect
```

### Section Numeric Sorting

Fixed section ordering to use numeric sort instead of alphabetical:

```python
def _section_sort_key(section_id: str) -> tuple[int, int]:
    """Sort key for section IDs by numeric order."""
    # BRD-01.6 → (6, 0)
    # BRD-01.10 → (10, 0)
    # BRD-01.6.1 → (6, 1)
```

### Project Template Support

Added support for project-specific persona customization:

```
project/
├── .ucx/
│   └── skills/
│       └── architect.md    # Project-specific architect skill
```

## Files Changed

| File | Changes |
|------|---------|
| `ucx/prompts/document.py` | Added preprocessing patterns and `preprocess_content()` function, `load_preprocessed()` method, `_section_sort_key()` |
| `ucx/prompts/api.py` | Added `_load_system_instructions()`, `_find_project_root()`, fixed anti-pattern regex |

## Before/After Comparison

### Before (v1.14.0)

```
YAML frontmatter: Present ❌
HTML comments: Present ❌
Navigation: Present ❌
Revision history: Present ❌
System instructions: Minimal (~10 lines) ❌
Section order: Alphabetical (BRD-01.11 before BRD-01.5) ❌
Skill anti-patterns: Missing ❌
```

### After (v1.14.1)

```
YAML frontmatter: Stripped ✓
HTML comments: Stripped ✓
Navigation: Stripped ✓
Revision history: Stripped ✓
System instructions: Full skill manifest (~100+ lines) ✓
Section order: Numeric (BRD-01.5 before BRD-01.11) ✓
Skill anti-patterns: Included ✓
```

## Token Savings

| Content Type | Tokens Saved |
|--------------|--------------|
| YAML frontmatter | ~175/prompt |
| HTML comments | ~245/prompt |
| Navigation | ~35/prompt |
| Document metadata | Variable |
| **Total per prompt** | ~455 tokens |
| **Total across 11 personas** | ~5,000 tokens |

## Usage

No CLI changes. Preprocessing is automatic when using `ucx prompt generate`:

```bash
# Generate preprocessed prompts
ucx prompt generate brd docs/01_BRD/BRD-01/ -p architect

# Verify preprocessing worked
grep -c "^---$" .ucx_review_session/prompt_architect.txt
# Expected: 0 (no YAML frontmatter)

# Verify skill sections present
grep "Anti-Patterns" .ucx_review_session/prompt_architect.txt
# Expected: BeeLocal-Specific Anti-Patterns section
```

## Project-Specific Skills

Create project-specific persona customization:

```bash
# Create project skills directory
mkdir -p .ucx/skills/

# Create BeeLocal-specific architect skill
cat > .ucx/skills/architect.md << 'EOF'
# BeeLocal Platform Architect Review Skill

## Role
Senior Solutions Architect reviewing BeeLocal cross-border remittance platform.

## Platform Context
- 8-Layer modular architecture
- 6 Core Partners (Nuvei, Payoneer, etc.)
- US→Uzbekistan remittance corridor

## BeeLocal-Specific Anti-Patterns
1. Missing partner SLA specifications
2. Incomplete fallback chain documentation
...
EOF
```

## Backward Compatibility

- No breaking changes
- All existing prompts continue to work
- Preprocessing is additive (removes noise, doesn't change content)
- Skill loading falls back to framework defaults if project skills not found

## Bug Fixes

### Anti-Pattern Regex Fix

The regex for extracting anti-patterns from skill manifests was not matching correctly:

**Before (broken)**:
```python
r'^## Common Anti-Patterns.*?\n(.*?)(?=\n##|\Z)'
# Problem 1: Only matched "Common Anti-Patterns", not project-specific titles
# Problem 2: (.*?) was too non-greedy, matching empty string
```

**After (fixed)**:
```python
r'^##\s+.*Anti-Patterns.*?\n([\s\S]*?)(?=\n##|\Z)'
# Fix 1: .*Anti-Patterns.* matches any title containing "Anti-Patterns"
# Fix 2: [\s\S]*? properly matches multiline content
```

## Verification

```bash
# Generate prompt and check metadata
cd /opt/data/b-local/b-local-docs
ucx prompt generate brd docs/01_BRD/BRD-01_platform_architecture/ -p architect

# Check tokens and sections
cat docs/01_BRD/BRD-01_platform_architecture/.ucx_review_session/prompt_architect.meta.json | jq '.tokens'
# {
#   "total": 16872,
#   "document": 16033,
#   "instructions": 839
# }

# Verify skill content present (BeeLocal-specific terms)
grep -c "8-Layer" .ucx_review_session/prompt_architect.txt
# Expected: 1+
```

## References

- [PLAN-005: Prompt Engineering Toolset](plans/PLAN-005_prompt_engineering_toolset.md)
- [CHANGELOG_v1.14.0](CHANGELOG_v1.14.0.md) - Prompt Inspection Toolset
- [ROADMAP.md](ROADMAP.md)

---

*UCX v1.14.1 - 2026-03-13*
