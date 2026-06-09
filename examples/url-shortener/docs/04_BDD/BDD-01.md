---
title: "BDD: URL Shortener"
doc_id: "BDD-01"
artifact_type: BDD
layer: 4
status: Draft
version: "1.0.2"
author: flow-walkthrough
reviewer: flow-walkthrough
approver: flow-walkthrough
created: "2026-06-08"
last_updated: "2026-06-09"
custom_fields:
  document_type: bdd-document
  artifact_type: BDD
  layer: 4
  deliverable_type: code
  upstream_artifacts: [BRD-01, PRD-01, EARS-01]
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
| EARS reference | @ears: EARS-01 |
| PRD reference | @prd: PRD.01.09.7f20 |
| BRD reference | @brd: BRD.01.07.6c3f |
| ADR readiness score | 94/100 |
| Created | 2026-06-08 |
| Last updated | 2026-06-09 |
| Author | flow-walkthrough |
| Reviewer | flow-walkthrough |
| Approver | flow-walkthrough |
| Execution environment | QA STAGING ONLY — never CI |

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0.0 | 2026-06-08 | flow-walkthrough | Initial BDD scenarios from EARS-01 v1.0.0. |
| 1.0.1 | 2026-06-08 | doc-bdd-fixer | Remediation it.1; see BDD-01.F fix report v001. |
| 1.0.2 | 2026-06-09 | doc-bdd-fixer | Remediation it.2; split 8 compound C2 steps + bound 2 rate-limit scenarios; see BDD-01.F fix report v002. |

`deliverable_type: code` inherited from EARS-01. The ADR readiness score is
provisional; the binding gate is the `doc-bdd-audit` readiness pass.

## 2. Feature Definition

Cumulative Layer-4 tags (Gherkin-native, no spaces after the colon) apply to
every scenario in this feature and appear before the `Feature:` keyword.

```gherkin
@brd:BRD.01.07.6c3f @prd:PRD.01.09.7f20 @ears:EARS-01
@bdd:BDD-01 @qa-staging-only
Feature: URL Shortener acceptance behaviour
  As a Link Submitter, Link Visitor, and Service Owner
  I want to shorten public URLs, resolve them quickly, and observe adoption
  So that long links become compact, dependable, and abuse-resistant short links

  Background:
    Given the URL Shortener service is in a ready state
    And the Link Store is empty and reachable
    And the destination-reputation source returns "clean" by default
    And the current time is "09:30:00" in "America/New_York"
```

Each scenario below carries its own `@scenario-type`, priority, `@scenario-id`,
and the specific upstream `@ears`/`@prd`/`@brd` lines it exercises. Timing
budgets reference the redirect threshold @threshold:PRD.01.perf.redirectp95 and the
named EARS latency budgets (issuance and visit-count budgets have no PRD
threshold key — EARS-01 §4 records them as author assumptions pending PRD
ratification).

## 3. Scenario Structure

### 3.1 Success scenarios

