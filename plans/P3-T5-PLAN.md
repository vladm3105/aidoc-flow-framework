# P3-T5 Plan — Phase 3 close

| Field      | Value                                |
|------------|--------------------------------------|
| Task       | P3-T5                                |
| Depends on | P3-T0…T4 done; P3-T4 verify green    |
| Status     | PLANNED — 2026-05-20T22:10:00Z       |
| Feeds      | Phase 4 — Conformance & Independence |

## Objective

Close Phase 3 by recording it as `[0.4.0]` in `CHANGELOG.md`, marking
the phase complete in `ROADMAP.md`, updating the `docs/TAGGING.md`
current-tags table, and cutting two annotated tags: `v0.4.0` (the
project milestone) and `claude-code-plugin/v0.1.0` (the platform's
first release). Mirrors P2-T6 in shape — formal versioning step;
no framework or platform code changes.

## Audit — current state

- **CHANGELOG.md** `[Unreleased]` is empty (placeholder header added
  by P2-T6 close). Phase 3 work moves here as `[0.4.0]`.
- **ROADMAP.md** line 6 status: `Phase 2 complete (v0.3.0) — Phase 3
  next`; Phase 3 section (line 57) carries no status marker.
- **docs/TAGGING.md** current-tags table has 5 rows (Phase 0–2 tags).
  Needs 2 new rows for `v0.4.0` and `claude-code-plugin/v0.1.0`. The
  footnote about the in-container 403 already applies; will reference
  P2-T6 + P3-T5 plans symmetrically.
- **Existing tags** on the remote: `v0.1.0`, `v0.2.0`, `v0.3.0`,
  `framework/v0.1.0`, `hermes/v0.1.0` (all from P1-T8 and P2-T6).
- **Tag-push environment:** in-container git proxy 403s on
  `refs/tags/*` (P1-T8 + P2-T6 close pattern). Workaround: re-create
  the same annotated tags on the same target commits in a local clone
  with normal credentials, then `git push origin <tagname>` from
  there. Commands baked in below.

## Scope

**In:**

1. **CHANGELOG.md** — open `[0.4.0] — 2026-05-20` below the current
   empty `[Unreleased]`. Body covers the full Phase 3 cycle (P3-T0
   audit through P3-T4 verify), grouped Added / Changed / Removed.
2. **ROADMAP.md** —
   - Line 6 status: `Phase 3 complete (v0.4.0) — Phase 4 next`.
   - Phase 3 section (line 57): append a
     `**Status:** complete (v0.4.0, claude-code-plugin/v0.1.0).`
     bullet at the end, matching the Phase 0/1/2 marker style.
3. **docs/TAGGING.md** — Current-tags table: append two rows for
   `v0.4.0` and `claude-code-plugin/v0.1.0`. Update the footnote
   note to reference P3-T5 alongside P1-T8 / P2-T6.
4. **Commit** the doc updates on the working branch as
   `chore: P3-T5 phase-3 close docs (changelog + roadmap + tagging table)`.
5. **Create** the two annotated tags **locally** on the close commit:
   - `v0.4.0` — milestone: "Phase 3 — Platform B: Claude Code plugin complete"
   - `claude-code-plugin/v0.1.0` — platform: "Claude Code plugin — first independent release; consumes framework/v0.1.0"
6. **Push** the working-branch commit (succeeds). Attempt to push
   the tags (expected to 403). Record the failure mode.
7. **Document** the local-clone workaround in the plan + commit
   message. User runs from their own clone.
8. **Tick** P3-T5 in `plans/MIGRATION_TODO.md`; refresh
   `plans/HANDOFF.md` (two-commit pattern per P2-T6 G3).

**Out:**

- Any code change in `framework/` or `platforms/{hermes,
  claude-code-plugin}/`. P3-T4 has locked the state; T5 only writes
  docs and tags.
- A `framework/v0.X.Y` tag — framework spec didn't change in
  Phase 3. Existing `framework/v0.1.0` still points at the
  authoritative spec commit.
- A `mark/<slug>` bookmark tag. None needed at this milestone.
- Symmetric retrofits to Hermes (platform CHANGELOG, expanded
  README) flagged as deferred during Phase 3 — out of P3-T5 scope.

