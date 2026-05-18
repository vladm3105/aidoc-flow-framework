# PLAN-006: ADR Layer Unification

**Status**: Complete
**Created**: 2026-03-29
**Scope**: Unify ADR (Layer 5) into single YAML template, same approach as BRD/PRD/EARS/BDD
**Depends on**: BRD (v0.2.0), PRD (v0.3.0), EARS (v0.4.0), BDD (v0.5.0) — all complete
**Risk**: Low — follows proven pattern. ADR YAML template already has 11 sections (363 lines)

---

## Problem

ADR layer has the same dual-file pattern:

| File | Lines | Role |
|------|-------|------|
| `ADR-MVP-TEMPLATE.md` | 406 | Human narrative template (11 sections) |
| `ADR-MVP-TEMPLATE.yaml` | 363 | YAML structure for autopilot |
| `ADR_MVP_SCHEMA.yaml` | 460 | Validation schema |
| `ADR_MVP_CREATION_RULES.md` | 500 | Authoring guidance |
| `ADR_MVP_VALIDATION_RULES.md` | 422 | Post-creation validation |
| `ADR_MVP_QUALITY_GATE_VALIDATION.md` | 967 | Quality gates |
| **Total** | **3,118** | 6 files to consolidate |

Additionally to archive:

| File | Lines | Reason |
|------|-------|--------|
| `ADR-MVP-TEMPLATE_FIX_PLAN.md` | 888 | Completed fix tracking |
| `ADR-00_TRACEABILITY_MATRIX-TEMPLATE.md` | 501 | Redundant (per-ADR traceability + AI-generated) |
| `ADR_AI_VALIDATION_DECISION_GUIDE.md` | 65 | Empty scaffold |
| `ADR_VALIDATION_STRATEGY.md` | 66 | References scripts, not mcp_ucx |
| `ADR_VALIDATION_COMMANDS.md` | 59 | References scripts, not mcp_ucx |
| `REVIEW_REPORT.md` | 208 | Historical review report |
| `FIXES_SUMMARY.md` | 101 | Historical fix summary |
| `ADR-CTR_SEPARATE_FILES_POLICY.md` | 306 | Keep as active ADR instance (NOT archive) |
| `ADR-00_ai_powered_documentation_assistant_architecture.md` | 463 | Keep as active ADR instance (NOT archive) |
| `examples/` (2 files) | 1,097 | Old format examples |
| `scripts/` (8 files) | ~1,663 | Validation via mcp_ucx |
| `.backup_2026-02-26/` | — | Historical backup |
| `README.md` | 1,160 | Old 1,160-line version |

**NOTE**: `ADR-00_*` files and `ADR-CTR_*` are ADR INSTANCES, not templates. They stay
in the active directory (not archived). Only template/rules/scripts/support files are archived.

---

## Target State

```text
05_ADR/
├── ADR-TEMPLATE.yaml                              ← single source of truth
├── ADR-00_index.md                                 ← ADR registry
├── ADR-00_ai_powered_documentation_assistant_architecture.md  ← active instance
├── ADR-CTR_SEPARATE_FILES_POLICY.md               ← active instance
├── README.md                                       ← new, concise (~80 lines)
└── ADR_v1_archive/                                 ← deprecated template/rules files
```

---

## C4 Model Position

ADR is the **decision bridge** between Container (PRD) and Component (SYS).
It is NOT a C4 level itself — it records architectural decisions that shape
the Component-level design.

```text
Container (PRD)  — product features, functional blocks
  └─ ADR         — decisions that shape Component architecture    ← this layer
Component (SYS)  — system structure, interfaces, quality attributes
```

No `c4_level.value` — use `_guidance` only to explain ADR's bridge role.

---

## Phase 1: Section Analysis

ADR has 11 sections. Evaluate for the unified template.

### Keep (all 11 — ADR structure is already well-defined)

| # | Section | Rationale |
|---|---------|-----------|
| 1 | Document Control | Standard metadata + SYS-Ready score |
| 2 | Context | Problem statement, constraints, technical context |
| 3 | Decision | Chosen solution, components, approach |
| 4 | Alternatives Considered | Options with pros/cons/cost/fit |
| 5 | Consequences | Positive outcomes, trade-offs, risks, costs |
| 6 | Architecture Flow | Mermaid diagrams, integration points |
| 7 | Implementation Assessment | MVP phases, rollback, monitoring |
| 8 | Verification | Success criteria, BDD scenarios |
| 9 | Traceability | Upstream BRD/PRD/EARS/BDD, downstream SYS/REQ/SPEC |
| 10 | Related Decisions | Dependencies, related ADRs, supersedes |
| 11 | MVP Lifecycle | Lifecycle phases, when to create new ADR |

### Evaluate for removal/merge