```gherkin
@scenario-type:success @p0-critical @scenario-id:BDD.01.03.d541
@ears:EARS.01.03.f909 @ears:EARS.01.03.97c4 @ears:EARS.01.04.4eec @prd:PRD.01.09.7f20 @brd:BRD.01.07.6c3f
Scenario: Shorten a valid public URL
  Given a Link Submitter with the well-formed public URL "https://example.com/page"
  When the submitter posts the URL to the Shortening API
  Then the API SHALL return a short code that uniquely resolves to "https://example.com/page" WITHIN the EARS.01.04.4eec issue-latency budget (p95)
  # spec_trace: SPEC §3 (Interfaces), SPEC §5 (Behavior)

@scenario-type:success @p1-high @scenario-id:BDD.01.03.0b2a
@ears:EARS.01.03.5aa9 @prd:PRD.01.09.7f20 @brd:BRD.01.07.6c3f
Scenario: Confirmation message after issuance
  Given a Link Submitter has posted a well-formed public URL
  When the Shortening API issues the short code
  Then the API SHALL present the confirmation "Your short link is ready." WITHIN the EARS.01.04.4eec issue-latency budget (p95)
  # spec_trace: SPEC §3 (Interfaces), SPEC §5 (Behavior)

@scenario-type:success @p1-high @scenario-id:BDD.01.03.5887
@ears:EARS.01.03.db78 @prd:PRD.01.13.0769 @prd:PRD.01.12.19b6 @brd:BRD.01.11.341c
Scenario: Reputation screen passes for a clean destination
  Given a Link Submitter with a destination that the reputation source rates "clean"
  When the destination passes URL validation
  Then the Shortening API SHALL screen the destination against the reputation source before issuing a short code WITHIN the EARS.01.04.4eec issue-latency budget (p95)
  And the reputation-source test double SHALL record exactly one screening call
  And no short code SHALL be committed to the Link Store before a "clean" verdict is returned from the reputation source (call-order verification establishes the before-relation)
  # spec_trace: SPEC §3 (Interfaces), SPEC §5 (Behavior), SPEC §6 (Error Handling)

@scenario-type:success @p0-critical @scenario-id:BDD.01.03.6d94
@ears:EARS.01.03.e2e9 @ears:EARS.01.03.187c @prd:PRD.01.09.ce85 @brd:BRD.01.07.15e1
Scenario: Redirect a known short code
  Given an issued short link "/abc123" mapping to "https://example.com/page"
  When a Link Visitor requests "/abc123"
  Then the Redirect Handler SHALL redirect to "https://example.com/page" WITHIN @threshold:PRD.01.perf.redirectp95
  # spec_trace: SPEC §3 (Interfaces), SPEC §5 (Behavior)

@scenario-type:success @p1-high @scenario-id:BDD.01.03.1664
@ears:EARS.01.03.8f70 @ears:EARS.01.03.19ec @ears:EARS.01.04.7934 @prd:PRD.01.09.5ec6 @brd:BRD.01.07.882c
Scenario: Visit count increments off the hot path
  Given an issued short link "/abc123" with a visit count of 0
  When a Link Visitor completes one redirect of "/abc123"
  Then the Redirect Handler SHALL increment that link's visit count to exactly 1 off the hot path WITHIN the EARS.01.03.8f70 visit-count budget (p95)
  # spec_trace: SPEC §5 (Behavior — async increment), SPEC §4 (Data Models)

@scenario-type:success @p1-high @scenario-id:BDD.01.03.f9d6
@ears:EARS.01.03.3306 @ears:EARS.01.03.a0ae @prd:PRD.01.09.21ad @brd:BRD.01.07.882c
Scenario: Service Owner retrieves adoption metrics
  Given a caller bearing the Service-Owner role
  When the caller requests adoption metrics
  Then the Metrics Reporter SHALL return the per-link visit count and the total short-link count WITHIN the EARS.01.03.3306 metrics budget (p95)
  # spec_trace: SPEC §3 (Interfaces), SPEC §5 (Behavior — authorization)

@scenario-type:success @p1-high @scenario-id:BDD.01.03.cbf4
@ears:EARS.01.03.539a @prd:PRD.01.13.0769 @brd:BRD.01.11.341c
Scenario: Service Owner takes a link down
  Given an issued short link "/abc123" that currently redirects
  When a Service Owner marks "/abc123" for takedown
  Then the Redirect Handler SHALL cease redirecting "/abc123" WITHIN the EARS.01.03.539a takedown budget (p95) of the mark
  And the Redirect Handler SHALL write a takedown-applied log entry at AUDIT severity carrying the short code, the operator identity, and a timestamp
  # spec_trace: SPEC §5 (Behavior — state_transitions), SPEC §3 (Interfaces)

@scenario-type:success @p1-high @scenario-id:BDD.01.03.40d7
@ears:EARS.01.03.a17e @prd:PRD.01.09.21ad @brd:BRD.01.07.882c
Scenario: Metrics authorization decision is audit-logged
  Given a caller bearing the Service-Owner role
  When the caller requests adoption metrics
  Then the Metrics Reporter SHALL grant the request
  And the Metrics Reporter SHALL write one audit record carrying caller identity, role-decision "granted", and timestamp WITHIN the EARS.01.03.a17e audit budget
  # spec_trace: SPEC §5 (Behavior — audit), SPEC §6 (Error Handling — observability)

@scenario-type:success @p1-high @scenario-id:BDD.01.03.b9e7
@ears:EARS.01.03.a132 @ears:EARS.01.04.e27b @ears:EARS.01.04.ca05 @prd:PRD.01.09.ce85 @brd:BRD.01.07.15e1
Scenario: Redirect latency holds under sustained load
  Given a single short link "/abc123" served at 100 requests per second with 20 concurrent visitors
  When the load is sustained for 5 minutes over at least 30,000 sampled requests
  Then the Redirect Handler SHALL sustain redirect latency WITHIN @threshold:PRD.01.perf.redirectp95
  And the Redirect Handler SHALL sustain a within-window success rate of at least 99.9% over the sampled requests, with no non-shed 5xx responses
  # the monthly availability SLO (the BRD-01 monthly redirect-availability reliability threshold) is a long-horizon target asserted separately; it is not computable from this 5-minute window, so the within-window success rate above is its observable proxy
  # measurement window (5 minutes) and minimum sample count are author assumptions pending a PRD §12 load-envelope element
  # spec_trace: SPEC §5 (Behavior — performance), SPEC §6 (NFR)

@scenario-type:success @p1-high @scenario-id:BDD.01.03.2986
@ears:EARS.01.04.c060 @brd:BRD.01.10.c2e1
Scenario: All client connections are served over TLS
  Given a client opening a connection to the service over plain HTTP
  When the client issues a submit or redirect request
  Then the service SHALL serve the request only over HTTPS with TLS 1.2 or higher
  # spec_trace: SPEC §3 (Interfaces — transport), SPEC §6 (NFR — security)

@scenario-type:success @p1-high @scenario-id:BDD.01.03.8b97
@ears:EARS.01.03.8df7 @ears:EARS.01.04.93f7 @prd:PRD.01.13.ebf9 @brd:BRD.01.10.3407
Scenario: Mapping is durably committed before acknowledgement
  Given a Link Submitter posts a well-formed public URL
  When the Shortening API acknowledges the issued short code
  Then the short-code-to-URL mapping SHALL already be durably committed at recovery-point-objective zero
  # spec_trace: SPEC §4 (Data Models — durability), SPEC §5 (Behavior — write ordering)
```

