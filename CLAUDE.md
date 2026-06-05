# CLAUDE.md — Project Memory

Persistent context for the **AI Doc Flow Framework**. Auto-loaded every
session. Keep it short and current.

## What this project is

The document-flow framework, delivered as **one engine-agnostic specification
(`framework/`) with two independent platforms**:

- **Platform A — Hermes AI** — MCP-server engine (`platforms/hermes/`).
- **Platform B — Claude Code plugin** — native Claude Code engine, no MCP
  (`platforms/claude-code-plugin/`).

The platforms share the `framework/` spec and nothing else. Both pass the same
shared conformance suite (`tests/conformance/`). The `framework/` spec defines
the 8-layer SDD flow (BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code).

**Current state (as of 2026-06-01):** framework spec `0.11.0`, Claude Code plugin `0.4.0` (pre-1.0 preview, 52 skills = 50 active + 2 deprecated stubs). IPLAN ↔ iplanic integration deferred — see `plans/IPLAN-IPLANIC-DEFERRED.md`.

## Durable conventions

- **The framework spec is the contract.** Engine-agnostic; carries no platform
  names or runtime code. Each platform declares the spec version it conforms to
  in `platforms/<name>/FRAMEWORK_SPEC_VERSION`, which must match
  `framework/VERSION`.
- **Conformance must stay green.** `tests/conformance/` is the runnable
  contract; never weaken a check to make it pass — fix the spec or the
  platform.
- **Single source of truth for templates (D-0013).** Platforms consume
  `framework/layers/<NN>_<X>/`; they never ship their own copies.
- **Tagging:** `docs/TAGGING.md` — release tags `vX.Y.Z` (project),
  `framework/vX.Y.Z`, `<platform>/vX.Y.Z`; `mark/<slug>` bookmarks. `VERSION`
  files hold bare SemVer; the tag adds the `v` + namespace.
- **Versioning streams are independent** (`docs/PROJECT.md` §2): project,
  framework spec, and each platform version separately.

## Development workflow (guidance)

Recommended flow for non-trivial changes — plan → review → implement →
verify → land:

1. **Plan** into `plans/` (start from `plans/PLAN-TEMPLATE.md`) before touching
   code.
2. **Two-cycle gap review (mandatory)** — once a plan is created, it MUST
   complete at least **two full review cycles** before implementation begins.
   Each cycle = *review to identify gaps → patch the plan to address every
   gap → re-review the patched plan*. The plan is ready for impl only when
   the second cycle's re-review surfaces no new substantive gaps (or all
   surfaced gaps have been folded into the plan via further patches).
   Record every cycle in the plan's `## Review log` with an ISO-stamped
   `Pass N` entry that lists the gaps found and how each was resolved.
   Cycle N+1 must always re-validate that cycle N's patches did not
   introduce new inconsistencies. Continue cycling until a review surfaces
   nothing; minimum is two cycles. Skipping the second cycle is forbidden
   — the rule exists because every plan touched in this repo so far has
   surfaced material gaps in the second pass that the first pass missed.
3. **Implement**, updating the plan with ISO-stamped progress.
4. **Verify** — run the conformance suite + the platform's own tests; nothing
   is "done" until they pass.
5. **Land** — one logical change per commit, conventional prefix (`docs:`,
   `feat:`, `fix:`, `refactor:`, `chore:`); update `CHANGELOG.md` / `ROADMAP.md`
   as needed.

Record non-obvious choices in `plans/DECISIONS.md` (ISO-stamped).

## Session handoff

Sessions run in ephemeral containers — preserve continuity in the repo:

- Maintain `plans/HANDOFF.md` — progress, achievements, next steps, open
  questions; refresh at milestones and before any context compaction.
- Start each session by reading `plans/HANDOFF.md`.
- **Only committed + pushed work survives.** Commit messages must not contain
  model identifiers.

## Where things are

- `framework/` — the engine-agnostic SDD specification (layers, registry,
  governance). `framework/README.md` is the spec overview.
- `platforms/hermes/` — Platform A (MCP server).
- `platforms/claude-code-plugin/` — Platform B (Claude Code plugin).
- `tests/conformance/` — the shared conformance suite (framework + platform
  checks).
- `ROADMAP.md` — phased delivery plan (Phase 0 → cutover `v1.0.0`).
- `CHANGELOG.md` — project-level changelog.
- `docs/PROJECT.md` — versioning, branching, conformance, change management.
- `docs/REPO_STRUCTURE.md` — repository layout (as-built).
- `docs/TAGGING.md` — git-tag policy. `docs/PARITY.md` — platform comparison.
- `plans/` — the migration record (per-task plans, audits, verify records,
  `DECISIONS.md`, `HANDOFF.md`, `MIGRATION_TODO.md`).

## Pre-migration history

This project was migrated from the pre-migration `ucx_framework` (v0.20.4).
The pristine pre-migration project is preserved on the protected, read-only
branch **`legacy-ucx-v3.2-read-only`**. Change management (the gated CHG
process) returns post-cutover to govern `framework/` spec changes — see
`docs/PROJECT.md` §6.