## Approach

### 1. CHANGELOG.md edits

Open `## [0.4.0] — 2026-05-20` immediately below `## [Unreleased]`.
Body should cover the major deliverables of Phase 3 grouped by
Keep-a-Changelog category:

- **Added** —
  - `platforms/claude-code-plugin/` — the Claude Code plugin
    delivery: 171 net files (142 skills + 19 root files + 1 agent +
    1 command + the 4 P3-T3 adds + 4 top-level entries), plus
    `.claude-plugin/plugin.json` (7-field minimal manifest, name
    `aidoc-flow`), `VERSION`, `FRAMEWORK_SPEC_VERSION`, and a
    populated `README.md`.
  - `plans/P3-T0-PLAN.md` + `plans/P3-AUDIT-claude-code-plugin.md`
    — the Phase 3 audit (191 source files inventoried, copy-with-
    divergence relationship resolved) and task breakdown.
  - Per-task plans `plans/P3-T1..T5-PLAN.md`, each with the two-pass
    review log mandated by D-0007.
  - `plans/P3-T1-DESIGN.md` — 7 design decisions resolved before any
    content moved (manifest schema, non-doc skill scope, copy
    strategy, plugin name `aidoc-flow`, etc.).
  - `plans/P3-T4-VERIFY.md` — the formal Phase 3 verify record
    covering 22 gates (conformance, structure, coupling sweep,
    manifest validity, integration checks).

- **Changed** —
  - All `ai_dev_flow` placeholder paths in the ported skill content
    rewired to `framework/` (211 line hits across 30 files cleared).
    Class B (5 layer dirs → `framework/layers/`) and Class C
    (`ID_NAMING_STANDARDS.md` → `framework/governance/`) sub-path
    corrections applied; G13 illustration paths preserved.
  - `project-mngt/SKILL.md` — the one current-behavior
    `/opt/data/ucx_framework/...` reference rewired to repo-relative
    `framework/governance/...`.

- **Removed** —
  - 7 non-SDD-adjacent skill directories not ported: `code-review`,
    `refactor-flow`, `analytics-flow`, `devops-flow`, `ai-pr-review`,
    `google-adk`, `n8n` (P3-T1 Q2 — general-purpose, not SDD-coupled).
  - 3 `.claude/skills/` root files not ported: `README.md`
    (referenced obsolete multi-project symlink pattern),
    `google-adk_quickref.md`, `n8n_quickref.md` (parent skills out).
  - 47 broken symlinks the source `.claude/skills/` carried into the
    plugin via `cp -r` — self-referencing pointers at
    `/opt/data/docs_flow_framework/.claude/skills/<name>`, leftovers
    from the old multi-project symlink consumption pattern. Removed
    in-flight during P3-T4 verify (G18 finding).

The fresh empty `## [Unreleased]` header above stays as-is for
forward-looking entries.

### 2. ROADMAP.md edits

```diff
-| Status           | Phase 2 complete (`v0.3.0`) — Phase 3 next                    |
+| Status           | Phase 3 complete (`v0.4.0`) — Phase 4 next                    |
```

```diff
 ### Phase 3 — Platform B: Claude Code Plugin  → `v0.4.0`
 - Scaffold `.claude-plugin/plugin.json`.
 - Port the `doc-*` skill set, commands, and agents into the plugin.
 - Remove all Hermes/MCP dependency — Claude is the engine.
 - Plugin passes the same conformance suite.
+- Status: **complete** (`v0.4.0`, `claude-code-plugin/v0.1.0`).
```

### 3. docs/TAGGING.md current-tags table

Append two rows:

```diff
 | `hermes/v0.1.0` | Phase 2 close | Hermes platform — first independent release |
+| `v0.4.0` | Phase 3 close | Platform B: Claude Code plugin milestone |
+| `claude-code-plugin/v0.1.0` | Phase 3 close | Claude Code plugin — first independent release |
```

Update the footnote to mention the P3-T5 workaround alongside the
P2-T6 reference (same shape; the 403 pattern persisted).

### 4. Tag annotation messages

Following the P1-T8 + P2-T6 pattern (one-line subject):

