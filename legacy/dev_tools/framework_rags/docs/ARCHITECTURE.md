# Option A: Dual-Service RAG Architecture — Detailed Implementation Plan

## Architecture Overview

Two purpose-built services, each optimized for a different class of knowledge:

- **Service 1 (Haystack):** Technical and project documentation — structured, factual, keyword-dense content where hybrid search (BM25 + vector + reranker) excels
- **Service 2 (LightRAG):** Research, analysis, and studies — content rich in entities, relationships, and cross-document themes where graph-based retrieval adds value

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Claude Desktop / Cursor                      │
│                    (MCP Client — routes queries)                     │
└──────────┬──────────────────────────────────────┬───────────────────┘
           │                                      │
           ▼                                      ▼
┌─────────────────────────┐          ┌───────────────────────────────┐
│   SERVICE 1: Hayhooks   │          │  SERVICE 2: LightRAG Server   │
│      MCP Server         │          │    + Daniel LightRAG MCP      │
│   (Port 1416/stdio)     │          │      (Port 9621/stdio)        │
├─────────────────────────┤          ├───────────────────────────────┤
│  Haystack Pipelines:    │          │  LightRAG Engine:             │
│  • Markdown Converter   │          │  • Entity Extraction (GPT-4o) │
│  • Semantic Splitter    │          │  • Knowledge Graph Builder    │
│  • Embedder (OpenAI)    │          │  • Dual-Level Retrieval       │
│  • BM25 Retriever       │          │  • Incremental Updates        │
│  • Vector Retriever     │          │  • Reranker (Cohere/Jina)     │
│  • Reranker (Cohere)    │          │  • WebUI (Graph Viz)          │
│  • LLM Generator        │          │                               │
├─────────────────────────┤          ├───────────────────────────────┤
│  PostgreSQL + pgvector  │          │  Storage Backends:            │
│  (Document Store)       │          │  • Neo4j Community (Graph)    │
│                         │          │  • PostgreSQL + pgvector      │
│                         │          │  • PostgreSQL KV Storage      │
└─────────────────────────┘          └───────────────────────────────┘
           │                                      │
           ▼                                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Shared PostgreSQL Instance                        │
│              (pgvector extension, separate schemas)                  │
│                                                                     │
│   haystack_docs schema:              lightrag schema:               │
│   • documents table                  • kv_store tables              │
│   • embeddings (pgvector)            • vector_store (pgvector)      │
│   • BM25 index                       • doc_status tables            │
└─────────────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                 Neo4j Community Edition (Docker)                     │
│                    (LightRAG graph storage only)                     │
│                    Port 7474 (HTTP) / 7687 (Bolt)                   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Service 1: Haystack — Technical & Project Documentation

### What It Handles

Structured, factual documentation in markdown format:
- Product Requirements Documents (PRDs)
- Architecture specifications
- API documentation
- Business Requirements Documents (BRDs)
- Technical specifications
- Meeting notes, decision logs
- Runbooks, deployment guides

### Why Haystack for This

Project documentation is **structured, factual, and keyword-rich**. You're asking questions like:
- "What are the API rate limits for the payments service?"
- "What did the BRD say about compliance requirements?"
- "Show me the authentication flow from the architecture spec"

These queries benefit from **hybrid search** (BM25 keyword matching + semantic vector search + reranking). Graph-based retrieval adds nothing here — the relationships between concepts in a PRD are already captured in the document structure. BM25 is essential because technical terms like "OAuth2", "HMAC-SHA256", or "idempotency key" need exact lexical matching, not just semantic similarity.

### Infrastructure

**PostgreSQL with pgvector** — single database serving as both:
- Haystack's `PgvectorDocumentStore` (stores documents, embeddings, metadata)
- BM25 full-text search via PostgreSQL's built-in `tsvector`/`tsquery`

### Haystack Pipeline Design

#### Indexing Pipeline

