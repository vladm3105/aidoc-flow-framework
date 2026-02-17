# AI Agent RAG Usage Guide

Instructions for AI agents to effectively use RAG services when working with AI Dev Flow Framework projects.

---

## When to Use RAG

Query RAG services when you need to:

| Situation | Action |
|-----------|--------|
| Create a new SDD document | Query for upstream dependencies and patterns |
| Understand existing requirements | Search for specific document content |
| Check traceability | Find cross-references between layers |
| Validate consistency | Compare definitions across documents |
| Find implementation patterns | Search for similar prior work |
| Answer user questions about docs | Query relevant documentation |

**Do NOT use RAG when:**
- Reading a specific file the user mentioned (use Read tool)
- The information is in a file you already read
- Making simple code changes unrelated to documentation

---

## Service Selection

### Use Haystack (project-docs) for:

| Query Type | Examples |
|------------|----------|
| **Factual lookups** | "What is the API endpoint for authentication?" |
| **Specific documents** | "Show me PRD-001 requirements" |
| **Enumeration** | "List all REQ items with priority=critical" |
| **Exact terms** | "Find documents mentioning OAuth2" |
| **Traceability** | "What REQ items reference SYS-AUTH-001?" |
| **Validation rules** | "What are the BRD validation rules?" |

**Haystack Keywords**: what is, list, show, find, get, which, specific IDs (PRD-001, REQ-AUTH-001)

### Use LightRAG (research-kb) for:

| Query Type | Examples |
|------------|----------|
| **Relationships** | "How does authentication relate to authorization?" |
| **Patterns** | "What patterns appear across ADR documents?" |
| **Cross-document** | "How do ADR decisions affect downstream requirements?" |
| **Rationale** | "Why was OAuth2 chosen over SAML?" |
| **Themes** | "What security concerns are mentioned across layers?" |
| **Impact analysis** | "What depends on the user authentication module?" |

**LightRAG Keywords**: how does, relate, pattern, across, why, affect, depend, theme, impact

---

## Query Syntax

### Haystack Queries

```bash
# Basic query
curl -X POST http://localhost:1416/query \
  -H "Content-Type: application/json" \
  -d '{"query": "validation rules for BRD documents"}'

# With metadata filters
curl -X POST http://localhost:1416/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "authentication requirements",
    "filters": {
      "doc_type": {"$eq": "PRD"}
    }
  }'

# Filter by layer
curl -X POST http://localhost:1416/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "security requirements",
    "filters": {
      "layer": {"$in": [1, 2, 3]}
    }
  }'
```

### LightRAG Queries

```bash
# Basic query (hybrid mode recommended)
curl -X POST http://localhost:9621/query \
  -H "X-API-Key: lightragsecretkey" \
  -H "Content-Type: application/json" \
  -d '{"query": "How do ADR decisions affect implementation?", "mode": "hybrid"}'

# Local mode (entity-focused)
curl -X POST http://localhost:9621/query \
  -H "X-API-Key: lightragsecretkey" \
  -H "Content-Type: application/json" \
  -d '{"query": "What entities relate to OAuth2?", "mode": "local"}'

# Global mode (theme-focused)
curl -X POST http://localhost:9621/query \
  -H "X-API-Key: lightragsecretkey" \
  -H "Content-Type: application/json" \
  -d '{"query": "What security themes appear across documents?", "mode": "global"}'
```

---

## Layer Reference

When filtering by layer, use these mappings:

| Layer | Type | Content |
|-------|------|---------|
| 0 | REF | Reference documents, initial project documentation |
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

---

## Common Workflows

### 1. Creating a New Document

Before creating a document, query for context:

```
# Step 1: Get upstream requirements (Haystack)
Query: "What requirements exist in [upstream layer] for [topic]?"
Filter: {"layer": {"$eq": [upstream_layer_number]}}

# Step 2: Find related patterns (LightRAG)
Query: "What patterns were used for similar [document type] documents?"

# Step 3: Check for existing work (Haystack)
Query: "List existing [document type] documents for [topic]"
```

**Example - Creating PRD for auth module:**
```
1. Haystack: "What auth requirements exist in BRD?" filters={"layer": 1}
2. LightRAG: "What auth patterns appear in existing PRDs?"
3. Haystack: "List PRD documents mentioning authentication"
```

### 2. Reviewing a Document

```
# Check traceability (Haystack)
Query: "What upstream documents are referenced by [DOC-ID]?"
Query: "What downstream documents reference [DOC-ID]?"

# Check consistency (LightRAG)
Query: "How is [term] defined across all documents?"

# Find conflicts (Haystack)
Query: "[specific value or term]"
# Then compare results across documents
```

### 3. Impact Analysis

```
# Find dependencies (Haystack)
Query: "What documents reference [ID or term]?"
Filter: {"layer": {"$gte": [current_layer]}}  # downstream only

# Understand relationships (LightRAG)
Query: "What depends on [component/module]?"
Query: "What would be affected by changing [feature]?"
```

### 4. Answering User Questions

