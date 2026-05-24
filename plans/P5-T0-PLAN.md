# P5-T0 Plan — Phase 5 (Cutover) audit & task breakdown

| Field      | Value                                |
|------------|--------------------------------------|
| Task       | P5-T0                                |
| Depends on | Phase 4 complete (`v0.5.0`)          |
| Status     | DONE — 2026-05-21T05:35:00Z          |
| Feeds      | P5-T1 … P5-Tn (Cutover tasks)        |

## Objective

Map Phase 5 (Cutover) on paper before any destructive operation
runs. Cutover is the terminal phase: it removes the frozen
`legacy/` tree (28M, 2275 files) and the dev-time root `.claude/`
loader, finalizes the project-level docs, and ships `v1.0.0` with
the new project **replacing `main`**.

Cutover is **high-stakes and partially outside the in-container
session's authority**:

- `legacy/` and root `.claude/` removal are **destructive** (git
  history preserves them, so reversible, but consequential).
- The `main` replacement is **forbidden by `CLAUDE.md` / `docs/PROJECT.md`
  §3 without explicit permission** and is the user's authorized
  cutover act.
- `v1.0.0` + per-platform stable tags hit the same `refs/tags/*`
  403 (5th occurrence; user local-clone push).

P5-T0 produces:

1. **`plans/P5-AUDIT-cutover.md`** — inventory of what's removed,
   what's finalized, what survives; a reversibility + authority
   classification for each operation; the carried-issue
   disposition.
2. **A concrete P5-T1…P5-Tn task breakdown** with explicit
   destructive-operation gates.
3. **The cutover sequencing** — what happens in-container vs
   user-local vs user-authorized, and in what order.

P5-T0 is **paper only**; nothing is removed and `main` is untouched.

## Scope

**In:**

- Inventory `legacy/` and root `.claude/` (the two removal targets);
  confirm nothing in the surviving tree references them at runtime.
- Inventory the project-level docs that need finalizing
  (`README.md` platform matrix, `docs/REPO_STRUCTURE.md` PLANNED →
  current, `docs/PROJECT.md` cutover note, `CLAUDE.md` migration →
  post-migration rewrite).
- Classify every cutover operation: **reversibility**
  (git-recoverable vs not) and **authority** (in-container /
  user-local-clone / user-authorized-main-push).
- Decide the carried-issue disposition: do the plugin layer-model
  gap + ~150 stale refs block `v1.0.0`, or ship with the documented
  gap (post-v1.0 fix)?
- Define P5-T1…P5-Tn with destructive-operation confirmation gates.

**Out:**

- Any actual removal, doc rewrite, tag, or `main` operation
  (later P5-T*).
- Post-cutover CHG re-introduction (`docs/PROJECT.md` §After
  cutover) — that's post-v1.0.
- Post-v1.0 domain profiles (ROADMAP Post-v1.0).
- The plugin content-migration (layer model / stale refs) **unless**
  P5-T1 decides it blocks v1.0.0 (audit recommends post-v1.0).

## Approach

1. **Removal-target inventory.** Size + file count of `legacy/`
   and root `.claude/`; confirm no surviving-tree runtime
   dependency on either.
2. **Doc-finalization inventory.** Which project docs carry
   migration-in-progress language that becomes stale once cutover
   completes.
3. **Operation classification.** Per cutover operation: reversible?
   who can do it? destructive?
4. **Carried-issue disposition.** Recommend ship-with-documented-gap
   vs block-on-fix for the plugin layer-model issues.
5. **Cutover sequencing.** Order the operations so the in-container
   work doesn't break itself prematurely (notably: root `.claude/`
   removal disables the session's own hooks — must be late).
6. **Task breakdown.** P5-T1…P5-Tn with confirmation gates.

## Step sequence

1. Recon (done during planning).
2. Write `plans/P5-AUDIT-cutover.md`.
3. Append the P5-T1…P5-Tn task breakdown to this plan.
4. **Verify** (see below).
5. **Land** — single commit
   `docs: P5-T0 cutover audit + task breakdown (paper-only)`;
   update `plans/HANDOFF.md`; tick P5-T0 in `plans/MIGRATION_TODO.md`.
   Push.

## Verification

- **Paper-only.** `git status` shows changes only under `plans/`;
  `legacy/`, `.claude/`, and `main` untouched.
- **Removal targets sized.** Audit states `legacy/` (28M / 2275
  files) and root `.claude/` (the loader + 3 migration hooks +
  settings) with a no-runtime-dependency confirmation.
