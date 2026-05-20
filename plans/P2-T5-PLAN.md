# P2-T5 Plan — Phase 2 verify

| Field      | Value                                |
|------------|--------------------------------------|
| Task       | P2-T5                                |
| Depends on | P2-T2, P2-T3, P2-T7, P2-T8, P2-T9    |
| Status     | DONE — 2026-05-20T16:20:00Z          |
| Feeds      | P2-T6 (Phase 2 close)                |

## Objective

Run a consolidated, end-to-end re-verification of every gate that
P2-T2 / T3 / T7 / T8 / T9 individually checked, and snapshot the
results as the formal Phase 2 verify record. This task is a **gate**,
not a code change — its purpose is to confirm that the combined state
of the working branch satisfies P2-T0's exit conditions before P2-T6
cuts the changelog and tags. If any gate fails, halt and re-open the
failing task; otherwise commit the snapshot and hand off to P2-T6.

## Scope

**In:**

- Re-run every verify gate from the prior tasks against the **current**
  working-branch state (not against historical task-time snapshots).
- Add three integration-level gates that prior tasks couldn't run alone:
  - Cross-task scope check: `platforms/hermes/` file inventory matches
    the audit's expected post-port total.
  - End-to-end smoke: `scaffold_project_ucx()` against real framework
    defaults installs all 8 layer templates correctly.
  - Tag-namespace check: `VERSION` (`0.1.0`) is consistent with the
    `hermes/v0.1.0` tag that P2-T6 will create.
- Write a one-page verify record (`plans/P2-T5-VERIFY.md`) capturing
  command output excerpts for the audit trail — Phase 2 has no
  CI/CD that produces this artifact, so the record itself is the
  artifact.

**Out:**

- Any code or content edit. If a gate fails, the fix is **not** P2-T5
  — re-open the responsible task (T2 / T3 / T7 / T8 / T9) and let
  P2-T5 re-run after the fix lands.
- Conformance suite extension (still Phase 4).
- `CHANGELOG.md` / `ROADMAP.md` / tag work (still P2-T6).
- Platform B (Claude Code plugin) — that's Phase 3.

## Approach

Run the gates in three groups, recording pass/fail per gate.

### Group 1 — Conformance + Hermes own tests

- **G1.** `pytest tests/conformance/` from repo root: expect `25
  passed`. (P1-T7 baseline, P2-T3 maintained.)
- **G2.** `pytest platforms/hermes/tests/` with `PYTHONPATH=src` and
  the 3.12 venv: expect `447 passed`. (P2-T9 closed.)

### Group 2 — Coupling + structural sweep

- **G3.** `grep -rE 'ucx_flow|UCX_FLOW' platforms/hermes/src
  platforms/hermes/tests platforms/hermes/skills
  platforms/hermes/pyproject.toml platforms/hermes/agent-skills`
  returns **zero**.
- **G4.** `grep -rE 'ucx_flow|UCX_FLOW' platforms/hermes/docs` returns
  hits in **exactly 11 files**: the historical whitelist established
  by P2-T3 §3c. Set-membership equality, not count tolerance.
- **G5.** No `platforms/framework/` wrong-prefix path computations in
  `platforms/hermes/src/`.
- **G6.** `find platforms/hermes/agent-skills -name '*-TEMPLATE.yaml'
  -not -path '*/governance/*'` returns **0**. (P2-T8 D-0013 conformance
  for the skill.)
