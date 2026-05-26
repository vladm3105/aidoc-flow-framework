# AGENT-TEAM Plan — SDD review team: independent persona-agents + shared blackboard + synthesis

| Field      | Value                          |
|------------|--------------------------------|
| Task       | AGENT-TEAM                     |
| Depends on | `REVIEW_REMEDIATION_FLOW.md` (the loop + trigger points); Hermes executor + `saga_orchestrator` + `persona_mappings.yaml`; the plugin 9-agent roster; framework spec `0.7.1` |
| Status     | IN PROGRESS — Phase 0 (spec) merged (spec `0.8.x`); Phase 1 (Hermes conform) STARTED — scoring/coverage + persona-name mapping landed; rest of Phase 1 + Phases 2–3 pending |
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

### Operations — the team works in three shapes

The team runs the same crew + blackboard + persona-output contract for all three
operations of the review→remediation→gate loop; only the roles differ:

- **Review** — the crew reviews the artifact in parallel; synthesis produces the
  unified findings report + score (the shape described above).
- **Create** — **one drafter** persona authors the artifact from the template +
  upstream artifacts, then the **review crew** reviews the draft and the drafter
  revises (an internal create→review→revise loop) until the gate passes. *Not* N
  parallel drafts (incoherent to merge) — one author, many reviewers. This is how
  a created document reaches review-grade quality, addressing the headline ask.
- **Remediate** — a **fixer** persona proposes a concrete patch per blocking
  finding from the review report; the relevant lens(es) **validate** each patch
  doesn't regress; synthesis emits the proposed fix set. (Generalizes
  Hermes' `*Fixer` personas + `UCRem_*`.)

### Scoring, conflicts & the gate

- **Per-lens score + findings.** Each persona emits a `lens_score` (0–100) and
  `findings` (with `priority` P0–P3).
- **Aggregate score = deterministic.** The overall readiness score is a
  **weighted average of the lens scores**, using per-layer persona weights declared
  in the crew map (generalizing the "Scoring Weight" tables already in the Hermes
  persona docs), **then capped**: any unresolved **P0 ⇒ fail** and **P1 ⇒ capped
  below the gate**, regardless of the average. The math is reproducible given the
  persona outputs.
- **Conflict resolution (defined, not ad hoc).** When personas disagree on the
  same location, the reduce step takes the **max severity** and **unions**
  recommendations (deduped by `location`+`code`); a genuine either/or judgment is
  surfaced to the synthesizer/chairperson as an explicit "contested" finding for a
  human/lead call — never silently dropped.
- **Gate stability (the reproducibility answer).** The **gate decision is
  deterministic**: it is the structural `sdd_doc_lint` check (the `pre_merge`
  gate) **plus** "no unresolved P0/P1". The stochastic *numeric* score and the
  prose findings are **advisory enrichment above** that floor — so a borderline
  document can't flap pass/fail run-to-run on LLM variance; only the
  deterministic floor gates.

### Synthesis = deterministic reduce + optional narrative

Split the synthesizer into two parts (generalizing Hermes' `saga_reducer` +
report prose):

1. **Reduce (deterministic, gating):** merge/dedup findings by `location`+`code`,
   take max severity, compute the weighted+capped score, mark coverage. Pure code,
   reproducible — this is what the gate reads.
2. **Narrative (LLM, advisory):** an executive-summary chairperson pass over the
   reduced findings. Non-gating; it explains, it doesn't decide.

### Resilience & security

- **Partial-crew degradation.** If a persona-agent fails/times out, the reduce
  proceeds on the crew that returned and the report records **coverage** (which
  lenses ran / were missing). Below a declared **quorum** the result is marked
  *low-confidence → human review*, never a silent pass. (Hermes already has saga
  compensation; the plugin orchestrator marks the slot failed.)
- **Inter-agent injection.** The artifact-under-review and peer outputs are
  **untrusted data** (per `SECURITY_REVIEW.md`): a persona never executes
  instructions found in the content, and the blackboard carries only the
  **structured persona-output schema** (findings), not free-form instructions —
  bounding injection propagation to/from the synthesizer.

## Platform adapters (the "how")

