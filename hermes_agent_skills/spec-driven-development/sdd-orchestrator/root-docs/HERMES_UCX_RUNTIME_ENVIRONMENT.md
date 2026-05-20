---
title: Hermes + UCX Runtime Environment
tags:
  - ai-agent-primary
  - shared-architecture
  - runtime-environment
  - mcp-integration
  - active
custom_fields:
  architecture_approaches:
    - ai-agent-primary
  priority: primary
  development_status: active
  components:
    - hermes-agent
    - ucx_hermes
    - ucx_kb
    - trace2skill
---

# Hermes + UCX + ucx_kb + Trace2Skill Runtime Environment

## 1. Scope

Define the runtime environment where Hermes is the interactive agent runtime, UCX MCP tools are the deterministic SDD lifecycle engine, ucx_kb provides indexed knowledge retrieval, and Trace2Skill is used for offline skill tuning.

This document describes architecture boundaries, data flow, operational modes, constraints, and validation criteria for `ucx_flow_v3` execution.

## 2. Component Roles

| Component | Runtime Role | Primary Interface | Responsibility Boundary |
| --- | --- | --- | --- |
| Hermes Agent | Agent runtime and orchestration shell | CLI/TUI, gateway, MCP client | Session management, model/tool routing, operator interaction |
| UCX (`ucx_hermes`) | Deterministic SDD lifecycle engine | MCP server `sdd-lifecycle` | `sdd_*` tools, validation/review/remediation pipeline, stage artifacts |
| ucx_kb (`ucx_kb`) | Knowledge retrieval subsystem | MCP server `ucx_kb.mcp.server` | RAG/graph retrieval via `kb_*` tools |
| Trace2Skill | Offline skill-evolution pipeline | Python runners (`skill_evolver/*`) | Candidate skill generation and consolidation from traces |

## 3. Runtime Architecture

```mermaid
flowchart LR
  U[Operator] --> H[Hermes Agent Runtime]
  H -->|MCP calls| UMX[sdd-lifecycle\n(UCX MCP)]
  H -->|MCP calls| UKB[ucx_kb MCP]

  UMX --> DF[ucx_flow_v3 documents]
  UKB --> KB[(Postgres pgvector + Neo4j)]

  H -. traces .-> T2S[Trace2Skill Offline Tuning]
  T2S -. candidate skills .-> H
```

## 4. Operating Modes

### 4.1 Baseline Mode (Default)

- Hermes + UCX enabled.
- ucx_kb optional (file-only mode allowed).
- Trace2Skill disabled for runtime decisions.
- Use this mode as the reference baseline for quality and regression checks.

### 4.2 Indexed Knowledge Mode

- Hermes + UCX + ucx_kb enabled.
- Start PostgreSQL (`pgvector`) and Neo4j from `ucx_kb/docker-compose.db.yml`.
- Use `kb_*` tools for retrieval and graph context during document operations.

### 4.3 Tuned Skill Mode (Controlled)

- Baseline stack plus Trace2Skill-generated candidate skills.
- Candidate skills are evaluated offline against baseline.
- Promote only candidates that pass all acceptance gates.

## 5. Tool Surfaces

### 5.1 UCX MCP Surface

- MCP server name: `sdd-lifecycle`.
- Primary lifecycle tools: `sdd_init`, `sdd_create`, `sdd_validate`, `sdd_review`, `sdd_remediate`, `sdd_run_lifecycle`, `sdd_score_*`, `sdd_validate_links`, `sdd_preflight`, `sdd_consistency`, `sdd_clean`.

### 5.2 ucx_kb MCP Surface

- MCP entrypoint: `python -m ucx_kb.mcp.server`.
- Exposed tools include:
  - retrieval: `kb_embed`, `kb_embed_text`, `kb_search`, `kb_hybrid_context`, `kb_status`
  - graph: `kb_extract`, `kb_extract_text`, `kb_graph_context`, `kb_graph_search`, `kb_graph_query`, `kb_graph_status`

