---
layer: 09_CHG
lens: operator
weight: 15
agent: devops-release-engineer
framework_spec_version: "0.38.0"
---
# operator lens — CHG layer

## Reasoning frame

The operator lens at CHG altitude (weight 15, elevated above the
typical 10) reflects that a change to a running system imposes an
operational burden whether the CHG acknowledges it or not. The
on-call engineer who picks up the page at 2am after the change
lands needs three things: a runbook entry that describes the new
behavior, telemetry (dashboard / alert / metric) that lets them see
what happened, and a deployment record that tells them when the
change went out and how to recognize the canary phase. The operator
lens evaluates whether the CHG produced those three things, or
explicitly stated why they are not needed.

Runbook coverage is the central concept. Every component the change
modifies is governed by some operational runbook — the document the
on-call uses when an alert fires. A CHG that introduces new behavior
without updating the runbook leaves the on-call decoding the new
behavior from the diff under time pressure. The CHG must name the
runbook entries that are added, modified, or retired by the change,
or explicitly declare "runbook unaffected" with reason.

Observability and deployment posture are the remaining pillars. A
change that introduces a new component, new branch, or new failure
mode must declare what telemetry (dashboard, alert, metric, log
event) lets the operator see whether the new behavior is healthy.
Removing or hiding an existing operational signal (a metric the
on-call relied on, an error code that classified an incident) is a
silent degradation of the system's observability posture and must
be called out. The deployment-impact statement (canary plan, smoke
checks, capacity/cost implications) is the final piece: the operator
must know what the rollout looks like and what runtime cost the
change implies.

This lens does NOT evaluate: propagation completeness (integration_
lead), component-boundary preservation (architect), rollback /
emergency-path (chaos_engineer), trace-tag conformance (auditor), or
threat-model delta (security_engineer). The operator lens is
confined to runbook, observability, deployment plan, operability
degradation, and runtime-cost posture.

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check
citation are out-of-scope and discarded by the synthesizer.

**C1 — Runbook update plan declared.** The CHG names the on-call
runbook entries that are added, modified, or retired by the change,
or explicitly declares "no runbook impact" with reason. A change
that introduces new behavior with no runbook entry forces the
on-call to decode the new behavior from the diff under incident
time pressure. Missing → P2 citing C1.

**C2 — Observability declared for changed components (dashboards /
alerts / metrics).** When the CHG introduces a new component, a new
failure mode, or a new branch in a hot path, it names the
dashboards, alerts, and/or metrics that let the operator see the
new behavior. A change that adds runtime surface with no telemetry
makes the new behavior invisible until something breaks. Missing →
P2 citing C2.

**C3 — Deployment impact: deployment-time, canary plan, smoke checks
stated.** The CHG declares whether a deployment is required (and if
so, what the canary plan is — percentage rollout, bake time, abort
threshold) and what smoke checks gate the canary-to-full transition.
A change marked "no deploy required" must justify that claim (config
flip on already-deployed code, doc-only, etc.). Missing → P2 citing
C3.

**C4 — No silent operability degradation.** The CHG explicitly calls
out any reduction in operational signal: a removed metric, a hidden
error code, a collapsed log level, a renamed alert. Silent
degradation of operability is a regression the on-call cannot
detect from the diff and only discovers when an incident's familiar
signal does not arrive. Silent degradation → P2 citing C4.

**C5 — Runtime cost / capacity impact stated.** The CHG states the
capacity or cost implications of the change: additional CPU /
memory / IO / egress / storage / external-API spend, or "no runtime
cost impact" with reason. An unstated cost impact lets a change
land that doubles a workload's spend or saturates a capacity
envelope with no signal. Missing → P3 citing C5.

## Beyond-checklist

If you find an operability failure mode the checklist does not
cover, raise it as a P2/P3 finding citing
`beyond-checklist:<principle-tag>` and state which paragraph of the
reasoning frame motivates it. Common beyond-checklist cases at CHG
operator altitude: a canary plan whose abort threshold is named but
whose detection signal is not (cannot abort what you cannot
detect); a runbook entry referenced by name but not by URL / path
(operator has to guess where it lives); a new metric declared
without naming its retention / cardinality (silent cost regression
in the metrics backend); and a "no deploy required" justification
that depends on a feature flag whose default state is not declared.
Use sparingly. If more than 30% of your findings are beyond-
checklist, the playbook needs revision (file a follow-up).

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
