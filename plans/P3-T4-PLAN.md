# P3-T4 Plan — Phase 3 verify

| Field      | Value                                |
|------------|--------------------------------------|
| Task       | P3-T4                                |
| Depends on | P3-T0, P3-T1, P3-T2, P3-T3           |
| Status     | DONE — 2026-05-20T21:55:00Z          |
| Feeds      | P3-T5 (Phase 3 close)                |

## Objective

Run a consolidated, end-to-end re-verification of every gate that
P3-T2 and P3-T3 individually checked, plus the items P3-T1 §Deferred
flagged for the verify pass (auto-discovery against non-`SKILL.md`
files at `skills/` root, per-skill content equivalence vs source).
Snapshot results as the formal Phase 3 verify record at
`plans/P3-T4-VERIFY.md`. Mirrors P2-T5 in shape — a gate, not a code
change. If any gate fails, halt and re-open the failing task; if all
pass, hand off to P3-T5.

## Scope

**In:**

- Re-run every verify gate from P3-T2 + P3-T3 against the current
  working-branch state.
- Add the three integration-level gates that the per-task plans
  couldn't run alone:
  - **Plugin file-inventory total** vs the math from the four tasks
    (mirrors P2-T5 G14).
  - **Per-skill content equivalence** vs `.claude/` source for a
    spot-check sample (catches accidental drift in the cp -r +
    sed pipeline).
  - **Auto-discovery sanity** — Claude Code's `SKILL.md` discovery
    convention applied to `platforms/claude-code-plugin/skills/`
    shouldn't trip on the 19 non-`SKILL.md` root files (P3-T1
    §Deferred R3).
- Write `plans/P3-T4-VERIFY.md` with per-gate output excerpts —
  Phase 3 has no CI/CD; the record is the artifact.

**Out:**

- Any code or content change. If a gate fails, the fix is **not**
  P3-T4 — re-open the responsible task (T2 / T3) and let P3-T4 re-run
  after the fix lands.
- Conformance suite extension to platform-level checks (still
  Phase 4).
- `CHANGELOG.md` / `ROADMAP.md` / tag work (still P3-T5).

## Approach

Run the gates in four groups; record pass/fail per gate.

### Group 1 — Conformance + structural baseline

- **G1.** `pytest tests/conformance/` from repo root: expect `25
  passed`. Sanity — the suite scans only `framework/`.
- **G2.** Top-level structure: `ls -A platforms/claude-code-plugin/`
  returns exactly 7 entries (`.claude-plugin`, `FRAMEWORK_SPEC_VERSION`,
  `README.md`, `VERSION`, `agents`, `commands`, `skills`). No
  `CHANGELOG.md` (Hermes-precedent). No `hooks/` (P3-T1 Q7).

### Group 2 — Content + coupling sweep

- **G3.** Skill dirs: `find platforms/claude-code-plugin/skills
  -mindepth 1 -maxdepth 1 -type d | wc -l` returns **142**.
- **G4.** Skill root files: `find platforms/claude-code-plugin/skills
  -maxdepth 1 -type f | wc -l` returns **19**.
- **G5.** Agents + commands: each directory has exactly 1 file.
- **G6.** No coupling to Hermes:
  `grep -rEc 'ucx_flow|UCX_FLOW|ucx_hermes' platforms/claude-code-plugin/`
  returns 0.
- **G7.** No `ai_dev_flow` residual:
  `grep -rE '\bai_dev_flow\b' platforms/claude-code-plugin/`
  returns 0.
- **G8.** No bare-layer-dir refs (Class B corrected):
  `grep -rE 'framework/0[1-5]_(BRD|PRD|EARS|BDD|ADR)/' platforms/claude-code-plugin/`
  returns 0.
- **G9.** No bare `framework/ID_NAMING_STANDARDS.md` (Class C
  corrected): `grep -rE '(^|[^/])framework/ID_NAMING_STANDARDS\.md' platforms/claude-code-plugin/`
  returns 0.
- **G10.** No `/opt/data/ucx_framework` framework refs:
  `grep -rn '/opt/data/ucx_framework' platforms/claude-code-plugin/`
  returns nothing.
- **G11.** G13 illustration paths preserved (set-membership check):
  - `grep -n '/opt/data/trading_nexus_v4.2' platforms/claude-code-plugin/skills/doc-req-autopilot/SKILL.md`
    matches line 312.
  - `grep -n '/opt/data/my_project' platforms/claude-code-plugin/skills/project-init/SKILL.md`
    matches line 149.

### Group 3 — Manifest + version

- **G12.** `.claude-plugin/plugin.json` is valid JSON.
- **G13.** Manifest field set:
  `python -c "import json; print(sorted(json.load(open('platforms/claude-code-plugin/.claude-plugin/plugin.json')).keys()))"`
  returns the expected 7 keys.
- **G14.** Manifest `name == "aidoc-flow"`.
- **G15.** Manifest `version == "0.1.0"`.
- **G16.** `cat VERSION` returns `0.1.0`; file is 6 bytes.
- **G17.** `diff FRAMEWORK_SPEC_VERSION framework/VERSION` empty.

