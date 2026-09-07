# SPEC-007: MCP Review and Remediation Operational Contracts

| Field | Value |
| --- | --- |
| Canonical ID | SPEC-007 |
| Status | Active |
| Version | 2.1 |
| Date | 2026-05-04 |
| Scope | Operational contracts for review modes, prompt artifacts, saga fan-out/fan-in extension, and remediation handoff prerequisites |

---

## 1. Purpose

Define operational behavior for MCP review and remediation handoff, including:

1. default prompt-only review mode
2. optional saga-parallel review mode extension for Hermes orchestration
3. remediation handoff requirements that remain source-protected

Implementation complexity: 4/5.

---

## 2. Scope and Boundaries

In scope:

- review command contract and source selection behavior
- review mode contract (`prompt_only`, `saga_parallel`)
- prompt artifact emission contracts
- optional saga branch/reducer artifact contracts
- remediation handoff prerequisites

Out of scope:

- automated source-document rewriting by external executors
- scoring semantics (defined by SPEC-002)
- report naming global rules (defined by SPEC-004)

---

## 3. Review Command Contract

### 3.1 Input contract

Required arguments:

- `project`
- `doc_type`
- `template`

One source mode is required:

1. `sections` payload, or
2. `document` path for document-mode section loading

Optional arguments:

- `personas` (resolved from `persona_mappings.yaml` when omitted)
- `layer`
- `out`
- `review_mode` (default `prompt_only`; optional extension `saga_parallel`)

### 3.2 Normative base behavior

1. Parse and validate arguments.
2. Resolve persona list.
3. Resolve review source sections.
4. Build prompt bundle and metadata sidecar.
5. Emit review artifacts to output directory when configured.

---

## 4. Review Mode Contract

### 4.1 `prompt_only` mode (default)

`prompt_only` is the canonical default behavior.

Required artifacts:

- `review_prompt.txt`
- `review_prompt_sidecar.json`
- `review_prompt_inspection.json`

Rules:

- review returns assembled prompt artifacts only
- no LLM-authored review report is persisted by MCP in this mode
- output ordering is deterministic for identical input

### 4.2 `saga_parallel` mode (optional extension)

`saga_parallel` is an orchestration extension for parallel persona fan-out/fan-in with compensation and escalation controls.

Rules:

- mode is enabled only when runtime/tool schema supports saga controls
- source documents remain immutable
- branch retries and compensation actions are journaled
- fan-in reducer output is deterministic for identical input
- branch-level LLM execution is controlled by feature flag `saga_branch_llm_enabled`
- rollout phase control uses `UCX_REVIEW_SAGA_BRANCH_LLM_PHASE` with allowed values `A`, `B`, `C`
- if explicit branch flag is omitted, runtime resolves by phase: `A=off`, `B=off`, `C=on`
- review branch executor default is `api/openrouter` when branch LLM mode is enabled
- remediation executor default is `api/claude-sonnet` when executor argument is omitted
- generation defaults for API executors are `temperature=0.2`, `top_p=0.9`, `top_k` unset, `max_output_tokens=4000`

Minimum saga outputs when mode is active:

- canonical prompt artifacts from `prompt_only`
- `review_run_id`
- `saga_status`
- branch summary and compensation summary payloads

Optional branch diagnostics output contract:

- branch telemetry list including `persona`, `branch_id`, `attempt`, `executor`, `model`, `latency_ms`, `token_usage`, `parse_status`
- raw branch outputs are persisted only when `UCX_REVIEW_DEBUG_RAW_OUTPUTS=true`
- persisted raw outputs must be redacted before write

If runtime does not support saga mode, command must fail explicitly with a mode/feature error payload and must not silently downgrade.

---

## 5. Inspection and Sidecar Contract

Required sidecar behavior:

- sidecar serializes validated prompt metadata sidecar
- sidecar includes personas, section inclusion/skip lists, and token totals

Required inspection behavior:

- deterministic inspection output for repeated identical input
- warnings for missing structure blocks or token budget thresholds

In `saga_parallel` mode:

- per-branch diagnostics may be emitted as optional fields/artifacts
- aggregate reducer diagnostics must include deterministic ordering/fingerprint metadata

---

## 6. Remediation Handoff Preconditions

Remediation handoff requires:

- review prompt artifact exists
- metadata sidecar exists
- inspection artifact exists
- source section identity traceable from sidecar/context contracts

Additional handoff requirements when `saga_parallel` was active:

- saga status is terminal (`CLOSED` or `ESCALATED`)
- reduced findings include required identity fields per SPEC-002
- escalation state is explicit for merge-gate consumption
- if raw branch outputs are present, they must be redacted and marked debug-only

Failure modes:

- missing review artifact in handoff package
- sidecar metadata missing required fields
- inspection artifact malformed/unreadable
- saga run not terminal at handoff time

---

## 7. Review Flow Failure Modes

| Failure Mode | Detection Point | Required Behavior |
| --- | --- | --- |
| missing source mode (`sections` and `document` absent) | argument parse stage | command failure with input correction guidance |
| source payload malformed | deserialization stage | command failure with payload error details |
| missing project assets | loader validation stage | `ProjectSkillsNotFound` |
| prompt bundle invalid | contract validation stage | contract validation failure |
| output path not writable | artifact write stage | command failure with I/O error |
| unsupported `review_mode` | mode validation stage | explicit unsupported mode error |
| saga branch timeout | branch execution stage | retry/compensation path, then escalation on exhaustion |
| reducer non-determinism detected | reducer verification stage | run failure with escalation |
| branch executor unavailable/invalid | branch execution stage | branch failure with `ExecutorRequired` or `ExecutorTypeNotAllowed` then retry/escalation |
| branch parser failure after retries | branch execution stage | fail with `BranchParseFailed` and escalate |

---

## 8. Validation Evidence Requirements

Required checks:

- argument and mode parity against `cli/main.py` and `tool_registry.py`
- review output naming and payload checks against `review/runner.py`
- prompt bundle validation checks against `prompts/context_builder.py`
- project-path validation behavior checks against `skills/project_ucx_loader.py`
- saga mode determinism and retry/compensation checks when mode is active

---

## 9. Constraints

1. Prompt-only mode remains the canonical default until saga mode is explicitly enabled by runtime contracts.
2. Any review-mode contract change requires synchronized updates to SPEC-008 output schemas.
3. Any saga artifact naming change requires synchronized updates to SPEC-004 naming and lineage contracts.
4. Source-protected behavior is mandatory in all review/remediation paths.
5. Raw branch output persistence is prohibited outside debug mode.

---

## 10. References

- `docs/specs/SPEC-002_mcp_review_scoring_handoff_identity_contracts.md`
- `docs/specs/SPEC-004_mcp_reporting_lineage_artifact_contracts.md`
- `docs/specs/SPEC-008_mcp_output_schema_contracts.md`
- `docs/architecture/MCP_OPERATIONAL_FLOWS.md`
