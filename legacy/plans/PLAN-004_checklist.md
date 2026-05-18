# PLAN-004 Implementation Checklist

**Plan**: PLAN-004_ears_layer_unification.md
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
  - [ ] `EARS-MVP-TEMPLATE.md` (264 lines)
  - [ ] `EARS-MVP-TEMPLATE.yaml` (292 lines)
  - [ ] `EARS_MVP_CREATION_RULES.md` (706 lines)
  - [ ] `EARS_MVP_VALIDATION_RULES.md` (690 lines)
  - [ ] `EARS_MVP_QUALITY_GATE_VALIDATION.md` (686 lines)
  - [ ] `EARS_MVP_SCHEMA.yaml` (350 lines)
- [ ] Read PRD EARS appendix: `tmp/EARS_APPENDIX_FROM_PRD.md` (local only, not in git)

---

## Phase 1: Section Analysis (Research)

- [ ] Confirm 5 sections + glossary for unified template:
  - [ ] Section 1: Document Control
  - [ ] Section 2: Purpose and Context (workflow info moves to `_guidance`)
  - [ ] Section 3: Requirements (WHEN-THE-SHALL-WITHIN)
  - [ ] Section 4: Quality Attributes
  - [ ] Section 5: Traceability (absorbs old Section 6 References)
  - [ ] Glossary (flat terms list)
- [ ] Confirm old Section 2 (Development Workflow) becomes metadata `_guidance`
- [ ] Confirm old Section 6 (References) merges into Section 5 (Traceability)

---

## Phase 1B: PRD EARS Appendix Content

- [ ] Read `tmp/EARS_APPENDIX_FROM_PRD.md` (exists locally, gitignored)
- [ ] Identify content to embed:
  - [ ] Timing Profile Matrix (p50/p95/p99) → Section 4 `_guidance`
  - [ ] Boundary Value Matrix → Section 3 `_guidance`
  - [ ] State Transition Diagram template → Section 3 `_guidance`
  - [ ] Fallback Path Documentation → Section 3 `_guidance`
  - [ ] EARS-Ready Checklist → Section 3 `_guidance`
  - [ ] Timing vocabulary (real-time → p50 <100ms, etc.) → Section 4 `_guidance`

---

## Phase 2: Create EARS-TEMPLATE.yaml

- [ ] Create `ai_dev_ssd_flow/03_EARS/EARS-TEMPLATE.yaml`
- [ ] Template metadata:
  - [ ] `schema_version: "1.0"`
  - [ ] `document_type: "ears-document"`
  - [ ] `layer: 3`
  - [ ] `total_sections: 5`
  - [ ] `c4_level`: `_guidance` only (no value — EARS is a refinement step, not a C4 level)
  - [ ] `diagram_standard`: state diagrams + sequence diagrams for requirements
  - [ ] `validation.tool: sdd_validate` / `server: mcp_ucx`
  - [ ] `validation._guidance`: BDD-Ready scoring criteria
  - [ ] `deliverable_type`: inherited from upstream PRD
  - [ ] `id_standard`: format `{doc_type}.{doc_id}.{section_id}.{hash}`, SHA256
- [ ] Document control:
  - [ ] `bdd_ready_score` field
  - [ ] `source_document`: `@prd: PRD.NN.09.xxxx` (new hash format)
  - [ ] `brd_reference`: `@brd: BRD.NN.07.xxxx`
- [ ] 5 sections with `_guidance` and `_antipatterns`:
  - [ ] Section 1: Document Control
  - [ ] Section 2: Purpose and Context (absorbs old workflow section as `_guidance`)
  - [ ] Section 3: Requirements — 4 EARS syntax patterns:
    - [ ] Event-driven: WHEN-THE-SHALL-WITHIN
    - [ ] State-driven: WHILE-THE-SHALL-WITHIN
    - [ ] Unwanted behavior: IF-THE-SHALL-WITHIN
    - [ ] Ubiquitous: THE-SHALL
    - [ ] `_guidance`: boundary value matrix, state transitions, fallback paths, EARS-Ready checklist
    - [ ] `_antipatterns`: vague timing ("real-time", "fast"), missing trigger clause
  - [ ] Section 4: Quality Attributes (performance, security, reliability in EARS format)
    - [ ] `_guidance`: timing profile matrix (p50/p95/p99), timing vocabulary replacements
  - [ ] Section 5: Traceability (absorbs old References section)
    - [ ] Upstream: `@prd:` + `@brd:` tags (cumulative hierarchy)
    - [ ] Downstream expected: BDD (layer 4)
    - [ ] Cross-links: `@depends:` + `@discoverability:`
    - [ ] Threshold references: `@threshold:` convention (no PRD section numbers)
  - [ ] Glossary: flat terms list
