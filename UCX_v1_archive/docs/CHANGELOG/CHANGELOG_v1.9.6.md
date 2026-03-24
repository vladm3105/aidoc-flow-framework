# UCX v1.9.6 Changelog - Auto-Fix and Report Management

**Release Date**: 2026-03-11
**Focus**: Structural Auto-Fix, Report Generation, Report Cleanup

---

## Summary

This release adds deterministic auto-fixing capabilities to `ucx validate`, allowing structural issues to be fixed without AI. Combined with report generation and cleanup options, this enables a complete fix-validate-report workflow in a single command.

---

## New Features

### 1. Auto-Fix Structural Issues (`--fix`)

Added `--fix` flag to automatically fix common structural validation errors:

| Error Code | Issue | Auto-Fix |
|------------|-------|----------|
| `BRD-E002` | Missing custom_fields | Adds document_type, artifact_type, layer |
| `BRD-E003` | Missing 'brd' tag | Adds to tags array |
| `BRD-E004` | Missing 'layer-1-artifact' tag | Adds to tags array |
| `BRD-E009` | Missing Document Control | Adds section (if none exists) |
| `BRD-W005` | Legacy development_status | Renames to status |
| `VAL-W002` | Legacy status value | Updates (active→production, draft→development) |

**Usage:**
```bash
ucx validate brd docs/01_BRD/BRD-01/ --fix
ucx validate brd docs/01_BRD/BRD-01/ --fix --tier1-only
```

**Files Changed:**
- `UCX/ucx/validators/brd/fixer.py` - NEW: BRDFixer class (488 lines)
- `UCX/ucx/cli/main.py` - Added --fix flag and integration

### 2. Auto-Report Generation (`--report`)

Added `--report` flag to automatically generate a validation report to the document directory after fixing:

```bash
ucx validate brd docs/01_BRD/BRD-01/ --fix --report
# → Creates: BRD-01.V_validation_report_v001.md
```

### 3. Combined Fix-Report-Cleanup Workflow

The `--fix`, `--report`, and `--clean-reports` flags can be combined for a complete workflow:

```bash
ucx validate brd docs/01_BRD/BRD-01/ --fix --report --clean-reports
```

**Workflow:**
1. Run validation
2. Apply fixes to source files
3. Re-validate to show updated state
4. Write new validation report
5. Clean up old reports (keep only latest)

**With version retention:**
```bash
ucx validate brd docs/01_BRD/BRD-01/ --fix --report --clean-reports --keep-versions 2
```

---

## v1.9.5 Changes (Included)

### Validation Report Cleanup

Added `--clean-reports` and `--keep-versions` flags:

```bash
# Clean up old reports, keep only latest
ucx validate brd docs/01_BRD/BRD-01/ --clean-reports

# Keep 3 most recent reports
ucx validate brd docs/01_BRD/BRD-01/ --clean-reports --keep-versions 3
```

---

## Bug Fixes

### Document Control Regex Fix

**Issue**: Document Control section regex was stopping at `|---` (table separator) instead of only `\n---` (horizontal rule).

**Fix**: Changed regex from `(?=## \d+\.|\Z|---)` to `(?=## \d+\.|\Z|\n---)`.

**File**: `UCX/ucx/validators/brd/structure.py`

---

## Files Changed (Summary)

| File | Lines | Description |
|------|-------|-------------|
| `ucx/validators/brd/fixer.py` | +488 | NEW: BRDFixer class with fix methods |
| `ucx/cli/main.py` | +72 | --fix, --report flags, cleanup refactor |
| `ucx/validators/brd/structure.py` | +3 | Document Control regex fix |
| `ucx/version.py` | +10 | Version bump and changelog |

---

## CLI Reference

### validate Command Options

| Option | Description |
|--------|-------------|
| `--fix` | Auto-fix structural issues (metadata, tags, Document Control) |
| `--report` | With --fix: auto-generate report to document directory |
| `--clean-reports` | Clean up old validation reports |
| `--keep-versions N` | Number of reports to keep (default: 1) |
| `--tier1-only` | Run only Tier 1 checks |
| `--strict` | Treat warnings as errors |
| `-o, --output PATH` | Write report to specific path |
| `--format [text|json]` | Output format |

### Common Workflows

```bash
# Quick validation (console only)
ucx validate brd docs/01_BRD/BRD-01/ --tier1-only

# Fix issues and see results
ucx validate brd docs/01_BRD/BRD-01/ --fix

# Complete workflow: fix, report, cleanup
ucx validate brd docs/01_BRD/BRD-01/ --fix --report --clean-reports

# CI/CD: strict validation with JSON output
ucx validate brd docs/01_BRD/BRD-01/ --strict --format json
```

---

## Migration Notes

### For Existing Documents

The auto-fix feature is safe to use on existing documents:

1. **Metadata fixes** - Only adds missing fields, doesn't modify existing
2. **Tag fixes** - Only adds missing tags, preserves existing
3. **Document Control** - Only adds if no section exists (skips if present)
4. **Status migration** - Renames development_status to status

### Recommended Workflow

```bash
# 1. Preview issues (no fix)
ucx validate brd docs/01_BRD/BRD-01/ --tier1-only

# 2. Fix and validate
ucx validate brd docs/01_BRD/BRD-01/ --fix --report --clean-reports

# 3. Review changes
git diff docs/01_BRD/BRD-01/

# 4. Commit if satisfied
git add docs/01_BRD/BRD-01/ && git commit -m "fix(brd): Apply structural fixes"
```

---

## Version Synchronization

| Component | Old Version | New Version |
|-----------|-------------|-------------|
| UCX Framework | 1.9.4 | 1.9.6 |

---

## Related Documents

- [CHANGELOG_v1.9.4.md](./CHANGELOG_v1.9.4.md) - QA codes and pattern compliance
- [validators/README.md](../ucx/validators/README.md) - Validator architecture
- [QUICK_START.md](./QUICK_START.md) - Usage examples
