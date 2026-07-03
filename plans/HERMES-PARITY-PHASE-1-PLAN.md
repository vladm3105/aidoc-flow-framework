# HERMES-PARITY-PHASE-1 Plan — Hermes saga state-machine conformance + enforced parity test

| Field          | Value                                       |
| -------------- | ------------------------------------------- |
| Task           | HERMES-PARITY-PHASE-1                        |
| Type           | feature                                     |
| Status         | PLANNED — 2026-07-02T21:51:39-04:00         |
| Depends on     | none |
| Feeds          | Phase 2 (playbook injection); the broader Hermes-parity arc |
| Version impact | **None** — no `framework/**` change (GATE-SPEC not triggered) and **no Hermes version bump**: Phase 1 ships a *latent* transition-table entry + a conformance test with no exercised capability; per `docs/PARITY.md`'s policy ("updates land when a platform ships a structurally different capability, not per-PR"), the Hermes bump waits for Phase 1b (the break-circuit *exercise*). A `[Unreleased]` Hermes CHANGELOG note records the conformance fix. |

## Objective

Close the smallest self-contained slice of the Hermes-parity gap: bring Hermes's
review-saga **state machine** into conformance with the spec's `REVIEW_SAGA.md`
transition table, and ship the conformance test that **enforces** it (and that
`docs/PARITY.md` already claims exists but does not). Hermes's
`_ALLOWED_TRANSITIONS` is missing the `PARTIAL_TIMEOUT` break-circuit state the
spec requires; nothing currently asserts Hermes's table against the spec. This
phase fixes both, corrects the stale `HERMES-BACKLOG.md` premise (Hermes already
has team-mode — the backlog is wrong), and lands with no LLM-content work.

## Scope

**In:**

- Add `PARTIAL_TIMEOUT` to Hermes `_ALLOWED_TRANSITIONS`
  (`platforms/hermes/src/mcp_server/review/saga_models.py:38`) so the table equals
  the spec's `REVIEW_SAGA.md` transition table (and matches the plugin's reference
  `tools/saga_driver.py:43`): reachable from `PREPARED`, `FANOUT_STARTED`,
  `BRANCH_RUNNING`, `BRANCH_COMPLETED`, `FANIN_REDUCED`; terminal (`set()`).
- New conformance test `tests/conformance/test_saga_lifecycle_parity.py` +
  fixtures `tests/conformance/fixtures/saga/{hermes,plugin}_BRD-01_saga.json` —
  both journals validate against `framework/governance/saga.schema.json`; Hermes's
  `_ALLOWED_TRANSITIONS` equals the `REVIEW_SAGA.md` table exactly. This makes the
  `docs/PARITY.md:202` claim TRUE (it is currently an over-claim — the test +
  fixtures do not exist).
- `platforms/hermes/CHANGELOG.md` `[Unreleased]` note (conformance fix; no version
  bump — see Version impact) + **honest `docs/PARITY.md` reconciliation**: mark the
  test-reference rows accurate BUT trim the false "28 orchestrator SKILLs" figure
  (real: 18 audit/fixer skills) AND correct the **Resilience row (`:182`)** which
  claims Hermes does a *preemptive* `PARTIAL_TIMEOUT` transition — that stays false
  after Phase 1 (table accepts it; orchestrator does not write it until Phase 1b).
  Do NOT let "saga row enforced" strengthen a behavioral over-claim.
- **Refresh `HERMES-BACKLOG.md`** to the corrected assessment (team-mode exists;
  the 0.32.x arc is auto-satisfied via vendored lint + shared templates; re-sequence
  the real gap into the phases below). Record the assessment + phasing as D-0045.

**Out of scope (deferred to later phases / follow-ons — enumerated, not designed):**

- **The orchestrator actively *exercising* `PARTIAL_TIMEOUT`** (writing it on a
  saga-level hard-timeout/break-circuit + resuming from it, per the plugin's
  `resume_from_partial_timeout`). Phase 1 makes the state machine *accept* the
  transition (the parity contract); wiring the orchestrator's break-circuit path is
  **Phase 1b** — Hermes has per-branch timeouts (`saga_orchestrator.py:375,431`) but
  no saga-level break-circuit today; adding one is a distinct, larger change.
- **`quality_loop_max_iterations` read (H-7).** The knob
  (`ADAPTATION_SURFACE.yaml:77`) governs the review→fix→re-review *remediation*
  loop, not the saga branch fan-out; its Hermes home must be confirmed before
  wiring. Deferred to Phase 1b (or its own small item) to keep Phase 1 crisp.
