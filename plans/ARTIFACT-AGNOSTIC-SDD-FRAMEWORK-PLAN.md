# Artifact-Agnostic SDD Framework Plan (Layers 01–10 & Companion Harness Contracts)

## 1. Objective & Architectural Context

The SDD framework (`aidoc-framework`) and its runtime execution governance (`aiops-harness`) are designed around a 10-layer contract hierarchy (`01_BRD` through `10_EVAL`). While `06_SPEC`, `07_TDD`, and `08_IPLAN` already provide CNCF Serverless Workflow v0.8 (`*-SWF-TEMPLATE.yaml`) and JSON-LD graph (`*-GRAPH-TEMPLATE.yaml`) companions for state-machine and multi-agent choreography, several normative templates, linter rules, graph ontology enums, and companion JSON Schemas remain hardcoded to software source code (`deliverable_type: code`, `code_build`, `target_files: minItems: 1`).

This plan makes `aidoc-framework` (and the companion IPLAN schema/taxonomy in `aiops-harness`) **100% artifact-agnostic** so any deliverable—multi-agent orchestration DAGs, generated media/image assets, API/data contracts, operational workflows, documentation corpora, or source code—flows cleanly through all 10 layers (`BRD` $\to$ `PRD` $\to$ `EARS` $\to$ `BDD` $\to$ `ADR` $\to$ `SPEC` $\to$ `TDD` $\to$ `IPLAN` $\to$ `CHG` $\to$ `EVAL`) and `iplan-chain` DAGs without bypassing `sdd_doc_lint` or conformance gates.

### Guardrails & Conformance Invariants Preserved

1. **Fixed Top-Level Section Counts (`test_required_section_sets.py`):**
   - `SPEC` is pinned to `EXPECTED["SPEC"] = 8` (`DECLARED["SPEC"] = 8`: `behavior`, `component_overview`, `data_models`, `document_control`, `implementation_notes`, `interfaces`, `tdd_contracts`, `traceability`). No top-level sections will be added, removed, or renamed.
   - `TDD` is pinned to `EXPECTED["TDD"] = 7` (`DECLARED["TDD"] = 7`: `document_control`, `tdd_order`, `test_cases`, `test_mapping`, `test_strategy`, `thresholds`, `traceability`).
   - `IPLAN` is pinned to `EXPECTED["IPLAN"] = 3` unconditionally required sections (`document_control`, `tdd_consistency`, `traceability`) and `DECLARED["IPLAN"] = 6` (`metadata.total_sections: 6`), with subtype-gated sections filtered by `_required_when_subtype:`.
2. **`code_inventory` Lifecycle & Guarded Phrases (`test_iplan_code_inventory_lifecycle.py`):**
   - `traceability.code_inventory` and its 3-state vocabulary (`planned | created | modified`) remain structurally unchanged. All guarded phrases in `IPLAN-TEMPLATE.yaml` and `08_IPLAN/README.md` (`one entry per`, `file_manifest`, `session: null`, `manifest order`, ``empty `code_inventory` is not the draft state``, `file_manifest + execution_commands not required`, `` `planned` MUST NOT survive a session ``, ``seeded `planned` ``, ``one entry per `file_manifest` path``) are preserved verbatim.
   - `platforms/` remains absent (`test_platform_skills_are_gone`).
3. **Governance & Engine-Token Hygiene Guards (`test_governance.py` & `test_spec_hygiene.py`):**
   - `Missing Tools` and `technology_stack` in `ADR-TEMPLATE.yaml` and `SPEC-TEMPLATE.yaml` (`lines 252–255`), `Missing Tools` in `TDD-TEMPLATE.yaml` (`line 459`), and `Missing Tools` + `INVARIANTS` in `IPLAN-TEMPLATE.yaml` are preserved untouched.
   - Banned engine-specific tokens enforced by `tests/conformance/test_spec_hygiene.py` across `framework/` (including `\bmcp\b` and `\bplugin\b`) must NEVER be introduced into any file under `framework/`. Use engine-agnostic terms (`tool_protocol`, `agent_protocol`, `tool contracts`) instead.
