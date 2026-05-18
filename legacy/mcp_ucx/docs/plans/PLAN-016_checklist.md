# PLAN-016 Executable Checklist

**Plan**: [PLAN-016_cross_section_validation.md](PLAN-016_cross_section_validation.md)
**Target**: mcp_ucx v1.7.0 / ucx_framework v0.14.0

---

## Phase 0: Baseline

- [ ] **0.1** Run existing test suite — all must pass before any changes
  ```bash
  cd /opt/data/ucx_framework && python -m pytest mcp_ucx/tests/unit/ -v
  ```
  **Expected**: All tests in `test_validation_runner.py`, `test_link_validation_runner.py`, and others pass
  **Record**: test count and pass rate as baseline

---

## Phase 1: Generic Cross-Section Module (Tier 1)

### File: `mcp_ucx/src/mcp_server/validation/cross_section.py` — CREATE (~200 lines)

- [ ] **1.1** Create file with imports:
  ```python
  from __future__ import annotations
  import json
  import re
  from typing import Any
  ```

- [ ] **1.2** Add `READINESS_SCORE_FIELDS` constant:
  ```python
  READINESS_SCORE_FIELDS: dict[str, str] = {
      "brd": "prd_ready_score",
      "prd": "ears_ready_score",
      "ears": "bdd_ready_score",
      "bdd": "adr_ready_score",
      "adr": "sys_ready_score",
      "sys": "req_ready_score",
      "req": "spec_ready_score",
      "ctr": "spec_ready_score",
      "spec": "task_ready_score",
      "tspec": "tasks_ready_score",
      "tasks": "execution_ready_score",
  }
  ```

- [ ] **1.3** Add `DIAGRAM_CONTRACT_LAYERS` constant:
  ```python
  DIAGRAM_CONTRACT_LAYERS: set[str] = {"brd", "prd", "adr", "sys", "spec"}
  ```

- [ ] **1.4** Implement `_collect_all_ids(yaml_data: dict) -> set[str]`:
  - Recursively walk the entire YAML dict
  - Collect all values of keys named `id` that match `r'^[A-Z]{2,8}\.\d{2,}\.[0-9a-f]{4,8}$'`
  - Return set of found IDs

- [ ] **1.5** Implement `_collect_referenced_ids(data: Any) -> set[str]`:
  - Recursively walk `traceability` section
  - Find all strings matching element ID pattern `r'[A-Z]{2,8}\.\d{2,}\.[0-9a-f]{4,8}'`
  - Return set of referenced IDs

- [ ] **1.6** Implement `_check_traceability_id_existence()` (SDD-XS-001):
  - Extract `traceability` key from yaml_data; if absent, skip with pass
  - Call `_collect_all_ids()` on full yaml_data to build registry
  - Call `_collect_referenced_ids()` on traceability section
  - For each referenced ID not in registry: append to errors `f"SDD-XS-001: Traceability references non-existent ID: {id}"`
  - If all found: append to passes `f"SDD-XS-001: All {len(refs)} traceability IDs exist in document"`

- [ ] **1.7** Implement `_check_readiness_score_plausibility()` (SDD-XS-002):
  - Look up score field name from `READINESS_SCORE_FIELDS[doc_type]`; if unknown layer, skip
  - Search yaml_data recursively for the field (may be in `document_control` or top-level)
  - Parse score string — match `r'(\d+)/(\d+)'`; extract numerator
  - If numerator equals denominator (100/100) AND (len(errors) > 0 or len(warnings) > 0): append warning `f"SDD-XS-002: {field_name} is {score} but validation has {len(errors)} errors and {len(warnings)} warnings — recalculate"`
  - If score is not 100/100 or no issues: append pass

- [ ] **1.8** Implement `_check_diagram_registry()` (SDD-XS-003):
  - If `doc_type` not in `DIAGRAM_CONTRACT_LAYERS`: skip
  - Check if `metadata.diagram_standard` exists with `tags` key in yaml_data
  - If diagram contract exists: check `diagrams.items` is a non-empty list
  - If missing/empty: append warning `f"SDD-XS-003: Document has diagram contract but no diagrams.items registered"`
  - If present: append pass with item count

