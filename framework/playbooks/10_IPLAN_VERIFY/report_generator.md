---
name: Report Generator
description: Generates validation reports using IPLAN-VERIFY-TEMPLATE
agent: general
layer: 08_IPLAN
trigger: Validation requested
---

# Report Generator Playbook

## Purpose

Generate comprehensive validation reports for IPLANs using the IPLAN-VERIFY-TEMPLATE. This playbook documents the validation process, findings, and recommendations.

## When to Use

- After running validation tests
- When documenting validation results
- For audit trail and compliance

## Inputs

- **IPLAN file**: The IPLAN being validated
- **Test results**: Unit, integration, lint results
- **Findings**: Any issues discovered

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
   - title
   - component
   - status
   - file_manifest.files
   - execution_commands.validation
3. Extract test commands for execution
```

### Step 2: Run Tests (Optional)

```
If --validate flag is set:
1. Run unit tests from execution_commands.validation
2. Run integration tests
3. Run lint checks
4. Record pass/fail and duration
```

### Step 3: Check File Completion

```
1. Read file_manifest.files
2. For each file:
   - Check if file exists on disk
   - Check status (should be DONE)
   - Check verified (should be true)
3. Calculate completion rate
```

### Step 4: Record Findings

```
For each issue found:
1. Assign finding ID (FINDING-001, FINDING-002, ...)
2. Classify severity (P0-P3)
3. Record file:line reference
4. Describe issue
5. Document fix (if applied)
6. Mark verified (if fixed)
```

### Step 5: Generate Report

```
1. Use IPLAN-VERIFY-TEMPLATE.yaml as base
2. Fill in sections:
   - metadata
   - document_control
   - validation_summary
   - validation_findings
   - severity_classification
   - cross_iplan_impact
   - file_manifest
   - validation_commands
   - session_handoff
   - recommendations
3. Save as IPLAN-NN_VALIDATION_REPORT.yaml
```

### Step 6: Provide Recommendation

```
Based on validation results:
- validation_result = "PASS" if:
  - All tests pass
  - All files complete
  - No P0/P1 findings
- validation_result = "FAIL" if:
  - Any test fails
  - Any P0 finding exists
- validation_result = "PARTIAL" if:
  - Some tests fail but P0 == 0
  - P1 findings exist but documented

status_recommendation:
- "Verified" if validation_result == "PASS"
- "Completed" if validation_result == "FAIL" or "PARTIAL"
```

## Report Structure

```yaml
metadata:
  document_type: "validation-report"
  validating_iplan: "IPLAN-NN"
  validation_date: "YYYY-MM-DD"

document_control:
  iplan_id: "IPLAN-NN_VALIDATION"
  subtype: audit_fix
  source_spec: "Validation of IPLAN-NN"
  status: Completed

validation_summary:
  original_iplan: "IPLAN-NN"
  validation_result: "PASS" | "FAIL" | "PARTIAL"
  files_declared: N
  files_done: N
  completion_rate: "X%"
  findings_count: N
  p0_count: N
  p1_count: N
  p2_count: N
  p3_count: N

validation_findings:
  findings: []

severity_classification:
  P0: { label, description, gate }
  P1: { label, description, gate }
  P2: { label, description, gate }
  P3: { label, description, gate }

cross_iplan_impact:
  original_iplan: "IPLAN-NN"
  impacts: []

file_manifest:
  files: []

validation_commands:
  unit_tests: { command, result, duration }
  integration_tests: { command, result, duration }
  lint: { command, result, duration }

session_handoff:
  sessions: [...]

recommendations:
  status_recommendation: "Verified" | "Completed"
  reasoning: "..."
  next_steps: [...]
```

## Example Usage

```bash
# Generate validation report for IPLAN-15
./scripts/generate_validation_report.sh IPLAN-15

# Generate report + fix IPLAN
./scripts/generate_validation_report.sh IPLAN-15 --fix-found
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

recommendations:
  status_recommendation: "Verified"
  reasoning: "All tests pass, lint clean, no findings"
  next_steps:
    - "Mark IPLAN-15 as Verified"
    - "Close validation IPLAN"
```

## Severity Reference

| Severity | Label | Description | Gate |
|----------|-------|-------------|------|
| P0 | Critical | Test failure, security issue, data corruption | Blocks Verified |
| P1 | High | Logic error, resilience gap | Should fix before Verified |
| P2 | Medium | Hardening, edge case | Can defer to follow-up |
| P3 | Low | Code quality, documentation | No gate |

## Key Rules

- **Use IPLAN-VERIFY-TEMPLATE**: Always use the official template
- **Record all findings**: Even P3 findings should be documented
- **Provide clear reasoning**: Explain why PASS/FAIL/PARTIAL
- **Include next steps**: Guide the user on what to do next
