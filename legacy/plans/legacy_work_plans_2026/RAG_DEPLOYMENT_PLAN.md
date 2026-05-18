# RAG Deployment Implementation Plan

## Overview

Deploy dual-service RAG architecture (Haystack + LightRAG) as part of the ucx_framework for comprehensive documentation retrieval.

**Target Directory**: `/opt/data/ucx_framework/framework_rags/`

---

## Directory Structure

```
framework_rags/
├── docker-compose.yml              # Master orchestration (all services)
├── .env.example                    # Environment template
├── Makefile                        # RAG-specific targets
├── README.md                       # Setup and usage guide
├── .gitignore
│
├── scripts/                        # Shared infrastructure scripts
│   ├── init_db.sql                 # PostgreSQL schema initialization
│   ├── backup.sh                   # Backup all services
│   └── restore.sh                  # Restore from backup
│
├── haystack/                       # Haystack RAG (project docs)
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── config/
│   │   ├── default.yaml            # Default pipeline config
│   │   └── pipelines/              # Serialized pipeline YAMLs
│   │       ├── indexing.yaml
│   │       └── query.yaml
│   ├── src/
│   │   └── haystack_rag/
│   │       ├── __init__.py
│   │       ├── config.py           # Configuration loader
│   │       ├── pipelines.py        # Pipeline builders
│   │       ├── server.py           # Hayhooks wrapper/entry point
│   │       └── components/         # Custom components
│   │           ├── __init__.py
│   │           ├── metadata_enricher.py
│   │           ├── document_cleaner.py
│   │           └── vision_captioner.py
│   ├── scripts/
│   │   ├── setup.sh                # Installation
│   │   ├── index_docs.py           # Bulk indexing
│   │   ├── verify.py               # Health check
│   │   ├── export_pipeline.py      # Pipeline serialization
│   │   └── evaluate.py             # RAGAS evaluation
│   └── tests/
│       ├── conftest.py
│       ├── test_pipelines.py
│       └── test_components.py
│
├── lightrag/                       # LightRAG (research KB)
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── config/
│   │   ├── default.env             # LightRAG env config
│   │   └── entity_types.py         # Custom entity definitions
│   ├── src/
│   │   └── lightrag_service/
│   │       ├── __init__.py
│   │       ├── config.py           # Config loader
│   │       ├── custom_prompts.py   # Entity extraction prompts
│   │       └── health.py           # Health monitoring
│   ├── scripts/
│   │   ├── setup.sh                # Installation (includes daniel-lightrag-mcp)
│   │   ├── index_docs.py           # Bulk indexing (30-50 doc batches)
│   │   ├── verify.py               # Health check
│   │   └── graph_stats.py          # Neo4j statistics
│   └── tests/
│       ├── conftest.py
│       ├── test_extraction.py
│       └── test_queries.py
│
├── rag_tools/                      # Shared utilities
│   ├── __init__.py
│   ├── doc_scanner.py              # Scan framework docs
│   ├── batch_indexer.py            # Unified batch indexing (respects limits)
│   ├── query_router.py             # Route queries to correct RAG
│   ├── health_monitor.py           # Monitor all services
│   └── mcp_config_generator.py     # Generate MCP configs
│
├── mcp/                            # MCP server configurations
│   ├── claude_desktop_config.json.example
│   └── cursor_config.json.example
│
├── docs/                           # Documentation
│   └── ARCHITECTURE.md             # Detailed architecture reference
│
└── tmp/                            # Temporary files (gitignored)
```

---

## Implementation Tasks

### Task 1: Create Directory Structure and Root Files

**Files to create:**
- `framework_rags/docker-compose.yml`
- `framework_rags/.env.example`
- `framework_rags/Makefile`
- `framework_rags/README.md`
- `framework_rags/.gitignore`

### Task 2: Shared Infrastructure Scripts

**2.1 Database Initialization**
- `scripts/init_db.sql` - Create schemas and extensions:
  ```sql
  -- Enable pgvector extension
  CREATE EXTENSION IF NOT EXISTS vector;

  -- Haystack schema
  CREATE SCHEMA IF NOT EXISTS haystack_docs;

  -- LightRAG schema
  CREATE SCHEMA IF NOT EXISTS lightrag;

  -- Grant permissions
  GRANT ALL ON SCHEMA haystack_docs TO raguser;
  GRANT ALL ON SCHEMA lightrag TO raguser;
  ```

