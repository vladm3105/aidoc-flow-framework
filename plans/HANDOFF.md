# Session Handoff

**One reader: a fresh session with zero context.** Current state, then what to do next.
**Rewritten wholesale each merge** — `git log -- plans/HANDOFF.md` is the archive; do not
restore prior states here. Settled traps live in `CLAUDE.md` § "Durable traps" and are
never repeated here.

**State:** framework spec **`0.41.3`**, plugin `0.25.0`, Hermes `0.12.1`; both platform
`FRAMEWORK_SPEC_VERSION` pins read `0.41.3`. **RELEASED** — `framework/v0.41.3` is an
annotated tag on `8dccc315` (PR #530), published as the **Latest** GitHub release on
2026-08-24. Conformance was verified green *at that commit*, not inferred from `main`, per
`docs/TAGGING.md`. No consumer has yet run against it. No open PRs, working tree clean.

The last **deployable** commit is `8dccc315` (PR #530); everything on `main` after it is
docs-only. Re-derive with **two** commands — `git rev-list -n1 framework/v0.41.3` for the
commit, and `gh release view framework/v0.41.3 --json tagName,isPrerelease,isDraft` for the
publication state. Do **not** use `git log -1 origin/main` (returns whatever docs commit
landed last, and shows no PR number) and do **not** use `--json targetCommitish`: that field
is the release's target branch, so it returns the literal string `main` and no SHA at all.
`gh release view` exposes no field carrying the tag's commit.

**Verified this session on `main` at `8dccc315`** (run, not asserted): conformance
371 passed / 795 subtests · acceptance-deterministic 64 passed / 56 subtests ·
`sdd_doc_lint` 6 passed ·
Hermes `570 passed` · `pre-commit run --all-files` clean, 19 hooks. **0 failing across
those four suites** — Phase 0 `lint-smoke` is a separate harness and is RED, see below.
*(`pytest tools/sdd_doc_lint/tests` needs `PYTHONPATH=tools` or it fails to collect.)*

## ⚠️ This repo does NOT auto-merge — ask every time

`.github/ai-review/config.json:22` records it as deliberately omitted from the
operations-side `auto_merge.repos` allowlist: spec/governance repo, `tier:spec`,
human-always. **`CLAUDE.md`'s OPS-0062 section reads the opposite way** and is where you
will look first — it describes the generic default, not this repo's exclusion. The
`"enabled": true` flag beside that comment is inert, and the allowlist itself lives in
`vladm3105/aidoc-flow-operations`. #530 was merged on the founder's explicit in-session
authorization for that PR only. Never infer standing approval.

## The backlog is GitHub issues

`plans/FRAMEWORK-TODO.md` is a tombstone carrying an entry → issue mapping. Do not add to
it. **Open issues: 16.** Re-derive with `gh issue list --state open --limit 300` — never
`--search` (tokenised, eventually consistent), never the default `--limit 30`.
In-progress work carries **`status: in progress`**.

## What this session did

**Adopted 175 uncommitted files** that were sitting on `main` from an unfinished earlier
session — a framework spec bump `0.41.2 → 0.41.3` with no branch, no commit and nothing on
the remote. Shipped as PR **#530**, ratified as **GD-13**, at 185 files: the extra 10 are
`TRACEABILITY.md`, the two auditor playbooks, `IPLAN-TEMPLATE.yaml`, the plugin agent doc,
`ROADMAP.md`, `DECISIONS.md`, both platform changelogs and their vendored mirrors.

**The draft carried two defects, one of them executable.** Its bubble-up example paired
`change_source: feedback` with `entry_gate: GATE-03`; both routing tables bind
Feedback → GATE-CODE, and `platforms/hermes/src/mcp_server/validation/chg_rules.py:15`
rejects the pairing as a hard `CHG-002`. It also set `status:` to a value absent from the
`CHG-TEMPLATE.yaml:82` enum. That routing line was the only new normative **routing**
assertion in the diff, and it was wrong. (Two other statements were newly *explicit* —
the 4-segment threshold width and `change_source: spec` being `>= C2` — but both restate
an existing authority rather than asserting something new.)

**GD-13 is an erratum, not a rule change.** GD-03 ratified in June that `@adr` / `@tdd`
trace citations must be element-level and only `@spec` / `@iplan` stay document-level;
`REFGRAN01` has enforced it since. **Six** authoring surfaces had never been reconciled —
including `ID_NAMING_STANDARDS.md`, which is GD-03's own named *authority*, and both the
ADR and TDD auditor playbooks, whose C5 rules **mandated** the form the linter flags
(penalty P3). Nothing consumer-visible moves, so PATCH, where GD-03 itself carried MINOR
for introducing the rule.

**The class sweep only happened because a reviewer asked for it.** The first fix
reconciled 2 surfaces of 6 and read as complete. `#531` was filed for the missing guard
that would have caught all six.

**Three OPS-0065 review agents, verdicts FAIL / FAIL / APPROVE-WITH-CHANGES, one fold
cycle** — the cap is 3 and was not exceeded. Every finding was re-derived against source
before folding: GD-03's own exemption clause (self-tags and downstream forward-pointers
are not trace citations) cleared roughly two-thirds of a 30-hit grep as legitimately
document-level, so the reviewer's raw surface list was larger than the real class.

## What to do next — prioritized

Filter: [`is:open is:issue`](https://github.com/vladm3105/aidoc-flow-framework/issues) ·
in-flight: `--label "status: in progress"`. Below is only the ordering.

1. **[#531](https://github.com/vladm3105/aidoc-flow-framework/issues/531) — filed this
   session, and the direct successor to GD-13.** *(Fold
   [#532](https://github.com/vladm3105/aidoc-flow-framework/issues/532) in with it — GD-13's
   title says "Two governance documents" where its body says six, and the `0.41.3` CHANGELOG
   names 2 of the 6 reconciled surfaces. Both need a `framework/VERSION` bump to fix, so
   they should ride the same release rather than burn one of their own.)* No conformance test locks the
   document-level-permitted set to `{SPEC, IPLAN}` across `ID_NAMING_STANDARDS.md`,
   `TAG_SYNTAX.md`, `TRACEABILITY.md` and `_REFGRAN_ELEMENT_DECLARING`. Six surfaces
   drifted for two months behind that absence. `tests/conformance/test_governance.py::GateCheckIdParity`
   is the same pattern one layer over — extending it is reuse, not authoring. Parse the
   structured artifacts; do **not** grep for a marker string, which is this defect's own
   failure mode. Mutation-test it before believing it.
2. **[#486](https://github.com/vladm3105/aidoc-flow-framework/issues/486)** — the same
   rule violated in the example corpus (`SPEC-01:31,67,469`, `TDD-01:204`, `IPLAN-01:43`).
   Likely the *same* root cause as #531 rather than an independent defect. ⚠️ Tension to
   resolve before starting: the corpus is regenerated wholesale after framework changes,
   which is why corpus findings are normally deferred — so decide whether #486 is
   remediation or is simply absorbed by the next regen.
3. **[#438](https://github.com/vladm3105/aidoc-flow-framework/issues/438)** — 8
   `*-MVP-TEMPLATE.yaml` non-conformant with the framework's own governance. ⚠️ **Its
   premise may be stale**: the issue says "remediation plan FRWK-REVIEW-003 unmerged",
   but `plans/FRWK-REVIEW-003-PLAN.md` is on `main`. Verify before planning work.
4. **[#423](https://github.com/vladm3105/aidoc-flow-framework/issues/423)** — the only
   issue marked in progress, and not this session's. Its work is committed as `f05dfc0d`
   on `origin/fix/423-site-badge-selfheal` (`scripts/sync-version-refs.sh`, +41/−14) and
   needs a PR, not a rescue.
5. **OKF-CONFORMANCE-001** — `plans/OKF-CONFORMANCE-001-DESIGN.md` (PR #529) is merged but
   has **no tracking issue** — re-derive rather than trusting this, an absence is the
   easiest claim to assert and the hardest to verify:
   `gh issue list --state all --limit 300 --json number,title --jq '.[]|select(.title|test("OKF";"i"))'`.
   Three open questions in it block the implementation
   plan. The decisive one: SPEC/TDD/IPLAN goldens are `.yaml` while OKF's atom is a `.md`
   file, so a YAML-authored tree is *vacuously* conformant and an OKF reader sees an empty
   bundle. Founder decision.

## Blockers and standing constraints

**⚠️ Every doc PR serialises on `CHANGELOG.md`.** All entries insert at the top of
`## [Unreleased]`, so each merge makes the next open PR `DIRTY`. Structural, not a
mistake; the only lever is fewer PRs.

**⚠️ A framework `VERSION` bump is an unsplittable governance PR and needs a per-bump
founder OK.** It touches four capped doc surfaces (`CHANGELOG.md`, `CLAUDE.md`,
`README.md`, `docs/PARITY.md`) against Rule 1's cap of three, and cannot be split because
`scripts/sync-version-refs.sh` writes the last three itself and **re-stages them**. Record
the grant as an audit-trail line in the commit message. Granted for #530; not standing.

**Phase 0 `lint-smoke` in `tests/scripts/test-acceptance.sh` is RED** — example-corpus debt
deferred to the wholesale regen; use `--skip-lint-smoke`.

**Hermes pytest is GREEN and #465 is closed** — by **#527**, squashed onto `main` as
`3354d4f6`. Earlier handoffs said it was red since 2026-07-27; that is no longer true and
cost a wrong prediction this session. **The root cause was fixed, not merely deferred:**
`platforms/hermes/pyproject.toml:7` now reads `mcp[cli]>=1.0.0,<2`, so the resolver can no
longer pull `mcp 2.0.0`. Do not describe this dependency as an open failure class.

**Repo hygiene done 2026-08-24:** stale branches pruned (local 14 → 2, remote 10 → 3, plus
whatever branch carries the change you are reading) and two abandoned worktrees removed. The
two survivor sets differ, so read them separately: **locally** `main` and
`fix/423-site-badge-selfheal`; **on origin** those two plus `legacy-ucx-v3.2-read-only`,
which is the protected read-only pre-migration branch and has no local counterpart. Kept
deliberately: `fix/423-site-badge-selfheal` carries live work for #423.

⚠️ When judging whether a branch is dead, **check its PR state, not
`git merge-base --is-ancestor`.** Everything here is squash-merged, and a squashed branch's
tip is never an ancestor of `main` — so the ancestor test called all thirteen "unmerged"
when twelve had fully landed. (It is a reliable test only for branches that were
fast-forwarded or rebase-merged; this repo has none.)

**What did NOT change:** neither platform version moved, no platform release was cut, the
example corpus was not touched, and no `plans/` document other than this one was written.
