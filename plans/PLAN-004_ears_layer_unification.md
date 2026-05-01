# PLAN-004: EARS Layer Unification

**Status**: Complete
**Created**: 2026-03-29
**Scope**: Unify EARS (Layer 3) into single YAML template, same approach as BRD/PRD
**Depends on**: BRD (v0.2.0), PRD (v0.3.0), mcp_ucx naming (v0.2.1) — all complete
**Risk**: Low — follows proven BRD/PRD migration pattern

---

## Problem

EARS layer has the same dual-file pattern:

| File | Lines | Role |
|------|-------|------|
| `EARS-MVP-TEMPLATE.md` | 264 | Human narrative template (6 sections) |
| `EARS-MVP-TEMPLATE.yaml` | 292 | YAML structure for autopilot |
| `EARS_MVP_SCHEMA.yaml` | 350 | Validation schema |
| `EARS_MVP_CREATION_RULES.md` | 706 | Authoring guidance |
| `EARS_MVP_VALIDATION_RULES.md` | 690 | Post-creation validation |
| `EARS_MVP_QUALITY_GATE_VALIDATION.md` | 686 | Quality gates |
| **Total** | **2,988** | 6 files to consolidate |

Additionally to archive:

| File | Lines | Reason |
|------|-------|--------|
| `EARS-MVP-TEMPLATE_FIX_PLAN.md` | 871 | Completed fix tracking (historical) |
| `EARS-00_TRACEABILITY_MATRIX-TEMPLATE.md` | 552 | Redundant (per-EARS traceability + AI-generated) |
| `EARS_AI_VALIDATION_DECISION_GUIDE.md` | 65 | Empty scaffold |
| `EARS_VALIDATION_STRATEGY.md` | 72 | References scripts, not mcp_ucx |
| `EARS_VALIDATION_COMMANDS.md` | 66 | References scripts, not mcp_ucx |
| `FIXES_SUMMARY.md` | 80 | Historical fix report |
| `examples/` (2 files) | 894 | Old format examples |
| `scripts/` (9 files) | ~1,918 | Not deprecated yet, but validation via mcp_ucx |
| `.backup_2026-02-26/` (13 files) | ~3,046 | Historical backup |
| `README.md` | 329 | Old 329-line version |

---

## Target State

```text
03_EARS/
├── EARS-TEMPLATE.yaml      ← single source of truth (~400-500 lines)
├── EARS-00_index.md         ← EARS registry (keep, update refs)
├── README.md                ← new, concise (~80 lines)
└── EARS_v1_archive/         ← all deprecated files
```

---

## Phase 1: Section Analysis

EARS has 6 sections (already lean). Evaluate for the unified template.

### Keep (all 6 — EARS is already minimal)

| # | Section | Rationale |
|---|---------|-----------|
| — | Document Control | Standard metadata |
| 1 | Purpose and Context | EARS scope, PRD reference |
| 2 | EARS in Development Workflow | Position in SDD workflow |
| 3 | Requirements | Core WHEN-THE-SHALL-WITHIN requirements |
| 4 | Quality Attributes | Performance/reliability in EARS format |
| 5 | Traceability | Upstream PRD/BRD tags, downstream BDD |
| 6 | References | Cross-references |

### Evaluate for merge

| Section | Assessment |
|---------|-----------|
| 2 (Workflow) | Could merge into introduction `_guidance` — workflow is template-level info |
| 6 (References) | Could merge into traceability section |

### Proposed structure: 5 sections (merge workflow into intro, refs into traceability)

| # | Section |
|---|---------|
| 1 | Document Control |
| 2 | Purpose and Context |
| 3 | Requirements (WHEN-THE-SHALL-WITHIN) |
| 4 | Quality Attributes |
| 5 | Traceability (absorbs References) |
| — | Glossary (flat terms list, consistent with BRD/PRD) |

---

## Phase 1B: Incorporate PRD EARS Appendix Content

The PRD migration preserved EARS Enhancement content in `tmp/EARS_APPENDIX_FROM_PRD.md`:
- Timing Profile Matrix (p50/p95/p99)
- Boundary Value Matrix
- State Transition Diagram template
- Fallback Path Documentation
- EARS-Ready Checklist
- Timing vocabulary replacements (real-time → p50 <100ms, etc.)

Embed as `_guidance` in Section 3 (Requirements) and Section 4 (Quality Attributes).

Note: `tmp/` is gitignored — the file exists locally but is NOT tracked.
Read content directly during Phase 2 template creation. No cleanup step needed.

---

## Phase 2: Create EARS-TEMPLATE.yaml

