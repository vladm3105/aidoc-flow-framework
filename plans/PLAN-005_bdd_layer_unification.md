# PLAN-005: BDD Layer Unification

**Status**: Complete
**Created**: 2026-03-29
**Scope**: Unify BDD (Layer 4) into single YAML template, same approach as BRD/PRD/EARS
**Depends on**: BRD (v0.2.0), PRD (v0.3.0), EARS (v0.4.0), mcp_ucx naming (v0.2.1) — all complete
**Risk**: Low — follows proven BRD/PRD/EARS pattern. BDD instances are `.feature` but the template is YAML (AI generates Gherkin from YAML guidance)

---

## Problem

BDD layer has the same dual-file pattern plus a unique challenge — Gherkin syntax:

| File | Lines | Role |
|------|-------|------|
| `BDD-MVP-TEMPLATE.feature` | 180 | Gherkin template (executable scenarios) |
| `BDD-MVP-TEMPLATE.yaml` | 259 | YAML metadata structure |
| `BDD_MVP_SCHEMA.yaml` | 628 | Validation schema |
| `BDD_MVP_CREATION_RULES.md` | 1,270 | Authoring guidance |
| `BDD_MVP_VALIDATION_RULES.md` | 815 | Post-creation validation |
| `BDD_MVP_QUALITY_GATE_VALIDATION.md` | 956 | Quality gates |
| **Total** | **4,108** | 6 files to consolidate |

Additionally to archive:

| File | Lines | Reason |
|------|-------|--------|
| `BDD-MVP-TEMPLATE_FIX_PLAN.md` | 509 | Completed fix tracking |
| `BDD-00_TRACEABILITY_MATRIX-TEMPLATE.md` | 537 | Redundant (per-BDD traceability + AI-generated) |
| `BDD_GENERATION_CHECKLIST.md` | 414 | Embed key rules as `_guidance` |
| `BDD_PRE_GENERATION_CHECKLIST.md` | 285 | Embed key rules as `_guidance` |
| `BDD_AI_AGENT_EXTENSION.md` | 245 | Embed as `_guidance` for AI-agent BDD |
| `BDD_AI_VALIDATION_DECISION_GUIDE.md` | 65 | Empty scaffold |
| `BDD_VALIDATION_STRATEGY.md` | 72 | References scripts, not mcp_ucx |
| `BDD_VALIDATION_COMMANDS.md` | 67 | References scripts, not mcp_ucx |
| `BDD-AGGREGATOR-TEMPLATE.feature` | 83 | Section splitting template — embed as `_guidance` |
| `REVIEW_REPORT.md` | 185 | Historical review report |
| `FIXES_SUMMARY.md` | 114 | Historical fix summary |
| `examples/` (3 files) | 1,121 | Old format examples |
| `scripts/` (9 files) | ~2,445 | Validation via mcp_ucx |
| `.backup_2026-02-26/` | — | Historical backup |
| `backup_20260208_162126/` | — | Historical backup |
| `README.md` | 609 | Old 609-line version |

---

## Design Decision: Single YAML Template (No .feature template)

BDD instances (actual test files) are `.feature` — but the **template** is YAML,
same as BRD/PRD/EARS. The AI generates valid Gherkin `.feature` instances from
YAML guidance, just as it generates `.md` BRD instances from YAML guidance.

**Rationale**:
- Consistency with BRD/PRD/EARS — all layers use single YAML template
- `resolve_template_path` already works with `.yaml` — no mcp_ucx code changes
- Gherkin syntax examples live inside `_guidance` and `_example` fields
- The template defines structure and rules; actual `.feature` files are instances

---

## Target State

```text
04_BDD/
├── BDD-TEMPLATE.yaml      ← single source of truth (metadata + Gherkin guidance)
├── BDD-00_index.md         ← BDD registry (keep, update refs)
├── README.md               ← new, concise (~80 lines)
└── BDD_v1_archive/         ← all deprecated files
```

---

## Phase 1: Section Analysis

BDD `.feature` files don't have numbered sections like BRD/PRD/EARS.
They have: Feature → Background → Scenario/Scenario Outline → tags.

The YAML template defines the metadata structure. Key sections for YAML:

| # | Section |
|---|---------|
| 1 | Document Control (metadata, ADR-Ready score, upstream refs) |
| 2 | Feature Definition (feature name, description, tags) |
| 3 | Scenario Structure (Given-When-Then patterns, scenario outlines) |
| 4 | Traceability (upstream EARS/PRD/BRD tags, downstream ADR) |
| 5 | Glossary (flat terms list) |

---

## Phase 1B: C4 Model Position

