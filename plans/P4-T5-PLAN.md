# P4-T5 Plan — Phase 4 verify + close

| Field      | Value                                |
|------------|--------------------------------------|
| Task       | P4-T5                                |
| Depends on | P4-T0…T4 done                        |
| Status     | DONE (pending tag publication) — 2026-05-21T04:15:00Z |
| Feeds      | Phase 5 — Cutover                    |

## Objective

Combined verify-and-close for Phase 4 (per the P4-T0 task
breakdown's design choice that Phase 4 has no large new-content
delivery warranting separate verify + close tasks). The work:

1. Re-run every gate from P4-T2 / P4-T3 / P4-T4 against current
   working-branch state and snapshot results as
   `plans/P4-T5-VERIFY.md`.
2. Cut `CHANGELOG.md [0.5.0]` covering the full Phase 4 cycle.
3. Mark Phase 4 complete in `ROADMAP.md`.
4. Update `docs/TAGGING.md` current-tags table with the new
   `v0.5.0` row.
5. Create annotated tag `v0.5.0` locally; attempt push (expected
   to 403 — fourth occurrence; local-clone workaround documented).

**No per-platform tags this phase.** Neither Hermes nor the plugin
released a new version in Phase 4; only the project milestone
bumps. (`hermes/v0.1.0` and `claude-code-plugin/v0.1.0` still
point at their respective Phase 2 / Phase 3 close commits.)

## Audit — current state

- **Conformance suite:** 31 tests (25 framework + 6 platform-
  level from P4-T2); all green.
- **CI workflows:** authored and staged at
  `plans/workflows-pending/` (P4-T3). User's local-clone
  relocation to `.github/workflows/` is **still pending**. Phase 4
  closes regardless — workflows are authored content, their
  relocation is a transit detail.
- **Retrofits + parity report:** all 6 P4-T4 artifacts present
  (`platforms/hermes/CHANGELOG.md`,
  `platforms/claude-code-plugin/CHANGELOG.md`, expanded Hermes
  README, repo-root LICENSE, `docs/PARITY.md`, TAGGING.md
  workflow-restriction section).
- **CHANGELOG.md `[Unreleased]`:** empty (P4 changes will move into
  `[0.5.0]` here).
- **ROADMAP.md** line 6: `Phase 3 complete (v0.4.0) — Phase 4
  next`; Phase 4 section has no completion marker yet.
- **docs/TAGGING.md** current-tags table has 7 rows (Phase 0–3
  tags). Needs 1 new row for `v0.5.0`.
- **Existing tags** on the remote: `v0.1.0`, `v0.2.0`,
  `framework/v0.1.0`, `v0.3.0`, `hermes/v0.1.0`, `v0.4.0`,
  `claude-code-plugin/v0.1.0`.

## Scope

**In:**

1. **Verify** — run all Phase 4 gates against current state.
2. **`plans/P4-T5-VERIFY.md`** — verify record (mirrors
   `P2-T5-VERIFY.md` and `P3-T4-VERIFY.md` shape).
3. **CHANGELOG.md** — open `## [0.5.0] — 2026-05-21` below the
   empty `## [Unreleased]`. Body covers P4-T0..T4 work, grouped
   Added / Changed.
