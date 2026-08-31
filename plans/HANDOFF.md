# Session Handoff

**One reader: a fresh session with zero context.** Current state, then what to do next.
**Rewritten wholesale each merge** — `git log -- plans/HANDOFF.md` is the archive; do not
restore prior states here. Settled traps live in `CLAUDE.md` § "Durable traps" and are
never repeated here.

**State:** framework spec **`0.48.0`**, plugin `0.25.0`, Hermes `0.12.1`; both platform
`FRAMEWORK_SPEC_VERSION` pins read `0.48.0`. `0.45.0` was **skipped** and never became a value
of `framework/VERSION` (`plans/DECISIONS.md` D-0082). `framework/v0.44.0` is the most recent
**tag**; `0.46.0`, `0.47.0` and `0.48.0` are untagged — see "Release provenance" below, the gap
is the same one #558 was about.

**Verified this session** (run, not asserted), after the `0.48.0` bump and both fanouts:
conformance **457 / 943 subtests** · acceptance-deterministic **64 / 56** · unit **196 / 231** ·
`sdd_doc_lint` **6** · `pre-commit` 19 hooks green. **0 failing.**
Conformance moved 453 → **457**: `tests/conformance/test_layer_title_declared.py` adds four.
**Re-run unchanged after `main` was merged into #598**, all still green. ⚠️ **That 457 is a
`pytest` count** (`python3 -m pytest tests/conformance -q` → `457 passed, 943 subtests passed`).
CI runs `python -m unittest discover -s tests/conformance -v`, which reports **493** for the same
tree — the two runners count subtests differently, so neither figure is wrong and neither
travels. Cite the command with the number.

⚠️ **One unreproduced transient, recorded rather than explained away.** The first measurement
run immediately after `bump_version.py` reported `1 failed` in **both** conformance and unit;
six subsequent full runs — including one with `platforms/**/__pycache__` deleted — were clean,
and the failing test names were not captured. **Do not treat this as known-benign.** The
concrete hazard found while chasing it: `tests/unit/test_sync_scripts.py:39` **executes
`sync-plugin-framework.sh` against the live working tree**, `rm -rf`-ing and regenerating 126
tracked files mid-suite. The regeneration is content-identical, so `git status` stays clean and
nothing is damaged — but any reader of those paths during that window sees them missing. That
is a real cross-suite hazard whether or not it caused this particular transient.

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

**Open issues: 27** (measured 2026-08-31). Re-derive with
`gh issue list --state open --limit 300 --json number --jq 'length'`.
In-progress work carries **`status: in progress`** — currently only **#423**.

**Ten are blocked on a founder decision** and are not pickable. Eight carry a `⏸ PARKED`
title prefix (#438, #483, #543–#548); two name the decision only in the body or in a plan, so a
title scan misses them: **#467** and **#507**. ~~**#540**~~ left this set when GD-19 shipped it
in `0.47.0` as the advisory `FRCAP01`; ~~**#558**~~ is CLOSED.

⚠️ **The count and the enumeration are one sentence, deliberately.** A previous revision tallied
"Eleven" as 8 + 3 and then added #553 as a "likewise gated" twelfth *outside* the count, so the
stated number and the list disagreed. Keep every gated issue inside the arithmetic or the tally
stops being checkable.

~~**#553**~~ is no longer gated — the IPLAN `title` placement question that
`IPLAN-LAYER-REVIEW-001-DESIGN.md` R8 owned was **decided** on 2026-08-31 (GD-23 / D-0083) and
shipped in `0.48.0`. R8 is superseded on placement; its `artifact_type` half is unaffected and
now belongs to **#588**.

Three more are blocked externally: **#484** (gated on v1.0.0), **#473** (the umbrella owns
the submodule pointer), **#528** (product call).

## What this session did

**Shipped `IPLAN-SELF-DESCRIPTION-001` — #553 — as framework `0.48.0` / GD-23.**
`SPEC-TEMPLATE.yaml`, `TDD-TEMPLATE.yaml` and `IPLAN-TEMPLATE.yaml` declared no document title
while every artifact they produce carries one. All three now declare a **top-level scalar**
`title:`; IPLAN also gains a per-entry `file_manifest.files[].description` and a
`document_control._guidance` note reserving `session_summary` so it cannot collide with the §5
`session_handoff` section. Guard: `tests/conformance/test_layer_title_declared.py`.
Rationale in **GD-23** and **D-0083**; do not re-derive it from here.

