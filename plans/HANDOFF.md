# Session Handoff

**One reader: a fresh session with zero context.** Current state, then what to do next.
**Rewritten wholesale each merge** — `git log -- plans/HANDOFF.md` is the archive; do not
restore prior states here. Settled traps live in `CLAUDE.md` § "Durable traps" and are
never repeated here.

**State:** framework spec **`0.46.0`**, plugin `0.25.0`, Hermes `0.12.1`; both platform
`FRAMEWORK_SPEC_VERSION` pins read `0.46.0` — the `0.43.0` skew is closed.
`framework/v0.44.0` is **tagged and released**, the first framework tag since `v0.41.3`.

**Verified this session** (run, not asserted), after the `0.46.0` bump and both fanouts:
conformance **414** · acceptance-deterministic **64** · unit **196** · packaging **5** ·
release **50** · `sdd_doc_lint` **6**. **0 failing.**
Phase 0 `lint-smoke` is a separate harness and is RED — corpus debt deferred to the
wholesale regen; use `--skip-lint-smoke`.
*(`pytest tools/sdd_doc_lint/tests` needs `PYTHONPATH=tools` or it fails to collect.)*

## Release provenance — #558 CLOSED (D-0078)

`0.42.0` was never a value of `framework/VERSION` and `0.43.0` shipped untagged. **Founder
decision 2026-08-28 (option 3):** correct forward, rewrite no published entry. **Executed** —
`framework/v0.44.0` cut at `2c69a402` and released, provenance in both the tag message and the
release notes. `gh release list` now reports `0.44.0` as Latest, which was the presenting
symptom.

⚠️ **Carried forward, and it is the sharper half of #558:** `GATE-SPEC` has **no release
step**. E001..E008 are all diff-local, so nothing checks that a superseded version was ever
published, and the gate is satisfied by *any* bump rather than the right one — which is what
produced the phantom `0.42.0`. It has **no tracker home of its own**: only this paragraph and
the release notes' "Known gap" block. File it if it should have one.

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

1. ~~**TEMPLATE-COMPLETENESS-001**~~ — **SHIPPED** as framework `0.46.0` / **GD-18**, branch
   `feat/template-completeness-001`. (The handoff previously said this plan lived on branch
   `plans/template-completeness-001`; it had already **merged** via PR #561 and is on `main`.)
   Bundles **#550, #551, #532** as planned, plus **#569** folded in under the founder's
   per-bump grant. All tiers green after both fanouts.
   ⚠️ **#557 was folded in and then REVERTED before commit** — independent review falsified
   both halves of its premise (see the plan's fold note and the comment on #557). It stays
   **open** and needs re-scoping: the real gap, if any, is that no surface says
   `total_sections` counts *numbered* sections only, which is a three-layer documentation
   issue rather than an EARS marker bug. `tests/conformance/test_required_section_sets.py`
   now pins every layer's derived required set so the class cannot recur silently.
   ⚠️ **#565 was granted for this bundle and then EXCLUDED on measurement.** Its fix shape
   assumes `warning` severity is safe for the all-`.md` corpus. It is not:
   `tests/acceptance/_harness.py` matches warnings as a **bidirectional multiset**, so a new
   warning fails a target exactly as an error does. 55 `.md` fixtures + 11 `.md` corpus files
   would each gain one, so shipping it here pins 55+ warnings that #555's regen then has to
   remove. Recorded on #565 and in the plan's fold note.

2. ~~**#531**~~ — **done**, PRs **#570** (plan) and **#571** (guard, merge second). Landed as
   its own module `tests/conformance/test_ref_granularity_parity.py`, not as an extension of
   `GateCheckIdParity`. ⚠️ The `TRACEABILITY.md` caveat was real **and understated**: beyond
   having no `###` heading, the anchor the plan specified for that surface matches the
   *drifted* text **zero** times, so the regression fixture would have raised `Unparseable` and
   stood as evidence of a detection that never happened.
3. ~~**#554**~~ — **done**, PR **#572**.
4. **#423** — the only issue marked in progress. `origin/fix/423-site-badge-selfheal`
   carries `f05dfc0d` (+41/−14 in `scripts/sync-version-refs.sh`). Needs a rebase onto
   current `main`, a finalized commit message and a PR — not a rescue.
5. **#393** — ⚠️ **NOT a `--repin`, and the issue body's stated remedy would hang a required
   check.** Plan: `plans/CI-CANON-V4-MIGRATION-PLAN.md`, PR **#573**. All five `ci/v4.0.0`
   breaking changes apply here. **BLOCKED on two founder/infrastructure prerequisites, both
   silent:** (a) both runners advertise only `self-hosted,ci-runner,single-use` while v4
   renames them to `ci`/`ephemeral`, and a job routed to labels no runner carries **queues
   forever** — `ai-review` is required, so the migration PR could not merge itself; (b)
   `LLM_URL`/`LLM_API_KEY` do not exist and the caller still forwards the three `LITELLM_*`
   names that v4 **un-declares**, which is a load-time `startup_failure`. Nothing can land
   ahead of the repin — the caller edits are only valid *at* v4.

   Nothing can land ahead of the repin: the BC4/BC5 caller edits are only valid *at* v4.
