# Trading RAG Module v2.0

Retrieval-Augmented Generation (RAG) system for trading knowledge. Embeds documents into PostgreSQL with pgvector for semantic search, with advanced features including cross-encoder reranking, query expansion, adaptive retrieval routing, and RAGAS evaluation.

## What's New in v2.0

| Feature | Description | Impact |
|---------|-------------|--------|
| **Optimized Chunking** | 768 tokens, 150 overlap (vs 1500/50) | 15-25% accuracy gain |
| **Cross-Encoder Reranking** | Two-stage retrieve-then-rerank | Higher relevance |
| **Query Expansion** | LLM-based semantic variations | Improved recall |
| **Adaptive Retrieval** | Query classification for routing | Optimal strategy per query |
| **RAGAS Evaluation** | Quality metrics for RAG responses | Measurable improvements |
| **Semantic Chunking** | Embedding-based document splitting | Coherent chunks |
| **Metrics Infrastructure** | Search logging and analysis | Before/after comparison |

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         RAG Pipeline v2.0                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Document Input                                                             │
│       │                                                                     │
│       ▼                                                                     │
│  ┌─────────┐    ┌──────────────┐    ┌──────────┐    ┌───────────┐          │
│  │  Parse  │───▶│    Chunk     │───▶│  Embed   │───▶│   Store   │          │
│  │  YAML   │    │ (768 tokens) │    │ (OpenAI) │    │ (pgvector)│          │
│  └─────────┘    └──────────────┘    └──────────┘    └───────────┘          │
│                        │                                                    │
│                        ▼                                                    │
│                 ┌──────────────┐                                            │
│                 │   Semantic   │  (experimental)                            │
│                 │   Chunking   │                                            │
│                 └──────────────┘                                            │
│                                                                             │
│  Query Input                                                                │
│       │                                                                     │
│       ▼                                                                     │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────┐                      │
│  │ Classify │───▶│   Expand     │───▶│    Route     │                      │
│  │  Query   │    │   Query      │    │  (adaptive)  │                      │
│  └──────────┘    └──────────────┘    └──────────────┘                      │
│       │                                    │                                │
│       │     ┌──────────────────────────────┤                                │
│       │     │              │               │                                │
│       ▼     ▼              ▼               ▼                                │
│  ┌─────────────┐   ┌────────────┐   ┌────────────┐                         │
│  │   Vector    │   │   Hybrid   │   │   Graph    │                         │
│  │   Search    │   │   Search   │   │   Search   │                         │
│  └─────────────┘   └────────────┘   └────────────┘                         │
│            │              │               │                                 │
│            └──────────────┴───────────────┘                                 │
│                           │                                                 │
│                           ▼                                                 │
│                    ┌──────────────┐    ┌──────────────┐                     │
│                    │   Rerank     │───▶│   Return     │                     │
│                    │ (CrossEnc)   │    │   Context    │                     │
│                    └──────────────┘    └──────────────┘                     │
│                                               │                             │
│                                               ▼                             │
│                                        ┌──────────────┐                     │
│                                        │   RAGAS      │                     │
│                                        │   Evaluate   │                     │
│                                        └──────────────┘                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Quick Start

```python
from rag.embed import embed_document
from rag.search import semantic_search, get_rag_stats, search_with_rerank

# Check RAG statistics
stats = get_rag_stats()
print(f"Documents: {stats.document_count}, Chunks: {stats.chunk_count}")
print(f"Tickers: {stats.tickers}")
print(f"Doc types: {stats.doc_types}")

# Embed a document
result = embed_document("tradegent_knowledge/knowledge/analysis/stock/NVDA_20250120.yaml")
print(f"doc_id: {result.doc_id}")
print(f"chunk_count: {result.chunk_count}")
print(f"status: {result.error_message or 'success'}")  # 'unchanged' if already exists

# Basic search
results = semantic_search(
    query="NVDA competitive advantages",
    ticker="NVDA",
    top_k=5,
)
for r in results:
    print(f"{r.score:.3f} | {r.doc_id} | {r.content[:80]}...")

# Reranked search (higher relevance)
results = search_with_rerank(
    query="NVDA competitive advantages",
    ticker="NVDA",
    top_k=5,
)
for r in results:
    print(f"{r.similarity:.3f} | rerank: {r.rerank_score:.3f} | {r.content[:80]}...")
```

