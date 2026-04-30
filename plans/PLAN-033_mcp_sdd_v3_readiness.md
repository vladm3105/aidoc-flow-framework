# PLAN-033: mcp_ucx V3 Readiness

**Date**: 2026-04-30  
**Status**: Draft (Updated with Gap Analysis)  
**Priority**: High  
**Estimated Effort**: 5-7 days (expanded from 3-5 to address all 12 gaps)  

## Executive Summary

Update `mcp_ucx` to support `ucx_flow_v3` (v3.2) layer architecture. V3 introduces TDD (L7) and IPLAN (L8) while cutting SYS, REQ, CTR, TSPEC, and TASKS layers. Current mcp_ucx (v1.21.0) lacks templates, prompts, validation rules, and configuration updates for V3 compatibility.

**Gap Analysis Results**: 12 gaps identified (3 Critical, 4 High, 5 Medium). All critical and high priority gaps are now addressed in this updated plan.

## V3 Layer Architecture

```
BRD (L1) → PRD (L2) → EARS (L3) → BDD (L4) → ADR (L5) → SPEC (L6) → TDD (L7) → IPLAN (L8) → Code
```

**Cut layers**: SYS, REQ, CTR, TSPEC, TASKS  
**New layers**: TDD, IPLAN

## Phase 1: Template Integration (Day 1)

### Tasks

1. **Copy V3 Templates**
   - Copy `ucx_flow_v3/07_TDD/TDD-TEMPLATE.yaml` → `mcp_ucx/templates/TDD-TEMPLATE.yaml`
   - Copy `ucx_flow_v3/08_IPLAN/IPLAN-TEMPLATE.yaml` → `mcp_ucx/templates/IPLAN-TEMPLATE.yaml`

2. **Create Prompt Templates** (6 files in `mcp_ucx/prompts/templates/`)
   - `creation/UCC_PROMPT_TDD.md` - TDD creation prompt based on TDD-TEMPLATE.yaml
   - `creation/UCC_PROMPT_IPLAN.md` - IPLAN creation prompt based on IPLAN-TEMPLATE.yaml
   - `review/UCR_PROMPT_TDD.md` - TDD review prompt with TDD-specific criteria
   - `review/UCR_PROMPT_IPLAN.md` - IPLAN review prompt with IPLAN-specific criteria
   - `remediation/UCRem_PROMPT_TDD.md` - TDD remediation prompt
   - `remediation/UCRem_PROMPT_IPLAN.md` - IPLAN remediation prompt

3. **Archive Cut Layer Templates**
   - Move to `mcp_ucx/templates/archive/`:
     - SYS-TEMPLATE.yaml
     - REQ-TEMPLATE.yaml
     - CTR-TEMPLATE.yaml
     - TSPEC-TEMPLATE.yaml
     - TASKS-TEMPLATE.yaml

## Phase 2: Validation Updates (Day 2-3)

### Tasks

1. **Update `cross_section.py`** (`mcp_ucx/src/mcp_server/validation/cross_section.py`)
   - Update `READINESS_SCORE_FIELDS`:
     ```python
     READINESS_SCORE_FIELDS = {
         "brd": "prd_ready_score",
         "prd": "ears_ready_score",
         "ears": "bdd_ready_score",
         "bdd": "adr_ready_score",
         "adr": "spec_ready_score",      # was "sys_ready_score"
         "spec": "tdd_ready_score",      # was "task_ready_score"
         "tdd": "iplan_ready_score",    # NEW
         # iplan is final layer before Code - no downstream readiness field needed
     }
     ```
   - Update `_DIAGRAM_LAYERS`:
     ```python
     _DIAGRAM_LAYERS = frozenset({"brd", "prd", "adr", "spec"})  # removed "sys"
     ```
   - Add cumulative tags enforcement (max 8 at IPLAN layer):
     ```python
     MAX_CUMULATIVE_TAGS = {
         "brd": 1, "prd": 2, "ears": 3, "bdd": 4, "adr": 5, "spec": 6, "tdd": 7, "iplan": 8
     }
     ```

