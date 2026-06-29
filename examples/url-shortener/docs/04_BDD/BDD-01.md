---
title: "BDD: URL Shortener"
doc_id: "BDD-01"
artifact_type: BDD
layer: 4
status: Draft
version: "1.0.2"
author: flow-walkthrough
created: "2026-06-10"
last_updated: "2026-06-10"
custom_fields:
  document_type: bdd-document
  artifact_type: BDD
  layer: 4
  deliverable_type: code
  upstream_artifacts: [EARS-01]
  downstream_artifacts: [ADR-01]
  adr_ready_score: 94
---

# BDD-01: URL Shortener

## 1. Document Control

| Field | Value |
|-------|-------|
| Document ID | BDD-01 |
| Status | Draft |
| Version | 1.0.2 |
| Priority | P1 |
| ADR readiness score | 94/100 |
| Created | 2026-06-10 |
| Last updated | 2026-06-10 |
| Author | flow-walkthrough |
| Execution environment | QA STAGING ONLY — never CI |

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0.0 | 2026-06-10 | flow-walkthrough | Initial BDD scenarios from EARS-01 v1.0.0 (saga iteration 1). |
| 1.0.1 | 2026-06-10 | doc-bdd-fixer | Remediated audit findings (saga iter 1); see BDD-01.F report. |
| 1.0.2 | 2026-06-10 | doc-bdd-fixer | Remediated iter-2 audit findings (saga iter 2); see BDD-01.F_fix_report_v002. |

`deliverable_type: code` inherited from EARS-01. BDD (Layer 4) carries the single
necessary-upstream tag `@ears`; PRD/BRD lineage is transitive via EARS-01. The ADR
readiness score is provisional — the binding gate is the `doc-bdd-audit` pass.

## 2. Feature Definition

The necessary-upstream tag (`@ears`, Gherkin-native, no space after the colon)
plus the `@bdd` self-tag apply to the feature and appear before the `Feature:`
keyword. Each scenario carries the specific `@ears` element lines it exercises.

```yaml
feature:
  name: URL Shortener acceptance behaviour
  tags:
  - '@qa-staging-only'
  background:
    steps:
    - the Shorten/Redirect API is in a ready state
    - the Mapping Store is empty and reachable
    - the destination-reputation source returns "clean" by default
    - the current time is "09:30:00" in "America/New_York"
  description: 'As a Link Submitter, Link Visitor, and Service Owner

    I want to shorten public URLs, resolve them quickly, and observe adoption

    So that long links become compact, dependable, and abuse-resistant short links'
```

Timing budgets reference threshold keys forwarded from EARS-01; each scenario
step carries the well-formed threshold tag inline. The redirect-path budget
resolves upstream, while the create-screening deadline, the visit-count
reconciliation window, and the code-space capacity bound are named keys whose
numeric values are deferred to the PRD-01 §14 ADR topics (EARS-01 §5). The
referenced keys are enumerated in §4.

## 3. Scenario Structure

### 3.1 Success scenarios

