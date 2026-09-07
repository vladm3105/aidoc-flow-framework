# CI-CANON-V2.16-001 Plan — bring every CI caller to `ci/v2.16.0`, and adopt the body changes a re-pin cannot deliver

| Field          | Value                                                                             |
| -------------- | --------------------------------------------------------------------------------- |
| Task           | CI-CANON-V2.16-001                                                                 |
| Type           | chore                                                                              |
| Status         | Completed — 2026-07-29 (PR 0 #374, PR 1 #375, PR 2 this; verification #8 run on scratch PR #376) |
| Depends on     | nothing blocking; canon `ci/v2.16.0` is cut (2026-07-27)                            |
| Feeds          | a single-tag fleet position for this repo's workflow callers; unblocks the next canon bump being mechanical |
| Version impact | none — no `VERSION` stream moves (CI infrastructure only)                           |
| Supersedes     | nothing. Continues `plans/CI-CANON-V2-MIGRATION-PLAN.md` (CI-CANON-V2-001, `ci/v1.9.5` → `ci/v2.14.0`) |

## Objective

This repo's eleven `aidoc-flow-ci` call sites sit at **two different tags**:
six workflow files at `@ci/v2.15.0`, four files (five sites) still at
`@ci/v2.14.0`. Canon is at **`ci/v2.16.0`**.

The split is not a decision — it is residue. PR #369 bumped `ai-review` by hand,
and the Dependabot group PR #370 carried exactly five reusables (`audit-trail-check`,
`composition`, `labeler`, `pre-commit`, `standards-drift`). *Why* the other four
were excluded is not established — the config groups all `github-actions`
minor/patch updates with no pattern exclusion and no ignore rule, so it does not
explain a partial group. Do not build on the cause; only on the state.
Dependabot rewrites `uses:` lines and nothing else, so it can
never deliver a caller-**body** change, and it never notices that a header comment
now names the wrong tag. Both failure modes are live in this repo right now.

This plan re-pins every site to `ci/v2.16.0`, adopts the **two** caller-body
changes that apply here, removes the same defect class from the **two
locally-owned** workflows that also feed required contexts, and corrects the prose
the bump falsifies — including the claim in `CLAUDE.md`.

### Why not just let Dependabot do it

Three reasons, each independently sufficient:

1. **Two of the changes live in caller bodies.** Canon's own release notes say a
   re-pin does not deliver them. Dependabot bumps the pin and leaves both defects
   in place. See §"Body changes" below.
2. **The bump makes existing comments false.** `docs-sync.yml` carries a 20-line
   comment asserting the upstream `pull-requests: read` cap is *still* unraised.
   It was raised — CI-0015, at `ci/v2.15.0`. After this bump the comment is not
   merely stale, it actively misdirects the next session away from graduating
   docs-sync out of dry-run.
3. **`CLAUDE.md` already lies.** It states all eleven sites are pinned
   `@ci/v2.14.0`. Six moved two days later and nothing updated the claim. Leaving
   the fleet position to piecemeal Dependabot PRs is what produced that drift.

## Scope

**In:**

- **PR 0 — this plan.** Per `CLAUDE.md` §Development-workflow item 2, the plan PR
  merges before implementation starts.
- **PR 1 — the migration.** All eleven `uses:` pins → `@ci/v2.16.0`; the two
  caller-body changes (§Body changes B1, B2); the #329 allowlist on the two
  locally-owned required-context workflows (B3, B4); the falsified comments
  (§Execution step 4); `plans/DECISIONS.md` (**D-0070**), `plans/HANDOFF.md`,
  `CHANGELOG.md`, and this plan's own `Status` field.
- **PR 2 — the propagation.** `CLAUDE.md` §"Unified CI" per-repo-state paragraph,
  **plus this plan's final `Status` → `Completed`**. Split out to respect the
  ≤3-doc-surface governance rule (see §Governance for the per-PR Status table).
  **As executed it also carried `plans/DECISIONS.md` and `plans/HANDOFF.md`** —
  verification #8 falsified D-0070's "still unexercised" wording *and* the
  HANDOFF banner's live status, and the per-PR doc-of-record rule requires the
  PR that falsifies a doc of record to correct it in the same change. Four
  surfaces; founder OK granted 2026-07-29, audit-trail line in the commit
  message. The ≤3 split this bullet originally described did not survive contact
  with a plan whose own completion falsifies three other documents — worth
  knowing before planning the next one.

**Out (named, not silently dropped):**

- `install.sh --update` body adoption of the other canon surfaces. Deliberate —
  see R1.
- Graduating `docs-sync` out of dry-run mode. The upstream blocker is now gone,
  which makes it *possible*, not *due*; it has its own ≥5-clean-merges condition
  and belongs in its own change.
- SHA-pinning `.github/workflows/codeql.yml`'s floating `github/codeql-action@v4`.
  Real, unrelated to canon, locally-owned. → backlog.
- Adopting `markdown-lint` (not installed here) or any other canon surface this
  repo has not opted into.
- Adding a `concurrency:` block to callers that have none. They cannot exhibit
  #329, and no block at all is strictly safer than canon's allowlist. Not
  because canon's block is dangerous — it is the allowlist, not `cancel:
  true` — but because the change is unmotivated by any defect.
- The `#329` allowlist on the five locally-owned workflows that carry
  `cancel-in-progress: true` but feed **no** required context (`codeql`,
  `chg-gate`, `doc-review`, `hermes`, `plugin`). Canon's rule is scoped to
  required contexts; a cancelled non-required check blocks nothing. Named
  explicitly so the next session does not read their absence as an oversight.

## Current state

Measured 2026-07-29. `R` = feeds a required status check on `main` (the six in M1).

### Canon callers (ten files, eleven sites)

