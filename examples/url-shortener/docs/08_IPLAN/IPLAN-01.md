---
title: "IPLAN: URL Shortener — Mapping Store"
doc_id: "IPLAN-01"
artifact_type: IPLAN
layer: 8
status: Draft
version: "1.0.1"
author: flow-walkthrough
created: "2026-06-10"
last_updated: "2026-06-10"
custom_fields:
  document_type: iplan-document
  artifact_type: IPLAN
  layer: 8
  component: Mapping Store
  deliverable_type: code
  upstream_artifacts: [SPEC-01, TDD-01]
  downstream_artifacts: [Code]
  complexity: 4
  estimated_files: 13
  session_count: 0
  code_ready_score: 90
tags:
  - iplan-document
  - layer-8-artifact
  - shared-architecture
---

# IPLAN-01: Mapping Store

Self-tag: @iplan: IPLAN-01 — the execution bridge from SPEC-01 / TDD-01 to the
`mapping_store` source component. Test-first file order is inherited from
TDD-01 §6; cumulative upstream lineage (@spec @tdd) is listed in §6. PRD/BRD/
EARS/BDD/ADR lineage is transitive via the SPEC/TDD chain and is not re-emitted.

## 1. Document Control

| Field | Value |
|-------|-------|
| Document ID | IPLAN-01 |
| Component | Mapping Store |
| Source SPEC | @spec: SPEC-01 |
| Source TDD | @tdd: TDD-01 (35 cases, 5 test files) |
| Status | Draft |
| Version | 1.0.1 |
| Author | flow-walkthrough |
| Complexity | 4 (substrate-coupled: sync-commit durability, declarative uniqueness, least-privilege reads, off-path counting) |
| Estimated files | 13 (5 test + 8 source) |
| Session count | 0 |
| CODE-Ready score | 90/100 (provisional — binding gate is doc-iplan-audit) |
| Created / Updated | 2026-06-10 |

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0.0 | 2026-06-10 | flow-walkthrough | Initial plan bridging SPEC-01 / TDD-01 v1.0.0 to `mapping_store` (saga iteration 1). |
| 1.0.1 | 2026-06-10 | doc-iplan-fixer | Iteration-1 remediation per the IPLAN-01 audit report (see fix report). |

## 2. File Manifest

Declared creation order. The five TDD-01 test files (§3) precede the eight
source files (TDD principle: Red → Green → Refactor). Source order follows the
import dependency graph: leaf value types → errors → records → contract →
access → adapter → counting → package exports. Status markers drive session
handoff (§5).

**Status legend** (the marker set the §5 resume protocol depends on):
`NOT_STARTED` (no work) · `IN_PROGRESS` (authoring open this session) ·
`PARTIAL` (session ended mid-file — `partial_work` MUST enumerate the case
IDs / method names already completed, giving the next session a deterministic
resume point) · `DONE` (file complete; `verified` reflects the §6 gate set).

| Order | Path | Kind | Status | Session | Verified |
|-------|------|------|--------|---------|----------|
| 1 | `tests/unit/test_mapping_store.py` | test (unit) | NOT_STARTED | null | false |
| 2 | `tests/unit/test_visit_count.py` | test (unit) | NOT_STARTED | null | false |
| 3 | `tests/integration/test_mapping_store_durability.py` | test (integration) | NOT_STARTED | null | false |
| 4 | `tests/integration/test_mapping_store_access.py` | test (integration) | NOT_STARTED | null | false |
| 5 | `tests/e2e/test_mapping_store_e2e.py` | test (e2e) | NOT_STARTED | null | false |
| 6 | `src/mapping_store/types.py` | source | NOT_STARTED | null | false |
| 7 | `src/mapping_store/errors.py` | source | NOT_STARTED | null | false |
| 8 | `src/mapping_store/models.py` | source | NOT_STARTED | null | false |
| 9 | `src/mapping_store/protocol.py` | source | NOT_STARTED | null | false |
| 10 | `src/mapping_store/access.py` | source | NOT_STARTED | null | false |
| 11 | `src/mapping_store/store.py` | source | NOT_STARTED | null | false |
| 12 | `src/mapping_store/visit_count.py` | source | NOT_STARTED | null | false |
| 13 | `src/mapping_store/__init__.py` | source | NOT_STARTED | null | false |

**File-to-contract map** (TDD-01 §3 coverage):