- [ ] **1.9** Implement main entry `run_cross_section_checks()`:
  ```python
  def run_cross_section_checks(
      *, yaml_data: dict[str, object], doc_type: str,
      errors: list[str], warnings: list[str], passes: list[str],
  ) -> None:
  ```
  - Call `_check_traceability_id_existence(yaml_data, errors, warnings, passes)`
  - Call `_check_diagram_registry(yaml_data, doc_type, errors, warnings, passes)`
  - Call `_check_readiness_score_plausibility(yaml_data, doc_type, errors, warnings, passes)` — LAST (reads current errors/warnings)

- [ ] **1.10** Implement MD fallback `run_cross_section_checks_md()`:
  ```python
  def run_cross_section_checks_md(
      *, content: str, doc_type: str,
      errors: list[str], warnings: list[str], passes: list[str],
  ) -> None:
  ```
  - SDD-XS-001: Extract all ID-shaped strings from content, build registry from `id:` lines, check `## Traceability` or `## 19.` section for references
  - SDD-XS-002: Skip with info "Structured validation requires YAML format"
  - SDD-XS-003: Skip with info "Structured validation requires YAML format"

---

## Phase 2: BRD-Specific Module (Tier 2)

### File: `mcp_ucx/src/mcp_server/validation/brd_rules.py` — CREATE (~200 lines)

- [ ] **2.1** Create file with imports:
  ```python
  from __future__ import annotations
  import json
  import re
  from typing import Any
  ```

- [ ] **2.2** Implement `_check_adt_propagation()` (BRD-XS-001):
  - Extract `adr_topics.topics` list from yaml_data; if absent, skip
  - For each topic: find entry in `alternatives` where `rationale` starts with "Selected" (case-insensitive)
  - Extract that entry's `option` value as the selected name
  - Serialize `implementation_approach` and `cost_benefit` sections to lowercase string via `json.dumps(...).lower()`
  - Check if `selected_name.lower()` appears in serialized string
  - If missing from either section: append warning `f"BRD-XS-001: ADT '{topic_title}' selected '{selected_name}' not found in {section_name}"`
  - If all propagated: append pass

- [ ] **2.3** Implement `_check_phase_alignment()` (BRD-XS-002):
  - Extract scope phases from `project_scope.phasing.phases` — collect `phase` values into list
  - Extract impl phases from `implementation_approach.phases.items` — collect `phase` values into list
  - If either key missing: skip with pass (section not present)
  - Compare sets: `scope_set = set(scope_phases)`, `impl_set = set(impl_phases)`
  - If `scope_set != impl_set`:
    - Missing from impl: `scope_set - impl_set` → error `f"BRD-XS-002: Phases in scope but missing from implementation: {missing}"`
    - Extra in impl: `impl_set - scope_set` → error `f"BRD-XS-002: Phases in implementation but missing from scope: {extra}"`
  - If count differs: error `f"BRD-XS-002: Phase count mismatch — scope has {len(scope_phases)}, implementation has {len(impl_phases)}"`
  - If aligned: pass `f"BRD-XS-002: {len(scope_phases)} phases aligned between scope and implementation"`

- [ ] **2.4** Implement `_check_entity_consistency()` (BRD-XS-004):
  - Extract entities from `executive_summary.key_stakeholders[].stakeholder` → set
  - Extract partner names from `executive_summary.business_problem` text: regex `r'\(([^)]+)\)'` to find parenthesized lists, split by comma, strip
  - Build search corpus: serialize `functional_requirements`, `stakeholders`, `introduction` sections to lowercase string
  - For each extracted entity: check if `entity.lower()` in corpus
  - If not found: append warning `f"BRD-XS-004: Entity '{entity}' in executive summary not found in functional requirements or stakeholders"`
  - If all found: append pass

