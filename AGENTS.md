# AGENTS.md — working agreement for AI coding agents on aidoc-flow-framework

Orients any AI agent (Claude Code, Codex, Gemini CLI, Copilot, Hermes, custom)
working on this repo. **This file is the single working agreement** — the short
orientation plus the rules that are most often missed. There is no second
agreement: the former `CLAUDE.md` was retired and its live rules folded in
below (conflicting clauses resolved in this file's favour); git history
preserves the old file.

## What this repo is

One engine-agnostic specification (`framework/`) defining the 10-layer SDD
flow (BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code → EVAL → Verified).
Platforms (Hermes MCP server, Claude Code plugin) were archived — any capable AI
agent derives its behavior from the framework spec, templates, and playbooks
directly. The repo ships `sdd_doc_lint/` (structural linter) and `hooks/`
(advisory hooks — `PostToolUse` + `PreCommit`, see `hooks/README.md`) as the only retained tooling.
The pristine pre-migration project is preserved on the protected, read-only
`legacy-ucx-v3.2-read-only` branch.

## Filing gaps — open a GitHub issue

When you find a defect, inconsistency, or missing capability, **open a GitHub
issue on this repo**. That is the whole rule — there is one surface.

Capture at discovery still applies, unchanged: open the issue when you find it,
not in a "later PR". What moved is the *surface*, not the timing.

The issue body carries: reproduction at `file:line`, blast radius **run** rather
than assumed, why it was hard to diagnose, a suggested fix, and what is **not**
broken. One issue per defect. **Move the analysis verbatim — never summarise a
finding into an issue**, because a re-derived finding silently contracts.

Search before filing (`gh issue list --search … --state all`); comment on an
**open** match instead of duplicating it; a **closed** match gets a new issue
cross-linked as a regression, never a reopen. The merge closes the issue — the PR
body carries `Closes #N`, one keyword per reference (`Closes #A and #B` closes
only `#A`). On merge, post a closing comment on each resolved issue — what
shipped plus verification evidence (green checks, merge SHA on the target) —
never leave a resolved issue closed without its record.

Use `gh issue create --body-file -`, **never `--body -`**: the latter publishes a
literal `-`, exits 0, and prints a URL, so it looks like it worked. Read the
artifact back — `gh issue view <N> --json body --jq '.body | length'` — a
non-zero length is the only proof it published.

> **`plans/FRAMEWORK-TODO.md` is retired.** It is a tombstone carrying the
> entry → issue mapping for the 42 entries migrated out of it on 2026-08-15.
> Do not add to it. Its file-queue rule (a TODO entry *plus* an issue, with a
> three-test bar deciding which gaps got one) is superseded: the file held 41
> entries no consumer could see, which is what retired it.

If the defect is owned by **another** repo (the CI canon `aidoc-flow-ci`, a
sibling submodule, an upstream spec), the issue goes **there**, not here. The
test is ownership, not severity.

Triage open issues with [`.agents/skills/aidoc-triage/`](.agents/skills/aidoc-triage/SKILL.md):
validate every claim live against the tree, review the full comment thread,
set priority + labels, post the note; transfer the issue when another repo
owns it.

**Verify what you published.** Use `gh issue create --body-file -`; `--body -`
sets the body to a literal `-`, exits 0, and prints a URL, so it looks like it
worked. Read it back:

```sh
gh issue view <N> -R vladm3105/aidoc-flow-framework --json body --jq '.body | length'
```

## Non-negotiables

- **Validate the task before implementing.** Re-check a picked-up issue live
  (`gh issue view` + the target branch): still open, still reproducible,
  still applicable — not fixed, stale, superseded, or declined. If it is,
  report that with evidence and stop; do not build around it. See
  `framework/AI_ASSISTANT_RULES.md` → "Issue Validation Before Work".
- **Keep changes safe.** No behavior change beyond the issue's scope, no
  weakened checks, suites green before the PR. Breaking or otherwise
  significant changes need a CHG first, then the CHG procedure — never code
  before the cascade (see Governance Gate below).

- **NEVER push directly to `main`.** All changes must go through the `dev` branch
  via a feature branch + PR. Pushing to `main` bypasses required status checks
  and review gates.
- **Example corpus retired.** The plugin-era `examples/<name>/` tree (`docs/` +
  `.aidoc/` system-under-test) was deliberately removed and must not be
  resurrected (enforced by `tests/conformance/test_coverage_engine.py`). Do not
  author new references to it; shared fixtures live under
  `tests/acceptance/fixtures/`.
- **Conformance stays green.** Never weaken a check in `tests/conformance/` to
  make it pass — fix the spec or the platform.
- **The spec is the contract.** `framework/` is engine-agnostic: no platform
  names, no runtime code. Platforms consume `framework/layers/<NN>_<X>/`; they
  never ship their own copies (D-0013).
- **Submit only finalized work.** A PR has already completed its review-and-fix
  cycles locally. Amendment PRs patching a just-merged PR are a smell that the
  original shipped early.
- **Plans get two review cycles before the plan PR opens.** Record every
  cycle in the plan's `## Review log` as an ISO-stamped `Pass N` entry (gaps
  found + how each was resolved); each pass re-validates the previous pass's
  patches. Implementation begins only after the plan PR is merged.