4. **Version Bump & Mechanical Sweep (`test_sync_version_refs.py`):**
   - When `framework/VERSION` is bumped from `0.96.23` to `0.96.24`, `0.96.23` is appended to `OLD_VERSIONS` in `hooks/sync-version-refs.sh` and `bash hooks/sync-version-refs.sh` is executed to propagate version pins atomically.

---

## 2. Implementation Phases

### Phase 1: IPLAN Subtype Matrix Alignment (`08_IPLAN` & `sdd_doc_lint`)

**Problem:** `sdd_doc_lint/__init__.py` defines `_VALID_IPLAN_SUBTYPES = frozenset({"code_build", "deploy", "combined", "workflow", "audit_fix", "bugfix", "docs"})`, where `workflow` is already accepted by the linter. However, `framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml` omits `workflow` from its inline enum comment (`# code_build | deploy | combined | audit_fix | bugfix | docs`), its `document_control._guidance` table, and all `_required_when_subtype:` section gates. Consequently, when `_load_section_targets` (`sdd_doc_lint/__init__.py:511-571`) evaluates `subtype="workflow"`, zero subtype-gated sections are required.

**Changes:**

1. **`framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml`:**
   - Update `document_control._guidance` (`lines 82–122`) to document `workflow` in the `SUB-TYPE SELECTION` table (for multi-agent orchestration DAGs, state-machine choreography, and non-code artifact generation pipelines) while keeping the `deploy` row's `"file_manifest + execution_commands NOT required"` phrasing intact for `test_iplan_code_inventory_lifecycle.py`.
   - Update `document_control.subtype` inline comment (`line 137`) to `# code_build | deploy | combined | workflow | audit_fix | bugfix | docs`.
   - Add `workflow` to `_required_when_subtype:` on the 3 subtype-gated sections present in `IPLAN-SWF-TEMPLATE.yaml` (`subtype: workflow`):
     - `file_manifest` (`line 195`) — manifests output artifacts, workflow definitions, generated media, or agent prompts produced by the workflow.
     - `implementation_contracts` (`line 456`) — invariants, step/state contracts, and failure handling.
     - `session_handoff` (`line 479`) — session progress tracking.
   - Keep `document_control` (`line 81`), `tdd_consistency` (`line 313`), and `traceability` (`line 525`) unconditionally required (no `_required_when_subtype:`), preserving `EXPECTED["IPLAN"] = 3` in `test_required_section_sets.py`.
   - Keep `execution_commands` (`line 352`, `[code_build, combined, bugfix]`) excluded from `workflow` so `IPLAN-SWF-TEMPLATE.yaml` (which uses the top-level `workflow` state-machine block instead of `execution_commands`, verified by `tests/conformance/test_iplan_workflow.py`) remains valid under `STRUCT01`.
   - Leave rollback/deploy sections unchanged (`rollback_procedure` at `line 596` with `[deploy, combined, bugfix]`; `smoke_tests` at `line 616`, `canary_metrics` at `line 633`, `observability_hooks` at `line 649`, and `runbook_reference` at `line 665` with `[deploy, combined]`).
2. **`sdd_doc_lint/tests/test_iplan_subtype_lint.py` & `tests/acceptance/deterministic/test_harness_template_sections.py`:**
   - Add unit test `test_workflow_subtype_requires_workflow_manifest_and_contracts` in `sdd_doc_lint/tests/test_iplan_subtype_lint.py` verifying that `subtype: workflow` requires `document_control`, `tdd_consistency`, `traceability`, `file_manifest`, `implementation_contracts`, and `session_handoff`, and does not require `execution_commands` or deploy-only sections (`rollback_procedure`, `smoke_tests`, `canary_metrics`, `observability_hooks`, `runbook_reference`).
   - Add `test_iplan_workflow_includes_manifest_and_contracts_sections` in `tests/acceptance/deterministic/test_harness_template_sections.py`.

---

### Phase 2: `deliverable_type` Metadata Taxonomy & Cascade Unification (`01_BRD`–`10_EVAL`)

**Problem:** `sdd_doc_lint/__init__.py` (`_check_cascade`, rule `CSC01`) enforces that every downstream document whose frontmatter includes `deliverable_type` matches its upstream BRD's `deliverable_type`. Currently:

- `01_BRD` through `05_ADR` templates list only `code | document | ux | risk | process` in `metadata.deliverable_type`.
- `06_SPEC` (`SPEC-TEMPLATE.yaml`, `SPEC-SWF-TEMPLATE.yaml`) and `07_TDD` (`TDD-TEMPLATE.yaml`, `TDD-SWF-TEMPLATE.yaml`) hardcode `deliverable_type: code` without inheritance guidance.
- `08_IPLAN` (`IPLAN-TEMPLATE.yaml`, `IPLAN-SWF-TEMPLATE.yaml`) and `10_EVAL` (`EVAL-TEMPLATE.yaml`) omit `deliverable_type` in `metadata:`.

**Changes:**

1. **Expand Canonical `deliverable_type` Enum Comment Across `01_BRD`–`05_ADR`:**
   - In `framework/layers/01_BRD/BRD-TEMPLATE.yaml` (`lines 50–52`), `02_PRD/PRD-TEMPLATE.yaml` (`lines 102–107`), `03_EARS/EARS-TEMPLATE.yaml` (`lines 109–113`), `04_BDD/BDD-TEMPLATE.yaml` (`lines 96–100`), and `05_ADR/ADR-TEMPLATE.yaml` (`lines 107–111`), expand the documented taxonomy comment to:
     `code | document | contract | infrastructure | workflow | media | ux | risk | process`
   - Document the 4 added artifact categories in `BRD-TEMPLATE.yaml` (`lines 50–52`):
     - `contract` — API schemas, Protobuf/OpenAPI specs, data models, wire protocols
     - `infrastructure` — OpenTofu/Terraform modules, Kubernetes manifests, network/ops topology
     - `workflow` — Multi-agent orchestration DAGs, CNCF Serverless Workflows, state machines
     - `media` — Generated images, SVG diagrams, visual/audio assets, creative pipelines
2. **Add Inheritance Guidance to `06_SPEC`, `07_TDD`, `08_IPLAN`, and `10_EVAL`:**
   - Update `metadata.deliverable_type` inline comment in `06_SPEC/SPEC-TEMPLATE.yaml` (`line 28`), `06_SPEC/SPEC-SWF-TEMPLATE.yaml` (`line 49`), `07_TDD/TDD-TEMPLATE.yaml` (`line 28`), and `07_TDD/TDD-SWF-TEMPLATE.yaml` (`line 49`) to `# code | document | contract | infrastructure | workflow | media | ux | risk | process (MUST match upstream BRD deliverable_type for CSC01)`.
   - Add `deliverable_type: code  # code | document | contract | infrastructure | workflow | media | ux | risk | process (inherited from upstream BRD)` under `metadata:` in `08_IPLAN/IPLAN-TEMPLATE.yaml` (`after line 42`), `08_IPLAN/IPLAN-SWF-TEMPLATE.yaml` (`after line 52`), and `10_EVAL/EVAL-TEMPLATE.yaml` (`after line 37`).

---

### Phase 3: Artifact-Agnostic `06_SPEC` Contracts & `07_TDD` Verification Oracles

**Problem:** While `06_SPEC` and `07_TDD` have 8 and 7 top-level sections respectively that are conceptually universal (Contracts + Oracles), the field guidance inside `SPEC-TEMPLATE.yaml` (`component_overview.language`, `component_overview.toolchain`, `interfaces.exports`, `data_models.models`) and `TDD-TEMPLATE.yaml` / `TDD-GRAPH-TEMPLATE.yaml` (`test_strategy`, `test_cases`, `test_fixture`) only illustrates Python/TypeScript/Go/Rust code and pytest/unittest runners.

**Changes:**

