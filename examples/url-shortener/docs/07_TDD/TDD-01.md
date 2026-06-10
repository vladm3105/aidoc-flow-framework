---
title: "TDD: URL Shortener — Mapping Store"
doc_id: "TDD-01"
artifact_type: TDD
layer: 7
status: Draft
version: "1.0.0"
author: flow-walkthrough
created: "2026-06-10"
last_updated: "2026-06-10"
custom_fields:
  document_type: tdd-document
  artifact_type: TDD
  layer: 7
  component: Mapping Store
  deliverable_type: code
  upstream_artifacts: [EARS-01, BDD-01, ADR-01, SPEC-01]
  downstream_artifacts: [IPLAN-01]
  iplan_ready_score: 90
tags:
  - tdd-document
  - layer-7-artifact
  - shared-architecture
---

# TDD-01: Mapping Store

Self-tag: @tdd: TDD-01 — test cases validating the SPEC-01 Mapping Store
contract. Cumulative upstream tags (@ears @bdd @adr @spec) are listed in §7;
PRD/BRD lineage is transitive via the EARS/BDD chain.

## 1. Document Control

| Field | Value |
|-------|-------|
| Document ID | TDD-01 |
| Component | Mapping Store |
| Status | Draft |
| Version | 1.0.0 |
| Author | flow-walkthrough |
| SPEC reference | @spec: SPEC-01 |
| IPLAN readiness score | 90/100 (provisional — binding gate is doc-tdd-audit) |
| Created / Updated | 2026-06-10 |

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0.0 | 2026-06-10 | flow-walkthrough | Initial test guide from SPEC-01 v1.0.0; 15 Mapping-Store BDD scenarios mapped to 35 cases (saga iteration 1). |

## 2. Test Pyramid

Effort distribution (targets, not quotas).

| Type | Target | Actual | Focus |
|------|--------|--------|-------|
| unit | 70% | 57% (20/35) | method contracts + data-model field validation |
| integration | 20% | 34% (12/35) | durable commit-before-ack, declarative uniqueness, concurrency, dead-letter/skew, authz, load shed |
| e2e | 10% | 9% (3/35) | RPO = 0 survival, degrade→recover, off-path reconciliation |

The integration band runs above target because the load-bearing guarantees —
synchronous commit-before-ack (RPO = 0), the declarative unique constraint,
no-lost-update under concurrency, and at-least-once delivery with dead-letter —
are substrate-coupled and cannot be isolated in a pure unit.

## 3. Test Mapping

Each of the 15 Mapping-Store BDD scenarios (SPEC-01 §8) maps to test types and
files. `@spec`/`@ears`/`@adr` rows are contract-derived (no single BDD scenario
isolates them). Test files precede code (§6).

| Scenario / source | Behavior | Unit | Integration | E2E |
|---|---|---|---|---|
| @bdd: BDD.01.03.9b90 | durable commit before ack (RPO = 0) | `TDD.01.04.1a2c` | `TDD.01.04.70a3` | `TDD.01.04.3c7f` |
| @bdd: BDD.01.03.a688 | one URL per code (unique-constraint property) | `TDD.01.04.3c6e` | `TDD.01.04.92c5` | — |
| @bdd: BDD.01.03.5ab2 | resolve unknown → not-found | `TDD.01.04.6fa1` | — | — |
| @bdd: BDD.01.03.3c70 | taken-down → not-found; audit on takedown | `TDD.01.04.70b2` `TDD.01.04.e729` | `TDD.01.04.093c` | — |
| @bdd: BDD.01.03.c8a6 | classified read denied without grant | `TDD.01.04.a3e5` | `TDD.01.04.e71a` | — |
| @bdd: BDD.01.03.167e | classified read permitted with grant | `TDD.01.04.92d4` | `TDD.01.04.e71a` | — |
| @bdd: BDD.01.03.cb64 | Service-Owner sees counts | `TDD.01.04.c507` | `TDD.01.04.f82b` | — |
| @bdd: BDD.01.03.6921 | non-owner denied counts, no disclosure | `TDD.01.04.d618` | `TDD.01.04.f82b` | — |
| @bdd: BDD.01.03.5645 | visit count increments once off the redirect path | `TDD.01.04.3c6f` | — | — |
| @bdd: BDD.01.03.1365 | re-delivered event does not double-count | `TDD.01.04.4d70` | — | — |
| @bdd: BDD.01.03.02c1 | concurrent visits lose no increment | — | `TDD.01.04.b4e7` | — |
| @bdd: BDD.01.03.976e | count path stalls, reconciles exactly-once | `TDD.01.04.5e81` | `TDD.01.04.c5f8` | `TDD.01.04.5e91` |
| @bdd: BDD.01.03.1f90 | store degradation → bounded error | — | `TDD.01.04.a3d6` `TDD.01.04.1a5d` | `TDD.01.04.4d80` |
| @bdd: BDD.01.03.44fe | store recovers, redirects resume within RTO | — | — | `TDD.01.04.4d80` |
| @bdd: BDD.01.03.588f | invalid destination rejected at store boundary | `TDD.01.04.4d8f` | — | — |
| @ears: EARS.01.03.c4c9 | `resolve`/`mark_taken_down` ShortCode allowlist | `TDD.01.04.81c3` | — | — |
| @ears: EARS.01.03.4ebf | classified read fail-closed when decision unavailable | `TDD.01.04.b4f6` | — | — |
| @adr: ADR.01.05.5896 | standby loss → durability halt, fail-closed | — | `TDD.01.04.81b4` | — |
| @spec: SPEC-01 §4 | data-model totality (4 records) | `TDD.01.04.093b` `TDD.01.04.6f92` | `TDD.01.04.d609` | — |
| @spec: SPEC-01 §6 | read/create design-load, overload shed | — | `TDD.01.04.2b6e` | — |

