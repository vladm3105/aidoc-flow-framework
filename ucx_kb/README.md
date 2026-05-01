# UCX Knowledge

Independent knowledge tools package (RAG + Graph + MCP) shared across projects.

> Deprecation note: `ucx_kb` is the canonical package and directory name.
> The legacy alias `ucx_knowledge` is temporary for backward compatibility.
> Use `ucx_kb` for all new imports and commands.

See full setup instructions in `SETUP.md`.

## Operating Modes

### 1) File-only mode

- Keep project knowledge as files only.
- Use direct file read/search workflows.
- No database or MCP startup required.

### 2) Indexed mode (RAG + Graph + MCP)

- Run PostgreSQL (`pgvector`) and Neo4j.
- Ingest files for semantic retrieval + graph context.
- Use MCP `kb_*` tools for knowledge queries.

## Modules

- `rag/` — vector embedding and retrieval
- `graph/` — entity extraction and relationship graph
- `mcp/` — MCP server/tool interfaces
- `tests/` — module and integration tests

## Migration Source

Initial implementation is extracted from:

- `/opt/data/tradegent_swarm/tradegent/rag`
- `/opt/data/tradegent_swarm/tradegent/graph`

Tradegent remains a client via compatibility adapters during migration.

## Databases (Docker)

RAG and Graph runtime require PostgreSQL (`pgvector`) and Neo4j.

```bash
cd /opt/data/ucx_framework/ucx_kb
cp .env.example .env
docker compose -f docker-compose.db.yml --env-file .env up -d
```

Connection defaults:

- PostgreSQL: `localhost:5433`
- Neo4j HTTP: `localhost:7475`
- Neo4j Bolt: `localhost:7688`

Schema assets are in:

- `db/rag_schema.sql`
- `db/neo4j_schema.cypher`
