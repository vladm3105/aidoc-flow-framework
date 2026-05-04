# ROLLBACK-NOTES-001: MCP Partial Deployment Rollback

Date: 2026-03-24
Status: Active

## Scope

This procedure covers local rollback of MCP workflow execution targets when a derived artifact stage must be abandoned and execution must return to the canonical source artifact.

## Rollback Rule

- Canonical source artifact remains immutable and is the rollback target.
- Validation-fixed and remediated artifacts remain preserved as historical derivatives.
- Rollback changes execution target selection only; it does not delete derived artifacts.

## Smoke Procedure

1. Confirm canonical source artifact exists.
2. Identify latest active derived artifact, if any.
3. Confirm rollback action resolves execution target to the canonical source artifact.
4. Confirm derived artifacts remain preserved and are not mutated by rollback planning.

## Verification

- Test: `test_rollback_smoke_restores_source_target_without_mutating_derived_artifacts`
- Evidence: `mcp/tmp/TEST_EVIDENCE_2026-03-24_LIFECYCLE_DISCOVERY_ROLLBACK.md`
