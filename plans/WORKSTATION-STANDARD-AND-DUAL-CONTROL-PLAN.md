# Implementation Plan: `.aidoc/` Workstation Standard & Dual-Control Architecture Rollout

## Document Control

| Field | Value |
|---|---|
| Version | 1.1 |
| Status | Approved |
| Last Updated | 2026-10-15 |
| Author | Framework Maintainer |
| Framework Version | 0.91.23 |
| Authority | [Decision D-0013 / GD-13](../framework/governance/DECISIONS.md), [`MULTI_PROJECT_FEDERATED_STANDARD.md`](../framework/governance/MULTI_PROJECT_FEDERATED_STANDARD.md), [`CHG_REQUEST_FLOWS.md`](../framework/governance/CHG_REQUEST_FLOWS.md), [`WORKTREE_FLOW.md`](../framework/governance/WORKTREE_FLOW.md) |

---

## 1. Objective

Operationalize and roll out the **`.aidoc/` Workstation Directory Standard** and **Dual-Control Architecture** across the Quad-Pillar federated ecosystem.

This plan addresses eight core architecture improvements and five adversarial audit findings:

1. **Pillar 2 Representation:** Incorporate `.aidoc/stack-policy.yaml` into the standardized workstation topology.
2. **Unified CLI Orchestration:** Transition from standalone `.aidoc/bin/*` shell scripts to a canonical `.aidoc/Taskfile.yml` included in consumer root `Taskfile.yml` files (`task sdd:lint`, `task sdd:review`, `task sdd:slice`, `task sdd:check`).
3. **In-Repo Installer & Template Parity:** Update `framework/scripts/install.sh`, `framework/scripts/upgrade.sh`, and `framework/templates/AGENTS-TEMPLATE.md` to scaffold `.aidoc/Taskfile.yml` while providing a backward-compatible `.aidoc/bin/sdd-lint` shim during migration.
4. **Canonical Hash Normalization Algorithm:** Formally define the byte-level normalization contract (`LF` line endings, whitespace trimming, UTF-8 encoding) for `reviewed_sha256` to prevent cross-platform CI failures between Linux, macOS, and Windows.
5. **Brownfield Grandfathering & Mutation Scoping:** Scope `GATE-FLOOR-01` cryptographic verification to new or modified documents in active PRs, preventing false-positive CI breaks on unmutated legacy documents.
6. **Deterministic Discovery Semantics:** Codify **Atomic File Shadowing** under Rule `ENGINE-DISCOV-01` (`.aidoc/project/` completely replaces `.aidoc/framework/` at the file level without partial key merging).
7. **Headless & Air-Gapped CI Modes:** Codify three engine operating modes (`live`, `verify-only`, `mock`), enabling zero-token, zero-latency PR gating in CI pipelines.
8. **Composite Fast Gate Integration:** Define `task sdd:check` (combining structural linting and `verify-only` review verification) and wire it into `EXTRA_FAST_CHECKS` in `aidoc-local-flow-ci`.
9. **Context Slicing Fallback Hierarchy:** Provide seamless fallback in `.aidoc/Taskfile.yml` from `aidoc-context-tools` to the built-in `python3 -m sdd_doc_lint --slice`.
10. **Workstation Git Tracking Discipline:** Codify the explicit Git tracking policy table for all `.aidoc/` workstation components, strictly banning brittle local symlinks in version control.
11. **Inception & Reconciliation Tooling Integration:** Connect the workstation standard to `aidoc-project-onboarding` (`onboard greenfield` and `onboard update`).
12. **Ecosystem Version Pin Synchronization:** Synchronize framework version pins across onboarding and consumer templates to `0.91.23`.

---

## 2. Scope

### In Scope