Files (test-first): `tests/unit/test_mapping_store.py` ·
`tests/unit/test_visit_count.py` ·
`tests/integration/test_mapping_store_durability.py` ·
`tests/integration/test_mapping_store_access.py` ·
`tests/e2e/test_mapping_store_e2e.py`. Coverage: 15/15 BDD scenarios, 6/6
methods, 4/4 data models; 35 cases (unit 20, integration 12, e2e 3).

## 4. Test Cases

Element IDs are four-segment, declared here in Section 4; trace tags in §7.
Cases tagged `type: security` carry a `threat`; e2e cases carry a `bdd_ref`.
Conventions: each unit case builds a fresh function-scoped in-memory store
double (order-independent); faults come from a controllable adapter double or
toxiproxy with a deterministic clock — never a real sleep or restart — and each
fault case clears the fault and asserts a clean baseline before the next.

**Unit — `tests/unit/test_mapping_store.py`** (SPEC §3–4):

- `TDD.01.04.1a2c` `put_mapping` on a free code → `MappingRecord(state=ACTIVE, classification="may-contain-PII")`; a later `resolve` returns it. type: unit.
- `TDD.01.04.2b4d` `put_mapping` retried with the same `(code, url)` → idempotent no-op success (the unique constraint makes the re-INSERT succeed, not a duplicate); one record. type: unit.
- `TDD.01.04.3c6e` `put_mapping` of an existing code with a different url → `DuplicateCodeError` (terminal, not-retryable); the winner is unchanged. type: unit.
- `TDD.01.04.4d8f` `put_mapping` with an invalid `original_url` (empty / over the URL max-length cap / javascript: / data: / file: / embedded NUL) → rejected at the store boundary before any write. type: security. threat: CWE-20.
- `TDD.01.04.5e90` `resolve` of a known ACTIVE code → `MappingResolution(found=True, original_url)`. type: unit.
- `TDD.01.04.6fa1` `resolve` of an unknown code → `found=False`, `original_url` absent; never raises. type: unit.
- `TDD.01.04.70b2` `resolve` of a TAKEN_DOWN code → `found=False` (state suppresses resolution). type: unit.
- `TDD.01.04.81c3` `resolve` / `mark_taken_down` with a code outside the generation charset/length allowlist → rejected before the PK lookup (defense in depth). type: security. threat: CWE-20.
- `TDD.01.04.92d4` `read_original_url` with the least-privilege grant → returns the `original_url`. type: unit.
- `TDD.01.04.a3e5` `read_original_url` without the grant → `AccessDenied`, fail-closed; no value disclosed. type: security. threat: CWE-862.
- `TDD.01.04.b4f6` `read_original_url` when the access decision is unavailable (grant down / classification missing / role-lookup error) → `AccessDenied`, fail-closed. type: security. threat: CWE-862.
- `TDD.01.04.c507` `read_counts` for a Service-Owner → `Counts(created_link_count, per_link)`. type: unit.
- `TDD.01.04.d618` `read_counts` by a non-Service-Owner → `AccessDenied`; no count disclosed. type: security. threat: CWE-862.
- `TDD.01.04.e729` `mark_taken_down` on a live code → `state=TAKEN_DOWN`; re-mark is an idempotent no-op success (converges). type: unit.
- `TDD.01.04.f83a` `mark_taken_down` of a code never issued → `UnknownCodeError` (not-retryable). type: unit.
- `TDD.01.04.093b` data-model totality: `MappingRecord` required fields, `state` defaults ACTIVE, `classification == "may-contain-PII"`; `MappingResolution` found=True ⇒ url present and ACTIVE, found=False ⇒ url absent; `Counts` maps each issued code to its count. type: unit.

