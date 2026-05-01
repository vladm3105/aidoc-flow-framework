# PLAN-003 Implementation Checklist

**Plan**: PLAN-003_prd_layer_unification.md
**Status**: Complete
**Date**: 2026-03-29

---

## Pre-Flight

- [ ] Confirm BRD migration complete (v0.2.0, v0.2.1)
- [ ] Confirm mcp_ucx naming migration complete (PLAN-002)
- [ ] Run baseline tests:
  ```bash
  cd /opt/data/ucx_framework/mcp_ucx && python -m pytest tests/ --tb=short 2>&1 | tail -5
  ```
- [ ] Record baseline: `___` passed, `___` failed
- [ ] Read all 6 source files to consolidate:
  - [ ] `PRD-MVP-TEMPLATE.md` (731 lines)
  - [ ] `PRD-MVP-TEMPLATE.yaml` (240 lines)
  - [ ] `PRD_MVP_CREATION_RULES.md` (1,268 lines)
  - [ ] `PRD_MVP_VALIDATION_RULES.md` (1,024 lines)
  - [ ] `PRD_MVP_QUALITY_GATE_VALIDATION.md` (973 lines)
  - [ ] `PRD_MVP_SCHEMA.yaml` (380 lines)

---

## Phase 1: Section Analysis (Research)

- [ ] Confirm 14 sections to keep (1-13 + 18→14)
- [ ] Confirm 9 sections/appendices to remove:
  - [ ] Section 14 (Success Definition) → merge into 5 + 11
  - [ ] Section 15 (Stakeholders) → remove (PM artifacts)
  - [ ] Section 16 (Implementation) → remove (IPLAN/TASKS)
  - [ ] Section 17 (Budget) → remove (BRD owns)
  - [ ] Section 19 (References) → merge into traceability
  - [ ] Section 20 (EARS Appendix) → move to EARS layer
  - [ ] Section 21 (QA & Testing) → remove (TSPEC owns)
  - [ ] Appendix A (Future Roadmap) → remove (BRD owns)
  - [ ] Appendix C (Lifecycle Ref) → remove (BRD owns)
- [ ] Confirm glossary (Appendix B) stays as Section 15

---

## Phase 1B: C4 Mapping (BRD already done)

- [ ] Verify BRD-TEMPLATE.yaml has `c4_level.value: context` — DONE
- [ ] Verify BRD README has C4 Model Mapping section — DONE
- [ ] Verify mcp_ucx/templates/BRD-TEMPLATE.yaml synced — DONE

---

## Phase 2: Create PRD-TEMPLATE.yaml

### 2.1 Preserve EARS appendix content first

- [ ] Copy EARS appendix from PRD-MVP-TEMPLATE.md (lines 548-595) to:
  ```bash
  mkdir -p /opt/data/ucx_framework/tmp
  ```
- [ ] Create `tmp/EARS_APPENDIX_FROM_PRD.md` with:
  - Timing Profile Matrix
  - Boundary Value Matrix
  - State Transition Diagram
  - Fallback Path Documentation
  - EARS-Ready Checklist

### 2.2 Build unified template

- [ ] Create `ai_dev_ssd_flow/02_PRD/PRD-TEMPLATE.yaml`
- [ ] Template metadata:
  - [ ] `schema_version: "1.0"`
  - [ ] `document_type: "prd-document"`
  - [ ] `layer: 2`
  - [ ] `lifecycle: mvp-prod-newmvp`
  - [ ] `total_sections: 15`
  - [ ] `c4_level.value: container` with full C4 mapping `_guidance`
  - [ ] `validation.tool: sdd_validate` / `server: mcp_ucx`
  - [ ] `deliverable_type` with routing map (inherited from BRD)
  - [ ] `id_standard` with SHA256 hash docs, format `PRD.{doc_id}.{section_id}.{hash}`
- [ ] Document control:
  - [ ] `ears_ready_score` (drop old `sys_ready_score`)
  - [ ] `brd_reference` using `@brd: BRD.NN.07.xxxx` format
