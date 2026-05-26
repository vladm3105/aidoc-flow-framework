# Review-Team Conformance (Hermes → framework)

How Hermes' saga review maps onto the engine-agnostic review-team spec
(`framework/governance/REVIEW_TEAM.md` + `REVIEW_CREWS.yaml`). This is the
AGENT-TEAM **Phase 1** record: Hermes *conforms* its existing persona-output /
reducer / scoring to the framework schema rather than rebuilding them.

## Persona-name mapping (Hermes runtime → framework crew)

The framework crews use engine-agnostic lens names; Hermes' runtime persona files
use its own. The mapping (in `mcp_server/review/review_scoring.py`,
`FRAMEWORK_PERSONA_ALIASES`):

| Hermes runtime persona | Framework crew persona |
|------------------------|------------------------|
| `chaos_engineer`       | `adversary`            |
| `chairperson`          | `synthesizer`          |
| `requirements_specialist`, `tech_lead`, `qa_lead`, `architect`, `product_owner`, `business_analyst`, `operator`, `auditor`, `integration_lead` | identity (same name) |

Hermes also defines creation-only personas (`strategist`, `ux_strategist`,
`content_strategist`, `fact_checker`) that are **not** framework review-crew
members; they carry no review weight and are ignored by the weighted score.

## Persona-output contract (field mapping)

Framework persona-output record (`REVIEW_TEAM.md`) ↔ Hermes finding fields
(`persona_output_parser.py`):

| Framework field | Hermes field | Notes |
|-----------------|--------------|-------|
| `persona`       | `persona`    | mapped via the alias table above for weighting |
| `findings[].priority` | `priority` | `P0`–`P3` (identical) |
| `findings[].id` | `branch_id` + content hash | the reducer derives a stable `finding_id` |
| `findings[].location` | `target_layer` (+ section when present) | engine enrichment |
| `findings[].message` | `message` | identical |
| `findings[].recommendation` | `recommended_action` | same concept, engine name |
| `lens_score`    | per-persona branch score | consumed by `score_review` |
| (synthesis) `coverage` | `CoverageReport` | computed by `score_review` |

Hermes keeps extra fields (`category`, `parse_status`, `provenance`) as
engine-specific enrichment above the framework contract.

## Scoring, coverage & the gate

`mcp_server/review/review_scoring.py` implements the framework policy:

- **Aggregate score** = weighted average of the crew's `lens_score`s using the
  `REVIEW_CREWS.yaml` per-layer weights, **renormalised** over the lenses that ran,
  **then capped**: an unresolved **P0 ⇒ 0 (fail)**; an unresolved **P1 ⇒ capped at
  `gate_threshold - 1`**.
- **Coverage** = expected (crew) vs. ran lenses + a `coverage_ratio` (ran
  crew-weight / total); below `quorum` the result is `low_confidence`
  (→ human review), never a silent pass.
- **Gate (deterministic)** = the structural `sdd_doc_lint` floor (computed
  elsewhere) **plus** `no_blocking` (no unresolved P0/P1). The numeric score is
  **advisory** — so a borderline artifact cannot flap pass/fail on model variance.

## Conformance status

- **Done:** the persona-name mapping + the deterministic weighted/capped score +
  coverage (`review_scoring.py`, unit-tested in `tests/unit/test_review_scoring.py`).
- **Remaining (Phase 1 cont.):** capture `lens_score` in `persona_output_parser`;
  surface `score` + `coverage` in the saga result and the `PERSONA_REVIEW_REPORT` /
  `UCR_*` report shape; align `persona_mappings.yaml` review crews with the framework
  crews where they differ.
