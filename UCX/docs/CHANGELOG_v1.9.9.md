# UCX v1.9.9 Changelog - UCRem Project Path Resolution & Prior Review Reconciliation

**Release Date**: 2026-03-12
**Focus**: UCRem prompt path resolution, project auto-detection fixes, and prior review reconciliation

---

## Summary

This release fixes critical path resolution issues in the UCRem (remediation) phase, improves project directory auto-detection for both `review` and `remediate` commands, and adds **Prior Review Reconciliation** to prevent re-flagging resolved findings.

---

## New Features

### 6. Prior Review Reconciliation (UCR Prompt Enhancement)

**Problem**: When running a new review after applying fixes, personas would re-flag findings that were already resolved. The Chairperson would count all P0/P1 findings without checking if they had been fixed, resulting in artificially low scores.

**Solution**: Updated UCR prompts to implement prior review reconciliation:

#### Fact Checker (Persona 10) - Updated

New responsibilities:
- Check prior review reports for previously flagged findings
- Verify resolution status of each prior finding against current document
- Only confirm findings as P0/P1 if genuinely UNRESOLVED

New output table:
```markdown
**Prior Review Findings - Resolution Status**:
| Prior Finding ID | Finding Description | Prior Priority | Current Status | Evidence Location |
|------------------|---------------------|----------------|----------------|-------------------|
| P0-1 | KYC tier upgrade path | P0 | ✅ RESOLVED | Section 6.1 - "[quote]" |
| P0-2 | SAR SLA undefined | P0 | ❌ UNRESOLVED | Still missing |
```

Resolution markers:
| Marker | Meaning |
|--------|---------|
| ✅ RESOLVED | Finding is now addressed in document |
| ❌ UNRESOLVED | Still missing |
| ⚠️ PARTIAL | Partially addressed, needs more detail |

#### Chairperson (Persona 11) - Updated

New responsibilities:
- Review Fact Checker's and Auditor's verification status
- EXCLUDE resolved findings from P0/P1 counts
- Only count genuinely UNRESOLVED findings in score calculation

Updated score formula:
```
PRD-Ready Score = 100 - (UNRESOLVED_P0 × 10) - (UNRESOLVED_P1 × 3) - (P2 × 1)
```

New output section:
```markdown
**Resolved Since Prior Review** (Progress from last review):
| Prior Finding | Priority | Resolution Status | Evidence |
|---------------|----------|-------------------|----------|
| P0-1: KYC tier upgrade | P0 | ✅ RESOLVED | Section 6.1 |
```

#### Auditor (Persona 2) - Updated

New output table:
```markdown
**Prior Review Findings - Verification Status**:
| Prior Finding ID | Description | Prior Priority | Current Status | Evidence |
|------------------|-------------|----------------|----------------|----------|
| P0-1 | [desc] | P0 | ✅ RESOLVED | Section X.X - "[exact quote]" |
```

**Impact**: Reviews now correctly recognize applied fixes, resulting in accurate scores that reflect actual document quality.

---

## Bug Fixes

### 1. UCRem Prompt Path Resolution

**Problem**: UCRem looked for prompts only at `{prompt_dir}/ucrem/` but project-specific prompts were at `docs/UCX/remediation/`.

**Fix**: `_load_prompt()` now checks multiple locations in priority order:
1. `{project_dir}/docs/UCX/remediation/UCRem_PROMPT_{TYPE}_PROJECT.md`
2. `{project_dir}/docs/UCX/remediation/UCRem_PROMPT_{TYPE}_BEELOCAL.md`
3. `{project_dir}/docs/UCX/remediation/UCRem_PROMPT_{TYPE}.md`
4. `{prompt_dir}/ucrem/UCRem_PROMPT_{TYPE}.md` (framework fallback)

**Error message improved**: Now lists all searched paths when prompt not found.

### 2. Fixer Skills Mapping Fix

