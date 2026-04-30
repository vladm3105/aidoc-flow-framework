# RAG Services for AI Dev Flow Framework

## Why RAG for Documentation?

The AI Dev Flow Framework generates extensive documentation across 13 layers (REF → TASKS). As projects grow, this creates challenges:

| Challenge | Impact |
|-----------|--------|
| **Document Volume** | 50-200+ markdown files per project |
| **Cross-References** | Requirements trace through 13 layers |
| **Knowledge Discovery** | Finding specific requirements buried in documents |
| **Pattern Recognition** | Identifying themes across architecture decisions |
| **Context Switching** | AI agents lose context between sessions |

RAG (Retrieval-Augmented Generation) solves these by providing instant, accurate retrieval from the entire documentation corpus.

---

## Two-Service Architecture

We deploy two purpose-built RAG services because documentation has fundamentally different retrieval patterns:

### Service 1: Haystack (Project Documentation)

**What it handles:**
- **REF documents** (Layer 0): Initial project documentation, business requirements, reference materials
- PRD, BRD, SPEC, REQ, TASKS documents (Layers 1-11)
- API specifications and contracts
- Architecture decision records
- Technical specifications

**Why Haystack:**
- **Hybrid search** (BM25 + Vector) catches exact technical terms
- "OAuth2", "HMAC-SHA256", "idempotency" need lexical matching
- Structured documents benefit from metadata filtering
- Fast retrieval for factual queries

**Example queries:**
```
"What are the validation rules for BRD documents?"
"Show me authentication requirements from PRD-001"
"List all REQ items with priority=critical"
```

### Service 2: LightRAG (Research & Analysis)

**What it handles:**
- Framework evaluation documents
- Technology research and comparisons
- Design rationale and trade-off analyses
- Cross-cutting concerns and patterns

**Why LightRAG:**
- **Knowledge graph** captures entity relationships
- Discovers connections across documents
- Answers relational and thematic queries
- Supports multi-hop reasoning

**Example queries:**
```
"How do ADR decisions affect downstream requirements?"
"What patterns appear across all EARS documents?"
"Which technologies are referenced in multiple layers?"
```

---

## SDD Layer Structure

The framework supports 13 documentation layers, indexed by Haystack:

| Layer | Type | Description |
|-------|------|-------------|
| 0 | REF | Reference documents, initial project documentation, business context |
| 1 | BRD | Business Requirements Documents |
| 2 | PRD | Product Requirements Documents |
| 3 | EARS | Easy Approach to Requirements Syntax |
| 4 | BDD | Behavior-Driven Development scenarios |
| 5 | ADR | Architecture Decision Records |
| 6 | SYS | System Requirements |
| 7 | REQ | Atomic Requirements |
| 8 | CTR | Data Contracts |
| 9 | SPEC | Technical Specifications |
| 10 | TSPEC | Test Specifications |
| 11 | TASKS | Task Breakdown |
| 12 | IPLAN | Implementation Plans |

REF documents (Layer 0) serve as the foundation - containing initial project documentation, business requirements, and reference materials that inform all downstream artifacts.

---

## Integration with AI Dev Flow

### Document Generation Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Agent Session                          │
│                                                             │
│  1. Agent receives task: "Create PRD for auth module"       │
│                          │                                  │
│  2. Query Haystack: ─────┴──────────────────────┐           │
│     "What auth requirements exist in BRD-001?"  │           │
│                                                 ▼           │
│                                    ┌────────────────────┐   │
│                                    │  Haystack RAG      │   │
│                                    │  Returns: BRD-001  │   │
│                                    │  auth sections     │   │
│                                    └────────────────────┘   │
│                          │                                  │
│  3. Query LightRAG: ─────┴──────────────────────┐           │
│     "What auth patterns were used before?"      │           │
│                                                 ▼           │
│                                    ┌────────────────────┐   │
│                                    │  LightRAG          │   │
│                                    │  Returns: Related  │   │
│                                    │  ADRs, prior PRDs  │   │
│                                    └────────────────────┘   │
│                          │                                  │
│  4. Generate PRD with full context                          │
└─────────────────────────────────────────────────────────────┘
```

### Traceability Verification

RAG enables automated traceability checking:

```python
# Example: Verify all REQ items trace to SYS requirements
query = "List REQ items that reference SYS-AUTH-001"
results = haystack.query(query, filters={"doc_type": "REQ"})

# Check coverage
if len(results) < expected_count:
    print("Missing traceability links detected")
```

### Cross-Document Validation

```python
# Example: Find inconsistencies across layers
query = "Authentication timeout values across all documents"
results = haystack.query(query)

# Compare values for consistency
timeouts = extract_timeout_values(results)
if len(set(timeouts)) > 1:
    print(f"Inconsistent timeout values: {timeouts}")
