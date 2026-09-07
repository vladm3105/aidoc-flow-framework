# P5-T1 Design — Cutover

| Field      | Value                                |
|------------|--------------------------------------|
| Task       | P5-T1                                |
| Depends on | P5-T0 audit, D-0014                  |
| Produced by| P5-T1 (this doc IS the plan output)  |
| Date       | 2026-05-21T06:00:00Z                 |
| Feeds      | P5-T2, P5-T3, P5-T4, P5-T6           |

## Summary

Five cutover decisions resolved. The `main` replacement is a
**force-replace** (histories diverged; old `main` preserved in the
archive branch, so it's lossless). `framework/` **stays at `0.1.0`**
(SemVer discipline + reaches `1.0.0` under post-cutover CHG
governance). The plugin layer-model gap is **not a `v1.0.0` blocker**
(ship with the documented gap). Component versions stay
**independent** of the project milestone — cutover tags `v1.0.0`
(project) only; optionally `hermes/v0.1.1` for the api_runner fix;
the plugin stays `0.1.0`. `plans/` is **kept in-tree** as the
migration's audit trail. `CLAUDE.md` is **rewritten** to
post-migration project memory (it's a root file; survives the
P5-T3 `.claude/` removal).

| Q | Question | Decision |
|---|----------|----------|
| Q1 | `main`-replacement mechanism | **Force-replace** `main` with the working-branch tip (FF impossible — histories diverged; old `main` is in the protected archive branch). User-authorized. |
| Q2 | `framework/` tag `v1.0.0`? | **No** — stays `0.1.0`; reaches `1.0.0` later under CHG governance. |
| Q3 | Plugin layer-model gap blocks `v1.0.0`? | **No** — ship with the documented gap (PARITY.md); content fix is post-v1.0. |
| Q4 | Tag scope at cutover | **Project `v1.0.0` only**; framework `0.1.0`; platforms independent (optional `hermes/v0.1.1`; plugin stays `0.1.0`). |
| Q5 | `plans/` disposition | **Keep in-tree** as-is (audit trail / provenance). |
| Q6 | `CLAUDE.md` | **Rewrite** to post-migration memory (root file; survives the `.claude/` removal). |

The single decision most likely to warrant user override is **Q4**
(whether v1.0.0 is a "bump everything to 1.0" unified launch vs the
project-milestone-only reading recommended here) — flagged in that
section.

## Q1 — `main`-replacement mechanism

**Topology (checked):** `origin/main` (`491e8db`) has **1 commit
that HEAD lacks**, and HEAD is **73 commits ahead**. So `origin/main`
is **not an ancestor** of HEAD — **fast-forward is impossible**, and
a normal merge would reconcile two structurally-unrelated project
layouts (old `ucx_framework` root vs the new multi-platform root),
producing a conflict-laden merge commit.

**Options:**

1. **Force-replace `main`** with the working-branch tip
   (`git push --force origin claude/multi-platform-migration-AamWB:main`,
   or a PR merged with admin override after lifting protection).
   `main` becomes exactly the new project.
2. **Merge `--no-ff`** — creates a merge commit; divergent layouts
   mean likely conflicts (both have root `README.md`, `pyproject.toml`,
   etc. with different content); resolving them all to favour the
   working branch is tedious and the result still carries a merge
   commit linking two unrelated trees.
3. **Squash** — collapses 73 commits into one on `main`; loses the
   migration's granular audit trail.

**Chosen:** Option 1 — **force-replace**.

**Rationale:** This is a wholesale **replacement**, not a feature
merge — `docs/PROJECT.md` §3 literally says "the new project
replaces `main`." Force-replace is the clean, literal realisation.
The usual objection to force-pushing `main` (losing history) **does
not apply here**: the entire old `main` (`491e8db`, including the 1
divergent commit) is preserved byte-for-byte in the protected
`legacy-ucx-v3.2-read-only` archive branch. So force-replace loses
nothing. Option 2 produces a messy conflict-resolution + a
misleading merge commit; Option 3 destroys the audit trail the
project deliberately maintained.

**Downstream implications:**

- **P5-T6 (user-authorized):** the in-container session does **not**
  push to `main`. P5-T6 hands the user the exact commands:

  ```sh
  # main is protected — temporarily lift protection, then:
  git fetch origin
  git push --force origin claude/multi-platform-migration-AamWB:main
  # re-enable protection on main
  ```

  Or, equivalently, via a PR with "allow force / admin merge."
- The old `main` is recoverable any time from
  `legacy-ucx-v3.2-read-only` (and its reflog).
- **Order:** the force-replace happens **after** all P5 in-container
  work (removals, docs, changelog) lands on the working branch, so
  `main` receives the finished v1.0.0 state in one move.

## Q2 — Does `framework/` tag `v1.0.0`?

**Options:**

1. Keep `framework/VERSION` at `0.1.0`; no `framework/v1.0.0` tag at
   cutover.
2. Bump `framework/VERSION` → `1.0.0`; tag `framework/v1.0.0`; update
   both platforms' `FRAMEWORK_SPEC_VERSION` to match + the
   conformance test.

**Chosen:** Option 1 — **stays `0.1.0`**.

**Rationale:**

- **SemVer discipline:** the spec has **not changed** since P1
  (P4 added enforcement *tests*, not spec content). A major bump
  with no change is noise.
- **CHG-governance timing:** `ROADMAP.md` / `docs/PROJECT.md` §
  "After cutover" reintroduces the gated CHG process to govern
  **`framework/` spec changes** post-Phase-5. A `1.0.0` spec is a
  stability commitment ("breaking changes bump major"); that
  commitment is best made *once CHG is governing the spec*, not the
  moment before. Let the framework earn `1.0.0` under CHG.
- **Lower risk:** keeps Phase 5 from touching `framework/` (the
  conformance suite stays stable; no FRAMEWORK_SPEC_VERSION ripple).

**Downstream implications:**

- `framework/VERSION` untouched in Phase 5.
- Both platforms' `FRAMEWORK_SPEC_VERSION` stay `0.1.0` — still match
  (conformance PC1 stays green).
- The project `v1.0.0` milestone and the framework spec version are
  **decoupled**, consistent with the project's multi-stream tag
  model (`docs/PROJECT.md` §3).

## Q3 — Does the plugin layer-model gap block `v1.0.0`?

**Chosen:** **No — ship `v1.0.0` with the documented gap.**

**Rationale:** (carried from P5-T0 audit §4)

- The gap (plugin lacks `doc-tdd` + `doc-iplan`; reflects the legacy
  11-layer model) is **documented** in `docs/PARITY.md` "Known
  parity gap."
- It is **content depth**, not a correctness or safety issue — the
  plugin works as a Claude Code artifact.
- D-0012 frames v1 as software/devops with content depth deferred;
  every prior phase deferred this consistently.
- Fixing it is a **large per-skill content migration** (which legacy
  concept maps to which new-model layer, MVP-vs-non-MVP naming) that
  would massively delay cutover for no correctness gain.

**Downstream implications:**

- Post-v1.0 content-migration task (already tracked: P3-T1 §Deferred
  R2, P3-T2 G18, PARITY.md). Not a Phase 5 deliverable.
- The `v1.0.0` CHANGELOG + README note the gap with a pointer to
  PARITY.md.

## Q4 — Tag scope at cutover

**Options:**

1. **Project milestone only:** tag `v1.0.0`. Framework stays `0.1.0`;
   platforms version independently (optional `hermes/v0.1.1` for the
   api_runner fix; plugin stays `0.1.0`).
2. **Unified 1.0 launch:** bump everything to `1.0.0` — `v1.0.0` +
   `framework/v1.0.0` + `hermes/v1.0.0` + `claude-code-plugin/v1.0.0`.
3. Hybrid: `v1.0.0` + platforms to `1.0.0`, framework stays `0.1.0`.

**Chosen:** Option 1 — **project `v1.0.0` only; components
independent.**

**Rationale:**

- The project milestone tags (`v0.1.0` … `v0.5.0`) have tracked
  **phases**, not component releases. `v1.0.0` = the **cutover
  phase** ("new project replaces `main`"), a project-lifecycle
  marker — *not* a claim that every component is 1.0-stable.
- **Honest SemVer per component:** the plugin has a documented
  layer-model gap (missing 2 of 8 layers) — calling it `1.0.0`
  would be misleading. Hermes is solid (447 tests) but young.
  `docs/PROJECT.md` §3: "Platforms tag their own releases
  independently."
- Forcing a unified `1.0.0` couples component maturity to a project-
  lifecycle event they don't share.
- **The api_runner fix** (commit `23ae664`, post-`hermes/v0.1.0`)
  is a real Hermes change → an **optional** `hermes/v0.1.1` patch
  is the natural way to capture it. Plugin has no post-`0.1.0`
  change → stays `0.1.0`.

**⚠ Most likely override:** if the intent is a **unified "1.0
launch"** (marketing / clean-slate signal — everything at 1.0.0),
Option 2 is the alternative. The recommendation here is the
SemVer-honest reading; the launch-signal reading is a legitimate
product call the user may prefer. Flagged for redirect.

**Downstream implications:**

- **P5-T6 tags:** `v1.0.0` (project) — required. `hermes/v0.1.1`
  (optional, captures the api_runner fix). No plugin tag, no
  framework tag.
- All tag pushes are user-local-clone (5th `refs/tags/*` 403).

## Q5 — `plans/` disposition

**Chosen:** **Keep `plans/` in-tree, as-is.**

**Rationale:** `plans/` is the migration's complete audit trail —
30+ task plans, 7 audits, verify records, the decision log, ~18
retrospectives. It's provenance (the `docs/STARTUP_HANDOFF.md`
explicitly cites it as the seed corpus), it's text (cheap to keep),
and trimming/archiving would discard hard-won record for no benefit.
The trackers (`MIGRATION_TODO.md`, `HANDOFF.md`) become historical
at cutover — fine; they document how the project got here.