### Group 4 — Integration-level gates

- **G18. Plugin file-inventory total.**
  `git ls-files platforms/claude-code-plugin/ | wc -l` matches the
  sum of P3-T2/T3 task numbers. Audit math:
  P3-T2 ports 168 files + P3-T3 adds 3 new files (plugin.json,
  VERSION, FRAMEWORK_SPEC_VERSION) + the P0-scaffolded README.md
  was overwritten in P3-T3 (no count change) → expected 171 files.
  Record the actual `wc -l` output; if it differs from 171, document
  the reason (e.g. hidden `.gitkeep` files in `cp -r`, or nested
  helper files inside individual skill dirs counted as separate
  files by `git ls-files` but as part of one "skill" in the
  Q6 recipe).
- **G19. Per-skill content equivalence** (spot-check). For 3
  random skills (`doc-brd`, `doc-flow`, `project-init`), `diff`
  the post-port content vs the source `.claude/` content. The
  post-port content should differ **only** by the sed-applied path
  rewires; everything else byte-identical. Captures any accidental
  drift the cp -r + sed pipeline introduced.
- **G20. Auto-discovery sanity** (P3-T1 §Deferred R3). The 19
  non-`SKILL.md` files at `platforms/claude-code-plugin/skills/`
  root sit alongside the 142 skill directories. Claude Code's
  auto-discovery looks for `skills/<name>/SKILL.md`. Verify that
  the 19 root files don't accidentally match the SKILL.md
  convention — they shouldn't (none are named `SKILL.md`). Check:
  `ls platforms/claude-code-plugin/skills/*.md 2>/dev/null | grep -v SKILL` — should match the 19 root files and **not** any
  `SKILL.md`.
- **G21. `.claude/` source unchanged.** Re-grep `\bai_dev_flow\b`
  in `.claude/`; count must match the P3-T2 pre-port snapshot
  (211 lines). Guards against accidental edits to the source
  during P3-T3 or T4.
- **G22. Hermes platform unaffected.** `git diff --stat HEAD~6
  HEAD -- platforms/hermes/ framework/` (since P3-T0): empty.
  Plus conformance 25/25 (already G1).

### Group 5 — Record

- **G23.** Write `plans/P3-T4-VERIFY.md` with per-gate output
  excerpts. One section per gate group. Auditable record of this
  run.

## Step sequence

1. Run G1–G22 in order; record pass/fail per gate.
2. If any FAIL: halt, post the failure, re-open the responsible
   sub-task. Do **not** commit P3-T4.
3. If all PASS: write `plans/P3-T4-VERIFY.md` (G23).
4. **Land** — single commit
   `chore: P3-T4 phase-3 verify record (all gates green)`; update
   `plans/HANDOFF.md`; tick P3-T4 in `plans/MIGRATION_TODO.md`. Push.

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | A gate that was green at task-time has regressed (cross-task interaction). | The whole point of the consolidated re-run — catch any cross-task interaction. The G6/G7/G10 sweeps + G18 inventory delta would flag a regression. |
| R2 | G19 content-equivalence diff misclassifies the sed-applied rewires as drift. | The diff is expected to be **non-empty** for the 30 rewired files; the equivalence claim is that *only* sed-rewired lines differ. Spot-check is a manual judgment, not an automated assertion. |
| R3 | G18 file-inventory math is off by `.gitkeep` / hidden files / nested skill content. | Math is recorded but not gated — record actual count, explain any delta. Mirrors P2-T5 G14's treatment. |
| R4 | The Hermes venv at `/tmp/hermes-venv` doesn't apply to this verify (plugin has no Python). | P3 plugin needs no venv; only conformance suite needs Python. The system Python with pytest installed satisfies G1. |
| R5 | Auto-discovery sanity (G20) is theoretical — we can't actually invoke Claude Code's discovery from inside the session. | Test what we can: confirm no file named `SKILL.md` sits at `skills/` root (only inside skill dirs). True end-to-end "user installs plugin and skills load" is post-Phase-3 user acceptance. |

## Review log

### Pass 1 — 2026-05-20T21:35:00Z

- **G-a.** Mirrors P2-T5 shape: 4 gate groups + record. Per-gate
  PASS/FAIL recorded.
- **G-b.** P2-T7 G13 lesson — set-membership for the G11
  illustration-paths check (2 specific files at specific line
  numbers). Stronger than "count == 2".
- **G-c.** G18 file-inventory math is recorded but not gated.
  P2-T5 G14 set the precedent (440 = 439 + 1 P0-scaffolded README).
  Same posture here: math reconciliation is for the audit trail,
  not a strict gate.
- **G-d.** Halt-on-failure clause in Step 2 is explicit. P3-T4
  doesn't fix anything; if a gate breaks, the responsible task
  re-opens.
- **G-e.** Verify record file (G23) is the artifact for Phase 3's
  audit trail; without it, the gate result lives only in the
  commit message and shell history. Worth the extra cost — same
  reasoning as P2-T5 G15.
