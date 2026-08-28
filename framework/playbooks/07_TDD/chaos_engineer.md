---
layer: 07_TDD
lens: chaos_engineer
weight: 10
agent: chaos-engineer
framework_spec_version: "0.44.0"
---
# chaos_engineer lens — TDD layer

## Reasoning frame

The chaos_engineer lens at TDD altitude evaluates whether the failure
scenarios committed by the upstream BDD layer have actually been
encoded as executable tests, and whether the resilience NFRs committed
by the SPEC layer are exercised by tests that target the right bounds.
A BDD chaos scenario without a paired TDD test is a behavior the
implementation can violate undetected. A SPEC saturation curve
without a load test means the production system will discover its
saturation point during an outage. The chaos_engineer lens enforces
that BDD's failure-scenario commitments and SPEC's resilience NFRs
have downstream test coverage with concrete, debuggable bounds.

Failure-recovery test pairing is the first concern. Each BDD scenario
that injects a failure (network partition, dependency timeout, store
outage, pool exhaustion) must have a paired TDD test asserting both
that the failure is detected and that the recovery condition holds —
that the system returns to normal once the failure clears. A failure
test without a recovery assertion silently allows the implementation
to enter a permanent degraded state.

Saturation / load / overload tests targeting SPEC bounds are the
second concern. SPEC names design load, safe overload margin, and
beyond-margin behavior with specific numbers. TDD tests must use
those exact numbers, not arbitrary "reasonable" values — a test that
asserts the system handles 90 RPS when SPEC says 100 RPS is the
design point either has a bug or has degraded silently. The tests
are the proof; the SPEC numbers are the contract.

Fault-injection primitives and recovery-time bounds round out the
lens. Network-partition / timeout / dependency-failure tests must use
injectable primitives (toxiproxy, controllable mocks, fault-injection
libraries) rather than relying on real failures. Recovery-time
assertions must reference SPEC's MTTR bound — not just "eventually."
Failure tests must be isolated from each other (cross-test
contamination, e.g. a leaked failure-inject left active for the next
test, is a major flake source).

This lens does NOT evaluate: test-suite integrity (qa_lead), test-
engineering (tech_lead), security-test coverage (security_engineer),
observability emission (operator), or upstream-trace conformance
(auditor). The chaos_engineer lens is confined to failure-mode test
coverage and resilience bounds.

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check citation
are out-of-scope and discarded by the synthesizer.

**C1 — Every BDD chaos scenario has a paired TDD test asserting
recovery.** Each BDD scenario that injects a failure (partition,
timeout, dependency outage, pool exhaustion) has a paired TDD test
that asserts (a) the failure is detected and (b) recovery condition
holds when the failure clears. Detection-only tests allow silent
degradation. Missing → P1 citing C1.

**C2 — Saturation / load / overload tests target SPEC's NFR
bounds.** Tests for load behavior use the specific numbers SPEC
named (design load, safe overload margin, beyond-margin shed/queue
threshold). Tests using arbitrary numbers test something the SPEC
doesn't constrain — they're noise. Missing or arbitrary → P2
citing C2.

**C3 — Fault-injection tests use injectable primitives.** Network-
partition / timeout / dependency-failure tests use controllable
fault primitives (toxiproxy, fault-injection libraries, controllable
mocks) — not real failures or sleeps. Real failures are non-
deterministic; sleeps don't actually inject the modeled fault.
Missing primitives → P2 citing C3.

**C4 — Recovery-time assertions reference SPEC's MTTR bound.**
Tests for recovery scenarios assert recovery within the MTTR bound
SPEC named — not just "eventually returns to normal." Open-ended
recovery assertions mask drift. Missing → P3 citing C4.

**C5 — Failure-test isolation prevents cross-test contamination.**
Each failure test cleans up its injected fault before exit; the next
test sees a clean baseline. Leaked fault-injections are a major
flake source. Missing isolation → P3 citing C5.

## Beyond-checklist

If you find a failure-mode test failure mode the checklist does not
cover, raise it as a P2/P3 finding citing `beyond-checklist:<principle-tag>`
and state which paragraph of the reasoning frame motivates it. Common
beyond-checklist cases at TDD: cascading-fault-untested (the test
injects one fault but the implementation can cascade — second-order
failures untested), retry-storm-not-exercised (retry tests don't
verify the back-off bound holds), or graceful-degradation-untested
(SPEC names degradation order but TDD only tests degraded-feature
absence, not preserved-feature presence). Use sparingly. If more
than 30% of your findings are beyond-checklist, the playbook needs
revision (file a follow-up).

## Scoring

| Outcome | lens_score |
|---|---|
| No findings; every check ran clean | 100 |
| P3 findings only; no checklist holes | 90-99 |
| 1-2 P2 findings against checks; no P1 | 80-89 |
| 3+ P2 against checks OR 1 P1 | 70-79 |
| P0 present OR systemic checklist failure | < 70 |
