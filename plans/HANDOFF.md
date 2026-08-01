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

## Where we are — 2026-07-31

Framework spec `0.40.0`, plugin `0.24.0`, Hermes `0.12.1`.
**Open PRs: 0. Open issues: 3** —
[#386](https://github.com/vladm3105/aidoc-flow-framework/issues/386),
[#405](https://github.com/vladm3105/aidoc-flow-framework/issues/405) and
[#412](https://github.com/vladm3105/aidoc-flow-framework/issues/412) (new this session).

**Last merge: [#413](https://github.com/vladm3105/aidoc-flow-framework/pull/413), squash
`f0dc63f3` — PLUGIN-PREPROD-001 **PR 2 of 5**, linter prerequisite guards.**

**The founder intends to deploy the plugin.** `plans/PLUGIN-PREPROD-001-PLAN.md` clears
the BLOCKER verdict in five staged PRs. **PRs 1 and 2 have shipped.** PR 2 closed `B4`'s
linter half and `L5`: PyYAML and the Python ≥3.11 floor are diagnosed in one line and exit
**3** — distinct from 2 (already *both* "argparse usage error" and "registry unavailable")
and from 1 ("this document has error findings"), which is what made an absent PyYAML
arrive in model context labelled as a lint finding. `--warn-exit` makes warning findings
reachable and the hook passes it. Conformance is now **299** tests.
The `PREPROD-*` entries stay under `FRAMEWORK-TODO.md` `## Open` until **PR 5** closes them
— that batching is the plan's design, so *the entries do not tell you what has shipped;
this file does.*

**Three things PR 2 changed that the plan does not describe.** All three came from the
mandatory pre-push review agents, and each was reproduced before folding:

- **`B1` was NOT fully closed by PR 1, and the record said it was.** The hook *appended*
  the inherited `PYTHONPATH` to the plugin root, so a `yaml/` package on any inherited
  entry was imported by the bundled linter and **executed** — measured during a real hook
  run, with the hook still exiting 0 and writing nothing, so nothing observable said so.
  `.envrc` is repository content and direnv exports it. `PYTHONPATH` is now **replaced**,
  not extended. Consequence to know: a PyYAML supplied *only* via `PYTHONPATH` now gets
  the exit-3 diagnostic instead of being silently used.
- **PR 2's own guard silently disarmed a PR 1 regression test.**
  `test_a_crashing_linter_yields_no_findings_block` provoked a linter crash by shadowing
  PyYAML with an `ImportError` — exactly what the new guard catches — so the linter exits
  3, the hook's `rc == 1` branch is never entered, and its three assertions passed because
  *nothing was produced* rather than because it was filtered. Proof it mattered: a mutant
  weakening the hook's finding-grammar filter passed the whole suite while forwarding a
  traceback into `<untrusted-tool-output>` — the exact `B4` defect PR 1 fixed. Both that
  test and the new exit-3 contract test now run against a **stub `python3` on `PATH`**
  (`HookHarness.stub_python3`); use it rather than inventing a new way to provoke a crash,
  because every real one runs through a path the hardening has closed.
- **`ruff.toml` gained a per-file `E402` ignore** for `**/sdd_doc_lint/__init__.py` — the
  guards run before the imports they protect, so every later import is "not at top of
  file" by construction.

**⚠️ The `ai-review` gate WILL request changes on a code or CI PR with no root
`CHANGELOG.md` entry.** It did on #413, and it was right: the plan's deferral of "the
changelogs" to PR 5 covers the *release narrative*, not the per-PR doc-currency rule.
**Budget 2 real doc surfaces + `CHANGELOG.md` on every remaining stage.** Read the verdict
before assuming infrastructure — the failing job **uploads a verdict artifact**
(`gh run download <id> -n ai-review-verdict`) naming the finding. A run that fails *after*
producing that artifact is a verdict, not an outage.

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

1. **PLUGIN-PREPROD-001 — implement PR 3 (saga driver).** Read
   `plans/PLUGIN-PREPROD-001-PLAN.md` § "PR 3"; it carries a 57-row claim ledger with
   verified `file:line` and five recorded review passes. **The only stage needing real
   design work**, and it depends on nothing — but it must precede PR 5.
   Scope (`B2`, `B3a`–`c`, `M3`–`M5`, `L2`, `L3`) is enumerated there — read it rather
   than this file. What the plan does **not** say:
   - **A release gate forbids the literal `--dangerously-skip-permissions` in any
     `SKILL.md`** (`tests/release/test_marketplace_gate.py:39`). Do not amend that gate;
     the 9 skills must name and **pass** the new `--allow-skip-permissions` instead.
   - **Do not re-derive the plan's rejected alternatives** — three independent passes
     killed several obvious-looking fixes, each written up with its evidence. Several
     fixes span *four* call sites or *both* return sites; a fix applied to some is worse
     than none, because it reads as closed.
   - **The plan's PR 5 section still says "add the README prerequisites section."** That
     shipped in PR 1. PR 5 must not re-add it.
   - PR 4 (agent and manifest hygiene) is small and independent — it can go in parallel.
     PR 5 (docs, version bump, tag, Release) is **founder-gated**.
2. **`SDD-CORPUS-UNVERIFIED` — the sdd-orchestrator corpus ships runnable Python that
   nothing parses, executes, or checks. START WITH THE FOUNDER DECISION; it gates the
   plan.** Census: **45 fenced Python blocks — 3 do not parse, 10 carry unused imports,
   10 call a locally-defined function with too few positional arguments.** `grep -rl
   agent-skills tests/ .github/workflows/ .pre-commit-config.yaml` returns only
   markdown-lint, pre-commit formatting, and a text-regex guard. `SKILL.md:1155` points
   agents at these files for "the complete scripts."
   - **Decision needed first:** make that Python genuinely executable and tested, demote
     it to explicitly-marked non-runnable pseudocode, or extract it to real `.py` files
     under test. The answer changes what the gate asserts.
   - **Then build the gate BEFORE touching content** — it enumerates the work
     mechanically instead of a human guessing at its bounds.
   - Non-trivial → needs a `plans/` plan with the two-cycle gap review.
3. **[#412](https://github.com/vladm3105/aidoc-flow-framework/issues/412) — linting a
   single file reports every cross-document trace tag as a `TRACE-RES-001` ERROR.**
   `SPEC-01.md` alone yields **66**; the whole corpus yields **0**; the cited documents
   exist. The review hook lints exactly one file, so `verbose` mode spends its whole
   budget on false errors. Fix shape is the single-file gate `_check_forward_coverage`
   already carries (`tools/sdd_doc_lint/__init__.py:1961-1963`).
4. **Watch [aidoc-flow-ci#351](https://github.com/vladm3105/aidoc-flow-ci/issues/351) —
   when canon ships its own reader, DELETE ours.** `.github/workflows/pin-currency-reader.yml`
   plus `scripts/read-pin-currency-log.sh` and `scripts/reconcile-pin-currency-issue.sh`
   are an override, not a permanent local surface (plan R9). Nothing else says so.
5. **[#405](https://github.com/vladm3105/aidoc-flow-framework/issues/405) —
   `sync-version-refs.sh` rewrites historical "shipped in vX" claims.** The
   `hermes/v<prev>` / `claude-code-plugin/v<prev>` fanout at `:347-355` is an unanchored
   global sed carrying neither of the two `HAZARD` notes the script already has.
   It corrupted `docs/PARITY.md:65` on **three consecutive bumps**.
   **PR 5 bumps the plugin version, so this fires next at PR 5** — the plan's mitigation
   is to hand-verify every surface rather than trust the script.
6. **[#386](https://github.com/vladm3105/aidoc-flow-framework/issues/386) — the
   framework-spec token gates five files on `CLAUDE.md`'s own state.** Mechanism and
   hazard: `CLAUDE.md` § "Durable traps → Local hooks and tooling". Outstanding is only
   the **fix shape** — #389's approach (detect from `CLAUDE.md`, write only `CLAUDE.md`)
   cannot be reused unchanged because this `prev` is load-bearing elsewhere. Derive the
   gating `prev` from a fanout target nobody hand-edits (`docs/PARITY.md`).
7. **`doc-maintainer` — nothing to do; it is PAUSED** (`kill_switch: true`, #397) and CI
   is green. **Resume requires `aidoc-flow-ci` #352 AND #353** — #353 alone is 15 of the
   23 failures, so flipping on #352 alone returns a majority-red pilot. Census in D-0072.
   ⚠️ **Do not re-file the `high_risk_paths` / `allowed_paths` mismatch as a defect** — it
   is deliberate and documented in the config; #396 recorded it as a bug and was wrong.
8. **Hermes parity — the residual arc.** `plans/HERMES-BACKLOG.md`: remaining
   plugin-vs-Hermes deltas plus quality-loop Phase 2 (cross-invocation resume / G-R1,
   the parallel-review global lock).
9. **Everything else** is in `FRAMEWORK-TODO.md` by tag. An entry under `## Open` with no
   `⏳ OPEN ON RESIDUAL` marker is genuinely open work (#403). Nothing there is blocking.

## Traps too fresh to have settled — not yet in `CLAUDE.md`

- **A fix can silently disarm an existing regression test, and the suite stays green.**
  PR 2's exit-3 guard turned a PR 1 crash test into three assertions that passed because
  nothing was produced. **When a change alters an exit code, a return value or an error
  type, grep the suite for tests that provoke the OLD behaviour** — they now assert
  against a path that no longer runs. Nothing in CI can detect this; only mutation
  testing found it (weakening the thing the test was supposed to guard, and watching the
  suite stay green).
- **Mutation-test the tests you just wrote, not only the code.** Two of PR 2's twelve
  mutants survived a first pass — the hook treating exit 3 like exit 1, and an unbounded
  interpolated exception string — because the *fixtures* were too tame to distinguish
  (short single-line message; no finding-shaped output on the exit-3 path). A guard whose
  fixture cannot express the failure is decoration.
- **A background review agent mutates YOUR working tree.** The test-quality agent built
  mutants in place while the parent was staging a commit; `git status` showed `MM` and one
  full-suite run went red on a mutant, not a regression. Stage early, verify the working
  tree matches the index (`git diff --quiet <path>`) before any run you intend to trust,
  and re-verify after the agents report.
- **A version-boundary env var fails silently, so "I set it" is not "it took effect."**
  `PYTHONSAFEPATH` exists only on Python ≥3.11; below it the interpreter ignores it and
  the CWD is back on `sys.path`. The mitigation that holds everywhere is to run from a
  directory the attacker does not control.
- **`cmd 2>/dev/null` does not suppress a failing `<"$file"` redirection** — the *shell*
  reports that, before `cmd` exists. Redirect the whole group or guard with `[ -f ]`.
- **Do not test a script from a copy when its behavior depends on its own location.**
  `sdd-doc-review.sh` derives its plugin root from `BASH_SOURCE`, so a copy resolves to
  the scratch dir and the linter is never found — every finding assertion then passes for
  the wrong reason. This produced a **false refutation** of a real defect.
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
| "`B1` is closed" (`PLUGIN-PREPROD-001-PLAN.md`, #410's commit body, `FRAMEWORK-TODO.md` `PREPROD-B1`) | **It was half closed until #413.** PR 1 closed the working-directory vector; the inherited-`PYTHONPATH` vector still executed project-supplied code. Both are closed now, and `test_plugin_hook_safety.py` locks each |
| "no authoring surface computes SHA-256 in-prompt any more" (`ROADMAP.md:113`, `platforms/hermes/CHANGELOG.md` `[0.12.0]` heading, `plans/IDGEN-NO-GENERATOR-PLAN.md`) | **Still false, in a narrower way.** #406 closed the plugin-SKILL and Hermes-reference halves; `agent-skills/**/SKILL.md` is reached by no root and `sdd-orchestrator/SKILL.md:667` still hashes. `ROADMAP.md` also dates the claim to Hermes `0.12.0`, which was never true |
| "`--admin` is required on every PR" (the `ai-review` self-cancel, `aidoc-flow-ci#322`) | **Fixed at `ci/v2.16.0`.** #378, #380, #392, #394, #406, #410 and #413 all reached mergeable with no `--admin` |
| "Branch protection requires the phantom `Lint / format / security hooks`, so every PR is BLOCKED" | **Fixed.** The six required contexts, re-read from the API on 2026-07-31, are `call / Lint / format / security hooks`, `call / composition`, `call / ai-review`, `call / verify`, `Framework + platform conformance`, `Acceptance tier (deterministic)`. `call / trust` and `Hermes pytest` are **not** required |
| `AIDOC-CI-COMPOSITION-CHECK-PRHEAD` — "`call / composition` is structurally unsatisfiable on a PR head" | **Stale.** composition reports success on PR heads. A reviewer once read this entry as proof that required checks gate nothing here, and it nearly killed a correct plan |
| "the acceptance deterministic tier has 3 pre-existing failures on `main`" | **Fixed** (#365, #371/#372). 0 failures / 64, and the tier is now a **required** context |
| Three pin-currency claims: `NO-PIN-CURRENCY-CHECK` ("this repo runs `check-pin-currency.sh` nowhere"), `PIN-CURRENCY-NO-READER` ("the fix **runs the script**"), and `PIN-CURRENCY-READER-PLAN.md:465`/`:469` ("the `clean` path is verified only by V4's stub") | **All three dead.** The check runs on every weekly `standards-drift` (the first was simply false — lesson in `CLAUDE.md` § "Durable traps → Process"); the reader SHIPPED at #392 and consumes the completed run's **log**; and V14 exercised close-on-clean for real |
| `plans/PLAN-*.md` as the governance-PR plan glob (`CHANGELOG.md`, `CI-CANON-V2.16-MIGRATION-PLAN.md:468`/`:784`) | **Fixed in `CLAUDE.md`** (#387/#390). The glob is a **suffix** — `plans/*-PLAN.md`. Merged plans and the CHANGELOG keep the old string as history; `CLAUDE.md` is the live rule |
