# hermes-server — Hermes MCP server platform

The **MCP-server** delivery of the AI Doc Flow framework. Hermes hosts the
SDD engine as a Model Context Protocol server: any MCP-compatible client
(Claude Code, custom integrations) connects over stdio or HTTP and invokes
the `sdd_*` tools to validate, generate, score, and remediate documents.
No native Claude Code integration; clients talk MCP.

## What's inside

| Component | Count | Path |
|-----------|------:|------|
| Source modules | 20 | `src/mcp_server/` — `cleanup`, `cli`, `consistency`, `core`, `creation`, `executor`, `link_validation`, `models`, `preflight`, `prescreening`, `prompts`, `remediation`, `reporting`, `review`, `scan`, `scoring`, `skills`, `team_emulator`, `utils`, `validation` |
| Tests (pytest) | 447 | `tests/` — unit, integration, contract |
| MCP prompts | 46 | `prompts/` + `prompts/templates/` |
| Personas | 16 | `skills/personas/` |
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

Hermes exposes **platform-wide MCP tools** for the SDD workflow (27
registered tools, `TOOLS` in `src/mcp_server/tool_registry.py`):

| Tool | Purpose |
|------|---------|
| `sdd_init` | Scaffold `<project>/UCX/` assets (personas, templates, schemas, prompts) |
| `sdd_set_project` / `sdd_get_project` | Set / show the session default project |
| `sdd_env_show` | Show project `.env` keys without exposing values |
| `sdd_preflight` | Runtime / environment readiness check before create/review/remediate |
| `sdd_create_build` / `sdd_create` | Assemble creation prompt / write the final artifact |
| `sdd_validate` | Structural validation against the layer schema/template |
| `sdd_validate_chg` | CHG (Change Management) governance validation |
| `sdd_validate_links` | Markdown cross-document link validation |
| `sdd_consistency` | Artifact lineage / stage-consistency check |
| `sdd_score_show` / `sdd_score_validate` / `sdd_score_compare` | Compute / gate / diff quality score |
| `sdd_review` | Assemble the multi-persona review prompt |
| `sdd_remediate` | Run remediation from review findings (source-protected derived copies) |
| `sdd_run_lifecycle` | Run multiple lifecycle stages in sequence |
| `sdd_next_action` | Recommend the next lifecycle stage for a document folder |
| `sdd_prescreen` | Identify high-priority remediation candidates |
| `sdd_scan` | Extract finding-category counts from a report |
| `sdd_clean` | Remove obsolete stage artifacts (keep latest per stage) |
| `sdd_personas_show` / `sdd_personas_set` / `sdd_personas_diff` | Show / update / diff persona assignments |
| `sdd_list_executors` / `sdd_register_executor` | List / register API executors |
| `sdd_team_plan` | Run the AI-employee planning council (supervisor-approved artifacts) |

The MCP client picks the tool; Hermes operates on any of the 8 SDD
layers (BRD, PRD, EARS, BDD, ADR, SPEC, TDD, IPLAN) generically.

## Framework spec conformance

Hermes consumes the engine-agnostic SDD specification at
`../../framework/` (layer templates, registry, governance). Two
version declarations:

```sh
$ cat VERSION
0.9.0

$ cat FRAMEWORK_SPEC_VERSION
0.36.2
```

Hermes declares conformance to framework spec `0.36.2`; the
framework's own version is at `../../framework/VERSION`. The Phase 4
conformance suite enforces this declaration matches.

### Review / remediation / gate triggers

Hermes binds the spec's review→remediation→gate trigger points
(`../../framework/governance/REVIEW_REMEDIATION_FLOW.md`) to its existing
runtime: server-side `validation/` + scoring covers `on_author` (on-demand
validate/score) and `pre_promotion` (the readiness gate before the next layer);
the `UCRem_*` remediation prompts cover `on_gate_fail`. For the `pre_merge`
(PR-time) point, a Hermes-based project uses the shared `doc-review.yml`
workflow running the deterministic `sdd_doc_lint` — the same structural gate the
plugin uses — so both platforms gate documents identically in CI. A
byte-identical copy of the linter is vendored at `sdd_doc_lint/` (kept in sync
with the canonical `tools/sdd_doc_lint/` by `sync-vendored.sh`, enforced by a
conformance guard); run it from the platform root with
`PYTHONPATH=. python -m sdd_doc_lint <docs-path>`.

## Platform info

| Field | Value |
|-------|-------|
| Engine | MCP server (stdio + HTTP per the MCP spec) |
| Distribution | `hermes-server` (PyPI when published) |
| Script entry | `hermes-mcp` → `mcp_server.server:main_sync` |
| Python | `>=3.12` |
| Version | `hermes/v0.9.0` (independent SemVer; tag namespace `hermes/v*`) |
| Conforms to | framework spec `0.36.2` (declared in `FRAMEWORK_SPEC_VERSION`) |
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
