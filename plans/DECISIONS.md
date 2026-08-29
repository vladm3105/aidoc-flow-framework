# Decision Log

Non-obvious decisions made during the migration, with rationale, so the "why"
survives across ephemeral sessions. Newest first. Timestamps are ISO 8601 UTC.

Decisions that affect the **shared spec** graduate into the spec's own register,
`framework/governance/DECISIONS.md` (established by CHG-D2). D-0020 (CHG-D1) is
graduated there as **GD-01**; D-0013 and D-0019 are listed there as pending
graduation.

---

## D-0081 — Both secret-scanning knobs are to be ON; the REST API silently refuses, so it is a UI change

**Date:** 2026-08-29 · **Issue:** #467 · **Decider:** founder (in session)

**Decision: enable `secret_scanning_non_provider_patterns` and
`secret_scanning_validity_checks`.** #467 framed this as a posture choice nobody had made
explicitly rather than a defect, and the choice is now made.

**It could not be executed from here, and the failure mode is worth recording.** A
`PATCH /repos/{owner}/{repo}` carrying either knob returns **`200` with the repository object
and the values unchanged** — no error, no warning, no `message` field. Verified by a fresh
`GET` after each attempt, not by trusting the response. Both bracket-style `-f` parameters and a
proper nested JSON body behave identically, so it is not a request-shape problem.

The token carries `repo` scope and `permissions.admin: true` on the repository, so this is a
feature-availability limit rather than an authorisation error — but GitHub reports it as
success either way. **The change has to be made in Settings → Code security.**

*This is the `--body -` lesson in a different API.* A write that returns 200 and does nothing is
indistinguishable from a write that worked, unless you read the artifact back. Anyone scripting
repository-settings changes should assume the same and verify with a separate `GET`.

**Fleet note, measured while diagnosing:** the two keys are *present and disabled* on
`aidoc-flow-framework` and `aidoc-flow-ci`, and **absent entirely** from the API response for
`aidoc-flow-operations` and `aidoc-flow`. So the setting's availability is not uniform across
the workspace, and a fleet-wide posture claim cannot be made from one repository's response.

**Consequence.** `SECURITY.md` now states both knobs, what each being off actually costs, and
why the in-repo scanners (`detect-secrets` + `detect-private-key` as required hooks, and
`secret-scan.yml` over full history) make this a *narrowing* rather than an absence. #467 stays
open until the UI toggle is made; it is no longer blocked on a decision, only on a click.

## D-0078 — Untagged spec versions are corrected forward in the next real release, never by rewriting a published record

**Date:** 2026-08-28 · **Issue:** #558 · **Decider:** founder (in session)

*Numbering note: `D-0077` is reserved on branch `docs/a2-discard-d0077` (commit `3a26050b`)
and is not yet merged. The gap is deliberate, recorded here rather than only in the handoff,
which is rewritten wholesale each merge.*

**The state.** `framework/VERSION` moved `0.41.3 → 0.43.0` in one commit. Spec `0.42.0` was
**never a value of the file**, yet `CHANGELOG.md` documents a `0.41.3 → 0.42.0` release and GD-14
is ratified against it. `0.43.0` was real but never tagged. Latest tag: `framework/v0.41.3`.

**Decision — option 3 of the three offered on #558.** Tag neither retroactively. The next real
release carries all three and states the history in its notes. No published CHANGELOG entry is
edited.