**Downstream implications:**

- **P5-T4 / P5-T6:** add a one-line "migration complete" banner to
  `MIGRATION_TODO.md` / `HANDOFF.md` tops, but keep all content.
- No `plans/` removal or restructure in Phase 5.
- Note: P5-T2 removes the in-tree `legacy/`; plan docs that cite
  `legacy/<path>` become pointers-to-history (the content is in the
  archive branch). Acceptable — they're a historical record.

## Q6 — `CLAUDE.md` (implicit, from D-0014)

**Chosen:** **Rewrite** `CLAUDE.md` to post-migration project memory
in P5-T4 (it is a **root file**, not under `.claude/`, so it
survives the P5-T3 `.claude/` removal).

**Rationale:** The current `CLAUDE.md` is migration-in-progress
("Phase: Phase 1 — Framework Spec Extraction"; "mid-restructure";
"Legacy is frozen / copy-don't-move"; working-branch + main-lock
rules). Post-cutover most of that is obsolete (legacy removed from
the tree → archive branch; migration done; main is the new project).
A slim post-migration `CLAUDE.md` keeps the durable parts.

**The rewritten `CLAUDE.md` covers:**

- What the project is (the shipped multi-platform structure:
  `framework/` spec + `platforms/hermes/` + `platforms/claude-code-plugin/`).
