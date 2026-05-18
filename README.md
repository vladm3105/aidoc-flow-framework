# AI Doc Flow Framework

A specification-driven document-flow framework for AI-assisted software
development, delivered as **one engine-agnostic specification with two
independent platforms**.

> Status: early restructure (Phase 0 — planning). See `ROADMAP.md`.

## Architecture

```
framework/                  Engine-agnostic specification (the shared contract)
platforms/
  hermes/                   Platform A — Hermes AI (MCP-server engine)
  claude-code-plugin/       Platform B — Claude Code plugin (native engine)
legacy/                     Frozen pre-migration project (ucx_framework v0.20.4)
```

The `framework/` spec defines the 8-layer SDD flow
(BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code), schemas, templates,
and governance. Each platform is an independent implementation of that spec —
they share the specification and nothing else.

## Platforms

| Platform | Engine | Status |
|----------|--------|--------|
| **Hermes AI** | MCP server | re-homed in Phase 2 |
| **Claude Code plugin** | Native Claude Code (skills / agents / commands / hooks) | built in Phase 3 |

## Documentation

- `ROADMAP.md` — phased delivery plan (Phase 0 → cutover v1.0.0).
- `CHANGELOG.md` — project-level changelog.
- `docs/REPO_STRUCTURE.md` — target repository layout and legacy mapping.
- `docs/PROJECT.md` — versioning, branching, milestones, conformance, change management.
- `legacy/README.md` — about the frozen pre-migration tree.

## Migration in progress

This repository is mid-restructure. The pre-migration project is preserved,
frozen, under `legacy/`. The current `main` branch is locked; all work happens
on the migration branch until the Phase 5 cutover replaces `main`.