| Source file | Implements | Validated by |
|-------------|-----------|--------------|
| `types.py` | `ShortCode`, `OriginalUrl`, `EventId`, `Principal`, `Timestamp` value types + parse/validate guards | `TDD.01.04.4d8f`, `TDD.01.04.81c3` |
| `errors.py` | exception hierarchy (§4 contract) | all error-path cases |
| `models.py` | `MappingState`, `MappingRecord`, `MappingResolution`, `VisitCountRecord`, `Counts` | `TDD.01.04.093b`, `TDD.01.04.6f92` |
| `protocol.py` | `MappingStore` Protocol (§4 contract) | type-checked at boundary |
| `access.py` | principal → least-privilege DB role translation + audit-event emission; fail-closed when the access decision is unavailable | `TDD.01.04.a3e5`, `TDD.01.04.e71a`, `TDD.01.04.f82b`, `TDD.01.04.b4f6` |
| `store.py` | `put_mapping` / `resolve` / `read_original_url` / `read_counts` / `mark_taken_down`; sync commit-before-ack; declarative unique constraint; bounded degradation + load-shed with write/read pool isolation | `TDD.01.04.1a2c`, `TDD.01.04.70a3`, `TDD.01.04.92c5`, `TDD.01.04.81b4`, `TDD.01.04.a3d6`, `TDD.01.04.1a5d`, `TDD.01.04.2b6e` |
| `visit_count.py` | `increment_visit`; `event_id` dedup; off-path dispatch; dead-letter reconciliation; no-lost-update under concurrency; redirect-path non-blocking when count path stalls; N-1 payload-skew interop | `TDD.01.04.3c6f`, `TDD.01.04.4d70`, `TDD.01.04.c5f8`, `TDD.01.04.b4e7`, `TDD.01.04.5e81`, `TDD.01.04.d609` |
| `__init__.py` | package surface (re-exports the `MappingStore` boundary only) | import smoke |

## 3. Execution Commands

Runnable bash. The durable relational store (primary + synchronous standby) and
toxiproxy for the degradation/durability faults run as ephemeral containers; no
real `sleep`/restart is used in unit/integration (TDD-01 §4 conventions).

The five build phases are explicit, each with an observable gate command. An
interrupted build resuming mid-sequence audits the gate, never re-derives it
from a sibling section. The compose fixture lifecycle is crash-safe: a `down -v`
runs BEFORE `up -d` so a prior run aborted while a container is hard-killed or
degraded (the states `TDD.01.04.3c7f` / `TDD.01.04.4d80` induce) cannot leak
state into this session. The e2e destructive-fault cases own their own
fixture restore in test setup/teardown so an aborted run is self-healing.

```bash
# --- setup ---
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt          # pytest, pytest-cov, mypy, ruff, testcontainers, toxiproxy-python
docker compose -f tests/compose.yaml down -v   # crash-safe: idempotent teardown of any leaked prior state
docker compose -f tests/compose.yaml up -d     # relational primary + synchronous standby + toxiproxy
docker compose -f tests/compose.yaml ps | grep 'Up'   # readiness gate — all containers Up before integration/e2e
mkdir -p src/mapping_store tests/unit tests/integration tests/e2e

# --- implementation (test-first, per file_manifest order) ---
# Phase 1 (Red — author tests): author the 5 test files (orders 1-5) from TDD-01 §3-4.
# Phase 2 (Red gate — confirm all fail): all 5 test files exist AND the suites fail on
#   collection/import with zero passes. This is the pre-condition to enter Phase 3 (Green).
python -m pytest tests/unit tests/integration tests/e2e --collect-only 2>&1 | grep -E 'ERROR|no tests ran'
python -m pytest tests/unit tests/integration -q   # expect collection/import failures (no src yet)
# e2e is collection-only at Red so destructive-fault fixtures (hard-kill, degrade) are proven to load.
# Phase 3 (Green — author source): author the 8 source files (orders 6-13) until tests pass.
# Phase 4 (Green gate — confirm all pass): all suites green at the §3 coverage thresholds AND
#   mypy --strict + ruff clean (the canonical `verified` definition, §6). Pre-condition to Refactor.
# Phase 5 (Refactor): clean up; tests stay green.

# --- validation (Phase 4 gate set) ---
python -m pytest tests/unit -v --cov=src/mapping_store --cov-report=term-missing   # gate: unit >= 90%
python -m pytest tests/integration -v                                              # gate: integration >= 85%
python -m pytest tests/e2e -v --durations=0 --timeout=300                          # gate: e2e >= 75%, suite ceiling <= 300s
python -m mypy src/mapping_store --strict
python -m ruff check src/mapping_store tests
docker compose -f tests/compose.yaml down -v
```

