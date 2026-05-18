# RAG Services for UCX Flow Framework

Dual-service RAG architecture for comprehensive documentation retrieval.

## Optional Usage

These services are optional for projects using this framework.

- Use `framework_rags` when you want a shared, standalone RAG runtime managed by this framework.
- Use your project's built-in RAG/graph stack when it already meets your needs.
- You can choose `framework_rags` instead of built-in RAG if you need a separate runtime, different retrieval behavior, or centralized operations across projects.

## Services

| Service | Port | Purpose |
|---------|------|---------|
| **Haystack** | 1416 | Project documentation (REF, PRD, BRD, SPEC, etc.) |
| **LightRAG** | 9621 | Research & analysis knowledge base |
| **PostgreSQL** | 5432 | Shared database (pgvector) |
| **Neo4j** | 7474/7687 | Graph storage for LightRAG |

## SDD Layers Supported

Haystack indexes all 13 SDD layers:

| Layer | Type | Description |
|-------|------|-------------|
| 0 | REF | Reference documents, initial project documentation |
| 1-12 | BRD→IPLAN | Full SDD workflow artifacts |

## Data Storage

All data is stored in your project's `tools/data/` directory:

```
${PROJECT_ROOT}/
└── tools/
    └── data/
        ├── postgres/        # PostgreSQL database files
        ├── neo4j/
        │   ├── data/        # Neo4j graph data
        │   └── logs/        # Neo4j logs
        ├── haystack/
        │   ├── data/        # Haystack indexes
        │   └── pipelines/   # Serialized pipelines
        ├── lightrag/
        │   ├── data/        # LightRAG data
        │   └── inputs/      # Input documents
        └── backups/         # Backup files
```

## Quick Start

```bash
# 1. Setup environment
make setup
# Edit .env with:
#   - PROJECT_ROOT: Path to your project directory
#   - OPENAI_API_KEY: Your OpenAI API key

# 2. Create data directories
make init-data-dirs

# 3. Build and start services
make rag-build
make rag-up

# 4. Verify services are healthy
make rag-verify

# 5. Index documentation
make rag-index
```

## Prerequisites

- Docker and Docker Compose
- OpenAI API key (required)
- Cohere API key (recommended for reranking)

## Configuration

### Environment Variables (.env)

```bash
# Required - Path to your project root
PROJECT_ROOT=/opt/data/my_project

# Required - API Key
OPENAI_API_KEY=sk-your-key-here

# Optional but recommended
COHERE_API_KEY=your-cohere-key

# Database credentials (defaults provided)
POSTGRES_PASSWORD=ragpass
NEO4J_PASSWORD=neo4jpass
LIGHTRAG_API_KEY=lightragsecretkey
```

### Haystack Configuration

Edit `haystack/config/default.yaml`:

```yaml
embedding:
  model: "text-embedding-3-small"
  dimensions: 1536

splitting:
  split_by: "sentence"
  split_length: 10
  split_overlap: 3

retrieval:
  reranker_top_k: 5
```

### LightRAG Configuration

Edit `lightrag/config/default.env`:

```bash
LLM_MODEL=gpt-4o-mini
CHUNK_SIZE=1200
DEFAULT_QUERY_MODE=hybrid
```

## Usage

### Makefile Commands

```bash
# Lifecycle
make rag-up          # Start all services
make rag-down        # Stop all services
make rag-restart     # Restart services
make rag-status      # Show service status

# Monitoring
make rag-logs        # Tail all logs
make rag-verify      # Health check

# Data
make rag-index       # Index framework docs
make rag-index-ref   # Index only REF docs (Layer 0)
make rag-index-project  # Index project docs from PROJECT_ROOT
make rag-backup      # Backup all data
make rag-restore     # Restore from backup

# Setup
make init-data-dirs  # Create tools/data directories

# Interactive
make haystack-shell  # Shell into Haystack
make lightrag-shell  # Shell into LightRAG
make postgres-shell  # PostgreSQL CLI
make neo4j-browser   # Show Neo4j URL
```

### Query Examples

**Haystack (factual queries):**
```bash
curl -X POST http://localhost:1416/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the validation rules for BRD documents?"}'
```

**LightRAG (relational queries):**
```bash
curl -X POST http://localhost:9621/query \
  -H "X-API-Key: lightragsecretkey" \
  -H "Content-Type: application/json" \
  -d '{"query": "What patterns connect EARS requirements to BDD scenarios?", "mode": "hybrid"}'
```

