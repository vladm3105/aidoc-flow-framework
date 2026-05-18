# PLAN-006 Implementation Checklist

**Plan**: PLAN-006_adr_layer_unification.md
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
  - [ ] `ADR-MVP-TEMPLATE.md` (406 lines)
  - [ ] `ADR-MVP-TEMPLATE.yaml` (363 lines)
  - [ ] `ADR_MVP_CREATION_RULES.md` (500 lines)
  - [ ] `ADR_MVP_VALIDATION_RULES.md` (422 lines)
  - [ ] `ADR_MVP_QUALITY_GATE_VALIDATION.md` (967 lines)
  - [ ] `ADR_MVP_SCHEMA.yaml` (460 lines)

---

## Phase 1: Section Analysis (Research)

- [ ] Confirm 10 sections + glossary + lifecycle appendix:
  - [ ] Section 1: Document Control
  - [ ] Section 2: Context
  - [ ] Section 3: Decision
  - [ ] Section 4: Alternatives Considered
  - [ ] Section 5: Consequences
  - [ ] Section 6: Architecture Flow
  - [ ] Section 7: Implementation Assessment (trimmed — decision-level only)
  - [ ] Section 8: Verification (cross-refs to BDD scenarios)
  - [ ] Section 9: Traceability
  - [ ] Section 10: Related Decisions
  - [ ] Glossary (flat terms list)
  - [ ] Appendix: MVP Lifecycle (from old Section 11)
- [ ] Confirm old Section 11 (Lifecycle) moves to appendix

---

## Phase 1B: C4 Model Position

- [ ] Confirm: ADR is decision bridge between Container (PRD) and Component (SYS)
- [ ] Confirm: no `c4_level.value` — `_guidance` only

---

## Phase 2: Create ADR-TEMPLATE.yaml

- [ ] Create `ai_dev_ssd_flow/05_ADR/ADR-TEMPLATE.yaml`
- [ ] Template metadata:
  - [ ] `schema_version: "1.0"`
  - [ ] `document_type: "adr-document"`
  - [ ] `layer: 5`
  - [ ] `total_sections: 10`
  - [ ] `c4_level`: `_guidance` only (decision bridge, no value)
  - [ ] `diagram_standard`: C4-L3 component, sequenceDiagram, flowchart
  - [ ] `validation.tool: sdd_validate` / `server: mcp_ucx`
  - [ ] `validation._guidance`: SYS-Ready scoring criteria
  - [ ] `deliverable_type`: inherited from upstream
  - [ ] `id_standard`: `{doc_type}.{doc_id}.{section_id}.{hash}`, SHA256
- [ ] Document control:
  - [ ] `sys_ready_score` field
  - [ ] `status`: Proposed | Accepted | Deprecated | Superseded
    (NOT Draft/In Review/Approved — ADR-specific lifecycle)
  - [ ] `originating_topic`: `@prd: PRD.NN.14.xxxx` (PRD ADR topic elaboration)
  - [ ] `brd_reference`: `@brd: BRD.NN.08.xxxx`
- [ ] 10 sections with `_guidance`, `_antipatterns`, `_example`:
  - [ ] Section 1: Document Control (ADR status lifecycle in `_guidance`)
  - [ ] Section 2: Context (problem statement from BRD, constraints, technical context)
  - [ ] Section 3: Decision (chosen solution, key components, approach)
    - [ ] `_guidance`: decision rationale must explain "why", not just "what"
  - [ ] Section 4: Alternatives Considered (2-3 minimum with pros/cons/cost/fit)
    - [ ] `_guidance`: each alternative needs structured evaluation
  - [ ] Section 5: Consequences (positive outcomes, trade-offs/risks, cost estimate)
  - [ ] Section 6: Architecture Flow (Mermaid diagrams, integration points)
    - [ ] `_guidance`: C4-L3 component diagrams showing decision impact
  - [ ] Section 7: Implementation Assessment (rollback plan, monitoring baseline)
    - [ ] `_guidance`: decision-level only, not implementation details (TASKS owns those)
  - [ ] Section 8: Verification (success criteria, BDD scenario cross-refs)
  - [ ] Section 9: Traceability
    - [ ] `originating_topic`: `@prd: PRD.NN.14.xxxx`
    - [ ] Upstream cumulative tags: `@bdd:` + `@ears:` + `@prd:` + `@brd:`
    - [ ] Downstream expected: SYS (layer 6) + REQ (layer 7) + SPEC (layer 9)
    - [ ] Cross-links: `@depends:` + `@discoverability:`
  - [ ] Section 10: Related Decisions (dependencies, related ADRs, supersedes)
  - [ ] Glossary (flat terms list)
  - [ ] Appendix: MVP Lifecycle (when to create new ADR, cross-ADR traceability)
