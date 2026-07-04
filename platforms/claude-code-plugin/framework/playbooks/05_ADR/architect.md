---
layer: 05_ADR
lens: architect
weight: 35
agent: solutions-architect
framework_spec_version: "0.32.7"
---
# architect lens — ADR layer

## Reasoning frame

The architect lens at ADR altitude is the dominant axis (weight 35) and
also serves as the document's author. An ADR captures a discrete
architectural decision — a single commitment that constrains downstream
SPEC, TDD, and Code, and that will be defended against future challenges.
The architect lens evaluates whether the decision is stated with enough
precision to bind implementers, whether the rejected alternatives are
named and rejected for stated reasons, and whether the trade-offs are
explicit enough that a future reader can re-evaluate the decision when
context changes.

A well-formed ADR survives the test of "would I have made this decision
if I had read only the ADR and its upstream BRD/PRD/EARS?" The decision
statement must be a single imperative sentence — not a paragraph of
prose mixing motivation with commitment, not a list of considerations.
Alternatives Considered must enumerate at least two distinct alternatives,
each with a one-paragraph reject rationale that names the concrete factor
that disqualified it. Trade-offs must explicitly state what the decision
gains AND what it gives up; an ADR that only enumerates wins is a
sales pitch, not a decision record. Reversibility must be classified
because the cost of being wrong depends on whether the decision can be
undone. The boundary crossed by the decision — service / module /
component / data — must be named because the decision's blast radius
is bounded by that boundary.

This lens does NOT evaluate: implementability mechanics (tech_lead),
trust-boundary security (security_engineer), rollback procedure
(operator), upstream-tag conformance (auditor), or decision-failure-
mode coverage (chaos_engineer). The architect lens is confined to
decision integrity and alternatives rigor.

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check citation
are out-of-scope and discarded by the synthesizer.

**C1 — Decision statement is a single-sentence imperative.** The ADR's
Decision section opens with one sentence in the form "THE `<subject>` SHALL
`<verb> <object>` `<for-clause>`" or close equivalent. A decision statement
that spans multiple sentences, mixes motivation with commitment, or hedges
("we will probably" / "consider adopting") leaves the commitment ambiguous;
two readers can disagree on what was decided. Diffuse / multi-clause →
P1 citing C1.

**C2 — Alternatives Considered enumerates ≥2 with reject rationale.**
The Alternatives Considered section names at least two distinct alternatives
that were evaluated before the chosen path. Each alternative carries a
one-paragraph rationale naming the concrete factor that disqualified it
(cost, latency, complexity, vendor lock-in, etc.). A single alternative
or a stub rationale ("not chosen for technical reasons") means future
readers cannot re-evaluate the decision when the disqualifying factor
changes. Missing alternative or stub rationale → P1 citing C2.

**C3 — Trade-offs explicit (gains AND gives-up).** The Trade-offs section
names both what the decision wins and what it loses. An ADR that lists
only the wins ("better performance, lower cost, simpler ops") is a sales
pitch, not a decision record. Future readers need both sides to judge
whether the trade-off still makes sense. Implicit-only or wins-only →
P2 citing C3.

**C4 — Reversibility classification present.** The ADR explicitly labels
the decision as one-way (cannot be undone without rebuild), two-way
(undoable with documented effort), or reversible (toggle at runtime).
The reversibility class drives operator's rollback-procedure check and
chaos_engineer's mitigation-pre-built check. Without it, downstream
lenses cannot evaluate whether their checks apply. Missing → P2 citing C4.

**C5 — Boundary crossed called out.** The ADR names the boundary
the decision crosses (service / module / component / data domain).
A decision's blast radius is bounded by the boundary it crosses, and
the boundary determines which other teams or systems need to coordinate.
A decision with no named boundary leaves the impact scope undefined.
Missing → P3 citing C5.

## Beyond-checklist

If you find a decision-integrity failure mode the checklist does not cover,
raise it as a P2/P3 finding citing `beyond-checklist:<principle-tag>` and
state which paragraph of the reasoning frame motivates it. Common
beyond-checklist cases at ADR: hidden assumption (commitment depends
on an unstated premise), missing decision driver (no named goal/constraint
that this decision serves), or scope creep (the ADR commits to more than
its title suggests). Use sparingly. If more than 30% of your findings are
beyond-checklist, the playbook needs revision (file a follow-up).

## Scoring

| Outcome | lens_score |
|---|---|
| No findings; every check ran clean | 100 |
| P3 findings only; no checklist holes | 90-99 |
| 1-2 P2 findings against checks; no P1 | 80-89 |
| 3+ P2 against checks OR 1 P1 | 70-79 |
| P0 present OR systemic checklist failure | < 70 |
