# project_knowledge DB assets

- `rag_schema.sql` initializes PostgreSQL schema and pgvector tables for RAG.
- `neo4j_schema.cypher` initializes Neo4j constraints/indexes for graph layer.

Usage:

```bash
cd /opt/data/docs_flow_framework/project_knowledge
cp .env.example .env
docker compose -f docker-compose.db.yml --env-file .env up -d
```