BDD (like EARS) is a **refinement step**, not a C4 level. BDD formalizes the
Context→Container transition alongside EARS:
- EARS: formal WHEN-THE-SHALL-WITHIN requirements
- BDD: executable Given-When-Then test scenarios from EARS

No `c4_level.value` — use `_guidance` only.

---

## Phase 2: Create BDD-TEMPLATE.yaml

Apply BRD/PRD/EARS conventions:
- `_guidance`, `_antipatterns`, `_note`, `_example` fields
- `metadata.c4_level`: `_guidance` only (refinement step, no C4 level)
- `metadata.diagram_standard`: sequence diagrams for scenario flows
- `metadata.validation.tool: sdd_validate` / `server: mcp_ucx`
- `metadata.deliverable_type`: inherited from upstream
- `metadata.id_standard`: `{doc_type}.{doc_id}.{section_id}.{hash}` — but BDD scenarios
  traditionally use `BDD.NN.14.SS` (element type 14 = Scenario). Migrate to hash-based:
  `BDD.NN.03.xxxx` (Section 3 = Scenario Structure).
- `document_control.adr_ready_score` (downstream is ADR)
- `document_control.ears_reference`: `@ears: EARS.NN.03.xxxx`

### Gherkin syntax in `_guidance` and `_example` fields

Embed complete Gherkin reference patterns directly in the YAML:
- Feature header with tags → `feature_definition._example`
- Background section → `scenario_structure._example`
- Scenario with Given-When-Then → `scenario_structure._example`
- Scenario Outline with Examples table → `scenario_structure._example`
- Traceability tag comments → `traceability._guidance`

**CRITICAL**: `scenario_structure._example` must include a COMPLETE valid Gherkin block
(Feature + Background + Scenario + Scenario Outline with Examples table) so the AI
can generate valid `.feature` instances. This replaces the old `.feature` template file.

### Execution environment

Embed in `metadata._guidance` or `document_control._guidance`:
- EXECUTION ENVIRONMENT: QA STAGING ONLY
- DO NOT run in CI pipeline — use UTEST/ITEST for CI
- BDD tests run AFTER staging deployment
- Part of QA workflow

### Embed from creation/validation rules

| Source | Embed in | Content |
|--------|----------|---------|
| Creation Rules: Gherkin patterns | `scenario_structure._guidance` | Given-When-Then format, scenario outlines |
| Creation Rules: Tag conventions | `feature_definition._guidance` | @tag format, required tags |
| Generation Checklist | `scenario_structure._guidance` | Key generation rules |
| Pre-Generation Checklist | `document_control._guidance` | Error prevention rules |
| AI Agent Extension | `scenario_structure._guidance` | AI-agent BDD patterns |
| Aggregator template | `feature_definition._guidance` | Section splitting rules |
| Validation Rules: ADR-Ready scoring | `metadata.validation._guidance` | Score thresholds |
| Quality Gate: Quality checks | Validation stays in mcp_ucx tools | Not embedded |

### Old element type codes to replace

- `BDD.NN.14.SS` (code 14 = Scenario) → `BDD.NN.03.xxxx` (Section 3, hash-based)

### Upstream Traceability (EARS → BDD)

```yaml
traceability:
  tags:
    - "@bdd: BDD-NN"
  upstream:
    - "@ears: EARS.NN.03.xxxx"   # links to EARS requirement
    - "@prd: PRD.NN.09.xxxx"    # links to PRD functional requirement
    - "@brd: BRD.NN.07.xxxx"    # links to BRD functional requirement
```

### Downstream Traceability (BDD → ADR)

```yaml
  downstream_expected:
    - type: ADR
      layer: 5
      description: "Architecture decisions informed by BDD scenario coverage"
```

---

## Phase 3: Archive Deprecated Files

Move to `04_BDD/BDD_v1_archive/`:

- `BDD-MVP-TEMPLATE.feature`
- `BDD-MVP-TEMPLATE.yaml`
- `BDD_MVP_SCHEMA.yaml`
- `BDD_MVP_CREATION_RULES.md`
- `BDD_MVP_VALIDATION_RULES.md`
- `BDD_MVP_QUALITY_GATE_VALIDATION.md`
- `BDD-MVP-TEMPLATE_FIX_PLAN.md`
- `BDD-00_TRACEABILITY_MATRIX-TEMPLATE.md`
- `BDD_GENERATION_CHECKLIST.md`
- `BDD_PRE_GENERATION_CHECKLIST.md`
- `BDD_AI_AGENT_EXTENSION.md`
- `BDD_AI_VALIDATION_DECISION_GUIDE.md`
- `BDD_VALIDATION_STRATEGY.md`
- `BDD_VALIDATION_COMMANDS.md`
- `BDD-AGGREGATOR-TEMPLATE.feature`
- `REVIEW_REPORT.md`
- `FIXES_SUMMARY.md`
- `examples/`
- `scripts/`
- `README.md` (old version)
- `.backup_2026-02-26/` → move into `BDD_v1_archive/backup_2026-02-26/`
- `backup_20260208_162126/` → move into `BDD_v1_archive/backup_20260208/`

