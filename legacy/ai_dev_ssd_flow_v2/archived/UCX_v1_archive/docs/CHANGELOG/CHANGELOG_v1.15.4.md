# CHANGELOG v1.15.4 - BRD-E002 Invalid Value Fixer & GATE-E001 Recursion Fix

**Release Date**: 2026-03-14

## Overview

This release fixes critical bugs in three auto-fixers and adds file exclusion patterns for non-BRD files. Key improvements include handling invalid values (not just missing fields), preventing recursive DEFERRED comment nesting, and safer element movement using markers.

## Bug Fixes

### BRD-E002: Invalid Value Handling

**Problem**: BRD-E002 fixer only checked for MISSING fields, not INVALID values. Validation messages like "Invalid value for status: 'Draft'" were reported as "No changes needed."

**Solution**: Added parsing for "Invalid value for X:" context messages and value remapping tables.

**Value Mappings Added**:
| Field | Invalid Value | Fixed Value |
|-------|---------------|-------------|
| status | `Draft`, `draft`, `DRAFT` | `development` |
| document_type | `brd-document`, `BRD`, `guide`, `reference` | `brd` |
| artifact_type | `VALIDATION_SUMMARY`, `BRD-REPORT` | `BRD` |

### GATE-E001: Recursive DEFERRED Nesting Fix

**Problem**: GATE-E001 fixer caused recursive nesting when processing files with existing DEFERRED comments. Pattern like `TODO` inside `<!-- DEFERRED: TODO item pending -->` got re-converted, producing:
```html
<!-- DEFERRED: <!-- DEFERRED: TODO item pending --> item pending -->
```

**Solution**: Added placeholder protection mechanism:
1. Find all existing `<!-- DEFERRED:...-->` comments
2. Replace with unique placeholders before pattern matching
3. Apply placeholder conversion patterns
4. Restore original DEFERRED comments

**Additional Patterns Added**:
- `[Pending]` → `<!-- DEFERRED: Pending item -->`
- `[placeholder]` → `<!-- DEFERRED: placeholder -->`

### GATE-W008: Safer Element Movement

**Problem**: GATE-W008 fixer moved elements between section files, but when multiple elements were processed from the same file, stale line numbers caused file corruption (duplicate YAML frontmatter blocks).

**Solution**: Changed approach from actual movement to marker insertion:
```html
<!-- MOVE-TO-SECTION-6: Element type 01 should be in BRD-XX.6_functional_requirements.md -->
```

**Extended TYPE_TO_SECTION Mapping**:
| Type Code | Section | Description |
|-----------|---------|-------------|
| 07 | 10 | Risk → Risk Assessment |
| 08 | 8 | Metric → Constraints |
| 09 | 5 | User Story → Use Cases |
| 10 | 7 | Decision/ADR Topic → Quality Attributes |
| 23 | 2 | Business Objective → Business Context |
| 32 | 7 | Architecture Topic → Quality Attributes |

### BRD-E003: Forbidden Tag Remover

**Problem**: `business-requirements` tag was incorrectly used in some files.

**Solution**: Added removal pattern for `business-requirements` → removed from tags list.

## New Features

### NON_BRD_FILE_PATTERNS Exclusion

**Problem**: Reference files placed in BRD directories (reports, guides, summaries) were validated as BRD artifacts, generating false errors.

**Solution**: Added `NON_BRD_FILE_PATTERNS` exclusion list in `ucx/validators/brd/__init__.py`:

| Pattern | Example Files |
|---------|---------------|
| `BRD_VALIDATION_REPORT.md` | Validation summary reports |
| `EXECUTIVE_SUMMARY.md` | Executive summaries |
| `GCP_DIAGRAM_GUIDE.md` | Reference guides |
| `README.md` | Directory READMEs |
| `CHANGELOG*.md` | Changelog files |
| `*V_validation_report*.md` | Validation reports |

## Impact

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Tier 1 Errors | 187 | 137 | -50 (27% reduction) |
| Tier 2 Warnings | 145 | 133 | -12 |
| GATE-W008 | 76 | 64 | -12 (markers added) |

### Remaining Errors (Non-Fixable)

| Code | Count | Reason |
|------|-------|--------|
| BRD-E006 | 122 | Missing required sections (needs AI content creation) |
| BRD-E011 | 15 | Missing Business Requirements (needs AI content creation) |

## Files Modified

| File | Changes |
|------|---------|
| `ucx/validators/brd/fixer.py` | BRD-E002 value parsing, GATE-E001 protection, GATE-W008 markers |
| `ucx/validators/brd/__init__.py` | NON_BRD_FILE_PATTERNS exclusion list |
| `ucx/validators/brd/schema.py` | TYPE_TO_SECTION mapping extensions |
| `ucx/validators/brd/structure.py` | Minor validation adjustments |
| `ucx/version.py` | Updated to v1.15.4 |

## Usage

```bash
# Apply all fixes to BRD directory
ucx validate brd docs/01_BRD/BRD-05_multi_agent_ai_system --fix

# Files with MOVE-TO-SECTION markers can be manually reviewed:
grep -r "MOVE-TO-SECTION" docs/01_BRD/

# Non-BRD files are automatically excluded:
ucx validate brd docs/01_BRD/  # Skips BRD_VALIDATION_REPORT.md, etc.
```

## Backward Compatibility

All changes are backward compatible. The marker-based approach for GATE-W008 is safer than actual element movement and preserves file integrity.

## Migration Notes

If you have corrupted files from previous GATE-W008 runs (duplicate YAML frontmatter), restore them with:
```bash
git checkout -- path/to/corrupted/file.md
```

Then re-run validation with this version, which adds markers instead of moving content.
