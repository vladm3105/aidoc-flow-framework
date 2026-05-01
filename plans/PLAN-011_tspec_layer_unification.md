# PLAN-011: TSPEC Layer Unification

**Status**: Complete
**Created**: 2026-03-30
**Scope**: Unify TSPEC (Layer 10) parent aggregator into single YAML template
**Depends on**: Layers 1-9 unified (v0.2.0-v0.10.0)
**Risk**: Low — same orchestrator pattern as SPEC (Layer 9)

---

## Problem

TSPEC is an **orchestrator/aggregator** for 6 test specification subtypes:

### Parent files to consolidate

| File | Lines | Role |
|------|-------|------|
| `TSPEC-MVP-TEMPLATE.md` | 259 | Parent aggregator template (6 sections) |
| `TSPEC-MVP-TEMPLATE.yaml` | 234 | YAML metadata |
| **Total** | **493** | 2 files (lean — no separate creation/validation rules) |

### Additional parent files to archive

| File | Lines | Reason |
|------|-------|--------|
| `TSPEC-MVP-TEMPLATE_FIX_PLAN.md` | — | Completed fix tracking |
| `TSPEC-00_TRACEABILITY_MATRIX-TEMPLATE.md` | — | Redundant |
| `TEST_PYRAMID_GUIDE.md` | — | Reference guide — embed key concepts as `_guidance` |
| `test_registry.yaml` | — | Runtime config, not template |
| `test_registry_schema.yaml` | — | Runtime schema |
| `test_result_schema.yaml` | — | Runtime schema |
| `examples/` (7 files) | — | Old format examples |
| `scripts/` (20+ files) | — | Validation via mcp_ucx |
| `README.md` | — | Old version |

### 6 Subtype directories (keep as-is — NOT migrated in this plan)

| Subtype | Directory | Purpose | Template Lines |
|---------|-----------|---------|---------------|
| UTEST | `UTEST/` | Unit tests (component-level) | 314 |
| ITEST | `ITEST/` | Integration tests (contract/interaction) | 309 |
| STEST | `STEST/` | Smoke tests (deployment critical-path) | 373 |
| FTEST | `FTEST/` | Functional tests (quality-attribute validation) | 370 |
| PTEST | `PTEST/` | Performance tests (load, stress, endurance) | 346 |
| SECTEST | `SECTEST/` | Security tests (threat/control validation) | 361 |

Each subtype has 7 files: template, YAML, schema, creation rules, validation rules,
quality gates, fix plan. These are separate artifact types — migrate individually if needed.

---

## C4 Model Position

TSPEC sits below Code (SPEC) — it validates the implementation. TSPEC is NOT a
C4 level; it's a validation step between Code and implementation (TASKS).

```text
Code (SPEC)      — implementation-ready specifications
  └─ TSPEC       — test specifications (validates SPEC)              ← this layer
  └─ TASKS       — implementation task breakdown
```

No `c4_level.value` — use `_guidance` only.

---

## Target State

```text
10_TSPEC/
├── TSPEC-TEMPLATE.yaml      ← single source of truth (parent aggregator)
├── TSPEC-00_index.md          ← TSPEC registry
├── README.md                  ← new, concise (~100 lines)
├── UTEST/                     ← subtype (kept)
├── ITEST/                     ← subtype (kept)
├── STEST/                     ← subtype (kept)
├── FTEST/                     ← subtype (kept)
├── PTEST/                     ← subtype (kept)
├── SECTEST/                   ← subtype (kept)
└── TSPEC_v1_archive/          ← deprecated parent files
```

---

## Phase 1: Section Analysis

Parent TSPEC has 6 sections. Already minimal.

### Proposed structure: 6 sections + glossary (no changes)

| # | Section |
|---|---------|
| 1 | Document Control |
| 2 | Traceability |
| 3 | Test Strategy Overview |
| 4 | Test Summary by Type (6 subtypes) |
| 5 | Quality Gates |
| 6 | Glossary |

Old Section 6 (Test Document Locations appendix) merged into traceability.

---

## Phase 2: Create TSPEC-TEMPLATE.yaml

- `metadata.c4_level`: `_guidance` only (validation step, no C4 level)
- `metadata.diagram_standard`: no diagram tags (test spec level)
- `metadata.validation.tool: sdd_validate` / `server: mcp_ucx`
- `metadata.id_standard`: `{doc_type}.{doc_id}.{section_id}.{hash}`
- `document_control.tasks_ready_score` (downstream is TASKS)

### Subtype routing table in `_guidance`

| Subtype | Test Category | Scope | Upstream |
|---------|--------------|-------|----------|
| UTEST | Unit | Component-level behavior | REQ, SPEC |
| ITEST | Integration | Contract/interaction | CTR, SPEC |
| STEST | Smoke | Deployment critical-path | SPEC |
| FTEST | Functional | Quality-attribute validation | SYS, SPEC |
| PTEST | Performance | Load/stress/endurance | SYS, SPEC |
| SECTEST | Security | Threat/control validation | SYS, SPEC |

### Upstream/Downstream

```yaml
traceability:
  upstream:
    - "@spec: SPEC.NN.05.xxxx"
    - "@req: REQ.NN.03.xxxx"
    - "@ctr: CTR.NN.05.xxxx"
    - "@sys: SYS.NN.04.xxxx"
  downstream_expected:
    - type: TASKS
      layer: 11
      description: "Implementation tasks including test implementation"
```

### Embed from TEST_PYRAMID_GUIDE

Key test pyramid concepts as `_guidance` in test strategy section:
- Test pyramid layers (unit → integration → smoke → functional → performance → security)
- Test coverage targets per layer
- When to use each test type

---

## Phase 3-8: Standard Execution

- Phase 3: Archive parent files to `TSPEC_v1_archive/` (keep 6 subtype dirs)
- Phase 4: Update `TSPEC-00_index.md`
- Phase 5: Create new `README.md` (include 6-subtype routing table)
- Phase 6: Add `TSPEC-TEMPLATE.yaml` to `mcp_ucx/templates/` (NEW)
- Phase 7: Cross-ref updates (SPEC downstream, verify TASKS upstream)
- Phase 8: Tests, changelog v0.11.0, roadmap

---

## Key Differences

| Aspect | SPEC (Layer 9) | TSPEC (Layer 10) |
|--------|---------------|-----------------|
| C4 level | Code (c4-l4) | None (validation step) |
| Subtypes | 5 (CSPEC, DSPEC, UXSPEC, RISKSPEC, PROCSPEC) | 6 (UTEST, ITEST, STEST, FTEST, PTEST, SECTEST) |
| Parent template | 1,672 lines (comprehensive) | ~300 lines (lean aggregator) |
| Readiness | TASKS-Ready | TASKS-Ready |
| Diagram tags | c4-l4, dfd-l4 | None |
| mcp_ucx template | Added | NEW (to add) |

---

## Decisions (Resolved)

1. **6 subtypes NOT migrated**: Each has 7 files — migrate individually if needed.
2. **C4 level**: None — TSPEC validates Code, not a C4 level itself.
3. **No diagram tags**: Test specs don't use architecture diagrams.
4. **TASKS-Ready score**: Same as SPEC — both feed into TASKS.
5. **Test Pyramid Guide**: Embed key concepts as `_guidance`, archive the file.
6. **Runtime files** (test_registry.yaml, schemas): Archive — these are runtime artifacts.