- Where things are (framework, platforms, conformance suite, docs).
- Durable conventions: the framework spec is the contract; both
  platforms declare `FRAMEWORK_SPEC_VERSION`; tagging policy
  (`docs/TAGGING.md`); conformance suite must stay green.
- A pointer to the archive branch `legacy-ucx-v3.2-read-only` for
  pre-migration history.
- **Drops:** migration-phase tracking, "legacy frozen / copy-don't-
  move," working-branch rules, main-lock (cutover done).

**Downstream implications:** P5-T4 writes the new `CLAUDE.md`. The
two-pass-review / plan-first workflow (D-0007) — keep or drop
post-migration? **Recommendation: keep a slimmed mention** (it's a
good practice) but mark it as guidance, not a hard gate, post-
migration. P5-T4 decides the exact wording.

## Cross-question conflicts

None. Specifically checked:

- Q1 (force-replace) × Q5 (keep plans/) — the force-replaced `main`
  carries the working branch's `plans/` intact. Consistent.
- Q2 (framework stays 0.1.0) × Q4 (component independence) — both
  say "don't force 1.0.0 on components"; aligned.
- Q3 (ship with gap) × Q4 (plugin stays 0.1.0) — the documented gap
  is *why* the plugin honestly stays 0.1.0; mutually reinforcing.
- Q6 (rewrite CLAUDE.md) × P5-T3 (remove `.claude/`) — `CLAUDE.md`
  is at repo root, **not** inside `.claude/`; the removal doesn't
  touch it. Confirmed by `ls` (root-level `CLAUDE.md`).

## Deferred items

1. **Unified-1.0-launch option (Q4).** If the user prefers bumping
   all components to `1.0.0`, that's a single redirect; the design
   defaults to component-independence.
2. **Framework `1.0.0` under CHG (Q2).** When CHG returns post-
   cutover to govern the spec, the framework can earn `1.0.0`. Not
   Phase 5.