1. **`framework/layers/06_SPEC/SPEC-TEMPLATE.yaml` & `README.md`:**
   - Keep all 8 top-level keys (`document_control`, `component_overview`, `interfaces`, `data_models`, `behavior`, `tdd_contracts`, `implementation_notes`, `traceability`) and the `Missing Tools` + `technology_stack` strings in `implementation_notes._guidance` (`lines 252–255`) intact.
   - Expand `component_overview.language` (`line 113`) comment to cover non-code deliverables:
     `# Primary specification language/notation (e.g., python | typescript | rust | go | cncf-swf-0.8 | json-schema | openapi-3.1 | opentofu | image-pipeline | markdown)`
   - Expand `component_overview.toolchain` `_guidance` (`lines 115–123`) to clarify that for non-code deliverables, `toolchain` pins the artifact validator, workflow engine, renderer, or schema linter (e.g., `aidoc-validate`, `check-jsonschema`, `tofu validate`, `magick identify`, `langgraph`).
   - Expand `interfaces._guidance` (`lines 130–137`) and `data_models._guidance` (`lines 166–170`) to explain how non-coding deliverables map to these sections (using engine-agnostic terminology compliant with `test_spec_hygiene.py`):
     - *Agent DAG / Workflow:* `interfaces.exports` = agent entrypoints, tool contracts, handoff events; `data_models.models` = shared state payload, checkpoint schema.
     - *Image / Media Generation:* `interfaces.exports` = prompt/render pipeline contract, asset resolution/format invariants; `data_models.models` = asset manifest metadata, style/seed parameters.
     - *Data / API Contract or Docs:* `interfaces.exports` = published schema endpoints or document section contracts; `data_models.models` = entity schemas or frontmatter structures.
2. **`framework/layers/07_TDD/TDD-TEMPLATE.yaml` & `TDD-GRAPH-TEMPLATE.yaml`:**
   - Keep all 7 top-level keys and the `Missing Tools` string (`line 459` in `TDD-TEMPLATE.yaml`) intact.
   - Update `test_strategy._guidance` (`lines 99–113` in `TDD-TEMPLATE.yaml`) to explicitly define the 3 verification tiers across all artifact types:
     - `unit` — Isolated artifact/component verification (function unit test, JSON Schema / YAML lint, image dimension/format/channel check, single agent prompt/tool-schema validation).
     - `integration` — Cross-component or pipeline handoff verification (service contract test, `iplan-chain` output-to-input artifact handoff check, multi-agent state transition test).
     - `e2e` — Full deliverable scenario or rubric evaluation (end-to-end user journey, full DAG dry-run trace, LLM-as-a-judge / visual rubric evaluation against `thresholds`).
   - Update `test_cases._guidance` (`lines 298–308` in `TDD-TEMPLATE.yaml`) and `test_fixture` node comments in `TDD-GRAPH-TEMPLATE.yaml` (`lines 26–73`) so test case and fixture guidance explicitly include deterministic CLI probes, schema validators, and rubric evaluators alongside code test runners.

---

### Phase 4: Native SDD Graph Ontology (`sdd-graph.schema.json`) & `LAYER_REGISTRY.yaml` Deliverable Sink Semantics

**Problem:**

1. `framework/governance/SDD_GRAPH_SCHEMA_SPECIFICATION.md` (§3.2, §3.8, §3.10) documents narrow code/service-centric examples (`system_container` `properties.container_archetype`: `api_service | worker | data_store | spa | gateway | library`; `component_contract` `properties.protocol`: `grpc | http | cloudevents`; `task_action` `action`: `apply_patch | create_file | run_script`), even though `framework/governance/sdd-graph.schema.json` accepts strings for those properties.
2. `framework/registry/LAYER_REGISTRY.yaml` (`lines 165–168` and `281–287`) describes `CODE` (`c4_mapping.code`) solely as source code class/package structure, creating ambiguity when an IPLAN produces workflow DAGs, images, schemas, or infrastructure manifests.

**Changes:**