**EmbedResult attributes:**
- `doc_id` - Document identifier
- `file_path` - Source file path
- `doc_type` - Document type (stock-analysis, earnings-analysis, etc.)
- `ticker` - Ticker symbol (if applicable)
- `chunk_count` - Number of chunks created
- `embed_model` - Embedding model used
- `error_message` - Error or "unchanged" if already embedded

**RAGStats attributes:**
- `document_count` - Total documents
- `chunk_count` - Total chunks
- `embed_model` - Current embedding model
- `tickers` - List of indexed tickers
- `doc_types` - Dict of document type counts
- `last_embed` - Timestamp of last embedding

## Components

### Core Modules

| File | Purpose |
|------|---------|
| `mcp_server.py` | **MCP server (primary interface)** - 12 tools |
| `embed.py` | Document embedding pipeline |
| `search.py` | Semantic, hybrid, reranked search |
| `chunk.py` | Text chunking with configurable parameters |
| `embedding_client.py` | Embedding client (OpenAI/Ollama) |
| `schema.py` | PostgreSQL schema management |
| `models.py` | Data classes (EmbedResult, SearchResult, HybridContext) |
| `hybrid.py` | Combined vector + graph context with adaptive routing |
| `config.yaml` | Configuration settings (v2.0.0) |

### v2.0 Modules

| File | Purpose |
|------|---------|
| `metrics.py` | Search metrics collection and analysis |
| `rerank.py` | Cross-encoder reranking (ms-marco-MiniLM-L-6-v2) |
| `query_classifier.py` | Rule-based query classification |
| `query_expander.py` | LLM-based query expansion |
| `evaluation.py` | RAGAS evaluation framework |
| `semantic_chunker.py` | Embedding-based semantic chunking |
| `tokens.py` | Token counting utilities |

## Configuration

### config.yaml (v2.0.0)

```yaml
# Feature flags
features:
  metrics_enabled: true          # Log search metrics
  element_aware_chunking: true   # Section-aware chunking
  preserve_tables: true          # Keep tables atomic
  reranking_enabled: true        # Cross-encoder reranking
  adaptive_retrieval: true       # Query-based routing
  query_expansion_enabled: true  # LLM query expansion
  semantic_chunking: false       # Experimental

# Optimized chunking (research-backed)
chunking:
  max_tokens: 768      # Was 1500 (arXiv 2402.05131 recommends 512-1024)
  min_tokens: 50
  overlap_tokens: 150  # Was 50 (100-300 optimal)

# Semantic chunking (experimental)
semantic_chunking:
  similarity_threshold: 0.8  # Split below this similarity
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://...` | PostgreSQL connection |
| `RAG_SCHEMA` | `nexus` | Database schema name |
| `EMBED_PROVIDER` | `openai` | Embedding provider |
| `OPENAI_API_KEY` | (none) | API key for embeddings |
| `CHUNK_MAX_TOKENS` | `768` | Max tokens per chunk |
| `CHUNK_OVERLAP` | `150` | Overlap tokens |

### Embedding Provider

| Provider | Model | Dimensions | Cost |
|----------|-------|------------|------|
| `openai` | text-embedding-3-large | 1536* | $0.13/1M tokens |

*Uses API-level dimension truncation (pgvector HNSW limit: 2000 dims)

**Cost estimate:** ~$2/year for 7,500 documents

## MCP Tools (12 total)

### Core Tools (6)

