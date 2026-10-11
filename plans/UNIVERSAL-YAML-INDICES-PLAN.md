# Plan: Universal AI-First 5-Quadrant YAML Index Modernization Across All SDD Layers

## Metadata

| Field | Value |
| --- | --- |
| Author | Framework Maintainer |
| Authority | Decision GD-74, Stage 2 Universal Index Architecture Mandate |
| Framework Version | 0.91.6 |
| Target Version | 0.91.7 |
| Date | 2026-10-11 |
| Status | Proposed |

## Objective

Modernize all remaining eight SDD layer index templates (`01_BRD`, `02_PRD`, `03_EARS`, `04_BDD`, `06_SPEC`, `07_TDD`, `09_CHG`, `10_EVAL`) from legacy Markdown (`*-00_index.TEMPLATE.md`) to canonical, agent-readable YAML specifications (`*-00_index.TEMPLATE.yaml`).

Unify all 10 SDD layers (combining with Layer 05 ADR modernized in CHG-87 and Layer 08 IPLAN) under a coherent **AI-First 5-Quadrant YAML Index Architecture**. In this architecture:

- Machine-readable YAML is the sole source of truth; human views are generated on-demand by AI agents.
- Each index provides structured metadata, a document registry, a planned backlog, layer-specific intelligence/traceability metrics, and declarative agent update triggers.
- The framework index ecosystem becomes 100% structured, deterministic, and AI-native.

## Scope

In scope:

- Convert eight remaining index templates to YAML:
  1. `framework/layers/01_BRD/BRD-00_index.TEMPLATE.yaml`
  2. `framework/layers/02_PRD/PRD-00_index.TEMPLATE.yaml`
  3. `framework/layers/03_EARS/EARS-00_index.TEMPLATE.yaml`
  4. `framework/layers/04_BDD/BDD-00_index.TEMPLATE.yaml`
  5. `framework/layers/06_SPEC/SPEC-00_index.TEMPLATE.yaml`
  6. `framework/layers/07_TDD/TDD-00_index.TEMPLATE.yaml`
  7. `framework/layers/09_CHG/CHG-00_index.TEMPLATE.yaml`
  8. `framework/layers/10_EVAL/EVAL-00_index.TEMPLATE.yaml`
- Archive pre-change Markdown index templates in `framework/archive/CHG-88/templates/`.
- Update `framework/registry/LAYER_REGISTRY.yaml` header comments to document universal YAML index templates across all 10 layers.
- Update layer READMEs and workflow standards to reference `*-00_index.TEMPLATE.yaml`.
- Ratify Decision `GD-75` (DEC-CHG-88) in `framework/governance/DECISIONS.md`.
- Update conformance mutation test `tests/conformance/test_instance_format_ssot.py` to reflect 6 sanctioned index mentions outside index files.
- Author authorizing change vehicles: `CHG-88.yaml` and `IPLAN-88.yaml` in `framework/archive/CHG-88/`.
- Advance framework spec version to `0.91.7` via `hooks/sync-version-refs.sh`.
- Validate with `sdd_doc_lint`, `test_index_template_lint.py`, `chg_lint.py`, and full test suites.

Out of scope:

- Modifying Layer 05 (`ADR-00_index.TEMPLATE.yaml`) or Layer 08 (`IPLAN-00_index.TEMPLATE.yaml`), which are already YAML.
- Altering layer instance templates (`*-TEMPLATE.yaml`).

## Unified 5-Quadrant YAML Index Specification

Every layer index template implements the 5-Quadrant architecture tailored to its domain:

```yaml
# =============================================================================
# Quadrant 1: Metadata & AI-First Contract
# =============================================================================
metadata:
  schema_version: "1.0"           # Strictly "1.0" per test_template_conventions.py
  framework_version: "[X.Y.Z]"     # Synced from framework/VERSION
  document_type: "<layer>-registry"
  artifact_type: "<LAYER>-INDEX"   # Matches sdd_doc_lint exemption marker
  layer: <N>
  status: "Active"
  format_ssot: "Machine-readable YAML is the sole source of truth; human views are generated on-demand by AI agents."
  total_items: 0
  last_updated: "YYYY-MM-DD"

# =============================================================================
# Quadrant 2: Document Registry (Layer Entities)
# =============================================================================
<collection_key>: []  # e.g., brds, prds, requirements, scenarios, specs, test_suites, changes, evaluations
  # Structured records containing ID, title, status, version, links, owner

# =============================================================================
# Quadrant 3: Backlog (Planned & Hypothesized Work)
# =============================================================================
backlog: []
  # Future work, MVP cycles, planned components, or candidate requirements

# =============================================================================
# Quadrant 4: Layer Intelligence & Cross-Layer Traceability
# =============================================================================
<intelligence_key>:
  # Upstream coverage matrices, quality gate thresholds, health indicators,
  # or module categorization (e.g., module_categories, traceability, thresholds)

# =============================================================================
# Quadrant 5: Agent Update Triggers & Maintenance Policies
# =============================================================================
update_triggers:
  _guidance: "When and how AI agents maintain this registry."
  on_document_created: []
  on_status_change: []
  on_document_deprecated: []
```

## Layer-Specific Schema Mapping

1. **Layer 01 (`BRD-00_index.TEMPLATE.yaml`)**:
   - Quadrant 2: `brds: []` (fields: `id`, `title`, `module`, `status`, `prd_ready`, `file_path`, `lead`)
   - Quadrant 3: `backlog: []` (fields: `id`, `title`, `cycle`, `priority`, `target_prod`, `depends_on`, `status`, `notes`)
   - Quadrant 4: `module_categories: []` (taxonomy of business & foundational modules)
   - Quadrant 5: `update_triggers` (`on_brd_created`, `on_status_change`, `on_brd_graduated`)

2. **Layer 02 (`PRD-00_index.TEMPLATE.yaml`)**:
   - Quadrant 2: `prds: []` (fields: `id`, `title`, `status`, `related_brd`, `features_count`, `priority`, `file_path`, `ears_ready_score`)
   - Quadrant 3: `backlog: []` (fields: `id`, `title`, `priority`, `target_date`, `notes`)
   - Quadrant 4: `thresholds: []` (cross-system quantitative parameters with `@threshold:` keys)
   - Quadrant 5: `update_triggers` (`on_prd_created`, `on_status_change`, `on_threshold_updated`)

3. **Layer 03 (`EARS-00_index.TEMPLATE.yaml`)**:
   - Quadrant 2: `requirements_documents: []` (fields: `id`, `title`, `statement_types`, `status`, `related_prd`, `bdd_ready_score`, `file_path`)
   - Quadrant 3: `backlog: []` (fields: `id`, `title`, `source_prd`, `priority`, `notes`)
   - Quadrant 4: `statement_patterns: []` (canonical EARS rules: Event-driven, State-driven, Optional, Unwanted, Ubiquitous)
   - Quadrant 5: `update_triggers` (`on_ears_created`, `on_status_change`, `on_verification`)

4. **Layer 04 (`BDD-00_index.TEMPLATE.yaml`)**:
   - Quadrant 2: `bdd_suites: []` (fields: `id`, `feature`, `upstream_ears`, `scenario_count`, `status`, `file_path`)
   - Quadrant 3: `backlog: []` (fields: `id`, `feature`, `source_ears`, `priority`, `notes`)
   - Quadrant 4: `traceability_matrix:` (mapping from EARS to BDD scenarios and downstream SPEC/TDD realization)
   - Quadrant 5: `update_triggers` (`on_bdd_created`, `on_scenario_added`, `on_status_change`)

5. **Layer 06 (`SPEC-00_index.TEMPLATE.yaml`)**:
   - Quadrant 2: `specs: []` (fields: `id`, `component`, `adr_ref`, `tdd_target`, `status`, `tdd_ready_score`, `file_path`)
   - Quadrant 3: `backlog: []` (fields: `id`, `component`, `upstream_bdd`, `priority`, `notes`)
   - Quadrant 4: `component_interfaces: []` (cross-component communication contracts, DFD/C4 mappings)
   - Quadrant 5: `update_triggers` (`on_spec_created`, `on_interface_updated`, `on_tdd_paired`)

