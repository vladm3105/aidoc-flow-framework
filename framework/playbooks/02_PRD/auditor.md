---
layer: 02_PRD
lens: auditor
weight: 10
agent: traceability-auditor
framework_spec_version: "0.15.0"
---
# auditor lens — PRD layer

## Reasoning frame

The auditor lens applies conformance and traceability checks that are objective
and layer-invariant: are the required sections present, do the element IDs
follow the naming standard, do cross-references resolve, is the glossary
complete? At PRD altitude the auditor applies these checks against PRD-specific
element-ID patterns (`PRD.{doc}.{section}.{hash[:4]}`) and PRD-required
template sections. The auditor does not evaluate the quality of product decisions
— that is the product_owner's domain — but verifies that the document is
structurally complete enough for downstream layers to inherit it without
navigational or traceability ambiguity.

At BRD altitude the auditor validated BRD-specific IDs and sections. At PRD
altitude the ID pattern changes, the required sections change (§5 Success
Metrics, §9 Functional Requirements, §11 Acceptance Criteria, §12 NFRs, §13
Risks replace BRD sections), and `@brd:` cross-reference tags become a new
resolution requirement. At EARS altitude the auditor validates EARS-specific
requirement IDs and conformance sections. The auditor's role — structural
completeness, ID conformance, reference resolution — is constant across
layers; only the layer-specific vocabulary changes.

The auditor lens does NOT evaluate: whether the product scope matches BRD
intent (product_owner), whether diagrams are structurally coherent (architect),
whether gates are implementable (tech_lead), whether failure paths are covered
(chaos_engineer), or whether trust boundaries are authorized (security_engineer).
This lens asks only: "Is this PRD complete, navigable, and anchored to its
cross-layer references?"

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check citation
are out-of-scope and discarded by the synthesizer.

**C1 — `@brd:` tag resolution rate 100%.** Every `@brd:` cross-reference tag
in the PRD must resolve to an identifiable element in the cited BRD (section,
requirement, capability, or objective by ID). An unresolvable `@brd:` tag
breaks the downstream traceability chain and prevents automated linkage tools
from validating inheritance. Missing → P1 finding citing C1.

**C2 — PRD element-ID conformance.** Every identifiable element (functional
requirement, acceptance criterion, NFR, risk row, persona) must carry an ID
conforming to `PRD.{doc-slug}.{section-code}.{hash[:4]}` (or the
project-declared variant in ID_NAMING_STANDARDS). IDs that are missing,
duplicated, or pattern-nonconforming prevent the synthesizer from linking PRD
elements to downstream EARS requirements. Missing → P1 finding citing C2.

**C3 — Required template sections present.** The PRD template mandates a
defined set of sections. Every mandatory section must be present, even if
populated with "N/A — not applicable" and a rationale. Mandatory sections
include at minimum: §1 Overview, §2 Problem Statement, §3 Goals, §4 Non-Goals,
§5 Success Metrics, §6 Personas, §7 Scope, §8 User Stories, §9 Functional
Requirements, §10 User-Facing Surfaces, §11 Acceptance Criteria, §12 NFRs,
§13 Risks, §14 Glossary, §15 Document Control. Absent sections without
explicit N/A are not inferrable. Missing → P1 finding citing C3.

**C4 — Glossary covers PRD-introduced terms.** Every domain-specific or
PRD-specific term introduced in the document body must appear in §14 Glossary
with a definition scoped to this document's usage. Terms that appeared in the
BRD and carry the same meaning may be cross-referenced rather than redefined.
Missing → P3 finding citing C4.

**C5 — Self-claimed score not used as audit verdict.** If the PRD's §15
Document Control contains a self-assessed quality score, the auditor must flag
that this score must not be used as the synthesizer's verdict. The synthesizer
determines the audit verdict from the aggregated lens findings in `verdict.json`,
not from author-supplied assessments. Missing → P3 finding citing C5.

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