**Unit — `tests/unit/test_visit_count.py`** (SPEC §3–4):

- `TDD.01.04.3c6f` `increment_visit` for a fresh `event_id` → count `+= 1` off the synchronous redirect path, returns `None`, raises nothing; `dedup_key` advanced. type: unit.
- `TDD.01.04.4d70` `increment_visit` re-delivered with the same `event_id` → count unchanged (idempotent on `event_id`). type: unit.
- `TDD.01.04.5e81` `increment_visit` while the count path is stalled → returns `None`, never blocks/raises on the redirect path; increment deferred off-path. type: unit.
- `TDD.01.04.6f92` `VisitCountRecord` totality: `count` monotonic and exactly-once reconciled; `dedup_key` is the last applied `event_id`. type: unit.

**Integration — `tests/integration/test_mapping_store_durability.py`** (real adapter, SPEC §5–6):

- `TDD.01.04.70a3` `put_mapping` returns only after the durable commit on more than one replica is observed (RPO = 0); no write-behind; durable-commit-latency metric and a `put_mapping` span emitted. type: integration.
- `TDD.01.04.81b4` `put_mapping` with the synchronous standby unavailable → `DurabilityHaltError`, fail-closed (RPO = 0 over availability); the read path is unaffected; a durability-halt signal fires; the retry is retryable on standby recovery using bounded backoff with jitter (no storm). type: integration.
- `TDD.01.04.92c5` two coroutines released on a shared barrier `put_mapping` the same code → exactly one `MappingRecord`, one `DuplicateCodeError`, no orphan; the unique constraint is database-declarative (an adapter that re-checks in app code is non-conformant). type: integration.
- `TDD.01.04.a3d6` `resolve` with the store degraded (unreachable / dns / tls / slow) → `StoreDegradedError` within the redirect budget; a `mapping_store_degraded` counter labelled by `degradation_type`; no hang past budget, no unshed 5xx. type: integration.
- `TDD.01.04.b4e7` 50 confirmed visits to one code dispatched behind a shared barrier → no lost updates, reconciled `count == 50`; partial-field write only, never blocks `resolve`. type: integration.
- `TDD.01.04.c5f8` an `increment_visit` event still unreconciled when the count-staleness window elapses is routed to the dead-letter destination and alerted (time-driven, not retry-count); reconciliation-lag and dead-letter metrics fire; operator replay through the idempotent path closes exactly-once. type: integration.
- `TDD.01.04.d609` `increment_visit` payload skew — producer/consumer interoperate across N-1 in both directions (decode); a payload outside the window is rejected to the dead-letter destination, never best-effort decoded. type: integration.
- `TDD.01.04.1a5d` `resolve` read design-load — sustained over a ~10^6-link envelope: p95 holds within the redirect budget; beyond a safe-overload margin the bounded read pool fast-fails to the bounded degraded response rather than exhausting the pool. type: performance.
- `TDD.01.04.2b6e` `put_mapping` create design-load — beyond a safe-overload margin the create path fast-fails with a bounded error and sheds (no unbounded queue); the create timeout caps write-connection hold; write and read pools are isolated so a stalled standby cannot starve reads. type: performance.

**Integration — `tests/integration/test_mapping_store_access.py`** (SPEC §5–6, audit plane):

- `TDD.01.04.e71a` `read_original_url` permit + deny verified together — the caller is translated at the API→Store boundary to a per-call-path least-privilege DB role; the grant is evaluated against that role, never a shared service account; an audit event `{subject, action, resource, decision, timestamp, reason}` is emitted on both paths. type: security. threat: CWE-285.
- `TDD.01.04.f82b` `read_counts` Service-Owner permit + non-owner deny; a deny-path audit event is emitted; no count is disclosed on deny. type: integration.
- `TDD.01.04.093c` `mark_taken_down` emits an audit event on the takedown and on a re-mark, so an unauthorized or erroneous takedown of a live code is traceable. type: integration.

**E2E — `tests/e2e/test_mapping_store_e2e.py`**:

- `TDD.01.04.3c7f` bdd_ref @bdd: BDD.01.03.9b90 — `put_mapping` → ack; hard-kill the store before any post-ack flush; restart; `resolve` still returns the original URL (RPO = 0 confirmed by survival). timeout 60 s; cleanup tear down store + namespace. type: e2e.
- `TDD.01.04.4d80` bdd_ref @bdd: BDD.01.03.1f90 | @bdd: BDD.01.03.44fe — store degraded during redirect → bounded `StoreDegradedError` + `mapping_store_degraded` signal; restore; `resolve` resumes within RTO ≤ 30 min. timeout 120 s; cleanup restore + assert healthy. type: e2e.
- `TDD.01.04.5e91` bdd_ref @bdd: BDD.01.03.976e — count path stalled while 12 confirmed visits occur; restore; reconcile the 12 exactly-once without loss; a `counting_path_recovered` event (or INFO log with `reconciled_count`); reconcile again → no double-count. timeout 90 s; cleanup drain queue. type: e2e.