- [ ] **2.5** Implement `_check_currency_consistency()` (BRD-XS-005):
  - Check if `mandatory_conditions` key exists with `precision` subkey; if not, skip with pass "No currency scope detected"
  - Extract currency codes from `mandatory_conditions` text: regex `r'\b([A-Z]{3,4})\b'` filtered to known currencies (`USD, MXN, UZS, USDC, EUR, GBP, BRL, COP`)
  - Extract currency codes from first FR's acceptance criteria (search for `currency` in items)
  - Codes in mandatory_conditions not in FR: append warning `f"BRD-XS-005: Currency '{code}' in mandatory conditions but not in FR acceptance criteria"`
  - If superset: append pass

- [ ] **2.6** Implement main entry `run_brd_cross_section_checks()`:
  ```python
  def run_brd_cross_section_checks(
      *, yaml_data: dict[str, object],
      errors: list[str], warnings: list[str], passes: list[str],
  ) -> None:
  ```
  - Call all 4 BRD-XS check functions in order: 001, 002, 004, 005

- [ ] **2.7** Implement MD fallback `run_brd_cross_section_checks_md()`:
  - BRD-XS-002: Count phase headings matching `Phase \d+` in scope and implementation sections
  - Others: Skip with info "Structured BRD validation requires YAML format"

---

## Phase 3: Validation Runner Changes

### File: `mcp_ucx/src/mcp_server/validation/runner.py` — MODIFY (+80-100 lines)

- [ ] **3.1** Add imports after line 9 (`import yaml`):
  ```python
  from mcp_server.validation.cross_section import (
      run_cross_section_checks,
      run_cross_section_checks_md,
  )
  from mcp_server.validation.brd_rules import (
      run_brd_cross_section_checks,
      run_brd_cross_section_checks_md,
  )
  ```

- [ ] **3.2** Add `_collect_yaml_files()` function after `_collect_markdown_files()` (after line 61):
  ```python
  def _collect_yaml_files(document_path: Path) -> list[Path]:
      """Collect YAML document files, excluding templates."""
      if document_path.is_file() and document_path.suffix.lower() in (".yaml", ".yml"):
          return [document_path]
      if not document_path.is_dir():
          return []
      candidates = sorted(document_path.glob("*.yaml"))
      return [
          path for path in candidates
          if re.match(r"^[A-Z]+-\d+_.+\.yaml$", path.name)
          and "TEMPLATE" not in path.name.upper()
      ]
  ```

- [ ] **3.3** Add `_validate_yaml_metadata()` helper (after `_collect_yaml_files`):
  ```python
  def _validate_yaml_metadata(
      yaml_data: dict[str, object],
      template: dict[str, object],
      errors: list[str],
      warnings: list[str],
      passes: list[str],
  ) -> None:
      """Validate YAML document metadata against template requirements."""
      metadata = yaml_data.get("metadata", {})
      if not isinstance(metadata, dict):
          warnings.append("YAML document missing metadata section")
          return
      # Tag validation
      tags = metadata.get("tags", [])
      tag_set = {t for t in tags if isinstance(t, str)} if isinstance(tags, list) else set()
      for required_tag in _extract_required_tags(template):
          if required_tag in tag_set:
              passes.append(f"required tag present: {required_tag}")
          else:
              errors.append(f"Missing required tag: {required_tag}")
      # Document type check
      doc_type_val = metadata.get("document_type")
      if doc_type_val is None:
          doc_type_val = yaml_data.get("document_control", {})
          if isinstance(doc_type_val, dict):
              doc_type_val = None  # not found
      if isinstance(doc_type_val, str) and doc_type_val == "template":
          warnings.append("document_type is 'template' — should be instance type (e.g., 'brd-document')")
  ```