### 3.2 Error scenarios

```gherkin
@scenario-type:error @p1-high @scenario-id:BDD.01.03.4356
@ears:EARS.01.03.5821 @ears:EARS.01.03.e606 @prd:PRD.01.09.c9b0 @brd:BRD.01.07.52c7
Scenario: Unknown short code returns not found
  Given no short link is issued for "/zzz999"
  When a Link Visitor requests "/zzz999"
  Then the Redirect Handler SHALL return "No such short link exists." WITHIN @threshold:PRD.01.perf.redirectp95
  And the Redirect Handler SHALL NOT redirect the visitor
  # spec_trace: SPEC §5 (Behavior — error_handling), SPEC §3 (Interfaces)

@scenario-type:error @p1-high @scenario-id:BDD.01.03.8604
@ears:EARS.01.03.539b @prd:PRD.01.13.0769 @brd:BRD.01.11.341c
Scenario: Taken-down short code returns not found
  Given an issued short link "/abc123" that a Service Owner has marked for takedown
  When a Link Visitor requests "/abc123"
  Then the Redirect Handler SHALL return "No such short link exists." WITHIN the EARS.01.03.539b takedown-response budget (p95)
  And the Redirect Handler SHALL emit a log entry at INFO severity carrying the short code and reason "taken_down", distinguishing it from an organic unknown-code lookup
  # spec_trace: SPEC §5 (Behavior — state_transitions), SPEC §6 (Error Handling)

@scenario-type:error @p1-high @scenario-id:BDD.01.03.bcf8
@ears:EARS.01.03.9671 @ears:EARS.01.04.ee3f @prd:PRD.01.13.0769 @brd:BRD.01.12.de0a
Scenario: Harmful destination is rejected
  Given a Link Submitter with a destination the reputation source flags "harmful"
  When the submitter posts the URL to the Shortening API
  Then the Shortening API SHALL reject the submission with "We can't shorten this link." WITHIN the EARS.01.04.4eec issue-latency budget (p95)
  And the Shortening API SHALL issue no short code
  # spec_trace: SPEC §5 (Behavior — abuse_control), SPEC §6 (Error Handling)

@scenario-type:error @p1-high @scenario-id:BDD.01.03.842c
@ears:EARS.01.03.3312 @ears:EARS.01.03.a17e @prd:PRD.01.09.21ad @brd:BRD.01.07.882c
Scenario: Unauthorised metrics request is denied
  Given a caller that does not bear the Service-Owner role
  When the caller requests adoption metrics
  Then the Metrics Reporter SHALL deny the request WITHIN the EARS.01.03.3306 metrics budget (p95)
  And the response SHALL contain no counts
  And the denial response body SHALL contain only the contracted denial response
  And the denial response body SHALL NOT disclose any server-side error, stack trace, or dependency diagnostic
  And the Metrics Reporter SHALL write one audit record carrying caller identity, role-decision "denied", and timestamp WITHIN the EARS.01.03.a17e audit budget
  # spec_trace: SPEC §5 (Behavior — authorization), SPEC §6 (Error Handling — audit)

@scenario-type:error @p2-medium @scenario-id:BDD.01.03.6f00
@ears:EARS.01.03.0b67 @prd:PRD.01.13.9a6d @brd:BRD.01.12.8b9b
Scenario: Short-code pool exhausted returns capacity error
  Given the short-code pool is exhausted
  When a Link Submitter posts a well-formed public URL
  Then the Shortening API SHALL return "We can't issue a short link right now." WITHIN the EARS.01.04.4eec issue-latency budget (p95)
  And the Shortening API SHALL emit a pool-exhausted log entry at WARN severity (metric: shortcode_pool_exhaustion_total) for each rejection
  # spec_trace: SPEC §5 (Behavior — capacity), SPEC §6 (Error Handling)

@scenario-type:error @p2-medium @scenario-id:BDD.01.03.b85f
@ears:EARS.01.03.135e @prd:PRD.01.13.9a6d @brd:BRD.01.12.8b9b
Scenario: Pool-exhaustion retry stays within the ceiling
  Given the short-code pool is exhausted and the configured retry ceiling is 3
  When a Link Submitter posts a well-formed public URL
  Then the Shortening API SHALL attempt at most 3 code-allocation retries before returning the capacity error
  # spec_trace: SPEC §5 (Behavior — retry_bound), SPEC §6 (Error Handling)
```

### 3.3 Recovery scenarios

