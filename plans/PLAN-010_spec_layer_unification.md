# PLAN-010: SPEC Layer Unification

**Status**: Complete
**Created**: 2026-03-29
**Scope**: Unify SPEC (Layer 9) into single YAML template, same approach as Layers 1-8
**Depends on**: BRD-CTR unification (v0.2.0-v0.9.0) — all complete
**Risk**: Medium — SPEC is an orchestrator with 5 subtypes; largest YAML template (1,648 lines)

---

## Problem

SPEC layer has the standard dual-file pattern PLUS 5 subtype subdirectories:

### Core files to consolidate

| File | Lines | Role |
|------|-------|------|
| `SPEC-MVP-TEMPLATE.md` | 320 | Human narrative template (8 sections + 2 appendices) |
| `SPEC-MVP-TEMPLATE.yaml` | 1,648 | Full YAML template (already comprehensive) |
| `SPEC_MVP_CREATION_RULES.md` | 820 | Authoring guidance |
| `SPEC_MVP_VALIDATION_RULES.md` | 502 | Validation rules |
| `SPEC_MVP_QUALITY_GATE_VALIDATION.md` | 656 | Quality gates |
| **Total** | **3,946** | 5 files (no separate schema — YAML template IS the spec) |

### Subtype directories (keep as-is for now)

| Subtype | Directory | deliverable_type | Template Lines |
|---------|-----------|-----------------|---------------|
| CSPEC | `CSPEC/` | code (default) | 253 |
| DSPEC | `DSPEC/` | document | 262 |
| UXSPEC | `UXSPEC/` | ux | 353 |
| RISKSPEC | `RISKSPEC/` | risk | 233 |
| PROCSPEC | `PROCSPEC/` | process | 305 |

**Decision**: Subtype directories are NOT migrated in this plan. They are separate
artifact types with their own templates and will be migrated individually if needed.
This plan unifies only the PARENT SPEC template.

### Additionally to archive

| File | Lines | Reason |
|------|-------|--------|
| `SPEC-MVP-TEMPLATE_FIX_PLAN.md` | 559 | Completed fix tracking |
| `SPEC-00_TRACEABILITY_MATRIX-TEMPLATE.md` | 497 | Redundant |
| `SPEC_AI_VALIDATION_DECISION_GUIDE.md` | 65 | Empty scaffold |
| `SPEC_VALIDATION_STRATEGY.md` | 154 | References scripts |
| `SPEC_VALIDATION_COMMANDS.md` | 69 | References scripts |
| `REVIEW_REPORT.md` | 277 | Historical |
| `FIXES_SUMMARY.md` | 188 | Historical |
| `examples/` | ~764 | Old format |
| `scripts/` (7 files) | ~1,169 | Validation via mcp_ucx |
| `.backup_*` | — | Historical |
| `README.md` | 1,324 | Old version |
| `SPEC-MVP-TEMPLATE.md` | 320 | Replaced by unified YAML |

---

## C4 Model Position — CODE LEVEL

SPEC is the **C4 Code level** — the deepest zoom in the C4 model.
It defines implementation-ready specifications for ANY deliverable type:
- **CSPEC** (code): algorithms, state machines, interfaces, configurations
- **DSPEC** (document): documentation structure, style, review criteria
- **UXSPEC** (ux): wireframes, mockups, design specifications
- **RISKSPEC** (risk): risk matrices, impact assessments, mitigation plans
- **PROCSPEC** (process): SOPs, runbooks, operational procedures

"Code level" means the most detailed zoom — not literally source code.
DSPEC is also at Code level because it's the implementation-ready spec
for documentation deliverables.

```text
Component (SYS)  — system structure, interfaces, quality attributes
  └─ REQ/CTR     — decompose Component→Code into atomic units
Code (SPEC)      — implementation-ready specifications              ← this layer
  └─ TSPEC       — test specifications
  └─ TASKS       — implementation task breakdown
```

**`c4_level.value: code`** — the fourth and final C4 level.

**Diagram tags**: `c4-l4`, `dfd-l4`, class diagrams, sequence diagrams.

All four C4 levels complete after this migration:
- Context (BRD) → Container (PRD) → Component (SYS) → **Code (SPEC)**

---

## Target State

```text
09_SPEC/
├── SPEC-TEMPLATE.yaml       ← single source of truth (unified from 1,648-line YAML)
├── SPEC-00_index.md           ← SPEC registry
├── README.md                  ← new, concise (~100 lines)
├── CSPEC/                     ← subtype (kept, not migrated)
├── DSPEC/                     ← subtype (kept, not migrated)
├── UXSPEC/                    ← subtype (kept, not migrated)
├── RISKSPEC/                  ← subtype (kept, not migrated)
├── PROCSPEC/                  ← subtype (kept, not migrated)
└── SPEC_v1_archive/           ← deprecated parent SPEC files
```

---

## Phase 1: Section Analysis

SPEC has 8 sections + 2 appendices. Lean — minimal removal needed.

### Keep

| # | Section | Rationale |
|---|---------|-----------|
| 1 | Document Control | Metadata, TASKS-Ready score |
| 2 | Traceability | Upstream REQ/CTR/SYS, downstream TASKS/TSPEC |
| 3 | Component Overview | Purpose, scope, boundaries |
| 4 | Technical Design | Architecture, interfaces, patterns |
| 5 | Implementation Logic | Pseudocode, state machines, algorithms |
| 6 | Configuration | Environment variables, feature flags |
| 7 | Non-Functional Requirements | Performance, security, observability |
| 8 | Quality Gates | Test requirements, coverage, acceptance |

