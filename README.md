# AI Doc Flow Framework

A specification-driven document-flow framework for AI-assisted software
development, delivered as **one engine-agnostic specification with two
independent platforms**.

## Architecture

```
framework/                  Engine-agnostic specification (the shared contract)
platforms/
  hermes/                   Platform A — Hermes AI (MCP-server engine)
  claude-code-plugin/       Platform B — Claude Code plugin (native engine)
tests/
  conformance/              Shared suite both platforms must pass
```

The `framework/` spec defines the 8-layer SDD flow
(BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code), schemas, templates,
and governance. Each platform is an independent implementation of that spec —
they share the specification and nothing else, and both pass the same
conformance suite at `tests/conformance/`.

## Platforms

| Platform | Engine | Release |
|----------|--------|---------|
| **Hermes AI** | MCP server | `hermes/v0.1.0` (`platforms/hermes/`) |
| **Claude Code plugin** | Native Claude Code (skills / agents / commands) | `claude-code-plugin/v0.2.0` (`platforms/claude-code-plugin/`) |

See [`docs/PARITY.md`](docs/PARITY.md) for the capability comparison and a
"which platform should I use?" guide.

### Install the Claude Code plugin

This repo doubles as a plugin marketplace (`.claude-plugin/marketplace.json`).
From Claude Code:

```
/plugin marketplace add vladm3105/aidoc-flow-framework
/plugin install aidoc-flow@aidoc-flow-framework
```

## Documentation

- `ROADMAP.md` — phased delivery plan (Phase 0 → cutover `v1.0.0`).
- `CHANGELOG.md` — project-level changelog.
- `docs/REPO_STRUCTURE.md` — repository layout (as-built).
- `docs/PROJECT.md` — versioning, branching, milestones, conformance, change management.
- `docs/TAGGING.md` — git-tag policy (release + bookmark tags).
- `docs/PARITY.md` — Hermes ↔ plugin capability comparison.
- `framework/README.md` — the engine-agnostic SDD specification.

## Pre-migration history

This project was migrated from the pre-migration `ucx_framework` (v0.20.4)
into the multi-platform structure above. The **pristine pre-migration project**
is preserved on the protected, read-only branch
**`legacy-ucx-v3.2-read-only`** (`git checkout legacy-ucx-v3.2-read-only`).
The full migration record — per-task plans, audits, verify records, and the
decision log — lives under `plans/`.
