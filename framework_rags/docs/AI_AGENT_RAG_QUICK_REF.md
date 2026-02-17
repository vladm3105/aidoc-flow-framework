# RAG Quick Reference for AI Agents

## Service Selection

| Query Type | Service | Port |
|------------|---------|------|
| Factual, specific docs, IDs, lists | **Haystack** | 1416 |
| Relationships, patterns, rationale | **LightRAG** | 9621 |

## Haystack Examples

```bash
# Basic query
curl -X POST http://localhost:1416/query \
  -d '{"query": "authentication requirements"}'

# With filter
curl -X POST http://localhost:1416/query \
  -d '{"query": "auth requirements", "filters": {"doc_type": {"$eq": "PRD"}}}'
```

**Filters**: `doc_type`, `layer` (0-12), `project_name`
**Operators**: `$eq`, `$in`, `$gt`, `$gte`, `$lt`, `$lte`, `$and`, `$or`

## LightRAG Examples

```bash
# Hybrid mode (recommended)
curl -X POST http://localhost:9621/query \
  -H "X-API-Key: lightragsecretkey" \
  -d '{"query": "How do ADRs affect implementation?", "mode": "hybrid"}'
```

**Modes**: `hybrid` (default), `local` (entities), `global` (themes)

## Layer Reference

| Layer | Type | Layer | Type |
|-------|------|-------|------|
| 0 | REF | 7 | REQ |
| 1 | BRD | 8 | CTR |
| 2 | PRD | 9 | SPEC |
| 3 | EARS | 10 | TSPEC |
| 4 | BDD | 11 | TASKS |
| 5 | ADR | 12 | IPLAN |
| 6 | SYS | | |

## When to Query

- **Before creating docs**: Get upstream context
- **During review**: Check traceability
- **Impact analysis**: Find dependencies
- **User questions**: Search documentation

## Decision Tree

```
Specific fact/doc? → Haystack
Relationships?     → LightRAG (hybrid)
Themes/rationale?  → LightRAG (global)
Entity details?    → LightRAG (local)
```
