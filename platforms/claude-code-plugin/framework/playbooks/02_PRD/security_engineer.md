---
layer: 02_PRD
lens: security_engineer
weight: 7
agent: security-engineer
framework_spec_version: "0.47.0"
---
# security_engineer lens — PRD layer

## Reasoning frame

The security_engineer lens at PRD altitude evaluates trust boundaries and
abuse-surface definition. It asks: does the PRD authorize every security control
it introduces against a BRD-granted permission, and does it bound the attack
surface with enough specificity that EARS and SPEC can derive concrete defensive
requirements without making security judgement calls? At BRD altitude this lens
reviewed whether the business acknowledged its threat surface. At PRD altitude
it descends to container-level trust boundaries and the data-classification
distinctions that govern what each container may see and store.

At SPEC altitude the security_engineer lens narrows to component-level: cipher
suites, key-rotation intervals, and access-control list schemas. At PRD the
lens operates at container boundary: which service crosses which trust boundary,
which data class flows across that boundary, and is the crossing authorized.
The PRD is the correct altitude to declare TOCTOU windows, abuse-mitigation
layering, and enumeration-defense strategies because those commitments constrain
container design before implementation locks them in.

The security_engineer lens does NOT evaluate: BRD-authorization of product
scope (product_owner), diagram reconciliation (architect), input-type bounds
(tech_lead), failure-path gating (chaos_engineer), or structural conformance
(auditor). This lens is confined to trust boundaries, authorization chains, and
abuse-surface layering.

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check citation
are out-of-scope and discarded by the synthesizer.

**C1 — Trust-boundary BRD authorization.** Every container-level trust boundary
introduced in the PRD (a new service exposed to the internet, a new
authenticated endpoint, a new data egress path) must trace to a BRD-authorized
capability or objective. A trust boundary that appears in the PRD without a BRD
anchor is unauthorized scope expansion from a security governance perspective.
Missing → P1 finding citing C1.

**C2 — Abuse-mitigation SLA or ADR-deferral.** Every §13 abuse-risk row must
carry either a takedown SLA (e.g., "malicious-link takedown within 24 h of
report") or an explicit ADR-deferral marker. A named abuse risk with no SLA and
no deferral leaves the response commitment undefined, which is a governance gap.
Missing → P2 finding citing C2.

**C3 — TOCTOU window addressed.** Where the PRD specifies screen-at-submit
behaviour (validate a resource at creation time), it must also address what
happens when that resource later becomes malicious. A screen-at-submit control
without a post-submission re-evaluation strategy or explicit deferral creates
a TOCTOU gap that grows over the link's lifetime. Missing → P3 finding citing C3.

**C4 — Per-artifact data classification.** Every distinct data artifact managed
by the system (e.g., visit-count aggregates, link-destination store, PII) must
carry an explicit data-classification label. Treating multiple data artifacts
under a single classification label obscures which controls apply to which
store, and may allow over-permissive access. Missing → P2 finding citing C4.

**C5 — Enumeration defense layered.** Where the PRD introduces a public lookup
surface (e.g., short-code resolution, link metadata access), the defense against
enumeration and scraping must specify at least two independent control layers.
A single-control defense (rate-limiting alone, or authentication alone) is a
single point of bypass. Missing → P3 finding citing C5.

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
