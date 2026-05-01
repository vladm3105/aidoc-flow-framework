# IPLAN-005 — Project Knowledge Tools Separation

## 1) Scope

Implement a standalone knowledge subsystem (RAG + Graph) outside Tradegent, located under `/opt/data/ucx_framework/ucx_knowledge`, with Tradegent consuming the subsystem through MCP/API contracts and temporary compatibility adapters.

## 2) Objectives

- Separate RAG and Graph from Tradegent internals.
- Generalize data model from trading-specific to project-knowledge-specific.
- Preserve current Tradegent behavior during migration.
- Add migration/backfill path and rollout controls.
- Respect repository constraint: `/opt/data/tradegent_swarm` is read-only in this workspace.
- Keep implementation simple: `ucx_knowledge` is primary and does not depend on `framework_rags` runtime services for initial rollout.
- Reuse and adapt `/opt/data/ucx_framework/framework_rags/rag_tools` utilities for `ucx_knowledge` where useful.

## 3) Target Architecture

- New core package boundary: `ucx_knowledge` (library/service layer).
- RAG module: vector storage/retrieval (PostgreSQL + pgvector).
- Graph module: entity/relation extraction + traversal (Neo4j).
- MCP layer: stable tool contracts for embedding, extraction, search, hybrid context, status.
- Tradegent integration: compatibility adapters calling `ucx_knowledge` interfaces.
- Primary path: extract and generalize production-ready internals from Tradegent into `ucx_knowledge`.

## 4) Implementation Phases

### Phase 0 — Tooling Reuse Review

1. Inventory reusable scripts in `/opt/data/ucx_framework/framework_rags/rag_tools`.
2. Select utilities to adapt into `ucx_knowledge/rag_tools`:
   - `query_router.py`
   - `doc_scanner.py`
   - `batch_indexer.py`
   - `health_monitor.py`
3. Adjust selected utilities to call `ucx_knowledge` contracts (not framework service endpoints).

**Acceptance**
- Reuse list is documented.
- Adapted tools run against `ucx_knowledge` interfaces.

### 4.1) Current Execution Status (2026-02-22)

- Completed:
   - Scope and contract direction approved
   - Separation architecture approved
   - Independent destination selected: `/opt/data/ucx_framework/ucx_knowledge`
   - Initial skeleton created:
      - `/opt/data/ucx_framework/ucx_knowledge/rag/`
      - `/opt/data/ucx_framework/ucx_knowledge/graph/`
      - `/opt/data/ucx_framework/ucx_knowledge/mcp/`
      - `/opt/data/ucx_framework/ucx_knowledge/tests/`
   - M1 metadata/contracts implemented:
      - `/opt/data/ucx_framework/ucx_knowledge/models/metadata.py`
      - `/opt/data/ucx_framework/ucx_knowledge/models/contracts.py`
      - `/opt/data/ucx_framework/ucx_knowledge/mappings/legacy_tradegent_map.yaml`
   - `rag_tools` reused and adapted in:
      - `/opt/data/ucx_framework/ucx_knowledge/rag_tools/`
   - Unified MCP server implemented:
      - `/opt/data/ucx_framework/ucx_knowledge/mcp/server.py`
   - Ingestion/backfill/pilot scripts implemented:
      - `/opt/data/ucx_framework/ucx_knowledge/orchestrator.py`
      - `/opt/data/ucx_framework/ucx_knowledge/scripts/backfill_legacy.py`
      - `/opt/data/ucx_framework/ucx_knowledge/scripts/pilot_validate.py`
   - Read-only Tradegent adapter handoff artifacts created:
      - `/opt/data/ucx_framework/plans/patches/tradegent_adapters/`
- In progress:
   - Neutral filter generalization in selected RAG/Graph query paths (`entity_id` aliases)
   - Integration testing against live PostgreSQL/Neo4j runtime

### 4.2) Immediate Next Milestone (M1)

Goal: complete neutral metadata model and extraction contract for cross-domain use.

Deliverables:
- `ucx_knowledge/models/metadata.py` (canonical metadata types)
- `ucx_knowledge/models/contracts.py` (embed/search/extract payload contracts)
- `ucx_knowledge/mappings/legacy_tradegent_map.yaml` (field migration map)
- Validation checklist in this IPLAN updated to M1 complete

Acceptance:
- Metadata supports both legacy trading docs and non-trading project docs.
- Contract payloads are versioned and backward-compatible (`v1`).
- Mapping covers all currently used `ticker`-based filters.

### Phase A — Architecture and Contracts

1. Freeze API contracts for:
   - `kb_embed`, `kb_embed_text`, `kb_search`, `kb_hybrid_context`, `kb_status`
   - `kb_extract`, `kb_extract_text`, `kb_graph_context`, `kb_graph_query`
2. Define neutral metadata schema:
   - `entity_id`, `domain`, `source_type`, `source_path`, `tags`, `created_at`, `updated_at`

