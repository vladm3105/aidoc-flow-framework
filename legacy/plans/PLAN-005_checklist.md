# PLAN-005 Implementation Checklist

**Plan**: PLAN-005_bdd_layer_unification.md
**Status**: Complete
**Date**: 2026-03-29

---

## Pre-Flight

- [ ] Run baseline tests:
  ```bash
  cd /opt/data/ucx_framework/mcp_ucx && python -m pytest tests/ --tb=short 2>&1 | tail -5
  ```
- [ ] Record baseline: `___` passed, `___` failed
- [ ] Read all 6 source files to consolidate:
  - [ ] `BDD-MVP-TEMPLATE.feature` (180 lines — Gherkin template)
  - [ ] `BDD-MVP-TEMPLATE.yaml` (259 lines — metadata)
  - [ ] `BDD_MVP_CREATION_RULES.md` (1,270 lines — authoring guidance)
  - [ ] `BDD_MVP_VALIDATION_RULES.md` (815 lines — validation)
  - [ ] `BDD_MVP_QUALITY_GATE_VALIDATION.md` (956 lines — quality gates)
  - [ ] `BDD_MVP_SCHEMA.yaml` (628 lines — schema)
- [ ] Read additional files for guidance extraction:
  - [ ] `BDD_GENERATION_CHECKLIST.md` (414 lines)
  - [ ] `BDD_PRE_GENERATION_CHECKLIST.md` (285 lines)
  - [ ] `BDD_AI_AGENT_EXTENSION.md` (245 lines)
  - [ ] `BDD-AGGREGATOR-TEMPLATE.feature` (83 lines)

---

## Phase 1: Section Analysis (Research)

- [ ] Confirm 5 sections for unified template:
  - [ ] Section 1: Document Control (metadata, ADR-Ready score, upstream refs)
  - [ ] Section 2: Feature Definition (feature name, description, tags)
  - [ ] Section 3: Scenario Structure (Given-When-Then, outlines, backgrounds)
  - [ ] Section 4: Traceability (upstream EARS/PRD/BRD, downstream ADR)
  - [ ] Section 5: Glossary (flat terms list)
- [ ] No sections to remove (BDD is already minimal)

---

## Phase 1B: C4 Model Position

- [ ] Confirm: BDD is refinement step alongside EARS (no C4 level value)
- [ ] Confirm: `_guidance` only in `c4_level` (same approach as EARS)

---

## Phase 2: Create BDD-TEMPLATE.yaml

- [ ] Create `ai_dev_ssd_flow/04_BDD/BDD-TEMPLATE.yaml`
- [ ] Template metadata:
  - [ ] `schema_version: "1.0"`
  - [ ] `document_type: "bdd-document"`
  - [ ] `layer: 4`
  - [ ] `total_sections: 5`
  - [ ] `c4_level`: `_guidance` only (refinement step, no value)
  - [ ] `diagram_standard`: sequence diagrams for scenario flows
  - [ ] `validation.tool: sdd_validate` / `server: mcp_ucx`
  - [ ] `deliverable_type`: inherited from upstream
  - [ ] `id_standard`: `{doc_type}.{doc_id}.{section_id}.{hash}`, SHA256
  - [ ] Execution environment note: QA STAGING ONLY, not CI pipeline
- [ ] Document control:
  - [ ] `adr_ready_score` field
  - [ ] `ears_reference`: `@ears: EARS.NN.03.xxxx`
  - [ ] `prd_reference`: `@prd: PRD.NN.09.xxxx`
  - [ ] `brd_reference`: `@brd: BRD.NN.07.xxxx`
- [ ] 5 sections with `_guidance`, `_antipatterns`, `_example`:
  - [ ] Section 1: Document Control
  - [ ] Section 2: Feature Definition
    - [ ] `_guidance`: tag conventions, feature naming, required tags
    - [ ] `_example`: complete Feature header with tags
  - [ ] Section 3: Scenario Structure
    - [ ] `_guidance`: Given-When-Then format, scenario outlines, backgrounds
    - [ ] `_guidance`: key rules from generation/pre-generation checklists
    - [ ] `_guidance`: AI-agent BDD patterns (from BDD_AI_AGENT_EXTENSION)
    - [ ] `_guidance`: section splitting rules (from aggregator template)
    - [ ] `_example`: COMPLETE valid Gherkin block:
      ```
      Feature + Background + Scenario + Scenario Outline with Examples table
      ```
    - [ ] `_antipatterns`: non-executable scenarios, missing Given, vague Then
  - [ ] Section 4: Traceability
    - [ ] Upstream: `@ears:` + `@prd:` + `@brd:` cumulative tags
    - [ ] Downstream expected: ADR (layer 5)
    - [ ] Cross-links: `@depends:` + `@discoverability:`
  - [ ] Section 5: Glossary (flat terms list)