**e2e timeout budgets.** The suite `--timeout=300` is the aggregate ceiling; the
per-test budgets from TDD-01 §4 are authoritative and carried as `pytest-timeout`
markers so a breach is attributable to the test, not the suite cap:
`TDD.01.04.3c7f` 60 s · `TDD.01.04.4d80` 120 s · `TDD.01.04.5e91` 90 s.

## 4. Implementation Contracts

Required: 8+ files share these interfaces (protocol, exceptions, records, state
machine), so they are declared here rather than rediscovered per file.

### Protocol interface — `MappingStore` (`protocol.py`)

The repository boundary (SPEC-01 §3). Callers depend on this Protocol, never on
the concrete adapter, so the engine is substitutable (ADR.01.05.47a1).

```python
class MappingStore(Protocol):
    def put_mapping(self, code: ShortCode, original_url: OriginalUrl) -> MappingRecord: ...
    def resolve(self, code: ShortCode) -> MappingResolution: ...
    def read_original_url(self, code: ShortCode, principal: Principal) -> OriginalUrl: ...
    def increment_visit(self, code: ShortCode, event_id: EventId) -> None: ...
    def read_counts(self, principal: Principal) -> Counts: ...
    def mark_taken_down(self, code: ShortCode) -> MappingRecord: ...
```

### Exception hierarchy (`errors.py`)

Retry semantics are part of the contract (SPEC-01 §3 Errors).

```python
class MappingStoreError(Exception): ...                 # base; carries .retryable: bool
class DuplicateCodeError(MappingStoreError): retryable = False   # code → different URL (terminal)
class DurabilityHaltError(MappingStoreError): retryable = True   # standby down; retry on recovery (ADR.01.05.5896)
class StoreDegradedError(MappingStoreError): retryable = False   # over read budget; caller degrades, no inline retry
class AccessDenied(MappingStoreError): retryable = False         # fail-closed deny (classified read / counts)
class UnknownCodeError(MappingStoreError): retryable = False     # mark_taken_down on an un-issued code
```

### State machine — `MappingState` (`models.py`)

| From | To | Trigger | Source |
|------|-----|---------|--------|
| (none) | ACTIVE | `put_mapping` durable commit | SPEC-01 §4 |
| ACTIVE | TAKEN_DOWN | `mark_taken_down` | @tdd: TDD.01.04.e729 |
| TAKEN_DOWN | TAKEN_DOWN | re-`mark_taken_down` (idempotent no-op) | @tdd: TDD.01.04.e729 |

`resolve` of a TAKEN_DOWN code returns `found=False` — state suppresses
resolution, which @tdd: TDD.01.04.70b2 verifies. The operational degraded →
recovered transition — store unreachable then restored within RTO — is owned by
the adapter, not the record state.

### Data models (`models.py`)

`MappingRecord` (code, original_url, state=ACTIVE default, created_at,
classification="may-contain-PII"); `MappingResolution` (code, found,
original_url present iff found and ACTIVE); `VisitCountRecord` (code, count
monotonic, dedup_key = last applied event_id); `Counts` (created_link_count,
per_link). Field-level totality is asserted by `TDD.01.04.093b` /
`TDD.01.04.6f92`.

### Consumed dependency (DI)

The durable async dispatch queue + dead-letter destination that carries
`increment_visit` off the redirect path is **owned by the Visit Counter**
(SPEC-01 §3), injected into `visit_count.py` as a transport interface — not
implemented in this IPLAN. The store implements only the idempotent
`event_id`-keyed consumer and reconciliation.

The consumed transport is pinned here with the same shape/version rigour the
`MappingStore` Protocol receives, so producer and consumer cannot drift to
divergent shapes at integration time (owned-by-Visit-Counter; consumed
read-only). Payload contract version: **v1** (`code + event_id`), under the
SPEC-01 §4 additive-backward-compatible / MAJOR-bump policy.

```python
class VisitDispatchTransport(Protocol):  # owned by Visit Counter; consumed read-only
    def enqueue(self, event: VisitEvent) -> None: ...           # off-path dispatch
    def ack(self, event_id: EventId) -> None: ...               # confirm consumed-once
    def dead_letter(self, event: VisitEvent, reason: str) -> None: ...  # out-of-window / staleness route
    def replay(self, event_id: EventId) -> VisitEvent | None: ...       # operator-driven idempotent replay
```

