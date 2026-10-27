# Approved Technology Stack Integration & Selection Governance Plan

## Document Control

| Field | Value |
|---|---|
| Version | 1.1 |
| Status | Proposed |
| Last Updated | 2026-10-11 |
| Author | Framework Maintainer |
| Framework Version | 0.91.4 |
| Authority | [Decision GD-72](../framework/governance/DECISIONS.md#gd-72) (DEC-CHG-83), [Decision D-0013 / GD-13](../framework/governance/DECISIONS.md) & GATE-SPEC |

## Objective

Establish comprehensive, end-to-end integration and governance of our enterprise-approved platform technology stack (codified in `vladm3105/technology-stack` and [`RECOMMENDED_PLATFORM_STACK.md`](../framework/governance/RECOMMENDED_PLATFORM_STACK.md)) across the 10-layer Specification-Driven Development (SDD) lifecycle.

This plan addresses four core deliverables:

1. Author a dedicated governance guide defining how to apply the approved technology stack within the framework across all tiers, SDD layers, and traversal flows (`SDD2C`, `SEED2C`, `CODE2S`), including formal stack variance/exception procedures.
2. Update framework architectural diagrams, state machine flows, and transition graphs to depict progressive technology refinement from Tier 0 to Tier 3, establishing Layer 05 (ADR, immediately after BDD) as the authoritative technology selection gate.
3. Review and update primary SDD templates—specifically the primary CNCF Serverless Workflow (`*-SWF-TEMPLATE.yaml`) specifications, companion static templates (`*-TEMPLATE.yaml`), Seed, and Module templates—to integrate the approved platform stack as concrete recommended defaults and guidance while preserving engine-agnostic core specification purity (Decision D-0013 / GD-13) and pinned section counts (`test_required_section_sets.py`).
4. Update the normative workflow standards (`*_WORKFLOW_STANDARD.md`) across layers 01 through 08 and governance to explicitly incorporate technology stack evaluation, validation, and contract generation primitives.

## Scope

In scope:

1. **Phase 1 — Governance Guide (`framework/governance/TECHNOLOGY_STACK_USAGE_GUIDE.md`)**:
   - Establish the multi-tier progressive refinement model:
     - Tier 0: Enterprise Baseline (`vladm3105/technology-stack`).
     - Tier 1: Seed Documents (`<project>/seed/`) — Environmental realities, baseline platform constraints, invariants (C4-L1).
     - Tier 2: Module Specifications (`docs/modules/MODULE-NN_*`) — Structural container modeling (C4-L2), data movement and trust boundaries (DFD-L2), mapping bounded contexts to approved platform container archetypes.
     - Problem Space (Layers 01–04: BRD $\rightarrow$ PRD $\rightarrow$ EARS $\rightarrow$ BDD) — Technology-agnostic business goals, feature requirements, timing constraints, and executable behavioral scenarios; defining `adr_topics`.
     - Selection Gate (Layer 05: ADR) — The formal evaluation and binding of technology alternatives from the company stack against EARS constraints and BDD failure modes via Multi-Criteria Decision Analysis (MCDA).
     - Solution Space (Layers 06–10: SPEC $\rightarrow$ TDD $\rightarrow$ IPLAN $\rightarrow$ Code $\rightarrow$ EVAL) — Technology-bound contracts, testcontainer fixtures, durable state machines, and sandboxed execution.
   - Codify traversal flow mappings:
     - Greenfield (`SDD2C`): Strict Problem Space $\rightarrow$ ADR Selection Gate $\rightarrow$ Solution Space sequence.
     - Brownfield / Supersedes (`SEED2C`): Cascading technology upgrades via Seed vN+1 $\rightarrow$ Module sync $\rightarrow$ ADR re-evaluation.
     - Reverse Reconciliation (`CODE2S`): Auditing existing codebases against the approved stack and logging non-conformance as technical debt.
   - Establish formal **Stack Variance & Exception Procedures** (authoring an architectural variance ADR, requiring security/operator review, and sandboxing non-standard components).

2. **Phase 2 — Graphs & Flows Enhancement**:
   - Update Mermaid diagrams in `framework/governance/RECOMMENDED_PLATFORM_STACK.md` and `framework/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md` to illustrate the two-phase funnel: Problem Space (tech-agnostic) vs. Solution Space (tech-bound) split by the Layer 05 ADR selection gate.
   - Update `framework/governance/DECISION_WORKFLOW.md` to integrate technology selection into the Four-Tier Decision Model diagram.
   - Update `framework/governance/SEED_TO_MODULE_DECOMPOSITION.md` container decomposition diagrams to reflect approved platform container roles.
   - Update `framework/layers/05_ADR/README.md` to illustrate the technology trade-off decision sequence and upstream/downstream bindings.
   - Update the CNCF Serverless Workflow graph `framework/governance/workflows/adr-decision-analysis.sw.yaml` to model candidate evaluation against the approved platform stack.

3. **Phase 3 — SDD Template Modernization (Primary SWF & Companion Static Templates)**:
   - Archive pre-change snapshots of all modified templates in `framework/archive/CHG-86/`.
   - Modernize primary SWF templates and synchronize companion static templates while strictly preserving pinned section sets (`STRUCT01` / `EXPECTED` in `test_required_section_sets.py`):
     - `framework/layers/01_BRD/BRD-SWF-TEMPLATE.yaml` & `BRD-TEMPLATE.yaml`: Guidance on capability framing vs. recommended technology selection in Section 8 ADR topics.
     - `framework/layers/02_PRD/PRD-SWF-TEMPLATE.yaml` & `PRD-TEMPLATE.yaml`: Clarify `adr_topic_elaboration` referencing approved platform categories.
     - `framework/layers/03_EARS/EARS-SWF-TEMPLATE.yaml` & `EARS-TEMPLATE.yaml`: Express timing, latency, and throughput SLAs that feed into technology selection.
     - `framework/layers/04_BDD/BDD-SWF-TEMPLATE.yaml` & `BDD-TEMPLATE.yaml`: Specify transactional and network failure scenarios that test candidate viability.
     - `framework/layers/05_ADR/ADR-SWF-TEMPLATE.yaml` & `ADR-TEMPLATE.yaml`: Candidate evaluation state machine branches evaluating approved stack options (PostgreSQL 18 vs ClickHouse, Temporal vs LangGraph core, NATS vs REST).
     - `framework/layers/06_SPEC/SPEC-SWF-TEMPLATE.yaml` & `SPEC-TEMPLATE.yaml`: Reference concrete contracts (Bytebase DDL, Protobuf, CloudEvents v1.0, LiteLLM proxy).
     - `framework/layers/07_TDD/TDD-SWF-TEMPLATE.yaml` & `TDD-TEMPLATE.yaml`: Reference ephemeral testcontainers (PostgreSQL 18, NATS fixtures) in automated test execution workflows.
     - `framework/layers/08_IPLAN/IPLAN-SWF-TEMPLATE.yaml` & `IPLAN-TEMPLATE.yaml`: Map task graphs to Temporal workflow activities with SAGA compensation rollbacks.
     - `framework/templates/SEED-TEMPLATE.md` & `MODULE-TEMPLATE.md`: Update baselines and container archetypes.

4. **Phase 4 — Workflow Standards Modernization (`*_WORKFLOW_STANDARD.md`)**:
   - Modernize the normative standards across layers 01 through 08 (`BRD_WORKFLOW_STANDARD.md`, `PRD_WORKFLOW_STANDARD.md`, `EARS_WORKFLOW_STANDARD.md`, `BDD_WORKFLOW_STANDARD.md`, `ADR_WORKFLOW_STANDARD.md`, `SPEC_WORKFLOW_STANDARD.md`, `TDD_WORKFLOW_STANDARD.md`, `IPLAN_WORKFLOW_STANDARD.md`, and `GOVERNANCE_WORKFLOW_STANDARD.md`) to formally codify technology stack evaluation, verification, and contract generation primitives within their respective state machine specifications.
   - Update `framework/governance/REVIEW_CREWS.yaml` to ensure the Architect and Operator review personas actively check alignment with `vladm3105/technology-stack`.

Out of scope:

- Adding an 11th SDD layer (e.g. "TDR"): Layer 05 ADR already encompasses technology selection; creating an extra layer introduces an artificial dichotomy, causes pipeline bloat, and breaks the 10-layer model.
- Introducing proprietary runtime code, banned engine tokens (`\bmcp\b`, `hermes`, `plugin`), or commercial vendor lock-in into core engine-agnostic contracts (violating D-0013 / GD-13 and `test_spec_hygiene.py`).
- Modifying historical archived change requests prior to CHG-86.

## Approach

Execute under the framework governance change workflow (DIR2C / C2 Spec / GATE-SPEC):

1. **Worktree & Change Vehicle Setup**:
   - Create task worktree `feature/techstack-selection-governance` off `dev`.
   - Author authorizing Change Request `CHG-86.yaml` and Implementation Plan `IPLAN-86.yaml` (next available identifier after archived `CHG-85`).
   - Graduate specification decision to `framework/governance/DECISIONS.md` as Decision `GD-73`.
2. **Pre-Change Archival**:
   - Create snapshot archive `framework/archive/CHG-86/` holding pre-change copies of all modified templates before applying edits.
3. **Phase 1 Implementation (Governance Guide)**:
   - Draft `framework/governance/TECHNOLOGY_STACK_USAGE_GUIDE.md` detailing the progressive refinement model, flow mappings (`SDD2C`, `SEED2C`, `CODE2S`), and the stack variance/exception procedure.
4. **Phase 2 Implementation (Graphs & Flows)**:
   - Enhance Mermaid diagrams across `RECOMMENDED_PLATFORM_STACK.md`, `DECISION_WORKFLOW.md`, `SEED_TO_MODULE_DECOMPOSITION.md`, `SPEC_DRIVEN_DEVELOPMENT_GUIDE.md`, and `framework/layers/05_ADR/README.md`.
   - Update `adr-decision-analysis.sw.yaml` to orchestrate candidate evaluation from the approved stack catalog.
5. **Phase 3 Implementation (SWF & Companion Templates Modernization)**:
   - Update `BRD-SWF-TEMPLATE.yaml`, `PRD-SWF-TEMPLATE.yaml`, `EARS-SWF-TEMPLATE.yaml`, `BDD-SWF-TEMPLATE.yaml`, `ADR-SWF-TEMPLATE.yaml`, `SPEC-SWF-TEMPLATE.yaml`, `TDD-SWF-TEMPLATE.yaml`, `IPLAN-SWF-TEMPLATE.yaml`, `SEED-TEMPLATE.md`, and `MODULE-TEMPLATE.md`.
   - Synchronize companion `*-TEMPLATE.yaml` guidance while strictly preserving top-level section keys and `_size_target` declarations.
6. **Phase 4 Implementation (Workflow Standards Modernization)**:
   - Update `*_WORKFLOW_STANDARD.md` across layers 01 through 08 and governance.
   - Update `REVIEW_CREWS.yaml` reviewer checklist to assert technology stack alignment.
7. **Verification & Linting Battery**:
   - Execute `python3 -m sdd_doc_lint.swf_lint` across all updated SWF templates and workflows (`SWF-L001`–`SWF-L007`).
   - Run `python3 sdd_doc_lint/chg_lint.py framework/archive/CHG-86/CHG-86.yaml` to validate `CHG-86`.
   - Run `pytest tests/conformance/test_required_section_sets.py` to ensure derived section sets match pins exactly.
   - Run `pytest tests/conformance/test_spec_hygiene.py` to assert zero engine-token leakage (`mcp`, `plugin`, etc.).
   - Run `python3 .agents/skills/verified-planning/check_plan.py plans/TECHSTACK-SELECTION-GOVERNANCE-PLAN.md`.
8. **Multi-Agent Review & Promotion**:
   - Perform dual-pass review per OPS-0065.
   - Open PR to `dev`, verify CI checks, and merge via squash.

## Claim ledger

| # | Claim | Symbol | Citation |
|---|---|---|---|
| 1 | Decision workflow defines the Four-Tier Decision Model partitioning choices across Seed, Module, SDD ADR, and CHG Decision | Four-Tier Decision Model | framework/governance/DECISION_WORKFLOW.md:32 |
| 2 | Layer 5 SDD ADR records ONE selected architecture with Context-Decision-Consequences | Tier 3: SDD ADR | framework/governance/DECISION_WORKFLOW.md:85 |
| 3 | Core framework specifications are strictly engine-agnostic and vendor-neutral | Decision D-0013 / GD-13 | framework/governance/RECOMMENDED_PLATFORM_STACK.md:20 |
| 4 | Platform technology stack defines the authoritative multi-tenant infrastructure matrix | Master Platform Technology Matrix | framework/governance/RECOMMENDED_PLATFORM_STACK.md:58 |
| 5 | SDD layer to platform runtime mapping details the concrete tooling role for each layer | SDD LAYER TO PLATFORM RUNTIME MAPPING | framework/governance/RECOMMENDED_PLATFORM_STACK.md:91 |
| 6 | Seed-to-module decomposition establishes the Triple-Lens modeling standard for containers | The Triple-Lens Modeling Standard | framework/governance/SEED_TO_MODULE_DECOMPOSITION.md:47 |
| 7 | Step 1 of seed-to-module decomposition establishes bounded contexts | Step 1: Domain Boundary Discovery | framework/governance/SEED_TO_MODULE_DECOMPOSITION.md:97 |
| 8 | SDD guide enumerates layer descriptions and artifact purposes from BRD to EVAL | Layer Descriptions | framework/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md:24 |
| 9 | ADR documents adopt Hybrid Envelope Architecture housing CNCF Serverless Workflow state machines | Hybrid Envelope Architecture | framework/layers/05_ADR/ADR_WORKFLOW_STANDARD.md:31 |
| 10 | ADR SWF template evaluates candidate options concurrently across quality attributes | EvaluateCandidatesConcurrently | framework/layers/05_ADR/ADR-SWF-TEMPLATE.yaml:232 |
| 11 | ADR SWF template computes quantitative multi-criteria decision analysis utility scoring | CalculateMCDAMatrix | framework/layers/05_ADR/ADR-SWF-TEMPLATE.yaml:255 |
| 12 | SPEC SWF template establishes technical specification document ID | doc_id: SPEC-NN | framework/layers/06_SPEC/SPEC-SWF-TEMPLATE.yaml:9 |
| 13 | SPEC SWF template specifies CNCF Serverless Workflow 0.8 standard | workflow_standard: "CNCF-Serverless-Workflow-0.8" | framework/layers/06_SPEC/SPEC-SWF-TEMPLATE.yaml:23 |
| 14 | TDD SWF template establishes test-driven development document ID | doc_id: TDD-NN | framework/layers/07_TDD/TDD-SWF-TEMPLATE.yaml:9 |
| 15 | BRD workflow standard establishes primitive mapping to CNCF Serverless Workflow | Primitive Mapping: BRD to CNCF Serverless Workflow | framework/layers/01_BRD/BRD_WORKFLOW_STANDARD.md:33 |
| 16 | PRD workflow standard establishes primitive mapping to CNCF Serverless Workflow | Primitive Mapping: PRD to CNCF Serverless Workflow | framework/layers/02_PRD/PRD_WORKFLOW_STANDARD.md:33 |
| 17 | BDD workflow standard maps Given-When-Then scenarios to CNCF workflow state primitives | The BDD Given-When-Then paradigm maps directly onto CNCF Serverless Workflow state primitives: | framework/layers/04_BDD/BDD_WORKFLOW_STANDARD.md:58 |
| 18 | SPEC workflow standard maps distributed interaction constructs to CNCF state primitives | The core constructs of distributed component specifications map directly onto CNCF Serverless Workflow state primitives: | framework/layers/06_SPEC/SPEC_WORKFLOW_STANDARD.md:71 |
| 19 | TDD workflow standard maps Arrange-Act-Assert testing patterns to CNCF state primitives | The standard Arrange-Act-Assert testing pattern maps directly onto CNCF Serverless Workflow state primitives: | framework/layers/07_TDD/TDD_WORKFLOW_STANDARD.md:65 |
| 20 | IPLAN workflow standard maps task graph DAGs to CNCF Serverless Workflow primitives | CNCF Serverless Workflow Primitives in IPLAN | framework/governance/IPLAN_WORKFLOW_STANDARD.md:126 |
| 21 | Conformance test suite pins exact required section counts for each SDD layer | EXPECTED = { | tests/conformance/test_required_section_sets.py:50 |
| 22 | Spec hygiene conformance test strictly bans engine-specific tokens in core framework | ENGINE_TOKENS = [ | tests/conformance/test_spec_hygiene.py:18 |
| 23 | GATE-SPEC governs framework specification and template modifications | # GATE-SPEC: Framework Specification Gate (meta) | framework/layers/09_CHG/gates/GATE-SPEC_FRAMEWORK.md:16 |
| 24 | Historical change archive records CHG-85 as already allocated | #  CHG-85: Pre-Production Review Findings Remediation Batch | framework/archive/CHG-85/CHG-85.yaml:2 |

## Review log

### Pass 1 - 2026-10-11 - independent

- *Review findings*: Analyzed the plan against SDD framework governance, D-0013/GD-13 vendor-neutrality rules, and the user requirements:
  1. The user proposed a potential 11th SDD layer ("Technology Decision Records" / TDR). The plan correctly refutes adding a redundant layer, preserving the 10-layer model while formally assigning technology selection to Layer 05 (ADR) immediately after BDD.
  2. The plan specifically accounts for the user's note that the framework has migrated to SWF templates as primary templates, enumerating all `*-SWF-TEMPLATE.yaml` files across layers 01 through 08.
  3. Identified 7 critical operational gaps in the initial draft:
     - Change ID collision: CHG-84 and CHG-85 already exist in `framework/archive/`; the authorizing vehicle must be `CHG-86` / `IPLAN-86`, graduating as Decision `GD-73` under `GATE-SPEC`.
     - Dual-template drift: Pinned section sets in `test_required_section_sets.py` require keeping companion `*-TEMPLATE.yaml` files in sync with SWF templates.
     - Spec token hygiene: `test_spec_hygiene.py` bans tokens like `\bmcp\b` and `plugin` in `framework/`, requiring vendor-neutral phrasing for stack primitives.
     - Snapshot archiving: Pre-change template snapshots must be placed in `framework/archive/CHG-86/`.
     - Stack variance workflow: Needs formal variance procedures for off-stack technologies.
     - Flow mappings: Needs explicit rules for `SDD2C`, `SEED2C`, and `CODE2S`.
     - Review crew integration: `REVIEW_CREWS.yaml` must incorporate technology stack checks.
- *Resolution*: Updated the plan to resolve all 7 gaps, retargeted to `CHG-86` / `GD-73`, added snapshot archiving and dual-template synchronization rules, codified the variance process, and expanded the claim ledger from 20 to 24 citations.

### Pass 2 - 2026-10-11 - independent

- *Review findings*: Re-validated the modernized plan against all 24 citations in the claim ledger. Verified that `check_plan.py` resolves every symbol and line number against the repository. Confirmed that all 7 identified gaps are thoroughly remediated with zero regressions.
- *Resolution*: Findings: none. Result: ready.