```
Markdown Files (from /docs directory)
        │
        ▼
MarkdownToDocument Converter
        │
        ▼
DocumentCleaner (remove artifacts, normalize whitespace)
        │
        ▼
DocumentSplitter
  • split_by: "sentence"
  • split_length: 10 (sentences per chunk)
  • split_overlap: 3 (sentence overlap)
        │
        ▼
MetadataEnricher (custom component)
  • Extracts: doc_type (PRD/BRD/API/ARCH), project_name,
    version, date, author from frontmatter/filename
        │
        ▼
OpenAIDocumentEmbedder
  • model: "text-embedding-3-small"
  • dimensions: 1536
        │
        ▼
DocumentWriter → PgvectorDocumentStore
```

#### Query Pipeline

```
User Query (from MCP tool call)
        │
        ├──────────────────────┐
        ▼                      ▼
OpenAITextEmbedder      BM25Retriever
        │               (PostgreSQL FTS)
        ▼                      │
PgvectorRetriever              │
  • top_k: 20                  │
        │                      │
        └──────────┬───────────┘
                   ▼
          DocumentJoiner
      (reciprocal_rank_fusion)
                   │
                   ▼
          CohereRanker (or JinaRanker)
            • top_k: 5
                   │
                   ▼
          PromptBuilder
      (system prompt + retrieved docs + query)
                   │
                   ▼
          OpenAIChatGenerator
            • model: "gpt-4o-mini"
                   │
                   ▼
          Answer (returned via MCP)
```

### Key Configuration Details

**PgvectorDocumentStore setup:**
```
Connection: postgresql://user:pass@localhost:5432/ragdb
Schema: haystack_docs
Table: documents
Embedding dimension: 1536
Vector index: HNSW (ef_construction=256, m=16)
Recreate table: false (preserves data across restarts)
```

**Splitting strategy rationale:**
- Sentence-based splitting preserves complete thoughts better than character-based
- 10 sentences ≈ 200-400 tokens per chunk, fits well within embedding model limits
- 3-sentence overlap ensures no information falls between chunk boundaries
- For structured docs (PRDs with headers), the splitter respects paragraph boundaries

**Metadata filters** that Haystack supports at query time:
- `doc_type == "PRD"` — restrict search to PRDs only
- `project_name == "BeeLocal"` — search within one project
- `date >= "2025-01-01"` — recent docs only

### Hayhooks MCP Server Configuration

Hayhooks exposes each Haystack pipeline as an MCP tool. Install and configure:

```bash
pip install hayhooks[mcp]
```

**Environment variables:**
```
HAYHOOKS_PIPELINES_DIR=/opt/haystack/pipelines
HAYHOOKS_HOST=0.0.0.0
HAYHOOKS_PORT=1416
```

**Pipeline YAML** (saved as `/opt/haystack/pipelines/query_docs.yaml`):
The pipeline is serialized to YAML and auto-loaded by Hayhooks on startup. Each pipeline becomes an MCP tool that Claude can call.