- [ ] Old element type codes replaced:
  - [ ] `ADR.NN.10.SS` → `ADR.NN.03.xxxx` (Decision, Section 3)
  - [ ] `ADR.NN.12.SS` → `ADR.NN.04.xxxx` (Alternative, Section 4)
  - [ ] `ADR.NN.13.SS` → `ADR.NN.05.xxxx` (Consequence, Section 5)
- [ ] Old upstream BRD refs replaced:
  - [ ] `BRD.NN.32.SS` → `BRD.NN.08.xxxx` (BRD Section 8)
  - [ ] `originating_topic` → `@prd: PRD.NN.14.xxxx` (PRD Section 14)
- [ ] Embedded guidance from rules:
  - [ ] Context-Decision-Consequences structure → `context/decision/consequences._guidance`
  - [ ] Alternatives format (pros/cons/cost/fit) → `alternatives._guidance`
  - [ ] ADR status lifecycle → `document_control._guidance`
  - [ ] Architecture flow diagrams → `architecture_flow._guidance`
  - [ ] SYS-Ready scoring → `metadata.validation._guidance`
- [ ] Validate YAML:
  ```bash
  python3 -c "import yaml; yaml.safe_load(open('ai_dev_ssd_flow/05_ADR/ADR-TEMPLATE.yaml')); print('YAML: VALID')"
  ```

---

## Phase 3: Archive Deprecated Files

- [ ] Create archive directory:
  ```bash
  mkdir -p ai_dev_ssd_flow/05_ADR/ADR_v1_archive
  ```
- [ ] Move files (NOT the active ADR instances):
  ```bash
  cd ai_dev_ssd_flow/05_ADR
  mv ADR-MVP-TEMPLATE.md ADR-MVP-TEMPLATE.yaml ADR_MVP_SCHEMA.yaml \
     ADR_MVP_CREATION_RULES.md ADR_MVP_VALIDATION_RULES.md \
     ADR_MVP_QUALITY_GATE_VALIDATION.md ADR-MVP-TEMPLATE_FIX_PLAN.md \
     ADR-00_TRACEABILITY_MATRIX-TEMPLATE.md \
     ADR_AI_VALIDATION_DECISION_GUIDE.md ADR_VALIDATION_STRATEGY.md \
     ADR_VALIDATION_COMMANDS.md REVIEW_REPORT.md FIXES_SUMMARY.md \
     examples/ scripts/ README.md \
     ADR_v1_archive/
  ```
- [ ] Consolidate backup:
  ```bash
  mv .backup_2026-02-26/ ADR_v1_archive/backup_2026-02-26/
  ```
- [ ] Create `ADR_v1_archive/README.md` with migration notes
- [ ] Verify active directory (must keep ADR instances):
  ```bash
  ls ai_dev_ssd_flow/05_ADR/
  # Expected: ADR-TEMPLATE.yaml, ADR-00_index.md,
  #           ADR-00_ai_powered_documentation_assistant_architecture.md,
  #           ADR-CTR_SEPARATE_FILES_POLICY.md, ADR_v1_archive/
  ```

---

## Phase 4: Update ADR-00_index.md

- [ ] Update template link: `ADR-MVP-TEMPLATE.md` → `ADR-TEMPLATE.yaml`
- [ ] Update copy command to `sdd_create` MCP tool reference
- [ ] Remove references to archived files
- [ ] Update template compliance reference

---

## Phase 5: Create New README.md

- [ ] Create `ai_dev_ssd_flow/05_ADR/README.md` (~80 lines) with:
  - [ ] Overview (ADR = Layer 5, architecture decisions)
  - [ ] C4 position (decision bridge between Container and Component)
  - [ ] Files table (template + active ADR instances)
  - [ ] Template Sync Rule (canonical → `mcp_ucx/templates/`)
  - [ ] MCP Tools table
  - [ ] ADR status lifecycle (Proposed→Accepted→Deprecated→Superseded)
  - [ ] Element ID format (`ADR.{doc_id}.{section_id}.{hash}`)
  - [ ] Upstream traceability (PRD originating topic + BDD/EARS/PRD/BRD cumulative tags)
  - [ ] Archive note