- **G7.** `find platforms/hermes/templates -type f` returns nothing
  (or directory absent). (D-0013 for the platform's runtime.)
- **G8.** `find platforms/hermes/docs/migration -type f` returns
  nothing. (P2-T3 audit §5 drop.)

### Group 3 — Version + smoke + structure

- **G9.** `diff platforms/hermes/FRAMEWORK_SPEC_VERSION
  framework/VERSION` prints nothing — both `0.1.0`.
- **G10.** `cat platforms/hermes/VERSION` prints `0.1.0`. Matches the
  `hermes/v0.1.0` tag namespace (`docs/TAGGING.md`).
- **G11.** Smoke test: scaffold against real defaults creates ≥ 70
  files, lands `BRD-TEMPLATE.yaml` at the expected
  `UCX/templates/layers/01_BRD/` path.
- **G12.** `pyproject.toml` carries `name = "hermes-server"`,
  `version = "0.1.0"`, and the `hermes-mcp` script entry; zero
  `ucx-hermes-server` / `mcp-ucx` markers.
- **G13.** Top-level `platforms/hermes/` carries the 11 expected
  directories / files (`VERSION`, `FRAMEWORK_SPEC_VERSION`,
  `README.md`, `pyproject.toml`, `agent-skills/`, `docs/`,
  `examples/`, `prompts/`, `skills/`, `src/`, `tests/`).
- **G14.** Inventory total: number of files under `platforms/hermes/`
  is the sum of the 4 ports:
  P2-T2 (verbatim) 64 + P2-T7 (agent-skills) 181 + P2-T3 (with-repoint)
  200 + P2-T9 ∆ 0 (in-place edits, no new files) + P2-T8 ∆ −8 (deletes)
  + 4 root files (`README.md`, `VERSION`, `FRAMEWORK_SPEC_VERSION`,
  `pyproject.toml` already counted in the 200) = approximately
  64 + 181 + 200 − 8 = **437** tracked files (give-or-take any directory
  README counts I may be missing; actual count is what
  `git ls-files platforms/hermes | wc -l` reports — the verify just
  records the number and confirms it equals the four sub-task totals
  net of T8 deletes).

### Group 4 — Record

- **G15.** Write `plans/P2-T5-VERIFY.md` with the per-gate output (PASS
  with key numbers, or FAIL with the gate's stderr). One section per
  gate. The file is the auditable record of this run.

## Step sequence

1. Run G1–G14 in order; record pass/fail per gate.
2. If any FAIL: halt, post the failure, re-open the responsible
   sub-task. Do **not** commit P2-T5.
3. If all PASS: write `plans/P2-T5-VERIFY.md` (G15).
4. **Land** — single commit `chore: P2-T5 phase-2 verify record (all
   gates green)`; update `plans/HANDOFF.md`; tick P2-T5 in
   `plans/MIGRATION_TODO.md`. Push.

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | A gate that was green at task-time has since regressed (e.g. a tracker edit reintroduced a `ucx_flow_v3` token). | This is the whole point of the consolidated re-run — catch any cross-task interaction. The set-membership whitelist check on docs (G4) is symmetric and would catch silent rewrites in either direction. |
| R2 | The Hermes venv at `/tmp/hermes-venv` is missing or stale. | Bash check: `test -x /tmp/hermes-venv/bin/python` before G2; recreate if missing using the documented steps from P2-T3 / P2-T9. |
| R3 | G14 file-count math is approximate; doesn't catch off-by-a-few. | Math is a sanity check, not a gate — the real gate is the per-task file inventories already passed. G14 just records the consolidated number for the verify document. |
| R4 | Tests are run against the committed branch tip, but uncommitted local edits could pollute. | Bash check: `git status` shows a clean working tree at the start of G1 (modulo the P2-T5 plan + verify file we're producing). Any other `M` / `A` / `D` halts the run. |

## Review log

### Pass 1 — 2026-05-20T16:00:00Z

- **G-a.** P2-T7 G13 + P2-T3 §3c lesson — coupling sweep must use the
  historical whitelist as **set membership** (not count tolerance).
  G4 says "exactly 11 files"; that's the right shape.
- **G-b.** P2-T9 G16 + G17 lessons — extending to runtime checks:
  added G5 (no `platforms/framework/` wrong-prefix anywhere in `src/`).
- **G-c.** Smoke test as an end-to-end gate beyond what unit tests
  catch — G11 added.
- **G-d.** Verify record file (G15) is the artifact for Phase 2's
  audit trail; without it, the gate result lives only in the commit
  message and shell history. Worth the small extra cost.
- **G-e.** Halt-on-failure clause in Step 2 is explicit. P2-T5 doesn't
  fix anything; if a gate breaks, the responsible task re-opens.
- **G-f.** Risk R2 (venv hygiene) is a real concern after a session
  restart — checked before G2 runs.

### Pass 2 — 2026-05-20T16:10:00Z

- **G-g.** Clean-tree check (R4) — added an explicit pre-step. Without
  it, the verify could record a green gate state that isn't actually
  on-branch.
- **G-h.** G14 (file inventory math) revisited: kept as a sanity check,
  not a gate. The true verify is the per-task inventories. The number
  is recorded for the audit trail.
- **G-i.** No new findings. Plan is internally consistent and the
  verify gates are observable / reproducible.

## Implementation note (2026-05-20T16:20:00Z)

Executed. All 14 gates ran green. See `plans/P2-T5-VERIFY.md` for the
detailed per-gate record (G15 deliverable).

Headline results:
- Conformance suite: **25 / 25** (unchanged since P1-T7).
- Hermes own test suite: **447 / 447** (trajectory 397→447 across
  P2-T3→P2-T9).
- Coupling sweep: **0** in current-behavior content; whitelist set
  membership **exactly** matches the 11 historical-docs files.
- File inventory: `git ls-files platforms/hermes/` returns **440** =
  439 (sub-task audit math) + 1 (P0-scaffolded `README.md`,
  reconciled).
- VERSION + FRAMEWORK_SPEC_VERSION: both `0.1.0`, identical to
  `framework/VERSION`.
- Smoke test scaffolded 71 files end-to-end against real defaults.
- `pyproject.toml`: `hermes-server` / `0.1.0` / `hermes-mcp`; zero
  legacy markers.

Phase 2 is structurally complete. P2-T6 may proceed.
