---
layer: 04_BDD
lens: operator
weight: 10
agent: devops-release-engineer
framework_spec_version: "0.48.0"
---
# operator lens — BDD layer

## Reasoning frame

The operator lens makes its first appearance at BDD altitude. No upstream
layer (BRD, PRD, EARS) carries an operator lens — those layers operate at
requirements and acceptance-criterion altitude where runtime behaviours are
not yet fully specified. BDD is the first layer at which runtime, operational,
and observability concerns become concrete enough to be expressed as executable
scenarios. At TDD downstream the operator lens deepens into implementation-level
concerns: metric instrumentation code, log-format contracts, alert rule
unit tests. At BDD altitude the lens validates that runtime-observable and
operationally-significant behaviours have scenario coverage before implementation
begins.

Operational scenarios at BDD altitude have three planes. The first is
observability: every significant state transition, every error path, and every
SLO-relevant event must produce an observable signal — a log entry, a metric
increment, or a distributed trace span — and the scenario must assert that
signal's presence. A feature that passes all functional scenarios but emits
no observable signals is not operable in production. The second plane is
runtime control: the system must expose operator actions — configuration
changes, drain commands, feature toggles, rollback triggers — and scenarios
must verify those actions take effect correctly. The third plane is deployment
safety: scenarios must exercise behaviour under concurrent traffic, including
deploy-during-traffic and gradual-rollout conditions.

This lens does NOT evaluate: EARS coverage completeness (qa_lead), step
implementability (tech_lead), failure-mode scenario coverage (chaos_engineer),
abuse-case coverage (security_engineer), or schema and ID conformance (auditor).
The operator lens is confined to runtime observability, operator-action
correctness, and deployment-safety coverage at the BDD scenario layer.

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check citation
are out-of-scope and discarded by the synthesizer.

**C1 — Observability hooks in scenarios.** For every scenario that exercises
a significant state transition, error condition, or SLO-relevant event, at
least one `then:` step must assert an observable signal: a log entry at the
specified severity and with the specified structured fields, a named metric
incremented to the expected value, or a distributed trace span with the
expected tags. Scenarios that assert only functional outcomes without any
observability assertion leave operational visibility unverified. Missing →
P3 citing C1.

**C2 — Runtime-config-change scenarios.** Where the system accepts
runtime-configuration changes — feature flags, rate-limit values, timeout
overrides, toggle states — the scenario set must include at least one
scenario per configurable parameter that exercises the change taking effect
without a service restart. The scenario must assert both the new behaviour
and the absence of regression on unrelated paths. Missing → P3 citing C2.

**C3 — Deploy-during-traffic scenarios.** For any system component declared
as a zero-downtime deployment target in EARS or PRD, the scenario set must
include at least one scenario that asserts in-flight requests complete
successfully when a new version is deployed alongside the old. The scenario
must assert that no requests return 5xx errors during the transition window.
Missing → P3 citing C3.

**C4 — Operator-action scenarios.** The scenario set must include at least
one scenario per declared operator action in EARS: drain (shed new traffic,
allow in-flight to complete), rollback (revert to prior version, assert
state consistency), freeze (suspend write operations, assert read-only mode
active), or equivalent. Operator actions without scenario coverage are
untested emergency procedures. Missing → P2 citing C4.

**C5 — Alerting-fire scenarios for SLO breaches.** For every SLO declared
in EARS (latency p99, error-rate ceiling, availability target), the scenario
set must include at least one scenario that exercises the breach condition
and asserts the alert fires with the correct payload to the declared channel.
SLO alerting that is never exercised in the test suite cannot be relied upon
in production. Missing → P3 citing C5.

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