- [ ] 15 sections with `_guidance` and `_antipatterns`:
  - [ ] Section 1: Document Control
  - [ ] Section 2: Executive Summary (MVP hypothesis, timeline)
  - [ ] Section 3: Problem Statement (current state, impact, opportunity)
  - [ ] Section 4: Target Audience & User Personas (with persona `_guidance`)
  - [ ] Section 5: Success Metrics & KPIs (absorbs old 14.2 post-launch + 14.3 into 5.3)
  - [ ] Section 6: Goals & Objectives (IDs: `PRD.NN.06.xxxx`)
  - [ ] Section 7: Scope & Requirements (features, dependencies, out-of-scope)
  - [ ] Section 8: User Stories & User Roles (with format `_guidance`)
  - [ ] Section 9: Functional Requirements (with FR structure + `@threshold:` `_guidance`)
  - [ ] Section 10: Customer-Facing Content & Messaging
  - [ ] Section 11: Acceptance Criteria (absorbs old 14.1 go-live criteria as `launch_gates`)
  - [ ] Section 12: Constraints & Assumptions
  - [ ] Section 13: Risk Assessment
  - [ ] Section 14: Traceability (upstream BRD tags, downstream EARS/BDD/ADR, ADR topic elaboration, cross-links)
  - [ ] Section 15: Glossary (flat terms list)
  - [ ] Appendix: EARS cross-reference `_note` pointing to 03_EARS
- [ ] Embed guidance from creation rules:
  - [ ] User story patterns → `user_stories._guidance`
  - [ ] FR structure → `functional_requirements._guidance`
  - [ ] Persona template → `target_audience._guidance`
  - [ ] Threshold conventions → `functional_requirements._guidance`
  - [ ] EARS-Ready scoring → `metadata.validation._guidance`
  - [ ] ADR topic elaboration → `traceability._guidance`
- [ ] All element IDs use `PRD.NN.{section_id}.xxxx` (hash from PRD content)
- [ ] All BRD references use `BRD.NN.08.xxxx` (new hash format, not `BRD.NN.32.*`)
- [ ] Validate YAML:
  ```bash
  python3 -c "import yaml; yaml.safe_load(open('ai_dev_ssd_flow/02_PRD/PRD-TEMPLATE.yaml')); print('YAML: VALID')"
  ```

---

## Phase 3: Archive Deprecated Files

- [ ] Create archive directory:
  ```bash
  mkdir -p ai_dev_ssd_flow/02_PRD/PRD_v1_archive
  ```
- [ ] Move 15 files + 2 directories:
  ```bash
  cd ai_dev_ssd_flow/02_PRD
  mv PRD-MVP-TEMPLATE.md PRD-MVP-TEMPLATE.yaml PRD_MVP_SCHEMA.yaml \
     PRD_MVP_CREATION_RULES.md PRD_MVP_VALIDATION_RULES.md \
     PRD_MVP_QUALITY_GATE_VALIDATION.md PRD-MVP-TEMPLATE_FIX_PLAN.md \
     PRD-00_threshold_registry_template.md PRD-00_TRACEABILITY_MATRIX-TEMPLATE.md \
     PRD_VALIDATION_STRATEGY.md PRD_VALIDATION_COMMANDS.md \
     PRD_AI_VALIDATION_DECISION_GUIDE.md \
     examples/ scripts/ README.md \
     PRD_v1_archive/
  ```
- [ ] Consolidate existing archive:
  ```bash
  mv archive/.backup_2026-02-26/ PRD_v1_archive/backup_2026-02-26/
  rmdir archive/ 2>/dev/null || true
  ```
- [ ] Create `PRD_v1_archive/README.md` with migration notes
- [ ] Verify active directory:
  ```bash
  ls ai_dev_ssd_flow/02_PRD/
  # Expected: PRD-TEMPLATE.yaml, PRD-00_index.md, PRD_v1_archive/
  ```

---

## Phase 4: Update PRD-00_index.md

- [ ] Read current `PRD-00_index.md`
- [ ] Remove references to archived files (old template, scripts, validation rules)
- [ ] Update validation commands to mcp_ucx tools
- [ ] Update template link to `PRD-TEMPLATE.yaml`
- [ ] Update Quick Start commands

---

## Phase 5: Create New README.md

