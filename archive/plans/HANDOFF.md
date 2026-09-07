# Session Handoff

**One reader: a fresh session with zero context.** Current state, then what to do next.
**Rewritten wholesale each merge** — `git log -- plans/HANDOFF.md` is the archive; do not
restore prior states here. Settled traps live in `CLAUDE.md` § "Durable traps" and are
never repeated here.

**State:** framework spec **`0.51.0`**, plugin `0.25.0`, Hermes `0.12.1`; both platform
`FRAMEWORK_SPEC_VERSION` pins read `0.51.0`. `0.45.0` was **skipped** and never became a value
of `framework/VERSION` (`plans/DECISIONS.md` D-0082). Tag high-water mark is
**`framework/v0.51.0`**, cut 2026-09-04 at `d218aefa` — re-derive with
`git ls-remote --tags origin 'refs/tags/framework/*'`. **A cut tag is not a published Release
here:** `framework/v0.44.0` is the newest framework Release and so still shows as *Latest* while
the spec is `0.51.0`; `v0.46.0`–`v0.51.0` are tag-only.

**Verified 2026-09-04 on `main` at `d218aefa`** (run, not asserted): conformance **513 passed /
1059 subtests** via `python3 -m pytest tests/conformance -q`, and **562** via
`python3 -m unittest discover -s tests/conformance -t tests/conformance` (CI's runner) — the two
count subtests differently, so cite the command with the number. Acceptance-deterministic **64**,
unit **209**, `sdd_doc_lint` **6**, `pre-commit run --all-files` green on two consecutive runs.
**0 failing.**

Phase 0 `lint-smoke` is a separate harness and is RED — corpus debt deferred to the wholesale
regen; use `--skip-lint-smoke`.

## What this session did

**Two PRs merged, both for #621, which is CLOSED.** PR #630 landed the plan; PR #631 landed the
implementation at **`d218aefa`** — framework spec **`0.50.0 → 0.51.0`, GD-26**: a Draft IPLAN's
§5 `session_handoff.sessions` is now **empty**. `framework/v0.51.0` was cut and pushed.

**Read the owners, not this summary** — `framework/governance/DECISIONS.md` **GD-26**, the
`0.51.0` entry in `CHANGELOG.md`, and `plans/IPLAN-SESSION-HANDOFF-001-PLAN.md` (Completed).

**Two issues filed from the review, both open:** **#632** (the deploy sections are 8-12 but
`doc-iplan/SKILL.md` calls them 7-11 twice, and the template has no Section 7) and **#633** (the
conformance prose guards cannot tell an instruction from a description, so a correct audit rule
would red the check that forbids the defect). An evidence comment also went on **#438** — the MVP
IPLAN template's `session_handoff` uses different keys entirely.

## ⚠️ #620 — a framework version bump cannot pass its own pre-commit

