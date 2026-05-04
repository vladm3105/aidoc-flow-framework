---
title: MCP Saga Orchestration Pattern
tags:
  - mcp
  - architecture
  - orchestration
  - saga
  - personas
custom_fields:
  document_type: architecture-guide
  status: active
  implementation_complexity: 4
  timezone: America/New_York
---

# MCP Saga Orchestration Pattern

| Field | Value |
| --- | --- |
| Status | Active |
| Version | 1.0 |
| Date | 2026-05-04 |
| Scope | Hermes orchestration pattern for multi-persona review fan-out/fan-in with transactional compensation |

---

## 1. Purpose

Define a Saga-based orchestration pattern for Hermes when executing multi-persona review workflows on top of UCX deterministic MCP tools.

Primary goals:

- reduce end-to-end review latency by parallelizing persona execution
- reduce context pressure by scoping each persona branch to relevant sections
- preserve deterministic governance through explicit state, retries, and compensation actions

Implementation complexity: 4/5.

---

## 2. Scope

In scope:

- Hermes orchestration behavior for review fan-out/fan-in
- saga state model and branch-level compensation rules
- branch result contracts and deterministic aggregation
- merge-gate integration with existing UCX validation and remediation flow

Out of scope:

- replacement of UCX deterministic validators
- direct executor delegation from UCX document-critical tools
- automatic source-document mutation without policy gates

---

## 3. Operating Model

### 3.1 Baseline

UCX remains deterministic for document-critical stages (`sdd_validate`, `sdd_review`, `sdd_remediate`). Hermes remains the control plane for workflow state, policy gates, and escalation.

### 3.2 Parallel Review Strategy

Hermes runs persona review in bounded parallel pools instead of a single long sequential chain.

1. Resolve persona list by doc type and phase.
2. Create one branch per persona with branch-scoped context.
3. Execute branches concurrently (bounded by configured pool size).
4. Persist branch outputs and statuses to saga journal.
5. Run deterministic fan-in reducer and chairperson synthesis.
6. Continue with remediation and post-remediation validation gates.

---

## 4. Saga Transaction Design

### 4.1 Transaction Boundaries

Saga instance key:

- `review_run_id`: deterministic hash from document path, document fingerprint, persona set, and run timestamp bucket

Branch key:

- `branch_id`: deterministic hash from `review_run_id` + persona name

Transaction stages:

1. `PREPARED`
2. `FANOUT_STARTED`
3. `BRANCH_RUNNING`
4. `BRANCH_COMPLETED` or `BRANCH_FAILED`
5. `FANIN_REDUCED`
6. `SYNTHESIZED`
7. `CLOSED` or `ESCALATED`

### 4.2 Required Journal Fields

- `review_run_id`
- `document_path`
- `document_fingerprint`
- `personas_requested`
- `branches[]` with `branch_id`, `persona`, `status`, `attempt`, `started_at`, `ended_at`, `error_code`
- `retry_count`
- `compensation_actions[]`
- `final_status`

### 4.3 Compensation Rules

| Failure Condition | Compensation Action | Escalation Trigger |
| --- | --- | --- |
| Persona timeout | retry branch up to configured max | retries exhausted |
| Persona execution error | restart branch with same context snapshot | repeated deterministic error |
| Branch result schema invalid | quarantine branch output and rerun once with strict schema mode | second schema failure |
| Reducer conflict on duplicate finding IDs | regenerate deterministic IDs from content hash and rerun reducer | unresolved collisions |
| Chairperson synthesis failure | rerun synthesis once from persisted reduced set | second failure |

Compensation does not mutate source documents.

---

## 5. Context Partitioning Contract

Each branch receives:

- persona-specific instructions from `{project}/UCX/skills/personas/{persona}.md`
- section subset selected by persona category map
- shared structural rules and layer assets
- stable prompt metadata sidecar with token estimate

Branch payload must exclude unrelated section blocks when category match confidence is below configured threshold.

---

## 6. Fan-In Reducer Contract

Reducer responsibilities:

1. parse branch outputs to canonical finding schema
2. normalize priorities and categories
3. deduplicate findings by deterministic content hash
4. preserve per-persona provenance fields
5. produce reduced finding set for chairperson synthesis

Required reducer output fields:

- `finding_id`
- `priority`
- `persona`
- `message`
- `recommended_action`
- `provenance.branch_id`
- `provenance.persona`
- `content_hash`

---

## 7. Governance Integration

This pattern integrates with existing gates:

1. `sdd_validate` (pre-review structural gate)
2. Hermes saga fan-out/fan-in review
3. `sdd_remediate`
4. post-remediation `sdd_validate`
5. Hermes final blocker-gap and inconsistency check

If saga final status is `ESCALATED`, merge remains blocked.

---

## 8. Resource and Constraint Profile

| Area | Requirement |
| --- | --- |
| CPU | Moderate increase during branch parallelization |
| Memory | Moderate increase for branch contexts and reducer buffers |
| Storage | Saga journal artifacts under workflow runtime directory |
| Constraints | Idempotent branch retries, deterministic reducer behavior, source protection |

---

## 9. Failure Modes

| Failure Mode | Detection | Required Response |
| --- | --- | --- |
| Branch starvation due to oversized persona pool | scheduler metrics | reduce pool size and rerun pending branches |
| Context overflow in branch payload | token estimate warning | split section subset and rerun branch |
| Partial completion with missing branch outputs | fan-in precheck | trigger compensation for missing branches |
| Reducer non-determinism across reruns | fingerprint mismatch | fail run and escalate |

---

## 10. References

- `docs/HERMES_INTEGRATION.md`
- `docs/architecture/MCP_OPERATIONAL_FLOWS.md`
- `docs/architecture/MCP_RUNTIME_ARCHITECTURE.md`
- `docs/plans/IPLAN-006_parallel_persona_review_saga_orchestration.md`
