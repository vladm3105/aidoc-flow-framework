# PLAN-003: PRD Layer Unification

**Status**: Complete
**Created**: 2026-03-29
**Scope**: Unify PRD (Layer 2) into single YAML template, same approach as BRD (PLAN-002)
**Depends on**: BRD unification (v0.2.0) and mcp_ucx naming migration (v0.2.1) — both complete
**Risk**: Low — follows proven BRD migration pattern

---

## Problem

PRD layer has the same dual-file problem BRD had before v0.2.0:

| File | Lines | Role |
|------|-------|------|
| `PRD-MVP-TEMPLATE.md` | 731 | Human narrative template (21 sections) |
| `PRD-MVP-TEMPLATE.yaml` | 240 | Minimal YAML (structure only, incomplete) |
| `PRD_MVP_SCHEMA.yaml` | 380 | Validation schema |
| `PRD_MVP_CREATION_RULES.md` | 1,268 | Authoring guidance |
| `PRD_MVP_VALIDATION_RULES.md` | 1,024 | Post-creation validation |
| `PRD_MVP_QUALITY_GATE_VALIDATION.md` | 973 | Quality gates |
| **Total** | **4,616** | 6 files to consolidate |

Additionally 8 files to archive:

| File | Lines | Reason |
|------|-------|--------|
| `PRD-MVP-TEMPLATE_FIX_PLAN.md` | 1,060 | Completed fix tracking (historical) |
| `PRD-00_threshold_registry_template.md` | 400 | Deprecated (inline thresholds now) |
| `PRD-00_TRACEABILITY_MATRIX-TEMPLATE.md` | 488 | Redundant (per-PRD Section 18 + AI-generated) |
| `PRD_VALIDATION_STRATEGY.md` | 66 | References deprecated scripts |
| `PRD_VALIDATION_COMMANDS.md` | 61 | References deprecated scripts |
| `PRD_AI_VALIDATION_DECISION_GUIDE.md` | 65 | Empty scaffold |
| `examples/PRD-01.0_example.md` | 221 | Old format example |
| `scripts/` (8 files) | ~2,100 | All deprecated, validation via mcp_ucx |

---

## Target State

```
02_PRD/
├── PRD-TEMPLATE.yaml      ← single source of truth (~800-1000 lines)
├── PRD-00_index.md         ← PRD registry (keep, update refs)
├── README.md               ← new, concise (~80 lines)
└── PRD_v1_archive/         ← all deprecated files
```

---

## Phase 1: Section Analysis — What PRD Owns vs Downstream

PRD has 21 sections + 3 appendices. Apply same downstream-ownership filter as BRD.

### Keep (PRD-layer concerns)

| # | Section | Rationale |
|---|---------|-----------|
| 1 | Document Control | Standard metadata |
| 2 | Executive Summary | Product overview |
| 3 | Problem Statement | Product-level problem (expands BRD Section 4) |
| 4 | Target Audience & User Personas | PRD owns personas (BRD only has target_users) |
| 5 | Success Metrics (KPIs) | Product-level metrics |
| 6 | Goals & Objectives | Product goals aligned to BRD |
| 7 | Scope & Requirements | Product scope, dependencies |
| 8 | User Stories & User Roles | PRD owns detailed user stories |
| 9 | Functional Requirements | Product-level FRs (technical detail of BRD FRs) |
| 10 | Customer-Facing Content | Messaging, notifications, error text |
| 11 | Acceptance Criteria | Product acceptance criteria |
| 12 | Constraints & Assumptions | Product-level constraints |
| 13 | Risk Assessment | Product risks |
| 18 | Traceability | Upstream BRD links, downstream EARS/BDD/ADR links |

### Remove (downstream-owned or merged)