```yaml
scenarios:
- id: BDD.01.03.ccd6
  name: Shorten a valid public URL
  type: success
  priority: p0-critical
  ears:
  - EARS.01.03.5066
  - EARS.01.03.bca8
  - EARS.01.03.6811
  given:
  - a Link Submitter with the well-formed public URL "https://example.com/page" within @threshold:PRD.01.quota.urlmaxlen
  when:
  - the submitter posts the URL to the Shorten/Redirect API
  then:
  - the API SHALL return a unique short code that resolves to exactly "https://example.com/page" WITHIN
    @threshold:PRD.01.perf.screeningdeadline
  - the API SHALL present the confirmation "Your short link is ready."
  spec_trace:
  - SPEC §3 (Interfaces), SPEC §5 (Behavior)
- id: BDD.01.03.613b
  name: Redirect a known short code
  type: success
  priority: p0-critical
  ears:
  - EARS.01.03.c4c9
  - EARS.01.04.cea3
  given:
  - an issued short code "/abc123" mapping to "https://example.com/page"
  when:
  - a Link Visitor requests "/abc123"
  then:
  - the Shorten/Redirect API SHALL redirect to "https://example.com/page" WITHIN @threshold:PRD.01.perf.redirectp95
  spec_trace:
  - SPEC §3 (Interfaces), SPEC §5 (Behavior)
- id: BDD.01.03.5645
  name: Visit count increments exactly once on redirect
  type: success
  priority: p1-high
  ears:
  - EARS.01.03.4425
  - EARS.01.04.1898
  given:
  - an issued short code "/abc123" with a visit count of 0
  when:
  - a Link Visitor completes one redirect of "/abc123"
  then:
  - the Visit Counter SHALL increment that code's visit count to exactly 1, dispatched off the synchronous
    redirect path, WITHIN @threshold:PRD.01.reliability.countstaleness
  notes:
  - split from the former combined counting+idempotency scenario (QA-BDD-01-F002); idempotency under re-delivery
    is asserted separately in BDD.01.03.1365
  spec_trace:
  - SPEC §5 (Behavior — async increment), SPEC §4 (Data Models)
- id: BDD.01.03.1365
  name: Duplicate redirect event does not double-count
  type: success
  priority: p1-high
  ears:
  - EARS.01.03.4425
  - EARS.01.04.1898
  given:
  - an issued short code "/abc123" with a visit count of 1 after one confirmed redirect event
  when:
  - the same redirect event is re-delivered to the Visit Counter
  then:
  - the visit count for "/abc123" SHALL remain exactly 1, WITHIN @threshold:PRD.01.reliability.countstaleness
  notes:
  - idempotency half of the split counting scenario (QA-BDD-01-F002); proves off-path exactly-once delivery
    under event re-delivery
  spec_trace:
  - SPEC §5 (Behavior — async increment idempotency), SPEC §4 (Data Models)
- id: BDD.01.03.cb64
  name: Service Owner sees created-link and per-link counts
  type: success
  priority: p1-high
  ears:
  - EARS.01.03.aa59
  given:
  - a caller bearing the Service-Owner role
  - one issued short code "/abc123" with a visit count of 7
  when:
  - the caller requests adoption counts
  then:
  - the Visit Counter SHALL return the created-link count and the per-link visit count 7 for "/abc123"
  spec_trace:
  - SPEC §3 (Interfaces), SPEC §5 (Behavior — authorization)
- id: BDD.01.03.a688
  name: Issued code maps to exactly one URL for its lifetime
  type: success
  priority: p1-high
  ears:
  - EARS.01.03.bca8
  given:
  - an issued short code "/abc123" mapping to "https://example.com/page"
  when:
  - the same destination "https://example.com/page" is submitted again
  then:
  - the API SHALL return a code that resolves to exactly "https://example.com/page"
  - the returned code SHALL resolve to exactly one original URL, namely "https://example.com/page"
  notes:
  - the system-wide code-to-URL uniqueness invariant (EARS.01.03.bca8) is verified as a property/contract
    test at the TDD layer, not as an observable of this single resubmission
  spec_trace:
  - SPEC §4 (Data Models — invariant), SPEC §5 (Behavior)
- id: BDD.01.03.ed49
  name: Redirect latency and availability hold under sustained load
  type: success
  priority: p1-high
  ears:
  - EARS.01.03.feaa
  - EARS.01.04.1598
  - EARS.01.04.cea3
  given:
  - a single issued short code "/abc123" served at @threshold:PRD.01.rate.redirectsustained with 20 concurrent
    visitors
  when:
  - the load is sustained for 5 minutes over at least 30,000 sampled requests
  then:
  - the Shorten/Redirect API SHALL sustain redirect latency WITHIN @threshold:PRD.01.perf.redirectp95
  - the API SHALL sustain a within-window success rate of at least 99.9% over the sampled requests, with
    no non-shed 5xx responses
  - the redirect-path latency histogram metric SHALL be emitted with its route and status labels for every
    sampled request
  notes:
  - the monthly availability SLO @threshold:PRD.01.reliability.availabilitymonthly is a long-horizon target
    asserted separately; the within-window success rate above is its observable proxy
  - measurement window (5 minutes) and minimum sample count are author assumptions pending a PRD §12 load-envelope
    element
  spec_trace:
  - SPEC §5 (Behavior — performance), SPEC §6 (NFR)
- id: BDD.01.03.f774
  name: Capacity-utilization alert fires at the alert threshold
  type: success
  priority: p1-high
  ears:
  - EARS.01.03.eca5
  given:
  - short-code utilization is just below the capacity alert threshold
  when:
  - utilization reaches @threshold:PRD.01.quota.codespacecapacity alert level
  then:
  - the Shorten/Redirect API SHALL emit exactly one capacity-utilization alert identifying the current
    utilization
  notes:
  - detection counterpart to the reject-at-capacity recovery (BDD.01.03.177e)
  spec_trace:
  - SPEC §5 (Behavior — capacity), SPEC §6 (NFR — observability)
- id: BDD.01.03.9b90
  name: Mapping survives a crash immediately after acknowledgement
  type: success
  priority: p1-high
  ears:
  - EARS.01.04.5e5b
  given:
  - a Link Submitter posts a well-formed public URL
  when:
  - the Shorten/Redirect API acknowledges the issued short code
  - the Mapping Store is hard-killed before any post-acknowledgement flush
  then:
  - after the Mapping Store restarts the issued short code SHALL still resolve to the original URL, confirming
    the mapping was durably committed at recovery-point-objective zero before acknowledgement
  notes:
  - 'crash-recovery probe gives "durably committed at ack" a deterministic observation point (TL-BDD-01):
    RPO-zero is verified by survival of the hard-kill, not by an unobservable point-in-time assertion
    at acknowledgement'
  spec_trace:
  - SPEC §4 (Data Models — durability), SPEC §5 (Behavior — write ordering)
- id: BDD.01.03.e5ec
  name: Issued codes are high-entropy and non-sequential
  type: success
  priority: p1-high
  ears:
  - EARS.01.03.ac68
  - EARS.01.04.cb3b
  given:
  - the Shorten/Redirect API issues short codes on the public resolution surface
  when:
  - 1,000 codes are issued in sequence
  then:
  - no issued code SHALL be derivable by incrementing or decrementing another issued code
  - the 1,000 issued codes SHALL be pairwise distinct and SHALL pass a monobit frequency test over their
    concatenated bit-string at the significance level @threshold:PRD.01.security.codeentropy
  spec_trace:
  - SPEC §4 (Data Models — code generation), SPEC §6 (NFR — security)
- id: BDD.01.03.567d
  name: Resolution requests are rate-limited per source
  type: success
  priority: p1-high
  ears:
  - EARS.01.03.9903
  - EARS.01.04.cb3b
  given:
  - the per-source resolution rate limit is @threshold:PRD.01.rate.resolutionpersource requests per @threshold:PRD.01.rate.resolutionwindow
  when:
  - one source issues one more than @threshold:PRD.01.rate.resolutionpersource resolution requests within
    a single @threshold:PRD.01.rate.resolutionwindow
  then:
  - the Shorten/Redirect API SHALL throttle the request beyond the limit for that source
  - resolution for other sources SHALL be unaffected
  spec_trace:
  - SPEC §3 (Interfaces — rate limiting), SPEC §6 (NFR — security)
- id: BDD.01.03.c8a6
  name: Mapping-store denies original-URL read to a principal without least-privilege grant
  type: success
  priority: p1-high
  ears:
  - EARS.01.03.4ebf
  given:
  - a stored code-to-URL mapping whose original-URL value is classified as may-contain-PII
  when:
  - a principal without the least-privilege read grant reads the mapping
  then:
  - the Mapping Store SHALL deny access to the original-URL value
  notes:
  - concrete access and erasure parameters are owned by the data-protection ADR topic
  spec_trace:
  - SPEC §4 (Data Models — classification), SPEC §6 (NFR — access control)
- id: BDD.01.03.167e
  name: Mapping-store permits original-URL read to a principal with least-privilege grant
  type: success
  priority: p1-high
  ears:
  - EARS.01.03.4ebf
  given:
  - a stored code-to-URL mapping whose original-URL value is classified as may-contain-PII
  when:
  - a principal holding the least-privilege read grant reads the mapping
  then:
  - the Mapping Store SHALL permit access to the original-URL value
  notes:
  - granted-path companion to the denied-path control (BDD.01.03.c8a6); access parameters owned by the
    data-protection ADR topic
  spec_trace:
  - SPEC §4 (Data Models — classification), SPEC §6 (NFR — access control)
- id: BDD.01.03.5ab2
  name: Unknown short code returns not found
  type: error
  priority: p1-high
  ears:
  - EARS.01.03.e4db
  given:
  - no short code is issued for "/zzz999"
  when:
  - a Link Visitor requests "/zzz999"
  then:
  - the Shorten/Redirect API SHALL return "No such short link exists." WITHIN @threshold:PRD.01.perf.redirectp95
  - the API SHALL NOT redirect the visitor
  spec_trace:
  - SPEC §5 (Behavior — error_handling), SPEC §3 (Interfaces)
- id: BDD.01.03.177e
  name: Code-space exhaustion returns a non-retryable capacity error
  type: error
  priority: p1-high
  ears:
  - EARS.01.03.5442
  given:
  - the short-code space is at @threshold:PRD.01.quota.codespacecapacity
  when:
  - a Link Submitter posts a well-formed public URL
  then:
  - the Shorten/Redirect API SHALL reject creation with "Short links are at capacity and can't be created
    right now. Existing links still work."
  - the API SHALL continue to resolve existing issued codes
  - the API SHALL issue no short code
  spec_trace:
  - SPEC §5 (Behavior — capacity), SPEC §6 (Error Handling)
- id: BDD.01.03.3c70
  name: Flagged or taken-down code returns not found
  type: error
  priority: p1-high
  ears:
  - EARS.01.03.f62a
  given:
  - an issued short code "/abc123" whose destination is later flagged and taken down
  when:
  - a Link Visitor requests "/abc123"
  then:
  - the Shorten/Redirect API SHALL return "No such short link exists." WITHIN @threshold:PRD.01.perf.takedownsla
  - the API SHALL NOT redirect the visitor
  - the API SHALL emit a "link_takedown_applied" event identifying the taken-down code
  notes:
  - the "link_takedown_applied" event assertion (observability plane) is intentionally co-located with
    the user-facing not-found outcome here; failure isolation between the behavioural and instrumentation
    planes is accepted as a documented dual-plane verification trade-off for this single takedown scenario
    (QA-BDD-01-F003)
  spec_trace:
  - SPEC §5 (Behavior — state_transitions), SPEC §6 (Error Handling)
- id: BDD.01.03.6921
  name: Adoption counts are withheld from a caller without the Service-Owner role
  type: error
  priority: p1-high
  ears:
  - EARS.01.03.aa59
  given:
  - a caller NOT bearing the Service-Owner role
  - one issued short code "/abc123" with a visit count of 7
  when:
  - the caller requests adoption counts
  then:
  - the Visit Counter SHALL deny access with the not-authorised status
  - the response body SHALL NOT disclose any created-link count or per-link visit count
  notes:
  - denied-path companion to the granted-path count scenario (BDD.01.03.cb64)
  spec_trace:
  - SPEC §3 (Interfaces), SPEC §5 (Behavior — authorization)
- id: BDD.01.03.f0a5
  name: Flagged destination is withheld a short code
  type: error
  priority: p1-high
  ears:
  - EARS.01.03.4400
  - EARS.01.04.6f59
  given:
  - destination-reputation screening is enabled
  - a Link Submitter with a destination the reputation source flags "harmful"
  when:
  - the submitter posts the URL to the Shorten/Redirect API
  then:
  - the API SHALL NOT issue a short code for the flagged destination
  - the API SHALL reject the submission with "That address can't be shortened — only public http/https
    web addresses are accepted."
  spec_trace:
  - SPEC §5 (Behavior — abuse_control), SPEC §6 (Error Handling)
- id: BDD.01.03.c65d
  name: Automated-repeat visits are distinguished from the owner-visible adoption count
  type: error
  priority: p2-medium
  ears:
  - EARS.01.03.fa0b
  given:
  - an issued short code "/abc123" receiving 10 visits within 1 second, of which 6 share a single automated
    source-signature and 4 are distinct human-attributed visits
  when:
  - the repeated visits are processed
  then:
  - the Visit Counter SHALL exclude the 6 automated-repeat visits from the owner-visible adoption count
    for "/abc123", retaining each excluded visit tagged "automated=true", WITHIN @threshold:PRD.01.reliability.countstaleness
  - the owner-visible adoption count for "/abc123" SHALL equal exactly 4, the number of human-attributed
    visits only
  notes:
  - the distinguish-not-bound branch is chosen so the observable is determinate; the input partition (10
    visits → 6 automated / 4 human) pins the test oracle in-scenario (TL-BDD-02), leaving only the production
    detection heuristic to the adoption-metric-integrity ADR topic
  spec_trace:
  - SPEC §5 (Behavior — adoption_integrity), SPEC §6 (Error Handling)
- id: BDD.01.03.41c7
  name: Fail closed when the reputation source is degraded
  type: recovery
  priority: p1-high
  ears:
  - EARS.01.03.50d1
  - EARS.01.04.6f59
  outline: true
  given:
  - destination-reputation screening is enabled
  - the reputation source is "<degradation>"
  when:
  - a Link Submitter posts a well-formed public URL
  then:
  - the Shorten/Redirect API SHALL reject create fail-closed with "Short links can't be created right
    now. Existing links still work." WITHIN @threshold:PRD.01.perf.screeningdeadline
  - the API SHALL continue to redirect issued codes
  - the API SHALL issue no short code
  - the API SHALL emit a "screening_fail_closed" counter increment for the rejected create
  examples:
    headers:
    - degradation
    rows:
    - - unreachable
    - - dns resolution failure
    - - tls handshake failure
    - - slow beyond the screening deadline
  notes:
  - dns-resolution and tls-handshake fixtures exercise partition variants on a different code path than
    an unreachable host (chaos partition breadth)
  spec_trace:
  - SPEC §5 (Behavior — fail_closed), SPEC §6 (Error Handling — recovery)
- id: BDD.01.03.3757
  name: Reputation source recovers and a resubmission is issued a code
  type: recovery
  priority: p1-high
  ears:
  - EARS.01.03.50d1
  given:
  - the reputation source was degraded and is now restored to "reachable"
  when:
  - a Link Submitter resubmits a well-formed public URL
  then:
  - the Shorten/Redirect API SHALL screen the destination and issue a short code WITHIN @threshold:PRD.01.perf.screeningdeadline
  spec_trace:
  - SPEC §5 (Behavior — recovery), SPEC §6 (Error Handling — recovery)
- id: BDD.01.03.3322
  name: Counting outage never blocks redirect
  type: recovery
  priority: p1-high
  ears:
  - EARS.01.03.9425
  given:
  - the visit-counting path is stalled or failing
  when:
  - a Link Visitor requests an otherwise-known short code "/abc123"
  then:
  - the Shorten/Redirect API SHALL still resolve the redirect to the original URL WITHIN @threshold:PRD.01.perf.redirectp95
  - the system SHALL emit a "counting_path_degraded" metric increment, or a structured WARN log entry
    carrying a degradation_type field, marking the degraded-mode entry
  notes:
  - the degraded-mode observable makes silent counting degradation detectable by operators (OP-I2-001)
  spec_trace:
  - SPEC §5 (Behavior — degraded_mode), SPEC §6 (Error Handling — recovery)
- id: BDD.01.03.02c1
  name: Concurrent visits are recorded without loss
  type: recovery
  priority: p1-high
  ears:
  - EARS.01.03.f766
  given:
  - an issued short code "/abc123" with a visit count of 0
  when:
  - 50 visits to "/abc123" are processed concurrently
  then:
  - the Visit Counter SHALL record every confirmed visit without loss, counting each distinct confirmed
    visit exactly once, WITHIN @threshold:PRD.01.reliability.countstaleness
  - the reconciled visit count SHALL equal 50
  spec_trace:
  - SPEC §5 (Behavior — concurrency), SPEC §4 (Data Models)
- id: BDD.01.03.1f90
  name: Mapping Store degradation during redirect returns a bounded error
  type: recovery
  priority: p1-high
  ears:
  - EARS.01.03.c4c9
  - EARS.01.04.5e5b
  - EARS.01.04.cea3
  outline: true
  given:
  - an issued short code "/abc123" mapping to "https://example.com/page"
  - the Mapping Store is "<degradation>"
  when:
  - a Link Visitor requests "/abc123"
  then:
  - the Shorten/Redirect API SHALL return the bounded degraded response "Redirect temporarily unavailable,
    please retry." WITHIN @threshold:PRD.01.perf.redirectp95
  - the API SHALL NOT hang beyond @threshold:PRD.01.perf.redirectp95 and SHALL NOT emit an unshed 5xx
  - the system SHALL emit a "mapping_store_degraded" counter increment labelled with the "<degradation>"
    degradation_type for the degraded redirect
  examples:
    headers:
    - degradation
    rows:
    - - unreachable
    - - dns resolution failure
    - - tls handshake failure
    - - slow beyond the redirect budget
  notes:
  - the store-partition (unreachable), dns-resolution, tls-handshake, and slow-read variants exercise
    distinct client-side timeout/retry code paths (CHAOS-BDD-01 partition breadth, matching BDD.01.03.41c7);
    the "temporarily unavailable" wording is an author assumption pending a PRD §10 degraded-redirect
    message; the "mapping_store_degraded" observable makes silent store failure detectable by operators
    (OP-I2-002); recovery is asserted in BDD.01.03.44fe
  spec_trace:
  - SPEC §5 (Behavior — degraded_mode), SPEC §6 (Error Handling — recovery)
- id: BDD.01.03.44fe
  name: Mapping Store recovers and redirects resume
  type: recovery
  priority: p1-high
  ears:
  - EARS.01.04.5e5b
  - EARS.01.03.c4c9
  given:
  - the Mapping Store was unreachable and is now restored to reachable
  - an issued short code "/abc123" mapping to "https://example.com/page" committed at recovery-point-objective
    zero
  when:
  - a Link Visitor requests "/abc123" after restoration
  then:
  - the Shorten/Redirect API SHALL redirect to "https://example.com/page" WITHIN @threshold:PRD.01.perf.redirectp95
  notes:
  - restoration counterpart to the degradation outline (BDD.01.03.1f90); RTO ≤ 30 min per EARS.01.04.5e5b
  spec_trace:
  - SPEC §5 (Behavior — recovery), SPEC §4 (Data Models — durability)
- id: BDD.01.03.076f
  name: A slow visit counter never delays the redirect
  type: recovery
  priority: p1-high
  ears:
  - EARS.01.03.4425
  - EARS.01.03.9425
  given:
  - an issued short code "/abc123" mapping to "https://example.com/page"
  - the visit-counting dispatch is lagging beyond @threshold:PRD.01.reliability.countstaleness
  when:
  - a Link Visitor requests "/abc123"
  then:
  - the Shorten/Redirect API SHALL resolve the redirect to "https://example.com/page" WITHIN @threshold:PRD.01.perf.redirectp95
  - the increment SHALL be deferred or buffered off the synchronous redirect path
  notes:
  - proves the off-path dispatch decouples redirect latency from counter latency (EARS.01.03.4425); slow-but-not-failed
    counterpart to the counting-outage scenario (BDD.01.03.3322)
  spec_trace:
  - SPEC §5 (Behavior — degraded_mode), SPEC §6 (NFR — performance isolation)
- id: BDD.01.03.976e
  name: Counting path recovers and reconciles missed visits
  type: recovery
  priority: p1-high
  ears:
  - EARS.01.03.f766
  - EARS.01.04.1898
  - EARS.01.03.4425
  given:
  - the visit-counting path was stalled while 12 confirmed visits to "/abc123" occurred
  - the counting path is now restored
  when:
  - the counting path resumes
  then:
  - the Visit Counter SHALL reconcile the 12 confirmed visits without loss to the exactly-once outcome
    WITHIN @threshold:PRD.01.reliability.countstaleness
  - the reconciled visit count for "/abc123" SHALL include every confirmed visit that occurred during
    the outage
  - the system SHALL emit a "counting_path_recovered" event, or a structured INFO log entry carrying a
    reconciled_count field, when the counting path resumes and reconciliation completes
  notes:
  - recovery pair for the counting-outage degraded-mode scenario (BDD.01.03.3322); the recovery observable
    confirms self-heal in real time, not only via eventual count correctness (OP-I2-003)
  spec_trace:
  - SPEC §5 (Behavior — recovery), SPEC §4 (Data Models — count durability)
- id: BDD.01.03.2a8c
  name: Code-space capacity is reclaimed and creation resumes
  type: recovery
  priority: p1-high
  ears:
  - EARS.01.03.5442
  - EARS.01.03.eca5
  given:
  - the short-code space was at @threshold:PRD.01.quota.codespacecapacity and capacity has since been
    reclaimed
  when:
  - a Link Submitter posts a well-formed public URL "https://example.com/page"
  then:
  - the Shorten/Redirect API SHALL resume issuing a unique short code that resolves to "https://example.com/page"
  notes:
  - recovery pair for the code-space-exhaustion rejection (BDD.01.03.177e); confirms no permanent capacity
    lockout
  spec_trace:
  - SPEC §5 (Behavior — capacity), SPEC §6 (Error Handling — recovery)
- id: BDD.01.03.e61c
  name: Concurrent reputation-unreachable and code-space-at-capacity yields the retryable message
  type: recovery
  priority: p1-high
  ears:
  - EARS.01.03.50d1
  - EARS.01.03.5442
  given:
  - destination-reputation screening is enabled
  - the reputation source is "unreachable"
  - the short-code space is at @threshold:PRD.01.quota.codespacecapacity
  when:
  - a Link Submitter posts a well-formed public URL
  then:
  - the Shorten/Redirect API SHALL reject creation with the retryable "Short links can't be created right
    now. Existing links still work." message, not the non-retryable at-capacity message
  - the API SHALL issue no short code
  notes:
  - 'exercises the EARS precedence note for simultaneous failure: the retryable fail-closed response (EARS.01.03.50d1)
    takes precedence over the non-retryable at-capacity response (EARS.01.03.5442) (CHAOS-BDD-02)'
  spec_trace:
  - SPEC §5 (Behavior — fail_closed precedence), SPEC §6 (Error Handling — recovery)
- id: BDD.01.03.588f
  name: Invalid destination is rejected across all invalid classes
  type: parameterized
  priority: p1-high
  ears:
  - EARS.01.03.97be
  outline: true
  given:
  - a Link Submitter with the destination "<destination>" of class "<class>"
  when:
  - the submitter posts the destination to the Shorten/Redirect API
  then:
  - the API SHALL reject it with "That address can't be shortened — only public http/https web addresses
    are accepted."
  - the API SHALL return neither a 5xx response nor an issued code
  examples:
    headers:
    - class
    - destination
    rows:
    - - empty
      - ''
    - - over max length
      - https://example.com/<2049-char-path>
    - - javascript scheme
      - javascript:alert(1)
    - - data scheme
      - data:text/html,<script>1</script>
    - - file scheme
      - file:///etc/passwd
    - - malformed/relative
      - /relative/path
  notes:
  - over-max-length destination exceeds @threshold:PRD.01.quota.urlmaxlen by one character
  spec_trace:
  - SPEC §5 (Behavior — input_validation), SPEC §6 (Error Handling)
- id: BDD.01.03.3708
  name: Destination screening is enforced when the feature gate is enabled
  type: optional
  priority: p2-medium
  ears:
  - EARS.01.03.6811
  given:
  - destination-reputation screening is enabled as a go-live precondition
  - a Link Submitter with a destination the reputation source rates "clean"
  when:
  - the destination passes URL validation
  then:
  - the Shorten/Redirect API SHALL screen the candidate destination at create time before issuing a short
    code
  - the reputation-source test double SHALL record exactly one screening call
  spec_trace:
  - SPEC §5 (Behavior — feature_gate), SPEC §3 (Interfaces)
```

