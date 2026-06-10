---
layer: 04_BDD
lens: auditor
weight: 10
agent: traceability-auditor
framework_spec_version: "0.16.1"
---
# auditor lens — BDD layer

## Reasoning frame

The auditor lens at BDD altitude validates conformance to the formal rules
that govern Gherkin document structure: ID naming, tag-to-EARS-line
traceability, step-definition catalog membership, and Gherkin-lint
compliance. At upstream layers the auditor lens examined different element
types: at EARS it checked EARS-line IDs, at PRD it checked section-heading
IDs and cross-reference integrity. At BDD altitude the element types change
— the auditor now works on scenario IDs, feature-file Document Control
blocks, and lint-rule compliance — but the principle is identical: formal
correctness is a precondition for downstream tooling, traceability matrices,
and regulatory evidence.

Traceability at BDD altitude runs in both directions. Each scenario tag must
resolve to a named upstream EARS line, confirming that the scenario exists
because a requirement demands it. Each feature file must carry a Document
Control block that names the EARS lines in scope, the author, the review
status, and the version. Without these records a BDD layer cannot serve as
audit evidence, cannot be linked to change management records, and cannot
be navigated by tools that generate traceability reports from structured
metadata.

Gherkin-lint compliance is separately required. Linting catches structural
defects — missing Feature: keyword, duplicate scenario titles, inconsistent
indentation, trailing whitespace — that are not caught by content review
but cause silent parser failures in automated BDD runners. A lint-clean
feature file set is a precondition for reliable CI execution.

This lens does NOT evaluate: EARS coverage completeness (qa_lead), scenario
implementability (tech_lead), failure-mode coverage (chaos_engineer), abuse-case
coverage (security_engineer), or observability hooks (operator). The auditor
lens is confined to formal document conformance and traceability integrity.

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check citation
are out-of-scope and discarded by the synthesizer.

**C1 — Tags resolve to upstream EARS lines.** Every `@ears:` or equivalent
traceability tag applied to a scenario or feature must resolve to a named
EARS line ID in the upstream EARS document. Tags that reference non-existent
EARS IDs produce orphan traceability — the scenario claims to test a
requirement that does not exist in the specification. Tags that are absent
leave the scenario with no declared upstream requirement. Missing → P1
citing C1.

**C2 — Step-definition catalog conformance.** Every Gherkin step used across
the feature file set must appear in the project's step-definition catalog
with a matching regular expression and declared parameter types. Steps that
have no catalog entry cannot be executed by the BDD runner and will produce
an "undefined step" error at run time. Missing → P2 citing C2.

**C3 — Scenario IDs follow `BDD.NN.SS.xxxx` per ID_NAMING_STANDARDS.** Every
scenario must carry a unique ID tag in the format `@id:BDD.NN.SS.xxxx` where
`NN` is the two-digit feature number, `SS` is the two-digit scenario number
within the feature, and `xxxx` is a four-character alphanumeric slug derived
from the scenario title. IDs that deviate from this format cannot be reliably
referenced in traceability matrices or change management records. Missing →
P2 citing C3.

**C4 — Gherkin-lint clean.** The complete set of feature files must pass the
project's configured Gherkin-lint ruleset with zero errors. Lint rules in
scope include at minimum: no duplicate scenario titles within a feature,
consistent indentation (2-space or 4-space, not mixed), no trailing whitespace,
Feature keyword present in every file, and no empty scenario bodies. Missing
→ P1 citing C4.

**C5 — Feature-file Document Control populated.** Every feature file must
open with a Document Control comment block containing at minimum: EARS
scope (list of EARS line IDs the file covers), author, review status
(Draft / In-Review / Approved), and schema version. A feature file without
a Document Control block cannot be linked to its upstream requirements in a
traceability audit or change management review. Missing → P3 citing C5.

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
