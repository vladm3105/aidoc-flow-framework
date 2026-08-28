# Session Handoff

**One reader: a fresh session with zero context.** Current state, then what to do next.
**Rewritten wholesale each merge** — `git log -- plans/HANDOFF.md` is the archive; do not
restore prior states here. Settled traps live in `CLAUDE.md` § "Durable traps" and are
never repeated here.

**State:** framework spec **`0.43.0`**, plugin `0.25.0`, Hermes `0.12.1`; both platform
`FRAMEWORK_SPEC_VERSION` pins read `0.43.0`.

**Verified this session** (run, not asserted): conformance **375 passed / 796 subtests** ·
acceptance-deterministic **64 passed / 56 subtests** · `sdd_doc_lint` **6 passed** ·
Hermes **570 passed** · `pre-commit` 19 hooks green on commit. **0 failing.**
Phase 0 `lint-smoke` is a separate harness and is RED — corpus debt deferred to the
wholesale regen; use `--skip-lint-smoke`.
*(`pytest tools/sdd_doc_lint/tests` needs `PYTHONPATH=tools` or it fails to collect.)*

## ⚠️ `0.43.0` is not released, and `0.42.0` never existed — #558

`framework/VERSION` reads `0.43.0` and every other surface agrees, so the natural inference
is that `0.43.0` shipped. **The latest framework release is `0.41.3`.** Worse, spec
`0.42.0` was never a value of `framework/VERSION` at all — `272d964d` moved the file
straight from `0.41.3` to `0.43.0` — yet `CHANGELOG.md:28` documents a `0.41.3 → 0.42.0`
release and GD-14 is ratified against it.

```sh
git tag --list 'framework/v0.4*'                 # -> v0.41.2, v0.41.3 only
gh release list --limit 5                        # -> "Framework Spec 0.41.3   Latest"
git log --oneline -S'0.42.0' -- framework/VERSION # -> no output
```

**Filed as #558 with three options; it needs a founder call.** Do not cut a tag without
reading it. This is also why `TEMPLATE-COMPLETENESS-001` blocks on its `0.41.3` CHANGELOG
edit — `0.41.3` is the one entry that *is* released.

## The backlog is GitHub issues

**Open issues: 32.** Re-derive with `gh issue list --state open --limit 300`.
In-progress work carries **`status: in progress`** — currently only **#423**.

**Twelve are blocked on a founder decision** and are not pickable. Eight carry a `⏸ PARKED`
title prefix (#438, #483, #543–#548); four name the decision only in the body or in a plan,
so a title scan misses them: **#467**, **#507**, **#558** (new, above), and **#540** (its
three options all touch `framework/**` and which one to take is a founder call).
**#553** is likewise gated — on the IPLAN `title` placement question that
`IPLAN-LAYER-REVIEW-001-DESIGN.md` R8 owns.

Three more are blocked externally: **#484** (gated on v1.0.0), **#473** (the umbrella owns
the submodule pointer), **#528** (product call).

## What this session did

**A backlog readiness pass over all open issues**, re-verifying each premise against `main`
rather than trusting the issue bodies. Four verification comments posted
(#438, #532, #393, #473) and three defects filed — **#556**, **#557**, **#558** — each
summarised in its own issue; do not re-derive them from here.

⚠️ **#556 is the one to read before any framework bump.** `CLAUDE.md`'s durable trap on
`fw_prev` is **wrong**: `fw_prev` is detected from `docs/PARITY.md`
(`scripts/sync-version-refs.sh:288`), not `CLAUDE.md`, and the script's own header at
`:50-54` is stale too. Following the trap protects the wrong file.

**Discarded design finding A2** (founder decision, 2026-08-27) — commit `3a26050b` on
branch **`docs/a2-discard-d0077`**, recorded as **`plans/DECISIONS.md` D-0077**. The same commit corrected three
stale claims that pre-push review surfaced in those files, the largest being that
`IPLAN-TDDREF-001-PLAN.md` still recorded itself as unmergeable with the version bump
withheld, when it had merged with the bump in `0.43.0` and is GD-16's named authority
record.

## What to do next — prioritized

1. **`plans/TEMPLATE-COMPLETENESS-001-PLAN.md`** — bundles **#550, #551, #532** into one
   framework MINOR (`0.43.0 → 0.44.0`); each independently trips GATE-SPEC-E005, so
   shipping them apart costs three bumps, three fanouts and three founder grants. Three
   review cycles done (1 self + 2 dispatched independent), 28-claim ledger, citation gate
   green. **#552 and #553 were cut from the bundle at Pass 2** — the plan's Out-of-scope
   section says why; each needs its own plan.
   Its one escalated decision was resolved by the founder as **option (b): correct forward
   inside the new `0.44.0` entry; do not rewrite the released `0.41.3` entry** — recorded
   here as well as in the plan, so it survives independently.
   The plan lives on branch **`plans/template-completeness-001`** (`aef7b76e`), which is
   branched from `main` and independent of the other two open branches.
2. **#531** — `tests/`-only, needs no version bump, so it lands independently of #558's
   release question. Extend `tests/conformance/test_governance.py::GateCheckIdParity`
   (`:143`) — the same set-equality-across-surfaces shape one layer over. ⚠️
   `framework/governance/TRACEABILITY.md` has no `### Reference granularity` heading (it has
   no `###` headings at all), so the issue's surface list needs adjusting first.
3. **#554** — `plans/`-only, no bump. Retires a resolved open question and a void Stage 1
   from `OKF-CONFORMANCE-001-DESIGN.md`, the entry point for that initiative; until it
   lands, a session picking OKF up gets a wrong blocker count and an instruction GD-15
   forbids.
4. **#423** — the only issue marked in progress. `origin/fix/423-site-badge-selfheal`
   carries `f05dfc0d` (+41/−14 in `scripts/sync-version-refs.sh`). Needs a rebase onto
   current `main`, a finalized commit message and a PR — not a rescue.
5. **#393** — CI pins are split **11 × `ci/v2.16.0` + 6 × `ci/v3.0.0`** against canon
   `ci/v4.0.0`. ⚠️ Two major boundaries: `--repin` rewrites the tag string only and cannot
   carry a breaking-change adaptation, so read canon's release notes first.

## Blockers and standing constraints

**⚠️ A framework `VERSION` bump needs a per-bump founder OK** and is unsplittable — it
exceeds Rule 1's 3-surface cap because `scripts/sync-version-refs.sh` writes three of the
four surfaces itself and re-stages them. Record the grant in the commit message. Not
standing.

**⚠️ Corpus and fixture debt all waits on one run.** #486, #487 and #555 item 1 are
deferred to the same `plans/CORPUS-REGEN-RUNBOOK.md` pass, which requires a live Claude Code
plugin session, not a framework-dev container.