3. **Plugin content migration (Q3).** Post-v1.0 per-skill work.
4. **Workflow relocation (P4-T3 carry-over).** Independent user
   action; ideally `.github/workflows/` exists before the `v1.0.0`
   tag so CI runs on the cutover commit.

## Verify (against the plan's gate)

- All 5 explicit questions + the implicit CLAUDE.md question covered;
  each with Options / Chosen / Rationale / Downstream.
- **Q1** — grounded in the checked topology (diverged; FF impossible);
  force-replace justified by the archive branch making it lossless.
- **Q2 / Q4** — component versions decoupled from the project
  milestone, consistent with `docs/PROJECT.md` §3.
- **Q3** — defers to the existing PARITY.md documentation.
- **Q6** — confirms `CLAUDE.md` is a root file surviving the
  `.claude/` removal.
- Cross-question conflicts: explicitly checked, none.
- The one likely-override (Q4 unified-1.0) is flagged.
- No code or files moved by P5-T1 — `git status` shows only `plans/`
  edits.

## Review log

### Pass 1 — 2026-05-21T06:15:00Z

- **G1. Q1 grounded in real topology.** Checked
  `git merge-base --is-ancestor` — diverged, FF impossible. Force-
  replace is the clean wholesale-replacement mechanism; lossless
  because the old `main` is the protected archive branch. Avoids the
  merge-conflict mess of reconciling two unrelated project layouts.
- **G2. Q2 — framework stays 0.1.0.** Two independent reasons:
  SemVer (no spec change) + CHG-governance timing (let the spec
  earn 1.0.0 under the gated process that returns post-cutover).
  Also keeps Phase 5 from touching `framework/`.
- **G3. Q4 is the judgment call.** The project-milestone-vs-unified-
  1.0 question is genuinely a product decision. Recommended the
  SemVer-honest reading (the plugin gap makes a plugin 1.0.0
  misleading) but flagged the unified-launch alternative explicitly
  for override — the user asked for recommendations, so I recommend,
  but mark this one as the most likely redirect.
- **G4. Q3 + Q4 reinforce.** The documented plugin gap is the reason
  the plugin honestly stays 0.1.0 — same fact, two questions.
- **G5. Q6 — CLAUDE.md is a root file.** Verified it's not under
  `.claude/`; P5-T3's removal doesn't touch it. The rewrite is a
  P5-T4 doc task, not blocked by the removal.
- **G6. api_runner fix → optional hermes/v0.1.1.** The fix
  (`23ae664`) post-dates `hermes/v0.1.0`; a patch tag is the
  natural capture, but optional (platforms version independently).
- **G7. Force-replace is user-authorized + needs protection lift.**
  P5-T6 hands the user the exact commands; in-container never
  pushes main. The protected `main` likely needs its protection
  temporarily lifted for the force-push.

### Pass 2 — 2026-05-21T06:30:00Z

- **G8. Re-examine Q1 force-replace risk.** The objection to
  force-pushing `main` is history loss. Mitigation is concrete and
  verified: `legacy-ucx-v3.2-read-only` = `491e8db` = the exact old
  `main` (including the 1 divergent commit), and it's branch-
  protected. Plus `main`'s reflog on the server. Lossless. The only
  operational nuance: branch protection on `main` must be lifted for
  the force-push then re-enabled — P5-T6 notes this.
- **G9. Does removing `legacy/` (P5-T2) before the main-replace
  matter?** No — all P5 in-container work lands on the working
  branch first; `main` receives the finished state in one force-
  replace at P5-T6. Sequencing is internally consistent.
- **G10. Q5 keep plans/ — interaction with legacy/ removal.** After
  P5-T2, plan docs citing `legacy/<path>` are pointers-to-history;
  the content is in the archive branch. Documented; acceptable. No
  need to rewrite the historical plans.
- **G11. CLAUDE.md rewrite — keep the review-workflow guidance?**
  Recommendation: keep it as *guidance* (the two-pass plan review
  is a good practice) but soften from a hard gate to a convention
  post-migration. P5-T4 finalizes wording; the
  `.claude/hooks/plan-review-gate.sh` hook is removed with `.claude/`
  in P5-T3 anyway, so it can't be a *hook-enforced* gate post-
  cutover regardless.
- **G12. No new findings.** Plan is internally consistent; verify
  gates observable. Ready to present on approval.
