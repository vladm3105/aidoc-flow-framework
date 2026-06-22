# SAGA-PARITY-001 Phase 4 — propagate the saga driver to the EARS..IPLAN autopilots

| Field          | Value |
| -------------- | ----- |
| Task           | SAGA-PARITY-001-PHASE-4 |
| Type           | refactor |
| Status         | READY FOR PLAN PR — 2026-06-21 (converged at Pass 3; see Review log) |
| Parent         | SAGA-PARITY-001 (`plans/SAGA-PARITY-001-PLAN.md`); pattern from Phase 2 Amendment 1 (`plans/SAGA-PARITY-001-PHASE-2-AMEND-001-PLAN.md`, PR #92) |
| Depends on     | Phase 2 Amendment 1 (preemptive `tools/saga_driver.py`) — done. BRD + PRD autopilots already migrated. |
| Feeds          | Unblocks MODEL-PRECHECK-ROLLOUT (parked — needs a uniform autopilot corpus). Hermes H-1/H-2 batch references "plugin Phase 4 should land first" (`HERMES-BACKLOG.md:79`). |
| Version impact | Claude Code plugin MINOR (`0.20.1 → 0.21.0`); no framework spec change |

## Objective

Bring the **6 remaining layer autopilots** — `doc-{ears,bdd,adr,spec,tdd,iplan}-autopilot`
— to the preemptive saga-driver pattern already shipped for `doc-brd-autopilot`
and `doc-prd-autopilot`. Today these 6 SKILLs describe **only** a legacy
in-session numbered `## Workflow` (Generation → Validation → Audit↔fix via
`../doc-<layer>/SKILL.md` references) with **no saga-driver invocation**. The
acceptance harness hides this: it invokes `saga_driver.py` **directly** per
layer, explicitly "NOT through the `doc-<layer>-autopilot` SKILL"
(`tests/scripts/test-acceptance.sh:1139`). So what a human triggers when they
run `/aidoc-flow:doc-bdd-autopilot` diverges from the saga-driven path the
suite proves, and these 6 SKILLs are effectively untested. Phase 4 closes that
divergence and makes the autopilot corpus uniform.

## Scope

**In:**

- Rewrite the `## Workflow` section of the 6 SKILLs to the
  proven two-subsection shape (verbatim pattern from `doc-prd-autopilot`):
  - `### Saga-driven generation loop (review_mode: team)` — Step 1 invoke the
    driver via Bash (`--layer <NN_TYPE> --threshold 90`), Step 2 report from
    `.aidoc/review/<NN_TYPE>/<ARTIFACT_ID>/saga.json`, Step 3 index update on
    `CLOSED`.
  - `### Linear Pipeline (review_mode: single_pass)` — the existing numbered
    steps, demoted under this heading + the standard "produces no saga.json;
    the harness's saga-journal check fails the layer; manual-dry-run only"
    caveat.
- A conformance test asserting all 8 layer autopilots (the 2 done + 6 new)
  carry the saga-driven `### Saga-driven generation loop` subsection with the
  correct `--layer <NN_TYPE>` argument, and retain the `single_pass` fallback
  subsection. This is the anti-drift guard + the mechanical closure of the
  "autopilot prose untested" gap.
- **Frontmatter `adapts:` fix** (Pass-2 R6.1): add `review_mode` to the
  `adapts:` list of the 6 migrated SKILLs (they now branch on `review_mode`,
  a valid closed-surface knob — `ADAPTATION_SURFACE.yaml:67`), AND reconcile
  `doc-prd-autopilot` to add `review_mode` too (it already branches on it but
  was missing the declaration — a pre-existing inconsistency vs
  `doc-brd-autopilot`, which already has it). 7 frontmatter edits;
  `test_adaptation.py::test_declared_adapts_are_in_surface` keeps them valid.
- Docs of record + plugin MINOR bump.

**Out of scope (deferred):**

- `MODEL-PRECHECK-ROLLOUT` — parked; resume against the uniform corpus this
  produces (`plans/MODEL-PRECHECK-ROLLOUT-PLAN.md`, Pass 4-6 findings recorded).
- Any `saga_driver.py` logic change — the driver already supports all 8 layers
  (`--layer` + `_LAYER_CREWS`); this is SKILL-only.
- The `chg` autopilot (already saga-driven; not a layer autopilot).
- Hermes-side parity (H-1/H-2) — separate batch, gated on this per backlog.
- Closing the *live* autopilot-vs-harness test gap by having the harness invoke
  the SKILL instead of the driver — the harness's direct-driver call is
  deliberate (AMEND-001 "autopilot is the single source of truth … harness
  invokes ONLY doc-<layer>-autopilot" was the *intent*, but the current harness
  still shells the driver directly). Whether to re-point the harness at the
  SKILL is a separate decision; this plan makes the SKILLs *correct* and guards
  them structurally. Flag, do not bundle.

## Approach / Design

### Source → target (per layer)

| Layer | `--layer` arg | Index file (Step 3) | SKILL |
| ----- | ------------- | ------------------- | ----- |
| EARS  | `03_EARS`  | `docs/03_EARS/EARS-00_index.md`   | `doc-ears-autopilot` |
| BDD   | `04_BDD`   | `docs/04_BDD/BDD-00_index.md`     | `doc-bdd-autopilot` |
| ADR   | `05_ADR`   | `docs/05_ADR/ADR-00_index.md`     | `doc-adr-autopilot` |
| SPEC  | `06_SPEC`  | `docs/06_SPEC/SPEC-00_index.md`   | `doc-spec-autopilot` |
| TDD   | `07_TDD`   | `docs/07_TDD/TDD-00_index.md`     | `doc-tdd-autopilot` |
| IPLAN | `08_IPLAN` | `docs/08_IPLAN/IPLAN-00_index.yaml` | `doc-iplan-autopilot` |

### Transformation rules

1. The new `### Saga-driven generation loop (`review_mode: team`)` (heading
   backtick-wrapped, as in the references) is the **`doc-prd-autopilot` block —
   that is the byte-source, NOT `doc-brd-autopilot`** (Pass-2 R3). BRD carries
   an extra `> **MANDATORY — DO THIS FIRST.**` blockquote that PRD does not;
   that blockquote is **intentionally NOT propagated** (PRD's leaner Step-1
   phrasing is canonical). Three substitutions: `02_PRD` → `<NN_TYPE>`, the
   report path `02_PRD` → `<NN_TYPE>`, and the index file + downstream-entry
   wording → the layer's row above. Threshold stays `90` (R2-verified: all 6
   declare `default 90`; harness hard-codes `--threshold 90`).