- [ ] Old element type code replaced:
  - [ ] `BDD.NN.14.SS` → `BDD.NN.03.xxxx` (Section 3, hash-based)
- [ ] Embedded guidance from rules:
  - [ ] Gherkin patterns → `scenario_structure._guidance`
  - [ ] Tag conventions → `feature_definition._guidance`
  - [ ] Generation checklist key rules → `scenario_structure._guidance`
  - [ ] Pre-generation checklist → `document_control._guidance`
  - [ ] AI agent extension → `scenario_structure._guidance`
  - [ ] Aggregator template → `feature_definition._guidance`
  - [ ] ADR-Ready scoring → `metadata.validation._guidance`
- [ ] Validate YAML:
  ```bash
  python3 -c "import yaml; yaml.safe_load(open('ai_dev_ssd_flow/04_BDD/BDD-TEMPLATE.yaml')); print('YAML: VALID')"
  ```

---

## Phase 3: Archive Deprecated Files

- [ ] Create archive directory:
  ```bash
  mkdir -p ai_dev_ssd_flow/04_BDD/BDD_v1_archive
  ```
- [ ] Move files:
  ```bash
  cd ai_dev_ssd_flow/04_BDD
  mv BDD-MVP-TEMPLATE.feature BDD-MVP-TEMPLATE.yaml BDD_MVP_SCHEMA.yaml \
     BDD_MVP_CREATION_RULES.md BDD_MVP_VALIDATION_RULES.md \
     BDD_MVP_QUALITY_GATE_VALIDATION.md BDD-MVP-TEMPLATE_FIX_PLAN.md \
     BDD-00_TRACEABILITY_MATRIX-TEMPLATE.md \
     BDD_GENERATION_CHECKLIST.md BDD_PRE_GENERATION_CHECKLIST.md \
     BDD_AI_AGENT_EXTENSION.md BDD_AI_VALIDATION_DECISION_GUIDE.md \
     BDD_VALIDATION_STRATEGY.md BDD_VALIDATION_COMMANDS.md \
     BDD-AGGREGATOR-TEMPLATE.feature \
     REVIEW_REPORT.md FIXES_SUMMARY.md \
     examples/ scripts/ README.md \
     BDD_v1_archive/
  ```
- [ ] Consolidate backups:
  ```bash
  mv .backup_2026-02-26/ BDD_v1_archive/backup_2026-02-26/
  mv backup_20260208_162126/ BDD_v1_archive/backup_20260208/
  ```
- [ ] Create `BDD_v1_archive/README.md` with migration notes
- [ ] Verify active directory:
  ```bash
  ls ai_dev_ssd_flow/04_BDD/
  # Expected: BDD-TEMPLATE.yaml, BDD-00_index.md, BDD_v1_archive/
  ```

---

## Phase 4: Update BDD-00_index.md

- [ ] Update template link: `BDD-MVP-TEMPLATE.feature` → `BDD-TEMPLATE.yaml`
- [ ] Update validation commands to mcp_ucx tools
- [ ] Remove references to archived files
- [ ] Fix cross-layer old template refs:
  - [ ] `REQ-MVP-TEMPLATE.md` → remove or update
  - [ ] `SPEC-MVP-TEMPLATE.yaml` → remove or update
  - [ ] `BDD-MVP-TEMPLATE.feature v1.0` → `BDD-TEMPLATE.yaml v1.0`

---

## Phase 5: Create New README.md

- [ ] Create `ai_dev_ssd_flow/04_BDD/README.md` (~80 lines) with:
  - [ ] Overview (BDD = Layer 4, Given-When-Then scenarios)
  - [ ] C4 position (refinement step alongside EARS)
  - [ ] Files table (single YAML template; instances are `.feature` files)
  - [ ] Template Sync Rule (canonical → `mcp_ucx/templates/`)
  - [ ] MCP Tools table
  - [ ] Gherkin syntax quick reference (Given-When-Then)
  - [ ] Element ID format (`BDD.{doc_id}.{section_id}.{hash}`)
  - [ ] Upstream traceability (EARS/PRD/BRD cumulative tags)
  - [ ] Execution environment note (QA staging only)
  - [ ] Archive note

---

## Phase 6: Update mcp_ucx

