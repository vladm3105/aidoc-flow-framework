# Project Knowledge Base Setup Guide

## 1) Scope

This guide configures and runs the standalone Project Knowledge Base in:

- `/opt/data/docs_flow_framework/project_knowledge`

Components covered:

- RAG storage and retrieval (PostgreSQL + pgvector)
- Graph extraction and queries (Neo4j)
- MCP server (`project_knowledge.mcp.server`)
- Ingestion, backfill, and pilot validation scripts

## 2) Prerequisites

Required tools:

- Docker Engine
- Docker Compose (v2)
- Python 3.11+

Recommended checks:

```bash
docker --version
docker compose version
python --version
```

## 3) Environment Configuration

From repository root:

```bash
cd /opt/data/docs_flow_framework/project_knowledge
cp .env.example .env
```

Edit `.env` as needed.

### Required Variables

| Variable | Purpose | Default |
|---|---|---|
| `PG_USER` | PostgreSQL user | `lightrag` |
| `PG_PASS` | PostgreSQL password | `lightrag` |
| `PG_DB` | PostgreSQL database | `lightrag` |
| `PG_HOST` | PostgreSQL host | `localhost` |
| `PG_PORT` | PostgreSQL host port | `5433` |
| `DATABASE_URL` | Full PostgreSQL URL | `postgresql://lightrag:lightrag@localhost:5433/lightrag` |
| `NEO4J_URI` | Neo4j Bolt URI | `bolt://localhost:7688` |
| `NEO4J_USER` | Neo4j user | `neo4j` |
| `NEO4J_PASS` | Neo4j password | `neo4jpass` |
| `NEO4J_DATABASE` | Neo4j database | `neo4j` |

## 4) Start Databases

```bash
cd /opt/data/docs_flow_framework/project_knowledge
docker compose -f docker-compose.db.yml --env-file .env up -d
```

Check status:

```bash
docker compose -f docker-compose.db.yml --env-file .env ps
```

Stop databases:

```bash
docker compose -f docker-compose.db.yml --env-file .env down
```

## 5) Schema Assets

Schema files used by this package:

- `db/rag_schema.sql`
- `db/neo4j_schema.cypher`

PostgreSQL schema is initialized automatically on first container startup via `docker-entrypoint-initdb.d`.

For Neo4j schema initialization from Python runtime, use graph schema utilities in:

- `project_knowledge/graph/schema.py`

## 6) Python Runtime Setup

Run from framework root:

```bash
cd /opt/data/docs_flow_framework
export PYTHONPATH=/opt/data/docs_flow_framework
```

Optional dependency install (if needed in your environment):

```bash
pip install -U psycopg neo4j fastapi uvicorn python-dotenv pyyaml requests tenacity ratelimit mcp
```

## 7) Start MCP Server

```bash
cd /opt/data/docs_flow_framework
python -m project_knowledge.mcp.server
```

Exposed tool contracts:

- `kb_embed`, `kb_embed_text`, `kb_search`, `kb_hybrid_context`, `kb_status`
- `kb_extract`, `kb_extract_text`, `kb_graph_context`, `kb_graph_search`, `kb_graph_query`, `kb_graph_status`

## 8) Ingestion and Backfill

### Ingest one folder

```bash
cd /opt/data/docs_flow_framework
python project_knowledge/orchestrator.py /path/to/docs --pattern "*.yaml"
```

### Backfill legacy corpus

Dry run:

```bash
python project_knowledge/scripts/backfill_legacy.py --source /path/to/legacy --dry-run
```

Execute:

```bash
python project_knowledge/scripts/backfill_legacy.py --source /path/to/legacy --pattern "*.yaml"
```

## 9) Validation and Health

Pilot validation report:

```bash
cd /opt/data/docs_flow_framework
python project_knowledge/scripts/pilot_validate.py
```

Tooling checks:

```bash
python project_knowledge/rag_tools/health_monitor.py -v
python project_knowledge/rag_tools/query_router.py "what requirements exist" --analyze-only
python project_knowledge/rag_tools/batch_indexer.py --source project_knowledge --dry-run --service both
```

## 10) Failure Modes

| Symptom | Likely Cause | Action |
|---|---|---|
| `connection refused` to PostgreSQL | DB container not running or port conflict | Check `docker compose ... ps` and `PG_PORT` |
| Neo4j auth failure | `NEO4J_PASS` mismatch | Align `.env` with running container credentials |
| `ModuleNotFoundError: project_knowledge` | `PYTHONPATH` not set to framework root | `export PYTHONPATH=/opt/data/docs_flow_framework` |
| RAG schema missing | PostgreSQL initialized without schema mount | Recreate container volume or run schema init manually |
| No graph context results | Graph has no committed entities | Run extraction via orchestrator/backfill |

## 11) Minimal Bring-Up Checklist

- [ ] Copy `.env.example` to `.env`
- [ ] Start `docker-compose.db.yml`
- [ ] Export `PYTHONPATH`
- [ ] Start `project_knowledge.mcp.server`
- [ ] Run folder ingestion
- [ ] Run `pilot_validate.py`