**2.2 Backup Scripts**
- `scripts/backup.sh` - Backup PostgreSQL, Neo4j, LightRAG data
- `scripts/restore.sh` - Restore from backup

### Task 3: Haystack Deployment

**3.1 Docker Configuration**
- `haystack/Dockerfile` - Python 3.11 + Haystack + pgvector dependencies

**3.2 Python Package**
- `haystack/pyproject.toml` - Dependencies:
  ```toml
  dependencies = [
    "haystack-ai>=2.0",
    "pgvector-haystack>=0.3.0",
    "hayhooks[mcp]>=0.1.0",
    "cohere>=5.0",
    "jina-reranker>=0.1.0",  # Alternative reranker
    "ragas>=0.1.0",          # Evaluation
    "openai>=1.0",
  ]
  ```

**3.3 Pipeline Configuration**
- `config/default.yaml`:
  ```yaml
  embedding:
    model: "text-embedding-3-small"
    dimensions: 1536
    batch_size: 32

  splitting:
    split_by: "sentence"
    split_length: 10          # sentences per chunk
    split_overlap: 3          # sentence overlap

  retrieval:
    vector_top_k: 20
    bm25_top_k: 20
    reranker_top_k: 5
    similarity_threshold: 0.7

  vector_store:
    schema: "haystack_docs"
    table: "documents"
    hnsw:
      ef_construction: 256
      m: 16

  generation:
    model: "gpt-4o-mini"
    max_tokens: 1024

  metadata_filters:
    supported:
      - doc_type      # PRD, BRD, API, ARCH, SPEC, etc.
      - project_name  # Project identifier
      - version       # Document version
      - date          # Creation/update date
      - layer         # SDD layer (1-12)
  ```

**3.4 Source Code**
- `src/haystack_rag/__init__.py`
- `src/haystack_rag/config.py` - Load YAML config
- `src/haystack_rag/pipelines.py` - Build indexing/query pipelines:
  - **Indexing Pipeline**: MarkdownToDocument → DocumentCleaner → DocumentSplitter → MetadataEnricher → OpenAIDocumentEmbedder → DocumentWriter
  - **Query Pipeline**: OpenAITextEmbedder + BM25Retriever → DocumentJoiner (RRF) → CohereRanker → PromptBuilder → OpenAIChatGenerator
- `src/haystack_rag/server.py` - Hayhooks wrapper/entry point
- `src/haystack_rag/components/__init__.py`
- `src/haystack_rag/components/metadata_enricher.py` - Extract doc metadata from frontmatter/filename
- `src/haystack_rag/components/document_cleaner.py` - Remove artifacts, normalize whitespace
- `src/haystack_rag/components/vision_captioner.py` - Image captioning (future)

**3.5 Scripts**
- `scripts/setup.sh` - Install deps, run init_db.sql
- `scripts/index_docs.py` - CLI for bulk indexing with deduplication
- `scripts/verify.py` - Health check and connectivity test
- `scripts/export_pipeline.py` - Serialize pipelines to YAML for Hayhooks
- `scripts/evaluate.py` - RAGAS evaluation (context precision, faithfulness, relevance)

**3.6 Tests**
- `tests/conftest.py` - Shared fixtures
- `tests/test_pipelines.py` - Pipeline integration tests
- `tests/test_components.py` - Component unit tests

### Task 4: LightRAG Deployment

**4.1 Docker Configuration**
- `lightrag/Dockerfile` - Python 3.11 + LightRAG + Neo4j client

**4.2 Python Package**
- `lightrag/pyproject.toml` - Dependencies:
  ```toml
  dependencies = [
    "lightrag-hku>=0.1.0",
    "neo4j>=5.0",
    "psycopg2-binary>=2.9",
    "cohere>=5.0",
    "openai>=1.0",
  ]
  ```