| Tool | Description |
|------|-------------|
| `rag_embed` | Embed a YAML document |
| `rag_embed_text` | Embed raw text |
| `rag_search` | Semantic search |
| `rag_similar` | Find similar analyses for ticker |
| `rag_hybrid_context` | Combined vector + graph context (adaptive) |
| `rag_status` | Get RAG statistics |

### v2.0 Tools (6)

| Tool | Description |
|------|-------------|
| `rag_search_rerank` | Search with cross-encoder reranking |
| `rag_search_expanded` | Search with query expansion |
| `rag_classify_query` | Classify query type and strategy |
| `rag_expand_query` | Generate semantic query variations |
| `rag_evaluate` | Evaluate RAG quality (RAGAS) |
| `rag_metrics_summary` | Get search metrics summary |

### MCP Usage Examples

```yaml
# Standard search
Tool: rag_search
Input: {"query": "NVDA earnings catalyst", "ticker": "NVDA", "top_k": 5}

# Reranked search (higher relevance)
Tool: rag_search_rerank
Input: {"query": "semiconductor supply chain risks", "ticker": "NVDA", "top_k": 5}

# Expanded search (better recall)
Tool: rag_search_expanded
Input: {"query": "AI demand drivers", "top_k": 5, "n_expansions": 3}

# Classify query for optimal strategy
Tool: rag_classify_query
Input: {"query": "Compare NVDA vs AMD competitive position"}
# Returns: {query_type: "comparison", suggested_strategy: "vector", tickers: ["NVDA", "AMD"]}

# Get hybrid context (uses adaptive routing)
Tool: rag_hybrid_context
Input: {"ticker": "NVDA", "query": "earnings analysis"}

# Evaluate RAG quality
Tool: rag_evaluate
Input: {
  "query": "What are NVDA risks?",
  "contexts": ["Context chunk 1...", "Context chunk 2..."],
  "answer": "Generated answer...",
  "ground_truth": "Optional reference answer..."
}
# Returns: {context_precision: 0.85, faithfulness: 0.92, ...}

# Get metrics summary
Tool: rag_metrics_summary
Input: {"days": 7}
```

## Search Functions

### semantic_search(query, ...)

Basic vector similarity search.

```python
from rag.search import semantic_search

results = semantic_search(
    query="semiconductor supply chain risks",
    ticker="NVDA",           # optional filter
    doc_type="research",     # optional filter
    top_k=5,
    min_similarity=0.3,
)
```

### hybrid_search(query, ...)

Combined BM25 + vector search using Reciprocal Rank Fusion.

```python
from rag.search import hybrid_search

results = hybrid_search(
    query="earnings volatility play",
    ticker="NVDA",
    vector_weight=0.7,
    bm25_weight=0.3,
    top_k=5,
)
```

### search_with_rerank(query, ...) [v2.0]

Two-stage retrieve-then-rerank for higher relevance.

```python
from rag.search import search_with_rerank

results = search_with_rerank(
    query="NVDA competitive position vs AMD",
    ticker="NVDA",
    top_k=5,           # Final results
    retrieval_k=50,    # Initial retrieval pool
    use_hybrid=True,   # Use hybrid search for stage 1
)

for r in results:
    print(f"Vector: {r.similarity:.3f} | Rerank: {r.rerank_score:.3f}")
```

### search_with_expansion(query, ...) [v2.0]

Search with LLM-generated query variations for better recall.

```python
from rag.search import search_with_expansion

results = search_with_expansion(
    query="AI chip demand",
    ticker="NVDA",
    top_k=5,
    n_expansions=3,  # Generate 3 variations
)
# Searches: "AI chip demand", "artificial intelligence semiconductor requirements", ...
```

## Query Classification [v2.0]

Classifies queries to determine optimal retrieval strategy.

```python
from rag.query_classifier import classify_query, QueryType

analysis = classify_query("Compare NVDA vs AMD earnings")
print(f"Type: {analysis.query_type}")           # QueryType.COMPARISON
print(f"Strategy: {analysis.suggested_strategy}") # "vector"
print(f"Tickers: {analysis.tickers}")           # ["NVDA", "AMD"]
print(f"Confidence: {analysis.confidence}")     # 0.9
```