2. **Create Validation Rules**
   - `mcp_ucx/src/mcp_server/validation/tdd_rules.py`:
     - `check_tdd_readiness_score()`: Verify TDD-READY score >= 90
     - `check_test_pyramid()`: Validate 70/20/10 distribution (unit/integration/e2e)
     - `check_bdd_scenario_coverage()`: All BDD scenarios mapped in `test_mapping.scenarios[].tests[]`
     - `check_test_thresholds()`: Validate coverage targets and pass criteria present
     - `check_tdd_execution_order()`: Verify Red-Green-Refactor sequence declared
     - `check_spec_traceability()`: Validate `spec_ref` in test cases (Section 4)
   
   - `mcp_ucx/src/mcp_server/validation/iplan_rules.py`:
     - `check_iplan_readiness_score()`: Verify IPLAN-READY score >= 90
     - `check_file_manifest()`: Validate all files listed with path, order, status, session fields
     - `check_execution_commands()`: Verify setup, implementation, validation commands present
     - `check_session_handoff()`: Validate section populated with markers (NOT_STARTED/IN_PROGRESS/DONE/PARTIAL)
     - `check_tdd_traceability()`: Verify `tdd_ref` and `spec_ref` links present
     - `check_implementation_contracts()`: Optional - validate if present (Section 4)

3. **Update Validation Runner** (`mcp_ucx/src/mcp_server/validation/runner.py`)
   - Add dispatch logic for "tdd" and "iplan" doc_types
   - Fix `_resolve_canonical_template_root()` (lines 152-158): Change `ucx_flow_v3` to `ucx_flow_v3`
   - Add TDD/IPLAN parity checks to `_run_doc_type_parity_checks()` (lines 277-315)
   - Register new rule modules in `run_project_validation_build()`

## Phase 3: Configuration Updates (Day 4)

### Tasks

1. **Update `profile_contracts.py`** (`mcp_ucx/src/mcp_server/creation/profile_contracts.py`)
   - Change `registry_source` from `"ucx_flow_v3/LAYER_REGISTRY.yaml"` to `"ucx_flow_v3/LAYER_REGISTRY.yaml"`

2. **Update `persona_mappings.yaml`** (`mcp_ucx/skills/persona_mappings.yaml`)
   - Add TDD phase mappings (creation/review/remediation personas)
   - Add IPLAN phase mappings  
   - Remove references to cut layers (sys, req, ctr, tspec, tasks) or mark as deprecated

3. **Update Layer Aliases** (`mcp_ucx/skills/layer_aliases/`)
   - Add `tdd` and `iplan` aliases if needed
   - Remove or deprecate cut layer aliases

4. **Update `sdd_next_action` for YAML Support** (`mcp_ucx/src/mcp_server/tool_registry.py`)
   - Fix `_inspect_document_folder()` (lines 529-593): Add `.yaml` to file scanning alongside `.md`
   - Ensure TDD/IPLAN YAML documents are detected for next-action recommendations

5. **Update `sdd_prescreen` for YAML Support** (`mcp_ucx/src/mcp_server/prescreening/runner.py`)
   - Fix `run_prescreen()` (lines 23-26): Add `.yaml` files to document collection
   - Enable TDD/IPLAN documents to be prescreened for remediation priority

6. **Update `sdd_run_lifecycle` Stages Enum** (`mcp_ucx/src/mcp_server/tool_registry.py`)
   - Fix hardcoded enum (line 322): Change from `"enum": ["validate", "validate_fix", "review", "remediate", "remediate_fix"]` 
   - Make stages parameter extensible to support V3-specific stages (e.g., "prescreen", "score_validate")

## Phase 4: Tool Registry Verification & Score Validation (Day 4)

### Tasks

1. **Verify doc_type Handling**
   - Check `mcp_ucx/src/mcp_server/tool_registry.py` accepts "tdd" and "iplan"
   - Verify `sdd_validate`, `sdd_create`, `sdd_review`, `sdd_remediate` handle new types

2. **Update `sdd_score_validate` Threshold Awareness** (`mcp_ucx/src/mcp_server/scoring/runner.py`)
   - Add special handling for TDD-READY >= 90 and IPLAN-READY >= 90 thresholds
   - Implement readiness gate validation in `run_score_validate_build()` (lines 51-81)
   - Return explicit pass/fail for readiness gates

3. **Test Lifecycle Flow**
   - Run `sdd_create` for TDD document
   - Run `sdd_validate` for TDD document
   - Run `sdd_review` for TDD document
   - Run `sdd_remediate` for TDD document
   - Repeat for IPLAN document