**The one fact worth carrying forward is about the two tiers, not about `title`.**
`sdd_doc_lint._load_section_targets` admits a top-level key only when its value is a mapping
carrying an integer `_size_target`. `tests/acceptance/_harness.template_sections` admits
**every** top-level mapping except `metadata`, with no `_size_target` requirement, and asserts
the result against the goldens. **So a template key authored as a mapping can leave conformance
green and redden every golden for that layer.** Measured, not reasoned: the mapping mutant was
executed and produced `missing template sections ['title']` in acceptance while
`test_required_section_sets.py` stayed green. Any future top-level template key faces the same
fork — check both tiers, and prefer a scalar.

**Two issues filed / corrected from measurement taken while baselining:**

- **#588** — the identity-carrier split. Templates declare `id:` (5 of 8, read by nothing);
  artifacts and goldens author `doc_id:` (what `sdd_doc_lint` actually reads); IPLAN adds
  `document_control.iplan_id` and goldens add `metadata.artifact_id`. Four carriers, none
  normative, and the two sets are **disjoint**. Belongs to OKF D1.
- **#546** — a **correction comment**, not a new issue. That issue's "What is NOT broken"
  section claims the `STY02` path is unaffected by `_load_section_targets`' skips. It is not:
  one function serves **two** rules, so a `continue` also drops the section's declared
  `_size_target` from the map `STY02` reads. **11 sections across 3 layers** fall back to the
  flat 200 — `file_manifest` declares 400 and is enforced at 200, and PRD's
  `component_decomposition` contradicts a comment two lines above the branch that drops it.

**Process, worth repeating.** The plan took four dispatched independent passes (8 → 4 → 2 → 0
load-bearing findings) and CI `ai-review` then caught a defect **none of them could have** —
introduced by the fold that closed the fourth pass. The reordering script matched
`startswith('| 4')`, which catches Claim **4** as well as 40-42, and deleted it. **The citation
gate had already reported it** as `verified 41 citation(s)` against a 42-row ledger; the `ok`
was read and the number was not. Two transferable rules, now in D-0083: a prefix match on a
numeric ID is a bug the moment the ID space passes 9, and a gate's success line carries a
measurement, not just a verdict.

**Also landed here: `call / ai-review` and `call / composition` were removed from `main`'s
required status checks** — `plans/DECISIONS.md` **D-0084**, PR **#598**. Both workflows still
run and still post verdicts; only the merge-blocking is gone. This is **server state that lives
in no git repository**, so D-0084 is the only artifact of it and carries the exact one-call
restore. The next section has the scope and the traps; read D-0084 before declaring any PR
unblocked.

## CI gating — `ai-review` and `composition` no longer gate (D-0084)

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
**intermittent**, and **not** size-driven. Measured across five runs (full table in D-0084): one
branch at ~34 KB failed at 13:55, produced a real verdict at 13:57, and failed again at 14:01.
⚠️ **This diagnosis was wrong twice** — first "file count", then "diff size, deterministic" —
both generalised from n=2. Every observed run is far under canon's **400,000-byte input cap,
which never fires** (34 KB is 8.5% of it), so a size budget upstream would chase the wrong
variable. A spec bump fans out to ~179 mostly one-line files
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
(D-0084). **#571** — the `#531` ref-granularity guard, merged 2026-08-30 — landed by `--admin`
under the old regime; a PR in that position today merges normally. The proxy is host-local and
its config lives in **no git repo**; `CLAUDE.md` § "Unified CI" (the `LITELLM_BASE_URL` bullet)
documents the address but the runtime value is a repository secret, so treat the documented
value as documentation, not as verified.

## What to do next — prioritized

Items 1-3 of the previous revision (`TEMPLATE-COMPLETENESS-001`, #531, #554) are all **shipped**
and have been removed rather than kept as struck-through history — `git log` is the archive.

1. **Tag the untagged releases.** `framework/v0.44.0` is still the most recent tag while
   `0.46.0`, `0.47.0` and `0.48.0` have all shipped to `main`. This is the *same* gap #558 was
   about, re-accumulating: **`GATE-SPEC` has no release step**, E001..E008 are all diff-local, so
   nothing checks that a superseded version was ever published. Three untagged releases is the
   point at which "correct forward" stops being cheap. That missing gate check still has **no
   tracker home of its own** — file it.
2. **#588** — the identity-carrier split, filed this session. Not startable alone: it is D1's to
   settle, and `framework/governance/FRONTMATTER_CONTRACT.md` does not exist. The useful next
   move is `OKF-CONFORMANCE-001` D1 itself, which #588, R8's surviving `artifact_type` half and
   R12's index row all wait on.
3. **#546** — now carries a measured correction (above) that **splits it**. The `_required:
   false` half of the `STY02` defect is independently shippable and does **not** wait on the
   parked subtype decision; only the `_required_when_subtype` half does. Re-title or split
   before picking it up, or the live half stays parked behind a decision it has nothing to do
   with.
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