1. **`vladm3105/aidoc-flow-framework` (Pillar 1 Process Canon)**:
   - Update [`docs/AIDOC_WORKSTATION_STANDARD.md`](../docs/AIDOC_WORKSTATION_STANDARD.md) with all approved architectural enhancements.
   - Update `framework/scripts/install.sh` and `framework/scripts/upgrade.sh` to scaffold `.aidoc/Taskfile.yml` alongside the backward-compatible `.aidoc/bin/sdd-lint` shim.
   - Update `framework/templates/AGENTS-TEMPLATE.md` to instruct `task sdd:lint` and `task sdd:check`.
   - Update `tests/conformance/test_consumer_scripts.py` to assert `.aidoc/Taskfile.yml` scaffolding and execution.
   - Synchronize cross-references in [`docs/REPO_STRUCTURE.md`](../docs/REPO_STRUCTURE.md) and [`docs/PROJECT.md`](../docs/PROJECT.md).
   - Author authorizing Change Request `framework/archive/CHG-106/CHG-106.yaml` and Implementation Plan `framework/archive/CHG-106/IPLAN-106.yaml` (Class C1, Type DIR2C).

2. **`vladm3105/aidoc-project-onboarding` (Ecosystem Inception Tooling)**:
   - Update `canons.yaml` to bump the framework version pin to `0.91.23`.
   - Update `templates/aidoc/` to scaffold the modernized `.aidoc/` layout:
     - Scaffold `.aidoc/stack-policy.yaml` from `STACK-POLICY-TEMPLATE.yaml`.
     - Scaffold `.aidoc/Taskfile.yml` with `sdd:lint`, `sdd:review`, `sdd:slice`, and `sdd:check`.
   - Update root `Taskfile.yml` template to include `.aidoc/Taskfile.yml` and wire `sdd:check` into `task check`.

3. **`vladm3105/aidoc-flow-langgraph` (Tier 1 Execution Engine)**:
   - Replace legacy `.aidoc/framework` filesystem symlink with canonical directory structure and `.aidoc/Taskfile.yml`.
   - Implement `verify-only` mode in engine CLI:
     - Assert `review_log` contains `verdict: PASS | REMEDIATED` and `blocking_remaining == 0`.
     - Calculate normalized $\text{SHA-256}(\text{document\_body\_excluding\_frontmatter})$.
     - Fail closed (`STALE_REVIEW_DETECTED`, exit code 1) if hash does not match `reviewed_sha256`.
   - Implement `reviewed_sha256` emission during `live` review crew execution passes.

### Out of Scope

- Modifying core SDD normative layers (`framework/layers/01_BRD` .. `10_EVAL`).
- Introducing runtime dependencies into `aidoc-flow-framework` (strictly forbidden by Decision D-0013 / GD-13).
- Altering the wire format schemas in `aidoc-data-contracts` (Pillar 3).

---

## 3. Implementation Phases & Deliverables

### Phase 1: Process Canon & Workstation Standard Refinements (`aidoc-framework`)

- **Phase 1.1: Standard Specification Enhancement**:
  - Update [`docs/AIDOC_WORKSTATION_STANDARD.md`](../docs/AIDOC_WORKSTATION_STANDARD.md):
    - **Section 1**: Reference `aidoc-project-onboarding` as the authoritative inception and reconciliation engine.
    - **Section 3**: Add `.aidoc/stack-policy.yaml` (Pillar 2); define `.aidoc/Taskfile.yml` as canonical orchestrator.
    - **Section 4**: Codify **Atomic File Shadowing** under `ENGINE-DISCOV-01`.
    - **Section 5**: Update the Quality Gate Floor formula to include cryptographic verification:
      $$\text{Gate Floor} = (\text{sdd\_lint\_pass} == \text{true}) \land (\text{blocking\_findings} == 0) \land (\text{review\_sha256\_valid} == \text{true})$$
      Codify the 4-step canonical hash normalization algorithm and the brownfield mutation scoping rule.
    - **Section 6**: Codify the three engine execution modes (`live`, `verify-only`, `mock`).
    - **Section 7**: Add `reviewed_sha256` to the `review_log` YAML frontmatter schema.
    - **Section 8**: Codify the Git Tracking Policy Table and Taskfile inclusion pattern (`task sdd:*`).
- **Phase 1.2: In-Repo Script & Template Synchronization**:
  - Update `framework/scripts/install.sh` to generate `.aidoc/Taskfile.yml` and provide a backward-compatible `.aidoc/bin/sdd-lint` wrapper.
  - Update `framework/scripts/upgrade.sh` to reconcile `.aidoc/Taskfile.yml`.
  - Update `framework/templates/AGENTS-TEMPLATE.md` to document `task sdd:lint` and `task sdd:check`.
  - Update `tests/conformance/test_consumer_scripts.py` with test assertions for `.aidoc/Taskfile.yml` and runner compatibility.