### 5.3 Trace2Skill Surface

- Offline executables under `skill_evolver/`.
- No direct mutation of production skill set without validation and approval.

## 6. Data and Control Flow

1. Operator submits task in Hermes.
2. Hermes calls UCX `sdd_*` tools via MCP for lifecycle actions.
3. Hermes optionally calls ucx_kb `kb_*` tools for retrieval context.
4. UCX writes lifecycle artifacts and reports to document-local `.ucx/` stage directories.
5. Hermes returns synthesized result and artifact locations.
6. Trace2Skill consumes historical traces offline and outputs candidate skill updates.
7. Candidate skills are validated against baseline gates before activation.

## 7. Resource Requirements

| Subsystem | Compute | Storage | Network |
| --- | --- | --- | --- |
| Hermes runtime | CPU-bound for orchestration | Session/log storage | LLM provider and MCP connections |
| UCX MCP | CPU-bound for validation/review orchestration | Artifact reports under project | Local MCP stdio (or configured transport) |
| ucx_kb | CPU + memory for retrieval/graph queries | Postgres + Neo4j persistent volumes | Local DB and MCP traffic |
| Trace2Skill runs | Batch CPU/GPU depending model endpoint | Trace corpus and skill snapshots | API endpoint throughput |

Implementation complexity: **4/5** (multi-service runtime with deterministic and learned subsystems).

## 8. Constraints

- UCX remains the source of truth for SDD lifecycle contract enforcement.
- Hermes skills must not bypass `sdd_validate`/`sdd_review`/`sdd_remediate` quality gates.
- Trace2Skill outputs are treated as candidate artifacts until validated.
- Runtime must support `ucx_flow_v3` document flow and naming/traceability policies.
- Planning-first governance is mandatory across document, testing, and code workflows:
  - analysis -> roadmap -> planning index -> changelog plan -> gap review -> IPLAN -> approval -> implementation.
  - approval authority is human reviewer or independent LLM-as-judge session.

## 9. Failure Modes and Mitigations

| Failure Mode | Impact | Detection | Mitigation |
| --- | --- | --- | --- |
| UCX MCP unavailable | Lifecycle operations blocked | MCP connection failure | Restart `sdd-lifecycle`; run `sdd_preflight` |
| ucx_kb DB unavailable | Retrieval degradation | `kb_status`/`kb_graph_status` failure | Fall back to file-only mode |
| Skill drift from Trace2Skill | Quality regression in outputs | Baseline-vs-candidate score delta | Reject candidate and restore baseline skills |
| Model/provider outage in Hermes | Reduced agent availability | Provider error rates/timeouts | Use Hermes fallback providers and retries |
| Report schema mismatch | Downstream automation breaks | Validation/scoring contract errors | Enforce UCX report contract checks pre-promotion |

## 10. Validation and Promotion Gates

A candidate runtime/skill change is accepted only if all conditions pass:

1. `sdd_validate` pass rate does not decrease from baseline.
2. `sdd_score_validate` threshold pass rate does not decrease from baseline.
3. No increase in link or consistency violations.
4. Full `ucx_flow_v3` stage completion succeeds on benchmark document set.
5. No new critical findings in remediation outputs.

## 11. Baseline Recommendation

Adopt **Hermes + UCX** as the default production baseline.

- Enable `ucx_kb` when indexed retrieval is required.
- Introduce Trace2Skill in controlled offline cycles after baseline metrics are captured.
- Keep deterministic UCX contract enforcement active in every mode.

## 12. Paths

- UCX framework root: `/opt/data/ucx_framework`
- UCX lifecycle engine: `/opt/data/ucx_framework/ucx_hermes`
- Knowledge subsystem: `/opt/data/ucx_framework/ucx_kb`
- SDD flow assets: `/opt/data/ucx_framework/ucx_flow_v3`
