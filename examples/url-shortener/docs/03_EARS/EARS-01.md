---
title: "EARS: URL Shortener"
doc_id: "EARS-01"
artifact_type: EARS
layer: 3
status: Draft
version: "1.0.0"
author: flow-walkthrough
reviewer: flow-walkthrough
approver: flow-walkthrough
created: "2026-06-08"
last_updated: "2026-06-08"
custom_fields:
  document_type: ears-document
  artifact_type: EARS
  layer: 3
  deliverable_type: code
  upstream_artifacts: [BRD-01, PRD-01]
  downstream_artifacts: [BDD-01]
  bdd_ready_score: 94
---

# EARS-01: URL Shortener

## 1. Document Control

| Field | Value |
|-------|-------|
| Document ID | EARS-01 |
| Status | Draft |
| Version | 1.0.0 |
| Priority | P1 |
| Source document | @prd: PRD.01.09.7f20 |
| BRD reference | @brd: BRD.01.07.6c3f |
| BDD readiness score | 94/100 |
| Created | 2026-06-08 |
| Last updated | 2026-06-08 |
| Author | flow-walkthrough |
| Reviewer | flow-walkthrough |
| Approver | flow-walkthrough |

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0.0 | 2026-06-08 | flow-walkthrough | Initial EARS draft from PRD-01 v1.2.0. |

`deliverable_type: code` inherited from PRD-01.

## 2. Purpose and Context

**Purpose.** Convert PRD-01 functional requirements into formal, atomic, testable
EARS statements ready for BDD translation.

**Scope.** The five PRD-01 P1 features (§5) plus their error/degraded paths, code
invariants, durability, reputation and SSRF screening, and fail-closed and
anti-automation controls. Out-of-scope: vanity domains, accounts, dashboards.

**Audience.** Architects, developers, and QA engineers translating these into BDD
(Layer 4).

## 3. Requirements

Each requirement is atomic and carries `@threshold` tags. Latency is server-side
per the PRD-01 §5 boundary; `p95` denotes the 95th percentile.

### 3.1 Event-Driven (WHEN-THE-SHALL-WITHIN)

#### EARS.01.03.f909 Shorten response

WHEN a Link Submitter submits a well-formed public http/https URL, THE Shortening
API SHALL return a unique short code resolving to that URL WITHIN 500 ms (p95).
(Idempotency: resubmission yields a new distinct code; no dedup.)

- @brd: BRD.01.07.6c3f | @prd: PRD.01.09.7f20 | @prd: PRD.01.09.0999

#### EARS.01.03.5aa9 Link confirmation

WHEN a short code is issued, THE Shortening API SHALL present the confirmation
"Your short link is ready." WITHIN 500 ms (p95).

- @brd: BRD.01.07.6c3f | @prd: PRD.01.09.7f20

#### EARS.01.03.db78 Reputation screening

WHEN a destination passes URL validation, THE Shortening API SHALL screen it against
the destination-reputation source before issuing a short code, WITHIN 500 ms (p95).
[ADR deferred: BRD.01.08.daeb]

- @brd: BRD.01.11.341c | @brd: BRD.01.12.de0a | @prd: PRD.01.13.0769 | @prd: PRD.01.12.19b6 | @prd: PRD.01.12.b4aa

#### EARS.01.03.00b9 Pool-utilization alert

WHEN short-code-pool utilization crosses the high-utilization threshold, THE
Shortening API SHALL emit a capacity-utilization alert to the Service Owner.
[ADR deferred: BRD.01.08.9665]

- @brd: BRD.01.12.8b9b | @prd: PRD.01.13.9a6d

#### EARS.01.03.e2e9 Redirect response

WHEN a Link Visitor requests a known short code, THE Redirect Handler SHALL redirect
to the original URL WITHIN 50 ms (p95).

- @brd: BRD.01.07.15e1 | @prd: PRD.01.09.ce85 | @prd: PRD.01.09.1ec5 | @threshold: PRD.01.perf.redirectp95