- [ ] Copy unified template:
  ```bash
  cp ai_dev_ssd_flow/04_BDD/BDD-TEMPLATE.yaml mcp_ucx/templates/BDD-TEMPLATE.yaml
  ```
- [ ] Remove old template:
  ```bash
  rm mcp_ucx/templates/BDD-MVP-TEMPLATE.feature
  ```
- [ ] Check `prompts/templates/creation/UCC_PROMPT_BDD.md`:
  - [ ] Grep for old refs (expected: none found)
  - [ ] Update only if old patterns found
- [ ] Check `prompts/templates/review/UCR_PROMPT_BDD.md`:
  - [ ] Grep for old refs (expected: none found)
  - [ ] Update only if old patterns found
- [ ] Check `prompts/templates/remediation/UCRem_PROMPT_BDD.md`:
  - [ ] Grep for old refs (expected: none found)
  - [ ] Update only if old patterns found
- [ ] Verify templates directory:
  ```bash
  ls mcp_ucx/templates/BDD*
  # Expected: BDD-TEMPLATE.yaml only
  ```

---

## Phase 7: Cross-Reference Updates

- [ ] `EARS-TEMPLATE.yaml` downstream_expected: verify BDD description is current
- [ ] `PRD-TEMPLATE.yaml` downstream_expected: verify BDD description is current
- [ ] `BRD-TEMPLATE.yaml` downstream_expected: verify BDD description (already split)
- [ ] `BRD-00_GLOSSARY.md`: verify BDD = "Behavior-Driven Development"
- [ ] Grep for stale BDD references:
  ```bash
  grep -rn 'BDD-MVP-TEMPLATE\|BDD_MVP_SCHEMA' ai_dev_ssd_flow/01_BRD/ ai_dev_ssd_flow/02_PRD/ ai_dev_ssd_flow/03_EARS/ ai_dev_ssd_flow/04_BDD/ mcp_ucx/src/ --include="*.md" --include="*.yaml" --include="*.py" | grep -v _v1_archive | grep -v __pycache__ | grep -v template_naming.py
  ```
  Expected: 0 matches outside archives

---

## Phase 8: Validation, Documentation, Changelog, Roadmap

### 8.1 Test Suite

- [ ] Run full mcp_ucx test suite:
  ```bash
  cd /opt/data/ucx_framework/mcp_ucx && python -m pytest tests/ -v --tb=short
  ```
- [ ] Final count: `___` passed, `___` failed
- [ ] No regressions (final >= baseline)

### 8.2 Template Resolution

- [ ] Verify BDD template resolves:
  ```bash
  cd /opt/data/ucx_framework/mcp_ucx && PYTHONPATH=src python -c "
  from pathlib import Path
  from mcp_server.utils.template_naming import resolve_template_path
  p = resolve_template_path(Path('../ai_dev_ssd_flow/04_BDD'), 'BDD', '.yaml')
  print(f'Resolved: {p}')
  assert p is not None and 'BDD-TEMPLATE.yaml' in str(p)
  print('PASS')
  "
  ```

### 8.3 Stale Reference Check

- [ ] No old BDD references in mcp_ucx source:
  ```bash
  grep -rn 'BDD-MVP-TEMPLATE' mcp_ucx/src/ --include="*.py" | grep -v __pycache__
  ```
  Expected: 0 matches

### 8.4 Changelog

- [ ] Create `changelog/CHANGELOG_v0.5.0.md`:
  - BDD template unification summary
  - Single YAML template (no `.feature` template — instances are `.feature`)
  - Hash-based ID migration (old type code 14 → section-based)
  - Gherkin syntax embedded in `_guidance`/`_example` fields
  - Execution environment documented (QA staging only)
  - Files archived

### 8.5 Roadmap

- [ ] Update `roadmap/ROADMAP.md`:
  - Current version → 0.5.0
  - v0.5.0 in completed releases
  - Renumber API executors from v0.5.0 → v0.6.0

### 8.6 Plan Status

- [ ] Mark PLAN-005 status as Complete
- [ ] Delete this checklist (temporary execution checklist)

---

## Post-Implementation Summary

- [ ] BDD-TEMPLATE.yaml created and synced to mcp_ucx
- [ ] All deprecated files archived to BDD_v1_archive/
- [ ] Gherkin syntax embedded in `_guidance`/`_example` fields (no `.feature` template)
- [ ] mcp_ucx prompts verified (minimal or no changes needed)
- [ ] Tests pass with 0 regressions
- [ ] Four layers unified: BRD (Context), PRD (Container), EARS (transition), BDD (transition)
- [ ] Changelog and roadmap updated
