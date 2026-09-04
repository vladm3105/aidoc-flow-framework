---
layer: 04_BDD
lens: auditor
weight: 10
agent: traceability-auditor
framework_spec_version: "0.51.0"
---
# auditor lens — BDD layer

## Reasoning frame

The auditor lens at BDD altitude validates conformance to the formal rules
that govern the structured BDD document: element-ID naming, element-level
`ears` traceability, `scenarios:` schema conformance (`BDD-SCHEMA-001`), and a
populated Document Control block. At upstream layers the auditor lens examined
different element types: at EARS it checked EARS-line IDs, at PRD it checked
section-heading IDs and cross-reference integrity. At BDD altitude the element
types change — the auditor now works on scenario `id:` fields, the
`document_control:` block, and the `scenarios:` YAML schema — but the principle
is identical: formal correctness is a precondition for downstream tooling,
traceability matrices, and regulatory evidence.

Traceability at BDD altitude runs in both directions. Each scenario's
element-level `ears:` list must resolve to named upstream EARS elements,
confirming that the scenario exists because a requirement demands it. The
feature's EARS coverage is the computed union of its scenarios' `ears`; the
`feature:` block itself carries no `ears` field (YAML-BDD-SCHEMA D-3). Each
document must carry a `document_control:` block that names the author, the
review status, and the version. Without these records a BDD layer cannot serve
as audit evidence, cannot be linked to change management records, and cannot
be navigated by tools that generate traceability reports from structured
metadata.

Schema conformance is separately required. The `BDD-SCHEMA-001` structural
check catches defects — a malformed `scenarios:` block, a non-mapping scenario,
a missing required field, an invalid `type`/`priority` enum — that are not
caught by content review but cause silent failures in the downstream
edge-graph and coverage tooling. A schema-clean `scenarios:` block is a
precondition for reliable traceability and coverage computation.

This lens does NOT evaluate: EARS coverage completeness (qa_lead), scenario
implementability (tech_lead), failure-mode coverage (chaos_engineer), abuse-case
coverage (security_engineer), or observability hooks (operator). The auditor
lens is confined to formal document conformance and traceability integrity.

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check citation
are out-of-scope and discarded by the synthesizer.

**C1 — Element-level `ears` resolves to upstream EARS elements.** Every item in
every scenario's `ears:` list must be an element-level EARS ID
(`EARS.NN.SS.xxxx`) that resolves to a named element in the upstream EARS
document. Doc-form items (`EARS-NN`) are rejected by REFGRAN01 and are not
acceptable here. An `ears` item that references a non-existent EARS element
produces orphan traceability — the scenario claims to test a requirement that
does not exist. A scenario with an empty `ears` list has no declared upstream
requirement. Missing → P1 citing C1.

**C2 — Required scenario fields present.** Every scenario in the `scenarios:`
list must carry all required fields: `id`, `name`, `type`, `priority`, `ears`,
`given`, `when`, `then` (each non-empty). A scenario missing any required field
is flagged by `BDD-SCHEMA-001` and cannot be consumed by the edge-graph or
coverage tooling. Missing → P2 citing C2.

**C3 — Scenario IDs follow `BDD.NN.SS.xxxx` per ID_NAMING_STANDARDS.** Every
scenario must carry a unique `id:` value in the format `BDD.NN.SS.xxxx` where
`NN` is the two-digit feature number, `SS` is the two-digit section number, and
`xxxx` is a four-character content-derived hash. On migration from a legacy
Gherkin document the `id:` is COPIED VERBATIM from the source `@scenario-id` —
never recomputed — so downstream `@bdd:` citations stay stable. IDs that
deviate from this format, collide, or were recomputed on migration cannot be
reliably referenced in traceability matrices or change management records.
Missing → P2 citing C3.

**C4 — `scenarios:` block schema-clean (`BDD-SCHEMA-001`).** The `scenarios:`
block must be a well-formed flat YAML list (not the deprecated category-dict),
and every scenario must be a mapping carrying an `id:` field, a `type:` that is
one of `success`/`error`/`recovery`/`parameterized`/`optional`, and a
`priority:` that is one of `p0-critical`/`p1-high`/`p2-medium`/`p3-low`. Any
such structural deviation is a `BDD-SCHEMA-001` finding and blocks reliable
downstream consumption. (Element-`id` uniqueness is `HASH01`'s corpus-wide
check, not BDD-SCHEMA-001; the `feature:`-block no-`ears` contract is the
tech_lead lens's C5.) Missing → P1 citing C4.

**C5 — Document Control populated.** Every BDD document must carry a
`document_control:` block containing at minimum: `version`, `status`
(`Draft`/`In Review`/`Approved`), `author`, and `date_created`/`last_updated`.
The block must NOT carry `ears`/`prd`/`brd` reference rows — upstream trace
lives element-level on each scenario's `ears:` list (D-3). A document without a
populated Document Control block cannot be linked to change management or audit
records. Missing → P3 citing C5.

## Beyond-checklist

If you find a layer-specific failure mode the checklist does not cover, raise
it as a P2/P3 finding citing `beyond-checklist:<principle-tag>` and state
which paragraph of the reasoning frame motivates it. Use sparingly. If
more than 30% of your findings are beyond-checklist, the playbook needs
revision (file a follow-up).


*Cross-layer cardinality note (CLEANUP-PR-F item 18):* apparent-orphan
downstream docs (e.g., `PRD-02` declaring `@brd: BRD-01` when `PRD-01`
also exists with the same upstream) MAY be valid siblings of the same
upstream, not actual orphans. Validate the trace by tag resolution, not
by doc-number alignment. See `framework/governance/ID_NAMING_STANDARDS.md`
§Cross-layer cardinality.
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