- [ ] **3.4** Modify `run_project_validation_build()` — replace lines 254-319 with YAML/MD decision fork:
  - After `template, template_error = ...` and error/warning/passes init (lines 252-257):
  - Add YAML collection: `yaml_files = _collect_yaml_files(document_path)`
  - Add decision fork:
    ```python
    yaml_files = _collect_yaml_files(document_path)
    
    if yaml_files:
        # --- YAML validation path ---
        yaml_text = yaml_files[0].read_text(encoding="utf-8")
        yaml_data = yaml.safe_load(yaml_text)
        if not isinstance(yaml_data, dict):
            errors.append("YAML file did not parse to a mapping")
            yaml_data = {}
        else:
            passes.append(f"yaml_parsed: {yaml_files[0].name}")
        
        files = yaml_files  # for report
        _validate_yaml_metadata(yaml_data, template, errors, warnings, passes)
        
        # Tier 1: Generic cross-section (all layers)
        run_cross_section_checks(
            yaml_data=yaml_data,
            doc_type=doc_type,
            errors=errors,
            warnings=warnings,
            passes=passes,
        )
        # Tier 2: Layer-specific
        if doc_type.strip().lower() == "brd":
            run_brd_cross_section_checks(
                yaml_data=yaml_data,
                errors=errors,
                warnings=warnings,
                passes=passes,
            )
        combined_content = yaml_text  # for report
    else:
        # --- Existing MD validation path (unchanged) ---
        files = _collect_markdown_files(document_path)
        if not files:
            errors.append("No markdown or YAML files found to validate")
        
        frontmatter: dict[str, object] = {}
        if files:
            frontmatter = _parse_frontmatter(files[0].read_text(encoding="utf-8"))
            if not frontmatter:
                errors.append("Missing or invalid YAML frontmatter")
        
        # ... existing custom_fields, tags, sections validation (lines 271-312) ...
        # (keep all existing MD validation logic exactly as-is)
        
        combined_content = "\n\n".join(
            path.read_text(encoding="utf-8") for path in files
        ) if files else ""
        
        _run_doc_type_parity_checks(
            doc_type=doc_type, content=combined_content,
            errors=errors, passes=passes,
        )
        
        # Tier 1: Generic cross-section (degraded MD)
        run_cross_section_checks_md(
            content=combined_content, doc_type=doc_type,
            errors=errors, warnings=warnings, passes=passes,
        )
        # Tier 2: Layer-specific (degraded MD)
        if doc_type.strip().lower() == "brd":
            run_brd_cross_section_checks_md(
                content=combined_content,
                errors=errors, warnings=warnings, passes=passes,
            )
    ```
  - Keep report building (lines 321-362) unchanged — it uses `errors`, `warnings`, `passes`, `files`

### File: `mcp_ucx/src/mcp_server/validation/__init__.py` — MODIFY

- [ ] **3.5** Update exports:
  ```python
  """Script-based document validation helpers."""
  
  from .runner import ValidationRunResult, run_project_validation_build
  from .cross_section import run_cross_section_checks, run_cross_section_checks_md
  from .brd_rules import run_brd_cross_section_checks, run_brd_cross_section_checks_md
  
  __all__ = [
      "ValidationRunResult",
      "run_project_validation_build",
      "run_cross_section_checks",
      "run_cross_section_checks_md",
      "run_brd_cross_section_checks",
      "run_brd_cross_section_checks_md",
  ]
  ```

---

## Phase 4: Tests

### File: `mcp_ucx/tests/unit/test_cross_section.py` — CREATE (~200 lines)

- [ ] **4.1** Test SDD-XS-001 passes when all traceability IDs exist:
  - Fixture: YAML with `quality_expectations.performance[0].id = "BRD.04.cfab"` and `traceability.matrix[0].quality_attributes = ["BRD.04.cfab"]`
  - Assert: no errors, passes contains "SDD-XS-001"

- [ ] **4.2** Test SDD-XS-001 errors on phantom ID:
  - Fixture: traceability references `"BRD.04.zzzz"` but no such ID in document
  - Assert: errors contains "SDD-XS-001" and "BRD.04.zzzz"

