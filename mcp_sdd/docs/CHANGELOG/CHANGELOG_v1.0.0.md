# CHANGELOG v1.0.0

**Release Date**: 2026-03-24
**Type**: Major (Initial MCP documentation layer release)
**Status**: Released

## Summary

This release establishes a complete L0-L9 MCP documentation set under mcp/docs and records closure evidence for IPLAN-002.

## Released Changes

### L0-L9 Documentation Coverage (IPLAN-002)

- Added MCP documentation index and reconciliation index:
  - mcp_sdd/docs/README.md
- Added architecture and operations documents:
  - mcp_sdd/docs/architecture/MCP_RUNTIME_ARCHITECTURE.md
  - mcp_sdd/docs/architecture/MCP_CLI_REFERENCE.md
  - mcp_sdd/docs/architecture/MCP_OPERATOR_RUNBOOK.md
- Added canonical operational specifications:
  - mcp_sdd/docs/specs/SPEC-005_mcp_source_input_ingestion_contracts.md
  - mcp_sdd/docs/specs/SPEC-006_mcp_creation_flow_operational_contracts.md
  - mcp_sdd/docs/specs/SPEC-007_mcp_review_remediation_operational_contracts.md
- Added governance policies:
  - mcp_sdd/docs/policies/DOC_COMPATIBILITY_AND_DEPRECATION_POLICY.md
  - mcp_sdd/docs/policies/DOC_QUALITY_GATES.md
  - mcp_sdd/docs/policies/DOC_LIFECYCLE_AND_VERSIONING_POLICY.md
- Added coverage and reconciliation evidence artifacts:
  - mcp_sdd/docs/plans/DOC-COVERAGE-MATRIX-001_mcp_layers.md
  - mcp_sdd/docs/plans/DOC-RECONCILIATION-LOG-001.md
  - mcp_sdd/docs/plans/COMPLIANCE-REPORT-002_mcp_docs_layer_coverage.md

### Plan Closure Updates

- Updated IPLAN-002 status to Completed:
  - mcp_sdd/docs/plans/IPLAN-002_mcp_docs_full_layer_coverage.md
- Updated compliance report with validation execution evidence:
  - mcp_sdd/docs/plans/COMPLIANCE-REPORT-002_mcp_docs_layer_coverage.md

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
  - `validate-build` in `mcp_sdd/src/mcp_server/cli/main.py`
  - validation runner module in `mcp_sdd/src/mcp_server/validation/runner.py`
  - validation package export in `mcp_sdd/src/mcp_server/validation/__init__.py`
- Standardized stage output root from `.ucx_create` to `.ucx` and normalized validation stage name to `validate`:
  - `mcp_sdd/src/mcp_server/core/stage_output.py`
- Defined UCX_v1 command-compatibility contracts in MCP CLI:
  - Added `review` as an alias to `review-build`
  - Added reserved `remediate`, `remediate-fix`, and `validate-fix` command contracts with explicit not-implemented responses
  - `mcp_sdd/src/mcp_server/cli/main.py`

### Test Coverage Updates (2026-03-25 Runtime Alignment)

- Added validator unit coverage:
  - `mcp_sdd/tests/unit/test_validation_runner.py`
- Updated CLI and integration expectations for `.ucx` stage paths and validate command behavior:
  - `mcp_sdd/tests/unit/test_cli_main.py`
  - `mcp_sdd/tests/integration/test_creation_prompt_builder.py`

### Documentation Updates (2026-03-25 Runtime Alignment)

- Updated CLI contract reference with `validate-build` and `.ucx/<stage>` defaults:
  - `mcp_sdd/docs/architecture/MCP_CLI_REFERENCE.md`
- Added UCX_v1 compatibility command definitions and implementation-status notes (`review`, `remediate`, `remediate-fix`, `validate-fix`):
  - `mcp_sdd/docs/architecture/MCP_CLI_REFERENCE.md`

### Validation Evidence Snapshot (2026-03-25)

- Targeted MCP test execution for new and changed validator/CLI paths: PASS (9 passed)

---

