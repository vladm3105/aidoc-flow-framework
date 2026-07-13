---
layer: 08_IPLAN
lens: tech_lead
weight: 30
agent: solutions-architect
framework_spec_version: "0.37.2"
---
# tech_lead lens — IPLAN layer

## Reasoning frame

The tech_lead lens at IPLAN altitude is the dominant axis (weight 30)
and also serves as the document's author. An IPLAN document is the
deploy-and-rollback procedure that lands a SPEC-and-TDD-approved change
into a running environment. It is procedural — a sequence of cutover
steps, smoke gates, canary windows, and rollback branches — and it is
the last document before the change touches production. The tech_lead
lens evaluates the reversibility and determinism of that procedure:
whether every step that moves the system forward has a matching step
that moves it back, whether cutover decisions are encoded as named
metrics and thresholds rather than operator judgment, and whether the
phase transitions read as a deterministic state machine rather than a
narrative.

Reversibility is the first concern. Every deploy step that mutates
state (a schema migration, a config rotation, a traffic shift, a
feature-flag flip) must be paired with a rollback step that returns
the system to its prior state. Unpaired forward steps create
one-way doors that the operator discovers mid-incident — exactly
when the system can least afford an irreversible decision. The
pairing must be explicit, not implied by "revert the previous step";
the rollback step has its own preconditions, its own command, and
its own success signal.

Decision determinism is the second concern. Cutover criteria like
"if metrics look good, proceed" defeat the IPLAN's purpose: any two
operators reading the same metrics may disagree on what counts as
"good." Every cutover decision must name the metric and the
threshold (p95 latency below X ms over Y-minute window, error-rate
below Z%, saturation below W%). Phase boundaries must declare
pre-conditions (what must be true to enter) and post-conditions
(what must be true to exit), and time-bound gates (smoke window,
canary duration, rollback SLA) must carry concrete numbers.

This lens does NOT evaluate: topology invariance vs the upstream
ADR/SPEC (architect), smoke-test / observability emission (operator),
cross-service contract pinning (integration_lead), upstream-trace
conformance (auditor), or rollback dress-rehearsal practice
(chaos_engineer). The tech_lead lens is confined to the deploy-
sequence's reversibility and decision determinism.

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check
citation are out-of-scope and discarded by the synthesizer.

**C1 — Every deploy step has a documented rollback step (paired).**
Each forward step that mutates state has a matching rollback step
with its own preconditions, command, and success signal. Implicit
"revert step N" is not a rollback step; the operator running the
rollback mid-incident must not have to derive it. Missing pair → P1
citing C1.

**C2 — Cutover decision criteria are explicit (named metric +
threshold).** Every cutover decision names the metric (p95 latency,
error rate, saturation, queue depth) and the threshold value plus the
observation window. Criteria of the form "use judgment" or "if the
system looks healthy" leave the procedure non-reproducible. Missing
→ P1 citing C2.

**C3 — Phase boundaries declare pre-conditions and post-conditions.**
Each phase boundary names the conditions that must hold to enter the
phase and the conditions that must hold to exit. Phases without
entry/exit conditions cannot be audited mid-cutover. Missing → P2
citing C3.

**C4 — Time-bound gates carry concrete numbers.** Smoke window,
canary duration, rollback SLA, and similar time-bound gates carry
specific values (a 10-minute smoke window, a 30-minute canary, a
5-minute rollback SLA). "Brief" and "extended" are not bounds.
Missing → P2 citing C4.

**C5 — State transitions are deterministic.** Transitions between
deploy phases follow a fixed state machine; branching on "operator
discretion" is not a transition. The operator may abort, but the
forward and rollback paths must be deterministic given the named
inputs. Missing → P3 citing C5.

## Beyond-checklist

If you find a reversibility or decision-determinism failure mode the
checklist does not cover, raise it as a P2/P3 finding citing
`beyond-checklist:<principle-tag>` and state which paragraph of the
reasoning frame motivates it. Common beyond-checklist cases at IPLAN
deploy-sequence altitude: an irreversible operation (a hard schema
DROP, a credential rotation, an outbound webhook to a third party)
buried mid-sequence behind several reversible steps so its one-way
nature is hard to spot; a cutover step whose rollback procedure
exists but lives in a separate runbook or ADR rather than alongside
the forward step, breaking the operator's mid-incident lookup; and a
time-bound gate whose pass criterion is a vague phrase
("metrics stable", "no alerts firing") rather than a concrete
threshold over a concrete window. Use sparingly. If more than 30% of
your findings are beyond-checklist, the playbook needs revision (file
a follow-up).

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
