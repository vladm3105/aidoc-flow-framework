---
layer: 01_BRD
lens: business_analyst
weight: 30
agent: requirements-analyst
framework_spec_version: "0.40.0"
---
# business_analyst lens — BRD layer

## Reasoning frame

The business_analyst lens is the drafter lens for the BRD layer. It owns the
document's content coherence: are the business objectives grounded in
stakeholder reality, do the stated personas match the capabilities being
defined, and is the scope boundary explicit enough to prevent requirements
creep at downstream layers? At BRD altitude the business_analyst focuses on
the *why* (business motivation) and the *who* (affected personas), not the
*how* (which is PRD territory).

At PRD altitude the product_owner lens displaces the business_analyst as the
primary drafter, shifting from business justification to capability
prioritisation within a time-boxed product increment. The business_analyst may
appear as a secondary reviewer at PRD but does not own that layer. At EARS the
requirements_specialist inherits the business_analyst's objective language and
refines it into atomic, verifiable acceptance conditions. The BRD
business_analyst lens therefore sets the quality floor that every downstream
layer must amplify, not redefine.

The BRD business_analyst lens does NOT evaluate: internal structural coherence
(architect), traceability ID conformance (auditor), reliability targets
(chaos_engineer), or security trust boundaries (security_engineer). Those lenses
apply their own checks independently. The business_analyst lens focuses on
whether the document faithfully captures business intent in terms observable by
a non-technical stakeholder and measurable by a post-launch analytics team.

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check citation
are out-of-scope and discarded by the synthesizer.

**C1 — Baseline + target on every business objective.** Each stated objective
must carry a current-state baseline ("today: X") and a numeric target at a
named time horizon (30-day, 60-day, 90-day, or explicit release milestone).
Objectives stated as directional aspirations without a baseline or a numeric
target are not verifiable. Missing → P1 finding citing C1.

**C2 — Persona-to-capability traceability.** Every capability declared in
§Scope or §Requirements must trace to at least one named persona in the
§Personas (or equivalent) section. Capabilities that serve no named persona
indicate scope inflation or an unnamed stakeholder. Missing → P2 finding
citing C2.

**C3 — Scope boundary explicit.** §Scope must state both inclusions and
exclusions. For each exclusion, a brief rationale must be given (cost,
regulatory, timeline, adjacent team ownership). An exclusion listed without
rationale is as ambiguous as no exclusion. Missing → P2 finding citing C3.

**C4 — Success metrics observable post-launch.** Each success metric must be
collectible from the running system or from an external source (NPS survey,
support ticket volume, revenue report). Metrics that require internal
assumptions, retrospective attribution, or unmeasured proxies are not
observable. Missing → P2 finding citing C4.

**C5 — Every requirement traces to a business motivator.** Each stated
requirement must link to at least one of: a named stakeholder ask (with
stakeholder identified), a regulatory obligation (with regulation cited), or
a named market driver. Requirements without a stated motivator risk scope
creep when contested in PRD. Missing → P3 finding citing C5.

**C6 — No requirement stated at implementation altitude.** Requirements at
BRD must describe business-level behaviour ("the system accepts N orders per
minute during peak") not implementation details ("the queue uses Redis Streams
with a 512 MB buffer"). Any requirement containing implementation vocabulary
belongs at PRD or SPEC. Missing → P2 finding citing C6.

**C7 — Document Control section complete.** §Document Control (or equivalent
header metadata) must include: document Owner (named individual or role),
Status (Draft/Review/Approved), Version, and Effective Date. An incomplete
Document Control block prevents governance routing and approval tracking.
Missing → P2 finding citing C7.

**C8 — Author the seed-disposition ledger.** When the cycle has a
`<project>/seed/` input, this BRD's `seed_disposition:` section must give
**every** claim the seed makes exactly one disposition (governance
`SEED_CONTRACT.md`, GD-08): `absorbed` names ≥1 BRD element ID from §Functional
Requirements that carries it; `rejected` gives a rationale; `deferred` gives a
rationale and a target cycle (and SHOULD also appear in §out_of_scope). Do
**not** edit the seed to resolve a finding — the seed is frozen historical
input; dispose the claim here. A seed claim first accounted for at PRD or later,
with no BRD row, is a gap. Missing/incomplete ledger → P2 finding citing C8.

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
