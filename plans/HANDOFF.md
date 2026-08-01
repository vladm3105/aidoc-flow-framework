# Session Handoff

**Purpose:** everything a *fresh* session needs to start work here with zero prior
context — current state, and what to do next. Nothing else.

**This file is regenerated, not appended.** Status that is appended rots, and a wrong
cause left standing gets re-read as fact by every later session. **Git is the archive** —
prior states live in `git log -- plans/HANDOFF.md`. Do not restore them here.

## What lives where — do not duplicate across these

| Surface | Holds | Lifespan |
|---|---|---|
| `CHANGELOG.md` | what shipped | permanent, append |
| `plans/DECISIONS.md` | why a non-obvious choice was made (`D-NNNN`) | permanent, append |
| `framework/governance/DECISIONS.md` | spec-tier decisions (`GD-NN`) | permanent, append |
| `plans/FRAMEWORK-TODO.md` | **the** open-task queue | until closed |
| `plans/HERMES-BACKLOG.md` | Hermes-parity queue | until closed |
| `CLAUDE.md` | the durable working agreement **and every settled trap**, auto-loaded every session | permanent |
| **this file** | current state + next tasks + traps too fresh to have settled | **rewritten each merge** |

**Traps live in `CLAUDE.md` § "Durable traps — do not re-derive these", not here** —
merging/CI mechanics, reading CI output, local hooks and tooling, the acceptance harness,
writing to GitHub from a script, the process lessons, and (in § "Unified CI") the
`--repin` vs `--update` distinction and the `#329` allowlist by *shape*. A trap recorded
there is **never** repeated here; this file carries only what has not settled yet.

## Where we are — 2026-08-01

