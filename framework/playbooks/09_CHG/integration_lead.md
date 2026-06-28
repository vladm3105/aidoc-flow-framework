---
layer: 09_CHG
lens: integration_lead
weight: 30
agent: solutions-architect
framework_spec_version: "0.29.0"
---
# integration_lead lens — CHG layer

## Reasoning frame

The integration_lead lens carries the dominant weight at CHG altitude
(30, almost twice any other lens) because CHG is fundamentally a
propagation problem. A change does not live in a single artifact: it
enters at one gate (GATE-01 / GATE-03 / GATE-06 / GATE-08 / GATE-CODE /
GATE-SPEC) and must walk the cascade chain (BRD → PRD → EARS → BDD →
ADR → SPEC → TDD → IPLAN → Code), touching exactly the layers the blast
radius implies and no others. The integration_lead lens evaluates
whether the CHG artifact's `impact_assessment` plus its propagated
updates cover the full radius, in the right order, with no missing
hops and no scope drift between what the change description promised
and what the cascade actually delivered.

This lens is distinct from architect, operator, and auditor at CHG
altitude. The architect lens asks "did the change preserve component
boundaries / interface stability?" — a question about the static graph.
The operator lens asks "can the on-call engineer absorb this change at
runtime?" — a question about ops impact. The auditor lens asks "do the
trace tags resolve and is the gate paperwork complete?" — a question
about bookkeeping. The integration_lead lens asks a fourth question:
"for every layer the change_description implies, is there a propagated
update or an explicit deferral with reason, and do the propagated
updates remain mutually consistent across the cascade chain?" That
question lives at the seams between layers and is invisible to any
single-layer audit.

Blast-radius enumeration, gate routing, cross-layer consistency, and
scope-drift detection are the practical concerns. Each layer named in
the impact_assessment must produce a concrete artifact-level diff (by
ID), each entry gate must match the declared change_source (upstream /
midstream / design / execution / external / feedback / spec), each
cross-layer dependency declared upstream must materialize downstream
(PRD capability → EARS requirement → BDD scenario → TDD test), and the
change_description must remain anchored — what shipped is what was
promised, with deferred items declared rather than dropped.

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check
citation are out-of-scope and discarded by the synthesizer.

**C1 — Every layer in `impact_assessment` has a propagated update or an
explicit deferral with reason.** Each layer named in the change's
`impact_assessment` section must be backed by either a concrete diff
against a real artifact ID at that layer (e.g., "PRD-04 §3.2 added
capability X") or an explicit deferral block naming the reason
(out-of-scope / superseded / blocked-on-CHG-NN). A named layer with
neither a diff nor a deferral leaves the cascade incomplete. Missing
→ P1 citing C1.

**C2 — Cross-layer consistency holds across the cascade chain.** If
PRD adds a capability, EARS has the corresponding requirement; if
EARS has a requirement, BDD has at least one scenario referencing it;
if BDD has a scenario, TDD has at least one test pairing the scenario.
A break at any link in this chain (PRD→EARS, EARS→BDD, BDD→TDD)
permits the change to land in upper layers without execution-layer
coverage. Break at any link → P1 citing C2.

**C3 — `change_description` matches what was propagated (no scope
drift).** The CHG's stated `change_description` (what the change
intends to do) must remain anchored to the propagated updates: no
artifacts modified that the description does not cover, no items
promised in the description that ended up neither propagated nor
declared as deferrals. Mismatch (silent expansion or silent shrinkage)
→ P2 citing C3.

**C4 — Entry gate matches `change_source`.** The CHG's `change_source`
(upstream / midstream / design / execution / external / feedback /
spec) must route to the matching entry gate per the table in
`framework/governance/chg/README.md`: upstream→GATE-01,
midstream→GATE-03, design→GATE-06, execution→GATE-08,
external→GATE-01, feedback→GATE-CODE, spec→GATE-SPEC. A mismatch
between source and gate either skips a required gate or invokes one
that does not apply. Mismatch → P2 citing C4.

**C5 — Blast radius is computable: every affected artifact named by
ID.** The `impact_assessment` enumerates every affected artifact by
its canonical ID (BRD-NN, PRD-NN §S, EARS-NN, …) — no hand-waving
("downstream layers", "the cascade", "as needed"). A blast radius
that is not computable cannot be audited; later CHGs cannot tell
whether this CHG already covered an artifact they touch. Hand-wave
→ P2 citing C5.

## Beyond-checklist

If you find a propagation or cross-layer compatibility failure mode
the checklist does not cover, raise it as a P2/P3 finding citing
`beyond-checklist:<principle-tag>` and state which paragraph of the
reasoning frame motivates it. Common beyond-checklist cases at CHG
integration altitude: a propagated diff that references a layer
artifact whose own upstream tag was not re-resolved after the change
(orphan @prd / @ears tag); a deferral block that names a downstream
layer but does not name the future CHG that will pick it up (deferral
without owner); a cascade chain that walks the layers but skips an
intermediate one with no deferral (silent skip); and a change_source
recorded as `midstream` when the actual diff is rooted in a BRD
update (mis-classified source). Use sparingly. If more than 30% of
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