## 4. Traceability

@bdd: BDD-01

The single necessary-upstream tag is `@ears`; PRD/BRD lineage is transitive via
EARS-01. Each §3 scenario carries the `@ears` elements it exercises, covering all
26 EARS-01 elements (20 functional in EARS §3, 6 NFR in EARS §4) at 100% across
31 scenarios. Downstream: ADR-01.

### 4.1 EARS → BDD coverage matrix

Every EARS-01 element and the scenario(s) that exercise it (forward direction):

| EARS ID | Scenario ID(s) |
|---------|----------------|
| EARS.01.03.4400 | BDD.01.03.f0a5 |
| EARS.01.03.4425 | BDD.01.03.5645, BDD.01.03.1365, BDD.01.03.076f, BDD.01.03.976e |
| EARS.01.03.4ebf | BDD.01.03.c8a6, BDD.01.03.167e |
| EARS.01.03.5066 | BDD.01.03.ccd6 |
| EARS.01.03.50d1 | BDD.01.03.41c7, BDD.01.03.3757, BDD.01.03.e61c |
| EARS.01.03.5442 | BDD.01.03.177e, BDD.01.03.2a8c, BDD.01.03.e61c |
| EARS.01.03.6811 | BDD.01.03.ccd6, BDD.01.03.3708 |
| EARS.01.03.9425 | BDD.01.03.3322, BDD.01.03.076f |
| EARS.01.03.97be | BDD.01.03.588f |
| EARS.01.03.9903 | BDD.01.03.567d |
| EARS.01.03.aa59 | BDD.01.03.cb64, BDD.01.03.6921 |
| EARS.01.03.ac68 | BDD.01.03.e5ec |
| EARS.01.03.bca8 | BDD.01.03.ccd6, BDD.01.03.a688 |
| EARS.01.03.c4c9 | BDD.01.03.613b, BDD.01.03.1f90, BDD.01.03.44fe |
| EARS.01.03.e4db | BDD.01.03.5ab2 |
| EARS.01.03.eca5 | BDD.01.03.f774, BDD.01.03.2a8c |
| EARS.01.03.f62a | BDD.01.03.3c70 |
| EARS.01.03.f766 | BDD.01.03.02c1, BDD.01.03.976e |
| EARS.01.03.fa0b | BDD.01.03.c65d |
| EARS.01.03.feaa | BDD.01.03.ed49 |
| EARS.01.04.1598 | BDD.01.03.ed49 |
| EARS.01.04.1898 | BDD.01.03.5645, BDD.01.03.1365, BDD.01.03.976e |
| EARS.01.04.5e5b | BDD.01.03.9b90, BDD.01.03.1f90, BDD.01.03.44fe |
| EARS.01.04.6f59 | BDD.01.03.f0a5, BDD.01.03.41c7 |
| EARS.01.04.cb3b | BDD.01.03.e5ec, BDD.01.03.567d |
| EARS.01.04.cea3 | BDD.01.03.613b, BDD.01.03.ed49, BDD.01.03.1f90 |

