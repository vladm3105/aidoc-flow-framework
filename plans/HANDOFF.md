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
**Open PRs: 0. Open issues: 2** —
[#386](https://github.com/vladm3105/aidoc-flow-framework/issues/386) and
[#405](https://github.com/vladm3105/aidoc-flow-framework/issues/405).

**Last merge: [#410](https://github.com/vladm3105/aidoc-flow-framework/pull/410), squash
`3bbadbb1` — PLUGIN-PREPROD-001 **PR 1 of 5**, hook hardening. Code + tests + docs.**

**The founder intends to deploy the plugin.** The merged plan
`plans/PLUGIN-PREPROD-001-PLAN.md` clears the BLOCKER verdict in five staged PRs.
**PR 1 shipped**, closing B1, B4's hook half, H1, H2, H3, M1, L4 and P1: the review hook
no longer executes code from the user's working directory, no longer relabels a crash as
structural findings, honours `review_hook`, frames untrusted content, and is bounded.
`tests/conformance/test_plugin_hook_safety.py` (26 tests) locks it; conformance is now
**281** tests. **All 23 findings now have a `FRAMEWORK-TODO.md` entry** (`PREPROD-*`);
PR 5 closes them. No GitHub issues were filed — all 23 are already-planned work, which
`GOV-TODO-ISSUE-SPLIT` keeps TODO-only.

**Two things PR 1 changed that the plan does not describe**, both found by review and
reproduced before folding — a later stage that assumes the plan's text will be wrong:

- **The linter now runs with its CWD set to the plugin root**, not just with
  `PYTHONSAFEPATH=1`. That variable landed in **Python 3.11** and is silently ignored
  below it, so B1 was unfixed on stock macOS (`/usr/bin/python3` is 3.9). Running from
  the plugin root holds on every version, and also stops a planted
  `framework/registry/LAYER_REGISTRY.yaml` supplying the regexes the linter compiles over
  document text. Consequence to know: the hook always resolves the **bundled** registry.
- **The `$HOME` bound applies to the adoption marker only, not to the config lookup.**
  Bounding both made a project rooted at `$HOME` unable to turn the hook off.

**The `#385` in-prompt-hashing property still does NOT hold platform-wide** (#406 closed
only the plugin-SKILL and Hermes-reference halves). `agent-skills/**/SKILL.md` is reached
by no guard root and `sdd-orchestrator/SKILL.md:667` still hashes. A green run of that
guard is not evidence. The deeper finding — three successive hand-patches, each bounded by
whatever its author grepped for, each declared complete, each wrong — is why
`SDD-CORPUS-UNVERIFIED` audits instead of patching a fourth time.

**⚠️ `Hermes pytest` is RED on `main` and it is not this repo's regression.**
`pyproject.toml` declares `mcp[cli]>=1.0.0` — a floor with no ceiling — and
`hermes.yml:40` runs `pip install -e .`, so CI resolves to whatever the SDK last
published; a release renamed `Tool.inputSchema` → `input_schema` and collection dies at
`tool_registry.py:790`. **Not a required context, so it does not block merges.**
`HERMES-MCP-FLOATING-DEP` has the detail — do not re-diagnose it, and do not date it to a
version without measuring (local `mcp 1.22.0` still exposes `inputSchema`).

**⚠️ Two tiers are RED on `main` for pre-existing reasons, and neither is CI-gated.**
Both re-measured on 2026-07-31 by stashing a branch and re-running, so neither is
attributable to recent work:

- `tests/release/test_changelog_entry.py` — its `TBD` placeholder check scans the whole of
  `CHANGELOG.md` and matches a **quoted historical commit message** at `:1192`. It can
  never pass. `RELEASE-GATE-TBD-FALSE-POSITIVE`; **PR 5 cuts a release and is the first
  stage that hits it.**
- Phase 0 `lint-smoke` in `tests/scripts/test-acceptance.sh` — example-corpus debt,
  deferred to the wholesale regen. Use `--skip-lint-smoke` to reach later phases.

**V15 (schedule→`workflow_run` chain) is still unconfirmed** — never a gate; V14 proved
the chain off a *dispatched* upstream only. `standards-drift` runs Mondays 09:00 UTC,
first observable **2026-08-03**. **On or past that date**, check that a
`pin-currency-reader` run followed the latest `standards-drift` with `event=workflow_run`,
then delete this paragraph. A failure there is a new bug, not a reopened plan.

## Next tasks — prioritized

The full queue is `plans/FRAMEWORK-TODO.md` (`## Open`) and `plans/HERMES-BACKLOG.md`.
This is only the ordering a fresh session should use.

1. **PLUGIN-PREPROD-001 — implement PR 2 (linter dependency guards).** Read
   `plans/PLUGIN-PREPROD-001-PLAN.md` § "PR 2"; it carries a 57-row claim ledger with
   verified `file:line` and five recorded review passes.
   - Scope: guard `import yaml` in `tools/sdd_doc_lint/__init__.py` behind a **distinct
     exit code 3** with a diagnostic naming PyYAML (2 already carries usage-error *and*
     registry-unavailable), make the Python ≥3.11 floor explicit, add `--warn-exit`, and
     **re-vendor both mirrors** (plugin **and** Hermes) with
     `tools/sdd_doc_lint/sync-vendored.sh` — not `tools/sync-plugin-framework.sh`.
   - **PR 2 depends on PR 1 and must edit the hook's invocation line to pass
     `--warn-exit`** — the flag closes `L5` only if the hook passes it. That line has
     moved: it is now inside a multi-line `cd "$plugin_root" && …` block.
   - **Do not touch `platforms/hermes/VERSION`** (founder decision O2). A bump fans out to
     five files through a self-re-staging pre-commit hook and cannot be split back out.
     Log the change under Hermes' `[Unreleased]` instead.
   - Then PR 3 (saga driver — the only stage needing real design work), PR 4 (agent and
     manifest hygiene, independent of 2 and 3), PR 5 (docs, version bump, tag, Release —
     **founder-gated**).
   - **Do not re-derive the plan's rejected alternatives.** Three independent passes
     killed several obvious-looking fixes: removing the "dead" `--threshold` breaks the
     acceptance cascade at layer 1; disclosing the permission flag literally in a
     `SKILL.md` trips `tests/release/test_marketplace_gate.py:39`. Each is written up with
     its evidence in the plan.
   - **The plan's PR 5 section still says "add the README prerequisites section."** That
     shipped in PR 1, per the plan's own Modified table and Docs-to-update line. PR 5 must
     not re-add it.
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
3. **Watch [aidoc-flow-ci#351](https://github.com/vladm3105/aidoc-flow-ci/issues/351) —
   when canon ships its own reader, DELETE ours.** `.github/workflows/pin-currency-reader.yml`
   plus `scripts/read-pin-currency-log.sh` and `scripts/reconcile-pin-currency-issue.sh`
   are the "add a custom workflow" override mode, not a permanent local surface (plan
   R9). Nothing else in a live queue says so.
4. **[#405](https://github.com/vladm3105/aidoc-flow-framework/issues/405) —
   `sync-version-refs.sh` rewrites historical "shipped in vX" claims.** The
   `hermes/v<prev>` / `claude-code-plugin/v<prev>` fanout at `:347-355` is an unanchored
   global sed carrying neither of the two `HAZARD` notes the script already has (`:141`,
   `:209`). It corrupted `docs/PARITY.md:65` on **three consecutive bumps**.
   **PR 5 bumps the plugin version, so this fires next at PR 5** — the plan's mitigation
   is to hand-verify every surface rather than trust the script.
5. **[#386](https://github.com/vladm3105/aidoc-flow-framework/issues/386) — the
   framework-spec token gates five files on `CLAUDE.md`'s own state.** The mechanism and
   the hand-edit hazard are in `CLAUDE.md` § "Durable traps → Local hooks and tooling".
   Outstanding here is only the **fix shape**: #389 fixed the plugin and Hermes tokens by
   detecting each from `CLAUDE.md` and writing only `CLAUDE.md`, but this one cannot take
   that shape unchanged, because its `prev` is load-bearing elsewhere. Derive the gating
   `prev` from a fanout target nobody hand-edits (`docs/PARITY.md`), and give `CLAUDE.md`
   its own block.
6. **`doc-maintainer` — nothing to do; it is PAUSED** (`kill_switch: true`, #397) and CI
   is green. 23 failures / 47 runs across four upstream defects; census in D-0072 and
   `.github/doc-maintainer-conventions.md`. **Resume requires `aidoc-flow-ci` #352 AND
   #353** — #353 alone is 15 of the 23, so flipping on #352 alone returns a majority-red
   pilot. When both ship in a released `ci/vX.Y.Z`: re-pin, flip the switch, watch the
   next few `push` runs.

   ⚠️ **Do not re-file the `high_risk_paths` / `allowed_paths` mismatch as a defect.**
   It is deliberate, inert, and documented in the config itself; #396 recorded it as a
   bug and was wrong. D-0072 point 2 explains why the error message manufactures that
   misreading.
7. **Hermes parity — the residual arc.** `plans/HERMES-BACKLOG.md`: remaining
   plugin-vs-Hermes deltas plus quality-loop Phase 2 (cross-invocation resume / G-R1,
   the parallel-review global lock).
8. **Everything else** is in `FRAMEWORK-TODO.md` by tag (`[ci]`, `[lint]`, `[plugin]`,
   `[template]`, `[harness]`, `[example-corpus]`, `[docs]`, `[skill]`, `[sync]`,
   `[hermes]`). An entry under `## Open` with no `⏳ OPEN ON RESIDUAL` marker is genuinely
   open work (#403). Nothing there is blocking.

## Traps too fresh to have settled — not yet in `CLAUDE.md`

- **A version-boundary env var fails silently, so "I set it" is not "it took effect."**
  `PYTHONSAFEPATH` exists only on Python ≥3.11; below it the interpreter ignores it and
  the CWD is back on `sys.path`. The mitigation that holds everywhere is to run from a
  directory the attacker does not control.
- **`cmd 2>/dev/null` does not suppress a failing `<"$file"` redirection** — the *shell*
  reports that, before `cmd` exists. Redirect the whole group (`{ …; } 2>/dev/null`) or
  guard with `[ -f ] && [ -r ]`. A missing, unreadable, or FIFO path each leaked a
  diagnostic that broke the hook's JSON contract.
- **Do not test a script from a copy when its behavior depends on its own location.**
  `sdd-doc-review.sh` derives its plugin root from `BASH_SOURCE`, so a copy in a scratch
  dir resolves to the scratch dir and the linter is never found — every finding-related
  assertion then passes for the wrong reason. This produced a **false refutation** of a
  real defect that was only caught by re-running against the real file.
- **`check_plan.py` false-greens on a not-ready plan.** Its zero-findings check is a
  phrase match, and it accepted a Review log whose final pass said *"**Result:** NOT
  READY"* — because the surrounding prose contained "all folded". Canonical script is
  `~/.claude/skills/verified-planning/check_plan.py`; no repo-local copy. **Not filed.**
- **markdownlint silently corrupts claim-ledger citations.** Its autofix rewrites
  `__init__.py` → `**init**.py` in an unbackticked table cell, which broke **ten**
  citations at once and made the gate fail with the misleading `path '.py' does not
  exist`. Workaround in #408: `<!-- markdownlint-disable MD050 -->` scoped around the
  ledger. A trailing space **inside** inline code is likewise stripped by the whitespace
  hook. **Not filed.**

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
| "`--admin` is required on every PR" (the `ai-review` self-cancel, `aidoc-flow-ci#322`) | **Fixed at `ci/v2.16.0`.** #378, #380, #392, #394, #406 and #410 all reached mergeable with no `--admin` |
| "Branch protection requires the phantom `Lint / format / security hooks`, so every PR is BLOCKED" | **Fixed.** The six required contexts, re-read from the API on 2026-07-31, are `call / Lint / format / security hooks`, `call / composition`, `call / ai-review`, `call / verify`, `Framework + platform conformance`, `Acceptance tier (deterministic)`. `call / trust` and `Hermes pytest` are **not** required |
| `AIDOC-CI-COMPOSITION-CHECK-PRHEAD` — "`call / composition` is structurally unsatisfiable on a PR head" | **Stale.** composition reports success on PR heads. A reviewer once read this entry as proof that required checks gate nothing here, and it nearly killed a correct plan |
| "the acceptance deterministic tier has 3 pre-existing failures on `main`" | **Fixed** (#365, #371/#372). 0 failures / 64, and the tier is now a **required** context |
| Three pin-currency claims: `NO-PIN-CURRENCY-CHECK` ("this repo runs `check-pin-currency.sh` nowhere"), `PIN-CURRENCY-NO-READER` ("the fix **runs the script**"), and `PIN-CURRENCY-READER-PLAN.md:465`/`:469` ("the `clean` path is verified only by V4's stub") | **All three dead.** The check runs on every weekly `standards-drift` (the first was simply false — lesson in `CLAUDE.md` § "Durable traps → Process"); the reader SHIPPED at #392 and consumes the completed run's **log**, since running the script would be the second detector that same entry forbids; and V14 exercised close-on-clean for real |
| `plans/PLAN-*.md` as the governance-PR plan glob (`CHANGELOG.md`, `CI-CANON-V2.16-MIGRATION-PLAN.md:468`/`:784`) | **Fixed in `CLAUDE.md`** (#387/#390). The glob is a **suffix** — `plans/*-PLAN.md`. Merged plans and the CHANGELOG keep the old string as history; `CLAUDE.md` is the live rule |