2. The existing numbered `## Workflow` steps move **verbatim** under
   `### Linear Pipeline (review_mode: single_pass)` — no content rewrite, only
   re-heading + the standard caveat paragraph. This preserves each layer's
   real authoring detail (e.g. IPLAN's test-first manifest, EARS's pattern
   categorization) as the single_pass fallback.
3. No change to `## Purpose`, `## Skill Dependencies`, `## Input Contract`,
   `## Smart Document Detection`, `## Execution Modes`, `## Quality Gates`,
   `## Error Handling`, `## Adaptation`, `## Related Resources` (Pass-2 R1/R5
   verified clean — the legacy Workflows are self-contained numbered lists that
   move verbatim; IPLAN's sub-type logic lives in `doc-iplan/SKILL.md`, not the
   autopilot). The body edit is the `## Workflow` restructure **plus** the
   one-line `adapts:` frontmatter fix above. Note (Pass-2 R6.4): the `VERSION`
   bump separately triggers `sync-version-refs.sh`, which mechanically rewrites
   the `version: "…"` frontmatter line in all 52 SKILLs — so these 6 files'
   diffs include that line too; not a content change, just flagged so the diff
   isn't a surprise.

### Why MINOR, not PATCH

Each of the 6 autopilots changes observable behaviour in the default
`review_mode: team`: it now invokes the driver instead of drafting in-session.
That is a behaviour change for a user-facing command → plugin MINOR. (AMEND-001
was a PATCH because it was a single SKILL + an additive helper; Phase 4
propagates a behaviour change across 6 commands.) No framework-spec surface
moves, so FSV stays `0.23.0`.