```gherkin
@scenario-type:recovery @p1-high @scenario-id:BDD.01.03.4df6
@ears:EARS.01.03.a2ae @ears:EARS.01.04.f50e @prd:PRD.01.12.19b6 @brd:BRD.01.11.341c
Scenario Outline: Fail closed when the reputation source is degraded
  Given the destination-reputation source is "<degradation>"
  When a Link Submitter posts a well-formed public URL
  Then the Shortening API SHALL fail closed and issue no short code WITHIN the EARS.01.04.4eec issue-latency budget (p95)
  And the Shortening API SHALL return "We can't check this link right now — please try again shortly."
  And the Shortening API SHALL emit a reputation-source-unavailable log entry at ERROR severity identifying the degradation for each rejected submission

  Examples:
    | degradation                              |
    | unreachable                              |
    | dns resolution failure                   |
    | tls handshake failure                    |
    | slow beyond screening budget (>= 600 ms) |
  # dns-resolution and tls-handshake fixtures exercise partition variants on a different code path than an unreachable host (chaos partition breadth)
  # screening budget = the 500 ms issue-latency budget; "slow" fixtures delay >= 600 ms (budget + 100 ms)
  # spec_trace: SPEC §5 (Behavior — fail_closed), SPEC §6 (Error Handling — recovery)

@scenario-type:recovery @p1-high @scenario-id:BDD.01.03.c826
@ears:EARS.01.03.a2ae @ears:EARS.01.04.f50e @prd:PRD.01.12.19b6 @brd:BRD.01.11.341c
Scenario: Reputation source recovers and a resubmission is issued a short code
  Given the destination-reputation source was degraded and is now restored to "reachable"
  When a Link Submitter resubmits a well-formed public URL
  Then the Shortening API SHALL screen the destination and issue a short code WITHIN the EARS.01.04.4eec issue-latency budget (p95)
  # spec_trace: SPEC §5 (Behavior — recovery), SPEC §6 (Error Handling — recovery)

@scenario-type:recovery @p1-high @scenario-id:BDD.01.03.f44a
@ears:EARS.01.03.fab2 @prd:PRD.01.09.ce85 @brd:BRD.01.07.15e1
Scenario Outline: Serve an explicit 5xx when the Link Store is degraded
  Given the Link Store is "<fault>" on the redirect path
  When a Link Visitor requests an otherwise-known short code "/abc123"
  Then the Redirect Handler SHALL return an explicit service-unavailable 5xx response WITHIN the EARS.01.03.fab2 store-unavailable budget (1 s) rather than hanging
  And the Redirect Handler SHALL emit a store-unavailable log entry at ERROR severity identifying the "<fault>"

  Examples:
    | fault                  |
    | connection refused     |
    | dns resolution failure |
    | tls handshake failure  |
    | timeout                |
    | error response         |
  # dns-resolution and tls-handshake fixtures exercise partition variants that take different code paths than a refused TCP connection (chaos partition breadth)
  # recovery after restoration is asserted as a discrete scenario (BDD.01.03.0759)
  # spec_trace: SPEC §5 (Behavior — degraded_mode), SPEC §6 (Error Handling — recovery)

@scenario-type:recovery @p1-high @scenario-id:BDD.01.03.0759
@ears:EARS.01.03.fab2 @prd:PRD.01.09.ce85 @brd:BRD.01.07.15e1
Scenario: Redirect recovers after the Link Store is restored
  Given the Link Store was degraded on the redirect path per BDD.01.03.f44a and has been restored to "reachable"
  When a Link Visitor retries the request for the otherwise-known short code "/abc123"
  Then the Redirect Handler SHALL redirect to the original URL successfully WITHIN @threshold:PRD.01.perf.redirectp95
  # spec_trace: SPEC §5 (Behavior — recovery), SPEC §6 (Error Handling — recovery)

@scenario-type:recovery @p1-high @scenario-id:BDD.01.03.5f58
@ears:EARS.01.03.d808 @ears:EARS.01.03.19ec @ears:EARS.01.04.7934 @prd:PRD.01.12.11be @brd:BRD.01.10.7d5a
Scenario Outline: Redirect survives a degraded visit-count write
  Given an issued short link "/abc123" and a visit-count store that is "<fault>"
  When a Link Visitor requests "/abc123"
  Then the Redirect Handler SHALL complete the redirect to the original URL without blocking or failing it
  And the Redirect Handler SHALL log the dropped increment for reconciliation

  Examples:
    | fault                                        |
    | failing the next write                       |
    | connection refused                           |
    | dns resolution failure                       |
    | tls handshake failure                        |
    | slow beyond the 1 s visit-count budget (p95) |
  # the connection-refused / dns / tls rows exercise true partition variants (different code paths than a write-error) so the EARS.01.03.d808 isolation guarantee holds for both partition and slow faults (chaos partition breadth)
  # spec_trace: SPEC §5 (Behavior — isolation), SPEC §6 (Error Handling — reconciliation)

@scenario-type:recovery @p1-high @scenario-id:BDD.01.03.a7ad
@ears:EARS.01.03.d808 @ears:EARS.01.03.19ec @ears:EARS.01.04.7934 @prd:PRD.01.12.11be @brd:BRD.01.10.7d5a
Scenario: Logged dropped increment is reconciled into the recorded visit count
  Given a visit-count increment was dropped and logged for reconciliation per BDD.01.03.5f58
  When the reconciliation process is triggered
  Then the recorded visit count SHALL be corrected to include the dropped increment WITHIN the reconciliation budget (60 s) of the trigger
  # reconciliation budget (60 s) is an author assumption pending a PRD/EARS reconciliation-window element; it backs the EARS.01.03.19ec visit-count no-loss invariant
  # spec_trace: SPEC §5 (Behavior — reconciliation), SPEC §4 (Data Models)

@scenario-type:recovery @p1-high @scenario-id:BDD.01.03.bdae
@ears:EARS.01.03.86ae @ears:EARS.01.03.97c4 @ears:EARS.01.04.8e22 @prd:PRD.01.13.7760 @brd:BRD.01.10.e118
Scenario: Concurrent issuance collision resolves to distinct codes
  Given two Link Submitters and a code generator seeded to emit the same candidate short code "abc123" for both submissions, forcing their allocation to race for that candidate
  When both submissions are processed concurrently
  Then the Shortening API SHALL atomically grant the candidate code to exactly one submission and issue a distinct code to the other, preserving uniqueness
  # spec_trace: SPEC §5 (Behavior — concurrency), SPEC §4 (Data Models — uniqueness)

@scenario-type:recovery @p1-high @scenario-id:BDD.01.03.ed21
@ears:EARS.01.03.8df7 @ears:EARS.01.04.93f7 @prd:PRD.01.13.ebf9 @brd:BRD.01.10.3407
Scenario Outline: Issuance fails closed when the Link Store is degraded on the write path
  Given a Link Submitter posts a well-formed public URL and the Link Store is "<fault>" on the issuance write path
  When the Shortening API attempts to durably commit the short-code-to-URL mapping
  Then the Shortening API SHALL return no acknowledged short code
  And the Shortening API SHALL leave no durable mapping in the Link Store
  And the Shortening API SHALL leave no orphan short code

  Examples:
    | fault                                     |
    | connection refused                        |
    | dns resolution failure                    |
    | tls handshake failure                     |
    | slow beyond the commit budget (>= 600 ms) |
  # dns-resolution and tls-handshake fixtures exercise partition variants on a different code path than a refused TCP connection (chaos partition breadth)
  # commit budget = the 500 ms issue-latency budget; "slow" fixtures delay >= 600 ms (budget + 100 ms)
  # idempotent recovery after restoration is asserted as a discrete scenario (BDD.01.03.bcfb)
  # spec_trace: SPEC §4 (Data Models — durability), SPEC §5 (Behavior — write ordering), SPEC §6 (Error Handling — recovery)

@scenario-type:recovery @p1-high @scenario-id:BDD.01.03.bcfb
@ears:EARS.01.03.8df7 @ears:EARS.01.04.93f7 @prd:PRD.01.13.ebf9 @brd:BRD.01.10.3407
Scenario: Issuance recovers idempotently after the Link Store write path is restored
  Given an issuance attempt failed closed while the Link Store write path was degraded per BDD.01.03.ed21, and the Link Store has been restored to "reachable"
  When the Link Submitter retries the submission
  Then the Shortening API SHALL issue exactly one short code under idempotent acknowledgement and leave no orphan code WITHIN the EARS.01.04.4eec issue-latency budget (p95)
  # spec_trace: SPEC §4 (Data Models — durability), SPEC §5 (Behavior — recovery), SPEC §6 (Error Handling — recovery)

@scenario-type:recovery @p2-medium @scenario-id:BDD.01.03.b3fe
@ears:EARS.01.03.0b67 @prd:PRD.01.13.9a6d @brd:BRD.01.12.8b9b
Scenario: Short-code issuance resumes after pool capacity is restored
  Given the short-code pool was exhausted and the capacity error was returned
  When pool capacity is restored by key-space expansion or code reclamation
  Then a fresh well-formed submission SHALL be issued a unique short code WITHIN the EARS.01.04.4eec issue-latency budget (p95)
  # spec_trace: SPEC §5 (Behavior — capacity recovery), SPEC §6 (Error Handling — recovery)

@scenario-type:recovery @p1-high @scenario-id:BDD.01.03.1a55
@ears:EARS.01.03.a132 @ears:EARS.01.03.fab2 @ears:EARS.01.04.ca05 @prd:PRD.01.09.ce85 @brd:BRD.01.07.15e1
Scenario: Redirect path sheds load under connection-pool saturation
  Given the redirect path is served at 100 requests per second with 20 concurrent visitors while the Link Store is slow beyond the 1 s budget
  When the redirect-path connection pool saturates under the sustained load
  Then the Redirect Handler SHALL shed excess load with an explicit service-unavailable 5xx WITHIN the EARS.01.03.fab2 store-unavailable budget (1 s) rather than queue-blocking or dropping non-shed requests
  And the Redirect Handler SHALL emit a load-shed log entry at WARN severity per shed request carrying reason "connection_pool_saturated" (metric: redirect_shed_total)
  # within-window success of non-shed requests is the observable proxy for the long-horizon redirect-availability SLO (the BRD-01 monthly redirect-availability reliability threshold); monthly uptime is not computable from this transient window
  # recovery after pressure clears is asserted as a discrete scenario (BDD.01.03.dd27)
  # spec_trace: SPEC §5 (Behavior — load_shedding), SPEC §6 (NFR — resource exhaustion, recovery)

@scenario-type:recovery @p1-high @scenario-id:BDD.01.03.dd27
@ears:EARS.01.03.a132 @ears:EARS.01.03.fab2 @ears:EARS.01.04.ca05 @prd:PRD.01.09.ce85 @brd:BRD.01.07.15e1
Scenario: Redirect path resumes normal latency after connection-pool pressure clears
  Given the redirect path was shedding load under connection-pool saturation per BDD.01.03.1a55 and the connection-pool pressure has cleared
  When a Link Visitor requests an otherwise-known short code "/abc123"
  Then the Redirect Handler SHALL resume serving redirects WITHIN @threshold:PRD.01.perf.redirectp95
  # spec_trace: SPEC §5 (Behavior — load_shedding, recovery), SPEC §6 (NFR — recovery)
```