### Query Types

| Type | Pattern | Strategy |
|------|---------|----------|
| `RETRIEVAL` | Standard fact-seeking | vector |
| `RELATIONSHIP` | "related to", "connected", "impact" | graph |
| `TREND` | "recent", "last week", time-based | vector + time filter |
| `COMPARISON` | "vs", "compare", multiple tickers | vector (multi-ticker) |
| `GLOBAL` | Broad, no specific ticker | hybrid |

## Adaptive Retrieval [v2.0]

`rag_hybrid_context` uses query classification to route to optimal strategy.

```python
from rag.hybrid import get_hybrid_context_adaptive

context = get_hybrid_context_adaptive(
    ticker="NVDA",
    query="How does NVDA relate to AMD?",
    analysis_type="stock",
)
# Uses graph-first retrieval for RELATIONSHIP queries
```

**Routing Logic:**
- **RELATIONSHIP** → Graph-first: search primary ticker + graph peers
- **COMPARISON** → Multi-ticker: search each mentioned ticker
- **TREND** → Time-filtered: apply date range from query
- **Default** → Reranked search with hybrid retrieval

## Cross-Encoder Reranking [v2.0]

Two-stage pipeline for higher relevance:

1. **Stage 1**: Fast retrieval (vector or hybrid) - get top 50 candidates
2. **Stage 2**: Cross-encoder reranking - score all 50, return top 5

```python
from rag.rerank import get_reranker

reranker = get_reranker()
# Uses: cross-encoder/ms-marco-MiniLM-L-6-v2

# Rerank candidates
reranked = reranker.rerank(query, candidates, top_k=5)
```

**Graceful fallback:** If sentence-transformers unavailable, uses NoOpReranker.

## Query Expansion [v2.0]

LLM-based semantic variations for improved recall.

```python
from rag.query_expander import expand_query

expanded = expand_query("AI chip demand", n=3)
print(expanded.original)     # "AI chip demand"
print(expanded.variations)   # ["artificial intelligence semiconductor requirements", ...]
print(expanded.all_queries)  # [original + variations]
```

**Uses:** gpt-4o-mini for fast, cheap expansion (~$0.001 per query)

## RAGAS Evaluation [v2.0]

Measure RAG quality using RAGAS metrics.

```python
from rag.evaluation import evaluate_rag, is_ragas_available

if is_ragas_available():
    result = evaluate_rag(
        query="What are NVDA's main risks?",
        contexts=["Context 1...", "Context 2..."],
        answer="Generated answer...",
        ground_truth="Optional reference...",  # optional
    )
    print(f"Context Precision: {result.context_precision}")
    print(f"Context Recall: {result.context_recall}")
    print(f"Faithfulness: {result.faithfulness}")
    print(f"Answer Relevancy: {result.answer_relevancy}")
    print(f"Overall Score: {result.overall_score}")
```

**Metrics:**
| Metric | Description |
|--------|-------------|
| `context_precision` | Ranking quality of retrieved context |
| `context_recall` | Coverage of relevant information |
| `faithfulness` | Factual accuracy (grounded in context) |
| `answer_relevancy` | How well answer addresses query |

**Requires:** `pip install ragas datasets`

## Semantic Chunking [v2.0 Experimental]

Embedding-based chunking for semantic coherence.

```python
from rag.semantic_chunker import semantic_chunk

chunks = semantic_chunk(text)
for chunk in chunks:
    print(f"Tokens: {chunk.tokens}, Sentences: {chunk.sentence_count}")
```

**Algorithm:**
1. Split text into sentences
2. Get embeddings for each sentence
3. Calculate cosine similarity between adjacent sentences
4. Split where similarity drops below threshold (default: 0.8)
5. Respect max_tokens constraint

**Enable:** Set `semantic_chunking: true` in config.yaml

## Metrics Infrastructure [v2.0]

