# Session Handoff

**Purpose:** everything a *fresh* session needs to start work here with zero prior
context — current state, what to do next, and the traps that cost an earlier session
real time. Nothing else.

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
| `CLAUDE.md` | the durable working agreement, auto-loaded every session | permanent |
| **this file** | current state + next tasks + traps **not** yet in `CLAUDE.md` | **rewritten each merge** |

**A trap already recorded in `CLAUDE.md` is not repeated here** — CLAUDE.md is loaded
automatically, so duplicating it just creates two copies to drift apart. In particular
CLAUDE.md already owns: the `--repin` vs `--update` distinction, `LITELLM_BASE_URL`
must be the Docker-bridge address, `secret-scan` at v2 scans full git history,
`GITHUB_TOKEN`-triggered events create no workflow run, check-run retention/rollup
semantics, the runner split incl. why `sast-scan` is the `ubuntu-latest` exception, the
`#329` concurrency allowlist by *shape*, and never hand-editing example artifacts.

## Where we are — 2026-07-30

Framework spec `0.40.0`, Claude Code plugin `0.24.0`, Hermes `0.12.0` — **no version
stream moved today**. **Open PRs: 0. Open issues: 2** —
[#385](https://github.com/vladm3105/aidoc-flow-framework/issues/385) and
[#386](https://github.com/vladm3105/aidoc-flow-framework/issues/386), both unchanged.

**`doc-maintainer` is PAUSED, and CI is green again.**
[#397](https://github.com/vladm3105/aidoc-flow-framework/pull/397) set
`kill_switch: true`. Verified in production, not assumed: the merge's own `push` run
succeeded with `doc-maintainer kill_switch=true; exiting cleanly (no LLM cost incurred)`.
Only one other `push` run had gone green since adoption, and that one passed by
proposing nothing; this is the first that is green *by design*. The caller, its config
and its conventions all stay in place; resume is a one-line flip.

It had 23 failures / 47 runs across **four** independent upstream defects — not the two
previously recorded, and **not** the config mismatch this repo was blamed for (retracted;
see Next tasks item 2 and **D-0072 §2**). The full census lives in D-0072 and in
`.github/doc-maintainer-conventions.md`, which is kept current for the resume; do not
copy it here.

**Resume requires ci#352 AND ci#353** — #353 alone is 15 of the 23, so flipping on #352
alone returns a majority-red pilot. #352 is the smaller count and still the blocker for
*graduation*: no plan containing a low-risk edit can complete a dry run, which is the
path a dry-run pilot exists to validate.

**Pin-currency reader (#392/#394) shipped earlier; V10–V14 all passed, so PR 3 is
unblocked.** **V15 (schedule→`workflow_run` chain) is still unconfirmed** — it was never
a gate; V14 proved the chain off a *dispatched* upstream. Whoever sees the first Monday
`standards-drift` run should check a `pin-currency-reader` run followed it, then delete
this paragraph.

## Next tasks — prioritized

The full queue is `plans/FRAMEWORK-TODO.md` (`## Open`) and
`plans/HERMES-BACKLOG.md`. This is only the ordering a fresh session should use.

1. **`PIN-CURRENCY-NO-READER` — PR 3, then PR 4. Both are governance PRs; the founder
   merges.** The gate they waited on has passed.
   - **PR 3** = `plans/DECISIONS.md` (a new `D-00NN`: why the log and not annotations,
     why the reader fails loudly), `plans/FRAMEWORK-TODO.md` (the entry at line ~107 →
     `## Closed` with the merge ref), and this file. **That is Rule 1's cap of three.**
     ⚠️ CI's `call / ai-review` independently demands a `CHANGELOG.md` `[Unreleased]`
     entry for substantive changes; if it demands one here, that is a **fourth** surface
     and the fix is to move this file out into its own follow-up, **not** to exceed the
     cap. Budget accordingly.
   - **PR 4** = `CLAUDE.md` (the annotation-cap trap at the granularity M1 supports,
     plus the concurrency inventory's **fourth** shape — `cancel-in-progress: false`
     under a fixed group, which `pin-currency-reader.yml` introduced) and the plan's
     Status → `IMPLEMENTED`. **Fold one more `CLAUDE.md` correction in while it is
     open:** it says "sixteen call sites across fifteen files"; the real count is
     **17 across 16** since #382 added `doc-maintainer.yml`. Re-count rather than
     copying that figure —
     `grep -rcE '^\s*uses: vladm3105/aidoc-flow-ci' .github/workflows/*.yml`.
   - The plan's §PR sequencing is the contract; read it rather than this summary.
2. **`doc-maintainer` — nothing to do here; it is paused and waiting on upstream.**
   Watch `aidoc-flow-ci` #352 and #353. When **both** ship in a released `ci/vX.Y.Z`:
   re-pin this caller, flip `kill_switch` → `false` in `.github/doc-maintainer.json`,
   and watch the next few `push` runs. Do **not** flip on #352 alone.

   ⚠️ **Do not re-file the `high_risk_paths` / `allowed_paths` mismatch as a defect.**
   It is deliberate, inert, and documented in the config itself; #396 recorded it as a
   bug and was wrong. D-0072 point 2 explains why the error message manufactures that
   misreading.

   `gh secret list` shows `LITELLM_BASE_URL` **and** `LITELLM_DOC_API_KEY` present here;
   only `AIDOC_FLOW_BOT_ID` / `AIDOC_FLOW_BOT_KEY` are absent, and those are **live-mode
   only**. Verify with `gh secret list` before repeating any secrets claim.
3. **`FRAMEWORK-TODO.md` hygiene — bigger than "pick a convention".** The queue is
   unreliable in *two* directions: entries marked `✅ CLOSED` sit under `## Open` (so it
   **overstates** what is open), and `## Closed` holds unmarked entries that read as
   live backlog — `[gate] Component-decomposition gate missing between PRD and ADR`,
   `[harness] Cascade harness lacks --skip-lint-smoke flag`, `[template] IPLAN
   sub-types: code-build vs deploy` — so it also **hides** open work, which is worse.
   Scope the sweep to both, and pick one convention stated at the top of the file.

   **Re-run these rather than trusting any count written down** — this figure has gone
   stale twice inside the very text documenting it, because the file is append-at-top:

   ```sh
   awk '/^## Open/{o=1} /^## Closed/{o=0} o&&/✅ CLOSED/{n++} END{print n}' plans/FRAMEWORK-TODO.md
   awk '/^## Closed/{c=1} c&&/^### /{e++} c&&/✅ CLOSED/{m++} END{print e, m}' plans/FRAMEWORK-TODO.md
   ```

4. **[#385](https://github.com/vladm3105/aidoc-flow-framework/issues/385) — the `#342`
   regression guard scans less than it claims.**
   `tests/conformance/platforms/test_no_inprompt_hashing.py:99`/`:103` use
   `glob("doc-*/SKILL.md")` and a non-recursive `glob("*.md")`, so **41 of 52** plugin
   SKILLs and **36 of 39** Hermes references are scanned. The 3 unscanned Hermes files
   are all of `references/batch-brd-processing/`, and
   `batch-remediation-script.md:24` still computes element IDs with its own
   `hashlib.sha256` routine that diverges from the normative transform on four points.
   The 11 unscanned plugin SKILLs are clean today — that half is latent. The guard's own
   docstring (`:92`) forbids narrowing coverage by glob, which is what happened. Fix is
   `rglob` both + point the script at `rehash --compute`; the issue carries the census
   command. **A green run of this guard is not evidence that no surface hashes.**
5. **[#386](https://github.com/vladm3105/aidoc-flow-framework/issues/386) — the
   framework-spec token gates five files on `CLAUDE.md`'s own state.**
   `sync-version-refs.sh:218` reads `fw_prev` from `CLAUDE.md` **and** uses it to gate
   propagation to `README.md`, `docs/PARITY.md`, both platform READMEs and a
   conformance-test literal — so correcting `CLAUDE.md` first strands all five, silently,
   at exit 0. #389 fixed the plugin and Hermes tokens by detecting each from `CLAUDE.md`
   and writing only `CLAUDE.md`; this one cannot take that shape unchanged, because its
   `prev` is load-bearing elsewhere. Fix shape: derive the gating `prev` from a fanout
   target nobody hand-edits (`docs/PARITY.md`), and give `CLAUDE.md` its own block. The
   SKILL frontmatter, playbooks and `platforms/*/FRAMEWORK_SPEC_VERSION` are **not** in
   the blast radius — each has its own detector, measured.
6. **Hermes parity — the residual arc.** `plans/HERMES-BACKLOG.md`: remaining
   plugin-vs-Hermes deltas plus quality-loop Phase 2 (cross-invocation resume / G-R1,
   the parallel-review global lock).
7. **Everything else** is in `FRAMEWORK-TODO.md` by tag (`[ci]`, `[lint]`,
   `[template]`, `[harness]`, `[example-corpus]`, `[docs]`, `[skill]`, `[sync]`),
   including the D54 and Engramory consumer-feedback batches. Nothing there is
   blocking.

**Standing:** the example corpus is regenerated wholesale after framework changes, so
corpus-remediation findings are deferred to that regen rather than fixed in place.
IPLAN ↔ iplanic integration is deferred (`plans/IPLAN-IPLANIC-DEFERRED.md`).

## Stale advice — a fresh session will find these referenced, and they are FIXED

Older plans, TODO entries and commit messages still describe these as live. They are
not. Verified 2026-07-29 unless noted.

| Stale claim | Reality |
|---|---|
| "`--admin` is required on every PR" (the `ai-review` self-cancel, `aidoc-flow-ci#322`) | **Fixed at `ci/v2.16.0`.** #378, #380, #392 and #394 all reached mergeable with no `--admin` |
| "Branch protection requires the phantom `Lint / format / security hooks`, so every PR is BLOCKED" | **Fixed.** The six required contexts, read from the API on 2026-07-30, are `call / Lint / format / security hooks`, `call / composition`, `call / ai-review`, `call / verify`, `Framework + platform conformance`, `Acceptance tier (deterministic)`. `call / trust` is **not** required |
| `AIDOC-CI-COMPOSITION-CHECK-PRHEAD` — "`call / composition` is structurally unsatisfiable on a PR head" | **Stale.** composition reports success on PR heads. A reviewer once read this entry as proof that required checks gate nothing here, and it nearly killed a correct plan |
| "commits need `SKIP=gitleaks`" | **Fixed** (#355) — the local gitleaks hook was dropped; CI's is unaffected |
| "the acceptance deterministic tier has 3 pre-existing failures on `main`" | **Fixed** (#365, #371/#372). 0 failures / 64, and the tier is now a **required** context |
| `NO-PIN-CURRENCY-CHECK` — "this repo runs `check-pin-currency.sh` nowhere" | **Retracted, it was false.** See below |
| `PIN-CURRENCY-NO-READER` — "the fix is a workflow that **runs the script** and opens an issue" | **Superseded and now SHIPPED** (#392). Running the script would be the second detector the same entry forbids; the reader consumes the completed run's **log** |
| The plan's "a live `clean` check is deliberately absent … verified only by V4's stub" | **Overtaken by events.** Canon `main` and every caller here are both `ci/v2.16.0`, so a live run reports `clean` — V14 exercised close-on-clean for real |
| `plans/PLAN-*.md` as the governance-PR plan glob (`CHANGELOG.md`, `CI-CANON-V2.16-MIGRATION-PLAN.md:468`/`:784`) | **Fixed in `CLAUDE.md`** (#387/#390). The glob is a **suffix** — `plans/*-PLAN.md`. Merged plans and the CHANGELOG keep the old string as history; `CLAUDE.md` is the live rule |

**The retraction, because the lesson generalises.** That entry named an absence as the
cause of a mixed-pin state surviving two days. The check *does* run — canon's
`check-standards-drift.sh` tail invokes it on every weekly `standards-drift` run — and it
fired on 2026-07-27 naming all ten stale pins **and** the `--repin` remedy. The proposed
fix would have added a **second copy of a check that was already running and already
right**. The real gap was that a warning-only annotation on a weekly scheduled job has no
reader, which is what #392 closed. One `gh run view --log | grep pin-currency` falsified
it. **An absence is the easiest defect to assert and the hardest to verify — read the log
before writing one down.**

## Durable traps — do not re-derive these

### Merging and CI mechanics

- **`call / verify` greps a commit body for a literal phrase**, and it is a *required*
  context — so a missing or paraphrased phrase blocks the merge. Exactly one of:
  `Multi-agent self-review per OPS-0065 (<agents>): <verdict>` or
  `Self-review skipped per founder OK — <reason>`. It is `grep -qF`; nothing else
  matches, and the phrase belongs in the **commit message**, not the PR body.
- **Stacked PRs: retarget the child before merging the parent.** Merging #357 with
  `--delete-branch` deleted #358's base, which **auto-closed #358**, and GitHub refuses
  to retarget a closed PR — it had to be rebuilt by cherry-picking onto `main`. Prefer
  branching each PR from `main` when the files don't overlap.
- **`Closes #A and #B` closes only `#A`.** The keyword is needed before *each*
  reference.
- **`report-only` protects the verdict, not the toolchain.** `sast-scan` went red on
  first run *with* `fail-on-findings: false` set, because its semgrep venv install
  failed before any findings logic. A report-only flag is not evidence a new caller
  cannot fail.
- **Reading drift output: count `::warning::drift-check:`, not `::warning::`.** A bare
  grep returns 12 for 10 annotations — `standards-drift.yml`'s canon header quotes the
  literal string, so its own drift body reproduces it twice.
- **Canon's manifest presence check is case-sensitive.** It lists
  `.github/pull_request_template.md`; this repo carries `PULL_REQUEST_TEMPLATE.md`,
  which reads as *absent*. Caught only because `pre-commit`'s case-conflict hook
  rejected the duplicate that mistake produced.
- **Never truth-test a `jq` scalar that can be `null`.**
  `gh api …/contents/<missing> --jq '.name'` emits the string `null`, which
  `[ -n "$n" ]` reads as **present** — that inverted a blast-radius finding from "no
  sibling repo adopts this" to "all seven do" until re-checked by listing the directory.

### Reading CI output (new 2026-07-30 — PIN-CURRENCY-READER plan)

`CLAUDE.md` does not own these yet; the plan's PR 4 propagates the first one.

- **The check-run annotations API silently truncates at 10 warnings, keeping the
  earliest.** Measured on check-run `89950624082`: the job emitted **22** `##[warning]`
  lines and the API returns **10 of them** — dropping all ten `pin-currency:` lines,
  because they are emitted at the drift script's tail. So **`gh api …/annotations` is not
  a substitute for the log** when the thing you want is emitted late.
  - **The response length is 11, not 10** — 10 `warning` plus 1 `notice`. Verify with
    `--jq 'group_by(.annotation_level)|map({(.[0].annotation_level):length})|add'`, not
    `length`, or this trap reads as false and gets discarded.
  - That surviving `notice` **is** evidence the cap is applied **per annotation level**:
    a full 10 warnings did not crowd it out. What stays unattributable from this run is
    per-step vs per-job vs per-run — the whole script is one `run:` step, so those three
    are indistinguishable here. PR 4 writes the cap into `CLAUDE.md`; it may claim
    per-level, not per-step.
- **A downloaded log contains `##[warning]`, never `::warning::`.** `gh run view --log`
  renders the workflow command. `grep -c '::warning::'` on it returns **0** while
  `##[warning]` returns 22. This is a different trap from the drift-body one below, and it
  silently makes a grep-based reader match nothing.
- **A measurement is dated to the canon version that RAN, not the one you have checked
  out.** Run `30257877863` executed `check-standards-drift.sh` at **`ci/v2.14.0`** (380
  lines) while the local checkout is `v2.16.0` (523 lines) — `emit_coverage` shipped in
  `v2.15.0` and does not exist in what ran. Cost most of a review cycle: a reviewer
  correctly derived a 23rd warning from the v2.16.0 source and concluded the measured 22
  was wrong. **Read the `adopted canon pin` notice in the run's own log before citing line
  numbers at it.**
- **`check-standards-drift:` is a PREFIX, not a completion marker.** The drift script
  emits an opening `repo=… tier=…` header and a `cannot check <family>` warning per
  unreadable family under that same prefix — the first of them **24 lines ahead** of the
  pin-currency section. A log truncated in that window satisfies a prefix test. The
  terminal markers are the summary line (`check-standards-drift: N drift,`) and
  `check-standards-drift: coverage —`, the latter emitted by `emit_coverage` at normal
  termination *and* from every `stop_uncheckable` early exit. This shipped as a real
  silent-failure path and was caught in review, not by a test.
- **Canon false-greens two ways, and one would make a reader close a tracking issue.**
  `check-pin-currency.sh:62` greps `@ci/v…` literally, so a **SHA-pinned** caller is
  invisible and reports `all pins current ✅` — and the *fleet* path at `:71` **does**
  match `@<40hex> # ci/v…`, so this is two paths in one script disagreeing, which is a
  far stronger upstream ask than a plain omission. Second path: if the `curl` of canon
  `main`'s `VERSION` returns an error page instead of failing, `ver_cmp` (`:39`) compares
  non-numeric fields under `2>/dev/null`, every comparison falls through to equal, and
  `:101` prints the same green. **`:87` is the only validation there is** — an emptiness
  guard — and an error-page body is non-empty, so it slips straight past. Validate a
  resolved canon token against `^ci/v[0-9]+\.[0-9]+\.[0-9]+$` before trusting any verdict
  built on it. Both are filed upstream by the plan's Task 3; cite `:39` + `:101` for the
  second, not `:87`.

### Local hooks and tooling

- **`tests/unit/` is executed by no hook and no workflow** — `.pre-commit-config.yaml:106`
  discovers `tests/conformance` only, and the workflows run `tests/conformance`,
  `tests/acceptance/deterministic`, `tools/sdd_doc_lint/tests` and Hermes' own suite.
  `pre_push_check.sh` invokes no `unittest` at all. So ~30 modules under `tests/unit/`
  (including `test_sync_scripts.py`) are **unguarded after merge**: a test placed there
  proves something once, locally, and never again.
  - **The one runner that exists is worse than none.** `tests/scripts/test-plugin.sh:257`
    and `:302` do `python3 -m unittest discover tests/unit` — but **nothing calls that
    script** (grep `.github/workflows/`, `.pre-commit-config.yaml`, `scripts/`), and both
    call sites end in `|| true`, so even the manual path cannot fail. Wiring the hook is
    therefore reuse, not authoring; dropping the `|| true` is the deeper fix.
  - This is why the merged PIN-CURRENCY plan adds a registration shim, and why R6 there
    says "no hook and no workflow" rather than "nothing" — that wording is accurate as
    written. Fixing the class instead of the instance is an accepted open item.
- **Local `pre-commit` on changed files ≠ CI's `--all-files`.** A rebase conflict
  resolution once dropped a blank line before a CHANGELOG heading; local hooks never
  re-linted the seam and CI failed on MD022. **Run `pre-commit run --all-files` after
  any manual conflict resolution.**
- **markdownlint autofix corrupts prose in two specific ways.** A line starting
  `#NNN` becomes an H1 (`# NNN`) — write `Issue #NNN` or backtick it; and
  `__init__.py` becomes `**init**.py`, silently breaking claim-ledger citations —
  backtick any path containing underscores. Both were hit again this session. **Eight
  older plan files still carry the `**init**.py` corruption** from before it was
  documented.
- **`sync-version-refs` reporting "files were modified" is usually a knock-on**, not a
  second defect — it re-stages whatever an earlier autofix touched. Verify by running
  it alone against a clean HEAD.
- **Editing `tools/sdd_doc_lint/*.py` requires re-copying both vendored platform
  mirrors by hand.** No script does it, and `ruff-format` may rewrite the file *after*
  you copy — re-copy and re-run until two consecutive `--all-files` runs are clean. The
  linter's own sync script is `tools/sdd_doc_lint/sync-vendored.sh`, **not**
  `tools/sync-plugin-framework.sh` (which vendors `framework/` subtrees plus three
  named tools files and does not touch `sdd_doc_lint`).
- **Both `CLAUDE.md` current-state platform tokens now self-heal** (PR #389). `sync-version-refs.sh`
  detects the previous plugin and Hermes values **from `CLAUDE.md` itself**, not from
  `plugin.json` / `README.md`, so a stale token is fixed even when every other surface is
  already current — the state that let `CLAUDE.md` sit at Hermes `0.11.1` against a
  `0.12.0` VERSION for four days. The plugin token had carried the same latent bug since
  SYNC-CLAUDE-PLUGIN-VERSION-GAP (its write was nested inside the `plugin.json`-derived
  guard); it is now independent too. **The framework-spec token still is not**, and it
  carries the higher-fanout version of the same bug: `fw_prev` is detected from
  `CLAUDE.md` *and* gates propagation to `README.md`, `docs/PARITY.md`, both platform
  READMEs and the conformance-test literal — five files stranded, silently, exit 0, if
  `CLAUDE.md` is corrected first. Measured, not inferred, and filed as
  [#386](https://github.com/vladm3105/aidoc-flow-framework/issues/386). **The hand-edit
  hazard below now applies to that token alone.** The 52 SKILL frontmatters, the
  playbooks and `platforms/*/FRAMEWORK_SPEC_VERSION` are **not** in that blast radius —
  each has its own detector.
- **Run a sync-script reproduction in a throwaway clone, never in the working tree.**
  Proving #386 meant bumping `framework/VERSION`, which fired the three independent
  detectors and rewrote **100+** SKILL / playbook / `FRAMEWORK_SPEC_VERSION` files — and
  the script's closing `git add -u` **staged all of them**. Restoring the two files the
  test targeted is not enough; the collateral is elsewhere and already in the index.
- **Propagation order for a framework version bump is load-bearing:**
  `framework/VERSION` → `scripts/sync-version-refs.sh` → **then**
  `tools/sync-plugin-framework.sh`. Reversing it lands 51 drifted bundled playbooks and
  a red bundle guard. And **do not hand-edit `CLAUDE.md` before running the version
  sync** — the sync detects the old literal *from CLAUDE.md*, so a pre-edited file
  makes it skip its own block silently, exit 0, and leave README / PARITY / both
  platform READMEs stale.

### Acceptance harness

- **Manifests live OUTSIDE `fixtures/`** (`tests/acceptance/expected_warnings/`).
  Inside a `NN_LAYER/` dir the linter ingests one as an artifact — measured at
  13 → 31 findings and `rc` 0 → 1, i.e. it *manufactures* errors. Latent for the live
  tier, since `live/_live_harness.py:stage_upstreams_into` copies `valid/` contents
  into exactly such a dir and live is `skipUnless(LIVE=1)`.
- **The pinned warning set measures trace-graph visibility, not fixture debt.** Six
  goldens have an unterminated frontmatter fence (one `---`, no `doc_id`) and are
  invisible to `build_edge_graph`. Repairing one is benign and **moves the manifest** —
  adding the fence to `layer_06_spec/valid` takes it 0 → 6.
- **`ELEM_FORM` cannot search a message** — it is fully anchored, so extraction is two
  steps: take the single-quoted token, then validate. And the linter's `file` key is
  CWD-relative or absolute, so a manifest loader **must** normalize to target-relative
  or every entry mismatches.
- **A *leading* `---` is only a document-start marker.** All six `fullpath` YAML
  goldens have one; only the three under `golden_chain/` carry a *closing* fence and are
  genuinely two documents. Walk them with `safe_load_all`, not `safe_load`.

### Writing to GitHub from a script (new 2026-07-30 — PIN-CURRENCY-READER PR 2)

These cost real defects in merged code, each found only by looking at the artifact.

- **`gh run view --log` renders ANSI as the two literal characters `^` `[`, never a raw
  ESC byte.** Measured on run `30257877863`: **0** occurrences of `0x1b`, **68** of
  `^[`. A filter written as `grep -v $'\x1b'` therefore matches nothing — it looks like
  a guard and is dead code. Filter on `'\^\['` instead. The same fact means a fixture
  built from a real download is byte-faithful even though it *looks* re-rendered; do not
  "fix" it.
- **In a single-quoted `printf` format, `\`` is a literal backslash, not an escape.**
  It publishes as `` \` `` to anyone reading the issue. In an **unquoted** heredoc
  (`<<EOF`) the opposite holds — a bare backtick is command substitution, so the
  backslash there is required. The two rules are inverted, and one script can contain
  both. Shipped in #392, caught on issue #393's real close comment, fixed in #394.
- **Command substitution strips trailing newlines**, so a helper that ends with
  `printf '\n'` cannot supply the blank line that terminates a GFM table when consumed
  as `$(helper)` inside a heredoc. The following paragraph is absorbed into the table as
  junk rows. The blank line has to be literal *in the heredoc*.
- **`gh --jq` uses gh's own built-in jq**, so a `|| die` on the `gh` call proves nothing
  about a *separate* external `jq` invocation on its output. Guard each extraction, and
  treat an unparseable id as fatal — an empty id is indistinguishable from "no such
  issue" and will route a read failure into a **create**.
- **`gh issue create --assignee` and `--label` both hard-error on an unknown value.**
  Apply the label by *retry* (labelled, then unlabelled + `::warning::`) — never
  `|| true`, which makes the whole creation non-fatal. Set the assignee *after*
  creation, so its failure cannot take the create with it.
- **The prescribed comment-readback can report a published comment as empty.**
  `gh issue view <N> --json comments --jq '.comments[-1].body|length'` returned **0**
  for a comment that had published in full (3,629 chars via
  `gh api …/issues/comments/<id>`), and the correct value on a later read —
  read-after-write lag. The feedback contract calls a non-zero length "the only proof it
  published", and the symptom is **identical to the `--body -` bug**, so the natural
  reaction is to re-post and duplicate. Anchor the check to the id in the URL `gh`
  returned, or retry before concluding anything. Filed as
  [aidoc-flow-operations#290](https://github.com/vladm3105/aidoc-flow-operations/issues/290).
- **`gh issue list` defaults to `--limit 30`**, and this repo is past #390. A tracking
  issue that has aged off page 1 is invisible to an exact-title lookup, and the run
  creates a duplicate. `--state all --limit 200`, and never `--search` (tokenized and
  eventually consistent, so a just-created issue can be missing).

### The absence-probe trap, restated because it bit again

`CLAUDE.md` records that `gh api …/contents/<missing> --jq '.name'` must not be
truth-tested. Re-measured 2026-07-30, the failure text is **not** the string `null` —
it is the full error JSON (`{"message":"Not Found",…,"status":"404"}`) on stdout. So a
guard written as `case "$n" in ''|null)` — which looks like it handles the documented
form — reads a missing file as **present**. It gave a blast-radius figure of **10 of 10**
workspace repos calling `standards-drift`; the truth, from listing the directory and
grepping, is **7 of 10**. **Do not pattern-match the failure string at all. List the
directory:** `gh api repos/<r>/contents/.github/workflows --jq '.[].name'`.

### Process

- **Verify a blocker before escalating it** (**D-0068**). `IDGEN-NO-GENERATOR`'s merged
  plan declared a founder decision was required over `state: canonical` vs
  `id_state: provisional`. There was no conflict — `id_standard.state` is template
  metadata with no code consumer, and the linter says so at
  `tools/sdd_doc_lint/__init__.py:558`. An unverified blocker in a merged plan stalls
  work on a decision nobody needs to make.
- **Write the scan before the census.** A surface count went 9 → 19 → the truth of
  **25**, because both manual passes sampled one file instead of the tree. A hand-built
  census of a class is a sample that gets reported as a total.
- **A root cause is a claim about a distribution — derive the distribution first**
  (**D-0072 §3**). A sampled read of `doc-maintainer`'s failures named ci#352 "the
  blocker" and that framing reached three files; the full census put #352 at 3 of 23 and
  #353 at 15. Both are true in their own sense, but conflating them produced a **resume
  condition that would have returned a majority-red pilot**. Loop every failing run and
  bucket the errors before naming a cause.
- **When an error names a condition, check the named artifact actually violates it**
  (**D-0072 §2**). Canon's `duplicate or non-allowlisted plan path: <path>` covers two
  conditions in one string, and its most frequent instance named a path that **is**
  allowlisted. An allowlist-shaped message about an allowlisted path read as a config
  mismatch, and that misdiagnosis was written into the backlog as this repo's bug. One
  `jq '.allowed_paths'` falsified it.
- **Mutation-test a negative-property guard.** `test_no_inprompt_hashing.py` passed a
  live reintroduction on first write: markdownlint reflows those surfaces into single
  long lines, so the correction and the regression shared a line and a line-scoped
  negation skip masked it.
- **Measure blast radius before shipping an operation over shared state.**
  `rehash --fix` was cut on measurement, not principle — it would rewrite all four of
  BRD-01's §7 FR IDs and break citations in 8 downstream files.
- **Before fixing a defect in a hand-rolled surface, check whether canon owns that
  surface** (**D-0071 §2**). #373 asked to SHA-pin an action; adopting canon's caller
  closed it and removed the class of defect, where editing the `uses:` lines would have
  fixed the symptom and left the workflow to drift at the next release.
