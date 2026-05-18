# Repository Structure — AI Doc Flow Framework (Multi-Platform)

> Status: PLANNED target structure. Created 2026-05-18.
> This is the layout the repository converges to at cutover (Phase 5),
> when the new project replaces `main`.

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

## Legacy → Target Mapping

| Legacy (current `main`)                     | Target location                         |
|----------------------------------------------|------------------------------------------|
| `ucx_flow_v3/01_BRD … 08_IPLAN/`             | `framework/layers/`                      |
| `ucx_flow_v3/LAYER_REGISTRY.yaml`            | `framework/registry/`                    |
| `ucx_flow_v3/CHG/`, `governance/`            | `framework/governance/`                  |
| `ucx_hermes/`, `mcp_ucx/`                    | `platforms/hermes/`                      |
| `.claude/` skills (`doc-*`), agents, commands | `platforms/claude-code-plugin/`          |
| `ai_dev_ssd_flow_v2/`                        | archived (superseded by `framework/`)    |
| `roadmap/`, `changelog/` (legacy)            | archived; replaced by root `ROADMAP.md` / `CHANGELOG.md` |

> Moves are executed in Phases 1–3, not during planning. This table records intent.
