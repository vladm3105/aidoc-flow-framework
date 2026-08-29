---
layer: 05_ADR
lens: tech_lead
weight: 25
agent: solutions-architect
framework_spec_version: "0.46.0"
---
# tech_lead lens — ADR layer

## Reasoning frame

The tech_lead lens at ADR altitude evaluates whether the decision is
implementable as written and whether it sits consistently in the
decision graph. An ADR is not merely a record of intent — it constrains
the SPEC that follows, must be reachable from the BRD/PRD/EARS that
precede it, and must not contradict prior ADRs. The tech_lead's job is
to catch decisions whose adoption mechanics are unspecified, decisions
that contradict an upstream constraint, decisions that leave downstream
SPEC/TDD with no clear interpretation, decisions that lack a migration
path when reversibility is non-trivial, and decisions that conflict
with or silently supersede a prior ADR.

Implementability at ADR altitude differs from implementability at SPEC
or Code altitude. An ADR is implementable when an engineer reading it
can map the commitment to concrete architectural primitives — a module
boundary, a protocol choice, a queue topology — without inferring
unstated context. An ADR that says "adopt event-driven communication"
without naming the queue technology, delivery semantics, or boundary
where the event crosses is not implementable; it is aspiration. The
lens flags such gaps as P1 because they push the decision into the
SPEC phase, where the SPEC author lacks the architectural context the
ADR was meant to provide.

Consistency at ADR altitude runs two directions. Upstream consistency
requires that the ADR not contradict any BRD/PRD/EARS line — a decision
that adopts an architecture incompatible with a BRD constraint is a
defect, not a trade-off. Cross-ADR consistency requires that the new
ADR either align with prior ADRs or explicitly supersede them via a
named cross-reference. Silent contradiction between ADRs leaves the
decision graph inconsistent and downstream code must guess.

This lens does NOT evaluate: decision integrity / alternatives
(architect), trust-boundary security (security_engineer), rollback
procedure (operator), upstream-tag conformance (auditor), or decision-
failure-mode coverage (chaos_engineer). The tech_lead lens is confined
to implementability and consistency.

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check citation
are out-of-scope and discarded by the synthesizer.

**C1 — Decision implementable as written.** A SPEC author reading only the
ADR + its upstream layers must be able to identify the concrete architectural
primitives the decision commits to (queue technology, delivery semantics,
protocol choice, module boundary, etc.) without inferring unstated context.
Ambiguity that pushes architectural choice into the SPEC phase is a P1
because the SPEC author lacks the architectural context the ADR was meant
to provide. Ambiguous adoption mechanics → P1 citing C1.

**C2 — Upstream BRD/PRD/EARS constraints satisfied.** The decision must
not contradict any explicit constraint from the BRD, PRD, or EARS that
this ADR claims to descend from. A decision that adopts an architecture
incompatible with an upstream constraint is a defect, not a trade-off:
either the constraint must be lifted (separate change-management
request) or the decision must change. Contradicts upstream → P1 citing C2.

**C3 — Downstream impact on SPEC + TDD enumerated.** The ADR explicitly
states what the SPEC must encode as a consequence of this decision and
what the TDD must verify. An ADR that commits to a queue topology without
saying which SPEC sections it constrains or which TDD scenarios must cover
the new delivery semantics leaves the downstream layers to discover the
impact through trial and error. Missing → P2 citing C3.

**C4 — Migration path described when reversibility ≠ one-way.** For
two-way and reversible decisions the ADR describes how to move from the
current state to the adopted state without service interruption — feature
flags, dual-write windows, schema migrations, rollback gates. A two-way
or reversible decision without a migration path is operationally
equivalent to one-way; the ability to reverse is theoretical. Missing
path on reversible decisions → P2 citing C4.

**C5 — Cross-ADR consistency check.** The ADR enumerates any prior ADR
that it conflicts with, supersedes, or is superseded by, using the
correct `@adr:` reference form. Silent contradiction between ADRs leaves
the decision graph inconsistent. A new ADR that quietly replaces a prior
one without naming the supersession leaves implementers reading both
documents and inferring the resolution. Missing cross-ref → P3 citing C5.

## Beyond-checklist

If you find an implementability or consistency failure mode the checklist
does not cover, raise it as a P2/P3 finding citing
`beyond-checklist:<principle-tag>` and state which paragraph of the
reasoning frame motivates it. Common beyond-checklist cases at ADR:
hidden coupling (the decision implies a coupling to another component
that is not stated), tech-debt amplifier (the decision adopts a pattern
known to compound technical debt), or premature commitment (the decision
binds the architecture before requirements stabilise). Use sparingly. If
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