1. **`framework/governance/SDD_GRAPH_SCHEMA_SPECIFICATION.md` & `framework/governance/sdd-graph.schema.json`:**
   - In `SDD_GRAPH_SCHEMA_SPECIFICATION.md` (preserving all existing values and avoiding banned engine tokens like `mcp`):
     - §3.2 (`line 73`, `system_container` `properties.container_archetype`): Expand values to `api_service | worker | data_store | spa | gateway | library | agent_orchestrator | media_pipeline | contract_registry | doc_corpus | infra_module`.
     - §3.8 (`line 103`, `component_contract` `properties.protocol`): Expand values to `grpc | http | cloudevents | tool_protocol | a2a | workflow_dag | file_artifact | cli_probe`.
     - §3.10 (`line 113`, `task_action` top-level `action`): Expand values to `apply_patch | create_file | run_script | call_tool | invoke_agent | render_asset | verify_probe`.
   - In `framework/governance/sdd-graph.schema.json` (`lines 86` and `94`):
     - Add descriptive `"description"` annotations on `nodes.items.properties.action` (`line 86`) and `nodes.items.properties.properties` (`line 94`) referencing the expanded artifact-agnostic vocabulary in `SDD_GRAPH_SCHEMA_SPECIFICATION.md` while keeping `"type": "string"` / `"type": "object"` so existing graphs remain 100% backward-compatible (`tests/conformance/test_sdd_graph_schema.py`).
2. **`framework/registry/LAYER_REGISTRY.yaml` & `framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml`:**
   - In `framework/registry/LAYER_REGISTRY.yaml` (`lines 165–168` and `281–287`), clarify in `c4_mapping.code.description` and `c4_mapping.code.note` that `CODE` (`artifact: CODE`) acts as the **universal deliverable sink** for any artifact produced by an IPLAN (source code, agent workflow DAGs, generated media/images, API contracts, IaC manifests, or documentation).
   - In `framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml` (`lines 532–550`), append a clarifying note to `traceability.code_inventory._guidance`—without altering any guarded sentence or regex pattern tested by `test_iplan_code_inventory_lifecycle.py`—stating that `code_inventory` tracks all manifested deliverable paths in `file_manifest` regardless of deliverable type (code, workflow definitions, media assets, contracts, or docs).

---

### Phase 5: Version Bump & Mechanical Reference Synchronization (`aidoc-framework`)

**Problem:** Modifying normative templates and governance documents in `aidoc-framework` requires a patch version bump and mechanical synchronization so `tests/conformance/test_sync_version_refs.py` passes.

**Changes:**

1. **`framework/VERSION` & `hooks/sync-version-refs.sh`:**
   - Append `0.96.23` to `OLD_VERSIONS` in `hooks/sync-version-refs.sh` (`line 128`).
   - Update `framework/VERSION` (`line 1`) from `0.96.23` to `0.96.24`.
   - Run `bash hooks/sync-version-refs.sh` to propagate `0.96.24` across all swept-form pins in `framework/`, `docs/`, `README.md`, and `.aidoc/profile.yaml`.

---

### Phase 6: Companion `aiops-harness` Schema & Deliverable Taxonomy Alignment

**Problem:** In `/home/ya/devd/aiops-harness`, `docs/IPLAN_RUNNER_PIPELINE.md` (`lines 302–313`) explicitly documents operational/command-centric steps with `target_files: []`, and `docs/ARTIFACT_CENTRIC_DELIVERY.md` (`lines 35–46`) defines non-code deliverable families. However:

1. `schemas/iplan-document.schema.json` enforces `"minItems": 1` on `steps[].target_files` (`line 215`) and top-level `files` (`line 442`), rejecting pure orchestration/deployment/probe steps that have `target_files: []`.
2. `aiops_harness/core/deliverables.py` (`lines 12–31`) defines `DeliverableType` (`SOFTWARE_CODE`, `TECHNICAL_DOCS`, `DATA_CONTRACT`, `IAC_INFRASTRUCTURE`, `COMPLIANCE_DOSSIER`, `DEVOPS_RELEASE`, `EDGE_DEVICE_SIGNAL`, `VERIFICATION_PROBE`) and `StepExecutionPrimitive` (`ARTIFACT_MUTATION`, `EDGE_DEVICE_SIGNALING`, `DEVOPS_RELEASE`, `VERIFICATION_PROBE`) using `UPPER_SNAKE_CASE` values, missing explicit variants for multi-agent workflow DAGs and generated media/image assets.

**Changes:**

