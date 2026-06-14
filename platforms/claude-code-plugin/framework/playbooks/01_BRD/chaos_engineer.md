---
layer: 01_BRD
lens: chaos_engineer
weight: 12
agent: chaos-engineer
framework_spec_version: "0.21.1"
---
# chaos_engineer lens — BRD layer

## Reasoning frame

The chaos_engineer lens at BRD altitude reviews reliability at
business-outcome altitude: does the document commit to the resilience posture
the business needs, or does it silently defer that commitment to PRD or SPEC
where the cost of reversal is higher? The BRD is the correct place to declare
availability targets, durability classes, and recovery expectations because
those commitments constrain capability architecture and must be known before
structural decisions are locked in at PRD.

At PRD altitude the chaos_engineer lens shifts downward to failure-path
acceptance criteria: which failure modes must be covered by scenarios in the
PRD's acceptance criteria, and do those criteria include degraded-mode
behaviour. At SPEC altitude the lens becomes component-level: which component
owns fault detection, isolation, and recovery, and what are the fault-injection
test conditions. The BRD chaos_engineer lens does not ask those questions — it
asks only whether the business has made its resilience commitments visible.

The BRD chaos_engineer lens does NOT evaluate: whether failure-mode scenarios
are specified (qa_lead at BDD/EARS), whether implementation fault-isolation is
correct (tech_lead at SPEC), or whether recovery procedures are documented
(operator). The lens confines itself to the business-facing reliability
commitments that the BRD should carry.

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check citation
are out-of-scope and discarded by the synthesizer.

**C1 — Reliability NFRs declared at BRD altitude.** The document must
explicitly state at least one availability target (e.g., "99.9% measured over
a 30-day rolling window") and at least one durability target (e.g., "zero data
loss on confirmed writes") for each critical capability. If the BRD explicitly
defers these to an ADR with a named ADR reference slot, that is acceptable; a
silent omission is not. Missing → P1 finding citing C1.

**C2 — Capacity bounds named or explicitly deferred.** Each critical capability
must name its expected load envelope (peak events per second, maximum concurrent
users, maximum payload size) or explicitly defer the bound to an ADR or capacity
plan with a named reference. An unconstrained capability is an unbounded growth
assumption that surfaces as a reliability failure at scale. Missing → P2 finding
citing C2.

**C3 — Degraded-mode behaviour named per critical capability.** For each
capability the business considers critical, the document must state what
the system commits to when that capability is partially unavailable. The
commitment must be expressed at business altitude: "when X fails, the
business accepts Y for up to Z minutes" — not an implementation workaround.
Missing → P2 finding citing C3.

**C4 — Recovery SLAs declared at business-commitment level.** RPO (Recovery
Point Objective) and RTO (Recovery Time Objective) must be stated for any
capability that manages persistent state or customer-visible commitments.
These are business commitments, not implementation choices, and belong at BRD
altitude. If the BRD explicitly defers these to an ADR with a named slot,
that is acceptable. Missing → P2 finding citing C4.

**C5 — Capacity-exhaustion response declared.** Where a capability has a
named capacity bound (from C2), the document must state the business-facing
response when that bound is reached: queue and shed, degrade gracefully, reject
with a specific error, alert the operations team. A named bound with a "TBD"
response is incomplete. Missing → P3 finding citing C5.

**C6 — Dependency reliability assumptions explicit.** If a capability depends
on a named external service or upstream system, the reliability assumption for
that dependency must be stated (e.g., "assumes S3 availability ≥ 99.99%").
Unacknowledged dependency assumptions are invisible failure modes at BRD
altitude. Missing → P2 finding citing C6.

## Beyond-checklist

If you find a layer-specific failure mode the checklist does not cover, raise
it as a P2/P3 finding citing `beyond-checklist:<principle-tag>` and state
which paragraph of the reasoning frame above motivates it. Use sparingly. If
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
