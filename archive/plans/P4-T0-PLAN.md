# P4-T0 Plan — Phase 4 audit & task breakdown

| Field      | Value                                |
|------------|--------------------------------------|
| Task       | P4-T0                                |
| Depends on | Phase 3 complete (`v0.4.0`, `claude-code-plugin/v0.1.0`) |
| Status     | DONE — 2026-05-20T23:45:00Z          |
| Feeds      | P4-T1 … P4-Tn (Conformance & Independence tasks) |

## Objective

Map Phase 4 on paper before any change lands. Phase 4 (Conformance &
Independence) has **no source-content port** — both platforms are
already in place and pass the framework's 25-test conformance suite.
The work is closing the gaps the prior phases deferred:

- **Platform-level conformance tests** the suite documents as the
  "Phase 4 contract" (`tests/conformance/README.md` §Platform-
  conformance contract) but doesn't yet implement.
- **Per-platform `CHANGELOG.md`** (P2-T3 + P3-T3 Finding 2 — both
  platforms lack one despite the project-level CHANGELOG's prose).
- **CI** (no `.github/workflows/` exists; legacy workflows are
  parked in `legacy/github-workflows-disabled/`).
- **Parity report** documenting feature gaps between Hermes and the
  Claude Code plugin.
- **Deferred cleanups** rolled up: `LICENSE` file at repo root,
  expanded Hermes README, ~150 Class D stale framework refs in
  plugin skills, skill schema-version naming reconciliation.

P4-T0 produces:

1. **`plans/P4-AUDIT-conformance.md`** — an audit doc inventorying
   the conformance gap, CI gap, CHANGELOG gap, deferred cleanups,
   and parity matrix.
2. **A concrete P4-T1…P4-Tn task breakdown** appended to this plan,
   with inputs/outputs for each task.
3. **A scope-pruning statement** — which deferred items are
   Phase 4 in-scope vs deferred further (e.g. some are post-v1.0
   per D-0012, some are content-design questions outside the
   migration's mechanical scope).

P4-T0 is **paper only**; no code or test moves.

## Scope

**In:**

- Inventory the conformance-suite gap: read
  `tests/conformance/README.md` §Platform-conformance contract and
  enumerate the 4 platform-level checks it specifies; assess which
  are testable today (machine-verifiable) vs need runtime exercise.
- Inventory the CI gap: confirm absence of `.github/workflows/`;
  sample the legacy `legacy/github-workflows-disabled/` set to size
  any reusable patterns (vs greenfield workflows).
- Inventory the CHANGELOG gap: confirm both platforms lack
  `CHANGELOG.md`; decide whether Phase 4 retrofits them
  symmetrically.
- Roll up the deferred cleanups from P2-T3, P3-T1, P3-T2, P3-T3
  and classify each: **in-scope for Phase 4**, **deferred to
  Phase 5 cutover**, or **deferred to post-v1.0**.
- Scope the parity report: which categories (skill coverage,
  validation behavior, scaffold behavior, etc.); current state vs
  intended state.
- Decide the per-task breakdown (P4-T1…P4-Tn) with deliverables and
  verify gates.

**Out:**

- Any actual test, workflow, CHANGELOG, or README change (later
  P4-T*).
- Conformance test implementation (P4-T*).
- CI workflow authoring (P4-T*).
- Phase 5 cutover work (`legacy/` removal, etc.).
- Post-v1.0 capabilities (domain profiles, etc.) — those are
  ROADMAP "Post-v1.0" section, not Phase 4.

## Approach

1. **Conformance-gap inventory.** Re-read the suite's documented
   platform-conformance contract; enumerate the 4 checks; classify
   each as machine-verifiable (static structural check) or
   runtime-exercise (would require executing a platform).
2. **CI-gap inventory.** Confirm no `.github/workflows/`; sample the
   legacy workflows for any retainable patterns; design a minimal
   CI shape (conformance suite + Hermes test suite + plugin smoke
   check).
3. **CHANGELOG / README symmetry.** Both platforms missing
   `CHANGELOG.md`; Hermes README still placeholder-style. Decide
   whether Phase 4 retrofits both symmetrically.
4. **Deferred cleanups roll-up.** List every item flagged "deferred
   to Phase 4 / Phase 5 / post-v1.0" by P2/P3 and assign each.
5. **Parity report scope.** Decide what categories the parity
   report covers and what comparison framework it uses (e.g. matrix
   of: SDD layers × skill coverage per platform).
6. **Task breakdown.** Define P4-T1…P4-Tn with concrete deliverables
   and verify gates.

## Step sequence

1. Recon (done during planning).
2. Write `plans/P4-AUDIT-conformance.md`.
3. Append the P4-T1…P4-Tn task breakdown to this plan.
4. **Verify** (see below).
5. **Land** — single commit
   `docs: P4-T0 phase-4 audit + task breakdown (paper-only)`;
   update `plans/HANDOFF.md`; tick P4-T0 in
   `plans/MIGRATION_TODO.md`. Push.

## Verification

- **Paper-only.** `git status` shows changes only under `plans/`.
- **Conformance-gap completeness.** All 4 platform-conformance
  contract bullets from `tests/conformance/README.md` enumerated
  in the audit with a "in scope for Phase 4 / deferred / not
  testable static" classification.
- **CI gap acknowledged.** Audit states "no `.github/workflows/`
  exists" and sketches the intended minimal CI shape.
- **Deferred-items roll-up completeness.** Every "deferred to
  Phase 4 / 5 / post-v1.0" item flagged in P2/P3 plans appears in
  §4 with an assignment.
- **Parity report scope statement.** Audit names the categories
  and the comparison framework.
- **Open questions list ≥ 4** (canonical Phase-N count) — items
  P4-T1 design must resolve.
- **Task breakdown self-contained.** Each P4-Tn task has a one-
  paragraph statement of inputs/outputs and a verify gate.

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | Phase 4 scope creeps into Phase 5 (legacy removal) or post-v1.0 (domain profiles). | Out-clause explicitly excludes both; deferred-items roll-up classifies anything ambiguous. |
| R2 | Some platform-conformance contract bullets aren't statically testable from inside the repo (e.g. "every artifact a platform generates validates"). | Audit classifies each bullet; non-static checks deferred to runtime exercise / Phase 5 user acceptance. |
| R3 | Symmetric retrofit (Hermes CHANGELOG + README) drags substantive content work into Phase 4 that should be its own task. | Audit decides "retrofit minimal" vs "retrofit substantive" per item; Phase 4 ships minimal symmetric changes, content design is post-v1.0. |
| R4 | Parity report ends up as an unbounded comparison exercise. | Audit fixes the comparison framework (categories + dimensions) upfront; the report itself is bounded to those. |
| R5 | The audit misses a deferred item from P1/P2/P3 plans. | Cross-check against the items the recon already enumerated; verify gate requires explicit roll-up coverage. |

## Review log

### Pass 1 — 2026-05-20T23:25:00Z

- **G1. Paper-only constraint matches the P2-T0 / P3-T0 pattern.**
  Verify gate checks `git status` for no edits outside `plans/`.
- **G2. The platform-conformance contract is already documented**
  (`tests/conformance/README.md` §Platform-conformance contract,
  written at P1-T5). Phase 4 inherits that contract — the audit's
  job is to assess testability, not redesign the contract.
- **G3. CI is greenfield.** No active workflows; legacy ones parked.
  Audit should sketch the minimum CI (conformance + per-platform
  suites + plugin smoke), not port the legacy 28-workflow set.
- **G4. CHANGELOG / README symmetry is two related but distinct
  items.** Per-platform CHANGELOG is a mechanical retrofit (open
  empty changelog files); expanded Hermes README is a content
  exercise (mirror the P3-T3 plugin README's structure for Hermes).
- **G5. Deferred-items roll-up is the high-risk completeness check.**
  R5 mitigation: cross-check against the items the recon already
  surfaced. Verify gate requires explicit roll-up.
- **G6. Parity report — what's the comparison framework?** The
  natural one is the 8 SDD layers × per-platform skill/tool
  coverage. Audit fixes this upfront so P4-T1 doesn't bikeshed.
- **G7. Open-questions list anchor count = 4.** Phase 4 is simpler
  than P2/P3 (no source-content port); ≥4 questions is enough.
- **G8. Task breakdown shape.** Mirrors P3 (5 sub-tasks). Likely
  shape: T1 design → T2 platform-conformance tests → T3 CI
  workflows → T4 CHANGELOG / README symmetric retrofit + parity
  report → T5 verify → T6 close. **6 sub-tasks** if T4 and T5
  separate; or 5 if combined.

### Pass 2 — 2026-05-20T23:40:00Z

- **G9. Cross-task interaction risk.** CI (T3) consumes
  platform-conformance tests (T2). T3 design depends on T2's
  output shape. Sequence: T2 before T3.
- **G10. CHANGELOG retrofit minimal-vs-substantive.** Pass 1 G4
  said "open empty files" for the minimal version. Refine: the
  retrofit can populate Hermes' `[0.1.0]` entry with the same
  Phase 2 content already in the project-level `[0.3.0]` (just
  re-scoped to Hermes-only); same for plugin's `[0.1.0]` mapping
  to project `[0.4.0]`. Honest content, no new design. P4-T0's
  audit should call this out and let P4-T1 design decide.
- **G11. LICENSE file deferred-item — is Phase 4 the right home?**
  The LICENSE is a project-wide concern, not a per-platform retro.
  Could land in any task. Audit assigns it to Phase 4 (low risk,
  small) but allows defer-to-Phase-5 as a fallback.
- **G12. List-completeness (P2-T0 Pass 3 lesson) applies to the
  deferred-items roll-up.** Audit §4 is the explicit list.
- **G13. No new findings.** Plan is internally consistent. Ready
  to present on approval.

## Phase 4 task breakdown (resolved here, executed P4-T1..P4-T5)

After the audit (this task), Phase 4 unfolds as **5 sub-tasks**.
The shape mirrors P3 (5 sub-tasks: T1 design → T2/T3 execution → T4
verify → T5 close) but reorders to put the conformance-tests
implementation before the CI that consumes them.

- **P4-T1 — Design.** Resolve the 4–6 open questions surfaced by
  the audit (test implementation approach, CI workflow shape,
  CHANGELOG retrofit posture, parity report scope, etc.). Output:
  `plans/P4-T1-DESIGN.md`. Mirrors P2-T1 / P3-T1.
- **P4-T2 — Platform conformance tests.** Implement the
  platform-conformance contract bullets that are statically
  testable (declared `framework_spec_version`, no platform writes
  to `framework/`, expected platform structure). Test modules live
  under `tests/conformance/platforms/`. Conformance suite grows
  from 25 tests to 25 + N.
- **P4-T3 — CI workflows.** Author `.github/workflows/conformance.yml`
  (runs the shared suite on push/PR), `hermes.yml` (Hermes' own
  pytest suite), and a `plugin.yml` smoke check (manifest valid,
  no coupling regression). Greenfield — no carry-over from
  `legacy/github-workflows-disabled/`.
- **P4-T4 — Retrofits + parity report.** Symmetric retrofits per
  P4-T1's posture: Hermes + plugin each get a `CHANGELOG.md`;
  Hermes README expanded to match P3-T3's plugin README structure.
  Plus `LICENSE` at repo root (P3-T1 §Deferred R1) and the parity
  report at `docs/PARITY.md`. Larger surface than the typical
  Phase-N execution task; expect more review-pass churn.
- **P4-T5 — Verify + close.** Combined gate + close, since Phase 4
  has no large new-content delivery to verify separately. Conformance
  suite at 25 + N tests; CI workflows lint-clean; parity report
  validated against actual content. Then `CHANGELOG.md [0.5.0]`,
  ROADMAP, tags `v0.5.0` (+ optionally `framework/v0.X.Y` if the
  conformance contract gained tests that effectively bump the spec
  — flagged for P4-T1 design). Anticipate the in-container
  `refs/tags/*` 403 (fourth occurrence; local-clone workaround
  baked in).

The Phase 5 cutover (legacy removal, `v1.0.0` final tag) is
explicitly outside Phase 4. P4-T5 closes Phase 4 at `v0.5.0`;
Phase 5 plans afresh.
