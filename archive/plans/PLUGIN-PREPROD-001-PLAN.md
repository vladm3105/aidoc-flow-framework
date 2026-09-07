# PLUGIN-PREPROD-001 Plan — close the pre-prod review gaps blocking the plugin deploy

| Field          | Value                                                       |
| -------------- | ----------------------------------------------------------- |
| Task           | PLUGIN-PREPROD-001                                           |
| Type           | bugfix                                                       |
| Status         | **Completed** — all **23 of 23** findings closed. `Draft` → `In Progress` 2026-08-02 → `Completed` 2026-08-02, when M6 (the `claude-code-plugin/v0.25.0` tag + public Release) landed on explicit founder approval. Superseded text kept for the audit trail: "In Progress — 22 of 23 findings closed; M6 … is founder-gated and OPEN. ⚠️ Deliberately **not** `Completed`: 5e's own instruction said to set it, but a declared item is still live … The founder flips this when M6 lands." |
| Depends on     | none                                                         |
| Feeds          | the `claude-code-plugin/v0.25.0` tag + first public marketplace announcement |
| Version impact | plugin MINOR (`0.24.0` → `0.25.0`); **Hermes: no version bump** (founder decision O2 — see Risks); framework spec unchanged |

## Objective

A five-lens pre-production review of `platforms/claude-code-plugin` returned
**BLOCKER**. The packaging is sound — conformance, acceptance and linter suites
are green, vendoring shows zero drift, and every cross-reference resolves — but
four defect classes make a third-party install unsafe or badly behaved: the
review hook executes code from the user's working directory, nine skills mandate
an undisclosed permission-model bypass, the saga driver can wedge permanently and
can report `PASS` on reviews that never ran, and two undeclared runtime
dependencies fail by injecting Python tracebacks into the model's context
labelled as lint findings. This plan closes every finding the review produced —
blocker through low — in five staged PRs ordered by risk, so the plugin can be
tagged and announced.

## Scope

**In:** all **23** findings from the 2026-07-31 pre-prod review — B1–B4 (4
BLOCKER, of which B3 has three distinct sub-defects B3a/b/c), H1–H3, M1–M8,
L1–L7, and P1 — grouped into five sequential PRs. PR 1 creates one
`FRAMEWORK-TODO` entry per finding; reconcile against this enumeration, not
against a headline count. The founder
selected full-scope coverage, fix-the-driver-in-place with an opt-in flag, and
staged PRs.

**Out of scope (deferred):**

- Redesigning the saga state machine. PR 3 adds a forced-transition path; it does
  not revisit the transition table's shape.
- Any `framework/` spec change. Every fix here is platform-side; the spec stays
  at `0.40.0`.
