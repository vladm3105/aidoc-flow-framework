---
title: "EARS: URL Shortener"
doc_id: "EARS-01"
artifact_type: EARS
layer: 3
status: Draft
version: "1.0.0"
created: "2026-06-10"
last_updated: "2026-06-10"
custom_fields:
  document_type: ears-document
  artifact_type: EARS
  layer: 3
  deliverable_type: code
  upstream_artifacts: [PRD-01]
  downstream_artifacts: [BDD-01]
  bdd_ready_score: 93
---

# EARS-01: URL Shortener

## 1. Document Control

| Field | Value |
|-------|-------|
| Document ID | EARS-01 |
| Status | Draft |
| Version | 1.0.0 |
| Priority | P1 |
| Source document | @prd: PRD.01.09.b6cb |
| BDD readiness score | 93 / 100 |
| Created | 2026-06-10 |
| Last updated | 2026-06-10 |
| Author | flow-walkthrough (Requirements Engineer) |

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0.0 | 2026-06-10 | flow-walkthrough | Initial EARS formalization of PRD-01 §9 (saga iteration 1). |

## 2. Purpose and Context

Purpose: formalize the PRD-01 §9 functional requirements into atomic, testable
WHEN-THE-SHALL-WITHIN statements ready for BDD translation.

Scope: the five PRD-01 MVP features — create short link (PRD.01.09.b6cb),
redirect (PRD.01.09.dd8d), handle unknown code (PRD.01.09.e525), count visits
(PRD.01.09.d101), and reject invalid destination (PRD.01.09.9e0f) — plus their
error, security, and reliability behaviors. Upstream BRD lineage is reachable
transitively via the PRD's own `@brd` tags; this layer carries `@prd` only.

Audience: BDD authors, system architects, QA engineers.

Component naming follows the PRD-01 container view: **Shorten/Redirect API** and
**Visit Counter** over a single **Mapping Store**.

## 3. Requirements

### Event-Driven (WHEN … THE … SHALL … WITHIN)

- **EARS.01.03.5066 — Create short link**
  WHEN a Link Submitter submits a well-formed public http/https URL of at most
  the maximum length, THE Shorten/Redirect API SHALL return a unique short code
  that resolves to the exact submitted URL WITHIN the create-path screening
  deadline. A duplicate submission of the same destination URL MAY return a
  previously-issued code or a newly-issued code; either outcome SHALL satisfy the
  code-to-URL uniqueness invariant (EARS.01.03.bca8). The collision-free
  generation strategy is owned by the code-generation ADR topic (BRD.01.08.9665).
  @prd: PRD.01.09.b6cb | @threshold: PRD.01.quota.urlmaxlen | @threshold: PRD.01.perf.screeningdeadline | @bdd: BDD-01
- **EARS.01.03.c4c9 — Redirect issued code**
  WHEN a Link Visitor requests an issued short code, THE Shorten/Redirect API
  SHALL redirect to the mapped original URL WITHIN p95 < 50 ms on the redirect
  path.
  @prd: PRD.01.09.dd8d | @threshold: PRD.01.perf.redirectp95 | @bdd: BDD-01
- **EARS.01.03.4425 — Increment visit count**
  WHEN a redirect for an issued code is served, THE Visit Counter SHALL increment
  that code's visit count by exactly one, dispatched off the synchronous redirect
  path, WITHIN the visit-count reconciliation window. Each confirmed redirect
  event SHALL increment the counter exactly once; duplicate delivery of the same
  event SHALL NOT produce a second increment, with the deduplication mechanism
  owned by the visit-observability ADR topic (BRD.01.08.c478).
  @prd: PRD.01.09.d101 | @threshold: PRD.01.reliability.countstaleness | @bdd: BDD-01

### State-Driven (WHILE … THE … SHALL … WITHIN)