**Cross-component skew obligation (SPEC-01 §4, `TDD.01.04.d609`):** the
idempotent consumer MUST implement the skew matrix — decode the v1 payload
across **N-1 in both directions**, and route any out-of-window payload to the
dead-letter destination rather than best-effort decoding it.

### Compensating control (carried from SPEC-01 §6)

`store.py` / `access.py` keep managed-tier **volume encryption enabled** as the
interim at-rest data-protection control for the deferred column-level encryption
(SPEC-01 §6 / ADR.01.05.98ff). This compensating control stays in force until
column-level at-rest encryption lands; it must not be silently dropped at
code-build.

## 5. Session Handoff

Stateless-executor bridge. Each session: read `sessions[]` for the last state →
find the next NOT_STARTED / PARTIAL file in §2 → read `partial_work` if resuming
(for a PARTIAL file `partial_work` enumerates the case IDs / method names already
completed — resume from the first unlisted item, do not re-author a listed one)
→ continue, do not regenerate DONE work → update §2 status + §6 `code_inventory`
→ append a session with a `next_session_directive`.

```yaml
sessions:
  - date: "2026-06-10"
    agent: "bootstrap (plan author)"
    files_touched: []          # no code written yet — plan seed only
    partial_work: "None — IPLAN authored; implementation not started."
    blockers: "None. Requires the tests/compose.yaml store fixtures from §3 setup before integration/e2e can run."
    next_session_directive: >
      Readiness gate first: run `docker compose -f tests/compose.yaml ps | grep
      'Up'`; if no containers are Up, run the §3 setup block before any
      integration or e2e command (a missing stack surfaces as opaque failures,
      not a code defect). Then start Phase 1 (Red). Author file order 1 —
      tests/unit/test_mapping_store.py — from TDD-01 §4 (unit cases on
      test_mapping_store.py: 1a2c, 2b4d, 3c6e, 4d8f, 5e90, 6fa1, 70b2, 81c3,
      92d4, a3e5, b4f6, c507, d618, e729, f83a, 093b). Run pytest, confirm Red
      (no src/mapping_store yet), then proceed to order 2. Do NOT author source
      files until all 5 test files exist and fail.
    validation_results:
      tests_passing: null
      coverage: null
      lint_clean: false
```

**Operational handoff.** When `mapping_store` enters a running environment, the
on-call runbook and monitoring config must be updated to cover the contract's
failure surface: `DurabilityHaltError` (standby loss / RPO = 0 commit-lag
alert) and `StoreDegradedError` (degradation counter labelled by
`degradation_type`, RTO ≤ 30 min recovery). Naming the runbook section and the
dashboard that surface these is a downstream obligation of the first
to-production session, out of scope for this code-build IPLAN.

## 6. Traceability

@iplan: IPLAN-01 — self-tag. Layer 8 carries necessary-upstream @spec @tdd;
PRD/BRD/EARS/BDD/ADR lineage is transitive via the SPEC/TDD chain.

**Upstream**

- @spec: SPEC-01
- @tdd: TDD.01.04.1a2c @tdd: TDD.01.04.3c6f @tdd: TDD.01.04.70a3 @tdd: TDD.01.04.e71a @tdd: TDD.01.04.3c7f — representative anchors; the full 35-case TDD-01 §4 contract is implemented in whole.

**Downstream**

- @code: src/mapping_store/
- @tests: tests/unit/ tests/integration/ tests/e2e/

**Code inventory** (audit trail — populated per session). Canonical `verified`
(referenced from §2, §5, and the §3 Phase-4 gate): tests pass AND coverage ≥ the
tier threshold (§3) AND `mypy --strict` clean AND `ruff` clean.

| Path | Status | Session | Verified |
|------|--------|---------|----------|
| _(empty — no files created yet)_ | — | — | — |

Health: 5/5 test files mapped · 6/6 methods · 4/4 data models · 13 files. Binding
gate is doc-iplan-audit.

## Glossary

| Term | Definition |
|------|------------|
| Red → Green → Refactor | TDD cycle: write a failing test, make it pass, clean up keeping it green. |
| Session handoff | The stateless-executor protocol (§5): each session resumes from recorded file status without regenerating completed work. |
| Code inventory | The §6 audit trail of every file created/modified, with session attribution and verification status. |
| RPO = 0 | No committed mapping is lost on failure — enforced by synchronous commit-before-ack. |
| Dead-letter | Destination for an `increment_visit` event unreconciled past the count-staleness window; replayed through the idempotent path on operator action. |
