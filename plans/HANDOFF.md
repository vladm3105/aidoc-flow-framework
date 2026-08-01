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
**Open PRs: 0. Open issues: 4** —
[#386](https://github.com/vladm3105/aidoc-flow-framework/issues/386),
[#405](https://github.com/vladm3105/aidoc-flow-framework/issues/405),
[#412](https://github.com/vladm3105/aidoc-flow-framework/issues/412) and
[#417](https://github.com/vladm3105/aidoc-flow-framework/issues/417) (new).

**Last merge: [#418](https://github.com/vladm3105/aidoc-flow-framework/pull/418), squash
`81a3b7a6` — PLUGIN-PREPROD-001 **PR 4 of 5**, agent and manifest hygiene.**

**The founder intends to deploy the plugin.** `plans/PLUGIN-PREPROD-001-PLAN.md` clears
the BLOCKER verdict in five staged PRs. **PRs 1–4 have shipped; only PR 5 remains**, and
it is founder-gated on the tag + Release. Conformance is now **361** tests.
The `PREPROD-*` entries stay under `FRAMEWORK-TODO.md` `## Open` until PR 5 closes them
— that batching is the plan's design, so *the entries do not tell you what has shipped;
this file does.*

**What PR 4 settled.** `requirements-analyst` no longer inherits every tool (it was the
only one of eleven declaring neither `tools:` nor `model:`); the plugin ships its
`LICENSE`; `marketplace.json` publishes `owner.url` instead of a personal email.
`tests/conformance/platforms/test_agent_frontmatter.py` locks those **and** the read-only
claim — an agent marked `custom_fields.access: read-only` may hold no `Write`, `Edit` or
`NotebookEdit`. `Bash` is deliberately *excluded* from that set (the lenses genuinely
shell out), which is why `docs/AGENTS.md` now says read-only means *no editing tools plus
an instruction*, not a sandbox.

**⚠️ The one thing PR 4 did NOT close, and a fresh session will misread it.** `L7` is
resolved because the *documentation* is now correct — not because the collision is gone.
Plugin agents register under a scoped identifier (`aidoc-flow:code-reviewer`), so
installation overwrites nothing; but a **bare** name resolves by *scope precedence*, where
a plugin ranks **lowest of five**, below `~/.claude/agents/`. Every dispatch this plugin
ships is bare, so a consumer defining `code-reviewer` silently replaces the read-only gate
with their own agent. Filed as `PREPROD-L7-BARE-DISPATCH` / #417 with the fix shape.

**⚠️ Three `FRAMEWORK-TODO.md` entries are NEW and *not* part of the original 23** —
`PREPROD-L7-BARE-DISPATCH`, `PREPROD-AGENT-WEBFETCH`, `PREPROD-PLAN-TESTPATH`. **PR 5 must
not close them** with the rest of the `PREPROD-*` batch; only `PREPROD-PLAN-TESTPATH` is
PR 5's to fix (a one-line path amendment).

**⚠️ The `ai-review` gate WILL request changes on a code or CI PR with no root
`CHANGELOG.md` entry.** It did on #413, and it was right: the plan's deferral of "the
changelogs" to PR 5 covers the *release narrative*, not the per-PR doc-currency rule.
**Budget 2 real doc surfaces + `CHANGELOG.md`** — #415 and #418 both did and passed. Read
the verdict before assuming infrastructure: the failing job **uploads a verdict artifact**
(`gh run download <id> -n ai-review-verdict`) naming the finding, so a run that fails
*after* producing it is a verdict, not an outage.

**⚠️ `Hermes pytest` is RED on `main`; not this repo's regression, does not block merges.**
An unpinned `mcp[cli]>=1.0.0` floor resolves to whatever the SDK last published. **Not a
required context**, and it is path-filtered, so a PR touching no Hermes file (like #418)
never runs it. Locally it passes (570). `HERMES-MCP-FLOATING-DEP` has the detail; do not
re-diagnose it.

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

1. **PLUGIN-PREPROD-001 — PR 5, the last stage: docs, version bump, tag, Release.
   FOUNDER-GATED.** The tag cut and the public Release are outward-facing and wait on
   explicit founder approval; the PR itself merges normally. Read
   `plans/PLUGIN-PREPROD-001-PLAN.md` § "PR 5". Five things to know before starting:
   - **`tests/release/test_changelog_entry.py` is RED on `main` and PR 5 is the first
     stage that hits it** — `RELEASE-GATE-TBD-FALSE-POSITIVE`. Fix or scope the gate
     before the release narrative, not during it.
   - **The plan's PR 5 section still says "add the README prerequisites section."** That
     shipped in PR 1. PR 5 must not re-add it.
   - **The plan's `--threshold` bullet says `CHANGELOG.md` claims the flag was removed
     from the driver, and that the claim is false.** It is now false in a second way: PR 3
     made the flag *live*. PR 5's entry must say that, not restate either.
   - **[#405](https://github.com/vladm3105/aidoc-flow-framework/issues/405) fires here** —
     the version fanout rewrites historical "shipped in vX" claims. Hand-verify every
     surface rather than trusting `sync-version-refs.sh`.
   - **Amend `plans/PLUGIN-PREPROD-001-PLAN.md:326`** — it names
     `tests/conformance/test_agent_frontmatter.py`; the file shipped under `platforms/`.
     That is `PREPROD-PLAN-TESTPATH`, and PR 5 is the natural place because it touches the
     plan anyway.
2. **[#417](https://github.com/vladm3105/aidoc-flow-framework/issues/417) — namespace the
   plugin's agent dispatch references.** The machine-facing half of L7 (above). **29
   `subagent_type=` occurrences across 20 files, none scoped** — but most are
   `subagent_type=<mapped agent>` *placeholders*, so the bare names actually live in the
   per-skill lens→agent mapping tables and `README.md:213`, which is where the sweep lands.
   Mechanical, but **verify first that `subagent_type` accepts `plugin:agent`** —
   the docs confirm the scoped form for `--agent` and @-mention and show
   `my-plugin:review:security`, but do not state it for `subagent_type`. If it does not,
   this reopens as a rename of the definitions.
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
   `docs/PARITY.md:65` on three consecutive bumps. **Fires next at PR 5**; mitigation is
   to hand-verify every surface rather than trust the script.
7. **[#386](https://github.com/vladm3105/aidoc-flow-framework/issues/386) — the
   framework-spec token gates five files on `CLAUDE.md`'s own state.** Mechanism:
   `CLAUDE.md` § "Durable traps → Local hooks and tooling". Outstanding is only the **fix
   shape** — #389's approach cannot be reused because this `prev` is load-bearing
   elsewhere; derive it from a fanout target nobody hand-edits (`docs/PARITY.md`).
8. **`doc-maintainer` — nothing to do; it is PAUSED** (`kill_switch: true`, #397), CI
   green. **Resume requires `aidoc-flow-ci` #352 AND #353** — #353 alone is 15 of the 23
   failures, so #352 alone returns a majority-red pilot. Census in D-0072. ⚠️ **Do not
   re-file the `high_risk_paths` / `allowed_paths` mismatch** — deliberate and documented
   in the config; #396 recorded it as a bug and was wrong.
9. **Hermes parity — the residual arc.** `plans/HERMES-BACKLOG.md`: remaining
   plugin-vs-Hermes deltas plus quality-loop Phase 2 (cross-invocation resume / G-R1,
   the parallel-review global lock).
10. **Everything else** is in `FRAMEWORK-TODO.md` by tag. An entry under `## Open` with no
   `⏳ OPEN ON RESIDUAL` marker is genuinely open work (#403). Nothing there is blocking.

## Traps too fresh to have settled — not yet in `CLAUDE.md`

- **When a platform behaviour has a *registration* rule and a *resolution* rule, they live
  in different tables and you will find the reassuring one first.** PR 4 verified that
  plugin agents are namespaced (true, and it means installation shadows nothing) and
  concluded the name collision was closed. The resolution rule is a *different* table in a
  *different* doc: a bare name is picked by scope precedence, plugin lowest. The result
  was documentation that told readers a real hazard was not one. **Neither the test suite
  nor a green CI can catch a wrong reassurance** — only a reader who goes back to the
  vendor's own source. Ask "what resolves this at call time?", not only "what does
  installing it do?"
- **Your own test can enshrine the defect you just introduced.** PR 3's first draft forced
  the saga toward `CLOSED` on an inconsistent journal *and* shipped a test asserting
  exactly that. Green, mutation-clean at 24/24, and wrong — the mutant and the test agree,
  so mutation testing is blind to it. **Only an independent reader with the spec in hand
  catches it.** When a fix has a *direction* (fail-open vs fail-closed), state the
  direction as an invariant in code rather than trusting each call site.
- **A surviving mutant usually indicts the test, not the fix.** Both PR 3 survivors were
  weak assertions. **Assert the classification, not the downstream outcome**, whenever the
  outcome has more than one possible cause.
- **A fix can silently disarm an existing regression test, and the suite stays green.**
  PR 2's exit-3 guard turned a PR 1 crash test into three assertions that passed because
  nothing was produced. **When a change alters an exit code, a return value or an error
  type, grep the suite for tests that provoke the OLD behaviour.**
- **Anything that mutates source in place leaves the tree dirty in a way that reads as
  authored code** — a background agent, or your own mutation harness. One PR 3 mutant hung
  the harness; killing it skipped the `finally` that restores the source. **Restore from a
  saved copy each iteration, never in a `finally`, bound each run with a timeout, and
  verify `git diff --quiet <path>` before any run you intend to trust.**
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

**Standing:** the example corpus is regenerated wholesale after framework changes, so
corpus-remediation findings are deferred to that regen rather than fixed in place.
IPLAN ↔ iplanic integration is deferred (`plans/IPLAN-IPLANIC-DEFERRED.md`).

## Stale advice — a fresh session will find these referenced, and they are FIXED

Older plans, TODO entries and commit messages still describe these as live. They are not.
Every row still has at least one live source in the repo.

| Stale claim | Reality |
|---|---|
| "no authoring surface computes SHA-256 in-prompt any more" (`ROADMAP.md:113`, `platforms/hermes/CHANGELOG.md` `[0.12.0]` heading, `plans/IDGEN-NO-GENERATOR-PLAN.md`) | **Still false, in a narrower way.** #406 closed the plugin-SKILL and Hermes-reference halves; `agent-skills/**/SKILL.md` is reached by no root and `sdd-orchestrator/SKILL.md:667` still hashes. `ROADMAP.md` also dates the claim to Hermes `0.12.0`, which was never true |
| "`--admin` is required on every PR" (the `ai-review` self-cancel, `aidoc-flow-ci#322`) | **Fixed at `ci/v2.16.0`.** Every PR since #378, most recently #418, reached mergeable with no `--admin`. Do not re-add PR numbers to this row — it is the one that accretes |
| "Branch protection requires the phantom `Lint / format / security hooks`, so every PR is BLOCKED" | **Fixed.** The six required contexts, re-confirmed green on #418, are `call / Lint / format / security hooks`, `call / composition`, `call / ai-review`, `call / verify`, `Framework + platform conformance`, `Acceptance tier (deterministic)`. `call / trust` and `Hermes pytest` are **not** required |
| `AIDOC-CI-COMPOSITION-CHECK-PRHEAD` — "`call / composition` is structurally unsatisfiable on a PR head" | **Stale.** composition reports success on PR heads. A reviewer once read this entry as proof that required checks gate nothing here, and it nearly killed a correct plan |
| Three pin-currency claims: `NO-PIN-CURRENCY-CHECK` ("this repo runs `check-pin-currency.sh` nowhere"), `PIN-CURRENCY-NO-READER` ("the fix **runs the script**"), and `PIN-CURRENCY-READER-PLAN.md:465`/`:469` ("the `clean` path is verified only by V4's stub") | **All three dead.** The check runs on every weekly `standards-drift` (the first was simply false — lesson in `CLAUDE.md` § "Durable traps → Process"); the reader SHIPPED at #392 and consumes the completed run's **log**; and V14 exercised close-on-clean for real |
| `plans/PLAN-*.md` as the governance-PR plan glob (`CHANGELOG.md`, `CI-CANON-V2.16-MIGRATION-PLAN.md:468`/`:784`) | **Fixed in `CLAUDE.md`** (#387/#390). The glob is a **suffix** — `plans/*-PLAN.md`. Merged plans and the CHANGELOG keep the old string as history; `CLAUDE.md` is the live rule |