- **G-f.** G19 content-equivalence is a sampling check, not
  exhaustive. The cp -r + sed pipeline is deterministic; spot-
  checking 3 skills covers the categories (a doc-* core skill, the
  orchestrator, a non-doc skill).
- **G-g.** G21 source-unchanged check — catches the failure mode
  "edits leaked back to `.claude/`". P3-T2 included this as V11;
  P3-T4 reaffirms across the four tasks.

### Pass 2 — 2026-05-20T21:45:00Z

- **G-h.** G20 limitation acknowledged in R5 — we can't fully
  exercise auto-discovery without actually installing the plugin in
  a Claude Code instance. Best we can do in-container: confirm the
  naming convention is respected.
- **G-i.** G22 (Hermes unaffected) uses `git diff` over commits, not
  just current working tree, to catch any inadvertent edits across
  the P3 commit series. Specifically `HEAD~6..HEAD` covers P3-T0,
  T1, T2, T3 commits (plus the HANDOFF fixup) — none should have
  touched Hermes or framework. (Note: actual commit count between
  Phase 2 close `bf2e037` and current HEAD may differ; use
  `git diff bf2e037..HEAD` for the canonical range.)
- **G-j.** Verify record structure (G23): one section per gate
  group, command + output excerpt per gate, headline numbers in a
  table at the top. Mirrors `plans/P2-T5-VERIFY.md`.
- **G-k.** No new findings. Plan is internally consistent and
  observable. Ready to present on approval.

## Implementation note (2026-05-20T21:55:00Z)

Executed. All 22 gates green. One mid-flight finding extended scope:

### G18 finding — 47 broken symlinks removed

Initial G18 reconciliation surfaced a 47-file delta between
`git ls-files platforms/claude-code-plugin/` (218) and `find -type f`
(171). Investigation showed the source `.claude/skills/` carries 47
self-referencing symlinks pointing at
`/opt/data/docs_flow_framework/.claude/skills/<name>` — leftovers
from the old multi-project symlink consumption pattern (the dropped
`.claude/skills/README.md` documented this pattern). `cp -r`
preserved them as broken symlinks (mode 120000) in the plugin.

User decision (AskUserQuestion): **Remove now in P3-T4** — small,
well-scoped cleanup discovered by the verify pass; symmetrical with
prior in-flight corrections (P2-T9 G17, P3-T2 G17).

Resolution: `xargs git rm` over the 47 symlink paths (derived via
`comm -23 git-sorted find-sorted`). Post-cleanup file count is **171
= git = disk**.

The cleanup is recorded in `plans/P3-T4-VERIFY.md`'s "Mid-flight
cleanup" section. P3-T2's audit math now reconciles:
236 source files - 16 (OUT skill dirs' files) - 3 (OUT root files) -
**47 (broken symlinks)** + 3 (P3-T3 adds) = **171 final**.

### Lesson for future port tasks

When `cp -r` from a source tree that may contain symlinks (especially
ones referencing absolute paths outside the repo), either:
- Use `cp -rL` to dereference (substantive content gets copied; bad
  if the symlinks are self-referencing as here).
- Use `find ... -not -type l` to filter symlinks out upfront.
- Run a `find -type l` recon during planning to surface them.

P3-T0 audit (and P2-T0/P2-T2 for that matter) didn't surface symlink
content in `.claude/`; future audit plans should add a symlink check
to the recon phase.

### Verify gate results

All 22 gates passed:

| Gate | Result | Key number |
|---|---|---|
| G1 conformance | PASS | 25 / 25 |
| G2 top-level structure | PASS | 7 entries |
| G3 skill dirs | PASS | 142 |
| G4 skill root files | PASS | 19 |
| G5 agents + commands | PASS | 1 + 1 |
| G6 Hermes coupling | PASS | 0 |
| G7 `ai_dev_flow` | PASS | 0 (was 211) |
| G8 bare-layer-dir refs | PASS | 0 |
| G9 bare governance file | PASS | 0 |
| G10 `/opt/data/ucx_framework` | PASS | 0 |
| G11 G13 illustration paths | PASS | 2 (set membership) |
| G12 manifest valid JSON | PASS | — |
| G13 manifest field set | PASS | 7 keys |
| G14 manifest name | PASS | `aidoc-flow` |
| G15 manifest version | PASS | `0.1.0` |
| G16 VERSION file | PASS | 6 bytes |
| G17 FRAMEWORK_SPEC_VERSION matches | PASS | identical to `framework/VERSION` |
| G18 file inventory | PASS (post-cleanup) | 171 = 171 |
| G19 content equivalence (spot-check) | PASS | 3 skills sampled |
| G20 auto-discovery sanity | PASS | 0 stray `SKILL.md` at `skills/` root |
| G21 `.claude/` unchanged | PASS | 211 line hits unchanged |
| G22 Hermes unaffected | PASS | empty diff over Phase 3 commits |

Verify record landed at `plans/P3-T4-VERIFY.md`. Phase 3 is
structurally complete; P3-T5 may proceed.
