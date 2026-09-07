# P5-T3 Plan — Remove root `.claude/`

| Field      | Value                                |
|------------|--------------------------------------|
| Task       | P5-T3                                |
| Depends on | P5-T1 design, P5-T2 (legacy/ removed), P5-T4 (docs finalized), D-0014 |
| Status     | DONE — 2026-05-21T08:55:00Z          |
| Feeds      | P5-T5 (verify), P5-T6 (cutover)      |

## Objective

Remove the dev-time root `.claude/` loader (skills, agents, commands,
the 3 migration hooks, settings) from the working branch. The skill
set was productized into `platforms/claude-code-plugin/` (Phase 3);
the root loader is the migration's own dev scaffolding and is dropped
at cutover so the shipped project's Claude Code delivery is the
plugin, not a root loader.

**Destructive + session-affecting + sequenced LATE.** It deletes
*this session's own* loaded skills + hooks (`plan-review-gate`,
`pre-compact-snapshot`, `session-start-handoff`); after it runs those
stop firing for the rest of the session. Gated on **explicit user
confirmation**; commit+push **immediately** after (no
pre-compact-snapshot safety net post-removal).

## Scope

**In:**

- `git rm -r .claude/` on the working branch — removes the tracked
  loader (skills/agents/commands/hooks/settings.json).
- Verify: tracked `.claude/` gone; conformance 31/31; plugin smoke
  unaffected; no surviving-tree **runtime** dependency on root
  `.claude/`; archive branch intact.

**Out:**

- Plugin's own `.claude-plugin/` — that's
  `platforms/claude-code-plugin/.claude-plugin/`, a *different* path;
  untouched.
- `main` operations — P5-T6.
- Re-pointing any doc — P5-T4 already finalized the docs (CLAUDE.md
  doesn't depend on `.claude/`; REPO_STRUCTURE/README describe the
  loader as ported+removed).
- `settings.local.json` if gitignored — `git rm` removes tracked
  files only; any gitignored leftover lingers on disk (won't
  propagate), same as `legacy/tmp/` at P5-T2.

## Open consideration — preserve the 3 migration hooks?

`.claude/hooks/` holds three **reusable** dev-workflow hooks
(`plan-review-gate.sh`, `pre-compact-snapshot.sh`,
`session-start-handoff.sh`) — the "ephemeral-session workflow
tooling" called out in `docs/STARTUP_HANDOFF.md` (idea #6). The
pre-migration `.claude/` in the archive branch has **no hooks**, so
after this removal the hooks survive only in working-branch git
history.

**Options (surface at the confirmation gate):**

- **(A) Straight removal** — hooks live in git history; restorable
  via `git show <commit>:.claude/hooks/...` if ever wanted.
- **(B) Preserve durably first** — copy the 3 hooks (+ a short
  README) to `docs/dev-hooks/` before the removal, so the reusable
  tooling stays discoverable in the shipped tree.

**Recommendation:** **(B)** — it's cheap (~4 small files), keeps the
genuinely-reusable tooling visible, and aligns with the
STARTUP_HANDOFF's framing of this infrastructure as a product idea.
But it's the user's call; (A) is fully defensible (git history is a
real archive).

## Approach

### 1. Pre-flight (read-only)

- **Content-preservation check:** the plugin holds the productized
  skills/agents/commands; the pre-migration `.claude/` is in the
  archive branch; confirm.
- **Runtime-dependency sweep:** nothing in the surviving tree resolves
  a root-`.claude/` path at runtime. (Distinguish: the plugin's skill
  bodies mention `.claude/` as documentary/known-stale-refs — allowed;
  any *runtime* root-`.claude/` dependency must be zero.)
- **Tracking check:** which `.claude/` files are tracked vs gitignored
  (e.g. `settings.local.json`) — informs what `git rm` removes vs what
  lingers on disk.

### 2. (If option B chosen) Preserve hooks

```sh
mkdir -p docs/dev-hooks
git mv .claude/hooks/plan-review-gate.sh      docs/dev-hooks/
git mv .claude/hooks/pre-compact-snapshot.sh  docs/dev-hooks/
git mv .claude/hooks/session-start-handoff.sh docs/dev-hooks/
# + a short docs/dev-hooks/README.md describing them
```