- **EARS.01.03.feaa — Sustain redirect availability**
  WHILE the service is in normal operation, THE Shorten/Redirect API SHALL serve
  redirects for issued codes at ≥ 99.9% monthly availability WITHIN the
  production load envelope (100 redirects/sec sustained, up to 20 concurrent
  visitors per link, ~10⁶-link corpus).
  @prd: PRD.01.09.dd8d | @threshold: PRD.01.reliability.availabilitymonthly | @threshold: PRD.01.rate.redirectsustained | @bdd: BDD-01
- **EARS.01.03.f766 — Concurrent count no-loss**
  WHILE multiple visits to one short code are processed concurrently, THE Visit
  Counter SHALL record every confirmed visit without loss WITHIN the visit-count
  reconciliation window. Each distinct confirmed visit SHALL be counted exactly
  once under concurrent conditions; where at-least-once delivery is used, the
  deduplication step owned by the visit-observability ADR topic (BRD.01.08.c478)
  reconciles to the exactly-once outcome (consistent with EARS.01.03.4425).
  @prd: PRD.01.09.d101 | @threshold: PRD.01.reliability.countstaleness | @bdd: BDD-01
- **EARS.01.03.eca5 — Capacity-utilization alert**
  WHILE short-code utilization is at or above the alert threshold, THE
  Shorten/Redirect API SHALL emit a capacity-utilization alert WITHIN the
  capacity-monitoring envelope. This detection obligation pairs with the
  reject-at-capacity recovery (EARS.01.03.5442).
  @prd: PRD.01.09.b6cb | @threshold: PRD.01.quota.codespacecapacity | @bdd: BDD-01

### Optional / Feature-Gated (WHERE … THE … SHALL)

- **EARS.01.03.6811 — Screen destination at create**
  WHERE destination-reputation screening is enabled (a go-live precondition),
  THE Shorten/Redirect API SHALL screen each candidate destination at create
  time.
  @prd: PRD.01.09.b6cb | @bdd: BDD-01
- **EARS.01.03.4400 — Withhold code for unscreened destination**
  WHERE destination-reputation screening is enabled (a go-live precondition),
  THE Shorten/Redirect API SHALL NOT issue a code for an unscreened or flagged
  destination.
  @prd: PRD.01.09.b6cb | @bdd: BDD-01

### Unwanted Behavior / Error Handling (IF … THE … SHALL … WITHIN)

- **EARS.01.03.97be — Reject invalid destination**
  IF a submitted destination is not a well-formed public http/https web address
  (empty/blank, longer than the maximum length, a non-http/https scheme including
  `javascript:`/`data:`/`file:`, or malformed/relative), THE Shorten/Redirect API
  SHALL reject it with the invalid-destination message, returning neither a 5xx
  nor an issued code, WITHIN the create response.
  @prd: PRD.01.09.9e0f | @threshold: PRD.01.quota.urlmaxlen | @bdd: BDD-01
- **EARS.01.03.e4db — Unknown code not-found**
  IF a requested short code was never issued or is unresolvable, THE
  Shorten/Redirect API SHALL return a clear not-found response WITHIN
  p95 < 50 ms on the resolution path.
  @prd: PRD.01.09.e525 | @threshold: PRD.01.perf.redirectp95 | @bdd: BDD-01
- **EARS.01.03.50d1 — Reputation source fail-closed**
  IF the reputation source is unreachable or exceeds its screening deadline, THE
  Shorten/Redirect API SHALL reject create fail-closed with the retryable
  §10 "Shortening unavailable" message while continuing to redirect issued codes,
  WITHIN the create-path screening deadline.
  @prd: PRD.01.09.b6cb | @threshold: PRD.01.perf.screeningdeadline | @bdd: BDD-01
- **EARS.01.03.5442 — Code-space exhaustion**
  IF the short-code space reaches capacity, THE Shorten/Redirect API SHALL reject
  new creation with the non-retryable §10 "at capacity" message while continuing
  to resolve existing codes, WITHIN the create response. (Capacity-guard origin:
  PRD.01.13.385e; detection counterpart: EARS.01.03.eca5.)
  @prd: PRD.01.09.b6cb | @threshold: PRD.01.quota.codespacecapacity | @bdd: BDD-01
