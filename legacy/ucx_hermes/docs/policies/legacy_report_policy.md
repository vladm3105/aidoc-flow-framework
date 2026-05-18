# Legacy Report Policy

Policy ID: LEGACY-REPORT-POLICY-001
Date: 2026-03-24
Status: Active
Scope: MCP reporting compatibility for legacy `UCX_*` report files

## Decision

Configured runtime policy: `ignore`

Meaning:

- Legacy `UCX_validation_report*`, `UCX_review_report*`, and `UCX_remediation_report*` files are read-only compatibility inputs.
- Canonical MCP workflows do not write new `UCX_*` report names.
- Legacy files are excluded from canonical version allocation unless an explicit import operation is invoked.

## Runtime Contract Binding

Runtime helper implementation:

- `ucx_hermes/src/mcp_server/reporting/contracts.py`
  - `resolve_legacy_report_policy(configured_policy)`
  - `evaluate_legacy_report_set(policy, discovered_legacy_reports)`

Allowed values:

- `import`
- `ignore`
- `fail-fast`

Default value:

- `ignore`

## Verification Evidence

- Unit tests:
  - `test_legacy_report_policy_defaults_to_ignore`
  - `test_legacy_report_policy_rejects_unknown_value`
  - `test_legacy_report_fail_fast_requires_action_when_legacy_reports_exist`
- Test command:
  - `../.venv/bin/pytest -q tests/unit/test_reporting_contracts.py tests/integration/test_reporting_contracts_integration.py`
- Result:
  - 13 passed, 0 failed

## Failure Conditions

- Unknown policy value provided to runtime configuration.
- Runtime path writes a new `UCX_*` report filename.
- Legacy files silently alter canonical report version allocation without explicit import behavior.
