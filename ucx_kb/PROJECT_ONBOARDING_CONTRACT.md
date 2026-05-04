# UCX KB Project Onboarding Contract

## 1. Scope

This contract defines the minimum runtime and validation requirements for running `ucx_kb` inside a downstream project.

Use this contract when enabling indexed knowledge retrieval (RAG + Graph + MCP) in a real project environment.

## 2. Runtime Modes

- File-only mode: no DB containers, no MCP server, file search/read only.
- Indexed mode: PostgreSQL (`pgvector`) + Neo4j + `ucx_kb` MCP server.

This contract covers indexed mode.

## 3. Required Runtime Inputs

### 3.1 Python and import path

- Python: `3.11` or `3.12`.
- Export framework root on `PYTHONPATH`.

```bash
export PYTHONPATH=/opt/data/ucx_framework
```

### 3.2 Environment file

Create `.env` from template in `ucx_kb` root.

```bash
cp /opt/data/ucx_framework/ucx_kb/.env.example /opt/data/ucx_framework/ucx_kb/.env
```

Required variables for indexed mode:

| Variable | Required | Example | Purpose |
|---|---|---|---|
| `DATABASE_URL` | Yes | `postgresql://kb_user:kb_pass@localhost:5433/kb_db` | RAG DB connection |
| `PG_USER` | Yes | `kb_user` | Compose and DB auth |
| `PG_PASS` | Yes | `kb_pass` | Compose and DB auth |
| `PG_DB` | Yes | `kb_db` | Compose DB name |
| `PG_HOST` | Yes | `localhost` | Postgres host |
| `PG_PORT` | Yes | `5433` | Postgres port |
| `NEO4J_URI` | Yes | `bolt://localhost:7688` | Graph connection |
| `NEO4J_USER` | Yes | `neo4j` | Graph auth user |
| `NEO4J_PASS` | Yes | `strong_password` | Graph auth password |
| `NEO4J_DATABASE` | Yes | `neo4j` | Graph database |

### 3.3 Port ownership contract

Before startup, verify that configured ports are not already in use by other stacks.

- PostgreSQL: `PG_PORT` / `PK_DB_POSTGRES_PORT`
- Neo4j HTTP: `PK_DB_NEO4J_HTTP_PORT`
- Neo4j Bolt: `PK_DB_NEO4J_BOLT_PORT`

If ports are already occupied, set non-conflicting values in `.env` and keep all connection values aligned.

## 4. Dependency Contract

`ucx_kb` depends on Python packages with compiled extensions (directly or transitively).

Minimum package set:

- `psycopg`
- `neo4j`
- `mcp`
- `fastapi`
- `uvicorn`
- `python-dotenv`
- `pyyaml`
- `requests`
- `tenacity`
- `ratelimit`

Compatibility requirement:

- Keep NumPy ABI consistent across compiled packages.
- If environment shows ABI errors (`compiled using NumPy 1.x cannot be run in NumPy 2.x`), pin:
  - `numpy<2`
  - reinstall dependent compiled packages in the same environment.

## 5. Database Bring-up Contract

From `ucx_kb` root:

```bash
docker compose -f docker-compose.db.yml --env-file .env up -d
docker compose -f docker-compose.db.yml --env-file .env ps
```

Expected:

- PostgreSQL and Neo4j services are running.
- PostgreSQL schema initialization executes from `db/rag_schema.sql` on first volume creation.

## 6. MCP Runtime Contract

Start MCP server from framework root:

```bash
python -m ucx_kb.mcp.server
```

Required MCP tools contract:

- RAG: `kb_embed`, `kb_embed_text`, `kb_search`, `kb_hybrid_context`, `kb_status`
- Graph: `kb_extract`, `kb_extract_text`, `kb_graph_context`, `kb_graph_search`, `kb_graph_query`, `kb_graph_status`

If process exits on import/startup, treat as contract failure and resolve environment/dependency mismatch before project rollout.

## 7. Project Smoke Validation Contract

Run in this order from framework root:

```bash
PYTHONPATH=/opt/data/ucx_framework python -m pytest -q ucx_kb
PYTHONPATH=/opt/data/ucx_framework python -m ucx_kb.mcp.server
PYTHONPATH=/opt/data/ucx_framework python ucx_kb/scripts/pilot_validate.py
```

Pass criteria:

- Test suite passes (integration tests may be skipped unless explicitly enabled).
- MCP server starts without import/runtime exceptions.
- `pilot_validate.py` writes status report and exits `0`.

Fail criteria:

- DB authentication failures.
- Port conflicts.
- Python dependency import/ABI failures.

## 8. Downstream Project Integration Contract

For each downstream project:

1. Provide project-specific `.env` values (do not reuse unrelated stack credentials).
2. Validate connectivity with project DB credentials before ingestion.
3. Run one ingestion command on project corpus:

```bash
PYTHONPATH=/opt/data/ucx_framework python ucx_kb/orchestrator.py /path/to/project/docs --pattern "*.yaml"
```

4. Validate retrieval:

```bash
PYTHONPATH=/opt/data/ucx_framework python ucx_kb/scripts/pilot_validate.py --out ucx_kb/tmp/pilot_validation.json
```

## 9. Known Framework Gap (Must Fix Before Release Tag)

- `ucx_kb/rag/schema.py` references `get_config()` in `get_db_stats()` but does not define/import it.
- This is a latent runtime defect for call paths using `get_db_stats()`.

Release gate:

- Fix this reference before marking UCX KB framework as release-ready for downstream adoption.