- Fixing `sync-version-refs.sh` issues [#386](https://github.com/vladm3105/aidoc-flow-framework/issues/386)
  and [#405](https://github.com/vladm3105/aidoc-flow-framework/issues/405). Both
  are latent risk for the *next* bump, not for this one; PR 5 works around them by
  verifying the fanout by hand after the version bump.
- A hook config-file reader beyond the single `review_hook` key (PR 1 wires that
  one key; a general config layer for the shell hook is not designed here).

## Approach / Design

### Source-of-truth rule (governs every PR below)

Three of the four surfaces being edited are **vendored**, and the vendoring
scripts regenerate their destinations with `rm -rf` — so an edit to a plugin-side
copy is destroyed by the next sync and never reaches a user.

| Surface | Canonical source | Mirrors | Re-vendor with |
| --- | --- | --- | --- |
| `saga_driver.py`, `playbook_loader.py`, `finding_filter.py` | `tools/` | plugin | `tools/sync-plugin-framework.sh` |
| `sdd_doc_lint/` | `tools/sdd_doc_lint/` | plugin **and** Hermes | `tools/sdd_doc_lint/sync-vendored.sh` |
| `hooks/sdd-doc-review.sh`, `hooks/hooks.json` | plugin (single copy) | — | n/a — edit in place |
| `agents/`, `commands/`, `skills/`, `.claude-plugin/` | plugin (single copy) | — | n/a — edit in place |

### PR 1 — hook hardening

Centred on one 51-line script, which carries the highest-value fixes — but the
PR also touches `hooks.json`, two doc surfaces, `plans/FRAMEWORK-TODO.md`, the
acceptance harness and a new conformance test. It is **not** a `hooks/`-only PR;
budget the doc surfaces accordingly.

**Every new command the hook runs must redirect `2>/dev/null`.** The acceptance
harness captures the hook with `2>&1` and then asserts the result parses as JSON
(claim 55), so a single stray `grep: …: No such file or directory` — from
probing a config file that is usually absent, or walking a directory that is not
there — turns that element red with the misleading reason "hook output invalid
JSON". Likewise use `wc -c < "$file"` for the size cap, not `stat`: `stat -c%s`
is GNU and macOS needs `stat -f%z`, which is the same portability class this PR
explicitly refuses for `timeout`.

1. **B1 — kill the CWD search path.** Add `PYTHONSAFEPATH=1` to the existing
   `python3 -m sdd_doc_lint` invocation. Verified working: it suppresses
   `sys.path[0] = ''` while preserving `PYTHONPATH`. **Rejected alternative:**
   invoking `sdd_doc_lint/__main__.py` by absolute path — tested, and it fails
   with `ImportError: attempted relative import with no known parent package`.
   `PYTHONSAFEPATH` requires Python ≥3.11, which the linter already requires
   (claim 9), so it adds no new floor.
2. **B4 (hook half) — stop conflating crash with findings.** The linter splits
   its output by severity: **errors go to stderr, warnings go to stdout**
   (claim 41). So neither stream alone carries every finding — **keep `2>&1` and
   filter the combined stream.** Retain only lines matching the finding grammar
   `^.*:[0-9]+: \[(ERROR|WARNING)<SP>` — where `<SP>` is a literal single space,
   written this way because a real trailing space inside inline code is stripped
   by the repo's trailing-whitespace pre-commit hook — and drop everything else, which removes
   tracebacks and the `sdd-doc-lint: N error(s)…` summary alike (the grammar
   rejects both: every `Finding` renders on one line and the summary lacks the
   `:<n>: [SEV<SP>` shape). If no line survives, emit no findings block.
   **The severity literal is `WARNING`, not `WARN`** (claim 42) — a
   `\[(ERROR|WARN)<SP>` pattern requires a space immediately after `WARN`, which
   `WARNING` never supplies, so it can never match a warning.
   **Capture the exit code before filtering:** run the linter unpiped into a
   variable, take `rc=$?` on that line, and filter the captured text afterwards.
   A pipeline (`… | grep -E …`) would make `$?` **grep's** status, and grep exits
   1 when *nothing* matched — inverting the hook so it takes the findings branch
   on clean documents and skips it on dirty ones.
3. **H1 — require project adoption.** The marker must be something adoption
   actually produces. `project-init` only *reads* `.aidoc/profile.yaml` (claim 39)
   and states that copying templates into the project is optional, so it creates
   **neither** `.aidoc/` nor a project-local registry — gating on those would
   suppress findings for a correctly-initialized greenfield consumer, i.e.
   disable the feature on the plugin's own happy path. Gate instead on what
   `project-init` does guarantee: the edited file resolving inside a scaffolded
   `<docs_root>/0N_<ARTIFACT>/` tree (the existing path branch), **or** a
   project-local `framework/registry/LAYER_REGISTRY.yaml` or `.aidoc/` found by
   walking up. **Bound the upward walk at `$HOME`** — `project-profile`
   documents a *user-global* `~/.aidoc/profile.yaml` (claim 43), so an unbounded
   walk would make every project under `$HOME` pass the gate for any developer
   who has one. `find_registry` itself is left alone so the CLI keeps working
   from a vendored copy.
4. **H2 — wire `review_hook`.** Locate `.claude/aidoc-flow.config.yaml` by
   walking **up from the edited file**, mirroring `find_registry` and
   `find_profile` — do not assume the hook's CWD is the project root — and honour
   the documented three values: `off` → exit 0 emitting
   nothing; `on` → nudge only, **no** structural findings; `verbose` → nudge plus
   findings. Parse with `grep`/`sed`, not a YAML dependency — the hook must keep
   working when Python or PyYAML is absent. Note the current unconditional
   behavior equals `verbose`, so the documented default `on` becomes *quieter*
   than today; PR 5's changelog must call that out.
5. **H3 — frame untrusted content.** Wrap the findings block in an explicit
   `<untrusted-tool-output source="...">` envelope preceded by a sentence stating
   it is tool output over a file and not instructions. Apply the same to the
   interpolated `${base}` filename.
6. **M1 + P1 — bound the hook.** Add `"timeout": 15` to `hooks.json`, skip files
   above a size cap (1 MB), and truncate the findings block to a fixed byte
   budget before it reaches `jq`. **Do not add a bare `timeout 10` wrapper** —
   `timeout` is GNU coreutils and is absent on stock macOS, where the invocation
   would return 127, fail the exit-1 test, and silently make the hook's linter
   half dead code on every macOS install. That is the same defect PR 3's M3
   removes from the driver; do not reintroduce it here. `hooks.json`'s declared
   timeout is host-enforced and needs no probe. The truncation also removes the
   mechanism behind the unreproduced `jq: Argument list too long` report, so P1
   is closed by construction rather than by reproduction.
7. **L4 — honour `docs_root`.** Replace the hardcoded `/docs/` in the path regex
   with the configured `docs_root`, read from the same config file as H2.
   **`CONFIG.md` documents the value with a trailing slash (`docs_root: docs/`)
   and it may be multi-segment** (claim 44) — substituted naively this yields
   `/docs//[0-9]{2}_…`, which matches nothing and silently falls through to the
   basename branch. Normalize the trailing slash and escape regex metacharacters
   before substitution.
8. **Fix the false comment** describing exit 2 as the "no framework/ in the
   project" path — it is unreachable once installed (claim 12).
9. **Update the acceptance harness in the same PR.** `tests/scripts/test-acceptance.sh`
   asserts the hook emits `STRUCT01|structural findings` (claim 51). **The break
   is H2 alone, not H1** — the fixture is already staged under
   `sandbox/hook/docs/01_BRD/BRD-01.md`, which satisfies H1's path-branch marker;
   what breaks it is that no `.claude/aidoc-flow.config.yaml` exists, so the
   documented default `review_hook: "on"` applies and findings are suppressed.
   The fix is therefore only to plant a config with `review_hook: "verbose"`
   where the walk-up from the staged file reaches it — **not** to restage the
   fixture with an adoption marker, which would be work against a wrong
   diagnosis. Consequence worth stating: H1 then has **no** harness coverage, so
   its conformance test is the only thing guarding it. Not CI-gated (the workflow runs only
   `tests/acceptance/deterministic`), but it is the documented release acceptance
   suite and PR 5 cuts a release. `tests/ACCEPTANCE.md` counts this element and
   must move with it.

### PR 2 — declare and guard the runtime dependencies (`tools/sdd_doc_lint/` + mirrors)

**B4 (linter half).** Inside `tools/sdd_doc_lint/` exactly **one** module imports
yaml at module level — `__init__.py` (claim 10); `trace_graph.py`, `rehash.py`
and `__main__.py` do not, and the second occurrence in `__init__.py` is a
function-local alias in that same module. The other unguarded importer is
`tools/saga_driver.py`, which belongs to **PR 3** and carries its own guard
there — do not reach for it here, and never hand-edit the Hermes mirror, which
the Source-of-truth rule says the next sync destroys. So: guard the single
module, with a one-line diagnostic naming PyYAML on stderr. **Use a
distinct exit code (3), not 2.** Exit 2 already carries "usage error" per the
module docstring and "registry unavailable" per the `OSError` handler; adding a
third condition to it inside a PR whose stated purpose is to stop conflating
failure modes would be self-defeating. Nothing forces reuse — the hook treats
every code other than 1 identically. Add the same guard shape for the
Python ≥3.11 floor that `StrEnum` and `datetime.UTC` impose. **L5:** make
warning-severity findings reachable — today `__main__.py` returns 0 unless a
finding is `error`, so the hook can never surface a warning despite claiming to.
Add a `--warn-exit` flag rather than changing the default exit contract, which
CI depends on. Re-vendor **both** mirrors and confirm two consecutive
`pre-commit run --all-files` runs are clean (ruff-format can rewrite after the
copy).

### PR 3 — saga driver correctness and disclosure (`tools/saga_driver.py`)

1. **B2 — make the permission bypass opt-in and disclosed.** Default
   `--dangerously-skip-permissions` **off**; add an explicit
   `--allow-skip-permissions` flag — **and no config key** (founder decision O1;
   the driver reads no plugin config file, so a key would document an
   enable-path nothing reads, and PR 3 does not touch `docs/CONFIG.md`).
   **A release gate forbids the literal string `--dangerously-skip-permissions`
   in any `SKILL.md`** (claim 45) and PR 5 cuts a release, so the 9 autopilot
   skills must name only the new `--allow-skip-permissions` flag; the underlying
   flag is explained in `README.md` and the `plugin.json` description, which the
   gate does not scan. Do not amend that gate to make room for the disclosure —
   it is enforcing exactly the property this fix restores.
   **The 9 skills must *pass* `--allow-skip-permissions`, not merely mention it**
   — the founder's choice was to keep autopilot working, and every known invoker
   passes only `--layer` (plus `--threshold`), so a documentation-only change
   would strip the bypass from the plugin's primary path and from the live
   cascade. Passing it at the invocation site is also the real disclosure win:
   the bypass becomes visible where it is requested instead of hidden in the
   driver.
   **Patch the harness too.** `tests/scripts/test-acceptance.sh` is the only
   non-skill invoker of the driver (claim 56) and passes just `--layer` and
   `--threshold`; once the default flips off, its child sessions lose the
   non-interactive write permission the cascade depends on. Add
   `--allow-skip-permissions` at that invocation in the same PR — otherwise the
   founder's "keep autopilot working" holds for the 9 skills and silently fails
   for the release-acceptance cascade.
2. **B3a — stop the permanent wedge.** Three non-terminal states cannot reach
   `PARTIAL_TIMEOUT`, yet **four** call sites transition to it from
   `saga["status"]` unconditionally — `check_break_circuit`, the MISSING-verdict
   branch, the iteration cap, and the subprocess-non-zero branch in `main`
   (claim 46) — and `append_transition` raises. Retrofit all four; a fix applied
   to three leaves one unprotected raise. Add an
   explicit **forced**-transition path (`append_transition(..., forced=True)`)
   that records the edge as reconciled rather than raising — do **not** relax
   `can_transition`, whose preemptive validation is correct. Fix the comment that
   claims `PARTIAL_TIMEOUT` is "universally reachable from non-terminal states".
3. **B3b — stop clobbering the subprocess's journal.** `main` **already**
   reloads from disk after dispatch (claim 47) — the bug is not a missing
   reload, it is that `dispatch_phase`'s post-subprocess `write_saga` clobbers
   the file *before* that reload runs. Fix the write ordering inside
   `dispatch_phase` (reload before appending the completion event); do **not**
   "fix" the caller's reload or add a second one. **Sequencing:** this un-masks a
   latent raise at the terminal-chain guard, which must be fixed in the same PR.
4. **B3c — scope the resume filter.** `resume_from_partial_timeout` selects the
   last non-`PARTIAL_TIMEOUT` transition without checking `scope`, so a
   branch-scoped terminal becomes the run status. The fix is
   `t.get("scope", "run") == "run"` — **defaulting to `"run"` is mandatory, not
   stylistic.** Scope-less transitions are real: the existing conformance fixture
   contains none (claim 48), so a bare `t.get("scope") == "run"` fails a required
   context, and `reconcile_post_audit` already reads `t.get("scope", "")`
   defensively because the audit skill's LLM writes transitions directly into
   `saga.json` — under the bare form, resuming any such journal restarts the saga
   at `PREPARED`.
5. **M3 — macOS.** `timeout` is GNU coreutils. Probe for `timeout`, then
   `gtimeout`, else fall back to `subprocess.run(..., timeout=…)` and drop the
   wrapper. Guard the `FileNotFoundError` so a failed spawn cannot leave a
   journalled dispatch that never happened.
6. **M4 — meaningful exit codes.** Return non-zero for `ESCALATED` and
   `PARTIAL_TIMEOUT` so a caller chaining on success cannot proceed on an
   artifact that never passed review. **Fix both return sites**: the unconditional
   one *and* the `return 0` taken immediately after `check_break_circuit` sets
   `PARTIAL_TIMEOUT` (claim 49) — the latter is the single most likely way a run
   ends non-`CLOSED`, so fixing only the former leaves the primary case reporting
   success. **Consumers:** the 9 autopilot skills are unaffected (they invoke the
   driver as a bare `Bash` command and read `saga.json` regardless of exit code),
   but `tests/scripts/test-acceptance.sh` captures the driver's return code and
   records `FAIL` on non-zero (claim 50) — today a `PARTIAL_TIMEOUT` run exits 0
   there. Update that harness in the same PR. **Choose a code that is neither 2
   (argparse usage error) nor 124 (`timeout`, which the harness special-cases)**,
   or failure attribution in that harness becomes ambiguous.
7. **M5 — invalidate `verdict.json` between iterations.** Unlink it before each
   audit dispatch, so a stale `PASS` cannot be read as current.
8. **L2 — `--threshold` is accepted and ignored.** ✅ **NO LONGER TRUE — PR 3 made it a live gate** (`tools/saga_driver.py`, `_meets_threshold` at `:814`, enforced at `:874`): a `PASS` whose `content_score` is under the threshold no longer counts as converged, and the flag string survived as required. The rest of this bullet is the pre-PR-3 state, kept for the audit trail — **except its "Also correct the record" clause, which was an instruction, not a description: the `0.23.4` changelog correction it demands SHIPPED in the root `CHANGELOG.md` `[Unreleased]` entry.** **Do not remove the flag.**
   `tests/scripts/test-acceptance.sh` passes `--threshold 90` on every cascade
   layer (claim 52); deleting the argparse entry makes the driver exit 2 on a
   usage error before any saga work, failing layer 1 and aborting the whole
   cascade under `FAIL_FAST`. Gate on it beside `status == "PASS"`, or keep it
   accepted and document it as reserved — either way the flag string survives.
   **Also correct the record:** `CHANGELOG.md` already claims plugin `0.23.4`
   "removed the dead `--threshold` flag from `saga_driver.py`" (claim 53). The
   skill half of that claim is true; the driver half never happened. PR 5's entry
   must say so rather than restating it.
9. **L3 — `playbook_loader.py`.** No runtime caller references it, though
   `tests/unit/test_playbook_loader.py` does exercise it (in the unguarded tier
   that no hook or workflow runs). Add the
   `Path.resolve().is_relative_to(root)` traversal guard and keep it (it is
   vendored deliberately), or drop it from `TOOLS_FILES` **and** delete that
   test. Decide in the PR; either is defensible, both close the finding.

### PR 4 — agent and manifest hygiene (plugin, single-copy files)

- **M2** — `agents/requirements-analyst.md` is the only one of 11 declaring
  neither `tools:` nor `model:`, so it inherits every tool including `Write`,
  `Edit` and `Bash`. Scope it to match its siblings.
- **L1** — add a `LICENSE` file inside the plugin directory; the installed
  artifact declares MIT and ships no license text.
- **L6** — replace the personal email in `marketplace.json` with a role address,
  if the founder wants it off a public manifest.
- **L7** — rename `agents/code-reviewer.md` under the plugin's namespace, or
  document the collision risk with a consumer's own agent of that name.
- Add a conformance test asserting every agent declares `tools:` and `model:`.

### PR 5 — docs, governance, and the release cut

**PR 5 ships as five stages (a–e), not one PR.** § "Docs to update" (`:537`, PR-5
sentence at `:543-547`) lists eight documents of record for this PR against the
≤3-surface Governance PR cap, and this plan says to split (`:558`). The split
is **measured**, not proposed:

| Stage | Surfaces | State |
|---|---|---|
| 5a | the release changelog gate | **done** — #420 |
| 5b | `SECURITY.md` + `CHANGELOG.md` (M7) | **done** — #422 |
| 5c | `VERSION` `0.24.0`→`0.25.0` + the 60-file fanout + both CHANGELOGs | **Rule 1 exception GRANTED by the founder 2026-08-02**; in flight — move to `done — #N` at 5d |
| 5d | `ROADMAP.md` (M8) + `plans/DECISIONS.md` (`D-00NN`) + `plans/FRAMEWORK-TODO.md` (close the batch) | |
| 5e | this plan (the corrections below + status → `Completed`) + `plans/HANDOFF.md` + `CLAUDE.md` | |

**5c cannot be split** — see O2 (`:435`, risk row `:568`) and `:549-556`: the `sync-version-refs`
pre-commit hook re-stages its own writes, so the diff cannot be separated after
the fact, and it rewrites `CLAUDE.md`, which pulls the stage under Governance PR
discipline. The Hermes case was resolved by skipping the bump (O2); the plugin
cannot skip, since M6 needs `0.25.0`. So 5c requires Rule 1's stated exception:
**explicit founder OK plus an audit-trail line in the commit message.** It is not
self-grantable, and one stage exceeding the cap is not evidence the split is
wrong.

**✅ FIVE claims in this plan were falsified by the work that implemented it** — the
four identified before 5e, plus a fifth that **5c itself created** (the "six versions
stale" figure, which its own bump made seven). All five were corrected in stage 5e
(2026-08-02), annotated in place below, with the originals kept for the audit trail
rather than deleted.**

⚠️ These are **self-references, and every edit to this file shifts them.** Each is
quoted as well as cited — match the quote, not the number, if they disagree.

1. **`:347` (M7) — "replace the scanner list" is wrong.** #422 deliberately did
   not replace it: the existing list was *incomplete*, not false, and replacing it
   would have deleted four accurate `pre-commit` entries (`bandit`,
   `detect-secrets`, `detect-private-key`, `pip-audit`). The shipped fix splits
   the list **by configuring file** — CI scanners under `.github/workflows/`,
   local/CI hooks in `.pre-commit-config.yaml` — and records which of them can
   actually block a merge.
2. **`:613` (claim-ledger row 34) is false.** It reads "`SECURITY.md` names
   scanners CI does not run | bandit". `.github/workflows/pre-commit.yml` **does**
   run bandit in CI, inside the required `call / Lint / format / security hooks`
   context. A plan marked `Completed` while carrying a falsified ledger row is the
   exact failure the ledger exists to prevent.
3. **`:377` — the README prerequisites section already shipped in PR 1.**
   Do not re-add it. (`:415` assigns it to PR 1; the two rows disagree.)
4. **`:262-272` — the `--threshold` bullet is doubly stale.** PR 3 made the flag
   live. The 5c changelog entry must say *that*, not restate either version of the
   old claim.

✅ Fixed at 5e — a **sixth** falsified claim, found after the block above was
written: the § "File structure" row at **`:389`** now names the `platforms/` path.
Superseded: "`:389` names `tests/conformance/test_agent_frontmatter.py`".

- **M7** — `SECURITY.md`: correct the spec version and the scanner list.
  ✅ **SHIPPED in #422, and NOT as this bullet specified.** The bullet said to
  *replace* the list with what CI runs; that would have deleted four accurate
  `pre-commit` entries. What shipped splits the list **by configuring file** — CI
  scanners under `.github/workflows/`, hooks in `.pre-commit-config.yaml` — and
  states which three checks can actually block a merge. The bullet's *omission*
  half was right and did ship: `trivy config` and CodeQL were missing. Superseded
  text kept for the audit trail: "replace the scanner list with what CI actually
  runs — semgrep (SAST), osv-scanner (dependencies), gitleaks (secrets),
  `trivy config` (IaC) and CodeQL."
- **M8** — `ROADMAP.md`: correct the stale plugin version.
- **M6** — cut `claude-code-plugin/v0.25.0` and publish a GitHub Release.
  ✅ **DONE 2026-08-02** on founder approval: annotated tag → `e6c6539d`, on the
  remote; Release published as a **pre-release** (pre-1.0 preview, `v0.18.0`'s
  tier). Superseded text — it carries the **fifth** falsified claim counted above:
  "The latest Release is **seven** versions stale (`0.18.0` against `VERSION`
  `0.25.0`) — it read *six* until 5c's own bump falsified it, making this a
  **fifth** claim this plan's implementation falsified. … **Founder-gated:** …"
- **Record the decision.** The opt-in permission flag (PR 3) is a policy choice
  embedded in shipped code, which `plans/DECISIONS.md` exists to authorize. Add a
  `D-00NN` entry covering it and the `review_hook` default becoming quieter than
  today's behavior.
- **Capture the queue, then publish.** Per `GOV-TODO-ISSUE-SPLIT`, every finding
  gets a `plans/FRAMEWORK-TODO.md` entry **created at PR 1** (not at PR 5), and
  each entry meeting the promotion bar gets a GitHub issue on this repo. PR 5
  closes both. Entries and issues are created up front so that a stall between
  stages leaves a readable queue rather than nothing.
- Version bump `0.24.0` → `0.25.0` in the documented propagation order, then
  hand-verify the fanout because of the two open `sync-version-refs.sh` defects.
- `CHANGELOG.md` entries for the plugin and the project. ⚠️ **The README
  prerequisites section (jq, Python ≥3.11, PyYAML) already SHIPPED in PR 1**
  (`platforms/claude-code-plugin/README.md:19-23`). Do not re-add it — `:404`
  assigns it to PR 1 (`:415`), and this row contradicted that.

## File structure

### Created

| Path | Purpose |
| ---- | ------- |
| `platforms/claude-code-plugin/LICENSE` | MIT text inside the installed artifact (L1) |
| `tests/conformance/test_plugin_hook_safety.py` | locks B1 (shadow package cannot execute), M1 (timeout present), H3 (untrusted envelope present) |
| `tests/conformance/platforms/test_agent_frontmatter.py` | every agent declares `tools:` and `model:` (M2) — shipped under `platforms/`, beside the other plugin-platform checks (`PREPROD-PLAN-TESTPATH`) |

### Modified

| Path | Change |
| ---- | ------ |
| `platforms/claude-code-plugin/hooks/sdd-doc-review.sh` | PR 1 — all eight hook fixes |
| `platforms/claude-code-plugin/hooks/hooks.json` | PR 1 — add `"timeout": 15` |
| `tools/sdd_doc_lint/__init__.py` | PR 2 — guarded `import yaml`, Python-floor guard |
| `tools/sdd_doc_lint/__main__.py` | PR 2 — `--warn-exit`, exit-code docstring correction |
| `tools/saga_driver.py` | PR 3 — B2, B3a–c, M3, M4, M5, L2 |
| `tools/playbook_loader.py` | PR 3 — traversal guard (L3), if kept |
| `platforms/claude-code-plugin/skills/doc-*-autopilot/SKILL.md` (9) | PR 3 — disclose the permission flag |
| `platforms/claude-code-plugin/agents/requirements-analyst.md` | PR 4 — scope `tools:` + `model:` |
| `platforms/claude-code-plugin/.claude-plugin/plugin.json` | PR 3/5 — disclosure in description; version bump |
| `.claude-plugin/marketplace.json` | PR 4/5 — email (L6); version bump |
| `plans/FRAMEWORK-TODO.md` | **PR 1 — create** an entry per finding; PR 5 — close them |
| `plans/DECISIONS.md` | **PR 5** — `D-00NN` covering both the opt-in permission flag (PR 3) and the quieter `review_hook` default (PR 1). Placed last deliberately: it records behavior from two PRs, so filing it in PR 3 would forward-reference unmerged PR 1 behavior |
| `platforms/claude-code-plugin/VERSION` | PR 5 — the bump every other plugin surface is derived from |
| `plans/HANDOFF.md` | PR 5 — refresh at the wrap |
| `platforms/claude-code-plugin/agents/code-reviewer.md` | PR 4 — L7 rename or documented collision note |
| `platforms/hermes/CHANGELOG.md` | PR 2 — an `[Unreleased]` entry for the re-vendored linter. **No `platforms/hermes/VERSION` change** (O2), so `sync-version-refs.sh`'s five-file fanout never fires |
| `CLAUDE.md` | PR 5 — current-state paragraph only |
| `tests/scripts/test-acceptance.sh` | PR 1 — plant `review_hook: "verbose"` for the hook element; PR 3 — tolerate a meaningful driver exit code |
| `tests/ACCEPTANCE.md` | PR 1 — the hook element's expectation moves with it |
| `SECURITY.md`, `ROADMAP.md` | PR 5 — M7, M8 |
| `platforms/claude-code-plugin/README.md` | PR 1 — prerequisites; PR 3 — permission disclosure (expect the conflict noted in the sequence) |
| `platforms/claude-code-plugin/docs/CONFIG.md` | PR 1 only — `review_hook` semantics. **Not PR 3** (O1: no config key ships) |
| `CHANGELOG.md`, `platforms/claude-code-plugin/CHANGELOG.md` | PR 5 — entries |

## Founder decisions (resolved 2026-07-31)

Two items the third independent pass surfaced that source could not resolve.
Both are now decided and folded into the sections above; recorded here because
each rejected an alternative for a reason a future session would otherwise
re-litigate.

**O1 — the opt-in config key has no reader → ship the flag alone.**
`saga_driver.py` reads no plugin config file; its only config read is
`.aidoc/profile.yaml`, for `quality_loop_max_iterations` (claim 57), and `docs/CONFIG.md`
scopes itself to keys consumed by three specific commands. A config key would
have documented an enable-path nothing reads. *Rejected:* building a reader
keyed off `.aidoc/profile.yaml` + `ADAPTATION_SURFACE.yaml` — coherent, but real
scope in PR 3 for a second path to a flag that already works. **PR 3 does not
touch `docs/CONFIG.md`.**

**O2 — the Hermes fanout cannot fit the governance cap → skip the bump.**
PR 2 re-vendors the linter into Hermes and leaves `platforms/hermes/VERSION`
alone, logging the change under Hermes' `[Unreleased]`. *Rejected:* deferring
the bump to PR 5, and giving Hermes a dedicated PR — both were viable; the
founder chose to avoid the fanout entirely. **Accepted cost:** Hermes ships a
behavior change with no version signal, so a Hermes consumer cannot tell from
the version that the linter changed. The `[Unreleased]` entry preserves the
record and the next Hermes release carries the signal. Tracked in Risks.

## Implementation sequence

1. **PR 1 — hook hardening.** Highest value per unit of effort; one script plus
   `hooks.json` plus two doc surfaces.
2. **PR 2 — dependency guards + re-vendor.** **Depends on PR 1** (see the
   dependency paragraph below); touches the canonical linter and both mirrors,
   including Hermes, and adds the `--warn-exit` argument to the hook's
   invocation line.
3. **PR 3 — saga driver.** The only stage needing real design work. B3b and the
   terminal-chain guard land together.
4. **PR 4 — agent/manifest hygiene.** Small, independent.
5. **PR 5 — docs, version bump, tag, Release.** Last, so the changelog describes
   what actually shipped.

**PRs 1 and 4 are mutually independent and may run in parallel. PR 2 depends on
PR 1** — its `--warn-exit` flag closes nothing unless the hook actually passes
it, and the hook invocation is a PR 1 file, so PR 2 adds that one line to
`sdd-doc-review.sh`. Without this dependency L5 stays open after both PRs land
while reading as closed. PR 3 depends on nothing but must precede PR 5; PR 5 is
last.

Each PR branches from `main` — do not stack, per the durable trap on stacked PRs
auto-closing when a parent merges with `--delete-branch`. **PR 1 and PR 3 both
touch `platforms/claude-code-plugin/README.md`** (prerequisites, and the
permission disclosure): expect a conflict on whichever lands second and re-run
`pre-commit run --all-files` after resolving it.

## Test-first step

Each PR writes its failing test before its fix:

- **PR 1:** a test that plants a `sdd_doc_lint/` package in a scratch directory,
  runs the hook's exact invocation, and asserts the vendored module ran — this
  currently **fails** (the shadow executes). Plus: a non-adopting directory
  produces a nudge with no structural findings; `review_hook: "off"` produces no
  output at all. **The H1 test must set `review_hook: "verbose"` in the scratch
  tree** — otherwise the default `on` suppresses findings on its own and the
  assertion passes on a build where H1 was never implemented. Pair it with a
  genuinely non-adopting layout (an `ADR-0001-x.md` at the root, no
  `framework/registry/`, no `.aidoc/`) so the basename branch is the only match. **Both scratch-directory tests false-pass if the scratch root is
  created under this repo** — H1's upward walk would reach the repo's own
  `framework/registry/LAYER_REGISTRY.yaml` and the gate would pass while the test
  asserts the opposite. Create scratch roots outside the repo tree and outside
  `$HOME` (see H1's `~/.aidoc/` hazard), and assert `jq` is present, since the
  hook exits 0 silently without it and the test would false-pass there too.
- **PR 2:** with PyYAML shadowed out, the linter exits **3** — the distinct code
  chosen in the Approach section, *not* 2, which already carries usage-error and
  registry-unavailable — and prints a diagnostic naming PyYAML. It currently
  exits 1 with a traceback. Also: a warnings-only document under `--warn-exit`
  still reaches the hook (guards against the stdout/stderr split re-closing this).
- **PR 3:** a saga at `BRANCH_FAILED` hitting the iteration cap terminates
  without raising and writes its journal; `dispatch_phase` preserves transitions
  a subprocess wrote. For B3c the correct expectation is **the last *run-scoped*
  non-`PARTIAL_TIMEOUT` state, else `PREPARED`** — not "resumes as
  `PARTIAL_TIMEOUT`". `resume_from_partial_timeout` exists precisely to *leave*
  that state and a saga left in it never enters the loop, so the earlier phrasing
  described an assertion that could only pass by breaking the function. Also
  assert the existing scope-less fixture still resolves to `BRANCH_RUNNING`.
- **PR 4:** the agent-frontmatter conformance test fails on
  `requirements-analyst.md` before it is fixed.

New test modules go under `tests/conformance/` — **not** `tests/unit/`, which no
hook and no workflow executes. Placed there they are auto-discovered by
`unittest discover -s tests/conformance` and need **no** registration: the
`REGISTERED` tuple in `tests/conformance/test_repo_scripts.py` exists solely to
pull modules that live under `tests/unit/` into the suite (claim 38). Adding a
conformance-resident module to it would be wrong.

## Verification

Per PR: `python3 -m pytest tests/conformance -q`,
`python3 -m pytest tests/acceptance/deterministic -q`,
`PYTHONPATH=tools python3 -m pytest tools/sdd_doc_lint/tests -q`, and
`pre-commit run --all-files`. All four are green on `main` today (measured
2026-07-31: 255 + 692 subtests, 64 + 56 subtests, 5 tests), so any red is
attributable to the change.

PR 2 additionally: re-run `tools/sdd_doc_lint/sync-vendored.sh` and confirm two
consecutive clean `pre-commit run --all-files` passes. PR 3 additionally:
`tools/sync-plugin-framework.sh` then verify zero bundle drift. PR 5
additionally: hand-verify every version-string surface after the bump rather than
trusting the fanout.

**Two test tiers the draft omitted, both un-run by any workflow and both
load-bearing for a release cut:** `tests/release/` (which holds the
marketplace/no-dangerous-flag gate PR 3 must not trip) and `tests/smoke/`. Run
both in PR 3 and again in PR 5. `tests/scripts/test-acceptance.sh` must be run in
PR 1 and PR 3, since both change behavior it asserts on.

Every commit message needs the literal `Multi-agent self-review per OPS-0065
(<agents>): <verdict>` line — `call / verify` is a required context and greps for
it with `grep -qF`.

## Docs to update

PR 1: `docs/CONFIG.md` (`review_hook` now actually does something), plugin
`README.md` (prerequisites), **`plans/FRAMEWORK-TODO.md` — create one entry per
finding**. PR 2: `platforms/hermes/CHANGELOG.md`. PR 3: 9 autopilot skills,
`plugin.json`, `README.md` (permission disclosure) — **three surfaces, and not
`docs/CONFIG.md`**, per O1. PR 5: `SECURITY.md`, `ROADMAP.md`, both changelogs,
`CLAUDE.md` current-state paragraph, `plans/FRAMEWORK-TODO.md` (close the
entries), `plans/HANDOFF.md`, `plans/DECISIONS.md` (the `D-00NN` record, placed
here deliberately — it covers behavior from both PR 1 and PR 3, so filing it in
PR 3 would forward-reference unmerged PR 1 behavior).

**PR 2 must not touch `platforms/hermes/VERSION`.** Doing so makes
`scripts/sync-version-refs.sh` fan the new value out to five files — `CLAUDE.md`,
`README.md`, `platforms/hermes/README.md`, `docs/PARITY.md` and
`platforms/hermes/pyproject.toml` (claim 54) — from a pre-commit hook that
re-stages its own writes, so the diff cannot be split back out. That would put
PR 2 at 5 doc surfaces against the ≤3 cap and pull it under Governance PR
discipline. Per O2 the bump is skipped entirely; PR 2 stays a code + one-changelog
PR. If a future session reinstates the bump, it inherits all of the above.

Governance PR discipline caps each PR at 3 doc surfaces; where a stage exceeds
it, split the doc updates into a trailing PR of their own rather than widening
the code PR.

## Risks

| Risk | Mitigation |
| --- | --- |
| PR 3's B3b fix un-masks a latent raise at the terminal-chain guard | Fix both in the same PR; the test asserts the full loop, not the single function |
| Re-vendoring the linter also changes Hermes | Verified 2026-07-31: all four Hermes mirror modules are byte-identical to source, so PR 2 inherits no pre-existing drift. Run the Hermes suite in PR 2. Note Hermes' pytest is red on `main` for an unrelated floating-dependency reason — establish that baseline before attributing any failure to this change |
| **Hermes ships a behavior change with no version signal** (accepted, O2) | Deliberate: bumping `platforms/hermes/VERSION` fans out to five files through a self-re-staging pre-commit hook, which cannot fit the ≤3 governance cap and cannot be split. The cost is that a Hermes consumer cannot tell from the version that the linter changed. Mitigated by a `[Unreleased]` CHANGELOG entry; the next Hermes release picks it up and carries the signal then |
| `PYTHONSAFEPATH` needs Python ≥3.11 | Already required by `StrEnum`; PR 2 makes that floor explicit and diagnosed |
| Hook config parsing without PyYAML could mis-parse | Restrict to two scalar keys with a strict `grep`/`sed` pattern; anything unrecognized falls back to the default |
| Version-bump fanout is known-broken (#386, #405) | Hand-verify every surface in PR 5 instead of trusting the script |
| Making `on` quieter than today's behavior surprises existing users | Call it out explicitly in the changelog; today's behavior remains available as `verbose` |

## Claim ledger

<!-- markdownlint-disable MD050 -->

| # | Claim | Symbol | Citation |
| --- | --- | --- | --- |
| 1 | The hook invokes the linter via `python3 -m`, which puts the CWD first on `sys.path` | `python3 -m sdd_doc_lint` | platforms/claude-code-plugin/hooks/sdd-doc-review.sh:43 |
| 2 | The hook treats linter exit 1 as structural findings | `if [ "$?" -eq 1 ]` | platforms/claude-code-plugin/hooks/sdd-doc-review.sh:44 |
| 3 | stderr is merged into the captured findings — **load-bearing today** (it is how *error* findings reach the model, see claim 41), and simultaneously how tracebacks do | `2>&1` | platforms/claude-code-plugin/hooks/sdd-doc-review.sh:43 |
| 4 | The artifact is detected from the basename alone when the path test fails | `elif [[ "$base" =~ ^([A-Za-z]+)-[0-9] ]]` | platforms/claude-code-plugin/hooks/sdd-doc-review.sh:23 |
| 5 | The path test hardcodes `/docs/`, defeating the configurable `docs_root` | `/docs/[0-9]{2}_([A-Za-z]+)/` | platforms/claude-code-plugin/hooks/sdd-doc-review.sh:21 |
| 6 | Findings are concatenated onto an instruction string with no untrusted-data framing | `Structural findings (sdd_doc_lint)` | platforms/claude-code-plugin/hooks/sdd-doc-review.sh:45 |
| 7 | The filename is interpolated into model-visible context unescaped | `${base}` | platforms/claude-code-plugin/hooks/sdd-doc-review.sh:34 |
| 8 | The hook declares no timeout | `PostToolUse` | platforms/claude-code-plugin/hooks/hooks.json:3 |
| 9 | The linter requires Python ≥3.11 | `from enum import StrEnum` | tools/sdd_doc_lint/__init__.py:27 |
| 10 | PyYAML is an unguarded hard import in the linter | `import yaml` | tools/sdd_doc_lint/__init__.py:30 |
| 11 | The registry search falls back to the module's own location, so the bundled copy always resolves | `find_registry` | tools/sdd_doc_lint/__init__.py:46 |
| 12 | The hook's comment claims exit 2 means "no framework/ in the project" (the string wraps across lines 39–40) | `2 = registry not` | platforms/claude-code-plugin/hooks/sdd-doc-review.sh:39 |
| 13 | Exit 2 is returned only when the registry raises `OSError` | `registry unavailable` | tools/sdd_doc_lint/__main__.py:86 |
| 14 | Warning-severity findings can never reach the hook, because exit is 0 unless a finding is `error` | `return 1 if any(f.severity == "error" for f in findings) else 0` | tools/sdd_doc_lint/__main__.py:118 |
| 15 | The driver spawns child sessions with the permission model disabled | `"--dangerously-skip-permissions"` | tools/saga_driver.py:398 |
| 16 | `PARTIAL_TIMEOUT` is not reachable from `BRANCH_FAILED` | `"BRANCH_FAILED"` | tools/saga_driver.py:47 |
| 17 | `PARTIAL_TIMEOUT` is not reachable from `BRANCH_COMPENSATING` | `"BRANCH_COMPENSATING"` | tools/saga_driver.py:48 |
| 18 | `PARTIAL_TIMEOUT` is not reachable from `SYNTHESIZED` | `"SYNTHESIZED"` | tools/saga_driver.py:51 |
| 19 | An illegal transition raises rather than being recorded | `raise ValueError` | tools/saga_driver.py:305 |
| 20 | The driver writes its stale in-memory dict back after the subprocess returns | `result = subprocess.run(cmd, capture_output=False, check=False)` | tools/saga_driver.py:406 |
| 21 | The resume filter ignores transition scope | `if t["to"] != "PARTIAL_TIMEOUT":` | tools/saga_driver.py:370 |
| 22 | `verdict.json` is read with no freshness check and never unlinked | `verdict_path = ctx.saga_dir / "verdict.json"` | tools/saga_driver.py:425 |
| 23 | `main()` returns 0 regardless of terminal saga status | `return 0` | tools/saga_driver.py:732 |
| 24 | `--threshold` is declared but never read as a gate | `parser.add_argument("--threshold", type=int, default=90)` | tools/saga_driver.py:644 |
| 25 | The child process is wrapped in GNU `timeout`, absent on stock macOS | `"timeout"` | tools/saga_driver.py:393 |
| 26 | `tools/` is the canonical source and the plugin bundle is regenerated by `rm -rf` | `TOOLS_FILES` | tools/sync-plugin-framework.sh:33 |
| 27 | The linter has a second vendored mirror under Hermes | `import yaml` | platforms/hermes/sdd_doc_lint/__init__.py:30 |
| 28 | Nine autopilot skills mandate the driver as the sole orchestration mechanism | `MANDATORY orchestration step` | platforms/claude-code-plugin/skills/doc-brd-autopilot/SKILL.md:85 |
| 29 | `review_hook` is documented with three values controlling hook behavior | `review_hook` | platforms/claude-code-plugin/docs/CONFIG.md:73 |
| 30 | `requirements-analyst` declares neither `tools:` nor `model:` | `name: requirements-analyst` | platforms/claude-code-plugin/agents/requirements-analyst.md:3 |
| 31 | The plugin manifest declares MIT while shipping no license text | `"license": "MIT"` | platforms/claude-code-plugin/.claude-plugin/plugin.json:10 |
| 32 | The marketplace manifest ships a personal email | `"email"` | .claude-plugin/marketplace.json:6 |
| 33 | `SECURITY.md` names a spec version five minors stale | `0.35.x` | SECURITY.md:11 |
| 34 | ❌ **FALSE — retracted 2026-08-02.** `SECURITY.md` names scanners CI does not run | `bandit` | SECURITY.md:49 — **`bandit` DOES run in CI**: `.github/workflows/pre-commit.yml:37` calls canon's reusable, which runs `pre-commit run --all-files`, so `.pre-commit-config.yaml:45-50` executes inside the required `call / Lint / format / security hooks` context. The row's *shape* held for a different entry: `pip-audit` is configured in that file and runs automatically nowhere (`stages: [manual]`, `.pre-commit-config.yaml:98`), which #422 resolved by **stating** it at `SECURITY.md:100-102` rather than by deletion. The real defect was an incomplete list plus one unqualified entry — the cited *symbol* was simply wrong |
| 35 | `ROADMAP.md` states a stale plugin version | `0.23.4` | ROADMAP.md:56 |
| 36 | `playbook_loader` joins caller-supplied segments with no traversal guard | `resolve_playbook_path` | tools/playbook_loader.py:18 |
| 37 | Raw file tokens are embedded in finding messages that reach model context | `malformed element id` | tools/sdd_doc_lint/__init__.py:642 |
| 38 | The `REGISTERED` shim exists only to pull `tests/unit/` modules in; conformance-resident modules are auto-discovered | `REGISTERED` | tests/conformance/test_repo_scripts.py:31 |
| 39 | `project-init` only **reads** `.aidoc/profile.yaml` — it creates neither it nor a project-local registry, so neither is a sound adoption marker | `.aidoc/profile.yaml` | platforms/claude-code-plugin/skills/project-init/SKILL.md:99 |
| 40 | The linter locates a project profile by walking up from the target — the pattern H2's config lookup must mirror | `find_profile` | tools/sdd_doc_lint/__init__.py:76 |
| 41 | Findings are routed per-severity — errors to **stderr**, warnings to **stdout** — so **neither stream alone carries every finding** on the exit-1 path | `stream = sys.stderr if f.severity == "error" else sys.stdout` | tools/sdd_doc_lint/__main__.py:107 |
| 42 | The rendered severity literal is `WARNING`, not `WARN` | `def __str__` | tools/sdd_doc_lint/__init__.py:219 |
| 43 | A **user-global** `~/.aidoc/profile.yaml` is documented, so an unbounded upward walk is not a project-scoped signal | `User-global seed` | platforms/claude-code-plugin/skills/project-profile/SKILL.md:55 |
| 44 | `docs_root` is documented with a trailing slash and may be multi-segment | `docs_root: docs/` | platforms/claude-code-plugin/docs/CONFIG.md:47 |
| 45 | A release gate fails if any `SKILL.md` contains the literal `--dangerously-skip-permissions` | `NoDangerousFlagDefaultsTests` | tests/release/test_marketplace_gate.py:39 |
| 46 | A fourth unconditional `PARTIAL_TIMEOUT` transition exists in `main` | `to_state="PARTIAL_TIMEOUT"` | tools/saga_driver.py:721 |
| 47 | `main` already reloads the saga from disk after dispatch; the clobber precedes it | `saga = json.loads(ctx.saga_file.read_text())` | tools/saga_driver.py:696 |
| 48 | The existing resume fixture carries no `scope` keys, so a bare `== "run"` filter fails a required context | `test_resume_walks_back_from_partial_timeout` | tests/conformance/test_saga_driver_invariants.py:71 |
| 49 | `main` also returns 0 straight after the break circuit sets `PARTIAL_TIMEOUT` | `return 0` | tools/saga_driver.py:679 |
| 50 | The acceptance harness records FAIL on a non-zero driver exit | `driver_rc=$?` | tests/scripts/test-acceptance.sh:1177 |
| 51 | The acceptance harness asserts the hook emits structural findings; the fixture is staged under `docs/01_BRD/`, so H1's path marker is already satisfied and only H2 breaks it | `STRUCT01\|structural findings` | tests/scripts/test-acceptance.sh:1870 |
| 52 | The acceptance harness passes `--threshold 90` on every cascade layer, so removing the flag makes argparse exit 2 before any saga work | `--threshold 90` | tests/scripts/test-acceptance.sh:1175 |
| 55 | The harness captures the hook with `2>&1` and asserts the result parses as JSON, so any stray stderr byte fails the element | `jq . > /dev/null 2>&1` | tests/scripts/test-acceptance.sh:1866 |
| 56 | The harness is the only non-skill invoker of the driver, and passes neither the new flag | `saga_driver.py` | tests/scripts/test-acceptance.sh:1173 |
| 57 | The driver's only config read is `.aidoc/profile.yaml`, never the plugin config file the plan's config key would live in | `.aidoc/profile.yaml` | tools/saga_driver.py:160 |
| 53 | The changelog already claims `--threshold` was removed from the driver; the driver half never happened | `removed the dead` | CHANGELOG.md:1125 |
| 54 | A Hermes VERSION bump fans out to **five** files — `CLAUDE.md`, `README.md`, `platforms/hermes/README.md`, `docs/PARITY.md`, `platforms/hermes/pyproject.toml` — via a pre-commit hook that re-stages its own writes | `hermes_prev` | scripts/sync-version-refs.sh:339 |

<!-- markdownlint-enable MD050 -->

## Review log

### Pass 1 — 2026-07-31 — self-review

Six load-bearing gaps found and folded in:

1. **Wrong test-registration instruction.** The draft told PR authors to register
   new conformance tests in `test_repo_scripts.py`'s `REGISTERED` tuple. That
   tuple exists *only* to pull `tests/unit/` modules into a suite that cannot
   reach them by pattern; a module already living under `tests/conformance/` is
   auto-discovered, and registering it would be wrong. Corrected, with claim 38.
2. **Config lookup assumed CWD == project root.** H2 said to read
   `.claude/aidoc-flow.config.yaml` "from the project root". The hook's CWD is
   not guaranteed to be that. Changed to walk up from the edited file, mirroring
   `find_registry`/`find_profile`; claim 40 added.
3. **No decision record.** Making the permission bypass opt-in is a policy choice
   embedded in shipped code — exactly what `plans/DECISIONS.md` authorizes — and
   the draft never created one. Added to PR 5.
4. **Backlog entries were closed but never created.** PR 5 said it would close
   `FRAMEWORK-TODO` entries and issues that no stage created. Moved creation to
   PR 1 so a stall mid-sequence leaves a readable queue.
5. **Tag/Release treated as routine.** Cutting a tag and publishing a public
   Release are outward-facing and fall outside the AI auto-merge default. Marked
   founder-gated.
6. **Hermes mirror status unstated.** PR 2 touches a surface Hermes vendors, and
   the draft asserted a PATCH bump without establishing whether the mirror was
   already drifted. Verified in sync (four of four modules byte-identical) and
   recorded, along with the pre-existing red Hermes pytest baseline so a failure
   is not misattributed to this work.

**Result:** six findings, all folded. Gate re-run green. Proceeding to the
independent pass.

### Pass 2 — 2026-07-31 — independent

Fresh-context `verified-planning-reviewer` against the post-Pass-1 draft. It
returned **13 load-bearing findings and 6 minor**; I re-verified every
consequential one against source before folding. All are folded; claims 41–51
added, claims 3, 25 and 39 corrected.

Five findings invalidated a plan step outright — the draft, executed literally,
would have shipped these regressions:

1. **PR 1 step 2 would have silently disabled structural findings entirely.**
   The linter prints error-severity findings to **stderr**, and exit 1 occurs
   only when an error exists — so stdout is empty on exactly the path the hook
   cares about. Filtering *stdout* would drop 100% of findings, forever, silently:
   the very regression class this plan exists to prevent. `2>&1` is load-bearing
   correctness today, not a pure defect. Redesigned to filter the *stderr*
   stream. Claim 3 reworded so an implementer cannot repeat the error.
2. **H1's adoption markers do not exist in projects the plugin itself
   initializes.** `project-init` only *reads* `.aidoc/profile.yaml` and makes
   template copying optional, so it creates neither marker — the gate would have
   disabled the feature on the plugin's own greenfield happy path. Claim 39 was
   semantically false as written. Redesigned around the scaffolded
   `<docs_root>/0N_<ARTIFACT>/` tree, plus a `$HOME` bound for the documented
   user-global `~/.aidoc/profile.yaml`.
3. **B3c's one-line fix would have broken a required context.** The existing
   conformance fixture carries no `scope` keys, so `t.get("scope") == "run"`
   makes every entry `None` and falls through to the `PREPARED` reset — failing
   `conformance` and, worse, restarting any real journal whose transitions an
   LLM wrote directly. Corrected to `t.get("scope", "run")`.
4. **PR 3's disclosure would have tripped a release gate.** `tests/release/`
   fails if any `SKILL.md` contains the literal `--dangerously-skip-permissions`
   — and PR 5 cuts a release. The 9 skills now name only the new opt-in flag.
5. **PR 1's `timeout 10` would have reintroduced in the hook the exact macOS
   defect PR 3 removes from the driver.** Dropped in favour of `hooks.json`'s
   host-enforced timeout.

Scope and sequencing corrections: B3a covers **four** wedge call sites, not
three; M4 must fix the post-break-circuit `return 0` as well as the final one,
and `test-acceptance.sh` consumes that exit code; B3b is a write-ordering fix
inside `dispatch_phase`, not a missing reload (`main` already reloads); L5 was
never actually closed, since the `--warn-exit` flag needs the hook to pass it —
PR 2 now explicitly depends on PR 1; H1 and H2 break the acceptance harness's
hook element, which the draft never touched — now a required PR 1 step; the
`\[(ERROR|WARN)<SP>` grammar can never match `WARNING`; `docs_root`'s documented
trailing slash would have made the L4 substitution match nothing.

Minor, folded: `tests/release/` and `tests/smoke/` added to Verification;
PyYAML failure gets a distinct exit code 3 rather than overloading 2 a third
time; `playbook_loader` does have a (unguarded-tier) test; M7's scanner list also
omitted trivy and CodeQL; the PR 1 / PR 3 `README.md` conflict noted; scratch-dir
tests would false-pass inside this repo or without `jq`.

**Result:** 13 load-bearing findings, all folded. A third independent pass is
warranted before implementation begins, since findings 1–5 changed the design of
both PR 1 and PR 3 rather than merely their wording.

### Pass 3 — 2026-07-31 — independent

Fresh-context reviewer, tasked primarily with checking whether Pass 2's folds
actually landed. **10 load-bearing findings**, all verified against source and
folded. Claims 52–54 added; claims 10 and 51 corrected.

The headline: **Pass 2's fold of its own finding 1 was itself wrong.** Claim 41
said errors go to stderr; the fold read that as "all findings go to stderr" and
prescribed filtering stderr alone. Warnings go to **stdout** — so the `WARNING`
alternative in the grammar was dead, and once PR 2's `--warn-exit` landed, a
warnings-only document would have produced a byte-empty stderr and no findings
block. L5 would have stayed open while the plan asserted it closed: the exact
failure mode Pass 2 finding 1 existed to prevent, reproduced one layer down.
Now: keep `2>&1`, filter the combined stream.

Other step-invalidating findings:

- **Removing `--threshold` would break the live cascade at every layer.** The
  acceptance harness passes `--threshold 90`; deleting the argparse entry makes
  the driver exit 2 on a usage error before any saga work, failing layer 1 and
  aborting under `FAIL_FAST`. The draft called removal "preferred". Now: keep the
  flag. Related discovery — the changelog already claims this removal shipped in
  `0.23.4`, and for the driver it never did.
- **The prescribed filter would have inverted the hook's exit test.** The natural
  implementation is a pipeline, after which `$?` is *grep's* status — and grep
  exits 1 when nothing matched, i.e. on clean documents. Now: capture `rc` on the
  unpiped run, filter afterwards.
- **B2's default-off had no path back on.** Every invoker passes only `--layer`,
  so a documentation-only disclosure would strip the bypass from the plugin's
  primary path. Now: the 9 skills *pass* `--allow-skip-permissions`, and the
  config key is assigned to `docs/CONFIG.md` (a PR 3 surface it previously lacked).
- **PR 2's "both modules" resolves to a PR 3 file.** Only `__init__.py` imports
  yaml at module level inside `tools/sdd_doc_lint/`; the other is
  `tools/saga_driver.py`. As written the guard was either never authored or
  authored into the Hermes mirror, which the sync destroys.

Diagnosis and bookkeeping corrections: the acceptance hook element breaks under
**H2 alone**, not H1 — the fixture already sits under `docs/01_BRD/` and
satisfies H1's marker, so "restage with an adoption marker" was work against a
wrong diagnosis (and H1 consequently has no harness coverage); PR 1's H1 failing
test could not fail for H1's reason, since the default `on` suppresses findings
regardless; PR 2's design said exit code 3 while its test-first step still said
2; Pass 1's backlog fold had landed only in prose, with no `FRAMEWORK-TODO` or
`DECISIONS` row in the file table; and the Hermes PATCH bump has no assigned file
*and* silently makes PR 2 a governance PR via `sync-version-refs.sh`'s
`CLAUDE.md` propagation.

Confirmed clean on re-derivation: B3a's four call sites are the complete set;
M4's two return sites are the complete set; `t.get("scope", "run")` keeps both
existing resume fixtures green and does suppress branch-scoped terminals; B3b is
correctly diagnosed as a write-ordering bug; the grammar does reject tracebacks
and the summary line; `--allow-skip-permissions` does not trip the release gate;
there are 9 autopilots, not the 8 that `CLAUDE.md` states.

**Result:** 10 load-bearing findings, all folded. Two independent passes have now
each invalidated design steps — including one that invalidated the previous
pass's own fix — so this plan is **not ready**, and per the OPS-0066
circuit-breaker one further independent pass is the last permitted before the
open items go to the founder instead.

### Pass 4 — 2026-07-31 — independent (third and final permitted)

**10 load-bearing findings, 5 invalidating a step.** Eight are folded; **two
require a founder decision and are recorded under "OPEN" above**. Claims 55–57
added; claims 3, 41 and 54 corrected.

The pattern this pass was dispatched to hunt — a fold that is itself half-right —
recurred: PR 3's B2 fold correctly identified that both the 9 skills *and* the
live cascade would lose the permission bypass, then patched only the skills. The
harness invocation is now patched too.

Step-invalidating, folded: the harness's driver call needed the opt-in flag; the
Hermes fanout is **five** files, not one, and the ≤3 cap cannot be met by the
plan's usual split remedy (→ O2); the Implementation sequence still called PR 2
"independent of PR 1" eight lines above the paragraph establishing the
dependency; PR 1 must redirect stderr on every new command or it fails the
harness's JSON assertion with a misleading reason, and must use `wc -c` rather
than the GNU-only `stat -c%s`.

Wording-level, folded: claim 41 still carried the inference Pass 3 refuted (the
prose was right, the claim an implementer would cite was not); `DECISIONS.md` and
the README prerequisites were each assigned to two different PRs; the headline
finding count said 25 against an enumeration of 23; the Modified table omitted
`VERSION`, `HANDOFF.md` and PR 4's agent rename; PR 1's "hooks/ only" heading was
falsified by its own step 9. Minor riders folded: `read_verdict_score` should
coerce `int(... or 0)` before any comparison; M4's non-zero exit degrades the
harness's failure attribution under `FAIL_FAST`.

Confirmed clean on re-derivation: PR 1 step 2 is now correct across all four
output cases (errors-only, warnings-only, mixed, crash), and the unpiped-capture
prescription is a minimal delta on the existing line;
`--allow-skip-permissions` does not trip the release gate and keeps the autopilot
saga-parity conformance test green; H1's path marker is satisfied by the harness
fixture and the H2 walk-up does reach the staging point; B3a's four sites and
M4's two return sites remain the complete sets.

**Result:** NOT READY. Three independent passes have each invalidated design
steps, so per the OPS-0066 circuit-breaker no fourth is dispatched. Eight
findings are folded; **O1 and O2 above are open and blocking.** The plan PR must
not open until the founder resolves them and one further verification pass
confirms the folds.

### Pass 5 — 2026-07-31 — focused verification of the O1/O2 folds

The founder resolved O1 (ship the flag alone) and O2 (skip the Hermes bump); I
folded both and dispatched a **scoped** verification — not a fourth general
review, which the circuit-breaker forbids — asking only whether those two folds
landed completely.

It found **two load-bearing misses in my own folds**, both now fixed:

1. The O1 fold reached the PR 3 design section and the Modified table but **not
   the "Docs to update" line**, which still instructed PR 3 to document the
   config key in `docs/CONFIG.md` — i.e. to ship exactly the artefact O1
   rejected. That line is the one an implementer assembles a PR's file list
   from, so the miss was consequential, not cosmetic. It also put PR 3 at 5 doc
   surfaces; it now lands at 3.
2. The same clause still assigned `plans/DECISIONS.md` to PR 3, contradicting
   the Modified table's deliberate PR 5 placement — the decision record was
   simultaneously mandated where the table forbids it and absent where the table
   assigns it. Moved to PR 5.

Also fixed: the `README.md`/`docs/CONFIG.md` Modified row was split, since those
two files no longer share a PR set; and the O1 paragraph named the driver's
profile knob as `max_iterations` when it is `quality_loop_max_iterations`
(claim 57's substance is unaffected).

Verified clean by that pass, against source rather than assumption: **skipping
the Hermes VERSION change genuinely avoids the five-file fanout** — the
pre-commit hook is gated on the staged path (`^(platforms/[^/]+/VERSION|framework/VERSION)$`),
and no file in PR 2's set matches, so `sync-version-refs.sh` never runs;
Hermes' `CHANGELOG.md` does have an `[Unreleased]` section to write into; and
claim 57 is semantically true (the driver has exactly three config-related
lines, all the same `.aidoc/profile.yaml` path). Every other O2 surface —
Version impact, Modified table, Risks, Docs-to-update, and the former
governance-PR paragraph — agrees on no bump.

After applying the four fixes I re-checked every `docs/CONFIG.md`,
`DECISIONS.md` and `hermes/VERSION` reference in the file by inspection; the
only surviving mentions of the rejected shapes are inside the historical Pass 3
log, which is a record of what that pass said and is correct as such.

**Result:** ready. No further independent pass is dispatched — the OPS-0066 cap
is exhausted, and the two residual findings were scoped corrections to my own
folds, verified by inspection. The remaining risk is carried openly in the Risks
table (notably the accepted O2 trade-off).