- **Minimal-and-realistic plans.** Size the plan to the problem (~N fixes for
  N substantive issues, not speculative features). Park deferred ideas as a
  one-line backlog enumeration in the plan's "Out of scope" section — do not
  draft them there.
- **Docs of record per PR.** Every PR keeps the documents-of-record in sync
  in the change's own PR — changelog entry, decisions, touched plans — never
  via a catch-up doc-refresh follow-up. The per-category matrix lives in
  `CONTRIBUTING.md` §Documentation discipline. Mechanical version fanout
  (`hooks/sync-version-refs.sh`) and the semantic reminder
  (`hooks/check-docs-updated.sh`, warning-only) run automatically on commit.
- **Versioning and tagging.** Project and framework spec version
  independently (`docs/PROJECT.md` §2; platform streams retired); tag rules
  in `docs/TAGGING.md` — `vX.Y.Z` (project), `framework/vX.Y.Z`; `VERSION`
  files hold bare SemVer.
- **One task, one worktree.** Feature/defect work runs in a per-task `git worktree` + branch (`feature/<issue-or-chg>-<slug>`), never in the main checkout; main checkout stays on `dev`. See `framework/governance/WORKTREE_FLOW.md` (§1 invariants, §3.8 order guard: `worktree remove` BEFORE branch delete, §4).
- **Autonomous implementation.** Routine implementation runs without human in the loop — branch, build, self-review, merge on green. Reserve confirmation for important or structural decisions: releases, destructive unmerged-work deletion, and any rule below that names a human.
- **Never bypass verification.** `--no-verify` (or any hook-bypass flag, skip-verification, or admin override) on commit, push, or merge is forbidden — a red hook means fix the cause in the worktree and re-run to green, never route around it.
- **Verify subagent writes; share branches.** After a subagent reports file writes, read back at least 3 specific changes before trusting `success` (phantom success has occurred). Subagents share the parent's branch and never mint their own; parallel writers need isolated worktrees.

## Governance Gate (applies to ALL agents)

Before writing ANY code for a feature, enhancement, or non-bugfix change:

1. Create a CHG document — do NOT write code first
2. Complete §3.4 checklist BEFORE writing the CHG
3. Run §3.4.1 validation AFTER writing the CHG, BEFORE committing
4. Declare SDD scope before code (SDD-first — F1/F3 only; F2 carries an empty lifecycle, F4 leaves the parent SDD standing): Seed → Module → SDD layers (SPEC/TDD/ADR/EARS/BDD as touched) — never jump from CHG approval straight to IPLAN/code with zero SDD steps (CHG-L005)
5. Create IPLAN with code steps (not in CHG)

Classify first: Emergency → Type-R → F4 → F3 → F2 → F1 — see `framework/governance/CHG_REQUEST_FLOWS.md` (ratified 0.57.0).