- [ ] **4.3** Test SDD-XS-001 works for PRD doc_type:
  - Fixture: PRD YAML with `traceability` section
  - Assert: rule runs (not BRD-only)

- [ ] **4.4** Test SDD-XS-002 warns when score is 100/100 with errors:
  - Fixture: BRD YAML with `document_control.prd_ready_score: "100/100"`, pre-populated errors list
  - Assert: warnings contains "SDD-XS-002"

- [ ] **4.5** Test SDD-XS-002 passes when score is 100/100 with no issues:
  - Fixture: same but errors/warnings lists empty
  - Assert: passes contains "SDD-XS-002"

- [ ] **4.6** Test SDD-XS-002 detects correct field per layer:
  - Fixtures: PRD with `ears_ready_score`, EARS with `bdd_ready_score`
  - Assert: each finds its field

- [ ] **4.7** Test SDD-XS-003 warns when diagram contract present but no items:
  - Fixture: BRD YAML with `metadata.diagram_standard.tags: ["@diagram: c4-l1"]` but no `diagrams` key
  - Assert: warnings contains "SDD-XS-003"

- [ ] **4.8** Test SDD-XS-003 skips for layers without diagram contracts:
  - Fixture: EARS YAML (no diagram contract)
  - Assert: no warnings from SDD-XS-003

- [ ] **4.9** Test MD fallback runs SDD-XS-001:
  - Fixture: MD content with `id: BRD.04.cfab` lines and `## Traceability` section
  - Assert: rule executes without crash

- [ ] **4.10** Test MD fallback skips SDD-XS-002/003 with info:
  - Assert: no errors/warnings from those rules on MD content

### File: `mcp_ucx/tests/unit/test_brd_rules.py` — CREATE (~250 lines)

- [ ] **4.11** Test BRD-XS-001 passes when selected ADT option in implementation:
  - Fixture: ADT with `alternatives[0].option: "Custom PostgreSQL"`, `rationale: "Selected - ..."`, `implementation_approach` containing "Custom PostgreSQL"
  - Assert: passes contains "BRD-XS-001"

- [ ] **4.12** Test BRD-XS-001 warns when selected option missing from cost section:
  - Fixture: ADT selected "Custom PostgreSQL" but `cost_benefit` has "Modern Treasury" only
  - Assert: warnings contains "BRD-XS-001" and "cost_benefit"

- [ ] **4.13** Test BRD-XS-001 case-insensitive match:
  - Fixture: selected "Custom PostgreSQL Ledger", implementation has "custom postgresql ledger"
  - Assert: passes (no warning)

- [ ] **4.14** Test BRD-XS-002 passes when phases match:
  - Fixture: `project_scope.phasing.phases` = 5 phases, `implementation_approach.phases.items` = same 5
  - Assert: passes contains "BRD-XS-002" with count

- [ ] **4.15** Test BRD-XS-002 errors on count mismatch:
  - Fixture: scope has 5 phases, implementation has 4
  - Assert: errors contains "BRD-XS-002" and "Phase 5"

- [ ] **4.16** Test BRD-XS-002 errors on name mismatch:
  - Fixture: scope has "Phase 1: Core", implementation has "Phase 1: Setup"
  - Assert: errors list names the mismatched phases

- [ ] **4.17** Test BRD-XS-004 passes when all entities referenced:
  - Fixture: exec summary stakeholder "Bridge", functional_requirements mentions "Bridge"
  - Assert: passes contains "BRD-XS-004"

- [ ] **4.18** Test BRD-XS-004 warns on stale entity:
  - Fixture: exec summary business_problem has "(Bridge, Sardine)", functional_requirements only has "Bridge"
  - Assert: warnings contains "BRD-XS-004" and "Sardine"