1. **`/home/ya/devd/aiops-harness/schemas/iplan-document.schema.json`:**
   - Relax `steps.items.properties.target_files.minItems` (`line 215`) from `1` to `0` so command/agent-invocation/validation steps with `target_files: []` validate cleanly per `docs/IPLAN_RUNNER_PIPELINE.md`.
   - Relax top-level `properties.files.minItems` (`line 442`) from `1` to `0` so `deploy` or operational IPLANs without static file mutations validate cleanly.
2. **`/home/ya/devd/aiops-harness/aiops_harness/core/deliverables.py`:**
   - Extend `DeliverableType` (`lines 12–22`) with `UPPER_SNAKE_CASE` members `WORKFLOW_DAG = "WORKFLOW_DAG"` and `MEDIA_ASSET = "MEDIA_ASSET"` (`DATA_CONTRACT = "DATA_CONTRACT"` already exists at `line 17`).
   - Extend `StepExecutionPrimitive` (`lines 25–31`) with `UPPER_SNAKE_CASE` members `AGENT_DISPATCH = "AGENT_DISPATCH"` and `ASSET_GENERATION = "ASSET_GENERATION"`.
   - Update unit tests in `/home/ya/devd/aiops-harness/tests/unit/test_pure_domain_core.py` verifying the new `DeliverableType` / `StepExecutionPrimitive` enum members and verifying `iplan-document.schema.json` accepts `target_files: []`.

---

## 3. Verification Plan

1. **Deterministic Plan Gate:**
   - Run `python3 /home/ya/.gemini/config/plugins/aiops-harness/skills/verified-planning/check_plan.py --root /home/ya/devd/aiops-harness /home/ya/devd/aidoc-framework/plans/ARTIFACT-AGNOSTIC-SDD-FRAMEWORK-PLAN.md`
2. **`aidoc-framework` Test Suites:**
   - `pytest sdd_doc_lint/tests/test_iplan_subtype_lint.py`
   - `pytest tests/conformance/test_required_section_sets.py tests/conformance/test_iplan_code_inventory_lifecycle.py tests/conformance/test_iplan_workflow.py tests/conformance/test_governance.py tests/conformance/test_spec_hygiene.py tests/conformance/test_sdd_graph_schema.py tests/conformance/test_sync_version_refs.py`
   - `pytest tests/acceptance/deterministic/test_harness_template_sections.py`
   - `task check` and `task ci` in `/home/ya/devd/aidoc-framework`
3. **`aiops-harness` Test Suites:**
   - `pytest tests/unit/test_pure_domain_core.py`
   - `task check` and `task ci` in `/home/ya/devd/aiops-harness`

---

## Claim ledger

