# Acceptance suite — project history

Historical record of how the acceptance test suite
(`tests/scripts/test-acceptance.sh` and supporting infrastructure)
was designed and built across 2026-05 / 2026-06. For the current
methodology, see
[`tests/ACCEPTANCE.md`](../tests/ACCEPTANCE.md).
For the original design plan, see
[`ACCEPTANCE-SUITE-FIXES-PLAN.md`](ACCEPTANCE-SUITE-FIXES-PLAN.md).

This file exists to preserve **why decisions evolved**, not to teach
the current state. Treat it as a changelog with rationale.

## Implementation timeline

All implementation work landed across these PRs:

| # | PR | Item | Date |
|---:|:---:|---|---|
| 1 | #53 | Impl-1 — Driver skeleton + Phase 0 + Phase 1.1 + schemas + `--mock` | 2026-05-29 |
| 2 | #54 | Impl-2 — Phase 1.2 negative validation + shared fixtures + `chg/test-change.md` + Phase 2 CHG | 2026-05-29 |
| 3 | #55 | Impl-3 — Phase 3 — 14 utility probes | 2026-05-30 |
| 4 | #56 | Impl-4 — Phase 4 — 11 agents + command + hook | 2026-05-30 |
| 5 | #57 | Impl-5 — `--promote` + README + CHANGELOG | 2026-05-31 |
| 6 | #59 | Restructure plan v3 | 2026-06-01 |
| 7 | #60 | PR A — Three-tier output separation (`docs/` + `.aidoc/` + flat logs); cascade writes to `docs/` directly; `--promote` redesigned; B1/B2/B3 bug fixes; Phase 0 enhancements (A11 profile bootstrap, A12 `--force`); auth-probe fix carried | 2026-06-02 |
| 8 | #61 | PR B — Script tightening (B4-B6 timeouts/cleanup/tokens; A6-A9 iteration modes/cost cap/retries); C2/C3 calibrations; framework-wide doc pass; `framework/docs/AIDOC.md` introduced; spec bump 0.11.0 → 0.11.1 | 2026-06-02 |
| 9 | #62 | Plan v4 — post-implementation reconciliation; Phase-C resume + partial-execution spec | 2026-06-02 |
| 10 | #63 | PR C — Resume / state recovery (R1-R6) + partial execution (P1-P5); schema v1.1 → v1.2 with RUNNING/INTERRUPTED outcomes | 2026-06-02 |
| 11 | (parent #7) | `release.yml` acceptance wiring | 2026-06-01 |

## Plan evolution (v1 → v4)

The plan was iterated four times before all implementation was merged.
Each revision is documented below; the gap-resolution log under each
records what was missing in the prior revision and how the next one
addressed it.

### v1 — initial plan

Initial scope: 50 skills only, happy-path cascade. Missing:
agents/command/hook coverage; negative-fixture validation; schema
definitions; `--promote` algorithm; bootstrap path; API-layer retry
policy; run-duration cap; CI artifact upload.

### v2 — gap-closure pass

Added what v1 missed.

| Gap | What was added |
|---|---|
| G1 — Agents/command/hook | New Phase 4 (§8); scope expanded to 63 elements |
| G2 — Negative fixtures | New §5.2 with 6-fixture coverage table |
| G3 — Schemas | New §3.1 with `summary.json` + `.meta.json` v1.0 schemas |
| G4 — Promote semantics | New §3.2 with the 7-step algorithm |
| G5 — Advisory thresholds | Minimum-coverage column added to §7 + §8 probes |
| G6 — API retry policy | Layered retry: 3× backoff on network/HTTP; no retry on skill instability |
| G7 — CI artifact upload | `upload-artifact@v4` step |
| G8 — Run duration cap | Max 45m wall-clock; GHA `timeout-minutes: 60` |
| G9 — Bootstrap behavior | New Phase 0 (§4) with `bootstrap_mode` detection; Phases 2 + 3 gating |
| G10–G15 | Logged as Phase B deferred work |

### v3 — open question closure

| Question | Decision |
|---|---|
| `docs/` policy each release | **Archive-first** with retention rule. Pre-1.0 keep all uncompressed; post-1.0 compress beyond 5 most recent if `docs-archive/` > 5 MB |
| Multi-example arg pattern | **First positional arg = `<example-name>`**, one example per invocation. `--all` deferred to Phase B |
| `T4L` token budget | **Raise 500K → 1M** in `release.yml` token ledger. Per-phase split deferred |
| CHG change-set source | **Hand-curated per example** at `examples/<NAME>/chg/test-change.md` with documented format |
| Negative-fixtures location | **Shared base set** at `tests/acceptance/fixtures/negative/`; per-example additions optional |

### v4 — post-implementation reconciliation

After the first partial live run (cancelled at ~110 min, 5/8 layers
done) surfaced concrete design issues, the restructure plan landed in
two PRs.

| Change | Where addressed |
|---|---|
| Cascade output ended up in `logs/` instead of `docs/` (the two-stage promote design conflated working state with canonical state) | A1 — cascade writes to `docs/` directly. `--promote` becomes `git commit`. PR #60 |
| Audit/fix/review reports polluted cascade dirs | A2 — routed to `.aidoc/<category>/`. PR #60 |
| Log layout was phase-subdir + separate `.meta.json` per element | A3 + A4 — flat `logs/<TS>/elements/`; YAML front-matter combined with raw stdout. PR #60 |
| `.aidoc/` was treated as gitignored "blackboard"; should be the third committed tier | Three-tier separation; `.gitignore` split. New `framework/docs/AIDOC.md`. PR #60 + #61 |
| Project profile not honoured by the suite | A11 — Phase 0 bootstraps `.aidoc/profile.yaml` from `framework/governance/REVIEW_CREWS.yaml`. PR #60 |
| Cascade silently overwrote `docs/` even with uncommitted edits | A12 — `--force` safety belt. PR #60 |
| Lint ran against whole layer dir (audit reports + tmp/backup polluted output) | B1 — lint targets `$artifact` only. PR #60 |
| Global 45-min runtime cap aborted healthy long cascades | B2 — per-layer 15-min cap. PR #60 |
| review-team persona-extraction grep picked up `weight:` lines | B3 — Python YAML parse of `profile.yaml`. PR #60 |
| No per-skill timeout — review-team ran 32 min unbounded | B4 — `timeout` wrapper. PR #61 |
| Fixer left `tmp/backup/` dirs tripping HASH01 lint check | B5 — `rm -rf $layer_dir/tmp` post-fixer. PR #61 |
| `tokens_in`/`tokens_out` always null | B6 — bytes ÷ 4 estimation (exact via JSON deferred). PR #61 |
| No iteration mode after partial run | A6 `--skip-completed` + A7 `--from-layer=<name>` resume. PR #61 |
| No cost cap | A8 `MAX_TOTAL_OUTPUT_TOKENS`. PR #61 |
| No retry on transient HTTP errors | A9 — 3× exponential backoff. PR #61 |
| `doc-validator` threshold ≥50 sized for 8-layer chain | C1 — `n_layers × 4` scale. PR #60 |
| `quality-advisor` regex too narrow | C2 — broader regex matching `### Layer N` + arrows + numbered/bullets. PR #61 |
| `knowledge-extractor` asked for clarification instead of producing graph | C3 — directive prompt; regex matches Mermaid syntax. PR #61 |
| Framework spec needed bump for `framework/docs/AIDOC.md` addition | Spec **0.11.0 → 0.11.1** (patch); 52 plugin skills' `framework_spec_version` resynced. PR #61 |
| Schema bumped to reflect new combined log layout | `tests/scripts/test-acceptance.schema.json` v1.0 → v1.1. PR #60 |

### Phase-C — resume + partial execution (Plan-C, PR #63)

Surfaced by user feedback ahead of the first live run: a multi-hour
operation must survive interruption, and single-document generation
should be possible without running the full cascade.

| ID | Issue | Resolution |
|---|---|---|
| **R1** | `summary.json` only written at end of run | Incremental rewrite after each element; uses `_rebuild_summary_json()` helper |
| **R2** | `Ctrl-C` / SIGTERM kills the script with no cleanup | `trap _on_exit EXIT` + `trap _on_interrupt INT TERM`. Trap rewrites RUNNING → INTERRUPTED, flushes summary |
| **R3** | Killed-mid-skill element has no `.log` file → appears as never attempted on resume | Pre-invoke RUNNING stub written; overwritten with PASS/FAIL on completion |
| **R4** | Cost cap marked one element FAIL but loop continued | `COST_CAP_EXCEEDED=1` flag halts dispatch loop |
| **R5** | `--skip-completed` only reads most-recent prior run | `--skip-completed=<run-dir>` accepts explicit path |
| **R6** | No way to know WHICH skill was interrupted | Resumed run logs INTERRUPTED elements from prior summary |
| **P1** | `--element=<name>` was parsed but never filtered execution | Wired: `_element_phase()` + `_should_invoke()` |
| **P2** | No `--to-layer` counterpart to `--from-layer` | Added; with `--from-layer` gives single-layer-only |
| **P3** | Cascade could run with missing upstream | Phase 0 step 0.8 — upstream presence check |
| **P4** | Lint smoke ran over whole tree even for partial runs | Already targets `$artifact` (B1); no change needed |
| **P5** | No preview before spending tokens | `--dry-run` prints planned execution and exits 0 |
| Schema | RUNNING/INTERRUPTED states added | v1.1 → v1.2 |

### P6 — framework-side audit (deferred, post-first-live-run)

The Plan-C plan acknowledged that partial-mode execution might surface
framework-side gaps (skill prompts assuming full cascade context).
Plan: exercise `--element=doc-prd-autopilot` against the existing
partial cascade in `--mock` mode; observe whether skills handle
single-element invocation; fix any skill prompts that surface
problems. Estimated 0-2 hours of skill prompt adjustments if any.

## Lessons learned

A handful of patterns that ended up being load-bearing across the
series:

1. **Plan before implementing, then re-plan after the first attempt.**
   The first live run (cancelled at minute 110) surfaced ~12
   design issues the plan hadn't predicted — output routing, log
   layout, runtime caps, threshold calibrations. The "Plan-A then
   Plan-B" approach (PR #60 + #61) addressed them in coordinated
   PRs rather than dribbling fixes.

2. **Don't conflate working state with canonical state.** The
   original `logs/<TS>/cascade/` intermediate looked clean but
   meant cascade output had to be promoted (copied) to its real
   home. Writing directly to `docs/` eliminated a whole class of
   "where did the artifact go?" confusion.

3. **`.aidoc/` formalization unblocked clarity.** Once "AI working
   notes" had a named home (committed alongside `docs/`), audit
   reports stopped polluting cascade dirs and provenance became
   reviewable in git rather than ephemeral in logs.

4. **Resume capability is a force multiplier for long runs.** A
   60-120 minute live cascade without resume support is brittle.
   Once `Ctrl-C` became safe (PR #63's R1-R6), iteration cost
   dropped substantially — the operator can kill at any moment and
   pick up where they stopped.

5. **Partial execution is more valuable than "just for tests".**
   `--element=<name>` started as an iteration helper but is also
   the right interface for "regenerate one document after the
   upstream changed." Worth wiring even though the original
   acceptance use case never needed it.

## What this history isn't

This document records the project-level evolution. It is **not**:

- The current methodology — that lives in
  [`tests/ACCEPTANCE.md`](../tests/ACCEPTANCE.md).
- Per-example specifics — those live under
  `examples/<NAME>/README.md`.
- The design plan — that's
  [`ACCEPTANCE-SUITE-FIXES-PLAN.md`](ACCEPTANCE-SUITE-FIXES-PLAN.md).
- A changelog — see
  [`../CHANGELOG.md`](../CHANGELOG.md) `[Unreleased] → Added` entry for
  the user-facing summary.
