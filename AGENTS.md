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

## Filing gaps — TODO entry **and** GitHub issue

When you find a defect, inconsistency, or missing capability, it gets **both**:

1. An entry in `plans/FRAMEWORK-TODO.md` — the triage queue. Inline as
   discovered: tag + one-line title + *Context* (what surfaced it) + *Fix shape*.
   The entry IS the capture moment; there is no "later PR".
2. **A GitHub issue on this repo** when the entry is (a) actionable by someone
   other than you, (b) reproducible at `file:line` with a concrete fix shape, or
   (c) user-visible / blocks a consumer. Speculative or purely local items stay
   TODO-only.

The issue body carries: reproduction at `file:line`, blast radius, why it was
hard to diagnose, a suggested fix, and what is **not** broken. One issue per
defect. Link both ways — the TODO heading ends with `→ #N`, the issue names the
TODO entry ID — and close both on the same merge SHA.

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
| TODO / backlog | `plans/FRAMEWORK-TODO.md` |
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
