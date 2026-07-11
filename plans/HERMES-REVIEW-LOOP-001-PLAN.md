# HERMES-REVIEW-LOOP-001 Plan — Phase 1: an outer review→remediate→re-review loop (H-7)

| Field          | Value                                       |
| -------------- | ------------------------------------------- |
| Task           | HERMES-REVIEW-LOOP-001 (Phase 1)            |
| Type           | feature (architecture)                      |
| Status         | ✅ SHIPPED — 2026-07-11 (`hermes/v0.11.0`, D-0063). Founder ratified the 4 design decisions + the LLM-path-only constraint ("Keep going now — build the wrapper carefully"). 565 Hermes + 208 conformance tests green; default path byte-identical. Plan-review history: READY FOR PR 2026-07-10 (4 review passes, 3 independent; gate green). |
| Depends on     | HERMES-ADAPT-ENFORCE-001 (`hermes/v0.10.0`) — `ProjectProfile.quality_loop_max_iterations` is already parsed; this consumes it |
| Feeds          | HERMES-BACKLOG **H-7** (iteration cap), **H-1** (PARTIAL_TIMEOUT write-site), **H-6.3** (iter-N vs iter-(N-1) regression detection — needs real iterations). Phase 2 (cross-invocation resume + G-R1) is a follow-up. |
| Version impact | Hermes stream only: **MINOR** (a new opt-in saga capability; the existing path is untouched — flag-gated, see Approach). No `framework/VERSION` change — the loop is an outer wrapper over the existing forward saga; the spec/schema/transition-table are unchanged. |

## Objective

Hermes's review saga is **single-pass**: fan out personas → reduce → synthesize →
CLOSE after one review (`iteration=1` hardcoded, `saga_orchestrator.py:637`). There is
**no automated review→remediate→re-review cycle** — the orchestrator never remediates,
and `sdd_remediate` is a separate human-invoked tool. So `quality_loop_max_iterations`
is parsed but bounds nothing (`profile.py:19`), and H-1/H-6.3 are dead-code-until-the-loop
(D-0050).

Phase 1 adds a **bounded, opt-in, in-process outer loop** that sequences up to
`quality_loop_max_iterations` review passes with **executor-driven** remediation
between them, terminating on PASS (CLOSED) or at the cap (PARTIAL_TIMEOUT), with a
SOFT_DEADLINE break-circuit. **Not a conformance fix** — the graceful-degrade
allowance (`REVIEW_SAGA.md:152`) already makes Hermes's single-pass conformant; this
is a *parity enhancement* toward the plugin autopilot loop.

### Corrected mechanism (post independent review — the first draft was unbuildable)

The independent Pass 2 established that the naïve "refactor the linear tail into a
`while` that re-enters the fan-out" **cannot work**: (1) the transition table is
strictly forward — `SYNTHESIZED→{CLOSED}` only, no edge back to `FANOUT_STARTED`, and
`can_transition` **raises** on an illegal transition (`saga_models.py:54-66,87`); and
(2) `run_remediate_fix_build` is **copy-only** — it emits a byte-identical derived copy

+ a fix *prompt* (`remediation/runner.py:1043`), and the actual fix is applied by a
**separate `run_executor` call** (`tool_registry.py:1793`). So the loop is redesigned
as an **outer wrapper**:

+ Each iteration is a **fresh forward saga run** (PREPARED→…, `iteration` threaded
  across runs) — no backward edges, table + spec unchanged.
+ The **gate + terminal decision happens at `FANIN_REDUCED`** (after
  `_compute_review_score`, `:907`, and **before** the `SYNTHESIZED` transition,
  `:914`) — the only run-state from which both `SYNTHESIZED→CLOSED` (continue) and
  `→PARTIAL_TIMEOUT` (cap) are legal edges.
+ Between failing iterations the wrapper drives **both** the remediation runner (for
  the fix prompt + `_remediate_vN` derived copy) **and** `run_executor` (to apply the
  fix to that copy), then **rebuilds `sections` from the derived copy path** for the
  next pass (`_build_review_sections_from_document`) — the fan-out reads `sections`
  captured once, not `document_path`, so re-reading the original would re-review a
  stale body.

## Scope

**In (Phase 1, Hermes-only):**

+ **Opt-in automated loop, flag-gated OFF by default.** A new capability engaged only
  when the caller opts in (see Design decision 1). When OFF, the existing
  fan-out→…→CLOSED path is **byte-identical** to today (the entire new block —
  gate eval, remediation, PARTIAL_TIMEOUT — is skipped). The manual
  `sdd_review`/`sdd_remediate` tools stay human-gated and unchanged.
