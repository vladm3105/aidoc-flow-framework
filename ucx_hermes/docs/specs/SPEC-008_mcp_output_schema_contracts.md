# SPEC-008: MCP Output Schema Contracts

| Field | Value |
| --- | --- |
| Canonical ID | SPEC-008 |
| Status | Active |
| Version | 2.2 |
| Date | 2026-05-04 |
| Scope | Canonical output schemas and schema versioning rules for MCP command results |

---

## 1. Purpose

Define stable output schema contracts for MCP command artifacts and console payloads used by operators, tests, and automation.

Implementation complexity: 4/5.

---

## 2. Scope and Boundaries

In scope:

- command-specific MCP JSON output schemas
- schema versioning and compatibility rules
- required fields for validate, validate-fix, remediate, remediate-fix, prescreen, scan, scoring, consistency, preflight, and link validation outputs
- deterministic serialization constraints

Out of scope:

- prompt text content quality
- LLM model behavior tuning
- UI rendering concerns outside schema payloads

---

## 3. Global JSON Contract

All MCP JSON outputs in scope are command-specific and deterministic. There is no universal required envelope shared across all commands.

Rules:

- Required fields are defined per command schema in Section 4.
- Unknown fields are allowed but must not alter required field semantics.
- Arrays must preserve deterministic ordering for identical input.
- Status semantics are command-specific (`is_valid`, `passed`, or `status`), not a single shared field.

Deprecated assumption:

- A universal envelope (`schema_id`, `schema_version`, `generated_at`, `command`, `status`) is not currently implemented and is not required by runtime tests.

---

## 4. Command Schema Contracts

### 4.1 validate schema

Primary payload fields:

- `report_path`
- `summary_path`
- `tier1_only`
- `strict`
- `errors`
- `warnings`
- `is_valid`
- `passed`
- `fix_generated`

Constraints:

- `passed` in MCP tool output indicates command execution success and remains true even when `is_valid` is false.
- CLI exit code carries validation failure semantics (`0` pass, `1` fail).

### 4.2 validate-fix schema (deprecated alias)

Alias behavior:

- `validate-fix` routes to `validate` and returns the same payload contract.

When validation fails, additional fields may include:

- `fix_report_path`
- `fix_summary_path`
- `derived_paths`

### 4.3 remediate schema

Primary payload fields:

- `project_root`
- `document_path`
- `doc_type`
- `layer`
- `review_report`
- `findings`
- `summary`

Constraints:

- finding category and severity fields must be present for each emitted finding.

### 4.4 remediate-fix schema

Alias behavior:

- Standalone `remediate-fix` CLI command is deprecated; canonical behavior is `remediate --fix`.

Primary payload fields (from `remediate --fix`):

- `project_root`
- `document_path`
- `doc_type`
- `layer`
- `remediation_report`
- `derived_paths`
- `remediate_version`
- `summary`

Constraints:

- no direct mutation of original source document in protected mode.

### 4.5 review-build / review schema

Review has two schema variants controlled by `review_mode`.

#### 4.5.1 `prompt_only` variant (default)

Primary payload fields:

- `prompt_path`
- `sidecar_path`
- `inspection_path`
- `prompt_text`
- `system_prompt`

Optional compatibility status fields:

- `review_mode` (`prompt_only`)
- `passed`

Constraints:

- review commands assemble prompt artifacts; they do not persist an LLM-authored review report artifact.
- `prompt_only` remains the default when `review_mode` is omitted.

#### 4.5.2 `saga_parallel` variant (optional extension)

Required request fields when enabled:

- `review_mode` (`saga_parallel`)

Optional request control fields:

- `max_parallel_branches`
- `branch_timeout_seconds`
- `max_branch_retries`
- `retry_backoff_seconds`
- `saga_resume`

Required response fields when enabled:

- `review_mode` (`saga_parallel`)
- `review_run_id`
- `saga_status`
- `branch_summary`
- `branch_summary_path`
- `compensation_summary`
- `reducer_summary`
- `reducer_summary_path`
- `synthesis_summary_path`
- `passed`

Allowed `saga_status` values:

- `PREPARED`
- `FANOUT_STARTED`
- `BRANCH_RUNNING`
- `BRANCH_COMPLETED`
- `BRANCH_FAILED`
- `BRANCH_COMPENSATING`
- `FANIN_REDUCED`
- `SYNTHESIZED`
- `CLOSED`
- `ESCALATED`

Constraints:

- `saga_parallel` must fail explicitly when runtime support is unavailable; implementations must not silently downgrade to `prompt_only`.
- `passed=false` when `saga_status=ESCALATED`.
- prompt artifacts (`prompt_path`, `sidecar_path`, `inspection_path`) remain valid outputs in this mode.
- `branch_summary_path` must be present when saga orchestration reaches `CLOSED` or `ESCALATED`.
- `reducer_summary_path` and `synthesis_summary_path` are required for `CLOSED` and may be `null` for `ESCALATED`.

Compatibility rule:

- Consumers that ignore saga fields can continue to use prompt artifact fields and `passed` status.

### 4.6 create-build schema

Primary payload fields:

- `prompt_path`
- `sidecar_path`
- `inspection_path`
- `layer_asset_names`

### 4.7 create schema

Primary payload fields:

- `target_path`
- `template_source`
- `prompt_path`
- `sidecar_path`
- `inspection_path`

### 4.8 prescreen schema

Primary payload fields:

- `document_path`
- `candidates`
- `summary`

### 4.9 scan schema

Primary payload fields:

- `report_file`
- `categories`
- `summary`

### 4.10 scoring schema

Scoring payload variants:

- `show`: `report_file`, `score`, `summary`
- `validate`: `report_file`, `score`, `threshold`, `passed`, `requested_threshold`, `readiness_gate`
- `compare`: `baseline_report_file`, `candidate_report_file`, `baseline_score`, `candidate_score`, `delta`

### 4.11 consistency schema

Primary payload fields:

- `status`
- `target_path`
- `errors`
- `warnings`
- `details`

### 4.12 preflight schema

Primary payload fields:

- `project_root`
- `context`
- `status`
- `checks`
- `warnings`
- `errors`

### 4.13 validate-links schema

Primary payload fields:

- `status`
- `target`
- `workspace_root`
- `broken_links`
- `summary`

---

## 5. Text Output Contract

For text outputs paired with JSON:

1. text summary must include command, status, and primary metric line.
2. text output must include artifact paths when files are emitted.
3. text output must not omit blocking errors present in JSON.

---

## 6. Versioning and Change Rules

Allowed without major bump:

- adding optional fields
- adding non-breaking enum values when documented

Requires major bump:

- removing required fields
- renaming required fields
- changing field type for required fields
- changing exit-code semantics tied to schema status

---

## 7. Validation Evidence Requirements

Required checks:

- schema presence test for each command family
- required-fields test per schema id
- deterministic ordering test on repeated identical input
- schema-version regression check in CI

Required test targets:

- `ucx_hermes/tests/unit/test_validation_runner.py`
- `ucx_hermes/tests/unit/test_remediation_runner.py`
- `ucx_hermes/tests/unit/test_prescreening.py`
- `ucx_hermes/tests/unit/test_scoring_cli.py`
- `ucx_hermes/tests/unit/test_server.py`
- `ucx_hermes/tests/unit/test_cli_main.py`
- `ucx_hermes/tests/integration/test_migration_flows.py`

---

## 8. Constraints

- Schema contracts are authoritative for automation integration.
- Runtime changes that affect schema shape must update this spec in the same change set.
- Docs and CLI examples must reflect the current schema version.
