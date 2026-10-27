# Implementation Plan: Native SDD Graph Migration for Tier 2 Module Specifications

## Executive Summary & Architecture Rationale

This plan defines the end-to-end migration of Tier 2 Module (Subsystem) specifications from static Markdown authoring ([`framework/templates/MODULE-TEMPLATE.md`](../framework/templates/MODULE-TEMPLATE.md#L6)) into Native SDD Typed Property Graphs ([`framework/templates/MODULE-TEMPLATE.md`](../framework/templates/MODULE-TEMPLATE.md#L10)), fulfilling the foundational Dual-Plane CQRS architecture established in [`framework/governance/DOC_GOVERNANCE_CORE.md`](../framework/governance/DOC_GOVERNANCE_CORE.md#L16).

### 1. Dual-Plane CQRS Rationale

Under [`framework/governance/DOC_GOVERNANCE_CORE.md`](../framework/governance/DOC_GOVERNANCE_CORE.md#L16) Rule 2:
> "YAML is the mandatory format and the source of truth... Markdown is optional and descriptive: a rendering of the YAML... Where a `.md` file restates YAML content it is generated, not authored."

All 10 SDD layers (from BRD through EVAL) operate on typed Property Graphs (`*-GRAPH-TEMPLATE.yaml`) and CNCF Serverless Workflows (`*-SWF-TEMPLATE.yaml`). Furthermore, Tier 1 Initiatives use [`framework/templates/INITIATIVE-GRAPH-TEMPLATE.yaml`](../framework/templates/INITIATIVE-GRAPH-TEMPLATE.yaml#L9) with `schema_version: "2.0-graph"` and `slice_id: "INIT-NN_[feature_slug]"` ([`framework/templates/INITIATIVE-GRAPH-TEMPLATE.yaml`](../framework/templates/INITIATIVE-GRAPH-TEMPLATE.yaml#L10)), and Tier 3 execution uses `EXECUTION-GRAPH-TEMPLATE.yaml`.

However, Tier 2 Modules were left authored as raw Markdown documents (`MODULE-TEMPLATE.md`) with frontmatter (`module_id: "MODULE-NN"`, `c4_level: "c4-l2"`). While [`framework/governance/SDD_GRAPH_SCHEMA_SPECIFICATION.md`](../framework/governance/SDD_GRAPH_SCHEMA_SPECIFICATION.md#L64) and [`framework/governance/sdd-graph.schema.json`](../framework/governance/sdd-graph.schema.json#L58) already reserve the `system_container` node ontology for `MODULE-NN` ([`framework/governance/sdd-graph.schema.json`](../framework/governance/sdd-graph.schema.json#L52)), there is currently no canonical template or automated projection adapter for modules.

### 2. Triple-Lens Modeling in Graph Representation

[`framework/governance/SEED_TO_MODULE_DECOMPOSITION.md`](../framework/governance/SEED_TO_MODULE_DECOMPOSITION.md#L50) establishes the Triple-Lens modeling standard for modules across 3 views:

1. **Structural (C4-L2 Container)**: Container boundaries, technology choices ([`framework/templates/MODULE-TEMPLATE.md`](../framework/templates/MODULE-TEMPLATE.md#L79)), runtime environments, and communication protocols.
2. **Data Movement (DFD-L2)**: Trust boundaries, data classifications, and data protection policies ([`framework/templates/MODULE-TEMPLATE.md`](../framework/templates/MODULE-TEMPLATE.md#L125)).
3. **Process Choreography**: Inter-module sequence flows, synchronous/asynchronous message interactions, and explicit failure recovery branches.

Migrating modules into graph slices completes the 3-tier continuum (Tier 1 Initiative $\rightarrow$ Tier 2 Module $\rightarrow$ Tier 3 Execution) and enables:

- Machine-verifiable end-to-end traceability: `seed_intent` ──`decomposes_to`──► `system_container` ([`framework/governance/SDD_GRAPH_SCHEMA_SPECIFICATION.md`](../framework/governance/SDD_GRAPH_SCHEMA_SPECIFICATION.md#L126), [`sdd_doc_lint/kuzu_adapter.py`](../sdd_doc_lint/kuzu_adapter.py#L90)) ──`decomposes_to`──► `component_contract` (`SPEC.06.01.xxxx`).
- Graph-driven projection: Generating `MODULE-NN_slug.md` and Mermaid diagrams (C4-L2, DFD-L2, Sequence) directly from YAML via [`sdd_doc_lint/observability_adapter.py`](../sdd_doc_lint/observability_adapter.py#L256).
- Analytical graph querying: Running Cypher queries in Kùzu across all module containers.

---

## User Review Required

> [!NOTE]
> All changes preserve complete backward compatibility. Existing `MODULE-TEMPLATE.md` remains the authoritative visual layout for generated Markdown spec sheets, while `MODULE-GRAPH-TEMPLATE.yaml` becomes the upstream machine-authored source of truth.

<!-- separator -->

> [!IMPORTANT]
> The migration will be governed by a dedicated Change Request (**CHG-118**, Flow DIR2C, Level C1) and Implementation Plan (**IPLAN-118**), creating pre-modification snapshots in `framework/archive/CHG-118/`.

---

## Open Questions

None. The ontology, schema patterns (`slice_id: "MODULE-NN_[slug]"`), node types (`system_container`), and relationship tables are already registered in [`framework/governance/sdd-graph.schema.json`](../framework/governance/sdd-graph.schema.json#L15), [`sdd_doc_lint/graph_engine.py`](../sdd_doc_lint/graph_engine.py#L20), and [`sdd_doc_lint/kuzu_adapter.py`](../sdd_doc_lint/kuzu_adapter.py#L40).

---

## Claim ledger

| # | Claim | Symbol | Citation |
|---|---|---|---|
| 1 | Module template defines module_id in document_control | `module_id: "MODULE-NN"` | framework/templates/MODULE-TEMPLATE.md:6 |
| 2 | Module template defines c4_level as c4-l2 | `c4_level: "c4-l2"` | framework/templates/MODULE-TEMPLATE.md:10 |
| 3 | Module template specifies candidate baseline selection status | `Candidate baseline identified; formal binding ratified at downstream Layer 05 ADR` | framework/templates/MODULE-TEMPLATE.md:79 |
| 4 | Module template carries Data Sensitivity and Protection Matrix table | `\| Data Entity \| Classification \| Storage Location \| In Transit \| At Rest \| Retention / Deletion Policy \|` | framework/templates/MODULE-TEMPLATE.md:125 |
| 5 | Seed decomposition playbook defines Triple-Lens modeling standard | `## 2. The Triple-Lens Modeling Standard` | framework/governance/SEED_TO_MODULE_DECOMPOSITION.md:50 |
| 6 | Seed decomposition playbook defines 5-step decomposition methodology | `## 3. The 5-Step Decomposition Methodology` | framework/governance/SEED_TO_MODULE_DECOMPOSITION.md:86 |
| 7 | Module layout standard specifies docs/modules directory location | `All module docs live in` | framework/governance/MODULE_LAYOUT.md:82 |
| 8 | Module layout standard documents directory naming convention | `MODULE-NN_descriptive-slug/` | framework/governance/MODULE_LAYOUT.md:98 |
| 9 | SDD graph specification defines system_container node ontology | `### 3.2 Tier 2: Subsystem Container (`system_container`)` | framework/governance/SDD_GRAPH_SCHEMA_SPECIFICATION.md:64 |
| 10 | SDD graph specification defines decomposes_to edge from seed_intent to system_container | `[seed_intent] ──decomposes_to──► [system_container]` | framework/governance/SDD_GRAPH_SCHEMA_SPECIFICATION.md:126 |
| 11 | SDD graph schema slice_id pattern accepts MODULE prefix | `^(INIT\|MODULE\|IPLAN\|EXEC\|[A-Z]{3,4})-` | framework/governance/sdd-graph.schema.json:15 |
| 12 | SDD graph schema node ID pattern accepts MODULE tokens | `MODULE-([0-9]{2}\|NN)` | framework/governance/sdd-graph.schema.json:52 |
| 13 | SDD graph schema includes system_container node type enum | `"system_container",` | framework/governance/sdd-graph.schema.json:58 |
| 14 | Graph engine defines system_container in canonical node types | `"system_container",` | sdd_doc_lint/graph_engine.py:20 |
| 15 | Graph engine pattern accepts MODULE-NN node IDs | `\|MODULE-[0-9]{2})$` | sdd_doc_lint/graph_engine.py:52 |
| 16 | Kuzu adapter defines system_container node table DDL | `"system_container": (` | sdd_doc_lint/kuzu_adapter.py:40 |
| 17 | Kuzu adapter decomposes_to relationship connects seed_intent to system_container | `FROM seed_intent TO system_container,` | sdd_doc_lint/kuzu_adapter.py:90 |
| 18 | Observability adapter renders system_container in C4 container diagram | `"system_container",` | sdd_doc_lint/observability_adapter.py:441 |
| 19 | Module contract conformance test suite defines ModuleTemplateContract | `class ModuleTemplateContract(unittest.TestCase):` | tests/conformance/test_module_contract.py:15 |
| 20 | SDD graph schema conformance test imports INITIATIVE template path | `INITIATIVE_TEMPLATE = FRAMEWORK / "templates" / "INITIATIVE-GRAPH-TEMPLATE.yaml"` | tests/conformance/test_sdd_graph_schema.py:22 |
| 21 | Document governance core establishes YAML as mandatory format and single source of truth | `YAML is the mandatory format and the source of truth` | framework/governance/DOC_GOVERNANCE_CORE.md:16 |
| 22 | Initiative graph template defines schema version 2.0-graph | `schema_version: "2.0-graph"` | framework/templates/INITIATIVE-GRAPH-TEMPLATE.yaml:9 |
| 23 | Initiative graph template defines slice_id pattern | `slice_id: "INIT-NN_[feature_slug]"` | framework/templates/INITIATIVE-GRAPH-TEMPLATE.yaml:10 |
| 24 | Decomposition serverless workflow declares template reference | `template: "framework/templates/MODULE-GRAPH-TEMPLATE.yaml"` | framework/governance/workflows/seed-to-module-decomposition.sw.yaml:51 |
| 25 | Seed contract mandates module formatting per template | `[`framework/templates/MODULE-GRAPH-TEMPLATE.yaml`]` | framework/governance/SEED_CONTRACT.md:229 |
| 26 | Seed decomposition playbook cites module living domain source of truth | `Living domain source of truth (MODULE_LAYOUT.md / MODULE-GRAPH-TEMPLATE.yaml / MODULE-TEMPLATE.md)` | framework/governance/SEED_TO_MODULE_DECOMPOSITION.md:38 |
| 27 | Seed decomposition playbook mandates template adherence | `[`framework/templates/MODULE-GRAPH-TEMPLATE.yaml`]` | framework/governance/SEED_TO_MODULE_DECOMPOSITION.md:160 |
| 28 | Module layout standard specifies canonical template in section 7 | `[`framework/templates/MODULE-TEMPLATE.md`]` | framework/governance/MODULE_LAYOUT.md:127 |
| 29 | Diagram standards specifies module tier template requirements | `framework/templates/MODULE-TEMPLATE.md` | framework/governance/DIAGRAM_STANDARDS.md:136 |
| 30 | Observability adapter contract defines c4-context boundaries | `system_container` | framework/governance/OBSERVABILITY_ADAPTER_CONTRACT.md:62 |

---

## Detailed Implementation Phases & Component Design

### Phase 1: Author `framework/templates/MODULE-GRAPH-TEMPLATE.yaml`

Author the canonical graph slice template for Tier 2 Modules adhering strictly to [`framework/governance/sdd-graph.schema.json`](../framework/governance/sdd-graph.schema.json#L15) and node ID pattern regexes:

```yaml
# ==============================================================================
# SDD Native Graph Template: Tier 2 Module Specification
# ==============================================================================
schema_version: "2.0-graph"
slice_id: "MODULE-NN_[module_slug]"

metadata:
  author: "[Engineer / AI Agent ID]"
  created_date: "YYYY-MM-DD"
  last_updated: "YYYY-MM-DD"
  status: "Draft"  # Draft | Active | Deprecated | Superseded
  framework_version: "0.96.4"
  description: "Subsystem architectural container specification and Triple-Lens model."
  c4_level: "c4-l2"
  seed_ref: "SEED-domain"

nodes:
  # Upstream Context Anchor
  - id: "SEED-domain"
    type: "seed_intent"
    title: "[Seed Domain Title]"
    statement: "[Strategic seed domain scope and boundaries]"

  # Subsystem Container (Core Subject)
  - id: "MODULE-NN"
    type: "system_container"
    title: "[Module / Subsystem Name]"
    statement: "Precise statement of subsystem role, boundaries, and responsibilities."
    description: |
      Comprehensive architectural narrative detailing container responsibilities,
      technology selections, communication protocols, and execution boundaries.
    properties:
      c4_level: "c4-l2"
      container_archetype: "api_service"  # api_service | worker | data_store | spa | gateway | library
      approved_stack:
        runtime: "Python 3.11+ / Node.js 20+ / Go 1.22+"
        framework: "FastAPI / Express / Gin"
        data_storage: "PostgreSQL / Redis"
        observability: "OpenTelemetry / Prometheus"
      runtime_platform: "container / serverless / k8s"
      candidate_stack_status: "Candidate baseline identified; formal binding ratified at downstream Layer 05 ADR"
      subsystem_invariants:
        - id: "INV-01"
          statement: "Subsystem invariant statement"
          enforcement: "Schema validation / DB constraint / middleware"
      trust_boundary: "Internal Subnet / DMZ / Public"
      data_classification: "CONFIDENTIAL / INTERNAL / PUBLIC"
      data_protection_matrix:
        - entity: "User Credentials"
          classification: "RESTRICTED"
          storage_location: "Encrypted DB"
          in_transit: "TLS 1.3"
          at_rest: "AES-256-GCM"
          retention_policy: "Account lifetime + 30 days"
      choreography:
        interactions:
          - target: "MODULE-MM"
            protocol: "gRPC / HTTPS / AMQP"
            synchronicity: "sync / async"
            payload: "RequestPayload"
            purpose: "Data retrieval / command dispatch"
        failure_branches:
          - condition: "Downstream service timeout"
            action: "Circuit breaker trips, fallback cache returned"

  # Downstream Component Contract Anchor
  - id: "SPEC.06.01.xxxx"
    type: "component_contract"
    title: "[Downstream Component Contract Title]"
    statement: "[Public interface and data contract specification]"

edges:
  # Seed Intent decomposes to Subsystem Container
  - from: "SEED-domain"
    to: "MODULE-NN"
    relation: "decomposes_to"
    notes: "Decomposes seed intent into subsystem container"
    description: "Connects business seed boundary to concrete technical subsystem container."
    rationale: "Fulfills SDD Tier 1 to Tier 2 decomposition invariant."

  # Subsystem Container decomposes to Component Contract
  - from: "MODULE-NN"
    to: "SPEC.06.01.xxxx"
    relation: "decomposes_to"
    notes: "Decomposes subsystem container into component contract"
    description: "Binds module container boundary to public wire-level component specification."
    rationale: "Fulfills SDD Tier 2 to Tier 3 decomposition invariant."
```

### Phase 2: Observability & Projection Adapter Enhancements

Update [`sdd_doc_lint/observability_adapter.py`](../sdd_doc_lint/observability_adapter.py#L256) and [`sdd_doc_lint/__main__.py`](../sdd_doc_lint/__main__.py#L136):

1. **Standalone Module Spec Projection (`render_module_spec`)**:
   - Add dedicated `render_module_spec(graph: SddGraph) -> str` to project `system_container` slices into full Markdown matching [`framework/templates/MODULE-TEMPLATE.md`](../framework/templates/MODULE-TEMPLATE.md#L6):
     - **Frontmatter Sequencing**: Emit the `---` fence at line 1, column 1 to ensure strict YAML frontmatter parsing compatibility across all consumers and test fixtures. The generator notice is embedded inside frontmatter comments (`# GENERATED BY SDD-RENDER`) or placed immediately below the closing `---` fence.
     - Document Control frontmatter (`module_id: "MODULE-NN"`, `c4_level: "c4-l2"`).
     - §1 Structural Definition (C4-L2 Container) with container archetype, stack, and platform.
     - §2 Data Movement & Boundary Analysis (DFD-L2) with Data Sensitivity and Protection Matrix table ([`framework/templates/MODULE-TEMPLATE.md`](../framework/templates/MODULE-TEMPLATE.md#L125)).
     - §3 Process Choreography & Failure Recovery Branches with interaction definitions and error actions.
     - §4 Subsystem Invariants & Downstream Traceability.
2. **CLI Integration (`sdd_doc_lint/__main__.py`)**:
   - Update `--render-spec`: automatically dispatch to `render_module_spec` when the target graph contains a `system_container` or `slice_id` starts with `MODULE-`.
   - Update `--diagram-type`: expand `choices=("lineage", "c4-container", "sequence", "dfd")` to allow CLI projection of choreography sequences and data flow diagrams.
3. **Mermaid Diagram Renderers**:
   - Enhance `render_mermaid(graph, diagram_type="c4-container")` to format `system_container` nodes with archetype styling.
   - Add `render_mermaid(graph, diagram_type="sequence")` to generate Mermaid sequence diagrams from `choreography` interactions and `failure_branches`.
   - Add `render_mermaid(graph, diagram_type="dfd")` to generate DFD-L2 subgraphs with trust boundaries and classified data flows.

### Phase 3: Kùzu Adapter Schema & Ingestion Harmonization

Update [`sdd_doc_lint/kuzu_adapter.py`](../sdd_doc_lint/kuzu_adapter.py#L40):

1. **Node Table Schema Extension & Parameterized Ingestion**:
   - Extend `NODE_TABLE_SCHEMAS["system_container"]` in `kuzu_adapter.py`:

     ```python
     "system_container": (
         "CREATE NODE TABLE IF NOT EXISTS system_container("
         "id STRING, title STRING, context STRING, "
         "container_archetype STRING, trust_boundary STRING, data_classification STRING, "
         "PRIMARY KEY (id))"
     ),
     ```

   - Update `ingest_graph()` in `kuzu_adapter.py` around line 202 to bind the new parameters during node creation:

     ```python
     elif ntype == "system_container":
         context = str(node.get("context", ""))
         props = node.get("properties", {})
         container_archetype = str(props.get("container_archetype", "api_service"))
         trust_boundary = str(props.get("trust_boundary", "Internal"))
         data_classification = str(props.get("data_classification", "INTERNAL"))
         self._conn.execute(
             "CREATE (n:system_container {"
             "id: $id, title: $title, context: $context, "
             "container_archetype: $container_archetype, "
             "trust_boundary: $trust_boundary, "
             "data_classification: $data_classification"
             "})",
             {
                 "id": nid,
                 "title": title,
                 "context": context,
                 "container_archetype": container_archetype,
                 "trust_boundary": trust_boundary,
                 "data_classification": data_classification,
             },
         )
     ```

2. **Rel Table Schema Harmonization**:
   - Update `REL_TABLE_SCHEMAS["decomposes_to"]`:
     - Add `FROM system_container TO component_contract`.
     - Add `FROM system_container TO product_capability`.
   - Update `REL_TABLE_SCHEMAS["constrains"]`:
     - Add `FROM system_container TO system_container`.
3. **Lake Exporter Validation**:
   - Verify that dynamic property serialization in `lake_exporter.py` (`export_cypher()` and `export_age_sql()`) correctly escapes and outputs all module container properties without requiring schema modifications.

### Phase 4: Governance Documentation & Playbook Alignment

Update governance documents to establish Dual-Plane CQRS across all normative surfaces:

1. **`framework/governance/MODULE_LAYOUT.md` ([`framework/governance/MODULE_LAYOUT.md`](../framework/governance/MODULE_LAYOUT.md#L82), [`framework/governance/MODULE_LAYOUT.md`](../framework/governance/MODULE_LAYOUT.md#L119))**:
   - Declare that module specifications are authored as `docs/modules/MODULE-NN_slug/MODULE-NN_slug.graph.yaml` (multi-file) or `docs/modules/MODULE-NN_slug.graph.yaml` (flat).
   - Update §7 (*Canonical Template & Triple-Lens Standard*, line 119) to cite `MODULE-GRAPH-TEMPLATE.yaml` (machine-authored source) and `MODULE-TEMPLATE.md` (projected Markdown visual standard).
   - Document automated projection to `.md` spec sheets via `sdd-render` / `observability_adapter`.
2. **`framework/governance/OBSERVABILITY_ADAPTER_CONTRACT.md` ([`framework/governance/OBSERVABILITY_ADAPTER_CONTRACT.md`](../framework/governance/OBSERVABILITY_ADAPTER_CONTRACT.md#L62))**:
   - Update §3 to specify `--type sequence` for choreography and document `render_module_spec` dispatching.
   - Document the YAML frontmatter line-1 ordering requirement for generated Module specifications.
3. **`framework/governance/DIAGRAM_STANDARDS.md` ([`framework/governance/DIAGRAM_STANDARDS.md`](../framework/governance/DIAGRAM_STANDARDS.md#L136))**:
   - Update line 136 to cite both `MODULE-GRAPH-TEMPLATE.yaml` (data source) and `MODULE-TEMPLATE.md` (visual projection standard).
4. **`framework/governance/workflows/seed-to-module-decomposition.sw.yaml` ([`framework/governance/workflows/seed-to-module-decomposition.sw.yaml`](../framework/governance/workflows/seed-to-module-decomposition.sw.yaml#L51))**:
   - Update Step 3 template reference to `framework/templates/MODULE-GRAPH-TEMPLATE.yaml` with projected visual delivery per `framework/templates/MODULE-TEMPLATE.md`.
5. **`framework/governance/SEED_CONTRACT.md` ([`framework/governance/SEED_CONTRACT.md`](../framework/governance/SEED_CONTRACT.md#L229))**:
   - Modernize Phase 0b wording: modules are authored in native SDD Graph format (`MODULE-GRAPH-TEMPLATE.yaml`) and projected to human-readable Markdown (`MODULE-TEMPLATE.md`).
6. **`framework/governance/SEED_TO_MODULE_DECOMPOSITION.md` ([`framework/governance/SEED_TO_MODULE_DECOMPOSITION.md`](../framework/governance/SEED_TO_MODULE_DECOMPOSITION.md#L38), [`framework/governance/SEED_TO_MODULE_DECOMPOSITION.md`](../framework/governance/SEED_TO_MODULE_DECOMPOSITION.md#L160))**:
   - Update living domain source of truth references to name `MODULE-GRAPH-TEMPLATE.yaml` (authoring) and `MODULE-TEMPLATE.md` (projection).
7. **`framework/governance/SDD_GRAPH_SCHEMA_SPECIFICATION.md` ([`framework/governance/SDD_GRAPH_SCHEMA_SPECIFICATION.md`](../framework/governance/SDD_GRAPH_SCHEMA_SPECIFICATION.md#L64))**:
   - Expand §3.2 to comprehensively document all properties of `system_container` (`container_archetype`, `approved_stack`, `subsystem_invariants`, `data_protection_matrix`, `choreography`).

### Phase 5: Tooling CLI, Invariants, and Conformance Testing

1. **Graph Engine CLI & Invariants (`sdd_doc_lint/graph_engine.py`)**:
   - Add `def main() -> int` and `if __name__ == "__main__":` entrypoint:
     - Accepts graph slice files as positional arguments.
     - Accepts `--template` flag to enable template validation mode (`is_template=True`).
     - Exits with code 0 on clean validation, 1 on errors.
   - Implement Cardinality Invariant `GRAPH-CARD-001` in `validate_btv`:
     - Every `seed_intent` in a unified graph must have $\ge 1$ outgoing `decomposes_to` edge pointing to a `system_container` or `product_capability`.
   - Add `extract_slice_subgraph(slice_id: str) -> SddGraph` to `SddGraph` to enable autonomous agents to isolate module slices from multi-slice graphs.
2. **Module Contract Conformance (`tests/conformance/test_module_contract.py`)** ([`tests/conformance/test_module_contract.py`](../tests/conformance/test_module_contract.py#L15)):
   - Add test asserting `MODULE-GRAPH-TEMPLATE.yaml` existence and YAML schema validity.
   - Assert presence of `system_container` node, Triple-Lens properties, and decomposition edges.
   - Assert `MODULE-TEMPLATE.md` remains intact as the visual rendering standard.
3. **SDD Graph Schema Conformance (`tests/conformance/test_sdd_graph_schema.py`)** ([`tests/conformance/test_sdd_graph_schema.py`](../tests/conformance/test_sdd_graph_schema.py#L22)):
   - Add `MODULE_TEMPLATE = FRAMEWORK / "templates" / "MODULE-GRAPH-TEMPLATE.yaml"`.
   - Validate `MODULE_TEMPLATE` against `sdd-graph.schema.json`.
4. **Observability Adapter Unit Tests (`tests/unit/test_observability_adapter.py`)**:
   - Test `render_module_spec()` projection produces Markdown adhering to `MODULE-TEMPLATE.md` with line 1 `---` frontmatter.
   - Test Mermaid sequence diagram generation from `choreography`.
   - Test Mermaid DFD generation from `trust_boundary` and `data_protection_matrix`.

---

## Verification Plan

### Automated Test Suites

Run the full verification suite across linters, conformance, and unit tests:

```bash
# 1. Conformance test for module contract and graph schema
pytest tests/conformance/test_module_contract.py tests/conformance/test_sdd_graph_schema.py -v

# 2. Graph engine CLI validation on the new template (template mode enabled)
python3 -m sdd_doc_lint.graph_engine --template framework/templates/MODULE-GRAPH-TEMPLATE.yaml

# 3. Unit tests for observability adapter and graph projections
pytest tests/unit/test_observability_adapter.py -v

# 4. Kuzu adapter schema initialization and parameterized ingestion test
pytest tests/unit/test_kuzu_adapter.py -v

# 5. Full conformance suite
pytest tests/conformance/ -v

# 6. Verified planning gate
python3 .agents/skills/verified-planning/check_plan.py plans/MODULE-GRAPH-MIGRATION-PLAN.md

# 7. Markdown linting and offline link checking
npx markdownlint-cli plans/MODULE-GRAPH-MIGRATION-PLAN.md
lychee --offline plans/MODULE-GRAPH-MIGRATION-PLAN.md
```

### Manual Validation

1. Verify that `render_module_spec()` produces Markdown matching the exact heading hierarchy and table structure of `MODULE-TEMPLATE.md`.
2. Verify that Kùzu graph query `MATCH (s:seed_intent)-[:decomposes_to]->(m:system_container)-[:decomposes_to]->(c:component_contract) RETURN s, m, c` executes cleanly without schema mismatch.

---

## Review log

### Pass 1 - 2026-10-18 - independent

- **Reviewer**: Independent Plan Reviewer (research subagent `161b4048-a650-4900-b3cc-e718fb6aa3be`)
- **Scope**: Semantic truth, completeness across framework governance, schema compliance, and regression risk.
- **Findings (5 Load-Bearing)**:
  1. *Schema Invalidation*: Draft `MODULE-GRAPH-TEMPLATE.yaml` violated `sdd-graph.schema.json` (`governance:` instead of `metadata:`, forbidden root keys, invalid status enums, `relationships:` instead of `edges:`).
  2. *Phantom Schema Relations*: Phase 3 proposed `produces`, `consumes`, and `data_entity`, none of which exist in the SDD ontology, crashing Kùzu DDL initialization.
  3. *Dangling Edge*: Phase 1 draft edge referenced undeclared `SEED-[domain]`, failing BTV with `GRAPH-DANGLE-001`.
  4. *Lake Exporter Assumptions*: Phase 3 assumed Arrow/Parquet/DuckDB export existed in `lake_exporter.py` (which actually exports openCypher/AGE SQL).
  5. *No-Op Verification Command*: `python3 -m sdd_doc_lint.graph_engine ...` had no CLI entrypoint, silently exiting 0.
  6. *Missed Governance Touchpoints*: `seed-to-module-decomposition.sw.yaml:51`, `SEED_CONTRACT.md:229`, `SEED_TO_MODULE_DECOMPOSITION.md:38, 160`, and `MODULE_LAYOUT.md`.
- **Resolution**:
  1. Rewrote `MODULE-GRAPH-TEMPLATE.yaml` in Phase 1 to 100% adhere to `sdd-graph.schema.json`.
  2. Stripped phantom relations; harmonized existing `decomposes_to` and `constrains` edges for `system_container`.
  3. Added stub `SEED-domain` and `SPEC.06.01.xxxx` nodes to the template slice to ensure BTV closed-graph integrity.
  4. Replaced Arrow/Parquet tasks with dynamic property verification in openCypher and AGE SQL exports.
  5. Added Phase 5 task to implement CLI entrypoint in `sdd_doc_lint/graph_engine.py`.
  6. Added all missing governance touchpoints with 4 verified citations (Claims 24–27).

### Pass 2 - 2026-10-18 - independent

- **Reviewer**: Independent Plan Reviewer (research subagent `0fca6ba0-6dc2-4ce8-ac15-cf5a4171f168`)
- **Scope**: Adversarial verification of revised plan, schema conformance against `sdd-graph.schema.json`, and live Kùzu DDL/Cypher execution.
- **Findings (1 Deterministic Schema Defect; 2 Clarifications)**:
  1. *Seed Node ID Pattern*: `SEED-[domain]` contained brackets `[` and `]` which violated `sdd-graph.schema.json` and `graph_engine.py` regex `|SEED-[a-zA-Z0-9_-]+`.
  2. *Frontmatter Line-1 Ordering*: `render_module_spec` must emit `---` at line 1, column 1 to avoid breaking frontmatter parsers that expect line 1 start.
  3. *Module Layout Citation*: Explicitly cite Section 7 of `MODULE_LAYOUT.md` (line 119) alongside line 82 for updating canonical template references.
- **Resolution**:
  1. Normalized `SEED-[domain]` to `SEED-domain` throughout Phase 1 YAML snippet. Tested against `sdd-graph.schema.json` via `jsonschema` and `test_sdd_graph_schema.py`: 100% clean schema validation with 0 errors.
  2. Clarified frontmatter ordering in Phase 2: `render_module_spec` emits `---` at line 1, column 1 with generator notice inside frontmatter comments or immediately after closing `---`.
  3. Added Section 7 citation (Claim 28, line 119) to Claim Ledger and Phase 4 touchpoints.

### Pass 3 - 2026-10-18 - independent

- **Reviewer**: Framework Architecture & Tooling Auditor
- **Scope**: Deep gap analysis across CLI argument parsing, parameterized ingestion in Kùzu, diagram standards governance, and cardinality invariants.
- **Findings (4 Architectural Gaps)**:
  1. *CLI Argument Parser Restriction*: `sdd_doc_lint/__main__.py:136` constrained `--diagram-type` to `("lineage", "c4-container")`, blocking CLI invocation of newly added sequence and DFD diagram generators.
  2. *Unparameterized Ingestion in Kùzu*: Phase 3 extended the `system_container` DDL table in `kuzu_adapter.py`, but missed updating `ingest_graph()` line 202 to bind the new parameters (`container_archetype`, `trust_boundary`, `data_classification`), leaving them NULL.
  3. *Missed Governance Surfaces*: `DIAGRAM_STANDARDS.md:136` and `OBSERVABILITY_ADAPTER_CONTRACT.md:62` also govern Module diagram contracts and observability subcommands.
  4. *Missing Invariant Enforcement*: `GRAPH-CARD-001` (seed decomposition cardinality) from `SDD_GRAPH_SCHEMA_SPECIFICATION.md:149` was defined in the spec but not yet implemented in `graph_engine.py:355`.
- **Resolution**:
  1. Updated Phase 2 to explicitly modify `sdd_doc_lint/__main__.py` expanding `--diagram-type` choices to include `"sequence"` and `"dfd"`, and auto-dispatching `--render-spec` to `render_module_spec`.
  2. Updated Phase 3 with complete parameterized binding implementation for `kuzu_adapter.py:ingest_graph()`.
  3. Added Claims 29 and 30 to Claim Ledger, incorporating `DIAGRAM_STANDARDS.md` and `OBSERVABILITY_ADAPTER_CONTRACT.md` into Phase 4 governance touchpoints.
  4. Added implementation of `GRAPH-CARD-001` and `extract_slice_subgraph` to Phase 5.
- **Result:** ready
