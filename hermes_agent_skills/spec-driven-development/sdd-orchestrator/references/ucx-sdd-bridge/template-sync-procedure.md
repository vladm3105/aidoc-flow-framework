# Template Synchronization: Hermes Local Copies ↔ UCX Canonical Sources

## Problem

Hermes maintains local template copies in `~/.hermes/skills/spec-driven-development/sdd-orchestrator/templates/`
These are consumed by the `sdd-orchestrator` skill for document creation/review workflows.

The canonical source of truth is `/opt/data/ucx_framework/ucx_flow_v3/0N_TYPE/TYPE-TEMPLATE.yaml`.

When UCX transitions between framework versions (e.g., v2 → v3), the templates change significantly:
- Layer numbering shifts (e.g., `SPEC` was Layer 9 in v2, became Layer 6 in v3)
- Layers get cut (SYS, REQ, CTR, TSPEC, TASKS removed)
- C4-level mappings change
- Downstream ownership comments in headers must drop cut layers
- Readiness gate names change

## Wrong Approach (Causes Template Drift)

```bash
# WRONG: sed-only replacement
sed -i 's/mcp_ucx/ucx_hermes/g' *.yaml
```

Why it fails:
- Preserves old v2 layer numbers in headers and comments
- Leaves cut layers (SYS, REQ, CTR, TSPEC, TASKS) referenced downstream
- Keeps stale `c4_level` mappings
- Retains old readiness score references like "SYS-Ready" or "TSPEC-Ready"

## Correct Procedure

```bash
# 1. Copy canonical templates FROM the v3 framework source
for f in /opt/data/ucx_framework/ucx_flow_v3/*/*-TEMPLATE.yaml; do
    name=$(basename "$f")
    cp "$f" ~/.hermes/skills/spec-driven-development/sdd-orchestrator/templates/"$name"
done

# 2. Replace the MCP server identifier so Hermes tools wire correctly
sed -i 's/server: mcp_ucx/server: ucx_hermes/g' \
    ~/.hermes/skills/spec-driven-development/sdd-orchestrator/templates/*.yaml
```

## Verification Checklist

After syncing, verify each template:

| Check | Pass Criteria |
|-------|---------------|
| Layer numbers | SPEC=6, TDD=7, IPLAN=8 (v3 mapping) |
| Cut layers absent | No SYS, REQ, CTR, TSPEC, TASKS in downstream ownership |
| C4 mapping | v3 4-layer: BRD→PRD→SPEC→Code |
| Server header | `server: ucx_hermes` present, no `mcp_ucx` remains |
| Readiness gates | BDD-Ready, ADR-Ready, TDD-Ready, IPLAN-Ready, EXEC-Ready (no SYS/REQ/CTR) |

## Automation Script

Use `scripts/sync-ucx-templates.sh` (static re-runnable script maintained in this skill).

## Why Hermes Keeps Local Copies

The UCX framework templates contain `server: ucx_hermes` in their YAML headers to declare which MCP server provides the `sdd_create_build` and `sdd_validate` tools. UCX cannot inject this at copy time because the templates are framework-agnostic assets. Hermes must maintain its own stamped copies.

## When to Sync

- After any UCX framework version bump (`git pull` in `/opt/data/ucx_framework/`)
- After any `LAYER_REGISTRY.yaml` change that shifts layer numbers or cuts layers
- After adding new document types or changing template schemas
- Before any skill version bump that claims v3.2+ compatibility
