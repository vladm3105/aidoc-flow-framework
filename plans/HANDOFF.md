# Session Handoff

**Purpose:** everything a *fresh* session needs to start work here with zero prior
context — current state, what to do next, and the traps that cost an earlier session
real time. Nothing else.

**This file is regenerated, not appended.** It had grown to 3377 lines of stacked
session banners, which is the failure mode the workspace rule forbids: status that is
appended rots, and a wrong cause left standing gets re-read as fact by every later
session. Two banners here were asserting resolved blockers as live, and one asserted a
cause that was measurably false. **Git is the archive** — the full prior history is at
`387d05a6:plans/HANDOFF.md` and in `git log -- plans/HANDOFF.md`. Do not restore it
here.

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

Framework spec `0.40.0`, Claude Code plugin `0.24.0`, Hermes `0.12.0`. `main` clean.
**Open issues: 2** — [#385](https://github.com/vladm3105/aidoc-flow-framework/issues/385)
(next-task 4 below) and [#386](https://github.com/vladm3105/aidoc-flow-framework/issues/386)
(the `sync-version-refs.sh` framework-token gate, under *Local hooks and tooling*), both
filed 2026-07-30. **Open PRs: 0** once the PR carrying this file lands.

**Last merge: PR [#383](https://github.com/vladm3105/aidoc-flow-framework/pull/383)
(`845ea13f`) — the PIN-CURRENCY-NO-READER *plan*, and nothing else.** No
implementation shipped. `plans/PIN-CURRENCY-READER-PLAN.md` is `READY` and is PR 1 of a
four-PR sequence it defines itself; **PR 2 (implementation) is the next task.** The
`PIN-CURRENCY-NO-READER` entry in `FRAMEWORK-TODO.md` is still **open** by design — the
plan's PR 3 closes it, gated on post-merge verification.

**The canon CI migration is complete on both dimensions.** Pins:
CI-CANON-V2.16-001 (PRs #374/#375, **D-0070**) took all call sites to `@ci/v2.16.0`.
Adoption: CANON-PARITY-001 (PR #378, **D-0071**) adopted the four surfaces this repo
had never called and converted `codeql` from hand-rolled into a canon caller — which
is what closed [#373](https://github.com/vladm3105/aidoc-flow-framework/issues/373).
Sixteen call sites across fifteen files. `sast-scan` carries the one deliberate
runner-label divergence ([aidoc-flow-ci#349](https://github.com/vladm3105/aidoc-flow-ci/issues/349)).

**The insight worth keeping:** re-pinning and adopting are different dimensions, and
only the first was automated. `check-pin-currency.sh` and `check-drift.sh` both iterate
over callers **that exist**, so they reported "all pins current ✅" while four surfaces
were absent. The census that finds the gap is canon's
`install/templates/manifest.json` walked against the working tree — **run it when the
canon minor moves, not just the re-pin.** Adopt with
`install/deploy-ci-wizard.sh scaffold <repo> <dir> [wf…]`: byte-exact callers at the
pin, into a scratch dir, never committed.

## Next tasks — prioritized

The full queue is `plans/FRAMEWORK-TODO.md` (`## Open`) and
`plans/HERMES-BACKLOG.md`. This is only the ordering a fresh session should use.

1. **`doc-maintainer` — founder-blocked, not declined.** The one canon surface still
   unadopted. `LITELLM_DOC_API_KEY`, `AIDOC_FLOW_BOT_ID`, `AIDOC_FLOW_BOT_KEY` exist on
   `aidoc-flow-operations` but **not here**, and a personal account has no org secrets
   to inherit (the API returns 422). Dry-run needs only the LiteLLM doc key:
   `export LITELLM_BASE_URL LITELLM_DOC_API_KEY; bash install/set-litellm-secrets.sh
   --repos "vladm3105/aidoc-flow-framework" --doc`. Live mode additionally needs App
   permissions raised to PR/Issues write, `aidoc-flow-bot[bot]` in
   `.github/ai-review/config.json#trust.ai_review`, and a hand-authored
   `.github/doc-maintainer-conventions.md`.
2. **`PIN-CURRENCY-NO-READER` — implement PR 2 of 4.** The plan is merged, `READY`, and
   carries its own §PR sequencing, §Verification (V1–V16, split pre/post-merge) and a
   40-row Claim ledger. **Read the plan, not this summary** — but three things about it
   are load-bearing enough to repeat, because they will look like over-engineering
   otherwise:
   - **PR 2 ships on unit + dry-run evidence only.** `workflow_run` and
     `workflow_dispatch` both require the file on the **default branch**, so V10–V15
     cannot run until after PR 2 merges. This is why the parse and reconcile logic is
     extracted into `scripts/` instead of living inline in the workflow YAML.
   - **PR 3 is gated on V10–V14** so the TODO entry cannot close on unverified work.
     V15 (the `schedule` → `workflow_run` chain) waits up to seven days for a Monday run
     and is a post-hoc observation, never a gate — PR 3 lands a `pending — V15
     unconfirmed` line in this file for whoever observes it to clear.
   - **All four PRs are governance PRs and none is auto-mergeable** — the auto-merge
     exception list is defined by reference to the governance-PR list, which includes
     plan files and `DECISIONS.md`. PR 1 was merged by the founder for this reason.

   Five upstream defects go to `aidoc-flow-ci` as one issue (plan Task 3). Worth filing
   early: if canon adds a `$GITHUB_STEP_SUMMARY` write plus a reusable `output`, the
   local workflow becomes **deletable** rather than permanent.
3. **`FRAMEWORK-TODO.md` hygiene — bigger than "pick a convention".** Re-counted
   2026-07-30; **both** figures previously in this file were wrong, and the queue is
   unreliable in *two* directions:
   - **7** entries marked `✅ CLOSED` sit under `## Open` (lines 27, 218, 230, 322, 337,
     353, 482), so the queue **overstates** what is open. The 7th,
     `CODEQL-FLOATING-ACTION-PIN`, was closed by PR #378 — which this very file
     documents, so the count went stale inside the range it was wrapping.
   - The `## Closed` section holds **32** entries of which only **10** carry a marker.
     Several of the 22 unmarked ones read as live backlog — `[gate] Component-decomposition
     gate missing between PRD and ADR`, `[harness] Cascade harness lacks
     --skip-lint-smoke flag`, `[template] IPLAN sub-types: code-build vs deploy`. So
     `## Closed` also **hides** open work, which is the worse direction.

   Scope the sweep to both: pick one convention, state it at the top of the file, and
   **triage the 22 unmarked `## Closed` entries** — each is either genuinely closed (add
   the marker) or was filed there by mistake (move it back to `## Open`). Count scoped
   between the two headings; a whole-file `grep -c` conflates them.

   Reproduce the counts:

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
5. **Hermes parity — the residual arc.** `plans/HERMES-BACKLOG.md`: remaining
   plugin-vs-Hermes deltas plus quality-loop Phase 2 (cross-invocation resume / G-R1,
   the parallel-review global lock).
6. **Everything else** is in `FRAMEWORK-TODO.md` by tag (`[ci]`, `[lint]`,
   `[template]`, `[harness]`, `[example-corpus]`, `[docs]`, `[skill]`, `[sync]`),
   including the D54 and Engramory consumer-feedback batches. Nothing there is
   blocking.

**Standing:** the example corpus is regenerated wholesale after framework changes, so
corpus-remediation findings are deferred to that regen rather than fixed in place.
IPLAN ↔ iplanic integration is deferred (`plans/IPLAN-IPLANIC-DEFERRED.md`).

## Stale advice — a fresh session will find these referenced, and they are FIXED

Older plans, TODO entries and commit messages still describe these as live. They are
not. Each was verified on 2026-07-29.

| Stale claim | Reality |
|---|---|
| "`--admin` is required on every PR" (the `ai-review` self-cancel, `aidoc-flow-ci#322`) | **Fixed at `ci/v2.16.0`.** #378 and #380 reached `CLEAN` and merged with no `--admin` |
| "Branch protection requires the phantom `Lint / format / security hooks`, so every PR is BLOCKED" | **Fixed.** Required contexts now read `call / Lint / format / security hooks`, `call / composition`, `call / ai-review`, `call / verify`, `Framework + platform conformance`, `Acceptance tier (deterministic)` |
| `AIDOC-CI-COMPOSITION-CHECK-PRHEAD` — "`call / composition` is structurally unsatisfiable on a PR head" | **Stale.** composition reports success on PR heads; 4/4 recent runs green. A reviewer once read this entry as proof that required checks gate nothing here, and it nearly killed a correct plan |
| "commits need `SKIP=gitleaks`" | **Fixed** (#355) — the local gitleaks hook was dropped; CI's is unaffected |
| "the acceptance deterministic tier has 3 pre-existing failures on `main`" | **Fixed** (#365, #371/#372). 0 failures / 64, and the tier is now a **required** context |
| `NO-PIN-CURRENCY-CHECK` — "this repo runs `check-pin-currency.sh` nowhere" | **Retracted, it was false.** See below |
| `PIN-CURRENCY-NO-READER` — "the fix is a workflow that **runs the script** and opens an issue" (the restated TODO entry's own fix shape) | **Superseded by the merged plan.** Running the script would be the second detector the same entry forbids. The reader consumes the completed run's **log** — the only one of four input surfaces that carries the signal |
| "canon has no adopter-facing pin reader at all" | **Overstated.** `standards-drift-self.yml:85` runs a `--fleet` pin audit against *this repo* every Monday and discards it with `\|\| true`. The gap is that **no** audit has a reader, on either side |
| `plans/PLAN-*.md` as the governance-PR plan glob (`CHANGELOG.md:1892`, `CI-CANON-V2.16-MIGRATION-PLAN.md:468`/`:784`) | **Fixed in `CLAUDE.md`.** The glob is a **suffix** — `plans/*-PLAN.md`. The prefix form matched only `PLAN-TEMPLATE.md`, so the governance list read as covering *no* real plan, and the auto-merge exception list inherits that list by reference. Merged plans and the CHANGELOG keep the old string as history; `CLAUDE.md` is the live rule |

**The retraction, because the lesson generalises.** That entry named an absence as the
cause of a mixed-pin state surviving two days. The check *does* run — canon's
`check-standards-drift.sh` tail (`:499-515` **at v2.16.0**; the same block is `:359-375` at v2.14.0, which is what that run executed) invokes it on every weekly
`standards-drift` run — and it fired on 2026-07-27 naming all ten stale pins **and**
the `--repin` remedy. The proposed fix would have added a **second copy of a check that
was already running and already right**. The real gap is that a warning-only
annotation on a weekly scheduled job has no reader. One
`gh run view --log | grep pin-currency` falsified it. **An absence is the easiest
defect to assert and the hardest to verify — read the log before writing one down.**

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