#### EARS.01.03.8f70 Visit-count increment

WHEN a redirect completes, THE Redirect Handler SHALL increment that link's visit
count by one off the hot path WITHIN 1 s (p95). (Idempotency: at-most-once per
visit; no double-count.)

- @brd: BRD.01.07.882c | @prd: PRD.01.09.5ec6 | @prd: PRD.01.09.0716

#### EARS.01.03.539a Takedown — cease redirect

WHEN a Service Owner marks a short link for takedown, THE Redirect Handler SHALL
cease redirecting it WITHIN 1 s (p95) of the mark. This overrides EARS.01.03.187c
for taken-down links.

- @brd: BRD.01.11.341c | @prd: PRD.01.13.0769

#### EARS.01.03.539b Taken-down not-found

WHEN a Link Visitor requests a taken-down short code, THE Redirect Handler SHALL
return "No such short link exists." WITHIN 1 s (p95).

- @brd: BRD.01.11.341c | @prd: PRD.01.13.0769

#### EARS.01.03.a0ae Metrics access control

WHEN a caller requests adoption metrics, THE Metrics Reporter SHALL serve the request
only to a caller bearing the Service-Owner role, WITHIN 1 s (p95).

- @brd: BRD.01.07.882c | @prd: PRD.01.09.21ad

#### EARS.01.03.3306 Counts query

WHEN the Service Owner requests adoption metrics, THE Metrics Reporter SHALL return
the per-link visit count and the total short-link count WITHIN 1 s (p95).

- @brd: BRD.01.07.882c | @prd: PRD.01.09.21ad | @prd: PRD.01.09.e19e

#### EARS.01.03.ab5e Abusive submission volume

WHEN submission volume from one source exceeds the anti-abuse threshold, THE
Shortening API SHALL throttle it and emit a detection event WITHIN 100 ms.
[ADR deferred: BRD.01.08.daeb]

- @brd: BRD.01.11.341c | @prd: PRD.01.13.835e

#### EARS.01.03.c7e3 Enumeration probe

WHEN sequential or high-cardinality short-code probes from one source exceed the
anti-enumeration threshold, THE Redirect Handler SHALL apply the cooldown and emit a
detection event WITHIN 100 ms. [ADR deferred: BRD.01.08.daeb]

- @brd: BRD.01.11.341c | @prd: PRD.01.13.835e

#### EARS.01.03.a17e Metrics authZ audit log

WHEN the Metrics Reporter grants or denies an adoption-metrics request, THE Metrics
Reporter SHALL record caller identity, role-decision, and timestamp to an audit log
WITHIN 100 ms.

- @brd: BRD.01.07.882c | @prd: PRD.01.09.21ad

### 3.2 State-Driven (WHILE-THE-SHALL-WITHIN)

#### EARS.01.03.a132 Redirect latency under load

WHILE serving load up to 100 req/s and 20 concurrent visitors on one short link, THE
Redirect Handler SHALL sustain redirect latency under 50 ms (p95).

- @brd: BRD.01.07.15e1 | @prd: PRD.01.09.ce85 | @threshold: PRD.01.perf.redirectp95 | [author assumption — load-envelope pending a PRD §12 element]

### 3.3 Optional / Feature-Gated (WHERE-THE-SHALL)

#### EARS.01.03.ee86 Anti-automation rate limiting

WHERE anti-automation rate limiting is configured, THE Shortening API SHALL reject
submit and redirect requests exceeding the rate with an explicit throttling
response. [ADR deferred: BRD.01.08.daeb]

- @brd: BRD.01.11.341c | @prd: PRD.01.13.835e

### 3.4 Unwanted Behavior (IF-THE-SHALL-WITHIN)

#### EARS.01.03.eeaf Invalid URL rejection

IF a submission is malformed, empty, missing, or over the maximum URL length of
2,048 characters, THE Shortening API SHALL reject it with "That doesn't look like a
valid web address." and issue no short code, WITHIN 500 ms (p95).