**Claude Desktop MCP config** (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "haystack-docs": {
      "command": "hayhooks",
      "args": ["--pipelines-dir", "/opt/haystack/pipelines"],
      "env": {
        "OPENAI_API_KEY": "sk-...",
        "PG_CONN_STR": "postgresql://user:pass@localhost:5432/ragdb"
      }
    }
  }
}
```

**What Claude sees as MCP tools:**
- `query_docs` — Run a query against project documentation
- `index_docs` — Index new markdown files into the document store (optional, can be a separate pipeline triggered manually)

---

## Service 2: LightRAG — Research & Analysis Knowledge Base

### What It Handles

Any research, analysis, or study content where **entities and their relationships** are the primary value — not just the text itself. This is domain-agnostic by design. Current and future content domains include:

**Trading & Financial Research:**
- Earnings analysis reports
- Fundamental analysis documents
- Analyst report summaries
- Trade journal entries
- Stock screening criteria, catalyst tracking

**Technology Research:**
- AI/ML landscape analyses
- Framework and tool evaluations (like this RAG comparison)
- Vendor assessments, competitive intelligence
- Technology trend studies

**Market & Industry Research:**
- Industry reports, market sizing studies
- Regulatory landscape analyses
- Competitive positioning documents

**Any Future Research Domain:**
- The graph-based approach works for any content where you need to discover relationships across documents: people → companies → events → outcomes → decisions

### Why LightRAG for This (Domain-Agnostic Rationale)

Research and analysis content has a fundamentally different query pattern than project documentation. With project docs you ask "what does document X say about Y?" — a retrieval question. With research, you ask questions that span across documents and require connecting entities:

- "What companies have I analyzed that had earnings misses followed by analyst downgrades?"
- "Which AI frameworks did I evaluate that support both Python and TypeScript?"
- "What patterns appear across my profitable trade analyses?"
- "How do the regulatory findings from my EU study connect to the US compliance research?"

These are **relational queries** — the answer lives in the connections between entities, not in any single document chunk. LightRAG's dual-level retrieval handles both:
- **Low-level (specific):** "What did my PayPal earnings analysis say?" → Finds the PayPal entity and its direct relationships
- **High-level (thematic):** "What common patterns appear across my fintech analyses?" → Traverses broader theme clusters across the entire knowledge graph

### Infrastructure

**Neo4j Community Edition (Docker)** — graph storage for entities and relationships
**PostgreSQL + pgvector** — vector storage and KV cache (shared instance with Haystack, separate schema)

### LightRAG Configuration

**`.env` file** (LightRAG server root):

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
LLM_BINDING_API_KEY=sk-...

# Embedding Configuration
EMBEDDING_BINDING=openai
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIM=1536
EMBEDDING_BINDING_HOST=https://api.openai.com/v1
EMBEDDING_BINDING_API_KEY=sk-...

# Storage Configuration — Production Stack
LIGHTRAG_KV_STORAGE=PostgreSQLStorage
LIGHTRAG_VECTOR_STORAGE=PGVectorStorage
LIGHTRAG_GRAPH_STORAGE=Neo4JStorage
LIGHTRAG_DOC_STATUS_STORAGE=PostgreSQLDocStatusStorage

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=raguser
POSTGRES_PASSWORD=ragpass
POSTGRES_DATABASE=ragdb

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=neo4jpass

# Query Defaults
DEFAULT_QUERY_MODE=hybrid
TOP_K=10
MAX_TOKEN_FOR_TEXT_UNIT=4000
MAX_TOKEN_FOR_GLOBAL_CONTEXT=4000
MAX_TOKEN_FOR_LOCAL_CONTEXT=4000

# Entity Extraction — CRITICAL CUSTOMIZATION
CHUNK_SIZE=1200
CHUNK_OVERLAP_SIZE=200

# Authentication
LIGHTRAG_API_KEY=lightragsecretkey

# Reranker (optional but recommended)
RERANK_BINDING=cohere
RERANK_MODEL=rerank-english-v3.0
RERANK_API_KEY=your-cohere-key
RERANK_TOP_K=5
```

### Custom Entity Types — Domain-Agnostic Approach

This is the most important customization. LightRAG's default entity types are `["organization", "person", "geo", "event"]` — too generic for any specialized research domain.

**Strategy: Use a broad but research-oriented entity type set** that covers multiple domains without being so specific it misses entities outside a narrow scope.

**Override in LightRAG's prompt configuration:**

```python
CUSTOM_ENTITY_TYPES = [
    # Universal research entities
    "organization",       # Companies, agencies, institutions, funds
    "person",             # Analysts, executives, researchers, authors
    "product",            # Software, platforms, services, instruments
    "technology",         # Frameworks, protocols, languages, algorithms
    "concept",            # Methodologies, theories, strategies, patterns
    "metric",             # KPIs, financial ratios, benchmarks, scores
    "event",              # Earnings calls, launches, regulatory actions, conferences
    "decision",           # Trade executions, architecture choices, go/no-go decisions
    "finding",            # Conclusions, insights, recommendations from analysis
    "risk",               # Identified risks, vulnerabilities, concerns
    "regulation",         # Laws, compliance requirements, standards
    "market_segment",     # Industries, sectors, geographies, demographics
]
```

