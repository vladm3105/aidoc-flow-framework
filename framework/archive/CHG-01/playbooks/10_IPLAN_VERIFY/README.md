# 10_IPLAN_VERIFY — IPLAN Verification Playbooks

## Purpose

Playbooks for verifying IPLAN implementation correctness and generating validation reports. These playbooks enforce the IPLAN status lifecycle and ensure quality before marking IPLANs as Verified.

## Playbooks

| Playbook | Role | Purpose |
|----------|------|---------|
| `validator.md` | IPLAN Validator | Validates IPLAN implementation, runs tests, records findings |
| `verifier.md` | IPLAN Verifier | Reviews validation results, marks IPLAN as Verified |
| `report_generator.md` | Report Generator | Generates validation reports using IPLAN-VERIFY-TEMPLATE |

## Workflow

```
1. IPLAN status = "Completed"
2. Validator runs tests (unit, integration, lint)
3. Validator creates validation report (IPLAN-VERIFY-TEMPLATE)
4. If findings exist:
   a. Create IPLAN-VERIFY to fix P0/P1 issues
   b. Fix all critical findings
   c. Re-run validation
5. When all findings resolved:
   a. Verifier marks original IPLAN as "Verified" (FINAL/FINITE)
   b. Close validation IPLAN as "Completed"
```

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/verify_iplan_status.sh` | Verify IPLAN status transitions |
| `scripts/generate_validation_report.sh` | Generate validation report |

## Usage

```bash
# Verify IPLAN status transitions
./scripts/verify_iplan_status.sh IPLAN-15

# Run validation workflow
./scripts/verify_iplan_status.sh IPLAN-15 --validate

# Generate validation report
./scripts/generate_validation_report.sh IPLAN-15

# Generate report + fix IPLAN
./scripts/generate_validation_report.sh IPLAN-15 --fix-found
```

## Status Lifecycle

```
Draft → Approved → In Progress → Completed → Verified
                                                   ↑
                                                   │ (Final/Finite)
                                                   │
                                          Cannot be changed
                                          (Need CHG + new IPLAN)
```

## Key Rules

- **Verified = Immutable**: Once Verified, no changes allowed
- **CHG Required**: To modify Verified IPLAN, create CHG + new IPLAN
- **Validation First**: Use IPLAN-VERIFY-TEMPLATE to verify implementation
- **Severity-Based Fixes**: Fix P0/P1 before marking Verified
