---
name: IPLAN Validator
description: Validates IPLAN implementation correctness, runs tests, and records findings
agent: general
layer: 08_IPLAN
trigger: IPLAN status = "Completed"
---

# IPLAN Validator Playbook

## Purpose

Validate that an IPLAN's implementation is correct by running tests, checking code quality, and recording any findings. This playbook enforces the quality gates before an IPLAN can be marked as Verified.

## When to Use

- After an IPLAN reaches "Completed" status
- Before marking an IPLAN as "Verified"
- When re-validating after fixes

## Inputs

- **IPLAN file**: The IPLAN to validate
- **Validation template**: `IPLAN-VERIFY-TEMPLATE.yaml`
- **Test commands**: From IPLAN's `execution_commands.validation`

## Outputs

- **Validation report**: `IPLAN-NN_VALIDATION_REPORT.yaml`
- **Findings list**: P0-P3 severity findings
- **Recommendation**: PASS/FAIL/PARTIAL

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
1. Assign finding ID (FINDING-001, FINDING-002, ...)
2. Classify severity:
   - P0: Test failure, security issue, data corruption
   - P1: Logic error, resilience gap
   - P2: Hardening, edge case
   - P3: Code quality, documentation
3. Record file:line reference
4. Describe what was wrong
5. Document fix applied (if any)
```

### Step 5: Generate Report

```
1. Use IPLAN-VERIFY-TEMPLATE.yaml as base
2. Fill in:
   - validation_summary (file completion, findings count)
   - validation_findings (all findings)
   - severity_classification (P0-P3 definitions)
   - cross_iplan_impact (if fixes affect other IPLANs)
   - file_manifest (files modified during validation)
3. Save as IPLAN-NN_VALIDATION_REPORT.yaml
```

### Step 6: Provide Recommendation

```
Based on findings:
- If P0_count == 0 AND P1_count == 0:
  recommendation = "Verified" (ready for final status)
- If P0_count > 0:
  recommendation = "FAIL" (must fix P0 before Verified)
- If P1_count > 0:
  recommendation = "PARTIAL" (should fix P1 before Verified)
```

## Severity Classification

| Severity | Label | Description | Gate |
|----------|-------|-------------|------|
| P0 | Critical | Test failure, runtime panic, data corruption, security breach | Blocks Verified status |
| P1 | High | Incorrect behavior, resilience gap, business logic error | Should fix before Verified |
| P2 | Medium | Missing feature, incomplete handling, hardening gap | Can defer to follow-up IPLAN |
| P3 | Low | Code quality, naming, documentation | No gate |

## Validation Checklist

- [ ] IPLAN status is "Completed"
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Lint passes with no errors
- [ ] All file_manifest entries are DONE
- [ ] All file_manifest entries have verified: true
- [ ] No P0 findings
- [ ] No P1 findings (or documented exceptions)
- [ ] Validation report generated

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