- **Playbook injection (H-4/H-5), calibration deltas (H-6), CHG parity (H-10),
  agent-skill modernization (H-11), lens sub-checks (H-2, subsumed by playbooks).**
  Phases 2–4 below.
- **The fixer-revisit spec question** (audit/fixer SKILLs emit
  `BRANCH_COMPLETED→BRANCH_COMPENSATING` etc. not in `_ALLOWED_TRANSITIONS`) — a
  plugin-side SKILL-vs-spec question, not Hermes-parity; noted, not resolved here.
- **The whole D-0038…D-0044 arc** — AUTO-SATISFIED for Hermes (vendored
  `sdd_doc_lint` + shared `framework/layers/` templates); no Hermes-native code.

## Approach / Design (D-0045)

### Corrected parity assessment (supersedes the stale HERMES-BACKLOG premise)

An independent assessment (2026-07-02) established, with file-level evidence, that
the `HERMES-BACKLOG.md` (dated 2026-06-11) is wrong on its central premise:

- **Hermes already has team-mode** — a working review-saga orchestrator with
  per-persona parallel branch fan-out (`saga_orchestrator.py:526,619`), crew
  mapping (`persona_mappings.yaml`) reconciled to `framework/governance/REVIEW_CREWS.yaml`
  (`review_scoring.py:54`), MCP-wired as `sdd_review` with a `saga_parallel`
  mode. H-4's "team-mode not implemented" is **false**.
- **The entire 0.32.x arc is AUTO-SATISFIED** for Hermes: Hermes vendors
  `sdd_doc_lint` byte-identical (so element coverage / provisional IDs / reuse /
  YAML-BDD-schema / STRUCT01 ride along) and consumes the shared `framework/layers/`
  templates (so advisory scores / sketch roadmap ride along). None of D-0038…D-0044
  needs Hermes-native code.
- **The real gap is older debt:** playbook injection (Hermes injects persona files,
  not the per-`(layer,lens)` `framework/playbooks/` — zero playbook code) + saga
  completeness (missing `PARTIAL_TIMEOUT`) + the calibration/CHG deltas that depend
  on playbook plumbing.

### Phasing roadmap (context; only Phase 1 is detailed/committed here)

| Phase | Scope | Depends on |
|-------|-------|-----------|
| **1 (this plan)** | saga state-machine conformance (`PARTIAL_TIMEOUT`) + enforced `test_saga_lifecycle_parity.py`; backlog refresh | — |
| 1b | orchestrator break-circuit *exercise* + resume; `quality_loop_max_iterations` read | Phase 1 |
| 2 | **playbook injection** (H-4) for BRD+PRD — inline `framework/playbooks/<NN>_<LAYER>/<lens>.md`, enforce `findings[].check`, emit `verdict.playbook_coverage`; fold H-6 (no-findings rationale / author-self-claim strip / fixer-regression) + H-2 | Phase 1 |
| 3 | playbook fan-out to the other 6 layers (H-5) + CHG crew + `09_CHG` playbooks (H-10); remove `CHG` from `HERMES_DEFERRED_LAYERS` | Phase 2 |
| 4 (optional) | `sdd-orchestrator` agent-skill v3.2 modernization (H-11) | — (independent) |

### Phase 1 design

1. **Transition table.** Extend the 5 non-terminal source states with
   `PARTIAL_TIMEOUT` and add `"PARTIAL_TIMEOUT": set()`, so Hermes's table is
   byte-equal in *content* to the spec table (`REVIEW_SAGA.md:47-57`) and to the
   plugin reference (`saga_driver.py:44-54`). `can_transition`
   (`saga_models.py:71`) then legally accepts a break-circuit write, which Phase 1b
   will produce. **G-R1 invariant** (never a `from: PARTIAL_TIMEOUT` transition)
   holds trivially in Phase 1 because nothing writes it yet; it becomes a live
   constraint in Phase 1b.
2. **Conformance test + fixtures.** Model on `test_review_report_parity.py`
   (fixtures validate against a shared schema; deterministic). The saga test: (a)
   load `saga.schema.json`, validate both fixtures; (b) import Hermes's
   `_ALLOWED_TRANSITIONS` and assert it equals the spec transition table. **The spec
   table (`REVIEW_SAGA.md:47-57`) is prose (terminal rows read `(terminal)`, cells
   are backticked comma-joined names) — not machine-parseable cleanly, so the test
   HARD-CODES the expected state→targets set** (a deliberate second-source-of-truth,
   exactly as the precedent `test_saga_driver_invariants.py:26` already does for the
   plugin). (c) For the plugin leg, **reuse/reference the existing
   `test_saga_driver_invariants.py`** (it already asserts the plugin
   `saga_driver._ALLOWED_TRANSITIONS` carries all 11 states incl. `PARTIAL_TIMEOUT`)
   rather than re-deriving it here — the new test's net-new job is the *Hermes* table
   - the two fixtures. The two fixtures are hand-authored sample journals of a normal
   BRD-01 review (`PREPARED → … → CLOSED`) — they need not exercise `PARTIAL_TIMEOUT`;
   the table just must *allow* it.
