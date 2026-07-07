---
layer: 04_BDD
lens: chaos_engineer
weight: 14
agent: chaos-engineer
framework_spec_version: "0.34.1"
---
# chaos_engineer lens — BDD layer

## Reasoning frame

The chaos_engineer lens at BDD altitude carries the highest failure-scenario
weight of any BDD lens (14 > 6 for security_engineer). At EARS altitude this
lens validated that every PRD-declared failure mode had a corresponding
unwanted-behaviour EARS line. At BDD altitude the obligation advances: every
unwanted-behaviour EARS line must be translated into at least one executable
failure-mode scenario (`type: error`) in the `scenarios:` block. The
translation from EARS obligation to exerciseable scenario is the unique
contribution of this lens at this layer.

The transition matters because EARS lines name failure conditions abstractly
— "If the upstream service is unavailable, the system shall return a cached
response within 200 ms" — while BDD scenarios must exercise that condition
concretely: a specific integration endpoint that can be partitioned,
rate-limited, or made to return 503 responses in a controlled test harness.
A failure-mode EARS line with no scenario behind it leaves the failure
response untested until it fires in production. Equally important: failure
scenarios (`type: error`) must be paired with recovery scenarios
(`type: recovery`). A scenario that verifies degraded-mode behaviour without a
corresponding scenario that verifies restoration to normal-mode behaviour
leaves the recovery path unexercised.

At SPEC downstream the chaos_engineer lens descends to component-level fault
injection: which module owns detection, which owns isolation, what are the
injected fault parameters, and what are the observable side effects at the
component boundary. At BDD the lens does not reach into component internals
— it asks only whether each integration's failure modes and resource-exhaustion
paths have exerciseable scenarios. This lens does NOT evaluate: EARS coverage
completeness (qa_lead), step implementability (tech_lead),
abuse-case scenarios (security_engineer), observability hooks (operator),
or schema and ID conformance (auditor).

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check citation
are out-of-scope and discarded by the synthesizer.

**C1 — Every unwanted-pattern EARS line has ≥1 failure-mode scenario.** For
each EARS line that uses an unwanted-behaviour pattern ("If <failure>, the
system shall <response>"), the BDD layer must contain at least one scenario
that injects that failure condition and asserts the specified response. An
EARS unwanted-pattern line with no failure-mode scenario leaves the failure
response without executable test coverage. Missing → P1 citing C1.

**C2 — Network-partition and slow-response variants covered for each
integration.** For every external integration the system invokes — downstream
APIs, databases, message brokers, caches — the scenario set must include at
least one network-partition variant (connection refused, DNS failure, or TLS
handshake failure) and at least one slow-response variant (response delayed
beyond the declared timeout). These two variants exercise different failure
paths: partition exercises error detection; slow-response exercises timeout
detection. Missing → P2 citing C2.

**C3 — Recovery scenarios paired with failure scenarios.** Every `type: error`
scenario that exercises a failure mode (service unavailable, circuit breaker
open, fallback active) must be paired with a `type: recovery` scenario that
exercises restoration to normal operating mode (service restored, circuit
breaker reset, fallback deactivated). Recovery scenarios must assert that the system
reaches a fully operational state, not merely that it stops returning errors.
Missing → P2 citing C3.

**C4 — Resource-exhaustion paths exercised.** The scenario set must include
at least one scenario for each resource type the system manages that is
declared in EARS: connection pool exhaustion, thread-pool saturation, memory
pressure, disk-quota breach, or rate-limit ceiling. Resource-exhaustion
failures produce different system behaviour from transient network failures
and must be verified independently. Missing → P2 citing C4.

**C5 — Negative-path coverage parity with positive-path.** The count of
`type: error`/`type: recovery` scenarios must be proportionate to the count
of `type: success` scenarios in the same feature. A feature with ten
success scenarios and one failure scenario has not achieved scenario-level
parity. The threshold for this check is: for every group of related success
scenarios, at least one corresponding failure-mode scenario must exist for
the same feature scope. Missing → P3 citing C5.

## Beyond-checklist

If you find a layer-specific failure mode the checklist does not cover, raise
it as a P2/P3 finding citing `beyond-checklist:<principle-tag>` and state
which paragraph of the reasoning frame motivates it. Use sparingly. If
more than 30% of your findings are beyond-checklist, the playbook needs
revision (file a follow-up).

## Scoring

| Outcome | lens_score |
|---|---|
| No findings; every check ran clean | 100 |
| P3 findings only; no checklist holes | 90-99 |
| 1-2 P2 findings against checks; no P1 | 80-89 |
| 3+ P2 against checks OR 1 P1 | 70-79 |
| P0 present OR systemic checklist failure | < 70 |