## File structure

### Created

| Path | Purpose |
| ---- | ------- |
| `tests/conformance/platforms/test_autopilot_saga_parity.py` | Assert all 8 layer autopilots carry `### Saga-driven generation loop` with `saga_driver.py --layer <NN_TYPE>` + retain the `single_pass` subsection. |

### Modified

| Path | Change |
| ---- | ------ |
| `platforms/claude-code-plugin/skills/doc-{ears,bdd,adr,spec,tdd,iplan}-autopilot/SKILL.md` | `## Workflow` restructured to team + single_pass subsections + `review_mode` added to `adapts:` frontmatter (6 files). |
| `platforms/claude-code-plugin/skills/doc-prd-autopilot/SKILL.md` | `review_mode` added to `adapts:` frontmatter only (reconcile pre-existing inconsistency vs brd; Pass-2 R6.1). |
| `platforms/claude-code-plugin/VERSION` | `0.20.1 → 0.21.0` (mechanical version-sync hook also rewrites `version:` in all 52 SKILL frontmatters). |
| `platforms/claude-code-plugin/CHANGELOG.md` | `[0.21.0]` entry. |
| `plans/FRAMEWORK-TODO.md` | Close/cross-ref the F7 entry. |
| `plans/HANDOFF.md` + `plans/DECISIONS.md` | narrative + any non-obvious choice. |

## Implementation sequence

### Task 1: Conformance test first

- **Test-first — [CODE]:** author `test_autopilot_saga_parity.py` (red — the 6
  new SKILLs fail). Assert, for all 8 layer autopilots: the
  `### Saga-driven generation loop` subsection + a `saga_driver.py --layer <NN_TYPE>`
  invocation with the correct `<NN_TYPE>`, the retained `single_pass`
  subsection, AND `review_mode` present in the `adapts:` frontmatter.

### Task 2: Restructure the 6 SKILLs + reconcile PRD frontmatter

- For each of the 6: open the SKILL, lift the proven block from
  `doc-prd-autopilot` (NOT brd — no MANDATORY blockquote), substitute the layer
  row, demote the existing numbered steps verbatim under
  `### Linear Pipeline (`review_mode: single_pass`)`, and add `review_mode` to
  `adapts:`. Diff each Workflow before/after to confirm no detail dropped (R1).
- Add `review_mode` to `doc-prd-autopilot`'s `adapts:` (reconcile vs brd).
- Make the test green.

### Task 3: Version bump + docs

- Bump `VERSION`; let `sync-version-refs.sh` propagate (it also rewrites the
  `version:` frontmatter line in all 52 SKILLs). CHANGELOG `[0.21.0]`;
  FRAMEWORK-TODO close; HANDOFF; DECISIONS; CLAUDE.md "Current state".

## Verification