## Post-Release Update (2026-03-26)

**Type**: Minor-level update (migration core implementation without autopilot)
**Status**: Implemented

### Runtime and CLI Implementation Updates

- Implemented in-scope command runtime behavior:
  - `remediate`
  - `validate-fix`
  - `remediate-fix`
  - `prescreen`
  - `scan`
  - `scoring show|validate|compare`
- Added review mode and maintenance controls:
  - `--unified`, `--one-turn`, `--no-resume`, `--session-ttl`
  - `--clean-memory`, `--clean-reports`, `--keep-versions`
- Added validation controls:
  - `--tier1-only`, `--strict`, `--format {text,json}`

### Test Coverage Updates (2026-03-26)

- Added command-path and flow tests:
  - `mcp_sdd/tests/unit/test_remediation_runner.py`
  - `mcp_sdd/tests/unit/test_prescreening.py`
  - `mcp_sdd/tests/unit/test_scoring_cli.py`
  - `mcp_sdd/tests/integration/test_migration_flows.py`

### Documentation and Policy Updates

- Added framework/flow architecture docs:
  - `mcp_sdd/docs/architecture/MCP_UNIFIED_CONTEXT_FRAMEWORK.md`
  - `mcp_sdd/docs/architecture/MCP_OPERATIONAL_FLOWS.md`
- Added new specs:
  - `mcp_sdd/docs/specs/SPEC-009_mcp_remediation_and_fix_flow_contracts.md`
  - `mcp_sdd/docs/specs/SPEC-010_mcp_prescreen_scan_scoring_contracts.md`
- Added cutover policy and release tracking record:
  - `mcp_sdd/docs/policies/MCP_CUTOVER_AND_UCXV1_ARCHIVE_POLICY.md`
  - `mcp_sdd/docs/plans/IPLAN-003_RELEASE_TRACKING.yaml`

### Validation Evidence Snapshot (2026-03-26)

- `pytest mcp_sdd/tests/unit/test_cli_main.py mcp_sdd/tests/unit/test_validation_runner.py mcp_sdd/tests/unit/test_remediation_runner.py mcp_sdd/tests/unit/test_prescreening.py mcp_sdd/tests/unit/test_scoring_cli.py -q`: PASS
- `pytest mcp_sdd/tests/integration/test_migration_flows.py -q`: PASS

---

## Post-Release Update (2026-03-27 All-Layer Monolith Policy)

**Type**: Minor-level update (lifecycle normalization and command alignment)
**Status**: Implemented

### Runtime and CLI Updates (All-Layer Monolith Policy)

- Renamed the active script-based validation command from `validate-build` to `validate`:
  - `mcp_sdd/src/mcp_server/cli/main.py`
- Generalized derived-artifact flow handling across document layers:
  - `validate`, `validate-fix`, and `remediate` resolve canonical source artifacts from document folders
  - `remediate-fix` resolves `_validation` artifacts from document folders
  - remediated outputs use canonical base names (`{slug}_remediated.md`)
  - `mcp_sdd/src/mcp_server/remediation/runner.py`

### Test Coverage Updates (All-Layer Monolith Policy)

- Updated CLI and lifecycle tests for `validate` naming and cross-layer derived-artifact behavior:
  - `mcp_sdd/tests/unit/test_cli_main.py`
  - `mcp_sdd/tests/unit/test_validation_runner.py`
  - `mcp_sdd/tests/unit/test_remediation_runner.py`
  - `mcp_sdd/tests/integration/test_migration_flows.py`

### Documentation and History Updates

- Expanded operational flow documentation with project initialization and full lifecycle lineage:
  - `mcp_sdd/docs/architecture/MCP_OPERATIONAL_FLOWS.md`
- Updated CLI reference to reflect `validate` naming, initialization flow, and derived-artifact lineage:
  - `mcp_sdd/docs/architecture/MCP_CLI_REFERENCE.md`
- Updated active runtime-facing and operator docs to use `validate` as canonical naming:
  - `mcp_sdd/docs/architecture/MCP_RUNTIME_ARCHITECTURE.md`
  - `mcp_sdd/docs/architecture/MCP_OPERATOR_RUNBOOK.md`
  - `mcp_sdd/docs/architecture/MCP_UNIFIED_CONTEXT_FRAMEWORK.md`
- Recorded historical closure in:
  - `mcp_sdd/docs/plans/IPLAN-004_mcp_lifecycle_normalization_and_command_alignment.md`
- Updated roadmap release tracking in:
  - `mcp_sdd/docs/ROADMAP.md`

### Validation Evidence Snapshot (2026-03-27)

- `pytest mcp_sdd/tests/ -q`: PASS (`107 passed, 2 warnings`)

---

## Post-Release Update (2026-03-27 IPLAN-005 Kickoff)

**Type**: Minor-level update (IPLAN-005 implementation kickoff)
**Status**: In Progress

### Runtime and CLI Updates (2026-03-27 IPLAN-005 Kickoff)

- Added `consistency` command for lightweight artifact lineage and stage-chain checks:
  - `mcp_sdd/src/mcp_server/consistency/runner.py`
  - `mcp_sdd/src/mcp_server/consistency/__init__.py`
  - `mcp_sdd/src/mcp_server/cli/main.py`
- Added `preflight` command for runtime and environment readiness checks:
  - `mcp_sdd/src/mcp_server/preflight/runner.py`
  - `mcp_sdd/src/mcp_server/preflight/__init__.py`
  - `mcp_sdd/src/mcp_server/cli/main.py`
- Applied frozen exit-code contract for both commands:
  - `0` success
  - `1` blocking failures
  - `2` runtime errors

### Test Coverage Updates (2026-03-27 IPLAN-005 Kickoff)

- Added CLI tests covering success and failure paths:
  - `mcp_sdd/tests/unit/test_cli_main.py`

### Documentation and Plan Tracking Updates

- Updated CLI command reference and exit semantics:
  - `mcp_sdd/docs/architecture/MCP_CLI_REFERENCE.md`
- Updated roadmap planned scope for v1.3.0:
  - `mcp_sdd/docs/ROADMAP.md`
- Updated IPLAN-005 phase and matrix tracking artifacts:
  - `mcp_sdd/docs/plans/IPLAN-005_mcp_gap_closure_from_ucx_roadmap.md`
  - `mcp_sdd/docs/plans/CHECKLIST-005-G1_baseline_and_contracts.md`
  - `mcp_sdd/docs/plans/CHECKLIST-005-G2_validation_and_consistency.md`
  - `mcp_sdd/docs/plans/CHECKLIST-005-G3_diagnostics_and_safety.md`
  - `mcp_sdd/docs/plans/GAP-CLOSURE-MATRIX-001_mcp_ucx_gap_closure.md`

### Validation Evidence Snapshot (2026-03-27 IPLAN-005 Kickoff)

- `pytest mcp_sdd/tests/unit/test_cli_main.py -q`: PASS (`11 passed, 2 warnings`)

---

## Post-Release Update (2026-03-27 Diagnostics and Parity Depth Progression)

**Type**: Minor-level update (IPLAN-005 diagnostics and parity depth progression)
**Status**: In Progress

### Runtime and Validation Updates

- Added deterministic fallback parsing for provider probe outputs in preflight diagnostics:
  - status-token fallback handling
  - ISO-date fallback extraction for degraded signal recovery
  - `mcp_sdd/src/mcp_server/preflight/runner.py`
- Added source protection telemetry and restoration guards in remediation fix flows:
  - integrity hash snapshots
  - mutation detection and restore telemetry
  - `mcp_sdd/src/mcp_server/remediation/runner.py`
- Added EARS plus SPEC TASKS CTR parity depth checks in project validation runner:
  - `mcp_sdd/src/mcp_server/validation/runner.py`

### Test Coverage Updates (2026-03-27 Diagnostics and Parity Depth Progression)

- Added focused preflight fallback unit coverage:
  - `mcp_sdd/tests/unit/test_preflight_runner.py`
- Expanded CLI runtime-error contract coverage for new commands:
  - `mcp_sdd/tests/unit/test_cli_main.py`
- Expanded remediation telemetry and restoration safety tests:
  - `mcp_sdd/tests/unit/test_remediation_runner.py`
- Added parity-depth validation tests for EARS and SPEC TASKS CTR:
  - `mcp_sdd/tests/unit/test_validation_runner.py`

---

## Post-Release Update (2026-03-27 All-Layer Monolith Alignment)

**Type**: Minor-level update (all-layer monolith validation and document-mode review alignment)
**Status**: Implemented

### Runtime and CLI Updates (2026-03-27 All-Layer Monolith Alignment)

- Generalized validation file-input canonicalization across all layers:
  - if a document folder contains exactly one canonical source (`TYPE-NN_{slug}.md`), non-source markdown file inputs now validate the canonical source artifact
  - applies to index/appendix/glossary/section-split file invocation patterns
  - `mcp_sdd/src/mcp_server/validation/runner.py`
- Extended review document-mode behavior across all layers:
  - `review-build` and `review` accept `--document` and auto-build sections from canonical main plus appendix files
  - existing `--sections-json` behavior remains supported for compatibility
  - `mcp_sdd/src/mcp_server/cli/main.py`

### Test Coverage Updates (2026-03-27 All-Layer Monolith Alignment)

- Added cross-layer validation redirection coverage:
  - `mcp_sdd/tests/unit/test_validation_runner.py`
  - `test_run_project_validation_build_file_section_redirects_to_source_artifact_across_layers`
- Added cross-layer review document-mode source assembly coverage:
  - `mcp_sdd/tests/unit/test_cli_main.py`
  - `test_main_review_build_document_auto_loads_main_and_appendices_across_layers`
- Verified retained BRD behavior with targeted regression tests:
  - `test_run_project_validation_build_file_index_redirects_to_source_artifact`
  - `test_main_review_build_document_auto_loads_main_and_appendices`

### Documentation Updates (All-Layer Monolith Policy)

- Updated CLI contracts and examples for all-layer canonical validation and review document mode:
  - `mcp_sdd/docs/architecture/MCP_CLI_REFERENCE.md`
- Updated runtime architecture flow definitions:
  - `mcp_sdd/docs/architecture/MCP_RUNTIME_ARCHITECTURE.md`
- Updated roadmap implemented scope:
  - `mcp_sdd/docs/ROADMAP.md`

### Validation Evidence Snapshot (2026-03-27 All-Layer Monolith Policy)

- `pytest -q mcp_sdd/tests/unit/test_validation_runner.py::test_run_project_validation_build_file_section_redirects_to_source_artifact_across_layers mcp_sdd/tests/unit/test_cli_main.py::test_main_review_build_document_auto_loads_main_and_appendices_across_layers mcp_sdd/tests/unit/test_validation_runner.py::test_run_project_validation_build_file_index_redirects_to_source_artifact mcp_sdd/tests/unit/test_cli_main.py::test_main_review_build_document_auto_loads_main_and_appendices`: PASS (`4 passed`)

### Gap Closure Tracking Updates

- GAP-02 status moved to Closed in matrix tracking.
- GAP-03 status moved to Closed in matrix tracking.
- GAP-04, GAP-01, and GAP-06 moved to In Progress as implementation depth expanded.
- Tracking updated in:
  - `mcp_sdd/docs/plans/GAP-CLOSURE-MATRIX-001_mcp_ucx_gap_closure.md`
  - `mcp_sdd/docs/plans/CHECKLIST-005-G2_validation_and_consistency.md`
  - `mcp_sdd/docs/plans/CHECKLIST-005-G3_diagnostics_and_safety.md`

### Validation Evidence Snapshot (2026-03-27 All-Layer Monolith Alignment)

- `pytest mcp_sdd/tests/unit/test_cli_main.py mcp_sdd/tests/unit/test_preflight_runner.py mcp_sdd/tests/unit/test_remediation_runner.py mcp_sdd/tests/unit/test_validation_runner.py -q`: PASS (`31 passed, 2 warnings`)

---

## Post-Release Update (2026-03-27 G3 Diagnostics Documentation Closure)

**Type**: Minor-level update (G3 diagnostics documentation and telemetry schema closure)
**Status**: Implemented

### Documentation and Spec Updates

- Updated operator procedures and troubleshooting for `consistency`, `preflight`, and telemetry omission behavior:
  - `mcp_sdd/docs/architecture/MCP_OPERATOR_RUNBOOK.md`
- Updated lifecycle flow documentation with readiness/lineage commands and corrected exit semantics:
  - `mcp_sdd/docs/architecture/MCP_OPERATIONAL_FLOWS.md`
- Updated reporting contract rules for conditional telemetry emission:
  - `mcp_sdd/docs/specs/SPEC-004_mcp_reporting_lineage_artifact_contracts.md`
- Updated remediation/fix-flow contract definitions for telemetry present and omitted branches:
  - `mcp_sdd/docs/specs/SPEC-009_mcp_remediation_and_fix_flow_contracts.md`

### Tracking Updates (2026-03-27 G3 Diagnostics Documentation Closure)

- G3 checklist updated to record completed telemetry branch coverage and documentation closure.
- GAP-04 moved to Closed in matrix tracking.

### Validation Evidence Snapshot (2026-03-27 G3 Diagnostics Documentation Closure)

- `pytest mcp_sdd/tests/unit/test_remediation_runner.py mcp_sdd/tests/unit/test_validation_runner.py -q`: PASS (`19 passed, 2 warnings`)

---

## Post-Release Update (2026-03-27 G2 EARS Parity Progression)

**Type**: Minor-level update (G2 EARS parity depth progression)
**Status**: In Progress

### Validation Updates (2026-03-27 G2 EARS Parity Progression)

- Strengthened EARS parity checks to require both a trigger clause and explicit `THE SYSTEM SHALL` actor semantics:
  - `mcp_sdd/src/mcp_server/validation/runner.py`
- Added folder-path validation coverage for EARS section-set execution:
  - `mcp_sdd/tests/unit/test_validation_runner.py`
  - `mcp_sdd/tests/integration/test_migration_flows.py`

### Test Coverage Updates (2026-03-27 G2 EARS Parity Progression)

- Added EARS negative-path coverage for missing trigger and missing actor-clause cases.
- Preserved SPEC, TASKS, and CTR negative-path parity fixtures.

### Validation Evidence Snapshot (2026-03-27 G2 EARS Parity Progression)

- `pytest mcp_sdd/tests/unit/test_validation_runner.py mcp_sdd/tests/integration/test_migration_flows.py -q`: pending in current implementation slice

---

## Post-Release Update (2026-03-27 G4 Identity Delivery and Closure)

**Type**: Minor-level update (G4 identity delivery and IPLAN-005 closure)
**Status**: Implemented

### Runtime and Contract Updates (2026-03-27 G4 Identity Delivery and Closure)

- Added deterministic hash-based identity builders for remediation findings and actions:
  - `mcp_sdd/src/mcp_server/reporting/contracts.py`
  - `mcp_sdd/src/mcp_server/reporting/__init__.py`
- Remediation reports now emit stable `finding_id`, `action_id`, and `priority` fields for each finding:
  - `mcp_sdd/src/mcp_server/remediation/runner.py`
- Added compatibility validation for legacy persona-prefixed and remediation-prefixed sequential finding IDs.

### Test Coverage Updates (2026-03-27 G4 Identity Delivery and Closure)

- Added deterministic ID, compatibility, and collision-length coverage:
  - `mcp_sdd/tests/unit/test_reporting_contracts.py`
- Added remediation rerun stability coverage for hash-based finding and action IDs:
  - `mcp_sdd/tests/unit/test_remediation_runner.py`
- Revalidated reporting, remediation, migration, and validation slices together:
  - `mcp_sdd/tests/integration/test_reporting_contracts_integration.py`
  - `mcp_sdd/tests/integration/test_migration_flows.py`
  - `mcp_sdd/tests/unit/test_validation_runner.py`

