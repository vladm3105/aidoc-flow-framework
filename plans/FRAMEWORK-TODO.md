# Framework TODO — Example-Driven Discovery Backlog

> Triage queue for framework inconsistencies / bugs / improvements
> discovered while driving the examples corpus (`examples/url-shortener/`)
> end-to-end. Per [[feedback_framework_todo_list]] and
> [[feedback_seed_examples_are_acceptance_tests]]: examples are the
> system-under-test; their friction is the framework's truth.
>
> **Rules:**
>
> - Append entries inline as discovered. No "later PR" — the entry IS
>   the capture moment.
> - Each entry: tag + one-line title + Context (link to commit/PR/plan
>   that surfaced it) + Fix shape (one-line description of what would
>   resolve it). ≤ 3 lines per entry.
> - Tags: `[lint]` / `[harness]` / `[skill]` / `[template]` / `[sync]` /
>   `[plan-review]` / `[docs]` / `[hermes-parity]` / `[example-corpus]` /
>   `[ci]` / `[hermes]` / `[plugin]`. The last three were added by use before
>   they were declared here; a new tag belongs in this list when it is coined.
> - Once an item is large enough to design, promote to a formal plan
>   and link from the TODO entry as `→ <NAME>-PLAN.md`. The TODO entry
>   stays open until the plan ships, then moves to **Closed** with the
>   merge-commit ref.
> - Don't double-track. If a plan already exists, cross-reference it
>   instead of creating a new entry.
> - **State an entry's status in its HEADING. Two markers, and they are
>   the whole vocabulary:**
>   - `— ✅ CLOSED (YYYY-MM-DD, <ref>)` — done. Lives under **Closed**.
>     Give the strongest ref you have (PR + merge SHA; else a spec
>     version, decision id, or plan name) — but never a `TBD`
>     placeholder. Older entries carry date-only parens; that is
>     tolerated where the ref was never recorded, not a form to copy.
>   - `— ⏳ OPEN ON RESIDUAL (<what shipped; what is left>)` — the bulk
>     shipped but a named leg is still live. Stays under **Open**,
>     because the residual is the work.
>
>   Every entry under **Closed** carries the first marker. Every entry
>   under **Open** carries the second or neither.
> - **Both halves are load-bearing, and each fails differently.** A
>   resolved entry left under **Open** *overstates* the queue; an entry
>   under **Closed** whose heading lacks the marker *hides* work, because
>   this file is skimmed by heading — a `*Resolution:*` line 15 lines
>   down is not read. The second is the worse failure, and it is the one
>   that went unnoticed longest.
> - **A body-level `*Status:*` line closes nothing — it is unswept
>   residue, and it is the trap.** Entries that predate this convention
>   declare their state in the body instead. **Do not pattern-match the
>   wording.** The shapes vary (`SHIPPED`, `CORE SHIPPED`, `CORE
>   SUBSUMED`, `DOC LEG ✅ SHIPPED, enforcement leg deferred`,
>   `Closed by …`) and the deferral that keeps an entry open is often a
>   trailing clause on an otherwise finished-looking line — `SHIPPED (…)
>   … Deferred: …` reads as done until the last sentence. **Read the
>   whole body, then choose a heading marker.** Closing a partial entry
>   is the failure that hides work, and skimming afterwards will not
>   recover it.

## Open

### `[plugin]` `PREPROD-L7-BARE-DISPATCH` — the plugin dispatches its agents by bare name, so a consumer's same-named agent wins → #417

- *Context:* found 2026-08-01 by security review during PLUGIN-PREPROD-001 PR 4,
  and **pre-existing**. Plugin agents register under a scoped identifier
  (`aidoc-flow:code-reviewer`), so no definition is overwritten — but Claude Code
  resolves a **bare** name by scope precedence, and a plugin's `agents/` is the
  lowest of five (managed 1, `--agents` 2, `.claude/agents/` 3,
  `~/.claude/agents/` 4, plugin 5); the higher-priority location wins. Every
  dispatch reference this plugin ships is bare: `agents/pm-orchestrator.md:55`
  (the delegation table of the one agent holding `Task`),
  `skills/review-team/SKILL.md:60-71` (the lens → agent map), the same block in
  the eight `doc-*-audit` skills, and `skills/doc-brd/SKILL.md:176`
  (`subagent_type=requirements-analyst`) — 28 `subagent_type=` occurrences across
  `skills/`.
- *Impact:* a consumer who defines `code-reviewer` at any higher scope has the
  plugin's read-only gate silently replaced by their own agent, which may hold
  `Write`/`Edit`. `docs/AGENTS.md:32` states read-only as a security property, and
  it is defeated with no error, warning, or log line.
- *Fix shape:* namespace the dispatch **references**, not the definitions —
  `` `code-reviewer` `` → `` `aidoc-flow:code-reviewer` `` across the delegation
  and lens tables. Touches no agent filename, so it churns neither the
  `tests/scripts/test-acceptance.sh:1719,2171` expectation strings nor the other
  surfaces a rename would. **Verify first that `subagent_type` accepts the scoped
  form**; the docs confirm it for `--agent` and @-mention and show scoped
  identifiers (`my-plugin:review:security`), but do not state it for
  `subagent_type`. If it does not, renaming the definitions is the only fix left
  and this reopens as a rename.
- *Not broken:* installation does not shadow or overwrite a consumer's agent, and
  PR 4's `docs/AGENTS.md` §"Naming" documents the hazard for a human reader. This
  entry is the machine-facing half.
- *Stage:* after PLUGIN-PREPROD-001; not a release blocker for the `0.25.0` cut.

### `[plugin]` `PREPROD-AGENT-WEBFETCH` — `WebFetch` is granted to 9 of 11 agents and used by no workflow

- *Context:* found 2026-08-01 by security review during PLUGIN-PREPROD-001 PR 4.
  `WebFetch` appears in 9 of 11 `agents/*.md` frontmatters and in **zero** skill
  or agent bodies — no shipped workflow instructs any agent to fetch a URL. For
  document-authoring agents whose inputs are a local template plus a local seed
  file it is surplus, and it is the canonical prompt-injection exfiltration
  primitive: an agent reading an attacker-supplied requirements document can be
  induced to fetch `https://evil/?d=<secret>`.
- *Fix shape:* drop `WebFetch` from the agents with no fetching workflow. Note
  the counter-argument that keeps this LOW rather than MEDIUM — those agents also
  hold `Bash`, so `curl` remains reachable; removing `WebFetch` narrows the
  easiest path, not the only one. A real fix pairs it with the `Bash` question.
- *Stage:* unscheduled.

### `[docs]` `PREPROD-PLAN-TESTPATH` — the PR 4 plan's file table names a path that does not exist

- *Context:* `plans/PLUGIN-PREPROD-001-PLAN.md:326` names
  `tests/conformance/test_agent_frontmatter.py`; it shipped at
  `tests/conformance/platforms/test_agent_frontmatter.py`, beside the 18 other
  plugin-platform checks. The `platforms/` placement is correct — the adjacent
  `:325` row (`test_plugin_hook_safety.py`, PR 1) is the one that is arguably
  misplaced. Not fixed in PR 4 because editing a `plans/*-PLAN.md` makes it a
  governance PR under the ≤3-doc-surface rule.
- *Fix shape:* amend `:326` during PR 5, which closes the plan out anyway.
- *Stage:* PR 5.

### `[plugin]` `SAGA-ALL-BRANCHES-FAILED-CLOSES` — a review where every lens failed still closes at exit 0

- *Context:* found 2026-08-01 by review during PLUGIN-PREPROD-001 PR 3, and
  **pre-existing** — not introduced by that PR, though B3b makes it more
  reachable by preserving the subprocess's real state.
  `tools/saga_driver.py` `reconcile_post_audit` counts `BRANCH_FAILED` as
  terminal-and-fine (`terminal_branch_states = {"BRANCH_COMPLETED",
  "BRANCH_FAILED"}`), so a run whose crew all failed walks `FANOUT_STARTED →
  BRANCH_RUNNING → BRANCH_COMPLETED` **legally**. A `PASS` verdict then closes
  it via the ordinary chain — PR 3's forced-edge guard does not catch this,
  because no edge is forced. Reachable in practice: `validate_and_repair_branches`
  fabricates `BRANCH_FAILED` for every persona with no slot file, which is what
  an audit that writes `verdict.json` but dies before stamping branches leaves.
- *Fix shape:* gate the run-level walk on `BRANCH_COMPLETED` only, or escalate
  when any branch is `BRANCH_FAILED`. Needs a decision on what a partially-failed
  crew means for quorum (`REVIEW_TEAM.md` §Resilience already defines
  `coverage.quorum_met`, which the driver never reads) — so it is a design
  question, not a one-liner, and deliberately out of PR 3's scope.

### `[plugin]` `SAGA-DRAFT-HARDCODED-FROM-STATE` — the draft branch journals a `from` state it never checked

- *Context:* found 2026-08-01 during PLUGIN-PREPROD-001 PR 3.
  `tools/saga_driver.py` `_advance_after_phase` stamps
  `append_transition(from_state="PREPARED", to_state="FANOUT_STARTED")` for the
  draft phase regardless of the saga's actual status, then overwrites
  `saga["status"]`. Latent while the draft subprocess leaves `saga.json` alone
  (it does today — journal writes belong to the audit skill), but B3b now
  preserves whatever the child wrote, so a draft skill that ever touches the
  journal would have its state silently replaced and the transition recorded
  with a `from` that was never true.
- *Fix shape:* read `saga["status"]` like the other branches do, and treat an
  unexpected state as the inconsistency it is rather than overwriting it.

### `[plugin]` `PREPROD-B2-GATE-SCOPE` — the no-bypass release gate matches a literal string, and skips `commands/` + `agents/`

- *Context:* found 2026-08-01 by security review of PLUGIN-PREPROD-001 PR 3.
  `tests/release/test_marketplace_gate.py:39` asserts the absence of the literal
  `--dangerously-skip-permissions` in `SKILL.md` files. PR 3 moved the bypass
  behind `--allow-skip-permissions`, which the gate does not match — the
  semantic invariant is still covered (conformance
  `test_bypass_absent_by_default` + `test_flag_defaults_off` assert the driver
  ships it off, `test_driver_invocation_passes_the_permission_flag` asserts which
  skills opt in), but the gate itself no longer measures it. Separately
  `skill_dirs()` (`tests/conformance/_spec.py:90`) scans `skills/` only, so a
  `commands/` or `agents/` surface that enabled a bypass would be outside both.
- *Fix shape:* have the gate assert the property rather than the spelling —
  any surface naming a bypass flag must be on a declared allowlist and carry an
  in-file disclosure — and extend the scan to `commands/` and `agents/`.
  **Not done in PR 3:** the plan forbids amending that gate, and PR 5 cuts the
  release off it.

### `[plugin]` `PLUGIN-PREPROD-001` — the pre-prod review queue (23 findings, one entry each below)

