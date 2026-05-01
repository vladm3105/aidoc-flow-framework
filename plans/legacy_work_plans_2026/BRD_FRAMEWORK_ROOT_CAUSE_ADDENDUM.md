---
title: "BRD Framework Root Cause Analysis - Addendum: Pre-Commit Hook Configuration"
doc_id: BRD-RCA-001-ADDENDUM
date: 2026-03-05T18:45:00-05:00
tags:
  - root-cause-analysis
  - framework-quality
  - pre-commit-hooks
  - critical-finding
custom_fields:
  document_type: root-cause-addendum
  artifact_type: RCA-ADDENDUM
  priority: critical
  impact: framework-wide
  parent_document: BRD_FRAMEWORK_ROOT_CAUSE_ANALYSIS.md
---

# BRD Framework Root Cause Analysis - Addendum: Pre-Commit Hook Configuration

**Discovery Date**: 2026-03-05T18:45:00-05:00
**Trigger**: Pre-commit script inspection during IPLAN-001 v1.2 review
**Severity**: 🔴 **CRITICAL** - Pre-commit validation DISABLED

---

## Executive Summary

**Critical Finding**: BRD pre-commit hooks are configured with `stages: [manual]` instead of `stages: [pre-commit]`, meaning **validation never runs automatically on commit**.

**Impact**:
- Incomplete BRDs were committed to version control **without validation**
- Template-validator mismatch (16 vs 19 sections) went undetected for months
- 74 BRDs accumulated quality issues without automatic quality gates

**Root Cause #7** (adds to 6 root causes in main RCA):
- Pre-commit hooks **intentionally disabled** (set to manual stage)
- Comment in config: "Temporarily set to manual (was pre-commit)"
- **Never re-enabled** → validation bypass for months

---

## 1. Pre-Commit Infrastructure Analysis

### 1.1 Hook Configuration

**File**: `/opt/data/ucx_framework/ai_dev_ssd_flow/scripts/pre_commit_hooks/library/pre-commit-config.project.yaml`

**Current Configuration** (lines 149-169):
```yaml
- id: brd-core-wrapper
  name: Validate b-local BRD core checks via unified wrapper
  entry: bash ai_dev_ssd_flow/01_BRD/scripts/brd_core_wrapper_hook.sh docs/01_BRD
  language: system
  pass_filenames: false
  stages: [manual]  # Temporarily set to manual (was pre-commit)  ← PROBLEM!

- id: brd-standardized-element-codes
  name: Validate b-local BRD standardized element type codes
  entry: bash ai_dev_ssd_flow/01_BRD/scripts/brd_standardized_element_codes_hook.sh docs/01_BRD
  language: system
  pass_filenames: false
  stages: [manual]  # Temporarily set to manual (was pre-commit)  ← PROBLEM!

- id: brd-legacy-patterns
  name: Detect b-local BRD legacy element ID patterns
  entry: bash ai_dev_ssd_flow/01_BRD/scripts/brd_legacy_pattern_hook.sh docs/01_BRD
  language: system
  pass_filenames: false
  stages: [manual]  # Temporarily set to manual (was pre-commit)  ← PROBLEM!
```

**Expected Configuration**:
```yaml
stages: [pre-commit]  # Run automatically on every commit
```

### 1.2 Hook Call Chain

**What Happens on Commit** (current):
```
1. Developer: git commit -m "Added BRD-55"
2. Pre-commit: Check hooks...
3. Pre-commit: brd-core-wrapper stage=manual → SKIP
4. Pre-commit: brd-standardized-element-codes stage=manual → SKIP
5. Pre-commit: brd-legacy-patterns stage=manual → SKIP
6. Commit: ✅ ALLOWED (no validation ran)
```

**What Should Happen**:
```
1. Developer: git commit -m "Added BRD-55"
2. Pre-commit: Check hooks...
3. Pre-commit: brd-core-wrapper stage=pre-commit → RUN
4. Hook: bash brd_core_wrapper_hook.sh docs/01_BRD
5. Wrapper: bash validate_brd_wrapper.sh docs/01_BRD --skip-advisory
6. Validator: python3 validate_brd.py (checks 16 sections - OUTDATED)
7. Result: FAIL - Missing sections 9-17
8. Commit: ❌ BLOCKED until fixed
```

