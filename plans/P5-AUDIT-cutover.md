# Phase 5 Audit — Cutover

| Field      | Value                                |
|------------|--------------------------------------|
| Audit of   | cutover scope: removals, doc finalization, main-replacement |
| Produced by| P5-T0                                |
| Date       | 2026-05-21T05:10:00Z                 |

> **Revised 2026-05-21T05:55:00Z (D-0014, final).** The cutover follows
> an **archive-then-clean** model: the pristine pre-migration project is
> preserved as the protected branch `legacy-ucx-v3.2-read-only` (created
> off `main` at `491e8db`; **done + protected**), and **then** `legacy/`
> + root `.claude/` are removed from the working branch. The removal
> analysis below (§1, §3, §5) is therefore **active** — and its
> conclusion ("no runtime dependency; removals safe") now also rests on
> the archive branch holding everything substantive (verified: all 7
> legacy trees + root `.claude/` present). Caveat: the archive holds the
> *pre-migration* `.claude/`; the working branch's *migration-era*
> `.claude/` (3 hooks) survives removal only in git history. See D-0014
> and the restored breakdown in `plans/P5-T0-PLAN.md`.

## Summary

Cutover ships `v1.0.0` and makes the new project replace `main`.
The in-container work is **removals + doc finalization + changelog/
tags**; the **`main` replacement is a user-authorized act** (the
lock in `docs/PROJECT.md` §3 forbids in-container main pushes), and
all tag pushes hit the 5th `refs/tags/*` 403 (user local-clone).

Two destructive removals: `legacy/` (28M, 2275 files) and root
`.claude/` (the dev-time loader). **Neither has a runtime dependency
from the surviving tree** — confirmed below. Both are git-recoverable.

The plugin layer-model gap + ~150 stale refs (P3/P4 carried issues)
are **recommended for post-v1.0**, not v1.0.0 blockers — `docs/PARITY.md`
already documents them, and D-0012 frames v1 scope as software/devops
with content depth deferred. Flagged as a P5-T1 confirm question
since v1.0.0 is a major milestone.

## 1. Removal targets + dependency check

### `legacy/` — 28M, 2275 files

```
legacy/
├── ai_dev_ssd_flow_v2/   (superseded earlier framework version)
├── mcp_ucx/              (deprecated Hermes predecessor)
├── ucx_flow_v3/          (the framework source — extracted to framework/)
├── ucx_hermes/           (the Hermes source — ported to platforms/hermes/)
├── ucx_kb/, ucx_knowledge/, governance/, scripts/, dev_tools/,
│   changelog/, roadmap/, plans/, tests/, tmp/, logs/,
│   github-workflows-disabled/  (28 frozen workflows)
└── (root docs: CONTRIBUTING.md, README.md, etc.)
```

**Runtime-dependency check (surviving tree → `legacy/`):**

| Surviving path | `legacy/` references | Class |
|----------------|----------------------|-------|
| `framework/` | **0** | clean |
| `tests/conformance/` | **0** | clean |
| `.mcp.json` | **0** | clean |
| `platforms/hermes/` | `CHANGELOG.md` only | documentary (migration history) |
| `platforms/claude-code-plugin/` | `skills/doc-brd-autopilot/SKILL.md` + CHANGELOG | part of the known ~150 stale-refs issue (PARITY.md) |

**Conclusion:** no runtime dependency. The Hermes CHANGELOG mentions
`legacy/ucx_hermes` as migration history (stays accurate as
history). The plugin skill reference is one of the already-documented
stale refs; removing `legacy/` makes it dangle slightly more, but it
was already slated for post-v1.0 content cleanup. **`legacy/` removal
is safe.**

### Root `.claude/` — dev-time loader

```
.claude/
├── skills/      (149 dirs — ported to platforms/claude-code-plugin/ at P3)
├── agents/      (requirements-analyst — ported)
├── commands/    (save-plan — ported)
├── hooks/       (plan-review-gate, pre-compact-snapshot, session-start-handoff
│                 — migration-only; NOT ported, per P3-T0)
├── settings.json       (configures the migration hooks)
└── settings.local.json (gitignored)
```

