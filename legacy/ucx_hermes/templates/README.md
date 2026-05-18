# UCX Hermes Templates

> Templates in this directory are the **active runtime copies** used by the `sdd-lifecycle` MCP server.
> The **canonical sources** live in `ucx_flow_v3/` (per-layer READMEs document the exact paths).

---

## What Changed (v2.0.0/v3.2)

| Before (mcp_ucx) | After (ucx_hermes) |
|---|---|
| `mcp_ucx/templates/*.yaml` | `ucx_hermes/templates/*.yaml` |
| `mcp_ucx/templates/` now frozen | `ucx_hermes/templates/` is the active runtime copy |

---

## Active Templates (v3.2 — 8 Layers)

| File | Layer | C4 Level | Upstream | Downstream |
|------|-------|----------|----------|------------|
| `BRD-TEMPLATE.yaml` | L1 | Context (C4-L1) | — | PRD |
| `PRD-TEMPLATE.yaml` | L2 | Container (C4-L2) | BRD | EARS |
| `EARS-TEMPLATE.yaml` | L3 | Decision Bridge | PRD | BDD |
| `BDD-TEMPLATE.yaml` | L4 | Decision Bridge | EARS | ADR |
| `ADR-TEMPLATE.yaml` | L5 | Decision Bridge | BDD | SPEC |
| `SPEC-TEMPLATE.yaml` | L6 | Component (C4-L3) | ADR + BDD | TDD |
| `TDD-TEMPLATE.yaml` | L7 | Implementation Bridge | SPEC | IPLAN |
| `IPLAN-TEMPLATE.yaml` | L8 | Implementation Bridge | TDD | Code |

---

## Cut / Archived Templates (v2 Layers)

These 5 templates exist in `templates/archive/` for historical reference but are **not part of the active v3.2 SDD flow**:

| File | Old Layer | Status |
|------|-----------|--------|
| `SYS-TEMPLATE.yaml` | L6 (v2) | Cut — ADR now captures architecture decisions |
| `REQ-TEMPLATE.yaml` | L7 (v2) | Cut — EARS + BDD provide requirement traceability |
| `CTR-TEMPLATE.yaml` | L8 (v2) | Cut — SPEC inline contracts replace CTR |
| `TSPEC-TEMPLATE.yaml` | L10 (v2) | Cut — TDD (L7) embeds test case definitions |
| `TASKS-TEMPLATE.yaml` | L11 (v2) | Cut — IPLAN (L8) replaces execution planning |

> **Rule**: New documents must NOT reference SYS, REQ, CTR, TSPEC, or TASKS as downstream or upstream layers in active templates. Use the archive templates only for legacy document migration.

---

## Template Sync Rule

After the canonical template is edited in `ucx_flow_v3/`, copy it here:

```bash
# Example: update BRD template
cp ucx_flow_v3/01_BRD/BRD-TEMPLATE.yaml ucx_hermes/templates/BRD-TEMPLATE.yaml
```

Then fix the `server:` reference (if not already using `ucx_hermes`):

```bash
sed -i 's/    server: mcp_ucx/    server: ucx_hermes/' ucx_hermes/templates/BRD-TEMPLATE.yaml
```

Verify no stale `mcp_ucx` or cut-layer references remain:

```bash
grep -n "mcp_ucx\|SYS\|REQ\|CTR\|TSPEC\|TASKS" ucx_hermes/templates/*.yaml
```

Expected output: only matches in `archive/*.yaml` (cut layers preserved for history).

---

## Server Reference

All active templates must reference:

```yaml
validation:
  server: ucx_hermes
```

---

## V3.2 C4 Mapping

```
C4-L1 Context    — BRD (L1)
  └─ Decision Bridge — EARS (L3), BDD (L4), ADR (L5)
C4-L2 Container  — PRD (L2)
  └─ Decision Bridge — EARS (L3), BDD (L4), ADR (L5)
C4-L3 Component  — SPEC (L6)
  └─ Implementation Bridge — TDD (L7), IPLAN (L8)
C4-L4 Code       — Source Code
```

---

## Verification Checklist

- [ ] All 8 active templates synced from `ucx_flow_v3/`
- [ ] `server: ucx_hermes` in all active templates
- [ ] Zero references to SYS, REQ, CTR, TSPEC, TASKS in active templates (except archive/)
- [ ] Layer numbers correct (BRD=1, PRD=2, EARS=3, BDD=4, ADR=5, SPEC=6, TDD=7, IPLAN=8)
- [ ] Downstream/upstream chains point to correct v3 layers
- [ ] C4 mapping mentions Context→Container→Component→Code with correct layer assignments

---
