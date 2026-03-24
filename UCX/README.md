# UCX v2 — Unified Context Framework

**Version**: 2.0.0  
**Interface**: MCP (Model Context Protocol) — primary  
**Architecture**: MCP-first, agentic document lifecycle

## Overview

UCX v2 is a complete rewrite of the UCX framework. v1 was CLI-first; v2 is **MCP-first**. There is no `ucx` command-line tool in v2. Agents interact with UCX through MCP tool calls.

## Architecture

```
Agent (Claude, GPT-4o, etc.)
    │
    ▼  MCP tool calls
UCX MCP Server (FastMCP)
    │
    ├── brd_*  tools  ──►  ucx/validators/layers/brd.py
    ├── prd_*  tools  ──►  ucx/validators/layers/prd.py
    ├── ears_* tools  ──►  ucx/validators/layers/ears.py
    ├── adr_*  tools  ──►  ucx/validators/layers/adr.py
    ├── sys_*  tools  ──►  ucx/validators/layers/sys.py
    ├── req_*  tools  ──►  ucx/validators/layers/req.py
    └── ctr_*  tools  ──►  ucx/validators/layers/ctr.py
```

## Starting the MCP Server

```bash
ucx-mcp
```

Or in a Claude Desktop / agent configuration:

```json
{
  "mcpServers": {
    "ucx": {
      "command": "ucx-mcp"
    }
  }
}
```

## Tool Namespaces

| Prefix | Layer | Document Type |
| --- | --- | --- |
| `brd_*` | Layer 1 | Business Requirements Document |
| `prd_*` | Layer 2 | Product Requirements Document |
| `ears_*` | Layer 3 | EARS Requirements |
| `adr_*` | Layer 5 | Architecture Decision Records |
| `sys_*` | Layer 6 | System Requirements |
| `req_*` | Layer 7 | Atomic Requirements |
| `ctr_*` | Layer 8 | Data Contracts |

Each layer exposes: `{layer}_validate`, `{layer}_review`, `{layer}_remediate`, `{layer}_status`.

## Agent Workflow Example

```
Agent calls: brd_validate(brd_path="docs/01_BRD/BRD-01.md")
  → findings list, next_step: "brd_review"

Agent calls: brd_review(brd_path="docs/01_BRD/BRD-01.md")
  → review_report_path, next_step: "brd_remediate"

Agent calls: brd_remediate(brd_path="...", review_report_path="...")
  → remediated document path, next_step: "brd_validate"
```

## Migration from v1

See `UCX_v1_archive/` for the v1 source. The CLI commands are gone; use MCP tool calls instead.

| v1 CLI | v2 MCP Tool |
| --- | --- |
| `ucx validate brd <path>` | `brd_validate(brd_path=<path>)` |
| `ucx review brd <path>` | `brd_review(brd_path=<path>)` |
| `ucx remediate <path>` | `brd_remediate(brd_path=<path>, review_report_path=<report>)` |

## Development

```bash
pip install -e ".[dev]"
pytest
```

## Plans

See `docs/plans/` for implementation plans. v2 plans start at PLAN-001.

## Reference

- [ROADMAP](docs/ROADMAP.md)
- [v1 Archive](../UCX_v1_archive/) — reference for porting logic