| Caller file | Sites | Pin | `concurrency:` | R | Body change needed |
| --- | --- | --- | --- | --- | --- |
| `ai-review.yml` | 1 | v2.15.0 | none | ✅ `call / ai-review` | no |
| `composition.yml` | 1 | v2.15.0 | none | ✅ `call / composition` | no |
| `pre-commit.yml` | 1 | v2.15.0 | `cancel-in-progress: true` | ✅ `call / Lint / format / security hooks` | **B1** (#329) |
| `audit-trail.yml` | 1 | v2.15.0 | none | ✅ `call / verify` | **B2** (label triggers) |
| `standards-drift.yml` | 1 | v2.15.0 | none | ✗ | no |
| `labeler.yml` | 1 | v2.15.0 | `cancel-in-progress: true` | ✗ | no |
| `links.yml` | 2 | v2.14.0 | `cancel-in-progress: true` | ✗ | no |
| `secret-scan.yml` | 1 | v2.14.0 | none | ✗ | no |
| `docs-sync.yml` | 1 | v2.14.0 | none | ✗ | no |
| `auto-merge-ai-prs.yml` | 1 | v2.14.0 | none | ✗ | no |

### Locally-owned workflows that also feed required contexts

These call no canon reusable, so no pin moves — but the #329 defect class is
defined by *context*, not by ownership: canon states the rule's trigger is
**required-context ∧ non-code-changing-event**, and §23.3 requires sweeping every
workflow sharing the shape.

| File | `concurrency:` | R | Body change needed |
| --- | --- | --- | --- |
| `conformance.yml` | `cancel-in-progress: true`, `on: pull_request` untyped | ✅ `Framework + platform conformance` | **B3** (#329) |
| `acceptance.yml` | `cancel-in-progress: true`, `on: pull_request` untyped | ✅ `Acceptance tier (deterministic)` | **B4** (#329 + a false comment) |
| `codeql.yml`, `chg-gate.yml`, `doc-review.yml`, `hermes.yml`, `plugin.yml` | **all five** `cancel-in-progress: true` | ✗ | no — exempt because non-required, **not** because they lack the shape |

`labeler` and `links` do carry `cancel-in-progress: true`, but neither feeds a
required context — canon left them untouched for exactly that reason, and so does
this plan. `secret-scan`, `audit-trail`, `docs-sync` and `auto-merge-ai-prs` have
no `concurrency:` block at all, so there is nothing to cancel; that is a local
divergence from the canon template, it is strictly safer than canon, and it stays.

**Seven local workflows carry the shape and are exempt only because they are not
required.** That exemption is a snapshot, not a property. `acceptance` was exempt
by the same reasoning until 2026-07-27, when it became the sixth required context
and its `cancel-in-progress: true` — defended by a comment arguing it was safe —
became the B4 defect. **Any future change that makes one of these seven a required
context must take the allowlist in the same PR.** Record that in D-0070.

### What the bump delivers on its own (pin-only, reusable-side)

| Change | Effect here |
| --- | --- |
| CI-0015 — `docs-sync` reusable raised to `pull-requests: write` (landed v2.15.0) | **Real.** The dry-run PR comment can finally post. Our caller has granted `write` since it was written; the missing half was upstream. |
| #331 — the `ai-review` FT-43 fail-closed step removed | **No-op here.** That step only fired on an *unarmed* repo; `vars.APP_REVIEWER_1_BOT_ID` is set (M2). |
| §23.4 — both `ai-review` job `if:`s exclude `ai:review-*` labels | **Also a no-op here.** The exclusion is ANDed *inside the unarmed disjunct* of both `if:` expressions; canon's own comment reads "Armed repos still job-skip such events". |
| node24 action majors across the reusables | Requires Actions Runner ≥ 2.327.1. This repo's pool reports **2.335.1**; `ubuntu-latest` is always current. |

**No interface breaks.** Every input each of the ten callers passes still exists
at `ci/v2.16.0`, and all eight secrets `ai-review.yml` maps explicitly are still
declared. The only `required: true` input in any reusable this repo calls is
`standards-drift`'s `tier`, which the caller passes. Every local `with:` block
stays valid verbatim (M4).

## Body changes (what `--repin` cannot deliver)

### B1 — `pre-commit.yml`: the #329 concurrency allowlist

`pre-commit.yml` feeds the required context `call / Lint / format / security
hooks` and carries `cancel-in-progress: true`. It subscribes to `pull_request`
with no `types:` filter, so `reopened` is in its trigger set. A reopen fires at
the *current* head and can cancel that required check; a cancelled required check
is retained alongside any later success from a separate run, leaving the PR
`--admin`-only.

### B2 — `audit-trail.yml`: the `labeled, unlabeled` triggers

Canon's v2.16.0 template subscribes to `types: [opened, synchronize, reopened,
labeled, unlabeled]` and calls the label events **load-bearing, not cosmetic**:
the reusable's documented escape hatch is a two-signal override (the
`skip-audit-trail` label **plus** a commit-body marker), and without a `labeled`
trigger, applying the label fires no event at all. This repo's caller subscribes
to `[opened, synchronize, reopened]` only — canon names `audit-trail` as the
historical outlier, and this repo **already hit the failure**:
`plans/DECISIONS.md:227` records that "the `skip-audit-trail` override could not
be applied to an open PR because the caller does not listen for `labeled`
events." `call / verify` is required, so the inoperative hatch sits on a
merge-blocking gate.

**Necessary, not sufficient — do not overclaim it.** B2 makes the hatch *fire*;
it does not make an already-red `call / verify` go green by labelling. Per the
§23.1 mechanism this plan relies on elsewhere, a label event starts a **separate
run**, and a separate run's check-run is retained *alongside* the earlier one with
the rollup keeping the worst. The override also requires a commit-body marker,
which means a new SHA regardless. So B2's benefit is: the two-signal override
becomes usable on the next push, instead of being unreachable. D-0070 must say
that, not "the label now clears the check."

**B2 rests on an unstated assumption: a job skipped by `if:` reports success to
branch protection.** The reusable re-runs for `skip-audit-trail` **only** —
canon deliberately excludes every other label so routine writes do not burn
runner minutes. After B2, though, *every* label write in this repo (`labeler`'s
path labels, `ai-review`'s own `ai:review-*` writes, the `skip-ai-review`
label-cycle recovery) starts an `audit-trail` run whose `verify` job is skipped,
adding a `skipped` check-run for a **required** context to the live head SHA.
That is benign only under the skipped⇒success rule. It already holds empirically
here — `call / ai-review` is job-skipped on every `ai:review-*` label event today
and PRs still merge — but it is the difference between B2 being harmless noise
and B2 bricking the gate, so it is stated rather than assumed.

> **⚠️ CORRECTED AT IMPLEMENTATION — the two preceding sentences are wrong; see
> `plans/DECISIONS.md` D-0070.** Measured on PR #375: `labeler` and `ai-review`
> write labels with `GITHUB_TOKEN` (actor `github-actions[bot]`), and a
> `GITHUB_TOKEN`-triggered event creates no workflow run. No `audit-trail` run on
> that branch was label-triggered — both came from `pull_request`. So it is **not**
> *every* label write, only a **human** or App-token one; and `call / ai-review`
> job-skipping on its own `ai:review-*` writes **is not evidence** for
> skipped⇒success, because no run is created to skip. That left verification #8
> as the only way to settle it — **run on scratch PR #376; see §Step 6, the
> verification #8 results table.** It had to apply the label **by hand**.

⚠️ **Add no `concurrency:` block when taking B2** — but not for the reason a first
draft of this plan gave. Canon's template block is the #329 **allowlist**, not
`cancel-in-progress: true`, so copying it would introduce only same-ref
supersession on code-changing events — exactly the set B1 keeps. The correct
reason is narrower: this repo's `audit-trail.yml` has no block, no block is
strictly safer than an allowlist, and no defect motivates adding one. Adding the
two trigger types alone is complete here.

### B3 / B4 — `conformance.yml` and `acceptance.yml`: the same allowlist

Both are locally owned, both feed required contexts, both carry
`cancel-in-progress: true` with an untyped `pull_request` trigger. Same vector as
B1, same fix.

`acceptance.yml:13-26` additionally carries a comment arguing the cancellation is
**safe here**, reasoning that `push` and `pull_request` resolve to different
`github.ref` values and so land in different groups. That is true and irrelevant:
the collision is *within* `pull_request`, where a `reopened` lands in the **same**
group at the **same** head SHA as an in-flight `synchronize` run. The comment
predates its own risk — `acceptance` became a required context on 2026-07-27 — and
it is precisely the kind of confident wrong reasoning the next session will trust
instead of re-checking. Correct it in the same change.

## Execution

### Step 1 — re-pin all eleven sites

Apply canon's own `repin_mode` transform. It rewrites the tag **only** on
`uses:` lines matching `vladm3105/aidoc-flow-ci/`, and deliberately leaves
`@main` and comments alone:

```sh
cd /opt/data/aidoc-flow/framework
git switch -c chore/ci-canon-v2.16
for f in .github/workflows/*.yml; do
  grep -qE '^\s*uses:.*vladm3105/aidoc-flow-ci/' "$f" || continue
  sed -i -E "s#(^[[:space:]]*uses:[[:space:]]*vladm3105/aidoc-flow-ci/[^@]+)@ci/v[0-9.]+#\1@ci/v2.16.0#" "$f"
done
git diff --stat        # expect 10 files, 11 lines
```

Equivalent to `CI_TAG=ci/v2.16.0 bash install/install.sh <repo> --repin`, which
clones the consumer into a scratch dir rather than operating on this working tree.
Run in-tree so the change is reviewable on the branch. Deliberately **not**
`--update` — see R1.

### Step 2 — apply B1, B3, B4 (the #329 allowlist)

In `pre-commit.yml`, `conformance.yml` and `acceptance.yml`, replace
`cancel-in-progress: true` with canon's allowlist, matching
`install/templates/workflows/pre-commit.yml` at `ci/v2.16.0` verbatim (comment
included — it carries the reasoning a future reader needs):

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: >-
    ${{ (github.event_name == 'push' || github.event_name == 'workflow_dispatch')
      || ((github.event_name == 'pull_request' || github.event_name == 'pull_request_target')
          && contains(fromJSON('["opened","synchronize"]'), github.event.action)) }}
```

All three files' trigger sets, since the expression must be checked against each:
`conformance.yml` and `acceptance.yml` subscribe to `push` (all branches) plus
untyped `pull_request`; `pre-commit.yml` subscribes to untyped `pull_request` plus
`push: branches: [main]`. Untyped `pull_request` = `opened | synchronize |
reopened` in all three. Against those sets the expression's only behavioral delta
is `reopened` — the defect. `push`,
`opened` and `synchronize` still cancel as today; the `workflow_dispatch` and
`pull_request_target` clauses are inert here and harmless. No cost or queue
regression.

**Trim canon's comment when copying it into these two.** It cites "a label write
(audit-trail's documented `skip-audit-trail` hatch)" as the motivating case;
neither `conformance.yml` nor `acceptance.yml` subscribes to label events, so
keep only the `reopened` case. Shipping the label sentence here would plant the
same species of confidently-wrong inline reasoning that B4 exists to delete.

**In `pre-commit.yml`, also drop the blank line between the `concurrency:` block
and `jobs:`.** Canon's template has none, and verification #3's second clause
turns on byte-exactness at that boundary. It is one line; leaving it in means the
`concurrency:` region never reads as matching canon.

The `==` form is load-bearing: with an unavailable `github` context it yields
false and cancels nothing, whereas a `!=` denylist would cancel everything in
that degraded state. Do not "simplify" it. Rewrite `acceptance.yml`'s
"Two different groups" comment per B4.

### Step 3 — apply B2 (the `audit-trail` label triggers)

`.github/workflows/audit-trail.yml:5` → `types: [opened, synchronize, reopened,
labeled, unlabeled]`, carrying canon's explanatory comment. Add **no**
`concurrency:` block (see B2's warning).

### Step 4 — correct the falsified prose

| File | Line | Now says | Becomes |
| --- | --- | --- | --- |
| `.github/workflows/links.yml` | 1 | `(@ci/v2.14.0)` | `(@ci/v2.16.0)` |
| `.github/workflows/docs-sync.yml` | 1 | `(@ci/v2.14.0)` | `(@ci/v2.16.0)` |
| `.github/workflows/docs-sync.yml` | 28–37 | "STILL NOT RAISED AT ci/v2.14.0" | CI-0015 raised the callee to `pull-requests: write` at `ci/v2.15.0`; the intersection now resolves to `write` and the dry-run comment can post. Keep the *mechanism* paragraph (permissions intersect); drop the "not yet fixed" verdict and the "track upstream before graduating" instruction, which is discharged. |
| `.github/workflows/ai-review.yml` | 29 | "a ready→draft is seen by the fail-closed guard" | Copy canon's revised template wording **verbatim, including its `while unarmed` qualifier**: #331 removed the step that used to intercept a ready→draft, so such a PR now gets a real review *while unarmed*. **This repo is armed**, so a `converted_to_draft` event still job-skips here (the armed disjunct requires `draft == false`). Dropping the qualifier would replace one false comment with another and contradict this plan's own "no-op here" row. |
| `.github/workflows/auto-merge-ai-prs.yml` | 8 | "re-arms `gh pr merge --auto --merge`" | `--squash`. The reusable has always run `--squash`; canon's own template says so. Not cosmetic — this repo's merge convention is squash, and the comment currently tells a reader the enforcer creates merge commits. |

Two judgement calls to make **deliberately**, not by omission:

- **D3 — `.github/ai-review/config.json:2`** pins its `$schema` at
  `ci/v2.14.0`. Neither `--repin` (workflows only) nor `check-pin-currency.sh`
  (scans `.github/workflows` only) touches it, so it will silently stay two minors
  behind the single-tag position this plan's *Feeds* row claims. Nothing in CI
  validates against it → currency, not breakage. **Decision: in scope, bump it in
  PR 1**, and say so in D-0070. This is the one in-scope item that traces to no
  defect, only to the plan's own headline claim; it is kept because leaving it
  makes that claim false, and it costs one line.
- **D4 — `.github/workflows/ai-review.yml:54-63`** is a ten-line annotation headed
  "ci/v2.15.0 — the CI-0025 self-cancel fix" justifying the pin on the line below.
  Its assertions stay true, but after the bump it annotates a pin that no longer
  exists. **Decision: retitle to name v2.15.0 as the tag that shipped the fix**,
  keeping the reasoning and decoupling it from the current pin.

### Step 5 — documents of record

`plans/DECISIONS.md` (**D-0070** — next free ID; D-0069 is the current maximum),
`plans/HANDOFF.md`, `CHANGELOG.md`, and this plan's `Status` field. Per the repo's
per-PR doc-of-record rule; note D-0065 explicitly requires a CHANGELOG entry for
CI-only PRs.

D-0070 must **not** record #329 as closed. Canon does not claim closure —
"Narrowed, not proven closed": GitHub cancels a *pending* run when a newer one
queues in the same group, independently of `cancel-in-progress`.

### Step 6 — verify

| # | Check | Pass condition |
| --- | --- | --- |
| 1 | `grep -rn '@ci/v' .github/workflows/ \| grep uses:` | 11 sites, all `@ci/v2.16.0` |
| 2 | `bash /opt/data/aidoc-flow/aidoc-flow-ci/sync/check-pin-currency.sh --canon ci/v2.16.0` | zero `::warning::` lines. Warning-only by design — read the output; the exit code is always 0 |
| 3 | `check-drift.sh`, **as a before/after diff of its own output**: `bash …/sync/check-drift.sh > /tmp/drift-before.txt 2>&1` on `main` *before* Step 1, the same on the branch after Step 4, then `diff /tmp/drift-before.txt /tmp/drift-after.txt` | **All ten canon callers already warn on `main` today** — **10** `::warning::drift-check:` annotations, exactly one per caller, measured 2026-07-29 by running it. ⚠️ **Count the `::warning::drift-check:` prefix, not the bare string.** A naive `grep -c '::warning::'` returns **12**: the two extra matches are diff *content*, not annotations — `standards-drift.yml`'s canon header comment quotes the literal string `::warning::`, so that file's own drift body reproduces it twice (once on each side of the hunk). Every one of R1's deliberate customizations is a warning, so a file-count pass condition carries almost no signal; **the value is in the diff bodies, so compare the outputs, not the counts.** ⚠️ **The comparison baseline moves under this change.** The script frames each caller against the template *at the tag that caller declares*, so Step 1 re-points four callers (`secret-scan`, `docs-sync`, `links`, `auto-merge-ai-prs`) from a v2.14.0 baseline to a v2.16.0 one. `secret-scan`'s template is one of the eight that gained the +13/−3 #329 allowlist at v2.16.0 (M6), and this plan forbids adding that block locally — so **`secret-scan.yml`'s diff body legitimately grows by ~13 lines and will be the loudest warning in the after-run. That is expected; do not "fix" it.** **Pass = the before/after diff shows only (a) the eleven pin strings, (b) the four body changes B1–B4, (c) the Step-4 comment edits, and (d) baseline-move growth on those four callers — and `pre-commit.yml`'s `concurrency:` block now matches canon.** Pulling canon's body to silence any warning is `--update` by hand, the outcome R1 exists to prevent, and it is what the script's own "bring back to canonical" advice will tempt you into |
| 4 | `pre-commit run --all-files` | green. **This does not validate the GHA expression** — this repo runs no actionlint hook, only `check-yaml` + `yamllint`. It proves the three files are still well-formed YAML and inside `yamllint`'s 120-char line limit (canon's longest copied line is ~93). The only real validator for a malformed expression is #7, where it surfaces as a `startup_failure` on a required context |
| 5 | `gh api repos/vladm3105/aidoc-flow-framework/actions/runners --jq '.runners[].version'` | every runner ≥ 2.327.1 — re-measure at execution time; do not trust this plan's snapshot |
| 6 | `gh variable list -R vladm3105/aidoc-flow-framework` | `APP_REVIEWER_1_BOT_ID` present — this is what "armed" means to the reusable, **not** the presence of the `APP_REVIEWER_1_*` secrets |
| 7 | The PR's own required checks | all six green. This is the real integration test: `ai-review`, `composition`, `pre-commit`, `audit-trail`, `conformance` and `acceptance` all execute their changed form on this very PR |
| 8 | B2 smoke (post-merge, ~~optional~~ **RUN — scratch PR #376, closed unmerged**) | On a scratch PR: (a) apply `skip-audit-trail` → `call / verify` **re-runs**; before B2 it fired on neither add nor remove. (b) apply any *other* label → an `audit-trail` run starts and its `verify` job is **skipped**, and the PR remains mergeable — this is what confirms the skipped⇒success assumption B2 rests on. **Results below.** It was reclassified from optional to required once #375 showed the assumption had never been exercised at all |

**Verification #8 — run 2026-07-29 on scratch PR #376 (closed unmerged).** The
labels were applied **by hand**; a bot label write uses `GITHUB_TOKEN` and
creates no run, so it would have proved nothing.

| Question | Answer | Evidence |
| --- | --- | --- |
| (a) Does the hatch now fire? | **Yes** | Hand-applied `skip-audit-trail` started an `audit-trail` run (18:47:45Z) whose `verify` job **ran** and passed on the two-signal override. Removing the label fired `unlabeled` and re-ran it too. Before B2, neither add nor remove fired anything |
| (b) Does a `skipped` job degrade a **required** context? | **No** | At the clean SHA `dd2d6046`, hand-applying an unrelated label (`ci`) produced `skipped` check-runs on **two** required contexts — `call / verify` and `call / ai-review` — alongside their earlier successes. `mergeStateStatus` stayed **CLEAN**. (`call / trust` also skipped, but it is **not** a required context, so it evidences nothing here) |
| (c) Are check-runs retained alongside, with the rollup keeping the worst? | **Yes** | At SHA `c9fcb5eb`, `call / verify` carried **both** a `failure` (18:47:02Z) and a later `success` (18:47:47Z); the PR read **BLOCKED**. It is why B2 cannot green a red check by labelling |

**Read (b) precisely — it proves less than "skipped ⇒ success."** The skipped
runs landed *alongside earlier successes* for the same contexts. Under (c)'s
worst-wins rule, `CLEAN` is consistent with both "`skipped` counts as success"
and "`skipped` is ignored while the earlier success governs." What is proven is
that **a `skipped` run does not degrade a required context that has already
succeeded at that SHA** — which is exactly and only what B2 needs, because
`audit-trail` always has a prior `pull_request` run at any SHA a label event can
reach. Strictly the narrowed claim wants a prior *success*, not merely a prior
run; the gap is closed by (c) rather than by the trigger set — if that prior run
failed or was cancelled the context is already red, and under worst-wins a later
skip cannot improve it. **The untested case is a required context whose *only*
run at a SHA job-skips**; nothing here speaks to it.

**Provenance for (c), stated so it can be audited.** Three `call / verify`
check-runs exist at `c9fcb5eb`, not two: `failure` 18:47:02Z, `success`
18:47:47Z, and a second `failure` at 18:49:31Z from the `unlabeled` event. The
`BLOCKED` reading was taken in the window **18:48:21Z–18:49:31Z** — after
`call / Lint / format / security hooks` completed at 18:48:21Z (so no required
context was still pending) and before the third run's check-run appeared at
18:49:31Z (the check-run query taken at the same moment returned exactly two
`call / verify` entries; the run itself was *created* two seconds earlier, at
18:49:29Z). In that window every one of the other five required contexts had
completed successfully, `required_approving_review_count` is 0 and `strict` is
false — so nothing but `call / verify`'s retained `failure` can explain
`BLOCKED`, and it is explainable neither by a pending check nor by
latest-run-wins.

**(c) corroborates canon rather than settling anything.**
[ci#330](https://github.com/vladm3105/aidoc-flow-ci/issues/330) was **closed
2026-07-27**, and `ci/v2.16.0` — the tag this plan adopts — already publishes the
answer at `docs/REPO_STANDARDS.md` §23.1 ("Scope, settled (#330)"): an in-place
**re-run replaces** a check-run, while a **separate run adds a second alongside**
and both are retained. #376 reproduced that independently on this repo. Recording
it as corroboration, not as a resolution.

**Conclusion: B2 is safe as shipped.** The escape hatch is reachable, and the
extra runs a human label write now starts are benign.

## Risks

**R1 — `--update --non-interactive` would clobber every local customization.**
`--update` replaces the whole body of all sixteen `safe_to_replace` surfaces;
`--repin` changes only the tag string. Canon's own guide says *default to
`--repin`*. The customizations at stake: `ai-review`'s dual self-hosted
`runner_labels_*` + `litellm_allow_insecure_http: true`; `secret-scan`'s required
`config-path: .gitleaks.toml` (without it the scan reports 27 synthetic findings
and goes red); `docs-sync`'s `pull-requests: write` grant; `auto-merge-ai-prs`'s
`pr_number` fallback expression; `links`'s two-job internal/external split;
`composition`'s Phase-2 trigger set. → **Mitigation:** `--repin` semantics only;
the four body changes are applied by hand, per file, quoted from canon.
Verification #3 restates the drift-check pass condition so the executor is not
nudged into an `--update`-by-hand.

**R2 — the node24 runner floor is a runtime failure, not a code failure.** If a
runner in the pool were below 2.327.1, `ai-review`'s first job dies on the action
runtime, and the symptom names neither the action nor the floor — it sends you to
the trust config or the LiteLLM proxy, none of which are involved. → **Mitigation:**
verification #5, re-measured at execution time. Note the floor already applies at
`ci/v2.15.0`, so six callers are exposed to it today.

**R3 — the pin bump is behaviorally inert on `ai-review` for this repo, so the PR
does not exercise the changes it ships.** Both #331 and §23.4 are gated on the
repo being *unarmed*; this one is armed, so neither fires. Checked for a live
delta that *would* be untested: the only genuinely new node24 surface
(`download-artifact` v4 → v8) sits in the **autofix** job, which is default-off
and credential-less here; `checkout@v7` in the trust job was already live at
`ci/v2.15.0`; `upload-artifact` in the review job is unchanged. So nothing live
goes untested — the delta is inert, not merely unexercised. The substantive risk
in this PR is B1–B4, which the PR *does* exercise (verification #7). →
**Mitigation:** none needed; recorded so a future session does not read a green PR
as having validated #331/§23.4.

**R4 — Dependabot may open a competing PR.** Its schedule is `weekly`/`monday`;
the next run is 2026-08-03. → **Mitigation:** land before then, or close the
Dependabot PR as superseded. A merge-conflict nuisance, not a correctness risk.

**R5 — `check-drift.sh` compares against the template at the tag a caller is
pinned to**, so it cannot tell you a pin is stale — that is
`check-pin-currency.sh`'s job, and it is the check this repo was missing when the
mixed-pin state accumulated unnoticed. → **Mitigation:** verifications #2 and #3
are both run; neither substitutes for the other.

**R6 — B3/B4 widen scope beyond the canon migration.** They touch locally-owned
workflows that no pin move requires. → **Accepted deliberately.** Shipping
the #329 fix for one of three affected required contexts, while leaving the
other two live and one of them defended by a comment arguing it is safe, is
worse than the scope creep. The edit is the same six lines three times.

## Governance

**Three PRs, in sequence.** `CLAUDE.md` §Development-workflow item 2: the plan PR
merges first, and implementation begins only after. So PR 0 (this plan) → PR 1
(migration) → PR 2 (`CLAUDE.md`).

**None of them auto-merge.** PR 1 touches `.github/workflows/ai-review.yml`, named
in `CLAUDE.md` as both a governance-PR surface and an explicit exception to the AI
auto-merge default. PR 2 touches `CLAUDE.md` itself. PR 0 is a plan file, also on
the governance list. Watch the checks, report green, **ask the founder to merge**.

**The ≤3-doc-surface count, stated exactly — PR 1 is at four, and needs founder
OK.** PR 1's propagation targets are `DECISIONS.md`, `HANDOFF.md`, `CHANGELOG.md`
— three — **plus this plan file**, whose `Status` must move `Draft → In Progress →
Completed` in the same change as the state change per the plan-status governance
rule. `plans/PLAN-*.md` is itself a named governance surface, so that is a genuine
fourth, and Rule 1 admits no exception "without explicit founder OK and an
audit-trail note in the commit message."

**Resolution — DECIDED by the founder, 2026-07-29: PR 1 requests the 4th-surface
OK and carries the audit-trail line in its commit message.** PR 1 is
founder-merged regardless (it touches `ai-review.yml`), so the ask costs nothing
extra. The exemption is **granted, not self-granted**; the commit message must
carry the audit-trail line naming the 4th surface and this decision, or the PR is
non-compliant even with the OK.

**The Status value each PR writes** — `Draft → In Progress → Completed` is a
sequence, not one edit, and PR 2 is in scope, so PR 1 cannot legitimately write
`Completed`:

| PR | Status written | Doc surfaces |
| --- | --- | --- |
| PR 0 | stays `Draft` (authored, not started) | this plan + `FRAMEWORK-TODO.md` = 2 |
| PR 1 | `Draft` → **`In Progress`** | `DECISIONS.md` + `HANDOFF.md` + `CHANGELOG.md` + this plan = **4** (founder OK) |
| PR 2 | `In Progress` → **`Completed`** | planned: `CLAUDE.md` + this plan = 2. **As executed: 4** — + `DECISIONS.md` (verification #8 falsified D-0070's wording) + `HANDOFF.md` (its live-status banner asserted `In Progress`, "PR 1 open", and "still unexercised", all falsified by this PR). **Founder OK granted 2026-07-29**, audit-trail line in the commit message |

Without PR 2 carrying the final transition the plan ends life stuck at
`In Progress` — the stale-status defect the governance rule explicitly names. Note
this also means the rejected alternative (defer `Status` to PR 2 entirely) would
have left the plan reading **`Draft`** through PR 1, not `In Progress`: nothing in
that branch ever sets it. That is the real reason to reject it.

**The cross-repo issue's link-back goes in PR 1**, with D-0070 — the issue itself
is filed during PR 0, but `DECISIONS.md` is a PR 1 surface, and adding it to PR 0
would take PR 0 to three surfaces for no benefit.

The collision is structural: the plan-status rule and Rule 1 pull against each
other on any plan whose implementation touches three other docs. Recorded so the
next session does not re-derive it — and so it does not quietly repeat the
first-draft error of declaring the plan file "not counted."

**`plans/FRAMEWORK-TODO.md` is captured in PR 0**, not PR 1 —
GOV-TODO-ISSUE-SPLIT makes the TODO entry the capture moment ("inline as
discovered… no 'later PR'"), and these are discoveries *of the planning work*.
PR 0's surfaces are then this plan + FRAMEWORK-TODO = two. `CLAUDE.md` goes to
PR 2.

**Each new TODO entry must carry a `*Tracker:*` disposition** — GOV-TODO-ISSUE-SPLIT
also requires deciding, per entry, whether it gets a GitHub issue on this repo
(any of: actionable by someone other than its finder / reproducible at `file:line`
with a concrete fix shape / user-visible). This repo's TODO file already records
that judgment inline per entry. The `codeql.yml` item meets the `file:line`-plus-
fix-shape test on its face; the `check-pin-currency.sh` item is arguably
speculative and TODO-only. **Decide both in PR 0** — the rule forbids deferring it.

**The cross-repo item is PR 0's work too, and carries its own obligations.** Per
this repo's cross-repo feedback rule: file it on `aidoc-flow-ci` with
`gh issue create --body-file -` (never `--body -`, which publishes a literal `-`),
including reproduction at `file:line`, blast radius, a suggested fix, and what is
*not* broken; read the body back with
`gh issue view <N> -R vladm3105/aidoc-flow-ci --json body --jq '.body | length'`;
then record the issue number in this repo's `DECISIONS.md` so a future session
finds the upstream thread.

**Adversarial self-review before push** is mandatory on every governance PR
(discipline Rule 2), with dead-ref and internal-consistency focus — this work
quotes paths and line numbers across two repos.

## Backlog spun out of this plan

Captured in PR 0 (see §Governance), not deferred.

- → `plans/FRAMEWORK-TODO.md` + **filed as
  [#373](https://github.com/vladm3105/aidoc-flow-framework/issues/373)** in PR 0
  (it meets the GD-10 bar on tests (a) and (b)): `.github/workflows/codeql.yml`
  pins `github/codeql-action@v4` (floating tag); canon SHA-pins to v4.37.3.
  Locally owned, unrelated to the canon bump.
- → `plans/FRAMEWORK-TODO.md`: no `check-pin-currency.sh` runs anywhere in this
  repo's CI or hooks, which is why the mixed-pin state went unnoticed. Consider a
  periodic warning-only job.
- Not a TODO entry — a condition to re-evaluate: `docs-sync` dry-run → live
  graduation, now that CI-0015 has unblocked it. Needs the ≥5-clean-merges
  condition evaluated and the bot App provisioned. Already tracked in the caller's
  own comment.
- **Cross-repo issue on `aidoc-flow-ci`:** `docs/UPDATE_GUIDE.md:88` states that
  `framework`'s ai-review caller pins `runner_labels_routine: '"ubuntu-latest"'`.
  False since PLAN-013 — the live caller pins the self-hosted array. Blast radius:
  any adopter reading the guide's worked example for this repo.

## Claim ledger

Gate command:

```sh
python3 ~/.claude/skills/verified-planning/check_plan.py \
  --root /opt/data/aidoc-flow plans/CI-CANON-V2.16-MIGRATION-PLAN.md
```

Canon rows are cited as `aidoc-flow-ci/<path>` and resolve against the workspace
root, **not** the canon repo root. That is deliberate: canon and this repo both
contain `.github/workflows/docs-sync.yml`, `.github/workflows/pre-commit.yml` and
`.github/workflows/auto-merge-ai-prs.yml`, and the gate resolves the plan's own
repo first — so a bare `.github/…` citation of a canon file silently verifies the
*local* file instead. The `aidoc-flow-ci/` prefix makes every canon path
unambiguous. Canon's working tree is at `main`, which is `ci/v2.16.0` plus two
docs-only commits.

| #   | Claim | Symbol | Citation |
| --- | --- | --- | --- |
| 1   | `ai-review` caller is pinned at v2.15.0 | `ai-review.yml@ci/v2.15.0` | .github/workflows/ai-review.yml:64 |
| 2   | `composition` caller is pinned at v2.15.0 | `composition.yml@ci/v2.15.0` | .github/workflows/composition.yml:30 |
| 3   | `pre-commit` caller is pinned at v2.15.0 | `pre-commit.yml@ci/v2.15.0` | .github/workflows/pre-commit.yml:27 |
| 4   | `pre-commit` carries the unconditional cancel that #329 fixes | `cancel-in-progress: true` | .github/workflows/pre-commit.yml:23 |
| 5   | `pre-commit` subscribes to `pull_request` with no `types:` filter, so `reopened` is in its trigger set | `pull_request:` | .github/workflows/pre-commit.yml:14 |
| 6   | `audit-trail` caller is pinned at v2.15.0 | `audit-trail-check.yml@ci/v2.15.0` | .github/workflows/audit-trail.yml:8 |
| 7   | `audit-trail` caller lacks the `labeled, unlabeled` triggers (B2) | `types: [opened, synchronize, reopened]` | .github/workflows/audit-trail.yml:5 |
| 8   | This repo already hit B2's failure: the `skip-audit-trail` override could not be applied | `applied to an open PR because the caller does not listen for` | plans/DECISIONS.md:227 |
| 9   | `standards-drift` caller is pinned at v2.15.0 | `standards-drift.yml@ci/v2.15.0` | .github/workflows/standards-drift.yml:59 |
| 10  | `labeler` caller is pinned at v2.15.0 | `labeler.yml@ci/v2.15.0` | .github/workflows/labeler.yml:39 |
| 11  | `links` has two call sites, both at v2.14.0 | `links.yml@ci/v2.14.0` | .github/workflows/links.yml:25 |
| 12  | — second `links` call site | `links.yml@ci/v2.14.0` | .github/workflows/links.yml:33 |
| 13  | `links` header comment names the tag, so a pin bump falsifies it | `reusable links workflow (@ci/v2.14.0)` | .github/workflows/links.yml:1 |
| 13a | `docs-sync` header comment likewise names the tag | `reusable docs-sync workflow (@ci/v2.14.0)` | .github/workflows/docs-sync.yml:1 |
| 14  | `secret-scan` caller is pinned at v2.14.0 | `secret-scan.yml@ci/v2.14.0` | .github/workflows/secret-scan.yml:12 |
| 15  | `docs-sync` caller is pinned at v2.14.0 | `docs-sync.yml@ci/v2.14.0` | .github/workflows/docs-sync.yml:42 |
| 16  | `docs-sync` caller asserts the upstream cap is still unraised — now false | `STILL NOT RAISED AT ci/v2.14.0` | .github/workflows/docs-sync.yml:28 |
| 17  | `docs-sync` caller already grants `pull-requests: write`, so only the callee half was missing | `pull-requests: write` | .github/workflows/docs-sync.yml:38 |
| 18  | `auto-merge-ai-prs` caller is pinned at v2.14.0 | `auto-merge-ai-prs.yml@ci/v2.14.0` | .github/workflows/auto-merge-ai-prs.yml:53 |
| 19  | `auto-merge-ai-prs` comment says the enforcer re-arms `--merge` | `gh pr merge --auto --merge` | .github/workflows/auto-merge-ai-prs.yml:8 |
| 20  | `ai-review` caller's FT-43 comment claims a fail-closed guard that #331 removed | `is seen by the fail-closed guard` | .github/workflows/ai-review.yml:28 |
| 21  | `config.json`'s `$schema` is pinned at `ci/v2.14.0` (D3) | `ci/v2.14.0/schemas/ai-review-config-v2.schema.json` | .github/ai-review/config.json:2 |
| 22  | `conformance.yml` carries the #329 shape (B3) | `cancel-in-progress: true` | .github/workflows/conformance.yml:15 |
| 23  | — and subscribes to `pull_request` untyped | `pull_request:` | .github/workflows/conformance.yml:8 |
| 24  | — and its job name is the required context `Framework + platform conformance` | `name: Framework + platform conformance` | .github/workflows/conformance.yml:19 |
| 25  | `acceptance.yml` carries the #329 shape (B4) | `cancel-in-progress: true` | .github/workflows/acceptance.yml:29 |
| 26  | — and subscribes to `pull_request` untyped | `pull_request:` | .github/workflows/acceptance.yml:8 |
| 27  | — and its job name is the required context `Acceptance tier (deterministic)` | `name: Acceptance tier (deterministic)` | .github/workflows/acceptance.yml:37 |
| 28  | `acceptance.yml`'s comment argues the cancel is safe, reasoning only about cross-event group collision | `Two different groups, so the two events on one commit never cancel each other.` | .github/workflows/acceptance.yml:19 |
| 28a | `acceptance` became the 6th required context on 2026-07-27 — after that comment was written | `Done 2026-07-27 — the gate is required.` | plans/HANDOFF.md:43 |
| 28b | R1's `secret-scan` clobber consequence is the caller's own recorded measurement | `without this input the scan reports 27 synthetic findings` | .github/workflows/secret-scan.yml:16 |
| 28c | Five more locally-owned workflows carry `cancel-in-progress: true` but feed no required context | `cancel-in-progress: true` | .github/workflows/chg-gate.yml:21 |
| 29  | Dependabot's `github-actions` update runs weekly on Monday | `interval: weekly` | .github/dependabot.yml:17 |
| 30  | D-0069 is the highest decision ID in use | `D-0069` | plans/DECISIONS.md:13 |
| 31  | Canon `repin_mode` rewrites only `uses:` lines and leaves comments alone | `leave @main and` | aidoc-flow-ci/install/install.sh:651 |
| 32  | Canon's guide directs consumers to `--repin` by default, not `--update` | `Default to` | aidoc-flow-ci/docs/UPDATE_GUIDE.md:79 |
| 33  | `--update --non-interactive` replaces the whole body of `safe_to_replace` workflow files | `safe_to_replace` | aidoc-flow-ci/docs/UPDATE_GUIDE.md:44 |
| 34  | Canon's `UPDATE_GUIDE` misstates this repo's ai-review runner labels (cross-repo backlog item) | `runner_labels_routine` | aidoc-flow-ci/docs/UPDATE_GUIDE.md:88 |
| 35  | The #329 allowlist expression this plan copies verbatim | `cancel-in-progress: >-` | aidoc-flow-ci/install/templates/workflows/pre-commit.yml:31 |
| 36  | Canon's `audit-trail` template ships the label triggers (B2) | `types: [opened, synchronize, reopened, labeled, unlabeled]` | aidoc-flow-ci/install/templates/workflows/audit-trail-public.yml:18 |
| 37  | Canon calls those triggers load-bearing and names `audit-trail` the outlier | `load-bearing, not cosmetic` | aidoc-flow-ci/install/templates/workflows/audit-trail-public.yml:11 |
| 37a | Canon's `audit-trail` template block is the #329 **allowlist**, not `cancel: true` — so the B2 warning's original reason was wrong | `cancel-in-progress: >-` | aidoc-flow-ci/install/templates/workflows/audit-trail-public.yml:31 |
| 37b | The reusable re-runs on a label event **only** for `skip-audit-trail`; every other label write yields a skipped `verify` job | `github.event.label.name == 'skip-audit-trail'` | aidoc-flow-ci/.github/workflows/audit-trail-check.yml:84 |
| 37c | A separate run adds a check-run alongside the earlier one — so B2 does not make a red `call / verify` clear by labelling | `separate run adds a second check-run alongside` | aidoc-flow-ci/docs/REPO_STANDARDS.md:2030 |
| 37d | Canon's revised `ai-review` comment carries the `while unarmed` qualifier Step 4 must copy | `still gets a real review while unarmed` | aidoc-flow-ci/install/templates/workflows/ai-review.yml:29 |
| 38  | The #329 rule is scoped by context, not by file ownership (justifies B3/B4) | `required-context ∧ non-code-changing-event` | aidoc-flow-ci/docs/REPO_STANDARDS.md:2049 |
| 39  | Canon does not claim #329 is closed | `Narrowed, not proven closed` | aidoc-flow-ci/CHANGELOG.md:171 |
| 40  | CI-0015 raised the `docs-sync` **reusable** to `pull-requests: write` | `pull-requests: write` | aidoc-flow-ci/.github/workflows/docs-sync.yml:77 |
| 41  | Canon states the consumer half already shipped, so a re-pin is the whole remedy | `CONSUMER ACTION: the caller must ALSO grant` | aidoc-flow-ci/.github/workflows/docs-sync.yml:69 |
| 42  | "Armed" is `vars.APP_REVIEWER_1_BOT_ID`, not the `APP_REVIEWER_1_*` secrets | `vars.APP_REVIEWER_1_BOT_ID` | aidoc-flow-ci/.github/workflows/ai-review.yml:146 |
| 43  | §23.4's `ai:review-*` exclusion sits inside the unarmed disjunct, so it is a no-op on an armed repo | `Armed repos still job-skip` | aidoc-flow-ci/.github/workflows/ai-review.yml:355 |
| 44  | The reusable re-arms `--squash`, not `--merge` | `gh pr merge "$PR" --auto --squash` | aidoc-flow-ci/.github/workflows/auto-merge-ai-prs.yml:427 |
| 45  | The required context `call / Lint / format / security hooks` is the `pre-commit` reusable's job | `name: Lint / format / security hooks` | aidoc-flow-ci/.github/workflows/pre-commit.yml:66 |
| 46  | The required context `call / verify` is the `audit-trail-check` reusable's job | `name: verify` | aidoc-flow-ci/.github/workflows/audit-trail-check.yml:69 |
| 47  | Canon's current version is `ci/v2.16.0` | `ci/v2.16.0` | aidoc-flow-ci/VERSION:1 |
| 48  | `check-pin-currency.sh` is warning-only and always exits 0 | `WARNING-ONLY, NEVER BLOCKS` | aidoc-flow-ci/sync/check-pin-currency.sh:10 |
| 49  | `check-drift.sh` compares a caller against the template at the tag it is pinned to, so it cannot detect a stale pin | `AT THE TAG IT IS PINNED TO` | aidoc-flow-ci/sync/check-pin-currency.sh:4 |
| 50  | `check-drift.sh` compares byte-exactly, so known-good local divergence still warns | `diff -q` | aidoc-flow-ci/sync/check-drift.sh:225 |
| 51  | D-0065 requires a CHANGELOG entry on CI-only PRs | `CI-only PRs carry a CHANGELOG entry` | plans/DECISIONS.md:207 |

## Measured facts (no file to cite)

Load-bearing, but derived from the GitHub API or a diff across two tags, so each
carries a command and its output instead of a `file:line`. All run **2026-07-29**;
re-measure M3 and M2 before executing (M3 is a live runtime floor).

| #   | Claim | Command | Output |
| --- | --- | --- | --- |
| M1  | The six required contexts on `main` | `gh api repos/vladm3105/aidoc-flow-framework/branches/main/protection --jq '.required_status_checks.contexts'` | `Framework + platform conformance`, `call / composition`, `call / Lint / format / security hooks`, `call / ai-review`, `call / verify`, `Acceptance tier (deterministic)` |
| M2  | The reviewer App is armed here, so #331 and §23.4 are both no-ops | `gh variable list -R vladm3105/aidoc-flow-framework` | `APP_REVIEWER_1_BOT_ID = 294948438` (set 2026-06-24). The `APP_REVIEWER_1_ID`/`_KEY` **secrets** are also present but are *not* what the reusable tests |
| M3  | The self-hosted pool clears the node24 floor of 2.327.1 | `gh api repos/vladm3105/aidoc-flow-framework/actions/runners --jq '.runners[].version'` | `2.335.1`, `2.335.1` — both online |
| M4  | No reusable this repo calls changed its `inputs:`/`secrets:` in a way that breaks a local `with:`/`secrets:` block, across v2.14.0 → v2.16.0 | in canon, over **all ten**: `git diff ci/v2.14.0 ci/v2.16.0 -- .github/workflows/{ai-review,composition,pre-commit,audit-trail-check,standards-drift,labeler,links,secret-scan,docs-sync,auto-merge-ai-prs}.yml` cross-checked against each caller's passed inputs | every input passed by a caller still exists at v2.16.0; all 8 secrets `ai-review` maps explicitly are still declared; the only `required: true` input across the ten is `standards-drift.tier`, which the caller passes |
| M5  | Seven of the ten canon callers have no `concurrency:` block | `grep -L '^concurrency:' .github/workflows/{ai-review,composition,audit-trail,standards-drift,docs-sync,auto-merge-ai-prs,secret-scan}.yml` | all seven listed |
| M6  | Canon caller-template deltas v2.15.0 → v2.16.0 are pin-only except the #329 files | in canon: `git diff --numstat ci/v2.15.0 ci/v2.16.0 -- install/templates/workflows/ \| awk '{print $1"/"$2}' \| sort \| uniq -c` | 25 files: **8 at +13/−3** (the allowlist — `audit-trail`, `pre-commit`, `secret-scan`, `markdown-lint`, each × public/private, matching canon's "all eight now carry a fail-safe allowlist"), 14 at 1/1, 2 at 2/2, 1 at 3/2 (pins and adjacent comment lines) |
| M7  | The mixed-pin state came from PR #369 + #370 on 2026-07-27 | `gh pr view 370 -R vladm3105/aidoc-flow-framework --json files` | #369 bumped `ai-review`; #370 touched exactly `audit-trail`, `composition`, `labeler`, `pre-commit`, `standards-drift`. The *reason* the other four were excluded is not established — see §Objective |
| M8  | Five more locally-owned workflows carry the #329 shape but feed no required context | `grep -A2 '^concurrency:' .github/workflows/{codeql,chg-gate,doc-review,hermes,plugin}.yml` | all five: `cancel-in-progress: true` |
| M9  | This repo runs no actionlint hook, so nothing local validates the GHA expression | `grep 'id:' .pre-commit-config.yaml` | `check-yaml`, `yamllint`, `markdownlint`, `ruff`, `bandit`, `detect-secrets`, `pip-audit`, + local `conformance` / `sync-version-refs` / `check-docs-updated` / `aidoc-flow-pre-push`. No actionlint |

## Review log

### Pass 1 — 2026-07-29 — independent (`verified-planning-reviewer`, fresh context)

Dispatched after the citation gate went green on the first draft (31/31
resolving). Seven load-bearing findings, all verified against source by the author
before folding; all seven folded.

1. **A second caller-body change was missed.** `audit-trail.yml` lacks canon's
   `labeled, unlabeled` triggers, so the `skip-audit-trail` escape hatch on the
   required context `call / verify` cannot fire — a failure this repo had already
   recorded at `plans/DECISIONS.md:227`. The draft's headline claim ("exactly one
   caller needs a body change") was false. → New §Body changes B2 + Step 3, with
   an explicit warning not to also copy canon's `concurrency:` block.
2. **The #329 audit only covered canon callers.** `conformance.yml` and
   `acceptance.yml` are locally owned, feed two of the six required contexts, and
   carry the identical defect shape; `acceptance.yml:19` even argues it is safe,
   reasoning only about cross-event group collision and missing the
   intra-`pull_request` `reopened` case. Canon scopes the rule by context, not
   ownership. → B3/B4 + R6 (scope-widening accepted, with reasoning).
3. **Verification #3's pass condition was unachievable** — `check-drift.sh` diffs
   byte-exactly, and this repo's `pre-commit.yml` legitimately diverges in two
   `runner_labels` comments plus a blank line, so "should now MATCH canon" would
   push the executor into `--update`-by-hand. → Restated as a bounded known-drift
   set.
4. **Self-contradiction on armed-vs-unarmed.** #331 and §23.4 are gated on the
   *same* predicate; the draft called one a no-op and elevated the other to R3.
   Both are no-ops here. Separately, "armed" is `vars.APP_REVIEWER_1_BOT_ID`, not
   the `APP_REVIEWER_1_*` secrets, so M2 measured the wrong signal. → Both rows
   corrected, R3 re-aimed, M2 re-measured (`gh variable list` → set), verification
   #6 added.
5. **M4 supported a ten-reusable claim with a four-reusable diff.** Conclusion
   survives — extended to all ten and re-verified: no local `with:`/`secrets:`
   block breaks.
6. **The prose-correction list was incomplete** — `auto-merge-ai-prs.yml:8` says
   the enforcer re-arms `--merge` when the reusable has always run `--squash`, and
   `config.json:2` pins a `ci/v2.14.0` `$schema` that no re-pin tool touches. →
   Both added to Step 4, plus D4 for the now-orphaned v2.15.0 annotation.
7. **The ≤3-doc-surface arithmetic omitted this plan file, and the PR sequence
   omitted the plan PR itself.** → §Governance rewritten as an explicit three-PR
   sequence with the plan-file exemption stated rather than assumed.

The reviewer also confirmed, and could not break: `--repin`-only is the right
operation; the #329 mapping across the ten canon callers; the required-context
mapping; the CI-0015 analysis and the Step-4 `docs-sync` rewrite; that
`secret-scan` will not newly fail; D-0070 as the next free ID; and the Dependabot
cadence R4 assumes.

**Result:** findings folded; re-review required.

### Pass 2 — 2026-07-29 — independent (`verified-planning-reviewer`, fresh context)

Dispatched to re-validate Pass 1's folds and hunt what both passes missed. Six
load-bearing findings plus five minor; all eleven verified against source and
folded. Three of the six are defects the fold itself introduced — which is the
argument for the second pass.

1. **Step 4's replacement text for `ai-review.yml` was false on this repo.**
   "A ready→draft now gets a real review" holds only *while unarmed*; canon's own
   revised template carries that qualifier, and the armed disjunct requires
   `draft == false`. The draft would have replaced one wrong comment with another,
   contradicting its own "no-op here" row. → Step 4 row now mandates copying the
   qualifier verbatim, and explains why.
2. **B2 was overclaimed.** "Without a `labeled` trigger the red check never
   clears" implies that *with* it, labelling clears the check. It does not — a
   label event starts a separate run, whose check-run is retained alongside the
   earlier one (the same §23.1 mechanism the plan cites elsewhere), and the
   two-signal override needs a commit-body marker, hence a new SHA anyway. → B2
   restated as *necessary, not sufficient*, with an instruction for D-0070.
3. **B2's ⚠️ rationale was itself confidently wrong.** Canon's `audit-trail`
   template block is the #329 *allowlist*, not `cancel-in-progress: true`, so
   copying it would not "introduce cancellation into a required context." The
   action (add no block) survives; the reason was replaced — precisely the class of
   inline reasoning B4 exists to delete from `acceptance.yml`.
4. **B2 rested on an unstated load-bearing assumption.** *(This finding's
   premise was later retracted — a `GITHUB_TOKEN` label write starts nothing;
   see D-0070 and §B2's corrected block. Kept verbatim as the Pass-N record.)*
   After B2, every label
   write in the repo starts an `audit-trail` run whose `verify` job is skipped,
   adding a `skipped` check-run to a *required* context; B2 is benign only under
   skipped⇒success. Now stated, cited (`audit-trail-check.yml:84`), and made
   observable by verification #8(b).
5. **A Current-state row was factually false.** The five other locally-owned
   workflows were shown with no `concurrency:` block; all five carry
   `cancel-in-progress: true`. The exemption conclusion is unchanged (none is
   required), but that row is the evidence base for claiming the #329 sweep is
   complete — and it is the row a future session reads when one of them *becomes*
   required, which is exactly how `acceptance` acquired B4. → Row corrected, an
   explicit Out-of-scope bullet added, and a standing rule written for D-0070.
6. **The ≤3-doc-surface arithmetic omitted `FRAMEWORK-TODO.md`**, which
   GOV-TODO-ISSUE-SPLIT forbids deferring, and the cross-repo item was assigned to
   no PR and carried none of the rule's filing obligations. → Backlog capture moved
   to PR 0; the `gh issue create --body-file -` + read-back + link-back steps
   written out.

Minor, all folded: Scope-Out and Step-4 D3 contradicted each other on
`config.json` (it is in scope); verification #4 credited an actionlint hook this
repo does not have; the Objective asserted an unverified cause for the Dependabot
split (now stated as measured state only, with the cause explicitly not
established); Step 2 would have copied a label-event example inapplicable to
`conformance`/`acceptance`; and four load-bearing assertions lacked ledger rows
(now 13a, 28a–28c, 37a–37d, M8, M9).

The reviewer independently confirmed and could not break: the B3/B4 allowlist is
*correct* for both workflows' exact trigger sets (only `reopened` changes; no
cost or queue regression); R3's re-aim hides no live untested delta (the one new
node24 surface is in the default-off autofix job); no `workflow_run` chain hangs
off `audit-trail`, so B2 cannot amplify through composition/auto-merge; the
counts are internally consistent; verification #3's known-drift set is accurate;
and the plan is not over-grown — every in-scope item traces to a named defect
except D3, which is now justified in place.

**Result:** findings folded; re-review required.

### Pass 3 — 2026-07-29 — independent (`verified-planning-reviewer`, fresh context)

Two load-bearing findings, three minor. All five folded. **This is the third
independent pass, the OPS-0066 cap.**

1. **Verification #3's known-drift set was wrong, and it contradicted R1.** Pass 1
   caught that "should now MATCH canon" was unachievable; the fold replaced the
   wording but sized the known-drift set to `pre-commit.yml`'s three lines.
   `check-drift.sh` whole-file-diffs *every* manifested caller, so every one of
   R1's deliberate customizations is a warning. **Measured by the author before
   folding: it emits 8 warnings on `main` today**, before any change
   (`ai-review`, `audit-trail`, `auto-merge-ai-prs`, `composition`, `docs-sync`,
   `labeler`, `links`, `pre-commit`). As written the check could never pass, and
   an executor holding it would be pushed toward exactly the `--update`-by-hand
   outcome that step is appointed to guard against. → Restated as a
   **before/after** comparison: pass = no *newly* drifting file, plus no drift
   inside `pre-commit.yml`'s `concurrency:` block.
2. **PR 1 touches four doc surfaces, and the plan self-granted the exemption
   Rule 1 reserves for the founder.** The fold declared this plan file "not
   counted" because it is the PR's own subject — true for PR 0, false for PR 1,
   whose subject is the migration. `plans/PLAN-*.md` is a named governance
   surface, and the plan-status rule forces the `Status` edit into the same PR as
   the work. → §Governance now states the collision as structural and offers two
   compliant mechanisms (ask for the founder OK + audit-trail commit line, or move
   `Status` to PR 2), rather than asserting an exemption.

Minor, all folded: M6's file split (21/4) contradicted canon's own "all eight
templates" record — remeasured as 8 at +13/−3 and 17 at ±1–3, conclusion
unchanged; §Governance applied only the *capture* half of GOV-TODO-ISSUE-SPLIT and
omitted the per-entry `*Tracker:*` issue-or-not decision, which the rule forbids
deferring; and Step 2 edits three files but analysed only two trigger sets
(`pre-commit`'s is `pull_request` + `push: branches: [main]`, not `push` on all
branches) — the `reopened`-only delta is unchanged.

The reviewer verified against source, and could not break: B2's four paragraphs
are mutually consistent and agree with Step 3, verification #8 and the Scope-Out
bullet; **the skipped⇒success assumption is true and correctly scoped** (it is the
reusable's job-level `if:`, which GitHub reports as a `skipped` check-run and
treats as success — unlike a workflow never triggered, which stays pending and
blocks); Step 4's `while unarmed` qualifier is right for this repo and agrees with
the "no-op here" row and R3; the five-non-required row, Scope-Out bullet and
standing rule agree with each other and with R6, and the "seven carry the shape"
count is exact; and **the execution order works** — Step 1's `sed` is guarded by a
`grep -q vladm3105/aidoc-flow-ci/` test, so it skips `conformance.yml` and
`acceptance.yml` entirely and cannot collide with Steps 2–4. It also confirmed
Step 4's header-comment fixes are load-bearing for verification #2, since
`check-pin-currency.sh` greps `@ci/vX.Y.Z` out of the whole file, comments
included.

**Result:** two load-bearing findings folded, but **not independently
re-verified** — the 3-pass cap (OPS-0066) is reached. Per the cap's own rule, the
open item goes to the human rather than to a fourth reviewer.

**Result:** findings folded; founder authorised a fourth, narrowly-scoped pass.

### Pass 4 — 2026-07-29 — independent, scoped (`verified-planning-reviewer`, fresh context)

Exceeds the OPS-0066 3-pass cap **by explicit founder authorisation** (2026-07-29),
and scoped deliberately to the three folds Pass 3 produced that had never been
independently checked: verification #3's restatement, §Governance's four-surface
resolution, and consistency damage from the Pass 3 fold itself. Three load-bearing
findings, two minor; all folded.

1. **Verification #3's measured "before" set was wrong — an author measurement
   error, caught by the reviewer reading source without running anything.** The row
   claimed 8 of 10 callers warn today; the author's original measurement had been
   truncated by a `head -30`. **Re-measured: all ten canon callers warn, 12
   `::warning::` lines across 10 files.** `secret-scan` and `standards-drift` were
   missing from the list, and the row was self-contradictory — it asserted "every
   one of R1's customizations is a warning" while omitting `secret-scan`'s
   `config-path`, which R1 names.
2. **The comparison baseline moves, and verification #3 did not account for it.**
   `check-drift.sh` frames each caller against the template *at the tag that caller
   declares*, so Step 1 re-points four callers from a v2.14.0 baseline to v2.16.0.
   `secret-scan`'s template is one of the eight that gained the +13/−3 allowlist at
   v2.16.0 (the plan's own M6 supplied the fact), and this plan forbids adding that
   block locally — so `secret-scan.yml` becomes the loudest warning in the
   after-run for a reason unrelated to any mistake, and the script's own "bring back
   to canonical" advice points straight at the `--update`-by-hand outcome R1 guards.
   → Row rewritten as a diff-of-outputs with an enumerated expected-delta set, and
   the baseline move called out explicitly.
3. **§Governance's Status arithmetic was self-defeating.** `Draft → In Progress →
   Completed` is a sequence, not one value; PR 2 is in scope, so PR 1 cannot
   legitimately write `Completed`. The `In Progress → Completed` edit was assigned
   to no PR at all, leaving the plan to end life stuck at `In Progress` — the exact
   stale-status defect the governance rule names. The stated reason for rejecting
   the deferral alternative was also wrong (it would have left the plan reading
   `Draft`, not `In Progress`). → Replaced with a per-PR Status table; PR 2 now
   carries the final transition and §Scope updated to match.

Minor, both folded: the cross-repo issue's link-back was unassigned between PR 0
and PR 1 (→ PR 1, with D-0070); and Step 2 did not say whether the blank line
between `concurrency:` and `jobs:` in `pre-commit.yml` goes, which
verification #3's byte-exactness clause turns on (→ it goes).

The reviewer verified sound, with no finding: the founder-OK mechanism is the one
`CLAUDE.md` actually prescribes and PR 0's two-surface count is right; Step 2's
rewritten trigger-set sentence is accurate for all three files and `reopened` is
the only behavioral delta; M6's restatement is internally consistent (8+14+2+1=25)
and `markdown-lint` is correctly out of scope as absent from this repo; the "seven
local workflows carry the shape" count is exact (17 files − 10 canon callers);
verification #3's `audit-trail.yml` note is right; and D4's annotation contains no
`@ci/v` string, so it is invisible to `check-pin-currency.sh` and correctly not
load-bearing for verification #2.

**Result: ready — with the residual stated, not hidden.** Four independent passes;
gate-green. Pass 4's three findings are folded but, like every fold, not
themselves re-verified. What makes this a stopping point rather than an infinite
regress: **two of the three were factual errors, not design defects** — a
truncated `head -30` that undercounted drift warnings, and Status-value
arithmetic — both of which the fold fixes by *measurement* (the drift count was
re-run and is now 10/10 from actual output) rather than by reasoning that could be
wrong again. The third (the baseline move) is now stated explicitly where it was
previously absent. No finding in Pass 4 touched B1–B4, the execution steps, or any
claim about canon's behaviour; those have survived three consecutive passes
unchanged. Cleared to open PR 0.
