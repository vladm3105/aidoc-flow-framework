---
name: RPT Generator
description: Generates EVAL-RPT reports from test execution output
agent: general
layer: 10_EVAL
trigger: After test execution completes
---

# RPT Generator Playbook

## Purpose

Generate self-contained EVAL-RPT reports from test execution output. This playbook
transforms raw test results into the standardized EVAL-RPT format with all context
inline.

## When to Use

- After running tests for an IPLAN's EVAL document
- When producing a new eval cycle report
- When automating RPT generation in CI

## Inputs

- **EVAL document**: `EVAL-{NN}/EVAL-{NN}.yaml`
- **Test output**: JSON, JUnit XML, or go test -json output
- **Previous RPT** (if cycle > 1): for regression detection
- **Cycle metadata**: trigger type, run date

## Outputs

- **EVAL-RPT**: `EVAL-{NN}/reports/EVAL-{NN}-RPT-{NNN}.yaml`

## Workflow

### Step 1: Determine Cycle Number

```
1. List existing RPT files in EVAL-{NN}/reports/
2. Extract cycle numbers from filenames (RPT-NNN)
3. New cycle = max(existing) + 1
4. If no existing: cycle = 1
```

### Step 2: Parse Test Output

```
For each test in output:
  1. Match to EVAL test case by:
     - test function name → test_case_id
     - or test file + line → test_case_id
  2. Record result: passed / failed / skipped
  3. Record duration_ms
  4. If failed: record error_message
  5. Match to source_id (BDD/TDD) from EVAL document
```

### Step 3: Classify by Severity

```
For each test case in EVAL document:
  - priority p0-critical → severity P0
  - priority p1-high → severity P1
  - priority p2-medium → severity P2

Count by severity:
  p0_critical: { total, passed, failed }
  p1_high: { total, passed, failed }
  p2_medium: { total, passed, failed }
```

### Step 4: Detect Regressions (if cycle > 1)

```
Read previous RPT:
  For each finding in previous RPT with status = OPEN:
    If test now passes:
      → Add to resolved_this_cycle
    If test still fails:
      → Add to carried_failures, increment cycles_open

  For each test that was PASS in previous RPT:
    If test now fails:
      → Add to findings as new regression
```

### Step 5: Compute Results

```
total = count(all test cases)
passed = count(passed)
failed = count(failed)
skipped = count(skipped)
pass_rate = (passed / (total - skipped)) * 100

by_regression:
  new_failures = count(new failures)
  carried_failures = count(carried failures)
  resolved = count(resolved from previous)
  never_tested = count(skipped)
```

### Step 6: Set Verdict

```
If p0_critical.failed > 0:
  overall = FAIL
  blockers = [P0 finding IDs]
Elif p1_high.failed > 0:
  overall = PASS-WITH-NOTES
  blockers = []
Else:
  overall = PASS
  blockers = []
```

### Step 7: Generate RPT YAML

```
1. Start from EVAL-RPT-TEMPLATE.yaml
2. Fill document_control:
   - eval_id, iplan_id, iplan_version, eval_version
   - cycle, run_date, trigger, status
   - baseline_report, previous_cycle_date
3. Fill iplan_context:
   - Snapshot from IPLAN file
4. Fill results:
   - Computed in Step 5
5. Fill findings:
   - One per failed test, with all context
6. Fill resolved_this_cycle:
   - From Step 4
7. Fill coverage:
   - What was tested vs what exists
8. Fill quality_thresholds:
   - Actual vs target with verdict
9. Fill verdict:
   - From Step 6
10. Fill evidence:
    - CI URLs, artifact paths
11. Fill linkage:
    - eval_id, iplan_id, upstream refs
```

### Step 8: Validate RPT

```
Before writing:
1. Check all required fields populated
2. Check pass_rate computed correctly
3. Check finding IDs are unique within this RPT
4. Check no external file references in findings
5. Check verdict matches findings (no contradictions)
```

### Step 9: Write RPT

```
Save as: EVAL-{NN}/reports/EVAL-{NN}-RPT-{NNN}.yaml
Verify file is valid YAML
```

## CI Integration

### go test -json output

```bash
# Run tests and capture JSON output
go test ./cmd/... ./internal/... -json > test-output.json

# Generate RPT from JSON (when scripts/generate-rpt.sh is implemented)
# scripts/generate-rpt.sh EVAL-01 test-output.json
```

### JUnit XML output

```bash
# Run tests and capture JUnit XML
npm run test -- --reporter=junit > test-results.xml

# Generate RPT from JUnit (when scripts/generate-rpt.sh is implemented)
# scripts/generate-rpt.sh EVAL-02 test-results.xml
```

## Example Generation

```bash
# Manual RPT generation (when scripts/generate-rpt.sh is implemented)
# scripts/generate-rpt.sh \
#   --eval EVAL-01 \
#   --cycle 2 \
#   --trigger bug_fix_verification \
#   --input test-output.json \
#   --output EVAL-01/reports/EVAL-01-RPT-002.yaml
```

**Note**: `scripts/generate-rpt.sh` is not yet implemented. Currently, RPT files are
authored manually following the EVAL-RPT-TEMPLATE.yaml structure. The script is planned
for future implementation to automate RPT generation from CI test output.