- @brd: BRD.01.07.6c3f | @prd: PRD.01.09.de1c | @prd: PRD.01.12.2670

#### EARS.01.03.fa44 Non-public destination

IF a submitted destination names a non-public host (loopback, RFC1918, link-local,
or cloud-metadata), THE Shortening API SHALL reject it under the not-a-valid-address
contract and issue no short code, WITHIN 500 ms (p95).

- @brd: BRD.01.08.daeb | @prd: PRD.01.12.6f96

#### EARS.01.03.5821 Unknown code not-found

IF a Link Visitor requests a short code that was never issued or is mistyped, THE
Redirect Handler SHALL return "No such short link exists." WITHIN 50 ms (p95).

- @brd: BRD.01.07.52c7 | @prd: PRD.01.09.c9b0 | @prd: PRD.01.09.49e2 | @threshold: PRD.01.perf.redirectp95

#### EARS.01.03.e606 Unknown code no-redirect

IF a Link Visitor requests a short code that was never issued or is mistyped, THE
Redirect Handler SHALL NOT redirect, WITHIN 50 ms (p95).

- @brd: BRD.01.07.52c7 | @prd: PRD.01.09.c9b0 | @prd: PRD.01.09.49e2 | @threshold: PRD.01.perf.redirectp95

#### EARS.01.03.fab2 Store-unavailable response

IF the Link Store is unavailable, times out, or errors on the redirect path, THE
Redirect Handler SHALL return an explicit service-unavailable (5xx) response WITHIN
1 s rather than hanging or failing silently.

- @brd: BRD.01.07.15e1 | @prd: PRD.01.09.ce85

#### EARS.01.03.d808 Visit-count write isolation

IF a visit-count write fails or exceeds the EARS.01.03.8f70 visit-count budget
(1 s, p95), THE Redirect Handler SHALL complete an otherwise-resolvable redirect
without blocking or failing it.

- @brd: BRD.01.10.7d5a | @prd: PRD.01.12.11be | @prd: PRD.01.09.0716

#### EARS.01.03.0b67 Pool exhaustion

IF the short-code pool is exhausted at submission, THE Shortening API SHALL return
the capacity error "We can't issue a short link right now." WITHIN 500 ms (p95).
[ADR deferred: BRD.01.08.9665]

- @brd: BRD.01.12.8b9b | @prd: PRD.01.13.9a6d

#### EARS.01.03.135e Pool-exhaustion retry bound

IF the short-code pool is exhausted at submission, THE Shortening API SHALL attempt
at most the configured retry ceiling before returning the capacity error, WITHIN
500 ms (p95). [ADR deferred: BRD.01.08.9665]

- @brd: BRD.01.12.8b9b | @prd: PRD.01.13.9a6d

#### EARS.01.03.a2ae Reputation source unreachable

IF the destination-reputation source is unreachable or does not respond within the
screening budget at submit, THE Shortening API SHALL fail closed, issue no short
code, and return "We can't check this link right now — please try again shortly."
WITHIN 500 ms (p95). [ADR deferred: BRD.01.08.daeb]

- @brd: BRD.01.11.341c | @prd: PRD.01.12.19b6 | @prd: PRD.01.12.b4aa

#### EARS.01.03.9671 Harmful-destination rejection

IF the destination-reputation source flags a submitted destination as harmful, THE
Shortening API SHALL reject the submission, issue no short code, and return "We
can't shorten this link." WITHIN 500 ms (p95).

- @brd: BRD.01.11.341c | @brd: BRD.01.12.de0a | @prd: PRD.01.13.0769 | @prd: PRD.01.12.19b6 | @prd: PRD.01.12.b4aa

#### EARS.01.03.3312 Unauthorised metrics request

IF a caller not authorised as Service-Owner requests adoption metrics, THE Metrics
Reporter SHALL deny the request and return no counts, WITHIN 1 s (p95).

