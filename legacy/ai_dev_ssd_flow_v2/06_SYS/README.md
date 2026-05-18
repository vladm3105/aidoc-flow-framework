# System Requirements (SYS) — Layer 6

## Overview

SYS defines system structure, interfaces, and quality attributes, implementing
architecture decisions from ADR. SYS is the C4 Component level.

**Workflow**: BRD → PRD → EARS → BDD → ADR → SYS → REQ → CTR → SPEC → TSPEC → TASKS → Code

## C4 Model Position

SYS is the **Component** level — the first C4 level with system-internal detail.

```text
Context (BRD)    — business environment, actors, boundaries
  └─ EARS/BDD    — formalize Context→Container transition
Container (PRD)  — product features, functional blocks
  └─ ADR         — decisions that shape Component architecture
Component (SYS)  — system structure, interfaces, quality attributes    ← this layer
  └─ REQ/CTR     — decompose Component→Code into atomic units
Code (SPEC)      — implementation-ready specifications
  └─ TSPEC       — test specifications
  └─ TASKS       — implementation task breakdown
```

## Files

| File | Purpose |
|------|---------|
| `SYS-TEMPLATE.yaml` | Single source of truth — template with embedded authoring guidance |
| `SYS-00_index.md` | SYS registry — tracks planned and active SYS documents per project |

## Template Sync Rule

**IMPORTANT**: `SYS-TEMPLATE.yaml` exists in two locations that must stay in sync:

| Location | Role |
|----------|------|
| `ucx_flow_v3/06_SYS/SYS-TEMPLATE.yaml` | **Canonical source** — edit here |
| `mcp_sdd/templates/SYS-TEMPLATE.yaml` | **Runtime copy** — used by MCP tools |

```bash
cp ucx_flow_v3/06_SYS/SYS-TEMPLATE.yaml mcp_sdd/templates/SYS-TEMPLATE.yaml
```

## MCP Tools (mcp_sdd)

| Tool | Purpose |
|------|---------|
| `sdd_create` | Generate SYS from template |
| `sdd_validate` | Structural validation |
| `sdd_score_validate` | REQ-Ready score (>=90/100 to proceed to REQ) |
| `sdd_consistency` | Cross-document traceability check |
| `sdd_next_action` | Lifecycle advisor |

## Quality Attributes (6 Categories)

| Category | Key Metrics |
|----------|------------|
| Performance | p50/p95/p99 latency, throughput (RPS), resource utilization |
| Reliability | Uptime %, RTO/RPO, fault tolerance, graceful degradation |
| Scalability | Horizontal/vertical scaling, load distribution |
| Security | Authentication, encryption (AES-256/TLS 1.3), RBAC, audit |
| Observability | Structured logging, distributed tracing, real-time metrics |
| Maintainability | Code coverage, CI/CD automation, rollback, zero-downtime deploy |

## Element IDs

Hash-based, content-derived IDs scoped to SYS content:

```text
Format: SYS.{doc_id}.{section_id}.{hash}
Example: SYS.01.04.f3a9
```

## Upstream Traceability

SYS requires cumulative tags (Layer 6 — all upstream layers):

```text
@adr: ADR.NN.03.xxxx    (architecture decision)
@bdd: BDD.NN.03.xxxx    (test scenarios)
@ears: EARS.NN.03.xxxx   (formal requirements)
@prd: PRD.NN.09.xxxx    (product features)
@brd: BRD.NN.07.xxxx    (business requirements)
```

## Archive

`SYS_v1_archive/` contains deprecated files from the previous dual-file template
approach. See `SYS_v1_archive/README.md` for migration details.
