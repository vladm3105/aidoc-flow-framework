---
name: IPLAN Verifier
description: Reviews EVAL-RPT verdict, marks IPLAN as Verified
agent: general
layer: 10_EVAL
trigger: Latest EVAL-RPT verdict = PASS
---

# IPLAN Verifier Playbook

## Purpose

Review the latest evaluation report for an IPLAN and mark it as Verified
(FINAL/FINITE) when all quality gates pass. This is the final step in the
IPLAN lifecycle before immutability.

## When to Use

- After an EVAL-RPT achieves PASS verdict
- Before marking an IPLAN as "Verified"
- When all P0 and P1 findings are resolved

## Inputs

- **Latest EVAL-RPT**: `EVAL-{NN}/reports/EVAL-{NN}-RPT-{NNN}.yaml`
- **IPLAN file**: `IPLAN-NN_*.yaml`
- **EVAL document**: `EVAL-{NN}/EVAL-{NN}.yaml`

## Outputs

- **IPLAN status update**: Completed → Verified
- **Verification record**: Added to IPLAN's verification_history

## Workflow

### Step 1: Read Latest RPT

```
1. Find latest RPT for this EVAL:
   - List EVAL-{NN}/reports/EVAL-{NN}-RPT-*.yaml
   - Sort by cycle number
   - Read the highest cycle number
2. Extract verdict:
   - verdict.overall
   - verdict.reasoning
   - findings[] (check all statuses)
3. Verify verdict = PASS
```

### Step 2: Verify Quality Gates

```
Check all gates:
1. verdict.overall == PASS
2. No OPEN findings with severity P0
3. No OPEN findings with severity P1
4. results.p0_critical.failed == 0
5. results.p1_high.failed == 0

If any gate fails:
  → Do NOT mark as Verified
  → Report which gates failed
  → Return to eval cycle (fix findings, re-run)
```

### Step 3: Verify IPLAN Completeness

```
1. Read IPLAN file
2. Check file_manifest:
   - All files status = DONE
   - All files verified = true
3. Check documentation:
   - traceability section complete
   - implementation_contracts documented
4. Check test coverage:
   - All test cases in EVAL are implemented
   - coverage_matrix summary = 100%
```

### Step 4: Record Verification

```
Add to IPLAN's verification_history:
  - verifier: "[agent or person]"
  - date: "YYYY-MM-DD"
  - eval_report: "EVAL-{NN}-RPT-{NNN}.yaml"
  - verdict: PASS
  - findings_resolved: N
  - cycles_to_resolve: N
  - notes: "All P0/P1 findings resolved"
```

### Step 5: Update IPLAN Status

```
1. Set IPLAN status: "Verified"
2. Set verification_date: current date
3. Set verified_by: verifier identity

Note: Verified = IMMUTABLE
  - No further changes allowed
  - To modify: create CHG + new IPLAN version
```

### Step 6: Update EVAL-00 Index

```
1. Update EVAL-00_index.md:
   - Mark IPLAN as Verified
   - Record final cycle count
   - Record resolution metrics
```

## Verification Checklist

- [ ] Latest RPT verdict = PASS
- [ ] No OPEN P0 findings
- [ ] No OPEN P1 findings
- [ ] All IPLAN files status = DONE
- [ ] All IPLAN files verified = true
- [ ] Coverage matrix = 100%
- [ ] Verification recorded in IPLAN
- [ ] IPLAN status = Verified
- [ ] EVAL-00 index updated

## Post-Verification

Once Verified:
- IPLAN is immutable
- EVAL document stays as-is (no new versions unless CHG)
- RPT files stay as historical record
- To make changes: create CHG → new IPLAN version → new EVAL version

## Example Verification Record

```yaml
verification_history:
  - verifier: "SDD Framework"
    date: "2026-10-29"
    eval_report: "EVAL-01-RPT-003.yaml"
    verdict: PASS
    findings_resolved: 4
    cycles_to_resolve: 3
    notes: "All P0/P1 findings resolved in 3 cycles"
```