### 3.4 Parameterized scenarios

```gherkin
@scenario-type:parameterized @p1-high @scenario-id:BDD.01.03.e8b9
@ears:EARS.01.03.eeaf @prd:PRD.01.09.de1c @prd:PRD.01.12.2670 @brd:BRD.01.07.6c3f
Scenario Outline: Reject malformed or oversized submissions
  Given a Link Submitter with the submission "<submission>"
  When the submitter posts it to the Shortening API
  Then the Shortening API SHALL reject it with "That doesn't look like a valid web address." WITHIN the EARS.01.04.4eec issue-latency budget (p95)
  And the Shortening API SHALL issue no short code
  And the response body SHALL contain only the contracted rejection string
  And the response body SHALL NOT disclose any server-side error, stack trace, or dependency diagnostic

  Examples:
    | submission                                      |
    | (empty)                                         |
    | not-a-url                                       |
    | ftp://example.com/resource                      |
    | https://example.com/<2049-char-path>            |
    | https://example.com/%3Cscript%3E%00DROP%20TABLE |
  # the injection-class row (percent-encoded script / NUL control-char / SQL payload) exercises the no-disclosure clause against a submission designed to provoke a parser or dependency error
  # spec_trace: SPEC §3 (Interfaces — validation), SPEC §6 (Error Handling)

@scenario-type:parameterized @p1-high @scenario-id:BDD.01.03.5599
@ears:EARS.01.03.fa44 @ears:EARS.01.04.1453 @prd:PRD.01.12.6f96 @brd:BRD.01.08.daeb
Scenario Outline: Reject non-public destinations
  Given a Link Submitter with a destination host "<host>"
  When the submitter posts the URL to the Shortening API
  Then the Shortening API SHALL reject it under the not-a-valid-address contract WITHIN the EARS.01.04.4eec issue-latency budget (p95)
  And the Shortening API SHALL issue no short code
  And the response body SHALL contain only the contracted rejection string
  And the response body SHALL NOT disclose any server-side error, stack trace, or dependency diagnostic

  Examples:
    | host                     |
    | 127.0.0.1                |
    | 10.0.0.5                 |
    | 169.254.169.254          |
    | metadata.google.internal |
  # host classes (non-parameterizing annotation): 127.0.0.1 = loopback; 10.0.0.5 = rfc1918; 169.254.169.254 = link-local; metadata.google.internal = cloud-metadata
  # spec_trace: SPEC §3 (Interfaces — SSRF denylist), SPEC §6 (NFR — security)

@scenario-type:parameterized @p1-high @scenario-id:BDD.01.03.6934
@ears:EARS.01.03.ab5e @ears:EARS.01.03.b5fa @ears:EARS.01.03.c7e3 @ears:EARS.01.03.d8a2 @prd:PRD.01.13.835e @brd:BRD.01.11.341c
Scenario Outline: Throttle abusive submission and probe sources
  Given one source whose traffic matches the "<pattern>" signature defined as "<threshold>"
  When the source's traffic crosses that "<threshold>" within the stated window
  Then the "<actor>" SHALL apply "<response>" under the "<control>" control
  And the "<actor>" SHALL emit one detection event WITHIN the EARS.01.03.ab5e detection budget (100 ms)
  And that detection event SHALL carry the offending source identity, the "<control>" and "<threshold>" crossed, the "<response>" applied, and a timestamp

  Examples:
    | pattern                | control          | threshold (author assumption)              | actor            | response                                |
    | submission flood       | anti-abuse       | > 60 submissions in 60 s from one source   | Shortening API   | throttle                                |
    | mass-minting signature | anti-abuse       | > 200 submissions in 600 s from one source | Shortening API   | cooldown denial, no codes issued        |
    | enumeration probe      | anti-enumeration | > 100 distinct code lookups in 60 s        | Redirect Handler | cooldown                                |
    | scraping signature     | anti-enumeration | > 1,000 not-found lookups in 600 s         | Redirect Handler | block returning only standard not-found |
  # threshold column values are author assumptions pending a PRD §13 anti-abuse threshold element
  # spec_trace: SPEC §5 (Behavior — abuse_control), SPEC §6 (Error Handling — detection events)
```

