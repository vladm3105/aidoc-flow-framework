---
title: "IPLAN-007: Persona Branch LLM Fan-Out/Fan-In Execution"
id: IPLAN-007
date_created: 2026-05-04
last_updated: 2026-05-04
status: planned
owner: ai-agent
tags:
  - implementation-plan
  - hermes
  - saga
  - review
  - remediation
  - litellm
  - api-executors
custom_fields:
  document_type: iplan
  plan_id: IPLAN-007
  execution_state: not_started
  created_date: 2026-05-04
  timezone: America/New_York
---

## IPLAN-007: Persona Branch LLM Fan-Out/Fan-In Execution

## 1. Objective

Implement true persona-branch LLM execution in saga review so each persona branch performs an API call and returns branch findings to orchestrator fan-in.

## 2. Scope

### In Scope

1. Branch-level API executor calls in saga review.
2. Persona-output parsing into normalized findings.
3. Branch telemetry capture (executor, model, timing, token usage when available).
4. Fan-in reducer integration with branch LLM outputs.
5. Persona-to-executor/model routing with LiteLLM defaults.
6. API generation controls (`temperature`, `top_p`, `top_k`, `max_output_tokens`).
7. Review/remediation API-only enforcement.

### Out of Scope

1. External workflow engine migration.
2. Non-review stage saga orchestration.
3. Deterministic validation rule redesign.

## 3. Problem Statement

Current saga review parallelizes persona branch orchestration but does not execute LLM per persona branch. This limits time reduction and context partitioning benefits expected from concurrent persona analysis.

## 3.1 Contract Gate (Mandatory Before Runtime Changes)

Update and align normative contracts before branch-LLM runtime activation:

1. `docs/specs/SPEC-007_mcp_review_remediation_operational_contracts.md`
2. `docs/specs/SPEC-008_mcp_output_schema_contracts.md`
3. `docs/specs/SPEC-004_mcp_reporting_lineage_artifact_contracts.md`
4. `docs/specs/SPEC-002_mcp_review_scoring_handoff_identity_contracts.md`

Gate requirement:

1. Runtime behavior changes must not merge before contract updates are merged in same or earlier changeset.

## 4. Target Runtime Behavior

1. `sdd_review` with `review_mode=saga_parallel` creates one branch per persona.
2. Each branch assembles persona-scoped prompt and executes API LLM call.
3. Each branch parses LLM output to normalized findings.
4. Orchestrator fan-ins all branch findings and runs deterministic reducer.
5. Synthesis step produces consolidated review output.
6. Retry/compensation/escalation remain active for branch failures/timeouts.

## 4.1 Branch LLM Input/Output Contract

Branch prompt output contract:

1. Branch LLM responses must request machine-parseable JSON output first.
2. Required finding fields:
   - `priority`
   - `category`
   - `message`
   - `recommended_action`
   - `target_layer`
3. Required branch metadata fields:
   - `persona`
   - `branch_id`
   - `attempt`
   - `parse_status`

Parser fallback order:

1. Strict JSON parse.
2. Structured block extraction.
3. Deterministic fallback finding emission.

## 4.2 Conflict Resolution and Fan-In Tie-Break

When multiple personas report overlapping findings:

1. Deduplicate by normalized content hash.
2. Priority precedence: `P0 > P1 > P2 > P3`.
3. If equal priority, preserve lowest lexical category.
4. If category also equal, preserve first deterministic branch order by `branch_id`.
5. Preserve all contributing personas in provenance list.

## 5. Workstreams

### 5.1 Workstream A: Branch LLM Execution Contract

Target modules:

1. `src/mcp_server/review/saga_orchestrator.py`
2. `src/mcp_server/review/runner.py`

Deliverables:

1. Branch result payload schema with:
   - `persona`, `branch_id`, `attempt`
   - `executor`, `model`
   - `latency_ms`
   - `token_usage` (when returned by provider)
   - `parse_status`
   - `findings`
2. Executor invocation in each branch via API path only.

Acceptance criteria:

1. Branches call API executors concurrently under configured max parallel limit.
2. Branch failures trigger retry/compensation logic.

### 5.2 Workstream B: Persona Output Parser

Target modules:

1. `src/mcp_server/review/persona_output_parser.py` (new)

Deliverables:

1. Parse persona output into canonical finding schema.
2. Fallback parsing path for malformed output.
3. Parser failure finding emission with deterministic IDs after reducer.

Acceptance criteria:

1. Parser yields machine-parseable findings for valid outputs.
2. Malformed outputs produce bounded fallback findings and do not crash saga run.

### 5.3 Workstream C: Persona Model Routing and LiteLLM Defaults

Target modules:

1. `src/mcp_server/executor/registry.py`
2. `src/mcp_server/executor/api_runner.py`
3. `src/mcp_server/skills/project_ucx_loader.py`

Deliverables:

1. Default API executor profile for review/remediation using LiteLLM server.
2. Persona-to-executor/model routing override support.
3. Generation control pass-through support:
   - `temperature`
   - `top_p`
   - `top_k` (provider-specific)
   - `max_output_tokens`

Acceptance criteria:

1. Default branch executor uses configured LiteLLM API route.
2. Persona-level overrides apply deterministically.

Default runtime matrix:

1. Review executor default: `api/openrouter` (override allowed).
2. Remediation executor default: `api/claude-sonnet` (override allowed).
3. API base default: `UCX_EXECUTOR_API_BASE` or executor config value.
4. Timeout default: 300 seconds unless overridden.
5. Generation defaults:
   - `temperature=0.2`
   - `top_p=0.9`
   - `top_k` unset by default
   - `max_output_tokens=4000`

### 5.4 Workstream D: Fan-In and Synthesis

Target modules:

1. `src/mcp_server/review/saga_reducer.py`
2. `src/mcp_server/review/saga_orchestrator.py`

Deliverables:

1. Fan-in of branch LLM findings with branch provenance.
2. Reducer deduplication and identity contract preservation.
3. Consolidated synthesis output generation.

Acceptance criteria:

1. Reduced output deterministic for identical branch outputs.
2. `finding_id` and `action_id` remain contract compliant.

## 6. Lifecycle Integration

Default lifecycle chain:

1. `validate`
2. `review` (saga parallel, branch-level API calls)
3. `remediate` (API-only apply)
4. `validate` (post-AI structural gate)

Requirement:

1. No extra confirmation gate between review and remediation in default pipeline behavior.

## 6.1 Failure Semantics and Error Codes

Lifecycle stop rules:

1. Stop at `review` when saga status is `ESCALATED`.
2. Stop at `review` on branch parser hard failure after retry exhaustion.
3. Stop at `review` on API auth/rate-limit/timeout exhaustion.
4. Stop at `remediate` when API executor returns non-zero exit code.

Required error codes:

1. `ExecutorRequired`
2. `ExecutorTypeNotAllowed`
3. `ExecutorFailed`
4. `SagaEscalated`
5. `BranchParseFailed`
6. `BranchTimeoutExceeded`

## 6.2 Feature Flag and Rollout Policy

Feature flag:

1. `saga_branch_llm_enabled` controls branch-level LLM execution.

Rollout phases:

1. Phase A: off by default, canary projects only.
2. Phase B: on for review with fallback retained.
3. Phase C: on by default after acceptance metrics pass.

Rollback trigger:

1. Two consecutive pipeline runs with unresolved branch escalation caused by parser/runtime regression.

## 7. Test Plan

1. Unit tests for branch API execution path and parser behavior.
2. Unit tests for persona model routing.
3. Integration tests for saga fan-out/fan-in with mixed branch outcomes.
4. Regression tests for lifecycle stop reasons and artifact path outputs.
5. Contract tests for branch JSON schema and error code domain.

## 8. Risks and Mitigations

1. Provider rate limits under concurrent branches.
   - Mitigation: bounded parallelism, retry with backoff, escalation thresholds.
2. Malformed model output.
   - Mitigation: strict parser + fallback findings.
3. Cost increase from parallel branch calls.
   - Mitigation: persona-based model tiering and max token limits.

4. Sensitive output leakage in branch artifacts.
   - Mitigation: redact secrets/tokens from persisted logs and summaries.

## 8.1 Artifact and Telemetry Retention Policy

1. Persist branch raw outputs only when debugging mode is enabled.
2. Persist normalized branch summaries and reducer outputs by default.
3. Redact secret-like patterns before write.
4. Retain saga artifacts with existing versioned naming contract.

## 8.2 Quantitative Acceptance Metrics

1. Wall-clock review latency reduction >= 30% vs sequential baseline for >=3 personas.
2. Per-branch prompt token footprint <= 60% of equivalent combined prompt token footprint.
3. Branch parse success rate >= 95% across integration test corpus.
4. No increase in post-review deterministic validation failure rate beyond 5% relative baseline.

## 9. Completion Criteria

1. Persona branch paths perform real API LLM calls in saga mode.
2. Orchestrator fan-ins parsed branch findings and produces deterministic reduced output.
3. Lifecycle flow operates as `validate -> review -> remediate -> validate` without confirmation pause.
4. Review/remediation remain API-only executor paths.
5. All updated unit/integration tests pass.
6. Contract/spec documents are updated and validated before runtime flag default-on.