- @brd: BRD.01.07.882c | @prd: PRD.01.09.21ad

#### EARS.01.03.b5fa Mass-minting pattern

IF submissions from one source match the mass-minting signature, THE Shortening API
SHALL deny further submissions under the EARS.01.03.ab5e cooldown and emit no short
codes during it, WITHIN 100 ms. [ADR deferred: BRD.01.08.daeb]

- @brd: BRD.01.11.341c | @prd: PRD.01.13.835e

#### EARS.01.03.d8a2 Enumeration scraping

IF probes from one source match the scraping signature, THE Redirect Handler SHALL
block that source under the EARS.01.03.c7e3 cooldown and return only the standard
not-found response during it, WITHIN 50 ms. [ADR deferred: BRD.01.08.daeb]

- @brd: BRD.01.11.341c | @prd: PRD.01.13.835e

#### EARS.01.03.86ae Concurrent issuance collision

IF two concurrent submissions claim the same short code, THE Shortening API SHALL
atomically grant the code to exactly one and issue a distinct code to the other,
preserving uniqueness.

- @brd: BRD.01.10.e118 | @prd: PRD.01.13.7760

### 3.5 Ubiquitous (THE-SHALL)

#### EARS.01.03.97c4 Code uniqueness invariant

THE Shortening API SHALL ensure every issued short code is unique and maps to exactly
one original URL, for all issued codes.

- @brd: BRD.01.10.e118 | @prd: PRD.01.09.9467 | @prd: PRD.01.12.1a73

#### EARS.01.03.8df7 Write-before-acknowledge durability

THE Shortening API SHALL return a short code only after its short-code-to-URL mapping
is durably committed, for every issued code. (Idempotency: a retried ack issues no
second code.)

- @brd: BRD.01.10.3407 | @prd: PRD.01.13.ebf9

#### EARS.01.03.19ec Visit-count no-loss invariant

THE Redirect Handler SHALL record every durably-accepted visit increment without loss
under concurrent access, for all short links; a best-effort increment dropped under
EARS.01.03.d808 is not durably accepted and is logged for reconciliation.

- @brd: BRD.01.07.390f | @prd: PRD.01.09.0716

#### EARS.01.03.187c Link resolvability durability

THE Link Store SHALL keep every confirmed-issued short link resolvable for its
committed lifetime, except links taken down per EARS.01.03.539a, for all issued links.

- @brd: BRD.01.10.3407 | @prd: PRD.01.12.8500

## 4. Quality Attributes

Performance, security, and reliability targets. Code-issuance (p95 < 500 ms),
visit-count (p95 < 1 s), and TLS (c060) lack an upstream PRD element — author
assumptions pending ratification.

**Performance**

| ID | Statement | Metric | Target | Measurement |
|----|-----------|--------|--------|-------------|
| EARS.01.04.e27b | THE Redirect Handler SHALL resolve a known code and redirect | Latency | p95 < 50 ms — @threshold: PRD.01.perf.redirectp95 | Load test |
| EARS.01.04.4eec | THE Shortening API SHALL issue a short code | Latency | p95 < 500 ms | Load test |

- EARS.01.04.e27b: @brd: BRD.01.11.e2a0 | @prd: PRD.01.05.cc92 | @prd: PRD.01.06.dc62 | @threshold: PRD.01.perf.redirectp95
- EARS.01.04.4eec: @brd: BRD.01.07.6c3f | @prd: PRD.01.09.7f20

**Security**

| ID | Statement | Control | Compliance | Priority |
|----|-----------|---------|------------|----------|
| EARS.01.04.1453 | THE Shortening API SHALL reject non-public destination hosts | SSRF denylist (loopback/RFC1918/link-local/cloud-metadata) | Internal SSRF policy | P1 |
| EARS.01.04.ee3f | THE Shortening API SHALL screen submitted destinations and reject those flagged harmful | Reputation screen-and-reject; takedown of issued links | Abuse-control gate | P1 |
| EARS.01.04.f50e | THE Shortening API SHALL fail closed when destination screening is unavailable | Fail-closed abuse screening at submit | Abuse-control gate | P1 |
| EARS.01.04.b1aa | THE Shortening API SHALL apply anti-automation rate limiting | Rate limiting / anti-automation [ADR deferred: BRD.01.08.daeb] | Abuse-control gate | P1 |
| EARS.01.04.c060 | THE service SHALL serve all client connections over HTTPS/TLS | Transport encryption | TLS 1.2+ | P1 |