**4.3 Configuration**
- `config/default.env`:
  ```bash
  # Server
  HOST=0.0.0.0
  PORT=9621
  WORKING_DIR=/opt/lightrag/data/rag_storage
  INPUT_DIR=/opt/lightrag/data/inputs

  # LLM Configuration
  LLM_BINDING=openai
  LLM_MODEL=gpt-4o-mini
  LLM_BINDING_HOST=https://api.openai.com/v1
  LLM_TIMEOUT=180              # Prevents hang on slow requests

  # Embedding Configuration
  EMBEDDING_BINDING=openai
  EMBEDDING_MODEL=text-embedding-3-small
  EMBEDDING_DIM=1536

  # Storage Configuration — Production Stack
  LIGHTRAG_KV_STORAGE=PostgreSQLStorage
  LIGHTRAG_VECTOR_STORAGE=PGVectorStorage
  LIGHTRAG_GRAPH_STORAGE=Neo4JStorage
  LIGHTRAG_DOC_STATUS_STORAGE=PostgreSQLDocStatusStorage

  # PostgreSQL
  POSTGRES_HOST=postgres
  POSTGRES_PORT=5432
  POSTGRES_USER=raguser
  POSTGRES_PASSWORD=ragpass
  POSTGRES_DATABASE=ragdb

  # Neo4j
  NEO4J_URI=bolt://neo4j:7687
  NEO4J_USERNAME=neo4j
  NEO4J_PASSWORD=neo4jpass

  # Query Defaults
  DEFAULT_QUERY_MODE=hybrid
  TOP_K=10
  MAX_TOKEN_FOR_TEXT_UNIT=4000
  MAX_TOKEN_FOR_GLOBAL_CONTEXT=4000
  MAX_TOKEN_FOR_LOCAL_CONTEXT=4000

  # Entity Extraction
  CHUNK_SIZE=1200
  CHUNK_OVERLAP_SIZE=200

  # Authentication
  LIGHTRAG_API_KEY=lightragsecretkey

  # Reranker
  RERANK_BINDING=cohere
  RERANK_MODEL=rerank-english-v3.0
  RERANK_TOP_K=5
  ```

- `config/entity_types.py` - 12 domain-agnostic entity types:
  ```python
  CUSTOM_ENTITY_TYPES = [
      "organization",    # Companies, agencies, institutions, funds
      "person",          # Analysts, executives, researchers, authors
      "product",         # Software, platforms, services, instruments
      "technology",      # Frameworks, protocols, languages, algorithms
      "concept",         # Methodologies, theories, strategies, patterns
      "metric",          # KPIs, financial ratios, benchmarks, scores
      "event",           # Earnings calls, launches, regulatory actions
      "decision",        # Trade executions, architecture choices
      "finding",         # Conclusions, insights, recommendations
      "risk",            # Identified risks, vulnerabilities, concerns
      "regulation",      # Laws, compliance requirements, standards
      "market_segment",  # Industries, sectors, geographies
  ]
  ```

**4.4 Source Code**
- `src/lightrag_service/__init__.py`
- `src/lightrag_service/config.py` - Load env config
- `src/lightrag_service/custom_prompts.py` - Entity extraction prompts
- `src/lightrag_service/health.py` - Health monitoring

**4.5 Scripts**
- `scripts/setup.sh` - Install deps, init Neo4j, **install daniel-lightrag-mcp**:
  ```bash
  # Install daniel-lightrag-mcp for MCP bridge
  git clone https://github.com/desimpkins/daniel-lightrag-mcp.git /opt/daniel-lightrag-mcp
  cd /opt/daniel-lightrag-mcp && pip install -e .
  ```
- `scripts/index_docs.py` - CLI for bulk indexing (**30-50 doc batch limit**)
- `scripts/verify.py` - Health check (includes WebUI availability at port 9621)
- `scripts/graph_stats.py` - Neo4j graph statistics

**4.6 Tests**
- `tests/conftest.py` - Shared fixtures
- `tests/test_extraction.py` - Entity extraction tests
- `tests/test_queries.py` - Query mode tests (local, global, hybrid)

### Task 5: Shared Infrastructure (docker-compose.yml)