If user says "build", "implement", "add feature" → stop, create CHG first.
Exception (only one): seed-phase drafting before the first BRD is authored against seed vN
(`SEED_CONTRACT.md` R1) — pre-first-BRD drafting with no other documents in existence. Everything else
is traced: (i) bug fixes ride their IPLAN's authorizing CHG (active IPLAN) or the bugfix vehicle (C1 CHG +
bugfix IPLAN, parent immutable, post-completion); (ii) every C1 — docs-only non-normative included —
requires a C1 CHG + scoped IPLAN, every author (CHG-12, issues #772/#773). §3.13 + `CHG_REQUEST_FLOWS.md` govern.

**Automated CHG validation:** Run `python3 sdd_doc_lint/chg_lint.py <chg-file.yaml>` to check:

- CHG-L001: Status lifecycle (§3.3) — must follow Proposed → Approved → In-Progress → Implemented → Completed
- CHG-L002: Gate approval (§3.1) — C3 changes must have approver
- CHG-L003: CHG scope (§3.4) — no code steps in CHG
- CHG-L004: IPLAN reference (§3.1.1) — must reference an IPLAN
- CHG-L005: SDD-first order (§3.1.1) — SDD lifecycle before IPLAN
- CHG-L013: Flow misfit (§3.1.3) — code manifest + empty lifecycle + wrong source (GOV-018; names F2/F3/F4)
- CHG-L014: Seed/module coverage (§3.1.3) — upstream/midstream/design/spec/reconciliation touches need `seed_scope` / `module_lifecycle` (GOV-020)
- CHG-L015: Lifecycle attribution (§3.1.3) — lifecycle-carrying entries need `author` (+ `chg_ref` for modules; GOV-021)
- CHG-L017: Premature step completion (§3.4.1 E28) — no `Completed` step on a `Proposed` / `Approved` CHG
- Full catalog (L006–L017, BGF-00..07, GOV aliases, reserved IDs): `framework/governance/LINT_RULES.md`

**When to run:** Pre-commit (after CHG creation), pre-implementation (before code), pre-merge (before PR merge). Exit codes: 0 clean, 1 error(s) (STOP), 2 usage error, 3 missing prerequisite (PyYAML).

**IPLAN Gate (§3.13):** No code may be written without an IPLAN. The IPLAN must be `In Progress`, reference the authorizing CHG, and list the files being modified in its `file_manifest`. Every post-seed change carries both objects: bug fixes ride their IPLAN's CHG (active IPLAN) or the bugfix vehicle (C1 CHG + bugfix IPLAN); every C1 rides a C1 CHG + scoped IPLAN. The sole change needing neither object is seed-phase drafting pre-first-BRD (CHG-12).

### Push Workflow

```bash
# CORRECT workflow (per-task worktree — no exceptions):
git checkout dev
git pull origin dev
git worktree add ../<project>-<issue> -b feature/<short-name> origin/dev
cd ../<project>-<issue>
# ... make changes ...
git add <owned-files-only>
git commit -m "feat: description"
git push origin feature/<short-name>
# Then open PR: feature/<short-name> → dev

# WRONG — never do this:
git push origin main   # ❌ BLOCKED by this rule
```

Branch promotion: `feature-branch → dev → main`. Release (`dev` → `main`) PRs are prepared and watched like any PR, but merge only with in-session human OK — a release is an important decision, never auto-merged.

### Commit audit-trail phrase

Every push must carry one literal phrase in a commit-message body in the push
range (`grep -qF`; CI `call / verify` is a required context, so a missing
phrase blocks the merge):

- `Multi-agent self-review per OPS-0065 (<agents>): <verdict>` — run the
  review first, then write the phrase. The gate checks the string, not the
  review: the skip form asserts a founder OK it never verifies, so never
  write it without one.
- `Self-review skipped per founder OK — <reason>` — only with in-session
  founder authorization.

Exempt: bot-authored ranges and revert-only ranges. Enforced pre-push by
`hooks/pre_push_check.sh` (via pre-commit) and restated in
`.github/PULL_REQUEST_TEMPLATE.md`.

### Governance PRs

A PR touching the working agreement (`AGENTS.md`), `plans/*-PLAN.md` and
their `plans/*-DESIGN.md` companions, `plans/DECISIONS.md`,
`framework/governance/DECISIONS.md`, `.github/ai-review/`,
`.github/workflows/ai-review.yml`, or a change superseding a locked decision
is a governance PR: cap it at ≤3 doc surfaces — split into sequential PRs
beyond that, or record a founder OK in the PR plus an audit-trail line in the
commit message (splitting is the default, carve-out the exception) — and
self-review it adversarially before every push. Non-governance PRs (code,
tests, docs-only) have no surface cap. The definition lives here;
`.github/PULL_REQUEST_TEMPLATE.md` carries a copy.

All feature/defect work runs in a per-task worktree + branch (`WORKTREE_FLOW.md` §3.2) — the main checkout stays on `dev` and is never branch-switched for feature work. There is no quick-path exception: single-shot edits use the same worktree flow. Post-merge cleanup removes the worktree BEFORE deleting the branch (§3.8 order guard).

### Watching your PR

After opening a PR you own, poll its status every 15 seconds until required checks settle — never assume a push is green:

```bash
gh pr checks <N> --json name,state,bucket,workflow --jq '.[] | select(.bucket!="pass")'
```

`gh pr checks --required --watch` blocks until required checks settle and is preferred for a single wait; poll manually at 15s intervals when you need to interleave other work. Read `mergeStateStatus` before any merge decision (`BLOCKED` ends the question regardless of check colour).

Auto-merge is authorized by default: on a PR you opened, once all required checks pass and the PR is mergeable (`mergeStateStatus` CLEAN on the current head — confirm `headRefOid`), enable it (`gh pr merge <N> --auto --squash --delete-branch`, the repo's squash-only convention) and read the merge back. Withhold auto-merge when the user said hold, required checks are incomplete or red, a repo rule reserves the merge for a human, or the PR is not yours — tool access is not merge authority.

Merge conflicts: never force-push, never rebase a pushed branch — `git fetch origin dev && git merge origin/dev` in the worktree. Additive conflicts (changelogs, indexes, non-overlapping edits) resolve directly; semantic conflicts (logic, migrations, policy, deletions) mean `git merge --abort` and escalate to the human. After pushing the resolution, confirm auto-merge is still armed (`gh pr view <N> --json autoMergeRequest`) and re-enable if cleared.

Delete merged branches by default: `--delete-branch` removes the remote at merge time; afterwards remove the worktree first (`git worktree remove …` from the main checkout), then switch to `dev`, fast-forward, and delete the local branch (`git branch -D` — the squash-only convention defeats `-d`'s ancestry guard, so the merge-commit-on-target check is the safety) once the merge commit is on `dev` — worktree removal always precedes branch deletion, never the reverse (§3.8 order guard). Never delete a branch whose unique work is unverified on its target (under squash-only, "merged" is a PR fact, not ancestry — the merge-commit-on-target check is the proof).

Stale-branch sweep: a branch whose work is implemented must not linger past the session that landed it. Sweep at session end (`git fetch --prune` first): own branches only unless the user names others, never a branch with an open PR, worktree removal before branch deletion (§3.8). Merged branches die per the paragraph above once the local tip is confirmed to hold nothing beyond the merged head (`git branch -D` local, `git push origin --delete` remote). A branch closed-as-superseded dies only with in-session human OK after the verification is reported: every unique commit's substance diffed onto a named landing commit on the target — a closed PR alone is not proof. Promotion (`dev`/`staging`/`main`) and protected (`legacy-*`/`archive/*`) branches are never touched.

When a required check fails, fix every error: diagnose from the failed logs, fix on the PR branch, push, and re-watch from the new head (confirm `headRefOid` — a previous run's green is not this commit's). Never merge while red. Stop and report to the human when the same check fails twice after a fix attempt, or when the fix reaches beyond the PR's scope.

## Where state lives (this repo owns its own continuity)

| Surface | Path |
|---|---|
| Live handoff | GitHub issues (open vehicles) + `plans/<NAME>-PLAN.md` — no `plans/HANDOFF.md` exists; do not invent one |
| TODO / backlog | **GitHub issues** — `plans/FRAMEWORK-TODO.md` is a retired tombstone |
| Decisions | `plans/DECISIONS.md`; spec governance in `framework/governance/DECISIONS.md` |
| Plans | `plans/<NAME>-PLAN.md` |
| Changelog | `framework/CHANGELOG.md` (live record, GATE-SPEC-E008) — root `CHANGELOG.md` is a frozen tombstone carrying the documented `gh` query, not maintained per-PR — no `ROADMAP.md` exists |
| Lessons | `.aidoc/learning/learnings.md` — consolidated, PR-reviewed system of record; harness memory is scratch, never the record |

Never put any of these in `tmp/`, and never centralize them in the `aidoc-flow`
umbrella — the umbrella holds no development of its own.

## Tooling

- **GitHub: use the `gh` CLI**, not the GitHub MCP servers or raw API calls. If
  unauthenticated, run `gh auth login`.
- Sessions run in ephemeral containers: **only committed + pushed work
  survives.** Commit messages carry no model identifiers.
- Conventional commit prefixes (`docs:`, `feat:`, `fix:`, `refactor:`,
  `chore:`), one logical change per commit.
- **Advanced git:** [`.agents/skills/git-techniques/`](.agents/skills/git-techniques/SKILL.md)
  for reflog recovery, history search, bisect, and worktrees — read-only by
  default; destructive, remote, and config-changing operations need explicit
  approval.

## Unified CI — consume from `aidoc-flow-ci`

This repo's CI workflows call reusable workflows from
`vladm3105/aidoc-flow-ci`, the source of truth for shared CI logic. Local
always wins — GitHub runs this repo's `.github/workflows/*.yml`, and a shared
workflow runs only when called via `uses:`. Three override modes, preferred
order: parameter override (`with:` knob, keep the `uses:` call) → full
replacement (drop `uses:`, write local jobs) → new custom workflow file.

- A canon bump is a migration, not a dependency update: re-pin tags only
  (`--repin`), never `--update` — full-body replacement clobbers local
  customizations (self-hosted runner labels, secret-scan config, docs-sync
  permissions). Dependabot carries a `semver-major` hold on canon
  (`.github/dependabot.yml`), so majors arrive as deliberate PRs.
- Drift detection is warning-only, never blocking: re-baseline to canonical,
  keep intentionally, or push the divergence upstream as a new shared default
  (broadly useful changes go to `aidoc-flow-ci` first, then re-pin here).
- **Self-hosted norm for private repos.** Private consumers run CI on
  self-hosted runners — keep shared and canon-bound workflow logic
  runner-portable (no GitHub-hosted-only tooling, caches, or egress
  assumptions); runner selection itself stays a consumer `ci_bindings` pin
  (`ADAPTATION.md` §4.7), never framework content.