- **Phase 1.3: Governance Vehicle Authoring**:
  - Author authorizing Change Request `framework/archive/CHG-106/CHG-106.yaml` (Class C1, Type DIR2C).
  - Author Implementation Plan `framework/archive/CHG-106/IPLAN-106.yaml`.
  - Validate with `python3 sdd_doc_lint/chg_lint.py framework/archive/CHG-106/CHG-106.yaml`.
- **Phase 1.4: Isolation, Verification & Merge**:
  - Execute in a dedicated per-task worktree (`../aidoc-framework-chg-106`) on branch `feature/chg-106-workstation-standard-refinements`.
  - Run full test suite, linter suite, and pre-push verification.
  - Open PR to `dev`, watch status checks, squash-merge into `dev`, and clean up worktree/branch.

### Phase 2: Inception & Scaffolding Tooling (`aidoc-project-onboarding`)

- **Phase 2.1: Version Pin Bump**:
  - Update `canons.yaml` to point `aidoc-flow-framework` to `0.91.23`.
- **Phase 2.2: Scaffolding Template Modernization**:
  - Update `templates/aidoc/` to scaffold:
    - `.aidoc/stack-policy.yaml` (Pillar 2)
    - `.aidoc/Taskfile.yml` (Canonical SDD tasks)
    - `.aidoc/project/` (Project overrides)
    - `.aidoc/engine/engine.yaml` (Engine configuration)
- **Phase 2.3: Root Taskfile Integration**:
  - Update consumer `Taskfile.yml` template to include `includes: sdd: .aidoc/Taskfile.yml` and wire `task sdd:check` into `task check`.
- **Phase 2.4: Verification**:
  - Run `task test` in `aidoc-project-onboarding` to confirm greenfield scaffolding output matches the standard.

### Phase 3: Runtime Execution Engine & Cryptographic QA (`aidoc-flow-langgraph`)

- **Phase 3.1: Topology Realignment**:
  - Remove legacy filesystem symlink (`.aidoc/framework -> ...`) and adopt `.aidoc/Taskfile.yml`.
- **Phase 3.2: Cryptographic Content Hashing**:
  - Implement normalized SHA-256 body hashing during `sdd-review` execution.
  - Emit `reviewed_sha256` in the generated `review_log` frontmatter block.
- **Phase 3.3: Headless `verify-only` Mode**:
  - Implement `aidoc-flow-langgraph review --verify-only` (or via `task sdd:review -- --verify-only`).
  - Read frontmatter, extract `reviewed_sha256`, compute normalized SHA-256 of document body, and assert zero blocking findings.
  - Return exit code 0 on valid match, exit code 1 on mismatch/stale review.
- **Phase 3.4: Verification**:
  - Run unit and integration tests asserting that modified specs fail validation in `verify-only` mode until re-reviewed.

### Phase 4: Reference Adoption & Dogfooding (`b-local-privy` & Ecosystem)

- **Phase 4.1: Consumer Upgrade**:
  - Execute `onboard update` in consumer testbed (`b-local-privy`).
- **Phase 4.2: Fast Gate Verification**:
  - Run `task check` to verify `sdd:check` executes seamlessly as part of `EXTRA_FAST_CHECKS`.
- **Phase 4.3: Review Crew End-to-End Validation**:
  - Run `task sdd:review` in `verify-only` mode on CI and `live` mode during drafting.

---

## Claim ledger