| Section | Assessment |
|---------|-----------|
| 7 (Implementation Assessment) | Overlaps with TASKS (Layer 11). BUT ADR needs rollback plan and monitoring baseline at decision time. **KEEP** — trim to decision-relevant content, not implementation details. |
| 8 (Verification) | BDD scenarios in ADR are cross-references, not full scenarios. **KEEP** as lightweight cross-ref. |
| 11 (MVP Lifecycle) | Similar to BRD appendix lifecycle. **MERGE into appendix** — not a numbered section. |

### Proposed structure: 10 sections + lifecycle appendix + glossary

| # | Section |
|---|---------|
| 1 | Document Control |
| 2 | Context |
| 3 | Decision |
| 4 | Alternatives Considered |
| 5 | Consequences |
| 6 | Architecture Flow |
| 7 | Implementation Assessment (trimmed — decision-level only) |
| 8 | Verification (cross-refs to BDD scenarios) |
| 9 | Traceability |
| 10 | Related Decisions |
| — | Glossary |
| — | Appendix: MVP Lifecycle (from old Section 11) |

---

## Phase 2: Create ADR-TEMPLATE.yaml

Apply BRD/PRD/EARS/BDD conventions:
- `_guidance`, `_antipatterns`, `_note`, `_example` fields
- `metadata.c4_level`: `_guidance` only (decision bridge, no C4 level value)
- `metadata.diagram_standard`: ADR uses architecture decision diagrams:
    - C4-L3 component diagrams (decision's impact on system structure)
    - sequenceDiagram (architecture interaction flows)
    - flowchart (decision logic, rollback paths)
- `metadata.validation.tool: sdd_validate` / `server: mcp_ucx`
- `metadata.deliverable_type`: inherited from upstream
- `metadata.id_standard`: `{doc_type}.{doc_id}.{section_id}.{hash}`, SHA256
- `document_control.sys_ready_score` (downstream is SYS)
- `document_control.originating_topic`: `@prd: PRD.NN.14.xxxx` (PRD ADR topic elaboration)

### Element ID Format

```text
Format: ADR.{doc_id}.{section_id}.{hash}
Example: ADR.01.03.e5b1
```

Hash derived from ADR content.

### Old element type codes to replace

ADR's own IDs:
- `ADR.NN.10.SS` (code 10 = Decision) → `ADR.NN.03.xxxx` (Section 3)
- `ADR.NN.12.SS` (code 12 = Alternative) → `ADR.NN.04.xxxx` (Section 4)
- `ADR.NN.13.SS` (code 13 = Consequence) → `ADR.NN.05.xxxx` (Section 5)

Upstream references (originating_topic + traceability tags):
- `originating_topic`: points to PRD Section 14 (ADR topic elaboration), NOT BRD directly
  Old: `BRD.NN.32.SS` → New: `PRD.NN.14.xxxx` (PRD elaborates topics with technical options)
- `@brd:` cumulative tag still links to BRD Section 8: `@brd: BRD.NN.08.xxxx`
- `@prd:` cumulative tag links to PRD Section 14: `@prd: PRD.NN.14.xxxx`

### ADR-specific status lifecycle

ADR uses different status values from other layers:
- `Proposed` → `Accepted` → `Deprecated` → `Superseded`
  (NOT Draft/In Review/Approved like BRD/PRD/EARS/BDD)
- Document in `document_control._guidance`

### Upstream Traceability (BDD → ADR)

```yaml
traceability:
  tags:
    - "@adr: ADR-NN"
  originating_topic: "@prd: PRD.NN.14.xxxx"  # PRD ADR topic elaboration (primary source)
  upstream:
    - "@bdd: BDD.NN.03.xxxx"     # BDD scenarios that informed this decision
    - "@ears: EARS.NN.03.xxxx"   # EARS requirements related to this decision
    - "@prd: PRD.NN.14.xxxx"    # PRD ADR topic elaboration
    - "@brd: BRD.NN.08.xxxx"    # BRD ADR topic (business-level origin)
```

### Downstream Traceability (ADR → SYS/REQ/SPEC)

```yaml
  downstream_expected:
    - type: SYS
      layer: 6
      description: "System requirements implementing this architecture decision"
    - type: REQ
      layer: 7
      description: "Atomic requirements decomposed from ADR decisions"
    - type: SPEC
      layer: 9
      description: "Technical specifications implementing ADR architecture"
```

### Embed from creation/validation rules

| Source | Embed in | Content |
|--------|----------|---------|
| Creation Rules: Context-Decision-Consequences structure | `context/decision/consequences._guidance` | Required subsections |
| Creation Rules: Alternatives format | `alternatives._guidance` | Pros/cons/cost/fit per option |
| Creation Rules: ADR status lifecycle | `document_control._guidance` | Proposed→Accepted→Deprecated→Superseded |
| Creation Rules: Architecture flow diagrams | `architecture_flow._guidance` | Mermaid diagram requirements |
| Validation Rules: SYS-Ready scoring | `metadata.validation._guidance` | Score thresholds |
| Quality Gate: Quality checks | Validation stays in mcp_ucx tools | Not embedded |

---

## Phase 3: Archive Deprecated Files

Move to `05_ADR/ADR_v1_archive/`:

- `ADR-MVP-TEMPLATE.md`
- `ADR-MVP-TEMPLATE.yaml`
- `ADR_MVP_SCHEMA.yaml`
- `ADR_MVP_CREATION_RULES.md`
- `ADR_MVP_VALIDATION_RULES.md`
- `ADR_MVP_QUALITY_GATE_VALIDATION.md`
- `ADR-MVP-TEMPLATE_FIX_PLAN.md`
- `ADR-00_TRACEABILITY_MATRIX-TEMPLATE.md`
- `ADR_AI_VALIDATION_DECISION_GUIDE.md`
- `ADR_VALIDATION_STRATEGY.md`
- `ADR_VALIDATION_COMMANDS.md`
- `REVIEW_REPORT.md`
- `FIXES_SUMMARY.md`
- `examples/`
- `scripts/`
- `README.md` (old version)
- `.backup_2026-02-26/` → `ADR_v1_archive/backup_2026-02-26/`

**DO NOT archive**:
- `ADR-00_index.md` (active registry)
- `ADR-00_ai_powered_documentation_assistant_architecture.md` (active ADR instance)
- `ADR-CTR_SEPARATE_FILES_POLICY.md` (active ADR instance)

---

## Phase 4: Update ADR-00_index.md

- Update template link to `ADR-TEMPLATE.yaml`
- Update validation commands to mcp_ucx tools
- Remove references to archived files

---

## Phase 5: Create New README.md

Same structure as other layers:
- Files table (including active ADR instances)
- C4 position (decision bridge between Container and Component)
- Template sync rule
- MCP tools reference
- ADR status lifecycle (Proposed→Accepted→Deprecated→Superseded)
- Element ID format
- Upstream traceability (BDD/EARS/PRD/BRD cumulative tags)
- Archive note

---

## Phase 6: Update mcp_ucx

- Copy `ADR-TEMPLATE.yaml` to `mcp_ucx/templates/ADR-TEMPLATE.yaml`
- Remove `mcp_ucx/templates/ADR-MVP-TEMPLATE.md`
- Check BDD/EARS/PRD/BRD prompts for stale ADR references (grep showed none)
- Check ADR prompts for old patterns (grep showed none)
- No source code changes needed

---

## Phase 7: Cross-Reference Updates

- `BDD-TEMPLATE.yaml` downstream_expected: verify ADR description
- `EARS-TEMPLATE.yaml`: verify no direct ADR downstream (EARS→BDD→ADR)
- `PRD-TEMPLATE.yaml` downstream_expected: verify ADR description
- `BRD-TEMPLATE.yaml` downstream_expected: verify ADR description
- `BRD-00_GLOSSARY.md`: verify ADR = "Architecture Decision Record"

---

## Phase 8: Validation, Documentation, Changelog, Roadmap

- Run mcp_ucx test suite
- Verify ADR template resolves: `resolve_template_path(layer_dir, "ADR", ".yaml")`
- Create `changelog/CHANGELOG_v0.6.0.md`
- Update `roadmap/ROADMAP.md`: current → v0.6.0, renumber API executors to v0.7.0
- Mark plan complete

---

## Key Differences from Previous Migrations

| Aspect | BRD | PRD | EARS | BDD | ADR |
|--------|-----|-----|------|-----|-----|
| Starting sections | 18 | 21+3 | 6 | Feature+YAML | 11 |
| Final sections | 15 | 15 | 5+glossary | 5 | 10+glossary+appendix |
| C4 level | Context | Container | Transition | Transition | Decision bridge |
| Readiness score | PRD-Ready | EARS-Ready | BDD-Ready | ADR-Ready | SYS-Ready |
| Source lines | 5,573 | 4,616 | 2,988 | 4,108 | 3,118 |
| Active instances to keep | 0 | 0 | 0 | 0 | 2 (ADR-00_*, ADR-CTR_*) |
| mcp_ucx code changes | 5 files | 0 | 0 | 0 | 0 |

---

## Decisions (Resolved)

1. **Section 11 (Lifecycle)**: Move to appendix (consistent with BRD/EARS pattern).
2. **Active ADR instances**: Keep in directory (NOT archived). Only template/rules/support archived.
3. **Architecture flow diagrams**: ADR uses C4-L2/L3 transition diagrams showing the
   decision's impact on system architecture. Documented in `diagram_standard`.
