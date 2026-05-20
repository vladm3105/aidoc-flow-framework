# P2-T6 Plan — Phase 2 close

| Field      | Value                                |
|------------|--------------------------------------|
| Task       | P2-T6                                |
| Depends on | P2-T0…T9 (all done), P2-T5 verify green |
| Status     | PLANNED — 2026-05-20T16:35:00Z       |
| Feeds      | Phase 3 (Platform B — Claude Code plugin) |

## Objective

Close Phase 2 by recording it as `[0.3.0]` in `CHANGELOG.md`, marking
the phase complete in `ROADMAP.md`, updating the `docs/TAGGING.md`
current-tags table, and cutting two annotated tags: `v0.3.0` (the
project milestone) and `hermes/v0.1.0` (the platform's first release).
This task does not change any framework or platform code — it's the
formal versioning step.

## Audit — current state

- **CHANGELOG.md** has `[Unreleased]` with 2 Added items (`docs/TAGGING.md`,
  `ROADMAP.md` post-v1.0 section) and 2 Changed items (D-0012 framework
  purpose, D-0012 R1+R2 refinements) — all of which post-date `[0.2.0]`
  and belong in `[0.3.0]`.
- **ROADMAP.md** line 6 says `Phase 1 complete (v0.2.0) — Phase 2 next`;
  Phase 2 section (line 52) carries no status marker.
- **docs/TAGGING.md** "Current tags" table (bottom) lists `v0.1.0`,
  `v0.2.0`, `framework/v0.1.0`. Needs two new rows.
- **Existing tags** on the remote: `v0.1.0`, `v0.2.0`, `framework/v0.1.0`
  (P1-T8 close).
- **Tag-push environment:** in-container git proxy 403s on `refs/tags/*`
  (P1-T8 close stack). Workaround: re-create the same annotated tags on
  the same target commits in a local clone with normal credentials, then
  `git push origin <tagname>` from there. Plan bakes the exact commands
  in below so the user can act on them without recon.

## Scope

**In:**

1. **CHANGELOG.md** — convert `[Unreleased]` into `[0.3.0] — 2026-05-20`
   and expand the body to cover the full Phase 2 work (P2-T0 audit
   through P2-T5 verify). Preserve the 4 existing items, append 8–10
   new ones grouped Added / Changed / Removed. Open a new empty
   `[Unreleased]` section above for forward-looking entries.
2. **ROADMAP.md** — line 6 status: `Phase 2 complete (v0.3.0) —
   Phase 3 next`. Line 52 Phase 2 section: append a `**Status:**
   complete (v0.3.0, hermes/v0.1.0).` bullet at the end, matching the
   Phase 0/1 marker style.
3. **docs/TAGGING.md** — Current-tags table: append two rows for
   `v0.3.0` and `hermes/v0.1.0`. Footnote note about the
   in-container 403 remains accurate.
4. **Commit** the doc updates on the working branch as
   `chore: P2-T6 phase-2 close docs (changelog + roadmap + tagging table)`.
5. **Create** the two annotated tags **locally** on the close commit:
   - `v0.3.0` — milestone: "Phase 2 — Platform A: Hermes Re-homing complete"
   - `hermes/v0.1.0` — platform: "Hermes — first independent release; consumes framework/v0.1.0"
6. **Push** the working-branch commit (this will succeed). Attempt to
   push the tags (this is expected to 403 — record the failure mode).
7. **Document** the local-clone workaround commands in the plan + the
   commit message + `docs/TAGGING.md` "Current tags" note. The user
   runs them from their own clone.
8. **Tick** P2-T6 in `plans/MIGRATION_TODO.md`; refresh `plans/HANDOFF.md`.

**Out:**

- Any code change in `framework/` or `platforms/hermes/`. P2-T5 has
  already locked the state; T6 only writes docs and tags.
- A `framework/v0.X.Y` tag — the framework spec didn't change in
  Phase 2. The existing `framework/v0.1.0` tag still points at the
  authoritative spec commit.
- A platform tag for Claude Code (Phase 3 territory).
- `mark/<slug>` bookmark tags. None are needed at this milestone.

## Approach

### 1. CHANGELOG.md edits

Replace `## [Unreleased]` with a new empty Unreleased + a full
`## [0.3.0] — 2026-05-20` section. The body should cover the major
deliverables of Phase 2 grouped by Keep-a-Changelog category:

- **Added** — the 4 existing Unreleased items (TAGGING.md, ROADMAP
  post-v1.0, D-0012 framework-purpose, D-0012 R1+R2) plus:
  - `platforms/hermes/` — the Hermes MCP server platform: 200 files
    via port-with-repoint (P2-T3), 64 verbatim (P2-T2), 181
    agent-skills (P2-T7), plus `VERSION`, `FRAMEWORK_SPEC_VERSION`,
    `pyproject.toml` (`hermes-server` / `0.1.0` / `hermes-mcp` entry).
  - `plans/P2-T0-PLAN.md` audit and the per-task plans (T1..T9)
    documenting the Phase 2 development.
  - Five new decisions in `plans/DECISIONS.md`: D-0013
    (single-source-of-truth for templates — platforms consume
    `framework/layers/`).
  - `plans/P2-T5-VERIFY.md` — the formal Phase 2 verify record (14
    gates green).
- **Changed** — the 2 existing Unreleased items (D-0012 refinements)
  plus:
  - All `ucx_flow_v3` runtime coupling rewritten to `framework/`
    (`framework/registry/`, `framework/layers/<NN>_<X>/`) — 18 files
    in the edit set; 11 historical-context docs preserved verbatim
    per the G13 lesson.
  - MCP scaffold + validation runtime rewired to consume
    `framework/layers/<NN>_<X>/` (P2-T9), closing the D-0013
    architectural gap.
  - `.mcp.json` cwd repointed to `platforms/hermes/src`.
  - `plans/P2-AUDIT-hermes.md` §3a extended to include test files;
    new §3c "Documentation cluster" classifies docs/ refs as
    historical-vs-current.
- **Removed** —
  - The 8 drifted layer templates at
    `platforms/hermes/agent-skills/.../sdd-orchestrator/templates/`
    (P2-T8); skill now consumes `framework/layers/` per D-0013.
  - The 6 D-0013-obsolete sync files from the skill package (P2-T7).
  - The `templates/` row from `CANONICAL_SCAFFOLD_MAPPINGS` and
    the no-op `exists()` branch from `_default_ssd_root` (P2-T9).

### 2. ROADMAP.md edits

```diff
-| Status           | Phase 1 complete (`v0.2.0`) — Phase 2 next                    |
+| Status           | Phase 2 complete (`v0.3.0`) — Phase 3 next                    |
```

```diff
 ### Phase 2 — Platform A: Hermes Re-homing  → `v0.3.0`
 - Copy `legacy/ucx_hermes/` + `legacy/mcp_ucx/` into `platforms/hermes/`.
 - Point Hermes at `framework/`; declare `framework_spec_version`.
 - Hermes passes the conformance suite.
+- Status: **complete** (`v0.3.0`, `hermes/v0.1.0`).
```

### 3. docs/TAGGING.md current-tags table

Append two rows:

```diff
 | `framework/v0.1.0` | Phase 1 close | Framework spec — first independent release |
+| `v0.3.0` | Phase 2 close | Platform A: Hermes Re-homing milestone |
+| `hermes/v0.1.0` | Phase 2 close | Hermes platform — first independent release |
```

The footnote about the in-container 403 remains accurate (and now also
applies to `v0.3.0` + `hermes/v0.1.0`).

### 4. Tag annotation messages

Following the P1-T8 pattern (one-line subject):

- `v0.3.0`:
  > Phase 2 — Platform A: Hermes Re-homing complete

- `hermes/v0.1.0`:
  > Hermes — first independent release; consumes framework/v0.1.0

### 5. Tag-push workaround — bake in from the start

Per P1-T8: the in-container git proxy returns HTTP 403 on
`refs/tags/*` pushes. The tags must be re-created on the same target
commits in a local clone and pushed from there. The exact commands
(to be run in the user's local clone after the working-branch commit
is pulled):

```sh
# In a local clone with normal GitHub credentials:
git fetch origin claude/multi-platform-migration-AamWB
git checkout claude/multi-platform-migration-AamWB
git pull --ff-only

# CLOSE_COMMIT will be the sha of the P2-T6 close commit pushed by
# the in-container session (visible via `git log -1 --oneline` after
# the pull).

git tag -a v0.3.0 <CLOSE_COMMIT> \
  -m "Phase 2 — Platform A: Hermes Re-homing complete"
git tag -a hermes/v0.1.0 <CLOSE_COMMIT> \
  -m "Hermes — first independent release; consumes framework/v0.1.0"

git push origin v0.3.0 hermes/v0.1.0
```

After the user runs these from their local clone, the in-container
session can verify with `git ls-remote --tags origin` to confirm both
tags landed on the remote.

## Step sequence

1. **CHANGELOG.md** — apply the Unreleased → `[0.3.0]` conversion + body
   expansion (§Approach.1). Open a fresh empty `[Unreleased]` section.
2. **ROADMAP.md** — apply the two edits (§Approach.2).
3. **docs/TAGGING.md** — append the two rows to the current-tags table
   (§Approach.3).
4. **Stage + commit** — single commit:
   `chore: P2-T6 phase-2 close — CHANGELOG [0.3.0], ROADMAP, TAGGING table`.
   Push to working branch.
5. **Tag locally** — create the two annotated tags on the new HEAD via
   the messages in §Approach.4.
6. **Tag push (expected to fail)** —
   `git push origin v0.3.0 hermes/v0.1.0`; capture the 403; record the
   failure mode + the local-clone workaround in the post-commit note.
7. **Update trackers** — tick P2-T6 in `MIGRATION_TODO.md`; refresh
   `HANDOFF.md` to show Phase 2 closed pending tag publication.
8. **Verify** (see below).
9. **Push** the tracker updates (a second commit, or amended into
   the close commit — see G9 in Review log; the plan opts for
   a second commit to keep the close commit clean).

## Verification

- **CHANGELOG.md `[0.3.0]` section present and self-consistent:**
  - Date `2026-05-20` matches the commit date.
  - Body covers Added / Changed / Removed sections.
  - The 4 pre-existing Unreleased items are folded in (no orphans).
  - A fresh empty `[Unreleased]` section opens above `[0.3.0]`.
- **ROADMAP.md status updated:** line 6 reads `Phase 2 complete
  (v0.3.0) — Phase 3 next`; Phase 2 section ends with a `Status:
  complete` bullet.
- **docs/TAGGING.md table has 5 rows:** `v0.1.0`, `v0.2.0`,
  `framework/v0.1.0`, `v0.3.0`, `hermes/v0.1.0`.
- **Local tag inventory:**
  `git tag -l` lists `framework/v0.1.0`, `hermes/v0.1.0`, `v0.1.0`,
  `v0.2.0`, `v0.3.0` (5 tags total).
- **Tags are annotated:** `git tag -n v0.3.0 hermes/v0.1.0` prints
  both with their annotation messages.
- **Tag target:** both new tags point at the P2-T6 close commit
  (`git rev-parse v0.3.0 hermes/v0.1.0` both return the same sha as
  `git rev-parse HEAD` immediately post-tag).
- **Branch push:** the working-branch commit reaches the remote
  (`git ls-remote origin claude/multi-platform-migration-AamWB`
  returns the new sha).
- **Tag push (expected failure):** `git push origin v0.3.0
  hermes/v0.1.0` returns HTTP 403 — recorded in the post-implementation
  note as expected, **not** as a verify-gate failure.
- **No code changes:** `git diff --stat HEAD~ HEAD -- platforms/ framework/`
  returns empty; the close commit touches only `CHANGELOG.md`,
  `ROADMAP.md`, `docs/TAGGING.md`.
- **Phase 2 still green:** re-run conformance suite (25/25) as a
  pre-tag sanity check. Hermes own suite (447/447) was already
  verified at P2-T5; no need to re-run.

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | The in-container git proxy 403s on the tag push (expected from P1-T8). | Bake the local-clone workaround commands directly into the plan (§Approach.5) and the commit message. Tags exist locally on the in-container session; the user re-creates them in a local clone with the same messages on the same target commit. No data loss, no rebase. |
| R2 | The pre-existing `[Unreleased]` items get lost when converting the section to `[0.3.0]`. | Edits are explicit (move the 4 items into the `[0.3.0]` body under Added / Changed). Verify gate confirms the 4 items appear in `[0.3.0]`. |
| R3 | A future `[Unreleased]` entry lands before the next phase close and gets confused with v0.3.0. | The fresh empty `[Unreleased]` section above `[0.3.0]` is the clear destination for forward-looking entries. Convention followed throughout the project. |
| R4 | The tag annotation messages drift from the project's naming convention. | Convention from P1-T8: short one-line subject, no body. Confirmed by `git tag -n` on the existing 3 tags. New messages follow the same shape. |
| R5 | A code change slips in between P2-T5 verify and P2-T6 close, invalidating the verify record. | Verify clause runs the conformance suite again (cheap, 0.23s). Also: `git diff --stat HEAD~1 HEAD` after the close commit should show only doc files. |
| R6 | The CHANGELOG ends up double-counting (e.g. a TAGGING.md entry under both v0.2.0 and v0.3.0). | The 4 pre-existing items currently live in `[Unreleased]` because they post-dated v0.2.0. Moving them into `[0.3.0]` is the correction — they were never in `[0.2.0]`. Verify gate checks the `[0.2.0]` section is untouched. |
| R7 | The verify note about the tag-push 403 reads as a verify failure. | Step 6 of the sequence explicitly classifies the 403 as expected; the verify gate records "tag push attempted, returned 403 as expected" and is not graded as failure. P1-T8 set the precedent. |
| R8 | A SemVer-clash risk between `hermes/v0.1.0` and `framework/v0.1.0`. | Per `docs/TAGGING.md` namespace rules (D-0011), tag namespaces are disjoint. `hermes/v0.1.0` and `framework/v0.1.0` are different refs — same SemVer is allowed and the project's documented norm. |
| R9 | Single close commit + tag commit conflate two operations. | The plan opts for a single close commit (CHANGELOG + ROADMAP + TAGGING table together) with the trackers (`MIGRATION_TODO.md`, `HANDOFF.md`) following as a small chore commit afterward. Cleaner separation: the close commit is the tag's target; the tracker update post-dates it. |

## Review log

### Pass 1 — 2026-05-20T16:45:00Z

- **G1. Workaround baked in from the start (P2-T0 task brief
  guidance).** §Approach.5 carries the exact commands the user runs in
  their local clone. P1-T8 had to derive them post-failure; P2-T6
  surfaces them up-front.
- **G2. Unreleased → 0.3.0 conversion carries the 4 pre-existing
  items.** The 2 Added + 2 Changed entries that post-dated v0.2.0
  (TAGGING.md, ROADMAP post-v1.0, D-0012 purpose, D-0012 R1+R2) are
  Phase 2 cycle deliverables even though they preceded the Hermes
  port itself. Their natural home is `[0.3.0]`.
- **G3. Two-commit pattern.** §Step 9 + R9: close commit (CHANGELOG +
  ROADMAP + TAGGING) is the tag target; trackers (`MIGRATION_TODO.md`,
  `HANDOFF.md`) follow as a separate chore commit. Avoids the temptation
  to amend the close commit and force-push (CLAUDE.md hygiene).
- **G4. Verify gate for 403.** R7 classifies the expected 403 as
  "verify recorded the expected failure mode", not as "verify failed".
  Step 6 makes this explicit.
- **G5. Phase 2 close is doc-only.** R5 makes the no-code-change
  invariant a verify-gate (`git diff --stat HEAD~ HEAD -- platforms/
  framework/` is empty). The close commit ships zero code; the verify
  record from P2-T5 stands.
- **G6. Annotation messages match precedent.** R4 + §Approach.4:
  message shape mirrors P1-T8 (one-line subject). No body. `git tag -n`
  on the existing 3 tags confirms the shape.
- **G7. List-completeness (P2-T0 Pass 3 lesson).** §Approach.1 lists
  the full Phase 2 work to include in the changelog; spot-check
  against `plans/MIGRATION_TODO.md` Phase 2 section to confirm no
  task missed (T0/T1/T2/T3/T5/T6/T7/T8/T9 — all present).
- **G8. SemVer-namespace cross-check (R8).** `hermes/v0.1.0` ≠
  `framework/v0.1.0` because the namespace prefix is different; per
  D-0011 / `docs/TAGGING.md` this is the documented norm. No clash.
- **G9. Trackers as a second commit, not amend.** Two reasons:
  (a) the close commit is the tag target — amend would force a tag
  retag, which is bad hygiene. (b) The trackers reference the close
  commit's sha in the HANDOFF log, so they must be edited *after*
  the close commit exists.

### Pass 2 — 2026-05-20T16:55:00Z

- **G10. P2-T5 verify record should be preserved through P2-T6.**
  R5 enforces no-code-change so `plans/P2-T5-VERIFY.md` stays valid as
  the formal Phase 2 verify record. Confirmed: `git diff --stat HEAD~1
  HEAD -- plans/P2-T5-VERIFY.md` after P2-T6 close should be empty.
- **G11. `[Unreleased]` body retention check.** Re-read Approach §1
  with the existing CHANGELOG body open: confirmed the 4 items
  (TAGGING.md, ROADMAP post-v1.0, D-0012 framework-purpose, D-0012
  R1+R2) all reference Phase-2-cycle work and belong in `[0.3.0]`. No
  item should be left behind in `[Unreleased]` after the conversion.
- **G12. Tag-push success criterion is binary, not partial.** If
  `v0.3.0` lands on the remote but `hermes/v0.1.0` doesn't (or vice
  versa), Phase 2 isn't formally closed. The user's local-clone
  push command pushes both in one `git push` invocation —
  atomic-enough that partial-publication is unlikely. Worth flagging
  for the user when they run the workaround.
- **G13. `framework/VERSION` unchanged.** Phase 2 didn't touch
  `framework/`; framework's SemVer stays at `0.1.0` and no new
  `framework/v0.X.Y` tag is needed. Out-clause covers this.
- **G14. No new findings.** Plan is internally consistent and the
  verify gates are observable. Ready to present on approval.
