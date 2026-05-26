# AGENT-TEAM Plan — SDD review team: independent persona-agents + shared blackboard + synthesis

| Field      | Value                          |
|------------|--------------------------------|
| Task       | AGENT-TEAM                     |
| Depends on | `REVIEW_REMEDIATION_FLOW.md` (the loop + trigger points); Hermes executor + `saga_orchestrator` + `persona_mappings.yaml`; the plugin 9-agent roster; framework spec `0.7.1` |
| Status     | PLANNED — 2026-05-25 (awaiting decisions D1–D6) |
| Feeds      | equal-quality multi-perspective review/remediation across both platforms; a shared, engine-agnostic "SDD review team" the plugin and Hermes both run |

## Objective

Hermes produces higher-quality documents than the plugin because it reviews and
remediates with a **multi-persona expert board**, while the plugin does a
**single-pass checklist + score**. Close that gap *by construction*: define one
engine-agnostic **SDD review-team** model in `framework/` — the persona lenses,
the per-layer crews, a shared **review-blackboard** contract for agents to
exchange findings, and a **synthesis** step that aggregates them — and have each
platform run it as **true independent agents** on its own runtime (the plugin via
Claude Code `Task` subagents; Hermes via its `saga_orchestrator` executor
branches). One team definition, two runners, identical output structure.

## Background — what exists