- [ ] **4.19** Test BRD-XS-005 passes when currency superset:
  - Fixture: mandatory_conditions.precision mentions "USD/UZS", FR has "MXN, USD, USDC, UZS"
  - Assert: passes

- [ ] **4.20** Test BRD-XS-005 warns on missing currency:
  - Fixture: mandatory_conditions mentions "UZS", FR only has "MXN, USD, USDC"
  - Assert: warnings contains "BRD-XS-005" and "UZS"

- [ ] **4.21** Test BRD-XS-005 skips when no currency keys:
  - Fixture: YAML without `mandatory_conditions.precision`
  - Assert: passes contains "No currency scope"

- [ ] **4.22** Test MD fallback phase count:
  - Fixture: MD with "## Phase 1" through "## Phase 5" in scope, only 4 in implementation
  - Assert: executes without crash

---

## Phase 5: Integration Test

- [ ] **5.1** Run full test suite:
  ```bash
  cd /opt/data/ucx_framework && python -m pytest mcp_ucx/tests/unit/ -v
  ```
  **Expected**: All existing + new tests pass, zero regressions

---

## Phase 6: Template Updates

### File: `mcp_ucx/templates/BRD-TEMPLATE.yaml` — MODIFY (+40 lines)

- [ ] **6.1** Add `diagrams` section after `executive_summary` section (find the `# Section 3` comment):
  ```yaml
  # =============================================================================
  # Diagrams Registry
  # =============================================================================
  diagrams:
    id: "{doc_type}.{doc_id}.xxxx"
    directory: "diagrams/"
    format: "SVG rendered from Mermaid sources (.mmd)"
    required_for_platform_brd:
      - type: "structure_overview"
        description: "Document section map with key metrics"
      - type: "cross_brd_dependencies"
        description: "Upstream/downstream BRD dependency graph"
      - type: "data_model"
        description: "Primary data model or entity hierarchy"
    required_for_feature_brd:
      - type: "user_journey"
        description: "Happy-path user flow"
      - type: "integration_points"
        description: "External system touchpoints"
    optional:
      - type: "implementation_phases"
      - type: "risk_summary"
      - type: "architecture_decisions"
      - type: "key_flow_diagrams"
    items: []
  ```

- [ ] **6.2** Add `cross_section_rules` to existing `metadata` section:
  ```yaml
    cross_section_rules:
      description: "Machine-enforced by sdd_validate (mcp_ucx)"
      generic:
        - id: SDD-XS-001
          rule: "All element IDs in traceability must exist in source sections"
        - id: SDD-XS-002
          rule: "Readiness score must be recalculated if validation findings exist"
        - id: SDD-XS-003
          rule: "Documents with diagram contracts must have diagrams section with items"
      brd_specific:
        - id: BRD-XS-001
          rule: "ADT selected decisions must propagate to implementation and cost sections"
        - id: BRD-XS-002
          rule: "Phase names and count must match between scope and implementation"
        - id: BRD-XS-004
          rule: "Entities in executive summary must appear in functional requirements or stakeholders"
        - id: BRD-XS-005
          rule: "Currency lists must be consistent across FR-01, mandatory conditions, acceptance criteria"
  ```

### File: `ucx_flow_v3/01_BRD/BRD-TEMPLATE.yaml` — SYNC

- [ ] **6.3** Copy exact same changes from step 6.1 and 6.2 to sync copy

### File: `mcp_ucx/templates/BRD-MD-TEMPLATE.md` — CREATE (~120 lines)

