---
layer: 02_PRD
lens: product_owner
weight: 30
agent: requirements-analyst
framework_spec_version: "0.31.0"
---
# product_owner lens — PRD layer

## Reasoning frame

The product_owner lens at PRD altitude is the primary authoring perspective.
It asks whether the PRD faithfully translates BRD-authorized requirements into
product decisions — scoped features, measurable success metrics, and acceptance
criteria that gate the launch decision — without inventing requirements the BRD
never authorized. The product_owner holds accountability for scope integrity: no
feature enters §9 (Functional Requirements) or §11 (Acceptance Criteria) unless
a BRD authorization can be cited, and no §11 gate exists without a traceable BRD
parent.

At BRD altitude the product_owner lens is not yet present; BRD uses a
business_analyst lens to validate objectives and personas. At PRD altitude the
product_owner becomes the primary author lens, responsible for the completeness
and internal consistency of the product definition. At EARS altitude the
product_owner recedes; the qa_lead and tech_lead take precedence for
requirement-level testability. The product_owner's PRD obligation is to leave
EARS with a definition precise enough that requirement authors need no product
judgement calls.

The product_owner lens does NOT evaluate: container coherence or diagram
reconciliation (architect), implementation measurability (tech_lead), failure-path
coverage (chaos_engineer), trust-boundary authorization (security_engineer), or
structural conformance (auditor). This lens confines itself to scope fidelity,
metric quality, AC completeness, and BRD-traceability of launch gates.

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check citation
are out-of-scope and discarded by the synthesizer.

**C1 — Launch-gate BRD authorization.** Every §11 acceptance criterion that
functions as a launch gate must trace to a BRD-authorized requirement or BRD
capability. A gate introduced at PRD without a BRD anchor (e.g., a rate-limiting
gate added where BRD only authorized screening and takedown) is scope drift.
Missing → P1 finding citing C1.

**C2 — Success metric rationale or baseline.** Every measurable threshold in §5
(Success Metrics) must carry either an explicit rationale ("based on P95 latency
of current baseline X") or a cited numeric baseline. A threshold with no
rationale and no baseline is not evidence-grounded and cannot gate the 30-day
launch decision. Missing → P2 finding citing C2.

**C3 — Functional requirement ACs complete.** Every §9 functional requirement
must carry nested acceptance criteria. A functional requirement with no ACs
leaves a gap the EARS layer cannot fill without product judgement (e.g., Expose
Counts in §9 with no nested AC). Missing → P2 finding citing C3.

**C4 — Priority consistency across sections.** Priority assignments (P1/P2/P3
or MoSCoW labels) must be consistent across §7 (Scope), §9 (Functional
Requirements), and §11 (Acceptance Criteria). A feature classified P2 in §7
but carrying P1 ACs in §11 introduces prioritisation ambiguity that cascades
into sprint planning. Missing → P2 finding citing C4.

**C5 — 30-day decision gate in §5.** §5 (Success Metrics) must define the
metrics and thresholds that will be evaluated at the 30-day post-launch
decision point. "Launch and monitor" is not a decision gate; the document
must name the decision criteria explicitly so the gate is evaluable. Missing
→ P2 finding citing C5.

**C6 — §11 validation cells are specific.** Every §11 gate's Validation cell
must specify a named validation method ("p95 measured via load-test," "verified
by audit log export"), not a vague label such as "Pass" or "controls in place."
A vague cell cannot be objectively evaluated. Missing → P2 finding citing C6.

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