- **Operation classification complete.** Every cutover operation
  tagged reversible/destructive + in-container/user-local/
  user-authorized.
- **Carried-issue disposition stated** with a recommendation.
- **Cutover sequencing** explicit, including the root-`.claude/`-
  removal-must-be-late constraint.
- **Open questions ≥ 4** for P5-T1.
- **Task breakdown self-contained**, each task with a verify gate
  and (for destructive tasks) a confirmation gate.

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | A surviving-tree file references `legacy/` at runtime; removing `legacy/` breaks it. | Audit §1 runs the dependency check; any hit is flagged for resolution before P5-T2 removes `legacy/`. |
| R2 | Removing root `.claude/` mid-session disables the migration hooks (session-start-handoff, pre-compact-snapshot, plan-review-gate) and the session's own skill loading. | Audit §5 sequences root-`.claude/` removal as a **late** P5 task; commit+push frequently so a post-removal compaction can't lose work; the session-start hook only matters for *new* sessions (none after cutover). |
| R3 | The `main` replacement is attempted in-container and fails / violates the lock. | Audit classifies main-replacement as **user-authorized only**; `CLAUDE.md` + `docs/PROJECT.md` §3 forbid in-container main pushes. P5's terminal task hands the merge to the user with explicit commands. |
| R4 | `v1.0.0` ships with the plugin layer-model gap, surprising users who expect full 8-layer coverage. | `docs/PARITY.md` already documents the gap. Audit §4 recommends ship-with-documented-gap (consistent with D-0012 / prior deferrals) but flags it as a P5-T1 confirm-with-user question — v1.0.0 is a major milestone. |
| R5 | Phase 5 scope creeps into post-v1.0 work (CHG, domain profiles, content migration). | Out-clause excludes all three; carried-issue disposition explicitly defers content migration to post-v1.0 unless P5-T1 says otherwise. |
| R6 | Destructive removals run without explicit user confirmation. | Every destructive P5 task (legacy/ removal, .claude/ removal) carries a confirmation gate in the breakdown; P5-T0 is paper-only and commits nothing destructive. |

## Review log

### Pass 1 — 2026-05-21T05:15:00Z

- **G1. Paper-only, like P2/P3/P4-T0.** Verify gate confirms no
  destructive change and `main` untouched.
- **G2. The three high-stakes operations** — legacy/ removal,
  root .claude/ removal, main replacement — are foregrounded in
  the Objective, not buried. Each gets a reversibility + authority
  classification (audit §3).
- **G3. main replacement is user-authorized.** `docs/PROJECT.md`
  §3 + `CLAUDE.md` forbid in-container main pushes. R3 + the
  terminal-task design hand it to the user with explicit commands.
- **G4. root .claude/ removal sequencing.** R2 — removing it
  disables the session's hooks; the audit sequences it as a late
  task. The migration ends at cutover, so no future session needs
  the session-start hook.
- **G5. Carried-issue disposition.** R4 — recommend ship-with-
  documented-gap (PARITY.md already documents it; D-0012 framing
  defers content depth to post-v1.0). Flag as a P5-T1 confirm
  question because v1.0.0 is a major milestone.
- **G6. Dependency check before legacy/ removal.** R1 — audit §1
  confirms nothing in the surviving tree references `legacy/` at
  runtime (conformance scans framework/ only; platforms reference
  framework/ repo-relative; plans reference legacy/ in historical
  prose only).
- **G7. CLAUDE.md is migration-specific** and becomes stale at
  cutover ("Phase 1 — Framework Spec Extraction" in Current state;
  "Legacy is frozen" rules; working-branch references). Needs a
  post-migration rewrite or removal — a P5 doc-finalization task.

### Pass 2 — 2026-05-21T05:30:00Z

- **G8. Tag set at v1.0.0.** `docs/PROJECT.md` §Tag namespaces +
  ROADMAP imply: `v1.0.0` (project milestone) + per-platform
  stable releases (`hermes/v1.0.0`, `claude-code-plugin/v1.0.0`).
  Does `framework/` also tag `v1.0.0`? Open question for P5-T1 —
  framework spec is at `0.1.0`; bumping it to `1.0.0` is a
  semantic statement ("the spec is stable"), not automatic.
  Audit §6 lists it.
- **G9. The workflow-relocation pending action** (P4-T3 carry-over)
  intersects cutover: `.github/workflows/` should exist before
  v1.0.0 ideally. Audit notes it as a pre-cutover user action
  (independent of the in-container P5 work).
