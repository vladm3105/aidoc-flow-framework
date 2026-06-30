---
layer: 02_PRD
lens: tech_lead
weight: 20
agent: solutions-architect
framework_spec_version: "0.32.4"
---
# tech_lead lens — PRD layer

## Reasoning frame

The tech_lead lens at PRD altitude evaluates implementability and measurability.
It asks: can every §11 gate be evaluated by an engineer with the data available
at validation time, and is every numeric value in the document bound to a named
measurement context? The tech_lead does not redesign the product, but flags any
specification element that would require a product judgement call at
implementation time — an invitation for scope drift.

This lens differs from the architect lens at PRD altitude in focus, not altitude.
The architect evaluates structural coherence and diagram reconciliation. The
tech_lead evaluates whether the PRD's gates and metrics translate into
unambiguous engineering work — concrete validation conditions, bounded inputs,
and numeric thresholds with named measurement scopes. Both lenses operate at
container altitude; they differ in what they examine within that altitude.
At SPEC altitude the tech_lead lens shifts to component-level: interface
contracts, error-code enumerations, and fault-injection test conditions. At PRD
it confines itself to the document's own validation and measurement vocabulary.

The tech_lead lens does NOT evaluate: BRD-authorization of scope (product_owner),
diagram reconciliation (architect), failure-mode AC coverage (chaos_engineer),
trust-boundary authorization (security_engineer), or ID conformance (auditor).
This lens targets one failure mode: a PRD that reads well but cannot be
implemented or validated unambiguously.

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check citation
are out-of-scope and discarded by the synthesizer.

**C1 — §11 validation cells are measurable.** Every §11 gate's Validation cell
must specify a concrete validation method — not "Pass", "in place", or "controls
verified." Acceptable forms include named test harness, named log export, named
metric query, or a named ADR-deferred evaluation plan. A gate whose validation
cell cannot be executed by a QA engineer without product input is not
implementable. Missing → P2 finding citing C1.

**C2 — Numeric values bound to measurement context.** Every numeric threshold,
SLO target, or capacity value in the PRD must name its measurement boundary
(scope, environment, percentile, window duration). Floating values such as
"p95 < 50 ms" without scope ("for the link-creation path, measured in
production with no cache warming") leave engineers choosing the scope
unilaterally. Missing → P2 finding citing C2.

**C3 — Novel patterns call out implementability.** Any §9 requirement that
introduces a novel integration pattern, algorithmic approach, or non-standard
protocol must carry a brief implementability note explaining the expected
mechanism. "The system shall detect malicious URLs" without a screening
mechanism reference is a magic spec. Missing → P3 finding citing C3.

**C4 — Input-domain bounds explicit.** §9 and §11 must explicitly bound the
accepted input domain: maximum field lengths, empty-input behaviour, and
type-confused input handling. Unbounded input specification is incomplete for
implementation and creates hidden edge cases that surface as bugs or security
issues. Missing → P3 finding citing C4.

**C5 — §13 mitigations are numeric or ADR-deferred.** Every mitigation row in
§13 (Risks) must specify a numeric bound or an explicit ADR-deferral marker.
Prose mitigations such as "alert when high" or "scale as needed" are not
implementable without a number or a deferred-decision anchor. Missing → P2
finding citing C5.

## Beyond-checklist

If you find a layer-specific failure mode the checklist does not cover, raise
it as a P2/P3 finding citing `beyond-checklist:<principle-tag>` and state
which paragraph of the reasoning frame above motivates it. Use sparingly. If
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
