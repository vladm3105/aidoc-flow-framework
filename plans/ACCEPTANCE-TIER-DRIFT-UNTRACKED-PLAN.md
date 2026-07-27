# ACCEPTANCE-TIER-DRIFT-UNTRACKED Plan — pin the warnings, then gate the tier

| Field          | Value                                                        |
| -------------- | ------------------------------------------------------------ |
| Task           | ACCEPTANCE-TIER-DRIFT-UNTRACKED                              |
| Type           | test-harness + ci                                            |
| Status         | PLANNED — 2026-07-27                                         |
| Depends on     | Nothing. Closes a long-standing failure on `main`            |
| Closes         | [#365](https://github.com/vladm3105/aidoc-flow-framework/issues/365) |
| Version impact | **None.** No `framework/` change, no platform change, no `VERSION` bump — `tests/` + `.github/workflows/` only |
| Gate           | Not GATE-SPEC (nothing under `framework/` is touched)        |

## Objective

Three tests in the deterministic acceptance tier fail on `main`, and no CI job
runs the tier, so nothing reports it. This plan makes the suite's assertion match
what it actually means to assert, pins today's known warnings so they cannot hide
new ones, and puts the tier behind a required check so the next drift is caught
by CI rather than by whoever next runs it by hand.

## The issue's premise is wrong, and I wrote it

**#365 says the fix is to "realign the acceptance fixtures with the coverage
rules that shipped after they were written."** That framing is mine, from filing
the issue during IDCOORD-SECOND-HASH-IMPL, and it is wrong. Verified, not
assumed:

| Claim in #365 | Reality |
| --- | --- |
| the fixtures fail the lint rules | **`rc=0` for all 8 layer dirs AND the fullpath chain.** The linter passes every one of them |
| "genuine findings against stale fixtures" | Genuine, but **all 13 are `severity: warning`** — zero errors anywhere |
| fix = realign the fixtures | One option, and the weakest: it clears today's 13 and leaves the mechanism that produced them intact |

What actually fails is the **second** assertion in
`assert_golden_passes_lint` (`tests/acceptance/_harness.py:155-164`):

```python
self.assertEqual(rc, 0, ...)          # passes — always has
self.assertEqual([], findings, ...)   # fails — this is the entire failure
```

It demands zero findings of **any** severity. `REFGRAN01` is documented as
warnings-only in `build` (`FRAMEWORK-TODO.md` → `CORPUS-REFGRAN-RECASCADE`);
`ACC01` and `COV02` are warnings too. **The suite asserts a standard stricter
than the framework's own gate**, so every newly-shipped advisory rule reddens it
on contact.

That is the observed history, not a hypothetical. Fixtures authored `e2058c1d`
(2026-05-31); `ACC01` shipped `4423a1cc` (2026-07-24). `REFGRAN01` did the same
earlier. **Two rules, two rounds of breakage, one mechanism.**

**Consequence for scope.** The work is not fixture authoring. It is a harness
contract fix plus a CI gate — both small, both structural.

## Why only layers 7/8 and fullpath — and why the obvious answer is wrong

Two hypotheses were tested and **both are false**:

1. *Partial-corpus artifact.* No — the complete 8-layer chain still emits
   findings (13). The partial corpora emit 6 and 11, so the counts differ; what
   is false is the idea that completeness would clear them.
2. *"Coverage rules can only fire in a corpus containing the downstream layers."*
   No. `REFGRAN01` runs **unconditionally**
   (`tools/sdd_doc_lint/__init__.py:2627-2629`). And the clean disproof for
   `COV02` is `layer_07_tdd/valid/`, which contains **no graph-visible TDD** —
   its `TDD-01_golden.yaml` has no `doc_id` — yet still emits 4 `COV02`, armed by
   the `doc_id`-bearing `SPEC-01_golden.yaml` beside it. Presence of a downstream
   layer *on disk* is irrelevant; graph **visibility** is the gate
   (`__init__.py:2232-2235`).

**The actual mechanism is frontmatter visibility.** `build_edge_graph` admits
only documents whose frontmatter carries a `doc_id`
(`tools/sdd_doc_lint/__init__.py:1651-1657` — `if not doc_id: continue`).
`layer_06_spec/valid/SPEC-01_golden.yaml` opens with `---` but has **no closing
fence**, so `_extract_frontmatter` returns `None`, the doc never enters the trace
graph, and its doc-level `@adr: ADR-01` at line 22 — byte-identical to the one
pinned as `REFGRAN01` in `layer_07_tdd/valid/SPEC-01_golden.yaml:24` — is never
evaluated.

**Verified empirically.** Copying `layer_06_spec/valid/` to a temp dir and adding
the `doc_id` + closing fence takes it from **0 findings to 6**.

So layers 1-6 are silent **by accident, not by construction**. This is not a
pedantic correction: it is the reason **D6** exists, because it means the pinned
counts measure what the trace graph can see, not the fixtures' advisory debt.

## Scope

**In:**

- **A — the harness contract.** `assert_golden_passes_lint` asserts `rc == 0`,
  **zero errors**, and that the emitted warnings **exactly match** the target's
  manifest as a **multiset** (D3). Not a subset: a new warning fails, and a
  manifest entry whose warning no longer fires **also** fails, so the manifest
  cannot rot into a permanent excuse list.
- **B — the manifests.** Three files under `tests/acceptance/expected_warnings/`
  (D1 — outside the fixture tree), one per affected lint target
  (`layer_07_tdd/valid`, `layer_08_iplan/valid`, `fullpath/golden_chain`), each
  entry carrying `code` + `file` + `ref` + `count` + `reason` (D3). Targets with
  no expected warnings need no manifest and keep today's strict behaviour.
- **C — the CI gate.** A workflow running the **deterministic** tier on every
  push/PR, mirroring `conformance.yml`, plus the branch-protection change adding
  it to `required_status_checks` — the half that actually prevents recurrence.

**Out of scope:**

- **Authoring the fixtures warning-clean** (the "A" of #365's comment). It is
  legitimate follow-up quality work that shrinks the manifest entry by entry, but
  it is a *fixture-content* project, not a defect fix, and doing it here would
  leave the recurrence mechanism unaddressed. See **D6**.
- **The `live/` tier.** `tests/acceptance/live/` needs a plugin runtime and is
  not deterministic; gating it is a different problem. The gate runs
  `deterministic` only.
- **Changing any lint rule or severity.** `ACC01`/`COV02`/`REFGRAN01` are firing
  correctly on real gaps; nothing under `framework/` moves.
- **`CORPUS-REFGRAN-RECASCADE`.** Adjacent and still open; it covers
  `examples/url-shortener/docs/`, not these fixtures.

## Approach / Design

### D1 — Manifests live OUTSIDE the fixture tree

The obvious design puts a manifest in each fixture directory, as the existing
`*_drift_codes.yaml` sidecars do. **Do not.** A manifest inside the fixture tree
is exposed to two independent hazards, both verified:

**Hazard 1 — the linter ingests it.** `detect_layer`
(`tools/sdd_doc_lint/__init__.py:243-255`) ingests a file if **either** branch
matches: a path component matching `\d{2}_([A-Z]+)`, **or** a filename starting
`<ARTIFACT>-`. Measured on a temp corpus:

| Manifest placement | Findings |
| --- | --- |
| *(baseline for that temp corpus)* | 12 |
| at the lint-target root | **12** — inert ✅ |
| `06_SPEC/SPEC-01_expected_warnings.yaml` | **23** — ingested as an artifact ❌ |

*(That 12 is the temp corpus's own baseline, not the chain's 13 — the experiment
isolated a single SPEC file. The chain is 13 everywhere else in this plan.)*

**Hazard 2 — the live tier copies it into exactly the bad placement.**
`tests/acceptance/live/_live_harness.py:92-104` `stage_upstreams_into` copies
**every item** of a `valid/` dir, unfiltered, into
`<workspace>/docs/<NN>_<TYPE>/`. So `layer_07_tdd/valid/_expected_warnings.yaml`
would land at `docs/07_TDD/_expected_warnings.yaml` — the path branch fires, the
manifest is linted as a TDD artifact, and `_live_harness.py:136-137`'s `rc == 0`
breaks. This is latent: the live tier is `skipUnless(LIVE=1)`, so step 2's
"confirm the other 60 stay green" would **not** surface it. The plan declares the
live tier out of scope, but a manifest in the fixture tree silently changes its
inputs.

**Therefore manifests live in a sibling directory, keyed by lint target:**

```
tests/acceptance/expected_warnings/
  layer_07_tdd__valid.yaml
  layer_08_iplan__valid.yaml
  fullpath__golden_chain.yaml
```

This removes both hazards structurally rather than by convention, and removes a
constraint every future contributor would otherwise have to remember. The
fixture tree stays exactly as it is — which also keeps "no golden churn"
trivially true.

Schema (one entry per distinct finding key; see **D3**):

```yaml
target: layer_07_tdd/valid          # relative to tests/acceptance/fixtures/
expected_warnings:
  - code: REFGRAN01
    file: SPEC-01_golden.yaml     # the linter's own JSON key, relative to target
    ref: "@adr: ADR-01"           # discriminator — see D3
    count: 2                      # multiplicity; two such tags in this file
    reason: >
      Doc-level `@adr: ADR-01` predates GD-03 element granularity. Clearing it
      is fixture-authoring work tracked separately; pinned so it cannot mask a
      new REFGRAN01 elsewhere.
```

### D2 — Bidirectional matching, because a subset check is how manifests rot

The obvious implementation is "every emitted warning must appear in the
manifest." That is a subset check, and it degrades predictably: warnings get
added to the manifest to make CI green, nothing ever removes them, and after two
years the manifest documents nothing.

Matching is therefore **bidirectional**:

- an emitted warning absent from the manifest → **fail** (new drift);
- a manifest entry with no matching emitted warning → **fail** (stale entry —
  the fixture was fixed, or the rule changed, and the manifest must shrink).

The second direction is what makes the follow-up authoring work self-verifying:
clean a fixture, and the suite *tells you* to delete the manifest entry.

### D3 — Match a MULTISET of `(code, file, ref)` + `count`, not message text

The first draft matched on `(code, file, count)`. **That cannot detect
substitution, which is the drift the manifest exists to catch.** `ACC01` and
`COV02` both report against the *host* document
(`__init__.py:2358-2367`, `:2267-2277` — `rel_by_doc.get(host, host)`), so all
four chain `ACC01`s collapse to one entry `(ACC01, BDD-01_golden.md, 4)`. Pair
two scenarios and orphan two different ones, and the count is still 4: the
manifest passes while real drift occurred. `count` closes only the *shrinkage*
hole, not the substitution hole.

**A first revision proposed `(code, path, element_id)` as an exact set. That is
also wrong, in two ways that only measurement exposed:**

- **REFGRAN01 messages carry no element ID at all.** The message
  (`__init__.py:2566-2569`) quotes the offending *tag* and a literal placeholder
  `ADR.NN.SS.xxxx` — `NN`/`SS` are not digits, so no ID regex can match.
  Measured over the chain: **8 of 13 findings expose an ID, 5 do not** — every
  REFGRAN01. A `null` fallback would put a third of the pinned set back into
  exactly the substitution hole this key exists to close.
- **Distinct findings can share a key.** `06_SPEC/SPEC-01_golden.yaml` emits
  **two** REFGRAN01 with the identical cited token (lines 24 and 77) — and does
  so in **all three** lint targets. (`08_IPLAN/IPLAN-01_golden.yaml` also emits
  two, but with *distinct* tokens — `@adr: ADR-01` and `@tdd: TDD-01` — so those
  are two entries of `count: 1`.) An exact-**set** comparison dedups
  them, so deleting one of the two tags would still pass — reopening the
  shrinkage hole **D2** exists to close.

**The match is therefore a MULTISET of `(code, file, ref)` with an explicit
`count`:**

- **`ref` is a per-code discriminator**, not element-ID-only:
  - `ACC01` / `COV02` → the element ID, in **two steps**: take the
    single-quoted token from the message (both render `'<ID>'` — `:2272`,
    `:2363`), then **validate** it with the canonical `ELEM_FORM`
    (`tools/sdd_doc_lint/trace_graph.py:37`), raising if it does not validate.
    The two-step form is required, not stylistic: `ELEM_FORM` is fully anchored
    (`^…$`, no `MULTILINE`), so `ELEM_FORM.search(message)` returns **`None`** —
    verified. It validates a token; it cannot find one. This still imports the
    contract rather than restating it, per ELEMENT-ID-LAYER-CONTRACT-001.
  - `REFGRAN01` → the cited tag, recovered with `@(\w+):\s*([A-Z]+-\d+)`. It is
    as stable as an element ID: rule authors retune wording, not tag values.
  - Any future code exposing neither → the manifest loader **raises**, rather
    than silently degrading to a countable blob. A rule that cannot be pinned
    precisely must be handled deliberately.
- **`count`** is the multiplicity of that key, and is therefore **required** —
  the earlier claim that "set cardinality carries it" was wrong.
- **`file`** is stored **target-relative** (`SPEC-01_golden.yaml`,
  `06_SPEC/SPEC-01_golden.yaml`) — collision-proof across `golden_chain/NN_LAYER/`
  and invocation-independent. **The loader must normalize, and this is not
  optional:** the linter's `file` key (`__main__.py:96`) is **CWD-relative**, or
  **absolute** when the target lies outside CWD
  (`__init__.py:2605-2608`). Measured from the repo root it emits
  `tests/acceptance/fixtures/layer_07_tdd/valid/BDD-01_golden.md` — which never
  equals a target-relative manifest entry. A loader that skips normalization
  mismatches **every** entry and reports all 30 findings as simultaneous drift and
  staleness. Normalize with
  `(Path.cwd() / emitted).resolve().relative_to(target.resolve())`.
- **`line` and message prose are excluded.** Lines shift whenever a fixture gains
  a line; prose churns on cosmetic rule edits. Either would make the manifest
  fail for reasons unrelated to drift, training people to regenerate it blindly.

**Manifest identity, stated once.** The filename is the lint target's path
relative to `tests/acceptance/fixtures/` with `/` → `__`
(`layer_07_tdd/valid` → `layer_07_tdd__valid.yaml`;
`fullpath/golden_chain` → `fullpath__golden_chain.yaml`). The `target:` key
restates that same fixtures-relative path for readability — **not** a
repo-relative one — and the loader **asserts the two agree**, so a renamed file
cannot silently point at another directory. Two entries with the
same `(code, file, ref)` inside one manifest are an **error**, not an implicit
`count: 2` — multiplicity is always explicit.

### D4 — Gate ordering, and the PATCH that would silently un-protect `main`

**Corrected rationale.** A required check *can* be added for a context that has
never reported — the REST API accepts arbitrary strings; the UI merely *suggests*
seen ones. The consequence is worse than rejection: every PR sits at "Expected —
waiting for status to be reported", indefinitely. So the ordering still holds,
but because of hang, not rejection:

1. land A + B + C in **one** PR (the `pull_request` trigger reports the new
   context on that PR itself, so no second landing is needed);
2. after merge, confirm the context reported on `main`;
3. **then** add it to `required_status_checks`;
4. **rebase any PR opened before the workflow file existed** — its branch cannot
   produce the context and will block until rebased.

**The PATCH is full-replace, not append.** `PATCH
/repos/{owner}/{repo}/branches/main/protection/required_status_checks` overwrites
`strict` + `contexts`/`checks` wholesale. A payload carrying only the new context
**silently drops the other five required checks**, leaving `main` less protected
than before while appearing to succeed. The payload must re-assert the full end
state, `strict: false` preserved explicitly, using the
`checks: [{context, app_id}]` shape (`app_id: 15368`, the GitHub Actions app)
that the existing entries use, since bare `contexts` is deprecated. **The block
below is the shape observed 2026-07-27 — illustrative only. Step 6 GETs the live
set and appends to it**; hardcoding these five would itself commit the Risk-2
error against any context added since:

```jsonc
{"strict": false, "checks": [
  {"context": "Framework + platform conformance",        "app_id": 15368},
  {"context": "call / composition",                      "app_id": 15368},
  {"context": "call / Lint / format / security hooks",   "app_id": 15368},
  {"context": "call / ai-review",                        "app_id": 15368},
  {"context": "call / verify",                           "app_id": 15368},
  {"context": "Acceptance tier (deterministic)",         "app_id": 15368}
]}
```

The read-back therefore asserts **set equality against `observed ∪ {new}`**, not
mere inclusion of the new one — an inclusion check passes even after a naive
PATCH has wiped the others.

Confirm `main` is under **classic branch protection** first: under rulesets,
`/branches/main/protection` 404s and this step is a silent no-op.

### D5 — The workflow mirrors `conformance.yml`; the job name IS the contract

Same shape as the existing gate: `ubuntu-latest`, `actions/checkout@v7`,
`setup-python@v7` at 3.12, install `tests/conformance/requirements.txt` (the
tier's only non-stdlib import is `yaml`; no acceptance-specific requirements file
exists), then `python -m unittest discover -s tests/acceptance/deterministic`.
Public-repo runner discipline from `conformance.yml`'s header comment carries over
verbatim: GitHub-hosted, never self-hosted.

**The required-check string is the JOB's `name:`, not the workflow's.**
`conformance.yml` is `name: Conformance` at the workflow level but registers the
context `Framework + platform conformance` — its `jobs.conformance.name`
(`:19`). A wrong string never matches and the gate silently never fires. This
plan therefore pins it:

```yaml
jobs:
  acceptance:
    name: Acceptance tier (deterministic)   # ← THE required-check context string
```

Step 6 quotes that literal. (The `call / X` contexts come from a different
pattern — a local job named `call` invoking a reusable `workflow_call` target —
which this workflow does not use.)

**Concurrency.** Copy `conformance.yml`'s
`group: ${{ github.workflow }}-${{ github.ref }}` with `cancel-in-progress: true`.
This is safe *because of the trigger shape*, and the reasoning must be recorded so
nobody re-derives it: the `push` event's `github.ref` is `refs/heads/<branch>`
while `pull_request`'s is `refs/pull/<N>/merge`, so the two events on one commit
land in **different** groups and never cancel each other. That is precisely the
precondition `ai-review.yml` violates — two trigger events collapsing to one group
on the same SHA — which stranded a CANCELLED check-run and blocked PR #366 despite
every required context passing. **Do not add a second trigger event to
`acceptance.yml` without re-deriving this.**

### D6 — What this plan does not fix, and the invariant that makes it fragile

After this lands, the fixtures still carry 13 real advisory findings. They are
*pinned and visible* rather than *red and ignored* — the difference between a
known state and an unknown one — but they are not gone. Clearing them is real
fixture-authoring work (element-level `@adr:` citations, TDD test cases paired to
4 BDD scenarios, element-level citations for uncovered EARS/BDD elements) and
lands as a follow-up TODO entry, self-verified by D2's stale-entry direction.

**The invariant a future author must know:** per the "Why only layers 7/8"
section, the pinned set measures **what the trace graph can see**, not the
fixtures' advisory debt. Several goldens carry an *unterminated* frontmatter fence
and are invisible to the graph — notably
**three** goldens — `layer_06_spec/valid/SPEC-01_golden.yaml`,
`layer_07_tdd/valid/TDD-01_golden.yaml`, and
`layer_08_iplan/valid/IPLAN-01_golden.yaml` (each: one `---`, no `doc_id`,
verified). Contrast `layer_08_iplan/valid/TDD-01_golden.yaml:2`, which *has*
`doc_id` and therefore **arms** `ACC01` — note the resulting findings are
reported against the BDD **host** doc (`__init__.py:2360`
`rel_by_doc.get(host, host)`), i.e. `BDD-01_golden.md`, not the TDD file, so a
hand-authored manifest entry must use the host path. Adding a closing fence to
any of the three is a **benign fixture repair that changes the expected set and
hard-fails what will by then be a required check** (repairing
`layer_06_spec/valid` alone is 0 → 6; `IPLAN-01` adds 2 REFGRAN01).

So D6's honest statement is narrower than "pinned and visible": absence of a
warning is not evidence of fixture health. The deferred TODO entry names those
goldens explicitly so the next author expects the manifest to move.

Each entry carries a `reason` naming what would clear it, so a reader cannot
mistake "pinned" for "acceptable."

### D7 — The operational cost, stated before it is discovered

Once the tier is required, **any PR shipping a new advisory lint rule must update
all three manifests in the same PR, or it blocks every merge.** That is the
intended behaviour — it is the recurrence fix working — but it is a real tax on
future GATE-SPEC authors and belongs here rather than being discovered by the
next one. It also belongs in `CONTRIBUTING.md`'s doc-of-record matrix; that edit
is in scope.

## File structure

### Modified

| File | Change |
| --- | --- |
| `tests/acceptance/_harness.py` | A — `assert_golden_passes_lint` rewritten; new `_expected_warnings()` loader |
| `tests/acceptance/deterministic/test_fullpath.py` | A — `test_chain_lint_passes` uses the same contract. **Note:** `FullpathChainTests` does not inherit `LayerHarness`, so the comparison must be factored into a module-level helper in `_harness.py` rather than living in the mix-in method |
| `CONTRIBUTING.md` | D7 — manifests join the doc-of-record matrix for advisory-rule PRs |
| `tests/acceptance/README.md` | `:5` claims "Runs: **deterministic in every PR**" — **false today**, and plausibly why the drift sat unnoticed. C makes it true; the manifest mechanism is documented here |
| `plans/FRAMEWORK-TODO.md` | entry → Closed; new entry for deferred D6 authoring work; **correct the stale `3 of 58` to `3 of 63`**; **mark `AIDOC-CI-COMPOSITION-CHECK-PRHEAD` resolved** (see below) |
| `CHANGELOG.md` | `[Unreleased]` entry |
| `plans/HANDOFF.md` | session state |

### Added

| File | Purpose |
| --- | --- |
| `tests/acceptance/expected_warnings/layer_07_tdd__valid.yaml` | 6 pinned warnings |
| `tests/acceptance/expected_warnings/layer_08_iplan__valid.yaml` | 11 pinned warnings |
| `tests/acceptance/expected_warnings/fullpath__golden_chain.yaml` | 13 pinned warnings |
| `.github/workflows/acceptance.yml` | C — the gate |

**Nothing is added under `tests/acceptance/fixtures/`** — see D1.

### Not modified

No golden. No `framework/`. No `VERSION`. No lint rule.

## Implementation sequence

**One PR** for steps 1-5 (D4 corrected: the `pull_request` trigger reports the
new context on the PR itself, so no second landing is needed). Step 6 is
post-merge and is a repo-settings change, not a diff.

1. **A — harness contract**, with the manifest loader. Assert `rc == 0`
   **first**, before any manifest comparison: a registry-unavailable exit 2
   produces empty stdout, which would otherwise surface as the nonsense
   "manifest has stale entries" (`__main__.py:118`).
2. **B — the three manifests**, generated from actual linter output rather than
   hand-typed. Three tests → green; confirm the other 60 stay green.
3. **Mutation-verify D2/D3 in all four directions** before believing any of it:
   add a bogus entry → must fail; delete a real entry → must fail; **substitute**
   an element ID (ACC01/COV02) **and** a cited tag (REFGRAN01), each keeping the
   count identical → must fail; **delete one of two duplicate-key findings**
   (`SPEC-01_golden.yaml`'s two `@adr: ADR-01`) → must fail; rename a rule's
   message prose → must **pass** (D3's anti-churn property). A mechanism that
   survives all five is worth having; one that does not is a rubber stamp.
   **Every mutation is reverted before the no-churn verification rows run** —
   several edit goldens, which those rows assert are untouched.
4. **C — the workflow**, with the job `name:` exactly as pinned in D5. Verify it
   runs green on the PR itself.
5. **Docs of record** — `CHANGELOG.md`, `CONTRIBUTING.md`, `FRAMEWORK-TODO.md`,
   `HANDOFF.md`.
6. **After merge:** confirm the context reported on `main`; verify `main` is
   under classic protection (not rulesets); **GET the live
   `required_status_checks`, append the new context to what is actually there,
   then PATCH that** — never the literal five from D4, which were observed
   2026-07-27 and would drop any context added since (Risk 2 applied to this
   plan's own payload); read back and assert **set equality** against
   `observed ∪ {new}`; rebase any PR that predates the workflow file.
7. **Comment on #365** correcting the premise before it closes, so the record
   does not preserve the wrong diagnosis (the issue text is mine and says the fix
   is fixture realignment).

## Discovered during review — a stale TODO that misled a reviewer

`plans/FRAMEWORK-TODO.md` `AIDOC-CI-COMPOSITION-CHECK-PRHEAD` states that
`call / composition` is "structurally unsatisfiable on a PR head" and that
"every PR (incl. doc-only) is closed via `--admin` override." A Pass-1 reviewer
correctly read that as invalidating this plan's entire premise: if all merges
bypass required checks, a new required check gates nothing.

**The entry is stale.** Verified on the four most recent PRs — `call / composition`
reports **success on the PR head** every time:

```
#366 head=2f684894  [success,success]
#363 head=484173e3  [success]
#361 head=6c6ef62c  [success]
#356 head=84b937bd  [success]
```

The `ci/v2.x` canon migration evidently fixed it. (PR #366 did need `--admin`, but
for an unrelated, correctly-diagnosed reason: `ai-review.yml`'s concurrency group
stranded a CANCELLED check-run — see D5.) The premise holds; the entry is
corrected in the same PR so the next reader is not misled the same way.

## Verification

| Check | Command | Expected |
| --- | --- | --- |
| Target tests | `python3 -m unittest discover -s tests/acceptance/deterministic` | **63 tests, 0 failures** (from 3 failures / 63) |
| New-warning detection | add a bogus `ACC01` entry to a manifest | **fails** |
| Stale-entry detection | delete a real manifest entry | **fails** |
| **Substitution detection (ID)** | swap one pinned `ref` (an ACC01/COV02 element ID) for another, count unchanged | **fails** |
| **Substitution detection (tag)** | swap a pinned REFGRAN01 `@tdd: TDD-01` for `@bdd: BDD-01`, count unchanged | **fails** — REFGRAN01 exposes no element ID, so this is the case an ID-only key missed |
| **Duplicate-key shrinkage** | delete one of `SPEC-01_golden.yaml`'s two identical `@adr: ADR-01` tags | **fails** — the case an exact *set* silently dedups |
| Message-churn immunity | reword a rule's message prose **preserving** the quoted ID / cited tag | **passes** (a reword that removes them makes the loader **raise** — intended loud failure, not silent drift) |
| Manifests do not touch the corpus | `git diff --stat tests/acceptance/fixtures/` | **empty** — D1 puts manifests outside the fixture tree |
| Live tier unaffected | `LIVE=1` staging copies no manifest into `docs/NN_TYPE/` | no manifest present (structural, per D1) |
| Conformance | `python3 -m pytest tests/conformance/` | 253 passed |
| Hermes | `python3 -m pytest platforms/hermes/tests/` | 570 passed |
| No golden churn | `git diff --stat tests/acceptance/fixtures/**/*_golden.*` | **empty** |
| No spec change | `git diff --stat framework/` | empty |
| Protection style | `gh api .../branches/main/protection` | 200, not 404 (classic, not rulesets) |
| Gate active | `gh api .../required_status_checks --jq '[.checks[].context]\|sort'` | **equals** `observed ∪ {new}` — not merely contains the new one |

## Risks

| # | Risk | Mitigation |
| --- | --- | --- |
| 1 | Required check added before the context ever reports → every PR hangs on "Expected" | D4 forces the order; step 6 is post-merge and verified by read-back |
| 2 | **The step-6 PATCH silently drops the other required checks**, under-protecting `main` while appearing to succeed | Step 6 GETs the live contexts and PATCHes `observed ∪ {new}`; verification asserts **set equality** against that union, which is the only check that catches this |
| 3 | Manifest becomes a permanent excuse list | D2's stale-entry direction fails the suite when a pinned warning stops firing; each entry carries a `reason` |
| 4 | Manifest matching too strict → fails on cosmetic linter edits | D3 matches `(code, file, ref)` + `count` — never message text, never line numbers; step 3 mutation-tests exactly this |
| 5 | The new workflow is flaky and blocks `main` | Runs the same suite that runs locally, no network, no LLM, ~9s; step 4 proves it green on the PR before gating |
| 6 | **A benign fixture repair (adding a closing frontmatter fence) changes the expected set and hard-fails a required check** | Cannot be prevented, only anticipated: D6 names the affected goldens and the deferred TODO warns the next author |
| 7 | A future advisory rule blocks every merge until manifests are updated | Intended (D7), but stated up-front and added to `CONTRIBUTING.md` so it is not discovered mid-PR |
| 8 | Someone adds a second trigger event to `acceptance.yml`, reintroducing the `ai-review.yml` concurrency failure | D5 records the derivation inline in the workflow's own comment, not only in this plan |
| 9 | A future dir gains warnings and someone pins instead of fixing | Not mechanically preventable; the `reason` field makes the choice explicit and reviewable in the diff |

## Claim ledger

Citations are to `tools/sdd_doc_lint/` (canonical). Note the harness actually
**executes the vendored copy** — `run_lint` sets
`PYTHONPATH=plugin_bundle_root()` (`_harness.py:94`) → `platforms/claude-code-plugin`.
The two are held byte-identical by
`tests/conformance/platforms/test_doc_lint_vendoring.py`, so the citations are
valid for the executed code; the indirection is recorded rather than assumed.

| #   | Claim | Symbol | Citation |
| --- | --- | --- | --- |
| 1 | The failing assertion demands zero findings of any severity | `self.assertEqual(` … `[],` … `findings,` | tests/acceptance/_harness.py:160-162 |
| 2 | The rc assertion already passes — the linter exits 0 | `self.assertEqual(` … `rc,` … `0,` | tests/acceptance/_harness.py:155-157 |
| 3 | `rc` is 0 unless some finding is an **error** | `return 1 if any(f.severity == "error" for f in findings) else 0` | tools/sdd_doc_lint/**main**.py:118 |
| 4 | The default mode is `build`, and `run_lint` never overrides it | `default="build"` | tools/sdd_doc_lint/**main**.py:44 |
| 5 | COV02 is a warning outside `gate-code` | `severity = "error" if mode == "gate-code" else "warning"` | tools/sdd_doc_lint/**init**.py:2248 |
| 6 | ACC01 is a warning outside `gate-code` | *(same construct)* | tools/sdd_doc_lint/**init**.py:2349 |
| 7 | REFGRAN01 is a warning outside `gate-code` | *(same construct)* | tools/sdd_doc_lint/**init**.py:2553 |
| 8 | Docs without a frontmatter `doc_id` never enter the trace graph — the real reason layers 1-6 are silent | `if not doc_id:` `continue` | tools/sdd_doc_lint/**init**.py:1651-1657 |
| 9 | Adding the `doc_id` fence to `layer_06_spec/valid/` takes it 0 → 6 findings | *(empirical, temp-dir copy)* | verified 2026-07-27 |
| 10 | REFGRAN01 runs unconditionally — not gated on downstream layers | comment: *"it runs unconditionally"* | tools/sdd_doc_lint/**init**.py:2627-2629 |
| 11 | ACC01/COV02 report against the **host** doc, so counts alone cannot detect substitution | `rel_by_doc.get(host, host)` | tools/sdd_doc_lint/**init**.py:2358-2367, :2267-2277 |
| 12 | Messages carry the element ID in a stable machine-readable form | `BDD scenario '<ID>' (host <DOC>)` | tools/sdd_doc_lint/**init**.py:2363 |
| 13 | Files matching no layer convention are skipped entirely | `if artifact is None:` `return` | tools/sdd_doc_lint/**init**.py:2603-2604 |
| 14 | `detect_layer` ingests on **either** a `NN_LAYER` path component **or** an `<ARTIFACT>-` filename | `re.fullmatch(r"\d{2}_([A-Z]+)", part)` / `re.match(rf"({_KNOWN})-", path.name.upper())` | tools/sdd_doc_lint/**init**.py:243-255 |
| 15 | A manifest at the target root is inert; misnamed inside `NN_LAYER/` it nearly doubles findings | 12 → 12 vs 12 → 23 | *(empirical, verified 2026-07-27)* |
| 16 | Only `.md`/`.yaml`/`.yml` are considered at all | `p.suffix.lower() in (".md", ".yaml", ".yml")` | tools/sdd_doc_lint/**init**.py:2615 |
| 17 | The broken-fixture path already uses a YAML sidecar — but per-file, codes-only, one-directional | `def assert_broken_fixture_emits_expected_codes` | tests/acceptance/_harness.py:166 |
| 18 | The fullpath test asserts the same zero-findings contract | `self.assertEqual([], findings` | tests/acceptance/deterministic/test_fullpath.py:21 |
| 19 | No CI workflow runs the acceptance tier | `grep -rn acceptance .github/workflows/` → no output | .github/workflows/ |
| 20 | The required-check context is the **job** name, not the workflow name | `name: Framework + platform conformance` | .github/workflows/conformance.yml:19 |
| 21 | Fixtures predate ACC01 by ~2 months | `e2058c1d 2026-05-31` vs `4423a1cc 2026-07-24` | `git log` |
| 22 | Per-directory finding counts (these *are* the manifests) | 6 / 11 / 13 | layer_07_tdd, layer_08_iplan, fullpath/golden_chain |
| 23 | The tier's only non-stdlib import is `yaml`, already in the conformance reqs | `PyYAML>=6.0.3` | tests/conformance/requirements.txt:4 |
| 24 | `AIDOC-CI-COMPOSITION-CHECK-PRHEAD` is stale — composition reports on PR heads | `#366/#363/#361/#356 → success` | *(empirical, verified 2026-07-27)* |
| 25 | REFGRAN01's message exposes **no** element ID — only the cited tag and a literal `NN.SS.xxxx` placeholder | `cite the specific element ('@{layer}: …NN.SS.xxxx')` | tools/sdd_doc_lint/**init**.py:2566-2569 |
| 26 | 8 of the chain's 13 findings expose an element ID; the 5 REFGRAN01 do not | per-finding regex scan | *(empirical, verified 2026-07-27)* |
| 27 | Distinct findings share a key — `SPEC-01_golden.yaml` emits 2 REFGRAN01 with the same cited tag (lines 24, 77), in **all three** targets | 2 × `@adr: ADR-01` | *(empirical; `08_IPLAN/IPLAN-01`'s two are **distinct** tags, `@adr`/`@tdd`)* |
| 28 | The live harness copies **every** item of a `valid/` dir into `docs/NN_TYPE/`, unfiltered | `shutil.copy2(item, dst / item.name)` | tests/acceptance/live/_live_harness.py:92-104 |
| 29 | The canonical element-ID pattern already exists and should be imported, not restated | `ELEM_FORM = re.compile(...)` | tools/sdd_doc_lint/trace_graph.py:37 |
| 30 | The linter's JSON key is `file`, not `path` | `"file": str(f.path)` | tools/sdd_doc_lint/**main**.py:96 |
| 31 | Three goldens carry an unterminated fence (1 `---`, no `doc_id`) | `layer_06_spec/SPEC-01`, `layer_07_tdd/TDD-01`, `layer_08_iplan/IPLAN-01` | *(empirical, verified 2026-07-27)* |
| 32 | `tests/acceptance/README.md` already claims the tier runs in every PR — it does not | `**Runs:** deterministic in every PR` | tests/acceptance/README.md:5 |

## Docs to update

`CHANGELOG.md` · `CONTRIBUTING.md` (D7) · `tests/acceptance/README.md` (its
"runs in every PR" claim becomes true) · `plans/FRAMEWORK-TODO.md` (entry →
Closed; new entry for the deferred D6 authoring work; correct `3 of 58` → `3 of
63`; mark `AIDOC-CI-COMPOSITION-CHECK-PRHEAD` resolved) · `plans/HANDOFF.md`.
**No** `framework/`, **no** `ROADMAP.md` (not a user-visible capability), **no**
`VERSION`.

## Review log

### Pass 1 — 2026-07-27 — two independent reviewers (design + CI), all findings reproduced before folding

**Six load-bearing findings. Two invalidated sections of the draft outright.**

1. **The draft's causal mechanism was wrong.** It claimed layers 1-6 are clean
   because "coverage rules can only fire in a corpus containing the downstream
   layers." False on both counts: `REFGRAN01` runs unconditionally
   (`:2627-2629`), and `COV02` is armed in `layer_06_spec/valid/`. The real
   mechanism is frontmatter `doc_id` visibility (`:1651-1657`) — **verified by
   copying the directory and adding the fence: 0 → 6 findings.** *Folded* — the
   section is rewritten, and this is now the reason **D6** exists.
2. **The pinned counts measure graph visibility, not fixture debt.** Follows from
   1: `layer_07_tdd/valid/TDD-01_golden.yaml` has no `doc_id` and so fires no
   `ACC01`, while `layer_08_iplan/valid/TDD-01_golden.yaml:2` does. A benign
   fixture repair therefore breaks a required check. *Folded* into D6 as a stated
   invariant plus the deferred TODO's warning.
3. **The step-6 PATCH would silently un-protect `main`.** Both reviewers, arrived
   at independently. `required_status_checks` is **full-replace**; a payload with
   only the new context drops the other five. *Folded* — D4 now carries the
   six-entry payload with `app_id`, and the verification asserts **set equality**
   (the old "includes the new context" row would have passed after the very
   mistake it was meant to catch).
4. **The draft never pinned the required-check string.** It is the *job's*
   `name:`, not the workflow's; a wrong string never matches and the gate
   silently never fires. *Folded* — D5 pins `Acceptance tier (deterministic)`
   verbatim and step 6 quotes it.
5. **`(code, file, count)` cannot detect substitution.** ACC01/COV02 report
   against the host doc (`:2358-2367`), so all four chain `ACC01`s collapse to one
   entry; re-pairing two scenarios while orphaning two others keeps the count at
   4 and passes. *Folded* — D3 now matches `(code, path, element_id)` with the ID
   extracted by a narrow regex, and step 3 mutation-tests exactly this case.
6. **A reviewer read `AIDOC-CI-COMPOSITION-CHECK-PRHEAD` as invalidating the
   whole plan** — if every PR merges via `--admin`, a required check gates
   nothing. Checked rather than accepted: composition reports **success on the PR
   head** on the last four PRs. *Folded* — the entry is stale, is corrected in
   this PR, and the finding is recorded as its own section so the next reader is
   not misled the same way.

Also folded, non-load-bearing: manifest naming/placement is a real hazard
(12 → 12 at the target root vs 12 → **23** misnamed inside `NN_LAYER/`, both
verified) and D1 now shows both `detect_layer` branches; three ledger rows had
line drift (1, 2, 20) and the severity chain — the plan's central premise — was
absent from the ledger entirely, now rows 3-7; the harness executes the
**vendored** linter copy, now stated above the ledger; `FRAMEWORK-TODO.md`'s
"3 of 58" is stale (63 is correct); D7 added for the standing manifest tax; D5
records why this workflow's trigger shape is immune to the `cancel-in-progress`
failure that blocked PR #366; D4-vs-sequence contradiction resolved to one PR.

### Pass 2 — 2026-07-27 — re-review of the Pass-1 patches

**Seven load-bearing findings, four of them introduced BY the Pass-1 patches.**
Every one reproduced against source before folding.

1. **D3's "(none today)" was false — and it was the plan's own load-bearing
   claim.** REFGRAN01's message (`:2566-2569`) exposes no element ID at all, only
   the cited tag and a literal `ADR.NN.SS.xxxx` placeholder that no digit-based
   regex matches. Measured: **8 of 13 findings expose an ID, 5 do not.** The
   `element_id: null` fallback would have returned a third of the pinned set to
   the exact substitution hole D3 was written to close. *Folded* — `ref` is now a
   **per-code discriminator** (element ID for ACC01/COV02, cited tag for
   REFGRAN01), and an un-pinnable future code **raises** rather than degrading.
2. **Exact-*set* matching silently dedups duplicate keys.**
   `06_SPEC/SPEC-01_golden.yaml` emits two REFGRAN01 with the *same* cited tag
   (lines 24, 77); `08_IPLAN/IPLAN-01` likewise. Deleting one would still pass —
   reopening D2's shrinkage hole. *Folded* — the comparison is a **multiset** and
   `count` is **restored as required**, reverting Pass 1's "set cardinality
   carries it," which was simply wrong.
3. **The live tier would break, latently.** `stage_upstreams_into`
   (`_live_harness.py:92-104`) copies **every** item of a `valid/` dir into
   `docs/NN_TYPE/` — precisely the placement D1 measured at 12 → 23. Invisible to
   step 2 because the tier is `skipUnless(LIVE=1)`. *Folded, and it simplified
   the design*: manifests moved **out of the fixture tree** to
   `tests/acceptance/expected_warnings/`, which removes this, removes D1's whole
   naming-hazard class, and keeps "no golden churn" trivially true.
4. **A Pass-1 patch contradicted its own mechanism.** The rewritten section
   claimed COV02's gate "is satisfied in `layer_06_spec/valid/`" — but under the
   corrected `doc_id` mechanism it is not, since that directory has no
   graph-visible SPEC. *Folded* — the disproof now uses `layer_07_tdd/valid`,
   which has no graph-visible TDD yet still emits 4 COV02.
5. **D6's list of fence-broken goldens was 2 of 3** — it missed
   `layer_08_iplan/valid/IPLAN-01_golden.yaml`, verified to have one `---` and no
   `doc_id`. A list whose entire purpose is warning the next author must be
   complete. *Folded*, with the ACC01 host-path correction (findings report
   against the BDD host, not the TDD file).
6. **The plan contradicted itself on 12 vs 13.** D1's empirical table used a
   single-file temp corpus whose baseline was 12; every other section says 13.
   *Folded* — the table now states which corpus it measured.
7. **Step 6's hardcoded payload was itself an instance of its own Risk 2.**
   Pinning the five contexts observed on 2026-07-27 would drop any context added
   between plan-merge and execution. *Folded* — step 6 is now GET → append →
   PATCH, asserting `observed ∪ {new}`.

Also folded: the schema was described three incompatible ways across Scope B, D1
and D3 (now one schema, stated once, using the linter's own `file` JSON key);
the element-ID regex is imported from `ELEM_FORM`
(`trace_graph.py:37`) rather than restated, per ELEMENT-ID-LAYER-CONTRACT-001;
hypothesis 1's "the same 13" overstated (partial corpora emit 6 and 11);
`tests/acceptance/README.md:5` already claims the tier "runs in every PR" — false
today, and the most plausible reason nobody noticed, now in scope. Ledger grew to
32 rows.

**Call-site enumeration (verified, no defect):** all 10 `run_lint` /
`assert_golden_passes_lint` sites were enumerated. No two lint the same
directory, so the per-target contract is sound; no directory emits warnings
without a manifest; the 63-test count is correct and `FRAMEWORK-TODO.md`'s "3 of
58" is stale.

### Pass 3 — 2026-07-27 — re-review of the Pass-2 patches

**Six load-bearing findings. Two were implementation-blocking** — a literal
implementation of the Pass-2 plan could not have worked.

1. **`file` normalization was missing, and the justification said the opposite of
   the truth.** D3 called the linter's `file` key "invocation-independent, since
   `run_lint` reports CWD-relative paths" — CWD-relative *is* invocation-dependent,
   and absolute when the target is outside CWD (`__init__.py:2605-2608`).
   Measured: the linter emits
   `tests/acceptance/fixtures/layer_07_tdd/valid/BDD-01_golden.md`, which never
   equals a target-relative manifest entry. **A loader following the plan verbatim
   would mismatch every entry** and report all 30 findings as simultaneous drift
   *and* staleness. *Folded* — D3 now specifies the normalization explicitly.
2. **`ELEM_FORM` cannot extract an ID.** D3 said to extract element IDs with the
   canonical pattern, "imported, not restated." But `ELEM_FORM`
   (`trace_graph.py:37`) is fully anchored (`^…$`, no `MULTILINE`), so
   `ELEM_FORM.search(message)` returns **`None`** — verified. Under D3's own
   "raise rather than degrade" rule the loader would have raised on 8 of 13
   findings. *Folded* — two steps: take the single-quoted token, then **validate**
   it with `ELEM_FORM`. Still imports the contract; now actually works.
3. **A ledger row was false.** Row 27 claimed `08_IPLAN/IPLAN-01_golden.yaml`
   emits duplicate-key REFGRAN01 "likewise." It emits two, but with **distinct**
   tags (`@adr: ADR-01`, `@tdd: TDD-01`) — verified — so they are two entries of
   `count: 1`. The real duplicate is `SPEC-01_golden.yaml` only, and it recurs in
   **all three** targets, which is the stronger claim. *Folded* in both row 27 and
   D3.
4. **D4 still mandated the hardcoded payload that step 6 calls a defect.** Pass 2
   patched step 6 but left three other surfaces (D4 prose, the read-back
   assertion, Risk 2's mitigation) directing the implementer to the literal five
   contexts. *Folded* — the JSON block is now labelled illustrative, and all four
   surfaces say `observed ∪ {new}`.
5. **D3's own heading still named the superseded key** (`(code, path,
   element_id)`) — the line a reader skims and quotes — as did Risk 4. *Folded.*
6. **The Added table was broken by a Pass-2 insertion**, leaving the workflow row
   rendering as literal text outside the table. *Folded.*

Also folded: `target:` and the `/`→`__` filename rule were used but never defined,
and duplicate in-manifest keys were unspecified — all three now stated once in D3;
"message-churn immunity" overstated (a reword that *drops* the quoted token makes
the loader raise — that is intended, and now said); a verification row still named
`element_id`; step 3's mutations edit goldens that later rows assert are
untouched, so the revert is now explicit.

**Independently re-derived, all confirmed:** per-target totals 6 / 11 / 13; the
chain split 5 REFGRAN01 + 4 ACC01 + 4 COV02; 8 of 13 findings expose an element
ID; `layer_06_spec/valid` repair is 0 → 6; all three fence-broken goldens; ledger
rows 25-32. **Collision check on `(code, file, ref)` across all 30 findings: no
unaccounted collisions** — every group is a singleton or the one documented
`count: 2`.

### Pass 4 — 2026-07-27 — convergence check

**Zero load-bearing findings. Converged.**

The reviewer walked the plan as an implementer and confirmed it is buildable from
this document alone: manifest location and filename rule, schema, match key and
multiplicity, duplicate-key handling, assertion order, the unknown-code raise,
workflow shape/job name/concurrency, and step 6's GET→append→PATCH are all
present and mutually consistent. No surviving contradiction of the Pass-3
semantics; every branch-protection surface now says `observed ∪ {new}`.

Independently re-derived rather than trusted: per-target totals **6 / 11 / 13**,
the chain split **5 REFGRAN01 + 4 ACC01 + 4 COV02** (with `@spec: SPEC-01`
correctly exempt per `_REFGRAN_ELEMENT_DECLARING`), all three fence-broken
goldens, and ledger rows 1-8, 10-14, 16-20, 23, 25, 27-32.

Two adversarial checks came back clean and are worth recording: the new
`tests/acceptance/expected_warnings/*.yaml` files are inert to `detect_layer`
(no `\d{2}_[A-Z]+` component, and `LAYER_07_TDD__VALID` does not match the
artifact-prefix branch), and no CI job lints them. The **no-manifest** case is
also provably equivalent to today's assertion: the linter emits only `error` and
`warning` severities, so "rc == 0 + warnings match an empty multiset" reproduces
`assertEqual([], findings)` exactly for the six manifest-less directories.

Both minor notes were folded regardless, since each would have failed on first
run: D1's `target:` example was repo-relative while the identity rule is
fixtures-relative, and `FullpathChainTests` does not inherit `LayerHarness`, so
the comparison must be a module-level helper.

**Four cycles: 6 + 7 + 6 + 0 load-bearing findings.** Two of Pass 3's would have
made the implementation fail outright.
