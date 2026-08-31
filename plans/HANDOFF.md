# Session Handoff

**One reader: a fresh session with zero context.** Current state, then what to do next.
**Rewritten wholesale each merge** — `git log -- plans/HANDOFF.md` is the archive; do not
restore prior states here. Settled traps live in `CLAUDE.md` § "Durable traps" and are
never repeated here.

**State:** framework spec **`0.47.0`**, plugin `0.25.0`, Hermes `0.12.1`; both platform
`FRAMEWORK_SPEC_VERSION` pins read `0.47.0` — the `0.43.0` skew is closed. `0.45.0` was
**skipped** and never became a value of `framework/VERSION` (`plans/DECISIONS.md` D-0082).
`framework/v0.44.0` is **tagged and released**, the first framework tag since `v0.41.3`.

**Verified this session** (run, not asserted), after the `0.47.0` bump and both fanouts:
conformance **451** · acceptance-deterministic **64** · unit **196** · packaging **5** ·
release **50** · `sdd_doc_lint` **6**. **0 failing.**
*(The conformance figure was left at the `0.46.0`-era **414** through several edits — it is the
one number this release moved, in the file whose whole purpose is a fresh session's verified
current state. Caught on OPS-0065 round 4; cf. the auto-memory entry "verify carried-forward
handoff claims".)*
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

**Open issues: 31.** Re-derive with `gh issue list --state open --limit 300`.
In-progress work carries **`status: in progress`** — currently only **#423**.

**Eleven are blocked on a founder decision** and are not pickable. Eight carry a `⏸ PARKED`
title prefix (#438, #483, #543–#548); three name the decision only in the body or in a plan,
so a title scan misses them: **#467**, **#507** and **#558** (new, above). ~~**#540**~~ is no
longer among them — GD-19 ships it in `0.47.0` as the advisory `FRCAP01`, so the founder call it
was waiting on has been made.
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
   ⚠️ **#557 was folded in, REVERTED before commit, then re-scoped and SHIPPED as GD-21** in
   `0.47.0`. Independent review had falsified both halves of its original premise, and the
   re-scope is the residue it named: no surface said `total_sections` counts *numbered*
   sections only. That is now stated in `LINT_RULES.md` and at each divergent declaration.
   **Four** layers diverge, not three — IPLAN diverges *downward* (2 vs 6) and was missing its
   comment until OPS-0065 review caught it. `tests/conformance/test_required_section_sets.py`
   pins every layer's derived required set so the class cannot recur silently.
   ⚠️ **#565 was granted for this bundle and then EXCLUDED on measurement.** Its fix shape
   assumes `warning` severity is safe for the all-`.md` corpus. It is not:
   `tests/acceptance/_harness.py` matches warnings as a **bidirectional multiset**, so a new
   warning fails a target exactly as an error does. 55 `.md` fixtures + 11 `.md` corpus files
   would each gain one, so shipping it here pins 55+ warnings that #555's regen then has to
   remove. Recorded on #565 and in the plan's fold note.

2. ~~**#531**~~ — **merged** 2026-08-30 as `0a2d4eeb` (PRs **#570** plan, **#571** guard);
   `#531` closed by the merge. Module `tests/conformance/test_ref_granularity_parity.py`,
   **32 tests**. ⚠️ Merged with `--admin` over a red required `call / ai-review` — see the
   ai-review note below.

   **The durable lesson is about guard design, not about GD-03.** Three adversarial rounds
   found **3, then 5, then 7** wrong phrasings; rounds 2 and 3 ran against branches already
   pushed for merge, and each found governance text that genuinely grants ADR/TDD
   document-level citation (the GD-13 drift verbatim) reported as **correct**. A
   marker-and-phrase classifier over prose has a known-closed set that is **never its
   coverage**, and one construction is provably not closable that way at all. The fix was to
   stop relying on classification for the direction that matters: `AnchoredProseIsPinned`
   pins each anchored region by digest, so a re-drift cannot pass unnoticed however it is
   worded. **Reach for a digest pin or a parsed set before reaching for another marker.**
   Rationale: `plans/DECISIONS.md` **D-0079** items 7-9.

   Two sub-lessons: **counts narrated from memory were wrong three times** across four
   documents (now asserted by `DocumentedCountsAreReal`); and a review whose reproductions
   were **hand-traced rather than executed** still found seven real defects — all seven
   reproduced when re-run, so trace-only findings are worth re-executing, not discounting.
3. ~~**#554**~~ — **done**, PR **#572**.

⚠️ **`call / ai-review` NO LONGER GATES — `plans/DECISIONS.md` D-0084 (2026-08-31), which is
authoritative; read it rather than this summary.** It and `call / composition` were removed from
`main`'s required status checks; both still run and still post verdicts. **No required status
check blocks on either** — that is the accurate scope, not "nothing blocks":
`required_conversation_resolution` is still true and `required_pull_request_reviews` still
exists, and both are inert only because canon submits COMMENT-state reviews here and opens no
inline threads.

**`call / verify` is NOT a review gate.** It is an audit-trail marker: the author writes the
phrase, `Self-review skipped per founder OK` is a self-authorizing opt-out, and bot authors are
exempt. With `required_approving_review_count: 0`, no automated surface can now falsify a
self-review claim. D-0084 §"What still gates review" has the detail.

**Never disable the ai-review WORKFLOW while `call / composition` is required** — de-requiring
ai-review is fine, since the workflow still runs and composition still fires and reports. The
pending-forever risk needs the workflow stopped, not the context de-required. (And on this repo
composition never enforced anything anyway: canon hardcodes it to pass — D-0084.)

**The failure below is now diagnosed, and the handoff's previous hypothesis was wrong.** It is
**not** an outage and **not** line-count: PR **#589** (+555/-0, **1 file**, 41,256 diff bytes)
produced two real verdicts on the same day PR **#595** (+630/-280, **179 files**, 149,906 diff
bytes) failed, deterministically, on re-run. ⚠️ **The exact discriminator is NOT settled** — with
n=2, file count and byte size co-vary, and an earlier version of this paragraph asserted file
count. What IS measured: #595 is **under canon's 400,000-byte input cap, which never fired**, so
the guard passes a payload the call then rejects. A spec bump fans out to ~179 mostly one-line files
and `GATE-SPEC-E005` forbids splitting it, so the repo's own release shape was structurally
unmergeable. Filed upstream as
[aidoc-flow-ci#543](https://github.com/vladm3105/aidoc-flow-ci/issues/543). The historical
record below is kept because it shows how the wrong inference was reached:

- **2026-08-29 was NOT an outage.** The LiteLLM step **succeeded** on three other branches
  (`33272686574` `fix/577` 20:08Z, `33273970026` `fix/574` 20:37Z, `33275838766`
  `feat/template-completeness-001` 21:20Z) while `feat/531-refgran-guard` failed **five
  times** (19:58 / 20:05 / 20:24 / 20:38 / 20:52Z). The proxy was up; that PR alone failed.
- **2026-08-30: every run that reached the proxy failed**, across three branches — and every
  `success` sampled took the **skip path** (`Run review through LiteLLM → verdict file =
  skipped`). **`#586` merged this way**: run `33344007376` on `c7cf1dbb` is green via
  `ai-review skipped (label OR R3 pre-approved OR review-event)`, having reviewed nothing.
  `#586` is **+3068** lines, so its green is *not* evidence the proxy handles large diffs.

**The one fact from that era still worth keeping:** `ResponseShapeError` is a **malformed
response body**, a **different symptom from the 402** this proxy is otherwise known for — so do
not check the account balance for it. *(The paragraph that used to sit here named `#559` as the
run that would decide between outage and large-diff. That framing is superseded: the failure is
neither an outage nor line-count, and the decisive measurement is above.)*

**Mechanics, measured:** `skip-ai-review` only *re-fires* ai-review, and this repo's own
measurement (scratch PR #376, `CLAUDE.md` § "Merging and CI mechanics") is that a label write
**cannot** clear a red required check. That mechanic is unchanged and still true of the
contexts that ARE required — but its old consequence is not: `gh pr merge --admin` is no longer
the only path for a PR whose ai-review runs and fails, because ai-review no longer gates
(D-0084). `#571` landed by `--admin` under the old regime; a PR in that position today merges
normally. The proxy is host-local and its config lives in **no git repo**; `CLAUDE.md:506`
documents the address but the runtime value is a repository secret, so treat the documented
value as documentation, not as verified.
4. **#423** — the only issue marked in progress. `origin/fix/423-site-badge-selfheal`
   carries `f05dfc0d` (+41/−14 in `scripts/sync-version-refs.sh`). Needs a rebase onto
   current `main`, a finalized commit message and a PR — not a rescue.
5. **#393** — ⚠️ **NOT a `--repin`; the issue body's stated remedy silently kills the review.**
   *(It used to say "would hang a required check" — void since D-0084; `ai-review` is advisory,
   so the failure mode is now an unreviewed merge rather than a deadlock.)* Plan: `plans/CI-CANON-V4-MIGRATION-PLAN.md`, PR **#573**. All five `ci/v4.0.0`
   breaking changes apply here. **BLOCKED on two founder/infrastructure prerequisites, both
   silent:** (a) both runners advertise only `self-hosted,ci-runner,single-use` while v4
   renames them to `ci`/`ephemeral`, and a job routed to labels no runner carries **queues
   forever** — which since D-0084 costs the verdict, not the merge; (b)
   `LLM_URL`/`LLM_API_KEY` do not exist and the caller still forwards the three `LITELLM_*`
   names that v4 **un-declares**, which is a load-time `startup_failure`. Nothing can land
   ahead of the repin — the caller edits are only valid *at* v4.

   Nothing can land ahead of the repin: the BC4/BC5 caller edits are only valid *at* v4.