Track search performance for before/after comparison.

```python
from rag.metrics import get_metrics_collector

collector = get_metrics_collector()

# Get summary
summary = collector.get_summary(days=7)
print(f"Total searches: {summary.total_searches}")
print(f"Avg latency: {summary.avg_latency_ms}ms")
print(f"Avg top similarity: {summary.avg_top_similarity}")
print(f"Rerank rate: {summary.rerank_rate}")
print(f"Strategy distribution: {summary.strategy_distribution}")
```

**Logs to:** `logs/rag_metrics.jsonl`

## Database Schema

```sql
-- Documents table
nexus.rag_documents (
    id SERIAL PRIMARY KEY,
    doc_id VARCHAR(255) UNIQUE,
    file_path TEXT,
    doc_type VARCHAR(50),
    ticker VARCHAR(10),
    doc_date DATE,
    chunk_count INT,
    embed_model VARCHAR(100),
    embed_version VARCHAR(20),
    chunk_version VARCHAR(10),  -- v2.0: track chunk params
    tags TEXT[]
)

-- Chunks table (with embeddings)
nexus.rag_chunks (
    id SERIAL PRIMARY KEY,
    doc_id INT REFERENCES rag_documents(id),
    section_path TEXT,
    section_label VARCHAR(255),
    chunk_index INT,
    content TEXT,
    content_tokens INT,
    embedding vector(1536),     -- OpenAI text-embedding-3-large
    content_tsv tsvector,       -- BM25 full-text search
    ticker VARCHAR(10),
    doc_type VARCHAR(50),
    doc_date DATE
)
```

## Testing

```bash
cd tradegent

# Run RAG tests
pytest rag/tests/ -v

# Test reranking
python -c "
from rag.search import search_with_rerank
results = search_with_rerank('NVDA competitive position', ticker='NVDA', top_k=3)
for r in results:
    print(f'{r.similarity:.2f} | {r.rerank_score:.2f} | {r.section_label}')
"

# Test query classification
python -c "
from rag.query_classifier import classify_query
print(classify_query('What are NVDA risks?'))
print(classify_query('Compare NVDA vs AMD'))
print(classify_query('Recent earnings surprises'))
"

# Test query expansion
python -c "
from rag.query_expander import expand_query
expanded = expand_query('AI chip demand', n=3)
print('Original:', expanded.original)
print('Variations:', expanded.variations)
"

# Test metrics
python -c "
from rag.metrics import get_metrics_collector
summary = get_metrics_collector().get_summary(days=7)
print(f'Searches: {summary.total_searches}, Avg latency: {summary.avg_latency_ms}ms')
"
```

## Troubleshooting

**"Reranker not available"**
- Install sentence-transformers: `pip install sentence-transformers`
- Falls back to NoOpReranker (no reranking)

**"Query expansion failed"**
- Check OPENAI_API_KEY is set
- Verify gpt-4o-mini access
- Falls back to original query only

**"RAGAS not available"**
- Install: `pip install ragas datasets`
- Returns None if unavailable

**"Empty search results"**
- Verify embeddings stored: `SELECT COUNT(*) FROM nexus.rag_chunks`
- Lower `min_similarity` threshold
- Try hybrid search with BM25

**"Slow embedding"**
- Check EMBED_PROVIDER=openai (faster than ollama)
- Verify API key valid

## Migration from v1.0

1. **Update config.yaml** to v2.0.0 format
2. **Re-embed documents** with new chunk parameters:
   ```bash
   python orchestrator.py rag reembed --version 2.0
   ```
3. **Enable features** incrementally via feature flags
4. **Monitor metrics** to compare before/after

## Feature Flags

All v2.0 features can be toggled via config.yaml or environment:

```bash
# Disable reranking
export RAG_RERANKING=false

# Disable adaptive retrieval
export RAG_ADAPTIVE=false

# Revert to old chunk sizes
export CHUNK_MAX_TOKENS=1500
export CHUNK_OVERLAP=50
```