3. **Docs (no version bump — see Version impact).** Reconcile `docs/PARITY.md` in
   TWO places, honestly: (a) the test-reference rows (`:202-210`) become accurate
   once the test exists — but trim the false detail: it says the "Break-circuit
   policy" section is in "28 orchestrator SKILLs"; the real count is **18** (the 9
   `doc-*-audit` + 9 `doc-*-fixer` skills, NOT the autopilots — verified
   `grep -rl "## Break-circuit policy" platforms/claude-code-plugin/skills/`), so the
   parity test should NOT assert a 28-SKILL / autopilot presence; scope its
   assertions to the table + fixture validation and reword the prose to 18
   audit/fixer skills. (b) **`PARITY.md:182`** (Resilience row) currently claims
   Hermes does a *"preemptive transition"* to `PARTIAL_TIMEOUT` — that stays FALSE
   after Phase 1 (the table only *accepts* the state; the orchestrator never writes
   it until Phase 1b). Correct `:182` to "table accepts `PARTIAL_TIMEOUT`;
   orchestrator does not yet write it (Phase 1b)" — do NOT let the "saga parity
   enforced" update strengthen a behavioral over-claim. Then Hermes CHANGELOG
   `[Unreleased]` note; refresh `HERMES-BACKLOG.md`.

## File structure

### Created

| Path | Purpose |
| ---- | ------- |
| `tests/conformance/test_saga_lifecycle_parity.py` | enforce both platforms' saga tables vs `REVIEW_SAGA.md` + validate fixtures |
| `tests/conformance/fixtures/saga/hermes_BRD-01_saga.json` | sample conformant Hermes review journal |
| `tests/conformance/fixtures/saga/plugin_BRD-01_saga.json` | sample conformant plugin review journal |

### Modified

| Path | Change |
| ---- | ------ |
| `platforms/hermes/src/mcp_server/review/saga_models.py` | add `PARTIAL_TIMEOUT` to `_ALLOWED_TRANSITIONS` (5 sources + terminal) |
| `platforms/hermes/CHANGELOG.md` | `[Unreleased]` conformance-fix note (no version bump) |
| `docs/PARITY.md` | saga row now enforced (the `test_saga_lifecycle_parity.py` reference becomes accurate) |
| `plans/HERMES-BACKLOG.md` | corrected premise + re-sequenced phases |
| `plans/DECISIONS.md` | D-0045 (assessment + phasing) |
| `plans/FRAMEWORK-TODO.md` / `plans/HANDOFF.md` | pointers |

## Implementation sequence

### Task 1: conformance test first — [CODE]

- Author the fixtures + `test_saga_lifecycle_parity.py`. Confirm the table-equality
  assertion **fails** on Hermes's current table (missing `PARTIAL_TIMEOUT`) — proves
  the test catches the gap — before Task 2.

### Task 2: fix the state machine

- Add `PARTIAL_TIMEOUT` to `saga_models.py:_ALLOWED_TRANSITIONS`. Re-run: the new
  test + the full Hermes unit suite green.

### Task 3: version + docs

- Hermes CHANGELOG `[Unreleased]` note (no version bump); reconcile `PARITY.md`
  (the saga assertion now matches the shipped test); refresh `HERMES-BACKLOG.md`;
  D-0045; HANDOFF/TODO pointers.

## Verification