- **G10. plans/ and the migration trackers** — do they survive
  cutover or get archived? They're the migration's working
  record. Likely survive (history is valuable) but `CLAUDE.md`
  and `MIGRATION_TODO.md` reference an in-progress migration.
  Open question for P5-T1: keep plans/ as-is, archive it, or
  trim it.
- **G11. `.mcp.json` at root** — points at `platforms/hermes/src`.
  Survives cutover (it's the reference MCP config). No change
  needed; note in audit.
- **G12. No new findings on structure / verify / risks.** Plan
  is internally consistent and paper-only. Ready to present.

## Phase 5 task breakdown (revised 2026-05-21T05:55:00Z per D-0014, final)

**Revision history:** the user first said "do not remove legacy
files," then settled on the **archive-then-clean** model: preserve
the pristine pre-migration project as the protected branch
`legacy-ucx-v3.2-read-only` (done), **then** remove `legacy/` + root
`.claude/` from the working branch. The two removal tasks (P5-T2,
P5-T3) are therefore **restored** — now safe because the archive
branch holds everything substantive (verified). Each removal is
gated on the archive existing (it does) + explicit confirmation at
execution.

- **P5-T1 — Design.** Resolve the remaining open questions (audit
  §6, minus the resolved removal scope): `main`-replacement
  mechanism (merge vs fast-forward vs reset); whether the plugin
  layer-model gap blocks `v1.0.0` (audit recommends post-v1.0);
  whether `framework/` tags `v1.0.0` or stays `0.1.0`; per-platform
  stable tags at cutover; `plans/` disposition. Output:
  `plans/P5-T1-DESIGN.md`.
- **P5-T2 — Remove `legacy/`** (restored). `git rm -r legacy/`
  (~2276 files). **Destructive — confirmation gate; precondition:
  archive branch `legacy-ucx-v3.2-read-only` exists on the remote
  (✓).** Verify: no surviving-tree runtime reference to `legacy/`
  (P5-T0 §1 confirmed framework/ + tests/ + .mcp.json clean; the
  few hits are documentary / known-stale-refs); conformance 31/31;
  Hermes suite unaffected.
- **P5-T3 — Remove root `.claude/`** (restored). `git rm -r .claude/`
  (skills, agents, commands, the 3 migration hooks, settings) —
  superseded by `platforms/claude-code-plugin/`. **Destructive +
  session-affecting — confirmation gate; sequenced LATE** (it
  disables this session's own hooks; commit+push immediately after).
  The migration-era `.claude/` survives in working-branch git
  history (the archive holds the pre-migration `.claude/`).
- **P5-T4 — Finalize project docs.** `README.md` (platform matrix;
  drop migration-in-progress language; drop `legacy/` from the
  architecture diagram — it's removed from the tree, pointer to the
  archive branch instead); `docs/REPO_STRUCTURE.md` (PLANNED →
  as-built; legacy-removal realised via the archive branch);
  `docs/PROJECT.md` (cutover note naming the archive branch);
  `ROADMAP.md` (Phase 5 marked; "legacy archived" → archived as the
  `legacy-ucx-v3.2-read-only` branch); `CLAUDE.md` (rewrite
  migration-in-progress → post-migration project memory; `CLAUDE.md`
  is a **root file**, not under `.claude/`, so it survives P5-T3).
- **P5-T5 — Verify.** Final consolidated gate: conformance 31/31;
  Hermes 447/447; plugin smoke; both platforms' VERSION files;
  removal targets absent from the working branch; archive branch
  reachable on remote; no dangling runtime references; doc
  finalization complete. Verify record at `plans/P5-T5-VERIFY.md`.
- **P5-T6 — Close + cutover.** Cut `CHANGELOG.md [1.0.0]`; mark
  Phase 5 complete + cutover in `ROADMAP.md`; create annotated tags
  per P5-T1's tag-scope decision. **The `main` replacement is a
  user-authorized act** — P5-T6 prepares the branch and hands the
  user the exact merge/push commands; the in-container session does
  not push to `main`.

Two operations are **never** done in-container: the `main`
replacement (forbidden by the lock; user-authorized) and all tag
pushes (5th `refs/tags/*` 403; user local-clone). Both are baked
into P5-T6's plan as user actions. The two destructive removals
(P5-T2, P5-T3) **are** in-container but each carries an explicit
confirmation gate at execution and depends on the archive branch
(✓ created + protected).
