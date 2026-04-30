# Contract Specifications (CTR) — Layer 8

## Overview

CTR defines formal interface contracts using OpenAPI 3.x specifications.
Each contract specifies request/response schemas, error handling, quality attributes,
and versioning policies. CTR instances are dual-file: `.md` (narrative) + `.yaml` (OpenAPI).

**Workflow**: BRD → PRD → EARS → BDD → ADR → SYS → REQ → CTR → SPEC → TSPEC → TASKS → Code

## C4 Model Position

CTR (like REQ) decomposes Component (SYS) into formal interface contracts for Code (SPEC).

```text
Component (SYS)  — system structure, interfaces, quality attributes
  └─ REQ/CTR     — decompose Component→Code into atomic units        ← this layer
Code (SPEC)      — implementation-ready specifications
```

## Files

| File | Purpose |
|------|---------|
| `CTR-TEMPLATE.yaml` | Single source of truth — template with embedded authoring guidance |
| `CTR-00_index.md` | CTR registry — tracks planned and active contracts per project |

CTR instances are dual-file: `CTR-NN_slug.md` + `CTR-NN_slug.yaml` (OpenAPI 3.x).

## Template Sync Rule

| Location | Role |
|----------|------|
| `ai_dev_ssd_flow/08_CTR/CTR-TEMPLATE.yaml` | **Canonical source** — edit here |
| `mcp_sdd/templates/CTR-TEMPLATE.yaml` | **Runtime copy** — used by MCP tools |

```bash
cp ai_dev_ssd_flow/08_CTR/CTR-TEMPLATE.yaml mcp_sdd/templates/CTR-TEMPLATE.yaml
```

## MCP Tools (mcp_sdd)

| Tool | Purpose |
|------|---------|
| `sdd_create` | Generate CTR from template |
| `sdd_validate` | Structural validation |
| `sdd_score_validate` | SPEC-Ready score (>=85/100 for implementation) |
| `sdd_consistency` | Cross-document traceability check |

## Element IDs

```text
Format: CTR.{doc_id}.{section_id}.{hash}
Example: CTR.01.05.b2d4
```

## Contract Status Lifecycle

```text
Draft → Active → Deprecated → Superseded
```

Versioning: SemVer (MAJOR.MINOR.PATCH). Breaking changes require new major version with 30-day migration.

## Archive

`CTR_v1_archive/` contains deprecated files. See `CTR_v1_archive/README.md`.