| # | Claim | Symbol | Citation |
|---|---|---|---|
| 1 | Authority anchors include Decision D-0013 / GD-13 | `[Decision D-0013 / GD-13](../framework/governance/DECISIONS.md)` | docs/AIDOC_WORKSTATION_STANDARD.md:12 |
| 2 | Decision D-0013 establishes zero runtime platform code in the Process Canon | `Governed by **Decision D-0013**` | docs/AIDOC_WORKSTATION_STANDARD.md:54 |
| 3 | Workstation layout definition anchors at consumer project root | `Every consumer project adopts the standardized` | docs/AIDOC_WORKSTATION_STANDARD.md:64 |
| 4 | Standard references canonical SDD task definitions under `.aidoc/Taskfile.yml` | `Taskfile.yml              # ⭐ CANONICAL SDD TASK DEFINITIONS` | docs/AIDOC_WORKSTATION_STANDARD.md:70 |
| 5 | Execution engines must implement the Two-Tier Discovery Protocol | `all conforming execution engines must implement the **Two-Tier Discovery Protocol**:` | docs/AIDOC_WORKSTATION_STANDARD.md:111 |
| 6 | Discovery resource resolver function checks project path before canon default | `def resolve_resource(project_root: Path, relative_path: str) -> Path:` | docs/AIDOC_WORKSTATION_STANDARD.md:125 |
| 7 | Quality Gate Floor formula mandates lint pass, zero blockers, and valid hash | `$$\text{Gate Floor} = (\text{sdd\_lint\_pass} == \text{true}) \land (\text{blocking\_findings} == 0) \land (\text{review\_sha256\_valid} == \text{true})$$` | docs/AIDOC_WORKSTATION_STANDARD.md:156 |
| 8 | Approved artifacts require machine-readable `review_log` frontmatter | `review_log:` | docs/AIDOC_WORKSTATION_STANDARD.md:294 |
| 9 | Current distribution table specifies Process Canon distribution path | `Submodule OR Dynamic Clone` | docs/AIDOC_WORKSTATION_STANDARD.md:330 |
| 10 | Pillar 1 is the Process Canon (`aidoc-flow-framework`) | `Pillar1["1. PROCESS CANON<br/><b>vladm3105/aidoc-flow-framework</b>` | framework/governance/MULTI_PROJECT_FEDERATED_STANDARD.md:49 |
| 11 | Pillar 2 is Platform & Infrastructure (`technology-stack`) | `Pillar2["2. PLATFORM & INFRASTRUCTURE<br/><b>vladm3105/technology-stack</b>` | framework/governance/MULTI_PROJECT_FEDERATED_STANDARD.md:51 |
| 12 | Pillar 3 is Data Contracts Canon (`aidoc-data-contracts`) | `Pillar3["3. DATA CONTRACTS CANON<br/><b>vladm3105/aidoc-data-contracts</b>` | framework/governance/MULTI_PROJECT_FEDERATED_STANDARD.md:53 |
| 13 | Pillar 4 is Agent Runtime & Tooling (`aidoc-context-tools`) | `Pillar4["4. AGENT RUNTIME & TOOLING<br/><b>vladm3105/aidoc-context-tools</b>` | framework/governance/MULTI_PROJECT_FEDERATED_STANDARD.md:55 |
| 14 | Stack policy contract template exists in framework templates | `Stack Policy Contract Template (stack-policy.yaml)` | framework/templates/STACK-POLICY-TEMPLATE.yaml:2 |
| 15 | Stack policy template sets placeholder tenant ID | `tenant_id: "example-org"` | framework/templates/STACK-POLICY-TEMPLATE.yaml:9 |
| 16 | Framework version is currently 0.91.23 | `0.91.23` | framework/VERSION:1 |
| 17 | Structural linter repository root surfaces check | `Validate repository root governance surfaces` | sdd_doc_lint/surface_lint.py:1 |
| 18 | Feature work must execute in an isolated worktree | `Feature work never executes in the main` | framework/governance/WORKTREE_FLOW.md:19 |
| 19 | Change management terminology and normative selector router | `**"CHG flows"** is the framework's standard umbrella terminology` | framework/governance/CHG_REQUEST_FLOWS.md:25 |
| 20 | Change Request CHG-105 is archived with ID | `chg_id: "CHG-105"` | framework/archive/CHG-105/CHG-105.yaml:31 |
| 21 | Install script scaffolds linter runner at `.aidoc/bin/sdd-lint` | `# Scaffold linter runner at .aidoc/bin/sdd-lint` | framework/scripts/install.sh:271 |
| 22 | AGENTS template instructs agents to run linter via `.aidoc/bin/sdd-lint` | `Submit only verified work` | framework/templates/AGENTS-TEMPLATE.md:38 |
| 23 | Conformance tests assert presence of `.aidoc/bin/sdd-lint` | `runner = self.project / ".aidoc" / "bin" / "sdd-lint"` | tests/conformance/test_consumer_scripts.py:409 |
| 24 | Content hash generator is tool-computed rather than prompt-computed | `prints the content hash for a` | sdd_doc_lint/rehash.py:11 |