4. **Test YAML-Based Tools**
   - Test `sdd_next_action` with TDD/IPLAN YAML documents
   - Test `sdd_prescreen` with TDD/IPLAN YAML documents
   - Test `sdd_score_validate` with >= 90 thresholds for TDD/IPLAN

## Phase 5: Testing (Day 5)

### Tasks

1. **Unit Tests**
   - `tests/validation/test_tdd_rules.py`
   - `tests/validation/test_iplan_rules.py`
   - Update `tests/validation/test_cross_section.py` for new READINESS_SCORE_FIELDS

2. **Integration Tests**
   - Full lifecycle test for TDD: create → validate → review → remediate
   - Full lifecycle test for IPLAN: create → validate → review → remediate

3. **Regression Tests**
   - Update existing tests referencing cut layers (sys, req, ctr, tspec, tasks)
   - Ensure backward compatibility for old document types during transition

## Phase 6: Documentation Updates (Day 5)

### Tasks

1. **Update Specs** (`mcp_ucx/docs/specs/`)
   - Update SPEC-003 (Validation) to reference TDD/IPLAN rules
   - Update SPEC-006 (Prompt Templates) to include new prompts

2. **Update README**
   - Update layer map diagram
   - Add TDD and IPLAN to supported document types

3. **Update Roadmap** (`mcp_ucx/docs/ROADMAP.md`)
   - Add V3 migration milestone
   - Mark cut layers as deprecated

## Phase 7: CHG Governance Integration (Optional - Medium Priority)

### Tasks

1. **CHG Governance Overlay** (`mcp_ucx/src/mcp_server/validation/chg_rules.py`)
   - Implement 5-gate system validation:
     - GATE-01: Business/Product Gate (L1-L2)
     - GATE-03: Requirements & Architecture Gate (L3-L5)
     - GATE-06: Design & Test Gate (L6-L7)
     - GATE-CODE: Implementation Gate (Code)
   - Support change levels: C1 (trivial), C2 (minor), C3 (major)
   - Reference: `/opt/data/ucx_framework/ucx_flow_v3/CHG/`

2. **Optional CHG Tool** (`mcp_ucx/src/mcp_server/tool_registry.py`)
   - Consider adding `sdd_validate_chg` tool for CHG gate validation
   - Integrate with `sdd_validate` as optional check

## Files to Modify

| File | Change |
|------|--------|
| `mcp_ucx/src/mcp_server/validation/cross_section.py` | Update READINESS_SCORE_FIELDS, _DIAGRAM_LAYERS, add MAX_CUMULATIVE_TAGS |
| `mcp_ucx/src/mcp_server/validation/runner.py` | Add tdd/iplan dispatch, fix template root path (G-01), add parity checks (G-12) |
| `mcp_ucx/src/mcp_server/creation/profile_contracts.py` | Update registry_source path to v3 |
| `mcp_ucx/src/mcp_server/tool_registry.py` | Verify doc_type handling, fix sdd_next_action YAML (G-02), fix sdd_run_lifecycle enum (G-04) |
| `mcp_ucx/src/mcp_server/prescreening/runner.py` | Add YAML support for TDD/IPLAN (G-05) |
| `mcp_ucx/src/mcp_server/scoring/runner.py` | Add threshold awareness for TDD/IPLAN >=90 (G-06) |
| `mcp_ucx/skills/persona_mappings.yaml` | Add tdd/iplan mappings, remove/deprecate cut layers |
| `mcp_ucx/skills/layer_aliases/` | Add tdd/iplan aliases, remove cut layer aliases |
| `mcp_ucx/docs/specs/SPEC-003.md` | Reference new validation rules |
| `mcp_ucx/docs/ROADMAP.md` | Add V3 migration milestone |

## Files to Create

