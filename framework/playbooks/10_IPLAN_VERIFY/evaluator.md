---
name: EVAL Executor
description: Runs eval cycles against IPLANs, creates EVAL-RPT reports
agent: general
layer: 10_EVAL
trigger: IPLAN status = "Completed" or bug_fix_verification
---

# EVAL Executor Playbook

## Purpose

Execute an eval cycle against an IPLAN's EVAL document and produce a self-contained
EVAL-RPT report. This playbook handles all cycle types: initial_eval, bug_fix_verification,
chg_verification, scheduled, and pre_deploy.

## When to Use

- After an IPLAN reaches "Completed" status (initial_eval)
- After code fixes for findings from a previous cycle (bug_fix_verification)
- After a CHG modifies the IPLAN or its code (chg_verification)
- Periodic regression checks (scheduled)
- Before branch promotion (pre_deploy)

## Inputs

- **EVAL document**: `EVAL-{NN}/EVAL-{NN}.yaml`
- **Previous RPT** (if cycle > 1): `EVAL-{NN}/reports/EVAL-{NN}-RPT-{NNN}.yaml`
- **Test commands**: From EVAL's execution_plan

## Outputs

- **EVAL-RPT**: `EVAL-{NN}/reports/EVAL-{NN}-RPT-{NNN}.yaml`
- **Verdict**: PASS / PASS-WITH-NOTES / FAIL / BLOCKED

## Workflow

### Step 1: Read EVAL Document

```
1. Read EVAL-{NN}/EVAL-{NN}.yaml
2. Extract metadata:
   - eval_id (EVAL-NN)
   - owning_iplan (IPLAN-NN)
   - iplan_version
   - eval_version
   - test_cases[]
3. Determine cycle number:
   - List existing RPT files in EVAL-{NN}/reports/
   - New cycle = max(existing cycles) + 1
   - If no existing RPTs, cycle = 1
```

### Step 2: Determine Trigger

```
If cycle == 1:
  trigger = initial_eval
  baseline_report = null
  previous_cycle_date = null
  cycles_since_last_eval = null
Else:
  Read previous RPT
  If CHG modified IPLAN since last run:
    trigger = chg_verification
  Elif code changes since last run:
    trigger = bug_fix_verification
  Else:
    trigger = scheduled
  baseline_report = previous RPT filename
  previous_cycle_date = previous RPT run_date
  cycles_since_last_eval = 1 (or more)
```

### Step 3: Run Tests

```
1. For each test_case in EVAL document:
   - Execute test command
   - Record: pass/fail/skip, duration, error_message
   - Record: test_file location
2. Run quality checks:
   - go vet (if Go project)
   - lint checks
   - build verification
```

### Step 4: Classify Findings

```
For each failed test case:
1. Assign finding ID: F-{NNN} (sequential within this RPT)
2. Classify severity (from EVAL document priority):
   - P0: p0-critical tests that fail
   - P1: p1-high tests that fail
   - P2: p2-medium tests that fail
3. Record eval_case_id (the EVAL test case ID)
4. Record source_id (upstream BDD/TDD source)
5. Record error_message (actual assertion failure)
6. Record test_file (where the test is)
7. Determine regression status:
   - If cycle == 1: regression = false (all new)
   - If cycle > 1 and test passed in previous cycle: regression = true
   - If cycle > 1 and test failed in previous cycle: regression = false (carried)
8. Determine cycles_open:
   - If new or carried: cycles_open = previous cycles_open + 1
   - If regression: cycles_open = 1
```

### Step 5: Record Resolved Findings

```
If cycle > 1:
  For each finding that was OPEN in previous RPT:
    If test now passes:
      Add to resolved_this_cycle:
        - finding_id: (from previous RPT)
        - resolved_in_cycle: (current cycle number)
        - fix_commit: (if available)
```

### Step 6: Compute Results

```
results:
  total = count(test_cases)
  passed = count(passing tests)
  failed = count(failing tests)
  skipped = count(skipped tests)
  pass_rate = (passed / (total - skipped)) * 100

  by_severity:
    p0_critical: { total, passed, failed }
    p1_high: { total, passed, failed }
    p2_medium: { total, passed, failed }

  by_regression:
    new_failures = count(failures where regression=false AND cycle=1 OR passed last time)
    carried_failures = count(failures where failed this AND last cycle)
    resolved = count(previously failing that now pass)
    never_tested = count(skipped)
```

### Step 7: Set Verdict

```
If p0_critical.failed > 0:
  verdict = FAIL
  reasoning = "N P0-critical failures"
  blockers = [list of P0 finding IDs]
Elif p1_high.failed > 0:
  verdict = PASS-WITH-NOTES
  reasoning = "All P0 pass, N P1 failures with workarounds"
Else:
  verdict = PASS
  reasoning = "All P0 and P1 pass"
```

### Step 8: Generate RPT

```
1. Use EVAL-RPT-TEMPLATE.yaml as base
2. Fill all sections:
   - document_control (cycle, trigger, status, baseline)
   - iplan_context (snapshot of IPLAN state)
   - results (computed in Step 6)
   - findings (from Step 4)
   - resolved_this_cycle (from Step 5)
   - coverage (from test execution)
   - quality_thresholds (actual vs target)
   - verdict (from Step 7)
   - evidence (CI URLs, artifacts)
   - linkage (eval, iplan, upstream refs)
3. Save as EVAL-{NN}-RPT-{NNN}.yaml
```

### Step 9: Update EVAL-00 Index

```
1. Update EVAL-00_index.md:
   - Latest report for this EVAL
   - Latest verdict
   - Total cycles
   - Open findings count
```

## Severity Classification

| Severity | Label | Description | Gate |
|----------|-------|-------------|------|
| P0 | Critical | Test failure in p0-critical case | Blocks PASS verdict |
| P1 | High | Test failure in p1-high case | Should fix before PASS |
| P2 | Medium | Test failure in p2-medium case | Can defer |

## Verdict Criteria

| Verdict | Condition |
|---------|-----------|
| PASS | p0_critical.failed == 0 AND p1_high.failed == 0 |
| PASS-WITH-NOTES | p0_critical.failed == 0 AND p1_high.failed > 0 |
| FAIL | p0_critical.failed > 0 |
| BLOCKED | Infrastructure unavailable, cannot run tests |

## Example RPT Entry

```yaml
id: "EVAL-01-RPT-001"
title: "Eval Report — EVAL-01 Cycle 1"

document_control:
  report_type: eval_report
  eval_id: "EVAL-01"
  iplan_id: "IPLAN-01"
  iplan_version: "2.0"
  eval_version: "1.0"
  cycle: 1
  run_date: "2026-10-27T14:30:00"
  trigger: initial_eval
  status: FAIL

results:
  total: 18
  passed: 13
  failed: 4
  skipped: 1
  pass_rate: 76.5

findings:
  - id: "F-001"
    eval_case_id: "EVAL.01.03.a7f3"
    source_id: "BDD.01.TC-01.4"
    name: "Idempotency replay returns stale data"
    severity: P0
    status: OPEN
    error_message: "expected cached response, got nil"
    test_file: "internal/platform/port_router_test.go"
    regression: false
    cycles_open: 1

verdict:
  overall: FAIL
  reasoning: "2 P0-critical failures"
  blockers: ["F-001", "F-002"]
```