(`git mv` out of `.claude/` first, then the `git rm -r .claude/`
removes the rest.)

### 3. The removal

```sh
git rm -r .claude/
```

### 4. Commit + push IMMEDIATELY

The `pre-compact-snapshot.sh` safety net is gone after this; commit
and push without delay so a post-removal compaction can't lose work.

## Step sequence

1. **Pre-flight checks** (Approach §1) — read-only.
2. **⛔ CONFIRMATION GATE** — present pre-flight results + the
   hook-preservation choice (A/B) + the exact `git rm` command;
   **do not proceed without explicit user go-ahead.**
3. (If B) preserve hooks to `docs/dev-hooks/` (Approach §2).
4. **`git rm -r .claude/`**.
5. **Verify** (below).
6. **Land — IMMEDIATELY** — single commit
   `chore: remove dev-time root .claude/ loader (superseded by the plugin) (P5-T3)`;
   update `plans/HANDOFF.md`; tick P5-T3 in `plans/MIGRATION_TODO.md`.
   Push without delay.

## Verification

- **V1. tracked `.claude/` gone:** `git ls-files .claude/ | wc -l`
  == 0. (The dir may linger on disk if a gitignored
  `settings.local.json` remains — note it; won't propagate.)
- **V2. Conformance suite:** 31/31 (scans `framework/`; unaffected —
  sanity).
- **V3. Plugin smoke unaffected:** `platforms/claude-code-plugin/`
  intact — 142 skill dirs; manifest valid. (Distinct path from root
  `.claude/`.)
- **V4. No runtime root-`.claude/` dependency** in the surviving
  tree (framework/, tests/, platforms/*/src + manifest, .mcp.json).
- **V5. Archive branch intact:** `git ls-remote origin
  legacy-ucx-v3.2-read-only` resolves (removal is working-branch-only).
- **V6. Scope discipline:** staged diff is **only** `.claude/`
  deletions (+ the `docs/dev-hooks/` moves if option B); no other
  path touched. The plugin's `.claude-plugin/` is **not** in the
  diff.
- **V7. (If B) hooks preserved:** `docs/dev-hooks/` holds the 3
  hooks + README.
- **V8. Committed + pushed** before any further work (session-impact
  mitigation).

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | Removing `.claude/` breaks the current session's skill/hook loading mid-Phase-5. | Sequenced LAST of the destructive ops; the remaining work (P5-T5 verify, P5-T6 close) is git + doc + conformance, needs no `.claude/` skills. Commit+push immediately (V8) so nothing is at risk. |
| R2 | A post-removal context compaction loses uncommitted work (pre-compact-snapshot hook gone). | Commit+push immediately after the removal; keep committing per-task through P5-T5/T6; HANDOFF stays current in the repo. |
| R3 | `git rm -r .claude/` accidentally catches the plugin's `.claude-plugin/`. | Different path (`platforms/claude-code-plugin/.claude-plugin/`); the arg is exactly `.claude/`. V6 confirms the plugin path is not in the staged diff. |
| R4 | Reusable hooks lost to git-history-only. | The hook-preservation choice (option B) is surfaced at the confirmation gate; recommendation is to preserve to `docs/dev-hooks/`. Either way git history retains them. |
| R5 | A surviving-tree runtime path actually reads root `.claude/`. | Pre-flight sweep (Approach §1); the plugin's `.claude/` mentions are documentary/known-stale, not runtime root-loader deps. Any runtime hit halts the removal. |
| R6 | Removal runs without explicit confirmation. | Step 2 is a hard CONFIRMATION GATE. |
| R7 | Settings (`settings.json`) held something not captured elsewhere. | `settings.json` configures the migration hooks (dev-time) — obsolete post-cutover; in git history. `settings.local.json` is gitignored local state, not valuable. |

## Review log

### Pass 1 — 2026-05-21T08:30:00Z

- **G1. Sequenced LAST + commit-immediately (R1/R2/V8).** Removing
  the session's own hooks is the reason this is the final destructive
  op; the immediate commit+push removes the only real hazard (work
  loss on compaction).
- **G2. Hook-preservation surfaced (R4 / Open consideration).** The
  3 hooks are reusable tooling (STARTUP_HANDOFF idea #6); the
  pre-migration `.claude/` (archive branch) has none. Option B
  (preserve to `docs/dev-hooks/`) recommended but the user decides
  at the gate.
- **G3. Plugin path is distinct (R3/V6).** `.claude-plugin/` lives
  under `platforms/claude-code-plugin/`; `git rm -r .claude/` only
  touches root `.claude/`. V6 confirms.
- **G4. Content preserved three ways.** Skills → the plugin;
  pre-migration `.claude/` → archive branch; migration-era `.claude/`
  (+ hooks) → git history (+ `docs/dev-hooks/` if option B). Nothing
  irrecoverable.
- **G5. Docs already finalized (P5-T4).** CLAUDE.md doesn't depend on
  `.claude/`; README/REPO_STRUCTURE describe the loader as
  ported+removed. No doc re-pointing needed here.
- **G6. Confirmation gate is explicit (R6).** Like P5-T2, no `git rm`
  until the user says go.

### Pass 2 — 2026-05-21T08:40:00Z

- **G7. gitignored leftovers (V1).** Mirror of P5-T2's `legacy/tmp/`:
  if `settings.local.json` (or a `__pycache__`) is gitignored, the
  `.claude/` dir lingers on disk after `git rm` but is gitignored →
  won't propagate to the new `main`. Pre-flight identifies tracked
  vs gitignored.
- **G8. The session-start-handoff hook removal.** After removal, a
  *new* session won't auto-inject `plans/HANDOFF.md`. Acceptable —
  the migration ends at cutover; and HANDOFF is always readable in
  the repo. Noted.
- **G9. Option B `git mv` ordering.** If preserving, `git mv` the
  hooks out **before** `git rm -r .claude/` (otherwise they'd be
  deleted). Step sequence orders this correctly (Step 3 before
  Step 4).
- **G10. docs/dev-hooks/ README (option B).** A short README so the
  preserved hooks are self-explanatory (what each does, that they're
  the migration's dev-workflow tooling). Keeps them discoverable.
- **G11. No new findings.** Plan internally consistent; confirmation
  gate + hook-preservation choice explicit. Ready to run pre-flight,
  then request go-ahead.

## Implementation note (2026-05-21T08:55:00Z)

Executed after explicit user confirmation. User chose **option A
(straight removal; hooks → git-history-only)** and **Go**.
`git rm -r .claude/` removed **240 tracked files** (80,676
line-deletions). All verify gates green:

- **V1.** `git ls-files .claude/` == 0. The `.claude/` dir lingers
  on disk holding only the **gitignored `settings.local.json`**
  (won't propagate to the new `main`), same pattern as `legacy/tmp/`
  at P5-T2.
- **V2.** Conformance suite 31/31 (the `\.claude/` forbidden-token
  pattern in `test_spec_hygiene.py` scans `framework/`, unaffected
  by the root-`.claude/` removal).
- **V3.** Plugin smoke unaffected — 142 skill dirs; manifest valid.
- **V4.** No runtime root-`.claude/` dependency (the 2
  `tests/conformance/` hits are the forbidden-token pattern + its
  doc, not path reads).
- **V5.** Archive branch `legacy-ucx-v3.2-read-only` intact at
  `491e8db` (removal was working-branch-only).
- **V6.** Scope clean — staged diff is **only** `.claude/` deletions
  (240 files); the plugin's `platforms/claude-code-plugin/.claude-plugin/`
  is **not** in the diff.
- **V8.** Committed + pushed **immediately** (no pre-compact-snapshot
  hook post-removal).

**Session impact (expected):** the root `.claude/` removal disabled
this session's loaded project skills + the 3 migration hooks
(visible in the reduced available-skills list afterward). The
remaining Phase 5 work (P5-T5 verify, P5-T6 close) is git / doc /
conformance — no `.claude/` dependency. The 3 hooks remain
recoverable from working-branch git history (option A).

Content preserved three ways: the productized skills/agents/commands
in `platforms/claude-code-plugin/`; the pre-migration `.claude/` in
the `legacy-ucx-v3.2-read-only` archive branch; the migration-era
`.claude/` (incl. hooks + settings) in working-branch git history.
