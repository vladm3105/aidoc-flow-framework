---
layer: 04_BDD
lens: tech_lead
weight: 25
agent: solutions-architect
framework_spec_version: "0.39.0"
---
# tech_lead lens — BDD layer

## Reasoning frame

The tech_lead lens at BDD altitude evaluates scenario implementability. At
EARS altitude this lens validated rule implementability: were the numeric
bounds, timeout values, and state-transition obligations achievable given the
system architecture? At BDD altitude the question is one layer more concrete:
can a step-definition author translate each scenario step (a `given`/`when`/
`then` entry) into a deterministic, automatable test implementation without
guessing? A scenario that uses natural-language steps which cannot be
expressed as a finite sequence of API calls, fixture operations, and
assertions is not an executable specification — it is documentation with
scenario syntax applied to it.

Step-definition implementability has several failure modes. Implicit timing
assumptions — a step that says "wait until the system responds" without a
numeric timeout — produce tests that pass on fast infrastructure and time out
on slow infrastructure, creating environment-sensitive flakiness. Cross-scenario
dependencies — a scenario whose preconditions assume another scenario ran
first — produce ordering-sensitive suites that cannot be parallelised and
produce misleading failures when run in isolation. Non-idempotent fixture
setup — teardown that does not fully reverse the state change setup produced
— leaves test-database pollution that accumulates across runs.

At SPEC downstream the tech_lead lens descends to component-level design
concerns: module interfaces, dependency boundaries, data contracts. At BDD the
lens does not reach into design — it asks only whether the scenario can be
implemented as written by a developer who knows nothing beyond the scenario's
`given`/`when`/`then` text. This lens does NOT evaluate: EARS coverage
(qa_lead), failure-mode scenario completeness (chaos_engineer), abuse-case
coverage (security_engineer), observability hooks (operator), or schema and ID
conformance (auditor).

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check citation
are out-of-scope and discarded by the synthesizer.

**C1 — Step definitions implementable as written.** Each `given`/`when`/`then`
step must be expressible as a bounded, deterministic sequence of operations
against the system under test. Steps that rely on subjective human judgement
("verify the response looks correct"), on conditions that cannot be observed
programmatically, or on external systems with no documented test-double
contract are not implementable. Missing → P2 citing C1.

**C2 — Timeout and wait reasoning explicit.** Every scenario step that
involves waiting for an asynchronous event, polling for a condition, or
asserting on an eventually-consistent state must declare a numeric timeout
or polling ceiling. Steps that say "eventually", "after some time", or
"when ready" without a numeric bound produce environment-sensitive timing
behaviour that is not reproducible. Missing → P2 citing C2.

**C3 — Fixture setup and teardown idempotent.** The `background:` steps or
`given:` steps that establish test preconditions must produce the same starting state
regardless of whether they run against a clean environment or an environment
partially modified by a prior test run. Teardown steps must fully reverse
all state changes made during the scenario. Missing → P2 citing C3.

**C4 — Cross-scenario dependencies absent.** No scenario may rely on state
produced by a prior scenario as a precondition. Each scenario must be
independently executable in any order, in isolation, and in parallel with
other scenarios. Scenarios that share mutable state through a common
fixture, database row, or file path without per-scenario isolation are
ordering-dependent and parallelisation-unsafe. Missing → P1 citing C4.

**C5 — Scenario-scoped attributes stay on the scenario.** A scenario's `ears`,
`type`, `priority`, and `spec_trace` are scenario-scoped and must live on that
scenario's mapping — not be hoisted to the `feature:` block. The `feature:`
block is a container and must carry no `ears` field; its coverage is the
computed union of its scenarios' `ears` (D-3). Attributing a scenario-specific
upstream reference or classification to the feature, or omitting it from the
scenario it belongs to, breaks element-level coverage attribution and the
edge-graph. Missing → P3 citing C5.

## Beyond-checklist

If you find a layer-specific failure mode the checklist does not cover, raise
it as a P2/P3 finding citing `beyond-checklist:<principle-tag>` and state
which paragraph of the reasoning frame motivates it. Use sparingly. If
more than 30% of your findings are beyond-checklist, the playbook needs
revision (file a follow-up).

## No-findings rationale

A lens returning `lens_score: 100` with `findings: []` (zero findings)
MUST accompany its persona-output record with a `no_findings_rationale`
field naming at least one specific section where the lens *did* examine
the artifact and explicitly cleared. Example for this lens:

> `no_findings_rationale: "§<section-number> <topic> — examined and
> verified clean against checks C1-C5; no deviation from upstream
> required attributes."`

The synthesizer treats a missing or empty `no_findings_rationale` on
a `lens_score: 100 / findings: []` output as a structural error and
caps the lens at 95 (with a `STRUCTURE-RAT-001` advisory in the
verdict). The cap is a calibration nudge against "convergence theater"
— a lens that genuinely cleared the artifact must say *what* it
cleared, otherwise the score is unsubstantiated.

Filing findings (any priority, including P3 nits) bypasses the
rationale requirement — findings ARE the rationale.

## Scoring

| Outcome | lens_score |
|---|---|
| No findings; every check ran clean | 100 |
| P3 findings only; no checklist holes | 90-99 |
| 1-2 P2 findings against checks; no P1 | 80-89 |
| 3+ P2 against checks OR 1 P1 | 70-79 |
| P0 present OR systemic checklist failure | < 70 |
