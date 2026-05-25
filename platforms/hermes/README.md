# hermes-server — Hermes MCP server platform

The **MCP-server** delivery of the AI Doc Flow framework. Hermes hosts the
SDD engine as a Model Context Protocol server: any MCP-compatible client
(Claude Code, custom integrations) connects over stdio or HTTP and invokes
the `sdd_*` tools to validate, generate, score, and remediate documents.
No native Claude Code integration; clients talk MCP.

## What's inside

| Component | Count | Path |
|-----------|------:|------|
| Source modules | 18 | `src/mcp_server/` — `cleanup`, `cli`, `consistency`, `core`, `creation`, `executor`, `link_validation`, `models`, `preflight`, `prescreening`, `prompts`, `remediation`, `reporting`, `review`, `scan`, `scoring`, `skills`, `utils`, `validation` |
| Tests (pytest) | 447 | `tests/` — unit, integration, contract |
| MCP prompts | 46 | `prompts/` + `prompts/templates/` |
| Personas | 15 | `skills/personas/` |
| Platform-specific skills | 5 | `skills/hermes/` — `ucx-github-deploy-governance`, `ucx-github-governance`, `ucx-kb-context`, `ucx-kb-maintenance`, `ucx-sdd-bridge` |
| Agent-skills package | 181 | `agent-skills/spec-driven-development/` — `sdd-orchestrator` + `sdd-review-personas` |
| Docs | 80 | `docs/` — `CHANGELOG/`, `architecture/`, `plans/`, `policies/`, `specs/` |

## Install

Hermes ships as a Python package. From the platform root:

```sh
pip install -e .
```

This installs the `hermes-mcp` script entry point. Add to an MCP
client's config (root-level `.mcp.json` in this repo is set up as
a reference):

```jsonc
{
  "mcpServers": {
    "sdd-lifecycle": {
      "command": "/path/to/python",
      "args": ["-m", "mcp_server.server"],
      "cwd": "/path/to/aidoc-flow-framework/platforms/hermes/src"
    }
  }
}
```

## Use

Hermes exposes **platform-wide MCP tools** for the SDD workflow:

| Tool | Purpose |
|------|---------|
| `sdd_init` | Scaffold `<project>/UCX/` from `framework/layers/` |
| `sdd_validate` | Structural validation of an artifact against its layer template |
| `sdd_validate_chg` | CHG (Change Management) artifact validation |
| `sdd_validate_links` | Cross-document link validation |
| `sdd_score_validate` | Readiness scoring (quality gate) |
| `sdd_score_show` / `sdd_score_compare` | Score inspection / diff |
| `sdd_preflight` | Environment / input readiness check |
| `sdd_consistency` | Cross-document traceability check |
| `sdd_create` / `sdd_create_build` | Artifact authoring + template build |
| `sdd_review` | Review workflow |
| `sdd_scan` | Project scan |

The MCP client picks the tool; Hermes operates on any of the 8 SDD
layers (BRD, PRD, EARS, BDD, ADR, SPEC, TDD, IPLAN) generically.

## Framework spec conformance

Hermes consumes the engine-agnostic SDD specification at
`../../framework/` (layer templates, registry, governance). Two
version declarations:

```sh
$ cat VERSION
0.1.0

$ cat FRAMEWORK_SPEC_VERSION
0.1.0
```

Hermes declares conformance to framework spec `0.1.0`; the
framework's own version is at `../../framework/VERSION`. The Phase 4
conformance suite enforces this declaration matches.

### Review / remediation / gate triggers

Hermes binds the spec's review→remediation→gate trigger points
(`../../framework/governance/REVIEW_REMEDIATION_FLOW.md`) to its existing
runtime: server-side `validation/` + scoring covers `on_author` (on-demand
validate/score) and `pre_promotion` (the readiness gate before the next layer);
the `UCRem_*` remediation prompts cover `on_gate_fail`. For the `pre_merge`
(PR-time) point, a Hermes-based project uses the shared `doc-review.yml`
workflow running `tools/sdd_doc_lint` — the same deterministic structural gate
the plugin uses — so both platforms gate documents identically in CI.

## Platform info

| Field | Value |
|-------|-------|
| Engine | MCP server (stdio + HTTP per the MCP spec) |
| Distribution | `hermes-server` (PyPI when published) |
| Script entry | `hermes-mcp` → `mcp_server.server:main_sync` |
| Python | `>=3.12` |
| Version | `0.1.0` (independent SemVer; tag namespace `hermes/v*`) |
| Conforms to | framework spec `0.1.0` (declared in `FRAMEWORK_SPEC_VERSION`) |
| License | MIT |
| Repository | <https://github.com/vladm3105/aidoc-flow-framework> |
| Platform changelog | [`CHANGELOG.md`](CHANGELOG.md) |
| Project changelog | [`../../CHANGELOG.md`](../../CHANGELOG.md) |
| Project roadmap | [`../../ROADMAP.md`](../../ROADMAP.md) |
| Tagging policy | [`../../docs/TAGGING.md`](../../docs/TAGGING.md) |

## Relationship to the Claude Code plugin

[`platforms/claude-code-plugin/`](../claude-code-plugin/) is the
**other** independent delivery of the same framework spec — a native
Claude Code plugin (no MCP backend). The two platforms share the
`framework/` specification and **nothing else** (different engines,
no runtime code overlap). Pick Hermes if you want an MCP server an
arbitrary client can integrate with; pick the plugin if you want
Claude Code as the engine. See [`../../docs/PARITY.md`](../../docs/PARITY.md)
for the capability-coverage comparison.

Both platforms pass the shared conformance suite at
[`../../tests/conformance/`](../../tests/conformance/).