**Why not the alternatives.** Tagging `0.42.0` retroactively would put a tag on a commit whose
`VERSION` file reads `0.41.3` — accurate to the changelog, false to the tree. Editing the
published `0.42.0` entry rewrites shipped history, which the same founder had already rejected on
`TEMPLATE-COMPLETENESS-001` ("correct forward inside the new entry; do not rewrite the released
`0.41.3` entry"). This decision applies that precedent one release on.

**What executed it.** `INSTANCE-FORMAT-SSOT-001` — the `0.44.0` CHANGELOG entry carries the
provenance paragraph; `GD-17` states its own SemVer pair explicitly, which GD-15 and GD-16 both
omitted. `framework/v0.44.0` is the first framework tag since `framework/v0.41.3`.

**Standing consequence.** `GATE-SPEC` has **no release step** — E001..E008 are all diff-local, so
nothing checks that a superseded version was ever published. That gap is what produced the phantom
and is not closed by this decision.

---

## D-0076 — A line-local carrier beats a document-scoped coverage primitive, and the carrier must land before the rule

**2026-08-26.** From the Layer-8 review (IPLAN-LAYER-REVIEW-001) and its three plan-review cycles.

**The finding.** Element-level coverage stops at TDD: `REALIZING_LAYERS` has no IPLAN key, so nothing asks whether a test case reached an implementation plan. Measured on the corpus: 7 of 35 `TDD-01` elements are cited by `IPLAN-01` in the trace graph, and the audit returned PASS at 100/100 (issue #543).

**Three design attempts were killed by independent review, each for the same class of reason**, and the sequence is the lesson:

1. A `COV04` built on `_element_realizing_citers` — refuted because that primitive returns citer *documents*, so one traceability line listing 35 tokens silences it. `ACC01`'s own source says this explicitly and refuses to reuse it.
2. A top-level `coverage_map:` section as the carrier — refuted because a section header is a **block** marker: no citation shares its line, so a line-local matcher counts nothing.
3. The same field nested in `file_manifest.files[]` — accepted, because `template_sections()` reads only top-level keys, so it reddens no golden, needs no subtype marker, and moves no section count.

**The transferable rule:** when a check must bind a citation to *something*, ask what shares the citation's **line**. `bdd_scenario:`/`bdd_ref:` work because the key's *value* is the tag. A path, a section header, or a table caption does not.

**Sequencing:** the rule cannot be specified against a field that does not exist, so the carrier (GD-16) ships first and `COV04` follows. A prerequisite linter defect had to precede both — a quoted tag was silently dropped from the edge graph (issue #542) — which was found only by executing the regex rather than reading it.

**Counting the passes.** Findings ran 5 → 7 → 5 across the first plan and 6 → 6 → 5 across its successor. Growth twice forced a scope cut rather than another fold, and both cuts were right: the second split a six-file linter fix out of a ~100-file spec change, because `spec_gate` fires only on `framework/` paths.

---

---

## D-0075 — Re-measurement of gh api 404 behavior supersedes D-0071 §8 failure-text claim

**2026-08-16.** Re-measurement from PIN-CURRENCY-NO-READER investigation (PR 3 review, issue #477).

A re-measurement on 2026-07-30 showed that `gh api …/contents/<missing> --jq '.name'` puts the full 404 JSON error payload on stdout/stderr and does **not** emit the bare string `null` (as claimed in D-0071 §8). A guard asserting `[ "$res" != "null" ]` against missing files reads a 404 error response as present.
The core lesson of D-0071 §8 stands unchanged: **test for a path's existence on disk, and never truth-test a jq scalar that can be absent or return an error envelope**.

---

## D-0074 — Ship a safety fix quieter than the behaviour it replaces, and make the bypass it needs opt-in and disclosed

**2026-08-02.** Decisions from `PLUGIN-PREPROD-001`
(`plans/PLUGIN-PREPROD-001-PLAN.md`), shipped across PRs
[#410](https://github.com/vladm3105/aidoc-flow-framework/pull/410),
[#413](https://github.com/vladm3105/aidoc-flow-framework/pull/413),
[#415](https://github.com/vladm3105/aidoc-flow-framework/pull/415),
[#418](https://github.com/vladm3105/aidoc-flow-framework/pull/418) and PR 5, and
recorded here at stage 5d because the two choices below are **policy embedded in
shipped code** — the class `plans/DECISIONS.md` exists to authorize. Both cross
PR boundaries, which is why neither was filed in the PR that implemented it.
**Supersedes nothing.**

**1. The permission-model bypass stays available, but opt-in and disclosed —
rather than removed.** Nine autopilot skills mandated
`--dangerously-skip-permissions` on the child sessions they spawn, and no shipped
file said so. Three options were on the table: delete the bypass (breaks
unattended cascades, which are the feature), keep it silent (the status quo, and
indefensible for a marketplace plugin a stranger installs), or gate it. Gating
won: `tools/saga_driver.py` defaults `allow_skip_permissions` to `False`
(`:261`), appends the flag only when explicitly set (`:569-570`), and
`platforms/claude-code-plugin/README.md:33-44` discloses what the flag does
before anyone installs.

**The reasoning that makes this a decision and not an implementation detail:**
the safe default is the one that *cannot* silently widen a stranger's trust
boundary, even though it is the default that makes the headline feature
(hands-off cascade) require an explicit argument. We accepted a worse
out-of-the-box demo for a defensible install.

⚠️ **The invariant IS guarded — but not by the gate whose name suggests it, and
not everywhere.** Stating this precisely, because the imprecise version ("the
invariant is no longer measured") is false and was nearly recorded here:

- **Covered:** conformance asserts the property — `test_bypass_absent_by_default`
  and `test_flag_defaults_off` (`tests/conformance/test_saga_driver_recovery.py:88`,
  `:114`) prove the driver ships the bypass off, and
  `test_driver_invocation_passes_the_permission_flag`
  (`tests/conformance/platforms/test_autopilot_saga_parity.py:105`) pins which
  skills opt in.
- **Not covered:** the *release* gate
  (`tests/release/test_marketplace_gate.py:42`) greps `skills/**/SKILL.md` for the
  literal `--dangerously-skip-permissions`. PR 3 moved the mechanism behind
  `--allow-skip-permissions`, which that string does not match — so the gate still
  runs, still forbids the **old** spelling, and no longer measures the **live**
  one. And `skill_dirs()` scans `skills/` only, so a `commands/` or `agents/`
  surface enabling a bypass is outside both.

Tracked as `PREPROD-B2-GATE-SCOPE`, whose fix is to assert the *property* rather
than a spelling. **The lesson worth more than the finding: a gate that greps a
literal stops measuring the moment the implementation is renamed, and it keeps
passing — so a green gate named for an invariant is not evidence the invariant
holds.**

**2. A hook that used to always speak now defaults to nudge-only, and that is a
deliberate regression in visibility.** The review hook behaved unconditionally as
`verbose`; the documented `review_hook` enum (`on`/`off`/`verbose`) was unwired
entirely. Wiring it meant choosing which value becomes the default, and the
documented default was `on` — quieter than the shipped behaviour. We honoured the
**documentation** over the **behaviour**, so existing users lose output they had.

Rationale: the hook fires on every file edit, and the same PR gated it on project
adoption (`PREPROD-H1`) precisely because it was emitting findings in repos that
never adopted the framework. A hook that is both always-on and always-verbose is
the shape that gets uninstalled. Recovery is one line —
`review_hook: "verbose"` in `.claude/aidoc-flow.config.yaml` — and it is
documented, which is the condition that made the regression acceptable.

**3. Where a fix had a documentation option, we took it only when the mechanical
half was separately tracked.** `PREPROD-L7` (a shipped `code-reviewer` agent can
collide with a consumer's own) allowed either a rename or documenting the
collision. Documentation shipped. That is defensible **only** because the live
half — every dispatch reference the plugin ships is a *bare* name, and a bare
name resolves by scope precedence where a plugin ranks lowest of five — is
carried by `PREPROD-L7-BARE-DISPATCH`
([#417](https://github.com/vladm3105/aidoc-flow-framework/issues/417)). Closing
L7 on documentation without that successor entry would have been closing a
partial finding. **The general rule: a documentation-only closure needs a named
owner for the mechanism, or it is not a closure.**

**4. What was NOT decided here.** The `claude-code-plugin/v0.25.0` tag and the
public GitHub Release (finding **M6**) are outward-facing acts that remain
founder-gated; the version cut in PR 5c is not a release. `PREPROD-M6` stays open
under `## Open` for exactly that reason, and it is the only member of the 23-item
batch that does.

⚠️ **§4 superseded 2026-08-02 — the gate opened, on the same day this was
written.** The founder authorized the cut. `claude-code-plugin/v0.25.0` is cut
(annotated → `e6c6539d`, on the remote) and the GitHub Release is published as a
pre-release, matching `v0.18.0`'s tier since the plugin is a declared pre-1.0
preview — closing **M6**, so all 23 findings are now closed. `PREPROD-M6` moved
to `## Closed` in `plans/FRAMEWORK-TODO.md` (PR #429). §4's present-tense claims
— that the tag and Release "remain founder-gated" and that `PREPROD-M6` "stays
open" — are therefore history, not live state; they are left unedited because
this log is append-only. **§§1–3 are unaffected, and the decision §4 records
still stands:** a tag cut and a public Release are outward-facing acts outside
the AI auto-merge default. What changed is that the approval was given, not the
rule that it was needed.

---

## D-0073 — Read the run that already ran; and a reader for a warning-only signal must itself fail loudly

**2026-07-31.** Decisions from `PIN-CURRENCY-NO-READER`
(`plans/PIN-CURRENCY-READER-PLAN.md`), shipped in PRs `#392` and `#394` and
closed out here. **Extends D-0071 §7; supersedes nothing.** D-0071 established
that the pin-currency *check* runs and is correct; this one is about what
happens to its output.

**1. The run log is not the preferred input surface — it is the only one that
carries the signal.** Four candidates were measured, and three lose it
structurally:

| Candidate | Verdict |
| --- | --- |
| Reusable job `outputs:` | does not exist — canon's reusable declares `inputs:` only, so a caller receives nothing |
| `$GITHUB_STEP_SUMMARY` | never written — no such call in `check-standards-drift.sh` **nor in the reusable that invokes it** |
| Check-run annotations API | truncates. Check-run `89950624082` emitted **22** `##[warning]` lines; the API returned **10 warnings** — the cap is **per annotation level**, so the response `length` is 11, one `notice` included — keeping the earliest. **None** of the ten `pin-currency:` lines survived, because they are emitted at the script's tail. Re-measure with `group_by(.annotation_level)`, never bare `length`, or this reads as off-by-one and gets discarded |
| The run **log** | complete: all ten stale-pin lines plus the tail count |

**That measurement is dated to `ci/v2.14.0`,** the canon version run
`30257877863` actually executed — not the `v2.16.0` then checked out. `v2.16.0`
emits *more* (`emit_coverage` shipped in `v2.15.0`), so the conclusion holds a
fortiori; the figure `22` does not travel. Two further surfaces a later reader
will think of — run **artifacts** and the check-run's own `output.summary` /
`output.text`, a different endpoint from annotations — are empty for the same
reason as rows 1 and 2: the reusable writes nothing.

So a parser of a downloaded log is not a workaround for missing tooling. It is
the design the available surfaces permit, and the upstream half of this plan
asks canon to change that.

**2. Give the existing output a reader; do not add a second invocation.** The
originating TODO entry proposed a job that *runs* `check-pin-currency.sh`. Be
precise about what that is and is not: it would have been a second **invocation**
of canon's one implementation, not a rival implementation — so the objection is
not "two definitions of stale could disagree". It is that a second invocation
needs its own fetch, its own pin resolution and its own schedule, and reports on
a moment other than the one the weekly audit already reported on.

**The coupling is relocated, not removed, and the next reader must know which
one this repo now owns.** `scripts/read-pin-currency-log.sh` matches **six**
literal canon log strings (`:79`, `:82`, `:86`, `:100`, `:104`, `:105`, `:133`).
Canon's warning-only script publishes no output-format contract, so its *message
text* is now a de-facto interface for this repo. That is a deliberate trade —
a message-format dependency that fails visibly (§3) in place of a duplicated
detector that would fail silently by drifting — but it is a real dependency, and
the upstream ask in §8 is partly a request to replace it with a structured one.

**3. The reader fails non-zero rather than reporting a false `clean` —
which is a narrower claim than "fails loudly", and the difference is the
residual risk.** `check-pin-currency.sh:10` declares itself
`WARNING-ONLY, NEVER BLOCKS`, correct for a detector that must not gate merges,
and precisely why nothing read it for two days. A reader inherits no such
constraint: a truncated log, an absent `check-standards-drift:` marker, or an
unparseable verdict exits **non-zero**. A warning-only reader of a warning-only
signal is two layers of silence.

⚠️ **But "loud" here means non-zero, not *heard*.** `pin-currency-reader.yml`
feeds no required context and sits on no PR path, so a red run is a red mark in
the Actions tab of a workflow nobody watches — the same invisibility this reader
exists to remove, one level up. The workflow says so itself for the
download-retry case (`:104-106`); the general form belongs here. **Named open
risk, not a solved problem**, with one concrete instance already in the merged
code: `:67`'s `if: … workflow_run.conclusion == 'success'` means an upstream
`standards-drift` **failure skips the reader and reports green**, so the pin
verdict goes unread exactly when something else has already gone wrong. Giving
the reader its own reader is the obvious next iteration and is deliberately not
in this plan.

**4. A malformed `canon` token is a hard failure, never a fallback to `clean`.**
If canon's `curl` of `main`'s `VERSION` returns an error page instead of
failing, `ver_cmp` compares non-numeric fields, every comparison falls through
to equal, and the script prints `all pins current ✅`. A parser that trusted
that string would **close** the tracking issue on a transient. So `clean`
requires a token matching `^ci/v[0-9]+\.[0-9]+\.[0-9]+$`, and anything else
exits non-zero. This is the difference between parsing a verdict and trusting
one.

**5. Reopen the same issue; do not create on every stale.** The stale → clean →
stale cycle recurs *per canon release* — the drift script resolves canon from
`main`'s `VERSION`, so the moment canon tags a new version every caller here
reads stale until re-pinned. Unguarded, create-on-stale would produce one issue
**per weekly run while stale**, not one per release; and even guarded by "no
*open* issue", a closed one plus a recurring condition still yields a fresh
issue every cycle. So the exact title is the idempotence key, and a closed issue
is reopened rather than duplicated.

**6. The logic left the YAML because nothing end-to-end can run on the PR that
introduces it.** `workflow_run` and `workflow_dispatch` both require the file on
the default branch. Extraction into two `scripts/` entry points is what makes
the load-bearing halves testable before merge — 18 unit tests over five
checked-in fixtures at the time of writing (`grep -c 'def test_'
tests/unit/test_pin_currency_reader.py`; the figure will drift, the command will
not), registered into conformance via `tests/conformance/test_repo_scripts.py`
because `tests/unit/` is reached by no hook and no workflow. An earlier draft
extracted only the parser and left the branchier reconcile inline, which was the
wrong half to trust.

**7. `cancel-in-progress: false` under a named group is serialization, and the
rationale must say so.** It stops a `workflow_run` and a concurrent
`workflow_dispatch` from both finding no open issue and creating duplicates.
The reasoning is recorded in the workflow file itself, and must **not** be
written as "nothing to cancel, so nothing to fix" — that is verbatim the
argument this repo uses to justify carrying **no** `concurrency:` block at all,
so a future sweep reading it would delete the block and reintroduce the race.
This is a fourth shape in the repo's concurrency inventory, distinct from the
`#329` allowlist, a bare `true`, and an absent block.

**8. The upstream ask is not politeness — the audit on *canon's own* side has no
reader either.** `standards-drift-self.yml` runs a **fleet** pin audit against
this repo every Monday (`cron: '0 9 * * 1'`) and discards the verdict with
`|| true` (`:88`). **That is the measured domain: canon's fleet job and this
repo's caller.** The stronger form — *no* pin audit anywhere in the workspace
has a reader — is plausible and unmeasured; do not repeat it without the census,
since this repo has twice inverted a blast-radius figure by asserting one
(`CLAUDE.md` § "Durable traps"). Filed as
[aidoc-flow-ci#351](https://github.com/vladm3105/aidoc-flow-ci/issues/351),
carrying five measured defects: the annotation cap, the missing step summary,
`strict` being unable to fire for stale pins, a SHA-pinned caller being
invisible to the in-repo path while the fleet path handles it (two paths in one
script disagreeing), and the unvalidated canon token of §4.

**Verified live — and the verification was not clean, which is the point of
doing it.** Against `#392`'s merged code, issue
[#393](https://github.com/vladm3105/aidoc-flow-framework/issues/393) was created
(V10), edited in place with no duplicate (V11), reopened after a manual close
(V12), and a reader run appeared with `event=workflow_run` (V14) — off a
**dispatched** upstream; the `schedule` leg is V15. V13, the label fallback, was
satisfied by the V4 stub rather than live. The issue also **closed when clean** —
which the plan had deliberately placed *outside* the gate (`:465`, "a live
`clean` check is deliberately absent"), so that is a bonus observation, not a
gate item. Every transition passed,
*and* the close comment published with literal backslashes, a defect only a real
published artifact could show; fixed in `#394` and re-confirmed after it. **A
green transition is not a correct artifact — read what you published.**
V15 was never a merge gate and remains unconfirmed until the first Monday run.

---

## D-0072 — Pause a pilot that cannot pass its own gate; and weight a failure census before naming a root cause

**2026-07-30.** Decisions from PR `#397`, which set `kill_switch: true` on the
`doc-maintainer` caller adopted in `#382`. **Supersedes the diagnosis recorded in
`#396`** (see point 2); supersedes nothing else.

**1. Pause, rather than narrow the config or un-adopt.** The caller was red on
23 of 47 runs across four independent upstream defects. `kill_switch: true` makes
canon exit cleanly before any LLM call (`doc-maintainer.yml:340-345`), so the
workflow is green at zero cost while the caller, its config and its conventions
stay in place — resume is a one-line flip. Un-adopting would have discarded the
28/28 canon manifest parity `#382` established, and narrowing the config could
not have worked: `max_edits_per_pr: 1` and an empty `low_risk_paths` between them
address 12 of the 23 failures and leave the rest. **The reason to pause is not
that it was red — it is that the pilot could not produce the evidence it exists
to produce.** A dry-run pilot's output is dry-run cycles carrying coherent
proposals, and `aidoc-flow-ci#352` means no plan containing a low-risk edit can
ever complete one. Running it therefore costs LLM calls and CI noise and returns
nothing.

⚠️ **The bar here is self-imposed, and earlier framing overstated its
authority.** `#382` and `#397` both cite IPLAN-0025 §3 P4 ("≥5 dry-run cycles…")
as *the* graduation gate for this caller. Read at source, P4 is written against
the **operations** repo as the sole pilot consumer, and §6 puts sibling-consumer
onboarding explicitly out of scope — *"each consumer onboards at its own pace
post-graduation."* No plan document binds this repo to P4's numbers. It remains a
sensible bar to hold ourselves to; it is not a requirement we are failing.

**2. The prior diagnosis was wrong, and the error was structural.** `#396`
recorded this repo's half of the bug as five paths in
`auto_merge.high_risk_paths` missing from `allowed_paths`, to be fixed by
aligning the lists. That fix would have changed nothing. `planner.py:187` rejects
a non-allowlisted path *before* classification is reached; `planner.py:197`
already treats anything not low-risk as high-risk; and `high_risk_paths` is never
shown to the model and never widens the allowlist. The five entries are inert
defence-in-depth and caused **none** of the 23 failures. They are now documented
as deliberate in the config itself, because the next reader will otherwise
re-derive the same wrong conclusion from the same evidence.

The misreading was not carelessness — it was **manufactured by canon's error
message**. `duplicate or non-allowlisted plan path: <path>` covers two conditions
in one string, and the single most common failure (9 of 23) names
`plans/HANDOFF.md`, which *is* allowlisted. An allowlist-shaped message about an
allowlisted path reads unambiguously as a config mismatch. **When a message names
a condition, verify the named artifact actually violates it before acting.**

**3. Census before root cause; a sample will mis-weight it.** The first pass here
sampled failures and named `#352` as "the blocker", then wrote that framing into
three files. A full census over all 23 failures put `#352` at 3 and `#353` at 15.
Both statements are true — `#352` is the *graduation* blocker because it is the
terminal gate that can never pass, while `#353` is the dominant *observed*
failure — but conflating them produced a **resume condition that would have
returned a majority-red pilot**, since it named `#352` alone. The corrected
condition requires `#352` **and** `#353`. **A root cause is a claim about a
distribution; derive the distribution first.**

**4. Report a guard that is working when its blast radius is wrong.** Two
failures were apply's *"deleted/replaced more than 30 % of README.md"* guard. The
guard is correct and should not be relaxed — but like the planner's, it aborts
the whole run instead of dropping the entry. That is the same defect as `#353`,
so it was added there as evidence rather than filed as a fourth issue.
**Correct-but-over-broad enforcement is still a defect worth reporting**, and it
belongs on the issue that already argues the general shape.

---

## D-0071 — Adoption is a separate dimension from pinning; and an asserted absence is the cheapest defect to file and the hardest to verify

**2026-07-29.** Decisions from CANON-PARITY-001 (PR `#378`), which adopted the
four `aidoc-flow-ci` surfaces this repo had never called and converted `codeql`
from a hand-rolled workflow into a canon caller. **Extends D-0070; supersedes
nothing.** D-0070's rule — *a canon bump is a migration, not a dependency
update* — is about caller **bodies**; this one is about caller **existence**.

**1. A green pin audit says nothing about adoption.** `check-pin-currency.sh`
and `check-drift.sh` both iterate over callers **that exist**. An absent surface
is invisible to both, so this repo could report "all pins current ✅" while
calling ten of canon's surfaces and ignoring four. The census that finds them is
canon's `install/templates/manifest.json`, walked against the working tree.
**Corollary:** run that walk when the canon minor moves, not just the re-pin.

**2. `#373` was a symptom, and fixing it directly would have been the wrong
repair.** The issue asked to SHA-pin `github/codeql-action` off the floating
`@v4`. Editing the local workflow's `uses:` lines would have closed it and left
the actual defect — a hand-rolled workflow where canon ships a reusable —
in place, to drift again at the next action release. Adopting the caller fixed
it upstream-of-the-symptom: canon already pins `e4fba868` (v4.37.3). **Before
fixing a defect in a hand-rolled surface, check whether canon owns that surface.**

**3. Byte-exactness is the default; each divergence pays for itself in a
comment.** Three of five adoptions landed byte-exact (`dep-scan`,
`sast-scan` modulo one label, `trivy-scan`), adding zero drift. Two diverge and
say why in-file, per `check-drift.sh`'s own "intentional divergence" resolution:
`codeql` (the `languages` input — which is *why* canon marks it
`safe_to_replace: false`) and `markdown-lint` (globs + a permanent
`fail-on-findings: false`).

**4. `fail-on-findings: false` on `markdown-lint` is a design position, not a
debt rollout.** The blocking markdown gate here is the `markdownlint-cli`
pre-commit hook, running in CI under the required `Lint / format / security
hooks` context. Canon's caller runs `markdownlint-cli2` — a different engine at
a different rev — over the same files. Two engines may disagree on rule
defaults; the advisory one must never be able to block a merge. So it stays
`false` permanently, and the graduation path canon's header recommends does not
apply.

**5. Scope a lint adopted into an existing corpus by measurement, and check
whether a "fix" is even permitted.** Canon's bare `**/*.md` reports **260 issues
in 78 files** here — all under `legacy/`, `framework/`,
`platforms/claude-code-plugin/framework/`, Hermes vendored content, and `.aidoc`
cascade output. Those are not merely unwanted: `framework/` is GATE-SPEC-governed
so a style edit **trips the gate**, and the vendored plugin copy is a generated
byte-identical mirror (D-0022) whose drift guard a fix **breaks**. Scoped to the
exclusion set `.pre-commit-config.yaml` had already justified: **447 files, 0
issues**. An advisory check that points at 260 unfixable findings trains readers
to ignore it.

**6. `report-only` protects the verdict, not the toolchain — and shipping it is
how you learn that.** `sast-scan` went red on first run with
`fail-on-findings: false` set: semgrep installs into a `python3 -m venv` and the
`aidoc-flow-runner` image ships no Python, so it died at *"ensurepip is not
available"* before any findings logic. The check name (`sast-scan FAILURE`) named
the wrong cause — it reads as "semgrep found something". Overridden to
`ubuntu-latest` locally, filed upstream as
[aidoc-flow-ci#349](https://github.com/vladm3105/aidoc-flow-ci/issues/349).
`dep-scan` and `trivy-scan` share the pool and pass, because they `curl` static
binaries. **A report-only flag is not evidence a new caller cannot fail.**

**7. An asserted absence needs a log, not an inference — this one cost a wrong
entry in two documents.** `NO-PIN-CURRENCY-CHECK` claimed "this repo runs
`check-pin-currency.sh` nowhere," reasoned from the symptom that a mixed-pin
state survived two days. It was false: canon's `check-standards-drift.sh` tail
(`:499-515`) invokes it on every weekly `standards-drift` run, and it fired on
2026-07-27 naming all ten stale pins **and** the `--repin` remedy. One
`gh run view --log | grep pin-currency` falsified it. The real defect is that a
warning-only annotation on a weekly scheduled job has **no reader** — a
different fix, since adding the proposed periodic job would have duplicated a
check that was already running and already correct. Restated in
`plans/FRAMEWORK-TODO.md` as `PIN-CURRENCY-NO-READER`. **Verify an absence
against a run log or a grep before writing it down; a wrong cause, once
recorded, is re-read as fact by every later session** — the same failure mode
D-0066 recorded for the nine-day `ai-review` outage.

**8. A manifest presence check is case-sensitive, and `--jq` on a 404 lies.**
Two false readings inside one session. The manifest lists
`.github/pull_request_template.md`; this repo carries the equally-valid
`.github/PULL_REQUEST_TEMPLATE.md`, which reads as absent on a case-sensitive
filesystem — caught only because `pre-commit`'s case-conflict hook rejected the
duplicate. And `gh api …/contents/<missing> --jq '.name'` emits the string
`null`, which a `[ -n "$n" ]` test reads as **present**: that turned "no sibling
repo adopts `sast-scan`" into "all seven do" until re-checked by listing the
directory. **Test for a path's existence on disk, and never truth-test a jq
scalar that can be `null`.**

---

## D-0070 — A re-pin is not a migration; and an exemption from a required-context rule is a snapshot, not a property

**2026-07-29.** Decisions from executing CI-CANON-V2.16-001
(`plans/CI-CANON-V2.16-MIGRATION-PLAN.md`), which took all eleven
`aidoc-flow-ci` call sites from a mixed `ci/v2.14.0` / `ci/v2.15.0` state to
`ci/v2.16.0`.

**Supersession scope.** This **supersedes D-0066 in one part only** — its
`@ci/v2.14.0` pin position (CI-CANON-V2-001, "Target `ci/v2.14.0`", shipped in
PRs `#334`/`#335`). Everything else in D-0066 is **carried forward unchanged**, in
particular its second half — *a shared trust config makes a partial fleet
migration a breaking change* — which is a standing rule about fleet
coordination, not a statement about any one tag, and its diagnosis of the
nine-day `ai-review` outage. D-0066 is superseded **in scope**, not retired.

One exception to "unchanged": D-0066's gitleaks bullet observes that "canon's own
header comment still says `dir`". That was true at `ci/v2.14.0` and is **not** at
`ci/v2.16.0`, which documents the CI-0016 scope change (upstream `aidoc-flow-ci`
issue 307, closed 2026-07-26). The bullet's *rule* — a header comment is not the
contract, so validate against what the job runs — stands; only that one
observation is spent.

- **Dependabot cannot deliver a caller-body change, so a pin bump is never the
  whole migration.** It rewrites `uses:` lines and nothing else. Two of the four
  changes in this PR live in caller bodies (`pre-commit.yml`'s concurrency
  allowlist, `audit-trail.yml`'s `labeled, unlabeled` triggers) and a third class
  — comments the bump *falsifies* — is invisible to it entirely. The mixed-pin
  state itself was Dependabot residue: PR #369 bumped one caller by hand and the
  group PR #370 carried five reusables, leaving four behind. **Treat a canon bump
  as a migration with a plan, not as a dependency update.**

- **`--repin`, never `--update`.** `install.sh --update` replaces the whole body
  of all sixteen `safe_to_replace` surfaces and would clobber every local
  customization this repo depends on — `ai-review`'s dual self-hosted
  `runner_labels_*` plus `litellm_allow_insecure_http: true`, `secret-scan`'s
  `config-path: .gitleaks.toml` (without which the scan reports 27 synthetic
  findings and goes red), `docs-sync`'s `pull-requests: write`, `links`'s
  two-job split. The four body changes were applied by hand, per file, quoted
  from canon. Canon's own guide says default to `--repin`.

- **The #329 allowlist is scoped by *context*, not by ownership.** `conformance.yml`
  and `acceptance.yml` call no canon reusable, so no pin moved in them — but both
  feed required contexts and both carried `cancel-in-progress: true` under an
  untyped `pull_request` trigger, which is the same defect `pre-commit.yml` had.
  A cancelled required check is not success; it is retained alongside any later
  success from a separate run, leaving the PR `--admin`-only. Shipping the fix
  for one of three affected required contexts would have been worse than the
  scope creep.

- **Seven local workflows still carry the shape and are exempt only because they
  are not required — that exemption is a snapshot, not a property.** `codeql`,
  `chg-gate`, `doc-review`, `hermes`, `plugin`, `labeler` and `links` all carry
  `cancel-in-progress: true`. `acceptance` was exempt by exactly that reasoning,
  and defended by a comment arguing the cancellation was safe here, until
  2026-07-27 made it the sixth required context and turned the comment into a
  defect. **Any future change that makes one of these seven a required context
  must take the allowlist in the same PR.**

- **B2 makes the escape hatch fire; it does not make a red check go green.** The
  `skip-audit-trail` override is two-signal (the label **plus** a commit-body
  marker), and per §23.1 a label event starts a *separate* run whose check-run is
  retained alongside the earlier one with the rollup keeping the worst. So the
  benefit is precisely that the override becomes usable on the next push instead
  of being unreachable — this repo had already hit the unreachable case (D-0065).
  B2 rests on an assumption that is now **measured, not assumed** — scratch PR
  #376, verification #8, run before this plan was marked Completed. **A job
  skipped by `if:` does not degrade a required context that already succeeded at
  that SHA**: `skipped` check-runs for `call / verify` and `call / ai-review`
  (both required) landed alongside their earlier successes and the PR stayed
  `CLEAN`. **And check-runs are retained alongside each other with the rollup
  keeping the worst**: at another SHA, a `failure` and a later `success` for
  `call / verify` coexisted and the PR read `BLOCKED`. The second result is what
  makes the first safe rather than merely observed — labelling cannot green a red
  required check. **B2 is safe as shipped.**

  **Three precision notes, because this is the kind of table that gets cited
  later.** (1) `call / trust` also skipped, and an earlier draft counted it as a
  third required context — **it is not required**; the required set is
  `Framework + platform conformance`, `call / composition`, `call / Lint /
  format / security hooks`, `call / ai-review`, `call / verify`, `Acceptance tier
  (deterministic)`. (2) The measurement does **not** establish the general
  "skipped ⇒ success" claim, because every skip observed landed beside an
  existing success; the untested case is a required context whose *only* run at a
  SHA job-skips. B2 does not need that case — `audit-trail` always has a prior
  `pull_request` run at any SHA a label event can reach. (3) It **corroborates**
  rather than settles: [ci#330](https://github.com/vladm3105/aidoc-flow-ci/issues/330)
  closed 2026-07-27, and `ci/v2.16.0` already publishes the mechanism at
  `docs/REPO_STANDARDS.md` §23.1 — an in-place re-run *replaces* a check-run, a
  separate run *adds one alongside*. An earlier draft of this bullet said #330
  "leaves open"; it did not.

- **B2's blast radius is much narrower than the plan assumed — measured on
  PR #375, this change's own PR.** The
  plan asserted that after B2 "*every* label write in this repo (`labeler`'s path
  labels, `ai-review`'s own `ai:review-*` writes, the `skip-ai-review`
  label-cycle) starts an `audit-trail` run whose `verify` job is skipped." **It
  does not.** All four label writes on #375 (`documentation`, `ci`, `plans`,
  `ai:review-passed`) were made by `github-actions[bot]` — i.e. `GITHUB_TOKEN` —
  and a `GITHUB_TOKEN`-triggered event does not create a workflow run (the
  documented exceptions, `workflow_dispatch` and `repository_dispatch`, are not
  in play for a label write). **No `audit-trail` run on that branch was created
  by a label event** — every one came from `pull_request`. State it as provenance,
  not as a count: the count moves with the next push. So routine bot labelling
  starts nothing; only a **human** label write, or one made under an App token,
  reaches the new trigger. The second `call / ai-review` run on #375 came from
  `pull_request_review` (the reviewer App `aidoc-reviewer[bot]` submitting its
  review — a different identity from `github-actions[bot]`, which is itself the
  corroboration), not from a label.

  Two consequences. First, the earlier empirical support offered for
  skipped⇒success — "`call / ai-review` job-skips on every `ai:review-*` label
  event and PRs still merge" — **is not evidence at all**: no run is created, so
  nothing job-skips. Do not cite it. Second, that left verification #8 as the
  *only* way to settle the assumption — which is why it was reclassified from
  optional to required and run on scratch PR #376 before this plan was marked
  Completed. **It must apply the label by hand**; a bot-applied label reproduces
  nothing, and a smoke test that used one would have "passed" while measuring
  precisely zero.

- **The general fact worth keeping, independent of this migration: a
  `GITHUB_TOKEN`-triggered event creates no workflow run.** Documented exceptions
  are `workflow_dispatch` and `repository_dispatch`. This is why a workflow can
  subscribe to `labeled` and still appear never to fire — the labels it sees in
  practice are written by other workflows under `GITHUB_TOKEN`. Reason about
  label-driven CI here with that in hand, or conclude the trigger is broken when
  it is working exactly as specified.

- **A byte-exact copy is worth keeping even when the copied comment is wrong —
  file the defect upstream instead.** Canon's `pre-commit.yml` allowlist comment
  cites "a label write (audit-trail's documented `skip-audit-trail` hatch)" as a
  motivating case, but that template's `pull_request:` is **untyped**, so it never
  receives a `labeled` event; only the `reopened` half is live. The same paragraph
  ships over the same untyped trigger in six templates (`pre-commit`,
  `markdown-lint`, `secret-scan` × public/private). Correcting it locally would
  have cost the byte-exactness that verification #3's pass condition turns on, and
  `check-drift.sh` would then warn permanently *for being right*. So this repo
  keeps canon's text verbatim in `pre-commit.yml` and filed
  [ci#348](https://github.com/vladm3105/aidoc-flow-ci/issues/348). The trim WAS
  applied to `conformance.yml` and `acceptance.yml` — those are locally owned,
  have no canon counterpart, and so carry no drift cost.

- **#329 is narrowed, not closed.** GitHub cancels a *pending* run when a newer
  one queues in the same group, independently of `cancel-in-progress`. Canon does
  not claim closure and neither does this repo.

- **`.github/ai-review/config.json`'s `$schema` was bumped for currency, not
  breakage.** Nothing in CI validates against it, and neither `--repin`
  (workflows only) nor `check-pin-currency.sh` (`.github/workflows` only) would
  ever touch it — so it would have silently stayed two minors behind the
  single-tag position this migration claims. One line, kept because leaving it
  makes the claim false.

- **Cross-repo feedback filed, not recorded locally.**
  [`aidoc-flow-ci#347`](https://github.com/vladm3105/aidoc-flow-ci/issues/347) —
  `docs/UPDATE_GUIDE.md:88` states that `framework`'s ai-review caller pins
  `runner_labels_routine: '"ubuntu-latest"'`, false since PLAN-013; the live
  caller pins the self-hosted array. Blast radius is any adopter reading the
  guide's worked example for this repo.

---

## D-0069 — A defect fix does not smuggle in a strategy change; and a coverage guard needs a guard of its own

**2026-07-26.** Three decisions from executing IDCOORD-SECOND-HASH-IMPL
(`plans/IDCOORD-SECOND-HASH-IMPL-PLAN.md`, #351).

- **Keep + fix, not delete — and the question went to the founder first.**
  `tests/acceptance/_id_coordinator.py` has no product consumer, its registry is
  `{}`, and `PLUGIN-TEST-SUITE-REVIEW.md:32` **F2** had already offered "remove
  both files" as a disposition. Deleting it would have closed #351 outright and
  strictly cheaper. It was still put to the founder as the plan's step 1 rather
  than decided in-flight, because *whether the suite wants cross-layer ID-closure
  testing* is a test-strategy question, while *a second wrong implementation of a
  normative algorithm* is a defect regardless of how that question resolves.
  **Rule: a defect fix must not be the vehicle for a strategy change.** Answer:
  keep + fix. The repo now carries a module with no consumer, now correct — a cost
  stated in the plan before the work, not discovered after it.

- **The string `section_id` was documented, not "fixed."** `element_id()` returns
  `BRD.01.project_scope.<hash>`, which `LAYER_REGISTRY.yaml:216` rejects. Making
  it numeric requires a per-layer heading→ordinal table that exists nowhere in the
  repo — inventing one is a new contract, the same overreach GD-09 declined for
  TDD field extraction. The docstring now states the limitation and the numeric
  form is a deferred TODO. **Rule: when the honest fix is a new contract, say what
  the thing is instead of quietly making it look conformant.**

- **A guard that proves the guard.** The parity table's own check
  (`test_parity_cases_actually_exercise_the_transform`) asserts each case differs
  pre/post transform — but it is a property of the *table*, and it cannot see
  which transform *step* a case covers. A per-step mutation matrix found that
  **one row covers NFC**, and only while its text stays decomposed: a formatter
  precomposing the literal would drop that step's coverage to zero with every
  test still green, because the row's casefold difference alone satisfies the
  check. **Rule: for a guard over an N-step contract, verify per-step coverage by
  mutation — a per-case "is it non-trivial" check will report full coverage while
  a step has none.** This is the same masking class as the
  `test_no_inprompt_hashing.py` finding recorded in D-0068's session.

---

## D-0068 — A blocker is only a blocker once verified; and a negative-property guard finds the surfaces a manual census misses

**2026-07-26.** Three decisions from executing IDGEN-NO-GENERATOR
(`plans/IDGEN-NO-GENERATOR-PLAN.md`, #342).

- **The plan's own "founder decision required" blocker dissolved on inspection.**
  D4 claimed that instructing five layers to emit `id_state: provisional` would
  contradict the templates' `state: canonical` and "may need a spec change after
  all". It does not: `id_standard.state` is **template metadata with no code
  consumer**, while `id_state` is **produced-document frontmatter**, and the
  linter says so itself — *"the template `id_standard.state` documents the
  convention"* (`tools/sdd_doc_lint/__init__.py:558`). Different fields, different
  layers, no enforceable conflict. **Rule: verify a blocker against source before
  escalating it.** An unverified blocker in a merged plan stalls the work
  indefinitely on a decision nobody actually needs to make — the cost is the same
  as a wrong fix, and harder to notice.

- **A negative-property guard beats a manual census.** #342 counted 9 surfaces,
  corrected to 19; a live grep in this session still said 19; the real figure is
  **25**, because both passes checked one Hermes `references/` file instead of the
  tree. The nine extra were shipping *runnable* ad-hoc hash code with per-file
  normalization variants, none matching the standard. They were found the moment a
  conformance test scanned the whole surface class. **Rule: when a defect class is
  "every place that says X", write the scan first and let it enumerate — a
  hand-built census of a class is a sample, and it will be reported as a total.**

- **`--fix` was cut on measured blast radius, not on principle.** The merged plan
  scoped it in. Measured first: on the example corpus `--fix` would rewrite **all
  4** of BRD-01's §7 FR IDs and break citations in **8 downstream files**, because
  an LLM-authored ID essentially never equals its content hash. That makes it a
  corpus-wide re-cascade, not a file-local fix, and shipping it without a
  citation-update design would be a footgun. `--compute` alone fully closes the
  issue's actual complaint ("no callable generator exists"). **Rule: when a plan
  scopes in an operation over shared state, measure its blast radius before
  building it, not after.**

---

## D-0067 — Deleting a re-specification beats correcting it; and a merged plan's honest deferral is still overridable by the founder

**2026-07-26.** Three decisions from executing ELEMENT-ID-LAYER-CONTRACT-001
(`plans/ELEMENT-ID-LAYER-CONTRACT-001-PLAN.md`, issues #343/#344/#352).
Graduated into the spec register as **GD-09**.

- **When a contract has drifted into N copies, delete the copies rather than
  fix them.** Seven framework surfaces published a hash algorithm that D-0062
  had superseded. The available fixes were (a) update the stale text in each
  layer, or (b) delete it and cross-reference the authority. (b): re-stating a
  *corrected* algorithm in seven places resets the drift clock rather than
  stopping it, and the re-specification is itself the mechanism that let D-0062
  reach exactly one of eight surfaces. The general form: **the number of places
  a rule is written is the rate at which it will drift**, so a fix that leaves
  the count unchanged has not fixed the class.

- **A regression lock must iterate a hardcoded list, not a glob, when the
  population has documented exemptions.** `framework/layers/**` contains
  `*-MVP-TEMPLATE.yaml`, `*-00_index.TEMPLATE.*`, and the `06_SPEC` / `08_IPLAN`
  templates and READMEs — the two layers `ID_NAMING_STANDARDS.md` explicitly
  exempts from element IDs. A glob over templates or READMEs would have produced
  a double-digit count of spurious failures and made the guard's red state
  meaningless. The test names its six `(README.md, <TYPE>-TEMPLATE.yaml)` pairs.

- **`placeholder: "0000"` was deleted, overriding the merged plan's D4
  deferral.** The plan deferred the key to its own issue (#352) with a correct
  and honestly-recorded rationale — resolving what it *means* is a governance
  question, not a drift fix — and Part C therefore added a sixth inert copy to
  TDD for uniformity. The founder chose deletion instead. Both the deferral and
  the override were right: the plan should not have unilaterally resolved a
  governance question mid-drift-fix, and once the owner ruled, shipping the
  ruling in the same PR avoided minting a sixth copy of a key that was about to
  be removed. **Rule: a merged plan's deferral binds the implementer, not the
  founder; when it is overridden, record the deviation in the plan's progress
  log rather than silently diverging from a merged document.**

---

## D-0066 — CI canon migration: target the latest tag, not the plan's; and a shared trust config makes a partial fleet migration a breaking change

**2026-07-25.** Four decisions from executing CI-CANON-V2-001
(`plans/CI-CANON-V2-MIGRATION-PLAN.md`, PRs #334/#335).

- **Target `ci/v2.14.0`, not PLAN-009's `ci/v2.8.0`.** Upstream's fleet-cutover
  plan names `v2.8.0`, but that banner dates to 2026-07-18 and canon has since
  shipped six further minors; `v2.14.0` is the current `Latest` and the tag
  canon's own install templates reference. Re-pinning to the plan's literal
  target would have required an immediate second bump. **Rule: a plan naming a
  version target is naming it as of its writing date — re-resolve against
  `Latest` at execution time, and record the deviation rather than following the
  stale number.**

- **Where upstream plan text conflicts with upstream source, source wins.**
  PLAN-009 Phase 2's Edit F says to move only `ai-review`'s heavy *review* job
  to the self-hosted pool and keep the trust job on `ubuntu-latest`. Canon's
  actual caller template has been a **single** protected file since `ci/v2.2.0`
  (PLAN-013), setting **both** `runner_labels_routine` and
  `runner_labels_review` to the pool. PLAN-009's own superseded-target banner
  says as much; its Phase 2 body was never updated. Following the prose would
  have diverged from canon and under-sized the runner pool by half.

- **`gitleaks` scan scope changed silently at v2; verify against the command CI
  runs, not the one the docs describe.** `ci/v1.9.5` ran `gitleaks dir .`
  (working tree); `ci/v2.x` runs `gitleaks git .` (full history — 1343 commits
  here). Canon's own header comment still says `dir`. Local verification with
  `dir` passed clean and CI then failed on 33 history findings, all
  pre-migration `ucx_framework` placeholders. **Rule: when validating a CI gate
  locally, read the step body for the actual invocation; a header comment is not
  the contract.**

- **A shared trust config makes a partial fleet migration a breaking change.**
  This repo's `ai-review` had been failing `no parseable verdict — fail-closed`
  since `aidoc-flow-operations` cut over to `ci/v2.0.1` on 2026-07-16 — not, as
  `plans/HANDOFF.md` recorded, because a reviewer key lapsed. Operations rewrote
  the **shared** trust config (`trust_config_repo`, which every consumer reads by
  default) to schema v2, removing the `reviewer` field. The `v1.9.5` reusable
  resolves the engine with `jq -r '.reviewer // "codex"'`, so the absent field
  silently selected **codex**, which requires `OPENAI_API_KEY` — never held here.
  Hence `401 Unauthorized` from `api.openai.com`. **Consequence for this repo:
  its AI review gate was unpassable for ~9 days and every merge in that window
  went through `--admin`, including #335's.** The migration is the fix: the v2
  reusable reads `litellm.model` from that same config. Recorded here because
  the failure mode is not local — a config this repo does not own can break its
  gate, and the symptom (`no parseable verdict`) names neither the cause nor the
  owner.

- **`LITELLM_BASE_URL` must be the Docker-bridge address, not loopback.** The
  single-use runner executes jobs **inside a container**, so `127.0.0.1` /
  `localhost` resolves to the container itself, not the host. Set it to
  `http://172.17.0.1:4001/v1`. Verified from inside a job container: the bridge
  address answers `GET /v1/models` with **HTTP 401** (proxy alive, virtual key
  required — the correct unauthenticated response), while both loopback forms are
  unreachable. Set to loopback first, the v2 review job failed
  `litellm: proxy request failed after 3 attempts: URLError`; corrected
  2026-07-25T20:44Z and it passed on the next run. Note the LiteLLM container
  publishes **host 4001 → container 4000**, and is a *different* service from
  `llm_router-llm-router-1` (unpublished 4000/tcp, plus a separate host listener
  on `0.0.0.0:4000`) — pointing at 4000 hits the wrong service.

- **Two independent causes of `BLOCKED` were conflated; fixing `ai-review` only
  removes one.** With the migration verified (`call / ai-review` and
  `call / composition` both green on the #336 probe — composition's first success
  in ~9 days), PRs here *still* report `BLOCKED`. Cause: branch protection
  requires the status context **`Lint / format / security hooks`**, but the check
  actually reports as **`call / Lint / format / security hooks`** — the reusable-
  workflow job prefix. A context that is never reported can never be satisfied, so
  every PR is blocked no matter how green. This is the "phantom
  branch-protection context" upstream PLAN-009 flags for framework/business/
  iplanic, and it is **independent of the reviewer**: it predates the migration
  and survives it. Fixing it is a branch-protection write (🔴 founder); until then
  `--admin` remains structurally necessary here, which is precisely the condition
  that made `--admin` feel routine.

## D-0065 — CI-plumbing PRs get a CHANGELOG entry (founder call, 2026-07-25); and warning-only tooling can hide a hard failure behind a gate that never fires

**2026-07-25.** Two decisions from the open-PR triage session.

- **CI-only PRs carry a CHANGELOG entry.** #329, #331 and #332 all landed
  without one. The reasoning at the time was that CI plumbing has no
  project-visible behaviour change, so an entry would be noise. The repo's own
  `docs-sync` tooling disagreed — its `changelog_stub` op proposed a CHANGELOG
  update after those merges — and the founder ruled for the tooling. **Rule
  going forward: a PR that changes `.github/workflows/**`,
  `.github/dependabot.yml`, or CI configuration gets a `[Unreleased]` entry like
  any other change.** Rationale: the "no user-visible change" test is the wrong
  one for this repo, where CI *is* the governance surface — #329's Dependabot
  hold and #332's SHA pin are exactly the decisions a future session needs to
  find without reading git log. Retroactive entries for the three PRs were added
  in the same commit as this decision. Supersedes the inline justification in
  #329's commit body ("No CHANGELOG entry: CI plumbing, no project-visible
  behaviour change; …").
- **A gated step that has never executed is untested, not working.**
  `docs-sync` had been broken since it was added: its caller granted
  `pull-requests: read` while the dry-run comment step needs `write`. The step is
  gated on `proposed != 0`, so it never ran, and the workflow reported green for
  weeks. The same shape recurred twice more in one day — `standards-drift`
  404'ing on an annotated-tag-object pin (fixed in #329) surfaced only because
  its output was finally read, and the `skip-audit-trail` override could not be
  applied to an open PR because the caller does not listen for `labeled` events.
  **When auditing CI, treat "never observed to run" as a red flag equal to
  "observed to fail"** — check the gate conditions, not just the badge.
- **Corollary, earned the hard way in this very commit: a caller-side permission
  raise does not fix a reusable workflow.** The first draft of this change raised
  the `docs-sync` caller to `pull-requests: write` and declared the bug Fixed.
  Author-side review caught that GitHub **intersects** caller and callee
  permissions, and the callee (`aidoc-flow-ci` `docs-sync.yml@ci/v1.9.5`) declares
  `pull-requests: read` at its own workflow level — so the effective token would
  have stayed `read` and the workflow would have stayed red behind a CHANGELOG
  entry claiming otherwise. Exactly the false-green failure this decision
  documents, reproduced while documenting it. The real fix is upstream; the caller
  raise is kept as the necessary-but-insufficient half.
- **Open follow-up (not in this PR — 3-surface governance cap).** The new
  CHANGELOG rule is recorded here but contradicted where contributors will
  actually look: `CONTRIBUTING.md`'s documents-of-record matrix has no
  `.github/**` row, so a CI-only PR falls under `Trivial / … → (none)`; and
  `scripts/check-docs-updated.sh` has no `.github/*` case arm, so its
  doc-currency reminder will never fire for one. Both need updating for this rule
  to stick — otherwise it is itself a gate that never fires.

---

## D-0064 — SEED-ABSORPTION-001: three project-side decisions behind GD-08 (Part B is a regression-lock, not a template change; `realizing_layers` stays unmutated; `ACC01` is case-scoped)

**2026-07-24.** Implemented the SEED-ABSORPTION-001 plan (spec-tier record is
**GD-08** in `framework/governance/DECISIONS.md`; framework `0.37.2 → 0.38.0`,
GATE-SPEC C2). Three non-obvious build choices are recorded here so the "why"
survives:

- **Part B is a regression-lock, not a template placeholder rewrite (founder
  direction 2026-07-24).** The templated `TYPE.NN.SS.xxxx` form is *correct* in
  the layer templates and README snippets — it is the shape of a future ID.
  `ID03`/`ID01` already reject it in a produced artifact (verified empirically).
  So Part B adds only a negative fixture + conformance assertion + one
  discoverability sentence; it changes **no** `framework/layers/` template
  (V6 asserts all eight `.xxxx` placeholder counts unchanged).
- **`realizing_layers` is NOT mutated; `acceptance_layers` is additive.**
  Changing the `BDD: [SPEC, TDD]` map would break the pinned COV02 corpus
  assertion (`test_coverage_engine.py:103`) and re-grade every consumer corpus.
  `ACC01` reads a new sibling `acceptance_layers: {BDD: [TDD]}` block instead.
- **`ACC01` is case-scoped, not document-scoped.** Reusing the realization
  primitive would count a *document* citation — and `TDD-01.md:206` already cites
  all 15 scenarios on one traceability line, so a document-scoped rule could be
  satisfied by appending IDs there with no test authored. `ACC01` instead pairs a
  scenario only when a `@bdd:` citation is co-located with a TDD test-case element
  id (a §3 mapping row or §4 `bdd_ref`). Measured corpus delta: ACC01 = 16
  (same orphans as COV02 here, but robust to the traceability-block loophole,
  which the V4 fixture proves closed). T7 confirmed the 16 orphans are
  un-*designed* (one SPEC; TDD-01 scoped to the 15 SPEC-01 scenarios) — filed as
  a SPEC-coverage gap in `FRAMEWORK-TODO.md`, pinned count left at 16, no
  hand-edits per `CLAUDE.md`.

Plan + full ledger: [`plans/SEED-ABSORPTION-001-PLAN.md`](SEED-ABSORPTION-001-PLAN.md).

---

## D-0063 — HERMES-REVIEW-LOOP-001 Phase 1: opt-in bounded review→remediate→re-review loop for Hermes (`sdd_review quality_loop`) — hermes 0.10.0 → 0.11.0 (no framework change)

**2026-07-11.** Hermes's review saga was single-pass, in-process, `iteration=1`
hardcoded. This ships the first outer review loop — the initiative D-0050 named as
the gate for the deferred H-1/H-6.3 saga-parity machinery — as a **minimal,
flag-gated Phase 1** so the higher-risk resume machinery stays deferred.

**Design decisions (ratified for build):**

1. **Loop trigger = opt-in `quality_loop` boolean on `sdd_review`** (default `false`).
   Not profile-auto-enabled; the caller opts in explicitly. The profile supplies only
   the cap (`quality_loop_max_iterations`, default 3).
2. **Outer wrapper, not a state-machine change.** Each iteration is a *fresh forward
   saga run* (`run_project_review_build_saga` gains `iteration` / `quality_loop` /
   `is_final_iteration`), sidestepping the forward-only transition table
   (`SYNTHESIZED→{CLOSED}` only). The transition table and `saga.schema.json` are
   unchanged → **no `framework/VERSION` change**; Hermes stream MINOR only. (Reviewed:
   adding a `quality_loop` arg is an additive tool-schema field, not a spec/schema
   change — MINOR, not MAJOR.)
3. **Cap terminal = `PARTIAL_TIMEOUT`.** A failing gate on the *final* iteration writes
   the break-circuit terminal state (satisfying part of H-1's write-site); non-final
   failing gates remediate + re-review. A `SOFT_DEADLINE_SECONDS` (3600s) wall-clock
   bound also forces the final iteration early.
4. **Auto-remediate mode = executor-driven.** `run_remediate_fix_build` is copy-only
   (LB-2); the actual fix is a separate `run_executor(prompt=fix.report_text, …)` on
   the derived copy, mirroring the manual `sdd_remediate` drive. The re-review rebuilds
   `sections` from the remediated derived file (LB-5 — the fan-out consumes `sections`,
   not `document_path`).

**Operating constraint (accepted):** the gate needs a numeric `review_score`, produced
only on the `saga_parallel` + branch-LLM + framework-crew path. Off it the score is
`None` → `_quality_gate_passed` returns `True` → the loop closes on the first pass (a
safe single-pass degrade). Documented, not a defect. **Boundary (review-surfaced):**
`review_score` is also `None` when the crew *did* run but produced no parseable
`lens_score` (all branches omit it) or the `doc_type` has no framework crew — those also
degrade to PASS. This is **not a regression**: the pre-existing `saga_parallel` path
already returned `passed=True` unconditionally regardless of score, so the loop is no
weaker than the status quo. Distinguishing "expected `None`" (deterministic path) from
"unexpected `None`" (crew ran, scores unparseable) and treating the latter as a gate
*miss* rather than a *pass* is deferred to **Phase 2** (it needs a score-coverage floor;
treating `None` as FAIL naively would create false-failure loops for legitimately
score-less configs).

**LB-7 journal discriminator:** `deterministic_review_run_id` appends `iterN` for
`iteration > 1` only (the `iteration == 1` id stays byte-identical), so a same-clock-hour
re-review lands in a distinct journal file instead of clobbering the prior pass's audit
trail — preserving the multi-iteration audit trail (and the H-6.3 comparison input).

**What this satisfies vs. defers:** H-7 iteration-cap = shipped; H-1 `PARTIAL_TIMEOUT`
write-site = PARTIAL (loop final-gate path + SOFT_DEADLINE; general break-circuit +
G-R1 cross-invocation resume = **Phase 2**); H-6.3 (iter-N vs iter-(N-1) regression
detection) = unblocked (real iterations now exist; the comparison itself is a follow-up).

**Verification:** 565 Hermes tests + 208 conformance tests green; the default
(`quality_loop` off) path is byte-identical (17 saga tests unchanged). New:
`tests/unit/test_quality_loop.py` (9 cases) + conformance multi-iteration journal +
Hermes `test_invalid_transition_raises` mirror (`SagaTransitionInvariant`).

## D-0062 — PROVISIONAL-IDS-002 Phase 1: formalize the hash-input contract + ship `rehash --check` (the Model-2 drift verifier, `IDDRIFT01`) — framework spec 0.34.2 → 0.35.0

**2026-07-08.** Executes the ratified Model-2 direction (D-0061). Element IDs now
have a real, verifiable content-drift signal, delivered as a **minimal Phase-1
core** so the higher-risk pieces stay deferred to founder-decided later phases.

**Shipped.**

1. **Formalized the byte-exact hash-input contract** in
   `framework/governance/ID_NAMING_STANDARDS.md` (the authority): the
   **normalization transform** (NFC → casefold → strip to `[a-z0-9 ]` → collapse
   whitespace → trim → first 100 chars) and the **BRD §7 FR field-extraction
   boundary** (title between `—` and `**`; description = post-band body accumulated
   across wrapped continuation lines until a blank line / next bullet / heading /
   acceptance label). Migrated the normalization out of the BRD template (now a
   cross-ref) so there is one source.
2. **`rehash --check`** (`python -m sdd_doc_lint.rehash --check <docs>`) — recomputes
   each canonical BRD §7 FR element's hash and emits **`IDDRIFT01`** (advisory) on a
   mismatch. **Opt-in** (NOT in the default `sdd_doc_lint` pass → default gate +
   corpus lint byte-identical), **`canonical`-gated** (provisional docs exempt),
   **BRD §7 only**. Primitives (`_normalize_hash_field`, `compute_element_hash`,
   `scan_fr_content`, `rehash_check`) live in the canonical `sdd_doc_lint/__init__.py`
   (vendored byte-identical to both platform mirrors); the CLI is `rehash.py`.
3. **Fixtures/tests** — `tests/conformance/test_rehash_verifier.py` (16 tests) proves
   the transform determinism (V4), extraction bytes incl. multi-line + wrapped-band +
   colon-in-body (V4b), §7-only scope (V4c), clean/drift/provisional-exempt (V1/V2/V3),
   the 8-char collision form, and advisory severity.

**Why "verifiable on demand," not "verified."** Pass-2 independent review of the
plan caught that writing "verified for canonical docs" into the authority would
re-introduce the exact over-claim D-0061 removed: Phase 1 does **not** run the check
on the corpus (whose LLM-minted IDs would drift wholesale), so the authority says
the contract is **verifiable on demand** via the opt-in command; the corpus stays
unverified until the Phase-2 reconciliation.

**Deferred (founder-decided) — Phase 2+.** `rehash --fix` (canonicalize + citation
cascade); all-8-layer extraction; corpus reconciliation (grandfather vs.
re-canonicalize at next wholesale regen); promoting `IDDRIFT01` advisory → gate; a
Unicode-category normalization strip. See `plans/PROVISIONAL-IDS-002-PLAN.md`.

**Versioning.** New normative spec content (the formalized contract) in
`framework/governance/` trips GATE-SPEC → framework **MINOR** `0.34.2 → 0.35.0`.
`IDDRIFT01` is opt-in advisory, so the default gate is unchanged; 182 conformance
green. Both `FRAMEWORK_SPEC_VERSION` pointers auto-re-matched; plugin + Hermes
product versions unchanged.

---

## D-0061 — Framework production-readiness: scope the SHA-256 element-ID guarantee to reality (13 surfaces) + ratify GD-02…05; the ID-model decision (PROVISIONAL-IDS-002) resolved as Model 2 (stable ID + drift fingerprint)

**2026-07-07.** FRAMEWORK-PROD-READINESS-001 (framework `0.34.1 → 0.34.2`, PATCH) — the 2
framework-side items from the production-readiness audit (the plugin items shipped in #266 /
D-0060).

**(1) SHA-256 over-claim scoped to reality.** `ID_NAMING_STANDARDS.md` + 12 more vendored spec
surfaces (5 templates' `id_standard` block, 5 layer READMEs, PRD-00/SPEC-00 index templates)
promised "deterministic, byte-identical" content-hash IDs that "any tool" produces. But the
engines LLM-generate IDs (not real `SHA256(content)`) and nothing verifies them — D-0040
explicitly deferred `rehash --check` to PROVISIONAL-IDS-002. Every surface now scopes the claim:
the SHA-256 form is the **canonicalization target**, not a currently-verified property; a
produced ID is a stable opaque string, unverified until `rehash --check`. The algorithm +
`hash_algorithm: SHA256` field are unchanged (the target stands; only the *guarantee* is scoped).
The independent review caught that the first draft scoped only 6 of the 13 surfaces — leaving 7
READMEs/index-templates still over-promising would have reproduced the exact gap; all 13 are now
covered.

**(2) GD-02…05 ratified.** Flipped `Status: Proposed → Accepted` for the four graduated
governance decisions that are merged + enforced (GD-05, GD-04, GD-03, GD-02); GD-01 was already
Accepted. Executes the "ratified on merge" convention's missing flip-mechanism.

**(3) The ID-model decision (PROVISIONAL-IDS-002) — RESOLVED as Model 2.** The founder chose to
**enforce the hash and use it as a content-drift identifier** (option A over the honesty-scoping
band-aid alone). Of the two enforcement models, **Model 2 (stable ID + drift fingerprint)** was
chosen over Model 1 (strict content-addressing): the element ID is minted once and stays stable
(so downstream `@`-tag citations never break on an edit), while `rehash --check` compares
`SHA256(current content)[:4]` to the ID's embedded hash and flags a mismatch as **drift** ("this
element's content changed since its ID was minted"). Rationale: the framework's entire
traceability graph (COV01/COV02/REFGRAN01/`@`-tags) depends on stable citations — Model 1 would
shatter citations across up to 7 downstream layers on a single upstream edit; Model 2 delivers
the drift-detection value with zero citation churn and **no extra storage** (the ID's hash *is*
the mint-time fingerprint), and dovetails with the existing `id_state: provisional/canonical`
machinery (drift → mark provisional → re-canonicalize as a controlled, opt-in cascade). This
honesty-scoping is the accurate **interim**; the Model-2 build (`rehash --check` drift-detect +
`rehash --fix` re-canonicalize + corpus reconciliation) follows as the **PROVISIONAL-IDS-002**
plan, which will flip "unverified until `rehash --check`" → "verified/drift-checked by
`rehash --check`."

Doc-accuracy + governance-status only; no rule/algorithm/structure change; deterministic lint
byte-identical; 166 conformance green. Reviewed: 3 passes (Pass 2 independent caught the 7-surface
completeness gap). Spec-tier (founder-ratified).

---

## D-0060 — Plugin production-readiness batch: fix the `${CLAUDE_PLUGIN_ROOT}/../../` playbook-path-escape BLOCKER + 3 SHOULD-FIX

**2026-07-06.** PLUGIN-PROD-READINESS-001 (plugin `0.23.1 → 0.23.2`, PATCH). A 4-agent
production-readiness audit of the Claude Code plugin (spec-consistency, skills, packaging,
conformance/tooling/docs) found it clean/green on every dimension **except** one BLOCKER + 3
SHOULD-FIX.

**🔴 BLOCKER — playbook / REVIEW_TEAM path escape.** The 9 `doc-*-audit` skills resolved their
per-`(layer,lens)` playbook, and `agents/synthesizer.md` its `REVIEW_TEAM.md` scoring contract,
via `${CLAUDE_PLUGIN_ROOT}/../../framework/…`. The `/../../` climbs two levels *above* the
plugin root, but those files are vendored *inside* it at `${CLAUDE_PLUGIN_ROOT}/framework/…`.
The escaping path resolved only in the source-repo checkout by coincidence
(`platforms/claude-code-plugin/../../` = repo root); **in a distributed install it pointed
outside the plugin → every playbook/contract load failed → the weighted-crew review collapsed
to zero coverage** (each lens hitting its own `BRANCH_FAILED "playbook missing"`). Fixed by
dropping `/../../` in all 11 refs — the 500+ correct sibling refs proved the pattern. This was
a genuine release blocker: the plugin's core reviewed-authoring feature silently degraded for
every installed user.

**+ 3 SHOULD-FIX.** (1) `doc-ears` + `doc-ears-audit` still mandated percentiles for *all*
timing (3 spots) — reconciled to the D54-F04 latency-vs-non-latency model (the template fix was
template-only; this propagates it to the plugin skills). (2) Deprecated-stub removal milestone
`v0.7.0 → v1.0.0` (8 occurrences — the 8th, `docs/PARITY.md`, caught by CI ai-review; the plugin is 16 minors past 0.7.0 — chose bump over remove
to avoid rippling into the skill-count/manifest/PARITY copy). (3) A "known lint baseline" note
in the url-shortener example README (the flagship example exits lint non-zero on a tracked
`TH-RES-001` + 16 by-design `COV02`, deferred to regen) + dropped a phantom `docs/.version`
line.

**Deferred (framework-side, separate):** the SHA-256 element-ID honesty gap
(`ID_NAMING_STANDARDS.md`, gated on PROVISIONAL-IDS-002) and the GD-02…05 "Proposed → Accepted"
status flip — both `framework/` hygiene items, not plugin blockers. Reviewed: 3 passes (Pass 2
independent caught 2 load-bearing enumeration gaps — a 7th `v0.7.0` spot + a 3rd doc-ears drift
line). No `framework/` change → plugin PATCH, not spec-tier.

---

## D-0059 — H-11b: delete (not re-sync) the 5 orphaned hand-vendored `references/` framework-doc copies from the sdd-orchestrator

**2026-07-06.** H-11b (Hermes `0.7.2 → 0.7.3`, skill `2.1.1 → 2.1.2`). The
`sdd-orchestrator/references/` directory carried 5 hand-vendored copies of framework docs —
`ucx-readme.md`, `doc-governance-core.md`, `id-naming-standards.md`, `layer-registry.yaml`,
`data-consistency-report.json`. [[D-0013]] framed this as a delete-vs-resync decision.

**Decision: delete.** Grounding found them (a) **orphaned** — a whole-repo grep found no loader
referencing them (`SKILL.md` loads none; the only hits are historical plan/backlog mentions),
and (b) **stale drift-sources** — e.g. `id-naming-standards.md` was titled "SDD v3.2", 53 lines
vs the canonical 191, and described the **retired sequential-ID scheme** contradicting the
current model. Under D-0013 Hermes reads `framework/` directly with **no local sync** — which is
exactly why these copies drifted. Re-syncing would reintroduce the maintenance burden D-0013
removed and re-create a second source of truth; **deleting** removes the drift/misinformation
with zero behavioral change (nothing loaded them). 166 conformance + 511 Hermes tests green.
No `framework/` change (Hermes-platform only). Closes H-11b. Remaining H-11 follow-ups: **H-11a**
(cosmetic `v3.2` string residue in 21 non-loaded files — deferred, low value) and **H-11c**
(element-ID SHA-256 residue — framework-gated by PROVISIONAL-IDS-002; the framework templates
also still say SHA256, so Hermes cannot be fixed alone).

---

## D-0058 — Defer D54-F08 (`--skeleton` template emit) as build-on-demand — a speculative DX convenience with real hazards, not built now

**2026-07-06.** D54-F08 asked for a `--skeleton` emit that strips a template's authoring keys
(`_guidance`/`_example`/`_antipatterns`) leaving the content keys, as plugin tooling. Grounding
found no existing internal "context-strip" to reuse (the TODO's premise), and the feature is a
speculative convenience with real hazards, so per the minimal-and-realistic / no-speculative-
features convention it is **deferred (build-on-demand)**, not built.

**Reasons.** (1) **Anti-aligned with the framework's own design** — templates are deliberately
`_guidance`-dense (127 `_guidance` blocks in BRD alone) because the framework bets guidance-
dense templates author *better*; the `doc-*` skills inject the **full** template. A guidance-
stripped skeleton produces lower-quality authoring, working against that thesis. (2) **Comment-
fidelity hazard** — a YAML `safe_load`→`safe_dump` strip destroys all inline `#` enum hints and
reformats, so the skeleton would not resemble the template; faithful output needs a
`ruamel.yaml` round-trip (a new dependency). (3) **Divergence risk** — the underscore keys are
NOT uniformly strippable: `_authored_form` (the BRD FR-coverage contract COV01 depends on),
`_required_when_subtype` (IPLAN sub-type gating), and `_required` are **normative**; a naive
strip drops required structure and misleads authors, and the preserve-list must stay in sync as
templates evolve. (4) **No demand signal** — no consumer requests it.

**Revive criterion.** Build only if a consumer actually asks. The safe form is then a `tools/`
script with a **curated strip denylist** (`_guidance`/`_size_target`/`_note`/`_antipatterns`/
`_example`) that preserves the normative keys, plus a test asserting they survive — ideally
`ruamel.yaml` round-trip for comment fidelity. Tracked as DEFERRED in FRAMEWORK-TODO
`D54-F08`. This closes out the framework-core backlog sweep: the remaining P2/P3 items were
either shipped or (this one) deferred with rationale.

---

## D-0057 — EARS quantification is dimension-appropriate: latency → percentiles, non-latency → a concrete numeric bound (reconcile the template rubric to the already-correct playbooks)

**2026-07-06.** D54-F04 (framework spec `0.34.0 → 0.34.1`, PATCH). The EARS quality-attribute
rubric in `EARS-TEMPLATE.yaml` conflated "quantified" with "has latency percentiles," mandating
`p50/p95/p99` for *every* timing requirement — so a quantified **non-latency** bound (a `WITHIN
N cycles/iterations`, an event-window, a `*.count` threshold) was docked for "lacking
percentiles."

**Decision: quantification is dimension-appropriate.** A latency/response-time dimension is
quantified by percentiles (a distribution); a count/window/size dimension is quantified by a
concrete numeric value + unit. The four percentile-mandating template surfaces (scoring weight,
EARS-Ready checklist, antipattern, quality-attributes guidance + its illustration block) were
reworded to scope percentiles to **latency** and admit a concrete non-latency bound as
quantified (with a new "Non-latency bound examples" table). The **latency-percentile bar is
preserved**.

**Template-only; the playbooks were already right.** Grounding found the review lenses already
count any quantified bound (`playbooks/03_EARS/tech_lead.md`: "retry counts, and any other
quantified" bound) and the threshold vocabulary already supports non-latency categories
(`circuit.failure.count`) — so the fix is template-only (the TODO's "+ auditor playbook" leg is
unnecessary; the playbooks are the authority the template now matches) and needs **no new
syntax**.

**PATCH, no automated re-score.** Prose-only `_guidance` reconciliation to already-shipped
behavior → PATCH (precedent: ENG-PLATFORM-ADR-TIMING, BL-READY-SCORE-ADVISORY). The percentile
rubric is **LLM-auditor scoring, not a `sdd_doc_lint` rule** — verified the deterministic lint
output over the corpus is byte-identical before/after, so no gate changed. The example corpus
carries non-latency bounds (`EARS-01.md`: `RTO ≤ 30 min`, `≥ 99.9% monthly`, a visit-window)
the strict rubric would have docked; the reword intentionally un-docks them, and that
improvement lands at the next **wholesale corpus regen** ([[project-examples-regenerated-wholesale]]),
not hand-applied. Reviewed: 3 passes (Pass 2 independent caught a load-bearing verification
defect — the corpus was not latency-only and the linter can't see the rubric). Closes
FRAMEWORK-TODO `D54-F04`.

---

## D-0056 — The ID02 malformed-doc-id scan flags only digit-leading `TYPE-<n>` tokens (generalizes D-0043's `-INDEX` exemption); no version bump

**2026-07-06.** LINT-DOCID-HEADER-FALSE-POSITIVE. The `sdd_doc_lint` ID02 check
(`_DOC_ID` = `\b(TYPE)-([A-Za-z0-9]+)\b`) flagged **any** `TYPE-<token>` that wasn't
`TYPE-<digits>` (or `-INDEX`) as a malformed document id — so prose like `PRD-Ready` (a
readiness-gate name), `BRD-TEMPLATE` (a quick-link), and `BRD-NN` (a placeholder) tripped it
on the BRD-00 index template and on any consumer's filled-in index.

**Decision.** A valid doc-id's post-hyphen segment is **always all-digits** (`doc_re` =
`^[A-Z]+-\d{2,}$`), so a `TYPE-<letter-leading>` token can never be a malformed instance of
that form — it is a compound word/marker. ID02 now fires **only when the second segment is
digit-leading** (`m.group(2)[0].isdigit()`) and fails `doc_re`. This removes the prose
false-positives while keeping every real malformed id flagged (`BRD-2`, `BRD-007x`), and
**generalizes** [[D-0043]]'s special-cased `-INDEX` exemption to any non-id-like token (the
explicit `-INDEX` clause is subsumed and removed). Accepted tradeoff: a letter-in-digit-slot
typo (`BRD-O1`) is no longer flagged — rare, and a future `≥1-digit` heuristic could recover
it without reintroducing the FPs.

**No version bump.** ID02 is not documented normatively in `framework/`; the rule's contract
("malformed doc-ids are flagged") is unchanged — only the FP scope narrows. The lint code
lives in `tools/sdd_doc_lint/` (vendored byte-identical to both platform mirrors via
`sync-vendored.sh`); no `framework/**` path is touched → GATE-SPEC does not fire, matching the
D-0043 (STRUCT01-INDEX-EXEMPTION) linter-bugfix-no-bump precedent. New unit cases guard the FP
removal (via the valid fixture) + the kept true-positive; 166 conformance green; zero ID02 on
the example corpus. Reviewed: 3 passes (Pass 2 independent). Closes FRAMEWORK-TODO
`LINT-DOCID-HEADER-FALSE-POSITIVE`.

---

## D-0055 — COV03 phase-leak advisory (deferred-band over-realization); no new phase tag — the band + BRD-00 roadmap already encode both phase axes

**2026-07-06.** D54-F13 (phase-leak leg; framework spec `0.33.1 → 0.34.0`, MINOR). The
original TODO proposed "a first-class phase tag on capability elements." Grounding found that
**redundant**: within-cycle phase is already the FR **band** (`priority_definitions`: `Future`
= "Next MVP cycle"), and cross-cycle phase is already the **BRD-00 `Cycle` roadmap** — where
later-cycle BRDs are `Planned`/`Sketch` = **trace-inert** (not in the `@`-tag graph), so an
IPLAN structurally cannot realize a future-cycle element (that leak is already prevented).

**Decision: ship only the missing check, no new tag.** `COV01` blocks an `AUTHORED` FR that is
NOT realized; nothing flagged the inverse — a `DEFERRED` (`Future`-banded) FR that IS realized
downstream. `COV03` adds exactly that as an **advisory** (`warning`, both modes, never blocks):
scope pull-forward is legitimate, so it prompts the author to re-band `P1`/`P2` or confirm the
deferral rather than failing a gate (the REUSE01-advisory precedent). It reuses the existing
band + coverage graph + `_element_realizing_citers` helper — a ~40-line sibling of
`_check_forward_coverage`, keyed strictly on `CoveredState.DEFERRED` (a bare `Future` band), so
a `realized_by:` FR (`REALIZED_BY`, a positive coverage claim) is never flagged. It has **no**
`{SPEC,IPLAN}` corpus precondition (unlike COV01) — it fires on a BRD+PRD-only corpus, the
early stage where a phase-leak is likeliest.

Rejected (out of scope, over-engineering): a first-class phase tag (duplicates the band +
roadmap); a cross-cycle IPLAN→Cycle binding + a **blocking** gate (cross-cycle already
prevented; blocking fights legitimate scope changes). Canonical edit in
`tools/sdd_doc_lint/__init__.py`, vendored byte-identical to both mirrors
(`sync-vendored.sh`); the `framework/**` GATE-SPEC change is the TRACEABILITY.md §Coverage
gates doc + a BRD band note. 6 new `test_coverage_engine.py` cases; zero findings on the
example corpus; new rule verified end-to-end across all 5 branch cases. Reviewed: 3 passes
(Pass 2 independent). Closes FRAMEWORK-TODO `D54-F13`.

---

## D-0054 — The IPLAN template inherits its implementation language from SPEC (no new IPLAN field); de-Python the template's example content

**2026-07-06.** IPLAN-LANG-001 (framework spec `0.33.0 → 0.33.1`, PATCH). Layer-8
`IPLAN-TEMPLATE.yaml` hardcoded a Python toolchain (`pip install`/`pytest`/`mypy`/`ruff`,
`src/[module]`, `*.py` paths) in its example content. Language + dependencies are a
**SPEC-owned fact** (Layer 6 `SPEC-TEMPLATE.yaml` `language:`/`dependencies:`), and every
IPLAN already cites its SPEC (`@spec: SPEC-NN`).

**Decision: inheritance, not a new field.** The template instructs the author to read the
`@spec` language/dependencies and express each phase in that toolchain, rather than adding
an IPLAN-level `language:` key (which would duplicate a SPEC-owned decision at the wrong
layer). Example content became `<…, per the @spec language>` placeholders + a labelled
`# example (Python):` line per `file_manifest` path (§2) and `execution_commands` category
(§3). During impl the same Python residue was found in §5 (session_handoff) + §6
(traceability `@code:`/`@tests:` + code_inventory) and given the identical treatment for
internal consistency (a discovered-in-impl extension of the ratified §2/§3 scope — same
fix, no new design).

**Contract preserved → no code change.** The six sections and the three
`execution_commands` categories (`setup`/`implementation`/`validation`, each a non-empty
list) are unchanged, so nothing that reads the template breaks: Hermes `iplan_rules.py`
category validation, `test_layers.py` metadata assertions, and the acceptance harness
(section-key presence only — no reader parses `execution_commands` *content*) all stay
green. Plugin bundle re-vendored via `sync-plugin-framework.sh`. Framework **PATCH**;
plugin + Hermes product versions unchanged. Rejected (out of scope): renaming the category
keys (a validated contract), an action-vocabulary DSL (speculative until a non-Python
platform demands it), and folding design-review governance into IPLAN (that rigor lives
upstream). Reviewed: 5 passes (3 independent) incl. a 0.33.0 refresh re-validation. Closes
FRAMEWORK-TODO `D54-F06-IPLAN-PROJECT-TYPES`.

---

## D-0053 — Modernize the Hermes sdd-orchestrator skill from the v3.2 15-persona + Lite/Standard/Full depth-tier model to the weighted-crew + playbook + single-path model

**2026-07-06.** H11-ORCHESTRATOR-CREW-MODEL. The `sdd-orchestrator` agent-skill described
the **v3.2-era review + flow model the engine abandoned** — a flat pool of "15 specialized
review personas" and a Lite/Standard/Full depth-tier selection. Both are gone from the
framework: the review model is the closed **weighted crews** of
`framework/governance/REVIEW_CREWS.yaml` (one per-layer crew of ~5-6 weighted lenses →
weighted-average readiness, per `review/review_scoring.py`) with per-`(layer,lens)`
playbook injection (LAYER-PLAYBOOKS-001); the flow is a **single path** over the 8 layers
with CHG as a governance overlay and the **necessary-upstream** contract
(NECESSARY-UPSTREAM-001) governing upstream realization — no depth tiers.

**Scope = the files that would MISLEAD a user/agent:** `SKILL.md` (persona model → point at
`REVIEW_CREWS.yaml` + one illustrative BRD crew, no second-source copy of weights; scoring
formula → weighted-average; BRD section list → point at `BRD-TEMPLATE.yaml`; "4-persona"
counts → 5-lens; stale `/opt/data/ucx_framework/.venv` MCP paths → `/path/to/python`; "v3.2"
pins dropped) **plus the two LOADED governance files** carrying the behavioral depth-tier
residue — `governance/GOVERNANCE_RULES.md` §7 (a fallback-loaded governance doc) and
`references/governance-load-protocol.md` (the **primary** mandatory load per `SKILL.md:26`).

**Point-at-authority, not copy** (the internal-consistency trap): the skill references
`REVIEW_CREWS.yaml`/`BRD-TEMPLATE.yaml`/`framework/VERSION` as authorities and shows only
one illustrative crew, applying the D-0006 single-source principle to a consuming skill so
the weights cannot drift.

**Versioning:** Hermes **PATCH** `0.7.0 → 0.7.1`, skill `2.0.0 → 2.1.0`. No `framework/`
change — prose corrected to match already-shipped engine behavior (no GATE-SPEC, no
re-vendor); backward-compat is prose-only, engine unchanged.

**Deferred (backlog follow-ups, carved in `HERMES-BACKLOG.md`):** the ~25-file cosmetic
"v3.2" string residue across the 72-file inherited governance scaffold + non-loaded
references; the stale hand-vendored `references/` framework-doc copies (a [[D-0013]]
delete-vs-resync decision); the element-ID SHA-256 residue (`SKILL.md` states IDs are
SHA-256-derived; per [[D-0040]] element IDs are LLM-generated stable strings — the rehash
is framework-gated by PROVISIONAL-IDS-002). Reviewed: 4 passes (Pass 2 = 3 independent
agents; Pass 3 = fresh-context independent adversarial re-review; both clean). Closes H-11.

---

## D-0052 — The plugin review lens honors the author-self-claim strip MUST via a disregard instruction (GD-05 fallback); implemented across the 9 audit + 9 fixer SKILLs + review-team + the auditor

**2026-07-06.** H-14 PR 2 — the plugin-side implementation of [[GD-05]] (framework
`0.33.0`, ratified in PR #246). The plugin's agentic review lens reads the artifact
directly, so it cannot physically strip the author's self-assessment score (the
"strip the body" prose was inert — the plugin analog of [[D-0051]]'s Hermes
content-blindness). Per GD-05's constrained fallback (a direct-read lens de-anchors by
instruction), every anchored lens path now instructs the lens to **not read, cite, or
weight** `*_ready_score`/`*_score`/`readiness_score`/`audit_score`/`gate_ready` when
forming its `lens_score`:

- the **9 `doc-*-audit`** SKILLs (fan-out brief bullet + the strip section replaced with
  the disregard framing, both modes; `doc-chg-audit` bespoke for `gate_ready`);
- the **9 `doc-*-fixer`** SKILLs (the inline patch-validation lens brief — surfaced by
  the H-14 plan Pass-3 as a missed surface `review-team` doesn't reach);
- **`review-team`** (the shared fan-out) + **`traceability-auditor`** (the readiness
  line qualified: lens disregards the author's score; the standalone gate uses the
  recomputed score).

Plugin PATCH `0.23.0 → 0.23.1`; no framework change (GD-05 landed in PR 1). Both
platforms now satisfy the strip MUST — a curated-input engine (Hermes) by physical
removal, a direct-read engine (the plugin) by the disregard instruction. Closes H-14.

---

## D-0051 — Hermes review was content-blind (the document body never reached the lens); inline the body into the review prompt; the H-6.2 strip was inert until now

**2026-07-04.** While implementing the single_pass author-self-claim strip
([[HERMES-SINGLE-PASS-PARITY-PLAN]], PR #242), impl-stage end-to-end verification
revealed that **Hermes's API-path LLM review never received the artifact body.**
`assemble_project_review_prompt` composed the prompt from persona + optional playbook +
template + actionable rules + optional layer assets + a **metadata-only JSON** block;
`section.content` fed only categorization/token-math/snippets, which land in
`bundle.context` and are never serialized into the prompt. The executor is a pure
completion (`run_executor`'s `working_dir` is not forwarded to `run_api_executor`), and
the review callers pass `system_prompt=None`. So the lens scored a document it had never
read. A dispatched investigation confirmed this is a **gap, not a design**: the review
templates carry an unfilled `## Document to Review` / `[PASTE … BELOW]` placeholder; the
creation flow inlines substance; and `REVIEW_TEAM.md:78-93` presupposes the body reaches
the lens.

**Fix.** At the single builder chokepoint `assemble_project_review_prompt`, inline a
`## Document to Review` block from the per-persona `included_sections` (falling back to
all sections when empty — though the existing `validate_prompt_bundle_or_raise` already
rejects an empty included set loudly), after removing the template's own placeholder so
exactly one block is emitted. Every review path (MCP `prompt_only`, CLI `single_pass`,
saga branches/aggregate) routes through this builder. **No new token accounting** —
`tokens_total` already folds `included_sections` content, so the existing warning
already reflects body size (adding accounting would double-count and spuriously trip the
saga's P1 finding).

**Two consequences worth recording:**

1. **The H-6.2 author-self-claim strip ([[D-0049]]) was inert.** It mutated
   `section.content`, which never reached the LLM. Folding the strip into
   `run_project_review_build` (extracted to `section_hygiene`) so the inlined body is
   stripped makes it effective **for the first time** — and closes the `single_pass`
   surfaces the saga-only strip never covered. This **supersedes the strip-only premise
   of [[HERMES-SINGLE-PASS-PARITY-PLAN]]** (#242), whose stated rationale ("both paths
   write the artifact body into the lens prompt") was false.
2. **Process:** the gap was invisible to planning and to three plan-review agents; only
   *exercising the change end-to-end* at impl time (the `verify`/"drive the real flow"
   discipline) surfaced it. A cosmetic conformance "fix" would otherwise have shipped.

Hermes MINOR `0.6.0 → 0.7.0`; no `framework/` change (the spec already assumes the lens
reads the body). Deferred (new backlog entries): large-artifact chunking (this fix
warns, does not truncate) and the **plugin-side** strip gap (the plugin lens reads the
raw on-disk file, so `REVIEW_TEAM.md:82` may be unfulfilled there too).

---

## D-0050 — Hermes Phase 1b (saga break-circuit / PARTIAL_TIMEOUT / G-R1 resume / `quality_loop_max_iterations`) deferred: architectural, not the stale reasons the backlog cited

**2026-07-04.** An evidence-based assessment (grounded file:line against both
platforms) re-scoped Hermes "Phase 1b / H-1." The backlog cited two blockers that
are **both stale**, and surfaced the **real** reason the work should not proceed now.

**Stale premises corrected:**

- **"Plugin Phase 4 (PRD..IPLAN saga-driver propagation) should land first" —
  SATISFIED.** Plugin Phase 4 shipped in `claude-code-plugin/v0.21.0` (2026-06-22):
  all 8 layer autopilots now drive `tools/saga_driver.py`
  (`platforms/claude-code-plugin/CHANGELOG.md:73-88`). The `_ALLOWED_TRANSITIONS`
  table is **stable** — byte-identical in `saga_models.py` and `saga_driver.py`,
  matching `REVIEW_SAGA.md`, and triple-enforced by conformance.
- **"BRANCH_COMPENSATING spec gap" — OPEN but ORTHOGONAL (not a Phase-1b blocker).**
  Correction (an earlier draft of this decision wrongly called it resolved on a
  false-negative grep): the `BRANCH_COMPLETED→BRANCH_COMPENSATING` transition IS
  still emitted — **branch-scoped** — by all 9 `doc-*-fixer` skills during the
  remediation cycle (e.g. `doc-brd-fixer/SKILL.md:150`, line-wrapped in the JSON),
  and it is NOT in the run-scope `_ALLOWED_TRANSITIONS` table (which permits
  `BRANCH_COMPLETED→{FANIN_REDUCED, PARTIAL_TIMEOUT}` only). (`BRANCH_COMPLETED→
  FANOUT_STARTED` is genuinely absent.) Whether the branch-scoped compensation arrow
  is a real spec gap turns on whether branch-scope transitions must validate against
  the run-scope table — an open question, assessable independently. It does **not**
  gate this deferral: Phase 1b is deferred on the architectural reason alone.

**The real reason to defer (architectural):** Hermes's review saga is a **single-pass,
in-process fan-out/fan-in** of one already-existing document — `iteration=1` hardcoded
(`saga_orchestrator.py`), no create→review→revise loop, no wall-clock soft deadline,
no cross-invocation resume. The plugin's PARTIAL_TIMEOUT / `resume_from_partial_timeout`
/ `quality_loop_max_iterations` are properties of an **outer, wall-clock-bounded,
multi-iteration** loop Hermes does not have. Therefore, building them into Hermes now
would be **speculative net-new machinery**, not "alignment":

- A PARTIAL_TIMEOUT write-site + break-circuit is **not required for conformance**.
  `REVIEW_SAGA.md:120` says an orchestrator MUST monitor a SOFT_DEADLINE (which
  Hermes does not), but `:150-154` explicitly forgives ignoring the break-circuit as
  a "cooperative failure" that is still a "valid graceful-degradation state;
  conformance accepts either." Hermes reaches a legal terminal by an orderly
  quorum-based escalation (branch timeout → `BRANCH_FAILED` → `ESCALATED`) — a
  different degradation path from the spec's "hard timeout fires → last checkpoint"
  example, but equally conformant. Adding a real SOFT_DEADLINE + PARTIAL_TIMEOUT is
  the honest way to satisfy the `:120` MUST, but it is net-new machinery, deferred
  with the rest.
- A G-R1 resume-walk (`transitions[]` backward) would be **dead code** — Hermes never
  writes PARTIAL_TIMEOUT and re-runs in-process, not across invocations.
- `quality_loop_max_iterations` is **inapplicable** to a single-pass saga.

**Decision:** the PARTIAL_TIMEOUT write-site, G-R1 resume-walk, and
`quality_loop_max_iterations` items are **deferred pending a future Hermes
multi-iteration / wall-clock-bounded review-loop initiative** — the same architectural
gate that already blocks H-6.3 ([[D-0049]]). Building them earlier would violate the
repo's "minimal-and-realistic / no speculative scope" convention. The one
genuinely-unblocked H-1 sub-task is a Hermes saga-invariant conformance test — but
its core (raise-on-invalid transition) is **already verified in Hermes's unit suite**
(`test_saga_review_journal.py::test_saga_journal_rejects_invalid_transition`), and
`test_saga_lifecycle_parity.py` asserts table-parity (`SagaTransitionTableParity`) +
real-journal conformance (`SagaRealJournalConformance`, [[D-0048]]). The only net-new
value is a ~15-line *conformance-level* mirror of the plugin's
`test_saga_driver_invariants.py::test_invalid_transition_raises` (the raise-invariant
lives in the shared conformance contract for the plugin but not yet for Hermes) —
small, non-speculative, unblocked, noted as an optional residual in the backlog, but
not required since the behavior is already tested, and needing none of the deferred
break-circuit machinery. Next Hermes item is `prompt_only`
playbook injection (architecturally unblocked, aligned with the single-pass fan-out).
This decision also corrects the stale `docs/PARITY.md` enforcement-parity prose
(which still described PRD..IPLAN as "v0.6.0 cooperative").

---

## D-0049 — Hermes review calibration: no-findings rationale cap + strip author self-claim (H-6.1 + H-6.2); fixer-regression stays deferred (single-pass saga)

> **Correction (2026-07-04, [[D-0051]]):** the H-6.2 author-self-claim strip recorded
> here as CLOSED/effective in `hermes/v0.6.0` was in fact **inert** — it mutated
> `section.content`, which never reached the review LLM (Hermes review was
> content-blind). D-0051 inlines the body into the review prompt and folds the strip
> into the shared builder, making it effective for the first time. The H-6.1
> no-findings cap is unaffected.

**2026-07-04.** Two of the three FRAMEWORK-CLEANUP-001 "PR-B heart" review-quality
deltas (H-6) were consumer-side gaps in Hermes's team-mode review path — the
contracts already existed in `REVIEW_TEAM.md` + the injected playbooks ([[D-0046]]),
but Hermes didn't enforce them. Implemented both; Hermes MINOR `0.5.1 → 0.6.0`, **no
framework change**.

- **No-findings rationale (H-6.1).** Parser captures `no_findings_rationale`;
  `score_review` caps a 100/zero-findings/no-rationale lens to 95 (`STRUCTURE-RAT-001`
  advisory). The cap lives in `review_scoring.score_review` (the module that owns the
  `REVIEW_TEAM.md` scoring policy) via optional params, so existing callers are
  unaffected. **Non-obvious:** implementing this required fixing a latent parser bug —
  a clean `findings: []` fell through to a `fallback` P1 with `lens_score=None`,
  dropping the lens from scoring entirely (the cap was unreachable). The parser now
  returns a successful empty result preserving the score.
- **Strip author self-claim (H-6.2).** `_strip_author_self_claim` redacts the
  canonical self-claim fields from section bodies once before fan-out, in-prompt only.

**Two calls worth recording:**

1. **`personas_with_findings` is measured post-citation-floor.** A lens that filed
   only *uncited* findings (discarded by the playbook citation floor) counts as
   zero-findings and is capped — a deliberate divergence from the spec's literal
   "filing any finding bypasses," on the grounds that an all-discarded lens produced
   nothing *substantiated*. The independent plan review endorsed this.
2. **H-6.3 (fixer-introduced regression detection) stays deferred, not attempted.**
   It requires an iter-N vs iter-(N-1) comparison; Hermes's saga is **single-pass**
   (`iteration=1`), so there is no prior iteration. It belongs to a future Hermes
   multi-iteration review-loop initiative. Likewise **H-2** (REVIEW-CALIBRATION-001
   sub-checks) was NOT bundled here: those live only in the plugin's audit SKILLs, not
   the shared playbooks, so reaching Hermes needs a framework-spec playbook port — a
   separate review-team calibration decision.

---

## D-0048 — Hermes real saga journals conform to `saga.schema.json`; `layer` derives from `doc_type`; `09_CHG` added to the schema enum (HERMES-SAGA-JOURNAL-CONFORMANCE, H-12)

**2026-07-03.** The **real** Hermes saga journal (`asdict(SagaRunState)`) was missing
4 `saga.schema.json`-required fields (`artifact_id`, `layer`, `iteration`,
`transitions`) and never recorded `transitions`. The Phase-1 conformance guard
([[D-0045]]) validated only **hand-authored fixtures** — which carried those fields —
so the cross-platform journal-conformance parity claim ([[D-0031]]) was aspirational
for Hermes, not enforced against real output. Fixed by adding the 4 defaulted fields
to `SagaRunState`, recording schema-shaped transitions (`{ts, from, to, scope}`) at
the run seed / each successful `update_run_status` / each branch status change, and
roundtripping them in `_to_run_state`.

**Two non-obvious calls:**

1. **`layer` derives from the required `doc_type`, not the optional `--layer`.** A
   review's `--layer` is optional (`default=None`) and free-text, while `--doc-type`
   is required. Setting `layer=layer` would emit `layer: null` on the default
   invocation → schema failure, re-creating the exact "fixture passes, real output
   doesn't" defect H-12 exists to kill. The orchestrator uses
   `normalize_layer(layer or doc_type)` (the existing helper maps either the
   doc-type form or the directory form to the enum-form dir), so the journal conforms
   whether `--layer` is supplied or omitted.
2. **`09_CHG` added to the schema `layer` enum (framework PATCH).** Phase 3 ([[D-0047]])
   made CHG a review target; a real CHG review journal carries `layer: "09_CHG"`,
   which the enum lacked. Adding it (additive; the plugin's `saga_driver` already
   carries `09_CHG` in its layer-crew map) completes the CHG sanctioning the H-12
   finding promised, and is guarded by a real CHG-journal conformance test.

Framework spec PATCH `0.32.6 → 0.32.7`; Hermes PATCH `0.5.0 → 0.5.1`. GATE-SPEC
applies (framework change); re-vendored to the plugin bundle. The new
`SagaRealJournalConformance` test validates a real journal (not a fixture) — the
guard that would have caught H-12. Closes H-12.

---

## D-0047 — Hermes playbook coverage is 8-layer-complete (Phase-2 payoff, verified); CHG gets crew-map parity, live CHG saga deferred (HERMES-PARITY-PHASE-3)

**2026-07-03.** Phase 2's playbook injection ([[D-0046]]) was written layer-agnostic,
so **all 8 lifecycle layers already inject** their per-`(layer,lens)` playbooks —
verified empirically (every `REVIEW_CREWS.yaml` crew lens resolves) and locked in by
a regression test. **CHG (H-10):** added the `chg` review crew to
`persona_mappings.yaml` and removed the `HERMES_DEFERRED_LAYERS` whitelist, so the
crew-coverage test now enforces CHG — **crew-map parity only**. A *live/sanctioned*
CHG saga review is deferred: Hermes never loads `saga.schema.json` at runtime (so
there is no runtime schema wall) and the crew resolver has no `doc_type` allowlist,
so adding the crew map makes an *explicit* `doc_type=chg` review dispatchable
(previously inert) — but its journal `layer` would be outside the schema enum. Making
CHG a first-class review target (add `09_CHG` to the schema + a sanctioned dispatch)
is the follow-on. `hermes/v0.5.0`; no framework spec change. (H-6/H-2 calibration
deltas + `prompt_only` injection remain later phases.)

## D-0046 — Hermes playbook injection (BRD+PRD): crew-membership-keyed, citation floor on the LLM path, byte-identical finding_filter vendor (HERMES-PARITY-PHASE-2)

**2026-07-03.** Hermes's review saga now injects per-`(layer,lens)` playbooks +
enforces the `check:` citation floor + emits `verdict.playbook_coverage`, for
BRD+PRD (`hermes/v0.4.0`). Key design decisions:

- **Keyed on framework crew membership, not file presence.** Branch personas come
  from `persona_mappings.yaml` (a superset of `REVIEW_CREWS.yaml`); a persona that
  is NOT a framework crew lens (`fact_checker`; `chairperson`→`synthesizer`) gets no
  playbook + no floor and is **never** `BRANCH_FAILED`. Only a crew lens with an
  absent playbook file fails. (A naive "missing file → fail" rule would have broken
  every BRD review — its list carries `fact_checker`.)
- **Absent `check` key, not `""`.** The parser omits `check` when the lens didn't
  cite one, so the vendored `finding_filter.emit_coverage` (which counts any
  non-`None` check) doesn't create a spurious `""` bucket.
- **Coverage counted pre-reduce.** Dedup keeps only one branch's citation, so
  post-reduce counting under-reports; `playbook_coverage` is computed from the kept
  pre-reduce findings.
- **Floor on the LLM path only.** The deterministic-fallback branch emits
  inspection-derived findings with no citation; discarding there would empty it.
- **`finding_filter.py` is a byte-identical vendor** of the plugin's (engine-agnostic,
  stdlib) with a drift-guard test — not a divergent port. `prompt_only`/aggregate
  builds + the other 6 layers + CHG are Phase 3. No framework spec change.

## D-0045 — Hermes parity is engine debt (playbook injection + saga completeness), not the 0.32.x arc; phased, starting with saga conformance (HERMES-PARITY-PHASE-1)

**2026-07-02.** An evidence-backed assessment corrected the stale
`HERMES-BACKLOG.md` premise: **Hermes already has team-mode** (a working saga
orchestrator with parallel per-persona fan-out + crew reconciliation to
`REVIEW_CREWS.yaml`), and **the entire 0.32.x arc (D-0038…D-0044) is
auto-satisfied** for Hermes via its byte-identical vendored `sdd_doc_lint` +
shared `framework/layers/` templates — none of it needs Hermes-native code. The
real gap is older engine debt: **playbook injection** (Hermes injects persona
files, not the per-`(layer,lens)` `framework/playbooks/`) + **saga completeness**.
Sequenced into phases (playbook plumbing gates the layer/CHG/calibration work);
each phase gets its own minimal plan. **Phase 1** (this decision's shipped slice):
add the spec-required `PARTIAL_TIMEOUT` state to Hermes `_ALLOWED_TRANSITIONS`
(was missing) and ship `test_saga_lifecycle_parity.py` — which `docs/PARITY.md`
over-claimed already existed — so *both* platforms' tables are enforced against
`REVIEW_SAGA.md`. **No Hermes version bump:** Phase 1 makes the state machine
*accept* `PARTIAL_TIMEOUT` (the parity contract); the orchestrator does not yet
*write* it (break-circuit exercise + resume = Phase 1b). Plan:
`plans/HERMES-PARITY-PHASE-1-PLAN.md`.

## D-0044 — the project roadmap lives in the BRD-00 index "Planned BRDs" table; a sketch is a trace-inert planned row (ENG-BRD-SKETCH-ROADMAP)

**2026-06-30.** Whole-project scope is captured at project init by enumerating
every planned MVP cycle as a row in the **`BRD-00` index "Planned BRDs" table**
(extended with cycle / target-PROD / `@depends:` / status columns) — the
recommended (not mandated) home, chosen over a separate top-level `ROADMAP.md` to
avoid colliding with a consumer's product-strategy file, and over a new artifact
to keep the change docs-only. A **Sketch** (scope-only future-cycle entry) is a
Planned-BRDs **row**, **trace-inert**: it carries only its `BRD-NN` id + `@depends:`,
no element IDs, is not in the `@`-tag graph, and forward coverage ignores it
(`scan_fr_elements` finds no FR section). `@depends:` is not a trace tag, so an
active BRD referencing a not-yet-authored planned row never trips TRACE-RES-001.
`Sketch` is a table-cell status, NOT added to the document `status` enum
(`Draft|In Review|Approved`), so it does not collide with [[BL-STATUS-SCOPE]].
A *standalone* scope-only `status: Sketch` BRD **file** is deferred — it would fail
STRUCT01 as an instance BRD (the index exemption covers only `<TYPE>-00_index`
docs); needs a STRUCT01 under-authoring exemption + a `SKETCH-001` over-authoring
guard, pulled only if over-authoring drift appears. Builds on [[D-0043]] (the
BRD-00 index is now STRUCT01-clean). Framework PATCH 0.32.4 → 0.32.5.

## D-0043 — `sdd_doc_lint` detects index/registry docs by filename (STRUCT01-INDEX-EXEMPTION)

**2026-06-30.** Index/registry docs (`<TYPE>-00_index`) are exempted from the
instance-doc structural checks (STRUCT01 required-sections, trace-resolution skip)
via a `_is_index_doc(rel, fm)` helper keyed primarily on the **`<TYPE>-00_index`
filename**, not on a top-level `artifact_type: <X>-INDEX`. Rationale: the filename
is the one signal reliably present on all 8 layer index templates and a consumer's
copies regardless of frontmatter shape — the `.md` templates nest `artifact_type`
under `custom_fields` (6 with a bare value) and the IPLAN-00 registry is a `.yaml`
with no `---` frontmatter (so `_extract_frontmatter` returns `None`). A top-level
`artifact_type` ending in `-INDEX` is still honored for back-compat. Separately, the
ID02 doc-id scan now skips `-INDEX` tokens (an index artifact-type marker is not a
malformed doc-id) — chosen over adding a top-level `artifact_type: <X>-INDEX` to the
templates, which would have self-tripped ID02 (the original docs-only plan; rejected
at independent review Pass 2). Pure linter fix; no `framework/` change, no spec bump.
Unblocks [[ENG-BRD-SKETCH-ROADMAP]] (BRD-00 index as a lint-clean roadmap home).

## D-0042 — readiness scores are advisory: marked in-template, no rubric (BL-READY-SCORE-ADVISORY)

**2026-06-30.** The `<next>_ready_score` (in `document_control`) and `target_score`
(in `health_score`) fields in all 7 layer templates (BRD…TDD) are **advisory**, not
a gate: the auditor review lens computes them, they are never hand-authored, and the
real merge gate is the deterministic `sdd_doc_lint` floor. A blank value is NOT
incomplete. Marked via two comment/guidance-only mechanisms (no new content data
keys in `document_control`): an inline `#` comment on each of the 14 score lines
(matching the existing `document_control` inline-comment house style, e.g.
`status: … # …`), plus one `_note:` guidance key per `health_score` block carrying
the fuller statement (`_note:` is an established template guidance key). The same
PR also reconciled **15 `_guidance` prose lines** in those templates that still
framed the score as "required before generation" / a "quality gate" (ai-review
caught the contradiction on the impl PR) — the field marker and the surrounding
prose now agree. **No offline
rubric/tool was built** (author Q4) — that would contradict [[D-0040]]'s sibling
D54-F03 stance that the audit skill is the rubric and `sdd_doc_lint` is the floor.
IPLAN/08 carries neither field, so "all 7" = layers 01–07. PATCH 0.32.3 → 0.32.4.

## D-0041 — reuse is satisfied-by-reference: coverage-exempt, in-repo-pinned, full-prefix (REUSE-MANIFEST-001)

**2026-06-29.** A `reuse: {state: referenced, target: <doc_id|path>@<commit>}`
frontmatter block marks a doc satisfied-by-reference: its elements are **exempt
from COV01/COV02** (reused as-is), surfaced by one `REUSE01` advisory per doc
(emitted by a dedicated corpus-level `_check_reuse`, all layers — NOT inside the
gates, which only skip). The escape is keyed on the **host doc** (a
`doc_id→reuse_state` map), never inside `covered_state_of` (which has no host-doc
access). **Target must be in-repo + commit-pinned** (`REUSE02`); URLs are
`@discoverability` only. **Full-prefix rule:** a referenced doc's upstream
lineage must also be in-repo + referenced, so all `@`-tags resolve with no
trace-engine change — an absent upstream stays a `TRACE-RES-001` finding. The
no-free-≥90 readiness rule is a governance contract (skill enforcement deferred).
Builds on [[D-0039]] (element-level coverage) + [[D-0040]].

## D-0040 — provisional IDs: `id_state` frontmatter flag, advisory-only, not coverage-exempt (PROVISIONAL-IDS-001)

**2026-06-29.** Manual-mode provisional element IDs are governed by an
`id_state: provisional|canonical` **frontmatter** flag (default `canonical`) —
NOT the template-only `metadata.id_standard.state` (produced `.md` docs carry no
`id_standard` block). A `provisional` doc gets one doc-level `PROV01` **advisory**
(warning), never a per-element error. **`id_state` governs ID stability only, not
coverage** — provisional elements are still subject to COV01/COV02 and REFGRAN01
(the ordinal-hex form `0001` is `ELEM_FORM`-valid + FR-scanner-visible, so it is
gated like any canonical id; no exemption hole). "Canonical leaks" are NOT
shape-detectable (`0001` is a valid hash); only non-hex `xxxx` is flagged
(`PH01`, via `(?<!\.)\bx{3,}\b`), and full canonical-correctness verification is
deferred to `rehash --check` (PROVISIONAL-IDS-002). The SHA-256 algorithm is now
normative in `ID_NAMING_STANDARDS.md` (the by-hand ↔ plugin parity anchor).
Builds on [[D-0039]].

## D-0039 — element-level coverage uses a curated one-hop realizing-layer map (ELEMENT-COVERAGE-001)

**2026-06-29.** Element-level `COV01`/`COV02` realize an element via a **curated
`REALIZING_LAYERS` constant** (BDD→{SPEC,TDD}, EARS→{BDD,SPEC,TDD}, BRD-FR→{PRD}),
checked **one-hop / directly** on the `@`-tag edge graph — NOT a transitive
doc-level reach and NOT the registry `downstream` list.

*Why not registry `downstream`:* it is the single-hop cascade (`BDD→[ADR]`), so
pinning to it would route realization through the **decision** layer ADR and mask
orphaned scenarios. ADR is excluded from every realizing set (it decides, it does
not realize). *Why EARS→{BDD,SPEC,TDD} (not {BDD}):* an EARS cited directly by
SPEC must not false-flag, while an EARS cited only by BDD must pass — including
all realization layers, checked one-hop, satisfies both (empirically all 26
corpus EARS pass; 16 would have false-blocked under a "must reach SPEC/TDD"
rule). *Accepted limitation:* an EARS realized only by an **orphan** BDD scenario
passes COV02 — the orphan is surfaced independently at the BDD layer, so no defect
is hidden; a transitive "is the realizer itself realized" check is out of scope.
Supersedes the CFB-PR-2 doc-level binding for COV01/COV02. Builds on [[D-0038]].

## D-0038 — YAML-native BDD scenarios replace Gherkin-in-markdown (YAML-BDD-SCHEMA, plan D-1…D-6)

- **Date:** 2026-06-28T00:00:00Z
- **Decision:** Migrate the BDD layer's produced artifact from Gherkin-embedded-
  in-markdown to a structured **YAML scenarios block inside `BDD-NN.md`**. The
  plan-local decisions (`plans/YAML-BDD-SCHEMA-PLAN.md`):
  - **D-1 Carrier** — a fenced ` ```yaml ` block in §2/§3 of `BDD-NN.md`; the
    doc stays markdown with the five `##` sections (STRUCT01 unchanged).
  - **D-2 Step model** — `given/when/then` phase lists; thresholds stay **inline
    `@threshold:` in step prose** (a bare `threshold:` field would fire ID03 and
    bypass TH-RES-001). Requires the `_THRESHOLD` regex to exclude trailing
    quotes (`([^\s|'"]+)`).
  - **D-3 Coverage** — the Feature carries **no `ears`**; coverage = union of
    scenario `ears` (kills the CFB-PR-3 fan-out).
  - **D-4 Emitter** — on-demand, one-way `tools/bdd_to_gherkin.py` (git-ignored
    output); these docs are QA-staging-only, not CI-executed.
  - **D-5 Scope** — plugin skills/engine; Hermes skills/engine deferred; the
    shared linter code still ships to the Hermes vendored copy (byte-identity).
  - **D-6 Migration** — a deterministic `tools/gherkin_to_bdd_yaml.py` transcoder
    (framework tool) that **copies each `@scenario-id:` verbatim** into `id:`,
    keeping all 16 downstream `@bdd:` citations stable. NOT an LLM regeneration
    (which would drift the content-hash IDs and break downstream).
- **Why:** GD-03 mandates pipe-delimited multi-element trace tags, but `|` is
  Gherkin's table delimiter and Gherkin tags cannot contain whitespace — so the
  GD-03 form is physically illegal on a Gherkin tag line. Carrying trace as typed
  YAML fields removes the collision at the root, makes REFGRAN a structural
  check, and turns element-level COV02 into a direct set computation. The
  framework is pre-1.0, so realigning the artifact with its own template's
  already-YAML scenario model is low-cost.
- **Review:** converged over 3 independent fresh-context passes (Pass 1: 10 gaps;
  Pass 2: 3 load-bearing + 5 minor; Pass 3: READY). Plan PR #197 merged
  (`dfb57309`, 2026-06-28). Implementation is a ~6–8 PR sequence.

## D-0037 — `realized_by` escape authored as an inline FR-bullet token (CFB-PR-2 DD-5)

- **Date:** 2026-06-27T00:00:00Z
- **Decision:** The `realized_by:<layer>` coverage escape (DD-5 — an FR realised
  by a non-SPEC layer: ADR-only decision / NFR / infra) is authored as a
  `realized_by: <LAYER>` token on the FR bullet's **first line**, canonically
  inside the band parenthetical (e.g. `- **BRD.NN.07.xxxx — Title**
  (P1, realized_by: ADR): …`). The scanner captures it into the additive
  `FRElement.realized_by` field; `covered_state_of` maps its presence to
  `CoveredState.REALIZED_BY`.
- **Why:** No `realized_by` surface existed anywhere (registry, templates, or
  corpus) — it had to be defined. A first-line inline token (a) needs no new
  YAML field, (b) is single-line so it sidesteps the wrapping-parenthetical
  parse problem (the band token already reads only the first line), and (c)
  fits the existing authored FR-bullet form rather than introducing a parallel
  structure. The BRD-template normative rule formalizing the annotation lands
  with the forward gate (2a-core step 4), where the rule and the gate that
  consumes it are coupled. `satisfied_by_reference` stays a stubbed enum member
  (PR-5). See D-0036 for the sibling CFB-PR-2 placement decision.

## D-0036 — Shared trace primitives live as a submodule of the `sdd_doc_lint` package (CFB-PR-2 DD-1)

- **Date:** 2026-06-27T00:00:00Z
- **Decision:** The shared `@`-tag trace primitives (CFB-PR-2 DD-1) live at
  `tools/sdd_doc_lint/trace_graph.py` — a submodule of the `sdd_doc_lint`
  package — not as a loose `tools/sdd_trace_graph.py` sibling (where step 1
  first placed them). `sync-vendored.sh` carries the submodule into each
  platform's vendored linter; the byte-identity drift-guard guards it.
- **Why:** The forward-coverage engine and gate live in the **vendored**
  `sdd_doc_lint` (the only whole-corpus tool, shipped byte-identical to both
  platforms). A package submodule is importable via package-relative
  `from .trace_graph import …` inside *any* copy regardless of how it landed on
  `sys.path`; a loose sibling would rely on a fragile parent-dir assumption that
  does not hold for the vendored copies. The two unvendored `tools/` scripts
  (`trace_walk.py`, `sdd_coverage.py`) reach it via `from sdd_doc_lint.trace_graph
  import …`. `trace_graph` itself stays pure stdlib (`re` + `pathlib`).

## D-0035 — MODEL-PRECHECK-ROLLOUT: print the per-layer model recommendation at the autopilot entry point

- **Date:** 2026-06-22T00:00:00Z
- **Decision:** Implement `model.precheck` as a `## Model precheck` section in
  the **8 layer autopilots only** that **prints** the per-layer recommendation
  (`model.per_layer.<L>` → else `model.default`) + the `/model <rec>` command —
  it does **not** compare against the session model. Modes: `warn` (print) /
  `silent` / `block` (print + confirm). Reword the Step-1 saga directive to
  "first orchestration action" so the notice runs before the driver. Plugin
  MINOR `0.21.0 → 0.22.0`.
- **Why (3 sub-decisions):**
  - *Print, not compare* — a skill cannot reliably read its own session-model
    id, so a compare-and-warn design is a near-permanent no-op (Pass-4 F3).
  - *Autopilots only* — post-Phase-4 the autopilot is the single interactive
    entry; base/audit/fixer run **headless** under the driver (no user for
    `warn`/`block`), so covering them needs an `AIDOC_SAGA` guard for no gain.
    Deferred.
  - *SKILL, not driver* — the saga driver is a Bash subprocess that can't pause
    for `block`'s acknowledgement; the autopilot SKILL runs in the live session
    and can, keeping all three modes honest.
- **Deferred:** standalone base-skill notice; any model *comparison*; auto-
  switching (impossible). Builds on D-0034 (uniform saga-driven autopilots).

## D-0034 — SAGA-PARITY-001 Phase 4: all 6 remaining layer autopilots driven by the saga driver

- **Date:** 2026-06-22T00:00:00Z
- **Decision:** Migrate `doc-{ears,bdd,adr,spec,tdd,iplan}-autopilot` to the
  proven `doc-prd-autopilot` two-subsection `## Workflow` shape — a
  `### Saga-driven generation loop` (`review_mode: team`, default) invoking
  `saga_driver.py --layer <NN_TYPE>`, plus the prior steps retained verbatim
  under `### Linear Pipeline` (`review_mode: single_pass`). Use `doc-prd-autopilot`
  as the byte-source (not `doc-brd-autopilot`, whose extra "MANDATORY" blockquote
  is not propagated). Add `review_mode` to the 6 SKILLs' `adapts:` and reconcile
  it into `doc-prd-autopilot` (it branched on the knob without declaring it).
  Guard with `test_autopilot_saga_parity.py`. Plugin MINOR `0.20.1 → 0.21.0`;
  no framework-spec change.
- **Why:** Only `brd`/`prd`/`chg` invoked the driver; the 6 layer autopilots
  described a legacy in-session loop. The acceptance harness shells the driver
  directly per layer (`test-acceptance.sh:1139`), *not* through the autopilot
  SKILL — so a user-invoked `/aidoc-flow:doc-bdd-autopilot` ran an untested path
  that diverged from the one the suite proves. Uniformity also unblocks the
  parked MODEL-PRECHECK-ROLLOUT (which needs a consistent autopilot corpus).
- **Scope deferred:** re-pointing the harness at the SKILL (its direct-driver
  call is AMEND-001's deliberate design); audit/fixer skills (review/fix, not
  drafting).

## D-0033 — Claude Code plugin user-facing commands: shape, channels, and honesty boundaries (PLUGIN-USER-COMMANDS)

- **Date:** 2026-06-14T00:00:00Z
- **Plan:** `plans/PLUGIN-USER-COMMANDS-PLAN.md` (merged via PR #142, plan-only;
  this PR delivers the implementation).
- **SemVer impact:** Plugin MINOR `0.18.0 → 0.19.0`.

Three sub-decisions, captured here so future contributors do not relitigate
them when extending the command surface.

### D-0033a — `/feedback` lands in GitHub Issues, not Discussions

Issues + a dedicated `.github/ISSUE_TEMPLATE/feedback.md` template covers the
v1 need (separate triage from bug reports, single backend that the maintainer
already monitors). Discussions adds setup overhead and a second moderation
surface for a channel that is empty today. Migration path: switching `/feedback`
to Discussions later is a one-URL change in `commands/feedback.md`; deferred
backlog only, no design debt.

### D-0033b — Split `/budget` and `/model` rather than ship a single `/performance`

A single command would collapse two orthogonal axes into one slider:
*cognitive depth* (which model the user runs against) and *effort the skill
spends* (how many passes, how verbose). Users genuinely want the four
combinations (Opus + min for high-stakes terse work; Haiku + max for
stress-tests; etc.). The split also makes each command's caveat sharper —
budget is a behavior knob, model is advisory — versus a single command that
would have to hedge both.

### D-0033c — Advisory-not-enforcing posture for `/model` and `/budget`

The plugin layer **cannot**:

- switch the Claude Code session model (only the native `/model <id>` does),
- enforce a hard token cap (no token-meter hook is available to plugins),
- remove itself (only the native `/plugin uninstall` does).

Rather than hide these limits or imply enforcement that doesn't exist, the
command prose names them explicitly. `/aidoc-flow:model` prints copy-paste
native `/model <id>` commands; `/aidoc-flow:budget` documents the empirical
40–60% token reduction `min` profile delivers via skipped passes; `/aidoc-flow:uninstall`
prints the exact native uninstall command and never claims to run it. The
honesty is verified by conformance test V5 (`grep -F "advisory" commands/model.md`).

---

## D-0032 — Unified development/work plan standard in the IPLAN layer (PLANSTD-001)

- **Date:** 2026-06-09T00:00:00Z
- **Decision:** Anchor a single, flexible development/work plan template to a
  normative spec doc at `framework/layers/08_IPLAN/PLAN_STANDARD.md`, and
  rewrite `plans/PLAN-TEMPLATE.md` to conform. The standard:
  - **(placement, D-PLANSTD-1)** lives in `08_IPLAN` as a **third, orthogonal**
    concept governing markdown `plans/*.md` dev/work plans — explicitly distinct
    from BOTH the Permanent per-SPEC `IPLAN-NN_{slug}.yaml` and the Temporary
    `tmp/TMP-IPLAN-*.yaml`. Neither YAML artifact changes; the IPLAN `README.md`
    cross-link is load-bearing for the layer's conceptual coherence.
  - **(flexibility, D-PLANSTD-2)** expresses section applicability via inline
    `[REQUIRED]` / `[CODE]` / `[IF APPLICABLE]` tags plus an applicability
    matrix over the confirmed work-type set `feature` / `bugfix` /
    `documentation` / `refactor` / `chore`; the agent keeps applicable chapters
    and deletes the rest (no `N/A` stubs).
  - **(engine-agnostic, D-PLANSTD-3)** carries no engine tokens and no literal
    version string (passes `test_spec_hygiene.py`).
  - **(verification, D-PLANSTD-4)** is `[REQUIRED]` for every work type; only
    the kind varies (runnable commands for code; lint/link/render/review for
    documentation).
  - **(versioning, D-PLANSTD-5)** bumps `framework/VERSION` MINOR
    (`0.14.3 → 0.15.0`, forced by GATE-SPEC-E005); re-matches both
    `FRAMEWORK_SPEC_VERSION` pointers; leaves plugin + Hermes **product**
    versions unchanged (independent streams, `docs/PROJECT.md` §2).
- **Why:** The prior `plans/PLAN-TEMPLATE.md` was thin and migration-flavored;
  real plans in this repo had outgrown it (File-structure / `### Task N` /
  Claim-ledger / Review-log sections absent from the template). One standard,
  reused across repos, replaces ad-hoc plan shapes. Full design, claim ledger,
  and 6-pass review trail in `plans/PLANSTD-001-PLAN.md` (PR #114).

## D-0031 — Promote the review-saga lifecycle into the framework spec (supersedes D-0005's scope)

- **Date:** 2026-06-05T13:00:00Z
- **Decision:** Promote the review-team saga lifecycle (state machine,
  transitions, journal schema, compensation events, break-circuit policy)
  from a Hermes-internal implementation detail to an engine-agnostic
  framework-spec contract at `framework/governance/REVIEW_SAGA.md` +
  `framework/governance/saga.schema.json`. Both platforms (Hermes Python
  runtime and Claude Code plugin via SKILL prompts + saga.json + Bash
  subprocesses) implement the same observable lifecycle. Framework spec
  bumps `0.12.0 → 0.13.0` (CHG-gated).
- **Why:** Two converging pressures:
  1. **New failure-class evidence.** D-0005 (2026-05-26) decided "no saga
     in plugin" on the premise that "there is nothing to journal" — the
     plugin's Task subagents are harness-managed and the blackboard +
     coverage/quorum handles partial-crew state. The 2026-06-05 live BRD
     verification (CHAOS-SEC-SPLIT-001, D-0030) revealed a failure class
     D-0005 did not contemplate: **partial outer-loop state** when
     `doc-brd-autopilot` times out mid-iteration with a 5-lens crew +
     multi-lens fixer validation. Concrete evidence:
     `examples/url-shortener/logs/2026-06-05T103311/elements/doc-brd-autopilot.log`
     shows `outcome: FAIL`, `duration_sec: 1802.0`, `error: claude -p exit
     124`, and no saga journal produced. The dual-dispatch path
     (acceptance script's standalone audit → fixer → re-audit) succeeded
     at total runtime 3535s — proof that the create→review→revise loop
     *did* have intermediate state worth preserving across phase
     boundaries, but the plugin had no place to durably record it.
     D-0005's "nothing to journal" assertion is factually incomplete: at
     the outer-loop level (phase progression, iteration count,
     transitions between phases) there *is* something to journal. The
     blackboard captured per-lens slot state correctly; what was missing
     was per-phase state.
  2. **Lifecycle-behavior parity requirement.** The project's parity goal
     is now lifecycle-behavior parity (per `docs/PARITY.md`), not just
     output-shape parity. Achieving it requires both platforms to expose
     the same observable saga lifecycle. The framework spec is the only
     durable place to define that lifecycle without locking platforms
     into a single implementation.
- **Supersession scope:** D-0031 **supersedes D-0005's scope-narrowing
  premise** ("the plugin needs no saga"), NOT D-0005's reasoning about
  partial-crew state. The blackboard remains the durable medium for
  per-lens slot state; D-0031 adds a parallel saga.json journal for
  outer-loop phase state. D-0005's text is preserved verbatim with a
  trailing pointer to D-0031.
- **Notes:** Adopts Hermes' existing state names + transitions verbatim
  (PREPARED, FANOUT_STARTED, BRANCH_RUNNING, etc.) as the spec source —
  cheaper than renaming a working implementation; the names are general,
  not Hermes-coined. Adds `PARTIAL_TIMEOUT` as the only new state
  (covers break-circuit + SIGTERM cases on both platforms). Adds a
  top-level `transitions: list[dict]` field that Hermes does not have
  today; Phase 3 of SAGA-PARITY-001 adds it to Hermes' `SagaRunState`.
  The plugin implementation is cooperative (LLM honors the contract);
  Hermes' is preemptive (Python runtime enforces). Same observable
  lifecycle, different enforcement — documented as a known platform
  asymmetry in REVIEW_SAGA.md.
- **Implementation:** SAGA-PARITY-001 plan (`plans/SAGA-PARITY-001-PLAN.md`)
  organizes 4 phases. This decision lands in Phase 1
  (`plans/SAGA-PARITY-001-PHASE-1-PLAN.md`). Phases 2-4 implement the
  contract on each platform.

---

## D-0030 — Partition `adversary` lens into `chaos_engineer` + `security_engineer`

- **Date:** 2026-06-05T10:00:00Z
- **PR:** CHAOS-SEC-SPLIT-001 (plan: `plans/CHAOS-SEC-SPLIT-001-PLAN.md`,
  merged PR #78; impl: this PR).
- **Decision:** Split the single `adversary` review-lens into two
  narrowly-scoped lenses aligned with intent — `chaos_engineer` (internal
  stability: failure paths, edge cases, race conditions, resource
  exhaustion, recovery) and `security_engineer` (external threats: trust
  boundaries, abuse cases, missing authn/authz/integrity controls,
  attack surface). Promote `agents/security-engineer.md` from transitive
  auditor sub-role to first-class crew lens; rename
  `agents/adversary.md` → `agents/chaos-engineer.md`. Per-layer crew
  weights redistributed in `REVIEW_CREWS.yaml` across 8 crews (all sums
  still 100). Plugin SemVer-major 0.4.5 → 0.5.0 (BREAKING — slot
  filenames change).
- **Why:** The single `adversary` lens conflated two structurally
  different review intents — what breaks the system *by accident*
  (chaos engineering) vs what an actor exploits *on purpose* (external
  threat modeling). Even the agent's own description called itself
  "devil's-advocate / chaos lens" while explicitly deferring half its
  scope ("deep security") to the `security_engineer` agent — which
  itself existed but wasn't a crew lens. Splitting gives: (a)
  traceable findings (verdict.json's `lens_scores` exposes which axis
  is failing), (b) targeted fixer dispatch (chaos validates with stress
  scenarios; security validates with threat models), (c) focused
  persona prompts instead of the 5-bucket grab-bag that deferred half
  its own scope.
- **Weight allocation method** (codified in `REVIEW_TEAM.md` §"Weight
  allocation rules"): chaos-heavy at BRD/EARS/BDD (reliability NFRs +
  failure scenarios dominate); security-heavy at ADR (architectural
  decisions encode trust boundaries); equal split at PRD/SPEC/TDD;
  chaos-only at IPLAN (security lives upstream in ADR/SPEC). Author and
  auditor weights untouched (auditor's "+security" sub-role moves out
  to the dedicated security_engineer lens).
- **Rationale propagation** — five places (REVIEW_CREWS.yaml comments,
  REVIEW_TEAM.md §Weight allocation rules, agent briefs' per-layer
  tables, audit-skill pseudo-text, CHANGELOG). Single source of truth
  is REVIEW_CREWS.yaml; conformance test enforces drift detection.
- **Hermes platform** (separate PR) already uses `chaos_engineer` as
  its internal runtime persona name with a translation layer back to
  framework's `adversary`. This spec change removes the translation;
  Hermes' migration is dropping the translation + adding the new
  `security_engineer` lens.

---

## D-0028 — One ORCHESTRATOR_TIMEOUT for every sub-team-dispatching skill

- **Date:** 2026-06-04T21:50:00Z
- **Context:** Three separate live re-verifications across BRD-RT-001 →
  002 → 003 revealed the same operational gap iteratively: any skill
  that internally dispatches a sub-team in team mode needs more than
  the default 600s `SKILL_TIMEOUT`. Each PR fixed one skill type at a
  time:
  - BRD-RT-002 (D-0026): `AUDIT_TIMEOUT=1200` for `doc-*-audit`
  - BRD-RT-003 (D-0027): `AUTOPILOT_TIMEOUT=1800` for `doc-*-autopilot`
  - BRD-RT-003 live re-verify exposed **G15**: `doc-*-fixer` also
    times out — same pattern, third skill class. Adding
    `FIXER_TIMEOUT` would have continued the per-skill-type
    proliferation.
- **Decision:** Generalise the three separate timeout variables into
  a single **`ORCHESTRATOR_TIMEOUT=1800s`** applied uniformly to every
  skill that dispatches a sub-team in team mode. Identified by name
  pattern in `tests/scripts/test-acceptance.sh:_pick_timeout_for`:
    `review-team` ∨ `doc-*-audit` ∨ `doc-*-autopilot` ∨ `doc-*-fixer`
  The globs are **anchored to the `doc-*-` prefix** (not bare
  `*-audit` etc.) so non-orchestrator utility skills with similar
  suffixes — notably `security-audit`, a single-pass leaf skill —
  keep the default `SKILL_TIMEOUT`. Inspection-confirmed: the
  intended set is exactly the 9 layer + CHG skills per pattern
  (BRD/PRD/EARS/BDD/ADR/SPEC/TDD/IPLAN/CHG × 3 operations + 1
  `review-team` = 28 orchestrator skills total).
  Leaf skills (no sub-team dispatch) keep the 600s `SKILL_TIMEOUT`.
  Phase 4.1 agents keep `AGENT_TIMEOUT=600s`. The per-layer outer cap
  (`MAX_LAYER_SEC=3600s`, from BRD-RT-003) remains as the wall-clock
  guard for cascades.
- **Why:**
  - **One concept, one knob.** All three orchestrator skills do the
    same kind of work (Task fan-out + synthesizer). They deserve the
    same budget. Live evidence: audit ~580-900s, autopilot ~1200-1500s,
    fixer ~500-700s. 1800s comfortably covers each.
  - **Pattern matches the architecture.** REVIEW_TEAM.md frames these
    as "operations on the blackboard" (Review, Create, Remediate).
    The plugin's binding has three skill types implementing those
    operations; they share orchestration shape, they should share
    timeout policy.
  - **Future-proofs PRD..IPLAN.** When PRD-RT-001 etc. propagate, the
    name-match catches their `doc-prd-audit` / `doc-prd-fixer` /
    `doc-prd-autopilot` automatically. No per-layer config changes
    needed.
  - **Closes G15** without adding another per-type variable. The
    iterative timeout-extension pattern (BRD-RT-002 → 003 → 004)
    stops here.
- **Scope:** Plugin v0.4.4 → v0.4.5. Framework spec unchanged. Three
  env vars removed (`AUDIT_TIMEOUT`, `AUTOPILOT_TIMEOUT`,
  `REVIEW_TEAM_TIMEOUT`); one introduced (`ORCHESTRATOR_TIMEOUT`).
  The change is backward-compat at the script's command-line surface:
  no flags or args change, only internal variable names. Operators
  who set these env vars externally need to migrate; live grep
  confirms no CI config references them.
- **Notes:** This is the architectural endpoint of the
  audit→autopilot→fixer timeout sequence. After BRD-RT-004,
  per-layer follow-ups land without inheriting any timeout-shape
  gaps — they only need the same name-pattern in their layer's
  SKILL.md text. The next BRD-RT verification run is expected to
  reach 6/6 pass criteria.

## D-0027 — Autopilot timeout matches its sub-team orchestration; multi-lens fixer findings dispatch all responsible lenses

- **Date:** 2026-06-04T13:30:00Z
- **Context:** BRD-RT-002's live verification (2026-06-04) produced 4 of
  6 pass criteria on the team-mode run. The 2 FAILs were operational —
  the architectural contract (verdict.json + cross-consumer consistency)
  verified end-to-end. Three gaps:
  - **G11**: `doc-brd-autopilot` in team mode now orchestrates a full
    `create → review → revise` loop inside one outer `claude -p`
    process. The default 600s `SKILL_TIMEOUT` killed it mid-iteration
    (exit 124). BRD-RT-002's `AUDIT_TIMEOUT=1200` name-match only
    covered `*-audit`.
  - **G12**: even with G11 fixed, a multi-iteration fix cycle (3 ×
    ~25 min) pushes a single layer's wall-clock past the 1800s
    per-layer cap.
  - **G13**: BRD-RT-001's fixer SKILL text said "dispatch *the*
    responsible lens" (singular). When a finding's `personas` array
    listed 2+ lenses (e.g. `[architect, business_analyst]`), the
    model bailed on lens validation instead of dispatching both.
    Result: fixer ran but wrote no `<persona>.fix_<N>.json` slots,
    leaving the team-mode patch-validation loop unverified.
- **Decision:**
  - Extend `_pick_timeout_for` in `tests/scripts/test-acceptance.sh` to
    match `*-autopilot` skills → new `AUTOPILOT_TIMEOUT=1800` (30 min).
  - Raise `MAX_LAYER_SEC` from 1800s to 3600s. Existing inner
    backstops (per-skill timeouts, `--cost-cap`, framework's
    `MAX_TOTAL_OUTPUT_TOKENS`) remain.
  - Codify `doc-brd-fixer/SKILL.md` Remediate Mode dispatch rules:
    single-lens finding → that lens; multi-lens finding → **all**
    listed lenses in parallel; orphan finding → layer's author lens
    as fallback.
  - Document `findings[].personas` field in `agents/synthesizer.md`
    schema (the synthesizer already writes it; the SKILL catches up).
- **Why:**
  - **G11/G12 are arithmetic.** The autopilot's nested loop has more
    work to do than a single audit, so it needs a longer timeout.
    Per-layer cap matches the worst-case ceiling (3 fix iterations at
    ~20 min each).
  - **G13 is prompt-correctness.** Singular "the responsible lens" is
    ambiguous when 2+ lenses co-own a finding. Explicit branching
    rules let the model dispatch correctly without inferring intent.
  - **Fallback-to-author** keeps every blocking finding validated
    even when synthesizer doesn't populate `personas` — avoiding
    silent skips while preserving lens-independence properties.
- **Scope:** Plugin v0.4.3 → v0.4.4. Framework spec unchanged. The
  fixer pattern + autopilot-timeout name-match are reusable verbatim
  for PRD-RT, EARS-RT, BDD-RT, ADR-RT, SPEC-RT, TDD-RT, IPLAN-RT —
  per-layer follow-ups inherit the corrected ops.
- **Notes:** Live re-verification (~$7, 25-30 min) is expected to take
  Run #1's pass-criteria from 4/6 to 6/6 on the BRD layer. The
  url-shortener BRD's BA-001 finding (visit-count contradiction, P1
  with `[architect, business_analyst]` personas) is now the live test
  case for multi-lens dispatch.

## D-0026 — Synthesizer writes a structured `verdict.json`; consumers parse JSON, not Markdown

- **Date:** 2026-06-03T18:25:00Z
- **Context:** BRD-RT-001's live verification runs surfaced a critical
  consistency bug: the doc-brd-audit skill's stdout response
  (audit_score: 92, PASS) diverged from the .aidoc/audit/01_BRD-audit.md
  it wrote to disk (Content score: 83, FAIL). Same invocation, two
  verdicts. Every downstream consumer (driver script, autopilot's revise
  loop) read stdout, not the written report — so team-mode FAIL
  verdicts never triggered fixer cycles. The autopilot's create→review→
  revise loop was structurally broken by the wrong source-of-truth
  read.
- **Decision:** The synthesizer subagent writes a flat, deterministic
  `verdict.json` companion alongside `report.md` at
  `.aidoc/review/<NN>_<LAYER>/<artifact-id>/verdict.json`. Every
  downstream verdict consumer — `doc-*-audit` SKILL's stdout response,
  `tests/scripts/test-acceptance.sh:parse_audit_score`, the
  autopilot's revise loop, `doc-*-fixer`'s blocking-findings list —
  reads from this JSON. Markdown `report.md` remains the human
  narrative; it is **never the machine parse target**. When the two
  files disagree, the JSON wins (it is what consumers parse).
- **Why:**
  - **Markdown is fragile.** Heading text, table format, value
    placement can drift between runs. Asking a model to extract values
    from prose shifts fragility from one place to another.
  - **JSON is deterministic.** Schema-checkable, parseable by
    `json.loads()`, and the synthesizer's reduce already produces the
    underlying values per `REVIEW_TEAM.md` §"Synthesis = reduce +
    narrative".
  - **Verdict-chain consistency at every consumer.** With one
    authoritative source (verdict.json), the driver, audit skill,
    autopilot, and fixer cannot disagree about gate state. The
    audit's stdout response mirrors the JSON key-for-key.
  - **Belt-and-suspenders.** Driver script's `parse_audit_score`
    cross-checks stdout against verdict.json; logs a warning and
    prefers JSON on drift. Catches future model-output divergence
    without depending on perfect prompt compliance.
- **Scope:** Plugin v0.4.2 → v0.4.3 binds the new mechanism at the BRD
  layer (BRD-RT-002). Per-layer follow-ups (PRD-RT, EARS-RT, etc.)
  copy the pattern verbatim. No framework spec change — `REVIEW_TEAM.md`
  already specifies the synthesizer's deterministic reduce; this is
  the plugin's binding catching up to the spec.
- **Notes:** The `<BRD-id>` path segment is codified as the **short
  artifact ID** (`BRD-01`), not the nested folder name
  (`BRD-01_url_shortener`) — BRD-RT-001's implementation already chose
  the short form. The `MAX_LAYER_SEC` cap rose 900s → 1800s to fit
  team-mode runs; a new `AUDIT_TIMEOUT=1200s` applies via name-match
  to any `doc-*-audit` skill. The always-on `single_pass` advisory
  note in audit reports is informational; it doesn't change PASS/FAIL
  outcome — projects making the cost-vs-rigor tradeoff via
  `ADAPTATION_SURFACE.yaml` are honored.

## D-0025 — Project profile is a delta, not a snapshot

- **Date:** 2026-06-03T14:14:42Z
- **Context:** In BRD-RT-001 (D-0024), the acceptance suite's profile
  bootstrap copied `framework/governance/REVIEW_CREWS.yaml` byte-for-byte
  into `.aidoc/profile.yaml`. That produced a 60-line file where every
  line was potentially an override or a stale default, with no way to
  distinguish them. Two problems followed: the framework couldn't evolve
  crew/persona defaults without breaking older projects (frozen
  snapshots), and profile readers couldn't tell what was customised.
- **Decision:** Project profiles are **override-only deltas**.
  `framework/governance/PROFILE-TEMPLATE.yaml` is the new bootstrap
  skeleton — a metadata-only file with every adaptation knob commented
  out. Unset keys fall through to framework defaults via the precedence
  chain `framework defaults < user-global seed < project profile`
  documented in `framework/governance/ADAPTATION.md` since v0.11.0.
- **Why:**
  - **Safe framework evolution.** If `REVIEW_CREWS.yaml` re-weights a
    crew in v0.12, existing projects pick up the change automatically —
    no migration required.
  - **Readable profiles.** A reader of `.aidoc/profile.yaml` sees only
    what the project chose to override; framework defaults stay where
    they belong.
  - **Operationalises the spec.** `ADAPTATION.md` already documents the
    precedence chain since the ADAPT work (D-0019); this decision wires
    it into the engine.
  - **Closed-surface conformance.** Out-of-surface keys in a profile
    would be silently ignored by a conforming engine — flagging them as
    a conformance violation is an authoring-mistake guard. New test
    `tests/conformance/platforms/test_profile_schema.py`.
- **Scope:** Plugin v0.4.1 → v0.4.2 binds the new mechanism. Framework
  spec **0.11.2 → 0.11.3** (additive — new template file). No existing
  key removed; every existing profile continues to parse. Backward-compat
  for projects with populated profiles: any present key is honored as an
  override; fallback only kicks in for absent keys.
- **Notes:** A full layered config-merge engine with a user-global seed
  file (the ADAPTATION.md "middle" precedence layer) is deferred until
  the override-only delta proves insufficient — YAGNI for current scale.
  Per-layer review-team wiring beyond BRD will consume the resolved
  profile transparently in PRD-RT-001 etc. The crews/persona definitions
  themselves remain framework-level only (not in the closed adaptation
  surface), so projects can't override the crew composition — they can
  only choose `team` vs `single_pass` and tune thresholds/toggles.

## D-0024 — BRD-layer team-mode dispatcher placement: at `doc-*-audit`, not at a higher orchestrator

- **Date:** 2026-06-03T13:30:51Z
- **Context:** The framework spec
  (`framework/governance/REVIEW_TEAM.md`,
  `framework/governance/REVIEW_CREWS.yaml`) endorses `independent`
  parallel-subagent review as the default mode at gates. The plugin's
  `platforms/claude-code-plugin/skills/review-team/SKILL.md` correctly
  describes Claude Code `Task`-tool fan-out as the mechanism, but the
  per-layer `doc-*-audit` skills did not invoke it — they ran
  single-pass content reviews in one model context. BRD-RT-001 (see
  `plans/BRD-REVIEW-TEAM-PLAN.md`) wires the fan-out at the BRD layer
  as a proof-of-concept; a design decision is needed on **which skill
  owns the dispatcher**.
- **Decision:** The dispatcher of the persona crew lives in
  `doc-<layer>-audit` (for review/gate) and `doc-<layer>-autopilot`
  (for the create→review→revise loop). **Not** in a higher orchestrator
  skill, **not** in `pm-orchestrator`, **not** as a separate
  pre-cascade phase in the acceptance suite.
- **Why:**
  - `review-team/SKILL.md:108` already designates this:
    "`pm-orchestrator` (or the invoking `doc-<layer>-audit`) is the
    dispatcher." This codifies that the audit skill is one valid owner;
    we pick it as **the** owner for per-layer gate-time review.
  - Per-layer dispatch at the gate matches `REVIEW_REMEDIATION_FLOW.md`
    trigger points (`on_gate_fail`, `pre_promotion`, `pre_merge`). A
    chain-wide orchestrator can't catch errors at the per-layer gate
    they originated at — the create→review→revise loop only converges
    when the review happens at the layer being authored.
  - The Phase 3 chain-wide `review-team` invocation in
    `tests/scripts/test-acceptance.sh:1239` continues to exist for
    cross-cutting review across the produced 8-layer chain. The two are
    complementary, not duplicative.
  - Keeping the dispatcher local to the audit skill preserves the
    "structured slots, never peer-to-peer" rule from `REVIEW_TEAM.md`
    §Blackboard — every contract between skills is the slot path +
    persona-output schema, not skill-internal logic.
- **Scope:** This decision is the rule for **every layer**'s team-mode
  wiring. BRD-RT-001 implements it for BRD; PRD-RT, EARS-RT, BDD-RT,
  ADR-RT, SPEC-RT, TDD-RT, IPLAN-RT will copy the pattern verbatim.
- **Notes:** This is a plugin-platform decision; it does not change the
  framework spec. The plugin-spec contract (consume `framework/`
  templates + governance, no platform names in `framework/**`) is
  preserved. Plugin v0.4.0 → v0.4.1.

## D-0023 — Domain & product identity: one brand, path-based per-integration pages

- **Date:** 2026-05-27T00:00:00Z
- **Context:** Three registered domains (`aidoc-flow.com`, `.ai`, `.io`) and an
  open question of how to host the Claude Code plugin's "home" — plus the
  realization that the plugin is **one of a family** of integrations (a Claude
  Code plugin, possibly a Codex plugin, a VS Code extension, …) all consuming the
  one engine-agnostic framework spec, alongside Hermes (the MCP surface).
- **Decision:**
  1. **One canonical brand domain — `aidoc-flow.com`** (company + product +
     marketing). The other TLDs are defensive assets: `aidoc-flow.io` and a
     non-canonical `.ai` **301-redirect** to it.
  2. **Integrations are a category, addressed path-based** — `aidoc-flow.com/claude-code`,
     `/codex`, `/vscode`, `/hermes` (framework docs + install guides under
     `docs.aidoc-flow.com`). **No dedicated domain or top-level subdomain per
     integration** (`claude.`/`plugin.` were rejected — engine-coupling + the
     "Claude" trademark, and there will be several integrations). A subdomain is
     promoted for a single integration only if it grows into a standalone property.
  3. **`aidoc-flow.ai` is reserved for the agents / A2A-protocol / cloud-hosting
     product** — not spent on a dev-tool plugin (mismatched fit + brand
     fragmentation).
  4. **Plugin identity** (applied to `platforms/claude-code-plugin/.claude-plugin/plugin.json`):
     `author = { name: "AI Doc Flow", email: plugins@aidoc-flow.com, url:
     https://aidoc-flow.com }`; `homepage = https://aidoc-flow.com/claude-code`;
     `repository` stays the GitHub monorepo (source ≠ product page). Replaces the
     P1 neutral placeholder.
- **Why:** Consolidating brand/SEO/trust + cross-property auth on one registrable
  domain beats fragmenting across three TLDs or minting a subdomain per surface;
  path-based integration pages scale to N integrations with zero new DNS/TLS and
  one SEO surface. Distribution channels still differ (Claude Code marketplace /
  VS Code Marketplace / Codex), but the *website* is unified and an
  `/integrations` hub links out to each.
- **Notes / P2 publish gate:** the site and the `plugins@aidoc-flow.com` mailbox
  are **not yet live** — before marketplace **submission** (P2), verify `homepage`
  resolves and the role mailbox receives mail. The public mirror's
  `marketplace.json` `owner` uses this company/role identity; the monorepo-root
  `.claude-plugin/marketplace.json` owner is left as the personal dev identity
  until the mirror is created.

---

## D-0022 — Vendor the framework spec into the plugin (shippability exception to D-0013)

- **Date:** 2026-05-27T00:00:00Z
- **Context:** The Claude Code plugin references **47 distinct `framework/…`
  paths across 64 files**, but Claude Code copies **only the plugin directory**
  to its cache on install — so every literal `framework/<path>` reference (which
  only ever resolved from the monorepo root) breaks for every installed user.
  The plugin is therefore not installable as shipped. Full design + 3 review
  passes in `plans/PLUGIN-MARKETPLACE-PLAN.md`.
- **Decision:** The plugin **vendors** the spec subtrees it consumes —
  `framework/{layers,governance,registry}` → `platforms/claude-code-plugin/framework/{…}`,
  **byte-identical, generated** by a sync script that extends the existing
  `tools/sdd_doc_lint/sync-vendored.sh` pattern. Plugin references are repointed
  to `${CLAUDE_PLUGIN_ROOT}/framework/…` (the documented runtime anchor for a
  plugin's own cached files). This is the sanctioned **shippability exception**
  to D-0013: the monorepo `framework/` stays the **single source of truth**; the
  plugin's bundled `framework/` is **generated and never hand-edited**.
- **Why:** Identical rationale to the already-vendored `sdd_doc_lint` — a plugin
  must be self-contained to install/run from a marketplace cache, but the spec
  must stay singly-owned to avoid the dual-ownership drift D-0013 was written to
  prevent. A **drift guard** (a conformance test mirroring
  `test_doc_lint_vendoring.py`) asserts the vendored bundle is byte-identical to
  canonical, so the copy can never silently diverge; a future `framework/` edit
  re-syncs the bundle (wired into the GATE-SPEC / spec-change checklist) and the
  drift guard is the backstop. The bundle is a snapshot pinned to the plugin's
  `FRAMEWORK_SPEC_VERSION`.
- **Notes:** Vendored docs' *own* internal cross-references stay
  monorepo-relative (repointing them would break byte-identity) and are treated
  as **advisory** — the resolution gate enforces only the *plugin's* refs
  (skills/agents/commands/docs/README), not the links inside vendored docs. A
  bundled doc that *hard-depends* on a framework file outside
  `{layers,governance,registry}` adds that file to the vendored set rather than
  repointing it. Repo-root `framework/` and the dev tooling that reads it are
  unaffected.

---

## D-0005 — No saga for the plugin review runner

- **Date:** 2026-05-26T00:00:00Z
- **Decision:** The Claude Code plugin's review-team runner will **not** port
  Hermes' saga (journal / compensation / retry state-machine). It instead relies on
  the git-ignored `.aidoc/review/<artifact>/<persona>.json` blackboard for durable
  per-persona slots (resume = re-dispatch only the missing lenses) and the
  `coverage`/`quorum` policy for partial-crew degradation
  (→ low-confidence / human-review).
- **Why:** The saga exists to coordinate Hermes' *external* LLM-API fan-out, which
  can fail/timeout mid-flight and needs durable orchestration + compensation. The
  plugin's agents are Claude Code `Task` subagents whose lifecycle the harness
  manages — there is nothing to journal or compensate. The blackboard already gives
  the durable-slot/resume property and coverage/quorum gives graceful degradation,
  so a saga would be over-engineering and would fight the runtime.
- **Notes:** Consistent with the engine-agnostic spec (shared contract, per-engine
  "how") and AGENT-TEAM plan **D9**. Locks the Phase 2 direction
  (blackboard-with-coverage, not a saga port).
- **Superseded in scope** by **D-0031** (2026-06-05). D-0005's
  blackboard-for-crew-state reasoning remains authoritative; D-0031
  extends the contract with an outer-loop saga.json journal to cover
  partial outer-loop state. See `framework/governance/REVIEW_SAGA.md`
  for the lifecycle contract.

---

## D-0021 — pre-commit hooks (lint / format / security / pip-audit) + repo cleanup

- **Date:** 2026-05-24
- **Context:** Adopt automated pre-commit checks across the repo (linter errors,
  security, dependency audit) per best practices.
- **Decisions:**
  1. **Tooling:** the `pre-commit` framework. Hooks: hygiene (pre-commit-hooks),
     **ruff** + ruff-format (Python = `platforms/hermes` + `tests` only), **bandit**
     SAST (gated **medium+** — all current findings are low), **markdownlint**,
     **yamllint**, **detect-secrets** (baseline), **pip-audit** (`manual` stage —
     heavy/network, runs in CI not every commit), and a **local conformance** hook.
  2. **Pragmatic rule sets, not raw defaults** (best practice for a doc-heavy
     brownfield repo): markdownlint disables stylistic rules (MD013 line-length,
     MD060 table-style, …); ruff selects E/F/W/I/UP; yamllint lenient.
  3. **Scope:** `legacy/` + **Hermes vendored/parsed content** (`agent-skills/`,
     `prompts/`, `skills/`) excluded from markdownlint — restructuring
     code-parsed prompt headers is risky and out of scope.
  4. **Full cleanup applied** (user choice): markdownlint `--fix` (321 files) +
     ruff safe-fix/format (127), then hand-fixed the residual — incl. the genuine
     pre-existing Hermes findings (F821 missing TYPE_CHECKING import, F823
     redundant local `import os`, UP042 `str,Enum`→`StrEnum` — behavior verified),
     malformed tables, hard tabs, a double-H1, and blockquote/blank-line edges.
     `pre-commit run --all-files` is green; conformance + 383 testable Hermes
     tests pass (the 2 failures are the standing `mcp`-SDK-missing collection
     errors). Replaced the stale `ucx_hermes`-era `repos: []` placeholder.
  5. **CI:** `.github/workflows/pre-commit.yml` runs all hooks + `pip-audit`.
- **Status — DONE (2026-05-24):** branch `claude/precommit-hooks`. Contributors
  enable locally with `pip install pre-commit && pre-commit install`; pin refresh
  via `pre-commit autoupdate`.

## D-0020 — GATE-SPEC: the framework-spec change gate (CHG-D1)

- **Date:** 2026-05-23T00:00:00Z
- **Context:** ROADMAP CHG-D1 — re-introduce change management as **skills +
  CI/CD**, both platforms. The five existing gates (GATE-01/03/06/08/CODE) all
  govern a project's **artifact instances** along the BRD→Code chain; none
  governed a change to the **`framework/` spec itself**. That gap was what
  `knowledge-extractor`'s spec→CHG drafts were stamped *blocked* on (D-0019,
  ADAPT-0). Full design + 2 review passes in `plans/CHG-D1-PLAN.md`.
- **Decisions:**
  1. **GATE-SPEC is a *meta* gate, orthogonal to the artifact cascade.** It
     governs the shared contract that defines the layers (templates, governance,
     registry, VERSION) — the `docs/PROJECT.md` §6 "Process" role. It has no
     GATE-03/06/08 successor; a passed spec change instead obliges every platform
     to re-declare `FRAMEWORK_SPEC_VERSION` and re-pass conformance. Selected by
     **target** (the change edits `framework/`), not by artifact layer.
  2. **Three-way enforcer split** (the ROADMAP CHG-D1 model). Record-level
     E001–E004 (provenance, `semver_impact`+major⇒C3, never-C1, C3-approval) →
     the platform's record validator (plugin `gate-check`/`doc-chg`, Hermes
     `chg_rules.py`). Diff-aware E005 (VERSION bump) + E008 (CHANGELOG) → CI
     (`tests/chg/spec_gate.py`). Static E006 (spec-version match) + E007 (suite
     green) → the shared conformance suite. The **human** approval (E004) is
     protected-branch review — **a skill never self-approves**.
  3. **`major`⇒C3 is one-directional.** A breaking spec change must be C3;
     `minor`/`patch` may be C2. An additive change (a new optional knob, a new
     gate) reaches both platforms yet is not breaking — so it is not forced to
     C3. (GATE-SPEC's own introduction is `minor`/C2.)
  4. **New `change_source: spec` + `semver_impact` field** added to
     CHG-TEMPLATE (additive, backward-compatible; Hermes validation is
     `.get`-based, no strict key-schema to violate).
  5. **CI tooling is engine-agnostic and lives under `tests/`**, not
     `framework/` (the spec ships no runtime). The workflow stages at
     `plans/workflows-pending/chg-gate.yml` — the in-container app can't push
     `.github/workflows/**` (the standing `workflows`-permission restriction).
  6. **GATE-SPEC's introduction lands under interim PR-review controls** — a gate
     cannot gate its own introduction (mirrors how D-0019's spec doc landed).
- **Status — DONE (2026-05-23):** landed across 5 commits on
  `claude/skill-revision`. Framework spec **0.2.0 → 0.3.0** (minor; + both
  `FRAMEWORK_SPEC_VERSION` + all 54 skills' `framework_spec_version`).
  Conformance **38 → 43**; Hermes CHG unit tests 8/8 (full validation suite
  green bar the pre-existing `mcp`-SDK-missing collection errors); `plm_lint`
  clean. **Follow-up: CHG-D2** — record this as a formal `framework/governance/`
  decision (now actionable). **User-only:** relocate `plans/workflows-pending/
  chg-gate.yml` → `.github/workflows/`; configure branch protection on
  `framework/**` (the human-approval half).

## D-0019 — Project adaptation overlay + knowledge extractor (ADAPT)

- **Date:** 2026-05-23T17:50:00Z
- **Context:** Give a consuming project a bounded way to adapt the SDD flow
  without forking, plus a manual path to promote proven adaptations upward.
  Full design + review (Pass 1–4) in `plans/ADAPT-PLAN.md`.
- **Decisions:**
  1. **Promotion routes by governance owner** (corrects the original draft). Per
     `docs/PROJECT.md` §6: `framework/` spec changes are CHG-governed; platform
     (skill/tool) changes are ordinary PRs, *not* CHG. The knowledge-extractor
     classifies each candidate and routes spec→CHG / tool→PR.
  2. **ADAPT-0 — defer the spec→CHG path (option b).** The spec-change CHG gate
     is unbuilt (ROADMAP CHG-D1). v1 ships the tool-PR promotion path
     (plugin-only reach); spec-level candidates are drafted but flagged
     "blocked — needs CHG-D1". Building CHG-D1 is an out-of-scope follow-up.
  3. **Surface is closed + declarative** (`framework/governance/ADAPTATION.md`
     - machine-readable `ADAPTATION_SURFACE.yaml`). **v1 = 4 knobs**
     (`active_layers`, `section_toggles`, `audit_threshold`, `glossary`);
     **`id_format` deferred** pending an `ID_NAMING_STANDARDS.md` review to
     enumerate genuinely-selectable conventions (narrow-surface principle —
     don't invent options).
  4. **`audit_threshold` is raise-only** — a project may only make a layer's
     quality gate stricter, never lower it (preserves CLAUDE.md "never weaken a
     check"). The Tier-1 score (default 90) is the real model; the CHG
     gate-approval model has no score and is untouched.
  5. **Skippable layers = `[BDD, ADR]`** (the two non-C4 bridge layers);
     `[BRD, PRD, EARS, SPEC, TDD, IPLAN]` mandatory. A **cascade rule** removes a
     disabled layer from downstream `required_tags`/`can_reference` so
     traceability stays consistent. Conservative + reviewable; lives in the
     adaptation surface, not the core `LAYER_REGISTRY.yaml` (`optional` there is
     a separate default-flow concern).
  6. **User-global profile is an authoring-time seed, not a runtime input**
     (reproducibility). Runtime (incl. audits) reads the version-controlled
     project profile `.aidoc/profile.yaml` only; `~/.aidoc/profile.yaml` is
     merged into it at authoring time. Same precedence semantics, merge moved
     earlier so CI audits identically.
  7. **The adapting set is wider than the base skills** — `-audit`/`-autopilot`
     must honor the profile or they false-fail adapted docs; `trace-check`,
     `project-init`, `project-adopt` consult `active_layers`. (Implemented in a
     later ADAPT-A increment.)
- **Status — ADAPT complete (2026-05-23):** landed across 7 commits on
  `claude/skill-revision`. ADAPT-A: `framework/governance/ADAPTATION.md` +
  `ADAPTATION_SURFACE.yaml` (4-knob closed surface); `adapts:` + consult-clause
  wired into the 35-skill adapting set; `project-profile` skill; full doc
  registration. ADAPT-B: `ADAPTATION.md` §7 learnings-log convention +
  `knowledge-extractor` skill (owner-routing; spec→CHG draft stamped blocked on
  the unbuilt CHG-D1 gate; guidance→PR). **Single feature-close version bump**
  (sequencing refinement vs the plan's per-step bump): `framework/VERSION` +
  both platform `FRAMEWORK_SPEC_VERSION` `0.1.0 → 0.2.0`, and all 54 plugin
  skills' `framework_spec_version` (user decision: bump everything). Conformance
  **33 → 37** (governance surface well-formedness, `adapts ⊆ surface` +
  authority-ref + ≥35-wired, framework leakage guard); `plm_lint` clean.
  **Deferred (CHG-D1):** the spec→CHG promotion gate — until built, spec-level
  promotions are drafted but cannot be gated.

## D-0018 — Cut Claude Code plugin `v0.2.0`; add a repo-root plugin marketplace

- **Date:** 2026-05-23T00:00:00Z
- **Context:** The plugin's last tag (`claude-code-plugin/v0.1.0`) predates the
  8-layer migration; everything since (124-skill 8-layer corpus, 9-agent roster,
  `project-mngt` parking) sat in CHANGELOG `[Unreleased]`. There was also no way
  to *install* the plugin — only a per-plugin `plugin.json`, no marketplace
  manifest.
- **Decisions:**
  1. **Version `0.2.0` (minor), not `1.0.0`.** The 8-layer migration is a large
     feature jump but the skill/command surface may still move; staying pre-1.0
     signals that. Bumped `platforms/claude-code-plugin/VERSION` + `plugin.json`
     `version`. `FRAMEWORK_SPEC_VERSION` stays `0.1.0` (independent streams,
     `docs/PROJECT.md` §2; the conformance test checks `FRAMEWORK_SPEC_VERSION`
     against `framework/VERSION`, not the platform version — verified green).
  2. **Repo-root `.claude-plugin/marketplace.json`** (schema confirmed against
     code.claude.com/docs): marketplace `name: aidoc-flow-framework` (matches the
     repo; reads as `aidoc-flow@aidoc-flow-framework` on install) → plugin
     `aidoc-flow` via relative subdir `source: ./platforms/claude-code-plugin`.
     `version`/`description` set on the entry (optional, not inherited). Install
     command added to root + plugin READMEs.
  3. **Tag deferred to the user.** Annotated `claude-code-plugin/v0.2.0` is cut
     locally on the release commit; the in-container push 403s (5th occurrence
     of the `refs/tags/*` restriction), so the user pushes it from a local clone
     — alongside merging this branch into `main` and relocating CI.
- **Conformance:** 32/32. Recorded in plugin CHANGELOG `[0.2.0]`,
  `docs/TAGGING.md`, and `plans/HANDOFF.md`.

## D-0017 — Park `project-mngt` as legacy (pending review); pull it from the shipped plugin

- **Date:** 2026-05-22T00:00:00Z
- **Context:** `project-mngt` is a generic MVP/MMP/MMR planning *methodology*
  skill (frontmatter `layer: null`, domain-generic `REQ-NN` requirement IDs) —
  it teaches HOW to plan, not an SDD-layer artifact. It does not cleanly fit the
  8-layer engine and needs re-evaluation for fit/placement, so it should not
  ship with the plugin in the meantime.
- **Decision / actions:**
  1. **Parked**, not deleted: moved `platforms/claude-code-plugin/skills/project-mngt/`
     → `legacy/claude-code-plugin/project-mngt/` (Claude Code auto-discovers
     everything under `skills/`, so leaving `skills/` is the only reliable way to
     stop shipping it). Frontmatter `development_status: active → legacy`; park
     rationale + un-park procedure in `legacy/claude-code-plugin/README.md`.
  2. **Neutralized all inbound references** in the shipped surface: `README`
     skill table + prose; `skill-recommender` intent-map + catalog rows;
     `adr-roadmap` (SKILL + quickref) "use instead"/"combine"/related-skills;
     `doc-flow`, `trace-check`, `mermaid-gen`, `workflow-optimizer` cross-links;
     `pm-orchestrator` + `agents/README` rosters. Where a recommendation pointed
     at it for requirement planning, repointed to the requirements layers
     (`doc-brd`/`doc-prd`/`doc-ears`).
  3. **Dropped** the now-dead `("legacy-doc-ref", "project-mngt")` `plm_lint`
     exception (the skill no longer lives under any scanned scope).
  4. **Corrected** the plugin `README` skill counts to the as-built totals
     (112 `doc-*` + 12 non-doc = 124). The migration's documented 142 → 125
     reduction (plugin CHANGELOG `[Unreleased]`) had never been reflected in the
     README; parking `project-mngt` then took 125 → 124.
- **Skill count:** 125 → 124. Conformance unaffected (no count assertion; the
  parked tree is outside `skills/`, `agents/`, `commands/`).
- **Follow-up (review later):** decide whether `project-mngt` is reworked into
  an IPLAN-layer (Layer 8) helper, kept as an out-of-band methodology doc, or
  retired. Tracked in `plans/MIGRATION_TODO.md`.
- **Resolution — RETIRED (2026-05-27):** removed `legacy/claude-code-plugin/project-mngt/`.
  Rationale: it is a generic **MVP/MMP/MMR product/release-planning methodology**
  (`layer: null`), not an SDD-layer artifact; its phased-roadmap function overlaps
  `adr-roadmap` and its execution-planning overlaps the terminal `doc-iplan`, so the
  in-scope slices are already covered; reviving it as-is would reintroduce the banned
  sequential `PLAN-NNN`/`REQ-NN`/`TASK-NNN` IDs; and release-staging is out of v1's
  software/devops scope (D-0012). The methodology is a candidate for a **post-v1.0
  domain/methodology profile** (ROADMAP "Domain profiles") and remains recoverable
  from git history + the `legacy-ucx-v3.2-read-only` branch if revived. No shipped
  surface referenced it (its inbound refs were neutralized when parked), so
  conformance is unaffected.

## D-0016 — Post-migration gap audit: fix plugin-surface residue + harden the gate (not bare-token/prose patterns)

- **Date:** 2026-05-22T03:10:00Z
- **Context:** A post-completion review (cross-checked against the v3.2 source
  on `legacy-ucx-v3.2-read-only`) confirmed the **framework** 8-layer model
  correctly absorbs the deprecated SYS/REQ/CTR layers (SYS→SPEC C4-Component,
  CTR→SPEC interfaces, REQ→EARS atomic-testable). But `plm_lint`'s blind spots
  (it scanned only `skills/`, and its element-code pattern needs a trailing
  `.digit`) let deprecated-layer residue survive in the **plugin surface**:
  `agents/requirements-analyst.md` still modeled REQ as a live layer
  (`BRD→PRD→EARS→REQ→SPEC`, `docs/REQ/`, `REQ-NNN`, 3-segment IDs);
  `skills/trace-check/examples/example_validation_report.md` traced to
  `SYS-002`/`REQ-001`; `doc-validator` linked a non-existent
  `../doc-brd-validator/`.
- **Decision / actions:**
  1. **Fixed** all three: requirements-analyst's lane now terminates at EARS
     (atomic-testable requirements = EARS, per v3.2 REQ→EARS mapping), 4-segment
     IDs, `docs/03_EARS/`; the trace-check example rewritten to 8-layer
     traceability + 2-digit doc refs; the doc-validator BRD row points at the
     existing `../doc-brd-audit/` (doc-brd ships no validator).
  2. **Hardened `plm_lint`:** scan scope extended to `agents/` + `commands/`
     (always enforced); added `legacy-doc-ref` (dash refs `SYS-002`…),
     `legacy-layer-dir` (`06_SYS`/`10_TSPEC`…), and a **context-aware**
     `legacy-3seg-id` pattern (skips lines marked ❌/legacy/→/reject so
     validators' "wrong-format" teaching examples don't false-fail). Already
     wired into conformance via `test_plm_lint.py` (suite stays 32).
- **Deliberately NOT added:** bare-token (`SYS`/`REQ`/`TSPEC`) and N-layer prose
  (`12-layer`) patterns — these occur legitimately in Version-History changelog
  rows across migrated skills; flagging them would force per-file exceptions or
  false failures. The 3-seg line-context heuristic is the safe middle ground.
- **`project-mngt` kept as-is:** it uses domain-generic `REQ-NN` requirement IDs
  (a general MVP/MMP/MMR methodology skill, not SDD-layer-specific); excepted
  from `legacy-doc-ref` in the checker. `doc-naming` is excepted from
  `legacy-3seg-id` (it is the ID-format teaching authority).

## D-0015 — Plugin SPEC-/test-subtype skill families: migrate & keep as helpers (PLM-B4/B5)

- **Date:** 2026-05-22T01:30:00Z
- **Decision:** The plugin's SPEC-subtype families
  (`doc-cspec/dspec/uxspec/riskspec/procspec`) and test-subtype families
  (`doc-utest/itest/stest/ftest/ptest/sectest`) are **kept as plugin-only
  authoring helpers** under SPEC (Layer 6) and TDD (Layer 7) respectively,
  and their bodies are **migrated to the 8-layer model** (paths, IDs,
  chains) like every other family — they are NOT retired and NOT folded
  into `doc-spec`/`doc-tdd`.
- **Why:** The framework defines SPEC and TDD as single unified templates
  with no subtypes, but the *plugin* is free to ship finer-grained
  authoring skills as a value-add (its per-operation granularity is a
  documented Plugin advantage in `docs/PARITY.md`). Retiring them would be
  a real capability loss; folding them into two skills would lose the
  per-subtype slash-commands users rely on. Keeping them as helpers under
  the canonical layers preserves capability while staying spec-conformant
  (they reference, not redefine, the L6/L7 contracts).
- **Consequence:** PLM-B4 migrates `doc-spec` + the 5 SPEC-subtype
  families; PLM-B5 migrates the 6 test-subtype families. Each subtype skill
  must position itself as a specialization of its parent layer (SPEC L6 /
  TDD L7) and reference the single framework template, not a legacy subtype
  template or element-code.

- **Date:** 2026-05-21T05:50:00Z (revised same day — see Note)
- **Decision:** Preserve the pristine pre-migration `ucx_framework`
  project (original root layout) as the **protected, read-only branch
  `legacy-ucx-v3.2-read-only`** (created off `main` at commit `491e8db`,
  byte-identical; branch protection enabled). **Then**, at the Phase 5
  cutover, remove `legacy/` and root `.claude/` from the working branch
  (→ new `main`) so the shipped project is clean. The archive branch +
  git history are the durable record.
- **Why:** User directive — preserve everything ("do not remove legacy
  files"; ensure root `.claude/` is captured too), **then** clean up the
  working branch ("keeping legacy files in [a] separated archived branch
  for future reference then clean up current branch"). A protected branch
  is a more discoverable, enforceably-immutable archive than relying on
  post-deletion git history; with it in place the working-branch removals
  lose nothing substantive.
- **Safety (verified before restoring the removals):** the archive branch
  contains all 7 legacy trees (`ucx_flow_v3`, `ucx_hermes`, `mcp_ucx`,
  `ai_dev_ssd_flow_v2`, `ucx_kb`, `ucx_knowledge`, `hermes_agent_skills`)
  and root `.claude/`. **Caveat:** the archive holds the *pre-migration*
  `.claude/` (236 files, no hooks); the working branch's *migration-era*
  `.claude/` (240 files, incl. the 3 migration hooks) survives removal
  only in the working branch's git history — acceptable, as those hooks
  are obsolete migration scaffolding and the skills were productized into
  `platforms/claude-code-plugin/`.
- **Aligns with** the original cutover policy ("`legacy/` removed /
  archived at the Phase 5 cutover" — `docs/REPO_STRUCTURE.md`,
  `docs/PROJECT.md` §4, `ROADMAP.md` Phase 5, `CLAUDE.md`) — now realised
  via the archive branch rather than history-only deletion. P5-T4
  reconciles those docs to name the `legacy-ucx-v3.2-read-only` branch as
  the archive.
- **Consequence:** Phase 5 keeps its two removal tasks **restored**
  (P5-T2 remove `legacy/`, P5-T3 remove root `.claude/`), each gated on
  the archive branch existing (it does) + explicit confirmation at
  execution; root `.claude/` removal is sequenced **late** (it disables
  the session's own hooks). `CLAUDE.md` is **rewritten** to post-migration
  memory in P5-T4 (it's a root file, not under `.claude/`, so it survives
  the `.claude/` removal).
- **Note (revision):** an interim reading of the user's directives
  (recorded briefly the same day) had this as "retain `legacy/` + root
  `.claude/` in-tree, no removals." Once the protected archive branch was
  created and confirmed, the user restored the original archive-then-clean
  intent; this entry reflects the final decision.

## D-0013 — Framework templates are the single source of truth; platforms consume, not duplicate

- **Date:** 2026-05-19T14:50:00Z
- **Decision:** The 8 layer document templates
  (`<X>-TEMPLATE.yaml` for BRD/PRD/EARS/BDD/ADR/SPEC/TDD/IPLAN) live
  exclusively in `framework/layers/<NN>_<X>/`. Platforms do **not** ship
  their own copies. Hermes' legacy `templates/` directory is dropped at the
  port (P2-T1 Q3); the platform's runtime template-loader reads from
  `framework/layers/`. Any platform-specific runtime data the legacy
  templates carried (e.g. `server: ucx_hermes`, `tool: sdd_validate`) moves
  to platform-side config — never into the engine-agnostic templates.
- **Why:** The framework is engine-agnostic by D-0006 and the conformance
  spec-hygiene tests. Embedding engine names in shared templates violates
  that contract. The legacy duplicate had already drifted from the framework
  by exactly that engine-named block (audit §3b), proving the maintenance
  burden of dual ownership. Single source of truth + clear runtime/document
  separation. Generalises: future platforms (Claude Code plugin and beyond)
  follow the same rule.
- **Notes:** Resolves the audit's §3b prose-coupling in `templates/*.yaml`
  automatically — those files are not copied to `platforms/hermes/`. The
  lone `BRD-MD-TEMPLATE.md` (no framework equivalent) is investigated at
  P2-T3 and ported-or-dropped based on call-site usage.

## D-0012 — Framework purpose: the IPLAN is the product; v1 scope is software/devops

- **Date:** 2026-05-19T12:45:00Z
- **Decision:**
  - aidoc-flow's purpose is to transform business intent into a
    fully-traceable, gate-approved **IPLAN** — the framework's *terminal
    artifact*. Source-code generation and deployment are **out of scope**:
    they are downstream, agent-agnostic steps performed by any capable AI
    agent, not by the framework.
  - The **IPLAN is the product**: a machine-readable, auditable handoff
    contract bundling reasoning (BRD/PRD), states (EARS), behavior (BDD),
    infrastructure decisions (ADR), testing procedures (TDD/TSPEC), and
    specifications — self-contained enough that any agent can execute it
    without further clarification.
  - **v1 scope is software + devops domains only.** The current SDD layers
    (EARS, BDD, ADR, TDD) are software-native. Non-technical task domains are
    deferred to a post-v1.0 **domain-profile** mechanism (see `ROADMAP.md`,
    "Post-v1.0 — Planned Capabilities").
  - Promise framing is **"rigorous, auditable, gap-surfacing"** — *not*
    "bullet-proof". The framework enforces structure and blocks on unresolved
    open questions, but cannot manufacture requirements a human never supplied.
- **Why:** Code generation and deployment are commoditized across AI agents;
  the scarce, defensible value is auditable reasoning with end-to-end
  traceability. Terminating scope at the IPLAN keeps the name `aidoc-flow`
  accurate — the framework *is* the document flow. Limiting v1 to
  software/devops keeps the existing layers fit-for-purpose; chasing
  universality early would dilute the framework into being vague at everything.
- **Notes:** The conformance suite gains a job — verifying IPLAN
  *agent-readiness* (no TBDs, full upstream traceability, bundled test specs,
  explicit stack/runtime constraints). Domain generalization is an
  architectural goal (a generic flow engine + per-domain profiles), sketched
  in `ROADMAP.md` as post-v1.0.

### Refinements

- **R1 — 2026-05-19T13:10:00Z — the IPLAN has a *planned* and an *executed*
  state.** The IPLAN is one artifact in two states: *planned* (YAML
  instructions with confirmations pending) and *executed* (each confirmation
  satisfied with evidence — what ran, results, actual vs expected). The
  *executed* IPLAN is the auditable trail behind a result; in practice humans
  scrutinise the result, not the forward plan, and often accept the planned
  IPLAN blindly. **Criticality scales audit depth:** low-criticality work
  (e.g. a throwaway MVP cloud deploy) — the IPLAN is internal quality control,
  nobody audits; high-criticality work — the executed IPLAN's evidence *is*
  the deliverable. Audit depth is a dial set by criticality, not all-or-nothing.

- **R2 — 2026-05-19T13:10:00Z — the unit of value is the curated corpus, not a
  single IPLAN.** A single IPLAN is reproducible and low-value. A curated,
  maintained library of *proven* IPLANs is codified, executable institutional
  knowledge — the customer's IP. An IPLAN earns library membership by being
  executed and audited (R1). The library — plus **composition** (IPLAN
  templates vs instances; IPLANs composing IPLANs) and **freshness**
  (re-validation, versioning, staleness flags) — is the post-v1.0 strategic
  destination: the framework as a system of record for an organisation's
  executable process knowledge. Sketched in `ROADMAP.md`.

## D-0011 — Bookmark tags alongside release tags

- **Date:** 2026-05-19T11:20:00Z
- **Decision:** Git tags serve two roles. **Release tags** (`vX.Y.Z`,
  `framework/vX.Y.Z`, `<platform>/vX.Y.Z`) are annotated, immutable, and
  permanent. **Bookmark tags** (`mark/<slug>`) are annotated, mutable, and
  disposable — they mark notable non-release commits (baselines, known-good
  states, audit points) for easy retrieval via `git tag -l 'mark/*'`. The full
  policy lives in `docs/TAGGING.md`; `docs/PROJECT.md` §3 links it.
- **Why:** Tags are a cheap, searchable way to mark history. Restricting them
  to releases wastes that. A separate, clearly non-SemVer namespace keeps
  bookmarks from being mistaken for versions.
- **Notes:** `docs/TAGGING.md` is the single authority; the tag-namespace
  table was moved there from `docs/PROJECT.md` §3 to avoid two copies drifting.

## D-0010 — Framework docs drop legacy version-lineage content

- **Date:** 2026-05-19T10:00:00Z
- **Decision:** When extracting docs into `framework/`, drop content that only
  documents the legacy SDD version lineage — the `## v3.2 Changes from v3.0`
  sections (P1-T7, in the guide and the testing-strategy doc) and the
  `CHG_MIGRATION_PLAN.md` (v2→v3) reference in `QUICK_REFERENCE.md`.
- **Why:** `framework/` is a fresh `0.1.0` version stream (D-0006); it does not
  continue the legacy `v3.x` numbering, so "changes from v3.0" history is both
  inaccurate framing and carries `v3.x` tokens the conformance hygiene check
  bans. The current layer order/rationale those sections explained is already
  stated as present-tense fact elsewhere in each doc.
- **Notes:** Removal is limited to version-lineage framing; all genuinely
  engine-agnostic methodology content is copied verbatim.

## D-0009 — Namespaced version tags; framework tag at Phase 1 close

- **Date:** 2026-05-19T09:15:00Z
- **Decision:** Each SemVer stream tags in its own namespace — project
  milestones `vX.Y.Z`, framework spec `framework/vX.Y.Z`, platforms
  `<platform>/vX.Y.Z`. `VERSION` files hold the bare SemVer; the tag adds the
  `v` and namespace. The `framework/v0.1.0` tag is created at Phase 1 close
  (after P1-T7), not at P1-T6 — so it marks a fully assembled spec — alongside
  the `v0.2.0` project milestone.
- **Why:** `docs/PROJECT.md` defined only bare milestone tags; the independent
  framework/platform streams need distinct, collision-free tag names.
  Slash-namespaced refs let `git tag -l 'framework/*'` filter one stream.
  Tagging an incomplete spec would burn a version on a partial assembly.
- **Notes:** Convention recorded in `docs/PROJECT.md` §3 (extended, not a new
  doc). P1-T6 delivers `framework/VERSION` + the convention; the deferred tag
  is tracked as the Phase 1 close task (P1-T8).

## D-0008 — Conformance suite is stdlib-only (`unittest`)

- **Date:** 2026-05-18T21:20:00Z
- **Decision:** Build `tests/conformance/` on the Python 3.11 standard library
  (`unittest`) plus `PyYAML`. No `pytest` dependency.
- **Why:** The conformance suite is the shared, engine-agnostic contract; it
  must be runnable by any platform with zero install friction. `pytest` is not
  installed in the environment, and `python -m unittest discover` runs the
  suite anywhere. `unittest.TestCase` classes remain `pytest`-discoverable for
  platforms that prefer that runner.
- **Notes:** Discovery uses a flat package-less layout (`tests/conformance/`
  with no `__init__.py`) so test modules can `import _spec` directly under
  `unittest discover`. The plan listed an `__init__.py`; it was dropped during
  implementation for clean discovery.

## D-0007 — Plan review is a two-pass, recorded gate

- **Date:** 2026-05-18T18:45:00Z
- **Decision:** Every plan file carries a `## Review log` with **≥2**
  ISO-stamped passes; a plan may not be presented, handed off, or implemented
  until it does. New plans start from `plans/PLAN-TEMPLATE.md`. A non-blocking
  `PreToolUse(git commit)` hook warns when a staged plan file falls short.
- **Why:** The review/harden step was prose-only, so a skipped second pass was
  invisible — it happened once on the P1-T2 plan. Making each pass a named,
  checkable artifact turns a silent omission into a visible gap.
- **Notes:** The hook enforces that a pass is *recorded*, not that it is
  thoughtful — review quality stays a manual judgment step.

## D-0006 — First `framework/` spec version is `0.1.0`

- **Date:** 2026-05-18T18:00:00Z
- **Decision:** The extracted `framework/` spec starts its independent version
  stream at `0.1.0`, carrying a `derived_from: "SDD v3.2"` metadata field.
  `1.0.0` is reserved for when both platforms pass the shared conformance suite.
- **Why:** The content is mature, but as a freshly re-packaged engine-agnostic
  artifact it is not yet conformance-proven and no platform is wired to it.
  `0.x` is the honest signal; the lineage field preserves provenance.

## D-0005 — `framework/` ships per-layer index templates

- **Date:** 2026-05-18T18:00:00Z
- **Decision:** Each `framework/layers/` directory ships a
  `{TYPE}-00_index.TEMPLATE.{md,yaml}` skeleton. Legacy `*-00_index.*` instance
  files are dropped (project data, not spec).
- **Why:** The index/registry *format* is a conformance concern — both
  platforms must produce and validate index files identically. Pinning the
  format in the spec prevents platform divergence.

## D-0004 — Compaction/continuity automation via hooks

- **Date:** 2026-05-18T17:27:00Z
- **Decision:** Add a `PreCompact` hook that auto-commits and pushes a WIP
  snapshot, and a `SessionStart` hook that injects `plans/HANDOFF.md` into
  context. Scripts live in `.claude/hooks/`.
- **Why:** Containers are ephemeral; only pushed work survives. The PreCompact
  hook guarantees a durable snapshot before any memory-reduction event; the
  SessionStart hook restores continuity automatically.
- **Notes:** Hooks run shell commands, not Claude reasoning — they cannot
  *write* the handoff narrative. `plans/HANDOFF.md` is refreshed manually as a
  workflow step; the hook only snapshots whatever is on disk. The PreCompact
  hook no-ops off the working branch as a safety guard.

## D-0003 — Project memory + development workflow in `CLAUDE.md`

- **Date:** 2026-05-18T00:00:00Z
- **Decision:** Maintain a root `CLAUDE.md` as auto-loaded project memory, and
  codify the change flow (plan → review → harden → implement → verify → land).
- **Why:** Each session starts cold in a fresh container. Persistent memory
  prevents re-discovery; an explicit flow keeps quality consistent.

## D-0002 — `plans/` workspace for migration tracking

- **Date:** 2026-05-18T00:00:00Z
- **Decision:** Create a fresh root `plans/` (distinct from the frozen
  `legacy/plans/`) holding `MIGRATION_TODO.md` (live tracker), `HANDOFF.md`,
  `DECISIONS.md`, and ad hoc working notes.
- **Why:** Separates volatile working state from the stable published
  `ROADMAP.md`.

## D-0001 — Isolate the pre-migration project into `legacy/`

- **Date:** 2026-05-18T00:00:00Z
- **Decision:** Move the entire pre-migration project into `legacy/` via git
  renames; freeze it (copy-don't-move); disable legacy CI.
- **Why:** A clean root for the new multi-platform structure with zero path
  overlap, while preserving the old project for content extraction in
  Phases 1–3 and full git history.