- [ ] Embed guidance from creation/validation rules:
  - [ ] EARS syntax patterns → `requirements._guidance`
  - [ ] Quality attribute patterns → `quality_attributes._guidance`
  - [ ] Timing profiles from PRD appendix → `quality_attributes._guidance`
  - [ ] Boundary values from PRD appendix → `requirements._guidance`
  - [ ] State transitions from PRD appendix → `requirements._guidance`
  - [ ] Fallback paths from PRD appendix → `requirements._guidance`
  - [ ] BDD-Ready scoring → `metadata.validation._guidance`
- [ ] All element IDs use `EARS.NN.{section_id}.xxxx` (hash from EARS content)
- [ ] Old type codes replaced:
  - [ ] `EARS.NN.25.SS` → `EARS.NN.03.xxxx` (requirements, Section 3)
  - [ ] `EARS.NN.02.SS` → `EARS.NN.04.xxxx` (quality attrs, Section 4)
  - [ ] `EARS.NN.03.SS` → `EARS.NN.04.xxxx` (quality attrs, Section 4)
  - [ ] `EARS.NN.04.SS` → `EARS.NN.04.xxxx` (quality attrs, Section 4)
- [ ] Workflow string: `BRD → PRD → EARS → BDD → ADR → SYS → REQ → CTR → SPEC → TSPEC → TASKS → Code`
- [ ] Validate YAML:
  ```bash
  python3 -c "import yaml; yaml.safe_load(open('ai_dev_ssd_flow/03_EARS/EARS-TEMPLATE.yaml')); print('YAML: VALID')"
  ```

---

## Phase 3: Archive Deprecated Files

- [ ] Create archive directory:
  ```bash
  mkdir -p ai_dev_ssd_flow/03_EARS/EARS_v1_archive
  ```
- [ ] Move files:
  ```bash
  cd ai_dev_ssd_flow/03_EARS
  mv EARS-MVP-TEMPLATE.md EARS-MVP-TEMPLATE.yaml EARS_MVP_SCHEMA.yaml \
     EARS_MVP_CREATION_RULES.md EARS_MVP_VALIDATION_RULES.md \
     EARS_MVP_QUALITY_GATE_VALIDATION.md EARS-MVP-TEMPLATE_FIX_PLAN.md \
     EARS-00_TRACEABILITY_MATRIX-TEMPLATE.md \
     EARS_AI_VALIDATION_DECISION_GUIDE.md EARS_VALIDATION_STRATEGY.md \
     EARS_VALIDATION_COMMANDS.md FIXES_SUMMARY.md \
     examples/ scripts/ README.md \
     EARS_v1_archive/
  ```
- [ ] Consolidate backup:
  ```bash
  mv .backup_2026-02-26/ EARS_v1_archive/backup_2026-02-26/
  ```
- [ ] Create `EARS_v1_archive/README.md` with migration notes
- [ ] Verify active directory:
  ```bash
  ls ai_dev_ssd_flow/03_EARS/
  # Expected: EARS-TEMPLATE.yaml, EARS-00_index.md, EARS_v1_archive/
  ```

---

## Phase 4: Update EARS-00_index.md

- [ ] Fix EARS acronym: "Event-Action-Response-State" → "Easy Approach to Requirements Syntax"
- [ ] Update template link: `EARS-MVP-TEMPLATE.md` → `EARS-TEMPLATE.yaml`
- [ ] Update copy command to `sdd_create` MCP tool reference
- [ ] Remove references to archived files (validation scripts, schema)

---

## Phase 5: Create New README.md

- [ ] Create `ai_dev_ssd_flow/03_EARS/README.md` (~80 lines) with:
  - [ ] Overview (EARS = Layer 3, formalizes Context→Container transition)
  - [ ] C4 position (refinement step between BRD Context and PRD Container)
  - [ ] Files table (EARS-TEMPLATE.yaml, EARS-00_index.md)
  - [ ] Template Sync Rule (canonical → `mcp_ucx/templates/`)
  - [ ] MCP Tools table
  - [ ] EARS syntax quick reference (4 patterns)
  - [ ] Element ID format (`EARS.{doc_id}.{section_id}.{hash}`)
  - [ ] Upstream traceability (`@prd:` + `@brd:` cumulative tags)
  - [ ] Archive note

---

## Phase 6: Update mcp_ucx

- [ ] Copy unified template:
  ```bash
  cp ai_dev_ssd_flow/03_EARS/EARS-TEMPLATE.yaml mcp_ucx/templates/EARS-TEMPLATE.yaml
  ```
- [ ] Remove old template:
  ```bash
  rm mcp_ucx/templates/EARS-MVP-TEMPLATE.md
  ```
- [ ] Update `prompts/templates/creation/UCC_PROMPT_EARS.md`:
  - [ ] Check for section/template refs (may need minimal changes)
  - [ ] Update any `EARS-MVP-TEMPLATE` refs → `EARS-TEMPLATE.yaml`
