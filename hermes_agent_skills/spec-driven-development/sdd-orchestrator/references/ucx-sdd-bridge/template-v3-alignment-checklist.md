# Template v3.2 Alignment Checklist

## Why This Matters

When syncing UCX templates from the canonical source (`ucx_flow_v3/`) to the
Hermes runtime copy (`ucx_hermes/templates/`), a simple `sed` to replace the
server header is **insufficient**. The old templates may contain stale
references to v2 layers that were cut in v3.2.

## The Wrong Way

```bash
# WRONG: sed-only replacement
sed -i 's/server: mcp_ucx/server: ucx_hermes/g' *.yaml
```

This preserves:
- Cut layer references (SYS, REQ, CTR, TSPEC, TASKS) in downstream ownership
- Wrong layer numbers (e.g., SPEC referred to as Layer 9 in v2 headers)
- Stale C4 mappings that include SYS/REQ/CTR as levels
- Obsolete readiness score names like "SYS-Ready" or "TSPEC-Ready"

## The Right Way

```bash
# 1. Copy fresh from canonical v3.2 source
cp ucx_flow_v3/01_BRD/BRD-TEMPLATE.yaml ucx_hermes/templates/BRD-TEMPLATE.yaml
# ... repeat for all 8 active layers

# 2. THEN stamp server header
sed -i 's/server: mcp_ucx/server: ucx_hermes/g' ucx_hermes/templates/*.yaml

# 3. Verify no stale references remain
```

## Audit Checks (Run After Every Sync)

### 1. Active Templates Must Reference Only v3.2 Layers

Active templates (8 layers):
- `BRD-TEMPLATE.yaml` (L1)
- `PRD-TEMPLATE.yaml` (L2)
- `EARS-TEMPLATE.yaml` (L3)
- `BDD-TEMPLATE.yaml` (L4)
- `ADR-TEMPLATE.yaml` (L5)
- `SPEC-TEMPLATE.yaml` (L6)
- `TDD-TEMPLATE.yaml` (L7)
- `IPLAN-TEMPLATE.yaml` (L8)

For each active template, verify:
| Check | Command |
|-------|---------|
| No `mcp_ucx` references | `grep -n "mcp_ucx" *.yaml` → should return nothing |
| No SYS downstream refs | `grep -n "SYS" *.yaml` → only in `archive/` |
| No REQ downstream refs | `grep -n "REQ" *.yaml` → only in `archive/` |
| No CTR downstream refs | `grep -n "CTR" *.yaml` → only in `archive/` |
| No TSPEC downstream refs | `grep -n "TSPEC" *.yaml` → only in `archive/` |
| No TASKS downstream refs | `grep -n "TASKS" *.yaml` → only in `archive/` |
| Correct layer numbers | SPEC=6, TDD=7, IPLAN=8 |
| Server field | `server: ucx_hermes` present |

### 2. Cut Layers Belong in Archive Only

Cut v2 layers (5 templates) — must live in `templates/archive/`:
- `SYS-TEMPLATE.yaml`
- `REQ-TEMPLATE.yaml`
- `CTR-TEMPLATE.yaml`
- `TSPEC-TEMPLATE.yaml`
- `TASKS-TEMPLATE.yaml`

Archive templates may retain `mcp_ucx` references; they are historical artifacts.

### 3. Layer Number Verification

| Template | Expected Layer | Expected C4 Level |
|----------|---------------|-----------------|
| BRD | L1 | Context (C4-L1) |
| PRD | L2 | Container (C4-L2) |
| EARS | L3 | Decision Bridge |
| BDD | L4 | Decision Bridge |
| ADR | L5 | Decision Bridge |
| SPEC | L6 | Component (C4-L3) |
| TDD | L7 | Implementation Bridge |
| IPLAN | L8 | Implementation Bridge |

### 4. Downstream Chain Verification

Active downstream chains (from header comments):
- BRD → PRD
- PRD → EARS
- EARS → BDD
- BDD → ADR
- ADR → SPEC
- SPEC → TDD
- TDD → IPLAN
- IPLAN → Code

Any reference to SYS, REQ, CTR, TSPEC, or TASKS in downstream position = **FAIL**.

## Quick Audit Script

```bash
#!/bin/bash
TMPL_DIR="ucx_hermes/templates"
ARCHIVE_DIR="$TMPL_DIR/archive"

echo "=== Active Template Audit ==="
for f in "$TMPL_DIR"/*-TEMPLATE.yaml; do
    fname=$(basename "$f")
    if [[ "$fname" =~ archive ]]; then continue; fi
    
    has_mcp_ucx=$(grep -c "mcp_ucx" "$f" || true)
    has_cut=$(grep -cE "\b(SYS|REQ|CTR|TSPEC|TASKS)\b" "$f" || true)
    
    if [[ $has_mcp_ucx -gt 0 || $has_cut -gt 0 ]]; then
        echo "  FAIL: $fname (mcp_ucx=$has_mcp_ucx, cut_layers=$has_cut)"
    else
        echo "  PASS: $fname"
    fi
done

echo ""
echo "=== Archive Templates (historical) ==="
for f in "$ARCHIVE_DIR"/*-TEMPLATE.yaml; do
    fname=$(basename "$f")
    has_mcp_ucx=$(grep -c "mcp_ucx" "$f" || true)
    echo "  INFO: $fname (mcp_ucx=$has_mcp_ucx, historical artifact)"
done
```

## When to Run This Audit

- After any git pull / update of `ucx_flow_v3/` canonical sources
- Before committing changes to `ucx_hermes/templates/`
- After any bulk operation on templates (sed, copy, rsync)
- During release preparation (verify templates are v3-aligned before tagging)
