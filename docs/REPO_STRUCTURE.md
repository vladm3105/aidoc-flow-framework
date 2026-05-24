# Repository Structure — AI Doc Flow Framework (Multi-Platform)

> Status: **as-built (post-migration).** Created 2026-05-18; the repository
> converged to this layout through Phases 1–5. The `legacy/` tree has been
> removed (preserved as the protected `legacy-ucx-v3.2-read-only` branch);
> the new project replaces `main` at the Phase 5 cutover (`v1.0.0`).

## Principles

1. **One spec, two engines.** The document-flow framework is an engine-agnostic
   specification. Hermes AI and the Claude Code plugin are two *independent*
   implementations of it. They share the spec, never runtime code.
2. **Separate directories now.** Each platform owns its own tree, version,
   and changelog from the start.
3. **The framework spec is the contract.** Both platforms declare which
   `framework_spec_version` they conform to.

## Target Layout

```
aidoc-flow-framework/
├── README.md                       Project overview, platform matrix
├── ROADMAP.md                      Phased delivery plan (project-level)
├── CHANGELOG.md                    Project-level changelog (Keep a Changelog)
├── LICENSE
├── docs/
│   ├── REPO_STRUCTURE.md            This file
│   ├── PROJECT.md                   Project management: versioning, branches, milestones
│   └── architecture/                Decision records (MADR markdown)
│
├── framework/                       SHARED engine-agnostic specification (the contract)
│   ├── VERSION                      Framework spec SemVer
│   ├── layers/                      01_BRD … 08_IPLAN: definitions, templates, schemas
│   ├── governance/                  Governance rules, CHG overlay, gate definitions
│   └── registry/LAYER_REGISTRY.yaml
│
├── platforms/
│   ├── hermes/                      PLATFORM A — Hermes AI (MCP-server engine)
│   │   ├── VERSION
│   │   ├── CHANGELOG.md
│   │   ├── README.md
│   │   └── src/ tests/ ...
│   │
│   └── claude-code-plugin/          PLATFORM B — Claude Code plugin (native engine)
│       ├── .claude-plugin/plugin.json
│       ├── VERSION
│       ├── CHANGELOG.md
│       ├── README.md
│       ├── skills/                  doc-* skill set (the engine)
│       ├── commands/                slash commands
│       ├── agents/                  subagents
│       └── hooks/
│
└── tests/
    └── conformance/                 Shared suite both platforms must pass
```

## Legacy → Target Mapping (historical record)

This table records **where the pre-migration content went** during
Phases 1–3. The `legacy/` tree it refers to has since been removed from the
working tree (Phase 5 / P5-T2) and preserved intact on the protected
`legacy-ucx-v3.2-read-only` branch.

| Legacy (was under `legacy/`)                     | Target location                         |
|--------------------------------------------------|------------------------------------------|
| `legacy/ucx_flow_v3/01_BRD … 08_IPLAN/`          | `framework/layers/`                      |
| `legacy/ucx_flow_v3/LAYER_REGISTRY.yaml`         | `framework/registry/`                    |
| `legacy/ucx_flow_v3/CHG/`, `legacy/governance/`  | `framework/governance/`                  |
| `legacy/ucx_hermes/`, `legacy/mcp_ucx/`          | `platforms/hermes/`                      |
| `.claude/` skills (`doc-*`), agents, commands    | `platforms/claude-code-plugin/`          |
| `legacy/ai_dev_ssd_flow_v2/`                     | dropped (superseded by `framework/`)     |
| `legacy/roadmap/`, `legacy/changelog/`           | dropped; replaced by root `ROADMAP.md` / `CHANGELOG.md` |
| `legacy/github-workflows-disabled/`              | rewritten fresh per platform             |

> Content was **copied** out of `legacy/` and adapted during Phases 1–3 (the
> legacy copy stayed untouched throughout). At the Phase 5 cutover the
> `legacy/` tree was **removed** from the working tree (P5-T2) and the pristine
> pre-migration project is preserved on the protected, read-only branch
> **`legacy-ucx-v3.2-read-only`**. The root `.claude/` skill set was ported
> into the Claude Code plugin in Phase 3; the root loader is removed at cutover
> (the plugin is the distribution).