```

---

## Use Cases

### 1. Document Creation

| Task | RAG Query | Service |
|------|-----------|---------|
| Create BRD | "What business context exists in REF documents?" | Haystack |
| Create PRD | "What requirements exist in upstream BRD?" | Haystack |
| Create ADR | "What technology decisions were made in similar projects?" | LightRAG |
| Create SPEC | "What interfaces are defined in CTR documents?" | Haystack |
| Create TASKS | "What implementation patterns work for this type of feature?" | LightRAG |

### 2. Review & Validation

| Task | RAG Query | Service |
|------|-----------|---------|
| Check completeness | "List all PRD requirements not traced to SPEC" | Haystack |
| Find conflicts | "Requirements mentioning authentication across all layers" | Haystack |
| Verify consistency | "How is 'user session' defined across documents?" | LightRAG |

### 3. Impact Analysis

| Task | RAG Query | Service |
|------|-----------|---------|
| Change impact | "What documents reference REQ-AUTH-001?" | Haystack |
| Dependency analysis | "What depends on the authentication module?" | LightRAG |
| Risk assessment | "What risks were identified for auth features?" | LightRAG |

### 4. Knowledge Discovery

| Task | RAG Query | Service |
|------|-----------|---------|
| Find examples | "Show examples of well-structured BDD scenarios" | Haystack |
| Learn patterns | "What patterns appear in successful implementations?" | LightRAG |
| Understand rationale | "Why was OAuth2 chosen over SAML?" | LightRAG |

---

## Benefits

### For AI Agents

| Benefit | Description |
|---------|-------------|
| **Persistent Memory** | Access all prior documentation across sessions |
| **Accurate Context** | Retrieve exact requirements, not hallucinated ones |
| **Faster Generation** | Don't re-read entire documents each time |
| **Better Traceability** | Automatic cross-reference discovery |

### For Developers

| Benefit | Description |
|---------|-------------|
| **Quick Answers** | Find specific requirements in seconds |
| **Impact Analysis** | Understand change consequences |
| **Onboarding** | New team members query existing decisions |
| **Audit Trail** | All documentation searchable and traceable |

### For Project Quality

| Benefit | Description |
|---------|-------------|
| **Consistency** | Detect conflicting requirements across layers |
| **Completeness** | Find missing traceability links |
| **Reusability** | Discover patterns from prior work |
| **Compliance** | Verify all requirements are addressed |

---

## Query Routing

The `query_router.py` tool automatically directs queries to the appropriate service:

| Query Pattern | Routed To | Reason |
|---------------|-----------|--------|
| "What is..." | Haystack | Factual lookup |
| "List the..." | Haystack | Enumeration |
| "Show PRD-001..." | Haystack | Specific document |
| "How does X relate to Y?" | LightRAG | Relationship |
| "What patterns..." | LightRAG | Thematic analysis |
| "Across all documents..." | LightRAG | Cross-document |

---

## Metadata Filtering

Haystack supports powerful filters for precise retrieval:

```python
# Filter by document type
filters = {"doc_type": {"$eq": "PRD"}}

# Filter by SDD layer (Layer 0 = REF reference documents)
filters = {"layer": {"$in": [0, 1, 2]}}  # REF, BRD, PRD only

# Filter by project
filters = {"project_name": {"$eq": "auth-module"}}

# Combined filters
filters = {
    "$and": [
        {"doc_type": {"$eq": "REQ"}},
        {"layer": {"$eq": 7}},
        {"status": {"$eq": "approved"}}
    ]
}
```

---

## Entity Types (LightRAG)

LightRAG extracts 12 domain-agnostic entity types:

| Entity Type | Examples in Framework Context |
|-------------|------------------------------|
| organization | Teams, external vendors, stakeholders |
| person | Authors, reviewers, domain experts |
| product | Modules, services, components |
| technology | Frameworks, languages, protocols |
| concept | Patterns, methodologies, approaches |
| metric | KPIs, thresholds, SLAs |
| event | Releases, reviews, milestones |
| decision | ADR choices, trade-offs |
| finding | Review outcomes, validations |
| risk | Identified concerns, mitigations |
| regulation | Compliance requirements, standards |
| market_segment | User segments, deployment targets |

---

## Cost Considerations

### One-Time Indexing

| Corpus Size | Haystack Cost | LightRAG Cost |
|-------------|---------------|---------------|
| 100 docs | $2-5 | $15-30 |
| 500 docs | $10-25 | $75-150 |
| 1000 docs | $20-50 | $150-300 |

*LightRAG is higher due to LLM-based entity extraction*

### Ongoing Usage

| Activity | Monthly Cost |
|----------|--------------|
| Embeddings (queries) | $2-5 |
| LLM generation | $5-15 |
| New doc indexing | $0.10-0.20/doc |

---

## Getting Started

### 1. Configure Environment

```bash
cd /opt/data/ucx_framework/framework_rags
make setup          # Create .env

# Edit .env with:
#   PROJECT_ROOT=/path/to/your/project
#   OPENAI_API_KEY=sk-your-key-here
```

### 2. Initialize Data Directories

```bash
make init-data-dirs  # Creates ${PROJECT_ROOT}/tools/data/
```

Data is stored in your project directory:
```
${PROJECT_ROOT}/
└── tools/
    └── data/
        ├── postgres/      # Vector storage
        ├── neo4j/         # Graph storage
        ├── haystack/      # Indexes
        ├── lightrag/      # LightRAG data
        └── backups/       # Backups
```

### 3. Start Services

```bash
make rag-build      # Build containers
make rag-up         # Start services
```

### 4. Index Documentation

```bash
make rag-index          # Index framework docs (ai_dev_ssd_flow/)
make rag-index-project  # Index project docs from PROJECT_ROOT
```

### 3. Query via CLI

```bash
# Health check
python rag_tools/health_monitor.py

# Route and execute query
python rag_tools/query_router.py "What validation rules exist for BRD?"

# Scan documents by layer
python rag_tools/doc_scanner.py --source ../ai_dev_flow --layer 2
```

### 4. Integrate with MCP

```bash
# Generate Claude Desktop config
python rag_tools/mcp_config_generator.py > ~/.config/claude/claude_desktop_config.json
```

---

## Architecture Reference

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed technical specifications including:
- Pipeline configurations
- Database schemas
- Entity extraction prompts
- Upgrade paths
- Risk mitigations