| #  | Check | Expected | Maps to |
| -- | ----- | -------- | ------- |
| V1 | new test on current Hermes table (pre-fix) | **fails** (no `PARTIAL_TIMEOUT`) — proves it catches the gap | test validity |
| V2 | `python -m pytest tests/conformance -q` (post-fix) | green incl. the new parity test | scope |
| V3 | `python -m pytest platforms/hermes/tests -q` (Hermes's own suite) | green — no regression from the table change | no regression |
| V4 | assert Hermes `_ALLOWED_TRANSITIONS` == plugin `saga_driver.py` table == `REVIEW_SAGA.md` | equal | parity |
| V5 | both saga fixtures validate against `saga.schema.json` | valid | fixtures |
| V6 | `platforms/hermes/FRAMEWORK_SPEC_VERSION` unchanged (`0.32.6`); no `framework/**` diff; `platforms/hermes/VERSION` still `0.3.0` | GATE-SPEC no-op; no bump | version scope |
| V7 | `grep -n "PARTIAL_TIMEOUT" docs/PARITY.md` (Resilience `:182`) + the test-ref rows | reworded to "table accepts; not yet exercised (Phase 1b)"; no "28 SKILLs" / autopilot claim remains | R4/R5 (honest docs) |

## Docs to update

- [ ] `platforms/hermes/CHANGELOG.md` — `[Unreleased]` conformance-fix note
- [ ] `docs/PARITY.md` — saga row (enforced)
- [ ] `plans/HERMES-BACKLOG.md` — corrected premise + phasing
- [ ] `plans/DECISIONS.md` — D-0045
- [ ] `plans/HANDOFF.md` — arc progress
- [ ] `CHANGELOG.md` (root) — the conformance test + fixtures (no version change)

## Risks

| #  | Risk | Likelihood | Mitigation |
| -- | ---- | ---------- | ---------- |
| R1 | Adding `PARTIAL_TIMEOUT` breaks an existing Hermes saga test that asserts the exact table shape | med | V3 runs Hermes's full suite; the plugin already carries the identical table with no ill effect; adjust any table-snapshot test to the spec shape |
| R2 | Phase 1 reads as "hollow" (table entry the orchestrator never writes) | low | it is the *parity contract* (both tables == spec) + the enforcement test that was missing; the active break-circuit exercise is a named Phase 1b, not dropped |
| R3 | Hand-authored fixtures drift from real journals | low | fixtures are schema-validated + a normal-path journal; deterministic, like the existing `test_review_report_parity` fixtures |
| R4 | `PARITY.md:202-210` describes assertions the literal test can't honor: the "Break-circuit policy in **28** orchestrator SKILLs" figure is FALSE (real: 18 `doc-*-audit`+`doc-*-fixer` skills, not autopilots) | med | only the *trim* arm is viable — the parity test asserts the table + fixture validation ONLY; Task 3 rewords `PARITY.md` prose to 18 audit/fixer skills. Do not assert a 28/autopilot presence (would fail) |
| R5 | Shipping Phase 1 while updating `PARITY.md` to "saga enforced" strengthens the false behavioral over-claim at `PARITY.md:182` ("Hermes preemptive `PARTIAL_TIMEOUT` transition") | med | Task 3 explicitly corrects `:182` to "table accepts it; orchestrator does not write it (Phase 1b)"; V7 greps `:182` post-edit |

## Claim ledger

| #  | Claim | Symbol | Citation |
| -- | ----- | ------ | -------- |
| 1  | Hermes `_ALLOWED_TRANSITIONS` has **no** `PARTIAL_TIMEOUT` (5 states + 2 terminal, none reach it) | `_ALLOWED_TRANSITIONS` | platforms/hermes/src/mcp_server/review/saga_models.py:38 |
| 2  | The spec requires `PARTIAL_TIMEOUT` reachable from PREPARED/FANOUT_STARTED/BRANCH_RUNNING/BRANCH_COMPLETED/FANIN_REDUCED, terminal-this-process | `PARTIAL_TIMEOUT` | framework/governance/REVIEW_SAGA.md:47 |
| 3  | The plugin's reference table has `PARTIAL_TIMEOUT` from those 5 + `PARTIAL_TIMEOUT: set()` | `_ALLOWED_TRANSITIONS` | tools/saga_driver.py:44 |
| 4  | `can_transition` gates on the table (so the entry is required before any write) | `can_transition` | platforms/hermes/src/mcp_server/review/saga_models.py:71 |
| 5  | `docs/PARITY.md` claims `test_saga_lifecycle_parity.py` + `fixtures/saga/` exist and assert Hermes's table == spec | `test_saga_lifecycle_parity.py` | docs/PARITY.md:202 |
| 6  | …the claim names `fixtures/saga/{hermes,plugin}_BRD-01_saga.json`, but neither the test nor that dir exists (over-claim, verified by `ls`) | `fixtures/saga` | docs/PARITY.md:205 |
| 7  | `saga.schema.json` (the shared schema the fixtures validate against) exists | `saga.schema.json` | framework/governance/saga.schema.json:1 |
| 8  | Hermes has team-mode: parallel per-persona branch fan-out orchestrator (ThreadPoolExecutor) | `run_project_review_build_saga` | platforms/hermes/src/mcp_server/review/saga_orchestrator.py:526 |
| 9  | Hermes reconciles crews to the framework `REVIEW_CREWS.yaml` | `_default_crews_path` | platforms/hermes/src/mcp_server/review/review_scoring.py:54 |
| 10 | Hermes has NO playbook injection — the parity contract marks the layer-playbooks row Hermes-deferred (zero `playbook` refs in Hermes src/skills, verified by grep) — the real Phase-2 gap | `Layer Playbooks` | docs/PARITY.md:184 |
| 11 | `quality_loop_max_iterations` is a governance knob (remediation loop, not the saga fan-out) | `quality_loop_max_iterations` | framework/governance/ADAPTATION_SURFACE.yaml:77 |
| 12 | Hermes has per-branch timeouts but no saga-level break-circuit | `timeout_seconds` | platforms/hermes/src/mcp_server/review/saga_orchestrator.py:375 |
| 13 | Model the new test on the existing report-parity fixture test | `ReviewReportParity` | tests/conformance/test_review_report_parity.py:69 |
| 14 | Hermes product version is `0.3.0` — **unchanged** by Phase 1 (latent table + test, not a shipped capability; PARITY.md capability-based bump policy) | `0.3.0` | platforms/hermes/VERSION:1 |
| 15 | Most recent decision is D-0044 → next free is D-0045 | `D-0044` | plans/DECISIONS.md:13 |

## Review log

### Pass 1 — 2026-07-02T21:51:39-04:00 — self-review

- **F1 (no version bump).** Reconsidered the Hermes bump: Phase 1 ships a *latent*
  transition-table entry + a conformance test — no *exercised* capability. Per
  `PARITY.md`'s explicit policy ("updates land when a platform ships a structurally
  different capability, not per-PR"), the Hermes version stays `0.3.0`; the bump
  waits for Phase 1b (break-circuit exercise). Revised metadata, Scope, File
  structure, Task 3, Docs. This also removes the over-claim of shipping a capability
  the orchestrator doesn't yet exercise.
- **F2 (test-vs-PARITY reconciliation flagged, R4).** `PARITY.md:202-210` describes
  the parity test as also asserting the "Break-circuit policy" section in 28 plugin
  SKILLs + schema validation — the impl must either implement exactly that or trim
  `PARITY.md` to what the test asserts (Task 3). Kept as R4 + a Task-3 step.
- Citation gate: all 15 ledger rows resolve after fixing rows 6/10/13 to concrete
  symbols.

### Pass 2 — 2026-07-02T22:20:00-04:00 — independent (fresh-context)

Fresh `code-reviewer` verified all 15 ledger citations resolve and the central
thesis holds (Hermes team-mode is real — `ThreadPoolExecutor` fan-out at
`saga_orchestrator.py:623`, MCP-wired `saga_parallel`; the two `saga_driver.py`
copies are byte-identical so the fix makes Hermes == spec == plugin; the 0.32.x
"auto-satisfied" claim checks out; GATE-SPEC is a genuine no-op). Scope judged
"thin but not hollow" and defensible. **3 load-bearing findings, all folded:**

- **F-LB1 — version-bump self-contradiction.** Pass-1's no-bump reversal didn't
  reach design-step-3 ("Bump Hermes to 0.4.0") or ledger row 14 ("→ 0.4.0 MINOR").
  Both corrected to no-bump.
- **F-LB2 — "28 orchestrator SKILLs" is false.** The "Break-circuit policy" section
  is in **18** skills (9 `doc-*-audit` + 9 `doc-*-fixer`, NOT autopilots). So the
  "implement exactly what PARITY.md describes" arm is unbuildable — only the *trim*
  arm works. Design step 3 + R4 now say: test asserts table + fixtures ONLY; reword
  PARITY prose to 18 audit/fixer skills.
- **F-LB3 — `PARITY.md:182` stays false after Phase 1.** The Resilience row claims a
  Hermes *preemptive* `PARTIAL_TIMEOUT` transition; Phase 1 only makes the table
  *accept* it. Updating PARITY to "saga enforced" without fixing `:182` would
  strengthen a behavioral over-claim. Added to Scope + design step 3 + R5 + V7.
- **Minor, folded:** reuse `test_saga_driver_invariants.py:26` for the plugin-table
  leg (don't re-derive); note the test HARD-CODES the state set (the spec table is
  prose, like the precedent); row-8 symbol → `run_project_review_build_saga`.

**Result:** ready