**5.1 PostgreSQL + pgvector**
```yaml
postgres:
  image: pgvector/pgvector:pg16
  ports:
    - "5432:5432"
  environment:
    POSTGRES_DB: ragdb
    POSTGRES_USER: raguser
    POSTGRES_PASSWORD: ragpass
  volumes:
    - pg_data:/var/lib/postgresql/data
    - ./scripts/init_db.sql:/docker-entrypoint-initdb.d/init_db.sql
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U raguser -d ragdb"]
    interval: 10s
    timeout: 5s
    retries: 5
```

**5.2 Neo4j Community**
```yaml
neo4j:
  image: neo4j:5-community
  ports:
    - "7474:7474"   # HTTP (Browser UI)
    - "7687:7687"   # Bolt
  environment:
    NEO4J_AUTH: neo4j/neo4jpass
    NEO4J_PLUGINS: '["apoc"]'
  volumes:
    - neo4j_data:/data
  healthcheck:
    test: ["CMD", "neo4j", "status"]
    interval: 10s
    timeout: 5s
    retries: 5
```

**5.3 Haystack Service**
```yaml
haystack:
  build: ./haystack
  ports:
    - "1416:1416"
  environment:
    - OPENAI_API_KEY=${OPENAI_API_KEY}
    - COHERE_API_KEY=${COHERE_API_KEY}
    - PG_CONN_STR=postgresql://raguser:ragpass@postgres:5432/ragdb
  volumes:
    - ./haystack/config:/app/config
    - haystack_data:/app/data
  depends_on:
    postgres:
      condition: service_healthy
```

**5.4 LightRAG Service**
```yaml
lightrag:
  build: ./lightrag
  ports:
    - "9621:9621"
  env_file:
    - ./lightrag/config/default.env
  environment:
    - OPENAI_API_KEY=${OPENAI_API_KEY}
    - COHERE_API_KEY=${COHERE_API_KEY}
  volumes:
    - ./lightrag/config:/app/config
    - lightrag_data:/app/data
  depends_on:
    postgres:
      condition: service_healthy
    neo4j:
      condition: service_healthy
```

### Task 6: RAG Tools (Shared Utilities)

- `rag_tools/__init__.py`
- `rag_tools/doc_scanner.py` - Scan ai_dev_flow/ for markdown docs by layer
- `rag_tools/batch_indexer.py` - Coordinate indexing across both RAGs:
  - Haystack: No batch limit (embedding only)
  - LightRAG: **30-50 doc batch limit** with status monitoring
- `rag_tools/query_router.py` - Route queries based on type:
  - Factual/keyword queries → Haystack
  - Relational/thematic queries → LightRAG
- `rag_tools/health_monitor.py` - Check all service health:
  - PostgreSQL: `pg_isready`
  - Neo4j: Bolt connection test
  - Haystack: API health endpoint
  - LightRAG: `/health` endpoint + WebUI availability
- `rag_tools/mcp_config_generator.py` - Generate Claude Desktop/Cursor configs

### Task 7: MCP Configuration

- `mcp/claude_desktop_config.json.example`:
  ```json
  {
    "mcpServers": {
      "project-docs": {
        "command": "hayhooks",
        "args": ["--pipelines-dir", "/opt/haystack/pipelines"],
        "env": {
          "OPENAI_API_KEY": "${OPENAI_API_KEY}",
          "PG_CONN_STR": "postgresql://raguser:ragpass@localhost:5432/ragdb"
        }
      },
      "research-kb": {
        "command": "python",
        "args": ["-m", "daniel_lightrag_mcp"],
        "env": {
          "LIGHTRAG_BASE_URL": "http://localhost:9621",
          "LIGHTRAG_API_KEY": "lightragsecretkey",
          "LIGHTRAG_TIMEOUT": "60"
        }
      }
    }
  }
  ```
- `mcp/cursor_config.json.example` - Cursor IDE configuration

### Task 8: Makefile Integration