**Unsettled, and it will hit the next spec release.**
`tests/conformance/test_release_record_integrity.py` (the #617/#618 phantom-release guard)
resolves `VERSION` values from **committed git history only** (`_version_values`), and
`.pre-commit-config.yaml:124-128` runs the conformance suite `always_run: true`. So the commit
that introduces a spec release — bumping `framework/VERSION` and adding the matching
`### Changed — Framework Spec` heading, exactly as `GATE-SPEC-E005`/`E008` require — is blocked
by the guard whose precondition that commit is about to satisfy.

Reproduced in a throwaway clone: **RED staged, GREEN once committed.** CI is unaffected (the PR
branch contains the commit). The only local way through is `git commit --no-verify`, which also
skips ruff, markdownlint, yamllint, detect-secrets and both sync hooks — so **run
`pre-commit run --all-files` immediately after and confirm green**, which is what #622 did and
recorded in its PR body. Fix shape is on **#620**.

## `ai-review` is RE-ENABLED and verified working (D-0087, #623 closed)

**The `ResponseShapeError` failures are RESOLVED, and the cause was neither of the two things
this file previously claimed.** It was host-side and outside every repo:

1. **The provider account was exhausted** — `api.deepseek.com` reported `total_balance: "-0.04"`,
   `is_available: false`, so every call silently fell to the Ollama Cloud fallback. Now `4.93`.
2. **Host DNS was failing in waves** — see the `#613` section below.

With both fixed, `call / ai-review` **passed on PR #628**, a 37,106-byte diff that had failed three
times, with no other change. That is the proof; nothing else here is.

⚠️ **Two mechanisms were published to `aidoc-flow-ci#543` and BOTH were retracted — do not
resurrect either from an older revision of this file or from that thread's middle.** The first
claimed PRs touching `.github/` fail (3-of-3 in a census, confounded with diff size); the second
claimed an input-size threshold near 20-37 KB. **Every measurement behind them was taken while the
balance and DNS were both moving underneath.** A distribution measured during an outage describes
the outage. The retraction is `aidoc-flow-ci#543`'s newest comment.

**One reproduction is real but is NOT the bug**, recorded so nobody chases it: a *bare*
single-user-message probe — 37 KB diff plus "reply with ONLY JSON", no system prompt — returns
empty `content` with `completion_tokens` exactly equal to `max_tokens`, at every budget tried, on
**both** routes, under healthy DNS and a positive balance. Canon succeeds on that same diff at the
same moment, so the two differ by call shape and the probe explains nothing about CI.

**The finding that survives, and is still upstream-owned:** the proxy returns **HTTP 200** with an
empty body — verified in its access log, every call across three failing runs — and canon reports
that as `litellm: proxy request failed after 3 attempts: ResponseShapeError`. The request did not
fail and the proxy did not error. That message is what sent two separate investigations to the
proxy and to diff size, and it is why `ai-review` was disabled for two days instead of someone
checking a balance.

**It was `disabled_manually` from 2026-09-01 to 2026-09-03** and produced no run, no verdict and
no check-run on any PR in that window — including PRs #619, #622, #624 and #625, all merged to
`main`. Nothing recorded the disable. **Read `plans/DECISIONS.md` D-0087 rather than this
summary**; the evidence that decided it is that four `ai-review` runs succeeded on three
branches between 02:45 and 03:12 on 2026-09-01, and the three failures that preceded the disable
were **all on one branch** (`fix/606-ai-review-schema-pin`, PR #612).

**Confirmed working, not merely re-enabled.** PR #626 — the change that re-enabled it — was
itself reviewed: a substantive `changes requested` (a missing CHANGELOG entry, which was
verified against the D-0084 changelog entry and correct), then `ai:review-passed` after the fold.
`composition` ran and passed alongside it. So the reviewer produces real verdicts on ordinary
PRs, and a red `call / ai-review` is the intended signal for `changes requested` rather than an
infrastructure error — check the PR comment before treating one as a break.

**Two traps from that window are worth keeping even though the state is fixed:**

- **`gh workflow list` showed `composition` as `active` throughout, and it was silent.** Its only
  PR-side triggers are `pull_request_review` and a `workflow_run` chained off **`ai-review`**
  completing, so disabling the parent silences the child while the listing still reads healthy.
  Check the child's *runs*, not its status.
- **D-0084 asserts "Both workflows still run", and that sentence was falsified two days after it
  was written.** It is annotated in place, not rewritten — a decision is accurate as of its date.
  Its gating half (the four required contexts, the restore command) was never affected.

Re-derive rather than trusting either: `gh workflow list --all` ·
`gh run list --workflow=ai-review.yml --limit 8`.

**Expect intermittent red, and it does not block.** `ai-review` is not a required context, so a
failure leaves a PR `UNSTABLE`. Upstream `aidoc-flow-ci#543` is **open** and its diagnosis does
not fit: it reports the failure as deterministic on a **many-file** diff and its own follow-up
retracts the file-count mechanism, but PR #612 is **5 files, +313/−40** and failed three times.
Neither file count, line count, nor the 400,000-byte input cap explains it. That evidence is now
a comment on #543; the discriminator is unmeasured and upstream-owned.

**#596's premise is restored.** Its items 1 and 2 were written assuming `ai-review` still runs;
that is true again, so they revert to their original form rather than resolving by deletion.

## CI gating — the branch-protection half of D-0084 still holds

**The four required contexts are:** `Framework + platform conformance`,
`call / Lint / format / security hooks`, `call / verify`, `Acceptance tier (deterministic)`.
Re-derive with
`gh api repos/vladm3105/aidoc-flow-framework/branches/main/protection/required_status_checks --jq '.contexts[]'`.
`GATE-SPEC` and `dep-scan` are **not** required — a red one leaves a PR `UNSTABLE`, not
`BLOCKED`. Branch protection requires **0** approving reviews, but merge is human-only on this
repo per `.github/ai-review/config.json`. D-0084 carries the one-call restore for the removed
contexts and that half is unchanged.

## The backlog is GitHub issues

**Open issues: 33**, of which **14** are parked (measured 2026-09-04, after #621 closed and #632/#633 were filed). Re-derive rather than copy:
`gh issue list --state open --limit 300 --json number --jq 'length'` and
`gh issue list --state open --limit 300 --json number,labels --jq '[.[]|select(.labels[].name=="parked")|.number]'`.
In-progress work carries **`status: in progress`** — that label is currently on nothing.

**The parked set** — not pickable: 438, 467, 473, 483, 484, 507,
528, 543, 544, 545, 546, 547, 548 and **563** (numbers unprefixed deliberately — a line
starting `#NNN` is autofixed into an H1, see `CLAUDE.md` § "Durable traps"). Derive that set
from the label, not from a title scan — two of them name the gating decision only in the body.
Three are blocked externally: **#484** (gated on v1.0.0), **#473** (the umbrella owns the
submodule pointer), **#528** (product call).

## #621 is shipped — what a future session needs from it

**A Draft IPLAN carries `session_handoff.sessions: []`.** No key added, none removed. The two
durable traps this implementation produced are in **`CLAUDE.md` § "Durable traps"**, not here.

**The one live consequence to know about:** `#633` records that the prose guards fire on correct
*descriptive* sentences. If you add a detection rule for this defect class to `doc-iplan-audit`
or `doc-iplan-fixer`, the guard will red — and the cheapest way to silence it (adding an
exemption word) permanently unscans that region. Read #633 before rewording anything to get
green.

## #606's fix is on `main` — the issue stays closed

Merged 2026-09-04 as PR #628 at `1c2958db`, a fresh branch off `main` rather than a replay. `.github/ai-review/config.json`'s
`$schema` now pins `ci/v3.0.0`, matching `ai-review.yml`'s caller, and
`tests/conformance/test_ai_review_schema_pin.py` (4 tests) enforces the coupling.
`plans/CI-CANON-V4-MIGRATION-PLAN.md` carries it as step 6 + V3b.

**The issue is left CLOSED and was not reopened.** It closed `COMPLETED` on 2026-09-01, 32
seconds after PR #612 closed unmerged; the record and `main` now agree, so reopening would only
churn. The original branch `fix/606-ai-review-schema-pin` (`cfb7b6e4`) is still on the remote and
is now **superseded** — do not merge it: its `CHANGELOG.md` and `plans/HANDOFF.md` commits would
resurrect superseded figures, which is exactly why only the three unique files were carried.

**Two claims from that branch were re-derived rather than trusted before shipping.** The schema
blob equality (`8012104…` identical at `ci/v2.16.0`/`v3.0.0`/`v4.0.0`, no v3/v4-numbered schema)
holds. The Pass-2 review log's "grep emits 7 tokens" does **not** — the merged file yields **5**;
corrected in the plan with the command, since the count moves with every `_note` edit.

⚠️ **After the v4 migration this guard starts intercepting Dependabot.** The `semver-major` hold
leaves minor/patch bumps in scope, and a grouped bump rewrites `uses:` while being unable to
touch `config.json`, so the required conformance context goes red. **That is the guard working —
push the one-line `$schema` edit onto the Dependabot branch, never remove the guard.** Exposure
is nil today: canon ships no further v3.

## Unsettled — watch

**#613 — root cause CONFIRMED and partly fixed; the residual is the router.** The LAN gateway
`192.168.86.1` episodically stops serving DNS: caught mid-outage, UDP/53 timed out, **TCP/53 was
refused outright**, and the LAN hop measured 1355-1569 ms RTT at 0% packet loss. It comes in waves
— twenty minutes later the same gateway answered at 3-94 ms. `eno2` shows 0 RX/TX errors and host
load 1.25, so it is not this machine. `aidoc-flow-operations` has a runbook naming the same router
from **2026-06-19**.

**Fixed this session:**

- **Host** — `/etc/resolv.conf` now lists public resolvers first with the gateway last, plus
  `options timeout:1 attempts:2`; `/etc/NetworkManager/conf.d/90-dns-none.conf` (`dns=none`) stops
  NM reverting it at the next DHCP renewal. Backup: `/etc/resolv.conf.bak-20260903-161439`.
  Measured **0/10 → 20/20 @ 78 ms**.
- **Containers** — founder added a `dns` key to `/etc/docker/daemon.json` and restarted Docker.
  `ci-job-*` containers now resolve `github.com` **15/15**; `litellm` **10/10**.

**Correction worth keeping:** the runner job containers were **never** on the bad resolver. That
June runbook's fix shipped, and `run-ephemeral.sh` passes `--dns 1.1.1.1 --dns 8.8.8.8` —
`docker inspect` confirms `["1.1.1.1","8.8.8.8"]`. Their `Could not resolve host` failures were
packet loss during a wave, not resolver inheritance. Do not go looking for that bug.

**Residual, and no software config closes it:** during a wave, UDP is lost to *any* resolver. Two
things would — a caching resolver on `172.17.0.1:53` with `RUNNER_DNS="172.17.0.1"` (CI resolves
the same few names hundreds of times per run, so cache hits ride out a wave; needs a package
install **and** a cross-repo edit in `aidoc-flow-operations`), or replacing the gateway. Also note
`daemon.json`'s `dns-opts` uses `rotate` with the gateway still in the list, so ~1 query in 3 goes
to it first at `timeout:5` — harmless outside a wave, amplifying inside one.

## What to do next — prioritized

1. **#620** — fix the phantom-release guard so a spec release can pass its own pre-commit. Every
   future framework bump pays the `--no-verify` cost until it lands, and that is the change class
   where skipping the other hooks is least acceptable.
2. **#632** — the IPLAN deploy sections are 8-12; `doc-iplan/SKILL.md:116` and `:194` call them
   7-11. Prose-only in the skill, and the issue argues for fixing the skill rather than
   renumbering the template (renumbering moves section numbers GD-25/GD-26/CHANGELOG cite).
   Small, well-scoped, and a conformance assertion tying the range to the template's real
   headers would stop it recurring.
3. **#613** — reopened; the fix is host-side resolver work, not a repo change. Not blocking.
4. **#614** — does the seed tier get a registered `@seed:` provenance tag on the `@chg:`
   precedent? Suggested default is **no** unless a second `real-use` report arrives; the point of
   the issue is that the *reason* must be scope, never "a tag is lineage". Not blocking anything.
5. **#393 / `plans/CI-CANON-V4-MIGRATION-PLAN.md`** — still **BLOCKED** on two founder /
   infrastructure prerequisites (runner labels `ci`/`ephemeral` do not exist; `LLM_URL` /
   `LLM_API_KEY` do not exist and the caller still forwards three `LITELLM_*` names v4
   un-declares). ⚠️ **Its stated `--repin` remedy is insufficient**, not unsafe — the plan
   (`:35-37`) says `--repin` cannot deliver two of the five required changes; *unsafe* is this
   repo's word for `--update` (risk R2). Read the plan, not the issue body. If #606 is
   re-submitted, its `$schema` edit and this plan's step 6 / verification V3b must stay
   consistent.
6. **#588** — the identity-carrier split. Not startable alone; it is `OKF-CONFORMANCE-001`
   D1's to settle.
7. **#546** — **parked**, and splitting it is what unparks it. The `_required: false` half of
   the `STY02` defect is independently shippable and does not wait on the parked subtype
   decision; the correction that establishes this is in the issue's own comments. Re-title or
   split before picking it up, and drop `parked` from the shippable half.

`framework/v0.50.0` was cut this session and is off this list. `docs/TAGGING.md` still records
the tag-cut lag as a sanctioned backlog — **77 of 90** values untagged, all of them older than
`v0.46.0` — so the *older* backlog stays deferred; only the contiguous recent run is maintained.