**Problem**: `_load_fixer_skills()` mapping referenced `integration_expert` but `FIXER_SKILLS` uses `integration_lead`.

**Fix**: Updated mapping to use `integration_lead`:

```python
fixer_names = {
    "architect": "Architect Fixer",
    "auditor": "Auditor Fixer",
    "qa_lead": "QA Fixer",
    "integration_lead": "Integration Fixer",  # Fixed from integration_expert
    "devils_advocate": "Devil's Advocate",
}
```

### 3. Project Directory Auto-Detection Bug

**Problem**: With relative paths (e.g., `docs/01_BRD/BRD-01`), the auto-detection loop exited before checking the current working directory (`.`).

**Root Cause**: The loop condition `while search_path.parent != search_path` exits when reaching `.` (current directory) because `.parent` equals `.`.

**Fix**:
1. Resolve path to absolute before searching: `search_path.resolve()`
2. Changed loop structure to check BEFORE testing parent condition

```python
# Before (buggy with relative paths)
while search_path.parent != search_path:
    if (search_path / "docs" / "UCX").exists():
        ...
    search_path = search_path.parent

# After (correct)
search_path = (doc_path if doc_path.is_dir() else doc_path.parent).resolve()
while True:
    if (search_path / "docs" / "UCX").exists():
        ...
    if search_path.parent == search_path:
        break  # Reached filesystem root
    search_path = search_path.parent
```

**Commands fixed**: Both `ucx review` and `ucx remediate` now correctly auto-detect project directories.

### 4. Fixer Skills Project Path Support

**Enhancement**: `_load_fixer_skills()` now checks project-specific skill directory before framework:

```python
skill_dirs = []
if project_dir:
    skill_dirs.append(project_dir / "docs" / "UCX" / "skills")
skill_dirs.append(self.config.get_skill_dir())
```

### 5. UCRem Report Output Path

**Change**: UCRem reports now write to the **document folder** by default, not the review report folder.

**Before**: `{review_report_dir}/BRD_UCRem_REPORT.md`
**After**: `{doc_path}/{DOC-ID}.UCRem_report.md`

**Example**:
```bash
ucx remediate docs/01_BRD/BRD-01/BRD-01.UCR_review_report_v001.md docs/01_BRD/BRD-01/
# Output: docs/01_BRD/BRD-01/BRD-01.UCRem_report.md
```

**Benefits**:
- Report is co-located with the document being remediated
- Consistent naming pattern with other reports (`{DOC-ID}.UCRem_report.md`)
- Document ID is extracted from path (e.g., `BRD-01` from `BRD-01_platform_architecture`)
- CLI now prints: `Remediation report written to: {path}`

---

## Files Changed

| File | Changes |
|------|---------|
| `ucx/api/remediation.py` | Fixed `_load_prompt()` and `_load_fixer_skills()` path resolution; returns (fixes, output_path) tuple |
| `ucx/cli/main.py` | Fixed auto-detection in `review` and `remediate` commands; prints report path |
| `ucx/version.py` | Version bump to 1.9.9 |
| `docs/UCX/review/UCR_PROMPT_BRD_PROJECT.md` | Updated Fact Checker, Chairperson, and Auditor for prior review reconciliation |

---

## Usage

```bash
# UCRem now works correctly with project-specific prompts
cd /path/to/project
ucx remediate docs/01_BRD/BRD-01.UCR_review_report_v001.md docs/01_BRD/BRD-01

# Auto-detects project directory from relative paths
ucx review brd docs/01_BRD/BRD-01
# Output: Auto-detected project directory: /path/to/project
```

---

## Related Documents

- [CHANGELOG_v1.9.8.md](./CHANGELOG_v1.9.8.md) - Tier 2 diagram auto-fix
- [CHANGELOG_v1.9.7.md](./CHANGELOG_v1.9.7.md) - Count mismatch auto-fix
- [QUICK_START.md](./QUICK_START.md) - Usage examples

---

*Generated for UCX Framework v1.9.9*