```makefile
.PHONY: help rag-up rag-down rag-build rag-index rag-verify rag-logs rag-backup rag-restore

help:
	@echo "RAG Deployment Targets:"
	@echo "  rag-up        Start all RAG services"
	@echo "  rag-down      Stop all services"
	@echo "  rag-build     Build Docker images"
	@echo "  rag-index     Index framework docs"
	@echo "  rag-verify    Health check all services"
	@echo "  rag-logs      Tail service logs"
	@echo "  rag-backup    Backup all data"
	@echo "  rag-restore   Restore from backup"
	@echo "  rag-eval      Run RAGAS evaluation"
	@echo "  haystack-shell  Interactive Haystack shell"
	@echo "  lightrag-shell  Interactive LightRAG shell"
	@echo "  neo4j-browser   Open Neo4j Browser URL"

rag-up:
	docker-compose up -d

rag-down:
	docker-compose down

rag-build:
	docker-compose build

rag-index:
	python rag_tools/batch_indexer.py --source ../ai_dev_flow

rag-verify:
	python rag_tools/health_monitor.py

rag-logs:
	docker-compose logs -f

rag-backup:
	./scripts/backup.sh

rag-restore:
	./scripts/restore.sh

rag-eval:
	python haystack/scripts/evaluate.py

haystack-shell:
	docker-compose exec haystack /bin/bash

lightrag-shell:
	docker-compose exec lightrag /bin/bash

neo4j-browser:
	@echo "Open http://localhost:7474 in your browser"
```

### Task 9: Documentation

- `README.md` - Complete setup guide with:
  - Prerequisites (Docker, API keys)
  - Quick start (3 commands)
  - Configuration reference
  - Metadata filter usage examples
  - Batch indexing guidelines
  - Troubleshooting
  - API examples
  - WebUI access (Neo4j Browser, LightRAG WebUI)

---

## Key Configuration Values

### Haystack (Service 1)
| Parameter | Value | Notes |
|-----------|-------|-------|
| Port | 1416 | Hayhooks MCP server |
| Embedding Model | text-embedding-3-small | 1536 dimensions |
| Chunk Size | 10 sentences | ~200-400 tokens |
| Chunk Overlap | 3 sentences | Preserves context |
| BM25 + Vector | Hybrid search | Reciprocal Rank Fusion |
| Reranker | Cohere rerank-english-v3.0 | Jina as fallback |
| Top-K | 5 | After reranking |
| HNSW ef_construction | 256 | Index build quality |
| HNSW m | 16 | Connections per node |
| LLM | gpt-4o-mini | Query answering |

### LightRAG (Service 2)
| Parameter | Value | Notes |
|-----------|-------|-------|
| Port | 9621 | REST API + WebUI |
| Embedding Model | text-embedding-3-small | 1536 dimensions |
| LLM Model | gpt-4o-mini | Entity extraction + queries |
| LLM_TIMEOUT | 180 | Prevents hang on slow requests |
| Chunk Size | 1200 tokens | Entity extraction units |
| Chunk Overlap | 200 tokens | Context preservation |
| Query Mode | hybrid | Default mode |
| Entity Types | 12 domain-agnostic | See entity_types.py |
| Graph Storage | Neo4j | Entities + relationships |
| Vector Storage | pgvector | Embeddings |
| Batch Limit | 30-50 docs | Per indexing session |

### Shared PostgreSQL
| Parameter | Value | Notes |
|-----------|-------|-------|
| Port | 5432 | Standard PostgreSQL |
| Database | ragdb | Shared database |
| Haystack Schema | haystack_docs | Document store |
| LightRAG Schema | lightrag | KV + vector storage |
| Extension | pgvector | Vector similarity |

### Neo4j
| Parameter | Value | Notes |
|-----------|-------|-------|
| HTTP Port | 7474 | Browser UI |
| Bolt Port | 7687 | Driver connections |
| Database | neo4j | Default database |
| Plugin | APOC | Graph utilities |

---

## Files to Create (49 files implemented)

### Root Level (5 files)
1. `framework_rags/docker-compose.yml`
2. `framework_rags/.env.example`
3. `framework_rags/Makefile`
4. `framework_rags/README.md`
5. `framework_rags/.gitignore`

### Shared Scripts (3 files)
6. `scripts/init_db.sql`
7. `scripts/backup.sh`
8. `scripts/restore.sh`