- [ ] Create `ai_dev_ssd_flow/02_PRD/README.md` (~80 lines) with:
  - [ ] Overview (PRD = Layer 2, Container level)
  - [ ] C4 Model Mapping section (PRD = Container)
  - [ ] Files table (PRD-TEMPLATE.yaml, PRD-00_index.md)
  - [ ] Template Sync Rule (canonical → `mcp_ucx/templates/`)
  - [ ] MCP Tools table (sdd_create, sdd_validate, sdd_score_validate)
  - [ ] Element ID format (`PRD.{doc_id}.{section_id}.{hash}`)
  - [ ] Archive note

---

## Phase 6: Update mcp_ucx

- [ ] Copy unified template:
  ```bash
  cp ai_dev_ssd_flow/02_PRD/PRD-TEMPLATE.yaml mcp_ucx/templates/PRD-TEMPLATE.yaml
  ```
- [ ] Remove old template:
  ```bash
  rm mcp_ucx/templates/PRD-MVP-TEMPLATE.md
  ```
- [ ] Update `mcp_ucx/prompts/templates/creation/UCC_PROMPT_PRD.md`:
  - [ ] Line 25: "exactly 21 numbered sections" → "exactly 15 numbered sections"
  - [ ] Line 342: `PRD-MVP-TEMPLATE.md` → `PRD-TEMPLATE.yaml`
  - [ ] Line 362: `PRD-MVP-TEMPLATE.md` → `PRD-TEMPLATE.yaml`
  - [ ] Update section list to match new 15-section structure
- [ ] Verify non-PRD templates unchanged:
  ```bash
  ls mcp_ucx/templates/
  ```

---

## Phase 7: Cross-Reference Updates

- [ ] `BRD-TEMPLATE.yaml` downstream_expected: verify PRD description is current
- [ ] `BRD-00_GLOSSARY.md` cross-references: update PRD template path if referenced
- [ ] Grep for stale PRD references in other layers:
  ```bash
  grep -rn 'PRD-MVP-TEMPLATE\|PRD_MVP_SCHEMA' ai_dev_ssd_flow/ --include="*.md" --include="*.yaml" | grep -v PRD_v1_archive | grep -v BRD_v1_archive
  ```
  Expected: 0 matches outside archives

---

## Phase 8: Validation and Documentation

### 8.1 Test Suite

- [ ] Run full mcp_ucx test suite:
  ```bash
  cd /opt/data/ucx_framework/mcp_ucx && python -m pytest tests/ -v --tb=short
  ```
- [ ] Final count: `___` passed, `___` failed
- [ ] No regressions (final >= baseline)

### 8.2 Template Resolution

- [ ] Verify PRD template resolves:
  ```bash
  cd /opt/data/ucx_framework/mcp_ucx && PYTHONPATH=src python -c "
  from pathlib import Path
  from mcp_server.utils.template_naming import resolve_template_path
  p = resolve_template_path(Path('../ai_dev_ssd_flow/02_PRD'), 'PRD', '.yaml')
  print(f'Resolved: {p}')
  assert p is not None and 'PRD-TEMPLATE.yaml' in str(p)
  print('PASS')
  "
  ```

### 8.3 Stale Reference Check

- [ ] No old PRD references in mcp_ucx source:
  ```bash
  grep -rn 'PRD-MVP-TEMPLATE' mcp_ucx/src/ --include="*.py" | grep -v __pycache__
  ```
  Expected: 0 matches (PLAN-002 already broadened filters)

### 8.4 Changelog

- [ ] Create `changelog/CHANGELOG_v0.3.0.md`:
  - PRD template unification summary
  - Files consolidated/archived
  - Section structure changes (21→15)
  - Hash-based ID migration
  - C4 model mapping added
  - EARS appendix preserved in `tmp/`

### 8.5 Roadmap

- [ ] Update `roadmap/ROADMAP.md`:
  - Current version → 0.3.0
  - v0.3.0 in completed releases
  - Renumber planned releases if needed

### 8.6 Plan Status

- [ ] Mark PLAN-003 status as Complete
- [ ] Delete this checklist (temporary execution checklist)

---

## Post-Implementation Summary

- [ ] PRD-TEMPLATE.yaml created and synced to mcp_ucx
- [ ] All deprecated files archived to PRD_v1_archive/
- [ ] EARS appendix preserved in tmp/ for Layer 3 migration
- [ ] C4 mapping in both BRD and PRD templates
- [ ] Tests pass with 0 regressions
- [ ] Changelog and roadmap updated