| # | Section | Action | Owner |
|---|---------|--------|-------|
| 14 | Success Definition | MERGE into Section 5 (KPIs) + Section 11 (Acceptance Criteria) | — |
| 15 | Stakeholders & Communication | REMOVE — defer to project management | PM artifacts |
| 16 | Implementation Approach | REMOVE — state timeline constraints in Section 12 (Constraints) | IPLAN/TASKS (Layer 11-12) |
| 17 | Budget & Resources | REMOVE — covered by BRD Section 4 (cost_benefit) | BRD (Layer 1) |
| 19 | References | MERGE into Section 18 (Traceability) | — |
| 20 | EARS Enhancement Appendix | MOVE to EARS layer (03_EARS). Add _note in traceability | EARS (Layer 3) |
| 21 | Quality Assurance & Testing | REMOVE — state testing expectations as one-liners | TSPEC (Layer 10) |
| App A | Future Roadmap | REMOVE — duplicate of BRD lifecycle appendix | BRD |
| App C | MVP Lifecycle Reference | REMOVE — duplicate of BRD lifecycle appendix | BRD |

### Keep

| # | Section | Keep as |
|---|---------|--------|
| App B | Glossary | Flat terms list (same as BRD Section 15) |

### Final structure: 15 sections + glossary (down from 21 + 3 appendices)

| # | Section |
|---|---------|
| 1 | Document Control |
| 2 | Executive Summary |
| 3 | Problem Statement |
| 4 | Target Audience & User Personas |
| 5 | Success Metrics & KPIs (absorbs old Section 14) |
| 6 | Goals & Objectives |
| 7 | Scope & Requirements |
| 8 | User Stories & User Roles |
| 9 | Functional Requirements |
| 10 | Customer-Facing Content & Messaging |
| 11 | Acceptance Criteria (absorbs old Section 14) |
| 12 | Constraints & Assumptions |
| 13 | Risk Assessment |
| 14 | Traceability (absorbs old Section 19) |
| 15 | Glossary |
| — | Appendix: EARS cross-reference note (points to 03_EARS) |

---

## Phase 1B: Embed C4 Model Mapping

Add `_guidance` note in `metadata` section of both BRD-TEMPLATE.yaml and PRD-TEMPLATE.yaml,
plus update both layer READMEs. This establishes the abstraction boundary for each layer.

### C4 mapping to embed

```yaml
metadata:
  c4_level:
    _guidance: |
      SDD layers map to C4 architecture model zoom levels:
        Context (BRD)    — business environment, actors, boundaries
          └─ EARS/BDD    — formalize Context→Container transition
        Container (PRD)  — product features, functional blocks
          └─ ADR         — decisions that shape Component architecture
        Component (SYS)  — system structure, interfaces, quality attributes
          └─ REQ/CTR     — decompose Component→Code into atomic units
        Code (SPEC)      — implementation-ready specifications
          └─ TASKS/TSPEC — implementation and test plans

      This layer is [Context|Container] level. Content must stay at this
      zoom level — do not include details belonging to deeper levels.
    value: context  # context | container | component | code
```

### Files to update

| File | Change | Status |
|------|--------|--------|
| `ai_dev_ssd_flow/01_BRD/BRD-TEMPLATE.yaml` | `c4_level` with `value: context` | DONE |
| `ai_dev_ssd_flow/01_BRD/README.md` | C4 Model Mapping section | DONE |
| `mcp_ucx/templates/BRD-TEMPLATE.yaml` | Synced copy | DONE |
| `ai_dev_ssd_flow/02_PRD/PRD-TEMPLATE.yaml` | `c4_level` with `value: container` | Phase 2 |
| `ai_dev_ssd_flow/02_PRD/README.md` | C4 Model Mapping section | Phase 5 |

---

## Phase 2: Create PRD-TEMPLATE.yaml

