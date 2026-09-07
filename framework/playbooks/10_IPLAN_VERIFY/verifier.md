---
name: IPLAN Verifier
description: Reviews validation results and marks IPLAN as Verified (final/finite status)
agent: general
layer: 08_IPLAN
trigger: Validation report = "PASS"
---

# IPLAN Verifier Playbook

## Purpose

Review validation results and mark an IPLAN as Verified (final/finite status). This is the final step in the IPLAN lifecycle before immutability.

## When to Use

- After validation report shows "PASS"
- When all P0/P1 findings are resolved
- Before closing the validation workflow

## Inputs

- **IPLAN file**: The IPLAN to verify
- **Validation report**: `IPLAN-NN_VALIDATION_REPORT.yaml`
- **Validation findings**: All findings resolved

## Outputs

- **Updated IPLAN**: Status changed to "Verified"
- **Validation reference**: validated_by, validation_date, findings_resolved
- **IPLAN-00 index**: Status history updated

## Workflow

### Step 1: Read Validation Report

```
1. Read validation report (IPLAN-NN_VALIDATION_REPORT.yaml)
2. Check validation_result:
   - If "PASS": proceed to Step 2
   - If "FAIL": stop, fix P0 findings first
   - If "PARTIAL": review P1 findings, decide if acceptable
3. Verify all findings are resolved:
   - findings_count == 0 OR all findings.verified == true
```

### Step 2: Verify Immutability Rules

```
1. Check current IPLAN status:
   - Must be "Completed" (not "Verified" already)
   - Cannot be "Draft", "Approved", or "In Progress"
2. Check validation reference:
   - validated_by should reference validation IPLAN
   - validation_date should be set
   - findings_resolved should be accurate
```

### Step 3: Update IPLAN Status

```
1. Update document_control.status:
   - From: "Completed"
   - To: "Verified"
2. Add validation metadata:
   - validated_by: "IPLAN-XX" (validation IPLAN)
   - validation_date: "YYYY-MM-DD"
   - findings_resolved: N
3. Update last_updated timestamp
```

### Step 4: Update IPLAN-00 Index

```
1. Read IPLAN-00_index.yaml
2. Find IPLAN entry in registry.plans
3. Update status:
   - From: "Completed"
   - To: "Verified"
4. Add validation fields:
   - validated_by: "IPLAN-XX"
   - validation_date: "YYYY-MM-DD"
   - findings_resolved: N
5. Append to status_history:
   - from: "Completed"
   - to: "Verified"
   - date: "YYYY-MM-DD"
   - reason: "Validation passed, all P0/P1 findings resolved"
```

### Step 5: Close Validation IPLAN

```
1. Update validation IPLAN status:
   - From: "Draft" or "In Progress"
   - To: "Completed"
2. Add completion notes:
   - All findings resolved
   - Original IPLAN verified
3. Update validation IPLAN's last_updated
```

### Step 6: Notify

```
1. Log verification completion
2. Update project tracker (if applicable)
3. Notify stakeholders (if configured)
```

## Immutability Rules

Once an IPLAN reaches "Verified" status:

- **No fields may be modified**
- **No files may be added or removed**
- **Status cannot be changed back**

To modify a Verified IPLAN:

1. Create a CHG record documenting the need for changes
2. Create a NEW IPLAN (IPLAN-NN+1) that references the original
3. The original IPLAN remains in "Verified" status as historical record

## Verification Checklist

- [ ] Validation report shows "PASS"
- [ ] All P0 findings resolved (count == 0)
- [ ] All P1 findings resolved (or documented exceptions)
- [ ] IPLAN status is "Completed" (not already "Verified")
- [ ] Validation reference exists (validated_by, validation_date)
- [ ] findings_resolved count is accurate
- [ ] IPLAN-00 index updated
- [ ] Validation IPLAN closed as "Completed"

## Example Usage

```bash
# Verify IPLAN-15 after validation passes
# (Manual process or via agent)

# 1. Read validation report
cat docs/sdd/08_IPLAN/IPLAN-15_VALIDATION_REPORT.yaml

# 2. Update IPLAN status to Verified
# Edit IPLAN-15 file:
#   status: Verified
#   validated_by: "IPLAN-16"
#   validation_date: "2026-09-05"
#   findings_resolved: 19

# 3. Update IPLAN-00 index
# Edit IPLAN-00_index.yaml:
#   status: Verified
#   validation_date: "2026-09-05"

# 4. Close validation IPLAN
# Edit IPLAN-16 file:
#   status: Completed
```

## Output Example

```yaml
# IPLAN-15 after verification
document_control:
  iplan_id: "IPLAN-15"
  status: Verified  # FINAL/FINITE
  validated_by: "IPLAN-16"
  validation_date: "2026-09-05"
  findings_resolved: 19

# IPLAN-00 index entry
- id: "IPLAN-15"
  status: Verified
  validated_by: "IPLAN-16"
  validation_date: "2026-09-05"
  findings_resolved: 19
```

## Status Transition

```
Completed → Verified (FINAL/FINITE)
              ↑
              │ Cannot be changed
              │ Need CHG + new IPLAN
```

## Key Rules

- **Verified = Immutable**: No changes allowed after Verified
- **CHG Required**: To modify Verified IPLAN, create CHG + new IPLAN
- **Validation First**: All P0/P1 findings must be resolved
- **Historical Record**: Original IPLAN stays in Verified status forever