Create `BDD_v1_archive/README.md` with migration notes.

---

## Phase 4: Update BDD-00_index.md

- Remove references to archived files (`BDD-MVP-TEMPLATE.feature`)
- Update validation commands to mcp_ucx tools
- Update template link to `BDD-TEMPLATE.yaml`
- Fix cross-layer refs that point to old template names in other layers
  (e.g., `REQ-MVP-TEMPLATE.md`, `SPEC-MVP-TEMPLATE.yaml` — update or remove)

---

## Phase 5: Create New README.md

Same structure as BRD/PRD/EARS README:
- Files table (single YAML template; BDD instances are .feature files)
- C4 position (refinement step alongside EARS)
- Template sync rule (canonical → `mcp_ucx/templates/`)
- MCP tools reference
- Gherkin syntax quick reference (Given-When-Then)
- Element ID format
- Upstream traceability (EARS/PRD/BRD cumulative tags)
- Archive note

---

## Phase 6: Update mcp_ucx

- Copy `BDD-TEMPLATE.yaml` to `mcp_ucx/templates/BDD-TEMPLATE.yaml`
- Remove `mcp_ucx/templates/BDD-MVP-TEMPLATE.feature`
- No source code changes needed — `resolve_template_path` finds `.yaml` natively
- Check `prompts/templates/creation/UCC_PROMPT_BDD.md` — may need minimal changes
  (grep shows no old template/ID refs; focuses on Gherkin syntax and personas)
- Check `prompts/templates/review/UCR_PROMPT_BDD.md` — may need minimal changes
- Check `prompts/templates/remediation/UCRem_PROMPT_BDD.md` — may need minimal changes
  (grep shows no old element ID convention section unlike EARS prompt)
- Verify during implementation; update only what references old patterns

---

## Phase 7: Cross-Reference Updates

- `EARS-TEMPLATE.yaml` downstream_expected: verify BDD description
- `PRD-TEMPLATE.yaml` downstream_expected: verify BDD description
- `BRD-TEMPLATE.yaml` downstream_expected: verify BDD description (already split as separate entry)
- `BRD-00_GLOSSARY.md`: verify BDD definition

---

## Phase 8: Validation, Documentation, Changelog, Roadmap

- Run mcp_ucx test suite: `python -m pytest tests/ -v`
- Verify BDD template resolves: `resolve_template_path(layer_dir, "BDD", ".yaml")`
- Verify EARS parity and other layer tests still pass
- Create `changelog/CHANGELOG_v0.5.0.md`
- Update `roadmap/ROADMAP.md`:
  - Current version → 0.5.0
  - v0.5.0 added to completed releases
  - Renumber API executors to v0.6.0

---

## Key Differences from BRD/PRD/EARS Migration

| Aspect | BRD | PRD | EARS | BDD |
|--------|-----|-----|------|-----|
| Starting files | 18 sections | 21 + 3 appendices | 6 sections | Feature + YAML |
| Final structure | 15 sections | 15 sections | 5 + glossary | 5 sections + Gherkin ref |
| Primary format | YAML | YAML | YAML | YAML (instances are .feature) |
| Source lines | 5,573 | 4,616 | 2,988 | 4,108 |
| C4 level | Context | Container | Transition | Transition |
| Readiness score | PRD-Ready | EARS-Ready | BDD-Ready | ADR-Ready |
| Unique feature | Business capabilities | User stories | WHEN-THE-SHALL | Given-When-Then |
| mcp_ucx code change | 5 source files | 1 prompt | 1 prompt | 3 prompts (no code change) |

---

## Decisions (Resolved 2026-03-29)

1. **Single YAML template**: No `.feature` template file. YAML is the authority; Gherkin
   syntax lives in `_guidance` and `_example` fields. AI generates `.feature` instances
   from YAML guidance. No mcp_ucx code changes needed.

2. **Scenario ID format**: Migrate to `BDD.NN.03.xxxx` (section-based hash) for
   consistency with BRD/PRD/EARS. Old `BDD.NN.14.SS` (type code 14) is deprecated.
