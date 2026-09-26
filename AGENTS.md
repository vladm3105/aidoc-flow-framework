# AGENTS.md — working agreement for AI coding agents on aidoc-flow-framework

Orients any AI agent (Claude Code, Codex, Gemini CLI, Copilot, Hermes, custom)
working on this repo. **This file is the single working agreement** — the short
orientation plus the rules that are most often missed.
[`CLAUDE.md`](CLAUDE.md) is deprecated: legacy detail only, never authority.
Where the two disagree, this file wins.

## What this repo is

One engine-agnostic specification (`framework/`) defining the 10-layer SDD
flow (BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → CHG → EVAL → Code).
Platforms (Hermes MCP server, Claude Code plugin) were archived — any capable AI
agent derives its behavior from the framework spec, templates, and playbooks
directly. The repo ships `sdd_doc_lint/` (structural linter) and `hooks/`
(PostToolUse advisory hook) as the only retained tooling.

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
only `#A`).

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
- **Never hand-edit example artifacts.** Files under `examples/<name>/docs/` and
  `examples/<name>/.aidoc/` are the system-under-test. Remediate them by
  dispatching the framework's own skills; a class of remediation the skills
  cannot handle is a **framework workflow gap**, never a reason to edit the
  artifact.
- **Conformance stays green.** Never weaken a check in `tests/conformance/` to
  make it pass — fix the spec or the platform.
- **The spec is the contract.** `framework/` is engine-agnostic: no platform
  names, no runtime code. Platforms consume `framework/layers/<NN>_<X>/`; they
  never ship their own copies (D-0013).
- **Submit only finalized work.** A PR has already completed its review-and-fix
  cycles locally. Amendment PRs patching a just-merged PR are a smell that the
  original shipped early.
- **Plans get two review cycles before the plan PR opens.**
- **One task, one worktree.** Feature/defect work runs in a per-task `git worktree` + branch (`feature/<issue-or-chg>-<slug>`), never in the main checkout; main checkout stays on `dev`. See `framework/governance/WORKTREE_FLOW.md` (§1 invariants, §3.7 order guard: `worktree remove` BEFORE branch delete, §4).

## Governance Gate (applies to ALL agents)

Before writing ANY code for a feature, enhancement, or non-bugfix change:

1. Create a CHG document — do NOT write code first
2. Complete §3.4 checklist BEFORE writing the CHG
3. Run §3.4.1 validation AFTER writing the CHG, BEFORE committing
4. Update EARS/BDD before code (SDD-first — F1/F3 only; F2 carries an empty lifecycle, F4 leaves the parent SDD standing)
5. Create IPLAN with code steps (not in CHG)

Classify first: Emergency → Type-R → F4 → F3 → F2 → F1 — see `framework/governance/CHG_REQUEST_FLOWS.md` (ratified 0.57.0).

If user says "build", "implement", "add feature" → stop, create CHG first.
Exceptions (not one): (i) bug fixes on active IPLANs (no CHG); (ii) docs-only non-normative C1 (direct commit);
(iii) post-completion repairs via the bugfix vehicle (C1 CHG + bugfix IPLAN, parent immutable);
(iv) F2 C1-direct (C1 CHG + scoped IPLAN). §3.13 + `CHG_REQUEST_FLOWS.md` govern.

**Automated CHG validation:** Run `python3 sdd_doc_lint/chg_lint.py <chg-file.yaml>` to check:

- CHG-L001: Status lifecycle (§3.3) — must follow Proposed → Approved → In-Progress → Implemented → Completed
- CHG-L002: Gate approval (§3.1) — C3 changes must have approver
- CHG-L003: CHG scope (§3.4) — no code steps in CHG
- CHG-L004: IPLAN reference (§3.1.1) — must reference an IPLAN
- CHG-L005: SDD-first order (§3.1.1) — SDD lifecycle before IPLAN
- CHG-L013: Flow misfit (§3.1.3) — code manifest + empty lifecycle + wrong source (GOV-018; names F2/F3/F4)
- Full catalog (L006–L012, BGF-01..07): `framework/governance/LINT_RULES.md`

**When to run:** Pre-commit (after CHG creation), pre-implementation (before code), pre-merge (before PR merge). Exit code 0=pass, 1=errors (STOP).

**IPLAN Gate (§3.13):** No code may be written without an IPLAN. The IPLAN must be `In Progress` and reference the authorizing CHG. Governed paths without a full CHG cascade: bug fixes on active IPLANs; post-completion repairs via the bugfix vehicle; F2 C1-direct (scoped IPLAN). Docs-only non-normative C1 needs neither CHG nor IPLAN.

### Push Workflow

```bash
# CORRECT workflow:
git checkout dev
git pull origin dev
git checkout -b feat/my-change
# ... make changes ...
git add .
git commit -m "feat: description"
git push origin feat/my-change
# Then open PR: feat/my-change → dev

# WRONG — never do this:
git push origin main   # ❌ BLOCKED by this rule
```

Branch promotion: `feature-branch → dev → main`

Trivial single-shot edits may use the quick path above. Multi-step feature work (or any work with running subagents): use `WORKTREE_FLOW.md` §3.2 (`worktree add ../<project>-<issue> -b feature/<short-name> origin/dev`) instead of branch-switching the main checkout.

## Where state lives (this repo owns its own continuity)

| Surface | Path |
|---|---|
| Live handoff | GitHub issues (open vehicles) + `plans/<NAME>-PLAN.md` — no `plans/HANDOFF.md` exists; do not invent one |
| TODO / backlog | **GitHub issues** — `plans/FRAMEWORK-TODO.md` is a retired tombstone |
| Decisions | `plans/DECISIONS.md`; spec governance in `framework/governance/DECISIONS.md` |
| Plans | `plans/<NAME>-PLAN.md` |
| Changelog | `CHANGELOG.md` (root) + `framework/CHANGELOG.md` — no `ROADMAP.md` exists |

Never put any of these in `tmp/`, and never centralize them in the `aidoc-flow`
umbrella — the umbrella holds no development of its own.

## Tooling

- **GitHub: use the `gh` CLI**, not the GitHub MCP servers or raw API calls. If
  unauthenticated, run `gh auth login`.
- Sessions run in ephemeral containers: **only committed + pushed work
  survives.** Commit messages carry no model identifiers.
- Conventional commit prefixes (`docs:`, `feat:`, `fix:`, `refactor:`,
  `chore:`), one logical change per commit.

Further detail — CI consumption from `aidoc-flow-ci`, governance PR discipline,
auto-merge defaults, multi-agent review, versioning and tagging — lives in
[`CLAUDE.md`](CLAUDE.md) (deprecated legacy detail, pending migration into this
file). On any conflict, this file wins.