- EARS.01.04.1453: @brd: BRD.01.08.daeb | @prd: PRD.01.12.6f96
- EARS.01.04.ee3f: @brd: BRD.01.11.341c | @brd: BRD.01.12.de0a | @prd: PRD.01.13.0769
- EARS.01.04.f50e: @brd: BRD.01.11.341c | @prd: PRD.01.12.19b6
- EARS.01.04.b1aa: @brd: BRD.01.11.341c | @prd: PRD.01.13.835e
- EARS.01.04.c060: @brd: BRD.01.10.c2e1 | [author assumption — no PRD transport-encryption element]

**Reliability**

| ID | Statement | Metric | Target | Priority |
|----|-----------|--------|--------|----------|
| EARS.01.04.ca05 | THE service SHALL maintain redirect-path availability | Monthly uptime | 99.9% — @threshold: BRD.01.reliability.availabilitymonthly | P1 |
| EARS.01.04.8e22 | THE Shortening API SHALL issue collision-free codes | Duplicate codes | 0 | P1 |
| EARS.01.04.93f7 | THE Link Store SHALL preserve confirmed-issued mappings | Record loss (RPO) | RPO = 0 | P1 |
| EARS.01.04.7934 | THE Redirect Handler SHALL preserve confirmed visit increments | Lost increments | 0 under concurrency | P1 |

- EARS.01.04.ca05: @brd: BRD.01.04.f439 | @threshold: BRD.01.reliability.availabilitymonthly
- EARS.01.04.8e22: @brd: BRD.01.10.e118 | @prd: PRD.01.06.2102
- EARS.01.04.93f7: @brd: BRD.01.10.3407 | @prd: PRD.01.12.8500
- EARS.01.04.7934: @brd: BRD.01.10.7d5a | @prd: PRD.01.09.0716

## 5. Traceability

Document tag: @ears: EARS-01

**Upstream** (tags appear inline in §3–§4)

| PRD feature | PRD | BRD | Downstream BDD (expected) |
|-------------|-----|-----|---------------------------|
| Submit & Shorten | PRD.01.09.7f20 | BRD.01.07.6c3f | BDD-01 (pending L4) |
| Redirect | PRD.01.09.ce85 | BRD.01.07.15e1 | BDD-01 (pending L4) |
| Unknown code | PRD.01.09.c9b0 | BRD.01.07.52c7 | BDD-01 (pending L4) |
| Count Visits | PRD.01.09.5ec6 | BRD.01.07.882c | BDD-01 (pending L4) |
| Expose Counts | PRD.01.09.21ad | BRD.01.07.882c | BDD-01 (pending L4) |

**Downstream.** BDD (Layer 4) inherits the cumulative `@brd`/`@prd`/`@ears`
references; scenario IDs are assigned at BDD authoring. Coverage: all five P1
features, error paths, security controls, durability, and concurrency invariants
(PRD 100%).

## Glossary

| Term | Definition |
|------|------------|
| Short code | A compact identifier standing in for a long URL |
| Short link | A short-code reference that redirects to its original URL when visited |
| Original URL | The long public web address supplied by a Link Submitter |
| Redirect | Sending a Link Visitor from a short link to its original URL |
| Visit count | How many times a short link has been visited |
| Hot path | The synchronous redirect path the latency budget measures |
| SSRF | Server-Side Request Forgery — abuse of a fetch to reach non-public hosts |
| Fail closed | On a dependency outage, deny rather than proceed unscreened |
