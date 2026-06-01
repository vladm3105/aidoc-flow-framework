# AI Doc Flow Framework

**AI Doc Flow Framework** is a structured workflow for
**Specification-Driven Development (SDD)** with AI coding assistants. It
guides a project through an 8-layer documentation chain — from business
intent down to executable implementation plans — so AI tools read, audit,
and act on a verifiable spec rather than ad-hoc prompts.

```text
BRD  →  PRD  →  EARS  →  BDD  →  ADR  →  SPEC  →  TDD  →  IPLAN  →  Code
business  product  formal  executable  decision  component  test    impl
intent    reqs     reqs    scenarios   record    contract   suite   plan
```

Each layer has its own template, contract, and quality gate. The framework
owns the engine-agnostic specification; two independent platforms (Hermes
MCP server, Claude Code plugin) each implement it. Both pass the same
conformance suite.

**What you get:**

- Templates + schemas for every layer.
- Cumulative `@upstream:` traceability tags from BRD all the way to code.
- Deterministic lint (`sdd_doc_lint`) for structural correctness.
- Conformance-tested outputs across both platforms.

**Use it when** you want AI-assisted development backed by a verifiable
specification trail, not ad-hoc prompts that produce inconsistent or
hard-to-audit output.

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
| **Hermes AI** | MCP server | `hermes/v0.1.1` (`platforms/hermes/`) |
| **Claude Code plugin** | Native Claude Code (skills / agents / commands) | `claude-code-plugin/v0.4.0` (`platforms/claude-code-plugin/`) |

See [`docs/PARITY.md`](docs/PARITY.md) for the capability comparison and a
"which platform should I use?" guide.

### Install the Claude Code plugin

This repo doubles as a plugin marketplace (`.claude-plugin/marketplace.json`).
From Claude Code:

```
/plugin marketplace add vladm3105/aidoc-flow-framework
/plugin install aidoc-flow@aidoc-flow-framework
```

## Status

The migration is complete (cutover shipped as `v1.0.0`); the project is now in
**post-cutover development** — latest project release `v1.1.0`, framework spec
`0.11.0`. The Claude Code plugin (`platforms/claude-code-plugin/`) is currently a **pre-1.0 preview** (v0.4.0); APIs and surfaces may change before 1.0. The framework spec is stable at `0.11.0`. Post-v1.0 work to date: the project adaptation overlay, the
GATE-SPEC change-management gate (`framework/governance/chg/`), the
authoring-style/spec quality updates through framework `0.11.0`, and the
pre-commit + CI security tooling (CodeQL, bandit, detect-secrets, pip-audit,
Dependabot).

## Contributing

Enable the pre-commit hooks before committing:

```sh
pip install pre-commit && pre-commit install
```

See `.pre-commit-config.yaml` for the hook set and [`SECURITY.md`](SECURITY.md)
for the vulnerability-reporting policy.

## Documentation

- `ROADMAP.md` — delivery plan and post-v1.0 work (migration complete at `v1.0.0`).
- `CHANGELOG.md` — project-level changelog.
- `SECURITY.md` — security policy and vulnerability reporting.
- `docs/REPO_STRUCTURE.md` — repository layout (as-built).
- `docs/PROJECT.md` — versioning, branching, milestones, conformance, change management.
- `docs/TAGGING.md` — git-tag policy (release + bookmark tags).
- `docs/PARITY.md` — Hermes ↔ plugin capability comparison.
- `framework/README.md` — the engine-agnostic SDD specification.
- [`docs/STARTUP_HANDOFF.md`](docs/STARTUP_HANDOFF.md) — historical session brief from the Phase-3/4 migration period.

## Pre-migration history

This project was migrated from the pre-migration `ucx_framework` (v0.20.4)
into the multi-platform structure above. The **pristine pre-migration project**
is preserved on the protected, read-only branch
**`legacy-ucx-v3.2-read-only`** (`git checkout legacy-ucx-v3.2-read-only`).
The full migration record — per-task plans, audits, verify records, and the
decision log — lives under `plans/`.
