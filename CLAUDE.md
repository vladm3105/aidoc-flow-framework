# CLAUDE.md — Project Memory

Persistent context for the **multi-platform migration** of the AI Doc Flow
Framework. Auto-loaded every session. Keep it short and current.

## What this project is

Delivering the document-flow framework as **one engine-agnostic specification
(`framework/`) with two independent platforms**:

- **Platform A — Hermes AI** — MCP-server engine (`platforms/hermes/`).
- **Platform B — Claude Code plugin** — native Claude Code engine, no MCP
  (`platforms/claude-code-plugin/`).

The platforms share the `framework/` spec and nothing else.

## Current state

- **Working branch:** `claude/multi-platform-migration-AamWB` — all work goes
  here. `main` is locked; never push to it without explicit permission.
- **Phase:** Phase 1 — Framework Spec Extraction (Phase 0 complete; Phase 1
  Step 0 legacy isolation complete).
- The repo is mid-restructure — root holds the new project; the frozen
  pre-migration project lives under `legacy/`.

## Rules

- **Legacy is frozen.** `legacy/` is read-only history. **Copy** content out of
  it and adapt — never move or edit files in place. `legacy/` is removed at the
  Phase 5 cutover.
- **Never push to `main`.** Only the working branch above.
- Legacy CI is disabled (parked in `legacy/github-workflows-disabled/`).

## Where things are

- `ROADMAP.md` — stable phased plan (Phase 0 → cutover v1.0.0).
- `plans/MIGRATION_TODO.md` — **live task tracker**; update it as work lands
  (check `[x]` only when committed + pushed).
- `plans/README.md` — migration workspace conventions.
- `docs/PROJECT.md` — versioning, branching, conformance, change management.
- `docs/REPO_STRUCTURE.md` — target layout + `legacy/` → target mapping.

## Environment

Ephemeral cloud container, re-cloned each session. **Only committed + pushed
work survives.** Commit messages must not contain model identifiers.