---

## Phase 6: Update mcp_ucx

- [ ] Copy unified template:
  ```bash
  cp ai_dev_ssd_flow/05_ADR/ADR-TEMPLATE.yaml mcp_ucx/templates/ADR-TEMPLATE.yaml
  ```
- [ ] Remove old template:
  ```bash
  rm mcp_ucx/templates/ADR-MVP-TEMPLATE.md
  ```
- [ ] Check ADR prompts for old references:
  ```bash
  grep -rn 'ADR-MVP-TEMPLATE\|ADR_MVP\|ADR\.NN\.\|BRD\.NN\.32' \
    mcp_ucx/prompts/templates/ --include="*.md" | grep -i adr
  ```
  Expected: 0 matches (verified in plan review)
- [ ] Verify templates directory:
  ```bash
  ls mcp_ucx/templates/ADR*
  # Expected: ADR-TEMPLATE.yaml only
  ```

---

## Phase 7: Cross-Reference Updates

- [ ] `BDD-TEMPLATE.yaml` downstream_expected: verify ADR description is current
- [ ] `PRD-TEMPLATE.yaml` downstream_expected: verify ADR description is current
- [ ] `BRD-TEMPLATE.yaml` downstream_expected: verify ADR description is current
- [ ] `EARS-TEMPLATE.yaml`: confirm no direct ADR downstream (EARS→BDD→ADR)
- [ ] `BRD-00_GLOSSARY.md`: verify ADR = "Architecture Decision Record"
- [ ] Grep for stale ADR references:
  ```bash
  grep -rn 'ADR-MVP-TEMPLATE\|ADR_MVP_SCHEMA' \
    ai_dev_ssd_flow/01_BRD/ ai_dev_ssd_flow/02_PRD/ ai_dev_ssd_flow/03_EARS/ \
    ai_dev_ssd_flow/04_BDD/ ai_dev_ssd_flow/05_ADR/ mcp_ucx/src/ \
    --include="*.md" --include="*.yaml" --include="*.py" \
    | grep -v _v1_archive | grep -v __pycache__ | grep -v template_naming.py
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

- [ ] Verify ADR template resolves:
  ```bash
  cd /opt/data/ucx_framework/mcp_ucx && PYTHONPATH=src python -c "
  from pathlib import Path
  from mcp_server.utils.template_naming import resolve_template_path
  p = resolve_template_path(Path('../ai_dev_ssd_flow/05_ADR'), 'ADR', '.yaml')
  print(f'Resolved: {p}')
  assert p is not None and 'ADR-TEMPLATE.yaml' in str(p)
  print('PASS')
  "
  ```

### 8.3 Stale Reference Check

- [ ] No old ADR references in mcp_ucx source:
  ```bash
  grep -rn 'ADR-MVP-TEMPLATE' mcp_ucx/src/ --include="*.py" | grep -v __pycache__
  ```
  Expected: 0 matches

### 8.4 Changelog

- [ ] Create `changelog/CHANGELOG_v0.6.0.md`:
  - ADR template unification summary
  - Section structure (11→10+glossary+appendix)
  - Hash-based IDs (old codes 10/12/13 → section-based)
  - Originating topic: PRD Section 14 (not BRD Section 8)
  - ADR-specific status lifecycle documented
  - Active ADR instances kept in directory
  - Downstream expanded: SYS + REQ + SPEC
  - Files archived

### 8.5 Roadmap

- [ ] Update `roadmap/ROADMAP.md`:
  - Current version → 0.6.0
  - v0.6.0 in completed releases
  - Renumber API executors from v0.6.0 → v0.7.0

### 8.6 Plan Status

- [ ] Mark PLAN-006 status as Complete
- [ ] Delete this checklist (temporary execution checklist)

---

## Post-Implementation Summary

- [ ] ADR-TEMPLATE.yaml created and synced to mcp_ucx
- [ ] All deprecated files archived to ADR_v1_archive/
- [ ] Active ADR instances kept: ADR-00_*, ADR-CTR_*
- [ ] Originating topic points to PRD Section 14 (not BRD)
- [ ] Upstream traceability: BDD + EARS + PRD + BRD (cumulative)
- [ ] Downstream: SYS + REQ + SPEC
- [ ] Tests pass with 0 regressions
- [ ] Five layers unified: BRD → PRD → EARS → BDD → ADR
- [ ] Changelog and roadmap updated
