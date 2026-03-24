# CHANGELOG v1.15.6 - Chairperson Findings Extraction Fix

**Release Date**: 2026-03-14

## Bug Fix

### Problem

Chairperson `REM-*` findings in review reports showed only the priority ("P1", "P0") instead of the actual finding description:

```markdown
### P1 High Priority Findings
- **[REM-P1-001]** P1 *(from chairperson)*  ← WRONG
- **[REM-P1-002]** P1 *(from chairperson)*
```

### Root Cause

The `_extract_title()` method in `review_memory.py` used a pattern that extracted the **first column after the ID** in table format:

```python
# Old pattern - captures "P1" (Priority column)
table_pattern = rf'\|\s*{finding_id}\s*\|\s*([^|]+)'
```

But the Chairperson's manifest table has **8 columns**:
```
| ID | Priority | Category | Status | Fixer | Target File | Target Section | Description |
```

The Description is in the **last column**, not the second.

### Solution

Updated `_extract_title()` to:
1. Detect `REM-*` IDs (Chairperson findings)
2. Extract the entire row and split by `|`
3. Return the **last column** (Description)

```python
# New logic for REM-* findings
if finding_id.startswith("REM-"):
    row_pattern = rf'\|\s*{finding_id}\s*\|([^\n]+)'
    # ... split columns and get last one
    description = columns[-1]  # ← Correct!
```

### Result

```markdown
### P1 High Priority Findings
- **[REM-P1-001]** Partial disbursement handling undefined when Paynet delivers <100% *(from chairperson)*  ← CORRECT
```

## Additional Improvements

- Table extraction now handles multi-column formats for all personas
- Skips short columns (Priority, Status, etc.) when searching for description
- Finds first column with >20 characters as fallback

## Files Modified

| File | Changes |
|------|---------|
| `ucx/core/review_memory.py` | Fixed `_extract_title()` method |
| `ucx/version.py` | Updated to v1.15.6 |

## Testing

```python
# Before fix
context = "| REM-P1-001 | P1 | [CAT:functional] | ... | Description |"
_extract_title(context, "REM-P1-001")  # Returns: "P1" ❌

# After fix
_extract_title(context, "REM-P1-001")  # Returns: "Description" ✅
```

## Impact

- Affects all review reports generated with UCX v1.11.0+ (when Chairperson manifest was added)
- Re-run `ucx review` on documents to regenerate reports with correct findings