+ **Outer loop** (up to `quality_loop_max_iterations`): run a fresh single-pass saga
  → at `FANIN_REDUCED`, evaluate the gate; **PASS** → `SYNTHESIZED`→`CLOSED`, done;
  **FAIL & iteration < max** → CLOSE this run, drive remediation (runner + executor),
  rebuild sections, `iteration++`, next run; **FAIL & iteration == max** →
  `FANIN_REDUCED`→`PARTIAL_TIMEOUT` (cap).
+ **Consume `quality_loop_max_iterations`** from `ProjectContext.profile`
  (`profile.py:53`, default 3, range 1-10) — threaded from the handler
  (`tool_registry.py:1481`).
+ **Executor-driven remediation between iterations** — `run_remediate_fix_build`
  (`remediation/runner.py:987`) for the prompt + copy, then `run_executor`
  (already imported + used at `saga_orchestrator.py:14/439`) to apply it; then
  `_build_review_sections_from_document` on the `_remediate_vN` copy.
+ **Iteration bump + per-iteration journal (LB-7)** — thread `iteration` across runs.
  **Critical:** `review_run_id` is computed from stable inputs — `document_fingerprint
  = doc_type:len(sections):len(personas)`, `personas`, and an **hour-granularity**
  `_time_bucket()` (`saga_orchestrator.py:607-608`) — so a structure-preserving fix in
  the same clock hour yields an **identical** `review_run_id` and journal path, and
  `create_saga_journal` overwrites with no existence guard (`saga_journal.py:60-66`) —
  iteration 2 would clobber iteration 1's journal, destroying the multi-iteration audit
  trail and the H-6.3 iter-N-vs-iter-(N-1) comparison. **Fix:** thread `iteration` into
  the `review_run_id` inputs (or the journal filename, e.g. `…_iter{N}_…`) so each pass
  writes a **distinct** journal. `SagaRunState.iteration` already exists
  (`saga_models.py:42`).
+ **SOFT_DEADLINE break-circuit** — monitor wall-clock against a Hermes SOFT_DEADLINE
  (≥300s buffer, `REVIEW_SAGA.md:120`); on overrun at a boundary, write PARTIAL_TIMEOUT
  from `BRANCH_COMPLETED`/`FANIN_REDUCED` (legal edges). Mirror
  `saga_driver.check_break_circuit` (`saga_driver.py:346`).
+ **New conformance** — a **real** Hermes multi-iteration journal (`iteration>1` +
  a PARTIAL_TIMEOUT write) validated against `saga.schema.json`, extending
  `SagaRealJournalConformance` (`test_saga_lifecycle_parity.py:187`, currently a
  hardcoded single pass); + the Hermes saga-invariant mirror of
  `test_invalid_transition_raises` (the D-0050 residual).

