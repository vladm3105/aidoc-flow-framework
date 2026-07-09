# Repository Structure — AI Doc Flow Framework (Multi-Platform)

> Status: **as-built (post-cutover).** Created 2026-05-18; the repository
> converged to this layout through Phases 1–5 and replaced `main` at the
> `v1.0.0` cutover. The `legacy/` tree was removed (preserved on the protected
> `legacy-ucx-v3.2-read-only` branch). Post-v1.0 additions (CI + security
> tooling, the GATE-SPEC change gate, the adaptation overlay) are reflected below.

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
├── ROADMAP.md                      Delivery plan + post-v1.0 work
├── CHANGELOG.md                    Project-level changelog (Keep a Changelog)
├── SECURITY.md                     Security policy / vulnerability reporting
├── LICENSE
├── .pre-commit-config.yaml         Pre-commit hooks (lint / format / security)
├── ruff.toml · .markdownlint.json · .markdownlintignore · .yamllint · .secrets.baseline
├── .github/
│   ├── workflows/                  CI: ai-review, audit-trail, auto-merge-ai-prs, chg-gate, codeql, composition, conformance, doc-review, hermes, labeler, plugin, pre-commit, standards-drift
│   ├── CODEOWNERS · dependabot.yml · labeler.yml
│   └── ISSUE_TEMPLATE/ · PULL_REQUEST_TEMPLATE.md
├── docs/
│   ├── REPO_STRUCTURE.md            This file
│   ├── PROJECT.md                   Versioning, branches, milestones, change management
│   ├── PARITY.md                    Hermes ↔ plugin capability comparison
│   ├── TAGGING.md                   Git-tag policy
│   ├── SUPPORT.md                   Support channels + how to get help
│   └── STARTUP_HANDOFF.md
│
├── framework/                       SHARED engine-agnostic specification (the contract)
│   ├── VERSION                      Framework spec SemVer
│   ├── layers/                      01_BRD … 08_IPLAN: definitions, templates, schemas
│   ├── governance/                  Rules; CHG overlay (gates incl. GATE-SPEC);
│   │                                ADAPTATION surface; DECISIONS.md (GD register)
│   └── registry/LAYER_REGISTRY.yaml
│
├── platforms/
│   ├── hermes/                      PLATFORM A — Hermes AI (MCP-server engine)
│   │   ├── FRAMEWORK_SPEC_VERSION   Spec version it conforms to
│   │   └── VERSION · CHANGELOG.md · README.md · src/ · tests/
│   │
│   └── claude-code-plugin/          PLATFORM B — Claude Code plugin (native engine)
│       ├── .claude-plugin/          plugin.json + marketplace.json
│       ├── FRAMEWORK_SPEC_VERSION   Spec version it conforms to
│       └── VERSION · README.md · skills/ · commands/ · agents/
│
├── tests/
│   ├── conformance/                 Shared suite both platforms must pass
│   └── chg/                         GATE-SPEC diff-aware guard (spec_gate.py)
│
├── tools/                 # sync-plugin-framework.sh, build-plugin-mirror.sh, sdd_doc_lint/
├── examples/              # url-shortener/ — acceptance-test example
│   └── url-shortener/
│       ├── seed/                    Human input — the acceptance-test seed
│       ├── chg/                     Human input — change request for Phase 2
│       ├── docs/                    AI output — produced 8-layer chain (committed)
│       ├── .aidoc/                  AI provenance — audit/review/remediation/validation
│       │                            reports (committed). See framework/docs/AIDOC.md
│       └── logs/<TS>/               Tool internals — gitignored, ephemeral
└── plans/                           Migration record: per-task plans, DECISIONS.md, HANDOFF.md, …
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