| Concern | Plugin runner | Hermes runner |
|---------|---------------|---------------|
| Agent runtime | `Task` subagents (map framework personas → the 9 `agents/`; add missing lenses) | executor API-agents via `saga_orchestrator` branches |
| Blackboard | **transient, git-ignored** files under `.aidoc/review/<artifact-id>/<persona>.json` (aligns with the existing `.aidoc/` project-runtime convention) — subagents return to the orchestrator, which writes the slots; the *unified report* may persist into the doc folder per existing audit convention, the per-persona slots do not | the saga **journal** + branch summaries |
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
- **D5 — Cost/perf + migration.** Default crews 3–5 personas; `single_pass`
  fallback always available; document the token/latency cost. **Default by trigger
  point:** multi-agent team at `pre_promotion`/`pre_merge` gates; **`single_pass`
  (advisory) at `on_author`** — so existing plugin users see no write-time cost
  surprise, and the richer review kicks in only at gates. The plugin behavior
  change (single-pass audit → team-at-gates) is documented in its CHANGELOG.
- **D6 — Conformance.** The framework owns *structure* (crew map valid against the
  8 layers; persona-output + report schema). It does **not** assert LLM output
  content. A conformance check validates `REVIEW_CREWS.yaml` (layers ⊆ the 8;
  personas ⊆ the defined set) — mirrors `test_adaptation`.
- **D7 — Scoring / conflict / gate policy** (see "Scoring, conflicts & the gate").
  Weighted-average lens scores with per-layer persona weights; unresolved P0 ⇒
  fail, P1 ⇒ capped below gate; conflicts → max-severity + union, contested items
  surfaced. The **gate decision is the deterministic `sdd_doc_lint` floor + no
  unresolved P0/P1**; the LLM score is advisory (reproducibility answer).
- **D8 — Adaptation knob.** Add a `review_mode` knob (`team` | `single_pass`) to
  `ADAPTATION_SURFACE.yaml` so a consuming project tunes review depth/cost without
  forking. Extending the closed knob set is a deliberate spec change (updates
  `test_adaptation`). *(Recommend; folds into Phase 0.)*

## Step sequence (phased; sequenced PRs)

1. **Confirm D1–D8.**
2. **Phase 0 — spec** (`framework/`): `REVIEW_TEAM.md` (personas, the three
   operations, blackboard, scoring/conflict/gate policy, resilience+security) +
   `REVIEW_CREWS.yaml` (per-layer/operation crews + persona weights + default mode)
   - the persona-output/report **JSON schema** (incl. `coverage`); add the
   `review_mode` knob to `ADAPTATION_SURFACE.yaml`; register in governance README +
   `test_governance`; add the crew-map + adaptation-knob conformance checks; version
   bump + CHANGELOG. *(Own PR.)*
3. **Phase 1 — Hermes adapter** (after Phase 0; *conform existing code*, don't
   rebuild the working saga). Concrete steps:
   1. **Scoring + coverage + persona mapping** — `review_scoring.py` (weighted/capped
      score from `REVIEW_CREWS.yaml`, `CoverageReport`, framework↔Hermes alias).
      *Landed 2026-05-26.*
   2. **Parser conformance** — extend `persona_output_parser` to capture `lens_score`
      (per persona), `location`, and a stable `id`; keep `recommended_action` as the
      engine's name for `recommendation`. Additive; existing tests stay green.
   3. **Wire scoring into the saga** — `saga_orchestrator` collects the per-persona
      `lens_score`s + doc-type, calls `score_review`, and puts `score` + `coverage`
      on `SagaReviewResult` + the reducer/synthesis summary.
   4. **Report-shape conformance** — surface `score` + `coverage` + the per-finding
      framework fields in the `PERSONA_REVIEW_REPORT` / `UCR_OUTPUT_UNIFIED` shape the
      review→remediation→gate loop reads.
   5. **Crew + name reconciliation** — align `persona_mappings.yaml` *review* crews
      with the framework `REVIEW_CREWS.yaml` crews (membership/weights, bridged by the
      alias map — the framework keeps its engine-agnostic names), and **retitle the
      `THE DEVIL'S ADVOCATE` lens** in the `UCR_PROMPT_*` / `UCRem_*` prompts to the
      canonical persona title (gap-review finding — 11 spots), so every persona title
      matches its runtime key.
   6. **Document** the mapping in `REVIEW_TEAM_CONFORMANCE.md` (started).