6. **Layer 07 (`TDD-00_index.TEMPLATE.yaml`)**:
   - Quadrant 2: `test_suites: []` (fields: `id`, `component`, `spec_ref`, `bdd_refs`, `adr_refs`, `iplan_target`, `iplan_ready_score`, `status`, `file_path`)
   - Quadrant 3: `backlog: []` (fields: `id`, `component`, `source_spec`, `priority`, `notes`)
   - Quadrant 4: `quality_thresholds: []` (coverage floors, mutation scores, performance SLAs)
   - Quadrant 5: `update_triggers` (`on_tdd_created`, `on_status_change`, `on_iplan_sync`)

7. **Layer 09 (`CHG-00_index.TEMPLATE.yaml`)**:
   - Quadrant 2: `change_records: []` (fields: `id`, `title`, `change_level`, `flow_code`, `status`, `entry_gate`, `file_path`, `semver_impact`)
   - Quadrant 3: `backlog: []` (fields: `id`, `title`, `priority`, `target_date`, `notes`)
   - Quadrant 4: `gate_registry: []` (GATE-01, 03, 06, 08, CODE, SPEC mappings)
   - Quadrant 5: `update_triggers` (`on_chg_created`, `on_gate_approved`, `on_implementation_completed`)

8. **Layer 10 (`EVAL-00_index.TEMPLATE.yaml`)**:
   - Quadrant 2: `evaluations: []` (fields: `id`, `owning_iplan`, `track`, `latest_verdict`, `cycles_count`, `open_findings`, `status`, `file_path`)
   - Quadrant 3: `backlog: []` (fields: `id`, `owning_iplan`, `track`, `priority`, `notes`)
   - Quadrant 4: `eval_tracks: []` (functional verification vs unit/smoke track configurations)
   - Quadrant 5: `update_triggers` (`on_eval_created`, `on_cycle_executed`, `on_verdict_rendered`)

## Execution Phases

### Phase 1: Authoring 8 YAML Index Templates & Archiving Legacy Markdown

1. Author `framework/layers/01_BRD/BRD-00_index.TEMPLATE.yaml`.
2. Author `framework/layers/02_PRD/PRD-00_index.TEMPLATE.yaml`.
3. Author `framework/layers/03_EARS/EARS-00_index.TEMPLATE.yaml`.
4. Author `framework/layers/04_BDD/BDD-00_index.TEMPLATE.yaml`.
5. Author `framework/layers/06_SPEC/SPEC-00_index.TEMPLATE.yaml`.
6. Author `framework/layers/07_TDD/TDD-00_index.TEMPLATE.yaml`.
7. Author `framework/layers/09_CHG/CHG-00_index.TEMPLATE.yaml`.
8. Author `framework/layers/10_EVAL/EVAL-00_index.TEMPLATE.yaml`.
9. Move legacy `*-00_index.TEMPLATE.md` files to `framework/archive/CHG-88/templates/`.
10. Verify `tests/conformance/test_index_template_lint.py` discovers exactly 10 index templates and lints clean.

### Phase 2: Registry & Standards Synchronization

1. Update `framework/registry/LAYER_REGISTRY.yaml` header comments to document universal YAML index templates across all layers.
2. Update Layer 01–04, 06, 07, 09, 10 READMEs and normative workflow standards.
3. Update root `README.md` spec tracking.

### Phase 3: Conformance Pin Update, Decision Ratification & Version Bump

1. Update `tests/conformance/test_instance_format_ssot.py` assertion from 12 to 6 sanctioned index mentions.
2. Ratify Decision `GD-75` (DEC-CHG-88) in `framework/governance/DECISIONS.md`.
3. Create `framework/archive/CHG-88/CHG-88.yaml` and `framework/archive/CHG-88/IPLAN-88.yaml`.
4. Bump `framework/VERSION` to `0.91.7` and update `framework/CHANGELOG.md`.
5. Run `hooks/sync-version-refs.sh` for full fanout.

