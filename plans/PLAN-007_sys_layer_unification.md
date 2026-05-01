# PLAN-007: SYS Layer Unification

**Status**: Complete
**Created**: 2026-03-29
**Scope**: Unify SYS (Layer 6) into single YAML template, same approach as BRD/PRD/EARS/BDD/ADR
**Depends on**: BRD-ADR unification (v0.2.0-v0.6.0) — all complete
**Risk**: Low — follows proven pattern. SYS is the first C4 Component level layer

---

## Problem

SYS layer has the same dual-file pattern:

| File | Lines | Role |
|------|-------|------|
| `SYS-MVP-TEMPLATE.md` | 1,242 | Human narrative template (15 sections) |
| `SYS-MVP-TEMPLATE.yaml` | 252 | YAML metadata structure |
| `SYS_MVP_SCHEMA.yaml` | 491 | Validation schema |
| `SYS_MVP_CREATION_RULES.md` | 664 | Authoring guidance |
| `SYS_MVP_VALIDATION_RULES.md` | 440 | Post-creation validation |
| `SYS_MVP_QUALITY_GATE_VALIDATION.md` | 696 | Quality gates |
| **Total** | **3,785** | 6 files to consolidate |

Additionally to archive:

| File | Lines | Reason |
|------|-------|--------|
| `SYS-MVP-TEMPLATE_FIX_PLAN.md` | 1,417 | Completed fix tracking |
| `SYS-00_TRACEABILITY_MATRIX-TEMPLATE.md` | 322 | Redundant (per-SYS traceability + AI-generated) |
| `SYS_AI_VALIDATION_DECISION_GUIDE.md` | 65 | Empty scaffold |
| `SYS_VALIDATION_STRATEGY.md` | 66 | References scripts, not mcp_ucx |
| `SYS_VALIDATION_COMMANDS.md` | 59 | References scripts, not mcp_ucx |
| `REVIEW_REPORT.md` | 193 | Historical review report |
| `FIXES_SUMMARY.md` | 146 | Historical fix summary |
| `validate_sys_fixes.sh` | 207 | Root-level fix validation script |
| `examples/` (4 files) | 2,297 | Old format examples |
| `scripts/` (7 files) | ~1,609 | Validation via mcp_ucx |
| `.backup_*` directories | — | Historical backups |
| `README.md` | 647 | Old version |

---

## C4 Model Position — FIRST COMPONENT LEVEL

SYS is the **C4 Component level** — the first layer with an actual C4 level value.
It defines system structure, interfaces, and quality attributes based on ADR decisions.

```text
Container (PRD)  — product features, functional blocks
  └─ ADR         — decisions that shape Component architecture
Component (SYS)  — system structure, interfaces, quality attributes  ← this layer
  └─ REQ/CTR     — decompose Component→Code into atomic units
Code (SPEC)      — implementation-ready specifications
```

**`c4_level.value: component`** — first layer to have a C4 level value since PRD (container).

**Diagram tags**: `c4-l3`, `dfd-l3`, `sequence-sync` — consistent with C4 Component level.

---

## Target State

```text
06_SYS/
├── SYS-TEMPLATE.yaml      ← single source of truth
├── SYS-00_index.md          ← SYS registry
├── README.md                ← new, concise (~90 lines)
└── SYS_v1_archive/          ← all deprecated files
```

---

## Phase 1: Section Analysis

SYS has 15 sections. Evaluate for the unified template.

### Keep (SYS-layer concerns)

| # | Section | Rationale |
|---|---------|-----------|
| 1 | Document Control | Standard metadata + REQ-Ready score |
| 2 | Executive Summary | System context, business value |
| 3 | Scope | System boundaries, acceptance scope, assumptions |
| 4 | Functional Requirements | Core system behaviors (SYS owns detailed quality attributes) |
| 5 | Quality Attributes | Performance, reliability, scalability, security, observability, maintainability |
| 6 | Interface Specifications | API contracts, integration points |
| 7 | Data Management Requirements | Data persistence, backup, retention |
| 11 | Acceptance Criteria | System acceptance criteria |
| 12 | Risk Assessment | System-level risks |
| 13 | Traceability | Upstream ADR/BDD/EARS/PRD/BRD, downstream REQ/CTR/SPEC |

### Evaluate for removal/merge