- **EARS.01.03.f62a — Flagged-code takedown**
  IF an issued code's destination is later flagged or taken down, THE
  Shorten/Redirect API SHALL return a not-found response for that code WITHIN the
  takedown SLA owned by the abuse-protection ADR topic (BRD.01.08.daeb).
  @prd: PRD.01.09.b6cb | @bdd: BDD-01
- **EARS.01.03.fa0b — Automated-repeat visit inflation**
  IF visits to an issued code exhibit automated-repeat patterns that would
  inflate adoption metrics, THE Visit Counter SHALL apply the adoption-integrity
  treatment owned by the adoption-metric-integrity ADR topic (BRD.01.08.c478),
  bounding or distinguishing the inflated counts, WITHIN the visit-count
  reconciliation window.
  @prd: PRD.01.09.d101 | @threshold: PRD.01.reliability.countstaleness | @bdd: BDD-01
- **EARS.01.03.9425 — Counting outage never blocks redirect**
  IF the counting path is stalled or failing, THE Shorten/Redirect API SHALL
  still resolve redirects for issued codes WITHIN p95 < 50 ms on the redirect
  path.
  @prd: PRD.01.09.d101 | @threshold: PRD.01.perf.redirectp95 | @bdd: BDD-01

> **Precedence note (simultaneous create-reject conditions).** When the
> reputation source is unreachable AND the code space is at capacity at the same
> time, EARS.01.03.50d1 (retryable "Shortening unavailable") takes precedence for
> the reputation-outage case and EARS.01.03.5442 remains the sole owner of the
> non-retryable "at capacity" message; message and retry semantics are therefore
> deterministic.

### Ubiquitous / System-Wide (THE … SHALL … for [scope])

- **EARS.01.03.bca8 — Code-to-URL uniqueness**
  THE Shorten/Redirect API SHALL ensure every issued short code maps to exactly
  one original URL for the code's lifetime, for all created links.
  @prd: PRD.01.09.b6cb | @bdd: BDD-01
- **EARS.01.03.ac68 — Non-walkable code keyspace**
  THE Shorten/Redirect API SHALL issue high-entropy, non-sequential short codes,
  for the public anonymous resolution surface.
  @prd: PRD.01.09.dd8d | @bdd: BDD-01
- **EARS.01.03.9903 — Per-source resolution rate-limiting**
  THE Shorten/Redirect API SHALL rate-limit resolution requests per source, for
  the public anonymous resolution surface.
  @prd: PRD.01.09.dd8d | @bdd: BDD-01
- **EARS.01.03.4ebf — Confidential mapping-store access control**
  THE Mapping Store SHALL restrict read access to the potentially-confidential,
  may-contain-PII original-URL value to least-privilege principals per the
  original-URL data classification, for all stored code-to-URL mappings, with
  concrete access and erasure parameters owned by the data-protection ADR topic
  (BRD.01.08.daeb).
  @prd: PRD.01.09.b6cb | @bdd: BDD-01
- **EARS.01.03.aa59 — Owner-visible counts**
  THE Visit Counter SHALL expose created-link and per-link visit counts to the
  Service Owner, for all issued codes. Audit-logging of Service Owner
  count-access authz decisions is an explicit deferral owned by the
  ops/observability ADR topic (BRD.01.08.c478).
  @prd: PRD.01.09.d101 | @bdd: BDD-01

## 4. Quality Attributes

### Performance

| ID | Statement | Metric | Target | Measurement |
|----|-----------|--------|--------|-------------|
| EARS.01.04.cea3 | THE Shorten/Redirect API SHALL complete redirect resolution | Latency | p95 < 50 ms | Load test on the redirect path, production-equivalent, excluding cold-start; @threshold: PRD.01.perf.redirectp95 |

### Security

