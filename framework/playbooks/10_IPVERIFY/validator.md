---
name: IPLAN Validator
description: Runs an eval cycle against a Completed IPLAN per its EVAL document, records an EVAL-RPT report
agent: general
layer: 10_EVAL
trigger: IPLAN status = "Completed"
---

# IPLAN Validator Playbook

> Flow note (CHG-08 #672): this playbook drives the EVAL-RPT flow — one eval
> cycle per validation pass, recorded as `EVAL-{NN}-RPT-{NNN}.yaml` authored
> from `EVAL-REPORT-TEMPLATE.yaml`. The legacy `IPLAN-VERIFY-TEMPLATE.yaml`
> flow (`IPLAN-NN_VALIDATION_REPORT.yaml`) is superseded; its template file
> remains until the last live readers retarget (see #662).

## Purpose

Validate that an IPLAN's implementation is correct by running the eval cycle defined in its EVAL document and recording an EVAL-RPT report. This playbook enforces the quality gates before an IPLAN can be marked as Verified.

## When to Use

- After an IPLAN reaches "Completed" status
- Before marking an IPLAN as "Verified"
- When re-validating after fixes

## Inputs

- **IPLAN file**: The IPLAN to validate (status "Completed")
- **EVAL document**: `EVAL-{NN}/EVAL-{NN}.yaml` — defines what to test
- **Report template**: `EVAL-REPORT-TEMPLATE.yaml`
- **Test commands**: From IPLAN's `execution_commands.validation`

## Outputs

- **Eval report**: `EVAL-{NN}/reports/EVAL-{NN}-RPT-{NNN}.yaml`
- **Findings list**: P0-P2 severity findings (finding IDs `F-NNN`)
- **Verdict**: PASS | PASS-WITH-NOTES | FAIL | BLOCKED

## Workflow

### Step 1: Read IPLAN

```
1. Read IPLAN file (IPLAN-NN_*.yaml)
2. Extract metadata:
   - iplan_id
   - status (should be "Completed")
   - component
   - file_manifest.files
3. Verify status is "Completed"
```

### Step 2: Run Tests

```
1. Extract test commands from execution_commands.validation
2. Run unit tests:
   - Execute: <unit_test_command>
   - Record: pass/fail, duration
3. Run integration tests:
   - Execute: <integration_test_command>
   - Record: pass/fail, duration
4. Run lint:
   - Execute: <lint_command>
   - Record: pass/fail, findings
```

### Step 3: Check File Manifest

```
1. Read file_manifest.files
2. For each file:
   - Verify file exists on disk
   - Verify status is DONE
   - Verify verified is true
3. Count completion rate
```

### Step 4: Record Findings

```
For each test failure or issue:
1. Assign finding ID (F-001, F-002, ...)
2. Classify severity:
   - P0: Test failure, security issue, data corruption
   - P1: Logic error, resilience gap
   - P2: Hardening, edge case
3. Record file:line reference
4. Describe what was wrong
5. Document fix applied (if any)
```

### Step 5: Generate Report

```
1. Use EVAL-REPORT-TEMPLATE.yaml as base
2. Fill in:
   - §3 results (totals from this run)
   - §4 test_results (one entry per EVAL test case, `EVAL.NN.SS.xxxx` IDs)
   - §5 findings (one per failure, `F-NNN` IDs, P0-P2)
   - §9 verdict (PASS | PASS-WITH-NOTES | FAIL | BLOCKED with reasoning)
3. Save as EVAL-{NN}/reports/EVAL-{NN}-RPT-{NNN}.yaml (next cycle number)
```

### Step 6: Record Verdict

```
Based on findings (REPORT §9 rules):
- If P0_count == 0 AND P1_count == 0:
  verdict = "PASS" (ready for Verified)
- If P0 pass but some P1 fail with documented workaround:
  verdict = "PASS-WITH-NOTES"
- If P0_count > 0:
  verdict = "FAIL" (must fix P0, then run the next cycle)
- If infrastructure unavailable:
  verdict = "BLOCKED"
```

## Severity Classification

| Severity | Label | Description | Gate |
|----------|-------|-------------|------|
| P0 | Critical | Test failure, runtime panic, data corruption, security breach | Blocks Verified status |
| P1 | High | Incorrect behavior, resilience gap, business logic error | Should fix before Verified |
| P2 | Medium | Missing feature, incomplete handling, hardening gap | Can defer to follow-up IPLAN |

## Validation Checklist

- [ ] IPLAN status is "Completed"
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Lint passes with no errors
- [ ] All file_manifest entries are DONE
- [ ] All file_manifest entries have verified: true
- [ ] No P0 findings
- [ ] No P1 findings (or documented exceptions)
- [ ] EVAL-RPT report generated (`EVAL-{NN}-RPT-{NNN}.yaml`)

## Example Usage

```bash
# Run validator on IPLAN-15
./scripts/verify_iplan_status.sh IPLAN-15 --validate

# Generate validation report
./scripts/generate_validation_report.sh IPLAN-15
```

## Output Example

```yaml
validation_summary:
  original_iplan: "IPLAN-15"
  validation_result: "PASS"
  files_declared: 22
  files_done: 22
  completion_rate: "100%"
  findings_count: 0
  p0_count: 0
  p1_count: 0
  p2_count: 0
  p3_count: 0

recommendations:
  status_recommendation: "Verified"
  reasoning: "All tests pass, lint clean, no findings"
```
