# Migration from mcp_ucx to ucx_hermes

> **Source**: `mcp_ucx/` (v1.22.0) — DEPRECATED, frozen  
> **Destination**: `ucx_hermes/` (v2.0.0+) — Active, canonical  
> **Date**: 2026-05-02  
> **Impact**: All new development, CI/CD, and MCP configuration  

---

## Summary

The `mcp_ucx/` directory is **deprecated** and **frozen at v1.22.0**. All active MCP code, tests, docs, templates, prompts, and skills now live in `ucx_hermes/`. The move was driven by a hardening effort to separate **deterministic validation** (safe, no AI delegation) from **interactive reasoning** (human-gated) in the document lifecycle.

| Concern | mcp_ucx (Deprecated) | ucx_hermes (Active) |
|---------|---------------------|---------------------|
| AI executor delegation | Silent auto-rewrite of documents via stateless CLI/API agents | Removed from all document-critical paths; returns structured reports/prompts only |
| Validation safety | Conditional AI fix path inside `sdd_validate` | 100% deterministic; fix path returns report text, does not execute |
| Review safety | Spawns AI executor for `sdd_review`, `sdd_create_build`, `sdd_remediate` | Returns assembled prompts/fix instructions only; no unsupervised execution |
| Hermes integration | None | Bridge skill + integration doc + explicit safety contract |
| Template server references | `mcp_ucx` | `ucx_hermes` |

---

## Path Mapping (Old → New)

| Old (`mcp_ucx/`) | New (`ucx_hermes/`) | Notes |
|------------------|---------------------|-------|
| `mcp_ucx/src/mcp_server/` | `ucx_hermes/src/mcp_server/` | All runtime code migrated |
| `mcp_ucx/tests/` | `ucx_hermes/tests/` | Test suite copied; new tests added for patch verification |
| `mcp_ucx/docs/` | `ucx_hermes/docs/` | Canonical documentation now maintained here |
| `mcp_ucx/templates/` | `ucx_hermes/templates/` | YAML templates updated to reference `ucx_hermes` |
| `mcp_ucx/skills/` | `ucx_hermes/skills/` | Personas + mappings |
| `mcp_ucx/prompts/` | `ucx_hermes/prompts/` | Creation, review, remediation prompts |
| `mcp_ucx/examples/` | `ucx_hermes/examples/` | Example boards |
| `mcp_ucx/pyproject.toml` | `ucx_hermes/pyproject.toml` | Updated name and paths |

---

## Configuration Changes

### MCP Configuration (`.mcp.json`)

> **Action required**: Update your MCP server config to point to `ucx_hermes`.

**Before (deprecated)**:
```json
{
  "mcpServers": {
    "sdd-lifecycle": {
      "command": "/opt/data/ucx_framework/.venv/bin/python",
      "args": ["-m", "mcp_server.server"],
      "cwd": "/opt/data/ucx_framework/mcp_ucx/src"
    }
  }
}
```

**After (current)**:
```json
{
  "mcpServers": {
    "sdd-lifecycle": {
      "command": "/opt/data/ucx_framework/.venv/bin/python",
      "args": ["-m", "mcp_server.server"],
      "cwd": "/opt/data/ucx_framework/ucx_hermes/src"
    }
  }
}
```

### Pre-commit Config

The `.pre-commit-config.yaml` at the repo root already has empty `repos: []`. All validation runs through MCP tools (`sdd_validate`, `sdd_score_validate`) invoked via UCX Hermes.

No action needed unless you had custom hooks pointing to `mcp_ucx` paths.

### Python Package

The `pyproject.toml` in `ucx_hermes/` still declares the same package name `mcp-ucx-server` for backward compatibility, but the source root is now `ucx_hermes/`.

```bash
# Install from ucx_hermes
cd /opt/data/ucx_framework/ucx_hermes
pip install -e .
```

---

## What Was Patched

### AI Executor Delegation Removed

Four tools had AI executor delegation that could silently rewrite documents:

| Tool | Patch | Behavior Now |
|------|-------|-------------|
| `sdd_validate` (with `--fix` or `executor` param) | Removed executor call from fix path | Returns `fix_report` text only; human or Hermes must apply |
| `sdd_create_build` | Removed executor content generation | Returns creation prompt + template metadata; human or Hermes writes |
| `sdd_review` | Removed executor multi-persona execution | Returns assembled `prompt_text` for Hermes/human to execute |
| `sdd_remediate` | Removed executor auto-application (all 3 paths) | Returns deterministic findings + fix instructions; no auto-write |

See `docs/HERMES_INTEGRATION.md` for the exact lines changed and safety rationale.

---

## Verification Checklist

After switching to `ucx_hermes/`:

- [ ] `.mcp.json` points to `ucx_hermes/src`
- [ ] `sdd_preflight --project <path>` runs without `ProjectSkillsNotFound`
- [ ] `sdd_validate` on a document returns only deterministic findings (no AI execution)
- [ ] `sdd_review` returns assembled prompt text (does not execute)
- [ ] `sdd_remediate` returns fix report text (does not modify source files)
- [ ] Hermes bridge skill installed: `~/.hermes/skills/ucx-sdd-bridge/SKILL.md` exists

---

## Rollback

If you need to revert to `mcp_ucx/`:

1. Change `.mcp.json` back to `mcp_ucx/src`
2. Reinstall `pip install -e /opt/data/ucx_framework/mcp_ucx`
3. Be aware: `mcp_ucx` allows unsupervised AI document rewrites via executor delegation

No data migration is needed between the two directories — they share the same document format and protocol version.

---

## Support

- **Active issues**: File against `ucx_hermes/`
- **Historical reference**: `mcp_ucx/` is frozen; no new issues accepted
- **Migration questions**: See `docs/HERMES_INTEGRATION.md` and bridge skill