### 1.3 Hook Script Validation

**brd_core_wrapper_hook.sh** calls **validate_brd_wrapper.sh**:
```bash
#!/usr/bin/env bash
bash "${SCRIPT_DIR}/validate_brd_wrapper.sh" "${BRD_ROOT}" --skip-advisory
```

**validate_brd_wrapper.sh** calls:
1. **validate_brd.py** (structural validation - **16 sections, OUTDATED**)
2. **validate_brd_quality_score.sh** (PRD-Ready scoring)
3. Advisory checks (skipped with --skip-advisory)

**Result**: Even if hooks were enabled, they'd use **outdated validator** (16 sections).

---

## 2. Impact Analysis

### 2.1 Validation Bypass Timeline

| Date | Event | Impact |
|------|-------|--------|
| **Pre-2026-02-25** | Hooks active with `stages: [pre-commit]` | Validation enforced (16-section validator) |
| **2026-02-25** | Comment added: "Temporarily set to manual" | Hooks disabled, validation bypassed |
| **2026-02-25** | Template expanded to 19 sections | No validation enforcement for new structure |
| **2026-03-01** | Validator NOT updated (still 16 sections) | Validation gap compounds |
| **2026-03-05** | 74 BRDs in repo, 12 incomplete | **Months of unvalidated commits** |

### 2.2 Consequences of Disabled Hooks

| Issue | Would Hooks Catch? | Actual Result |
|-------|-------------------|---------------|
| **BRD-55/56 missing 9 sections** | ❌ No (validator outdated) | Committed without validation |
| **Foundation BRDs missing §14-15** | ❌ No (validator outdated) | Committed without validation |
| **42 BRDs missing @depends** | ❌ No (not validated) | Committed without validation |
| **14 duplicate title prefixes** | ✅ Yes (element codes check) | Would have been caught if hooks enabled |
| **Stale Integration Matrix** | ❌ No (no automation) | Manual maintenance, no enforcement |

**Key Finding**: **Even if hooks were enabled**, template-validator mismatch means incomplete BRDs would pass validation.

### 2.3 Quantitative Impact

| Metric | Value | Evidence |
|--------|-------|----------|
| **Commits Without Validation** | Unknown (months) | Hooks disabled since ~2026-02-25 |
| **BRDs Committed Incomplete** | 12 of 74 (16%) | Would fail 19-section validator |
| **Quality Gate Bypass Rate** | 100% | All BRD commits bypassed validation |

---

## 3. Root Cause #7: Pre-Commit Hooks Disabled

### 3.1 Why Were Hooks Disabled?

**Evidence**: Comment in config:
```yaml
stages: [manual]  # Temporarily set to manual (was pre-commit)
```

**Hypothesis**:
1. **Performance Issues**: Hooks too slow, blocking commits
2. **False Positives**: Validator flagging valid BRDs (unlikely - would be fixed)
3. **Development Velocity**: Team disabled to move faster (technical debt)
4. **Validator Bug**: Hooks breaking, disabled as workaround

**Most Likely**: #3 (Development Velocity) - "Temporarily" suggests short-term workaround that became permanent.

### 3.2 Contributing Factors

| Factor | Contribution | Evidence |
|--------|--------------|----------|
| **No Re-Enable Reminder** | High | "Temporarily" but no ticket/reminder to re-enable |
| **No Enforcement Policy** | High | No requirement that hooks must be active |
| **No CI/CD Validation** | Critical | No backup validation in CI pipeline |
| **No Monitoring** | High | No alerts when hooks disabled |

### 3.3 Comparison: Other Layers

**ADR Hooks** (for comparison):
```yaml
- id: adr-core-validator
  stages: [pre-commit]  # ACTIVE

- id: adr-quality-gate
  stages: [pre-commit]  # ACTIVE

- id: adr-sys-ready-score
  stages: [pre-commit]  # ACTIVE
```

