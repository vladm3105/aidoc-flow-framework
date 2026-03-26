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

---

## Post-Release Update (2026-03-25)

**Type**: Patch-level update (documentation + runtime alignment)
**Status**: Implemented

### Runtime/CLI Alignment Updates

- Added script-based validation command:
  - `validate-build` in `mcp/src/mcp_server/cli/main.py`
  - validation runner module in `mcp/src/mcp_server/validation/runner.py`
  - validation package export in `mcp/src/mcp_server/validation/__init__.py`
- Standardized stage output root from `.ucx_create` to `.ucx` and normalized validation stage name to `validate`:
  - `mcp/src/mcp_server/core/stage_output.py`
- Defined UCX_v1 command-compatibility contracts in MCP CLI:
  - Added `review` as an alias to `review-build`
  - Added reserved `remediate`, `remediate-fix`, and `validate-fix` command contracts with explicit not-implemented responses
  - `mcp/src/mcp_server/cli/main.py`

### Test Coverage Updates

- Added validator unit coverage:
  - `mcp/tests/unit/test_validation_runner.py`
- Updated CLI and integration expectations for `.ucx` stage paths and validate command behavior:
  - `mcp/tests/unit/test_cli_main.py`
  - `mcp/tests/integration/test_creation_prompt_builder.py`

### Documentation Updates

- Updated CLI contract reference with `validate-build` and `.ucx/<stage>` defaults:
  - `mcp/docs/architecture/MCP_CLI_REFERENCE.md`
- Added UCX_v1 compatibility command definitions and implementation-status notes (`review`, `remediate`, `remediate-fix`, `validate-fix`):
  - `mcp/docs/architecture/MCP_CLI_REFERENCE.md`

### Validation Evidence Snapshot

- Targeted MCP test execution for new and changed validator/CLI paths: PASS (9 passed)
