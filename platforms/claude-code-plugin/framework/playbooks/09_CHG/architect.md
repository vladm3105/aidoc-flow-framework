---
layer: 09_CHG
lens: architect
weight: 20
agent: solutions-architect
framework_spec_version: "0.29.1"
---
# architect lens — CHG layer

## Reasoning frame

The architect lens at CHG altitude (weight 20, second after
integration_lead) carries the structural-preservation concern: a
change to existing artifacts must not silently erode the topology,
the component boundaries, or the interface contracts that the
affected ADRs and SPECs already committed the system to. A CHG that
mutates a SPEC capability without touching the corresponding ADR
implicitly re-decides the decision; a CHG that introduces a new
component without producing a new ADR commits the system to a
boundary the architecture record does not show; a CHG that changes
an interface signature without versioning the contract leaves
downstream consumers on an old shape.

Component boundaries are the central concept. Every ADR fixes a
slice of the topology — what is a service, what is a library, what
the trust boundaries are, what data flows where. A CHG that touches
the artifacts those ADRs govern must either preserve those slices
(no boundary impact, reason recorded) or amend the ADR (boundary
changed, decision re-stated). The CHG that does neither leaves the
system in a state where the ADR record and the propagated SPEC/code
no longer agree, and future ADR consumers cannot tell which is
authoritative.

Interface stability and backward compatibility are the remaining
pillars. A change that mutates a contract (signature, schema, error
code, status, header semantic) must either preserve the existing
shape (additive only, deprecation declared) or version the contract
explicitly so consumers can pin. A change that silently re-shapes a
contract is indistinguishable to consumers from a partial outage:
existing calls fail in new ways with no signal that the producer
intended the failure. The architect lens evaluates whether the CHG
declares its compatibility implications rather than leaving them
implicit.

This lens does NOT evaluate: propagation completeness across the
cascade (integration_lead), rollback procedure (chaos_engineer),
runbook/observability impact (operator), trace-tag conformance
(auditor), or threat-model delta (security_engineer). The architect
lens is confined to component-boundary preservation, ADR coverage
for new structure, contract versioning, SPEC coverage, and
backward-compatibility declarations.

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check
citation are out-of-scope and discarded by the synthesizer.

**C1 — Change preserves component boundaries from affected ADRs.**
For every ADR named in `impact_assessment`, the CHG either preserves
the component boundaries that ADR fixes (boundary-impact: none,
rationale stated) or proposes an ADR amendment alongside. A CHG that
touches an ADR-governed artifact without preserving or amending the
ADR silently re-decides the decision. Missing → P1 citing C1.

**C2 — New components require a new ADR.** When the CHG introduces a
new component (service, library, scheduled job, queue, external
integration) that does not appear in any current ADR, the CHG names
the new ADR-NN that will codify the decision (or includes it inline
under the impact_assessment with a draft state). A new component
introduced without an ADR commits the system to a structural
decision with no decision record. Missing → P1 citing C2.

**C3 — Interface stability: existing contracts preserved or
versioned.** When the CHG mutates a contract (API signature, schema
field, error code semantic, RPC method, event payload), it either
keeps the existing shape additively (no removed/renamed/retyped
fields) or declares a new contract version with a deprecation
window for the old shape. A silent in-place mutation breaks
consumers without warning. In-place mutation → P1 citing C3.

**C4 — SPEC update declared when behavior or contract shifts.** When
the CHG mutates a behavior or contract that an active SPEC encodes,
the CHG names the SPEC-NN section that must be updated (or already
shows the diff). A behavior shift without a SPEC update leaves the
SPEC out-of-sync with the system, and downstream TDD/IPLAN drift
follows. Missing → P2 citing C4.

**C5 — Backward compatibility implications explicitly stated.** The
CHG names whether the change is backward-compatible (additive only,
no consumer action), backward-compatible-with-migration (consumers
have a deprecation window), or breaking (consumers must change in
lockstep). An unstated compatibility posture forces every consumer
to re-discover the implications from the diff. Missing → P2 citing
C5.

## Beyond-checklist

If you find a structural-preservation failure mode the checklist
does not cover, raise it as a P2/P3 finding citing
`beyond-checklist:<principle-tag>` and state which paragraph of the
reasoning frame motivates it. Common beyond-checklist cases at CHG
architect altitude: an ADR amendment that flips the decision rather
than evolving it (silent reversal); a new component declared without
naming whether it is in-process, out-of-process, or external (trust-
boundary class implicit); a contract version bump that does not
declare which version the producers ship at deploy time (version
introduced but not pinned); and a SPEC update that adds a capability
not traceable to any upstream PRD/EARS change (orphan capability).
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
