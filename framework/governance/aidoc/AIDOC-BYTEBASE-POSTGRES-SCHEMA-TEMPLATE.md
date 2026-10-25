# `.aidoc/` Blueprint: Bytebase Schema Engine & PostgreSQL 18 Database Standard

## Document Control

| Field | Value |
|---|---|
| Version | 1.0 |
| Status | Approved |
| Last Updated | 2026-10-10 |
| Author | Framework Maintainer |
| Framework Version | 0.96.14 |
| Authority | [RECOMMENDED_PLATFORM_STACK.md](../RECOMMENDED_PLATFORM_STACK.md) & [SPEC_WORKFLOW_STANDARD.md](../../layers/06_SPEC/SPEC_WORKFLOW_STANDARD.md) |

Operational blueprint for specifying relational database schemas, monotonic UUIDv7 keys,
vector embeddings, and lossless audit ledgers managed via **Bytebase Schema Engine** and deployed onto **PostgreSQL 18**.

---

## 1. PostgreSQL 18 Architectural Baseline

1. **Native UUIDv7 Monotonic Primary Keys:**
   PostgreSQL 18 includes native UUIDv7 generation. Eliminates extensions and provides time-ordered, index-friendly primary keys *(for PostgreSQL 15–17 LTS environments, install `pg_uuidv7` via `CREATE EXTENSION IF NOT EXISTS "pg_uuidv7"; DEFAULT uuid_generate_v7()` or generate UUIDv7 at the application layer)*:
   ```sql
   id UUID PRIMARY KEY DEFAULT gen_random_uuid_v7()
   ```
2. **`pgvector` Indexing Standards:**
   For high-dimensional embeddings (e.g., 1536d or 3072d), use HNSW indexes for low-latency similarity queries:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   CREATE INDEX ON document_embeddings USING hnsw (embedding vector_cosine_ops)
   WITH (m = 16, ef_construction = 64);
   ```
3. **Lossless Wire Ledger (`xp.ledger`):**
   Partitioned monthly by timestamp or UUIDv7, storing exact wire `bytea` payloads immutably:
   ```sql
   CREATE SCHEMA IF NOT EXISTS xp;

   CREATE TABLE xp.ledger (
       msg_id UUID NOT NULL,
       ts TIMESTAMPTZ NOT NULL,
       project VARCHAR(64) NOT NULL,
       topic VARCHAR(128) NOT NULL,
       wire_bytes BYTEA NOT NULL,
       wire_hash CHAR(64) NOT NULL,
       PRIMARY KEY (msg_id, ts)
   ) PARTITION BY RANGE (ts);
   ```

---

## 2. Bytebase Model Context Protocol Integration

Autonomous coding agents (Tier 3 execution) MUST interact with database schemas strictly through Bytebase Model Context Protocol endpoints rather than executing raw, ungoverned DDL against database instances.

### Agent Tool Configuration
In the agent's tool settings:
```json
{
  "mcpServers": {
    "bytebase": {
      "command": "bytebase-tool",
      "args": ["--endpoint", "http://bytebase:5678", "--token-env", "BYTEBASE_SERVICE_TOKEN"]
    }
  }
}
```

### Agent Schema Workflow Lifecycle
1. **Schema Inspection:** Coding agent invokes Bytebase tool `get_schema(database="db_proj_a")` to inspect live tables, constraints, and column types.
2. **Migration Script Generation:** Agent generates an idempotent, versioned SQL migration file following the naming convention:
   ```text
   migrations/
   └── V20261010120000__add_user_sessions_table.sql
   ```
3. **Pre-Commit DDL Validation:** Agent invokes Bytebase tool `lint_ddl(sql=...)` to verify:
   - No table locks or long-running exclusive locks.
   - All foreign keys indexed.
   - Backward compatibility for online zero-downtime rolling upgrades.
4. **GitOps Submission:** The migration script is committed to the feature branch and submitted via Pull Request. Bytebase automates the migration pipeline upon PR merge.

---

## 3. Database Migration Script Template

```sql
-- Migration: V20261010140000__create_agent_tasks_table.sql
-- Description: Create agent tasks tracking table with native UUIDv7 and pgvector

CREATE TABLE IF NOT EXISTS agent_tasks (
    task_id UUID PRIMARY KEY DEFAULT gen_random_uuid_v7(),
    project_id VARCHAR(64) NOT NULL,
    run_id VARCHAR(128) NOT NULL,
    task_state VARCHAR(32) NOT NULL DEFAULT 'PENDING',
    payload_hash CHAR(64) NOT NULL,
    artifact_uri VARCHAR(512) NOT NULL,
    task_embedding vector(1536),
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);

-- Monotonic index on creation timestamp for efficient pagination
CREATE INDEX IF NOT EXISTS idx_agent_tasks_created_at ON agent_tasks (created_at DESC);

-- Fast exact-match lookup on run_id
CREATE INDEX IF NOT EXISTS idx_agent_tasks_run_id ON agent_tasks (run_id);

-- HNSW vector similarity index for semantic task search
CREATE INDEX IF NOT EXISTS idx_agent_tasks_embedding ON agent_tasks 
USING hnsw (task_embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```