### Evaluate for removal/merge

| Section | Assessment | Action |
|---------|-----------|--------|
| App A (Glossary) | Keep as standard glossary section | **KEEP** as glossary |
| App B (References) | Merge into traceability | **MERGE** |

### Proposed structure: 8 sections + glossary

Same 8 sections (already lean) + glossary. References merged into traceability.

---

## Phase 2: Create SPEC-TEMPLATE.yaml

The existing `SPEC-MVP-TEMPLATE.yaml` (1,648 lines) is already comprehensive.
The migration adds `_guidance`, `_antipatterns`, C4 metadata, hash IDs, and
embeds creation/validation rules — but keeps the core structure.

- `metadata.c4_level.value: code` — FOURTH and final C4 level
- `metadata.diagram_standard`: `c4-l4`, `dfd-l4`, class diagrams, sequence diagrams
- `metadata.validation.tool: sdd_validate` / `server: mcp_ucx`
- `metadata.id_standard`: `{doc_type}.{doc_id}.{section_id}.{hash}`, SHA256
- `document_control.tasks_ready_score` (CSPEC downstream readiness)
- Subtype routing documented in `metadata._guidance`:

  | deliverable_type | Subtype | Readiness Score | CTR Required | Sections |
  |-----------------|---------|-----------------|-------------|----------|
  | `code` (default) | CSPEC | TASKS-Ready | Yes | 10 (arch, interfaces, behavior, perf, security, observability) |
  | `document` | DSPEC | DOC-Ready | No | 8 (doc spec, style, review criteria) |
  | `ux` | UXSPEC | DESIGN-Ready | Optional | domain-specific |
  | `risk` | RISKSPEC | RISK-Ready | No | domain-specific |
  | `process` | PROCSPEC | PROC-Ready | Optional | domain-specific |

  The parent SPEC template is the ROUTER. Each subtype has its own section
  structure in its subdirectory. `deliverable_type` is set at BRD (Layer 1)
  and inherited down the entire chain.

### Element ID Format

```text
Format: SPEC.{doc_id}.{section_id}.{hash}
Example: SPEC.01.05.d8e2
```

### Upstream/Downstream Traceability

```yaml
traceability:
  upstream:
    - "@req: REQ.NN.03.xxxx"
    - "@ctr: CTR.NN.05.xxxx"
    - "@sys: SYS.NN.04.xxxx"
  downstream_expected:
    - type: TSPEC
      layer: 10
      description: "Test specifications validating this SPEC"
    - type: TASKS
      layer: 11
      description: "Implementation tasks from this SPEC"
```

### Embed from creation/validation rules

| Source | Embed in | Content |
|--------|----------|---------|
| Creation Rules: SPEC structure | `component_overview._guidance` | Scope, boundaries |
| Creation Rules: Implementation patterns | `implementation_logic._guidance` | Pseudocode, state machines |
| Creation Rules: Subtype routing | `metadata._guidance` | deliverable_type → subtype mapping with readiness scores |
| Creation Rules: CTR dependency | `metadata._guidance` | CTR required for CSPEC, optional/not for others |
| Validation Rules: TASKS-Ready scoring | `metadata.validation._guidance` | 10-criteria rubric (CSPEC) |
| Validation Rules: DOC-Ready scoring | `metadata.validation._guidance` | Scoring criteria (DSPEC) |

---

## Phase 3-8: Standard Execution

- Phase 3: Archive to `SPEC_v1_archive/` (parent files only, keep subtype dirs)
- Phase 4: Update `SPEC-00_index.md`
- Phase 5: Create new `README.md` (include subtype routing table)
- Phase 6: Copy to `mcp_ucx/templates/SPEC-TEMPLATE.yaml` (NEW — no old to remove)
- Phase 7: Cross-ref updates (REQ/CTR downstream, BRD glossary)
- Phase 8: Tests, template resolution, changelog v0.10.0, roadmap

---

## Key Differences

| Aspect | Layers 1-8 | SPEC |
|--------|-----------|------|
| C4 level | Context/Container/Component/none | **Code (c4-l4)** |
| Subtypes | None | 5 (CSPEC, DSPEC, UXSPEC, RISKSPEC, PROCSPEC) |
| YAML template size | 250-466 lines | **~1,648 lines** (largest) |
| Diagram tags | c4-l1/l2/l3/none | **c4-l4, dfd-l4, class diagrams** |
| Readiness score | Various | TASKS-Ready |
| mcp_ucx template | Existed or added | **NEW** (no old to remove) |

---

## Decisions (Resolved)

1. **Subtypes NOT migrated**: CSPEC/DSPEC/UXSPEC/RISKSPEC/PROCSPEC stay as-is.
   Each is a separate artifact type. Migrate individually if needed.
2. **C4 level**: `code` — fourth and final C4 level.
3. **Diagram tags**: `c4-l4`, `dfd-l4` — Code level. Plus class diagrams.
4. **TASKS-Ready score**: Downstream readiness metric.
5. **Template size**: Keep existing 1,648-line YAML structure but add `_guidance` conventions.
6. **References appendix**: Merge into traceability section.