Apply BRD template conventions:
- `_guidance`, `_antipatterns`, `_note`, `_example` fields
- `metadata.validation.tool: sdd_validate` / `server: mcp_ucx`
- `metadata.deliverable_type` with routing map (inherited from BRD)
- `metadata.id_standard` with SHA256 hash algorithm docs
- `document_control.ears_ready_score` field (analogous to BRD's `prd_ready_score`)
  Note: Old PRD had both SYS-Ready and EARS-Ready scores. Keep only `ears_ready_score` —
  EARS is the immediate downstream. SYS-Ready belongs in ADR or SYS layer (two layers down).
- `document_control.brd_reference` field using new hash format: `@brd: BRD.NN.07.xxxx`
- `@threshold:` tag convention documented in relevant `_guidance` fields
  (reference `THRESHOLD_NAMING_RULES.md` for full specification)

### Element ID Format

PRD element IDs use the same hash convention as BRD but scoped to PRD content:

```
Format: PRD.{doc_id}.{section_id}.{hash}
Example: PRD.01.09.b3f2
```

- `doc_id`: PRD document number (e.g., "01")
- `section_id`: section number from THIS template (1-15, not old 1-21)
- `hash`: SHA256 of `"{doc_id}:{section_id}:{title}:{description}"` from PRD content
- Hash is derived from PRD content, NOT from upstream BRD content

### Upstream Traceability Tags (BRD → PRD)

Each PRD must link to its source BRD via traceability tags using the new BRD hash format:

```yaml
traceability:
  tags:
    - "@prd: PRD-NN"
  upstream:
    - "@brd: BRD.NN.08.xxxx"    # links to BRD ADR topic
    - "@brd: BRD.NN.07.xxxx"    # links to BRD functional requirement
```

The `@brd:` tags use BRD's new hash-based IDs (Section 8 = ADR topics, Section 7 = FRs).
PRD features trace back to specific BRD elements, enabling bidirectional traceability.

### Downstream Traceability (PRD → EARS/BDD/ADR)

```yaml
  downstream_expected:
    - type: EARS
      layer: 3
      description: "Formal requirements from PRD features"
    - type: BDD
      layer: 4
      description: "Acceptance test scenarios"
    - type: ADR
      layer: 5
      description: "Architecture decisions from PRD traceability ADR topic elaboration"
```

### Section 14 merge details

Old Section 14 (Success Definition) splits into:
- **14.1 Go-Live Criteria** → New Section 11 `acceptance_criteria.launch_gates`
- **14.2 Post-Launch Validation** → New Section 5 `success_metrics.post_launch_validation`
- **14.3 Measurement Timeline** → Merge into existing Section 5.3 (Go/No-Go Decision Gate)
  which already has proceed/iterate/pivot/shutdown logic — avoid duplication

### Section 18 (Traceability) — update BRD references

Old PRD traceability uses `BRD.NN.32.01` (legacy sequential codes).
New PRD template must use `BRD.NN.08.xxxx` (hash-based, matching BRD-TEMPLATE.yaml Section 8).

### Section 6 (Goals & Objectives) — update element IDs

Old format: `PRD.NN.23.01` (element type code 23 = business objective).
New format: `PRD.NN.06.xxxx` (section 6, hash-based). All element IDs across
all sections must use new `PRD.NN.{section_id}.xxxx` format.

### Section 20 (EARS Enhancement) — preserve content

Copy EARS appendix content (Timing Profile Matrix, Boundary Value Matrix, State Transition
Diagram, Fallback Path Documentation, EARS-Ready Checklist) to `tmp/EARS_APPENDIX_FROM_PRD.md`
as holding file for EARS layer migration. Add `_note` in PRD traceability section pointing
to EARS layer.

### Embed from creation/validation rules

| Source | Embed in | Content |
|--------|----------|---------|
| Creation Rules: User story patterns | `user_stories._guidance` | Format, anti-patterns, acceptance criteria patterns |
| Creation Rules: FR structure | `functional_requirements._guidance` | Atomic FR format, testability criteria |
| Creation Rules: Persona template | `target_audience._guidance` | Persona structure, empathy map |
| Creation Rules: Threshold conventions | `functional_requirements._guidance` | `@threshold:` tag format and usage |
| Validation Rules: EARS-Ready scoring | `metadata.validation._guidance` | Score thresholds |
| README: ADR topic elaboration guidance | `traceability._guidance` | How PRD elaborates BRD ADR topics |
| Quality Gate: Quality checks | Validation stays in mcp_ucx tools | Not embedded |

---

## Phase 3: Archive Deprecated Files

Move to `02_PRD/PRD_v1_archive/`:

- `PRD-MVP-TEMPLATE.md`
- `PRD-MVP-TEMPLATE.yaml`
- `PRD_MVP_SCHEMA.yaml`
- `PRD_MVP_CREATION_RULES.md`
- `PRD_MVP_VALIDATION_RULES.md`
- `PRD_MVP_QUALITY_GATE_VALIDATION.md`
- `PRD-MVP-TEMPLATE_FIX_PLAN.md`
- `PRD-00_threshold_registry_template.md`
- `PRD-00_TRACEABILITY_MATRIX-TEMPLATE.md`
- `PRD_VALIDATION_STRATEGY.md`
- `PRD_VALIDATION_COMMANDS.md`
- `PRD_AI_VALIDATION_DECISION_GUIDE.md`
- `examples/`
- `scripts/`
- `README.md` (old 474-line version)
- Merge existing `archive/.backup_2026-02-26/` into `PRD_v1_archive/` (consolidate archives)

Create `PRD_v1_archive/README.md` with migration notes.

---

## Phase 4: Update PRD-00_index.md

- Remove references to archived files
- Update validation commands to mcp_ucx tools
- Update template link to `PRD-TEMPLATE.yaml`

---

## Phase 5: Create New README.md

Same structure as BRD README:
- Files table
- C4 Model Mapping (PRD = Container level)
- Template sync rule (canonical → `mcp_ucx/templates/`)
- MCP tools reference
- Element ID format
- Archive note

---

## Phase 6: Update mcp_ucx

- Copy `PRD-TEMPLATE.yaml` to `mcp_ucx/templates/PRD-TEMPLATE.yaml`
- Remove `mcp_ucx/templates/PRD-MVP-TEMPLATE.md`
- Update `prompts/templates/creation/UCC_PROMPT_PRD.md`:
  - 3 refs to `PRD-MVP-TEMPLATE.md` → `PRD-TEMPLATE.yaml`
  - Line 25: "exactly 21 numbered sections" → "exactly 15 numbered sections"
  - Update section list to match new 15-section structure
- No source code changes needed — PLAN-002 already broadened filters

---

## Phase 7: Cross-Reference Updates

- `BRD-TEMPLATE.yaml` downstream_expected: PRD description may need update
- `BRD-00_GLOSSARY.md` cross-references: update PRD template path
- Check other layer templates that reference PRD naming

---

## Phase 8: Validation and Documentation

- Run mcp_ucx test suite: `python -m pytest tests/ -v`
- Verify PRD template resolves: `resolve_template_path(layer_dir, "PRD", ".yaml")`
- Update `changelog/CHANGELOG_v0.3.0.md` (or patch version)
- Update `roadmap/ROADMAP.md`

---

## Key Differences from BRD Migration

| Aspect | BRD | PRD |
|--------|-----|-----|
| Starting sections | 18 | 21 + 3 appendices |
| YAML template completeness | Minimal (structure only) | Minimal (structure only) |
| Downstream sections to remove | 6 (user stories, QA, implementation, support, quality attrs, cost-benefit) | 9 (success def merged, stakeholders deferred, implementation, budget, references merged, EARS appendix moved, QA, future roadmap, lifecycle ref) |
| User stories | Removed (PRD owns) | Keep (PRD owns this) |
| Quality attributes detail | Removed (SYS owns) | N/A (PRD doesn't have this) |
| Customer-facing content | N/A | Keep (PRD owns this) |
| mcp_ucx code changes | 5 source files | 1 prompt file + template copy only |

---

## Estimated Effort

| Phase | Complexity |
|-------|-----------|
| Phase 1: Section analysis | Research only |
| Phase 2: Create template | Primary work (~800-1000 line YAML) |
| Phase 3: Archive files | Mechanical (mv commands) |
| Phase 4-5: Update index/README | Small edits |
| Phase 6: mcp_ucx updates | Template copy + 1 prompt file |
| Phase 7: Cross-refs | Grep + small edits |
| Phase 8: Validation | Test run + docs |

---

## Decisions (Resolved 2026-03-29)

1. **Section 14 (Success Definition)**: MERGE into Section 5 (KPIs) + Section 11 (Acceptance Criteria). Remove as standalone.
2. **Section 15 (Stakeholders & Communication)**: DEFER to project management artifacts. Remove from PRD template.
3. **Section 20 (EARS Enhancement Appendix)**: MOVE to EARS layer (03_EARS). Add `_note` in PRD traceability pointing to EARS. Handle during EARS migration.

**Final section count**: 15 sections + glossary appendix (down from 21 + 3 appendices).