**Why these 12 types work across domains:**
- Trading: "PayPal" (organization) → "Q3 earnings miss" (event) → "bought at $72" (decision) → "15% return" (metric)
- Tech evaluation: "LightRAG" (product) → "graph-based retrieval" (technology) → "entity extraction issues" (finding) → "28K GitHub stars" (metric)
- Regulatory research: "GDPR" (regulation) → "EU" (market_segment) → "data residency requirement" (finding) → "non-compliance penalty" (risk)

The graph captures the same structural pattern — entities connected by relationships — regardless of what domain the research covers.

**Per-domain refinement (optional, later):** If a specific domain needs tighter extraction, you can create domain-specific extraction prompts and switch between them. But the broad set above is the right starting point — it avoids premature optimization.

**Known limitation:** Even with custom types, expect ~70-80% extraction accuracy on first pass. You'll need to review and potentially re-index documents after tuning the prompts. This is normal for any LLM-based extraction system.

### LightRAG Server Deployment

**Docker Compose** (recommended):

```yaml
version: '3.8'

services:
  lightrag:
    image: lightrag/lightrag:latest
    ports:
      - "9621:9621"
    volumes:
      - ./data:/app/data
      - ./.env:/app/.env
    depends_on:
      - postgres
      - neo4j
    extra_hosts:
      - "host.docker.internal:host-gateway"

  neo4j:
    image: neo4j:5-community
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      NEO4J_AUTH: neo4j/neo4jpass
      NEO4J_PLUGINS: '["apoc"]'
    volumes:
      - neo4j_data:/data

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

volumes:
  neo4j_data:
  pg_data:
```

**Note:** If you're already running PostgreSQL for Haystack, skip the postgres service and point both Haystack and LightRAG at the same instance (different schemas).

### Daniel LightRAG MCP Server

This is the bridge between LightRAG's REST API and Claude Desktop's MCP protocol. It provides 22 tools across 4 categories.

**Installation:**
```bash
git clone https://github.com/desimpkins/daniel-lightrag-mcp.git
cd daniel-lightrag-mcp
pip install -e .
```