4. **Phase 2 — plugin adapter** (after Phase 0): a `review-team` mechanism —
   `pm-orchestrator`/`doc-<layer>-audit` fans out the crew as subagents writing to
   the git-ignored `.aidoc/review/` blackboard; deterministic reduce + score; add
   the `adversary` + `synthesizer` agents; wire `-audit` (review), `-fixer`
   (remediate-team), `-autopilot` (create-team: drafter + review loop), with the
   `single_pass` fallback and the trigger-point default (team at gates).
5. **Phase 3 — parity proof + docs**: (a) a deterministic **CI check** that the
   committed sample **report fixtures** from both runners validate against the
   framework JSON schema; (b) a **documented manual live-run** comparison (same
   artifact → both runners → structurally identical report) — live LLM runs are
   not deterministic, so this is manual, not an automated end-to-end test. Update
   `docs/PARITY.md`.
6. **Land** each phase; update CHANGELOG / platform changelogs / HANDOFF.

## Verification

- Phase 0: conformance green incl. the crew-map + `review_mode`-knob checks;
  `spec_gate` green; the spec names personas/blackboard/synthesis without engine
  tokens (`test_spec_hygiene`).
- Phase 1: Hermes pytest green; the parser captures `lens_score`/`location`/`id`; a
  saga review emits findings + `coverage` matching the framework persona-output
  schema; the `score` follows the weighted/capped + P0/P1 policy; the report shape
  carries `score` + `coverage`; **no `UCR_PROMPT_*` persona title uses a non-key
  descriptor** (`grep -ri "devil's advocate" platforms/hermes/prompts` returns
  nothing).
- Phase 2: a plugin `doc-<layer>-audit` run dispatches the crew, writes per-persona
  blackboard slots, the deterministic reduce produces the scored unified report;
  partial-crew degradation flags coverage; `single_pass` fallback works;
  conformance unaffected (platform change).
- Phase 3: report fixtures from both runners pass the framework schema check (CI);
  manual: same sample artifact → structurally identical report from both runners.

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
| R8 | Non-deterministic panel → flapping gate | Gate = deterministic `sdd_doc_lint` floor + no unresolved P0/P1; LLM score is advisory only (Scoring section, D7). |
| R9 | Inter-agent prompt injection via the blackboard | Artifact + peer outputs are untrusted data (`SECURITY_REVIEW.md`); blackboard carries only the structured findings schema, not instructions (Resilience & security). |
| R10 | A persona-agent fails / times out | Reduce proceeds on the returned crew + records `coverage`; below quorum → low-confidence/human-review, never a silent pass (Resilience & security). |
| R11 | Create/remediate ill-defined (the headline ask) | Explicit team shapes: create = one drafter + review loop; remediate = fixer proposes + lens validates (Operations). |

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

### Pass 3 — 2026-05-25 (gap-review hardening)

A critical re-read found ten gaps; all folded in:

- **Create & remediate were unmodeled** (the headline ask was *creation* quality).
  Added the **Operations** section: create = one **drafter** + the review crew in a
  draft→review→revise loop; remediate = a **fixer** proposes patches that lenses
  **validate** — both over the same blackboard (R11).
- **Scoring/conflict/gate were hand-waved.** Added the **Scoring** section: a
  deterministic **weighted-average** of lens scores (per-layer persona weights, from
  the existing Hermes scoring tables), **P0 ⇒ fail / P1 ⇒ capped**; conflicts →
  **max-severity + union**, contested items surfaced; the **gate is the
  deterministic `sdd_doc_lint` floor + no unresolved P0/P1**, LLM score advisory —
  which is also the **reproducibility** answer for a stochastic panel (D7, R8).
- **Synthesizer conflated reduce vs LLM.** Split into a deterministic **reduce**
  (gating) + an **advisory narrative** (non-gating), generalizing `saga_reducer`.
- **No adaptation integration.** Added **D8** — a `review_mode` knob on
  `ADAPTATION_SURFACE.yaml` so a project tunes review depth/cost.
- **Partial-failure + injection.** Added **Resilience & security**: coverage +
  quorum degradation (R10); blackboard-as-untrusted-data per `SECURITY_REVIEW.md`
  (R9).
- **Migration.** D5 now pins the trigger-point default (team at gates,
  `single_pass` advisory at `on_author`) so existing plugin users aren't surprised.
- **Phase 3 verification** clarified: a deterministic **schema check on report
  fixtures** (CI) + a **manual live-run** parity comparison (LLM output isn't
  CI-deterministic) — not an automated end-to-end test.
- **Blackboard lifecycle**: transient + git-ignored under `.aidoc/review/`.
- No further findings — implementable pending D1–D8 confirmation.