26 of 26 EARS-01 elements covered (no orphans).

### 4.2 BDD → EARS provenance matrix

Every scenario and the EARS element(s) it traces back to (reverse direction):

| Scenario ID | EARS ID(s) |
|-------------|------------|
| BDD.01.03.ccd6 | EARS.01.03.5066, EARS.01.03.bca8, EARS.01.03.6811 |
| BDD.01.03.613b | EARS.01.03.c4c9, EARS.01.04.cea3 |
| BDD.01.03.5645 | EARS.01.03.4425, EARS.01.04.1898 |
| BDD.01.03.1365 | EARS.01.03.4425, EARS.01.04.1898 |
| BDD.01.03.cb64 | EARS.01.03.aa59 |
| BDD.01.03.a688 | EARS.01.03.bca8 |
| BDD.01.03.ed49 | EARS.01.03.feaa, EARS.01.04.1598, EARS.01.04.cea3 |
| BDD.01.03.f774 | EARS.01.03.eca5 |
| BDD.01.03.9b90 | EARS.01.04.5e5b |
| BDD.01.03.e5ec | EARS.01.03.ac68, EARS.01.04.cb3b |
| BDD.01.03.567d | EARS.01.03.9903, EARS.01.04.cb3b |
| BDD.01.03.c8a6 | EARS.01.03.4ebf |
| BDD.01.03.167e | EARS.01.03.4ebf |
| BDD.01.03.5ab2 | EARS.01.03.e4db |
| BDD.01.03.177e | EARS.01.03.5442 |
| BDD.01.03.3c70 | EARS.01.03.f62a |
| BDD.01.03.6921 | EARS.01.03.aa59 |
| BDD.01.03.f0a5 | EARS.01.03.4400, EARS.01.04.6f59 |
| BDD.01.03.c65d | EARS.01.03.fa0b |
| BDD.01.03.41c7 | EARS.01.03.50d1, EARS.01.04.6f59 |
| BDD.01.03.3757 | EARS.01.03.50d1 |
| BDD.01.03.3322 | EARS.01.03.9425 |
| BDD.01.03.02c1 | EARS.01.03.f766 |
| BDD.01.03.1f90 | EARS.01.03.c4c9, EARS.01.04.5e5b, EARS.01.04.cea3 |
| BDD.01.03.44fe | EARS.01.04.5e5b, EARS.01.03.c4c9 |
| BDD.01.03.076f | EARS.01.03.4425, EARS.01.03.9425 |
| BDD.01.03.976e | EARS.01.03.f766, EARS.01.04.1898, EARS.01.03.4425 |
| BDD.01.03.2a8c | EARS.01.03.5442, EARS.01.03.eca5 |
| BDD.01.03.e61c | EARS.01.03.50d1, EARS.01.03.5442 |
| BDD.01.03.588f | EARS.01.03.97be |
| BDD.01.03.3708 | EARS.01.03.6811 |

