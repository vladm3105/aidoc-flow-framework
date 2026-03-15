# UCX v1.16.1 - Single-File Validation Reports

**Release Date**: 2026-03-15
**Status**: Complete

## Summary

UCX v1.16.1 changes the validation report format from versioned files to a single file with a meaningful name that overwrites on each run. This eliminates the accumulation of versioned reports and provides a cleaner repository history.

## Changes

### Validation Report Naming

| Aspect | Before (v1.16.0) | After (v1.16.1) |
|--------|------------------|-----------------|
| **Filename** | `{doc_id}.V_validation_report_v{NNN}.md` | `precommit_validation_report.md` |
| **Versioning** | Auto-incrementing (v001, v002, ...) | Single file, overwrites |
| **Accumulation** | Creates new file each run | Replaces existing file |
| **Typical Count** | 25+ files over time | 1 file always |

### Example

```bash
# Before (v1.16.0)
ls docs/01_BRD/
# 01.V_validation_report_v001.md
# 01.V_validation_report_v002.md
# ...
# 01.V_validation_report_v025.md  (25 files!)

# After (v1.16.1)
ls docs/01_BRD/
# precommit_validation_report.md  (1 file)
```

### CLI Behavior

```bash
# Run validation (creates/overwrites single report)
ucx validate brd docs/01_BRD --tier1-only
# → Creates: docs/01_BRD/precommit_validation_report.md

# Run again (overwrites same file)
ucx validate brd docs/01_BRD --tier1-only
# → Overwrites: docs/01_BRD/precommit_validation_report.md
```

### Clean Reports Flag

The `--clean-reports` flag now cleans up **legacy** versioned reports only:

```bash
# Clean up legacy versioned reports (if migrating from older UCX)
ucx validate brd docs/01_BRD --clean-reports
# Output: Cleaned up legacy validation reports: docs/01_BRD
#         Removed: 25 files (156.2 KB)
```

## Files Changed

| File | Changes |
|------|---------|
| `ucx/cli/main.py` | Changed report filename to `precommit_validation_report.md`, removed versioning logic |
| `ucx/validators/brd/__init__.py` | Added `precommit_validation_report.md` to `NON_BRD_FILE_PATTERNS` |
| `ucx/validators/common/file_utils.py` | Updated `COMPANION_REPORT_PATTERN` to recognize new filename |
| `ucx/version.py` | Updated to 1.16.1 |

## Migration

### Automatic Migration

No action required. New validations automatically use the new format.

### Clean Up Legacy Reports

To remove accumulated legacy versioned reports:

```bash
# Option 1: Use UCX built-in cleanup
ucx validate brd docs/01_BRD --clean-reports

# Option 2: Manual cleanup
rm docs/01_BRD/*.V_validation_report_v*.md
```

### Pre-commit Hook

No changes needed. The pre-commit hook continues to work:

```yaml
# .pre-commit-config.yaml (unchanged)
- id: ucx-brd-validate
  name: UCX BRD Validation (Tier 1)
  entry: bash -c 'source /opt/data/docs_flow_framework/.venv/bin/activate && ucx validate brd docs/01_BRD --tier1-only'
  language: system
  files: ^docs/01_BRD/.*\.md$
  stages: [pre-commit]
```

## Benefits

1. **Cleaner Repository**: No accumulation of versioned validation reports
2. **Smaller History**: Fewer files to track in git
3. **Meaningful Name**: `precommit_validation_report.md` clearly indicates purpose
4. **CI/CD Friendly**: Single file path for artifact collection
5. **Reduced Clutter**: Document directories stay clean

## Backward Compatibility

- Legacy patterns (`*.V_validation_report_v*.md`) are still recognized and excluded from BRD validation
- `--clean-reports` flag cleans up legacy reports
- Review reports (`*.UCR_review_report_v*.md`) continue to use versioned naming (these benefit from history tracking)

---

*See also*: [CHANGELOG_v1.16.0.md](CHANGELOG_v1.16.0.md), [README.md](../README.md)