- `v0.4.0`:
  > Phase 3 — Platform B: Claude Code plugin complete

- `claude-code-plugin/v0.1.0`:
  > Claude Code plugin — first independent release; consumes framework/v0.1.0

### 5. Tag-push workaround — bake in upfront

Per P1-T8 + P2-T6: the in-container git proxy returns HTTP 403 on
`refs/tags/*` pushes. Tags must be re-created on the same target
commits in a local clone and pushed from there.

The exact commands the user runs in their local clone after the
working-branch commit lands:

```sh
# In a local clone with normal GitHub credentials:
git fetch origin claude/multi-platform-migration-AamWB
git checkout claude/multi-platform-migration-AamWB
git pull --ff-only

# CLOSE_COMMIT is the sha of the P3-T5 close commit (visible via
# `git log -1 --oneline` after the pull).

git tag -a v0.4.0 <CLOSE_COMMIT> \
  -m "Phase 3 — Platform B: Claude Code plugin complete"
git tag -a claude-code-plugin/v0.1.0 <CLOSE_COMMIT> \
  -m "Claude Code plugin — first independent release; consumes framework/v0.1.0"

git push origin v0.4.0 claude-code-plugin/v0.1.0
```

After the push, the in-container session verifies via
`git ls-remote --tags origin` — expected 7 tags total.

## Step sequence

1. **CHANGELOG.md** — apply the `[0.4.0]` body (§Approach.1).
2. **ROADMAP.md** — apply the two edits (§Approach.2).
3. **docs/TAGGING.md** — append the two rows + update the footnote
   (§Approach.3).
4. **Stage + commit** — single commit:
   `chore: P3-T5 phase-3 close — CHANGELOG [0.4.0], ROADMAP, TAGGING table`.
   Push to working branch.
5. **Tag locally** — create the two annotated tags on the new HEAD
   via the messages in §Approach.4.
6. **Tag push (expected to fail)** —
   `git push origin v0.4.0 claude-code-plugin/v0.1.0`; capture the
   403; record the failure mode + local-clone workaround in the
   post-commit note.
7. **Update trackers** — tick P3-T5 in `MIGRATION_TODO.md`; refresh
   `HANDOFF.md` to show Phase 3 closed pending tag publication.
8. **Verify** (see below).
9. **Push** the tracker updates (a second commit per the P2-T6 G3
   two-commit pattern).

## Verification

- **CHANGELOG.md `[0.4.0]` present and self-consistent:**
  - Date `2026-05-20` matches the commit date.
  - Added / Changed / Removed sections cover the Phase 3 cycle.
  - A fresh empty `[Unreleased]` section stays above `[0.4.0]`.
- **ROADMAP.md status updated:** line 6 reads `Phase 3 complete
  (v0.4.0) — Phase 4 next`; Phase 3 section ends with a `Status:
  complete` bullet.
- **docs/TAGGING.md table has 7 rows:** `v0.1.0`, `v0.2.0`,
  `framework/v0.1.0`, `v0.3.0`, `hermes/v0.1.0`, `v0.4.0`,
  `claude-code-plugin/v0.1.0`.
- **Local tag inventory:** `git tag -l` lists 7 tags.
- **Tags are annotated and point at HEAD:** `git rev-parse
  v0.4.0^{commit}` and `git rev-parse claude-code-plugin/v0.1.0^{commit}`
  both equal `git rev-parse HEAD` immediately post-tag.
- **Branch push:** the working-branch commit reaches the remote.
- **Tag push (expected failure):** returns HTTP 403 — recorded in
  the post-implementation note as expected, **not** as verify failure.
- **No code changes:** `git diff --stat HEAD~ HEAD -- platforms/
  framework/` returns empty.
