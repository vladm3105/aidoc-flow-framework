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
writing to GitHub from a script, and the process lessons. A trap recorded there is
**never** repeated here; this file carries only what has not settled yet.

## Where we are — 2026-08-02

Framework spec `0.40.0`, plugin `0.24.0`, Hermes `0.12.1`.
**Open PRs: 0. Open issues: 4** —
[#386](https://github.com/vladm3105/aidoc-flow-framework/issues/386),
[#405](https://github.com/vladm3105/aidoc-flow-framework/issues/405),
[#412](https://github.com/vladm3105/aidoc-flow-framework/issues/412),
[#417](https://github.com/vladm3105/aidoc-flow-framework/issues/417).

**Last merge: [#420](https://github.com/vladm3105/aidoc-flow-framework/pull/420), squash
`28c40e94` — the release changelog gate, `RELEASE-GATE-TBD-FALSE-POSITIVE`.**
`tests/release/` is now **green on `main` for the first time since 2026-07-08** (49 tests).

**⚠️ PR 5 is not one PR. It is five, and 5a is done — it was #420 above.** `PLUGIN-PREPROD-001-PLAN.md`
"Docs to update" table (`:330-354`, the PR-5 rows) lists **eight** documents of record
against the ≤3-surface governance cap, and the plan says to split (`:495`). The measured split, with the constraint that
forces it, is task 1 below. **PRs 1–4 shipped; the `PREPROD-*` batch stays under
`FRAMEWORK-TODO.md` `## Open` until 5d closes it — the entries do not tell you what has
shipped; this file does.**

**⚠️ Three `FRAMEWORK-TODO.md` entries are NOT part of the original 23 and must NOT be
closed with the batch** — `PREPROD-L7-BARE-DISPATCH` (#417), `PREPROD-AGENT-WEBFETCH`,
`PREPROD-PLAN-TESTPATH`. Only `PREPROD-PLAN-TESTPATH` is PR 5's to fix (a one-line path
amendment at `PLUGIN-PREPROD-001-PLAN.md:326`).

**⚠️ `L7` is resolved only because the *documentation* is now correct.** Plugin agents
register under a scoped identifier, so installation overwrites nothing — but a **bare**
name resolves by scope precedence, where a plugin ranks lowest of five. Every dispatch
the plugin ships is bare. #417 is the machine-facing half.

**⚠️ The `ai-review` gate WILL request changes on a code or CI PR with no root
`CHANGELOG.md` entry.** Budget 2 real doc surfaces + `CHANGELOG.md`; #415, #418 and #420
all did and passed. A failing run **uploads a verdict artifact**
(`gh run download <id> -n ai-review-verdict`) — a run that fails *after* producing it is
a verdict, not an outage.

**⚠️ Two tiers are RED on `main` for pre-existing reasons, neither CI-gated, neither
yours.** `Hermes pytest` — an unpinned `mcp[cli]>=1.0.0` floor, path-filtered, locally
green (570), see `HERMES-MCP-FLOATING-DEP`, do not re-diagnose. Phase 0 `lint-smoke` in
`tests/scripts/test-acceptance.sh` — example-corpus debt deferred to the wholesale regen;
use `--skip-lint-smoke`.

**V15 (schedule→`workflow_run` chain) is still unconfirmed** — never a gate; V14 proved
the chain off a *dispatched* upstream only. `standards-drift` runs Mondays 09:00 UTC,
**first observable 2026-08-03**. On or past that date, confirm a `pin-currency-reader` run
followed it with `event=workflow_run`, then delete this paragraph. A failure there is a
new bug, not a reopened plan.

## Next tasks — prioritized

The full queue is `plans/FRAMEWORK-TODO.md` (`## Open`) and `plans/HERMES-BACKLOG.md`.
This is only the ordering a fresh session should use.

1. **PLUGIN-PREPROD-001 — PR 5, stages b–e. The last stage of the initiative.**
   Read `plans/PLUGIN-PREPROD-001-PLAN.md` § "PR 5". The split below is **measured, not
   proposed** — a plugin `VERSION` bump makes `scripts/sync-version-refs.sh` rewrite
   **60 files including `CLAUDE.md`**, which pulls the bump under Governance PR
   discipline. Verified 2026-08-02 in a throwaway clone; the fanout was **clean** (only
   current-state tokens moved, no historical claim corrupted, so #405 did not fire on
   this bump).

   **⚠️ 5c CANNOT be split, and this is a founder decision — do not start it blind.**
   The hook re-stages its own writes, so the diff cannot be separated after the fact;
   the plan states exactly this at `:486-493` and resolved the identical Hermes case by
   **skipping the bump** (O2, `:505`). The plugin cannot skip — M6 needs `0.25.0`. So 5c
   needs Rule 1's stated exception: **explicit founder OK plus an audit-trail line in the
   commit message**. Ask for it before touching `VERSION`; do not self-grant it, and do
   not conclude the split above is wrong because one stage will not fit.

   | | Surfaces | Notes |
   |---|---|---|
   | **5b** | `SECURITY.md` (M7) + `CHANGELOG.md` | see M7 below — the plan's instruction is wrong |
   | **5c** | `VERSION` `0.24.0`→`0.25.0` + the 60-file fanout + both CHANGELOGs | run the propagation, then **hand-verify** |
   | **5d** | `ROADMAP.md` (M8) + `plans/DECISIONS.md` (`D-00NN`) + `plans/FRAMEWORK-TODO.md` (close the batch) | |
   | **5e** | `PLUGIN-PREPROD-001-PLAN.md` (`:326` fix + status → `Completed`) + `HANDOFF.md` + `CLAUDE.md` | |

   Two surfaces appear twice on purpose. `CLAUDE.md` takes the **mechanical version
   token** at 5c (hook-written) and the **authored** trap correction + trap graduation at
   5e. `CHANGELOG.md` takes a per-PR entry at every stage — that is doc-currency, not
   duplication.

   - **M7 — the plan says to *replace* `SECURITY.md`'s scanner list with what CI runs.
     Do not.** The existing list is not false, it is *incomplete*: `bandit`,
     `detect-secrets`, `detect-private-key` and `pip-audit` really are in
     `.pre-commit-config.yaml`, and the file says "in CI **and via pre-commit**". Split
     it by surface instead. **In CI:** semgrep (`sast-scan`), osv-scanner (`dep-scan`),
     gitleaks over full history (`secret-scan`), `trivy config` (`trivy-scan`), CodeQL.
     **Via pre-commit:** bandit (scoped to `platforms/hermes/src/` + `tests/`),
     detect-secrets, detect-private-key, pip-audit (`stages: [manual]`, so *not* every
     commit). Also wrong at `SECURITY.md:11`: spec `0.35.x` against an actual `0.40.0`;
     and CodeQL is listed as Python-only when `codeql.yml:42` sets
     `'["actions","python"]'`.
   - **M8 — `ROADMAP.md:56` says the plugin is `0.23.4`.** `sync-version-refs.sh` does
     **not** touch `ROADMAP.md`, which is why M8 rides with 5d rather than landing early.
     ⚠️ **`ROADMAP.md:113` also says `0.24.0` and is a *historical* claim**
     (IDGEN-NO-GENERATOR shipped at `0.24.0`) — it must survive untouched. That is
     exactly [#405](https://github.com/vladm3105/aidoc-flow-framework/issues/405).
   - **The plan's PR 5 section still says "add the README prerequisites section."** That
     shipped in PR 1. Do not re-add it.
   - **The plan's `--threshold` bullet is doubly stale** — PR 3 made the flag *live*.
     The changelog entry must say that, not restate either version of the old claim.
   - **M6 — cut `claude-code-plugin/v0.25.0` + publish a Release. FOUNDER-GATED**, after
     5c. The latest Release is `claude-code-plugin/v0.18.0` (2026-06-12), six versions
     stale. The PRs merge normally; only the tag and the public Release wait.
2. **[#417](https://github.com/vladm3105/aidoc-flow-framework/issues/417) — namespace the
   plugin's agent dispatch references.** 29 `subagent_type=` occurrences across 20 files,
   none scoped — but most are `subagent_type=<mapped agent>` *placeholders*, so the bare
   names live in the per-skill lens→agent mapping tables and
   `platforms/claude-code-plugin/README.md:215+` (`:213` is the table header). Mechanical,
   but **verify first that `subagent_type` accepts `plugin:agent`**; the docs confirm the
   scoped form for `--agent` and @-mention but do not state it for `subagent_type`. If it
   does not, this reopens as a rename of the definitions.
3. **`SDD-CORPUS-UNVERIFIED` — START WITH THE FOUNDER DECISION; it gates the plan.**
   Census in the `FRAMEWORK-TODO.md` entry. Two rules not there: **build the gate before
   touching content**, and this needs a `plans/` plan with the two-cycle gap review.
4. **[#412](https://github.com/vladm3105/aidoc-flow-framework/issues/412) — linting a
   single file reports every cross-document trace tag as a `TRACE-RES-001` ERROR.** Fix
   shape is the single-file gate `_check_forward_coverage` already carries
   (`tools/sdd_doc_lint/__init__.py:1972-1973`, documented at `:1965-1967`). ⚠️ The
   previous handoff cited `:1961-1963` for this and was wrong — those are run-mode
   severity bullets. Re-derive a carried-forward line number before re-publishing it.
5. **Watch [aidoc-flow-ci#351](https://github.com/vladm3105/aidoc-flow-ci/issues/351) —
   when canon ships its own reader, DELETE ours.** `.github/workflows/pin-currency-reader.yml`
   plus `scripts/read-pin-currency-log.sh` and `scripts/reconcile-pin-currency-issue.sh`
   are an override, not a permanent local surface (plan R9). Nothing else says so.
6. **[#405](https://github.com/vladm3105/aidoc-flow-framework/issues/405) —
   `sync-version-refs.sh` rewrites historical "shipped in vX" claims.** Corrupted
   `docs/PARITY.md:65` on three consecutive bumps. **Did NOT fire on the `0.25.0` plugin
   bump** (verified in a clone, 2026-08-02) — still open for framework-spec bumps.
7. **[#386](https://github.com/vladm3105/aidoc-flow-framework/issues/386) — the
   framework-spec token gates five files on `CLAUDE.md`'s own state.** Outstanding is only
   the **fix shape** — #389's approach cannot be reused because this `prev` is
   load-bearing elsewhere; derive it from a fanout target nobody hand-edits
   (`docs/PARITY.md`).
8. **`doc-maintainer` — nothing to do; it is PAUSED** (`kill_switch: true`, #397), CI
   green. Resume requires `aidoc-flow-ci` #352 **AND** #353 — #353 alone is 15 of the 23
   failures. Census in D-0072. ⚠️ **Do not re-file the `high_risk_paths` /
   `allowed_paths` mismatch** — deliberate and documented; #396 recorded it as a bug and
   was wrong.
9. **Hermes parity — the residual arc.** `plans/HERMES-BACKLOG.md`.
10. **Everything else** is in `FRAMEWORK-TODO.md` by tag. An entry under `## Open` with no
   `⏳ OPEN ON RESIDUAL` marker is genuinely open work (#403). Nothing there is blocking.

## Traps too fresh to have settled — not yet in `CLAUDE.md`

- **A perfect first-try mutation kill rate is the symptom, not the result.** Two runs in
  one session scored 11/11 and 17/17 and **both were worthless** — the first because the
  harness copied the module to a scratch dir where its `sys.path` sibling did not resolve,
  so every mutant died of `ModuleNotFoundError`; the second because two new tests were
  failing, so every mutant died of the red baseline. **Assert the unmutated baseline is
  green *inside* the harness, and include a control mutant that must die.** The valid run
  then found six real survivors, every one of which drove a code change.
  **The other half of this trap, still recorded nowhere else:** anything that mutates
  source in place leaves the tree dirty in a way that reads as authored code. Restore from
  a saved copy each iteration, **never in a `finally`** (killing a hung mutant skips it),
  bound each run with a timeout, and verify `git diff --quiet <path>` before any run you
  intend to trust.
- **When a fix has a *scope* and a *matcher*, changing one re-breaks the other.** The
  release gate's scope fix immediately failed against the PR's own changelog entry,
  because an entry documenting a placeholder check has to name the tokens it checks for.
  Ask which *other* dimension the change moved.
- **`CLAUDE.md` § "Durable traps → Local hooks and tooling" carries two wrong claims in
  one sentence, at `:829-836`.** (a) "`test-plugin.sh:257`/`:302` end in `|| true`, so
  even the manual path cannot fail" — the script sets `set -uo pipefail` with **no `-e`**
  (`:52`), `FAILED` is `declare -i` (`:114`), and `run()` increments it *before*
  returning (`:123-137`), which `:369-376` turns into `exit 1`. The `|| true` suppresses
  nothing. (b) "nothing calls that script" — refuted by umbrella `release.yml:32`.
  **Fix both in 5e, not the one that is easier to see.**
- **Before writing "nothing runs X", check the umbrella.** A first draft of
  `RELEASE-TIER-STALE-SUBMODULE-PIN` shipped exactly that inversion. The umbrella runs
  `tests/release/` unguarded on **every PR** (`aidoc-flow/.github/workflows/pr-checks.yml:42`)
  and every `v*` tag (`release.yml:37`) — it just pins this repo at `0ffa153c`
  (2026-06-15), three weeks before the defect. A green umbrella run is not evidence about
  this repo's `main`.
- **`check_plan.py` false-greens on a not-ready plan.** Its zero-findings check is a
  phrase match, and it accepted a Review log whose final pass said *"**Result:** NOT
  READY"* — because the surrounding prose contained "all folded". Canonical script is
  `~/.claude/skills/verified-planning/check_plan.py`; no repo-local copy. **Not filed.**
- **markdownlint silently corrupts claim-ledger citations.** Its autofix rewrites
  `__init__.py` → `**init**.py` in an unbackticked table cell, which broke **ten**
  citations at once and made the gate fail with the misleading `path '.py' does not
  exist`. Workaround in #408: `<!-- markdownlint-disable MD050 -->` scoped around the
  ledger. It also normalizes `_x_` → `*x*` across a **whole** changelog file you touch.
  **Not filed.**

**These four have settled and belong in `CLAUDE.md` — graduate them in 5e, which touches
that file anyway.** They are kept here, condensed, because they are *not* there yet:

- **A registration rule and a resolution rule live in different tables; you find the
  reassuring one first.** "Installing it shadows nothing" ≠ "a bare name resolves to it".
  Ask what resolves it *at call time*. No test and no green CI catches a wrong reassurance.
- **Your own test can enshrine the defect you just introduced** — written beside its fix,
  it inherits the fix's misconception, and mutation testing is blind because mutant and
  test agree. When a fix has a *direction*, state it as an invariant in code.
- **A surviving mutant usually indicts the test, not the fix.** Assert the classification,
  not the downstream outcome, when the outcome has more than one possible cause.
- **A fix can silently disarm an existing regression test and the suite stays green.**
  When a change alters an exit code, return value or error type, grep for tests provoking
  the OLD behaviour.

Also unresolved and blocking nothing: the founder flagged plugin `requirements-analyst`'s
`model: sonnet` as unratified.

**Standing:** the example corpus is regenerated wholesale after framework changes, so
corpus-remediation findings are deferred to that regen. IPLAN ↔ iplanic integration is
deferred (`plans/IPLAN-IPLANIC-DEFERRED.md`).

## Stale advice — a fresh session will find these referenced, and they are FIXED

| Stale claim | Reality |
|---|---|
| "no authoring surface computes SHA-256 in-prompt any more" (`ROADMAP.md:113`, `platforms/hermes/CHANGELOG.md` `[0.12.0]`, `plans/IDGEN-NO-GENERATOR-PLAN.md`) | **Still false, in a narrower way.** #406 closed the plugin-SKILL and Hermes-reference halves; `agent-skills/**/SKILL.md` is reached by no root and `sdd-orchestrator/SKILL.md:667` still hashes. `ROADMAP.md` also dates the claim to Hermes `0.12.0`, which was never true |
| "`--admin` is required on every PR" (`aidoc-flow-ci#322`) | **Fixed at `ci/v2.16.0`.** Every PR since #378, most recently #420, reached mergeable with no `--admin`. Do not re-add PR numbers to this row — it is the one that accretes |
| "Branch protection requires the phantom `Lint / format / security hooks`, so every PR is BLOCKED" | **Fixed.** The six required contexts, re-confirmed green on #420, are `call / Lint / format / security hooks`, `call / composition`, `call / ai-review`, `call / verify`, `Framework + platform conformance`, `Acceptance tier (deterministic)`. `call / trust` and `Hermes pytest` are **not** required |
| `AIDOC-CI-COMPOSITION-CHECK-PRHEAD` — "`call / composition` is structurally unsatisfiable on a PR head" | **Stale.** composition reports success on PR heads. A reviewer once read this entry as proof that required checks gate nothing here, and it nearly killed a correct plan |
| Three pin-currency claims: `NO-PIN-CURRENCY-CHECK`, `PIN-CURRENCY-NO-READER`, `PIN-CURRENCY-READER-PLAN.md:465`/`:469` | **All three dead.** The check runs on every weekly `standards-drift`; the reader SHIPPED at #392 and consumes the completed run's **log**; V14 exercised close-on-clean for real |
| `plans/PLAN-*.md` as the governance-PR plan glob (`CHANGELOG.md`, `CI-CANON-V2.16-MIGRATION-PLAN.md:468`/`:784`) | **Fixed in `CLAUDE.md`** (#387/#390). The glob is a **suffix** — `plans/*-PLAN.md`. Merged plans and the CHANGELOG keep the old string as history; `CLAUDE.md` is the live rule |
