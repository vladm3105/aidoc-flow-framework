# Session Handoff

**One reader: a fresh session with zero context.** Current state, then what to do next.
**Rewritten wholesale each merge** — `git log -- plans/HANDOFF.md` is the archive; do not
restore prior states here. Settled traps live in `CLAUDE.md` § "Durable traps" and are
never repeated here; open work lives in `plans/FRAMEWORK-TODO.md`, never here.

## Where we are — 2026-08-02

Framework spec `0.40.0`, plugin `0.24.0`, Hermes `0.12.1`.
**Open PRs: 0. Open issues: 5** —
[#386](https://github.com/vladm3105/aidoc-flow-framework/issues/386),
[#405](https://github.com/vladm3105/aidoc-flow-framework/issues/405),
[#412](https://github.com/vladm3105/aidoc-flow-framework/issues/412),
[#417](https://github.com/vladm3105/aidoc-flow-framework/issues/417),
[#423](https://github.com/vladm3105/aidoc-flow-framework/issues/423).

**Last merge: [#422](https://github.com/vladm3105/aidoc-flow-framework/pull/422), squash
`4cbaaad5` — `SECURITY.md` corrected, finding M7, PR 5 stage b.** The file had described
a security posture this repo does not have; the enforcement half was inverted. Ground
truth, as of 2026-08-02 and now recorded in `SECURITY.md` itself: **none** of the five
scanners under `.github/workflows/` (`codeql`, `dep-scan`, `sast-scan`, `secret-scan`,
`trivy-scan`) is a required status check, and the required
`call / Lint / format / security hooks` context is the `pre-commit` job — so the only
*checks* whose findings block a merge are `bandit`, `detect-secrets` and
`detect-private-key`. Two qualifiers travel with that claim; do not drop them when
re-summarizing:

- **`bandit` is scoped** `^(platforms/hermes/src/|tests/).*\.py$`
  (`.pre-commit-config.yaml:50`), so most of `tools/` and the plugin tree is outside it.
- **`SECURITY.md:66` names the one non-check control that does block** — GitHub
  secret-scanning push protection. It is enabled.

Branch protection is mutable and this claim now lives in a public file — re-derive with
`gh api repos/vladm3105/aidoc-flow-framework/branches/main/protection --jq '.required_status_checks.contexts'`
before citing it.

**Private vulnerability reporting was DISABLED and is now on** (founder-authorized
2026-08-02, verified by readback). `SECURITY.md` had pointed researchers at a Security-tab
control that did not render while forbidding the public fallback, so its only reporting
channel dead-ended. Do not re-file this; do not disable it.

**⚠️ PR 5 is five PRs. 5a (#420) and 5b (#422) are done; 5c is next and is FOUNDER-GATED
on the Rule 1 surface-cap exception.** `PLUGIN-PREPROD-001-PLAN.md` § "Docs to update"
(`:532-536`) lists **eight** documents of record for PR 5 against the ≤3-surface
governance cap, and the plan says to split (`:547`). The measured split is task 1 below.
**PRs 1–4 shipped; the `PREPROD-*` batch stays under `FRAMEWORK-TODO.md` `## Open` until
5d closes it — the entries do not tell you what has shipped; this file does.**

**⚠️ Three `FRAMEWORK-TODO.md` entries are NOT part of the original 23 and must NOT be
closed with the batch** — `PREPROD-L7-BARE-DISPATCH` (#417), `PREPROD-AGENT-WEBFETCH`,
`PREPROD-PLAN-TESTPATH`. Only `PREPROD-PLAN-TESTPATH` is PR 5's to fix (a one-line path
amendment at `PLUGIN-PREPROD-001-PLAN.md:378`).

**⚠️ `L7` is resolved only because the *documentation* is now correct.** Plugin agents
register under a scoped identifier, so installation overwrites nothing — but a **bare**
name resolves by scope precedence, where a plugin ranks lowest of five. Every dispatch the
plugin ships is bare. #417 (task 2) is the machine-facing half.

**⚠️ The `ai-review` gate WILL request changes on a code or CI PR with no root
`CHANGELOG.md` entry.** The ≤3-surface cap is a *ceiling*, not observed practice — recent
PRs have used one real surface + `CHANGELOG.md` and others three; what they share is the
changelog entry. A failing run **uploads a verdict artifact**
(`gh run download <id> -n ai-review-verdict`) — a run that fails *after* producing it is a
verdict, not an outage.

**⚠️ Two tiers are RED on `main` for pre-existing reasons, neither CI-gated, neither
yours.** `Hermes pytest` — an unpinned `mcp[cli]>=1.0.0` floor, path-filtered, locally
green (570), see `HERMES-MCP-FLOATING-DEP`, do not re-diagnose. Phase 0 `lint-smoke` in
`tests/scripts/test-acceptance.sh` — example-corpus debt deferred to the wholesale regen;
use `--skip-lint-smoke`.

**V15 (schedule→`workflow_run` chain) is still unconfirmed** — never a gate; V14 proved the
chain off a *dispatched* upstream only. `standards-drift` runs Mondays 09:00 UTC, **first
observable 2026-08-03**. On or past that date, confirm a `pin-currency-reader` run followed
it with `event=workflow_run`, then delete this paragraph. A failure there is a new bug, not
a reopened plan.

## Next tasks — prioritized

The full queue is `plans/FRAMEWORK-TODO.md` (`## Open`) and `plans/HERMES-BACKLOG.md`.
This is only the ordering a fresh session should use.

1. **PLUGIN-PREPROD-001 — PR 5, stages c–e. The last stage of the initiative.**
   Read `plans/PLUGIN-PREPROD-001-PLAN.md` § "PR 5" (`:292`).

   **⚠️ STOP: 5c needs an explicit founder OK before you touch `VERSION`, plus an
   audit-trail line in the commit message.** A plugin bump is a 60-file diff including
   `CLAUDE.md` (Governance PR discipline), and the hook re-stages its own writes so it
   **cannot be split**. Do not self-grant the Rule 1 exception; do not conclude the split
   is wrong because one stage will not fit. The full argument, the stage table, and the
   **four falsified plan claims 5e must correct** are now in the plan (§ "PR 5") — durable
   content, kept there because this file is deleted at the next merge. Read it; do not
   re-derive it.

   `CLAUDE.md` takes the **mechanical version token** at 5c (hook-written) and the
   **authored** trap corrections + trap graduation at 5e. `CHANGELOG.md` takes a per-PR
   entry at every stage — that is doc-currency, not duplication.

   - **How to propagate (5c).** Edit `platforms/claude-code-plugin/VERSION` and commit;
     the `sync-version-refs` pre-commit hook fires on `^platforms/[^/]+/VERSION$`
     (`.pre-commit-config.yaml:116-124`), rewrites the fanout and re-stages itself.
     `tools/sync-plugin-framework.sh` is **not** part of a plugin bump — it is
     framework-spec-driven and references no `VERSION` file. Re-derive the 60 before
     trusting it (throwaway clone, per the `CLAUDE.md` trap):

     ```sh
     d=$(mktemp -d) && git clone -q --no-hardlinks . "$d/f" && cd "$d/f" \
       && echo 0.25.0 > platforms/claude-code-plugin/VERSION \
       && bash scripts/sync-version-refs.sh >/dev/null 2>&1; git status --porcelain | wc -l
     ```

   - **⚠️ A clone cannot verify the whole fanout, and the part it cannot see is broken.**
     `scripts/sync-version-refs.sh:180` also writes the **sibling repo**
     `../web-site/src/pages/index.astro`, which no clone has. In the real tree that write
     **silently no-ops**: the site badge reads `Pre-release v0.20.1` (`:19`), the script
     greps for the *previous* value, and `replace_in_file` returns 0 without logging on a
     miss. So 5c must update the site **by hand in a `web-site` PR**, or the public page
     stays five minors stale — and no future bump will ever repair it. Filed as
     [#423](https://github.com/vladm3105/aidoc-flow-framework/issues/423)
     (`SYNC-WEBSITE-SILENT-NOOP`).
   - **5d must correct `PREPROD-M7`'s *Context* line before closing it**
     (`FRAMEWORK-TODO.md:390`) — it repeats the same rejected misconception
     ("`SECURITY.md:49` names `bandit`"), which is now stale in line number *and*
     substance. It also clears the GOV-TODO-ISSUE-SPLIT bar and has no `→ #N`.
   - **M8 — `ROADMAP.md:56` says the plugin is `0.23.4`.** `sync-version-refs.sh` does
     **not** touch `ROADMAP.md`, which is why M8 rides with 5d rather than landing early.
     ⚠️ **`ROADMAP.md:113` also says `0.24.0` and is a *historical* claim**
     (IDGEN-NO-GENERATOR shipped at `0.24.0`) — it must survive untouched. That is exactly
     [#405](https://github.com/vladm3105/aidoc-flow-framework/issues/405).
   - **M6 — cut `claude-code-plugin/v0.25.0` + publish a Release. SEPARATELY
     FOUNDER-GATED** (an outward-facing tag + Release, not the Rule 1 exception), after
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
   (`tools/sdd_doc_lint/__init__.py:1972-1973`, documented at `:1965-1967`). ⚠️ An earlier
   handoff cited `:1961-1963` and was wrong — those are run-mode severity bullets.
   Re-derive a carried-forward line number before re-publishing it.
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
   the **fix shape** — #389's approach cannot be reused because this `prev` is load-bearing
   elsewhere; derive it from a fanout target nobody hand-edits (`docs/PARITY.md`).
8. **`doc-maintainer` — nothing to do; it is PAUSED** (`kill_switch: true`, #397), CI
   green. Resume requires `aidoc-flow-ci` #352 **AND** #353 — #353 alone is 15 of the 23
   failures. Census in D-0072. ⚠️ **Do not re-file the `high_risk_paths` /
   `allowed_paths` mismatch** — deliberate and documented; #396 recorded it as a bug and
   was wrong.
9. **Hermes parity — the residual arc.** `plans/HERMES-BACKLOG.md`.
10. **Everything else** is in `FRAMEWORK-TODO.md` by tag. An entry under `## Open` with no
   `⏳ OPEN ON RESIDUAL` marker is genuinely open work (#403). Nothing there is blocking.

## Traps too fresh to have settled — not yet in `CLAUDE.md`

- **A review fold authors its own false claims, and the pass that produced the fold never
  catches them.** Three on #422, each caught by the *next* cycle: "`codeql` fails on
  findings" (its reusable has no findings gate at all); "tags lag `main` **by design**"
  (`docs/TAGGING.md:97` calls it a known backlog); and a supported-versions table whose two
  ✅ rows cancelled the ❌ row below them. No rate is implied — the removed-defect count was
  never tallied. **Re-verify folded text against source, not against the findings list**,
  and expect a fold that rewrites a section wholesale to need its own full pass.
- **A document can name a channel, a control or a setting that does not exist, and nothing
  in CI will ever notice** — `SECURITY.md` pointed at private vulnerability reporting for
  months while it was disabled. Found only by running
  `gh api repos/<r>/private-vulnerability-reporting`. **When a doc tells a reader to go
  somewhere, go there.** The same pass found push protection on but
  `secret_scanning_non_provider_patterns` and `..._validity_checks` off, which narrows what
  it catches (`SYNC-SECRET-SCANNING-KNOBS` in `FRAMEWORK-TODO.md`).
- **A cross-repo write is invisible to the isolation you verify in.** See the `../web-site/`
  warning under task 1 — a throwaway clone is the prescribed way to test a sync script, and
  it is structurally blind to the one write that leaves the repo. **Ask what the sandbox
  cannot see**, and check whether a "skipped silently" path is silent about *absence* only
  or about *a value mismatch* too.
- **A perfect first-try mutation kill rate is the symptom, not the result.** Two runs in one
  session scored 11/11 and 17/17 and **both were worthless** — one harness copied the module
  where its `sys.path` sibling did not resolve, so every mutant died of
  `ModuleNotFoundError`; the other ran against a red baseline. **Assert the unmutated
  baseline green *inside* the harness, and include a control mutant that must die.** The
  valid run then found six real survivors, every one of which drove a code change. Also:
  anything mutating source in place leaves the tree dirty in a way that reads as authored
  code — restore from a saved copy each iteration, **never in a `finally`** (killing a hung
  mutant skips it), bound each run with a timeout, and verify `git diff --quiet <path>`
  before any run you intend to trust.
- **When a fix has a *scope* and a *matcher*, changing one re-breaks the other.** The release
  gate's scope fix immediately failed against the PR's own changelog entry, because an entry
  documenting a placeholder check has to name the tokens it checks for. Ask which *other*
  dimension the change moved.
- **`CLAUDE.md` § "Durable traps → Local hooks and tooling" carries two wrong claims in one
  sentence, at `:829-836`.** (a) "`test-plugin.sh:257`/`:302` end in `|| true`, so even the
  manual path cannot fail" — the script sets `set -uo pipefail` with **no `-e`** (`:52`),
  `FAILED` is `declare -i` (`:114`), and `run()` increments it *before* returning
  (`:123-137`), which `:369-376` turns into `exit 1`. The `|| true` suppresses nothing.
  (b) "nothing calls that script" — refuted by umbrella `release.yml:32`. **Fix both in 5e,
  not the one that is easier to see.** Related and durable: the umbrella runs
  `tests/release/` unguarded on **every** PR (`aidoc-flow/.github/workflows/pr-checks.yml:42`)
  and every `v*` tag, but pins this repo at `0ffa153c` (2026-06-15) — so a green umbrella run
  is not evidence about this repo's `main`. **Before writing "nothing runs X", check the
  umbrella.**
- **`check_plan.py` false-greens on a not-ready plan.** Its zero-findings check is a phrase
  match, and it accepted a Review log whose final pass said *"**Result:** NOT READY"* —
  because the surrounding prose contained "all folded". Canonical script is
  `~/.claude/skills/verified-planning/check_plan.py`; no repo-local copy. **Not filed.**
- **markdownlint's `__init__.py` → `**init**.py` corruption is already in `CLAUDE.md`; two
  things are not.** It made the citation gate fail with the misleading
  `path '.py' does not exist`, and the workaround in #408 is
  `<!-- markdownlint-disable MD050 -->` scoped around the ledger. It also normalizes
  `_x_` → `*x*` across a **whole** changelog file you touch. **Fold these two into the
  existing `CLAUDE.md` bullet at 5e; do not re-state the corruption itself.**

**Four settled traps to graduate into `CLAUDE.md` at 5e** (it touches that file anyway).
Titles only — the full text is in `git log -- plans/HANDOFF.md` at `4cbaaad5`:
registration-rule vs resolution-rule; your own test can enshrine the defect it was written
beside; a surviving mutant usually indicts the test, not the fix; a fix can silently disarm
an existing regression test.

Also unresolved and blocking nothing: the founder flagged plugin `requirements-analyst`'s
`model: sonnet` as unratified.

## Stale advice — a fresh session will find these referenced, and they are FIXED

| Stale claim | Reality |
|---|---|
| "`--admin` is required on every PR" ([aidoc-flow-ci#322](https://github.com/vladm3105/aidoc-flow-ci/issues/322)) | **Fixed at `ci/v2.16.0`.** Every PR since #378 has reached mergeable with no `--admin`. Do not re-add PR numbers to this row — it is the one that accretes |
| "Branch protection requires the phantom `Lint / format / security hooks`, so every PR is BLOCKED" | **Fixed.** The six required contexts are `call / Lint / format / security hooks`, `call / composition`, `call / ai-review`, `call / verify`, `Framework + platform conformance`, `Acceptance tier (deterministic)`. `call / trust` and `Hermes pytest` are **not** required |
| `AIDOC-CI-COMPOSITION-CHECK-PRHEAD` — "`call / composition` is structurally unsatisfiable on a PR head" | **Stale.** composition reports success on PR heads. A reviewer once read this entry as proof that required checks gate nothing here, and it nearly killed a correct plan |
| Three pin-currency claims: `NO-PIN-CURRENCY-CHECK`, `PIN-CURRENCY-NO-READER`, `PIN-CURRENCY-READER-PLAN.md:465`/`:469` | **All three dead.** The check runs on every weekly `standards-drift`; the reader SHIPPED at #392 and consumes the completed run's **log**; V14 exercised close-on-clean for real |

**Standing:** the example corpus is regenerated wholesale after framework changes, so
corpus-remediation findings are deferred to that regen. IPLAN ↔ iplanic integration is
deferred (`plans/IPLAN-IPLANIC-DEFERRED.md`).
