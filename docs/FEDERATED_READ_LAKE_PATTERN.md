# Enterprise Architecture Pattern: Isolated Edge Ingestion $\to$ Central Federated Read Lake

## Document Control

| Field | Value |
|---|---|
| Pattern ID | `PAT-GRAPH-001` |
| Title | Isolated Edge Ingestion $\to$ Central Federated Read Lake |
| Status | Approved Architecture Standard |
| Version | 1.0 |
| Last Updated | 2026-10-16 |
| Target Scope | Multi-project engineering ecosystems (`devd/*`, `/mnt/e/dev/*`), autonomous coding agents, CI/CD runners |
| Companion Standards | [`docs/AIDOC_WORKSTATION_STANDARD.md`](AIDOC_WORKSTATION_STANDARD.md), [`framework/governance/MULTI_PROJECT_FEDERATED_STANDARD.md`](../framework/governance/MULTI_PROJECT_FEDERATED_STANDARD.md), [`framework/governance/SDD_GRAPH_SCHEMA_SPECIFICATION.md`](../framework/governance/SDD_GRAPH_SCHEMA_SPECIFICATION.md), [`plans/SDD-GRAPH-SCHEMA-AND-OBSERVABILITY-ADAPTER-PLAN.md`](../plans/SDD-GRAPH-SCHEMA-AND-OBSERVABILITY-ADAPTER-PLAN.md) |

---

## 1. Executive Summary & Problem Context

In modern software organizations running multiple polyglot repositories and autonomous AI coding agents, architectural knowledge and specification dependencies must satisfy two diametrically opposing requirements:

1. **The Edge Invariant (Local Autonomy & Hermetic Isolation):**
   - Individual developers, AI agent swarms, and CI runners operate on specific repositories, branches, and ephemeral `git worktree` checkouts.
   - Local verification (`task sdd:lint`, `task sdd:graph-check`, `task sdd:slice`) must run **100% offline, in-process, and sub-second**, with zero external daemon dependencies and zero risk of cross-branch or cross-project state pollution.
2. **The Central Invariant (Global Observability & Cross-Project Lineage):**
   - System architects, security officers, and autonomous multi-repo planning agents must understand the **global blast radius** of changes across all sibling repositories.
   - Answering questions like *"If `auth-service` modifies token schema V1, which downstream microservices and test suites break?"* requires an aggregated, global view of the entire enterprise dependency DAG.

### The Two Anti-Patterns to Avoid

```
❌ ANTI-PATTERN A: The Monolithic Central DB           ❌ ANTI-PATTERN B: The Siloed Repository Islands
   (Local Dev connects directly to central DB)           (No shared view across sibling repositories)

   Project A ──┐                                         [Project A]             [Project B]
   Project B ──┼──► [Shared Central DB]                     (isolated)              (isolated)
   Project C ──┘    (Neo4j / Postgres)                           │                       │
                                                                 ▼                       ▼
   • Worktree & branch collisions in local dev           • Zero cross-project blast-radius detection
   • Breaks CI runner isolation (requires VPN/ports)     • Breaking contract changes discovered in prod
   • Local development fails when offline/unreachable    • Blind multi-repo refactoring by AI agents
```

---

## 2. The Pattern: Isolated Edge Ingestion $\to$ Central Federated Read Lake

This specification establishes the **Two-Tier CQRS Graph Topology**:

- **Write Plane (Edge):** Isolated, embedded graph execution per repository worktree.
- **Read Plane (Central Lake):** Asynchronous, event-driven aggregation into a central multi-tenant graph database.

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                               TIER 1: EDGE WRITE PLANE (Local Workstations & CI)                       │
├───────────────────────────────────┬───────────────────────────────────┬────────────────────────────────┤
│    Repo A: vladm3105/auth-core    │   Repo B: vladm3105/b-local-privy │  Repo C: vladm3105/aidoc-flow  │
│                                   │                                   │                                │
│  • SSOT: docs/sdd/graph/*.yaml    │  • SSOT: docs/sdd/graph/*.yaml    │  • SSOT: docs/sdd/graph/*.yaml │
│  • Engine: Embedded KÙZU / RAM    │  • Engine: Embedded KÙZU / RAM    │  • Engine: Embedded KÙZU / RAM │
│  • Scope: Local Worktree Cache    │  • Scope: Local Worktree Cache    │  • Scope: Local Worktree Cache │
│  • Task: `task sdd:graph-check`   │  • Task: `task sdd:graph-check`   │  • Task: `task sdd:graph-check`│
└─────────────────┬─────────────────┴─────────────────┬─────────────────┴────────────────┬───────────────┘
                  │                                   │                                  │
                  │ Push on Merge to `dev`/`main`     │ Push on Merge to `dev`/`main`    │ Push on Merge
                  ▼                                   ▼                                  ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                        TIER 2: CENTRAL FEDERATED READ LAKE (Central Observability)                     │
│                           Hosted on PostgreSQL 18 + Apache AGE  or  Memgraph / Neo4j                   │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                        │
│   (@auth-core:SPEC.06.01.token) ◄───────── [:verifies] ───────── (@b-local-privy:BDD.04.login)        │
│                 │                                                             │                        │
│                 └───────────────────── [:realizes] ───────────────────────────┘                        │
│                                               │                                                        │
│                                               ▼                                                        │
│                             (@aidoc-flow:01_BRD:compliance_req)                                        │
│                                                                                                        │
│   CAPABILITIES:                                                                                        │
│   • Global Cross-Repo Blast Radius Calculation (Cypher pathing: `[:verifies|implements*1..5]`)        │
│   • Interactive Enterprise C4-L1 / C4-L2 System Context Maps (Neo4j Bloom / Memgraph Lab)              │
│   • Multi-Tenant GraphRAG for Cross-Repository Planning Agents (LangGraph crews)                       │
│   • Automated Contract Deprecation & Version Stagnation Audits                                         │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Tier 1: The Edge Write Plane Specification

### 3.1. Worktree & Repository Isolation

1. **Single Source of Truth (SSOT):**
   The normative specification lives in plain text inside the repository:
   - Modular slices: `docs/sdd/graph/modules/<module_id>/<slug>.graph.yaml`
   - Initiative slices: `docs/sdd/graph/initiatives/<init_id>.graph.yaml`

2. **Embedded Graph Engine:**
   - **Default Engine:** **[Kùzu](https://kuzudb.com/)** (`pip install kuzu`). Runs 100% in-process via C++ bindings.
   - **Fallback Engine:** Pure-Python **NetworkX** (`networkx`) for restricted environments where binary wheels cannot be installed.

3. **Cache Storage Directory:**
   - The compiled binary graph database is an **ephemeral cache**, strictly gitignored:

     ```text
     .aidoc/cache/graph.kuzu/
     ```

   - In CI runners and automated unit tests, the engine runs purely in-memory:

     ```python
     db = kuzu.Database("")  # 100% RAM-backed, 0ms disk cleanup
     ```

### 3.2. Cross-Project References via Federated Stubs

Per [`MULTI_PROJECT_FEDERATED_STANDARD.md`](../framework/governance/MULTI_PROJECT_FEDERATED_STANDARD.md) §2.1.C, edge repositories never clone sibling repositories to resolve dependencies:

- Cross-project node IDs use globally qualified URIs: `@<repo_slug>:<NODE_ID>`.
- Example: `@auth-core:SPEC.06.01.token_v1`.
- The edge engine resolves `@repo_slug:` references against `.aidoc/contracts-registry.yaml`. Declared contracts are materialized as validated external stubs, enabling Binary Topological Validation (BTV) to pass cleanly in complete isolation.

---

## 4. The Graph Stitching & Synchronization Protocol

### 4.1. Namespacing & Global Identity Contract

When a repository exports its graph into the Central Read Lake, every node and edge is automatically namespaced to ensure zero collisions across sibling projects:

```json
{
  "node_id": "@b-local-privy:BDD.04.01.checkout",
  "project": "b-local-privy",
  "layer": "04_BDD",
  "type": "acceptance_scenario",
  "title": "OAuth2 Authenticated Checkout",
  "status": "Active",
  "edges": [
    {
      "type": "verifies",
      "target": "@auth-core:SPEC.06.01.token_v1"
    }
  ]
}
```

### 4.2. Automatic In-Lake Edge Stitching

Because cross-project targets cite the canonical `@<repo_slug>:<NODE_ID>` format:

1. When `auth-core` publishes, its node `@auth-core:SPEC.06.01.token_v1` is upserted into the Central Lake.
2. When `b-local-privy` publishes, its edge `(@b-local-privy:BDD.04.01.checkout)-[:verifies]->(@auth-core:SPEC.06.01.token_v1)` resolves immediately.
3. The central graph becomes an **organically interconnected enterprise knowledge graph** without requiring centralized manual authoring.

### 4.3. Synchronization Triggers

1. **CI/CD Ingestion on Merge (Automated):**
   When a PR merges into `dev` or `main` in any project, the repository's post-merge CI pipeline executes:

   ```bash
   task sdd:publish-lake -- --endpoint "$CENTRAL_GRAPH_ENDPOINT" --token "$LAKE_INGEST_TOKEN"
   ```

2. **Local Workstation Sweep (`task sdd:federate-local`):**
   On a local development workstation holding sibling checkouts (e.g. `$WORKSPACE/*`), developers can synchronize all local repositories into a local central graph container in a single command:

   ```bash
   task sdd:federate-local -- --root "$WORKSPACE" --lake bolt://localhost:7687
   ```

---

## 5. Tier 2: The Central Federated Read Lake Specification

### 5.1. Database Engine Selection

The Central Read Lake is a server-based graph database. In accordance with the enterprise technology stack:

| Database Option | Technology Stack Role | Primary Strength |
|---|---|---|
| **PostgreSQL 18 + Apache AGE** | **Primary Corporate Standard** | Zero new database infrastructure; combines openCypher, SQL tables, and `pgvector` for unified GraphRAG. |
| **Memgraph** | **Recommended Local Dev & High-Performance Lake** | 100% in-memory, C++, blazing fast, drop-in Neo4j Bolt compatibility, includes Memgraph Lab UI. |
| **Neo4j Enterprise** | **Dedicated Graph Analytics Standard** | Mature APOC procedures, Graph Data Science (GDS) algorithms, Neo4j Bloom visual explorer. |

### 5.2. Core Central Lake Capabilities

#### A. Global Cross-Repository Blast-Radius Calculation

When an upstream service considers mutating a contract, architects or AI agents query the Central Lake:

```cypher
// Query: Identify every project across the company impacted by modifying token_v1
MATCH (contract:ComponentContract {id: "@auth-core:SPEC.06.01.token_v1"})
      <-[:verifies|proves|implements*1..6]-(dependent)
WHERE dependent.project <> "auth-core"
RETURN dependent.project AS ImpactedProject,
       dependent.id AS ImpactedNode,
       labels(dependent) AS NodeType,
       dependent.status AS Status
```

#### B. Enterprise Architecture Map (Mermaid & C4 Projection)

The central lake can compile global system interactions on demand:

```cypher
MATCH (p1:SystemContainer)-[r:communicates_with|depends_on]->(p2:SystemContainer)
RETURN p1.name, type(r), p2.name
```

Projected automatically into visual C4-L1/L2 diagrams in documentation portals.

#### C. Cross-Repository AI Agent Planning (Multi-Repo Crews)

When an enterprise-level AI Planner (e.g. in `aidoc-flow-langgraph`) initiates a cross-system feature:

1. It queries the Central Lake for all services implementing relevant capabilities.
2. It generates scoped, atomic tasks for each downstream project's local worktree.
3. Each project's autonomous agent executes the task in its local embedded Kùzu environment.

---

## 6. Implementation Checklist & Migration Matrix

| Phase | Milestone | Action Item | Target Artifact |
|---|---|---|---|
| **Phase 1: Edge Engine** | Embedded Kùzu Engine | Implement in-process Kùzu with NetworkX fallback in `sdd_doc_lint`. | `sdd_doc_lint/graph_engine.py` |
| **Phase 2: Local Tasks** | Workstation Integration | Add `sdd:graph-check`, `sdd:slice`, and `sdd:publish-lake` to Taskfile. | `.aidoc/Taskfile.yml` |
| **Phase 3: Central Lake** | Server Deployment | Deploy Memgraph or Apache AGE container in `technology_stack`. | `compose.dev-tooling.yaml` |
| **Phase 4: Sync Pipeline**| CI & Local Sweeper | Implement local multi-repo crawler and post-merge CI publisher. | `scripts/federate_graph_lake.py` |

---

## 7. Architectural Guarantees & Summary

1. **Zero Worktree Contention:** Local developers and AI agents in parallel branches never block each other or experience database lock errors.
2. **Hermetic CI:** Repositories build, test, and pass topological validation in isolation without external database network connections.
3. **Global Traceability:** The enterprise gains unified, queryable, 3D visualization and impact analysis across all projects in the corporate fleet.