### 3.5 Optional scenarios

```gherkin
@scenario-type:optional @p2-medium @scenario-id:BDD.01.03.e452
@ears:EARS.01.03.ee86 @ears:EARS.01.04.b1aa @prd:PRD.01.13.835e @brd:BRD.01.11.341c
Scenario: Anti-automation rate limiting when configured
  Given anti-automation rate limiting is configured at 60 requests per 60 s from one source
  When a source issues submit or redirect requests exceeding the configured rate within that window
  Then the Shortening API SHALL reject the over-rate requests with an explicit throttling response WITHIN the throttle-response budget (100 ms) of the configured rate being exceeded
  # the 60-requests-per-60-s configured rate and the 100 ms throttle-response budget are fixture-configured author assumptions pending a PRD §13 rate-limit element; EARS.01.03.ee86 names the rate-limit control but assigns no value
  # spec_trace: SPEC §5 (Behavior — rate_limit), SPEC §6 (NFR — abuse control)

@scenario-type:optional @p3-low @scenario-id:BDD.01.03.d521
@ears:EARS.01.03.ee86 @prd:PRD.01.13.835e @brd:BRD.01.11.341c
Scenario: No throttling where rate limiting is not configured
  Given anti-automation rate limiting is not configured
  When a source issues 120 submit requests at 2 requests per second from one source
  Then the Shortening API SHALL apply the default behaviour to every request
  And the Shortening API SHALL NOT throttle any request on rate alone within a 60 s observation window
  # the 120-request / 2-requests-per-second load and the 60 s observation window after which a non-throttled outcome is conclusive are fixture-configured author assumptions pending a PRD §13 rate-limit element; EARS.01.03.ee86 names the rate-limit control but assigns no value
  # spec_trace: SPEC §2 (Component Overview — defaults), SPEC §5 (Behavior)

@scenario-type:optional @p2-medium @scenario-id:BDD.01.03.fa47
@ears:EARS.01.03.00b9 @prd:PRD.01.13.9a6d @brd:BRD.01.12.8b9b
Scenario: Pool-utilization alert when threshold crossed
  Given the high-utilization threshold is configured to 80% over a 100-slot short-code pool with 79 slots occupied (79% utilization)
  When a single code allocation pushes utilization to 80%, crossing the configured high-utilization threshold
  Then the Shortening API SHALL emit one capacity-utilization alert to the Service Owner WITHIN the EARS.01.03.00b9 alert-emission budget (5 s) of the crossing
  And the alert SHALL carry the current utilization percentage, the configured high-utilization threshold value, and a timestamp, delivered to the Service-Owner operations channel
  # the 80% high-utilization threshold, the 100-slot pool cardinality (79 of 100 slots occupied, so one allocation crosses 79%->80%), and the 5 s alert-emission budget are fixture-configured author assumptions pending a PRD §13 capacity-threshold element; EARS.01.03.00b9 names the threshold but assigns no value
  # spec_trace: SPEC §5 (Behavior — alerting), SPEC §6 (NFR — observability)
```