**Claude Desktop MCP config:**
```json
{
  "mcpServers": {
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

**22 MCP Tools Available:**

| Category | Tools | What They Do |
|----------|-------|-------------|
| **Document Management** (6) | `insert_text`, `insert_texts`, `upload_document`, `get_documents`, `get_documents_paginated`, `delete_document` | Add/remove/list research documents |
| **Query Operations** (2) | `query_text`, `query_text_stream` | Run queries in local/global/hybrid/naive/mix modes |
| **Knowledge Graph** (10) | `get_entity`, `get_entities`, `get_relation`, `get_relations`, `get_knowledge_graph`, `update_entity`, `update_relation`, `delete_entity`, `delete_relation`, `get_graph_statistics` | Full CRUD on entities and relationships |
| **System** (4) | `get_health`, `get_pipeline_status`, `get_document_status_counts`, `clear_cache` | Monitor health and processing status |

**What Claude can do with these tools:**
- "Search my research for earnings analysis on PayPal" → `query_text` with mode="hybrid"
- "Add this new analysis to the research KB" → `insert_text`
- "Show me all entities related to graph databases" → `get_entity` then `get_relations`
- "What patterns connect my fintech and regulatory research?" → `query_text` with mode="global"
- "What's the overall structure of my knowledge graph?" → `get_graph_statistics`

---

## Combined Claude Desktop Configuration

The final `claude_desktop_config.json` with both services:

```json
{
  "mcpServers": {
    "project-docs": {
      "command": "hayhooks",
      "args": ["--pipelines-dir", "/opt/haystack/pipelines"],
      "env": {
        "OPENAI_API_KEY": "sk-...",
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

**How Claude Routes Queries:**
Claude sees both tool sets and naturally routes based on context:
- "What are the API requirements in the payments PRD?" → Uses `project-docs` tools
- "What did my analysis say about PayPal's earnings?" → Uses `research-kb` tools
- "What patterns connect my AI framework evaluations?" → Uses `research-kb` tools
- If Claude picks wrong, you just say "use the research KB" or "check project docs"

---

## Document Ingestion Workflow

### Project Documentation (Haystack)

**Initial bulk load:**
```bash
# Place all markdown files in the input directory
cp /path/to/your/docs/*.md /opt/haystack/input/

# Run the indexing pipeline (via Hayhooks API or direct Python)
python -c "
from haystack_pipelines import create_indexing_pipeline
pipeline = create_indexing_pipeline()
pipeline.run({'sources': ['/opt/haystack/input/']})
"
```

**Ongoing updates:**
- Drop new/updated markdown files into `/opt/haystack/input/`
- Re-run indexing pipeline (Haystack handles deduplication via document IDs)
- Or trigger via MCP tool if you've exposed an `index_docs` pipeline

**Estimated time for 100 docs:** 5-10 minutes (mostly embedding generation)
**Estimated cost:** $2-5 one-time (embeddings only, no LLM extraction needed)

### Research & Analysis (LightRAG)

**Initial bulk load:**
```bash
# Option 1: Copy files to LightRAG input directory
cp /path/to/research/*.md /opt/lightrag/data/inputs/

# Option 2: Use the REST API
curl -X POST http://localhost:9621/documents/upload \
  -F "files=@earnings_analysis_pypl.md" \
  -H "X-API-Key: lightragsecretkey"

# Option 3: Use the MCP tool from Claude
# Just ask Claude: "Upload all files from /path/to/research/ to the research KB"
```

**What happens during indexing:**
1. LightRAG chunks each document (1200 tokens, 200 overlap)
2. Each chunk is sent to GPT-4o-mini for entity/relationship extraction
3. Extracted entities are deduplicated (name-based matching)
4. Knowledge graph is built/updated in Neo4j
5. Embeddings are generated and stored in pgvector
6. KV cache is updated in PostgreSQL

**Estimated time for 100 docs:** 1-2 hours (LLM extraction is the bottleneck)
**Estimated cost:** $15-30 one-time (GPT-4o-mini entity extraction + embeddings)

**IMPORTANT: Server stability during bulk indexing**
LightRAG server can hang after 3+ hours of continuous processing (documented Issue #1300). Mitigation:
- Index in batches of 30-50 documents
- Monitor via `get_pipeline_status` MCP tool
- If hang occurs, restart server — LightRAG resumes from where it stopped (it tracks document status)

**Ongoing updates:**
- New research/analysis → `insert_text` via MCP or drop file in input directory
- LightRAG performs incremental graph update (no full rebuild)
- Cost: ~$0.10-0.20 per new document

---

## Infrastructure Requirements

### Minimum VPS Specification

| Component | Requirement | Notes |
|-----------|-------------|-------|
| **CPU** | 4 cores | Neo4j and LightRAG both benefit from multi-core |
| **RAM** | 16 GB | Neo4j: 4-6 GB, PostgreSQL: 2-4 GB, LightRAG: 2-3 GB, Haystack: 1-2 GB |
| **Storage** | 50 GB SSD | Neo4j data, PostgreSQL data, document cache |
| **OS** | Ubuntu 22.04+ or Ubuntu 24.04 | Docker support, Python 3.11+ |
| **Network** | Outbound HTTPS | OpenAI API, Cohere API |

**Recommended VPS options:**
- Hetzner CPX41: 8 vCPU, 16 GB RAM, 240 GB — ~$28/month
- DigitalOcean Premium: 4 vCPU, 16 GB RAM, 100 GB — ~$48/month
- AWS t3.xlarge: 4 vCPU, 16 GB RAM — ~$120/month (overkill but reliable)

### Monthly Cost Breakdown

| Item | Cost | Notes |
|------|------|-------|
| **VPS** | $28-48 | Hetzner or DigitalOcean |
| **OpenAI API (embeddings)** | $2-5 | text-embedding-3-small, ~500 queries + incremental docs |
| **OpenAI API (LLM generation)** | $5-15 | GPT-4o-mini for query answering, ~500 queries |
| **OpenAI API (entity extraction)** | $5-15 | GPT-4o-mini for new research docs (~50-100/month) |
| **Cohere Reranker** | $0-8 | Free tier: 1000 calls/month, sufficient for this scale |
| **Neo4j** | $0 | Community Edition, self-hosted |
| **PostgreSQL** | $0 | Self-hosted, included in VPS |
| **Total** | **$40-90/month** | |

**One-time initial costs:**
- Initial document indexing (embeddings + entity extraction): $20-40
- Your time for setup: 2-3 weeks of part-time work

---

## Implementation Phases

### Phase 1: Foundation (Week 1)

**Goal:** PostgreSQL + pgvector running, Haystack indexing pipeline working

1. Provision VPS, install Docker
2. Deploy PostgreSQL with pgvector extension via Docker
3. Create database schemas (`haystack_docs`, `lightrag`)
4. Install Haystack: `pip install haystack-ai pgvector-haystack`
5. Build and test indexing pipeline with 5-10 sample project docs
6. Build and test query pipeline — verify hybrid search works
7. Validate with sample queries: "What does the PRD say about X?"

**Deliverable:** Working Haystack RAG for project docs, queryable via Python

### Phase 2: Haystack MCP (Week 1-2)

**Goal:** Claude Desktop can query project documentation

1. Install Hayhooks: `pip install hayhooks[mcp]`
2. Serialize query pipeline to YAML
3. Configure Hayhooks environment variables
4. Add `project-docs` server to `claude_desktop_config.json`
5. Test from Claude Desktop: "What are the API requirements for the payments service?"
6. Index all project documentation (full corpus)
7. Iterate on splitting strategy and retrieval params based on query quality

**Deliverable:** Claude can search project docs via MCP

### Phase 3: LightRAG Setup (Week 2)

**Goal:** LightRAG running with Neo4j, initial research docs indexed

1. Deploy Neo4j Community via Docker
2. Deploy LightRAG server via Docker (or pip install)
3. Configure `.env` with production storage backends (Neo4j + PostgreSQL)
4. Customize entity types with the domain-agnostic research set (12 types)
5. Index 10-20 sample research documents (mix of domains — some trading, some tech eval, some market research)
6. Test via LightRAG WebUI (http://localhost:9621):
   - Verify entities are extracted correctly across different research domains
   - Check knowledge graph visualization — do cross-domain connections appear?
   - Run sample queries in all modes (local, global, hybrid)
7. Tune entity extraction: review extracted entities, adjust prompts if needed

**Deliverable:** Working LightRAG with multi-domain entity extraction validated

### Phase 4: LightRAG MCP (Week 2-3)

**Goal:** Claude Desktop can query research knowledge base

1. Install daniel-lightrag-mcp
2. Add `research-kb` server to `claude_desktop_config.json`
3. Test from Claude Desktop across multiple domains:
   - "What did my PayPal earnings analysis conclude?"
   - "Which RAG frameworks did I evaluate that support graph storage?"
   - "What risks did I identify across all my regulatory research?"
   - "What entities connect my fintech analysis to my tech evaluations?"
4. Index full research corpus (batch by 30-50 docs)
5. Monitor indexing via `get_pipeline_status` and `get_document_status_counts`

**Deliverable:** Claude can search research KB via MCP, both services running

### Phase 5: Tuning and Evaluation (Week 3+)

**Goal:** Measure and improve retrieval quality

1. Create a test set of 30-50 queries with expected answers:
   - 15-20 project doc queries (factual, keyword-heavy)
   - 15-20 research queries (relational, thematic, cross-domain)
2. Measure retrieval quality:
   - Haystack: Use RAGAS integration (context precision, faithfulness, relevance)
   - LightRAG: Manual evaluation (compare local vs global vs hybrid mode quality)
3. Tune parameters:
   - Haystack: chunk size, overlap, top_k, reranker threshold
   - LightRAG: chunk size, query mode defaults, entity type prompts
4. Review Neo4j graph: Use Neo4j Browser (http://localhost:7474) to visually inspect entity relationships, find duplicates, verify extraction quality
5. Document what works and what doesn't for your specific content

**Deliverable:** Calibrated system with measured quality, known limitations documented

---

## Operational Procedures

### Adding New Project Documentation

```bash
# 1. Place file in input directory
cp new_prd.md /opt/haystack/input/

# 2. Trigger re-index (via script or MCP)
python scripts/reindex_haystack.py

# 3. Or ask Claude: "Index the new file new_prd.md into project docs"
```

### Adding New Research / Analysis

```bash
# Option A: Via Claude MCP
# Just tell Claude: "Add this analysis to the research KB"
# Then paste or reference the content

# Option B: Via REST API
curl -X POST http://localhost:9621/documents/upload \
  -F "files=@new_analysis.md" \
  -H "X-API-Key: lightragsecretkey"

# Option C: Drop in input directory
cp new_analysis.md /opt/lightrag/data/inputs/
# LightRAG processes new files on scan
```

### Monitoring

**LightRAG health check:**
```bash
curl http://localhost:9621/health
# Or via Claude: "Check research KB health"
```

**Neo4j status:**
```bash
# Open Neo4j Browser: http://localhost:7474
# Run: MATCH (n) RETURN count(n) as nodes
# Run: MATCH ()-[r]->() RETURN count(r) as relationships
```

**PostgreSQL status:**
```bash
psql -U raguser -d ragdb -c "
  SELECT schemaname, relname, n_live_tup
  FROM pg_stat_user_tables
  ORDER BY n_live_tup DESC;"
```

### Backup

```bash
# PostgreSQL
pg_dump -U raguser ragdb > backup_$(date +%Y%m%d).sql

# Neo4j
docker exec neo4j neo4j-admin database dump neo4j --to-path=/backups/
docker cp neo4j:/backups/ ./neo4j_backups/

# LightRAG working directory (KV cache, config)
tar czf lightrag_data_$(date +%Y%m%d).tar.gz /opt/lightrag/data/
```

---

## Risk Mitigation

### LightRAG Entity Extraction Quality

**Risk:** Hallucinated or missing entities across diverse research domains
**Mitigation:**
1. Start with 10-20 docs from different domains, manually review extracted entities in Neo4j Browser
2. Customize entity types before full corpus indexing — the 12-type research set covers most domains
3. Use GPT-4o (not mini) for initial indexing if budget allows — better extraction quality
4. After initial review, switch to GPT-4o-mini for incremental updates (cheaper, quality is acceptable for ongoing additions)

### LightRAG Server Stability

**Risk:** Server hangs during long indexing sessions
**Mitigation:**
1. Index in batches of 30-50 documents
2. Set `LLM_TIMEOUT=180` to prevent individual request hangs
3. Monitor with `get_pipeline_status` between batches
4. LightRAG tracks document status — restart-and-resume is safe

### Entity Deduplication Across Domains

**Risk:** Same entity extracted differently from different research contexts — "PayPal" vs "PYPL" vs "PayPal Holdings"; "LightRAG" vs "LightRAG framework" vs "HKUDS/LightRAG"
**Mitigation:**
1. Standardize naming in your markdown files (use consistent entity names across documents)
2. Review and manually merge entities in Neo4j if needed:
   ```cypher
   // Find potential duplicates
   MATCH (n) WHERE n.name CONTAINS 'PayPal' RETURN n.name, n.id
   MATCH (n) WHERE n.name CONTAINS 'LightRAG' RETURN n.name, n.id
   ```
3. Watch for LightRAG's entity merging feature (#1323) — active development

### Community MCP Server Maintenance

**Risk:** daniel-lightrag-mcp breaks after LightRAG API update
**Mitigation:**
1. Pin LightRAG version in Docker image tag
2. Fork daniel-lightrag-mcp to your own repo
3. Test after any LightRAG update before deploying
4. Fallback: LightRAG's REST API works directly — worst case, build a minimal MCP wrapper yourself

---

## Upgrade Path

Once this system is running and you've lived with it for 1-2 months, natural upgrade paths include:

1. **Direct Cypher queries** — Since LightRAG uses Neo4j under the hood, you can write Cypher queries directly against the same Neo4j instance for complex multi-hop patterns that LightRAG's built-in retrieval can't handle. No re-indexing needed.

2. **Haystack agent layer** — Add a Haystack `Agent` component that decides which service to query based on the question, rather than relying on Claude's routing.

3. **RAGAS automated evaluation** — Build a CI pipeline that runs evaluation queries after each batch of new documents, tracking retrieval quality over time.

4. **Local LLM for extraction** — If API costs become a concern, switch entity extraction to a local 32B+ model (e.g., Qwen3-30B via Ollama). Keep GPT-4o-mini for query-time generation where quality matters most.

5. **Domain-specific extraction profiles** — Create specialized entity type sets and extraction prompts per research domain (trading, tech, regulatory) and route documents to the appropriate profile during indexing. The graph stays unified — only the extraction prompt changes.

6. **Cross-KB queries** — If you find yourself needing queries that span both services ("find projects where the research findings influenced architecture decisions"), build a custom Haystack SuperComponent that queries both backends and synthesizes results.

7. **Multimodal image support (Haystack)** — Add image handling for architecture diagrams, UI mockups, and flowcharts embedded in documentation.

   **Native image capabilities:**
   - `Document` dataclass supports a `blob` field for binary data alongside text `content`
   - `MarkdownToDocument` handles inline images referenced in markdown
   - `PyPDFToDocument`, `HTMLToDocument` extract embedded images alongside text
   - `OpenAIChatGenerator` supports vision inputs for analysis, captioning, Q&A

   **Implementation approach — Caption-and-index (recommended):**
   ```
   Image Files (from /docs directory)
           │
           ▼
   ImageToDocument Converter (custom)
           │
           ▼
   VisionLLMCaptioner (custom component)
     • Sends image to GPT-4o-mini vision
     • Generates text description of diagram/screenshot
           │
           ▼
   OpenAIDocumentEmbedder
     • Embeds caption text
           │
           ▼
   DocumentWriter → PgvectorDocumentStore
     • Stores caption + metadata linking to source image
   ```

   **Custom component example (~50 lines):**
   ```python
   from haystack import component, Document
   from openai import OpenAI
   import base64

   @component
   class VisionLLMCaptioner:
       def __init__(self, model: str = "gpt-4o-mini"):
           self.client = OpenAI()
           self.model = model

       @component.output_types(documents=list[Document])
       def run(self, documents: list[Document]) -> dict:
           results = []
           for doc in documents:
               if doc.blob:
                   b64_image = base64.b64encode(doc.blob).decode()
                   response = self.client.chat.completions.create(
                       model=self.model,
                       messages=[{
                           "role": "user",
                           "content": [
                               {"type": "text", "text": "Describe this technical diagram in detail for searchability."},
                               {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64_image}"}}
                           ]
                       }],
                       max_tokens=500
                   )
                   caption = response.choices[0].message.content
                   results.append(Document(
                       content=caption,
                       meta={**doc.meta, "image_source": doc.meta.get("file_path"), "content_type": "image_caption"}
                   ))
           return {"documents": results}
   ```

   **Alternative — Multimodal embeddings (experimental):**
   - Use CLIP (`clip-vit`) to embed images directly into the same vector space as text
   - Haystack supports custom embedders
   - Less reliable for technical diagrams than caption-based approach

   **When to add this:**
   - After text-only pipeline is stable (Phase 5+)
   - When repeatedly needing to search architecture diagrams or screenshots
   - Estimated effort: 1-2 days for basic implementation

   **LightRAG multimodal note:** RAG-Anything integration (June 2025) handles PDFs with images, tables, equations. Less mature than text pipeline — evaluate after Haystack image support is working.