| Capability | Plugin | Hermes | Framework spec |
|------------|--------|--------|----------------|
| Independent agent runtime | Claude Code `Task` subagents (9-agent roster in `agents/`) | executor "API agents" (litellm) + `saga_orchestrator` per-persona **branches** (asyncio/ThreadPool, saga journal/compensation) | — |
| Persona/lens definitions | implicit in the 9 agents | `skills/personas/*.md` | — |
| Per-layer crew mapping | none (skills don't dispatch a panel) | `persona_mappings.yaml` (create/review per layer) | — |
| Per-agent findings → aggregate | none (single-pass audit) | `persona_output_parser` (P0–P3 findings) → `saga_reducer` → `PERSONA_REVIEW_REPORT` | — |
| Review/remediation/gate loop | `doc-*-audit`/`-fixer` (single pass) | `UCR_*`/`UCRem_*` + saga | `REVIEW_REMEDIATION_FLOW.md` (light contract: surface findings/score/path) |

**Both platforms can already run agents independently** (confirmed: plugin
subagents; Hermes saga branches = one executor call per persona). What's missing
is a *shared* team definition + a *shared* info-exchange/aggregation contract so
the two produce the same review depth and report shape.

## The model (engine-agnostic)

A **review team** = a **crew** of persona-agents + a **synthesizer** + a shared
**blackboard**, run in a chosen **mode**, producing a **unified review report**.

1. **Persona (review lens).** A named expert lens with a focus + checklist —
   e.g. `requirements_specialist`, `tech_lead`, `qa_lead`, `adversary`
   (devil's-advocate / chaos), `integration_lead`, `architect`, `auditor`,
   `synthesizer` (chairperson). Engine-agnostic definitions (the "what to look
   for"), not engine wiring.
2. **Crew per layer/operation.** Which personas review each artifact, per
   operation (create / review / remediate). Generalizes Hermes' `persona_mappings`
   to the framework level (machine-readable, like `ADAPTATION_SURFACE.yaml`).
3. **Review blackboard (the "inbox"/shared store).** A defined per-review
   workspace where each persona-agent **writes** its findings and **reads** the
   artifact-under-review (and, in sequential mode, peers' prior findings). It is a
   *hub* (orchestrator-mediated), not a peer-to-peer mesh — because the plugin's
   subagents return outputs to the orchestrator rather than sharing live memory.
   - **Persona-output contract** (the artifact each agent deposits): standardize
     Hermes' existing shape — `{persona, lens, findings:[{id, priority(P0–P3),
     location, message, recommendation}], lens_score}` — as the framework schema.
4. **Synthesis (chairperson/reducer).** A final agent reads all persona outputs
   from the blackboard, **dedupes/merges** findings, resolves conflicts, computes
   the **overall readiness score**, and emits the **unified review report**
   (generalizing Hermes' `saga_reducer` → `PERSONA_REVIEW_REPORT`). The report
   feeds the existing review→remediation→gate loop.
5. **Mode.**
   - `independent` (map-reduce, **default**): personas run isolated/parallel, then
     synthesis reduces — cheaper, higher signal-independence, fewer anchoring
     biases. Matches plugin subagents + Hermes saga branches naturally.
   - `sequential` (context-passing): each persona sees prior outputs from the
     blackboard — richer cross-talk, more tokens, possible anchoring. Optional,
     per-crew.
   - `single_pass` (lightweight fallback): one agent applies all lenses in one
     prompt (today's plugin audit / Hermes' no-executor `UCR_*` mode) — for cost-
     constrained or no-subagent environments.

## Platform adapters (the "how")

| Concern | Plugin runner | Hermes runner |
|---------|---------------|---------------|
| Agent runtime | `Task` subagents (map framework personas → the 9 `agents/`; add missing lenses) | executor API-agents via `saga_orchestrator` branches |
| Blackboard | files under `.aidoc/review/<artifact-id>/<persona>.json` (+ `report.md`) — subagents return to the orchestrator, which writes the slots | the saga **journal** + branch summaries |
| Dispatch | `pm-orchestrator` (or upgraded `doc-<layer>-audit`) fans out the crew, then runs the `synthesizer` subagent | `saga_orchestrator` (already per-persona) |
| Synthesis | `synthesizer`/chairperson subagent reduces the blackboard | `saga_reducer` |
| Output | unified review report → `doc-<layer>-fixer` | `PERSONA_REVIEW_REPORT` → `UCRem_*` |

Both bind to the **same** crew map + persona-output schema + report shape, so a
BRD reviewed by either platform gets the same lenses and a structurally identical
report.

## Decisions (recommendations — pending confirmation)

- **D1 — Where the team spec lives.** `framework/governance/REVIEW_TEAM.md`
  (personas + the blackboard/persona-output/synthesis contract) + a machine-
  readable `framework/governance/REVIEW_CREWS.yaml` (per-layer/operation crews +
  default mode). Engine-agnostic; companion to `REVIEW_REMEDIATION_FLOW.md`.
  *(Recommend.)* GATE-SPEC change ⇒ version bump.
- **D2 — Info-sharing model.** **Hub blackboard + map-reduce default**
  (`independent` mode), with `sequential` and `single_pass` as declared options.
  Reject peer-to-peer mesh (plugin subagents can't share live state).
- **D3 — Persona-output schema.** Adopt/standardize Hermes' existing
  `priority(P0–P3)` finding shape as the framework contract (so Hermes conforms
  with minimal change; the plugin emits the same JSON).
- **D4 — Persona set + plugin mapping.** Start with the 5 review lenses Hermes
  already uses (requirements/tech/qa/adversary/integration) + `synthesizer`; map
  to the plugin's existing agents where they fit, and **add the missing lenses**
  (`adversary`, `synthesizer`) as plugin agents. Don't force a 1:1 rename of the
  plugin's lifecycle agents.
- **D5 — Cost/perf.** Default crews 3–5 personas; `single_pass` fallback always
  available; document the token/latency cost; make multi-agent the default only
  for `pre_promotion`/`pre_merge` gates, advisory `single_pass` for `on_author`.
- **D6 — Conformance.** The framework owns *structure* (crew map valid against the
  8 layers; persona-output + report schema). It does **not** assert LLM output
  content. A conformance check validates `REVIEW_CREWS.yaml` (layers ⊆ the 8;
  personas ⊆ the defined set) — mirrors `test_adaptation`.

## Step sequence (phased; sequenced PRs)

1. **Confirm D1–D6.**
2. **Phase 0 — spec** (`framework/`): `REVIEW_TEAM.md` + `REVIEW_CREWS.yaml` +
   persona-output/report schema; register in governance README + `test_governance`;
   add the crew-map conformance check; version bump + CHANGELOG. *(Own PR.)*
3. **Phase 1 — Hermes adapter** (after Phase 0): align `persona_mappings.yaml`,
   `persona_output_parser`, `saga_reducer`, and the `UCR_*`/`UCRem_*` report shape
   to the framework schema; document the mapping. Mostly *conform existing code*.
4. **Phase 2 — plugin adapter** (after Phase 0): a `review-team` mechanism —
   `pm-orchestrator`/`doc-<layer>-audit` fans out the crew as subagents writing to
   the `.aidoc/review/` blackboard; add the `adversary` + `synthesizer` agents;
   wire `-audit`/`-fixer`/`-autopilot` to use it (with the `single_pass` fallback).
5. **Phase 3 — parity check + docs**: a fixture-based check that both runners emit
   the same report schema for a sample artifact; update `docs/PARITY.md`.
6. **Land** each phase; update CHANGELOG / platform changelogs / HANDOFF.

## Verification

- Phase 0: conformance green incl. the crew-map check; `spec_gate` green; the spec
  names personas/blackboard/synthesis without engine tokens (`test_spec_hygiene`).
- Phase 1: Hermes pytest green; a saga review emits findings matching the
  framework persona-output schema; `saga_reducer` report maps to the spec report.
- Phase 2: a plugin `doc-<layer>-audit` run dispatches the crew, writes per-persona
  blackboard slots, and the synthesizer produces the unified report; `single_pass`
  fallback still works; conformance unaffected (platform change).
- Phase 3: same sample artifact → structurally identical report from both runners.

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | Cost/latency blow-up (N agents × layers) | Small default crews (3–5); `single_pass` fallback; multi-agent default only at gates, advisory at `on_author` (D5). |
| R2 | Plugin subagents can't share live state | Hub blackboard (orchestrator-mediated), not mesh (D2); subagents return → orchestrator writes slots. |
| R3 | Spec over-reach (mandating LLM behavior / engine wiring) | Spec owns structure only (crew map + schemas); "how" is per-platform; conformance checks structure, not content (D6). |
| R4 | Fighting Hermes' working saga system | Generalize Hermes' *existing* model (persona_output/saga_reducer) into the spec rather than inventing a new one (D3); Phase 1 is "conform," not "rebuild". |
| R5 | Plugin scope creep (audit+fixer+autopilot × 8 layers) | One shared `review-team` mechanism invoked by the skills, not 24 bespoke rewrites; add lenses once. |
| R6 | Engine tokens leak into the spec | No `subagent`/`Task`/`mcp`/`saga`/platform names in `framework/`; describe abstractly; run `test_spec_hygiene`. |
| R7 | GATE-SPEC self-gate (Phase 0) | VERSION + CHANGELOG by construction; FSV match; suite green. |

## Review log

> ≥2 passes before implementation (CLAUDE.md). Each pass re-reads the whole plan,
> lists findings, folds fixes back above; stop when a pass finds nothing.

### Pass 1 — 2026-05-25

- **Mesh vs hub.** First sketch implied agents messaging each other; plugin
  subagents can't share live memory (they return to the caller). Reframed the
  "inbox" as a **hub blackboard** (orchestrator-mediated slots) — implementable on
  both runtimes (R2, D2).
- **Don't reinvent Hermes.** Hermes already has persona-output + `saga_reducer` +
  per-persona branches. The spec should **generalize that proven shape**, making
  Phase 1 a conform-and-document step, not a rebuild (R4, D3).
- **Spec/impl boundary.** Pulled all engine wiring (subagents, saga, executor) out
  of the framework spec — it owns personas + crew map + schemas only; conformance
  checks structure, not LLM content (R3, R6, D6).
- **Cost.** Added mode tiers (`independent`/`sequential`/`single_pass`) + a
  default-by-trigger-point policy so multi-agent isn't forced everywhere (R1, D5).

### Pass 2 — 2026-05-25

- **Sequencing.** Phase 0 (GATE-SPEC) lands alone; Hermes (conform) and plugin
  (build) adapters follow as separate PRs cut after it — same discipline as
  DOC-CHECK / PLATFORM-ALIGN (avoids version/CHANGELOG collisions).
- **Plugin persona gap.** Confirmed the missing lenses are `adversary`
  (devil's-advocate/chaos) and `synthesizer` (chairperson); the other lenses map
  to existing agents. Scoped D4 to add exactly those two, not a roster overhaul.
- **Conformance realism.** The crew-map check validates structure (layers ⊆ 8,
  personas ⊆ defined set) like `test_adaptation`; it can't assert review quality —
  stated explicitly so the gate isn't oversold (D6).
- **Parity proof.** Added Phase 3 (same artifact → structurally identical report
  from both runners) as the concrete parity evidence, not just "both implement it."
- No further findings — implementable pending D1–D6 confirmation.