- **Phase 3 still green:** re-run conformance suite (25/25) as a
  pre-tag sanity check.

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | In-container 403 on tag push. | Workaround baked into §Approach.5 + commit message. User runs from local clone. |
| R2 | The `claude-code-plugin/v0.1.0` namespace is verbose. | Pattern from `docs/TAGGING.md` D-0011: `<platform>/vX.Y.Z`. `claude-code-plugin` is the platform name; the verbose tag matches the platform directory. Symmetric with `hermes/v0.1.0`. |
| R3 | A code change slips between P3-T4 verify and P3-T5 close. | Verify clause runs the conformance suite again. Also: `git diff --stat HEAD~1 HEAD -- platforms/ framework/` should show only doc files. |
| R4 | The CHANGELOG entry references a `LICENSE` file the repo doesn't have. | Plugin manifest declares `"license": "MIT"` as a placeholder; CHANGELOG mentions MIT but does not link to a missing file. P3-T1 §Deferred R1 tracks the LICENSE work item. |
| R5 | SemVer-clash between `claude-code-plugin/v0.1.0` and `framework/v0.1.0` / `hermes/v0.1.0`. | Per D-0011, tag namespaces are disjoint. Same SemVer across namespaces is the documented norm. |
| R6 | Single close commit + tag commit conflate two operations. | Per P2-T6 G3: two-commit pattern. Close commit is the tag target; tracker updates follow as a chore commit. |
| R7 | The 47-symlink cleanup was part of P3-T4 (commit `634c59f`); a future archeologist could wonder if it belongs in P3-T5 CHANGELOG. | CHANGELOG body's **Removed** section explicitly cites the P3-T4 commit + the G18 finding. Traceability preserved. |

## Review log

### Pass 1 — 2026-05-20T22:20:00Z

- **G1. Workaround baked in upfront (P2-T6 G1 lesson carried
  forward).** §Approach.5 carries the exact commands. P1-T8 had to
  derive them post-failure; P2-T6 baked them in; P3-T5 inherits the
  pattern.
- **G2. CHANGELOG body covers full Phase 3 cycle.** Added / Changed
  / Removed groupings mirror P2-T6's `[0.3.0]`. The 47-symlink
  cleanup goes under **Removed** with cross-reference to P3-T4 G18.
- **G3. Two-commit pattern (P2-T6 G3 + G9).** Close commit is the
  tag target; trackers follow as a separate chore commit. Avoids
  amending the tag's target.
- **G4. Verify gate for 403 (P2-T6 R7).** Expected 403 recorded as
  "tag push attempted, returned 403 as expected" — not graded as
  verify failure.
- **G5. No code changes (R3).** `git diff --stat HEAD~ HEAD --
  platforms/ framework/` is the invariant. P3-T4 locked the state;
  T5 ships docs + tags only.
- **G6. Tag annotation messages.** One-line subject, no body —
  matches P1-T8 + P2-T6 precedent. Verified by `git tag -n` on
  existing 5 tags.
- **G7. List-completeness (P2-T0 Pass 3 lesson).** §Approach.1 lists
  the full Phase 3 work. Spot-check against
  `plans/MIGRATION_TODO.md` Phase 3 section: T0/T1/T2/T3/T4 all
  covered.
- **G8. SemVer-namespace cross-check (R5).** `claude-code-plugin/v0.1.0`
  ≠ `framework/v0.1.0` ≠ `hermes/v0.1.0` because the namespace
  prefix differs. Per D-0011 / `docs/TAGGING.md`, this is the
  documented norm.

### Pass 2 — 2026-05-20T22:30:00Z

- **G9. Cross-check P3-T4 verify record stays valid through P3-T5.**
  R3 enforces no-code-change so `plans/P3-T4-VERIFY.md` remains the
  authoritative Phase 3 verify gate. Confirmed: P3-T5 only edits
  `CHANGELOG.md`, `ROADMAP.md`, `docs/TAGGING.md`, and the trackers.
- **G10. `[Unreleased]` retention.** P2-T6's pattern was to fold the
  pre-existing `[Unreleased]` items into the released section. P3
  inherits an empty `[Unreleased]` (P2-T6 left it empty); no items
  to fold here.
- **G11. `framework/VERSION` untouched.** Phase 3 didn't change
  `framework/`; framework's SemVer stays at `0.1.0`. No new
  `framework/v0.X.Y` tag. Out-clause covers this.
- **G12. Tag-push partial publication.** Both tags pushed in one
  `git push` invocation — atomic-ish. Flag worth raising in the
  workaround commands for the user.
- **G13. No new findings.** Plan is internally consistent and the
  verify gates are observable. Ready to present on approval.