- [ ] Update `prompts/templates/review/UCR_PROMPT_EARS.md`:
  - [ ] Update section cross-references if present
  - [ ] Update template name refs
- [ ] Update `prompts/templates/remediation/UCRem_PROMPT_EARS.md`:
  - [ ] Line 207: Element ID convention `EARS.{doc_num}.{pattern_code}.{seq}` →
    `EARS.{doc_id}.{section_id}.{hash}`
  - [ ] Lines 209-215: Remove old pattern codes (UB, EV, ST, OP, UW, CX) →
    replace with section-based hash IDs
  - [ ] Update quality checklist
- [ ] Verify non-EARS templates unchanged:
  ```bash
  ls mcp_ucx/templates/
  ```

---

## Phase 7: Cross-Reference Updates

- [ ] `BRD-TEMPLATE.yaml` downstream_expected: split `"EARS/BDD"` (layer "3/4") into:
  - `type: EARS, layer: 3, description: "Formal WHEN-THE-SHALL-WITHIN requirements"`
  - `type: BDD, layer: 4, description: "Given-When-Then test scenarios"`
- [ ] Validate BRD template after change:
  ```bash
  python3 -c "import yaml; yaml.safe_load(open('ai_dev_ssd_flow/01_BRD/BRD-TEMPLATE.yaml')); print('BRD: VALID')"
  ```
- [ ] Sync BRD template:
  ```bash
  cp ai_dev_ssd_flow/01_BRD/BRD-TEMPLATE.yaml mcp_ucx/templates/BRD-TEMPLATE.yaml
  ```
- [ ] `PRD-TEMPLATE.yaml` downstream_expected: verify EARS description is current
- [ ] `BRD-00_GLOSSARY.md`: verify EARS = "Easy Approach to Requirements Syntax"
- [ ] Grep for stale EARS references:
  ```bash
  grep -rn 'EARS-MVP-TEMPLATE\|EARS_MVP_SCHEMA' ai_dev_ssd_flow/01_BRD/ ai_dev_ssd_flow/02_PRD/ ai_dev_ssd_flow/03_EARS/ mcp_ucx/src/ --include="*.md" --include="*.yaml" --include="*.py" | grep -v _v1_archive | grep -v __pycache__ | grep -v template_naming.py
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

- [ ] Verify EARS template resolves:
  ```bash
  cd /opt/data/ucx_framework/mcp_ucx && PYTHONPATH=src python -c "
  from pathlib import Path
  from mcp_server.utils.template_naming import resolve_template_path
  p = resolve_template_path(Path('../ai_dev_ssd_flow/03_EARS'), 'EARS', '.yaml')
  print(f'Resolved: {p}')
  assert p is not None and 'EARS-TEMPLATE.yaml' in str(p)
  print('PASS')
  "
  ```

### 8.3 EARS Parity Validation

- [ ] Verify EARS syntax check still works in `validation/runner.py` (lines 206-216):
  ```bash
  cd /opt/data/ucx_framework/mcp_ucx && python -m pytest tests/unit/test_validation_runner.py -k "ears" -v --tb=short
  ```

### 8.4 Stale Reference Check

- [ ] No old EARS references in mcp_ucx source:
  ```bash
  grep -rn 'EARS-MVP-TEMPLATE' mcp_ucx/src/ --include="*.py" | grep -v __pycache__
  ```
  Expected: 0 matches

### 8.5 Changelog

- [ ] Create `changelog/CHANGELOG_v0.4.0.md`:
  - EARS template unification summary
  - Section structure changes (6→5+glossary)
  - PRD EARS appendix incorporated (timing profiles, boundary values, etc.)
  - Hash-based ID migration (old type codes 25/02/03/04 → section-based)
  - BRD downstream_expected split (EARS/BDD → separate entries)
  - Files archived
  - C4 position documented (refinement step, no C4 level value)

### 8.6 Roadmap

- [ ] Update `roadmap/ROADMAP.md`:
  - Current version → 0.4.0
  - v0.4.0 in completed releases
  - Renumber API executors from v0.4.0 → v0.5.0

### 8.7 Plan Status

- [ ] Mark PLAN-004 status as Complete
- [ ] Delete this checklist (temporary execution checklist)

---

## Post-Implementation Summary

- [ ] EARS-TEMPLATE.yaml created and synced to mcp_ucx
- [ ] All deprecated files archived to EARS_v1_archive/
- [ ] PRD EARS appendix content incorporated into template `_guidance`
- [ ] BRD downstream_expected split into EARS + BDD
- [ ] mcp_ucx prompts updated (3 files)
- [ ] Tests pass with 0 regressions
- [ ] Changelog and roadmap updated
