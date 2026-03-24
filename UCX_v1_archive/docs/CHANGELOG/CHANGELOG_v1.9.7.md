# UCX v1.9.7 Changelog - Tier 2 Count Mismatch Auto-Fix

**Release Date**: 2026-03-11
**Focus**: Count Mismatch Auto-Fix for GATE-W003 and DIAG-W001

---

## Summary

This release extends the `--fix` flag to handle Tier 2 count mismatch warnings. When prose text claims a specific count (e.g., "5 requirements") but the actual element count differs, the fixer updates the prose to match reality.

---

## New Features

### 1. GATE-W003 Auto-Fix (Count Mismatch)

Fixes prose count claims that don't match actual element counts:

| Example | Before | After |
|---------|--------|-------|
| Requirements | "2 requirements" (actual: 39) | "39 requirements" |
| User Stories | "1 user story" (actual: 25) | "25 user stories" |
| Constraints | "5 constraints" (actual: 12) | "12 constraints" |

**Supported item types:**
- requirements, user stories, quality attributes
- business objectives, acceptance criteria
- constraints, assumptions, risks
- dependencies, stakeholders, items

### 2. DIAG-W001 Auto-Fix (Diagram Node Count)

Fixes prose claims about diagram node counts:

| Example | Before | After |
|---------|--------|-------|
| Text claim | "10 nodes" (diagram has 64) | "64 nodes" |
| Components | "10 components" (diagram has 51) | "51 components" |

---

## Usage

```bash
# Fix all fixable issues (Tier 1 + Tier 2 count mismatches)
ucx validate brd docs/01_BRD/BRD-01/ --fix

# Fix, generate report, and cleanup
ucx validate brd docs/01_BRD/BRD-01/ --fix --report --clean-reports
```

---

## Fixable Codes Summary (v1.9.7)

| Code | Tier | Issue | Auto-Fix |
|------|------|-------|----------|
| `BRD-E002` | 1 | Missing custom_fields | Adds document_type, artifact_type, layer |
| `BRD-E003` | 1 | Missing 'brd' tag | Adds to tags array |
| `BRD-E004` | 1 | Missing 'layer-1-artifact' tag | Adds to tags array |
| `BRD-E009` | 1 | Missing Document Control | Adds section (if none exists) |
| `BRD-W005` | 1 | Legacy development_status | Renames to status |
| `VAL-W002` | 1 | Legacy status value | Updates (active→production, draft→development) |
| **`GATE-W003`** | **2** | **Count mismatch** | **Updates prose count to match actual** |
| **`DIAG-W001`** | **2** | **Diagram node count** | **Updates prose to match diagram nodes** |

---

## Files Changed

| File | Lines | Description |
|------|-------|-------------|
| `ucx/validators/brd/fixer.py` | +75 | Added _fix_gate_w003 and _fix_diag_w001 methods |
| `ucx/version.py` | +6 | Version bump and changelog |

---

## Implementation Notes

### GATE-W003 Fix Logic

1. Parses issue context: "Count mismatch: stated X, found Y"
2. Searches for count patterns: `{X} requirements`, `{X} user stories`, etc.
3. Replaces with actual count: `{Y} requirements`
4. Only fixes first match to avoid over-correction

### DIAG-W001 Fix Logic

1. Parses issue context: "Text claims X nodes, diagram has Y nodes"
2. Searches for count patterns: `{X} nodes`, `{X} components`, etc.
3. Replaces with actual diagram count

---

## Related Documents

- [CHANGELOG_v1.9.6.md](./CHANGELOG_v1.9.6.md) - Structural auto-fix, report generation
- [validators/README.md](../ucx/validators/README.md) - Validator architecture
- [QUICK_START.md](./QUICK_START.md) - Usage examples
