# KB Entry Template (UCX V3)

Use this template when adding or updating knowledge records after approved IPLAN implementation evidence.

## Admission Checklist

- [ ] IPLAN execution evidence is available.
- [ ] Relevant UCX V3 lifecycle gates are complete for scope.
- [ ] Entry contains traceability links (artifact IDs and issue/PR references).
- [ ] Content excludes secrets and unverified claims.
- [ ] Human/operator policy allows KB write-back.

## Entry Metadata

- `entry_id`:
- `title`:
- `project`:
- `domain`:
- `status`: `active` | `superseded` | `deprecated`
- `sensitivity`: `public` | `internal` | `restricted`
- `source_type`: `implementation_evidence` | `review_finding` | `remediation_pattern` | `constraint`
- `created_at` (ISO 8601 with timezone):
- `updated_at` (ISO 8601 with timezone):

## Traceability

- `plan_id` (document-layer `IPLAN-*` or permanent development `PLAN-*`):
- `artifact_ids`: []
- `lifecycle_stages`: []
- `issue_refs`: []
- `pr_refs`: []
- `report_refs`: []

## Knowledge Content

### Facts (Verified)

-

### Decision/Pattern

-

### Constraints

-

### Failure Modes

-

### Mitigations (Validated)

-

## Supersession

- `supersedes_entry_ids`: []
- `superseded_by_entry_id`:
- `supersession_reason`:

## Validation Notes

- `validation_method`:
- `validation_evidence_refs`: []
- `reviewed_by`:
- `approved_by`:

## Operator Summary

- `change_summary`:
- `risk_notes`:
- `rollback_note`:
