# CHANGELOG — Framework v0.20.4

**Release Date**: 2026-05-04

## Summary

Implemented saga branch LLM fan-out/fan-in runtime behavior in `ucx_hermes` with rollout controls, deterministic reducer tie-break rules, parser fallback handling, and debug-only redacted raw-output retention. Updated SDD root documentation and UCX operational/specification documentation to document the new behavior, defaults, and controls.

## Changes

- Runtime and contract implementation updates in `ucx_hermes`:
  - Added branch output parser with strict JSON -> structured block -> fallback flow:
    - `ucx_hermes/src/mcp_server/review/persona_output_parser.py`
  - Added saga branch LLM runtime controls, rollout phase resolution, telemetry capture, reducer output handoff, and redacted debug raw-output retention:
    - `ucx_hermes/src/mcp_server/review/saga_orchestrator.py`
  - Updated reducer deduplication and conflict resolution rules (content-hash dedup, priority/category/branch tie-break, provenance list):
    - `ucx_hermes/src/mcp_server/review/saga_reducer.py`
  - Added executor metadata support for API usage telemetry:
    - `ucx_hermes/src/mcp_server/executor/api_runner.py`
    - `ucx_hermes/src/mcp_server/executor/cli_runner.py`
  - Added saga branch LLM control surfaces and executor/generation defaults in tool/CLI paths:
    - `ucx_hermes/src/mcp_server/tool_registry.py`
    - `ucx_hermes/src/mcp_server/cli/main.py`

- UCX documentation updates for contract/runtime behavior:
  - `ucx_hermes/docs/specs/SPEC-002_mcp_review_scoring_handoff_identity_contracts.md`
  - `ucx_hermes/docs/specs/SPEC-004_mcp_reporting_lineage_artifact_contracts.md`
  - `ucx_hermes/docs/specs/SPEC-007_mcp_review_remediation_operational_contracts.md`
  - `ucx_hermes/docs/specs/SPEC-008_mcp_output_schema_contracts.md`
  - `ucx_hermes/docs/architecture/MCP_RUNTIME_ARCHITECTURE.md`
  - `ucx_hermes/docs/architecture/MCP_OPERATIONAL_FLOWS.md`
  - `ucx_hermes/docs/architecture/MCP_CLI_REFERENCE.md`
  - `ucx_hermes/docs/README.md`

- Root SDD documentation updates to include runtime behavior and controls:
  - `README.md`
  - `governance/SDD_DEPTH_GUIDE.md`
  - `ucx_flow_v3/README.md`

- New and updated tests:
  - `ucx_hermes/tests/unit/test_persona_output_parser.py`
  - `ucx_hermes/tests/unit/test_saga_review_orchestrator.py`
  - `ucx_hermes/tests/unit/test_saga_review_reducer.py`
  - `ucx_hermes/tests/unit/test_server.py`
  - `ucx_hermes/tests/unit/test_cli_main.py`
  - `ucx_hermes/tests/integration/test_saga_review_pipeline.py`

## Backward Compatibility

- `review_mode=prompt_only` behavior remains unchanged and still requires explicit review executor input.
- `review_mode=saga_parallel` now supports branch-level LLM execution with explicit or rollout-resolved enablement and retains deterministic saga artifacts.
- Remediation now has an API executor default (`api/claude-sonnet`) when executor is omitted.
- Existing consumers of saga summary paths remain compatible; additional saga fields are additive.

## Validation Evidence

- Targeted runtime and contract tests executed from `ucx_hermes`:
  - `pytest tests/unit/test_persona_output_parser.py tests/unit/test_saga_review_reducer.py tests/unit/test_saga_review_orchestrator.py tests/unit/test_server.py tests/unit/test_cli_main.py tests/integration/test_saga_review_pipeline.py`
  - Result: all tests passed.