## 4. Traceability

**Document tag:** @bdd: BDD-01

### 4.1 Cumulative upstream tags (Layer 4 — all mandatory)

Every scenario carries `@brd`, `@prd`, and `@ears` inline (§3). Distinct
upstream documents referenced:

- **EARS:** EARS-01 (all §3 trigger-response lines and §4 quality lines).
- **PRD:** PRD-01 (PRD.01.09.\*, PRD.01.12.\*, PRD.01.13.\* feature/NFR lines).
- **BRD:** BRD-01 (BRD.01.07.\*, BRD.01.08.\*, BRD.01.10.\*, BRD.01.11.\*,
  BRD.01.12.\* objectives).

### 4.2 EARS → BDD coverage matrix (bidirectional)

Every EARS-01 line maps to at least one scenario; every scenario maps back to
at least one EARS line. EARS coverage: 44/44 lines (100%).

| EARS line | Pattern | BDD scenario(s) |
|-----------|---------|-----------------|
| EARS.01.03.f909 | event | BDD.01.03.d541 |
| EARS.01.03.5aa9 | event | BDD.01.03.0b2a |
| EARS.01.03.db78 | event | BDD.01.03.5887 |
| EARS.01.03.00b9 | event | BDD.01.03.fa47 |
| EARS.01.03.e2e9 | event | BDD.01.03.6d94 |
| EARS.01.03.8f70 | event | BDD.01.03.1664 |
| EARS.01.03.539a | event | BDD.01.03.cbf4 |
| EARS.01.03.539b | event | BDD.01.03.8604 |
| EARS.01.03.a0ae | event | BDD.01.03.f9d6, BDD.01.03.842c |
| EARS.01.03.3306 | event | BDD.01.03.f9d6 |
| EARS.01.03.ab5e | event | BDD.01.03.6934 |
| EARS.01.03.c7e3 | event | BDD.01.03.6934 |
| EARS.01.03.a17e | event | BDD.01.03.40d7, BDD.01.03.842c |
| EARS.01.03.a132 | state | BDD.01.03.b9e7, BDD.01.03.1a55, BDD.01.03.dd27 |
| EARS.01.03.ee86 | optional | BDD.01.03.e452, BDD.01.03.d521 |
| EARS.01.03.eeaf | unwanted | BDD.01.03.e8b9 |
| EARS.01.03.fa44 | unwanted | BDD.01.03.5599 |
| EARS.01.03.5821 | unwanted | BDD.01.03.4356 |
| EARS.01.03.e606 | unwanted | BDD.01.03.4356 |
| EARS.01.03.fab2 | unwanted | BDD.01.03.f44a, BDD.01.03.0759, BDD.01.03.1a55, BDD.01.03.dd27 |
| EARS.01.03.d808 | unwanted | BDD.01.03.5f58, BDD.01.03.a7ad |
| EARS.01.03.0b67 | unwanted | BDD.01.03.6f00, BDD.01.03.b3fe |
| EARS.01.03.135e | unwanted | BDD.01.03.b85f |
| EARS.01.03.a2ae | unwanted | BDD.01.03.4df6, BDD.01.03.c826 |
| EARS.01.03.9671 | unwanted | BDD.01.03.bcf8 |
| EARS.01.03.3312 | unwanted | BDD.01.03.842c |
| EARS.01.03.b5fa | unwanted | BDD.01.03.6934 |
| EARS.01.03.d8a2 | unwanted | BDD.01.03.6934 |
| EARS.01.03.86ae | unwanted | BDD.01.03.bdae |
| EARS.01.03.97c4 | ubiquitous | BDD.01.03.d541, BDD.01.03.bdae |
| EARS.01.03.8df7 | ubiquitous | BDD.01.03.8b97, BDD.01.03.ed21, BDD.01.03.bcfb |
| EARS.01.03.19ec | ubiquitous | BDD.01.03.1664, BDD.01.03.5f58, BDD.01.03.a7ad |
| EARS.01.03.187c | ubiquitous | BDD.01.03.6d94 |
| EARS.01.04.e27b | perf | BDD.01.03.b9e7 |
| EARS.01.04.4eec | perf | BDD.01.03.d541 |
| EARS.01.04.1453 | security | BDD.01.03.5599 |
| EARS.01.04.ee3f | security | BDD.01.03.bcf8 |
| EARS.01.04.f50e | security | BDD.01.03.4df6, BDD.01.03.c826 |
| EARS.01.04.b1aa | security | BDD.01.03.e452 |
| EARS.01.04.c060 | security | BDD.01.03.2986 |
| EARS.01.04.ca05 | reliability | BDD.01.03.b9e7, BDD.01.03.1a55, BDD.01.03.dd27 |
| EARS.01.04.8e22 | reliability | BDD.01.03.bdae |
| EARS.01.04.93f7 | reliability | BDD.01.03.8b97, BDD.01.03.ed21, BDD.01.03.bcfb |
| EARS.01.04.7934 | reliability | BDD.01.03.1664, BDD.01.03.5f58, BDD.01.03.a7ad |