---

## Review log

### Pass 1 - 2026-10-15 - independent

- *Review findings*: Analyzed the initial implementation roadmap against the Quad-Pillar federated architecture standard (`MULTI_PROJECT_FEDERATED_STANDARD.md`) and the freshly ratified `.aidoc/` Workstation Standard (`docs/AIDOC_WORKSTATION_STANDARD.md`):
  1. Identified that `.aidoc/stack-policy.yaml` (Pillar 2) was completely missing from the directory topology in Section 3 of `AIDOC_WORKSTATION_STANDARD.md`, creating a discrepancy with `MULTI_PROJECT_FEDERATED_STANDARD.md` §2.
  2. Identified that retaining `.aidoc/bin/*` shell scripts while projects use `Taskfile.yml` creates a Dual-CLI conflict and violates `b-local-privy`'s contract ("Taskfile.yml — the single orchestrator").
  3. Identified that without cryptographic content hashing (`reviewed_sha256`), approved documents can be mutated post-review without failing CI gates.
  4. Confirmed that all 20 citations in the claim ledger map to verified source lines in the active repository tree.
- *Resolution*: Codified the comprehensive 4-phase rollout plan. Replaced `.aidoc/bin/*` with `.aidoc/Taskfile.yml`, added `reviewed_sha256` to the Quality Gate Floor formula, and integrated `aidoc-project-onboarding` and `aidoc-flow-langgraph`.

### Pass 2 - 2026-10-15 - independent

- *Review findings*: Conducted adversarial second-opinion review focusing on cross-repository dependencies and headless CI constraints:
  1. **Air-Gapped CI Constraint:** If `sdd:review` only supports live LLM execution, automated CI runners without API keys will fail. Added Section 6 codifying the `verify-only` mode (zero LLM tokens, validates hash and verdict only).
  2. **Inheritance Ambiguity:** Discovery protocol (`ENGINE-DISCOV-01`) needed clarification regarding partial key merging vs atomic replacement. Explicitly codified **Atomic File Shadowing** in Section 4.
  3. **Symlink Portability:** Clarified the Git Tracking Policy Table in Section 8 to ban brittle local filesystem symlinks across repositories.
  4. **Governance Alignment:** Verified that Phase 1 falls under Class C1 DIR2C change control (`CHG_REQUEST_FLOWS.md`), requiring a dedicated worktree and authorizing CHG/IPLAN records.
- *Resolution*: Folded all 4 findings into the plan phases and deliverables. Confirmed that deterministic linter checks and `check_plan.py` validate cleanly.

### Pass 3 - 2026-10-15 - independent

- *Review findings*: Conducted cross-platform, brownfield migration, and in-repo consistency review:
  1. **In-Repo Scripts Drift:** Noted that `framework/scripts/install.sh`, `framework/scripts/upgrade.sh`, and `framework/templates/AGENTS-TEMPLATE.md` still scaffold and document `.aidoc/bin/sdd-lint`. Added Phase 1.2 to synchronize installer scripts to scaffold `.aidoc/Taskfile.yml` while providing a backward-compatible shim in `bin/` during migration. Added Claims 21–23.
  2. **Hash Normalization Spec:** Noted that CRLF/LF line endings and trailing whitespace would cause hash mismatches on Windows or git `core.autocrlf`. Mandated a 4-step canonical normalization contract (`LF`, `strip()`, UTF-8). Added Claim 24.
  3. **Brownfield Grandfathering:** Noted that requiring `reviewed_sha256` unconditionally across all `docs/sdd/` would break existing unmutated documents in brownfield repos. Scoped `GATE-FLOOR-01` to new or modified documents in active PRs.
  4. **CI Fast Gate Wiring:** Noted that running `task sdd:lint` alone in `task check` skips review hash verification. Defined composite `task sdd:check` (lint + verify-only review) and wired it into `EXTRA_FAST_CHECKS`.
  5. **Context Slicing Fallback:** Added a resilient fallback in `.aidoc/Taskfile.yml` to `python3 -m sdd_doc_lint --slice` when `aidoc-context-tools` is not installed.
- *Resolution*: Folded all 5 findings into the plan. Re-ran `check_plan.py` across all 24 citations. **Result:** ready.