| #  | Check | Expected | Maps to |
| -- | ----- | -------- | ------- |
| V1 | `python3 -m pytest tests/conformance/ -q` | all pass incl. new test | Scope |
| V2 | `python3 tests/conformance/platforms/plm_lint.py --all` | clean | regression guard |
| V3 | `grep -L "### Saga-driven generation loop" skills/doc-{brd,prd,ears,bdd,adr,spec,tdd,iplan}-autopilot/SKILL.md` | empty (all 8) | Objective |
| V4 | `grep -c "saga_driver.py" skills/doc-{ears,bdd,adr,spec,tdd,iplan}-autopilot/SKILL.md` | ≥1 each | Source→target |
| V4b | `grep -L "review_mode" <(for s in brd prd ears bdd adr spec tdd iplan; do grep "adapts:" skills/doc-$s-autopilot/SKILL.md; done)` — all 8 `adapts:` declare `review_mode` | all present | adapts fix |
| V5 | **Live (user CLI, deferred):** run `/aidoc-flow:doc-bdd-autopilot` interactively → first tool call is the Bash saga-driver invocation, produces `saga.json`, reaches `CLOSED` | matches brd/prd behaviour | divergence closed |
| V6 | Full acceptance cascade (`tests/scripts/test-acceptance.sh`) still green | unchanged (harness calls driver directly; SKILL change doesn't affect it) | no-regression |
| V7 | `cat platforms/claude-code-plugin/FRAMEWORK_SPEC_VERSION` | `0.23.0` | Version impact |

## Docs to update

- [ ] `platforms/claude-code-plugin/CHANGELOG.md` — `[0.21.0]`
- [ ] `plans/FRAMEWORK-TODO.md` — close the F7/Phase-4 entry
- [ ] `plans/HANDOFF.md` — narrative + next steps
- [ ] `plans/DECISIONS.md` — any non-obvious choice
- [ ] `CLAUDE.md` "Current state" — note all 8 layer autopilots now saga-driven
- [ ] `ROADMAP.md` — move SAGA-PARITY Phase 4 to "Recently shipped" on merge

## Risks

| #  | Risk | Likelihood | Mitigation |
| -- | ---- | ---------- | ---------- |
| R1 | A legacy layer's authoring detail (e.g. IPLAN test-first manifest) lost in the re-heading | med | Move numbered steps **verbatim** under single_pass; diff each before/after to confirm no content dropped. |
| R2 | A layer's real threshold ≠ 90 or index file differs from the table | low | Task 2 verifies per-file against the existing legacy step 5 before substituting. |
| R3 | Conformance test too rigid (exact-string) → brittle | low | Assert the `--layer <NN_TYPE>` substring + subsection headers, not whole-block equality. |
| R4 | Behaviour change surprises single_pass/dry-run users | low | single_pass path retained verbatim; only the team default changes (matches brd/prd already shipped). |
| R5 | The autopilot-vs-harness live test gap remains (V5 is user-CLI) | med | Out-of-scope by decision; structural test (Task 1) + V5 manual run documented; re-pointing the harness is a separate flagged decision. |
| R6 | `adapts:` declares `review_mode` but a non-surface value slips in | low | `review_mode` IS in the closed surface (`ADAPTATION_SURFACE.yaml:67`); `test_adaptation.py::test_declared_adapts_are_in_surface` enforces; V4b checks presence. |

## Claim ledger

| #  | Claim | Citation |
| -- | ----- | -------- |
| 1  | Only brd/prd/chg autopilots invoke `saga_driver.py`; 6 layer autopilots are legacy in-session | `grep -rl saga_driver.py skills/*/SKILL.md` → brd/prd/chg only |
| 2  | Migrated pattern = `### Saga-driven generation loop (team)` + `### Linear Pipeline (single_pass)` | `skills/doc-prd-autopilot/SKILL.md:78,113`; `doc-brd-autopilot/SKILL.md:78,113` |
| 3  | Driver supports all 8 layers via `--layer NN_TYPE` + `_LAYER_CREWS` | `tools/saga_driver.py:61,628,658` |
| 4  | Harness invokes the driver directly, NOT the autopilot SKILL | `tests/scripts/test-acceptance.sh:1139,1164` |
| 5  | Per-layer index files | `grep` per SKILL (table above) |
| 6  | Phase 4 = "PRD..IPLAN propagation, inherits the preemptive-driver pattern" | `plans/SAGA-PARITY-001-PHASE-2-AMEND-001-PLAN.md` Feeds row |
| 7  | The 6 legacy SKILLs have the standard non-Workflow sections intact | file reads of doc-ears/iplan-autopilot (Purpose…Related Resources present) |
| 8  | All 6 legacy Workflows are clean self-contained numbered lists (verbatim-movable) | Pass-2: ears:60-76, bdd:60-76, adr:64-80, spec:60-75, tdd:63-79, iplan:66-82 |
| 9  | `review_mode` is a valid closed-surface knob; only brd-autopilot declares it; prd + the 6 don't | `ADAPTATION_SURFACE.yaml:67`; per-SKILL `adapts:` grep (Pass-2 R6.1) |
| 10 | Report path is layer-agnostic: `.aidoc/review/<layer>/<artifact_id>/saga.json` | `tools/saga_driver.py:660` (`saga_dir = … / args.layer / args.artifact_id`) |
| 11 | IPLAN sub-type (code_build/deploy) logic is in `doc-iplan/SKILL.md`, not the autopilot | Pass-2 R5: grep `code_build`/`deploy`/`sub_type` in doc-iplan-autopilot → 0 hits |
| 12 | No existing test asserts the legacy Workflow shape; canonical + vendored saga_driver are byte-identical | Pass-2 R6.3/R6.5 (`diff -q` clean) |

## Review log

### Pass 1 — 2026-06-21 — self-review (draft)

- Scoped to the minimal proven transformation (re-use brd/prd block verbatim;
  no new design) per minimal-and-realistic. 6 SKILL edits + 1 test + docs.
- Kept the harness-repoint decision OUT (the deliberate direct-driver call is
  AMEND-001's harness design); this plan makes SKILLs correct + guards them.
- Captured the live-vs-structural test distinction (V5 user-CLI, deferred) so
  "tested" isn't overclaimed — the structural test (Task 1) is the CI guard.

### Pass 2 — 2026-06-21 — independent (fresh-context subagent, against the codebase)

> Executed the pending checklist against all 6 legacy SKILLs + the 2 migrated
> references + the driver. Core mechanism verified sound; one load-bearing gap
>
> - two accuracy fixes folded in.

- **R1 (no detail lost) — CLEAR.** All 6 legacy Workflows are clean, self-contained
  numbered 5-step lists (claim 8); the verbatim move under `single_pass` is safe.
  IPLAN's test-first manifest / EARS's pattern categorization live *inside* the
  numbered steps and move cleanly.
- **R2 (threshold + index) — CLEAR.** Table fully correct; all 6 default to 90;
  IPLAN's `.yaml` index confirmed.
- **R3 (shared test) — MINOR, fixed.** Headings are backtick-wrapped (plan now
  matches); BRD has an extra `MANDATORY` blockquote PRD lacks → plan now names
  **PRD as the byte-source** and states the blockquote is not propagated.
- **R4 (driver arg/env) — CLEAR.** Env contract + report path are layer-agnostic
  (claim 10); driver supports all 8 (claim 3). No driver change.
- **R5 (IPLAN outside Workflow) — CLEAR.** Sub-type logic is in `doc-iplan/SKILL.md`,
  not the autopilot (claim 11); nothing outside `## Workflow` contradicts a
  saga default.
- **R6.1 (LOAD-BEARING) — `adapts:` `review_mode`.** The migrated Workflow
  branches on `review_mode`, but only `doc-brd-autopilot` declares it in
  `adapts:`; `doc-prd-autopilot` + the 6 don't (claim 9). → Plan now adds
  `review_mode` to the 6 + reconciles PRD (7 frontmatter edits); conformance
  guards it (V4b, R6).
- **R6.4 (minor) — version-sync.** Noted the `VERSION` bump rewrites the
  `version:` frontmatter line in all 52 SKILLs, so "pure Workflow restructure"
  was inaccurate; transformation rule 3 + Modified table now say so.
- **Corpus cross-check** (CLEANUP-PR-B item 5): NOT triggered — no
  lint/@-tag/registry/playbook change. Confirmed and moved on.
- **Verdict:** one revision cycle needed (fold R6.1 + R3 + R6.4). Done above.

### Pass 3 — 2026-06-21 — re-validation (confirm Pass-2 edits introduced nothing new)

- The `adapts:` addition is consistent with the conformance test (now asserts
  `review_mode` present) and V4b; PRD reconcile makes all 8 saga-driven
  autopilots uniform (no new split). Scope grew by 7 one-line frontmatter edits
  - 1 PRD file — still minimal-and-realistic; plugin stays MINOR.
- The PRD-byte-source clarification (R3) removes the brd/prd ambiguity for the
  implementer; no contradiction with claim 2.
- Verification matrix updated (V4b) and risks (R6) cover the new surface; docs
  list already includes CLAUDE.md.
- **Result: zero new substantive gaps. Plan CONVERGED — ready for the plan PR.**
  (CLAUDE.md per-layer-style rollout converges in 2-3; this took 3 with the
  independent pass at Pass 2.) Implementation begins only after the plan PR
  merges.