Framework spec `0.40.0`, plugin `0.24.0`, Hermes `0.12.1`.
**Open PRs: 0. Open issues: 3** —
[#386](https://github.com/vladm3105/aidoc-flow-framework/issues/386),
[#405](https://github.com/vladm3105/aidoc-flow-framework/issues/405) and
[#412](https://github.com/vladm3105/aidoc-flow-framework/issues/412).

**Last merge: [#415](https://github.com/vladm3105/aidoc-flow-framework/pull/415), squash
`889d85c5` — PLUGIN-PREPROD-001 **PR 3 of 5**, saga driver correctness and disclosure.**

**The founder intends to deploy the plugin.** `plans/PLUGIN-PREPROD-001-PLAN.md` clears
the BLOCKER verdict in five staged PRs. **PRs 1, 2 and 3 have shipped**; PR 3 was the only
stage needing real design work. Conformance is now **357** tests (was 299).
The `PREPROD-*` entries stay under `FRAMEWORK-TODO.md` `## Open` until **PR 5** closes them
— that batching is the plan's design, so *the entries do not tell you what has shipped;
this file does.*

**What PR 3 settled.** `tools/saga_driver.py` no longer wedges, no longer clobbers its
subprocess's journal, and no longer exits 0 on a run that never converged (**4**
`PARTIAL_TIMEOUT`, **5** `ESCALATED`, **127** unspawnable, 0 only for `CLOSED`). The
permission bypass is opt-in behind `--allow-skip-permissions`, passed by the 9 autopilot
skills and the acceptance harness. Three invariants a later session would otherwise
re-litigate — **a forced transition may only ever target `PARTIAL_TIMEOUT`** (forcing
toward `CLOSED` reports a pass the transition table says was unreachable); **`--threshold`
keeps three outcomes distinct** (a number is gated, *no* `content_score` is ungated because
CHG has none by design, *unreadable* fails closed); and **`verdict.json` is rotated, not
deleted**. Rationale is in `CHANGELOG.md`; PR 5 records the formal `D-00NN`.

**⚠️ The `ai-review` gate WILL request changes on a code or CI PR with no root
`CHANGELOG.md` entry.** It did on #413, and it was right: the plan's deferral of "the
changelogs" to PR 5 covers the *release narrative*, not the per-PR doc-currency rule.
**Budget 2 real doc surfaces + `CHANGELOG.md` on every remaining stage.** #415 followed
that and passed. Read the verdict before assuming infrastructure — the failing job
**uploads a verdict artifact** (`gh run download <id> -n ai-review-verdict`) naming the
finding. A run that fails *after* producing that artifact is a verdict, not an outage.

**⚠️ `Hermes pytest` is RED on `main`; it is not this repo's regression and does not block
merges.** An unpinned `mcp[cli]>=1.0.0` floor resolves to whatever the SDK last published.
**Not a required context** — #413 merged at `mergeStateStatus=UNSTABLE` with it red and all
six required contexts green. Locally it passes (570). `HERMES-MCP-FLOATING-DEP` has the
detail; do not re-diagnose it.

**⚠️ Two tiers are RED on `main` for pre-existing reasons, neither CI-gated:**
`tests/release/test_changelog_entry.py` (its `TBD` check scans the whole of `CHANGELOG.md`
and matches a **quoted historical commit message**, so it can never pass —
`RELEASE-GATE-TBD-FALSE-POSITIVE`; **PR 5 is the first stage that hits it**), and Phase 0
`lint-smoke` in `tests/scripts/test-acceptance.sh` (example-corpus debt deferred to the
wholesale regen — use `--skip-lint-smoke` to reach later phases).

**V15 (schedule→`workflow_run` chain) is still unconfirmed** — never a gate; V14 proved
the chain off a *dispatched* upstream only. `standards-drift` runs Mondays 09:00 UTC,
first observable **2026-08-03**. **On or past that date**, check that a
`pin-currency-reader` run followed the latest `standards-drift` with `event=workflow_run`,
then delete this paragraph. A failure there is a new bug, not a reopened plan.

## Next tasks — prioritized

The full queue is `plans/FRAMEWORK-TODO.md` (`## Open`) and `plans/HERMES-BACKLOG.md`.
This is only the ordering a fresh session should use.

1. **PLUGIN-PREPROD-001 — implement PR 4 (agent and manifest hygiene).** Read
   `plans/PLUGIN-PREPROD-001-PLAN.md` § "PR 4". Small, independent, no design work:
   `M2` (`agents/requirements-analyst.md` is the only one of 11 declaring neither
   `tools:` nor `model:`, so it inherits `Write`/`Edit`/`Bash`), `L1` (no `LICENSE` in
   the plugin dir), `L6` (personal email in `marketplace.json` — founder's call), `L7`
   (`agents/code-reviewer.md` may collide with a consumer's own agent), plus a new
   conformance test asserting every agent declares `tools:` and `model:`.
   **Model that test on `tests/conformance/platforms/test_tools_vendoring.py`** (new in
   #415) rather than inventing a shape.
2. **Then PR 5 — docs, version bump, tag, Release. FOUNDER-GATED.** The tag cut and the
   public Release are outward-facing and wait on explicit founder approval; the PR itself
   merges normally. Four things a fresh session must know before starting it:
   - **`tests/release/test_changelog_entry.py` is RED on `main` and PR 5 is the first
     stage that hits it** — `RELEASE-GATE-TBD-FALSE-POSITIVE`. Fix or scope the gate
     before the release narrative, not during it.
   - **The plan's PR 5 section still says "add the README prerequisites section."** That
     shipped in PR 1. PR 5 must not re-add it.
   - **The plan's `--threshold` bullet says `CHANGELOG.md` already claims the flag was
     removed from the driver, and that the claim is false.** It is now false in a second
     way: PR 3 made the flag *live*. PR 5's entry must say that, not restate either.
   - **[#405](https://github.com/vladm3105/aidoc-flow-framework/issues/405) fires here** —
     the version fanout rewrites historical "shipped in vX" claims. Hand-verify every
     surface rather than trusting `sync-version-refs.sh`.
3. **`SDD-CORPUS-UNVERIFIED` — the sdd-orchestrator corpus ships runnable Python that
   nothing parses, executes, or checks. START WITH THE FOUNDER DECISION; it gates the
   plan.** Census and fix options are in the `FRAMEWORK-TODO.md` entry. Two rules that are
   *not* there: **build the gate before touching content** (it enumerates the work
   mechanically instead of a human guessing at its bounds), and this is non-trivial, so it
   needs a `plans/` plan with the two-cycle gap review.

4. **[#412](https://github.com/vladm3105/aidoc-flow-framework/issues/412) — linting a
   single file reports every cross-document trace tag as a `TRACE-RES-001` ERROR.** The
   review hook lints exactly one file, so `verbose` mode spends its whole budget on false
   errors. Fix shape is the single-file gate `_check_forward_coverage` already carries
   (`tools/sdd_doc_lint/__init__.py:1961-1963`).

5. **Watch [aidoc-flow-ci#351](https://github.com/vladm3105/aidoc-flow-ci/issues/351) —
   when canon ships its own reader, DELETE ours.** `.github/workflows/pin-currency-reader.yml`
   plus `scripts/read-pin-currency-log.sh` and `scripts/reconcile-pin-currency-issue.sh`
   are an override, not a permanent local surface (plan R9). Nothing else says so.
6. **[#405](https://github.com/vladm3105/aidoc-flow-framework/issues/405) —
   `sync-version-refs.sh` rewrites historical "shipped in vX" claims.** Corrupted
   `docs/PARITY.md:65` on three consecutive bumps. **Fires next at PR 5**, whose
   mitigation is to hand-verify every surface rather than trust the script.

7. **[#386](https://github.com/vladm3105/aidoc-flow-framework/issues/386) — the
   framework-spec token gates five files on `CLAUDE.md`'s own state.** Mechanism and
   hazard: `CLAUDE.md` § "Durable traps → Local hooks and tooling". Outstanding is only
   the **fix shape** — #389's approach cannot be reused unchanged because this `prev` is
   load-bearing elsewhere; derive it from a fanout target nobody hand-edits
   (`docs/PARITY.md`).

8. **`doc-maintainer` — nothing to do; it is PAUSED** (`kill_switch: true`, #397) and CI
   is green. **Resume requires `aidoc-flow-ci` #352 AND #353** — #353 alone is 15 of the
   23 failures, so flipping on #352 alone returns a majority-red pilot. Census in D-0072.
   ⚠️ **Do not re-file the `high_risk_paths` / `allowed_paths` mismatch as a defect** — it
   is deliberate and documented in the config; #396 recorded it as a bug and was wrong.
9. **Hermes parity — the residual arc.** `plans/HERMES-BACKLOG.md`: remaining
   plugin-vs-Hermes deltas plus quality-loop Phase 2 (cross-invocation resume / G-R1,
   the parallel-review global lock).
10. **Everything else** is in `FRAMEWORK-TODO.md` by tag. An entry under `## Open` with no
   `⏳ OPEN ON RESIDUAL` marker is genuinely open work (#403). Nothing there is blocking.

## Traps too fresh to have settled — not yet in `CLAUDE.md`

- **A killed mutation run is a code-modifying event, not a no-op.** One PR 3 mutant left
  the driver's `main` loop non-terminating, so the harness hung; killing it skipped the
  `finally` that restores the source, and a mutant sat in the working tree looking like
  authored code. Caught only by scanning for mutant fingerprints against a list of markers
  that must be present. **Restore from a saved copy on every iteration, never in a
  `finally`, and bound each run with a timeout** — a hang is a detection, not a harness
  failure. The hardened harness is `scratchpad/mutate2.py` in this session's transcript;
  the shape is worth rebuilding, not the file.
- **Your own test can enshrine the defect you just introduced.** PR 3's first draft forced
  the saga toward `CLOSED` on an inconsistent journal *and* shipped
  `test_pass_from_unreachable_state_reaches_closed` asserting exactly that. The suite was
  green, mutation-clean at 24/24, and wrong — the test made the correct fix look like a
  regression. Mutation testing cannot catch this: the mutant and the test agree. **Only an
  independent reader with the spec in hand does**, which is what the pre-push review
  agents are for. When a fix has a *direction* (fail-open vs fail-closed), state the
  direction as an invariant in code — `append_transition` now refuses any forced edge that
  does not target `PARTIAL_TIMEOUT` — rather than trusting each call site to get it right.
- **A surviving mutant usually indicts the test, not the fix.** Both survivors in PR 3's
  second round were weak assertions: `content_score: true` compares as `1` and so fails a
  threshold of 90 *for the wrong reason*, and a resolved-vs-unresolved return path is
  indistinguishable until a symlink makes the two differ. **Assert the classification, not
  the downstream outcome**, whenever the outcome has more than one possible cause.
- **A fix can silently disarm an existing regression test, and the suite stays green.**
  PR 2's exit-3 guard turned a PR 1 crash test into three assertions that passed because
  nothing was produced. **When a change alters an exit code, a return value or an error
  type, grep the suite for tests that provoke the OLD behaviour** — they now assert
  against a path that no longer runs. Nothing in CI can detect this; only mutation
  testing found it (weakening the thing the test was supposed to guard, and watching the
  suite stay green).
- **Anything that mutates source in place — a background agent, your own mutation
  harness — can leave the tree dirty in a way that reads as authored code.** Verify the
  working tree matches the index (`git diff --quiet <path>`) before any run you intend to
  trust, and re-verify after agents report. Both failure modes have now bitten: a
  test-quality agent building mutants while the parent staged a commit (PR 2), and a
  killed mutation harness (PR 3, above).
- **`check_plan.py` false-greens on a not-ready plan.** Its zero-findings check is a
  phrase match, and it accepted a Review log whose final pass said *"**Result:** NOT
  READY"* — because the surrounding prose contained "all folded". Canonical script is
  `~/.claude/skills/verified-planning/check_plan.py`; no repo-local copy. **Not filed.**
- **markdownlint silently corrupts claim-ledger citations.** Its autofix rewrites
  `__init__.py` → `**init**.py` in an unbackticked table cell, which broke **ten**
  citations at once and made the gate fail with the misleading `path '.py' does not
  exist`. Workaround in #408: `<!-- markdownlint-disable MD050 -->` scoped around the
  ledger. It also normalizes `_x_` → `*x*` across a **whole** changelog file you touch,
  so a one-entry changelog commit can carry rewrites of historical entries. **Not filed.**

**Standing:** the example corpus is regenerated wholesale after framework changes, so
corpus-remediation findings are deferred to that regen rather than fixed in place.
IPLAN ↔ iplanic integration is deferred (`plans/IPLAN-IPLANIC-DEFERRED.md`).

## Stale advice — a fresh session will find these referenced, and they are FIXED

Older plans, TODO entries and commit messages still describe these as live. They are
not. Every row below still has at least one live source in the repo; rows whose only
remaining source was this file have been deleted rather than carried forward.

| Stale claim | Reality |
|---|---|
| "no authoring surface computes SHA-256 in-prompt any more" (`ROADMAP.md:113`, `platforms/hermes/CHANGELOG.md` `[0.12.0]` heading, `plans/IDGEN-NO-GENERATOR-PLAN.md`) | **Still false, in a narrower way.** #406 closed the plugin-SKILL and Hermes-reference halves; `agent-skills/**/SKILL.md` is reached by no root and `sdd-orchestrator/SKILL.md:667` still hashes. `ROADMAP.md` also dates the claim to Hermes `0.12.0`, which was never true |
| "`--admin` is required on every PR" (the `ai-review` self-cancel, `aidoc-flow-ci#322`) | **Fixed at `ci/v2.16.0`.** #378, #380, #392, #394, #406, #410 and #413 all reached mergeable with no `--admin` |
| "Branch protection requires the phantom `Lint / format / security hooks`, so every PR is BLOCKED" | **Fixed.** The six required contexts, re-read from the API on 2026-07-31, are `call / Lint / format / security hooks`, `call / composition`, `call / ai-review`, `call / verify`, `Framework + platform conformance`, `Acceptance tier (deterministic)`. `call / trust` and `Hermes pytest` are **not** required |
| `AIDOC-CI-COMPOSITION-CHECK-PRHEAD` — "`call / composition` is structurally unsatisfiable on a PR head" | **Stale.** composition reports success on PR heads. A reviewer once read this entry as proof that required checks gate nothing here, and it nearly killed a correct plan |
| Three pin-currency claims: `NO-PIN-CURRENCY-CHECK` ("this repo runs `check-pin-currency.sh` nowhere"), `PIN-CURRENCY-NO-READER` ("the fix **runs the script**"), and `PIN-CURRENCY-READER-PLAN.md:465`/`:469` ("the `clean` path is verified only by V4's stub") | **All three dead.** The check runs on every weekly `standards-drift` (the first was simply false — lesson in `CLAUDE.md` § "Durable traps → Process"); the reader SHIPPED at #392 and consumes the completed run's **log**; and V14 exercised close-on-clean for real |
| `plans/PLAN-*.md` as the governance-PR plan glob (`CHANGELOG.md`, `CI-CANON-V2.16-MIGRATION-PLAN.md:468`/`:784`) | **Fixed in `CLAUDE.md`** (#387/#390). The glob is a **suffix** — `plans/*-PLAN.md`. Merged plans and the CHANGELOG keep the old string as history; `CLAUDE.md` is the live rule |
