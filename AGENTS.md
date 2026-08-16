# AGENTS.md — working agreement for AI coding agents on aidoc-flow-framework

Orients any AI agent (Claude Code, Codex, Gemini CLI, Copilot, Hermes, custom)
working on this repo. **[`CLAUDE.md`](CLAUDE.md) is the full working agreement**;
this file is the short orientation plus the rules that are most often missed.
Where the two disagree, `CLAUDE.md` wins — fix this file.

## What this repo is

One engine-agnostic specification (`framework/`) and two independent platforms
that consume it: **Hermes** (MCP server, `platforms/hermes/`) and the **Claude
Code plugin** (`platforms/claude-code-plugin/`). The spec defines the 8-layer SDD
flow (BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code). Both platforms
pass the same shared conformance suite (`tests/conformance/`).

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
test is ownership, not severity. See `CLAUDE.md` → "Cross-repo feedback".

**Verify what you published.** Use `gh issue create --body-file -`; `--body -`
sets the body to a literal `-`, exits 0, and prints a URL, so it looks like it
worked. Read it back:

```sh
gh issue view <N> -R vladm3105/aidoc-flow-framework --json body --jq '.body | length'
```

## Non-negotiables

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
- **Plans get two review cycles before the plan PR opens** — see `CLAUDE.md`
  → "Development workflow".

## Where state lives (this repo owns its own continuity)

| Surface | Path |
|---|---|
| Live handoff | `plans/HANDOFF.md` — read it first, every session |
| TODO / backlog | **GitHub issues** — `plans/FRAMEWORK-TODO.md` is a retired tombstone |
| Decisions | `plans/DECISIONS.md`; spec governance in `framework/governance/DECISIONS.md` |
| Plans | `plans/<NAME>-PLAN.md` |
| Changelog / roadmap | `CHANGELOG.md`, `ROADMAP.md` |

Never put any of these in `tmp/`, and never centralize them in the `aidoc-flow`
umbrella — the umbrella holds no development of its own.

## Tooling

- **GitHub: use the `gh` CLI**, not the GitHub MCP servers or raw API calls. If
  unauthenticated, run `gh auth login`.
- Sessions run in ephemeral containers: **only committed + pushed work
  survives.** Commit messages carry no model identifiers.
- Conventional commit prefixes (`docs:`, `feat:`, `fix:`, `refactor:`,
  `chore:`), one logical change per commit.

Everything else — CI consumption from `aidoc-flow-ci`, governance PR discipline,
auto-merge defaults, multi-agent review, versioning and tagging — is in
[`CLAUDE.md`](CLAUDE.md).
