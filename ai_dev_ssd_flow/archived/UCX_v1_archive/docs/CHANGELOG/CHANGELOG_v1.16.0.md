# UCX v1.16.0 - Auto-Detection of Latest Review Report

**Release Date**: 2026-03-15
**Status**: Complete

## Summary

UCX v1.16.0 simplifies the remediation workflow by auto-detecting the latest UCR review report, eliminating the need to specify exact report versions.

## Changes

### Remediation Command Improvements

| Aspect | Before | After |
|--------|--------|-------|
| **CLI Usage** | `ucx remediate BRD-01.UCR_review_report_v003.md docs/01_BRD/BRD-01` | `ucx remediate docs/01_BRD/BRD-01` |
| **Report Discovery** | Required explicit path | Auto-detects `*.UCR_review_report_v*.md` |
| **Override Option** | N/A | `--report` / `-r` to specify explicit report |

### New CLI Syntax

```bash
# Auto-detect latest review report (RECOMMENDED)
ucx remediate docs/01_BRD/BRD-01

# Explicit report path (override auto-detect)
ucx remediate docs/01_BRD/BRD-01 -r BRD-01.UCR_review_report_v002.md
ucx remediate docs/01_BRD/BRD-01 --report BRD-01.UCR_review_report_v002.md
```

### New Utilities

**File**: `ucx/utils/file_ops.py`

| Function | Purpose |
|----------|---------|
| `find_latest_review_report(doc_path)` | Finds most recent `*.UCR_review_report_v*.md` file |
| `find_latest_remediation_report(doc_path)` | Finds most recent `*.UCRem_*.md` file |

### API Changes

**UCRemPhase.generate_fixes() Signature Change**:

```python
# Before (v1.15.x)
fixes, report_path = ucrem.generate_fixes(review_report, doc_path)

# After (v1.16.0)
fixes, report_path = ucrem.generate_fixes(doc_path, review_report=None)
# review_report is optional - auto-detected if not provided
```

**New Attribute**:
- `UCRemPhase.last_review_report` - Path to the review report used (auto-detected or explicit)

## Usage Examples

### CLI Auto-Detection

```bash
# Directory contains:
# - BRD-01.UCR_review_report_v001.md
# - BRD-01.UCR_review_report_v002.md
# - BRD-01.UCR_review_report_v003.md

ucx remediate docs/01_BRD/BRD-01
# Output: Using latest review report: BRD-01.UCR_review_report_v003.md
```

### Python API

```python
from ucx import UCRemPhase, UCXConfig

config = UCXConfig()
ucrem = UCRemPhase(config)

# Auto-detect latest review report
fixes, report_path = ucrem.generate_fixes(Path("docs/01_BRD/BRD-01"))
print(f"Used report: {ucrem.last_review_report}")

# Explicit report (override)
fixes, report_path = ucrem.generate_fixes(
    Path("docs/01_BRD/BRD-01"),
    review_report=Path("BRD-01.UCR_review_report_v002.md")
)
```

## Files Changed

| File | Changes |
|------|---------|
| `ucx/cli/main.py` | Updated remediate command with auto-detection |
| `ucx/utils/file_ops.py` | Added `find_latest_review_report()`, `find_latest_remediation_report()` |
| `ucx/api/remediation.py` | Changed argument order, added `last_review_report` attribute |
| `ucx/version.py` | Updated to 1.16.0 |
| `docs/HOW_TO_USE.md` | Updated remediation examples |
| `remediation/UCRem_PERSONAS.md` | Updated CLI usage documentation |

## Migration

**CLI Users**: No changes required. Old syntax with explicit report path still works.

**API Users**: Update argument order if calling `generate_fixes()` directly:

```python
# Before
ucrem.generate_fixes(review_report_path, doc_path)

# After
ucrem.generate_fixes(doc_path, review_report=review_report_path)
```

## Benefits

1. **Simpler CLI**: No need to remember or look up exact report version numbers
2. **Fewer Errors**: Eliminates typos in report filenames
3. **Workflow Alignment**: Matches how users typically work (always use latest report)
4. **Override Available**: Explicit `--report` flag for edge cases

---

*See also*: [HOW_TO_USE.md](HOW_TO_USE.md), [UCRem_PERSONAS.md](../remediation/UCRem_PERSONAS.md)