> **Coverage note (EARS.01.04.4eec — issuance-latency budget):** the row above
> lists BDD.01.03.d541 as the named-binding scenario, but the 500 ms issuance
> latency budget is exercised as the `WITHIN ... EARS.01.04.4eec issue-latency
> budget (p95)` constraint in every issuance-path scenario that cites it —
> 5887, 6d94-adjacent issuance flows, bcf8, e8b9, 5599, 4df6, c826, ed21, bcfb,
> b3fe, and 6f00 among them. All such scenarios also cover this quality line;
> the single-row listing understates actual coverage and is retained only as
> the canonical binding anchor.

### 4.3 Scenario category coverage

| Category | Count | Scenario IDs |
|----------|-------|--------------|
| success | 11 | d541, 0b2a, 5887, 6d94, 1664, f9d6, cbf4, 40d7, b9e7, 2986, 8b97 |
| error | 6 | 4356, 8604, bcf8, 842c, 6f00, b85f |
| recovery | 12 | 4df6, c826, f44a, 0759, 5f58, a7ad, bdae, ed21, bcfb, b3fe, 1a55, dd27 |
| parameterized | 3 | e8b9, 5599, 6934 |
| optional | 3 | e452, d521, fa47 |

Failure↔recovery pairing: reputation-source outage pairs a degraded fail-closed
path (4df6) with an explicit restoration assertion (c826); the visit-count write
fault (5f58) pairs with a bounded reconciliation assertion (a7ad); the Link-Store
fault is paired on both the redirect path (f44a) and the issuance write path
(ed21); pool exhaustion (6f00) pairs with a capacity-restoration assertion (b3fe);
and the issuance race (bdae) preserves uniqueness. Resource-exhaustion paths: pool
exhaustion (6f00), bounded retry (b85f), rate-limit ceiling (e452), and
connection-pool saturation under load with load-shedding recovery (1a55).

### 4.4 Downstream (expected)

| Consumer | Layer | Relationship |
|----------|-------|--------------|
| ADR | 5 | Architecture decisions must satisfy these scenarios (registry downstream). |
| SPEC | 6 | Each scenario's `spec_trace` names the SPEC sections it will exercise. |
| TDD | 7 | Cross-reference: TDD maps these scenarios to concrete test cases via SPEC contracts. |

### 4.5 Health score

| Metric | Value |
|--------|-------|
| ADR readiness (provisional) | 94/100 |
| EARS coverage | 100% (44/44 lines) |
| Target score | ≥90/100 |

## Glossary

| Term | Definition |
|------|------------|
| BDD | Behavior-Driven Development — executable Given-When-Then acceptance scenarios. |
| Gherkin | Structured Given-When-Then syntax for executable scenarios. |
| Scenario Outline | A parameterized Gherkin scenario driven by an Examples table. |
| ADR readiness | Score measuring BDD maturity for the ADR transition (≥90 required). |
| Short code | A compact identifier standing in for a long URL. |
| Short link | A short-code reference that redirects to its original URL when visited. |
| Hot path | The synchronous redirect path the latency budget measures. |
| Fail closed | On a dependency outage, deny rather than proceed unscreened. |
| SSRF | Server-Side Request Forgery — abuse of a fetch to reach non-public hosts. |
| Detection event | An emitted signal recording that an abuse threshold was crossed. |
| RPO | Recovery Point Objective — tolerated data loss window; zero for issued mappings. |