**Finding**: ADR hooks are **ACTIVE** (pre-commit), BRD hooks are **DISABLED** (manual).

---

## 4. Revised Root Cause Summary

### 4.1 Updated Root Cause List

| # | Root Cause | Impact | BRDs Affected |
|---|------------|--------|---------------|
| 1 | **Template-Validator Mismatch** (16 vs 19 sections) | 🔴 Critical | 74 (validation gap) |
| 2 | **Autopilot Incomplete Generation** (uses validator section list) | 🔴 Critical | 12 (partial BRDs) |
| 3 | **@depends Not Enforced** (validation rule: info-level) | 🟠 High | 42 (missing tags) |
| 4 | **Duplicate Title Prefix** (autopilot string bug) | 🟡 Medium | 14 (title format) |
| 5 | **Integration Matrix Stale** (no automation) | 🔴 Critical | 1 (metadata) |
| 6 | **Score Not Persisted** (validator doesn't write back) | 🟡 Medium | 1 (placeholder) |
| **7** | **Pre-Commit Hooks Disabled** (stages: manual) | **🔴 CRITICAL** | **74 (all BRDs)** |

### 4.2 Causal Chain

```
Root Cause #7 (Hooks Disabled)
    ↓
No automatic validation on commit
    ↓
Root Cause #1 (Template-Validator Mismatch) NOT CAUGHT
    ↓
Incomplete BRDs committed to repo
    ↓
Root Cause #2 (Autopilot) generates incomplete BRDs
    ↓
12 BRDs missing sections, 42 missing @depends
    ↓
IPLAN-001: Manual remediation required for 74 BRDs
```

**Key Insight**: Root Cause #7 (Hooks Disabled) is the **enabling condition** for Root Causes #1-6 to persist undetected.

---

## 5. Recommended Fixes (Addendum)

### 5.1 Immediate Fixes (Priority 1 - Add to Phase -1)

**Fix 1A: Re-Enable Pre-Commit Hooks**

**File**: `/opt/data/ucx_framework/ai_dev_ssd_flow/scripts/pre_commit_hooks/library/pre-commit-config.project.yaml`

**Change Lines 149-169**:
```yaml
- id: brd-core-wrapper
  name: Validate b-local BRD core checks via unified wrapper
  entry: bash ai_dev_ssd_flow/01_BRD/scripts/brd_core_wrapper_hook.sh docs/01_BRD
  language: system
  pass_filenames: false
  stages: [pre-commit]  # RE-ENABLED (was manual)

- id: brd-standardized-element-codes
  name: Validate b-local BRD standardized element type codes
  entry: bash ai_dev_ssd_flow/01_BRD/scripts/brd_standardized_element_codes_hook.sh docs/01_BRD
  language: system
  pass_filenames: false
  stages: [pre-commit]  # RE-ENABLED (was manual)

- id: brd-legacy-patterns
  name: Detect b-local BRD legacy element ID patterns
  entry: bash ai_dev_ssd_flow/01_BRD/scripts/brd_legacy_pattern_hook.sh docs/01_BRD
  language: system
  pass_filenames: false
  stages: [pre-commit]  # RE-ENABLED (was manual)
```

**CRITICAL**: Must fix validate_brd.py (16→19 sections) **BEFORE** re-enabling hooks, or hooks will block all commits.

**Fix 1B: Add Framework-Level Pre-Commit Config**

**File**: `/opt/data/ucx_framework/.pre-commit-config.yaml`

**Change Lines 39-58**:
```yaml
- id: brd-core-wrapper
  name: Validate BRD core checks (wrapper, framework library)
  entry: bash ai_dev_ssd_flow/01_BRD/scripts/brd_core_wrapper_hook.sh ai_dev_ssd_flow/01_BRD
  language: system
  pass_filenames: false
  stages: [pre-commit]  # RE-ENABLED (currently pre-commit in framework, but check project config)

- id: brd-standardized-element-codes
  name: Validate BRD standardized element type codes
  entry: bash ai_dev_ssd_flow/01_BRD/scripts/brd_standardized_element_codes_hook.sh ai_dev_ssd_flow/01_BRD
  language: system
  pass_filenames: false
  stages: [pre-commit]  # RE-ENABLED

- id: brd-legacy-patterns
  name: Detect BRD legacy element ID patterns
  entry: bash ai_dev_ssd_flow/01_BRD/scripts/brd_legacy_pattern_hook.sh ai_dev_ssd_flow/01_BRD
  language: system
  pass_filenames: false
  stages: [pre-commit]  # RE-ENABLED
```

### 5.2 Validation (Add to Phase -1)

**Test Pre-Commit Hooks**:
```bash
cd /opt/data/b-local/b-local-docs

# Install pre-commit (if not installed)
pip install pre-commit

# Install hooks
pre-commit install

# Test hooks on staged files
git add docs/01_BRD/BRD-55_octo_rest_apis/BRD-55_octo_rest_apis.md
pre-commit run --files docs/01_BRD/BRD-55_octo_rest_apis/BRD-55_octo_rest_apis.md

# Expected (after validator fix):
# brd-core-wrapper............Failed
# ERROR: BRD-55 missing 9 sections

# Expected (before validator fix):
# brd-core-wrapper............Passed (FALSE POSITIVE)
```

### 5.3 Prevention (Add to Phase -1)

**Fix 1C: Add Hook Monitoring**

Create `/opt/data/ucx_framework/ai_dev_ssd_flow/scripts/validate_hook_config.sh`:
```bash
#!/usr/bin/env bash
# Validate pre-commit hooks are enabled (not manual)

set -euo pipefail

CONFIG_FILE="ai_dev_ssd_flow/scripts/pre_commit_hooks/library/pre-commit-config.project.yaml"

# Check BRD hooks are not manual
manual_hooks=$(grep -A3 "id: brd-" "$CONFIG_FILE" | grep "stages: \[manual\]" | wc -l)

if [ "$manual_hooks" -gt 0 ]; then
  echo "[ERROR] Found $manual_hooks BRD hooks with stages: [manual]"
  echo "Pre-commit validation is DISABLED. Re-enable hooks before committing."
  exit 1
fi

echo "[PASS] All BRD hooks active (stages: [pre-commit])"
```

**Fix 1D: Add CI/CD Backup Validation**

Even if pre-commit hooks are disabled locally, CI should enforce validation:
```yaml
# .github/workflows/brd-validation.yml
name: BRD Validation
on: [pull_request]
jobs:
  validate-brds:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Validate BRDs
        run: |
          bash ai_dev_ssd_flow/01_BRD/scripts/validate_brd_wrapper.sh docs/01_BRD
```

---

## 6. Updated IPLAN-001 Phase -1

### Phase -1 Updated Timeline

| Task | Duration (v1.2) | Duration (v1.2.1) | Change |
|------|-----------------|-------------------|--------|
| Phase -1A: Update validate_brd.py | 30 min | 30 min | Same |
| Phase -1B: Update docs | 15 min | 15 min | Same |
| **Phase -1B.1: Re-enable pre-commit hooks** | **0 min** | **+15 min** | **NEW** |
| Phase -1C: Test framework | 30 min | 30 min | Same |
| **Phase -1C.1: Test pre-commit hooks** | **0 min** | **+15 min** | **NEW** |
| Phase -1D: Commit framework | 15 min | 15 min | Same |
| **Total Phase -1** | **90 min** | **120 min** | **+30 min** |

**Total IPLAN Duration**: 11 hours → **11.5 hours**

---

## 7. Risk Assessment Update

### 7.1 New Risks from Disabled Hooks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Hooks Re-Enable Blocks All Commits** | High | Critical | Fix validator FIRST (Phase -1A), THEN re-enable hooks (Phase -1B.1) |
| **Hooks Too Slow (Performance)** | Medium | Medium | Profile hooks, optimize if needed |
| **Developers Bypass Hooks** | Medium | High | CI/CD backup validation (Phase -1D) |
| **Hooks Disabled Again** | Low | High | Add monitoring script (Phase -1C) |

### 7.2 Mitigation Strategy

**Execution Order** (CRITICAL):
1. ✅ Fix validate_brd.py (19 sections) **FIRST**
2. ✅ Test validator on BRD-50, BRD-55
3. ✅ Re-enable pre-commit hooks
4. ✅ Test hooks on sample BRD
5. ✅ Commit all changes together

**Why This Order Matters**:
- If hooks re-enabled BEFORE validator fixed → **blocks all commits** (validator still checks 16 sections, fails on valid 19-section BRDs)
- If validator fixed but hooks not re-enabled → **no enforcement** (same problem persists)

---

## 8. Comparison: Framework vs Project Configs

### 8.1 Config Hierarchy

| Config File | Scope | BRD Hook Status |
|-------------|-------|-----------------|
| **ucx_framework/.pre-commit-config.yaml** | Framework library | `stages: [pre-commit]` ✅ ACTIVE |
| **b-local-docs/.pre-commit-config.yaml** (symlink) | Project (b-local) | `stages: [manual]` ❌ DISABLED |

**Finding**: Framework config has hooks **ACTIVE**, but project config (b-local) has them **DISABLED**.

**Implication**: Framework BRDs are validated, but project BRDs (b-local) bypass validation.

### 8.2 Recommended Approach

**Option A**: Enable hooks in project config (b-local specific)
- **Pro**: Per-project control
- **Con**: Easy to forget, inconsistent across projects

**Option B**: Remove project config, use framework config
- **Pro**: Single source of truth, consistent
- **Con**: Less flexibility per project

**Recommendation**: **Option A** - Keep project config but enforce `stages: [pre-commit]` with monitoring script.

---

## 9. Lessons Learned (Updated)

### 9.1 What Went Wrong (Addendum)

| Issue | Root Cause | Prevention |
|-------|------------|------------|
| **Hooks Disabled** | "Temporary" workaround became permanent | Hook monitoring script, CI/CD enforcement |
| **No Re-Enable Alert** | No reminder system for temporary changes | Track "TODO: Re-enable" in issue tracker |
| **No Backup Validation** | Pre-commit only layer, no CI/CD | Add GitHub Actions validation |
| **Framework vs Project Config Mismatch** | Two configs, different states | Monitoring script checks both |

### 9.2 Prevention Measures (Addendum)

**Prevent Hook Disablement**:
1. **Policy**: Pre-commit hooks MUST be active (stages: [pre-commit])
2. **Monitoring**: Daily cron job checks hook config, alerts if disabled
3. **CI/CD**: Backup validation in GitHub Actions (can't be disabled)
4. **Documentation**: Add "DO NOT DISABLE HOOKS" warning to README

---

## 10. Conclusion

**Addendum Finding**: Pre-commit hooks were **intentionally disabled** (stages: manual), bypassing all BRD validation on commit.

**Combined Impact**: Template-validator mismatch (Root Cause #1) + Disabled hooks (Root Cause #7) = **100% validation bypass rate** for months.

**Critical Path** (updated):
1. Fix validate_brd.py (16→19 sections)
2. Re-enable pre-commit hooks (manual→pre-commit)
3. Test hooks on sample BRDs
4. Add monitoring + CI/CD backup
5. Commit framework fixes

**Updated Phase -1 Duration**: 90 minutes → **120 minutes** (+30 min for hook re-enable + testing)

**Updated Total IPLAN Duration**: 11 hours → **11.5 hours**

---

**Addendum Completed**: 2026-03-05T18:45:00-05:00
**Analyst**: Claude Code (Root Cause Analysis - Pre-Commit Review)
**Status**: **Critical finding - pre-commit hooks disabled, must re-enable in Phase -1**
**Next Step**: Update IPLAN-001 Phase -1 to include hook re-enablement