Apply BRD/PRD template conventions:
- `_guidance`, `_antipatterns`, `_note`, `_example` fields
- `metadata.c4_level`: NO value assigned — EARS is a refinement step between
  Context (BRD) and Container (PRD), not a C4 level itself. Use `_guidance` only
  to explain EARS' transitional role in formalizing business requirements.
- `metadata.diagram_standard` with C4-aligned diagram types (EARS uses state diagrams
  and sequence diagrams for requirement visualization, not C4 container/component)
- `metadata.validation.tool: sdd_validate` / `server: mcp_ucx`
- `metadata.deliverable_type`: inherited from upstream PRD (which inherits from BRD)
- `metadata.id_standard` with SHA256 hash algorithm: `{doc_type}.{doc_id}.{section_id}.{hash}`
- `document_control.bdd_ready_score` field (analogous to BRD's prd_ready_score)

### Old element type codes to replace

Old EARS template uses sequential type codes:
- `EARS.NN.25.SS` (code 25 for EARS statements) → `EARS.NN.03.xxxx` (Section 3)
- `EARS.NN.02.SS` (code 02 for performance QA) → `EARS.NN.04.xxxx` (Section 4)
- `EARS.NN.03.SS` (code 03 for security QA) → `EARS.NN.04.xxxx` (Section 4)
- `EARS.NN.04.SS` (code 04 for reliability QA) → `EARS.NN.04.xxxx` (Section 4)

All quality attributes share Section 4; hash differentiates them.

### Threshold references — fix PRD section pointers

Old: `@threshold: PRD.NN.timeout.category.key | PRD Section 20.1`
PRD Section 20 (EARS appendix) was removed in v0.3.0.
New: Reference thresholds via `@threshold:` tag convention only, no section numbers.

### Workflow string

Use correct workflow: `BRD → PRD → EARS → BDD → ADR → SYS → REQ → CTR → SPEC → TSPEC → TASKS → Code`

### Element ID Format

```text
Format: EARS.{doc_id}.{section_id}.{hash}
Example: EARS.01.03.c4d8
```

Hash derived from EARS content, NOT upstream PRD content.

### Upstream Traceability (PRD → EARS)

```yaml
traceability:
  tags:
    - "@ears: EARS-NN"
  upstream:
    - "@prd: PRD.NN.09.xxxx"    # links to PRD functional requirement
    - "@brd: BRD.NN.07.xxxx"    # links to BRD functional requirement
```

### Downstream Traceability (EARS → BDD)

```yaml
  downstream_expected:
    - type: BDD
      layer: 4
      description: "Given-When-Then test scenarios from EARS requirements"
```

### EARS Syntax Guidance

Embed WHEN-THE-SHALL-WITHIN patterns, timing vocabulary, boundary values as `_guidance`
in Section 3 (Requirements).

### Embed from creation/validation rules

| Source | Embed in | Content |
|--------|----------|---------|
| Creation Rules: EARS syntax patterns | `requirements._guidance` | WHEN-THE-SHALL-WITHIN format |
| Creation Rules: Quality attribute patterns | `quality_attributes._guidance` | Performance/reliability in EARS format |
| PRD EARS Appendix: Timing profiles | `quality_attributes._guidance` | p50/p95/p99, timing vocabulary |
| PRD EARS Appendix: Boundary values | `requirements._guidance` | Boundary value matrix pattern |
| PRD EARS Appendix: State transitions | `requirements._guidance` | State diagram template |
| PRD EARS Appendix: Fallback paths | `requirements._guidance` | Fallback documentation pattern |
| Validation Rules: BDD-Ready scoring | `metadata.validation._guidance` | Score thresholds |
| Quality Gate: Quality checks | Validation stays in mcp_ucx tools | Not embedded |

---

## Phase 3: Archive Deprecated Files

Move to `03_EARS/EARS_v1_archive/`:

- `EARS-MVP-TEMPLATE.md`
- `EARS-MVP-TEMPLATE.yaml`
- `EARS_MVP_SCHEMA.yaml`
- `EARS_MVP_CREATION_RULES.md`
- `EARS_MVP_VALIDATION_RULES.md`
- `EARS_MVP_QUALITY_GATE_VALIDATION.md`
- `EARS-MVP-TEMPLATE_FIX_PLAN.md`
- `EARS-00_TRACEABILITY_MATRIX-TEMPLATE.md`
- `EARS_AI_VALIDATION_DECISION_GUIDE.md`
- `EARS_VALIDATION_STRATEGY.md`
- `EARS_VALIDATION_COMMANDS.md`
- `FIXES_SUMMARY.md`
- `examples/`
- `scripts/`
- `README.md` (old version)
- `.backup_2026-02-26/` (consolidate into archive)

Create `EARS_v1_archive/README.md` with migration notes.

---

## Phase 4: Update EARS-00_index.md

- Remove references to archived files
- Update validation commands to mcp_ucx tools
- Update template link to `EARS-TEMPLATE.yaml`
- Fix EARS acronym: "Event-Action-Response-State" → "Easy Approach to Requirements Syntax"
- Update copy command to mcp_ucx `sdd_create` tool reference

---

## Phase 5: Create New README.md

Same structure as BRD/PRD README:
- Files table
- C4 Model Mapping (EARS formalizes Context→Container transition)
- Template sync rule (canonical → `mcp_ucx/templates/`)
- MCP tools reference
- EARS syntax quick reference (WHEN-THE-SHALL-WITHIN)
- Element ID format
- Archive note

---

## Phase 6: Update mcp_ucx

- Copy `EARS-TEMPLATE.yaml` to `mcp_ucx/templates/EARS-TEMPLATE.yaml`
- Remove `mcp_ucx/templates/EARS-MVP-TEMPLATE.md`
- Update `prompts/templates/creation/UCC_PROMPT_EARS.md` — section structure (6→5+glossary),
  template refs (`EARS-MVP-TEMPLATE.md` → `EARS-TEMPLATE.yaml`), element ID format
- Update `prompts/templates/review/UCR_PROMPT_EARS.md` — section cross-references,
  template name refs
- Update `prompts/templates/remediation/UCRem_PROMPT_EARS.md` — element ID format
  (old type codes → hash-based), section numbers, template name refs
- No source code changes needed — PLAN-002 naming migration already in place
- Note: `UCC_PROMPT_EARS.md` focuses on EARS syntax and personas, not template
  structure — may need minimal changes only (verify during implementation)
- Note: `BDD-MVP-TEMPLATE.feature` uses `.feature` extension — `resolve_template_path`
  won't find it. Document as future BDD migration concern, not EARS scope.

---

## Phase 7: Cross-Reference Updates

- `PRD-TEMPLATE.yaml` downstream_expected: verify EARS description is current
- `BRD-TEMPLATE.yaml` downstream_expected: split `"EARS/BDD"` (layer "3/4") into
  two separate entries: EARS (layer 3) and BDD (layer 4)
- `BRD-00_GLOSSARY.md`: verify EARS acronym is "Easy Approach to Requirements Syntax"
- `document_control.source_document`: use new PRD hash format `@prd: PRD.NN.09.xxxx`

---

## Phase 8: Validation, Documentation, Changelog, Roadmap

- Run mcp_ucx test suite: `python -m pytest tests/ -v`
- Verify EARS template resolves: `resolve_template_path(layer_dir, "EARS", ".yaml")`
- Verify EARS parity validation still works (trigger clause + actor clause check
  in `validation/runner.py` lines 206-216 — no code change, just verify)
- Create `changelog/CHANGELOG_v0.4.0.md` with:
  - EARS template unification summary
  - Section structure changes (6→5+glossary)
  - PRD EARS appendix incorporation
  - Hash-based ID migration
  - Files archived
- Update `roadmap/ROADMAP.md`:
  - Current version → 0.4.0
  - v0.4.0 added to completed releases
  - Renumber API executors to v0.5.0

---

## Key Differences from BRD/PRD Migration

| Aspect | BRD | PRD | EARS |
|--------|-----|-----|------|
| Starting sections | 18 | 21 + 3 appendices | 6 |
| Final sections | 15 | 15 | 5 + glossary |
| Sections removed | 6 | 9 | 1 (merged) |
| Source lines to consolidate | 5,573 | 4,616 | 2,988 |
| C4 level | Context | Container | Transition (no C4 level — refinement step) |
| Readiness score | PRD-Ready | EARS-Ready | BDD-Ready |
| Unique feature | Business capabilities | User stories, customer content | WHEN-THE-SHALL-WITHIN syntax |
| PRD appendix content | N/A | EARS appendix moved out | Incoming from PRD |
| mcp_ucx prompts | 1 to update | 3 to update | 3 to update |

---

## Known Issues (Not in EARS Scope)

- `mcp_ucx/templates/BDD-MVP-TEMPLATE.feature` uses `.feature` extension.
  `resolve_template_path` tries `.yaml` then `.md` — won't find `.feature`.
  Address during BDD layer migration.

---

## Decisions Required

None — EARS is already lean (6 sections). The only merge (workflow into intro, refs into traceability) is straightforward.