### Haystack (16 files)
9. `haystack/Dockerfile`
10. `haystack/pyproject.toml`
11. `haystack/config/default.yaml`
12. `haystack/src/haystack_rag/__init__.py`
13. `haystack/src/haystack_rag/config.py`
14. `haystack/src/haystack_rag/pipelines.py`
15. `haystack/src/haystack_rag/server.py`
16. `haystack/src/haystack_rag/components/__init__.py`
17. `haystack/src/haystack_rag/components/metadata_enricher.py`
18. `haystack/src/haystack_rag/components/document_cleaner.py`
19. `haystack/src/haystack_rag/components/vision_captioner.py`
20. `haystack/scripts/setup.sh`
21. `haystack/scripts/index_docs.py`
22. `haystack/scripts/verify.py`
23. `haystack/scripts/export_pipeline.py`
24. `haystack/scripts/evaluate.py`
25. `haystack/tests/conftest.py`
26. `haystack/tests/test_pipelines.py`
27. `haystack/tests/test_components.py`

### LightRAG (14 files)
28. `lightrag/Dockerfile`
29. `lightrag/pyproject.toml`
30. `lightrag/config/default.env`
31. `lightrag/config/entity_types.py`
32. `lightrag/src/lightrag_service/__init__.py`
33. `lightrag/src/lightrag_service/config.py`
34. `lightrag/src/lightrag_service/custom_prompts.py`
35. `lightrag/src/lightrag_service/health.py`
36. `lightrag/scripts/setup.sh`
37. `lightrag/scripts/index_docs.py`
38. `lightrag/scripts/verify.py`
39. `lightrag/scripts/graph_stats.py`
40. `lightrag/tests/conftest.py`
41. `lightrag/tests/test_extraction.py`
42. `lightrag/tests/test_queries.py`

### RAG Tools (5 files)
43. `rag_tools/__init__.py`
44. `rag_tools/doc_scanner.py`
45. `rag_tools/batch_indexer.py`
46. `rag_tools/query_router.py`
47. `rag_tools/health_monitor.py`
48. `rag_tools/mcp_config_generator.py`

### MCP (2 files)
49. `mcp/claude_desktop_config.json.example`
50. `mcp/cursor_config.json.example`

**Total: 50 files**

---

## Verification

After implementation:

1. **Docker Build**
   ```bash
   cd framework_rags && make rag-build
   ```

2. **Start Services**
   ```bash
   make rag-up
   ```

3. **Health Check**
   ```bash
   make rag-verify
   # Expected: All 4 services healthy (postgres, neo4j, haystack, lightrag)
   ```

4. **Verify WebUIs**
   - Neo4j Browser: http://localhost:7474
   - LightRAG WebUI: http://localhost:9621

5. **Index Sample Docs**
   ```bash
   make rag-index
   # Indexes ai_dev_flow/ documentation
   ```

6. **Query Tests**
   - Haystack (factual): "What are the validation rules for BRD documents?"
   - Haystack (filtered): "Show PRD requirements for authentication" (doc_type=PRD)
   - LightRAG (relational): "What patterns connect EARS requirements to BDD scenarios?"
   - LightRAG (global): "What common themes appear across all architecture decisions?"

7. **Evaluation**
   ```bash
   make rag-eval
   # Runs RAGAS metrics on test query set
   ```

8. **MCP Integration**
   ```bash
   python rag_tools/mcp_config_generator.py > ~/claude_desktop_config.json
   # Restart Claude Desktop, verify tools available
   ```

9. **Backup Test**
   ```bash
   make rag-backup
   # Verify backup files created in ./backups/
   ```

---

## Risk Mitigations (Implemented)

| Risk | Mitigation | Implementation |
|------|------------|----------------|
| LightRAG server hang | Batch limits + timeout | `LLM_TIMEOUT=180`, 30-50 doc batches in `batch_indexer.py` |
| Entity extraction quality | Custom entity types | 12 domain-agnostic types in `entity_types.py` |
| Entity deduplication | Standardized naming | Document scanner respects frontmatter conventions |
| MCP server breaks | Version pinning | Pin LightRAG version in Dockerfile |
| Data loss | Automated backups | `backup.sh` covers PostgreSQL, Neo4j, LightRAG data |
| Query routing errors | Explicit routing | `query_router.py` with type detection |