**Acceptance**
- Contract document exists and is versioned (`v1`).
- Example request/response payloads validated.

---

### Phase B — Extract Standalone Core

1. Create package skeleton:
   - `/opt/data/ucx_framework/ucx_knowledge/rag/`
   - `/opt/data/ucx_framework/ucx_knowledge/graph/`
   - `/opt/data/ucx_framework/ucx_knowledge/mcp/`
2. Move reusable logic from Tradegent into the independent package:
   - `tradegent/rag/*`
   - `tradegent/graph/*`
3. Prepare wrapper/adapter patch set for old module paths (no breaking imports) as a handoff artifact.

**Acceptance**
- Imports succeed from both old and new paths.
- Basic unit tests run against new package.
- Adapter patch instructions are generated for application in writable Tradegent environment.

---

### Phase C — RAG Generalization

1. Replace trading-only filters (`ticker`) with generic filters (`entity_id`, `domain`, `tags`).
2. Parameterize schema/table references and remove hardcoded assumptions.
3. Keep hybrid/rerank/query-expansion features unchanged in behavior.

**Acceptance**
- Search works with generic metadata filters.
- Existing Tradegent retrieval still works via adapters.

---

### Phase D — Graph Generalization

1. Replace trading ontology defaults with configurable ontology packs.
2. Generalize field mappings for non-trading documents.
3. Normalize provider naming and extractor enums.

**Acceptance**
- Extraction works on at least one non-trading sample corpus.
- Graph context query returns domain-neutral entities and relations.

---

### Phase E — Ingestion and Tooling

1. Build unified ingestion orchestration:
   - parse -> validate -> embed -> extract -> commit -> metrics
2. Implement MCP knowledge tools from Phase A contracts.
3. Add observability:
   - ingestion success/fail counts
   - retrieval latency and top-k quality metrics

**Acceptance**
- End-to-end ingestion pipeline runs for folder input.
- MCP tools return schema-valid payloads.

---

### Phase F — Migration and Rollout

1. Create backfill scripts for legacy documents.
2. Add dry-run mode for migration validation.
3. Execute pilot rollout:
   - one project corpus
   - compare retrieval quality before/after
4. Progressive rollout with rollback criteria.

**Acceptance**
- Pilot passes quality and latency thresholds.
- Rollback procedure documented and tested.

## 5) Suggested Command Checklist

```bash
# Paths
DF=/opt/data/ucx_framework
TS=/opt/data/tradegent_swarm

set -euo pipefail

# 1) Validate source baseline in Tradegent (migration source only)
cd "$TS/tradegent"
pytest rag/tests graph/tests -q

# 2) Ensure independent destination package exists
cd "$DF"
mkdir -p ucx_knowledge/{rag,graph,mcp,tests,models,mappings,rag_tools}

# 2b) Reuse/adapt framework rag_tools into ucx_knowledge
cp -R "$DF/framework_rags/rag_tools/." "$DF/ucx_knowledge/rag_tools/"

# 3) Extract/copy modules from source to independent destination
cp -R "$TS/tradegent/rag/." "$DF/ucx_knowledge/rag/"
cp -R "$TS/tradegent/graph/." "$DF/ucx_knowledge/graph/"
# Remove environment files from copied modules (managed per target environment)
rm -f "$DF/ucx_knowledge/rag/.env" "$DF/ucx_knowledge/graph/.env"

# 4) Add Tradegent compatibility adapters (import forwarding to ucx_knowledge)
# NOTE: $TS is read-only in this workspace.
# Do not edit files under $TS here.
# Instead, generate adapter patch artifacts under:
#   $DF/plans/patches/tradegent_adapters/
# for later application in a writable Tradegent clone.

# 5) Run focused source regression checks (read-only validation)
cd "$TS/tradegent"
pytest rag/tests/test_search.py graph/tests/test_extract.py -q

# 6) Run source integration checks
pytest rag/tests/test_integration.py graph/tests/test_integration.py -q

# 7) Run independent package tests (as they are added)
cd "$DF"
pytest ucx_knowledge/tests -q
```

## 6) Risks and Controls

- Risk: import breakage during extraction.
  - Control: adapter wrappers + staged refactor.
- Risk: cannot apply Tradegent adapter changes from this workspace (read-only source repo).
   - Control: produce patch bundle and apply in writable Tradegent environment.
- Risk: metadata mismatch for old records.
  - Control: migration map + validation checks.
- Risk: retrieval quality regression.
  - Control: evaluate with baseline queries and metrics gate.

## 7) Completion Criteria

- `ucx_knowledge` hosts reusable RAG and Graph internals.
- Tradegent adapter patch bundle is ready and validated for application in writable environment.
- MCP knowledge toolset is available and contract-stable.
- Migration scripts and pilot rollout validated.
- `ucx_knowledge/rag_tools` is implemented and integrated with project contracts.