- *Context:* a five-lens pre-production review of `platforms/claude-code-plugin`
  on 2026-07-31 returned **BLOCKER**. Every blocker and HIGH was reproduced
  against source before it survived into the verdict. The packaging is sound;
  what blocks the deploy is runtime behavior on a stranger's machine. Plan:
  `plans/PLUGIN-PREPROD-001-PLAN.md` (merged, PR
  [#408](https://github.com/vladm3105/aidoc-flow-framework/pull/408)).
- *Why one entry per finding rather than one for the plan:* the plan ships as
  **five sequential PRs**, so a stall between stages must leave a readable queue.
  The 23 entries below are the queue; the plan is the design. PR 5 closes them.
- *Citations are to `d789651b`, the pre-PR-1 tree.* Several of the lines
  cited below are moved or deleted by PR 1 itself, which is what closing a
  finding means; each such citation says so.
- *Tag note:* `[plugin]` is new here — the documented tag list predates a
  platform with its own runtime surface. Plugin runtime and packaging items carry
  it; linter, harness and doc items keep their existing tags.

### `[plugin]` `PREPROD-B1` — the review hook executes code from the user's working directory

- *Context:* `hooks/sdd-doc-review.sh:43` (pre-PR-1) invokes the linter with `python3 -m`,
  which puts the CWD ahead of `PYTHONPATH`. A `sdd_doc_lint/` package in any
  cloned repo shadows the vendored one; reproduced — the payload ran and the hook
  still exited 0.
- *Fix shape:* `PYTHONSAFEPATH=1` on the invocation. Invoking `__main__.py` by
  absolute path is **not** an alternative — it fails the relative imports.
- *Stage:* PR 1.

### `[plugin]` `PREPROD-B2` — nine skills mandate a permission-model bypass disclosed in no shipped file

- *Context:* `tools/saga_driver.py:398` spawns child sessions with
  `--dangerously-skip-permissions`, and nine autopilot skills name the driver as
  the MANDATORY orchestration step (e.g.
  `skills/doc-brd-autopilot/SKILL.md:85`). Zero shipped `.md`/`.json` discloses it.
- *Fix shape:* make the bypass opt-in behind a flag the skills pass explicitly,
  and disclose it. A doc-only disclosure would strip the bypass from the plugin's
  primary path, since every invoker passes only `--layer`.
- *Stage:* PR 3. The literal flag string must not reach a `SKILL.md` —
  `tests/release/test_marketplace_gate.py:39` fails the release if it does.

### `[plugin]` `PREPROD-B3` — the saga driver can wedge permanently and can report PASS on reviews that never ran

- *Context:* three distinct sub-defects. **B3a** — an illegal transition raises
  (`saga_driver.py:305`) and `PARTIAL_TIMEOUT` is unreachable from
  `BRANCH_FAILED`/`BRANCH_COMPENSATING`/`SYNTHESIZED` (`:47`, `:48`, `:51`), so
  four call sites can wedge. **B3b** — `dispatch_phase` writes its stale
  in-memory dict back after the subprocess returns (`:406`), discarding
  transitions the child wrote. **B3c** — the resume filter ignores transition
  scope (`:370`).
- *Fix shape:* a forced-transition path plus write-ordering, not a redesign of
  the transition table. B3c must use `t.get("scope", "run")` — a bare `== "run"`
  fails the existing scope-less fixture (`tests/conformance/test_saga_driver_invariants.py:71`).
- *Stage:* PR 3.

### `[lint]` `PREPROD-B4` — PyYAML and Python ≥3.11 are undeclared, and their absence is reported as lint findings

- *Context:* `tools/sdd_doc_lint/__init__.py:30` imports `yaml` unguarded and
  `:27` requires `StrEnum` (3.11+). Either absence exits 1 — the same code the
  hook reads as structural findings — so a traceback is injected into model
  context labelled as a finding.
- *Fix shape:* a distinct exit code (3) plus a diagnostic naming the dependency,
  and a hook-side filter that forwards only lines matching the finding grammar.
- *Stage:* PR 1 (hook half) and PR 2 (linter half).

### `[plugin]` `PREPROD-H1` — the hook emits findings in repos that never adopted the framework

- *Context:* the plugin bundles a registry and `find_registry`
  (`tools/sdd_doc_lint/__init__.py:46`) falls back to the module's own location,
  so the documented "skip silently when there is no framework/" path is
  unreachable once installed.
- *Fix shape:* gate findings on an adoption marker — the scaffolded
  `<docs_root>/0N_<ARTIFACT>/` tree, or a project-local registry / `.aidoc/`
  found by walking up. Bound the walk at `$HOME`: a user-global
  `~/.aidoc/profile.yaml` is documented and would otherwise make every project
  under `$HOME` pass.
- *Stage:* PR 1.

### `[plugin]` `PREPROD-H2` — the documented `review_hook` on/off/verbose enum is unwired

- *Context:* `docs/CONFIG.md` documents three values controlling the hook
  (`review_hook:` in the schema block).
  The hook reads no config at all, so there is no way to turn it off.
- *Fix shape:* locate `.claude/aidoc-flow.config.yaml` by walking up from the
  edited file (not from the CWD) and honour the enum. Parse with `grep`/`sed` —
  the hook must keep working when Python or PyYAML is absent.
- *Stage:* PR 1. Note the default `on` becomes quieter than today's behavior,
  which is `verbose`.

### `[plugin]` `PREPROD-H3` — untrusted file content crosses into instruction context unframed

- *Context:* `hooks/sdd-doc-review.sh:45` (pre-PR-1) concatenates linter output
  onto an instruction string, and `:34` interpolates the filename. Finding messages quote
  raw tokens from the document (`tools/sdd_doc_lint/__init__.py:642`).
- *Fix shape:* an explicit `<untrusted-tool-output source="...">` envelope
  preceded by a sentence stating it is data, not instructions; the same framing
  for the filename.
- *Stage:* PR 1.

### `[plugin]` `PREPROD-M1` — the hook declares no timeout

- *Context:* `hooks/hooks.json` (pre-PR-1) declared a `PostToolUse` command with
  no `timeout`, so a hung linter hung the edit.
- *Fix shape:* `"timeout": 15` in `hooks.json`. **Not** a `timeout 10` wrapper —
  GNU `timeout` is absent on stock macOS, where the invocation returns 127.
- *Stage:* PR 1.

### `[plugin]` `PREPROD-M2` — one agent declares neither `tools:` nor `model:`

- *Context:* `agents/requirements-analyst.md:3` is the only one of 11, so it
  inherits every tool including `Write`, `Edit` and `Bash`.
- *Fix shape:* scope it to match its siblings; add a conformance test asserting
  every agent declares both.
- *Stage:* PR 4.

### `[plugin]` `PREPROD-M3` — the driver wraps the child in GNU `timeout`, absent on stock macOS

- *Context:* `tools/saga_driver.py:393`. On macOS the invocation returns 127 and
  the driver's subprocess half is dead.
- *Fix shape:* probe for it, or implement the bound in-process.
- *Stage:* PR 3.

### `[plugin]` `PREPROD-M4` — `main()` returns 0 regardless of terminal saga status

- *Context:* `tools/saga_driver.py:732`, and again at `:679` straight after the
  break circuit sets `PARTIAL_TIMEOUT`. Both return sites are the complete set.
- *Fix shape:* a meaningful exit code. `tests/scripts/test-acceptance.sh:1177`
  consumes it and records FAIL on non-zero, so the harness moves with it.
- *Stage:* PR 3.

### `[plugin]` `PREPROD-M5` — `verdict.json` is read with no freshness check and never unlinked

- *Context:* `tools/saga_driver.py:425`. A stale verdict from a prior run is
  indistinguishable from this run's.
- *Fix shape:* unlink before dispatch, or stamp and verify the run id. Coerce
  `int(... or 0)` before any score comparison.
- *Stage:* PR 3.

### `[docs]` `PREPROD-M6` — the latest GitHub Release is six versions stale

- *Context:* what a visitor to the repo sees first. Not a code defect.
- *Fix shape:* cut `claude-code-plugin/v0.25.0` and publish a Release.
- *Stage:* PR 5. **Founder-gated** — a tag cut and a public Release are
  outward-facing acts outside the AI auto-merge default.

### `[docs]` `PREPROD-M7` — `SECURITY.md` names a stale spec version and scanners CI does not run

- *Context:* `SECURITY.md:11` says `0.35.x`; `:49` names `bandit`. CI runs
  semgrep, osv-scanner, gitleaks, `trivy config` and CodeQL.
- *Fix shape:* correct both to what is true.
- *Stage:* PR 5.

### `[docs]` `PREPROD-M8` — `ROADMAP.md` states a stale plugin version

- *Context:* `ROADMAP.md:56` says `0.23.4`.
- *Fix shape:* correct it with the PR 5 bump.
- *Stage:* PR 5.

### `[plugin]` `PREPROD-L1` — the plugin declares MIT and ships no license text

- *Context:* `.claude-plugin/plugin.json:10` declares `"license": "MIT"`; the
  installed artifact contains no `LICENSE`.
- *Fix shape:* add `platforms/claude-code-plugin/LICENSE`.
- *Stage:* PR 4.

### `[plugin]` `PREPROD-L2` — `--threshold` is accepted and ignored

- *Context:* `tools/saga_driver.py:644` declares it; nothing reads it as a gate.
  `CHANGELOG.md:1125` already claims the removal shipped — for the driver it
  never did.
- *Fix shape:* honour it. **Do not remove the flag** —
  `tests/scripts/test-acceptance.sh:1175` passes `--threshold 90` on every
  cascade layer, so deleting the argparse entry makes the driver exit 2 on a
  usage error before any saga work.
- *Stage:* PR 3.

### `[plugin]` `PREPROD-L3` — `playbook_loader` joins caller-supplied segments with no traversal guard

- *Context:* `tools/playbook_loader.py:18` `resolve_playbook_path`.
- *Fix shape:* resolve and assert containment under the playbook root.
- *Stage:* PR 3.

### `[plugin]` `PREPROD-L4` — the hook's layer path test hardcodes `/docs/`

- *Context:* `hooks/sdd-doc-review.sh:21` (pre-PR-1), defeating the configurable
  `docs_root` (`docs/CONFIG.md:47`, documented with a trailing slash and
  possibly multi-segment).
- *Fix shape:* substitute the configured value, normalizing the trailing slash
  and escaping regex metacharacters first.
- *Stage:* PR 1.

### `[lint]` `PREPROD-L5` — warning-severity findings can never reach the hook

- *Context:* `tools/sdd_doc_lint/__main__.py:118` exits 0 unless a finding is
  `error`, and the hook acts only on exit 1.
- *Fix shape:* a `--warn-exit` flag — which closes nothing unless the hook passes
  it, so the hook's invocation line moves in the same PR.
- *Stage:* PR 2 (depends on PR 1).

### `[docs]` `PREPROD-L6` — `marketplace.json` ships a personal email

- *Context:* `.claude-plugin/marketplace.json:6`, on a public manifest.
- *Fix shape:* a role address, if the founder wants it off the manifest.
- *Stage:* PR 4.

### `[plugin]` `PREPROD-L7` — `agents/code-reviewer.md` can collide with a consumer's own agent

- *Context:* a generic name in a namespace the consumer shares.
- *Fix shape:* rename under the plugin's namespace, or document the collision.
- *Stage:* PR 4.

### `[plugin]` `PREPROD-P1` — unreproduced `jq: Argument list too long` from the hook

- *Context:* reported, never reproduced. The mechanism would be an unbounded
  findings block reaching `jq`.
- *Fix shape:* closed by construction — a file-size cap and a byte budget on the
  findings block remove the mechanism.
- *Stage:* PR 1.

### `[harness]` `RELEASE-GATE-TBD-FALSE-POSITIVE` — the release changelog gate is red on `main` and will block the PLUGIN-PREPROD release cut

- *Context:* found 2026-07-31 running `tests/release/` for PLUGIN-PREPROD-001
  PR 1. `tests/release/test_changelog_entry.py:45` asserts the literal `TBD` is
  absent from the whole of `CHANGELOG.md`. It appears at `CHANGELOG.md:1192` —
  inside a *quoted historical commit message* that records a past review fixing a
  TBD placeholder. Confirmed pre-existing: red on `main` with this branch stashed.
- *Why it matters:* the tier is run by no workflow and no hook, so nothing
  surfaced it; PLUGIN-PREPROD-001 PR 5 cuts a release and is the first thing that
  will hit it. A placeholder check that scans an append-only historical record
  gets strictly more false positives over time.
- *Fix shape:* scope the assertion to the `[Unreleased]` section, or to lines
  that are not inside a quotation — not by deleting the historical text.

### `[lint]` `LINT-TRACE-RES-SINGLE-FILE` — linting one file reports every cross-document trace tag as an ERROR → [#412](https://github.com/vladm3105/aidoc-flow-framework/issues/412)

- *Context:* found 2026-07-31 by review during PLUGIN-PREPROD-001 PR 2, in the
  plugin's own `verbose` hook path. `_check_trace_resolution`
  (`tools/sdd_doc_lint/__init__.py:1782`) resolves `@<layer>:` tags against
  `doc_index`, which is built from **the paths passed on this invocation**. Lint
  one file and every upstream tag it emits is unresolvable by construction:
  `python3 -m sdd_doc_lint examples/url-shortener/docs/06_SPEC/SPEC-01.md` yields
  **66** `TRACE-RES-001` ERRORs — `references unknown document (no corpus member
  has doc_id 'ADR-01')` while `docs/05_ADR/ADR-01.md` sits right there — against
  **0** for `…/docs`. Every layer-02..08 document in the shipped corpus behaves
  the same.
- *Blast radius:* the review hook lints exactly one file (the edited one) and
  forwards up to 4000 bytes of findings into model context on every edit of an
  adopted project in `verbose` mode. That budget is spent almost entirely on
  false ERRORs, and `--warn-exit` (PR 2) does not cause this — the exit code was
  already 1. Also reached by any consumer linting a single path.
- *Fix shape:* gate `TRACE-RES-001`'s cross-document arm on a whole-corpus run,
  the way `_check_forward_coverage` already gates itself
  (`__init__.py:1961-1963` returns `[]` when the corpus has no SPEC or IPLAN,
  "which also covers the single-file `on_author` case"). Same idea, applied to
  the tag resolver: an unresolvable tag is only evidence of a defect when the
  corpus was whole. NOT in PLUGIN-PREPROD-001's scope — a linter-semantics
  change with its own design, deliberately not folded into a dependency-guard PR.

### `[lint]` `LINT-FINDING-MESSAGES-UNBOUNDED` — finding messages interpolate unbounded document-controlled text, and the hook forwards them to the model

- *Context:* found 2026-07-31 by security review during PLUGIN-PREPROD-001 PR 2.
  `STY02` interpolates the raw section heading
  (`tools/sdd_doc_lint/__init__.py:571-576`; `_SECTION_HEADING` at `:267`
  captures the whole rest of the line), and `PROV01` the raw `id_state`
  frontmatter value (`:645-650`). Both are bounded only by the hook's 1 MiB file
  gate. Demonstrated: a BRD with a ~7 KB hostile heading fills the hook's entire
  4000-byte findings budget with attacker-chosen prose inside
  `<untrusted-tool-output>`.
- *Not a PR 2 regression, but PR 2 widened it.* Such a document reached the model
  before only if it also carried an ERROR; `--warn-exit` makes warnings-only
  documents (largely BRDs) reachable too. **Envelope integrity holds either way**
  — `tr -d '<>'` plus the line-anchored grammar filter were verified against a
  multi-line breakout attempt, and only the first line survived. What is
  unbounded is plain prose inside a correctly-formed envelope.
- *Fix shape:* truncate at the source — `heading[:80]` in the `STY02` message and
  the same for `PROV01` — so the bound holds for every consumer (CI logs and
  pre-commit too), not only the hook. The finding stays actionable: the line
  number and word count carry it. Deferred deliberately: it moves linter output,
  so it needs a blast-radius pass over `tests/acceptance/expected_warnings/`
  and the golden fixtures first.
- *Also here, same class, latent:* `STALE01` interpolates raw `last_audited_spec`
  (`:1294-1299`) but is **unreachable through the plugin today only by accident**
  — `_framework_version` (`:1239-1246`) reads `registry.parent.parent/VERSION`
  and `platforms/claude-code-plugin/framework/VERSION` does not exist. A future
  sync that adds that file makes it reachable with nothing to notice.

### `[lint]` `LINT-LOCAL-REGISTRY-NO-TEMPLATES` — a project-local registry without its layer templates silently disables the structural checks

- *Context:* found 2026-07-31 while building
  `tests/conformance/test_plugin_hook_safety.py`. `find_registry`
  (`tools/sdd_doc_lint/__init__.py:46`) resolves the **nearest** registry by
  walking up from the CWD, and each layer's required sections are then read from
  a template resolved relative to that registry. A project that vendors
  `framework/registry/LAYER_REGISTRY.yaml` alone therefore lints to **zero
  findings** — measured: the same `BRD-01.md` that yields
  `[ERROR STRUCT01] missing required section` against the bundled registry yields
  `no structural findings` against a lone copied one, exit 0.
- *Why it matters:* the failure is silent and green. A consumer who vendors part
  of the framework gets a linter that reports clean documents forever, and
  nothing says the templates are missing.
- *Scope after PLUGIN-PREPROD-001 PR 1:* the review hook is no longer exposed —
  it runs the linter from the plugin root, so it always resolves the bundled
  registry. This is now a defect of the linter's own CLI path only.
- *Fix shape:* fail loudly when a resolved registry's template directory is
  absent, rather than treating a missing template as "no required sections".
- *Tracker:* TODO-only for now — clears the issue bar (reproducible, concrete fix
  shape, user-visible), but it is one repo's linter and not on the PLUGIN-PREPROD
  critical path.

### `[hermes]` `HERMES-MCP-FLOATING-DEP` — `Hermes pytest` is red on an unpinned SDK floor, and a path filter hid it for days

- *Context:* surfaced 2026-07-31 on PR #406, which is the first PR to touch
  `platforms/hermes/**` since 2026-07-27 — the workflow is path-filtered, so the
  break sat unobserved. `pyproject.toml` declares `mcp[cli]>=1.0.0` (floor, no
  ceiling) and `.github/workflows/hermes.yml:40` runs `pip install -e .`, so CI
  resolves to whatever the SDK published last. A release renamed the `Tool` model's
  `inputSchema` field to `input_schema`, and collection dies at
  `src/mcp_server/tool_registry.py:790`:
  `AttributeError: 'Tool' object has no attribute 'inputSchema'`.
- *Blast radius is smaller than the raw grep suggests.* 36 hits, but **27 are
  constructor kwargs** (`inputSchema={`) which the traceback proves still work —
  `TOOLS` builds, and only the later attribute read fails. The real surface is **9
  attribute accesses**: `tool_registry.py:790` plus 8 in
  `tests/unit/test_server.py` (`:38-40`, `:44`, `:90`, `:95`, `:103`, `:107`).
- *Do not date this to a version without measuring.* Locally-installed `mcp
  1.22.0` still exposes `inputSchema` and has **no** `input_schema`, so the rename
  landed **after** 1.22.0 — CI resolved something newer. Check what CI actually
  installed before naming a version.
- *Fix shape:* a bare rename to `input_schema` breaks anyone on an older SDK,
  which the `>=1.0.0` floor explicitly still admits. Pin a floor that matches the
  attribute the code uses (or add a compat accessor), then update the 9 reads.
  Worth asking separately whether a path-filtered workflow is right for a package
  whose dependencies float — the filter is what turned a dependency break into a
  latent one.
- *Not blocking:* `Hermes pytest` is **not** a required context (required are
  conformance, `call / composition`, `call / Lint / format / security hooks`,
  `call / ai-review`, `call / verify`, `Acceptance tier (deterministic)`).
  Deferred by founder direction on 2026-07-31; captured here so it does not die
  with the session.
- *Tracker:* TODO-only pending founder direction — clears the issue bar
  (reproducible at `file:line`, concrete fix shape, breaks a consumer's test run)
  if it is picked up.

### `[skill]` `SDD-CORPUS-UNVERIFIED` — the sdd-orchestrator reference corpus ships runnable Python that nothing parses, executes, or checks

- *Context:* founder call, 2026-07-31, after #385's fix surfaced the fourth
  defect in this corpus in three remediation passes. A census of the
  sdd-orchestrator surfaces (excluding the vendored `governance/` mirror) found
  **45 fenced Python blocks: 3 do not parse, 10 carry unused imports, and 10 call
  a locally-defined function with too few positional arguments.** Roughly half the
  blocks carry a defect that a 20-line AST check finds in under a second.
  `sdd-orchestrator/SKILL.md:1155` points agents at these files for "the complete
  scripts," so this is live authoring guidance, not archive.
- *Why the remediation method is the defect, not the count.* #342 corrected 9
  reference files and declared the property closed; it missed a 10th, left 6
  files with stale `import hashlib`, and rewrote `hash4()`'s signature at
  `brd-validation-automation.md:21` without touching its call site at `:31`
  (3 positional params required, called with 1 — a runtime `TypeError`). #385
  then fixed the 10th, declared it closed, and missed
  `sdd-orchestrator/SKILL.md:667` plus 3 more import sites. Three passes, each
  bounded by whatever the author grepped for, each declared complete, each wrong.
  A fourth hand-patch would repeat it.
- *Nothing guards it.* `grep -rl agent-skills tests/ .github/workflows/
  .pre-commit-config.yaml` returns only markdown-lint, pre-commit formatting, and
  `test_no_inprompt_hashing.py` — a text-regex guard. **No test executes,
  imports, or AST-parses a single block.** That is why arity errors and dead
  imports survive indefinitely.
- *Fix shape — gate first, then remediate against it.* Build the mechanical check
  before touching content: extract every fenced block, assert it parses, has no
  undefined names, no unused imports, call arity matches local defs, and that
  `compute_element_hash` is called with 4 real arguments (4 of 8 call sites pass
  `""` as description or the description as title, so the IDs they mint would be
  rejected by `rehash --check`). The gate enumerates the work mechanically
  instead of a human guessing at its bounds, and makes "closed" mean something.
  Then fold in the known instances: `SKILL.md:667`; the `INSTRUCTION` regex gap
  (`:1183` says "first 4 **chars** of SHA256", which the regex misses — it only
  matches "**hex** of"); the 4th guard root for `agent-skills/**/SKILL.md`; the 3
  files / 4 sites of stale `import hashlib`; `hash4()`'s arity.
- *Founder decision needed first:* these files ship Python that has never run.
  Make it genuinely executable and tested, demote it to explicitly-marked
  non-runnable pseudocode, or extract it to real `.py` files under test. Today it
  is the worst of the three — it reads as authoritative, agents are told to copy
  it, and about half of it is wrong. The answer changes what the gate asserts, so
  it precedes the plan.
- *Also re-point on landing:* `CLAUDE.md`'s current-state line cites #385 for
  "one unscanned surface still hashes"; that clause should cite this entry once
  the root gap closes.
- *Tracker:* plan + issue to open once the design call above is made. Needs a
  `plans/` plan with the two-cycle gap review — it is a non-trivial change.

### `[sync]` `SYNC-HISTORICAL-REF-CORRUPTION` — the `hermes/v*` fanout has silently rewritten a "shipped in version X" claim on three consecutive bumps → [#405](https://github.com/vladm3105/aidoc-flow-framework/issues/405)

- *Context:* surfaced 2026-07-31 during the #385 fix, whose Hermes PATCH bump made
  the hook rewrite `docs/PARITY.md:65` from `hermes/v0.12.0` to `hermes/v0.12.1`.
  That line dates **when HERMES-REVIEW-LOOP-001 Phase 1 shipped**, which was
  `0.11.0` (`08e98968`, `platforms/hermes/CHANGELOG.md` `[0.11.0]`). `git log -L`
  shows it correct at authoring and rewritten by **every** bump since —
  `65a8936d` → `v0.11.1`, `a00f804e` → `v0.12.0`, and this one → `v0.12.1`. It has
  been wrong in published docs since 2026-07-11.
- *This is the already-documented hazard class, one literal short.*
  `scripts/sync-version-refs.sh:209` (FRWK-REVIEW-002 F1) warns that
  `replace_in_file` is a **global** sed that "cannot tell a current-state row from
  a historical/provenance mention," and `:141` repeats it for the `CLAUDE.md`
  tokens. Neither covers the `hermes/v<prev>` / `claude-code-plugin/v<prev>`
  literals swept across `README.md`, `docs/PARITY.md` and
  `platforms/hermes/README.md` at `:347-355` — which carry no warning and no
  anchor. `docs/PARITY.md:43` (`claude-code-plugin/v0.21.0`) is a latent second
  instance, unhit only because the plugin's previous version has never been
  `0.21.0` since.
- *Fix shape:* the hazard note's own remedy is to write historical mentions in a
  form the sed cannot match; PARITY:65 was corrected that way here (`the 0.11.0
  Hermes cycle`). That fixes the instance, not the class. The class needs either
  an anchored replace (as the `$ cat VERSION` awk block at `:367` already does)
  or a guard that fails when a bump would rewrite more occurrences than the
  known current-state rows. A conformance check that every `X/vN.N.N` literal in
  those three files is either the current version or provably historical would
  catch the next one.
- *Tracker:* filed as [#405](https://github.com/vladm3105/aidoc-flow-framework/issues/405).

### `[ci]` `PIN-CURRENCY-READER-HAS-NO-READER` — the reader is skipped exactly when the upstream run has already broken

- *Context:* filed 2026-07-31 from `plans/DECISIONS.md` D-0073 §3, which names
  this a **live open risk, not a solved problem**, and which
  `PIN-CURRENCY-NO-READER` deliberately left out of scope — so no queue held it
  until now. Two levels: generally, `pin-currency-reader.yml` feeds no required
  context and sits on no PR path, so its own red run is a red mark in the
  Actions tab of a workflow nobody watches — the same invisibility it exists to
  remove, one level up. Concretely, in the merged code,
  `.github/workflows/pin-currency-reader.yml:67` gates the read job on
  `${{ github.event_name == 'workflow_dispatch' || github.event.workflow_run.conclusion == 'success' }}`,
  so on a `workflow_run` event the first disjunct is false and an upstream
  `standards-drift` **failure skips the reader** — and a skipped job is green, so
  the pin verdict goes unread precisely when something else has already gone wrong.
- *Fix shape:* read on upstream `failure` too, and distinguish "the drift script
  never reached the pin-currency section" from "it ran and reported" — the
  terminal markers for that are in `CLAUDE.md` § "Durable traps → Reading CI
  output" (`check-standards-drift: coverage —`). **Keep the `workflow_dispatch`
  disjunct** when editing that condition: dropping it green-skips every manual
  dispatch, which is exactly what the comment above the line warns about.
  Routing a real failure somewhere
  with a reader is the separate, larger half. **Bounded by
  [aidoc-flow-ci#351](https://github.com/vladm3105/aidoc-flow-ci/issues/351):**
  this whole surface is an override that gets **deleted** when canon ships its
  own reader (plan R9), so invest here only if #351 stays open long enough to
  matter.

### `[docs]` `D-0071-JQ-NULL-CLAIM-CONTRADICTED` — a permanent decision entry states a failure mode `CLAUDE.md` re-measured and reversed

- *Context:* found 2026-07-31 during PR 3 review of `PIN-CURRENCY-NO-READER`.
  `plans/DECISIONS.md:300` (D-0071 §8) says `gh api …/contents/<missing>
  --jq '.name'` "emits the string `null`". `CLAUDE.md:732-736` says the opposite
  on a **2026-07-30 re-measurement**: it puts the full 404 JSON on stdout and is
  *not* the bare string `null` — which matters, because a guard written against
  the `null` form reads a missing file as **present**. Both are load-bearing
  statements of the same trap; a reader landing on the decision log first gets
  the falsified one.
- *Fix shape:* the decision log is append-only, so **do not edit D-0071**. Add a
  new dated entry recording the re-measurement and superseding §8's failure-text
  claim only (the §8 *lesson* — never truth-test a `jq` scalar that can be
  absent — stands unchanged). Fold into the next `DECISIONS.md` PR rather than
  spending one on it.
- *Tracker:* **TODO-only.** Purely local, no consumer affected, and no
  `file:line` outside this repo.

### `[sync]` `SYNC-FW-TOKEN-SELF-GATED` — the framework-spec fanout is gated on `CLAUDE.md`'s own token → [#386](https://github.com/vladm3105/aidoc-flow-framework/issues/386)

- *Context:* surfaced 2026-07-30 in PR #387, which made the plugin and Hermes
  `CLAUDE.md` tokens self-detecting and deliberately left this one alone.
  `sync-version-refs.sh:218` reads `fw_prev` from `CLAUDE.md` **and** uses it to
  gate propagation to `README.md`, `docs/PARITY.md`, both platform READMEs and
  the conformance-test literal — so correcting `CLAUDE.md` first strands five
  files, silently, exit 0. `plans/HANDOFF.md` already carries the workaround as
  folklore. SKILL frontmatter, playbooks and `platforms/*/FRAMEWORK_SPEC_VERSION`
  are **not** in the blast radius; each has its own detector.
- *Fix shape:* split detection from propagation — give `CLAUDE.md` its own
  self-detecting block, and derive the gating `fw_prev` from a fanout target the
  author is not hand-editing (`docs/PARITY.md` or the plugin README).

### `[harness]` `ACCEPTANCE-FIXTURE-WARNING-DEBT` — 13 distinct advisory findings pinned across the acceptance fixtures (30 manifest warnings / 27 entries)

- *Context:* deferred from `ACCEPTANCE-TIER-DRIFT-UNTRACKED` (2026-07-27). The
  fixtures carry 5 `REFGRAN01` (doc-level `@adr:`/`@tdd:` tags predating GD-03),
  4 `COV02` (elements realized by nothing) and 4 `ACC01` (BDD scenarios paired to
  no TDD test case). The three manifests hold **30 warnings across 27 entries** —
  the layer dirs reuse byte-identical goldens, so the 13 are the distinct debt.
  Pinned is
  not acceptable — each entry's `reason` names what would clear it.
- *Fix shape:* author the missing element-level citations and paired TDD test
  cases. Self-verifying: the match is bidirectional, so clearing a fixture fails
  the suite until its manifest entry is deleted.
- *Caveat:* the pinned set reflects **trace-graph visibility**, not total debt.
  `layer_06_spec/valid/SPEC-01_golden.yaml`,
  `layer_07_tdd/valid/TDD-01_golden.yaml` and
  `layer_08_iplan/valid/IPLAN-01_golden.yaml` each have one `---` and no
  `doc_id`, so they are invisible to the graph; adding a closing fence is a
  benign repair that ADDS findings and moves the manifest. (Three MORE share the
  shape under `fullpath/broken_chain/` — six in the tree; the three above are the
  ones inside `valid/` dirs that a manifest covers.)

### `[harness]` `IDCOORD-NUMERIC-SECTION-ID` — `_id_coordinator.element_id()` emits a string `section_id`, so its IDs can never be registry-valid

- *Context:* deferred out of `IDCOORD-SECOND-HASH-IMPL` as plan **D3 option (b)**
  (2026-07-26). `extract_elements()` derives `section_id` from a normalised
  heading (`"project_scope"`), so `element_id()` returns
  `BRD.01.project_scope.<hash>`, which the registry element pattern
  `^[A-Z]+\.\d{2,}\.\d{2,}\.[a-f0-9]{4,8}$` (`LAYER_REGISTRY.yaml:216`) rejects.
  The shipped fix documented the limitation (option c) rather than inventing a
  heading→ordinal mapping — a new contract, the same overreach GD-09 declined
  for TDD field extraction. Harmless today: the module has no product consumer.
- *Fix shape:* a per-layer heading→section-ordinal table, which does not exist
  anywhere in the repo. Only worth building if cross-layer ID-closure testing is
  actually wired up (the other, still-unactioned half of
  `PLUGIN-TEST-SUITE-REVIEW.md:32` **F2**); until then the string form is
  honest about what it is.
- *Tracker:* **TODO-only** per the GD-10 three-test bar — fails (c) (no consumer
  is affected: the module has none) and is conditional on prerequisite work
  nobody has scheduled, i.e. the "already-planned / purely local" carve-out.

### `[example-corpus]` `SEED-ABSORPTION-001-T7` — 16 BDD scenarios are un-designed (SPEC-coverage gap), not merely un-tested

- *Context:* SEED-ABSORPTION-001 T7 (2026-07-24). New `ACC01` fires on the same
  16 orphan BDD scenarios as `COV02`. The T7 probe (dispatch `doc-tdd-audit`/
  `doc-tdd-fixer` against `examples/url-shortener/docs/07_TDD/`) is blocked
  **upstream**: `TDD-01.md:66` scopes itself to "the **15** Mapping-Store BDD
  scenarios (SPEC-01 §8)", the corpus has exactly **one** SPEC, and TDD's
  declared upstream includes `spec`. So the 16 orphans are un-**designed** — no
  SPEC specifies them — and the TDD skills cannot author paired test cases for
  scenarios no SPEC covers. Per `CLAUDE.md` "Never hand-edit example artifacts",
  the corpus was not touched; `test_coverage_engine.py:103` stays pinned at 16.
- *Fix shape:* the corpus is regenerated wholesale after framework changes
  (`CLAUDE.md`), so the real fix is a regen that either designs the other 16
  scenarios in SPEC (then TDD pairs them) or trims BDD-01 to the 15 that SPEC-01
  covers. This entry records the SPEC-coverage gap the T7 probe surfaced; it is
  not a hand-edit task.

### `[ci]` `LINKS-PLATFORM-DEBT` — pre-existing internal-link debt under `platforms/**` + `examples/**`

- Context: 2026-07-11, aidoc-flow-ci links-workflow population (ci/v1.9.4). A
  `lychee --offline` sweep of hand-maintained + generated docs found **248
  broken internal links**, ~245 of them clustered in
  `platforms/hermes/agent-skills/spec-driven-development/**` skill docs, plus a
  few durable-doc links pointing into `examples/url-shortener/**` (a
  regenerated system-under-test corpus that must never be hand-edited).
- Interim: the deployed `.lychee.toml` scopes the links gate to hand-maintained
  top-level docs via `exclude_path = ["platforms", "examples", "tests"]` (+ URL
  excludes for links pointing into them), so the gate is green on what's
  actually maintained. The excluded paths carry the debt.
- Fix shape: audit the `platforms/hermes/agent-skills/**` READMEs for the
  relocated/renamed targets (likely one systematic dir move); repair
  durable-doc → example links or confirm the example corpus regen resolves
  them. Then narrow the `.lychee.toml` excludes. Framework-domain remediation,
  NOT a CI change — example artifacts are fixed by regen, never by hand.

### `[docs]` `PREPROD-HYGIENE` — extend `test_spec_hygiene` `ENGINE_TOKENS` to guard `plugin`/`SKILL`/`doc-*`

- Context: pre-prod readiness audit (2026-07-11). The engine-token sweep in
  `REVIEW_SAGA.md` was completed by hand (3 leaks GD-06 missed), but
  `tests/conformance/test_spec_hygiene.py` `ENGINE_TOKENS` still omits
  `plugin`/`SKILL`/`doc-<layer>`, so a future leak of that class regresses unguarded.
- Fix shape: add those patterns to `ENGINE_TOKENS` **with an allowlist** for the
  GD-06-sanctioned `AIDOC.md` illustration (`framework/docs/AIDOC.md:96-103`) and the
  `governance/DECISIONS.md` GD-06 decision record (legitimate meta-content naming what
  it neutralized) — per GD-06:98-99's own note that the test "may later be extended to
  allow-list exactly the two sanctioned bindings."

### `[skill]` `SKILL-DEDUP-001` — ⏸ PARKED (2026-07-09, founder decision) — 36 per-layer skills share duplicated boilerplate

- Context: FRWK-REVIEW-002 skill-redundancy review. The 4 families × 9 layers
  share near-identical saga / break-circuit / adaptation / report-format blocks;
  PR-A fixed the drift *instances* but not the duplication *class*. Also would
  absorb A7 (cosmetic autopilot-wording normalization) and L16 (quality-advisor
  re-implements the audits' Structural-Checklist checks with no shared source).
- **Parked.** Drafted `→ SKILL-DEDUP-001-PLAN.md`; the **template-generation
  approach was rejected** by independent review — the per-layer skills are NOT
  ~96% boilerplate (chg-audit ≈60% identical to prd-audit; crew weights, lens
  maps, and layer-specific checklists genuinely differ), so whole-file generation
  can't reach byte-identity without the "template" degenerating into per-layer
  content. The motivating drift is already fixed (PR-A); this is now a
  maintainability-only concern, not a live problem. **Do not re-investigate the
  template-generation approach.** If revisited, the candidate is **shared-section
  extraction** (dedup only the ~90-line identical blocks into a shared reference
  the skills cite; trade-off: a runtime `Read` per invocation) — needs a fresh
  founder decision + redraft. See the plan's Review-log Pass 2 for the full
  measurement.

### `[skill]` `DEPRECATED-STUB-REMOVAL-V1` — remove `doc-review` / `trace-check` stubs at v1.0.0

- Context: FRWK-REVIEW-002 L15. The two deprecated redirect stubs (`replacement:
  doc-validator`) are correctly marked and scheduled for removal at the plugin
  v1.0.0 milestone; no action before then (review concluded no live dependencies).
- Fix shape: at the v1.0.0 cut, delete the two `skills/` dirs, drop them from the
  registry/README/marketplace counts, and update the "52 = 50 + 2" claims to 50.

**[docs] PLAN-003 §5.4c framework link-summary retrofit — deferred from Wave 1a**

- Context: Wave 1 PR (2026-07-08) closed the parser-gate `--check-governance`
  drift in `CLAUDE.md ## Per-repo governance` (added missing Roadmap required
  row + 3 additional rows + fixed Plans path). PLAN-003 §5.4c framework row
  also mandates the "path-with-summary" retrofit of the workspace-standards
  blocks (`## Governance PR discipline` / `## AI agent auto-merge default`
  / `## Multi-agent automated review`) per §4.2 H5 mechanism — replacing the
  ~150 lines of duplicated OPS-NNNN body content with concise pointer format.
- Fix shape: rewrite framework's 3 workspace-standards sections to match the
  path-with-summary format shown in `aidoc-flow-ci/CLAUDE.md` line 76-105
  (one-sentence summary + `→ ../operations/CLAUDE.md — search "OPS-NNNN"`).
  Follow-up PR; kept separate from Wave 1a to preserve Rule 1 ≤3 surfaces.

> **CONSUMER-FEEDBACK-001 progress (2026-06-27):** 3 consumer logs triaged → 22
> items (the 3 dated banners below), orchestrated by
> `plans/CONSUMER-FEEDBACK-001-PLAN.md`. **Closed:** `BL-TAG-CHAIN-GATE-SYNC`
> (#180/#181). **CFB-PR-2 coverage engine — SHIPPED (full arc):**
> `ENG-FWD-COVERAGE` forward gate `COV01` (#187, spec 0.24.0); `D54-F13`/`D54-F05`
> backward gate `COV02` (#190, 0.25.0); GD-03 ref-granularity policy (#192,
> 0.26.0); `BL-REF-GRANULARITY` + `D54-F07` enforcement `REFGRAN01` (#194,
> 0.27.0); **element-level `COV01`/`COV02` — SHIPPED** (ELEMENT-COVERAGE-001,
> spec 0.30.0; catches the 16 orphaned BDD scenarios).
>
> **Session-end status (2026-06-30, spec `0.32.6`) — P1 wave + the P3 cleanup arc
> shipped:** PR-4 `D54-F01-PROVISIONAL-IDS` (#212, 0.31.0) and PR-5
> `D54-F02-REUSE-MANIFEST` (#214, 0.32.0), the earlier P3 docs sweep (#215/#216/#217),
> then the **2026-06-30 arc**: `BL-READY-SCORE-ADVISORY` (#222, 0.32.4),
> `STRUCT01-INDEX-EXEMPTION` bugfix (#224, no bump, D-0043),
> `ENG-BRD-SKETCH-ROADMAP` (#226, 0.32.5, D-0044), the corpus-regen runbook (#227),
> and the **P3 docs sweep** (`INDEX-UPSTREAM-RESIDUE` + `ENG-PLATFORM-ADR-TIMING` +
> `D54-F12-AGENTIC-ANTIPATTERNS`, 0.32.6). **Remaining
> (next-session, see `plans/HANDOFF.md` ▶ RESUME HERE):** the wholesale **corpus
> regen** (run `plans/CORPUS-REGEN-RUNBOOK.md` on a live plugin CLI); Hermes parity
> (the large arc); the P2/P3 items still marked OPEN below (`D54-F04`, `IPLAN-LANG`,
> the D54/ENG P2s, etc.).
> **Subsumed / retired:** sub-PR 2c (`D54-F13` phase-leak) — part (a) is COV01;
> 2d (`D54-F05` BDD-rollup) — COV02 is already corpus-wide; the **corpus-side**
> remediation items (`CORPUS-REFGRAN-RECASCADE`, `CORPUS-PRD-TH-RES`, the 16 COV02
> orphans) are deferred to the wholesale corpus regen. (`INDEX-UPSTREAM-RESIDUE`
> was **template-side**, NOT corpus-side — shipped in the 0.32.6 sweep, not via regen.)
>
> **YAML-BDD-SCHEMA arc — CORE COMPLETE (2026-06-28):** migrated BDD off
> Gherkin-in-markdown to structured YAML `scenarios:` blocks. Plan #197 (D-0038,
> 3-pass). **Shipped:** PR-1 transcoder + `_THRESHOLD` fix (#198); PR-2
> `sdd_doc_lint` dual-mode parse path + `BDD-SCHEMA-001` (#200); PR-3 template +
> schema + GD-03/TAG_SYNTAX (framework `0.29.0`, #201); PR-4 corpus BDD-01
> migration (REFGRAN 7→5, #202); PR-5 `doc-bdd*` skills (plugin `0.23.0`, #203).
> **Remaining:** (a) **PR-3b** — SHIPPED (#206, `0.29.1`); (b) **element-level
> COV01/COV02 upgrade** — SHIPPED (ELEMENT-COVERAGE-001, `0.30.0`; the deferred
> payoff — catches the 16 orphaned BDD scenarios);
> (c) `CORPUS-REFGRAN-RECASCADE` (below) — now just the 5 SPEC/TDD/IPLAN edges.

### `[sync]` `SYNC-VERSION-PROVENANCE-OVERBUMP` — `sync-version-refs.sh` global-sed rewrites historical version refs

- *Context:* CFB-PR-2 2a-core step 6 (`a0cb426f`). The framework-spec bump
  `0.23.1 → 0.24.0` swept two HISTORICAL provenance lines in `docs/PARITY.md`
  (SAGA-PARITY-001 / D-0031 "arriving with framework spec 0.23.0") to 0.24.0 —
  `scripts/sync-version-refs.sh` does a global `sed s|<old>|<new>|g` for the
  framework-spec string, matching every occurrence, not just the current-state
  row. (It only matched because the current-state rows were themselves stale at
  0.23.0, so `fw_prev` resolved to 0.23.0.)
- *Fix shape:* anchor the framework-spec replacement to the documented
  current-state row only (drop the `/g`, or match the `claude-code-plugin/vX
  (framework spec …)` line specifically) so future bumps stop rewriting
  provenance. Restored the two lines by hand in `a0cb426f`.
- **RESOLVED (FRWK-REVIEW-002 PR-F, 2026-07-09).** The prior hand-restore in
  `a0cb426f` restored them to the wrong value (`0.23.0`, not the authored
  `0.13.0`). PR-F F1 restored both PARITY lines to `0.13.0` and made them
  sweep-proof by rephrasing to "`0.13.0` spec cycle" (no `framework spec \`X\``
  literal for the sed to match), and documented the hazard inline in
  `scripts/sync-version-refs.sh`. The`/g` behavior is left as-is; the
  convention (historical mentions avoid the literal) is the guard.

### `[example-corpus]` `CORPUS-REFGRAN-RECASCADE` — 5 SPEC/TDD/IPLAN doc-level `@adr`/`@tdd` tags need element-level re-cascade (REFGRAN01)

- *Context:* CFB-PR-3 shipped `REFGRAN01` (GD-03 enforcement). Originally **7**
  doc-level trace tags; **YAML-BDD-SCHEMA PR-4 (#202) resolved the 2 BDD edges**
  (`BDD-01:31,55`) by migrating BDD-01 to YAML `ears:` lists. **5 remain** (all
  non-BDD, warnings in `build` / errors in `gate-code`): `SPEC-01:31,67,469`,
  `TDD-01:204`, `IPLAN-01:43` — doc-form `@adr: ADR-01` / `@tdd: TDD-01`. 3 are
  same-line redundant drops (`SPEC-01:31,469`, `TDD-01:204`); 1 table-cell drop
  (`IPLAN-01:43`); 1 prose convert/drop (`SPEC-01:67`). Same 3 cases also fail
  the acceptance suite (pre-existing) on the `SPEC-01_golden` fixtures.
- *Fix shape:* re-cascade via the `doc-<layer>-fixer` skills in a live plugin
  session (now rewritten for YAML BDD but the SPEC/TDD/IPLAN fixers handle
  markdown `@`-tags), OR a `REFGRAN --fix` mechanical auto-fixer (the 3 same-line
  drops are deterministic; `SPEC-01:67` prose needs a judgment call). Until then
  `REFGRAN01` is warnings-only in `build`; gate-code-clean lands with the
  re-cascade. The Gherkin complexity that originally blocked this is gone.

### `[example-corpus]` `CORPUS-PRD-TH-RES` — PRD-01 missing `component_decomposition` → 11 unresolvable `@threshold:` citations

- *Context:* surfaced while verifying CFB-PR-2 2a-core step 4 (forward-coverage
  gate) on `examples/url-shortener/docs/`. `02_PRD/PRD-01.md` trips `TH-RES-001`
  (error): downstream docs cite `@threshold: PRD.01.perf.*` but PRD-01 declares
  no `component_decomposition` thresholds. Pre-existing — identical under main's
  linter; unrelated to coverage (CLEANUP-PR-D threshold-resolution).
- *Fix shape:* dispatch `doc-prd-fixer` to add the `component_decomposition`
  thresholds the downstream `@threshold:` tags expect, then re-cascade. Never
  hand-edit the example artifact.

### `[harness]` `TRACE-RES-001-PER-LAYER-TEST-MODE` — per-layer acceptance tests duplicate the upstream chain

- *Context:* ACCEPTANCE-FIXTURES-DRIFT (2026-06-14) closed 12
  long-standing deterministic-test failures by copying upstream
  goldens (layers 1..N-1) into each `tests/acceptance/fixtures/layer_NN_<NAME>/valid/`
  dir — 28 files total. This is intentional duplication so each
  per-layer fixture dir is self-contained; the per-layer
  `assert_golden_passes_lint` runs `run_lint(golden.parent)` which
  satisfies TRACE-RES-001 only when the cited upstream host docs are
  present in the same directory.
- *Fix shape (deferred):* extend `sdd_doc_lint` with a CLI flag
  `--allow-unresolved-upstream` (or `--isolated-layer`) that
  downgrades TRACE-RES-001 to a warning when the upstream host doc is
  missing. The per-layer tests pass that flag; fullpath does not.
  Eliminates the 28-file duplication; the per-layer dirs again
  contain only the layer's own golden. Weakens the rule slightly but
  the fullpath chain still enforces it strictly.
- *Status:* Parked. Not a blocker — the duplication is small, the
  fixtures are stable, and the rule remains strict where it matters
  (fullpath integration). Pull when fixture maintenance becomes a
  real burden, OR when adding a new layer makes the duplication
  pattern obvious.

### `[sync]` `WEBSITE-VERSION-BADGE-DRIFT` — `web-site/src/pages/index.astro` `Pre-release v<X.Y.Z>` badge — ⏳ OPEN ON RESIDUAL (sync-script leg landed; the cross-repo confirmation gate is in IPLAN-0008)

- *Context:* IPLAN-0008 step 6 closed the bug class for the web-site
  home-page badge by extending `scripts/sync-version-refs.sh` to
  propagate `Pre-release v<X.Y.Z>` into the sibling
  `../web-site/src/pages/index.astro` (cross-submodule write at the
  umbrella layer). The script change ships in the framework PR;
  the actual badge value is set in the web-site PR (also part of
  IPLAN-0008, step 4-5-7). This entry exists so the cross-repo
  coupling is discoverable from the framework side.
- *Fix shape:* Same `replace_in_file "Pre-release v<old>" "Pre-release v<new>"` shape
  as the v0.20.1 plugin-README fix used. The replace_in_file helper is
  no-op if `../web-site/src/pages/index.astro` does not exist
  (framework cloned standalone without the umbrella siblings). When
  framework's plugin VERSION bumps next, the hook propagates to the
  web-site working tree; the developer commits the change in
  web-site's own PR.
- *Status:* Closed by the framework PR for IPLAN-0008 step 3+6 — the
  sync-script extension lands here; the cross-repo verification (bump
  VERSION → run sync → observe web-site badge change) is the
  Confirmation gate in IPLAN-0008.

### `[skill]` `MODEL-PRECHECK-ROLLOUT` — original framing (superseded; see PARKED entry above)

- The original "wire `model.precheck` into every `doc-*` SKILL (up to 32),
  compare against the session model, gate by the acceptance suite" framing
  (introduced by PLUGIN-USER-COMMANDS, merged 2026-06-14) was **superseded**
  by the 2026-06-21 review: a skill cannot read its own session model, so the
  *compare* premise is unworkable; the redesign prints the recommendation
  instead and scopes to interactive entry points. Tracked in the **PARKED**
  entry near the top of this Open section + `plans/MODEL-PRECHECK-ROLLOUT-PLAN.md`.

### `[layer-promotion]` Promote `component_decomposition` to a first-class `02b_DECOMP` layer (Option B from DECISION-GATE-D)

- *Context:* DECISION-GATE-D (2026-06-11) resolved as Option A
  (subsection in PRD). Option B (new layer between PRD and EARS) was
  deferred because most aidoc-flow consumers will have ≤ 5-component
  systems where buried decomp in PRD is sufficient. **User direction:
  "We will have complex projects in the future — keep Option B as
  further development for when Option A is not enough."**
- *When to revisit:* signs that Option A is insufficient include:
  (a) consumer PRDs growing past ~600 lines because component
  decomp is bloating PRD §7b; (b) auditor lens unable to evaluate
  decomp quality at PRD altitude because it competes with product
  concerns; (c) `@decomp:` becoming a desired @-tag form for richer
  downstream binding; (d) C4-L2 diagrams or component-level chaos
  scenarios that don't fit cleanly in PRD §7b.
- *Fix shape (when triggered):* new layer `02b_DECOMP` between PRD
  (02) and EARS (03). `DECOMP-NN.yaml` artifact with components +
  dataflow + threshold bindings. EARS pivots its `required_tags` from
  `[prd]` → `[decomp]`. ADR + SPEC gain `decomp` in their
  necessary-upstream sets. New 6-lens crew (architect, tech_lead,
  integration_lead, chaos_engineer, security_engineer, auditor).
  4 new SKILLs (doc-decomp / -audit / -fixer / -autopilot). Estimated
  framework MINOR `0.20.x → 0.21.0`; 5-6h cascade re-run required.
- *Effort estimate:* ~12-15h (vs. PR-D's ~3h). See
  `plans/CLEANUP-PR-D-DECOMP-THRESHOLD-GATES-PLAN.md` §Option B
  comparison for the full scope analysis preserved during the
  decision gate.

### D54 consumer feedback (CC Phase-1 manual L1–L8 build) — triaged 2026-06-26

> Source: D54 "Framework Usage Feedback" (2026-06-12), a consumer-project
> log from authoring the full 8-layer chain BY HAND against spec 0.13.1,
> no plugin. Re-checked against live spec 0.23.0: F-10 (inline-Mermaid)
> and F-11 (compat matrix + `/about`) already ADDRESSED — not logged.
> F-03 (offline readiness score) and F-09 (MVP sizing) resolved-by-design
> — see notes in `[lint] D54-F01` and below. Each entry below carries the
> author's resolved fork-decision (clarified 2026-06-26).
>
> **Orchestration:** → `plans/CONSUMER-FEEDBACK-001-PLAN.md` sequences all
> 22 items (D54 + Engramory + BeeLocal) into child PRs PR-1…PR-12.

### `[template]` `D54-F02-REUSE-MANIFEST` — no first-class reuse of an existing/external artifact — ⏳ OPEN ON RESIDUAL (core shipped 2026-06-29, spec 0.32.0; deferred: element-granular marking → REUSE-MANIFEST-002, commit-existence verification, audit no-free-≥90 enforcement)

- *Context:* D54 F-02 (P1, make-or-break for brownfield). Framework
  assumes greenfield authoring of all 8 layers; `active_layers` only
  *disables* BDD/ADR, can't *satisfy-by-reference*. `trace_walk.py`
  treats a referenced artifact as orphan/missing. Absent from this
  backlog + ROADMAP. The CC build improvised `*-00_index.md` reuse-maps.
- *Fix shape:* one element-granular reuse manifest — each element marked
  `authored | referenced`; whole-layer mid-chain reuse (the P1 need) is
  just "all elements referenced." Introduce `satisfied_by_reference`:
  passes coverage/traceability ("present + linked") but records "reuse,
  not re-audited" — does NOT earn an authored-layer ≥90 readiness score
  for free. Reference target MUST be in-repo / pinned (path + commit),
  deterministically verifiable; live external URLs allowed only as
  non-authoritative `@discoverability` hints, never the trace target.
- *Status:* SHIPPED (REUSE-MANIFEST-001, spec 0.32.0, 2026-06-29) — `reuse: {state: referenced, target}` frontmatter; COV01/COV02 exempt referenced docs; REUSE01 advisory + REUSE02 in-repo-pinned-target contract; full-prefix rule; TRACEABILITY.md reuse contract. Deferred: element-granular per-element marking (REUSE-MANIFEST-002), commit-existence verification, audit-skill no-free-≥90 enforcement.

### `[lint]` `D54-F01-PROVISIONAL-IDS` — manual-mode placeholder-ID convention + hash-algo parity — ⏳ OPEN ON RESIDUAL (core shipped 2026-06-29, spec 0.31.0; the reference-aware `rehash` leg → PROVISIONAL-IDS-002)

- *Context:* D54 F-01 (P1). Templates still use `xxxx`; the id regex
  `[a-f0-9]{4,8}` rejects it, and `sdd_doc_lint`'s placeholder check
  `\bXX+\b` only catches *uppercase* — leftover lowercase `xxxx` passes
  silently. No doc-level provisional flag, no rehash. (F-03 "offline
  readiness score" folds here: author concedes the score stays the LLM
  `-audit` skill; the no-tooling need is met by the published hash
  algorithm plus this placeholder convention plus a trivial plugin install,
  not an offline scorer.) Engramory feedback #2 corroborates + sharpens: the SHA-256
  algorithm IS published, but only in `EARS-TEMPLATE.yaml:94-100`, NOT in
  `ID_NAMING_STANDARDS.md` (which states only "4-char hex SHA256"), and
  the standard never says hand-authored hashes are placeholders-until-
  canonical — so the parity premise isn't yet anchored where authors look.
- *Fix shape:* (a) add `metadata.id_standard.state: provisional|canonical`
  (keystone — marks "all IDs here are placeholders; canonicalize" once
  per doc, not per-ID character); (b) section-ordinal hex placeholder
  (`BRD.01.07.0001`) as a *temporary crutch* — stable-across-reorder
  content-hash is still the canonical end-state, the `provisional→canonical`
  flip guards provisional ordering from leaking; (c) ship a regex-valid
  literal (`0000`) in templates + fix the lint to flag lowercase `xxxx`;
  (d) promote the SHA-256 algorithm from template `_guidance` prose to a
  *normative* spec (pin input normalization + 4→8 collision rule) so an
  external reference-aware `rehash` produces byte-identical IDs to the
  plugin. Land `rehash` as an `sdd_doc_lint` subcommand, not a new CLI.
  Concretely: lift the `EARS-TEMPLATE.yaml:94-100` algorithm into
  `ID_NAMING_STANDARDS.md` as the normative source + add a
  "hand-authored hashes are placeholders until canonicalized" statement
  there (Engramory #2).
- *Status:* CORE SHIPPED (PROVISIONAL-IDS-001, spec 0.31.0, 2026-06-29) —
  `id_state` flag + `PROV01` advisory, ordinal-hex provisional form + `0000`
  template literal, `PH01` lowercase fix, normative SHA-256 algorithm in
  `ID_NAMING_STANDARDS.md`. **Remaining:** the reference-aware `rehash` subcommand
  (+ `rehash --check`) → **PROVISIONAL-IDS-002** (follow-on).

### `[lint]` `D54-F05-BDD-COVERAGE-ROLLUP` — no aggregate EARS coverage across a split BDD set — ⏳ OPEN ON RESIDUAL (core subsumed by COV02 2026-07-06; residual is P3 cosmetic — per-file `ears_coverage` reporting + the unenforced split convention)

- *Context:* D54 F-05. `ears_coverage` is per-file only; no tool
  aggregates EARS coverage across `BDD-01/02`; per-file reads "partial"
  when split, true coverage only visible by reading both. "≤12 scenarios
  → split" is an unenforced antipattern, decoupled from the 50k-token
  split trigger.
- *Fix shape:* first-class the "multiple BDD files → one EARS" relation —
  an EARS-level coverage roll-up across the BDD set (in `sdd_doc_lint` /
  `trace_walk.py`) + a documented split-by-functional-block convention so
  per-file "partial" aggregates to a true score.
- *Status:* **CORE SUBSUMED (verified 2026-07-06); residual = P3 cosmetic/doc.**
  The "aggregate EARS coverage across a split BDD set" gate shipped as **`COV02`**
  (`_check_backward_coverage`, corpus-wide) + element-level ELEMENT-COVERAGE-001 (spec
  0.30.0): every EARS element's downstream BDD coverage is now computed across the whole
  corpus, so a split `BDD-01/02` no longer hides coverage from the gate. **Residual
  (P3):** the per-file `ears_coverage` *reporting field* still reads "partial" in
  isolation (cosmetic — the gate is correct), and the "split-by-functional-block ≤12
  scenarios" convention is documented in `AUTHORING_STYLE.md` / `04_BDD/` as guidance
  but unenforced. Low value; fold into a future authoring-doc pass if it bites.

### `[docs]` `D54-F07-TAG-SYNTAX-REFERENCE` — per-layer tag punctuation undocumented + unenforced — ⏳ OPEN ON RESIDUAL (doc leg shipped spec 0.29.0; the per-layer punctuation enforcement leg is cosmetic and deferred)

- *Context:* D54 F-07. BDD template demands no-space `@brd:BRD.01`
  (Gherkin-parser-forced); EARS/ADR/SPEC use pipe+space `@brd: X | @prd: Y`
  (convention). `sdd_doc_lint`'s `\s*:\s*` accepts both everywhere, so the
  per-layer rule is never enforced.
- *Fix shape:* narrowed (author) to **document + enforce**, NOT unify
  (Gherkin makes one-format impossible): a single tag-syntax reference
  page stating the legitimately-per-layer rules, plus `taglint` (an
  `sdd_doc_lint` check) enforcing them per layer.
- *Status:* **DOC LEG ✅ SHIPPED, enforcement leg deferred (cosmetic).**
  The reference page shipped as `framework/governance/TAG_SYNTAX.md` (YAML-BDD-SCHEMA
  PR-3, #201, spec 0.29.0): per-layer punctuation ("one space after the colon"), the
  **BDD exception** (structured `ears:` YAML list, not an `@`-tag), pipe-delimited
  multi-tags, and the per-layer example table. The **enforcement leg is cosmetic-only
  and deferred**: `sdd_doc_lint`'s `_TAG` regex (`@(...)\s*:\s*(...)`) accepts both
  `@brd:X` and `@brd: X`, but the trace graph resolves identically either way — a
  per-layer punctuation lint would catch nothing that breaks traceability, and the
  original divergence driver (BDD Gherkin no-space tags) is now a legacy-only dual-mode
  path since YAML-BDD. Not worth a GATE-SPEC change; revive only if a real
  punctuation-driven mis-parse surfaces.

### `[harness]` `D54-F08-SKELETON-EMIT` — no content-keys-only template emit

- *Context:* D54 F-08. Templates are large (`BRD-TEMPLATE.yaml` 992 lines)
  and `_guidance`-dense; the internal audit context-strip is not a
  user-facing skeleton emit.
- *Fix shape:* a `--skeleton` emit (strip `_guidance`/`_example`/
  `_antipatterns`, leave content keys) — land as plugin tooling, not a
  new CLI.
- *Status:* ⏸️ **DEFERRED — build-on-demand (2026-07-06, D-0058).** Grounding found this a
  speculative DX convenience with real hazards, so it is not built now (per the
  minimal-and-realistic convention). Reasons: (1) **anti-aligned with the framework's own
  design** — templates are deliberately `_guidance`-dense because the framework bets that
  guidance-dense templates author *better* (the `doc-*` skills inject the full template); a
  guidance-stripped skeleton produces lower-quality authoring. (2) **Comment-fidelity hazard**
  — a YAML `safe_load`→`safe_dump` strip destroys all `#` inline enum hints
  (`value: feature  # platform | feature`) and reorders/reformats, so the skeleton would not
  resemble the template; faithful output needs a `ruamel.yaml` round-trip (a new dependency).
  (3) **Divergence risk** — not all underscore keys are strippable: `_authored_form` (the BRD
  FR-coverage contract COV01 depends on), `_required_when_subtype` (IPLAN sub-type gating), and
  `_required` are **normative** and must be preserved; a naive "strip all `_`" would drop
  required structure and mislead authors, and the preserve-list must stay in sync as templates
  evolve. (4) **No demand signal** — no consumer log requests a skeleton; the `doc-*` skills
  already own authoring. **Revive only if a consumer actually asks** — at which point the safe
  form is a `tools/` script with a curated strip denylist (`_guidance`/`_size_target`/`_note`/
  `_antipatterns`/`_example`) that preserves the normative keys, plus a test asserting they
  survive.

### Engramory consumer feedback (SDD authoring against v0.23.0) — triaged 2026-06-26

> Source: aidoc-flow-engramory feedback log (June 2026), authoring
> Engramory's SDD artifacts against spec 0.23.0. All 🟡 (clarification /
> improvement) — none block. Item #2 (standalone hash helper) folded into
> `D54-F01-PROVISIONAL-IDS` above; item #7's forward-coverage half overlaps
> `D54-F13` — see `ENG-FWD-COVERAGE` below. Item #6's *premise is invalid*
> (Lite/Standard/Full depth variants were removed 2026-06-12; the framework
> is single-path) — only the stale-docs residue it exposed is logged.
>
> **Orchestration:** → `plans/CONSUMER-FEEDBACK-001-PLAN.md` (PR-2/5/6/7/10).

### `[lint]` `SKETCH-FILE-STANDALONE` — standalone scope-only `status: Sketch` BRD *file* support (deferred from ENG-BRD-SKETCH-ROADMAP)

- *Context:* ENG-BRD-SKETCH-ROADMAP (D-0044) shipped the Sketch concept as a
  Planned-BRDs **row**. A *standalone* scope-only `BRD-NN_*.md` Sketch file (only
  document_control/introduction/project_scope) is NOT supported: STRUCT01 enforces
  the full required-section set on any instance BRD, and the index exemption covers
  only `<TYPE>-00_index` docs.
- *Fix shape (when triggered):* a STRUCT01 under-authoring exemption keyed on
  `status: Sketch` (relaxes required sections) + a `SKETCH-001` over-authoring guard
  (forbid element IDs / downstream tags on a Sketch). Pull only if authors actually
  want standalone Sketch files / over-authoring drift appears. Likely framework MINOR.
- *Status:* OPEN — P3, deferred (author (d): "only if over-authoring drift shows up").

### `[hermes-parity]` `ENG-STALE-DEPTH-DOCS` — dead Lite/Standard/Full tables still in Hermes orchestrator docs — ⏳ OPEN ON RESIDUAL (Hermes legs closed 2026-07-06; leg (a), the public README render at the released tag, verify at the next release cut)

- *Context:* Engramory #6 — its *requested clarification is moot* (depth
  variants are dead since 2026-06-12, framework is single-path; author
  confirmed via clone-grep that no Engramory component was authored "Lite" —
  all six carry SPEC→TDD→IPLAN, nothing under-built). Withdraw #6's
  orthogonality ask; THIS entry is the replacement. Stale surfaces that fed
  the misconception: (1) the **public GitHub README** still advertises
  SDD-Lite/Standard/Full — the v0.20-era copy the author originally read
  (this repo's own `README.md:47-48` is already clean, single-flow); (2) two
  Hermes docs still publish the dead tables —
  `platforms/hermes/.../sdd-orchestrator/root-docs/README.md:100-106`
  ("SDD Depth Variants") and `.../governance/CHG_GOVERNANCE_BRIDGE.md:20`
  ("Lite/Standard may use subset gates").
- *Fix shape:* reconcile all stale surfaces to the single-path model (all 8
  layers required per necessary-upstream; CHG is an orthogonal governance
  overlay; only the MVP→PROD→new-MVP loop). (a) Verify/refresh the published
  GitHub README at the released tag (F-11-adjacent — guard against the stale
  public render); (b) refresh the two Hermes docs — cross-reference
  `HERMES-BACKLOG.md` H-11 (the broader sdd-orchestrator v3.2-worldview
  refresh already parked there); this entry is the concrete file:line
  evidence for it. Do not double-track.
- *Status:* ✅ **CLOSED (2026-07-06, `ENG-STALE-DEPTH-DOCS-PLAN.md`, hermes 0.7.2 + skill
  2.1.1).** The Hermes-side legs are done: grounding found **7** published surfaces (not the
  2 named here) — `root-docs/README.md` (tagline + the "SDD Depth Variants" table that
  **self-contradicted** the file's own single-path prose), `MULTI_PROJECT_QUICK_REFERENCE.md`
  - `MULTI_PROJECT_SETUP_GUIDE.md` (two depth tables + an embedded changelog line),
  `governance/README.md` + `MULTI_PROJECT_SETUP_GUIDE.md` (two **dead links** to a
  nonexistent `SDD_DEPTH_GUIDE.md`, removed), `CHG_GOVERNANCE_BRIDGE.md` (subset-gate rule),
  and the "SDD-Full" CHG-label comments — all reconciled to the single-path model.
  Doc-accuracy only; no framework change; no new decision (governed by the 2026-06-12
  cleanup + D-0053). **Residual (leg (a), tracked here):** the *public GitHub README render
  at the released tag* — this repo's own README is already single-flow; the stale public
  copy is a released-tag/mirror concern, not an editable file in this tree. Verify at the
  next release cut.

### BeeLocal consumer feedback (SDD authoring against v0.23.0) — triaged 2026-06-26

> Source: aidoc-flow BeeLocal feedback log (June 2026), authoring BeeLocal's
> SDD artifacts. The OLDEST of the three consumer logs + the origin of items
> the others extend. Re-checked against v0.23.0:
> **Dropped — OBSOLETE** (pre-migration `ucx_flow_v3/`/`mcp_ucx/`/`ucx_hermes/`
> structure removed at v1.0.0 cutover, preserved only on
> `legacy-ucx-v3.2-read-only`): #3/#37 (duplicate `ucx_flow_v3/`), #4/#38
> (stale template paths — current README correctly points at `framework/layers/`).
> **Dropped — ADDRESSED**: #5/#39 (layer-count drift — single 8-layer model
> is now the only story; no SYS/REQ/CTR/TSPEC/TASKS as current); #8a/#52-pt1
> (per-layer numbering independence + fan-out — closed by CLEANUP-PR-F in
> `ID_NAMING_STANDARDS.md:18-51`).
> **Folded**: #6/#40 → `ENG-PLATFORM-ADR-TIMING` (PRD-layer note added);
> #8b/#52-pt2 (generated matrix) + #10/#54 (backward coverage) →
> `ENG-FWD-COVERAGE` (d)/(e). Remaining open items below.
>
> **Orchestration:** → `plans/CONSUMER-FEEDBACK-001-PLAN.md` realizes the
> sequencing below as child PRs PR-1…PR-12.
>
> **Suggested PR sequencing (author Q5 — small themed PRs, NOT one sweep;
> each ≤3 doc surfaces per governance Rule 1):**
>
> 1. **Trace correctness (first — load-bearing):** `BL-TAG-CHAIN-GATE-SYNC`
>    (`GATE-08-E003` + `TRACEABILITY.md` diagram). Goes first because it
>    changes how everyone reads the chain.
> 2. **Lint hardening:** `BL-REF-GRANULARITY` + `BL-STATUS-SCOPE` — both land
>    in `ID_NAMING_STANDARDS.md` + the taglint; cohesive.
> 3. **BRD lifecycle + authoring pattern:** `BL-BRD-SET-WORDING` +
>    `ENG-BRD-SKETCH-ROADMAP` ("current set full, rest stubbed") —
>    BRD-TEMPLATE + README + BRD-00 index.
> 4. **Template ambiguities + advisory score:** pair `BL-SIZE-UNITS` +
>    `BL-VENDOR-NAME-SCOPE`, with `BL-READY-SCORE-ADVISORY` separate if the
>    pair already hits 3 surfaces.

### `[lint]` `BL-REF-GRANULARITY` — doc-level vs element-level refs interchangeable, silently defeats coverage

- *Context:* BeeLocal #55. Templates allow both `@bdd: BDD-NN` (whole doc)
  and `@bdd: BDD.NN.03.xxxx` (element). A doc-level ref in a *verification*
  context silently defeats element-level coverage computation (BeeLocal
  SPEC-09/TDD-09 cited `BDD-01` though the exact scenario `BDD.01.03.3aa0`
  exists). Nothing in `ID_NAMING_STANDARDS.md`/`TRACEABILITY.md` states a
  granularity rule; lint doesn't enforce it.
- *Fix shape (author Q2):* state the rule via the derivable principle —
  **citing an oracle layer (EARS requirement or BDD scenario) ⇒ element-level
  required; citing an upstream design doc as a unit (ADR/SPEC/TDD) ⇒ doc-level
  permitted** — in `ID_NAMING_STANDARDS.md`, + a `sdd_doc_lint` check that
  **blocks at GATE-06** (a doc-level ref in a verification context silently
  zeroes coverage — a correctness defect, not mid-build incompleteness, so it
  blocks; distinct from the missing-IPLAN=warning case). Element-level fields
  (verification): SPEC `upstream.bdd_references`/`ears_references` + inline
  `source: "@bdd/@ears: …"` in invariants/state_machine/error_handling; TDD
  `scenarios[].bdd_scenario`/`test_cases[].bdd_ref`/`upstream.bdd_references`/
  `ears_references`. Doc-level OK: SPEC `architecture_decision`/
  `upstream.adr_references`; TDD `test_cases[].spec_ref`/`upstream.spec_references`;
  IPLAN `source_spec`/`upstream.spec_references`/`tdd_references` (the principle
  auto-excludes IPLAN→SPEC/TDD). **Derive the exact field list from the live
  SPEC/TDD templates** so it stays in sync. Interacts with `ENG-FWD-COVERAGE`
  (granularity makes element-level coverage computable) + `D54-F07` (same
  taglint surface).
- *Status:* OPEN — P2.

### `[template]` `BL-STATUS-SCOPE` — `status:` key overloaded across 3 scopes, unlintable

- *Context:* BeeLocal #57. `status:` carries 3 different legal-value sets:
  document (`Draft|In Review|Approved`), ADR lifecycle
  (`Proposed|Accepted|Deprecated|Superseded`), option (`Selected|Pending`)
  — plus IPLAN (`Draft|In Progress|Completed`). A linter can't validate
  `status` without knowing its scope; a wrong-scope value passes silently.
- *Fix shape (author Q3 — enum, NOT rename):* define per-context `status`
  enums in `ID_NAMING_STANDARDS.md` + teach `sdd_doc_lint` the scope→enum
  map (validate `status` by its scope). Do **not** rename to
  `document_status`/`option_status` — that's a breaking change across every
  artifact + the example corpus for no behavioral gain; a scope-aware linter
  solves the actual problem. Fold a rename in only at a future major break.
- *Status:* OPEN — P3.

## Closed

### `[harness]` `IDHASH-GUARD-GLOB-NARROW` — ✅ CLOSED (2026-07-31, `371f6261` PR #406) — the guard was green partly because it did not look where a violation survived → [#385](https://github.com/vladm3105/aidoc-flow-framework/issues/385)

- *Context:* surfaced 2026-07-30 while correcting a `CLAUDE.md` claim that no
  surface computes SHA-256 in-prompt (PR #387). `test_no_inprompt_hashing.py`
  globbed `doc-*/SKILL.md` (41 of 52 plugin SKILLs) and a non-recursive
  `references/*.md` (36 of 39), so all of `references/batch-brd-processing/` was
  unscanned — and `batch-remediation-script.md:24` still minted element IDs with
  its own `hashlib.sha256` routine, diverging from the normative transform on
  four points and hashing a different input tuple, so it computed **different
  IDs**. The guard's own docstring forbids narrowing coverage by glob.
- *Resolution:* both roots `rglob` now; the script calls `compute_element_hash()`,
  matching the sibling corrected by `#342`; a coverage census walks each root
  independently of the scan's own patterns; and the exempt filenames are pinned as
  a literal set, since re-applying `_SESSION_RECORD` in the census would have been
  the same computation twice — broadening it to `\.md$` empties the scan and a
  census written that way stays green. Six mutations verified: reintroduce the
  hash, re-narrow either glob, plant a violation in a previously unreachable
  plugin SKILL, broaden the exemption, delete a whole root. The 11 unscanned
  plugin SKILLs were confirmed clean, so that half was latent, not live.
  Hermes `0.12.0` → `0.12.1`.
- *Scope — closed as filed, not as titled.* #385 named the plugin-SKILL and
  Hermes-reference halves and both are closed. It did **not** cover
  `agent-skills/**/SKILL.md`, which no root reaches and where
  `sdd-orchestrator/SKILL.md:667` still hashes. Left deliberately to
  `SDD-CORPUS-UNVERIFIED` above rather than hand-patched, on the reasoning that
  produced that entry.

### `[ci]` ~~`NO-PIN-CURRENCY-CHECK`~~ → `PIN-CURRENCY-NO-READER` — ✅ CLOSED (2026-07-31, `d3d7f845` PR #392 + `c77ff3f4` PR #394) — the check ran and warned correctly; nothing read a warning-only annotation on a weekly scheduled job

- *Context:* the original entry claimed this repo "runs `check-pin-currency.sh`
  nowhere." **It was measured false** (2026-07-29, CANON-PARITY-001): canon's
  `check-standards-drift.sh` tail invokes it on every weekly `standards-drift`
  run, and it fired on 2026-07-27 — run
  [30257877863](https://github.com/vladm3105/aidoc-flow-framework/actions/runs/30257877863)
  — naming all ten stale callers *and* the `--repin` remedy, two days before a
  human noticed. Restated then as `PIN-CURRENCY-NO-READER`: the defect is that
  the signal has no reader, since `standards-drift.yml` is `schedule:`-only and
  the script is `WARNING-ONLY, NEVER BLOCKS` by design
  (`check-pin-currency.sh:10`).
- *Resolution:* `.github/workflows/pin-currency-reader.yml` reads a completed
  `standards-drift` run and reconciles **one** auto-maintained tracking issue
  from its verdict — created on `stale`, edited in place, reopened rather than
  duplicated, closed when clean. **No second detector was added**, which the
  entry's own fix shape would have done: the reader consumes the run that
  already happened. The parse and reconcile halves live in `scripts/` rather
  than inline in YAML, because `workflow_run` and `workflow_dispatch` both
  require the file on the default branch, so nothing end-to-end can run on the
  PR that introduces it; 18 unit tests over five checked-in fixtures cover what
  ships, registered into conformance by `tests/conformance/test_repo_scripts.py`.
  Verified live after merge: issue
  [#393](https://github.com/vladm3105/aidoc-flow-framework/issues/393) created
  (V10), edited without duplicating (V11), reopened after a manual close (V12),
  and a reader run appeared with `event=workflow_run` (V14). V13 was satisfied
  by the stub; the live close-on-clean was outside the gate by design.
  Rationale in **D-0073**; plan `plans/PIN-CURRENCY-READER-PLAN.md`.
- *Upstream half — filed, not merely noted:* no pin audit anywhere has a reader;
  canon's own fleet audit discards its verdict with `|| true`. Five measured
  defects went to
  [aidoc-flow-ci#351](https://github.com/vladm3105/aidoc-flow-ci/issues/351),
  including two paths in `check-pin-currency.sh` that report a green that is not
  one. Open at time of closure.
- *Tracker:* stayed **TODO-only** under the carve-out
  `FRAMEWORK_FEEDBACK_LOG.md:90` actually names — *"already covered by an open
  plan"* — which `PIN-CURRENCY-READER-PLAN.md` was from the moment this entry was
  picked up. ⚠️ **Not** because it closed on the same merge as its fix: `:104`
  makes closing together the *normal case* for an issue that meets the bar, not
  an exemption from filing one. The *upstream* defects met the bar and are the
  issue above.
- *Lesson:* graduated to `CLAUDE.md` § "Durable traps → Process" — *an absence is
  the easiest defect to assert and the hardest to verify.* Not restated here.

### `[docs]` `HANDOFF-OVER-SIZE` — ✅ CLOSED (2026-07-30, PR #399) — the handoff was 424 lines against a ~200-line target, and the overflow was durable content in the wrong file

- *Context:* noted 2026-07-30 while regenerating for #397. The bulk was
  **`## Durable traps` (~250 lines)** — content the rule says to keep, but keep
  *small*, and which the file's own header already routed elsewhere: "a trap already
  recorded in `CLAUDE.md` is not repeated here."
- *Resolution:* the whole traps section graduated to `CLAUDE.md` § "Durable traps —
  do not re-derive these" (six sub-sections, deduplicated against what `CLAUDE.md`
  already owned), and the one `## Stale advice` row whose only remaining source was
  the handoff itself (`SKIP=gitleaks`) was deleted. Measured, not estimated:
  `plans/HANDOFF.md` **424 → 182** lines, `CLAUDE.md` **697 → 948**. Done in one pass
  rather than the tag-sized batches this entry proposed — batching would have left the
  two files duplicating each other between merges, which is the drift the split exists
  to prevent.
- *Two corrections found while moving the content, both carried into `CLAUDE.md`:*
  the handoff's absence-probe section claimed `CLAUDE.md` "records that
  `gh api …/contents/<missing> --jq '.name'` must not be truth-tested" — it did not,
  and the handoff's own two statements of that trap contradicted each other on
  whether the failure text is the bare string `null` (it is the full 404 JSON); they
  are now one correct bullet. The manifest-case-sensitivity trap was already in
  `CLAUDE.md` § "Unified CI" and was dropped rather than duplicated; `report-only` was
  kept as a short bullet carrying the transferable rule ("a report-only flag is never
  evidence that a new caller cannot fail"), cross-referencing the concrete `sast-scan`
  instance rather than restating it.
- *Deliberately not graduated:* the check-run annotation-cap trap stays in the
  handoff, because `PIN-CURRENCY-READER-PLAN.md` PR 4 is chartered to propagate it.

### `[docs]` `DOC-MAINTAINER-ADOPTION-CLAIM-STALE` — ✅ CLOSED (2026-07-30, PR #399) — `CLAUDE.md` said sixteen call sites across fifteen files

- *Context:* found 2026-07-30. The real count has been **17 across 16** since #382
  added `doc-maintainer.yml`. The `plans/HANDOFF.md` half of this entry (the "still
  unadopted" and "secrets absent" claims) was corrected in #396.
- *Resolution:* fixed in the same PR as `HANDOFF-OVER-SIZE`, which was already
  editing `CLAUDE.md` — this entry's own fix shape asked for exactly that, and named
  the pin-currency plan's PR 4 only because that was the next `CLAUDE.md` PR then in
  prospect. Re-counted with the two commands this entry prescribed (17 sites, 16
  files); both commands are now inline in `CLAUDE.md` beside the figure, so the next
  session re-derives instead of copying.

### `[ci]` `DOC-MAINTAINER-RED-ON-EVERY-PUSH` — ✅ CLOSED (2026-07-30, PR #397) — the adopted dry-run caller was red on nearly every push, unwatched

- *Context:* found 2026-07-30 while confirming the `ci/v2.16.0` migration was
  complete (it is — 17/17 call sites). `doc-maintainer.yml` was adopted in #382 on
  2026-07-29; **23 failures / 47 runs**, 12 of 13 `push` runs, across **four**
  independent upstream defects — not the two originally recorded.
- *Resolution:* `kill_switch: true` (PR #397, D-0072). Verified in production: the
  merge's own push run went green — `kill_switch=true; exiting cleanly (no LLM cost
  incurred)`. `CHANGELOG.md` also removed from `allowed_paths` (281 KB, past the
  200 KB apply refusal). **Resume requires `aidoc-flow-ci` #352 AND #353** — #353
  alone is 15 of the 23, so #352 alone returns a majority-red pilot.
- *Correction — the original fix shape in this entry was wrong.* It named five
  paths in `auto_merge.high_risk_paths` absent from `allowed_paths` as "ours" and
  proposed aligning the lists. That is a no-op: `planner.py:187` rejects a
  non-allowlisted path before classification, `planner.py:197` already treats
  anything not low-risk as high-risk, and `high_risk_paths` is never shown to the
  model. Those five caused **none** of the 23 failures; they are deliberate
  defence-in-depth and are now documented as such in the config. The misreading
  came from canon's message conflating *duplicate* with *non-allowlisted* — see
  D-0072 point 2.
- *Filed upstream:* [#352](https://github.com/vladm3105/aidoc-flow-ci/issues/352)
  (Step 9 `set -e` — the graduation blocker),
  [#353](https://github.com/vladm3105/aidoc-flow-ci/issues/353) (one bad entry reds
  the run; `validation.rejected` declared and never written; the 30 %-deletion
  guard added as evidence),
  [#354](https://github.com/vladm3105/aidoc-flow-ci/issues/354) (200 KB refusal vs
  an install template shipping `CHANGELOG.md` as low-risk, while canon's own
  changelog is 363 KB).

### `[docs]` `FEEDBACK-READBACK-FALSE-NEGATIVE` — ✅ CLOSED (2026-07-30, filed) — the cross-repo comment readback can report a published comment as empty

- *Context:* found 2026-07-30 while filing the three canon issues above.
  `operations/docs/AGENT_FEEDBACK_INTAKE.md:201` (and the `submit-feedback` skill
  §5) prescribe `gh issue view <N> --json comments --jq '.comments[-1].body|length'`
  as proof a comment published. It returned **0** for a comment that had published
  in full (3,629 chars, confirmed via `gh api …/issues/comments/<id>`), and
  returned the right value on a later read — read-after-write lag, not a broken
  command. The doc calls a non-zero length "the only proof it published", so an
  agent following it literally re-posts and duplicates.
- *Resolution:* filed as
  [aidoc-flow-operations#290](https://github.com/vladm3105/aidoc-flow-operations/issues/290)
  with the id-anchored readback as the suggested fix. Not this repo's to fix.

### `[ci]` `CODEQL-FLOATING-ACTION-PIN` — ✅ CLOSED (2026-07-29, CANON-PARITY-001 / PR #378) — `codeql.yml` resolved `github/codeql-action` through the floating `@v4` major → [#373](https://github.com/vladm3105/aidoc-flow-framework/issues/373)

**Closed by adoption, not by the fix shape below.** `codeql.yml` became a canon
caller (`@ci/v2.16.0`), and canon's reusable already SHA-pins both steps to one
peeled commit (`github/codeql-action@e4fba868…` / v4.37.3) plus
`actions/checkout@3d3c42e5…` / v7.0.1. So the floating references are gone
*because this repo stopped owning the workflow*, and the "pin both steps to
canon's SHA" plan below was never executed — it would have fixed the symptom and
left a hand-rolled workflow to drift again at the next action release.

**The caveat below still stands and was NOT widened:** `actions/checkout@v7` /
`setup-python@v7` still float in the six remaining locally-owned workflows
(`conformance`, `acceptance`, `chg-gate`, `doc-review`, `hermes`, `plugin`).
Whether that convention should change is still the different, unasked question.
`codeql` simply left that set.

**Generalisable, recorded as D-0071 §2:** before fixing a defect in a
hand-rolled surface, check whether canon owns that surface. The entry below
correctly observed that neither canon check could see the defect — true, and the
reason was that the surface was not a canon caller at all.

- *Context:* surfaced while scoping `CI-CANON-V2.16-MIGRATION-PLAN.md`
  (2026-07-29) and named there as explicitly out of scope. `codeql.yml:30,36`
  pin `github/codeql-action/{init,analyze}@v4`; canon SHA-pins the same action to
  one commit wherever it uses it (`aidoc-flow-ci/.github/workflows/codeql.yml:98`,
  `e4fba868…` / v4.37.3). It is the only floating action reference this repo
  *owns* that runs under `security-events: write` — `secret-scan.yml:9` holds the
  same permission but delegates to canon, which SHA-pins its `upload-sarif`.
  Invisible to both canon checks — `check-drift.sh` needs a declared canon tag,
  `check-pin-currency.sh` greps `@ci/vX.Y.Z` only — and Dependabot never converts
  a floating tag to a SHA, so nothing can close it automatically.
- *Fix shape:* pin both steps to canon's SHA with the version as a trailing
  comment. `init` and `analyze` must share **one** commit, and it must be the
  *peeled commit*, not the annotated tag object — canon hit exactly that failure
  (`aidoc-flow-ci/CHANGELOG.md:1380-1384` and `aidoc-flow-ci/plans/FRAMEWORK-TODO.md:859-866`:
  `autobuild` pinned the tag object, which 422s on the commits API and trips the
  workspace SHA audit; canon's `test_lint.sh` now asserts all three steps pin one
  commit). Canon's `e4fba868…` is already the peeled commit, so copying it is
  safe. Leave `actions/checkout@v7` alone — see the caveat.
- *Caveat — do not widen this into a policy change.* Floating majors are the
  repo's standing convention for locally-owned workflows: `actions/checkout@v7`
  / `setup-python@v7` float in seven files (`codeql`, `conformance`,
  `acceptance`, `chg-gate`, `doc-review`, `hermes`, `plugin`). `codeql-action` is
  separable on two specific grounds only — canon SHA-pins that action
  deliberately, and every *other* floating reference in the repo runs under
  `contents: read` while this one runs under `security-events: write`. Whether
  the convention itself should change is a different, unasked question.
- *Tracker:* **issue** per the GD-10 three-test bar — meets (a) (mechanical, any
  contributor can land it) and (b) (reproducible at `file:line` with a concrete
  fix shape). Fails (c): `codeql.yml` feeds no required context, so it degrades
  the Security tab rather than blocking merges.

### `[ci]` `ACCEPTANCE-TIER-REQUIRED-CHECK` — ✅ CLOSED (2026-07-27) — promote the acceptance gate to a required status check

- *Context:* `ACCEPTANCE-TIER-DRIFT-UNTRACKED` (2026-07-27) added
  `.github/workflows/acceptance.yml`, which runs the deterministic tier on every
  push/PR. Making it **required** is a branch-protection change — repo settings,
  not a file — so it cannot ship in the same diff, and until it lands the tier
  can go red without blocking a merge.
- *Fix shape:* **GET → append → PATCH.**
  `PATCH /repos/{owner}/{repo}/branches/main/protection/required_status_checks`
  is **full-replace**: a payload carrying only the new context silently drops the
  others. Read the live `checks` array, append
  `{"context": "Acceptance tier (deterministic)", "app_id": 15368}`, preserve
  `strict: false`, PATCH the union, then read back and assert set equality against
  `observed ∪ {new}`. Confirm `main` is under classic protection first (under
  rulesets the endpoint 404s and the step is a silent no-op), and rebase any PR
  opened before the workflow file existed — it cannot produce the context.
- *Precondition:* the tier must be green on `main` first, and worth a soak run —
  a reviewer observed two non-reproducible failures in ~45 runs that could not be
  isolated. A flaky required check blocks everything.
- *Done:* 2026-07-27. `Acceptance tier (deterministic)` is now the **6th** required
  context on `main` (was 5). Executed as GET → append → PATCH against the live
  `checks` array; `strict: false` preserved; `app_id: 15368` (GitHub Actions) to
  match the existing entries. Read-back asserted **set equality** against
  `observed ∪ {new}` — not mere inclusion, which would have passed even if the
  full-replace endpoint had dropped the other five. Preconditions checked first:
  `main` is under classic protection (rulesets would 404 the endpoint), and the
  context had already reported **success on `main` HEAD**, so no PR hangs on a
  context that never arrives. No open PR predated the workflow file, so no rebase
  was needed.

### `[ci]` `AIDOC-CI-COMPOSITION-CHECK-PRHEAD` — ✅ CLOSED (2026-07-27, stale — mechanism no longer occurs) — required `call / composition` check never landed on a PR head

- *Status (2026-07-27): **STALE — the described mechanism no longer occurs.***
  Verified on the four most recent PRs: `call / composition` reports **success on
  the PR head** every time (#366 `[success,success]`, #363, #361, #356). The
  `ci/v2.x` canon migration fixed it. **A reviewer read this entry as proof that
  required checks gate nothing here, which nearly killed a correct plan** — hence
  this note. PRs #366/#367 *did* need `--admin`, but for an unrelated cause: the
  `ai-review.yml` self-cancel (`aidoc-flow-ci#322`), fixed by pinning
  `ci/v2.15.0` in PR #369. Retained for history; do not act on the body below.

- *Discovered:* 2026-06-29 (PR #219; confirmed byte-identical state on #218,
  merged ~1h earlier by `vladm3105` via admin). Branch protection on `main`
  requires the `call / composition` context, but it is **structurally
  unsatisfiable on a PR head**: `ai-review.yml` runs on `pull_request_target`,
  whose run `head_sha` is the **base** (main HEAD), not the PR head. The
  `workflow_run`-triggered `composition.yml` keys off that `head_sha` and posts
  `call / composition` to main's HEAD — never to the PR's head commit. The PR's
  combined status therefore stays `pending` on that context indefinitely.
- *Impact:* the OPS-0062 green-path `gh pr merge` is `BLOCKED` even when all real
  checks are green; every PR (incl. doc-only) is closed via `--admin` override.
  This defeats the auto-merge default's normal path for this repo. **A
  `skip-ai-review` label-cycle does NOT help** — it re-fires the same
  `pull_request_target` → main-SHA composition.
- *Fix locus:* **aidoc-flow-ci** `composition.yml` reusable — post the
  `call / composition` status to
  `github.event.workflow_run.pull_requests[0].head.sha` (the PR head) instead of
  the run `head_sha`; OR make the required context conditional. Cross-repo (CI
  library + operations auto-merge enforcer backlog); track the fix upstream.
  Logged here for next-session merge-flow awareness.
- *Escalation (2026-07-11, pre-prod audit):* a **second, distinct** failure mode
  now compounds this — `composition` (and the `pull_request`-triggered
  `audit-trail`) `startup_failure` **repo-wide** (on `main` too) since
  **2026-07-10 ~20:49** (last success 18:43). The caller
  `.github/workflows/composition.yml` is valid and pins the immutable `@ci/v1.8.1`
  tag (unchanged sha); the callee `composition.yml` is byte-identical at
  `ci/v1.8.1` and `ci/v1.9.0`; no relevant merge to `main` in the break window.
  Only **aidoc-flow-ci reusable-workflow callers** fail (local-job checks +
  `pull_request`-triggered reusable `lint` still pass), pointing to a **GitHub
  Actions access/visibility change on the `aidoc-flow-ci` repo** (ci commit #120 at
  19:54 = "private repos use self-hosted runners by default") making its reusable
  workflows unresolvable from this repo → `startup_failure` ("workflow file
  issue"). *Fix:* an **org/repo Actions-settings / ci-repo-visibility change
  (founder/CI-owner)**, NOT a repo-file edit; a caller re-pin won't help (callee is
  identical across tags). Until fixed, all PRs land via `--admin` (#305/#306/#307/
  #308 did). Founder-owned.

### `[harness]` `ACCEPTANCE-TIER-DRIFT-UNTRACKED` — ✅ CLOSED (2026-07-27) — 3 acceptance tests failed on `main`, and no CI job ran the tier → [#365](https://github.com/vladm3105/aidoc-flow-framework/issues/365)

- *Context:* found 2026-07-26 while shipping `IDCOORD-SECOND-HASH-IMPL`, which
  needed a before/after baseline. `python3 -m unittest discover -s
  tests/acceptance/deterministic` fails 3 of 63 on `main`: `test_fullpath` and
  `test_layer_iplan` (ACC01 + COV02 + REFGRAN01), `test_layer_tdd` (COV02 +
  REFGRAN01), on the `layer_*`/`fullpath` goldens. Not covered by
  `CORPUS-REFGRAN-RECASCADE`, which is `[example-corpus]`, scoped to
  `examples/url-shortener/docs/`, and mentions the acceptance suite only for
  `SPEC-01_golden` REFGRAN01 — nothing about ACC01 or these COV02 findings.
  **`grep -rn acceptance .github/workflows/` returns nothing**, which is how
  three red tests sat on `main` unnoticed.
- *Fix shape:* two independent halves — (1) realign the acceptance fixtures with
  the coverage rules that have shipped since they were authored (ACC01/COV02
  element-level coverage, REFGRAN01), and (2) decide whether the tier belongs in
  CI. Half (2) is the one that keeps this from recurring; it is also the one that
  needs a call on whether these fixtures are meant to be gate-clean.
- *Shipped:* 2026-07-27, `plans/ACCEPTANCE-TIER-DRIFT-UNTRACKED-PLAN.md`.
  **The premise in this entry was wrong and the plan corrected it:** the goldens
  PASS the lint gate (`rc=0` everywhere) and all 13 findings are
  `severity: warning`. What failed was a second assertion demanding zero findings
  of *any* severity — stricter than any gate the framework defines, so every new
  advisory rule reddened the tier on contact. Fixed by asserting `rc == 0` + zero
  errors + a **bidirectional multiset** match against
  `tests/acceptance/expected_warnings/<target>.yaml`, and by adding
  `.github/workflows/acceptance.yml`, which runs the tier on every push/PR.
  Tier: **64 tests, 0 failures.** Promotion to a *required* check is a
  branch-protection change, not in the diff → `ACCEPTANCE-TIER-REQUIRED-CHECK`.
- *Deferred:* the 13 pinned warnings are real advisory debt →
  `ACCEPTANCE-FIXTURE-WARNING-DEBT` (Open). Note the pinned set measures what the
  **trace graph can see**: three goldens carry an unterminated frontmatter fence
  and are invisible to it, so repairing one is a benign edit that MOVES the
  manifest.

### `[conformance]` `IDCOORD-SECOND-HASH-IMPL` — ✅ CLOSED (2026-07-26) — the acceptance harness re-implemented the element hash without normalization → [#351](https://github.com/vladm3105/aidoc-flow-framework/issues/351)

- *Context:* found 2026-07-26 during `ELEMENT-ID-LAYER-CONTRACT-001` Pass 1.
  `tests/acceptance/_id_coordinator.py:17-19` hashed
  `f"{doc_id}:{section_id}:{title}:{description}"` raw — no
  `_normalize_hash_field`. Its smoke test (`deterministic/test_id_coordinator.py`)
  checked determinism and shape only, never parity with `compute_element_hash()`,
  so a wrong algorithm was indistinguishable from a right one.
- *Shipped:* `plans/IDCOORD-SECOND-HASH-IMPL-PLAN.md` — `element_hash()` now
  delegates to `compute_element_hash()[:4]` (import hoisted to module scope, since
  the `tools/` path insert previously ran only inside `extract_elements()`); an
  8-case parity table covers every transform step, guarded by a second test
  asserting each case's normalized and un-normalized hashes actually differ;
  `safe_load` → `safe_load_all` fixes a **latent `ComposerError`** on the three
  multi-document `fullpath/golden_chain` YAML goldens, with a `fullpath/`
  regression test closing the coverage gap that hid it; AS11's docstring now names
  the transform (re-vendored ×2).
- *Premise correction:* the entry's original "expect fixture-golden churn" claim
  was **false** — `write_registry()` has zero callers, `ID_REGISTRY.yaml` is `{}`
  at 3 bytes, and no golden carried an ID this code minted. Verified at ship:
  `git diff --stat tests/acceptance/fixtures/` empty.
- *Deferred:* the string-`section_id` half → `IDCOORD-NUMERIC-SECTION-ID` (Open).
  The keep-or-delete question from `PLUGIN-TEST-SUITE-REVIEW.md:32` **F2** was put
  to the founder before the work started; answer: **keep + fix**.

### `[skill]` `IDGEN-NO-GENERATOR` — ✅ CLOSED (2026-07-26) — 19 skill/prompt surfaces instruct LLM-side SHA-256; no callable generator exists → [#342](https://github.com/vladm3105/aidoc-flow-framework/issues/342)

- *Context:* founder review 2026-07-26. `compute_element_hash()`
  (`tools/sdd_doc_lint/__init__.py:922`) is reachable only via
  `rehash --check` — no `--fix`, no generator, none in Hermes. Yet the six
  `doc-*-fixer` skills (`doc-brd-fixer/SKILL.md:239,245` + siblings),
  `doc-naming/SKILL.md:106`, and Hermes `UCC_PROMPT_BRD.md:79` /
  `UCC_PROMPT_PRD.md:65` all tell the engine to compute SHA-256 by hand. That
  contradicts `PROVISIONAL-IDS-002-PLAN.md:112-114` ("LLMs can't compute SHA-256
  reliably … the generator emits provisional ordinal IDs"). Observed: an agent
  hit the instruction, found no callable, and wrote its own ad-hoc hash script.
- *Count corrected 9 → 19* (2026-07-26, `ELEMENT-ID-LAYER-CONTRACT-001` census;
  full enumeration in the issue comment). The original nine missed the six
  `doc-*` **authoring** skills (`doc-brd/SKILL.md:125` + siblings — the creation
  path, where most IDs are actually minted), three more Hermes prompts
  (`UCC_PROMPT_EARS.md:74`, `UCRem_PROMPT_EARS.md:186`,
  `UCRem_PROMPT_PRD.md:199`), and **`brd-validation-automation.md:179`** — a
  *loaded* reference (`sdd-orchestrator/SKILL.md:836`) shipping runnable code
  with a **fourth** normalization variant that disagrees with
  `ID_NAMING_STANDARDS.md:88-93` on five of six steps. That last one is the
  highest-value item: it is what an agent finds instead of writing its own script.
- ✅ **Fixed** (IDGEN-NO-GENERATOR, D-0068; plugin `0.24.0`, Hermes `0.12.0`; no
  framework change): the generator ships as
  `python -m sdd_doc_lint.rehash --compute` (rejecting the `artifact_id` form,
  which would silently produce a hash `--check` can never match), and **25 live
  authoring surfaces** were rewritten — BRD calls the tool; PRD/EARS/BDD/ADR/TDD
  emit a stable opaque 4-hex identifier with **no** `id_state: provisional`
  (canonicalization cannot run for those layers, so the mark could never be
  discharged). Locked by
  `tests/conformance/platforms/test_no_inprompt_hashing.py`.
- 📌 *The count was 25, not 19.* Both this entry's census and the plan's
  "re-derived by live grep" checked one Hermes `references/` file, not the tree.
  The 9 extra were shipping **runnable** ad-hoc hash code, each with its own
  normalization variant, none matching the standard — found only because the
  guard scanned the whole class.
- ↪ *`--fix` deferred to PROVISIONAL-IDS-002 Phase 2/3, on measurement:* it would
  rewrite all 4 of BRD-01's §7 FR IDs and break citations in **8 downstream
  files**, so it is a corpus-wide re-cascade needing a citation-update design,
  not a file-local fix.

### `[governance]` `GOV-TODO-ISSUE-SPLIT` — ✅ CLOSED (2026-07-26) — framework-owned gaps are tracked only here; no rule opens a GitHub issue → [#345](https://github.com/vladm3105/aidoc-flow-framework/issues/345)

- *Context:* founder question 2026-07-26. Governance mandates the TODO tier
  (`DOC_GOVERNANCE_CORE.md:13` Principle 9 → `FRAMEWORK_FEEDBACK_LOG.md:55-74`)
  and mandates GitHub issues **only for cross-repo** defects
  (`CLAUDE.md:276-320`). Nothing routes an own-repo gap to the tracker: this file
  is 1,376 lines / ~40 entries while the repo held 1 issue, despite 11 issue
  templates + a full area-label taxonomy. `FRAMEWORK_FEEDBACK_LOG.md:100` already
  assumes issues exist ("if a plan or issue already exists…") without saying when
  one is created.
- ✅ **Fixed in both halves.** Repo working rule landed first in `CLAUDE.md`
  (PR #347, 2026-07-26). Spec half ratified as **GD-10**, framework
  `0.39.0 → 0.40.0`: `DOC_GOVERNANCE_CORE.md` Principle 9 gains the
  queue-vs-channel sentence, and `FRAMEWORK_FEEDBACK_LOG.md` gains
  §"Tier 2 → the tracker" — the three-test bar (actionable by a non-finder /
  reproducible at `file:line` with a fix shape / user-visible), the evidence an
  issue must carry, one-issue-per-defect, link-both-ways + close-on-the-same-SHA,
  and read-the-filed-artifact-back. Purely local or speculative entries stay
  queue-only so the tracker does not become a second copy of the backlog.
  Written host-agnostically ("the framework's tracker"), so a consumer on any
  tracker can satisfy it. `CLAUDE.md`'s "spec counterpart is not yet ratified"
  caveat was replaced in the same PR.

### `[template]` `IDPLACEHOLDER-UNDEFINED` — ✅ CLOSED (2026-07-26) — `placeholder: "0000"` matches no documented meaning and has no consumer → [#352](https://github.com/vladm3105/aidoc-flow-framework/issues/352)

- *Context:* raised as #343's secondary observation, deliberately not actioned
  there (drift fix ≠ governance question). All five element-ID templates declare
  `placeholder: "0000"` + *"Template placeholder"* prose
  (`BRD-TEMPLATE.yaml:147,153` + siblings) while using `.xxxx` in their own
  bodies. Neither reading fits: as a *template* placeholder each file
  self-contradicts; as a *produced-document* placeholder the documented form is
  `0001` (`ID_NAMING_STANDARDS.md:152-155`), not `0000`. `0000` appears nowhere
  in `framework/governance/`; D-0040 never mentions the key; nothing reads it.
  Inert today only because `xxxx` in a template is separately sanctioned
  (`ID_NAMING_STANDARDS.md:212-220`).
- ✅ **Fixed** (ELEMENT-ID-LAYER-CONTRACT-001, D-0067 / GD-09): founder chose
  option (a) — **delete the key**. `placeholder: "0000"` and its
  *"Template placeholder"* prose line removed from all five templates that
  carried it; deliberately NOT added to TDD, so no sixth copy was ever minted.
  Locked by `test_element_id_layer_contract.py::test_no_template_reintroduces_the_placeholder_key`.
  This overrode the merged plan's D4 deferral — see the plan's
  `## Implementation log`. Spec `0.38.0 → 0.39.0`.

### `[template]` `IDHASH-NORM-TEMPLATE-DRIFT` — ✅ CLOSED (2026-07-26) — 4 layer templates + 3 READMEs publish the pre-normalization hash input → [#343](https://github.com/vladm3105/aidoc-flow-framework/issues/343)

- *Context:* founder review 2026-07-26. D-0062 made the normalization transform
  normative (`ID_NAMING_STANDARDS.md:81-99`) but propagated it to
  `BRD-TEMPLATE.yaml:134-141` only. `PRD-TEMPLATE.yaml:106-109`,
  `EARS-TEMPLATE.yaml:96-99`, `BDD-TEMPLATE.yaml:91-94`,
  `ADR-TEMPLATE.yaml:101-104` and the BRD/PRD/EARS READMEs still print raw
  `{title}:{description}` — so a generator following them computes a *different*
  hash than the verifier. Undetected because `rehash --check` covers BRD §7 only,
  i.e. the one layer already fixed.
- ✅ **Fixed for the 7 framework surfaces** (ELEMENT-ID-LAYER-CONTRACT-001,
  D-0067 / GD-09): the re-specified 3-step algorithm is **deleted** from the PRD,
  EARS, BDD and ADR templates and the BRD/PRD/EARS READMEs, each replaced by the
  `norm()` shape line plus a cross-reference to `ID_NAMING_STANDARDS.md` as the
  single source — the BRD template's own instruction, applied everywhere. Each
  layer's "from *this* layer's content, NOT upstream" scoping clause is preserved,
  and each now also states that byte-exact field extraction is defined for BRD §7
  only. Locked by `tests/conformance/test_element_id_layer_contract.py`.
  Spec `0.38.0 → 0.39.0`.
- ↪ **Residual clauses transferred, not dropped:** `doc-tdd-fixer/SKILL.md`'s
  divergent `SHA256(case content)` → **#342** (which owns those exact lines and
  whose fix shape would discard any edit made here); the `.xxxx`-vs-`0000`
  secondary → **#352**, resolved in the same PR by deleting the key.

### `[template]` `TDD-ELEMENT-ID-SPEC-GAP` — ✅ CLOSED (2026-07-26) — TDD layer documents no element-ID format or hash algorithm → [#344](https://github.com/vladm3105/aidoc-flow-framework/issues/344)

- *Context:* founder review 2026-07-26. `ID_NAMING_STANDARDS.md:162-164` mandates
  element IDs for TDD, but `framework/layers/07_TDD/README.md` has no
  `## Element IDs` section and `TDD-TEMPLATE.yaml` has no `element_id` block —
  it uses `id: "TDD.NN.04.xxxx"` (lines 132/152/171/190) with no derivation, no
  `hash_algorithm`, no `placeholder`. All five sibling mandated layers have both.
  The only written TDD contract is a *platform* surface (`doc-tdd/SKILL.md:119`),
  inverting spec-owns-the-contract.
- ✅ **Fixed** (ELEMENT-ID-LAYER-CONTRACT-001, D-0067 / GD-09):
  `07_TDD/README.md` gains an `## Element IDs` section in its five siblings' form
  (format, the fixed `04` section segment for test cases, the `norm()` algorithm
  line, the standard as authority); `TDD-TEMPLATE.yaml`'s `id_standard` block
  gains the four keys plus the shape line. Both state explicitly what is **not**
  defined: a TDD case declares `name`/`spec_ref`/`target`/`test_file`/`test_function`
  and carries neither `title` nor `description`, so the field-extraction mapping is
  deferred to PROVISIONAL-IDS-002 Phase 2+ rather than invented here — PRD/EARS/BDD/ADR
  are in the identical position. `placeholder` was NOT added (see
  `IDPLACEHOLDER-UNDEFINED`). Locked by `test_element_id_layer_contract.py`.
  Spec `0.38.0 → 0.39.0`.

### `[ci]` `GITLEAKS-PRECOMMIT-GO-FLOOR` — ✅ CLOSED (2026-07-26) — the local gitleaks pre-commit hook could not install on Go < 1.21 and aborted every commit

- *Context:* 2026-07-26, while committing PRs #346/#347.
  `.pre-commit-config.yaml:82-85` pinned `gitleaks/gitleaks@v8.21.2`, a
  `language: golang` hook pre-commit builds from source; Go 1.19.8 rejects the
  module's `go 1.22.0` + `toolchain` directives, so the build always failed — at
  *install* time, which aborts the commit before any other hook runs. Local
  addition (`935befed`), not canon: canon's `pre-commit-hook-block.yaml` @
  `ci/v2.14.0` has no gitleaks entry and no sibling repo pins it. Redundant with
  `call / gitleaks` in CI (green throughout) + `detect-secrets` locally.
- ✅ **Fixed** ([#348](https://github.com/vladm3105/aidoc-flow-framework/issues/348)):
  hook dropped, replaced by a comment at the same location recording *why* there
  is no local gitleaks pass so it is not re-added. `CONTRIBUTING.md` gains a
  "Secret scanning — where each pass runs" table making the split explicit
  (`detect-secrets` local / `gitleaks` over full history in CI) and warning that
  a clean working tree can still fail the CI gate. `.gitleaks.toml` is untouched
  — it is what CI consumes.

### `[sync]` `HERMES-README-VERSION-DRIFT` — ✅ CLOSED (2026-07-10, HERMES-REVIEW-001 PR-DOCS) — `platforms/hermes/README.md` Version + framework-spec cells stale

- *Context:* Plugin `0.20.1` PATCH (2026-06-14) found and fixed the same
  drift class in `platforms/claude-code-plugin/README.md` (`0.6.3` →
  `claude-code-plugin/v<X.Y.Z>` canonical form). `platforms/hermes/README.md`
  carried the bug: `Version | 0.1.0` and `framework spec 0.1.0` (plus
  `pyproject.toml` frozen at `0.1.0` and the README `$ cat VERSION` /
  `$ cat FRAMEWORK_SPEC_VERSION` blocks).
- *Resolution (HERMES-REVIEW-001 PR-DOCS):* (a) canonicalized the hermes README
  Version cell to the `hermes/v<X.Y.Z>` tag form (already sync-covered); (b) added
  the hermes README `framework spec \`X\`` prose + `$ cat FRAMEWORK_SPEC_VERSION`
  awk sync to the framework-VERSION fanout block; (c) added `platforms/hermes/pyproject.toml`
  version + README `$ cat VERSION` awk sync to the hermes-VERSION fanout block. All
  stale `0.1.0` strings reconciled to the real `0.7.3` / spec `0.36.2`; future bumps
  auto-propagate.

### `[docs]` `FRWK-REVIEW-002-PR-E` — ✅ CLOSED (2026-07-09) — engine-agnosticism sweep

- Context: FRWK-REVIEW-002 PR-E — the spec carried engine-specific tokens (the
  playbook `agent:` field pointing into `platforms/claude-code-plugin/`;
  `doc-*`/"SKILL" vocabulary; a workspace-CI section; repo-root tool refs).
- Resolved: founder chose the **Hybrid** ruling, recorded as **GD-06** in
  `framework/governance/DECISIONS.md` (PR-E0 #284). PR-E-impl (#285) neutralized
  the generic vocabulary (doc-*/"SKILL" → engine-neutral, `claude -p` → neutral,
  AIDOC table → Platform-B illustration, tool paths → reference implementation)
  and kept the two sanctioned exceptions (the `agent:` executor field, softened;
  the workspace-CI section, scope-noted). Spec `0.36.0 → 0.36.2`.

### `[sync]` `SYNC-CLAUDE-PLUGIN-VERSION-GAP` — ✅ CLOSED (2026-07-09) — `sync-version-refs.sh` didn't update CLAUDE.md's plugin-version string

- Context: FRWK-REVIEW-002 PR-A/B bumped the plugin `0.23.2 → 0.23.4` but the
  `Current state` line in `CLAUDE.md` stayed at `0.23.2` — PR-G #281 fixed it by
  hand. The sync hook updated CLAUDE.md's framework-spec string but not the
  plugin-version string, so every plugin bump left it stale.
- Fixed: extended the `scripts/sync-version-refs.sh` plugin-version block to also
  rewrite the `Claude Code plugin \`X.Y.Z\`` token in `CLAUDE.md`(mirrors the
  framework-spec handling), and added a conformance guard
  (`test_claude_md_current_state_matches_plugin_version`) so re-drift fails CI.

### `[template]` `D54-F06-IPLAN-PROJECT-TYPES` — IPLAN hardcodes a Python source tree — ✅ CLOSED (2026-07-06, D-0054, spec 0.33.1)

- *Context:* D54 F-06. `IPLAN-TEMPLATE.yaml` still hardcodes
  `pytest/mypy/ruff`, `src/`, `tests/`; PR-E sub-types only split
  `code_build`/`deploy`/`combined`, not language/deliverable. Non-Python
  deliverables (plugin SKILL.md sets, managed infra) don't fit.
- *Fix shape:* **cross-reference `plans/IPLAN-LANG-001-PLAN.md`** (already
  drafted, PLANNED, not merged) — language-neutral template inheriting
  `language:`/`dependencies:` from SPEC. Revive + merge it; extend with
  non-code deliverable scaffolds (plugin/infra/docs) if SPEC-inheritance
  alone doesn't cover them. Do NOT duplicate the plan here.
- *Status:* ✅ **CLOSED (2026-07-06, `IPLAN-LANG-001-PLAN.md`, D-0054, spec 0.33.0 →
  0.33.1).** `IPLAN-TEMPLATE.yaml` example content is now language-neutral: `file_manifest`
  paths (§2) + `execution_commands` (§3) + the residual §5/§6 example paths use
  `<…, per the @spec language>` placeholders with labelled `# example (Python):` lines, and
  the `_guidance` instructs deriving the toolchain from `@spec: SPEC-NN` (SPEC owns
  `language:`/`dependencies:`). Inheritance, not a new IPLAN field; structural contract
  preserved (no validator/schema/conformance change). **Deferred residual:** non-code
  *deliverable scaffolds* (plugin SKILL.md sets / managed infra / docs) — SPEC-language
  inheritance covers the language axis; a dedicated deliverable-type scaffold is a separate
  item, surface it only if a non-code IPLAN actually needs one.

### `[lint]` `D54-F13-PHASE-SCOPE-RECONCILIATION` — no phase tag / no missing-downstream check — ✅ CLOSED (2026-07-06, D-0055, spec 0.34.0)

- *Context:* D54 F-13 (gap only — the underlying drift was a workflow
  error, not a framework defect). `trace_walk.py`/TRACE-RES-001 detect
  *orphans* (downstream→no upstream) but there is no *missing-downstream*
  check (accepted feature → no IPLAN) and no phase/scope-band tag.
- *Fix shape:* asymmetric, per author: "accepted feature has no IPLAN" =
  **warning** (legitimately mid-build; respects the completeness-check
  convention); "out-of-phase item leaked into an in-phase plan" (Phase-2
  SP in a Phase-1 IPLAN) = **blocking/high-severity** — a correctness
  defect, not incompleteness. Add a first-class phase tag on capability
  elements. The "scope ledger" is a *designated section of the existing
  BRD acceptance/index* (acceptance_criteria / launch_gates), NOT a new
  artifact — everything references it.
- *Status:* ✅ **CLOSED (2026-07-06, `D54-F13-PHASE-LEAK-PLAN.md`, D-0055, spec 0.33.1 →
  0.34.0).** The missing-downstream half shipped earlier as `COV01`; the phase-leak leg now
  ships as **`COV03`** — the inverse of COV01's escape: a `Future`-banded (deferred) FR that
  IS realized downstream draws an **advisory** (`warning`, both modes, never blocks; re-band
  P1/P2 or confirm the deferral). **No first-class phase tag was added** — grounding found it
  redundant with the existing FR band (`Future` = next-cycle) + the BRD-00 `Cycle` roadmap
  (later-cycle BRDs are trace-inert, so cross-cycle leaks are already structurally
  prevented). Canonical `tools/sdd_doc_lint` + both vendored mirrors; documented in
  TRACEABILITY.md §Coverage gates; 6 test cases; zero example-corpus findings.

### `[playbook]` `D54-F04-EARS-NONLATENCY-RUBRIC` — readiness rubric docks non-latency quantified bounds — ✅ CLOSED (2026-07-06, D-0057, spec 0.34.1)

- *Context:* D54 F-04. Syntax already flexes (`@threshold:` + cycle-based
  `WITHIN` + a `batch` category work), but the EARS-Ready checklist
  mandates `p50/p95/p99` and docks a quantified cycle/iteration/event-window
  bound for lacking percentiles.
- *Fix shape:* the rubric is the real work — broaden the EARS-Ready
  scoring criteria (`framework/layers/03_EARS/` + auditor playbook) to
  count a quantified non-latency bound as "quantified." No new syntax.
- *Status:* ✅ **CLOSED (2026-07-06, `D54-F04-EARS-RUBRIC-PLAN.md`, D-0057, spec 0.34.0 →
  0.34.1).** Reworded the four percentile-mandating surfaces in `EARS-TEMPLATE.yaml` (scoring
  weight, EARS-Ready checklist, antipattern, quality-attrs guidance + a new "Non-latency bound
  examples" table): **latency** → percentiles; **non-latency** (cycle/iteration/event-window/
  `*.count`) → concrete value + unit. Latency bar preserved; no new syntax. **Template-only**
  — the playbook lenses were already correct (`tech_lead.md` "any other quantified"), so the
  "+ auditor playbook" leg was unnecessary. Prose `_guidance` only (deterministic lint
  byte-identical); the corpus score improvement lands at the next wholesale regen.

### `[lint]` `ENG-FWD-COVERAGE` — no full-chain FORWARD coverage gate; single-upstream EARS hides built requirements — ✅ CLOSED (2026-07-06, CFB-PR-2, spec 0.24.0–0.30.0)

- *Context:* Engramory #7 (extends BeeLocal #54). Two implemented core
  requirements traced to NO IPLAN because the serving EARS lines carried
  only one `@brd:` each. `trace_walk.py` is BACKWARD-only (downstream →
  upstream orphan resolution); nothing asserts FORWARD that every BRD FR
  reaches ≥1 SPEC and ≥1 IPLAN. `ID_NAMING_STANDARDS.md:34-36` permits
  multi-`@brd:` at *document* level but not explicitly at EARS-*line* level,
  and no lint flags a BRD FR with zero downstream coverage.
- *Fix shape:* (a) a forward coverage report/GATE-CODE pre-check
  (`sdd_coverage`): resolve the `@`-tag graph, assert every BRD FR reaches
  ≥1 SPEC + ≥1 IPLAN, emit the full BRD→…→IPLAN matrix, list broken/empty
  downstream paths. **Severity is split (author):** a BRD FR explicitly
  marked `deferred:`/future-cycle with no IPLAN = **warning** (legitimately
  mid-build); an *in-scope* FR with no IPLAN at GATE-CODE = **block** (can't
  codegen an in-scope requirement with no plan); the **SPEC leg is stricter
  than the IPLAN leg** — a BRD FR reaching NO SPEC at all = **block** (the
  false-pass design gap the gate exists to catch). (b) Permit + encourage
  multiple `@brd:` per EARS line; lint any BRD FR with zero downstream EARS
  coverage. **Syntax (author):** repeated same-layer tags, pipe-delimited —
  `@brd: X | @brd: Z | @prd: Y`; `taglint` splits on `|`, parses each token
  as `@<layer>: <ID>`, OR-groups by layer. NOT comma lists (the EARS
  traceability antipattern already forbids commas/ranges — would collide
  with `D54-F07`). Backward-compatible: single-tag lines are the degenerate
  case. (c) Bind the gate at each layer's native granularity — element-level
  for BRD→…→ADR, **document-level** for SPEC/TDD/IPLAN (`@spec: SPEC-NN`,
  `@iplan: IPLAN-NN` are document-level by design), so the gate never
  depends on SPEC/IPLAN element IDs (keeps it non-conflicting with
  `ENG-SPEC-IPLAN-ID-EXEMPTION-NOTE`). (d) **Backward leg (BeeLocal #54/#10):**
  add a `coverage` section to the `SPEC-00` index template — each L3/L4
  (EARS/BDD) element → its covering SPEC or an explicit `deferred: <reason>`
  — plus a GATE-06 backward-coverage check flagging any EARS req / BDD
  scenario with no downstream SPEC/TDD, distinguishing *deferred* from
  *missed* (BeeLocal measured EARS-01 11/16, BDD-02 6/12 uncovered at
  element level, indistinguishable today). (e) The forward gate's emitted
  BRD→…→IPLAN matrix doubles as BeeLocal #52's "recommended generated
  `TRACEABILITY.md` matrix" (#8b — the cardinality *note* is already closed
  via CLEANUP-PR-F; only the generated matrix remained open).
- *Related:* the "every accepted feature → ≥1 IPLAN = warning" half is
  shared with `D54-F13-PHASE-SCOPE-RECONCILIATION`; one forward-coverage
  engine can serve both. Build once.
- *Status:* ✅ **CLOSED (verified 2026-07-06 against shipped code).** Delivered
  by the CFB-PR-2 coverage engine (spec 0.24.0–0.30.0). **Leg (a) forward gate =
  `COV01`** (`sdd_doc_lint/__init__.py` `_check_forward_coverage`): every in-scope
  (AUTHORED) BRD FR must reach ≥1 SPEC + ≥1 IPLAN corpus-wide, with the exact
  author-specified severity split (escaped/`deferred` FR never blocks; no-SPEC =
  error; SPEC-but-no-IPLAN = warning in `build` / error in `gate-code`); element
  granularity added by ELEMENT-COVERAGE-001 (spec 0.30.0). **Leg (d) backward =
  `COV02`** (`_check_backward_coverage`, corpus-wide, deferred-vs-missed split).
  **Leg (e) generated matrix = `docs/TRACEABILITY_MATRIX.md`** (`tools/sdd_coverage.py`).
  Residual: **the phase-leak row (DD-6 row 4)** is explicitly deferred in the COV01
  docstring — tracked under `D54-F13` (the phase-tag leg), not here.

### `[lint]` `LINT-DOCID-HEADER-FALSE-POSITIVE` — `_DOC_ID` scan flags `<TYPE>-<word>` header/filename tokens as ID02 — ✅ CLOSED (2026-07-06, D-0056)

- *Context:* surfaced by ENG-BRD-SKETCH-ROADMAP Pass-4 review. The ID02 doc-id scan
  matches any `<KNOWN-TYPE>-<token>` and flags it unless it is `TYPE-<digits>` (or,
  post-D-0043, ends in `-INDEX`). So legitimate prose tokens trip it: e.g.
  `BRD-00_index.TEMPLATE.md` carries ID02 on the `PRD-Ready` column header and the
  `BRD-TEMPLATE` quick-link. Pre-existing; orthogonal to the roadmap rows; harmless
  (templates aren't CI-linted) but a consumer's filled-in index keeps 2 standing ID02s.
- *Fix shape:* narrow the `_DOC_ID` malformed-id check — skip tokens inside
  inline-code / link targets / known header words, or require the doc-id to be a
  standalone token in a trace context. Needs care not to mask real malformed ids.
- *Status:* ✅ **CLOSED (2026-07-06, `LINT-DOCID-HEADER-FALSE-POSITIVE-PLAN.md`, D-0056).**
  ID02 now fires **only on a digit-leading second segment** (a valid doc-id is
  `TYPE-<digits>`, always digit-leading; a letter-leading `TYPE-<word>` is prose). Removes
  `PRD-Ready`/`BRD-TEMPLATE`/`BRD-NN` while keeping real malformed ids (`BRD-2`, `BRD-007x`);
  generalizes D-0043's `-INDEX` exemption. Pure `tools/sdd_doc_lint` bugfix (vendored to both
  mirrors) — **no `framework/` change, no version bump** (D-0043 precedent). New unit guard +
  166 conformance green. *(Chosen over the inline-code/link-context parse — that would miss
  the bare table-cell `PRD-Ready`.)*

### `[template]` `INDEX-UPSTREAM-RESIDUE` — stale cumulative `Upstream:` enumerations in layer index templates / READMEs — ✅ CLOSED (2026-06-30, spec 0.32.6 — P3 docs sweep)

- *Context:* CFB-PR-1 (PR #180) migrated cumulative→necessary-upstream across
  ~20 surfaces, but its V6 grep keyed on the literal "cumulative" and missed the
  per-layer **`Upstream:` enumerations** in the layer index templates / READMEs.
  Concrete: `framework/layers/06_SPEC/SPEC-00_index.TEMPLATE.md:27` declares
  `Upstream: BRD, PRD, EARS, BDD, ADR` (the old full chain) where SPEC's
  `required_tags` is `[ears, bdd, adr]`; `:29` carries the full-chain line. The
  other layer index templates likely carry the same.
- *Fix shape:* sweep the `NN_*/<TYPE>-00_index.TEMPLATE.*` + layer READMEs;
  correct each `Upstream:` line to the registry `required_tags`. Same class as
  CFB-PR-1; doc-only. (CFB-PR-2 2b fixes the SPEC-00 two lines in-passing while
  it's open; this entry tracks the cross-layer sweep.)
- *Status:* SHIPPED (spec 0.32.6, 2026-06-30 — P3 docs sweep). Corrected the 5
  stale `Upstream:` lines in EARS/BDD/ADR/TDD-00 index templates to
  necessary-upstream (SPEC-00/PRD-00 were already correct). **Template-side only** —
  the example corpus has no layer index (only `09_CHG/CHG-00_index.md`), so the
  wholesale corpus regen does NOT touch this (earlier banner/runbook mischaracterized
  it as corpus-side — corrected).

### `[template]` `D54-F12-AGENTIC-ANTIPATTERNS` — BRD/PRD business-vs-technical boundary fuzzy for AI-agent systems — ✅ CLOSED (2026-06-30, spec 0.32.6 — P3 docs sweep)

- *Context:* D54 F-12. BRD/PRD antipatterns are CRUD-flavored; no agentic
  example distinguishing "independent review stage" (business) from
  "multi-stage agent pipeline w/ timeouts" (architecture).
- *Fix shape:* add agentic/AI-system examples to the BRD/PRD
  `_antipatterns` business-vs-technical lists (resolve via C4 altitude).
  Cheap docs/template fix.
- *Status:* SHIPPED (spec 0.32.6, 2026-06-30 — P3 docs sweep). Added an agentic
  FAIL/PASS pair to BRD `_antipatterns` (agent-topology = architecture, not business
  value) and PRD `_antipatterns` (pipeline topology/timeouts = ADR/SPEC, not
  Container product behavior).

### `[docs]` `ENG-BRD-SKETCH-ROADMAP` — no project-init roadmap + BRD "sketch" sub-form — ✅ CLOSED (2026-06-30, D-0044, spec 0.32.5)

- *Context:* Engramory #1 (extends the "author current cycle full, stub the
  rest" practice). Authoring only `BRD-01` full + index one-liners leaves
  whole-project scope under-specified before cycle 1. `BRD-00_index` already
  has an optional "Planned BRDs" table and `@depends:` chaining exists, but
  there is no scope-only "sketch" form: `BRD-TEMPLATE.yaml:179` status is
  only `Draft|In Review|Approved`, and a scope-only future-cycle BRD would
  fail lint as an incomplete full BRD.
- *Fix shape (author scoped to docs-only now; lint deferred):* (a) document
  a project-initiation step (README + `01_BRD/README.md`): enumerate all MVP
  cycles **by extending the existing `BRD-00_index` "Planned BRDs" table**
  with cycle / PROD / `@depends:` columns (its natural home — avoids
  colliding with a consumer's top-level `ROADMAP.md` product-strategy file);
  *recommend* the BRD-layer location, do NOT mandate a path. (b) Add a
  `status: Sketch` value for scope-only future-cycle BRDs (document_control,
  introduction, business_objectives hypothesis, project_scope only). (c) A
  sketch is **trace-inert**: carries only its document-level `BRD-NN` +
  `@depends:` for sequencing — no element IDs, not in the `@`-tag graph,
  ignored by `ENG-FWD-COVERAGE`; on graduation to a full BRD it gets element
  IDs + enters the graph. (d) Add a `SKETCH-001` lint (forbid downstream
  content / element IDs on a Sketch) **only if** over-authoring drift shows
  up in practice — deferred to keep this out of MINOR territory.
- *Status:* SHIPPED (spec 0.32.5, 2026-06-30 — `ENG-BRD-SKETCH-ROADMAP-PLAN.md`,
  D-0044). The `BRD-00` index "Planned BRDs" table is the roadmap home (extended
  with cycle/PROD/`@depends:`/status `Planned|Sketch`); `01_BRD/README.md` documents
  the project-init enumeration step + the trace-inert Sketch concept; cross-ref in
  `BRD-TEMPLATE.yaml`. Built on STRUCT01-INDEX-EXEMPTION (D-0043). **Deferred
  follow-ons** logged below: standalone Sketch-file lint support; the `_DOC_ID`
  header/filename false-positive.

### `[template]` `ENG-PLATFORM-ADR-TIMING` — "ADRs created BEFORE PRD" wording conflicts with cumulative-tag chain — ✅ CLOSED (2026-06-30, spec 0.32.6 — P3 docs sweep)

- *Context:* Engramory #5 (resolves BeeLocal #40 by clarification).
  `BRD-TEMPLATE.yaml:101` (platform-BRD guidance): "ADRs created BEFORE PRD
  to validate architectural decisions." Read literally this conflicts with
  the chain — an ADR carries `@ears`/`@bdd`, which can't exist pre-PRD.
- *Fix shape:* reword: author ADRs in sequence (after BDD) so they carry
  the full cumulative chain; "decided before PRD" refers to decision
  *provenance* (recorded in the ADR's `context`/`originating_topic`), not
  authoring *order*. **Confirmed pure wording fix — no platform-ADR-first
  workflow variant (author Q8):** Engramory authored in strict layer order,
  ADRs carried full `@ears`/`@bdd`, #40 never bit; their 5 ADRs were
  converted from prior design decisions but still authored in-sequence.
  **BeeLocal #40 adds a PRD-layer manifestation:** `PRD-TEMPLATE`
  traceability says "Do NOT reference specific ADR numbers — ADRs don't
  exist yet" and frames `adr_topic_elaboration` as "options for ADR to
  evaluate" — backwards for a platform PRD whose ADRs are already decided.
  Add a platform-flow note to the PRD template too (a platform PRD MAY cite
  existing ADRs). Same clarification, second surface.
- *Status:* SHIPPED (spec 0.32.6, 2026-06-30 — P3 docs sweep). Reworded the
  platform-BRD ADR-timing line (decisions DECIDED before PRD = provenance; ADR
  *documents* still AUTHORED in-sequence so they carry the full upstream chain) +
  added the platform-flow exception to `PRD-TEMPLATE` traceability +
  `adr_topic_elaboration` (a platform PRD MAY cite already-decided ADRs).

### `[template]` `BL-READY-SCORE-ADVISORY` — `*_ready_score` placeholders read as a required gate — ✅ CLOSED (2026-06-30, D-0042, spec 0.32.4)

- *Context:* BeeLocal #56 (52 occurrences). Every ADR/SPEC/TDD ships
  `*_ready_score: [Score]/100` + `target_score: ">=90/100"`, which reads as
  a required gate, but the score is **advisory** — the deterministic lint
  floor is the real gate and the score is computed by the auditor lens, not
  hand-authored. A blank field makes a finished set look half-done.
- *Fix shape (author Q4 — mark-advisory, do NOT build a rubric):* mark the
  field explicitly advisory in every template (`_note: "Computed by the
  auditor lens; authoring this is advisory — a blank value is NOT
  incomplete"`) and reword `target_score` so it reads as a readability
  threshold, not a gate. **No offline rubric/tool** — that would contradict
  `D54-F03` (the audit skill IS the rubric; the deterministic floor is
  `sdd_doc_lint`).
- *Status:* SHIPPED (spec 0.32.4, 2026-06-30 — `BL-READY-SCORE-ADVISORY-PLAN.md`,
  D-0042). All 7 layer templates (BRD…TDD) marked: inline `#` comment on each of the
  14 score lines + one `_note:` per `health_score` block + **15 reworded
  `_guidance` prose lines** that still framed the score as "required"/a "quality
  gate" (ai-review caught the contradiction on impl PR #222 — plan Pass 3); PATCH
  0.32.3 → 0.32.4. No rubric (author Q4). The "52 occurrences" was BeeLocal's
  per-artifact tally; the template fix is 14 field lines + 15 prose lines. IPLAN/08
  carries neither field, so "all 7" = 01–07.

### `[lint]` `STRUCT01-INDEX-EXEMPTION-NESTED` — ✅ CLOSED (2026-06-30) — index/registry templates never hit the STRUCT01/trace `-INDEX` exemption

- *Discovered:* 2026-06-30 by the ENG-BRD-SKETCH-ROADMAP plan's independent review.
  The STRUCT01 required-section exemption + the trace-resolution INDEX skip both read
  a **top-level** `artifact_type` ending in `-INDEX`, but the 7 `.md` layer index
  templates nest `artifact_type` under `custom_fields` (6 with a bare value) and the
  IPLAN-00 registry is a `.yaml` with no `---` frontmatter — so the exemption never
  fired and a consumer's copied index threw STRUCT01 errors (BRD-00: 17). The
  `-INDEX` token also self-tripped the ID02 doc-id scan.
- ✅ **Fixed** (STRUCT01-INDEX-EXEMPTION, D-0043): filename-based `_is_index_doc`
  (`<TYPE>-00_index`) used in both exemptions + ID02 skips `-INDEX` tokens; all 8
  index templates (incl. the `.yaml`) lint clean; new conformance guard
  `test_index_template_lint.py`. Pure linter fix, no spec bump.
  Plan: `plans/STRUCT01-INDEX-EXEMPTION-PLAN.md`.

### `[template]` `ENG-SPEC-IPLAN-ID-EXEMPTION-NOTE` — element-ID exemption lives only in the standard, not the templates — ✅ CLOSED (2026-06-29, spec 0.32.1)

- *Context:* Engramory #4. `ID_NAMING_STANDARDS.md:64-98` documents that
  SPEC §5/§3 and IPLAN §4/§2 MAY omit layer-local element IDs, but
  `SPEC-TEMPLATE.yaml` / `IPLAN-TEMPLATE.yaml` are silent — an author
  reading only the template may over-assign IDs (noise) or worry they're
  missing required ones. Follow-on to the closed item that *added* the
  exemption to the standard (CLEANUP-PR-C).
- *Fix shape:* add a one-line `_note` in SPEC §5/§3 and IPLAN §4/§2
  template guidance cross-referencing the exemption; **keep the exemption**
  (author Q7 — do NOT require element IDs everywhere; that would reintroduce
  the second-naming-surface the standard created the exemption to avoid).
  Non-conflicting with `ENG-FWD-COVERAGE`: that gate binds SPEC/TDD/IPLAN at
  *document* level, so it never relied on their element IDs. Keep the
  standard authoritative; the template just cross-references it.
- *Status:* SHIPPED (spec 0.32.1, 2026-06-29) — cross-ref `_note` added to SPEC §3/§5 + IPLAN §2/§4 template guidance; exemption unchanged.

### `[docs]` `ENG-IPLAN-REGISTRY-README` — registry-vs-document schema distinction undocumented in the layer README — ✅ CLOSED (2026-06-29, spec 0.32.2)

- *Context:* Engramory #3. `IPLAN-00_index` is `document_type:
  iplan-registry` (no `document_control`); `IPLAN-NN_*` are
  `iplan-document`. A naive "validate every `08_IPLAN/IPLAN-*.yaml`" glob
  trips on the registry. `sdd_doc_lint` ALREADY special-cases INDEX docs
  (`__init__.py:927-969`, `:836-850`) — so only the *author-facing note* is
  missing.
- *Fix shape:* one-line note in `08_IPLAN/README.md` that registry vs
  document are distinct schemas + how each is validated (lint exempts
  `artifact_type: *-INDEX`). Docs-only.
- *Status:* SHIPPED (spec 0.32.2, 2026-06-29) — 'Index registry vs document schema' section added to 08_IPLAN/README.md.

### `[docs]` `BL-BRD-SET-WORDING` — "each BRD = one cycle" misreads as one-BRD-per-cycle — ✅ CLOSED (2026-06-29, spec 0.32.3 — BeeLocal docs sweep)

- *Context:* BeeLocal #34. `01_BRD/README.md:6,34` says "Each BRD represents
  ONE iteration cycle." Platform/feature BRD typing
  (`BRD-TEMPLATE.yaml:95-109`) + `@depends:` already support a BRD *set* per
  cycle (one platform BRD + child feature BRDs), but the wording hides it —
  caused real BeeLocal planning confusion.
- *Fix shape:* reword to "each BRD *set* (platform + its feature BRDs) = one
  iteration cycle" + add a parent/child tree example. Docs-only; ties to
  `ENG-BRD-SKETCH-ROADMAP` (same BRD-00/cycle area).
- *Status:* SHIPPED (spec 0.32.3, 2026-06-29 — BeeLocal docs sweep).

### `[docs]` `BL-SIZE-UNITS` — section `_size_target` in words vs document cap in tokens — ✅ CLOSED (2026-06-29, spec 0.32.3 — BeeLocal docs sweep)

- *Context:* BeeLocal #41a. Section `_size_target` values are WORDS
  (`BRD-TEMPLATE.yaml:171` `100 # words`, …) and `AUTHORING_STYLE.md:62-69`
  targets are words, but the document split cap is 50,000 TOKENS
  (`BRD-TEMPLATE.yaml:117-118`). Mixed units, no stated relationship.
- *Fix shape:* one clarifying note (in `AUTHORING_STYLE.md` or the template
  size guidance) stating the two units' relationship — section targets are
  authoring guidance in words; the 50k-token cap is the split trigger.
- *Status:* SHIPPED (spec 0.32.3, 2026-06-29 — BeeLocal docs sweep).

### `[template]` `BL-VENDOR-NAME-SCOPE` — "no vendor names" rule collides with `recommended_selection` — ✅ CLOSED (2026-06-29, spec 0.32.3 — BeeLocal docs sweep)

- *Context:* BeeLocal #41b. `adr_topics` guidance
  (`BRD-TEMPLATE.yaml:615-617`) says "use business capability descriptions,
  not vendor names (FAIL: MUST use PostgreSQL)" — yet `recommended_selection`
  is exactly where the chosen vendor goes. The rule's scope is unstated.
- *Fix shape:* clarify the rule applies to titles/`business_driver` (stay
  business-level) but vendor names ARE allowed in `recommended_selection`
  (the decision record). One-line template note.
- *Status:* SHIPPED (spec 0.32.3, 2026-06-29 — BeeLocal docs sweep).

### `[sync]` `BUMP-SKILL-AUTHORING-CHECKLIST-STRAGGLER` — ✅ CLOSED (2026-06-29) — `bump_version.py` misses the SKILL_AUTHORING acceptance-checklist line

- ✅ **Fixed:** `bump_version.py` now sweeps any unanchored
  `framework_spec_version: "X"` in `SKILL_AUTHORING.md` (idempotent), catching
  the backtick-wrapped §6 checklist line; the current stale `0.27.0` value
  corrected to `0.30.0`.
- *Context:* recurred in CFB-PR-2 2a-core step 6 (0.23.1→0.24.0) AND 2b step 3
  (0.24.0→0.25.0). `SKILL_AUTHORING.md:112` (`- [ ] … framework_spec_version:
  "X" present.`) is a backtick-wrapped checklist line, not the `^…
  framework_spec_version: "…"` frontmatter form `bump_version.bump_fsv` matches,
  so every framework bump leaves it stale (fixed by hand each time). Author-facing
  (a skill author following the checklist asserts the wrong value).
- *Fix shape:* extend `bump_version.py` (a `bump_plugin_readme`-style targeted
  rewrite for the SKILL_AUTHORING checklist line), or add a conformance guard
  asserting the checklist version == `framework/VERSION`.

### `[harness]` `RELEASE-CHANGELOG-TEST-CONVENTION-GAP` — ✅ CLOSED (2026-06-29) — `tests/release/test_changelog_entry.py` doesn't match the `[Unreleased]` convention

- ✅ **Fixed:** the test now accepts the current version in EITHER a released
  `## [X.Y.Z]` heading OR an `[Unreleased]` `### … <version>` subsection heading
  (matches the version in any level-2/3 heading, trailing-boundary guarded).
  3/3 release tests green.
- *Context:* surfaced in CFB-PR-2b self-review. The test requires a top-level
  `## [<version>]` heading, but the repo nests releases under `## [Unreleased]`
  with `### Added — Framework Spec X → Y`. It is RED at HEAD for `0.25.0` (and on
  `main` for `0.24.0`) — but **outside CI scope** (conformance.yml runs only
  `tests/conformance`; hermes.yml runs pytest under `platforms/hermes`), so CI
  stays green. Pre-existing, not a 2b regression.
- *Fix shape:* update the test to recognize the `[Unreleased]` + `### … X → Y`
  convention, or move release entries to top-level `## [X]` headings on release.

### `[governance]` `BL-TAG-CHAIN-GATE-SYNC` — stale cumulative-tag docs contradict the necessary-upstream contract — ✅ CLOSED (2026-06-27, PR #180, `8e001192`)

- *Context:* BeeLocal #53. The author flagged that SPEC/TDD carry only
  `@adr,@bdd,@ears` and IPLAN only `@spec,@tdd`, "contradicting GATE-08-E003."
  **The templates are CORRECT** — NECESSARY-UPSTREAM-001 (PR #121) deliberately
  replaced the old cumulative chain (immediate-upstream only; the cumulative
  form caused trace-fabrication). The real defect is the OPPOSITE of the
  author's proposed fix: `GATE-08_IPLAN.md:222-231` (E003 *resolution*
  example) and `TRACEABILITY.md:9-24` (cumulative-tags diagram) are STALE —
  they still show the old full chain, contradicting `LAYER_REGISTRY.yaml`
  `required_tags` + the live templates.
- *Fix shape:* do NOT re-add cumulative tags to SPEC/TDD/IPLAN templates.
  Instead correct the two stale docs to the necessary-upstream contract:
  fix the `GATE-08-E003` resolution example to `[spec, tdd]` and resync the
  `TRACEABILITY.md` chain diagram to immediate-upstream. The corrected
  diagram MUST state the transitive path **explicitly** (PRD/BRD reachable
  by walking ADR/BDD/EARS→PRD→BRD, not via L6+ local tags), and point the
  reverse lookup ("which BRD is SPEC-07?") at the generated `TRACEABILITY.md`
  matrix (`ENG-FWD-COVERAGE` (e)) so nobody re-files it as a gap.
- *Confirmed (author Q1):* BeeLocal's chain verified clean with exactly this
  contract — SPEC `@adr/@bdd/@ears`, TDD `@spec/@bdd/@ears`, IPLAN `@spec/@tdd`
  only, zero dangling refs. GATE-08-E003 requiring `@brd+@prd` is the bug,
  not the templates. Do NOT re-add cumulative tags.
- *Status:* **CLOSED** — 2026-06-27, squash `8e001192` (PR #180), as
  **CFB-PR-1** (CONSUMER-FEEDBACK-001). Expanded during implementation from the
  2 named docs to the **full ~20-surface cumulative→necessary-upstream
  reconciliation** (the V6 grep + independent review surfaced the stale model
  across EARS/BDD templates, GATE-03 + error catalog with FALSE `required_tags`
  claims, 3 layer READMEs, BDD-00 index, DEFINITION_OF_DONE, the ADR + IPLAN
  auditor playbooks, the guides, and the `AI_ASSISTANT_RULES` live author-facing
  bug). Framework spec 0.23.0 → 0.23.1; plugin VERSION unchanged. See
  `plans/CFB-PR-1-TAG-CHAIN-GATE-SYNC-PLAN.md` Pass-4 log.

### `[skill]` `MODEL-PRECHECK-ROLLOUT` — autopilots print the per-layer model recommendation — ✅ CLOSED (2026-06-22, PR #164, `6700301f`)

- *Context:* `commands/model.md` documented a `model.precheck` mode the
  `doc-*` skills "consult," but no skill did — a documented-but-unimplemented
  behavior introduced by PLUGIN-USER-COMMANDS.
- *Resolution:* MODEL-PRECHECK-ROLLOUT (PR #164, merge `6700301f`). The 8 layer
  autopilots gained a `## Model precheck` section (before `## Workflow`) that
  reads `model.per_layer`/`model.default`/`model.precheck` from
  `.claude/aidoc-flow.config.yaml` and **prints** the recommendation + the
  `/model <rec>` command (no compare — a skill can't read its own session
  model). `warn`/`silent`/`block` modes; Step-1 saga directive reworded to
  "first orchestration action" so the notice runs before the driver. New
  `tests/conformance/platforms/test_model_precheck.py`; `commands/model.md` +
  `docs/CONFIG.md` mode descriptions corrected to print-not-compare. Plugin
  `0.21.0 → 0.22.0`; no framework-spec change. Scope locked autopilots-only
  (D-0035); base/audit/fixer deferred (headless under the driver). Converged
  Pass 1-7 + independent diff review (caught the stale `commands/model.md`
  wording). See `plans/MODEL-PRECHECK-ROLLOUT-PLAN.md`.

### `[skill]` `SAGA-PARITY-001-PHASE-4` — 6 layer autopilots now saga-driven — ✅ CLOSED (2026-06-22, PR #161, `f277ea1a`)

- *Context:* Only `doc-brd/prd/chg-autopilot` invoked `tools/saga_driver.py`;
  the 6 layer autopilots `doc-{ears,bdd,adr,spec,tdd,iplan}-autopilot` still
  described a legacy in-session `## Workflow`. The acceptance harness shells
  the driver directly per layer (`test-acceptance.sh:1139`), masking the
  divergence — a user-invoked `/aidoc-flow:doc-bdd-autopilot` ran an untested
  path. Surfaced 2026-06-21 while reviewing MODEL-PRECHECK-ROLLOUT.
- *Resolution:* SAGA-PARITY-001 Phase 4 (PR #161, merge `f277ea1a`). Each of
  the 6 `## Workflow` sections rewritten to the proven `doc-prd-autopilot`
  two-subsection shape (`### Saga-driven generation loop (team)` invoking
  `saga_driver.py --layer <NN_TYPE>` + `### Linear Pipeline (single_pass)`
  verbatim); `review_mode` added to the 6 SKILLs' `adapts:` + reconciled into
  `doc-prd-autopilot`; new `tests/conformance/platforms/test_autopilot_saga_parity.py`
  (8×3 subtests + a dangling-cross-ref guard). Plugin `0.20.1 → 0.21.0`; no
  framework-spec change. Plan converged Pass 1-3 (independent Pass 2);
  independent diff review caught + fixed a Step-3 dangling cross-reference.
  See `plans/SAGA-PARITY-001-PHASE-4-PLAN.md`.

### `[example-corpus]` url-shortener corpus regen → all 6 layers PASS — ✅ CLOSED (2026-06-10, PR #125, `90f37002` + PR #127, `c56c386f`)

- *Resolution:* TRACE-RES-FIXUP-001 (PR #125, merge `90f37002`) + IPLAN-RT-001
  (PR #127, merge `c56c386f`). Cascade scores: PRD 92 / EARS 94 / BDD 91 /
  ADR 96 / SPEC 97 / TDD 90 / IPLAN 100. Post-cascade review (2026-06-11)
  surfaced 9 NEW framework-improvement items, captured above as Open
  entries for FRAMEWORK-CLEANUP-001 triage.

### `[harness]` Cascade harness lacks `--skip-lint-smoke` flag for migration scenarios — ✅ CLOSED (2026-06-11, PR #129, `79b91d0e`)

- *Context:* TRACE-RES-FIXUP-001 cascade (2026-06-10) needed
  `SDD_LINT_SKIP_TRACE_RES=1` env-var bypass to run against the legacy
  url-shortener corpus before the new contract was applied.
- *Fix shape:* add `--skip-lint-smoke` flag to `tests/scripts/test-acceptance.sh`
  Phase 0 so migration runs can defer lint until after the corpus is
  regenerated. Removes the need for per-rule env-var bypasses.
  *Resolution:* CLEANUP-PR-A (PR #129, merge `79b91d0e`) — first child PR of FRAMEWORK-CLEANUP-001. See `plans/CLEANUP-PR-A-HARNESS-LINT-PLAN.md` for impl details.

### `[harness]` Tree-safety check requires `--force` after pre-cleanup; plan templates don't surface this — ✅ CLOSED (2026-06-11, PR #129, `79b91d0e`)

- *Context:* TRACE-RES-FIXUP-001 first cascade attempt (2026-06-10) aborted
  in 30s at Phase 0 "tree-safety FAIL" because `rm -rf` of legacy artifacts
  created unstaged deletions. Five-pass plan review missed this. Re-run
  with `--force` succeeded.
- *Fix shape:* either (a) document the cleanup-then-`--force` pattern in
  the cascade-rebuild section of plans that touch `examples/<NAME>/`,
  or (b) auto-stage the cleanup in the harness so the safety check sees
  a clean tree.
  *Resolution:* CLEANUP-PR-A (PR #129, merge `79b91d0e`) — first child PR of FRAMEWORK-CLEANUP-001. See `plans/CLEANUP-PR-A-HARNESS-LINT-PLAN.md` for impl details.

### `[lint]` `sync-vendored.sh` and `sync-plugin-framework.sh` are two separate sync mechanisms; easy to confuse — ✅ CLOSED (2026-06-11, PR #129, `79b91d0e`)

- *Context:* TRACE-RES-FIXUP-001 Task 2 (2026-06-10) and earlier
  NECESSARY-UPSTREAM-001 (PR #121): I edited the vendored lint module,
  ran `sync-plugin-framework.sh`, and the edit was overwritten because
  that script syncs `tools/sdd_doc_lint/` → vendored copies (treating
  `tools/` as canonical), not the reverse. The lint module's canonical
  source is `tools/sdd_doc_lint/__init__.py`; the vendored copies under
  `platforms/<name>/sdd_doc_lint/` are byte-identical mirrors.
- *Fix shape:* either (a) consolidate to one sync script that knows the
  direction per directory, or (b) add a top-of-file comment to each
  vendored module declaring "DO NOT EDIT — synced from tools/...". A
  brief CONTRIBUTING.md note next to the existing sync-script docs
  would also help.
  *Resolution:* CLEANUP-PR-A (PR #129, merge `79b91d0e`) — first child PR of FRAMEWORK-CLEANUP-001. See `plans/CLEANUP-PR-A-HARNESS-LINT-PLAN.md` for impl details.

### `[skill]` Auditor + fixer SKILLs emit unescaped `|` inside backtick code spans in table cells (MD056) — ✅ CLOSED (2026-06-11, PR #129, `79b91d0e`)

- *Context:* IPLAN-RT-001 live cascade (2026-06-10) produced
  `examples/url-shortener/.aidoc/audit/08_IPLAN-audit.md:105` and
  `.aidoc/review/08_IPLAN/IPLAN-01/IPLAN-01.F_fix_report_v001.md:50`
  containing rows where a `docker compose ps | grep 'Up'` code span
  inside a table cell has its shell pipe treated by markdownlint as a
  column separator, tripping MD056 (column-count mismatch). Pre-commit
  hook blocked impl commits on cascade output.
- *Fix shape:* update audit + fixer SKILL prompts to escape `|` inside
  code spans within markdown table cells (use `\|` or move the code
  span to a paragraph reference). Until then, `examples/<name>/.aidoc/`
  is excluded from the pre-commit markdownlint hook (workflow-gap fix
  landed in IPLAN-RT-001 commit).
  *Resolution:* CLEANUP-PR-A (PR #129, merge `79b91d0e`) — first child PR of FRAMEWORK-CLEANUP-001. See `plans/CLEANUP-PR-A-HARNESS-LINT-PLAN.md` for impl details.

### `[governance]` Iteration cap for the quality loop is implementation-bound, not spec-bound — ✅ CLOSED (2026-06-11, PR #130, `60f72a5e`)

- *Context:* `REVIEW_REMEDIATION_FLOW.md` defines the quality loop as
  "Draft → Review → (Remediate → Re-review)* → Gate Pass" and states
  *"the loop repeats until the gate passes"* — open-ended. But the cap
  is hard-coded at `tools/saga_driver.py:125` `MAX_ITERATIONS = 3` (and
  default threshold 90). No `ADAPTATION_SURFACE.yaml` knob exposes this;
  the spec gives no guidance on default cap or how to tune it per layer
  / project.
- *Fix shape:* either (a) elevate the iteration cap to spec — declare a
  default in `REVIEW_REMEDIATION_FLOW.md` or `REVIEW_SAGA.md` and expose
  it via `ADAPTATION_SURFACE.yaml` (e.g. `quality_loop.max_iterations:
  3`, tunable per project) — or (b) leave it as a platform implementation
  detail but explicitly document that in the spec so consumers know to
  consult their platform's docs for the cap. Either way, the framework
  shouldn't have a silent implementation-bound cap that the spec is
  unaware of. Discovered while observing the TRACE-RES-FIXUP-001 corpus
  regen cascade (2026-06-10): PRD-01 converged in iter-2 (PASS 92),
  EARS-01 in iter-2 (PASS 94); both ran the loop until gate passed,
  consistent with spec — but the silent 3-iter ceiling means
  near-convergent artifacts (89/90) end up `PARTIAL_TIMEOUT` instead of
  one-more-cycle.
  *Resolution:* CLEANUP-PR-C (PR #130, merge `60f72a5e`) — second child PR of FRAMEWORK-CLEANUP-001. See `plans/CLEANUP-PR-C-SPEC-REGISTRY-PLAN.md` for impl details.

### `[registry]` `@threshold:` 3-segment keys vs element-ID 4-segment pattern — ✅ CLOSED (2026-06-11, PR #130, `60f72a5e`)

- *Context:* `LAYER_REGISTRY.yaml` `id_patterns.element` regex covers
  the 4-segment hash form `TYPE.NN.SS.xxxx`. But threshold keys use a
  3-segment form `PRD.01.perf.redirectp95`. The current `sdd_doc_lint`
  cannot distinguish a legitimate threshold from a malformed 3-segment
  element ID — a hand-edit introducing `PRD.01.perf.typo` would slip
  past validation.
- *Fix shape:* add a `threshold` ID pattern to `LAYER_REGISTRY.yaml`
  `id_patterns:`; extend `sdd_doc_lint` to validate the new namespace.
  Coordinate with the `[gate] Threshold-binding gate` entry above.
  *Resolution:* CLEANUP-PR-C (PR #130, merge `60f72a5e`) — second child PR of FRAMEWORK-CLEANUP-001. See `plans/CLEANUP-PR-C-SPEC-REGISTRY-PLAN.md` for impl details.

### `[template]` SPEC + IPLAN declare no layer-local element IDs — ✅ CLOSED (2026-06-11, PR #130, `60f72a5e`)

- *Context:* url-shortener review (2026-06-11) — `SPEC-01.md` and
  `IPLAN-01.md` carry no `SPEC.NN.SS.xxxx` or `IPLAN.NN.SS.xxxx`
  element IDs (only upstream `@adr`/`@tdd` refs + Protocol method
  names). Templates `SPEC-TEMPLATE.yaml` / `IPLAN-TEMPLATE.yaml` do
  not require any. If a downstream consumer ever needs to cite an
  individual SPEC rule (e.g. "the §5 fail-closed rule") or an
  individual IPLAN step, they have no element ID to bind to.
- *Fix shape:* either (a) require element IDs at SPEC §5 rules and
  IPLAN §4 contracts via template + auditor lens, or (b) document the
  deliberate exemption in `ID_NAMING_STANDARDS.md` so future authors
  know it's intentional.
  *Resolution:* CLEANUP-PR-C (PR #130, merge `60f72a5e`) — second child PR of FRAMEWORK-CLEANUP-001. See `plans/CLEANUP-PR-C-SPEC-REGISTRY-PLAN.md` for impl details.

### `[template]` EARS emits per-line `@bdd:` downstream slots — direction-of-flow violation — ✅ CLOSED (2026-06-11, PR #130, `60f72a5e`)

- *Context:* url-shortener review (2026-06-11) — `EARS-01.md:68, 73, 81 etc.`
  emit per-line `@bdd: BDD-01` slots BEFORE the downstream BDD exists.
  These work as downstream slots but bypass the necessary-upstream
  contract direction (upstream-only).
- *Fix shape:* either (a) drop per-line `@bdd:` slots from EARS and
  rely on BDD's reverse `@ears:` tags for the trace (cleaner direction),
  or (b) declare downstream-slot semantics officially in
  `LAYER_REGISTRY.yaml` so the contract names them.
  *Resolution:* CLEANUP-PR-C (PR #130, merge `60f72a5e`) — second child PR of FRAMEWORK-CLEANUP-001. See `plans/CLEANUP-PR-C-SPEC-REGISTRY-PLAN.md` for impl details.

### `[plan-review]` Plan reviews should cross-check claims against the example corpus, not only test fixtures — ✅ CLOSED (2026-06-11, PR #131, `1f28cc16`)

- *Context:* NECESSARY-UPSTREAM-001 (PR #121) Pass 4 verified
  TRACE-RES-001 against `tools/sdd_doc_lint/fixtures/` but **not**
  against `examples/url-shortener/docs/`. The latter carried 107 orphan
  `@prd:` tags that broke the TDD-RT-001 cascade. The plan's
  "backwards compatibility" claim was wrong because the corpus
  cross-check was missing.
- *Fix shape:* update the plan-review templates / verified-planning
  skill to require, when a plan changes lint rules or @-tag semantics,
  a `python3 -m sdd_doc_lint examples/<NAME>/docs/` smoke run as a
  mandatory Pass-N check. Catches corpus drift before merge.
  *Resolution:* CLEANUP-PR-B (PR #131, merge `1f28cc16`) — third child PR of FRAMEWORK-CLEANUP-001 (heart). See `plans/CLEANUP-PR-B-REVIEW-CALIBRATION-PLAN.md` for impl details.

### `[skill]` doc-tdd auditor C4 inter-section consistency may be over-strict (or the cascade-produced TDD-01 has a real inconsistency) — ✅ CLOSED (2026-06-11, PR #131, `1f28cc16`)

- *Context:* TDD-RT-001 live cascade (2026-06-09) finished with
  `content_score 89`; one P2 finding cited "§1 line 30 (cumulative
  upstream tags header) vs §3 lines 89-90 and §7 line 206". The §1 line
  was correctly `@ears | @bdd | @adr | @spec` per the new contract;
  inconsistency was elsewhere. Not investigated.
- *Fix shape:* run a focused diagnostic on the TDD-01.md generated by
  PR #122 + decide whether C4 is the right gate or whether the TDD
  author needs to be tighter about section-level tag consistency. May
  result in a small `doc-tdd/SKILL.md` tightening.
  *Resolution:* CLEANUP-PR-B (PR #131, merge `1f28cc16`) — third child PR of FRAMEWORK-CLEANUP-001 (heart). See `plans/CLEANUP-PR-B-REVIEW-CALIBRATION-PLAN.md` for impl details.

### `[plan-review]` 5-pass plan reviews are paying off; consider codifying minimum-pass count by plan-type — ✅ CLOSED (2026-06-11, PR #131, `1f28cc16`)

- *Context:* TRACE-RES-FIXUP-001 plan took 5 passes to converge
  (Pass 4 caught a silent-no-op `rm -rf .aidoc/saga/` that would have
  wasted a 6-9 hour cascade). NECESSARY-UPSTREAM-001 took 4 passes;
  TDD-RT-001 took 2; the 8-skill rollout plans typically took 2-3.
- *Fix shape:* not urgent, but worth noting in the verified-planning
  skill: framework-level / cross-cutting plans seem to need 4-5 cycles
  in practice; per-layer rollout plans converge in 2. CLAUDE.md's
  "minimum 2" floor is correct; an advisory upper-bound by plan-type
  would help future estimation.
  *Resolution:* CLEANUP-PR-B (PR #131, merge `1f28cc16`) — third child PR of FRAMEWORK-CLEANUP-001 (heart). See `plans/CLEANUP-PR-B-REVIEW-CALIBRATION-PLAN.md` for impl details.

### `[playbook]` `auditor` + `tech_lead` lens calibration — convergence theater — ✅ CLOSED (2026-06-11, PR #131, `1f28cc16`)

- *Context:* url-shortener cascade audit trail (2026-06-11) — `auditor`
  lens scored **100 on 4 of 5 cascaded layers** where it ran; `tech_lead`
  scored **100 on 3 of 4** even when `chaos`+`security_engineer` found
  multiple P2/P3 issues in the same sections. The synthesizer's weighted
  mean still surfaces real findings (verdicts 91-97 honest), but 2 of 6
  lenses are giving blank checks. IPLAN-01 scored 100 with 5/6 lenses
  returning zero findings — the strongest convergence-theater signal.
- *Fix shape:* refresh `framework/playbooks/<layer>/auditor.md` and
  `tech_lead.md` for each layer with more falsifiable checks. Specifically
  require tech_lead to cross-check the sections security/chaos flagged.
  Add a "no-lens-scores-100-without-falsifiable-evidence" guard to the
  synthesizer.
  *Resolution:* CLEANUP-PR-B (PR #131, merge `1f28cc16`) — third child PR of FRAMEWORK-CLEANUP-001 (heart). See `plans/CLEANUP-PR-B-REVIEW-CALIBRATION-PLAN.md` for impl details.

### `[skill]` `doc-*-audit` must strip author's self-claimed scores before lens fan-out — ✅ CLOSED (2026-06-11, PR #131, `1f28cc16`)

- *Context:* url-shortener cascade audit trail (2026-06-11) —
  `02_PRD/PRD-01/verdict.json:AUD-002` flagged that the author's
  `ears_ready_score: 92` self-claim survived into the artifact body
  the lenses see. The synthesizer's final score was **also 92**.
  Coincidence, or anchor-effect from lenses reading the author's claim?
  Either way, the framework should not let author self-assessment leak
  into the review surface.
- *Fix shape:* `doc-*-audit/SKILL.md` step that prepares the lens brief
  must strip fields like `ears_ready_score`, `prd_score`, etc. from the
  artifact text before passing to each lens subagent. Document the
  stripped-field list in `REVIEW_TEAM.md` §Operations.
  *Resolution:* CLEANUP-PR-B (PR #131, merge `1f28cc16`) — third child PR of FRAMEWORK-CLEANUP-001 (heart). See `plans/CLEANUP-PR-B-REVIEW-CALIBRATION-PLAN.md` for impl details.

### `[saga]` Saga lifecycle — no `fixer_introduced_finding` tag — ✅ CLOSED (2026-06-11, PR #131, `1f28cc16`)

- *Context:* `examples/url-shortener/.aidoc/review/04_BDD/BDD-01/saga.json`
  shows iter-2 fixer rewrote scenario `.9b90`; iter-3 audit found the
  rewrite introduced **two new P2s** at the same location (compound
  `When` + unbounded timeout). The framework has no way to flag findings
  that the fixer itself caused — they appear as "new findings" with no
  link to the change set.
- *Fix shape:* extend `REVIEW_SAGA.md` schema with a
  `fixer_introduced_finding` tag on iter-N findings whose location
  matches a iter-(N-1) "Fixes Applied" table row. Surface in the audit
  report under `## Regressions` (new section in audit report format).
  *Resolution:* CLEANUP-PR-B (PR #131, merge `1f28cc16`) — third child PR of FRAMEWORK-CLEANUP-001 (heart). See `plans/CLEANUP-PR-B-REVIEW-CALIBRATION-PLAN.md` for impl details.

### `[template]` IPLAN sub-types: code-build vs deploy — ✅ CLOSED (2026-06-11, PR #132, `9358faf0`)

- *Context:* url-shortener review (2026-06-11) — IPLAN-01 covers Red/Green/
  Refactor with pytest gates but has **no canary, no smoke endpoint, no
  observability dashboard, no rollback procedure** (§5 explicitly defers
  runbook/dashboard to "first to-production session"). It scored 100, but
  it's a code-build plan, not a deploy plan. The crew (operator + chaos
  - integration_lead lenses) is calibrated for deploy concerns; if the
  artifact silently scopes out those concerns, the crew can't catch it.
- *Fix shape:* `IPLAN-TEMPLATE.yaml` gains a `subtype` field with values
  `code_build` | `deploy` | `combined`. Deploy IPLANs are gated on
  rollback/smoke/observability sections; code-build IPLANs are exempt.
  Audit dispatch selects the section set by subtype.
  *Resolution:* CLEANUP-PR-E (PR #132, merge `9358faf0`) — fourth child PR. See `plans/CLEANUP-PR-E-IPLAN-SUBTYPES-PLAN.md`.

### `[gate]` Component-decomposition gate missing between PRD and ADR — ✅ CLOSED (2026-06-11, PR #133, `a9f1a795`)

- *Context:* url-shortener review (2026-06-11) — BRD/PRD scoped the **whole
  service** (shorten + redirect + counter + abuse screening); ADR-01 onward
  silently narrowed to **one component** (Mapping Store). ADR §10 mentions
  "five sibling ADRs as future work" but no scope-contraction artifact
  records the decision. Downstream layers (SPEC/TDD/IPLAN) implement only
  the Mapping Store, not the URL shortener.
- *Fix shape:* introduce a `which-containers-from-PRD-§9-get-ADRs-this-cycle`
  artifact (a CHG-like decision record) at the PRD↔ADR boundary. ADR
  authoring SKILL must reference it; auditor must verify scope matches.
  Without it, downstream layers silently shrink scope unobserved.
  *Resolution:* CLEANUP-PR-D (PR #133, merge `a9f1a795`) — fifth and final child PR. Option A chosen; Option B deferred to item #19.

### `[gate]` Threshold-binding gate missing before BDD/TDD PASS — ✅ CLOSED (2026-06-11, PR #133, `a9f1a795`)

- *Context:* url-shortener review (2026-06-11) — 7 of 11 threshold keys
  in PRD-01 are placeholders (`screeningdeadline`, `countstaleness`,
  `codespacecapacity`, `takedownsla`, `codeentropy`, `resolutionpersource`,
  `resolutionwindow`) with no numeric values bound. BDD scenarios cite
  `WITHIN @threshold:PRD.01.perf.screeningdeadline` and TDD test cases
  cite them too — neither is testable, both passed audit.
- *Fix shape:* extend `sdd_doc_lint` with a `THRESHOLD-RES-001` rule
  (mirror of TRACE-RES-001 for threshold keys): every `@threshold:KEY`
  citation must resolve to a numeric-bound value in the host doc.
  Unbound thresholds fire P1 at BDD/TDD audit.
  *Resolution:* CLEANUP-PR-D (PR #133, merge `a9f1a795`) — fifth and final child PR. Option A chosen; Option B deferred to item #19.

### `[governance]` Doc-number independence across layers not codified anywhere — ✅ CLOSED (2026-06-11, PR #135, `7736120d`)

- *Context:* User clarification (2026-06-11) — document numbers (the
  `NN` in `BRD-01` / `PRD-01` / `EARS-01` / ...) are **per-layer
  sequential and independent**; one BRD MAY drive multiple downstream
  PRDs (PRD-01, PRD-02, ...), one PRD MAY cite multiple BRD upstream
  docs. Framework currently has zero explicit mention of this:
  `ID_NAMING_STANDARDS.md` says *"sequential two-digit number"* (per
  layer, but doesn't say independent across); `TRACEABILITY.md` has
  no cross-layer cardinality discussion; `REVIEW_TEAM.md` +
  `REVIEW_REMEDIATION_FLOW.md` are silent on cardinality. The
  url-shortener example's 1:1 numbering alignment (BRD-01 → PRD-01 →
  ... → IPLAN-01) reinforces the wrong "numbers line up" mental model.
- *Fix shape:* (a) add "Cross-layer cardinality" subsection to
  `ID_NAMING_STANDARDS.md` (or `TRACEABILITY.md`) explicitly stating
  doc numbers are per-layer independent + one-to-many + many-to-one
  both supported; (b) update `doc-<layer>` author SKILL prompts:
  *"the upstream's number is NOT your number — pick next-free in
  YOUR layer's index"*; (c) auditor playbooks: clarify orphan-looking
  downstream docs may be siblings of the same upstream, not actual
  orphans. **Deferred to a follow-up CLEANUP-PR-F (single-item)** —
  cataloged here per Tier-2 pipeline (FRAMEWORK-FEEDBACK-LOG-001
  Principle 9); impl waits until after current cleanup PRs settle.
  *Resolution:* CLEANUP-PR-F (PR #135, merge `7736120d`) — single-item follow-up after FRAMEWORK-CLEANUP-001 workstream closed; codified per-layer cardinality independence in ID_NAMING_STANDARDS.md.

### `[legacy]` Scan for v3.2-era anachronisms across the codebase — ✅ CLOSED (2026-06-12, PR #139, `f2b76d4b`)

- *Context:* user-surfaced (2026-06-12) — the `sdd-orchestrator`
  agent-skill still carried `sdd_depth: lite | standard | full` tiers
  from the SDD v3.2 era. The current framework spec has settled on a
  single SDD path (BRD..IPLAN, all 8 required per necessary-upstream)
  with an adaptive loop (MVP → PROD → New MVP → Updated PROD). The
  legacy-sdd-depth follow-up PR removed the depth references but
  surfaced that the orchestrator's broader worldview (15-persona
  model, ucx_hermes templates, SDD v3.2 versioning) is also stale.
- *Fix shape:* dedicated v3.2-residue scan pass: grep across all
  non-`legacy-ucx-v3.2-read-only` paths for: `SDD v3`, `v3.2`,
  `sdd_depth`, `lite|standard|full` triples in SDD context, `15
  personas`, `ucx_hermes/templates`, `sdd_create` / `sdd_validate`
  CLI invocations. Hermes-side scope tracked separately in
  HERMES-BACKLOG H-11.
  *Resolution:* v3.2-residue scan (PR #139, merge `f2b76d4b`) — scanned 7
  target patterns across the codebase. One purely-dead file deleted:
  `platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/governance/SDD_DEPTH_GUIDE.md`
  (52 lines, entirely about the dead lite/standard/full depth concept).
  The broader sdd-orchestrator v3.2 worldview (SKILL.md framing,
  governance/README.md baseline references, 15-persona dispatch claim)
  stays deferred to HERMES-BACKLOG H-11 — out of scope for the
  bounded scan. References classified as legitimately-current
  (Hermes 15-persona PERSONA_CATEGORY_MAP architecture, current
  Hermes MCP tool names `sdd_create`/`sdd_validate`, CHANGELOG
  historical entries, migration plans/P*-T* files) deliberately
  not touched.
