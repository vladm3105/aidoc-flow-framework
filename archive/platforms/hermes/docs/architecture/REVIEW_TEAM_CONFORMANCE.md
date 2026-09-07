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
| `chairperson`          | `synthesizer`          |
| `chaos_engineer`, `security_engineer`, `requirements_specialist`, `tech_lead`, `qa_lead`, `architect`, `product_owner`, `business_analyst`, `operator`, `auditor`, `integration_lead` | identity (same name) |

> As of framework spec 0.12.0 (CHAOS-SEC-SPLIT-001, D-0030), the framework's
> public name `chaos_engineer` matches Hermes' runtime name — the prior
> `chaos_engineer → adversary` translation is removed. `security_engineer` is
> the new first-class lens; Hermes adopts the identity binding.

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

## Conformance status (Phase 1 complete)

- **Scoring + coverage + persona mapping** — `review_scoring.py` (weighted/capped
  score, `CoverageReport`, alias), unit-tested.
- **Parser** — `persona_output_parser` captures `lens_score`, `location`, a stable
  `id`, and accepts `recommendation` (alias of `recommended_action`).
- **Saga wiring** — `saga_orchestrator` collects per-persona `lens_score`s, computes
  `review_score` + `coverage` via `score_review`, and surfaces them on
  `SagaReviewResult`, the synthesis summary, and the branch summary.
- **Resilience** — the saga degrades on an unrecoverable branch (proceeds on the
  returned crew + records `coverage`), escalating **only below quorum** (was: escalate
  the whole review on any single failure). New `BRANCH_FAILED → BRANCH_COMPLETED`
  transition; the aggregate prompt build uses only the completed lenses.
- **Report shape** — `UCR_OUTPUT_UNIFIED.md` carries the advisory readiness score +
  coverage (+ the gate/quorum note).
- **Crew + name reconciliation** — every framework review-crew lens is covered by the
  Hermes review mapping via the alias (guarded by
  `test_review_scoring::test_hermes_review_crews_cover_framework_crews`); the
  `UCR_PROMPT_*` / `UCRem_*` prompts retitle the lens `THE DEVIL'S ADVOCATE →
  THE CHAOS ENGINEER` to match the runtime persona key. (The `devil_advocate_note`
  report-schema field is retained — it is a field key, not a persona title.)

The numeric score stays **advisory**; the gate is the deterministic structural
floor combined with the "no unresolved P0/P1" rule (`REVIEW_TEAM.md`).
