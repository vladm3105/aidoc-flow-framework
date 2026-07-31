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

**Traps live in `CLAUDE.md` § "Durable traps — do not re-derive these", not here.**
That section owns merging/CI mechanics, reading CI output, local hooks and tooling, the
acceptance harness, writing to GitHub from a script, and the process lessons — plus, in
§ "Unified CI", the `--repin` vs `--update` distinction, `LITELLM_BASE_URL`,
`secret-scan`'s history scope, `GITHUB_TOKEN`-triggered events, check-run rollup
semantics, the runner split, and the `#329` concurrency allowlist by *shape*. A trap
recorded there is **never** repeated here; this file carries only what has not settled
yet, and graduates it once it has.

## Where we are — 2026-07-31

Framework spec `0.40.0`, plugin `0.24.0`, Hermes `0.12.1`.
**Open PRs: 0. Open issues: 2** —
[#386](https://github.com/vladm3105/aidoc-flow-framework/issues/386) and
[#405](https://github.com/vladm3105/aidoc-flow-framework/issues/405).

**Last merge: [#408](https://github.com/vladm3105/aidoc-flow-framework/pull/408), squash
`bdac0a11` — `plans/PLUGIN-PREPROD-001-PLAN.md`. Plan only; no code shipped.**

**The founder intends to deploy the plugin. A five-lens pre-prod review of
`platforms/claude-code-plugin` returned BLOCKER, and the plan to clear it is now merged
and is task 1.** The packaging is sound and must not be disturbed — all suites green,
123/123 vendored files byte-identical, all 572 `${CLAUDE_PLUGIN_ROOT}` refs and 149
slash-command refs resolve. What blocks the deploy is runtime behavior on a stranger's
machine. **All four blockers were reproduced, not inferred:**

- **B1** — the review hook executes code from the user's CWD. `python3 -m` puts CWD ahead
  of `PYTHONPATH`, so a `sdd_doc_lint/` package in any cloned repo shadows the vendored
  one; the payload ran and the hook still exited 0. Fix is `PYTHONSAFEPATH=1` (verified);
  invoking `__main__.py` by absolute path does **not** work — relative-import failure.
- **B2** — 9 skills mandate a driver that spawns `claude --dangerously-skip-permissions`
  (`tools/saga_driver.py:398`), disclosed in **zero** shipped `.md`/`.json`.
- **B3** — the saga driver can wedge permanently and can report `PASS` on reviews whose
  lenses never ran.
- **B4** — PyYAML and Python ≥3.11 are undeclared; their absence exits 1, the same code
  the hook reads as findings, so a traceback is injected into model context labelled
  "Structural findings" on every edit.

Plus 3 HIGH — the hook fires in repos that never adopted the framework (the bundled
registry makes the documented "skip silently" path unreachable); the entire documented
`review_hook` on/off/verbose enum is **unwired**, so there is no way to turn the hook off;
and untrusted file content crosses into instruction context unframed.

**The `#385` in-prompt-hashing property still does NOT hold platform-wide** (#406 closed
only the plugin-SKILL and Hermes-reference halves). `agent-skills/**/SKILL.md` is reached
by no guard root and `sdd-orchestrator/SKILL.md:667` still hashes. A green run of that
guard is not evidence. The deeper finding — three successive hand-patches, each bounded by
whatever its author grepped for, each declared complete, each wrong — is why
`SDD-CORPUS-UNVERIFIED` audits instead of patching a fourth time.

**⚠️ `Hermes pytest` is RED on `main` and it is not this repo's regression.**
`pyproject.toml` declares `mcp[cli]>=1.0.0` — a floor with no ceiling — and
`hermes.yml:40` runs `pip install -e .`, so CI resolves to whatever the SDK last
published. A release renamed `Tool.inputSchema` → `input_schema`; collection dies at
`tool_registry.py:790`. **It is not a required context, so it does not block merges** —
PR #406 merged over it by founder direction. Captured as `HERMES-MCP-FLOATING-DEP`. Do not
re-diagnose it from scratch, and do not date it to a version without measuring: local
`mcp 1.22.0` still exposes `inputSchema`, so the rename postdates 1.22.0.

**V15 (schedule→`workflow_run` chain) is still unconfirmed** — it was never a gate; V14
proved the chain off a *dispatched* upstream only. `standards-drift` runs Mondays at
09:00 UTC, first observable **2026-08-03**. **If today is on or past that date**, read
the latest `standards-drift` run and check a `pin-currency-reader` run followed it with
`event=workflow_run`, then delete this paragraph. A failure there is a new bug against
the merged workflow, not a reopening of the plan.

**`doc-maintainer` is PAUSED and CI is green** (`kill_switch: true`, #397). 23 failures /
47 runs across four upstream defects; census in D-0072 and
`.github/doc-maintainer-conventions.md`. **Resume requires ci#352 AND ci#353** — #353
alone is 15 of the 23, so flipping on #352 alone returns a majority-red pilot.

## Next tasks — prioritized

The full queue is `plans/FRAMEWORK-TODO.md` (`## Open`) and `plans/HERMES-BACKLOG.md`.
This is only the ordering a fresh session should use.

1. **PLUGIN-PREPROD-001 — implement PR 1 (hook hardening). The plan is merged, reviewed
   to convergence, and actionable with no further discovery.** Read
   `plans/PLUGIN-PREPROD-001-PLAN.md`; it carries a 57-row claim ledger with verified
   `file:line` for every assertion, and five review passes recorded.
   - **Five staged PRs**, ordered by risk: (1) hook hardening — B1, B4-hook-half, H1, H2,
     H3, M1, L4, L5-visible-half; (2) linter dependency guards + re-vendor **both**
     mirrors; (3) saga driver — B2, B3a/b/c, M3, M4, M5, L2, L3; (4) agent/manifest
     hygiene; (5) docs, version bump, tag, Release. **PR 2 depends on PR 1**; PRs 1 and 4
     are independent; PR 5 is last and its tag + GitHub Release are **founder-gated**.
   - **PR 1 also creates one `FRAMEWORK-TODO.md` entry per finding** (23 findings:
     B1–B4, H1–H3, M1–M8, L1–L7, P1) — they do not exist yet. PR 5 closes them.
   - Founder decisions already taken and recorded in the plan: full scope · fix the
     driver in place behind an opt-in flag · staged PRs · **O1** ship the flag with **no**
     config key · **O2** skip the Hermes version bump, accepting that Hermes ships a
     behavior change with no version signal.
   - **Do not re-derive the plan's rejected alternatives.** Three independent passes
     (13, 10 and 10 load-bearing findings) killed several obvious-looking fixes: removing
     the "dead" `--threshold` flag breaks the acceptance cascade at layer 1; gating the
     hook on `.aidoc/` disables the feature on the plugin's own greenfield path; filtering
     the linter through a pipeline inverts `$?` to grep's status; disclosing the
     permission flag literally in a `SKILL.md` trips a release gate. Each is written up
     with its evidence in the plan.
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
     mechanically instead of a human guessing at its bounds. The TODO entry carries the
     assertions and the five known instances to fold in (`SKILL.md:667`, the `:1183`
     regex gap, the 4th guard root, 3 files / 4 stale imports, `hash4()`'s arity).
   - Non-trivial → needs a `plans/` plan with the two-cycle gap review.
3. **Watch [aidoc-flow-ci#351](https://github.com/vladm3105/aidoc-flow-ci/issues/351) —
   when canon ships its own reader, DELETE ours.** `.github/workflows/pin-currency-reader.yml`
   plus `scripts/read-pin-currency-log.sh` and `scripts/reconcile-pin-currency-issue.sh`
   are the "add a custom workflow" override mode, not a permanent local surface (plan
   R9). Nothing else in a live queue says so — the statement otherwise survives only
   inside the merged plan, which is why it is here.
4. **[#405](https://github.com/vladm3105/aidoc-flow-framework/issues/405) —
   `sync-version-refs.sh` rewrites historical "shipped in vX" claims.** The
   `hermes/v<prev>` / `claude-code-plugin/v<prev>` fanout at `:347-355` is an unanchored
   global sed carrying neither of the two `HAZARD` notes the script already has (`:141`,
   `:209`). It corrupted `docs/PARITY.md:65` on **three consecutive bumps**; #406 fixed
   that instance by rewording, not the class. `docs/PARITY.md:43` is latent behind it.
   Fix shape: anchor the replace (the `$ cat VERSION` awk block at `:367` is the model)
   or fail when a bump would rewrite more occurrences than the known current-state rows.
5. **[#386](https://github.com/vladm3105/aidoc-flow-framework/issues/386) — the
   framework-spec token gates five files on `CLAUDE.md`'s own state.** The mechanism
   and the hand-edit hazard are in `CLAUDE.md` § "Durable traps → Local hooks and
   tooling"; do not restate them here. Outstanding here is only the **fix shape**:
   #389 fixed the plugin and Hermes tokens by detecting each from `CLAUDE.md` and
   writing only `CLAUDE.md`, but this one cannot take that shape unchanged, because
   its `prev` is load-bearing elsewhere. Derive the gating `prev` from a fanout target
   nobody hand-edits (`docs/PARITY.md`), and give `CLAUDE.md` its own block.
6. **`doc-maintainer` — nothing to do; it is paused and waiting on upstream.** Watch
   `aidoc-flow-ci` #352 and #353. When **both** ship in a released `ci/vX.Y.Z`: re-pin,
   flip `kill_switch` → `false`, watch the next few `push` runs.

   ⚠️ **Do not re-file the `high_risk_paths` / `allowed_paths` mismatch as a defect.**
   It is deliberate, inert, and documented in the config itself; #396 recorded it as a
   bug and was wrong. D-0072 point 2 explains why the error message manufactures that
   misreading.
7. **Hermes parity — the residual arc.** `plans/HERMES-BACKLOG.md`: remaining
   plugin-vs-Hermes deltas plus quality-loop Phase 2 (cross-invocation resume / G-R1,
   the parallel-review global lock).
8. **Everything else** is in `FRAMEWORK-TODO.md` by tag (`[ci]`, `[lint]`, `[template]`,
   `[harness]`, `[example-corpus]`, `[docs]`, `[skill]`, `[sync]`, `[hermes]`), including
   the D54 and Engramory consumer-feedback batches. An entry under `## Open` with no
   `⏳ OPEN ON RESIDUAL` marker is genuinely open work (#403). Nothing there is blocking.

**Two planning-tool defects found 2026-07-31, not yet filed** (both hit while
authoring PR #408 — neither is in `CLAUDE.md` yet because neither has settled):

- **`check_plan.py` false-greens on a not-ready plan.** Its zero-findings check is a
  phrase match, and it accepted a Review log whose final pass said, in terms,
  *"**Result:** NOT READY"* — because the surrounding prose contained "all folded". A gate
  that passes a plan declaring itself unready is worse than no gate. Canonical script is
  `~/.claude/skills/verified-planning/check_plan.py`; there is no repo-local copy.
- **markdownlint silently corrupts claim-ledger citations.** Its autofix rewrites
  `__init__.py` → `**init**.py` in an unbackticked table cell, which broke **ten**
  citations at once and made the gate fail with the misleading
  `path '.py' does not exist`. `CLAUDE.md` already records the corruption, not that it
  lands on ledgers. Workaround in #408: `<!-- markdownlint-disable MD050 -->` scoped
  around the ledger, and backtick dunder paths outside it. A trailing space **inside**
  inline code is likewise stripped by the whitespace hook — which silently changed a
  regex whose whole point was that trailing space.

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
| "`--admin` is required on every PR" (the `ai-review` self-cancel, `aidoc-flow-ci#322`) | **Fixed at `ci/v2.16.0`.** #378, #380, #392, #394 and #406 all reached mergeable with no `--admin` |
| "Branch protection requires the phantom `Lint / format / security hooks`, so every PR is BLOCKED" | **Fixed.** The six required contexts, re-read from the API on 2026-07-31, are `call / Lint / format / security hooks`, `call / composition`, `call / ai-review`, `call / verify`, `Framework + platform conformance`, `Acceptance tier (deterministic)`. `call / trust` and `Hermes pytest` are **not** required |
| `AIDOC-CI-COMPOSITION-CHECK-PRHEAD` — "`call / composition` is structurally unsatisfiable on a PR head" | **Stale.** composition reports success on PR heads. A reviewer once read this entry as proof that required checks gate nothing here, and it nearly killed a correct plan |
| "the acceptance deterministic tier has 3 pre-existing failures on `main`" | **Fixed** (#365, #371/#372). 0 failures / 64, and the tier is now a **required** context |
| `NO-PIN-CURRENCY-CHECK` — "this repo runs `check-pin-currency.sh` nowhere" | **Retracted, it was false** — the check runs on every weekly `standards-drift`. The generalised lesson is in `CLAUDE.md` § "Durable traps → Process" |
| `PIN-CURRENCY-NO-READER` — "the fix is a workflow that **runs the script** and opens an issue" | **Superseded and now SHIPPED** (#392). Running the script would be the second detector the same entry forbids; the reader consumes the completed run's **log** |
| `PIN-CURRENCY-READER-PLAN.md:465`/`:469` — "a live `clean` check is deliberately absent … the `clean` path is verified only by V4's stub" | **Overtaken by events.** Canon `main` and every caller here are both `ci/v2.16.0`, so a live run reports `clean` — V14 exercised close-on-clean for real. This is the stale row most likely to be hit, because task 2 above sends the next session into that same plan |
| `plans/PLAN-*.md` as the governance-PR plan glob (`CHANGELOG.md`, `CI-CANON-V2.16-MIGRATION-PLAN.md:468`/`:784`) | **Fixed in `CLAUDE.md`** (#387/#390). The glob is a **suffix** — `plans/*-PLAN.md`. Merged plans and the CHANGELOG keep the old string as history; `CLAUDE.md` is the live rule |
