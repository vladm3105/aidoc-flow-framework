---
layer: 05_ADR
lens: operator
weight: 10
agent: devops-release-engineer
framework_spec_version: "0.36.0"
---
# operator lens — ADR layer

## Reasoning frame

The operator lens at ADR altitude evaluates whether the decision is
operable in production — whether it can be rolled out, observed,
sequenced with other deployments, sized for capacity, and toggled at
runtime when the design admits a toggle. ADRs frequently encode
commitments that the architect treats as design decisions but the
operator must execute as deployment events. An ADR that adopts a new
queue technology, switches a data store, or introduces a new boundary
crossing is also a deployment change; if the ADR is silent on rollout
and observability, the operator inherits an unscoped operational
exposure.

Rollback procedure matters most for two-way and reversible decisions.
A two-way decision (undoable with documented effort) without a written
rollback procedure is operationally equivalent to one-way during an
incident — the procedure that doesn't exist on paper won't be invented
under pressure at 03:00. A reversible decision (toggle at runtime)
without a written rollback procedure is theoretical reversibility;
the toggle exists but the operator doesn't know what to flip or what
state to expect after flipping. One-way decisions are exempt from
rollback documentation because the rollback path is "rebuild from
scratch," which is covered elsewhere.

Observability is the operator's window into whether the decision is
working as intended. An ADR that adopts a new architectural pattern
without naming the metric, log, or event that signals success or
failure in production commits the operator to operational blindness.
The metric must exist at the right altitude — adopting a new queue
technology requires queue-depth + dead-letter metrics, not just
CPU/memory. Detection-time matters too: the metric is useful only if
it surfaces faster than the consequence of the failure it detects.

Deployment ordering, capacity, and runtime knobs round out the lens.
A decision that sequences with others (e.g., must precede or follow
another ADR's rollout) must say so or the operator will discover the
sequence by failed deploys. A decision with non-trivial capacity or
cost impact must enumerate it at order-of-magnitude precision so
operations can plan. A toggleable decision (feature flag, profile,
runtime env) must declare the toggle in the ADR — operators should not
have to grep config files to learn what knobs exist.

This lens does NOT evaluate: decision integrity (architect),
implementability mechanics (tech_lead), trust boundaries
(security_engineer), upstream-tag conformance (auditor), or decision-
failure-mode coverage (chaos_engineer). The operator lens is confined
to rollout, observability, sequencing, capacity, and runtime
toggleability.

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check citation
are out-of-scope and discarded by the synthesizer.

**C1 — Rollback procedure described for reversible decisions.** When the
ADR's reversibility classification is two-way or reversible (per architect
lens C4), the ADR includes a written rollback procedure naming the steps
to undo the decision in production. One-way decisions are exempt. Missing
on a two-way or reversible decision → P2 citing C1.

**C2 — Observability hooks identified.** The ADR names the metric, log,
or event at the appropriate altitude that signals success or failure of
this decision in production. For an architecture change the metric must
match the architecture (queue depth + DLQ rate for queue adoption, not
just CPU/memory). For a control change the signal must surface faster
than the consequence it detects. Missing → P2 citing C2.

**C3 — Deployment ordering called out when sequenced.** When the decision
must precede or follow another ADR's rollout (or another team's deploy),
the ADR names the dependency explicitly. Implicit ordering is discovered
through failed deploys, which is an expensive teaching mechanism. Missing
when ordering matters → P3 citing C3.

**C4 — Capacity / cost impact enumerated.** When the decision has non-
trivial capacity or cost impact (new infrastructure component, increased
network or storage footprint, additional license cost), the ADR enumerates
the impact at order-of-magnitude precision so operations can plan capacity
and budget. Hand-wave ("modest increase") → P3 citing C4.

**C5 — Runtime config knob declared on toggleable decisions.** When the
decision admits a runtime toggle (feature flag, profile, env var), the
ADR declares the knob: name, possible values, default, and where it lives
(config file / env / feature-flag service). Operators should not have to
grep config to learn what knobs exist. Missing on toggleable decisions →
P3 citing C5.

## Beyond-checklist

If you find an operational failure mode the checklist does not cover, raise
it as a P2/P3 finding citing `beyond-checklist:<principle-tag>` and state
which paragraph of the reasoning frame motivates it. Common beyond-
checklist cases at ADR: deploy-time-fragility (the decision implies a
deploy that breaks on a common transient condition), oncall-onramp gap
(the decision changes the incident response surface in ways the runbook
does not cover yet), or budget-cliff (the decision is cheap until a
discrete threshold and then expensive). Use sparingly. If more than 30%
of your findings are beyond-checklist, the playbook needs revision (file
a follow-up).

## Scoring

| Outcome | lens_score |
|---|---|
| No findings; every check ran clean | 100 |
| P3 findings only; no checklist holes | 90-99 |
| 1-2 P2 findings against checks; no P1 | 80-89 |
| 3+ P2 against checks OR 1 P1 | 70-79 |
| P0 present OR systemic checklist failure | < 70 |
