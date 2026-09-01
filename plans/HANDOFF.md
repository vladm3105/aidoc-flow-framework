# Session Handoff

**One reader: a fresh session with zero context.** Current state, then what to do next.
**Rewritten wholesale each merge** — `git log -- plans/HANDOFF.md` is the archive; do not
restore prior states here. Settled traps live in `CLAUDE.md` § "Durable traps" and are
never repeated here.

**State:** framework spec **`0.48.0`**, plugin `0.25.0`, Hermes `0.12.1`; both platform
`FRAMEWORK_SPEC_VERSION` pins read `0.48.0`. `0.45.0` was **skipped** and never became a value
of `framework/VERSION` (`plans/DECISIONS.md` D-0082). `framework/v0.44.0` is the most recent
**tag**; `0.46.0`, `0.47.0` and `0.48.0` are untagged — see "Release provenance" below.

**Verified this session** (run, not asserted, at `794aa573`): conformance **457 passed / 943
subtests** via `pytest`, and **493** via `python -m unittest discover -s tests/conformance`
(CI's runner) — the two count subtests differently, so cite the command with the number ·
acceptance-deterministic **64** · unit **196** · `sdd_doc_lint` **6** (needs `PYTHONPATH=tools`)
· `pre-commit run --all-files` 19 hooks green, rc=0. **0 failing.**

Phase 0 `lint-smoke` is a separate harness and is RED — corpus debt deferred to the wholesale
regen; use `--skip-lint-smoke`.

## Release provenance — #558 CLOSED (D-0078)

**Founder decision 2026-08-28 (option 3):** correct forward, rewrite no published entry.
Executed — `framework/v0.44.0` cut at `2c69a402`.

⚠️ **Carried forward, and it is the sharper half of #558:** `GATE-SPEC` has **no release
step**. E001..E008 are all diff-local, so nothing checks that a superseded version was ever
published, and the gate is satisfied by *any* bump rather than the right one. It has **no
tracker home of its own** — only this paragraph and the release notes' "Known gap" block.
File it if it should have one.

## The backlog is GitHub issues

**Open issues: 34** (re-derived 2026-09-01 after PR #612 was raised — it files **#611** and
**#613** and closes **#606** on merge, leaving 33). Every figure in this section was re-derived
by command, not carried: the previously recorded 34 was right by coincidence, having been
measured before #609 closed and before this PR's two filings. Re-derive with
`gh issue list --state open --limit 300 --json number --jq 'length'`.
In-progress work carries **`status: in progress`** — currently only **#423**.

**Fourteen carry the `parked` label** and are not pickable: #438, #467, #473, #483, #484, #507, #528, #543, #544, #545, #546, #547, #548, #563.
Derive that set from the label, not from a title scan — two of them name the gating decision only in the body.
Three are blocked externally: **#484** (gated on v1.0.0), **#473** (the umbrella owns the
submodule pointer), **#528** (product call).

## What this session did

Four merges, in order: **#605** (closes #603) → **#608** (unbreak `main`) → **#607**
(closes #604). Two issues filed: **#606** — fixed in this session's fifth PR, which closes it —
and **#609** — which the founder closed COMPLETED at 05:08Z, mid-session, with no closing
comment. #606's fix also filed **#611**, and PR #612's own CI filed **#613**.

**`doc-maintainer` is eliminated — `plans/DECISIONS.md` D-0085, PR #605 (#603).** The caller
was pinned `@ci/v4.0.0`, a tag at which canon had **deleted** that reusable (v4 BC #2 /
CI-0040). Dependabot PR #591 made that repin and it **merged green**, because the workflow had
been `disabled_manually` since 2026-08-22 — a disabled workflow never runs, so there was
nothing to observe. Deleted the caller and its two config files; **supersedes D-0072 point 1**,
whose manifest-parity objection had evaporated (canon removed all three surfaces from its
manifest at v4). Discharges `CI-CANON-V4-MIGRATION-PLAN` step 2 / BC #2 early.

**Dependabot no longer proposes canon majors.** `.github/dependabot.yml` carries a
`version-update:semver-major` hold on `vladm3105/aidoc-flow-ci/*`, in **both** name forms (the
path form `owner/repo/<path>.yml` and the bare `owner/repo`, since a composite action would
escape the first). **Ten** canon majors had merged unreviewed — #522–#526 → `ci/v3.0.0`,
and #590–#594 → `ci/v4.0.0` — which is the entire explanation for the pin split.

**Pins are now 7 × `ci/v2.16.0` + 5 × `ci/v3.0.0` + 4 × `ci/v4.0.0` = 16 sites / 15 files**
(#607 / #604 corrected `CLAUDE.md`, which had claimed 17 sites all at `v2.16.0`). Two facts
that must travel together with that number: the hold is **major-only**, so grouped
minor/patch bumps can still widen the split — that is how it split the first time; and the
7 callers at `v2.16.0` will now go **silent**, because canon ships no more v2, making
`pin-currency-reader` / #393 the compensating detector.

⚠️ **Correction worth reading before trusting D-0085's first version.** #603 shipped the claim
that "**no** drift check covers `.github/dependabot.yml`". That was an unchecked two-item
enumeration and the conclusion was **inverted**: `install/apply-standards.sh:434` exact-matches
that file and `--check` exits 1, and canon's template has **no `ignore:` block** — so the hold
*is* the drift. **A session that "restores canonical" on that red deletes the hold.** Nothing
detects its deletion. Corrected in D-0085, `CLAUDE.md` and the file's own comment by #607.

## `main` was broken mid-session by a direct push — the mechanism, not the incident

`2943bf3b` ("Update status options in IPLAN-TEMPLATE.yaml") was pushed **directly to `main`**
and edited `framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml` without re-running
`tools/sync-plugin-framework.sh`. The vendored plugin copy drifted and took down three
contexts at once — conformance, GATE-SPEC (its *conformance* step; the diff-aware E001–E008
checks **passed**), and pre-commit. #608 repaired it with the generator, one file.

**The durable part:** a direct push to `main` bypasses PR checks entirely, so `GATE-SPEC` never
evaluated that `framework/**` edit. Whether it owes a version bump was tracked in
**#609**, which the founder **closed COMPLETED at 05:08Z with no closing comment** — so the
answer is not recorded on the issue, and no `plans/DECISIONS.md` or GD entry carries it either.
Treat the divergence as **accepted, not resolved**: `IPLAN-TEMPLATE.yaml` is unchanged since
`2943bf3b` and still carries the `created | modified` vocabulary its `:160-165` note now flags
explicitly as "NOT reconciled here". Re-file if that costs anything downstream; do not
reopen #609 expecting to find reasoning in it.

## CI gating — `ai-review` and `composition` no longer gate (D-0084)

**Read `plans/DECISIONS.md` D-0084 rather than this summary.** Both were removed from `main`'s
required status checks; both still run and still post verdicts. This is **server state that
lives in no git repository**, and D-0084 carries the one-call restore.

**The four required contexts are:** `Framework + platform conformance`,
`call / Lint / format / security hooks`, `call / verify`, `Acceptance tier (deterministic)`.
Re-derive with
`gh api repos/vladm3105/aidoc-flow-framework/branches/main/protection/required_status_checks --jq '.contexts[]'`.
`GATE-SPEC` and `dep-scan` are **not** required — a red one leaves a PR `UNSTABLE`, not
`BLOCKED`.

**`call / verify` is NOT a review gate.** It greps the commit body for a literal phrase; the
skip form is self-authorizing and bot authors are exempt.

**`ai-review` fails intermittently** with `litellm: proxy request failed after 3 attempts:
ResponseShapeError` (upstream `aidoc-flow-ci#543`) — observed earlier this session and passing
on a re-run of that branch. It is **not** the 402 this proxy is otherwise known for, and not
size-driven. **On PR #612 it did not clear**: two consecutive failures on the same head, so
"re-run and it passes" is not reliable. Since it no longer gates the cost is a lost
verdict — #612 carries none and rests on its author-side OPS-0065 review. Evidence added to that upstream

issue, because at **5 files / +387−239** this instance also sits below the file-count
discriminator its title asserts (1 file passes, 179 fails), so satisfying that budget is not
sufficient to pass.

**`dep-scan` fails intermittently too, from a different cause — #613.** Four instances of one
resolver fault, and they are not all the same shape: **three** are `call / dep-scan` hitting
`curl: (6) Could not resolve host: github.com`, each clearing on a re-run of the same SHA; the
fourth was a local `git fetch` on the host hitting `ssh: Could not resolve hostname github.com`.
That fourth one is the evidence the fault is **host-level, not workflow-level**. `trivy-scan`
passes on the same pool in the same windows while downloading from that same `github.com` host,
so it is not a pool outage. Since `dep-scan` does not gate (above), re-run it rather than
diagnosing the workflow; ownership of the host-side fix is the open question in the issue.

## What to do next — prioritized

1. **Tag the untagged releases.** `framework/v0.44.0` is still the most recent tag while
   `0.46.0`, `0.47.0` and `0.48.0` have all shipped to `main`. Three untagged releases is the
   point at which "correct forward" stops being cheap, and the missing `GATE-SPEC` release
   step still has no tracker home — file it.
2. **#393 / `plans/CI-CANON-V4-MIGRATION-PLAN.md`** — still **BLOCKED** on two founder /
   infrastructure prerequisites (runner labels `ci`/`ephemeral` do not exist; `LLM_URL` /
   `LLM_API_KEY` do not exist and the caller still forwards three `LITELLM_*` names v4
   un-declares). ⚠️ **Its stated `--repin` remedy is unsafe** — read the plan, not the issue
   body. The plan's exposure table and every line citation were re-measured 2026-09-01 and it
   now carries a `## Review log`. **Its repin must now also move
   `.github/ai-review/config.json`'s `$schema`** (plan step 6 / verification V3b) —
   `tests/conformance/test_ai_review_schema_pin.py` fails the required conformance context
   otherwise.
3. **#588** — the identity-carrier split. Not startable alone; it is `OKF-CONFORMANCE-001`
   D1's to settle.
4. **#546** — carries a measured correction that **splits it**. The `_required: false` half of
   the `STY02` defect is independently shippable and does not wait on the parked subtype
   decision. Re-title or split before picking it up.
5. **#423** — the only issue marked in progress. `origin/fix/423-site-badge-selfheal` carries
   `f05dfc0d`. Needs a rebase onto current `main`, a finalized commit message and a PR.
