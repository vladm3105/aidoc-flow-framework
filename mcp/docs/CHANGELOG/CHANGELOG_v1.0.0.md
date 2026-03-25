# CHANGELOG v1.0.0

**Release Date**: 2026-03-24
**Type**: Major (Initial MCP documentation layer release)
**Status**: Released

## Summary

This release establishes a complete L0-L9 MCP documentation set under mcp/docs and records closure evidence for IPLAN-002.

## Released Changes

### L0-L9 Documentation Coverage (IPLAN-002)

- Added MCP documentation index and reconciliation index:
  - mcp/docs/README.md
- Added architecture and operations documents:
  - mcp/docs/architecture/MCP_RUNTIME_ARCHITECTURE.md
  - mcp/docs/architecture/MCP_CLI_REFERENCE.md
  - mcp/docs/architecture/MCP_OPERATOR_RUNBOOK.md
- Added canonical operational specifications:
  - mcp/docs/specs/SPEC-005_mcp_source_input_ingestion_contracts.md
  - mcp/docs/specs/SPEC-006_mcp_creation_flow_operational_contracts.md
  - mcp/docs/specs/SPEC-007_mcp_review_remediation_operational_contracts.md
- Added governance policies:
  - mcp/docs/policies/DOC_COMPATIBILITY_AND_DEPRECATION_POLICY.md
  - mcp/docs/policies/DOC_QUALITY_GATES.md
  - mcp/docs/policies/DOC_LIFECYCLE_AND_VERSIONING_POLICY.md
- Added coverage and reconciliation evidence artifacts:
  - mcp/docs/plans/DOC-COVERAGE-MATRIX-001_mcp_layers.md
  - mcp/docs/plans/DOC-RECONCILIATION-LOG-001.md
  - mcp/docs/plans/COMPLIANCE-REPORT-002_mcp_docs_layer_coverage.md

### Plan Closure Updates

- Updated IPLAN-002 status to Completed:
  - mcp/docs/plans/IPLAN-002_mcp_docs_full_layer_coverage.md
- Updated compliance report with validation execution evidence:
  - mcp/docs/plans/COMPLIANCE-REPORT-002_mcp_docs_layer_coverage.md

## Validation Evidence Snapshot

- Required artifact existence check: PASS
- Internal link integrity scan for mcp/docs: PASS
- CLI contract parity signal checks for init, create-build, review-build: PASS

## Commit References

- 2e1412224e9d79b01821ad4e6d63f3b7f41cd210
- 061d01d3dd334de30dd72eb080ed2f3a0b396aa7

## Constraints

- This changelog records documentation changes only.
- Runtime behavior changes are out of scope for this release and must be tracked in runtime-specific release records.