| # | Section | Assessment | Action |
|---|---------|-----------|--------|
| 8 | Testing and Validation | Owned by TSPEC (Layer 10). Keep as lightweight testing expectations. | **TRIM** — one-liners only |
| 9 | Deployment and Operations | Overlaps with TASKS/IPLAN. BUT SYS needs deployment architecture at Component level. | **KEEP** — trim to architecture, not operations details |
| 10 | Compliance and Regulatory | Could merge into Quality Attributes Section 5. | **MERGE** into Section 5 as compliance subsection |
| 14 | Implementation Notes | Overlaps with TASKS/SPEC. Drop entirely — SPEC/TASKS own this. | **REMOVE** |
| 15 | Change History | Standard revision history, merge into Document Control. | **MERGE** into Section 1 |

### Proposed structure: 12 sections + glossary

| # | Section |
|---|---------|
| 1 | Document Control (absorbs old Section 15 Change History) |
| 2 | Executive Summary |
| 3 | Scope |
| 4 | Functional Requirements |
| 5 | Quality Attributes (absorbs old Section 10 Compliance) |
| 6 | Interface Specifications |
| 7 | Data Management Requirements |
| 8 | Testing Expectations (trimmed from old Section 8) |
| 9 | Deployment Architecture (trimmed from old Section 9) |
| 10 | Acceptance Criteria |
| 11 | Risk Assessment |
| 12 | Traceability |
| — | Glossary |

---

## Phase 2: Create SYS-TEMPLATE.yaml

Apply BRD/PRD/EARS/BDD/ADR conventions:
- `_guidance`, `_antipatterns`, `_note`, `_example` fields
- `metadata.c4_level.value: component` — FIRST actual C4 level since PRD
- `metadata.diagram_standard`: C4-L3 component diagrams, DFD-L3, sequence diagrams
  Tags: `@diagram: c4-l3`, `@diagram: dfd-l3`, `@diagram: sequence-sync`
- `metadata.validation.tool: sdd_validate` / `server: mcp_ucx`
- `metadata.deliverable_type`: inherited from upstream
- `metadata.id_standard`: `{doc_type}.{doc_id}.{section_id}.{hash}`, SHA256
- `document_control.req_ready_score` (downstream is REQ)
  Note: Old SYS had both ears_ready_score and req_ready_score.
  Drop ears_ready_score — SYS doesn't validate EARS readiness.

### Old upstream format to fix

- `@adr: ADR-NN` (document-level only) → `@adr: ADR.NN.03.xxxx` (hash-based)
- All upstream tags must use hash format

### Element ID Format

```text
Format: SYS.{doc_id}.{section_id}.{hash}
Example: SYS.01.04.f3a9
```

### Upstream Traceability (ADR → SYS)

```yaml
traceability:
  tags:
    - "@sys: SYS-NN"
  upstream:
    - "@adr: ADR.NN.03.xxxx"    # ADR decision
    - "@bdd: BDD.NN.03.xxxx"    # BDD scenarios
    - "@ears: EARS.NN.03.xxxx"  # EARS requirements
    - "@prd: PRD.NN.09.xxxx"   # PRD features
    - "@brd: BRD.NN.07.xxxx"   # BRD requirements
```

### Downstream Traceability (SYS → REQ/CTR/SPEC)

```yaml
  downstream_expected:
    - type: REQ
      layer: 7
      description: "Atomic requirements decomposed from SYS system requirements"
    - type: CTR
      layer: 8
      description: "Data contracts for SYS interface specifications"
    - type: SPEC
      layer: 9
      description: "Technical specifications implementing SYS requirements"
```

### Embed from creation/validation rules

| Source | Embed in | Content |
|--------|----------|---------|
| Creation Rules: Functional requirements structure | `functional_requirements._guidance` | System behavior format |
| Creation Rules: Quality attribute categories | `quality_attributes._guidance` | 6 categories with metrics |
| Creation Rules: Interface specifications | `interface_specifications._guidance` | API contract format |
| Creation Rules: Data management patterns | `data_management._guidance` | Persistence, backup, retention |
| Validation Rules: REQ-Ready scoring | `metadata.validation._guidance` | Score thresholds |
| Quality Gate: Quality checks | Validation stays in mcp_ucx tools | Not embedded |

---

## Phase 3: Archive Deprecated Files

Move to `06_SYS/SYS_v1_archive/`:

- `SYS-MVP-TEMPLATE.md`
- `SYS-MVP-TEMPLATE.yaml`
- `SYS_MVP_SCHEMA.yaml`
- `SYS_MVP_CREATION_RULES.md`
- `SYS_MVP_VALIDATION_RULES.md`
- `SYS_MVP_QUALITY_GATE_VALIDATION.md`
- `SYS-MVP-TEMPLATE_FIX_PLAN.md`
- `SYS-00_TRACEABILITY_MATRIX-TEMPLATE.md`
- `SYS_AI_VALIDATION_DECISION_GUIDE.md`
- `SYS_VALIDATION_STRATEGY.md`
- `SYS_VALIDATION_COMMANDS.md`
- `REVIEW_REPORT.md`
- `FIXES_SUMMARY.md`
- `validate_sys_fixes.sh`
- `examples/`
- `scripts/`
- `README.md` (old version)
- `.backup_2026-02-26/` → `SYS_v1_archive/backup_2026-02-26/`
- `backup_20260208_161017/` → `SYS_v1_archive/backup_20260208/`

---

## Phase 4: Update SYS-00_index.md

- Update template link to `SYS-TEMPLATE.yaml`
- Update validation commands to mcp_ucx tools
- Remove references to archived files

---

## Phase 5: Create New README.md

Same structure as other layers:
- Files table
- C4 Model Mapping (SYS = Component level — c4-l3, dfd-l3)
- Template sync rule
- MCP tools reference
- Quality attributes overview (6 categories)
- Element ID format
- Upstream traceability (ADR/BDD/EARS/PRD/BRD cumulative tags)
- Archive note

---

## Phase 6: Update mcp_ucx

- Copy `SYS-TEMPLATE.yaml` to `mcp_ucx/templates/SYS-TEMPLATE.yaml`
- Remove `mcp_ucx/templates/SYS-MVP-TEMPLATE.md`
- Check SYS prompts for old references (grep showed none)
- No source code changes needed

---

## Phase 7: Cross-Reference Updates

- `ADR-TEMPLATE.yaml` downstream_expected: verify SYS description
- `BRD-TEMPLATE.yaml` downstream_expected: update SYS description
  (currently "detailed quality attributes from Section 9" — stale BRD section ref)
- `BRD-00_GLOSSARY.md`: verify SYS definition
- Verify SYS is NOT in BDD/EARS downstream (correct — they go through ADR)

---

## Phase 8: Validation, Documentation, Changelog, Roadmap

- Run mcp_ucx test suite
- Verify SYS template resolves
- Create `changelog/CHANGELOG_v0.7.0.md`
- Update `roadmap/ROADMAP.md`: current → v0.7.0, renumber API executors to v0.8.0

---

## Key Differences from Previous Migrations

| Aspect | BRD | PRD | EARS | BDD | ADR | SYS |
|--------|-----|-----|------|-----|-----|-----|
| Starting sections | 18 | 21+3 | 6 | Feature+YAML | 11 | 15 |
| Final sections | 15 | 15 | 5+glossary | 5 | 10+glossary+app | 12+glossary |
| C4 level | Context | Container | Transition | Transition | Bridge | **Component** |
| Readiness score | PRD-Ready | EARS-Ready | BDD-Ready | ADR-Ready | SYS-Ready | **REQ-Ready** |
| Source lines | 5,573 | 4,616 | 2,988 | 4,108 | 3,118 | 3,785 |
| Diagram tags | c4-l1,dfd-l1 | c4-l2,dfd-l2 | none | none | none | **c4-l3,dfd-l3** |
| mcp_ucx code changes | 5 files | 0 | 0 | 0 | 0 | 0 |

---

## Decisions (Resolved)

1. **Section 10 (Compliance)**: MERGE into Section 5 (Quality Attributes) as compliance subsection.
2. **Section 15 (Change History)**: MERGE into Section 1 (Document Control) as revision_history.
3. **Section 8 (Testing)**: TRIM to testing expectations one-liners (TSPEC owns details).
4. **Section 9 (Deployment)**: TRIM to deployment architecture (TASKS/IPLAN owns operations).
5. **C4 level**: `component` — first layer with C4 level value since PRD.
6. **Diagram tags**: `c4-l3`, `dfd-l3`, `sequence-sync` — Component level.