- [ ] **6.4** Create with:
  - YAML frontmatter block with fields: title, document_type, layer, schema_version, tags, brd_type, deliverable_type
  - Section heading template: `## N. Section Title` + newline + `` `[BRD.NN.xxxx]` ``
  - Diagram index section (## 2a. Diagram Index) with table: #, Diagram (link), ID, Scope
  - Inline diagram reference format: `> **Diagram**: [title](diagrams/filename.svg) \`[ID]\``
  - Table format specs for: stakeholders, RACI, risks (L/I/Score), ADTs (alternatives), costs, quality attributes
  - Bold formatting rule: `**MUST**`, `**SHALL**`, `**MUST NOT**` for business rules
  - User story format: As a / I want / So that
  - Cross-ref format: `` `[BRD.NN.xxxx]` `` inline, `BRD-NN` for doc-level

---

## Phase 7: Standards Update

### File: `ucx_flow_v3/DIAGRAM_STANDARDS.md` — MODIFY (+25 lines)

- [ ] **7.1** Add new subsection "BRD Required Diagrams by Type" after existing BRD diagram guidance:
  - Platform BRD table: 3 required (structure overview, cross-BRD deps, data model)
  - Feature BRD table: 2 required (user journey, integration points)
  - Optional list: implementation phases, risk summary, architecture decisions, key flows

- [ ] **7.2** Fix DFD-L0 vs DFD-L1 discrepancy:
  - Search for any `dfd-l0` references in BRD context
  - Standardize to `dfd-l1` (matches template metadata `@diagram: dfd-l1`)

---

## Phase 8: Smoke Tests

- [ ] **8.1** Run `sdd_validate` against BRD-04 YAML (pre-fix version from git):
  ```bash
  git show HEAD~2:docs/01_BRD/BRD-04_data_model_ledger/BRD-04_data_model_ledger.yaml > /tmp/brd04_prefix.yaml
  ```
  **Expected**: Detects phantom IDs (SDD-XS-001), score plausibility (SDD-XS-002), phase mismatch (BRD-XS-002), Modern Treasury inconsistency (BRD-XS-001)

- [ ] **8.2** Run `sdd_validate` against BRD-04 YAML (current post-fix version):
  **Expected**: Clean pass or warnings-only (no errors from cross-section rules)

- [ ] **8.3** Run `sdd_validate` against a PRD YAML (if available):
  **Expected**: SDD-XS-001/002/003 run, BRD-XS rules skipped

- [ ] **8.4** Run `sdd_validate` against MD-format BRD:
  **Expected**: Degraded path works, no crashes, info messages for YAML-only rules

- [ ] **8.5** Verify template sync:
  ```bash
  diff mcp_ucx/templates/BRD-TEMPLATE.yaml ucx_flow_v3/01_BRD/BRD-TEMPLATE.yaml
  ```
  **Expected**: Identical content

---

## Phase 9: Documentation (already done)

- [x] **9.1** Created `mcp_ucx/docs/plans/PLAN-016_cross_section_validation.md`
- [x] **9.2** Created `mcp_ucx/docs/CHANGELOG/CHANGELOG_v1.7.0.md`
- [x] **9.3** Updated `mcp_ucx/docs/README.md` — added PLAN-016 + CHANGELOG v1.7.0 links
- [x] **9.4** Updated `mcp_ucx/docs/ROADMAP.md` — added v1.7.0 planned release
- [x] **9.5** Created `changelog/CHANGELOG_v0.14.0.md`
- [x] **9.6** Updated `roadmap/ROADMAP.md` — added v0.14.0 planned release

---

## Phase 10: Final Commit

- [ ] **10.1** Run full test suite one final time
- [ ] **10.2** Stage all changed files
- [ ] **10.3** Commit with message:
  ```
  feat(mcp_ucx): add cross-section validation rules (PLAN-016)
  
  Tier 1 (all layers): traceability ID existence (SDD-XS-001),
  readiness score plausibility (SDD-XS-002), diagram registry (SDD-XS-003).
  
  Tier 2 (BRD-specific): ADT propagation (BRD-XS-001), phase alignment
  (BRD-XS-002), entity consistency (BRD-XS-004), currency scope (BRD-XS-005).
  
  YAML document support in sdd_validate pipeline. BRD template updates
  (diagrams section, cross_section_rules). BRD-MD-TEMPLATE.md for
  YAML-to-MD rendering. DIAGRAM_STANDARDS.md BRD diagram list.
  ```