## 5. Thresholds

CI enforces these gates.

| Type | Coverage | Pass criteria | Fail action |
|------|----------|---------------|-------------|
| unit | ≥ 90% | all pass; no skips | block merge |
| integration | ≥ 85% | commit-before-ack + declarative-uniqueness + no-lost-update + at-least-once contracts validate | block merge |
| e2e | ≥ 75% happy paths; ≤ 300 s | RPO = 0, degrade→recover, reconciliation pass; no regressions | block deploy to staging |
| security | all authz + classified-read paths | classified read + count read fail-closed; input re-validation holds | block deploy |
| performance | design-load + safe-overload margin | p95 within budget; bounded degraded response; create fast-fail-and-shed | block deploy |

Per-operation latency gates:

| Operation | Gate | Threshold |
|-----------|------|-----------|
| `resolve` (incl. `StoreDegradedError` raise) | p95 / fail-fast within the redirect budget | @threshold: PRD.01.perf.redirectp95 |
| `put_mapping` | within the create/screening budget | @threshold: PRD.01.perf.screeningdeadline |
| visit-count reconciliation | within the count-staleness window | @threshold: PRD.01.reliability.countstaleness |

Runtime baselines via `pytest --durations=0` on the first green run; over-budget
tests quarantined within one business day. Flake budgets: unit 0%, integration
≤ 1% (30-day rolling), e2e ≤ 2%; > 50% over baseline trips an investigation gate.

## 6. TDD Order

Test-first generation (Red → Green → Refactor); test files precede code.

| Phase | Name | Action |
|-------|------|--------|
| 1 | Write Tests | generate all five test files from §3–4 |
| 2 | Run (Red) | execute; confirm failure (no implementation yet) |
| 3 | Implement | generate the `MappingStore` adapter to pass tests |
| 4 | Verify (Green) | re-run; confirm all pass |
| 5 | Refactor | clean up; tests stay green |

Phase-1 order: unit → integration → e2e.

## 7. Traceability

Document tag: @tdd: TDD-01 — self-tag. Cumulative upstream tags (Layer 7
necessary-upstream contract @ears @bdd @adr @spec); PRD/BRD lineage is
transitive via the EARS/BDD chain and is not re-emitted.

- @spec: SPEC-01
- @adr: ADR-01 @adr: ADR.01.03.4226 @adr: ADR.01.05.47a1 @adr: ADR.01.05.454a @adr: ADR.01.05.5896 @adr: ADR.01.05.7dde @adr: ADR.01.05.2740
- @ears: EARS.01.04.5e5b @ears: EARS.01.03.bca8 @ears: EARS.01.03.4ebf @ears: EARS.01.04.1898 @ears: EARS.01.03.c4c9 @ears: EARS.01.03.e4db @ears: EARS.01.03.f62a @ears: EARS.01.03.4425 @ears: EARS.01.03.9425 @ears: EARS.01.03.aa59
- @bdd: BDD.01.03.9b90 @bdd: BDD.01.03.a688 @bdd: BDD.01.03.c8a6 @bdd: BDD.01.03.167e @bdd: BDD.01.03.5ab2 @bdd: BDD.01.03.3c70 @bdd: BDD.01.03.5645 @bdd: BDD.01.03.1365 @bdd: BDD.01.03.02c1 @bdd: BDD.01.03.976e @bdd: BDD.01.03.1f90 @bdd: BDD.01.03.44fe @bdd: BDD.01.03.cb64 @bdd: BDD.01.03.6921 @bdd: BDD.01.03.588f

Downstream: @iplan: IPLAN-01 references this TDD and enforces test-before-code.
Thresholds: @threshold: PRD.01.perf.redirectp95 @threshold: PRD.01.perf.screeningdeadline @threshold: PRD.01.reliability.countstaleness

Health: 15/15 BDD scenarios · 6/6 methods · 4/4 data models · target ≥ 90/100.

## Glossary

| Term | Definition |
|------|------------|
| RPO | Recovery Point Objective; RPO = 0 means no committed mapping is lost on failure. |
| RTO | Recovery Time Objective; the bound within which resolves resume after an outage (≤ 30 min). |
| Idempotency key | The `dedup_key` / `event_id` reconciling at-least-once delivery to exactly-once. |
| Dead-letter | Destination for an event unreconciled past the count-staleness window; replayed on operator action. |
| Fail-closed | On a durability or access-decision failure, deny rather than proceed unsafely. |