| # | Claim | Symbol | Citation |
| --- | --- | --- | --- |
| 1 | `_VALID_IPLAN_SUBTYPES` in `sdd_doc_lint` already includes `"workflow"` alongside `"code_build"`, `"deploy"`, `"combined"`, `"audit_fix"`, `"bugfix"`, and `"docs"`. | `_VALID_IPLAN_SUBTYPES` | `sdd_doc_lint/__init__.py:506-508` |
| 2 | `_load_section_targets` filters required template sections using `_required_when_subtype:` lists loaded from `{artifact}-TEMPLATE.yaml`. | `_load_section_targets` | `sdd_doc_lint/__init__.py:511-571` |
| 3 | `IPLAN-TEMPLATE.yaml` currently omits `workflow` from `document_control.subtype` inline comment. | `subtype` | `framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml:137` |
| 4 | `IPLAN-TEMPLATE.yaml` currently omits `workflow` from `_required_when_subtype:` gates on `file_manifest` (`line 195`), `implementation_contracts` (`line 456`), and `session_handoff` (`line 479`), while `traceability` (`line 525`) is unconditionally required. | `_required_when_subtype` | `framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml:195` |
| 5 | `_check_cascade` (`CSC01`) enforces that every downstream document's `deliverable_type` matches its parent BRD's `deliverable_type`. | `_check_cascade` | `sdd_doc_lint/__init__.py:1610-1615` |
| 6 | `BRD-TEMPLATE.yaml`, `PRD-TEMPLATE.yaml`, `EARS-TEMPLATE.yaml`, `BDD-TEMPLATE.yaml`, and `ADR-TEMPLATE.yaml` currently document `deliverable_type` values as `code`, `document`, `ux`, `risk`, and `process`. | `deliverable_type` | `framework/layers/01_BRD/BRD-TEMPLATE.yaml:50-52` |
| 7 | `SPEC-TEMPLATE.yaml`, `SPEC-SWF-TEMPLATE.yaml`, `TDD-TEMPLATE.yaml`, and `TDD-SWF-TEMPLATE.yaml` hardcode `deliverable_type: code` in `metadata`. | `deliverable_type` | `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml:28` |
| 8 | `test_required_section_sets.py` pins `EXPECTED["SPEC"] = 8`, `EXPECTED["TDD"] = 7`, `EXPECTED["IPLAN"] = 3`, and `DECLARED` section counts with exact top-level section key sets. | `EXPECTED` | `tests/conformance/test_required_section_sets.py:50-61` |
| 9 | `test_governance.py` asserts `"Missing Tools"` and `"technology_stack"` in `ADR-TEMPLATE.yaml` and `SPEC-TEMPLATE.yaml`, `"Missing Tools"` in `TDD-TEMPLATE.yaml`, and `"Missing Tools"` + `"INVARIANTS"` in `IPLAN-TEMPLATE.yaml`. | `Missing Tools` | `tests/conformance/test_governance.py:446-464` |
| 10 | `test_iplan_code_inventory_lifecycle.py` enforces the 3-value `planned`, `created`, and `modified` lifecycle on `code_inventory`, guards specific prose substrings in `IPLAN-TEMPLATE.yaml` and `08_IPLAN/README.md`, and asserts `platforms/` does not exist. | `LIFECYCLE` | `tests/conformance/test_iplan_code_inventory_lifecycle.py:72-73` |
| 11 | `SDD_GRAPH_SCHEMA_SPECIFICATION.md` defines `system_container` `properties.container_archetype` (§3.2), `component_contract` `properties.protocol` (§3.8), and `task_action` `action` (§3.10) backed by `sdd-graph.schema.json` (`lines 86, 94`). | `container_archetype` | `framework/governance/SDD_GRAPH_SCHEMA_SPECIFICATION.md:71-73` |
| 12 | `LAYER_REGISTRY.yaml` defines `CODE` (`artifact: CODE`) as a downstream terminal sink referenced by Layer 8 (`IPLAN`). | `CODE` | `framework/registry/LAYER_REGISTRY.yaml:281-286` |
| 13 | `framework/VERSION` is currently `0.96.23` and `hooks/sync-version-refs.sh` sweeps `OLD_VERSIONS` across `framework/`, `docs/`, `README.md`, and `.aidoc/profile.yaml`, guarded by `test_sync_version_refs.py`. | `OLD_VERSIONS` | `hooks/sync-version-refs.sh:128` |
| 14 | In `aiops-harness`, `schemas/iplan-document.schema.json` enforces `"minItems": 1` on `steps[].target_files` and top-level `files`, whereas `docs/IPLAN_RUNNER_PIPELINE.md` specifies `target_files: []` for operational steps. | `target_files` | `schemas/iplan-document.schema.json:210-217` |
| 15 | In `aiops-harness`, `DeliverableType` and `StepExecutionPrimitive` in `aiops_harness/core/deliverables.py` define `UPPER_SNAKE_CASE` deliverable and step execution enums. | `DeliverableType` | `aiops_harness/core/deliverables.py:12-31` |

---

## Review log

### Pass 1 - 2026-11-07 - self

- **Findings:**
  - Verified that `platforms/` was retired in `CLEANUP-001` and `tests/conformance/test_iplan_code_inventory_lifecycle.py:302-306` explicitly asserts `not (REPO_ROOT / "platforms").exists()`. Removed any reference to syncing `platforms/claude-code-plugin` from Phase 5.
  - Verified exact string assertions in `tests/conformance/test_governance.py:446-464` (`Missing Tools`, `technology_stack`, `INVARIANTS`) and `tests/conformance/test_iplan_code_inventory_lifecycle.py:250-273` (`file_manifest + execution_commands not required`, ``empty `code_inventory` is not the draft state``, etc.) and added explicit preservation guardrails in §1 and Phases 1, 3, and 4.
  - Checked all 15 claim citations against live line numbers in `/home/ya/devd/aidoc-framework` and `/home/ya/devd/aiops-harness`.
