# CHANGELOG v1.21.6

**Release Date**: 2026-03-21
**Type**: Patch (Safety & Protection)

## Summary

This patch release adds source file protection to the validation workflow. Validation now analyzes structural issues and documents recommendations in validation reports without modifying the source PRD/BRD documents. This ensures validation remains a safe, read-only operation.

## Changes

### Validation Source Protection

**Problem**:
The `ucx validate` command, when run with auto-fix analysis enabled (default behavior), would execute the fixer which would write corrections directly to source markdown files. While this was designed for convenience, it conflicted with the principle that validation should be a safe, read-only analysis operation.

**Solution**:
- Snapshot source markdown files before running fix analysis
- Analyze what could be fixed and generate detailed recommendations
- Restore source files to their original state after analysis completes
- Keep only the validation report artifact as output

**Impact**:
- `ucx validate` now guarantees source document immutability
- Fix recommendations are fully documented in validation reports
- Users can review recommendations and apply fixes manually or via `ucx remediate`
- Consistent with remediation source protection pattern from v1.21.4
- Safe to run validation in CI/CD pipelines without side effects

### Code Changes

**File**: `ucx/cli/main.py`

**Modified command**: `validate()` (lines 1021-1250+)
- Added source file snapshotting before fixer execution
- Added source file restoration after fixer analysis completes
- Updated command docstring to document source protection behavior
- Added warning messages when source files are restored

**New behavior**:
```
Auto-fixing 3 structural issue(s)...
  ✓ GATE-E001: Missing custom_fields.document_type
  ◐ GATE-E002: Missing required tags
    LLM Task: Cross-verify tag alignment with PRD scope

⚠ Restored source files (validation report-only):
  → PRD-01_platform_architecture.md
Source documents unchanged. Fix recommendations documented in validation report only.
```

### Documentation

**Updated**:
- `docs/HOW_TO_USE.md` - Added "Source Protection (v1.21.6+)" section explaining read-only behavior
- `ucx/cli/main.py` docstring - Updated validate command documentation
- `README.md` - Added v1.21.6 release summary and version history entry

### Test Coverage

All existing validation tests passing. Source protection is implemented at the CLI layer and doesn't affect validator APIs.

## Usage Examples

```bash
# Validate with source protection (default)
ucx validate brd docs/01_BRD/BRD-01/
# Analyzes fixes, documents in report, source file unchanged

# Validate without fix analysis
ucx validate brd docs/01_BRD/BRD-01/ --no-fix
# Structure checks only, no fix analysis

# Review recommendations and apply fixes
cat docs/01_BRD/BRD-01/.precommit_validation_report.md
ucx remediate docs/01_BRD/BRD-01/ --from-review docs/01_BRD/BRD-01/.precommit_validation_report.md
```

## Backward Compatibility

✅ **Fully backward compatible**
- API behavior unchanged (validators still work same way)
- CLI behavior changed only in side effects (source no longer modified)
- Fix analysis and reporting workflow identical; output is the same
- All existing tests and scripts continue to work
- Users won't notice the change except source files remain untouched

## Known Limitations

- Source protection only applies to markdown files (`.md` extension)
- Reports and companion files are excluded from protection
- If fix analysis itself creates new files (rare), those remain in place
- Only applies to BRD validation (PRD/EARS/etc follow same validator pattern)

## Workflow Implications

**Before v1.21.6** (source modified by validation):
```
ucx validate → source updated → manual review → decide to fix
```

**After v1.21.6** (source protected):
```
ucx validate → recommendations in report → source unchanged
→ review recommendations → apply fixes with ucx remediate
→ source updated only when explicitly requested
```

## Next Steps (v1.22.0)

- Extend source protection pattern to other validators (PRD, EARS, etc.)
- Consider `--apply-fixes` flag to restore old behavior if needed
- Add telemetry to track how often source restoration occurs
- Document validation + remediation workflow improvements

## Migration Guide

No changes required. Existing workflows continue to work:
- Scripts that depend on validation reports: ✅ No change
- Pre-commit hooks using `--no-fix`: ✅ No change
- CI/CD pipelines with `ucx validate`: ✅ No change
- Manual source modifications after validation: Must use `ucx remediate` now

## Related Issues

- Closes: Source protection consistency (validation should match remediation pattern)
- Related to v1.21.4 remediation source protection feature

## Contributors

UCX Team - v1.21.6 release
