# PLAN-008: REQ Layer Unification

**Status**: Complete
**Created**: 2026-03-29
**Scope**: Unify REQ (Layer 7) into single YAML template, same approach as Layers 1-6
**Depends on**: BRD-SYS unification (v0.2.0-v0.7.0) — all complete
**Risk**: Low — follows proven pattern

---

## Problem

REQ layer has the same dual-file pattern:

| File | Lines | Role |
|------|-------|------|
| `REQ-MVP-TEMPLATE.md` | 529 | Human narrative template (11 sections) |
| `REQ-MVP-TEMPLATE.yaml` | 421 | YAML structure for autopilot |
| `REQ_MVP_SCHEMA.yaml` | 655 | Validation schema |
| `REQ_MVP_CREATION_RULES.md` | 583 | Authoring guidance |
| `REQ_MVP_VALIDATION_RULES.md` | 1,152 | Post-creation validation |
| `REQ_MVP_QUALITY_GATE_VALIDATION.md` | 835 | Quality gates |
| **Total** | **4,175** | 6 files to consolidate |

Additionally to archive:

| File | Lines | Reason |
|------|-------|--------|
| `REQ-MVP-TEMPLATE_FIX_PLAN.md` | 865 | Completed fix tracking |
| `REQ-00_TRACEABILITY_MATRIX-TEMPLATE.md` | 491 | Redundant |
| `REQ_AI_VALIDATION_DECISION_GUIDE.md` | 755 | Heavy but can be embedded |
| `REQ_VALIDATION_STRATEGY.md` | 110 | References scripts |
| `REQ_VALIDATION_TESTING_GUIDE.md` | 174 | References scripts |
| `REQ_VALIDATION_COMMANDS.md` | 125 | References scripts |
| `REVIEW_REPORT.md` | 154 | Historical |
| `FIXES_SUMMARY.md` | 149 | Historical |
| `GATE-05_INTEGRATION_SUMMARY.md` | 217 | Historical |
| `GATE-05_CROSS_LINKING_ENHANCEMENT.md` | 139 | Historical |
| `examples/` (4+ files) | ~1,467 | Old format |
| `scripts/` (11+ files) | large | Validation via mcp_ucx |
| `.backup_2026-02-26/` | — | Historical |
| `README.md` | 1,025 | Old version |

---

## C4 Model Position

REQ decomposes Component (SYS) into atomic requirements. REQ sits between
Component (SYS) and Code (SPEC) — it is NOT a C4 level itself, similar to
how EARS/BDD sit between Context and Container.

```text
Component (SYS)  — system structure, interfaces, quality attributes
  └─ REQ/CTR     — decompose Component→Code into atomic units        ← this layer
Code (SPEC)      — implementation-ready specifications
```

No `c4_level.value` — use `_guidance` only.

---

## Target State

```text
07_REQ/
├── REQ-TEMPLATE.yaml      ← single source of truth
├── REQ-00_index.md          ← REQ registry
├── README.md                ← new, concise (~90 lines)
└── REQ_v1_archive/          ← all deprecated files
```

---

## Phase 1: Section Analysis

REQ has 11 sections. All are REQ-layer concerns — minimal removal needed.

### Evaluate for removal/merge

| # | Section | Assessment | Action |
|---|---------|-----------|--------|
| 8 | Testing Requirements | Lightweight in REQ already. | **KEEP** — needed for TSPEC downstream |
| 11 | Implementation Notes | Overlaps SPEC/TASKS. | **REMOVE** — SPEC owns implementation |

### Proposed structure: 10 sections + glossary

| # | Section |
|---|---------|
| 1 | Document Control |
| 2 | Requirement Description |
| 3 | Functional Specification |
| 4 | Interface Definition |
| 5 | Error Handling |
| 6 | Quality Attributes |
| 7 | Configuration |
| 8 | Testing Requirements |
| 9 | Acceptance Criteria |
| 10 | Traceability |
| — | Glossary |

---

## Phase 2: Create REQ-TEMPLATE.yaml

- `metadata.c4_level`: `_guidance` only (decomposition step, no C4 level value)
- `metadata.diagram_standard`: sequence diagrams, component interaction diagrams
  No C4 level tags — REQ is a decomposition step like EARS/BDD
- `metadata.validation.tool: sdd_validate` / `server: mcp_ucx`
- `metadata.id_standard`: `{doc_type}.{doc_id}.{section_id}.{hash}`, SHA256
- `document_control.spec_ready_score` (downstream is SPEC)

### Element ID Format

```text
Format: REQ.{doc_id}.{section_id}.{hash}
Example: REQ.01.03.a1c7
```

### Upstream Traceability (SYS → REQ)

```yaml
traceability:
  tags:
    - "@req: REQ-NN"
  upstream:
    - "@sys: SYS.NN.04.xxxx"    # SYS functional requirement
    - "@adr: ADR.NN.03.xxxx"    # ADR decision
    - "@prd: PRD.NN.09.xxxx"
    - "@brd: BRD.NN.07.xxxx"
```

### Downstream Traceability (REQ → CTR/SPEC)

```yaml
  downstream_expected:
    - type: CTR
      layer: 8
      description: "Data contracts for REQ interface definitions"
    - type: SPEC
      layer: 9
      description: "Technical specifications implementing this requirement"
    - type: TSPEC
      layer: 10
      description: "Test specifications validating this requirement"
```

### Embed from creation/validation rules

| Source | Embed in | Content |
|--------|----------|---------|
| Creation Rules: Atomic requirement format | `requirement_description._guidance` | Single testable concept |
| Creation Rules: Functional spec structure | `functional_specification._guidance` | I/O/processing/validation |
| Creation Rules: Interface definition | `interface_definition._guidance` | API contract pointers |
| Creation Rules: Error handling patterns | `error_handling._guidance` | Error categories, recovery |
| Validation Rules: SPEC-Ready scoring | `metadata.validation._guidance` | Score thresholds |
| AI Decision Guide: Key patterns | Relevant `_guidance` sections | Unique decision patterns |

---

## Phase 3-8: Standard Execution

Same pattern as previous 6 migrations:
- Phase 3: Archive to `REQ_v1_archive/`
- Phase 4: Update `REQ-00_index.md`
- Phase 5: Create new `README.md`
- Phase 6: Copy to `mcp_ucx/templates/`, remove old `REQ-MVP-TEMPLATE.md`
- Phase 7: Cross-ref updates (SYS downstream, BRD glossary)
- Phase 8: Tests, template resolution, changelog v0.8.0, roadmap

---

## Key Differences from Previous Migrations

| Aspect | Layers 1-6 | REQ |
|--------|-----------|-----|
| Starting sections | 6-21 | 11 |
| Final sections | 5-15 | 10 + glossary |
| C4 level | Context/Container/Component/none | None (decomposition step) |
| Readiness score | Various | SPEC-Ready |
| Unique feature | Various | Atomic requirements, single testable concept |
| mcp_ucx template | .md or .yaml existed | `REQ-MVP-TEMPLATE.md` to replace |

---

## Decisions (Resolved)

1. **Section 11 (Implementation Notes)**: REMOVE — SPEC/TASKS own implementation.
2. **C4 level**: No value — REQ is a decomposition step between Component and Code.
3. **Diagram tags**: None — REQ operates at atomic requirement level, not architecture.
4. **SPEC-Ready score**: Downstream readiness metric (SPEC is next in workflow).