- **Disposition:** All self-review findings resolved in plan text.
- **Result:** needs-pass

### Pass 2 - 2026-11-07 - independent (`verified-planning-reviewer`)

- **Findings:**
  1. **[BLOCKING]** Phase 1 and Claim 4 referenced non-existent sections (`execution_contract`, `implementation_steps`), proposed adding `_required_when_subtype` to unconditional `traceability` (which would break `EXPECTED["IPLAN"] = 3` in `test_required_section_sets.py`), and proposed adding `workflow` to `execution_commands` (which is absent from `IPLAN-SWF-TEMPLATE.yaml`, breaking `STRUCT01`). Fixed Phase 1 and Claim 4 to keep `traceability` (`line 525`) unconditional, keep `execution_commands` (`line 352`) out of `workflow`, and add `workflow` only to `file_manifest` (`line 195`), `implementation_contracts` (`line 456`), and `session_handoff` (`line 479`), matching `IPLAN-SWF-TEMPLATE.yaml`. Corrected line numbers for deploy sections (`596`, `616`, `633`, `649`, `665`).
  2. **[BLOCKING]** Phase 3 and Phase 4 used the token `mcp` / `MCP` inside `framework/` files, which violates `tests/conformance/test_spec_hygiene.py:19-38` (`\bmcp\b` ban). Replaced with `tool_protocol` / `tool contracts` and added `test_spec_hygiene.py` to §1 Guardrails and §3 Verification Plan. Fixed line citations for `Missing Tools` in `SPEC-TEMPLATE.yaml` (`lines 252–255`) and `TDD-TEMPLATE.yaml` (`line 459`).
  3. **[BLOCKING]** Phase 4 and Claim 11 misstated current enum values in `SDD_GRAPH_SCHEMA_SPECIFICATION.md` (§3.2 `api_service | worker | data_store | spa | gateway | library`, §3.8 `grpc | http | cloudevents`, §3.10 `apply_patch | create_file | run_script`) and cited non-existent lines in `sdd-graph.schema.json` (actual: `lines 86` and `94` on flat node schema). Fixed both.
  4. **[BLOCKING]** Phase 4 prose stated `LAYER_REGISTRY.yaml` mentioned `code_inventory`; corrected to `c4_mapping.code` (`lines 281–287`) and `IPLAN` `downstream: [CODE, EVAL]` (`lines 165–168`).
  5. **[BLOCKING]** Phase 6 misstated existing enum members of `aiops_harness/core/deliverables.py` (`lines 12–31`) and proposed lowercase enum values instead of `UPPER_SNAKE_CASE`. Fixed Phase 6 to cite the actual members, preserve existing `DATA_CONTRACT = "DATA_CONTRACT"`, and add `WORKFLOW_DAG = "WORKFLOW_DAG"`, `MEDIA_ASSET = "MEDIA_ASSET"`, `AGENT_DISPATCH = "AGENT_DISPATCH"`, and `ASSET_GENERATION = "ASSET_GENERATION"`.
  6. **[NON-BLOCKING]** Corrected `BRD-TEMPLATE.yaml` `deliverable_type` citation to `lines 50–52` and `TDD-GRAPH-TEMPLATE.yaml` `test_fixture` node citation to `lines 26–73`.
- **Disposition:** All 5 blocking and 3 non-blocking findings folded subtractively into Phases 1–6 and Claim Ledger without adding new rows.
- **Result:** needs-pass

### Pass 3 - 2026-11-07 - independent (`verified-planning-reviewer`)

- **Findings:** None (`0 blocking`, `0 non-blocking`). All 5 blocking and 3 non-blocking findings from Pass 2 verified resolved against live source files and conformance tests (`test_required_section_sets.py`, `test_iplan_workflow.py`, `test_spec_hygiene.py`, `test_governance.py`, `test_sdd_graph_schema.py`, and `aiops-harness` `test_pure_domain_core.py`).
- **Result:** ready — no further findings.