All 31 scenarios resolve to a declared EARS-01 element (no orphan scenarios).

Thresholds referenced (deferred values owned by the PRD-01 §14 ADR topics):

- @threshold: PRD.01.perf.redirectp95
- @threshold: PRD.01.perf.screeningdeadline
- @threshold: PRD.01.reliability.countstaleness
- @threshold: PRD.01.reliability.availabilitymonthly
- @threshold: PRD.01.rate.redirectsustained
- @threshold: PRD.01.quota.urlmaxlen
- @threshold: PRD.01.quota.codespacecapacity
- @threshold: PRD.01.perf.takedownsla
- @threshold: PRD.01.security.codeentropy
- @threshold: PRD.01.rate.resolutionpersource
- @threshold: PRD.01.rate.resolutionwindow

Health: EARS coverage 26/26 · all five scenario categories present · target
≥ 90/100. The four threshold keys added in v1.0.1 (takedownsla, codeentropy,
resolutionpersource, resolutionwindow) are named deferrals whose numeric values
are owned by the PRD-01 §14 ADR topics, consistent with the existing budget keys.

## 5. Glossary

| Term | Definition |
|------|------------|
| BDD | Behavior-Driven Development (Layer 4 executable acceptance scenarios). |
| Gherkin | Structured Given-When-Then syntax for executable scenarios. |
| ADR readiness | Score measuring BDD maturity for ADR transition (≥ 90 / 100). |
| Scenario Outline | Parameterized Gherkin scenario with an Examples table. |
| spec_trace | Per-scenario list of the SPEC sections a scenario maps to (req-to-SPEC bridge). |
| Short code | A compact, high-entropy identifier that resolves to one original URL. |
| Fail-closed | On screening-source degradation, create is rejected rather than issued unscreened. |
| Reconciliation window | The bounded lag within which a confirmed visit increment becomes owner-visible. |
