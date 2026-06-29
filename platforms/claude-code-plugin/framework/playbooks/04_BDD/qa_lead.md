---
layer: 04_BDD
lens: qa_lead
weight: 35
agent: test-architect
framework_spec_version: "0.32.0"
---
# qa_lead lens — BDD layer

## Reasoning frame

The qa_lead lens is the authoring lens at BDD altitude. At EARS altitude this
lens operated as a reviewer, validating that each EARS trigger-response pair
was translatable to a scenario without interpretation. At BDD altitude the
lens shifts role: the qa_lead now owns scenario-schema correctness, scenario
structure, and EARS-to-BDD coverage parity. Every EARS acceptance-criterion
line must become at least one executable scenario in the `scenarios:` YAML
block; the qa_lead lens is the primary enforcer of that obligation.

Coverage parity at BDD has two planes. The first is forward coverage: every
EARS element must be cited by at least one scenario's element-level `ears:`
list, and the feature's coverage — the computed union of its scenarios'
`ears` — must reach every EARS element. There is no feature-level `ears`
field; the `feature:` block is a container and its coverage is derived
(YAML-BDD-SCHEMA D-3). The second plane is structural soundness: each step in
a scenario's `given:`/`when:`/`then:` phase lists must be atomic — one
trigger, one action, one observable outcome per list entry. Compound steps
that bundle multiple triggers or actions into a single `given`/`when`/`then`
entry resist automation, produce false-positive test results, and obscure
which condition caused a failure.

At TDD downstream the qa_lead lens descends to test-implementation concerns:
fixture contracts, mock fidelity, assertion granularity. At BDD the lens does
not ask those questions. The qa_lead lens at BDD is confined to scenario
authoring quality and EARS coverage completeness. It does NOT evaluate:
scenario implementability (tech_lead), failure-mode scenario coverage
(chaos_engineer), abuse-case scenarios (security_engineer), observability
hooks (operator), or schema and ID conformance (auditor).

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check citation
are out-of-scope and discarded by the synthesizer.

**C1 — Every EARS element covered by ≥1 scenario.** Every EARS element must be
cited by at least one scenario's element-level `ears:` list, and every scenario
must carry a non-empty `ears:` list naming its parent EARS element(s). The
feature's coverage is the computed union of its scenarios' `ears` — there is
no feature-level `ears` field (D-3). An EARS element absent from every
scenario's `ears` has no executable acceptance test. A scenario with an empty
`ears` list is a test without a stated requirement. Both gaps are equally
defective. Missing → P1 citing C1.

**C2 — given/when/then atomicity.** Each entry in a scenario's `given:`,
`when:`, and `then:` phase lists must contain exactly one trigger, one action,
or one observable outcome respectively. Multiple entries in a phase list are
And-continuations and are well-formed; the defect is a single list entry that
combines multiple triggers with "and", or bundles multiple observable outcomes
into one `then` entry. Compound entries break the one-trigger-one-result
contract that makes scenarios independently executable and failure-diagnosable.
Missing → P2 citing C2.

**C3 — Parameterized scenarios used appropriately.** A `type: parameterized`
scenario with `outline: true` and an `examples: {headers, rows}` table must be
used when a single scenario template applies across multiple parametric data
sets. A singular scenario must use literal `given`/`when`/`then` steps with no
`examples` table. Duplicating concrete scenarios where one parameterized
`examples` table would eliminate the repetition, or marking a single-row
scenario `outline: true`, are both authoring defects. Missing → P3 citing C3.

**C4 — Shared preconditions hoisted into `background:`.** Precondition steps
that appear verbatim in three or more scenarios must be extracted to the
feature's `background.steps` block, which runs before every scenario, rather
than copy-pasted into each scenario's `given:` list. Inline duplication of a
shared precondition produces maintenance fragility: a single phrasing change
requires editing every occurrence rather than one background entry. (Action or
outcome steps that repeat only because they vary by data belong in a
parameterized scenario instead — see C3.) Missing → P3 citing C4.

**C5 — Scenario classification consistent.** Each scenario's `type:` must match
its behaviour (`success` for a happy path, `error` for a rejection/failure,
`recovery` for restoration, `parameterized` for a data-table template,
`optional` for a non-MVP path), and its `priority:` (`p0-critical` … `p3-low`)
must be consistent with the parent EARS element's stated priority.
Misclassifying a failure scenario as `type: success`, or assigning a
`priority:` that contradicts the EARS element it covers, corrupts coverage
reporting and gate scoring. (Structurally invalid `type:`/`priority:` enum
values are the auditor's BDD-SCHEMA-001 concern; this check is semantic
correctness of the classification.) Missing → P3 citing C5.

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