**Runtime-dependency check (surviving tree → root `.claude/`):**
The only references are inside `platforms/claude-code-plugin/skills/*`
(plugin skill bodies that mention `.claude/` paths) — these are the
**plugin's own copies**, part of the documented stale-refs set, not
a live dependency of the surviving tree on the *root* `.claude/`
directory.

**Session-impact caveat:** root `.claude/` is what the *current
in-container migration session* loads (skills + the 3 hooks). Removing
it disables:
- `session-start-handoff.sh` — only matters for *new* sessions (none
  after cutover).
- `pre-compact-snapshot.sh` — matters if a compaction happens after
  removal (mitigate: commit+push frequently).
- `plan-review-gate.sh` — the commit-time warning (non-blocking).

**Conclusion:** root `.claude/` removal is safe but **session-
affecting**; sequence it **late** in P5 (P5-T3), and the migration
ends at cutover so no future session needs the loader.

## 2. Doc-finalization inventory

Project-level docs carrying migration-in-progress language that goes
stale at cutover:

| Doc | Stale content | P5-T4 action |
|-----|---------------|--------------|
| `README.md` | "Status: early restructure (Phase 0 — planning)"; `legacy/` in the architecture diagram | Update status to v1.0.0 / shipped; drop `legacy/` from the diagram; finalize the platform matrix. |
| `docs/REPO_STRUCTURE.md` | "Status: PLANNED target structure"; "the layout the repository converges to at cutover" | Flip PLANNED → as-built; drop the `legacy/` → target mapping (legacy gone). |
| `docs/PROJECT.md` | §3 "Until then `main` remains the legacy"; "`main` is protected for the duration of the migration" | Add a cutover-complete note; the migration-era branching rules become historical. |
| `CLAUDE.md` | "Phase: Phase 1 — Framework Spec Extraction"; "mid-restructure"; "Legacy is frozen"; working-branch + main-lock rules | **Rewrite to post-migration project memory** (or remove). Migration-specific rules (legacy frozen, copy-don't-move) are obsolete once legacy is gone. |
| `ROADMAP.md` | Phases 0–4 marked; Phase 5 pending | Mark Phase 5 complete + cutover; foreground the Post-v1.0 section. |
| `plans/MIGRATION_TODO.md` + `plans/HANDOFF.md` | Live migration trackers | Disposition decided in P5-T1 (keep as history / archive / trim). |

## 3. Operation classification — reversibility × authority

| Operation | Destructive? | Reversible? | Authority |
|-----------|--------------|-------------|-----------|
| Remove `legacy/` | Yes | Yes (git history) | **In-container** (working branch) |
| Remove root `.claude/` | Yes (+ session-affecting) | Yes (git history) | **In-container** (late, careful) |
| Finalize docs | No | Yes | In-container |
| Cut `CHANGELOG.md [1.0.0]` | No | Yes | In-container |
| Create `v1.0.0` + platform tags | No | Yes (delete + recreate) | **User local-clone** (5th `refs/tags/*` 403) |
| **Replace `main`** | Yes (overwrites `main`) | Partially (main history rewrite is consequential) | **User-authorized only** — `CLAUDE.md` + `docs/PROJECT.md` §3 forbid in-container main pushes |
| Relocate workflows (P4-T3 carry-over) | No | Yes | **User local-clone** (workflows permission) |

**Two operations are never done in-container:** the `main`
replacement and all tag pushes. Both are baked into P5-T6 as user
actions.

## 4. Carried-issue disposition

| Issue | Source | Recommendation |
|-------|--------|----------------|
| Plugin lacks `doc-tdd` + `doc-iplan`; legacy 11-layer model | P3-T1 §Deferred R2; `docs/PARITY.md` | **Post-v1.0.** Documented in PARITY.md; D-0012 defers content depth. Confirm with user (v1.0.0 is major). |
| ~150 stale `framework/<X>` refs in plugin skills | P3-T2 G18 | **Post-v1.0.** Same root cause; per-skill content migration. |
| `api_runner.py:115` install string | P4-T5 G10 | **Already fixed** (commit `23ae664`). |
| Workflow relocation | P4-T3 | **Pre-cutover user action** (independent; ideally `.github/workflows/` exists before v1.0.0). |

**Recommendation:** ship `v1.0.0` with the documented plugin
layer-model gap; do **not** block cutover on the content migration.
This is consistent with every prior phase's deferral discipline and
with D-0012's "v1 = software/devops, content depth post-v1.0"
framing. **P5-T1 confirms with the user.**

## 5. Cutover sequencing

Order matters — the in-container work must not break itself
prematurely:

1. **P5-T1 design** (paper) — resolve open questions.
2. **P5-T2 remove `legacy/`** — destructive; no session impact.
3. **P5-T4 finalize docs** — before the `.claude/` removal so the
   plan-review-gate hook still warns on the doc commits (minor, but
   why not).
4. **P5-T3 remove root `.claude/` + rewrite CLAUDE.md** — **late**,
   because it disables the session's hooks. After this, commit+push
   immediately (no hook safety net).
5. **P5-T5 verify** — consolidated final gate.
6. **P5-T6 close + cutover** — CHANGELOG [1.0.0], tags (user),
   `main` replacement (user).

(P5-T3 and P5-T4 could swap; the audit puts doc-finalization before
`.claude/` removal so the commit-warning hook is alive for the doc
commits. Minor; P5-T1 can reorder.)

## 6. Open questions (for P5-T1 design)

1. **`main` replacement mechanism.** Merge commit (`git merge
   --no-ff`), fast-forward, or squash? The branch is **70 commits
   ahead** of `origin/main`; `main` currently holds the legacy
   `ucx_framework`. A merge preserves the 70-commit migration
   history; a squash collapses it. Recommendation: merge (preserve
   history) or reset `main` to the branch tip — user decides since
   it's their authorized act.

2. **Does `framework/` tag `v1.0.0`?** The spec is at `0.1.0`.
   Bumping to `framework/v1.0.0` is a semantic statement that the
   spec is stable. Options: (a) bump framework to 1.0.0 alongside
   the milestone; (b) keep framework at 0.1.0 (spec hasn't changed
   since P1) and only tag the project `v1.0.0` + platform stables.
   Recommendation: keep framework at `0.1.0` unless P5 makes a spec
   change — but flag for user (a 1.0.0 framework tag signals
   stability).

3. **Plugin layer-model gap — v1.0.0 blocker or post-v1.0?**
   Audit §4 recommends post-v1.0 (ship with documented gap).
   Confirm.

4. **`CLAUDE.md` — rewrite or remove?** Migration-specific today.
   Post-cutover it could become post-migration project memory
   (architecture, conventions, where things are) or be removed
   entirely (the README + docs/ cover the project). Recommendation:
   rewrite to a slim post-migration memory.

5. **`plans/` disposition.** Keep the full migration record as
   history (valuable provenance — feeds the STARTUP_HANDOFF corpus
   idea), archive it (e.g. `docs/migration-history/`), or trim it?
   Recommendation: keep as-is (history is cheap and valuable).

6. **Per-platform stable tags.** `hermes/v1.0.0` +
   `claude-code-plugin/v1.0.0` at cutover? Or do platforms stay at
   `0.1.0` until they independently decide to cut a stable? The
   `api_runner.py` fix would make `hermes/v0.1.1` natural. Open:
   does cutover force platform 1.0.0, or is platform versioning
   independent of the project milestone? (`docs/PROJECT.md` §3:
   "Platforms tag their own releases independently.")

## 7. Verify (against the plan's gate)

- Removal targets sized: `legacy/` (28M / 2275 files), root
  `.claude/` (loader + 3 migration hooks + settings).
- No runtime dependency from the surviving tree on either target
  (framework/ + tests/ + .mcp.json clean; the few hits are
  documentary or already-known stale refs).
- Every cutover operation classified (reversibility × authority);
  `main` replacement + tag pushes flagged user-only.
- Carried-issue disposition recommends post-v1.0 for the content
  migration; confirms `api_runner.py` already fixed.
- Cutover sequencing addresses the root-`.claude/`-removal session-
  impact (late task).
- 6 open questions for P5-T1.
- No files removed / `main` untouched (`git status` shows only
  `plans/` edits).