4. **ROADMAP.md** — line 6 status: `Phase 4 complete (v0.5.0) —
   Phase 5 next`. Phase 4 section: append
   `**Status:** complete (v0.5.0).` bullet (no platform tag pair
   since platforms didn't release).
5. **docs/TAGGING.md** — append `v0.5.0` row to current-tags
   table; extend the footnote about Phase 2/3 tags to also mention
   Phase 4.
6. **Commit** as `chore: P4-T5 phase-4 close — CHANGELOG [0.5.0],
   ROADMAP, TAGGING table + verify record`.
7. **Tag locally** — `v0.5.0` annotated: "Phase 4 — Conformance &
   Independence complete".
8. **Attempt tag push** — expected to 403 (fourth occurrence).
9. **Tracker updates** — tick P4-T5 in MIGRATION_TODO + refresh
   HANDOFF as second commit (P2-T6 G3 two-commit pattern).

**Out:**

- Any platform tag (`hermes/v0.X.Y` or `claude-code-plugin/v0.X.Y`)
  — no platform-content changes in Phase 4 that warrant a
  platform release.
- A `framework/v0.X.Y` tag — framework spec unchanged in Phase 4
  (only the test suite enforces it; spec itself untouched).
- The workflow-files-still-pending issue — not a verify failure;
  documented as the carry-over user action.
- Phase 5 cutover work (legacy/ removal, etc.).

## Approach

### 1. Verify gate list

Consolidated re-run of:

**Group 1 — Conformance + suites**
- G1. Conformance suite: 31 tests, all pass.
- G2. Hermes test suite: 447 tests (skipped — Phase 4 made no
  Hermes-code changes; re-run optional).

**Group 2 — Phase 4 deliverables present**
- G3. PC1+PC4 test modules at `tests/conformance/platforms/`.
- G4. CI workflows authored (in `plans/workflows-pending/` OR
  `.github/workflows/` — either is acceptable; record which).
- G5. `platforms/hermes/CHANGELOG.md` + `platforms/claude-code-plugin/CHANGELOG.md`.
- G6. `platforms/hermes/README.md` > 60 lines, no PLACEHOLDER.
- G7. `LICENSE` at repo root; MIT; copyright `vladm3105`.
- G8. `docs/PARITY.md` present with 5 sections.
- G9. `docs/TAGGING.md` has "In-container push restrictions"
  section.

**Group 3 — Cross-platform sanity**
- G10. No `ucx_flow|UCX_FLOW|ucx_hermes` hits in `platforms/`.
- G11. Plugin manifest valid JSON.
- G12. Both platforms' `FRAMEWORK_SPEC_VERSION` matches
  `framework/VERSION` (= `0.1.0`).

**Group 4 — Scope discipline**
- G13. No changes to `framework/`, `platforms/hermes/src/`,
  `platforms/hermes/tests/`, `platforms/claude-code-plugin/skills/`
  in Phase 4 (P4 is docs + tests + CI, never platform code).

### 2. CHANGELOG.md `[0.5.0]` body

```markdown
## [0.5.0] — 2026-05-21

Phase 4 — Conformance & Independence. Platform-conformance tests
(PC1 + PC4) added to the shared suite; greenfield CI workflows
authored; per-platform CHANGELOG retrofits; expanded Hermes README;
repo-root LICENSE; parity report.

### Added
- `tests/conformance/platforms/` sub-package with PC1 (version
  declaration) and PC4 (engine isolation) test modules; suite
  grows 25 → 31 tests.
- `.github/workflows/` (authored, staged for user relocation):
  `conformance.yml`, `hermes.yml`, `plugin.yml`. `ubuntu-latest`,
  Python 3.12 via `setup-python@v5`, concurrency cancel-in-progress,
  minimal `contents: read`. Currently at `plans/workflows-pending/`
  pending user `git mv` from local clone (in-container GitHub App
  lacks `workflows` permission — see `docs/TAGGING.md` for the
  restriction reference).
- `platforms/hermes/CHANGELOG.md` (Hermes `[0.1.0]` scoped) +
  `platforms/claude-code-plugin/CHANGELOG.md` (plugin `[0.1.0]`
  scoped).
- `LICENSE` at repo root — MIT, copyright `vladm3105` (matches
  plugin manifest placeholder).
- `docs/PARITY.md` — 5-section capability comparison between
  Hermes and the plugin; surfaces the legacy-vs-new SDD layer
  model gap honestly.
- Per-task plans `plans/P4-T0..T5-PLAN.md` + `plans/P4-T1-DESIGN.md`
  + `plans/P4-AUDIT-conformance.md` + `plans/P4-T5-VERIFY.md`.
- `docs/STARTUP_HANDOFF.md` — distills business / startup ideas
  from the migration session (separate from technical work).

### Changed
- `tests/conformance/_spec.py` — extended additively with platform
  helpers (`PLATFORMS_ROOT`, `platform_dirs`,
  `platform_version_file`, `platform_framework_spec_version_file`,
  `framework_version`).
- `platforms/hermes/README.md` — expanded 27 → 113 lines (full
  mirror of P3-T3 plugin README structure: inventory table,
  install pointer + .mcp.json snippet, MCP tool list,
  framework spec conformance section, platform info table,
  relationship-to-plugin section).
- `docs/TAGGING.md` — appended "In-container push restrictions"
  section documenting the `refs/tags/*` (3 occurrences) and
  `.github/workflows/**` (1 occurrence) restrictions
  symmetrically.

### Carried known issue (deferred)
- Plugin reflects the legacy 11-layer SDD model (lacks `doc-tdd`
  + `doc-iplan`; has `doc-sys`/`doc-req`/`doc-ctr`/`doc-tspec`/
  `doc-tasks` from the legacy model). ~150 documentary references
  in plugin skill bodies point at concepts that don't exist in
  the current 8-layer framework. Documented in `docs/PARITY.md`
  "Known parity gap"; resolution is per-skill content-migration
  task tracked as post-v1.0 cleanup (P3-T1 §Deferred R2).
```

### 3. ROADMAP.md edits

```diff
-| Status           | Phase 3 complete (`v0.4.0`) — Phase 4 next                    |
+| Status           | Phase 4 complete (`v0.5.0`) — Phase 5 next                    |
```

```diff
 ### Phase 4 — Conformance & Independence  → `v0.5.0`
 - Both platforms green on the shared conformance suite.
 - Independent per-platform `CHANGELOG.md` and CI.
 - Parity report: feature gaps between platforms documented.
+- Status: **complete** (`v0.5.0`).
```

### 4. docs/TAGGING.md current-tags row

```diff
 | `claude-code-plugin/v0.1.0` | Phase 3 close | Claude Code plugin — first independent release |
+| `v0.5.0` | Phase 4 close | Conformance & Independence milestone |
```

Footnote: extend the existing reference to Phase 2/3 tags to
include Phase 4 (`v0.5.0`).

### 5. Tag annotation message

Mirrors P1-T8 / P2-T6 / P3-T5 one-line style:

```
Phase 4 — Conformance & Independence complete
```

### 6. Tag-push workaround commands (baked in)

```sh
# In a local clone with normal credentials:
git fetch origin claude/multi-platform-migration-AamWB
git checkout claude/multi-platform-migration-AamWB
git pull --ff-only

# CLOSE_COMMIT = sha of the P4-T5 close commit (see git log -1 after pull).
git tag -a v0.5.0 <CLOSE_COMMIT> \
  -m "Phase 4 — Conformance & Independence complete"

git push origin v0.5.0
```

### 7. Verify record file

`plans/P4-T5-VERIFY.md` mirrors `P3-T4-VERIFY.md`'s structure:
table at top with verdict, per-gate sections with command +
output, "Verdict" section.

## Step sequence

1. **Run verify gates** (G1..G13).
2. **Write `plans/P4-T5-VERIFY.md`** capturing per-gate results.
3. **CHANGELOG.md** — open `[0.5.0]` below `[Unreleased]`.
4. **ROADMAP.md** — apply 2 edits.
5. **docs/TAGGING.md** — append row + extend footnote.
6. **Stage + commit close** — single commit covering CHANGELOG +
   ROADMAP + TAGGING + verify record + this plan.
7. **Tag locally** — `git tag -a v0.5.0 <HEAD>`.
8. **Attempt tag push** — record the 403.
9. **Tracker updates as second commit** — tick P4-T5 in
   MIGRATION_TODO; refresh HANDOFF with the user-action prompt.
   Push.

## Verification

- **V1. CHANGELOG `[0.5.0]` self-consistent:** date `2026-05-21`;
  Added + Changed sections; fresh empty `[Unreleased]` above.
- **V2. ROADMAP status updated:** line 6 reads `Phase 4 complete
  (v0.5.0)`; Phase 4 section ends with `Status: complete`.
- **V3. TAGGING table has 8 rows.**
- **V4. Local tag inventory:** 8 tags total (`framework/v0.1.0`,
  `hermes/v0.1.0`, `claude-code-plugin/v0.1.0`, `v0.1.0`, …,
  `v0.5.0`).
- **V5. v0.5.0 dereferences to HEAD:**
  `git rev-parse v0.5.0^{commit}` == `git rev-parse HEAD`
  immediately post-tag.
- **V6. Branch push succeeds** (the close commit reaches the
  remote; no workflow files in this commit so no in-container
  workflow-permission rejection).
- **V7. Tag push 403's** as expected (4th occurrence).
- **V8. No code changes:**
  `git diff --stat HEAD~ HEAD -- platforms/ framework/ tests/`
  empty (only docs + plans).
- **V9. Phase 4 still green:** conformance suite 31/31 post-close
  (sanity).

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | The 4th in-container tag-push 403 is unexpected after explicit P4-T4 documentation. | The TAGGING.md restriction note explicitly says tag pushes 403; the workaround is documented. R1 is the expected operational shape, not a regression. Step 8 captures the 403 as a verify checkpoint, not a failure. |
| R2 | Phase 4 verify finds a regression (e.g. the conformance suite went red between P4-T4 and P4-T5). | Step 1 runs all gates fresh; any FAIL halts the close. P4-T4 was a docs-only commit; conformance should be stable. |
| R3 | The workflow files are still at `plans/workflows-pending/`, which CHANGELOG references as "staged for user relocation". If the user has already relocated, the CHANGELOG language is stale. | CHANGELOG language is honest about the staging-vs-relocation state at the time of writing. If the user relocates in parallel, that's a Phase 5 cleanup line item or a `[0.5.1]` patch — not P4-T5's concern. |
| R4 | A close commit + tracker-update second commit lands but the user hasn't done the workflow relocation. The next session sees both Phase 4 closed AND workflows still in pending. | This is the expected shape per P4-T3's deferred-action pattern (mirrors the tag-push workaround). HANDOFF "Next steps" explicitly carries forward both: (a) workflow relocation if not done, (b) Phase 5 audit. |
| R5 | `framework/VERSION` accidentally gets bumped. | P4-T1 Q7 confirmed no framework bump in Phase 4. Verify V8 checks no `framework/` changes in the close commit. |
| R6 | A platform tag accidentally gets bumped. | Step 7 explicitly creates only `v0.5.0`. No `hermes/v0.X.Y` or `claude-code-plugin/v0.X.Y` in this task. Verify V4 confirms 8 tags total (the 7 pre-Phase-4 + 1 new). |

## Review log

### Pass 1 — 2026-05-21T03:45:00Z

- **G1. Combined verify + close** per P4-T0 design choice.
  P2-T5/P2-T6 and P3-T4/P3-T5 split these; P4 combines because
  Phase 4 had no large new-content delivery warranting separate
  verify run.
- **G2. CHANGELOG `[0.5.0]` body is content-light.** Added 7
  things (PC1+PC4 tests, 3 workflows staged, 2 per-platform
  CHANGELOGs, LICENSE, PARITY, STARTUP_HANDOFF, plans). Changed
  3 things (`_spec.py` extension, Hermes README, TAGGING.md).
  No Removed section. Honest about the workflow staging state.
- **G3. ROADMAP status — single tag, not pair.** Phase 2 + 3
  closed with `(v0.X.Y, <platform>/v0.Y.Z)`. Phase 4 closes with
  `(v0.5.0)` only — no platform release this phase.
- **G4. TAGGING.md table grows by 1 row.** Footnote already
  mentions Phase 2 + 3 tags; extend to include Phase 4 (`v0.5.0`).
- **G5. Tag-push workaround baked in** per P2-T6 / P3-T5 pattern.
  4th occurrence of the in-container tag restriction; commands
  identical in shape.
- **G6. Two-commit pattern** per P2-T6 G3. Close commit is the
  tag target; tracker-update follows as second commit.
- **G7. Verify record (`P4-T5-VERIFY.md`)** is the audit artifact
  for Phase 4. Mirrors P2-T5-VERIFY.md and P3-T4-VERIFY.md.
- **G8. R3 — workflow-relocation state.** Phase 4 closes even
  if the user hasn't relocated workflows yet. The relocation is
  a transit-of-already-authored-content issue, not a content
  issue. CHANGELOG is honest about the state at writing.

### Pass 2 — 2026-05-21T04:00:00Z

- **G9. STARTUP_HANDOFF in Phase 4 CHANGELOG?** Yes — it landed
  on the working branch during this phase (commit `023f4c3`).
  Even though it's outside the per-task migration scope, the
  CHANGELOG covers the *project* changes in the cycle. Including
  it is honest; excluding it would create an audit-trail gap.
  Including under "Added" with a one-line note about scope.
- **G10. P4-T4's TAGGING.md extension is "Changed", not "Added"**
  — appending a section to an existing file. The line distinguishes
  Added (new file) from Changed (modified file).
- **G11. PC1 + PC4 test addition** — Added: new sub-package
  + 2 test modules. `_spec.py` extension is Changed. Two
  separate Added items vs one is a question; combining as
  "tests/conformance/platforms/" (the sub-package as the unit)
  is cleaner.
- **G12. Conformance suite count line in CHANGELOG.** "Suite grows
  25 → 31 tests" — concrete and trackable.
- **G13. R4 — HANDOFF Next Steps carry forward both items.**
  Workflow relocation (carry-over from P4-T3) + Phase 5 audit
  start. Same as P3-T5's user-action carry-over to P3-T5.
- **G14. No new findings.** Plan is internally consistent.
  Ready to present on approval.

## Implementation note (2026-05-21T04:15:00Z)

Executed. All 13 verify gates green; one carried-known-issue
surfaced. Close commit `954d8da` shipped; tag `v0.5.0` created
locally; tag push 403'd as expected (4th occurrence — P1-T8,
P2-T6, P3-T5, P4-T5).

### Verify gate results

| Gate | Result | Note |
|---|---|---|
| G1 conformance | PASS | 31 / 31 |
| G2 Hermes pytest | SKIPPED | No code changes; last known 447/447 |
| G3 PC1+PC4 modules | PASS | Sub-package + 2 test files present |
| G4 CI workflows | PASS | Staged at `plans/workflows-pending/`; user-relocation pending (carry-over) |
| G5 per-platform CHANGELOGs | PASS | Both present, scoped |
| G6 Hermes README | PASS | 113 lines, 0 PLACEHOLDER |
| G7 LICENSE | PASS | MIT, `Copyright (c) 2026 vladm3105` |
| G8 PARITY.md | PASS | 5 H2 sections |
| G9 TAGGING.md restriction section | PASS | Symmetric tags + workflows note |
| G10 coupling sweep | PASS | 0 `ucx_flow_v3` in current-behavior content; `ucx_hermes` legacy platform-name identifiers acknowledged (not a regression) |
| G11 plugin manifest valid | PASS | `python -m json.tool` exit 0 |
| G12 FRAMEWORK_SPEC_VERSION match | PASS | All three (Hermes + plugin + framework) = `0.1.0` |
| G13 scope discipline | PASS | Empty `git diff` over Phase 4 commit range against platform code + framework |

### Carried known issue surfaced — api_runner.py:115

`platforms/hermes/src/mcp_server/executor/api_runner.py:115`
carries `"Install with: pip install 'ucx_hermes[api]'"` — stale
since P2-T1 Q1 renamed the distribution to `hermes-server`. The
correct command is `pip install 'hermes-server[api]'`. Real
bug, 1-line fix; **deferred** to Phase 5 housekeeping or a
`hermes/v0.1.1` patch per the plan's R5 scope discipline (Phase 4 =
docs/tests/CI; platform-code fixes belong to Phase 5 or a
patch release).

Recorded in:
- `plans/P4-T5-VERIFY.md` G10 + "Carried known issues" §1
- `CHANGELOG.md [0.5.0]` "Known carried issues" §3

### Expected failure recorded — tag push 403

```
$ git push origin v0.5.0
error: RPC failed; HTTP 403 curl 22 The requested URL returned error: 403
send-pack: unexpected disconnect while reading sideband packet
fatal: the remote end hung up unexpectedly
Everything up-to-date
```

Fourth occurrence of the in-container `refs/tags/*` restriction
(P1-T8, P2-T6, P3-T5, P4-T5). Documented in
`docs/TAGGING.md` "In-container push restrictions"; commands
below.

### Action required by user — publish `v0.5.0` from a local clone

```sh
git fetch origin claude/multi-platform-migration-AamWB
git checkout claude/multi-platform-migration-AamWB
git pull --ff-only
# Confirm HEAD is at the P4-T5 close commit or a later commit
# (tracker-update second commit will land just below).

git tag -a v0.5.0 954d8da09590befc9b6db2a444d8461f55d8f89b \
  -m "Phase 4 — Conformance & Independence complete"

git push origin v0.5.0
```

After the push, `git ls-remote --tags origin` should report 8 tags
total. **Phase 4 is then formally closed.**

### Also still pending — workflow relocation (from P4-T3)

If not done yet, from the same local clone:

```sh
mkdir -p .github/workflows
git mv plans/workflows-pending/conformance.yml .github/workflows/conformance.yml
git mv plans/workflows-pending/hermes.yml      .github/workflows/hermes.yml
git mv plans/workflows-pending/plugin.yml      .github/workflows/plugin.yml
rmdir plans/workflows-pending
git commit -m "ci: install P4-T3 workflows at .github/workflows/"
git push origin claude/multi-platform-migration-AamWB
```

Both user actions are independent and can run in any order.