```
# For specific information
Use Haystack with relevant filters

# For understanding/rationale
Use LightRAG with hybrid mode

# For finding examples
Use Haystack: "Show examples of [pattern/structure]"
```

---

## Filter Operators

Haystack supports these filter operators:

| Operator | Description | Example |
|----------|-------------|---------|
| `$eq` | Equals | `{"doc_type": {"$eq": "PRD"}}` |
| `$ne` | Not equals | `{"status": {"$ne": "deprecated"}}` |
| `$in` | In list | `{"layer": {"$in": [1, 2, 3]}}` |
| `$nin` | Not in list | `{"doc_type": {"$nin": ["TEMPLATE"]}}` |
| `$gt` | Greater than | `{"layer": {"$gt": 5}}` |
| `$gte` | Greater or equal | `{"layer": {"$gte": 5}}` |
| `$lt` | Less than | `{"layer": {"$lt": 5}}` |
| `$lte` | Less or equal | `{"layer": {"$lte": 5}}` |
| `$and` | Logical AND | `{"$and": [{...}, {...}]}` |
| `$or` | Logical OR | `{"$or": [{...}, {...}]}` |

---

## Query Modes (LightRAG)

| Mode | Best For | Description |
|------|----------|-------------|
| `hybrid` | General queries | Combines local + global (recommended default) |
| `local` | Entity questions | Focuses on specific entities and their relationships |
| `global` | Theme questions | Focuses on high-level themes and patterns |
| `naive` | Simple search | Basic vector search without graph |

---

## Best Practices

### Do:

1. **Start with Haystack** for factual queries, switch to LightRAG if relationships matter
2. **Use specific filters** to narrow results and improve relevance
3. **Include document IDs** when you know them (e.g., "PRD-001", "REQ-AUTH-001")
4. **Query before creating** to find existing context and patterns
5. **Use hybrid mode** in LightRAG for most queries
6. **Check both services** when doing comprehensive research

### Don't:

1. **Don't query for files you can read directly** - use Read tool instead
2. **Don't make multiple queries** when one filtered query suffices
3. **Don't ignore the layer structure** - use it to narrow searches
4. **Don't query LightRAG for exact lookups** - Haystack is faster for these
5. **Don't assume results are complete** - RAG provides relevant excerpts, not full docs

---

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Connection refused | Services not running | Run `make rag-up` in framework_rags/ |
| Empty results | No matching documents | Broaden query or check if docs are indexed |
| Timeout | Large result set or complex query | Add filters to narrow scope |
| 401 Unauthorized | Missing API key (LightRAG) | Include X-API-Key header |

### Health Check

```bash
# Check if services are running
curl http://localhost:1416/health  # Haystack
curl http://localhost:9621/health  # LightRAG
```

---

## Integration with MCP

When RAG services are configured as MCP servers, use the provided tools:

### project-docs (Haystack) Tools:
- `search_docs` - Search with query and optional filters
- `get_document` - Retrieve specific document by ID
- `list_documents` - List documents with filters
- `query_requirements` - Specialized requirement queries

### research-kb (LightRAG) Tools:
- `query` - Query knowledge graph (specify mode)
- `search_entities` - Find specific entities
- `get_relationships` - Get entity relationships
- `analyze_patterns` - Pattern analysis across documents

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│                    RAG Query Decision Tree                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Need specific fact or document?                            │
│    YES → Haystack (port 1416)                               │
│    NO  ↓                                                    │
│                                                             │
│  Need relationships or patterns?                            │
│    YES → LightRAG (port 9621, mode: hybrid)                 │
│    NO  ↓                                                    │
│                                                             │
│  Need to understand rationale/themes?                       │
│    YES → LightRAG (port 9621, mode: global)                 │
│    NO  ↓                                                    │
│                                                             │
│  Need entity-specific information?                          │
│    YES → LightRAG (port 9621, mode: local)                  │
│    NO  → Try Haystack first, then LightRAG                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘

Common Filters:
  doc_type: REF|BRD|PRD|EARS|BDD|ADR|SYS|REQ|CTR|SPEC|TSPEC|TASKS|IPLAN
  layer: 0-12
  project_name: your-project-name
```

---

## Example Session

**User Request**: "Create a PRD for the new payment processing feature"

**Agent Actions**:

1. **Query existing BRD** (Haystack):
   ```
   Query: "payment processing requirements"
   Filter: {"doc_type": {"$eq": "BRD"}}
   ```
   → Returns BRD-003 payment requirements

2. **Check for related ADRs** (LightRAG):
   ```
   Query: "What architecture decisions relate to payments?"
   Mode: hybrid
   ```
   → Returns ADR-007 payment gateway selection

3. **Find similar PRDs** (Haystack):
   ```
   Query: "transaction processing PRD"
   Filter: {"doc_type": {"$eq": "PRD"}}
   ```
   → Returns PRD-002 as reference

4. **Create PRD** with gathered context

5. **Verify traceability** (Haystack):
   ```
   Query: "PRD-005"  # newly created
   ```
   → Confirm it references BRD-003 and ADR-007