| ID | Statement | Control | Compliance |
|----|-----------|---------|------------|
| EARS.01.04.6f59 | THE Shorten/Redirect API SHALL screen every create against the reputation source and fail closed when it is unreachable or past its screening deadline | Destination-abuse screening | Fail-closed create |
| EARS.01.04.cb3b | THE Shorten/Redirect API SHALL protect the resolution surface with high-entropy non-sequential codes and per-source rate-limiting | Enumeration / scraping defense | Two independent layers (PRD-01 §7) |

### Reliability

| ID | Statement | Metric | Target |
|----|-----------|--------|--------|
| EARS.01.04.1598 | THE Shorten/Redirect API SHALL maintain redirect availability | Uptime | ≥ 99.9% monthly — @threshold: PRD.01.reliability.availabilitymonthly |
| EARS.01.04.5e5b | THE Mapping Store SHALL preserve confirmed-issued links | Durability | RPO = 0; RTO ≤ 30 min — the store-loss detection that starts the RTO clock is deferred to the availability ADR topic (BRD.01.08.5b91) |
| EARS.01.04.1898 | THE Visit Counter SHALL preserve confirmed visit increments | Count durability | No loss; bounded reconciliation lag — @threshold: PRD.01.reliability.countstaleness |

## 5. Traceability

@ears: EARS-01

Each EARS requirement carries its `@prd` upstream tag and a per-line downstream
`@bdd` slot inline in §3 (BDD-01 not yet authored; the slot resolves to the
citing scenario once BDD cites the EARS ID by `@ears`). The matrix below rolls
up both directions by source.

| @prd source | EARS requirements | Downstream |
|-------------|-------------------|------------|
| PRD.01.09.b6cb | EARS.01.03.5066, .eca5, .6811, .4400, .50d1, .5442, .f62a, .bca8, .4ebf | BDD-01 (per-line @bdd, pending) |
| PRD.01.09.dd8d | EARS.01.03.c4c9, .feaa, .ac68, .9903 | BDD-01 (per-line @bdd, pending) |
| PRD.01.09.e525 | EARS.01.03.e4db | BDD-01 (per-line @bdd, pending) |
| PRD.01.09.d101 | EARS.01.03.4425, .f766, .fa0b, .9425, .aa59 | BDD-01 (per-line @bdd, pending) |
| PRD.01.09.9e0f | EARS.01.03.97be | BDD-01 (per-line @bdd, pending) |

PRD §13 abuse-case / risk rows anchored at EARS altitude:

| PRD risk | EARS line(s) |
|----------|--------------|
| PRD.01.13.011a — harmful destinations | .6811, .4400, .50d1 (at-create) · .f62a (post-issue takedown) |
| PRD.01.13.385e — code-space depletion | .eca5 (detect) · .5442 (recover) |
| PRD.01.13.e661 — automated repeat-visit inflation | .fa0b |
| PRD.01.13.d50d — anonymously-submitted PII | .4ebf |

Thresholds (values owned upstream; deferred values owned by the PRD-01 §14 ADR topics):

- @threshold: PRD.01.perf.redirectp95
- @threshold: PRD.01.reliability.availabilitymonthly
- @threshold: PRD.01.rate.redirectsustained
- @threshold: PRD.01.quota.urlmaxlen
- @threshold: PRD.01.perf.screeningdeadline
- @threshold: PRD.01.reliability.countstaleness
- @threshold: PRD.01.quota.codespacecapacity

Health: BDD readiness 93% · PRD §9 coverage 5/5 · PRD §13 risk coverage 4/4 · target ≥ 90 / 100.

## Glossary

| Term | Definition |
|------|------------|
| EARS | Easy Approach to Requirements Syntax (Layer 3 formal requirements). |
| BDD readiness | Score measuring EARS maturity for BDD transition (≥ 90 / 100). |
| Short code | A compact, high-entropy identifier that resolves to one original URL. |
| Resolution path | The redirect lookup from short code to original URL. |
| Screening deadline | The latency bound after which a slow reputation source trips fail-closed (deferred to the abuse-protection ADR topic). |
| Reconciliation window | The bounded lag within which a confirmed visit increment becomes owner-visible (deferred to the visit-observability ADR topic). |