### Metadata Filtering (Haystack)

Filter queries by document attributes:

```python
# Filter by document type
filters = {"doc_type": {"$eq": "PRD"}}

# Filter by SDD layer
filters = {"layer": {"$gte": 5}}  # ADR and above

# Combined filters
filters = {
    "$and": [
        {"doc_type": {"$in": ["PRD", "BRD"]}},
        {"layer": {"$lte": 3}}
    ]
}
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              Claude Code / VS Code / Cursor                   │
│                      (MCP Client)                            │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┴───────────────┐
          ▼                               ▼
┌─────────────────────┐       ┌───────────────────────────┐
│  Haystack (1416)    │       │    LightRAG (9621)        │
│  - Hybrid Search    │       │    - Entity Extraction    │
│  - BM25 + Vector    │       │    - Knowledge Graph      │
│  - Cohere Reranker  │       │    - Dual-Level Retrieval │
└─────────┬───────────┘       └─────────────┬─────────────┘
          │                                 │
          └─────────────┬───────────────────┘
                        ▼
          ┌─────────────────────────┐
          │  PostgreSQL + pgvector  │
          │  (Shared, Port 5432)    │
          └─────────────────────────┘
                        │
                        ▼
          ┌─────────────────────────┐
          │  Neo4j (7474/7687)      │
          │  (LightRAG Graph)       │
          └─────────────────────────┘
                        │
                        ▼
          ┌─────────────────────────┐
          │  ${PROJECT_ROOT}/       │
          │  tools/data/            │
          │  (Persistent Storage)   │
          └─────────────────────────┘
```

## MCP Integration

Configuration examples for all supported tools are in `mcp/`:

| File | Tool |
|------|------|
| `claude_code_config.json.example` | Claude Code CLI |
| `claude_desktop_config.json.example` | Claude Desktop |
| `vscode_settings.json.example` | VS Code |
| `cursor_config.json.example` | Cursor |
| `windsurf_config.json.example` | Windsurf |
| `zed_settings.json.example` | Zed Editor |

Generate configs for your tool:

```bash
python rag_tools/mcp_config_generator.py --tool claude-code > ~/.claude/mcp.json
python rag_tools/mcp_config_generator.py --tool vscode > .vscode/settings.json
python rag_tools/mcp_config_generator.py --show-paths  # Show all config locations
```

See `mcp/README.md` for detailed setup instructions.

## Web UIs

- **Neo4j Browser**: http://localhost:7474
- **LightRAG WebUI**: http://localhost:9621

## Backup & Restore

```bash
# Create backup (stored in ${PROJECT_ROOT}/tools/data/backups/)
make rag-backup

# Restore from backup
make rag-restore
# Follow prompts
```

## Troubleshooting

### Services not starting

```bash
# Check logs
make rag-logs

# Verify Docker resources
docker system df
```

### PROJECT_ROOT not set

```bash
# Check your .env file
grep PROJECT_ROOT .env

# Verify directory exists
ls -la ${PROJECT_ROOT}/tools/data/
```

### Database connection errors

```bash
# Check PostgreSQL
make postgres-shell
\dt haystack_docs.*
\dt lightrag.*
```

### LightRAG indexing hangs

LightRAG may hang after extended processing. Mitigations:
- Index in batches of 30-50 documents
- Monitor with `curl http://localhost:9621/health`
- Restart if hung: `docker-compose restart lightrag`

### Out of memory

Increase Docker memory allocation or reduce batch sizes.

## Using with Multiple Projects

Each project using this framework should:

1. Set `PROJECT_ROOT` in `.env` to its own directory
2. Run `make init-data-dirs` to create its data directories
3. Data will be isolated in `${PROJECT_ROOT}/tools/data/`

This allows multiple projects to share the framework code while maintaining separate RAG indexes.

## Documentation

| Document | Description |
|----------|-------------|
| [RAG_OVERVIEW.md](docs/RAG_OVERVIEW.md) | Why RAG, architecture, use cases |
| [AI_AGENT_RAG_GUIDE.md](docs/AI_AGENT_RAG_GUIDE.md) | Instructions for AI agents |
| [AI_AGENT_RAG_QUICK_REF.md](docs/AI_AGENT_RAG_QUICK_REF.md) | Quick reference card |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Technical specifications |
| [mcp/README.md](mcp/README.md) | MCP configuration guide |

## License

Part of the UCX Flow Framework.