### Documentation and Closure Updates (2026-03-27 G4 Identity Delivery and Closure)

- Updated identity and reporting specifications for canonical remediation finding IDs:
  - `mcp_sdd/docs/specs/SPEC-002_mcp_review_scoring_handoff_identity_contracts.md`
  - `mcp_sdd/docs/specs/SPEC-004_mcp_reporting_lineage_artifact_contracts.md`
- Updated operator runbook with remediation identity verification guidance:
  - `mcp_sdd/docs/architecture/MCP_OPERATOR_RUNBOOK.md`
- Closed G2 and G4 checklists, finalized matrix state, and published final closure report:
  - `mcp_sdd/docs/plans/CHECKLIST-005-G2_validation_and_consistency.md`
  - `mcp_sdd/docs/plans/CHECKLIST-005-G4_identity_and_release.md`
  - `mcp_sdd/docs/plans/GAP-CLOSURE-MATRIX-001_mcp_ucx_gap_closure.md`
  - `mcp_sdd/docs/plans/CLOSURE-REPORT-005_mcp_ucx_gap_closure.md`
  - `mcp_sdd/docs/plans/IPLAN-005_mcp_gap_closure_from_ucx_roadmap.md`

### Validation Evidence Snapshot (2026-03-27 G4 Identity Delivery and Closure)

- `pytest mcp_sdd/tests/unit/test_reporting_contracts.py mcp_sdd/tests/unit/test_remediation_runner.py mcp_sdd/tests/integration/test_reporting_contracts_integration.py mcp_sdd/tests/integration/test_migration_flows.py mcp_sdd/tests/unit/test_validation_runner.py -q`: PASS (`40 passed, 2 warnings`)

---

## Post-Release Update (2026-03-28 MCP Protocol Transport Layer)

**Type**: Minor-level update (MCP server with 19 tools and executor registry)
**Status**: Implemented

### Directory Rename

- Renamed `mcp/` to `mcp_sdd/` to avoid confusion with MCP protocol
- Updated all internal documentation path references (38 files)
- Python package name `mcp_server` unchanged

### New Files

- `mcp_sdd/src/mcp_server/server.py`: MCP server entry point (stdio transport, server name `sdd-lifecycle`)
- `mcp_sdd/src/mcp_server/executor/__init__.py`: Executor package public API
- `mcp_sdd/src/mcp_server/executor/registry.py`: Open executor registry with ExecutorConfig, ExecutorType (CLI/API), 5 CLI + 3 API stubs
- `mcp_sdd/src/mcp_server/executor/cli_runner.py`: Async subprocess runner with file-based prompt delivery
- `mcp_sdd/src/mcp_server/executor/api_runner.py`: LiteLLM API stub (NotImplementedError)
- `mcp_sdd/src/mcp_server/executor/dispatcher.py`: Routes by executor type
- `mcp_sdd/src/mcp_server/tool_registry.py`: 19 MCP tool definitions and handler dispatch
- `mcp_sdd/pyproject.toml`: Package mcp-sdd-server v0.1.0
- `mcp_sdd/tests/unit/test_server.py`: 33 new tests

### Tool Summary

- Deterministic (11): sdd_init, sdd_validate, sdd_consistency, sdd_preflight, sdd_prescreen, sdd_scan, sdd_score_show, sdd_score_validate, sdd_score_compare, sdd_list_executors, sdd_register_executor
- Orchestration (2): sdd_run_lifecycle (pipeline), sdd_next_action (lifecycle advisor)
- LLM-dependent (6): sdd_create_build, sdd_create, sdd_review, sdd_validate_fix, sdd_remediate, sdd_remediate_fix

### Validation Evidence Snapshot (2026-03-28 MCP Transport)

- `pytest mcp_sdd/tests/unit/test_server.py -q`: PASS (`33 passed`)
- `pytest mcp_sdd/tests/ -q`: PASS (`169 passed, 1 pre-existing failure`)
- MCP server JSON-RPC initialize: responds with protocol version 2024-11-05
- End-to-end test against b-local project: preflight, create, validate, next_action, run_lifecycle all passing