| File | Purpose |
|------|---------|
| `mcp_ucx/templates/TDD-TEMPLATE.yaml` | TDD document template (from ucx_flow_v3/07_TDD/) |
| `mcp_ucx/templates/IPLAN-TEMPLATE.yaml` | IPLAN document template (from ucx_flow_v3/08_IPLAN/) |
| `mcp_ucx/prompts/templates/creation/UCC_PROMPT_TDD.md` | TDD creation prompt |
| `mcp_ucx/prompts/templates/creation/UCC_PROMPT_IPLAN.md` | IPLAN creation prompt |
| `mcp_ucx/prompts/templates/review/UCR_PROMPT_TDD.md` | TDD review prompt |
| `mcp_ucx/prompts/templates/review/UCR_PROMPT_IPLAN.md` | IPLAN review prompt |
| `mcp_ucx/prompts/templates/remediation/UCRem_PROMPT_TDD.md` | TDD remediation prompt |
| `mcp_ucx/prompts/templates/remediation/UCRem_PROMPT_IPLAN.md` | IPLAN remediation prompt |
| `mcp_ucx/src/mcp_server/validation/tdd_rules.py` | TDD validation rules (G-07, G-09) |
| `mcp_ucx/src/mcp_server/validation/iplan_rules.py` | IPLAN validation rules (G-08, G-10, G-11) |
| `mcp_ucx/src/mcp_server/validation/chg_rules.py` | CHG governance validation (G-08, optional) |
| `mcp_ucx/tests/validation/test_tdd_rules.py` | TDD rules unit tests |
| `mcp_ucx/tests/validation/test_iplan_rules.py` | IPLAN rules unit tests |
| `mcp_ucx/tests/validation/test_chg_rules.py` | CHG rules unit tests (optional) |

## Success Criteria

1. TDD and IPLAN templates present in `mcp_ucx/templates/` (G-01 fixed)
2. All 6 prompt templates created and functional
3. `sdd_validate` correctly validates TDD and IPLAN documents with new rules
4. `sdd_create` generates TDD and IPLAN documents
5. `sdd_review` performs multi-persona review for TDD and IPLAN
6. `sdd_remediate` generates findings and fixes for TDD and IPLAN
7. READINESS_SCORE_FIELDS updated with correct v3 mappings (G-03 fixed - removed incorrect iplan mapping)
8. All unit and integration tests pass
9. Documentation updated to reflect v3 layer architecture
10. `sdd_next_action` detects YAML documents (G-02 fixed)
11. `sdd_prescreen` processes YAML documents (G-05 fixed)
12. `sdd_run_lifecycle` stages parameter is extensible (G-04 fixed)
13. `sdd_score_validate` enforces >=90 thresholds for TDD/IPLAN (G-06 fixed)
14. Cumulative tags enforcement active (max 8 at IPLAN) (G-07 partially)
15. TDD/IPLAN parity checks added to runner.py (G-12 fixed)
16. Validation runner uses `ucx_flow_v3/` path (G-01 fixed)

## Gap Summary Addressed

| Gap ID | Description | Priority | Status |
|--------|-------------|----------|--------|
| G-01 | Template root path in validation runner | Critical | Fixed in Phase 2 |
| G-02 | sdd_next_action YAML support | Critical | Fixed in Phase 3 |
| G-03 | IPLAN exec_ready_score mapping incorrect | Critical | Fixed in Phase 2 |
| G-04 | sdd_run_lifecycle stages enum hardcoded | High | Fixed in Phase 3 |
| G-05 | sdd_prescreen YAML support | High | Fixed in Phase 3 |
| G-06 | sdd_score_validate threshold awareness | High | Fixed in Phase 4 |
| G-07 | Maximum 8 cumulative tags enforcement | High | Fixed in Phase 2 |
| G-08 | CHG governance overlay integration | Medium | Phase 7 (optional) |
| G-09 | Test pyramid structure validation | Medium | Fixed in Phase 2 (tdd_rules.py) |
| G-10 | IPLAN file manifest detailed validation | Medium | Fixed in Phase 2 (iplan_rules.py) |
| G-11 | Session handoff protocol implementation | Medium | Fixed in Phase 2 (iplan_rules.py) |
| G-12 | Layer-specific parity checks for TDD/IPLAN | Medium | Fixed in Phase 2 |

## Dependencies

- V3 template files must exist at `ucx_flow_v3/07_TDD/TDD-TEMPLATE.yaml` and `ucx_flow_v3/08_IPLAN/IPLAN-TEMPLATE.yaml`
- `ucx_flow_v3/LAYER_REGISTRY.yaml` must be accessible
- No external package dependencies required

## Risks

| Risk | Mitigation |
|------|-----------|
| Breaking change to READINESS_SCORE_FIELDS | Support both old and new field names during transition period |
| Old templates removed too early | Keep in `templates/archive/` with validation support for 1 release |
| Prompt template quality | Base on existing prompt patterns; review against V3 template structure |