**Operating constraint (must be stated — it bounds the feature):** the loop needs a
PASS/FAIL **gate**, which requires a **numeric `review_score`**.
`_compute_review_score` returns `None` unless the run is `saga_parallel` **with
branch-LLM enabled and a framework-crew doc-type** (`saga_orchestrator.py:514-522`).
So Phase 1 functions **only on the LLM crew-review path**; in the deterministic /
`prompt_only` path there is no score → the loop is a no-op single pass (falls back to
today's behavior). This is a real limitation, not a bug to fix here.

**Out (deferred / not this plan):**

+ **Phase 2 — cross-invocation resume + G-R1** (`resume_from_partial_timeout`,
  `saga_driver.py:362`). Phase 1 makes PARTIAL_TIMEOUT *writable*; resuming it in a
  later invocation is Phase 2.
+ **The `create`/draft step** — Phase 1 loops review→remediate on an existing document.
+ **Framework-spec / transition-table changes** — the outer-wrapper design needs
  none (each run is forward; PARTIAL_TIMEOUT is already an accepted target from the
  fan-out states, `saga_models.py:60-61`).
+ **A PASS/FAIL gate for the deterministic path** — out (would need a score model the
  deterministic path lacks).
+ The branch-scoped `BRANCH_COMPENSATING` fixer-arrow spec question
  (`HERMES-BACKLOG.md:180`) — orthogonal, not gating (D-0050).

## Design decisions (surfaced for plan review / founder)

1. **Loop trigger / off-switch.** Opt-in via a new `quality_loop: bool` arg on
   `sdd_review` (`saga_parallel` mode). When false → the existing straight-to-CLOSED
   path runs untouched (NOT "max_iterations=1" — with the gate active even max=1 would
   newly write PARTIAL_TIMEOUT on a failing doc; the off-switch must bypass the whole
   new block). **Recommend** the flag gates the entire loop block.
2. **Cap-with-fail terminal.** At `iteration == max` with a failing gate: write
   **PARTIAL_TIMEOUT** (matches the knob's spec wording + enables Phase-2 resume) from
   `FANIN_REDUCED`. Keep **ESCALATED** for the below-quorum path (unchanged).
3. **Auto-remediation & the human-gated philosophy.** The loop is a distinct opt-in
   *automated* mode (like the plugin autopilot); the manual tools stay human-gated —
   nothing auto-applies fixes unless a caller opts into the quality loop.
4. **SOFT_DEADLINE value.** Implementation-defined Hermes constant, ≥300s buffer;
   number set in implementation.

## Approach

1. **Outer wrapper** — a new function (e.g. `run_review_quality_loop`) around the
   existing `run_project_review_build_saga` (`:565`). It owns the `while iteration ≤
   max` loop, the remediation-between-iterations, and the iteration counter; each
   pass calls the (lightly extended) saga.
2. **Gate hook in the saga run** — extend the run so that at `FANIN_REDUCED` (after
   `_compute_review_score`, `:907`) it returns the score + whether the gate passed,
   and — when told it is the final iteration and the gate failed — transitions
   `FANIN_REDUCED→PARTIAL_TIMEOUT` instead of `→SYNTHESIZED→CLOSED`. Default (loop off)
   → the current unconditional `SYNTHESIZED→CLOSED` (`:914/:925`) is unchanged.
3. **Threading** — pass `quality_loop_max_iterations` (from `ctx.profile`, handler
   `:1481/1496`) + the opt-in flag into the wrapper.
4. **Remediation apply** — wrapper calls `run_remediate_fix_build` then `run_executor`
   (via `asyncio.run`, as `:439`) against the `_remediate_vN` copy dir, then rebuilds
   `sections` via `_build_review_sections_from_document(derived_copy)` for the next pass
   (note: that helper currently lives in `cli/main.py:743` — the impl should import it
   from there or lift it to a shared module).
5. **Per-iteration journal (LB-7) / SOFT_DEADLINE** — add `iteration` to the
   `review_run_id`/journal-filename discriminator so each pass writes a distinct journal
   (else iterations collide, LB-7); record iteration boundaries + the PARTIAL_TIMEOUT
   write; a `check_break_circuit`-equivalent + Hermes SOFT_DEADLINE constant.
6. **Tests** — unit: loop-off byte-identical single pass; FAIL→remediate→PASS closes;
   cap→PARTIAL_TIMEOUT; SOFT_DEADLINE→PARTIAL_TIMEOUT; deterministic path (no score) →
   single pass. Conformance: real multi-iteration Hermes journal + the invariant mirror.

## Verification

+ `cd platforms/hermes && python3 -m pytest -q` — green (+ loop unit tests).
+ `python3 -m unittest discover -s tests/conformance` — green, incl. the new real
  multi-iteration Hermes journal + the invariant mirror; the transition-table parity
  guard stays green (table unchanged).
+ Manual: a failing artifact on the `saga_parallel`+LLM path with
  `quality_loop_max_iterations: 2` → remediate + re-review, closing on PASS or writing
  PARTIAL_TIMEOUT at the cap; loop-off → identical to today's single pass.

## Risks

| Risk | Mitigation |
|------|------------|
| **The transition table is forward-only** (LB-1) — an internal re-fanout would raise | Outer-wrapper design: each iteration is a fresh forward run; PARTIAL_TIMEOUT is written from `FANIN_REDUCED`/`BRANCH_COMPLETED` (legal edges). No table/spec change. |
| **`run_remediate_fix_build` is copy-only** (LB-2) — it doesn't apply the fix | The wrapper also drives `run_executor` with the fix prompt against the derived copy (mirrors the manual flow `tool_registry.py:1793`); a runner-only loop would re-review an unchanged copy and always hit the cap. |
| **No PASS/FAIL gate today; score is `None` off the LLM path** (LB-4) | Introduce the score-vs-threshold gate at `FANIN_REDUCED`; document that Phase 1 functions only on `saga_parallel`+LLM+framework-crew; the deterministic path falls back to a single pass (no-op). |
| **`sections` captured once** (LB-5) | Rebuild `sections` from the `_remediate_vN` copy via `_build_review_sections_from_document` each pass — not a re-read of `document_path`. |
| **"Loop off" must be byte-identical** (LB-6) | The opt-in flag bypasses the entire new block (gate + remediation + PARTIAL_TIMEOUT); off ≠ max=1. Unit-test the off path against current output. |
| **Per-iteration journal collision** (LB-7) — identical `review_run_id` across passes overwrites the prior journal | Thread `iteration` into the `review_run_id`/journal filename so each pass writes a distinct journal; unit-test that iter-1 and iter-2 journals both persist (the H-6.3 prerequisite). |
| Grafting destabilizes the single-pass path | Loop-off default + flag gate; the existing `_safe_transition` chain to CLOSED is untouched when off. |

## Docs to update

+ `platforms/hermes/CHANGELOG.md` + `VERSION` (MINOR), root `CHANGELOG.md`,
  `plans/HERMES-BACKLOG.md` (H-7 Phase-1 shipped; H-1 partial; H-6.3 unblocked;
  the LLM-path constraint), `docs/PARITY.md` (Hermes gains a bounded LLM-path review
  loop), a `plans/DECISIONS.md` entry (trigger, cap-terminal, auto-remediate mode,
  the LLM-path constraint).

## Claim ledger

| #   | Claim | Symbol | Citation |
| --- | ----- | ------ | -------- |
| 1 | the saga hardcodes `iteration=1` (never incremented — the single-pass tell) | `iteration=1,` | platforms/hermes/src/mcp_server/review/saga_orchestrator.py:637 |
| 2 | the saga entry point the wrapper calls per iteration | `def run_project_review_build_saga` | platforms/hermes/src/mcp_server/review/saga_orchestrator.py:565 |
| 3 | the review score is computed at FANIN_REDUCED (the gate input; the decision must be here) | `review_score = _compute_review_score(` | platforms/hermes/src/mcp_server/review/saga_orchestrator.py:907 |
| 4 | the flow transitions SYNTHESIZED→CLOSED unconditionally today (no gate) | `_safe_transition(journal_path=journal_path, target="CLOSED")` | platforms/hermes/src/mcp_server/review/saga_orchestrator.py:925 |
| 5 | `_compute_review_score` returns None off the LLM/framework-crew path (the gate operating constraint, LB-4) | `def _compute_review_score` | platforms/hermes/src/mcp_server/review/saga_orchestrator.py:507 |
| 6 | the transition table is strictly FORWARD — SYNTHESIZED→{CLOSED} only, no backward edge (LB-1) | `"SYNTHESIZED": {"CLOSED"},` | platforms/hermes/src/mcp_server/review/saga_models.py:62 |
| 7 | PARTIAL_TIMEOUT IS a legal target from FANIN_REDUCED (the cap write-site) | `"FANIN_REDUCED": {"SYNTHESIZED", "PARTIAL_TIMEOUT"},` | platforms/hermes/src/mcp_server/review/saga_models.py:61 |
| 8 | `transition_run_status` raises on an illegal transition (so an internal re-fanout would raise; `can_transition` returns False) | `def transition_run_status` | platforms/hermes/src/mcp_server/review/saga_models.py:91 |
| 9 | `run_remediate_fix_build` is COPY-ONLY — applies no fix (LB-2) | `"none (copy-only deterministic baseline)"` | platforms/hermes/src/mcp_server/remediation/runner.py:1043 |
| 10 | it emits a fix PROMPT (the executor applies it) | `report_text = _build_remediate_fix_prompt` | platforms/hermes/src/mcp_server/remediation/runner.py:1050 |
| 11 | the manual flow applies the fix via a SEPARATE run_executor call (the loop must too) | `prompt=fix_result.report_text,` | platforms/hermes/src/mcp_server/tool_registry.py:1793 |
| 12 | the orchestrator already imports/uses run_executor (so the wrapper can drive it) | `run_executor` | platforms/hermes/src/mcp_server/review/saga_orchestrator.py:14 |
| 13 | `SagaRunState.iteration` exists (journal round-trips it) | `iteration: int = 1` | platforms/hermes/src/mcp_server/review/saga_models.py:42 |
| 14 | the profile parses `quality_loop_max_iterations` (default 3) but nothing consumes it | `quality_loop_max_iterations: int` | platforms/hermes/src/mcp_server/profile.py:53 |
| 15 | `ctx.profile` is reachable from the sdd_review handler (where to thread the knob) | `ctx.profile` | platforms/hermes/src/mcp_server/tool_registry.py:1496 |
| 16 | the plugin reference outer loop (mirror the structure, not the subprocess mechanism) | `while saga["status"] not in {"CLOSED", "ESCALATED", "PARTIAL_TIMEOUT"}:` | platforms/claude-code-plugin/tools/saga_driver.py:677 |
| 17 | the plugin break-circuit (SOFT_DEADLINE → PARTIAL_TIMEOUT) to mirror | `def check_break_circuit` | platforms/claude-code-plugin/tools/saga_driver.py:346 |
| 18 | the plugin resume-walk / G-R1 (Phase 2 — explicitly out) | `def resume_from_partial_timeout` | platforms/claude-code-plugin/tools/saga_driver.py:362 |
| 19 | the spec's SOFT_DEADLINE MUST (≥300s buffer) | `SOFT_DEADLINE` | framework/governance/REVIEW_SAGA.md:120 |
| 20 | the graceful-degrade allowance — Hermes single-pass is ALREADY conformant (enhancement, not fix) | `graceful-degradation` | framework/governance/REVIEW_SAGA.md:152 |
| 21 | the knob's spec: default 3, range 1-10, "cycles before PARTIAL_TIMEOUT" | `quality_loop_max_iterations` | framework/governance/ADAPTATION_SURFACE.yaml:77 |
| 22 | the sdd_review handler (where the loop trigger + profile thread in) | `if name == "sdd_review":` | platforms/hermes/src/mcp_server/tool_registry.py:1481 |
| 23 | the real-journal conformance test currently walks a hardcoded single pass (to extend) | `SagaRealJournalConformance` | tests/conformance/test_saga_lifecycle_parity.py:187 |
| 24 | `review_run_id` is built from stable inputs + hour-granularity time_bucket → identical across iterations (the LB-7 collision source; needs an `iteration` discriminator) | `review_run_id = deterministic_review_run_id(` | platforms/hermes/src/mcp_server/review/saga_orchestrator.py:608 |
| 25 | `create_saga_journal` writes with no existence guard (so a colliding run_id overwrites) | `def create_saga_journal` | platforms/hermes/src/mcp_server/review/saga_journal.py:60 |

## Review log

### Pass 1 — 2026-07-10 — self-review (draft)

+ Scoped to Phase 1 (the loop + knob + SOFT_DEADLINE/PARTIAL_TIMEOUT); resume/G-R1 →
  Phase 2. Founder chose the "big" auto-remediate loop over the small break-circuit slice.
+ Open questions for the independent pass: remediation-runner signature, artifact
  re-read, PARTIAL_TIMEOUT transition validity, MINOR vs MAJOR.

### Pass 2 — 2026-07-10 — independent (fresh-context subagent) + fold

The independent reviewer verified all 21 (then) ledger rows and found the first
draft's **core mechanism unbuildable** — 2 blockers + 4 majors, all folded (this was a
redesign, not a patch):

+ **LB-1 (blocker) — the transition table is forward-only.** No backward edge to the
  fan-out; `can_transition` raises. **Folded:** redesigned as an **outer wrapper**
  sequencing *fresh forward runs* (no table/spec change, MINOR preserved) instead of an
  internal `while` re-entering the fan-out. New ledger rows 6/7/8.
+ **LB-2 (blocker) — `run_remediate_fix_build` is copy-only** (`"applied_changes:
  none"`); the fix is a separate `run_executor` apply. **Folded:** the wrapper drives
  BOTH the runner and `run_executor`; rows 9/10/11/12.
+ **LB-3 — PARTIAL_TIMEOUT unreachable from SYNTHESIZED.** **Folded:** the gate/cap
  decision moved to `FANIN_REDUCED` (before SYNTHESIZED); row 7.
+ **LB-4 — no gate exists + score is `None` off the LLM path.** **Folded:** added the
  operating-constraint section + risk + row 5 — Phase 1 functions only on
  `saga_parallel`+LLM+framework-crew; deterministic path falls back to single pass.
+ **LB-5 — `sections` captured once; remediation writes a new path.** **Folded:**
  rebuild `sections` from the `_remediate_vN` copy each pass.
+ **LB-6 — "off = max=1" is wrong.** **Folded:** the opt-in flag bypasses the whole
  block; off ≠ max=1 (Design decision 1 + risk).
+ Row 5's mis-citation (was `:22`) corrected to the `_compute_review_score` def.

**Open for Pass 3:** does the outer-wrapper + FANIN_REDUCED-gate + executor-apply
redesign hold with no new inconsistency; are rows 5-12 accurate; and is the
LLM-path-only operating constraint stated correctly (does the wrapper degrade safely
to a single pass when the score is None)?

### Pass 3 — 2026-07-10 — independent confirmation (fresh-context subagent) + fold

A second fresh-context reviewer confirmed the outer-wrapper redesign resolves LB-1
through LB-6 (all verified from source: forward-only table sidestepped by fresh runs;
copy-only runner + separate executor apply; FANIN_REDUCED is the only state with both
`→SYNTHESIZED` and `→PARTIAL_TIMEOUT` legal; score-None LLM-path constraint; sections
captured-once; off=flag). It traced every loop path and found **no illegal transition**.
It found **one NEW load-bearing gap the redesign introduced:**

+ **LB-7 — per-iteration journal collision.** `review_run_id` is computed from stable
  inputs (`doc_type:len(sections):len(personas)`, `personas`, hour-granularity
  `_time_bucket()`, `saga_orchestrator.py:607-608`), so a structure-preserving fix in
  the same clock hour yields an **identical** journal path, and `create_saga_journal`
  overwrites with no existence guard — iteration 2 clobbers iteration 1's journal,
  defeating both the multi-iteration-journal conformance deliverable AND the H-6.3
  iter-N-vs-iter-(N-1) unblock this plan claims to feed. Threading `iteration` into
  `SagaRunState` alone does NOT fix it (it's not an input to the run_id/filename).
  **Folded:** Scope §In journal bullet + Approach step 5 + a Risk row now require an
  `iteration` discriminator in the `review_run_id`/journal filename so each pass writes
  a distinct journal; new ledger rows 24/25.

Minor non-blocking notes folded: `_build_review_sections_from_document` lives in
`cli/main.py:743` (import-path note in Approach step 4); row-8 wording corrected
(`transition_run_status` raises, not `can_transition`). Acknowledged (not changed): a
failing non-final iteration still runs the full aggregate synthesis before CLOSE —
wasted work, not incorrect.

**Open for Pass 4:** does the LB-7 fold (per-iteration journal discriminator) fully
close the collision with no new inconsistency, and are rows 24/25 accurate? (This is
the third independent pass because Pass 3 surfaced a new load-bearing finding —
verified-planning requires cycling until an independent pass returns zero.)

### Pass 4 — 2026-07-10 — independent confirmation (fresh-context subagent)

A third fresh-context reviewer confirmed the **LB-7 fold is correct and complete with
zero load-bearing findings**, verified from source:

+ The collision is real (`review_run_id` payload `path|fingerprint|persona_key|time_bucket`,
  `saga_models.py:76-79`, with no `iteration` input; hour-granularity bucket) and the
  fix is **sufficient + feasible** — there are exactly two journal-path derivation
  sites (`saga_orchestrator.py:614`, `saga_journal.py:61`) and **both** key off
  `review_run_id`, so threading `iteration` into the run_id fixes both atomically;
  `load_saga_journal` takes an explicit path (no re-derivation) and the resume path
  becomes *safer*. Rows 24/25 accurate.
+ **No new inconsistency:** the run_id/filename are Hermes-internal (not in `framework/`
  or `saga.schema.json`, which validates content not filenames) → MINOR / no-spec-change
  preserved; distinct per-iteration journals are precisely the precondition for both the
  "real multi-iteration journal" conformance deliverable and the H-6.3 unblock — the fold
  and the goal reinforce each other.
+ Re-scanned LB-1/LB-2/LB-3/LB-4/LB-5/LB-6 against source — all folded consistently
  across Scope/Approach/Design/Risks/ledger; every loop path traced; **no remaining
  load-bearing gap** makes Phase 1 unbuildable or unsafe.

**Result:** ready. Claim ledger has zero UNVERIFIED rows and the gate passes; four
review passes (three independent, fresh-context) drove the load-bearing count to zero
— Pass 2 forced a full mechanism redesign (2 blockers), Pass 3 caught the journal
collision, Pass 4 confirmed clean. **Two open items belong to the founder, not
plan-review:** (1) ratify the 4 design decisions (loop trigger, cap-terminal,
auto-remediate mode, SOFT_DEADLINE value); (2) accept the **LLM-path-only operating
constraint** — Phase 1's auto-remediate loop functions only on the `saga_parallel`+LLM+
framework-crew path (the deterministic/`prompt_only` path has no score → single-pass
no-op). Implementation should begin only after that ratification.