### Phase 4: Full Verification Battery

1. Run `python3 sdd_doc_lint/chg_lint.py framework/archive/CHG-88/CHG-88.yaml`.
2. Run `pytest tests/conformance/test_index_template_lint.py`.
3. Run `pytest tests/conformance/test_instance_format_ssot.py`.
4. Run `pytest tests/conformance/test_sync_version_refs.py`.
5. Run `python3 -m unittest discover -s tests/unit`.
6. Run `python3 -m sdd_doc_lint.swf_lint framework/`.
7. Run `npx markdownlint-cli2`.
8. Run full conformance and acceptance suites.

## Claim ledger

| # | Claim | Symbol | Citation |
|---|---|---|---|
| 1 | Index template discovery matches `<TYPE>-00_index.TEMPLATE.*` | `_index_templates` | tests/conformance/test_index_template_lint.py:32 |
| 2 | Index template test asserts exactly 10 templates exist | `test_all_ten_index_templates_present` | tests/conformance/test_index_template_lint.py:41 |
| 3 | Index templates are exempt from STRUCT01 and -INDEX ID02 | `test_index_templates_emit_no_struct01_or_index_id02` | tests/conformance/test_index_template_lint.py:49 |
| 4 | Template YAMLs must declare schema_version: "1.0" | `test_yaml_templates_declare_schema_version` | tests/unit/test_template_conventions.py:57 |
| 5 | LAYER_REGISTRY index templates block describes per-layer index formats | `Index templates:` | framework/registry/LAYER_REGISTRY.yaml:51 |
| 6 | Removing index exemption surfaces sanctioned mentions | `test_index_exemption_is_mention_level_not_file_level` | tests/conformance/test_instance_format_ssot.py:105 |
| 7 | Decision GD-74 ratified Layer 05 YAML index modernization | `GD-74` | framework/governance/DECISIONS.md:12 |
| 8 | Index filename regex recognizes any `TYPE-00_index` file in `sdd_doc_lint` | `_INDEX_FILENAME` | `sdd_doc_lint/__init__.py:1612` |
| 9 | Index doc exemption recognizes `artifact_type` ending with -INDEX | `_is_index_doc` | `sdd_doc_lint/__init__.py:1615` |
| 10 | TDD index sync rule requires maintaining IPLAN status alignment | `TDD-SYNC-E` | framework/layers/08_IPLAN/IPLAN-00_index.TEMPLATE.yaml:8 |

## Review log

### Pass 1 - 2026-10-11T17:40:00Z - independent

Reviewer: Spec Auditor (Subagent)

Findings:

1. Gaps: Verified that all 8 layers have corresponding `.TEMPLATE.md` files that can be converted cleanly into `.TEMPLATE.yaml` without loss of domain information.
2. Mutation pin: When the 6 remaining `.md` index files for layers 01, 02, 03, 04, 06, 07 are converted to `.yaml`, the number of surfaced violations in `test_index_exemption_is_mention_level_not_file_level` drops from 12 to 6 (the remaining 6 are outside index files).
3. Conformance discovery: Confirmed `_index_templates()` in `test_index_template_lint.py` matches both `.md` and `.yaml`, ensuring total count remains pinned at 10.

Resolution: Verified against codebase. 0 open findings.

### Pass 2 - 2026-10-11T17:42:00Z - independent

Reviewer: Lead Architect (Subagent)

Findings:

1. Schema consistency: Ensure all 8 new YAML index templates declare `schema_version: "1.0"` (string) to prevent `test_template_conventions.py` assertion errors.
2. AI-First SSOT contract: Include explicit `format_ssot` disclaimer across all templates stating that machine-readable YAML is the primary source of truth, and human views are generated dynamically.
3. Pre-change snapshots: Ensure all 8 legacy `.md` templates are moved into `framework/archive/CHG-88/templates/` to preserve historical lineage.

Resolution: Incorporated complete design into execution plan. 0 open findings.

**Result:** ready