## Implementation log

### Phase 0 — spec — 2026-05-25 (branch `claude/agent-team-plan`, spec `0.8.0`)

- `framework/governance/REVIEW_TEAM.md` — the engine-agnostic model: personas,
  blackboard + persona-output contract, modes, the three operations
  (create/review/remediate), the deterministic weighted/capped scoring + conflict
  policy with the structural gate as the reproducible floor, synthesis
  reduce+narrative, resilience (coverage/quorum) + security (untrusted blackboard).
- `framework/governance/REVIEW_CREWS.yaml` — closed persona set + per-layer
  `author` + `review` crews with weights (sum 100) + `default_mode: independent`.
- `ADAPTATION_SURFACE.yaml` — new `review_mode` (`team`|`single_pass`) knob (D8).
- `tests/conformance/test_review_team.py` — crews ⊆ 8 layers, personas ⊆ set,
  weights sum 100, modes valid; both governance files in `test_governance`
  EXPECTED_FILES + the README. Suite **50 → 54**. `spec_gate` green; hygiene clean
  (no engine tokens). Spec `0.7.1 → 0.8.0` (+ both FSV + 54 skills + CHANGELOG).
- **Next:** Phase 1 (Hermes *conform* to the schema) then Phase 2 (plugin *build*
  the review-team mechanism), each cut from `main` after this merges; Phase 3
  parity proof.

### Phase 1 — Hermes conform — 2026-05-26 (started, branch `claude/multi-platform-migration-AamWB`)

- **Scoring + coverage + persona-name mapping** (`mcp_server/review/review_scoring.py`
  - `tests/unit/test_review_scoring.py`, 10 tests): the deterministic weighted/capped
  readiness score (per-layer `REVIEW_CREWS.yaml` weights, renormalised over lenses
  that ran; unresolved P0 ⇒ 0, P1 ⇒ capped below gate) + `CoverageReport`
  (expected/ran/missing, quorum → low-confidence) + the framework↔Hermes persona
  alias (`chaos_engineer`→`adversary`, `chairperson`→`synthesizer`). Documented in
  `docs/architecture/REVIEW_TEAM_CONFORMANCE.md`. Additive; the working
  saga/reducer/parser untouched. Conformance 54; ruff clean; reducer/parser/scoring
  tests green (14).
- **Remaining Phase 1 (gap-closing checklist):**
  - [ ] **Parser:** capture `lens_score` + `location` + stable `id` in
        `persona_output_parser` (additive; keep existing tests green).
  - [ ] **Saga wiring:** collect per-persona `lens_score`s and call `score_review`;
        put `score` + `coverage` on `SagaReviewResult` + the reducer/synthesis summary.
  - [ ] **Report:** surface `score` + `coverage` + the framework finding fields in the
        `PERSONA_REVIEW_REPORT` / `UCR_OUTPUT_UNIFIED` shape.
  - [ ] **Crew/name reconciliation:** align `persona_mappings.yaml` review crews with
        `REVIEW_CREWS.yaml`; **retitle `THE DEVIL'S ADVOCATE` → the canonical persona
        title** across the `UCR_PROMPT_*` / `UCRem_*` prompts (gap-review finding, 11
        spots) so every persona title matches its runtime key.

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

### Pass 4 — 2026-05-26 (gap-review fold-in)

Re-reviewed the AUDIT-FIXUPS changes; folded the findings into Phase 1 scope:

- **Persona-title gap (WS-C).** The `UCR_PROMPT_*` / `UCRem_*` prompts still title the
  adversary lens `THE DEVIL'S ADVOCATE` while every other persona title matches its
  runtime key — added as an explicit Phase-1 step 5 + a Verification grep, since it is
  the framework↔Hermes persona-name reconciliation Phase 1 already owns.
- **Phase 1 made concrete.** Expanded the one-line Phase 1 step into six tracked
  sub-steps + a gap-closing checklist (parser `lens_score`/`location`/`id`; saga
  wiring of `score`+`coverage`; report shape; crew/name reconciliation; doc) so the
  remaining work is unambiguous.
- **Out of scope (noted in `AUDIT-FIXUPS-PLAN.md`):** the ADR README is silent on the
  now-required decision sequence — optional, would need another spec bump; not a
  correctness gap (the template + `DIAGRAM_STANDARDS.md` carry the rule).
- No further findings.