---

## Metadata Filter Examples

Haystack supports filtering at query time:

```python
# Filter by document type
filters = {"doc_type": {"$eq": "PRD"}}

# Filter by project
filters = {"project_name": {"$eq": "BeeLocal"}}

# Filter by SDD layer
filters = {"layer": {"$gte": 5}}  # ADR and above

# Filter by date
filters = {"date": {"$gte": "2025-01-01"}}

# Combined filters
filters = {
    "$and": [
        {"doc_type": {"$in": ["PRD", "BRD"]}},
        {"layer": {"$lte": 3}}
    ]
}
```

---

## Upgrade Path Reference

See `docs/ARCHITECTURE.md` for detailed upgrade paths:
1. Direct Cypher queries
2. Haystack agent layer
3. RAGAS automated evaluation (implemented)
4. Local LLM for extraction
5. Domain-specific extraction profiles
6. Cross-KB queries
7. Multimodal image support

---

## Implementation Status

**Last Updated**: 2026-02-16

### Completion Summary

| Category | Planned | Implemented | Status |
|----------|---------|-------------|--------|
| Root files | 5 | 5 | Complete |
| Shared scripts | 3 | 3 | Complete |
| Haystack | 19 | 18 | 95% (vision_captioner deferred) |
| LightRAG | 15 | 15 | Complete |
| RAG Tools | 6 | 6 | Complete |
| MCP configs | 2 | 2 | Complete |
| **Total** | **50** | **49** | **98%** |

### Files Implemented (49/50)

**Root Level (5/5)**
- [x] docker-compose.yml
- [x] .env.example
- [x] Makefile
- [x] README.md
- [x] .gitignore

**Shared Scripts (3/3)**
- [x] scripts/init_db.sql
- [x] scripts/backup.sh
- [x] scripts/restore.sh

**Haystack (18/19)**
- [x] Dockerfile
- [x] pyproject.toml
- [x] config/default.yaml
- [x] src/haystack_rag/__init__.py
- [x] src/haystack_rag/config.py
- [x] src/haystack_rag/pipelines.py
- [x] src/haystack_rag/server.py
- [x] src/haystack_rag/components/__init__.py
- [x] src/haystack_rag/components/metadata_enricher.py
- [x] src/haystack_rag/components/document_cleaner.py
- [ ] src/haystack_rag/components/vision_captioner.py *(deferred - Phase 5+)*
- [x] scripts/setup.sh
- [x] scripts/index_docs.py
- [x] scripts/verify.py
- [x] scripts/export_pipeline.py
- [x] scripts/evaluate.py
- [x] tests/conftest.py
- [x] tests/test_pipelines.py
- [x] tests/test_components.py

**LightRAG (15/15)**
- [x] Dockerfile
- [x] Dockerfile.mcp
- [x] pyproject.toml
- [x] config/default.env
- [x] config/entity_types.py
- [x] src/lightrag_service/__init__.py
- [x] src/lightrag_service/config.py
- [x] src/lightrag_service/custom_prompts.py
- [x] src/lightrag_service/health.py
- [x] scripts/setup.sh
- [x] scripts/index_docs.py
- [x] scripts/verify.py
- [x] scripts/graph_stats.py
- [x] tests/conftest.py
- [x] tests/test_extraction.py
- [x] tests/test_queries.py

**RAG Tools (6/6)**
- [x] __init__.py
- [x] doc_scanner.py
- [x] batch_indexer.py
- [x] query_router.py
- [x] health_monitor.py
- [x] mcp_config_generator.py

**MCP (2/2)**
- [x] claude_desktop_config.json.example
- [x] cursor_config.json.example

**Documentation (1/1)**
- [x] docs/ARCHITECTURE.md

### Deferred Items

| Item | Reason | Target Phase |
|------|--------|--------------|
| vision_captioner.py | Multimodal support | Phase 5+ |

### Next Steps

1. Run `make setup` to create .env from template
2. Add OpenAI API key to .env
3. Run `make rag-build` to build Docker images
4. Run `make rag-up` to start services
5. Run `make rag-verify` to check health
6. Run `make rag-index` to index framework docs
