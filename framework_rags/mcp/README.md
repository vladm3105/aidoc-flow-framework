# MCP Server Configuration

Configuration examples for connecting RAG services to various AI coding tools.

## Services

| Server | Port | Transport | Description |
|--------|------|-----------|-------------|
| `project-docs` | 1416 | SSE/stdio | Haystack - Project documentation (REF→TASKS) |
| `research-kb` | 9621 | SSE/stdio | LightRAG - Research & cross-document analysis |

## Tool Configuration

### Claude Code (CLI)

**Location**: `~/.claude/mcp.json` or `~/.config/claude-code/mcp.json`

```bash
cp claude_code_config.json.example ~/.claude/mcp.json
```

Or add to existing config:
```json
{
  "mcpServers": {
    "project-docs": {
      "type": "sse",
      "url": "http://localhost:1416/sse"
    },
    "research-kb": {
      "type": "sse",
      "url": "http://localhost:9621/sse"
    }
  }
}
```

### Claude Desktop

**Location**:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

```bash
cp claude_desktop_config.json.example ~/.config/Claude/claude_desktop_config.json
```

### VS Code (Claude Extension)

**Location**: `.vscode/settings.json` or User Settings

```bash
cp vscode_settings.json.example .vscode/settings.json
```

Or add to User Settings (Ctrl+Shift+P → "Preferences: Open User Settings (JSON)"):
```json
{
  "claude.mcpServers": {
    "project-docs": {
      "url": "http://localhost:1416/sse",
      "transport": "sse"
    },
    "research-kb": {
      "url": "http://localhost:9621/sse",
      "transport": "sse"
    }
  }
}
```

### Cursor

**Location**: Cursor Settings → Features → MCP Servers

```bash
cp cursor_config.json.example ~/.cursor/mcp.json
```

### Windsurf (Codeium)

**Location**: `~/.windsurf/mcp.json`

```bash
cp windsurf_config.json.example ~/.windsurf/mcp.json
```

### Zed

**Location**: `~/.config/zed/settings.json`

```bash
# Merge with existing settings
cat zed_settings.json.example
```

## Prerequisites

Before configuring MCP clients, ensure RAG services are running:

```bash
cd /opt/data/ucx_framework/framework_rags
make rag-up
make rag-verify
```

## Available Tools

### project-docs (Haystack)

| Tool | Description |
|------|-------------|
| `search_docs` | Search project documentation by query |
| `get_document` | Retrieve specific document by ID |
| `list_documents` | List available documents with filters |
| `query_requirements` | Query requirements with traceability |

**Filters supported**:
- `doc_type`: REF, BRD, PRD, EARS, BDD, ADR, SYS, REQ, CTR, SPEC, TSPEC, TASKS, IPLAN
- `layer`: 0-12 (REF=0, BRD=1, ..., IPLAN=12)
- `project_name`: Filter by project

### research-kb (LightRAG)

| Tool | Description |
|------|-------------|
| `query` | Query knowledge graph with relationship discovery |
| `search_entities` | Search for specific entities |
| `get_relationships` | Get relationships between entities |
| `analyze_patterns` | Identify patterns across documents |

**Query modes**:
- `local`: Entity-focused retrieval
- `global`: Theme-focused retrieval
- `hybrid`: Combined (recommended)

## Troubleshooting

### Connection Refused

Ensure services are running:
```bash
make rag-status
curl http://localhost:1416/health
curl http://localhost:9621/health
```

### SSE Not Working

Some tools require SSE endpoints. Verify:
```bash
curl -N http://localhost:1416/sse
```

### Environment Variables

For stdio transport (Claude Desktop), ensure environment variables are set:
```bash
export OPENAI_API_KEY="sk-..."
```

Or use the `.env` file in the framework_rags directory.

## Generating Configs

Use the config generator for custom setups:

```bash
python rag_tools/mcp_config_generator.py --tool claude-code > ~/.claude/mcp.json
python rag_tools/mcp_config_generator.py --tool vscode > .vscode/settings.json
python rag_tools/mcp_config_generator.py --tool cursor > ~/.cursor/mcp.json
```
