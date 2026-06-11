---
layer: 04_BDD
lens: qa_lead
weight: 35
agent: test-architect
framework_spec_version: "0.19.0"
---
# qa_lead lens — BDD layer

## Reasoning frame

The qa_lead lens is the authoring lens at BDD altitude. At EARS altitude this
lens operated as a reviewer, validating that each EARS trigger-response pair
was translatable to a scenario without interpretation. At BDD altitude the
lens shifts role: the qa_lead now owns Gherkin syntax correctness, scenario
structure, and EARS-to-BDD coverage parity. Every EARS acceptance-criterion
line must become at least one executable Gherkin scenario; the qa_lead lens
is the primary enforcer of that obligation.

Coverage parity at BDD has two planes. The first is forward coverage: every
EARS line must be traceable to at least one scenario, and the bidirectional
coverage matrix must be present and readable. The second is structural
soundness: each scenario step must be atomic — one trigger, one action, one
observable outcome. Compound steps that bundle multiple triggers or actions
into a single Given/When/Then clause resist automation, produce
false-positive test results, and obscure which condition caused a failure.

At TDD downstream the qa_lead lens descends to test-implementation concerns:
fixture contracts, mock fidelity, assertion granularity. At BDD the lens does
not ask those questions. The qa_lead lens at BDD is confined to Gherkin
authoring quality and EARS coverage completeness. It does NOT evaluate:
scenario implementability (tech_lead), failure-mode scenario coverage
(chaos_engineer), abuse-case scenarios (security_engineer), observability
hooks (operator), or ID and lint conformance (auditor).

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check citation
are out-of-scope and discarded by the synthesizer.

**C1 — Every EARS line covered by ≥1 scenario.** A bidirectional coverage
matrix must be present mapping each EARS line ID to at least one BDD scenario
ID, and each BDD scenario ID back to its parent EARS line. An EARS line with
no entry in the matrix has no executable acceptance test. A scenario with no
EARS parent is a test without a stated requirement. Both gaps are equally
defective. Missing → P1 citing C1.

**C2 — Given/When/Then atomicity.** Each scenario step must contain exactly
one trigger (Given), one action (When), and one observable outcome (Then).
Steps that combine multiple triggers with "and" in the same clause, or that
bundle multiple observable outcomes into a single Then, are compound steps.
Compound steps break the one-trigger-one-result contract that makes scenarios
independently executable and failure-diagnosable. Missing → P2 citing C2.

**C3 — Data tables vs Scenario Outlines used appropriately.** Scenario
Outlines with Examples tables must be used when a single scenario template
applies across multiple parametric data sets. Inline data tables must be used
when a scenario has structured input or structured expected output that is
singular. Duplicating concrete scenarios where a Scenario Outline would
eliminate repetition, or using Scenario Outlines for a single example row,
are both authoring defects. Missing → P3 citing C3.

**C4 — Shared steps deduplicated into a step-definition catalog.** Steps that
appear verbatim in three or more scenarios across the feature file set must be
extracted to a shared step-definition. Inline duplication of shared steps
produces maintenance fragility: a single phrasing change requires editing
every occurrence rather than one catalog entry. Missing → P3 citing C4.

**C5 — Tag conventions consistent.** Tags applied to features, scenarios, and
Scenario Outlines must follow the project tag taxonomy declared in the BDD
layer's tag-convention document. Tag names must be lowercase with hyphens,
not underscores. Scenario-level tags must appear on the line immediately
preceding the `Scenario:` or `Scenario Outline:` keyword with no blank line
between tag and keyword. Missing → P3 citing C5.

## Beyond-checklist

If you find a layer-specific failure mode the checklist does not cover, raise
it as a P2/P3 finding citing `beyond-checklist:<principle-tag>` and state
which paragraph of the reasoning frame motivates it. Use sparingly. If
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
