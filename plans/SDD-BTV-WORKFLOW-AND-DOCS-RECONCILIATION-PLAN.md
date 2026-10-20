# Implementation Plan: Framework-Wide BTV Workflow Modernization & Stale Docs Reconciliation

## Document Control

| Field | Value |
|---|---|
| Plan Name | `sdd_btv_workflow_and_docs_reconciliation_plan` |
| Framework Version | 0.96.9 |
| Proposed Version Bump | 0.96.10 (C2 / Spec Governance) |
| Author | AI Pair Programming Assistant |
| Date | 2026-10-19 / 2026-10-20 |
| Target Scope | `framework/layers/`, `framework/governance/`, `docs/`, `tests/` |

---

## 1. Goal Description

Following the foundational adoption of Binary Topological Validation (**BTV**, SDD-0044) and the successful pilot implementations in Layer 08 IPLAN (CHG-121) and GATE-06 (CHG-122), a comprehensive repository-wide audit revealed that the remaining 9 SDD layers and 10 standalone governance workflows still enforce legacy numeric heuristic scoring conditions (`.review_score >= 90`). Furthermore, several declarative layer templates retain percentage placeholders (`[X]%`), 5 SDD-GRAPH templates retain scalar `"90/100"` readiness targets, action arguments in governance workflows pass scalar scores, and legacy platform distribution claims linger in `docs/REPO_STRUCTURE.md`.

This plan systematically eliminates all remaining numeric heuristic readiness gates across the framework, aligns all CNCF Serverless Workflow state machines with zero-blocking-findings binary gates (`.blocking_findings == 0 and .gate_passed == true`), standardizes declarative and graph readiness indicators to `[PASS | FAIL]` / `"PASS"`, locks down 3-way CHG mirror parity in conformance tests, and corrects outdated platform distribution text in project documentation.

---

## 2. User Review Required

> [!IMPORTANT]
> **Normative BTV Principle (SDD-0044)**:
> In the SDD BTV model, layer advancement is strictly binary: an artifact either passes all structural schema invariants and zero-blocking review findings (`BTV PASS`), or it is blocked. Scalar readiness scores (e.g. `90/100`) are purely advisory and cannot serve as deterministic state machine transitions.
>
> **Domain Software Metrics Preserved**:
> This modernization strictly purges **document review readiness scores**. It explicitly **preserves** domain-specific software test metrics (such as unit test `coverage_target: ">=90%"` in TDD) and product SLA performance thresholds (such as transaction success `threshold: ">=90%"` in PRD), which are normative engineering requirements.

---

## 3. Open Questions

1. **Governance Workflow Mirroring**: Should `framework/layers/09_CHG/CHG-SWF-TEMPLATE.yaml` and its mirrors in `framework/governance/chg/` and `framework/governance/templates/` be synchronized simultaneously?
   *(Recommendation: Yes. Exact 3-way byte parity across CHG mirrors is enforced by conformance tests).*
2. **EARS Quality Gate Transitions**: In `03_EARS`, should `readinessScore >= 90` / `70` be modernized to deterministic syntax, ambiguity, and conflict checks?
   *(Recommendation: Yes. Modernize to `.conflictCount == 0 and .syntax_valid == true and .hasAmbiguity == false` for approved transition, preventing short-circuit bugs where ambiguous drafts bypass clarification).*

---

## 4. Proposed Changes

### Component 1: Layer Workflow Templates & Standards Reconciliation

Update the review gate transition condition from `${ .review_score >= 90 and .blocking_findings == 0 and .gate_passed == true }` to `${ .blocking_findings == 0 and .gate_passed == true }` across all layer SWF templates and workflow standards.

#### [MODIFY] `framework/layers/01_BRD/`

- `BRD-SWF-TEMPLATE.yaml:557`: Modernize switch condition to `${ .blocking_findings == 0 and .gate_passed == true }`.
- `BRD_WORKFLOW_STANDARD.md:147`: Update workflow documentation to reflect zero-blocking-findings gate.

#### [MODIFY] `framework/layers/02_PRD/`

- `PRD-SWF-TEMPLATE.yaml:390`: Modernize switch condition to `${ .blocking_findings == 0 and .gate_passed == true }`.
- `PRD_WORKFLOW_STANDARD.md:148`: Update workflow documentation to reflect zero-blocking-findings gate.

#### [MODIFY] `framework/layers/03_EARS/`

- `EARS-SWF-TEMPLATE.yaml`:
  - Line 235: Modernize operation `urn:aidoc:functions:readiness#score` $\to$ `urn:aidoc:functions:readiness#verify`.
  - Line 324: Modernize action name `scoreReadiness` $\to$ `verifyBddReadiness`.
  - Line 336 (`ReadinessApproved`): Modernize condition to `${ .conflictCount == 0 and .syntax_valid == true and .hasAmbiguity == false }` (short-circuit guard).
  - Line 339 (`AmbiguityDetected`): Modernize condition to `${ .hasAmbiguity == true }`.
  - Line 359 (review gate switch): Modernize condition to `${ .blocking_findings == 0 and .gate_passed == true }`.
- `EARS_WORKFLOW_STANDARD.md:154`: Update workflow documentation to reflect zero-blocking-findings gate.

#### [MODIFY] `framework/layers/04_BDD/`

- `BDD-SWF-TEMPLATE.yaml:202`: Modernize switch condition to `${ .blocking_findings == 0 and .gate_passed == true }`.
- `BDD_WORKFLOW_STANDARD.md:176`: Update workflow documentation.

#### [MODIFY] `framework/layers/05_ADR/`

- `ADR-SWF-TEMPLATE.yaml:355`: Modernize review switch condition to `${ .blocking_findings == 0 and .gate_passed == true }`. *(Note: MCDA candidate utility score in lines 306/313 is an architectural trade-off evaluation and is preserved).*
- `ADR_WORKFLOW_STANDARD.md:281`: Update workflow documentation.

#### [MODIFY] `framework/layers/06_SPEC/`

- `SPEC-SWF-TEMPLATE.yaml:349`: Modernize switch condition to `${ .blocking_findings == 0 and .gate_passed == true }`.
- `SPEC_WORKFLOW_STANDARD.md:242`: Update workflow documentation.

#### [MODIFY] `framework/layers/07_TDD/`

- `TDD-SWF-TEMPLATE.yaml:279`: Modernize switch condition to `${ .blocking_findings == 0 and .gate_passed == true }`.
- `TDD_WORKFLOW_STANDARD.md:228`: Update workflow documentation.

#### [MODIFY] `framework/layers/09_CHG/` and Governance Mirrors

- `framework/layers/09_CHG/CHG-SWF-TEMPLATE.yaml:329`: Modernize switch condition to `${ .blocking_findings == 0 and .gate_passed == true }`.
- `framework/governance/chg/CHG-SWF-TEMPLATE.yaml:329`: Synchronize byte-identically.
- `framework/governance/templates/CHG-SWF-TEMPLATE.yaml:329`: Synchronize byte-identically.

#### [MODIFY] `framework/layers/10_EVAL/`

- `EVAL-SWF-TEMPLATE.yaml:312`: Modernize switch condition to `${ .blocking_findings == 0 and .gate_passed == true }`.
- `EVAL_WORKFLOW_STANDARD.md:75, 76, 169`: Update workflow documentation:
  - Line 75: replace `Calculate aggregated score and gate metrics` with `Calculate quality gate metrics and BTV pass verification`.
  - Line 76: replace `Assesses score >= 90 and blocker_count == 0` with `Assesses blocker_count == 0 and gate_passed == true`.
  - Line 169: replace `${ .review_score >= 90 and .blocking_findings == 0 and .gate_passed == true }` with zero-blocking-findings gate.

#### [MODIFY] `framework/governance/GOVERNANCE_WORKFLOW_STANDARD.md`

- Line 382: Modernize generic review gate documentation to zero-blocking-findings gate.

---

### Component 2: Standalone Governance Workflows Modernization

Modernize `.review_score >= 90` conditions and scalar action arguments in `framework/governance/workflows/`:

- `brd-business-validation.sw.yaml:174`: Condition $\to$ `${ .blocking_findings == 0 and .gate_passed == true }`.
- `prd-feature-decomposition.sw.yaml:186`: Condition $\to$ `${ .blocking_findings == 0 and .gate_passed == true }`.
- `ears-requirements-validation.sw.yaml`:
  - Line 164 (`BddReadyApproved`): Condition $\to$ `${ .conflictCount == 0 and .upstreamPrdVerified == true and .ambiguityFlag == false }`.
  - Line 167 (`ClarificationRequired`): Condition $\to$ `${ .ambiguityFlag == true }`.
  - Line 187 (`ReviewApproved`): Condition $\to$ `${ .blocking_findings == 0 and .gate_passed == true }`.
  - Line 235 (`publishRatifiedEarsSet`): Argument `readinessScore: "${ .readinessScore }"` $\to$ `bdd_ready: "PASS"`.
  - Line 306 (`recordRejectionDetails`): Argument `readinessScore: "${ .readinessScore }"` $\to$ `bdd_ready: "FAIL"`.
- `bdd-acceptance-run.sw.yaml:129`: Condition $\to$ `${ .blocking_findings == 0 and .gate_passed == true }`.
- `adr-decision-analysis.sw.yaml`:
  - Line 214: Condition $\to$ `${ .blocking_findings == 0 and .gate_passed == true }`.
  - Line 252 (`RatifyArchitectureDecision`): Modernize hardcoded argument `spec_readiness_score: 95` to `spec_ready: "PASS"`.
- `spec-choreography-contract.sw.yaml:201`: Condition $\to$ `${ .blocking_findings == 0 and .gate_passed == true }`.
- `tdd-test-execution.sw.yaml:256`: Condition $\to$ `${ .blocking_findings == 0 and .gate_passed == true }`.
- `chg-request-flow.sw.yaml:347`: Condition $\to$ `${ .blocking_findings == 0 and .gate_passed == true }`.
- `eval-verification-run.sw.yaml`:
  - Line 82 (`LoadEvaluationStrategy`): Modernize argument `threshold_min_score: 90` to `verify_btv_pass: true`.
  - Line 194 (`ReviewGateApproved`): Condition $\to$ `${ .blocking_findings == 0 and .gate_passed == true }`.
- `iplan-escalation-flow.sw.yaml:123`: Condition $\to$ `${ .blocking_findings == 0 and .gate_passed == true }`.
- `review-remediation-flow.sw.yaml`:
  - Line 178 (`EmitApprovalRecord`): Modernize argument `score: "${ .readiness_score }"` to `gate_verdict: "PASS"`.

---

### Component 3: Declarative & Graph Template Readiness Indicators

#### Declarative Templates

Standardize downstream readiness indicators in declarative templates from percentage placeholders (`[X]%`) to binary status (`[PASS | FAIL]`):

- `framework/layers/03_EARS/EARS-TEMPLATE.yaml:421`: Update `bdd_ready: "[X]%"` $\to$ `bdd_ready: "[PASS | FAIL]"`.
- `framework/layers/04_BDD/BDD-TEMPLATE.yaml:353`: Update `adr_ready: "[X]%"` $\to$ `adr_ready: "[PASS | FAIL]"`.
- `framework/layers/05_ADR/ADR-TEMPLATE.yaml:424`: Update `spec_ready: "[X]%"` $\to$ `spec_ready: "[PASS | FAIL]"`.
- `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml:292`: Update `tdd_ready: "[X]%"` $\to$ `tdd_ready: "[PASS | FAIL]"`.

#### SDD-GRAPH Templates

Standardize metadata readiness targets in property graph templates from scalar `"90/100"` to binary `"PASS"`:

- `framework/layers/02_PRD/PRD-GRAPH-TEMPLATE.yaml:35`: Update `ears_ready_target: "90/100"` $\to$ `ears_ready_target: "PASS"`.
- `framework/layers/03_EARS/EARS-GRAPH-TEMPLATE.yaml:21`: Update `bdd_ready_target: "90/100"` $\to$ `bdd_ready_target: "PASS"`.
- `framework/layers/05_ADR/ADR-GRAPH-TEMPLATE.yaml:24`: Update `spec_ready_target: "90/100"` $\to$ `spec_ready_target: "PASS"`.
- `framework/layers/06_SPEC/SPEC-GRAPH-TEMPLATE.yaml:22`: Update `tdd_ready_target: "90/100"` $\to$ `tdd_ready_target: "PASS"`.
- `framework/layers/07_TDD/TDD-GRAPH-TEMPLATE.yaml:24`: Update `iplan_ready_target: "90/100"` $\to$ `iplan_ready_target: "PASS"`.

---

### Component 4: Project Documentation & Structure Cleanup

#### [MODIFY] `docs/REPO_STRUCTURE.md`

- Lines 87–88: Update target location for legacy platforms to clarify that runtime code was removed from the working tree and preserved on branch `legacy-ucx-v3.2-read-only`.
- Lines 97–99: Remove stale statement *"the plugin is the distribution"*; align with engine-agnostic framework model in `AGENTS.md`.

#### [MODIFY] `docs/PROJECT.md`

- Line 183: Clarify that `CHANGELOG.md` in `framework/` is a frozen tombstone (`(retired tombstone)`).

---

### Component 5: Conformance Suite Verification & Regression Guards

#### [MODIFY] `tests/conformance/test_governance_workflows.py`

- Add a centralized test `test_no_residual_review_score_in_workflows` verifying that zero workflows in `framework/governance/workflows/` or layer SWF templates in `framework/layers/` retain the legacy strings `.review_score >= 90`, `.readinessScore >= 90`, or `.score >= 90`.

#### [MODIFY] `tests/conformance/test_chg_flows_router.py`

- Extend `test_swf_template_copies_identical` and `test_graph_template_copies_identical` to assert 3-way byte parity across `framework/layers/09_CHG/`, `framework/governance/chg/`, and `framework/governance/templates/`.

---

### Component 6: Normative Spec Version Bump Protocol

Per `AGENTS.md` and `GATE-SPEC-E005`:

1. Bump `framework/VERSION` from `0.96.9` to `0.96.10`.
2. Append `0.96.9` to `OLD_VERSIONS` in `hooks/sync-version-refs.sh`.
3. Run `bash hooks/sync-version-refs.sh` to propagate pins.
4. Verify locally with `python3 tests/chg/spec_gate.py --base origin/dev`.

---

## 5. Verification Plan

### Automated Tests

1. **Plan Gate**:

   ```bash
   python3 .agents/skills/verified-planning/check_plan.py plans/SDD-BTV-WORKFLOW-AND-DOCS-RECONCILIATION-PLAN.md
   ```

2. **Spec Change Gate**:

   ```bash
   python3 tests/chg/spec_gate.py --base origin/dev
   ```

3. **SWF Workflow Linter**:

   ```bash
   python3 -m sdd_doc_lint.swf_lint --warn-exit framework/layers/ framework/governance/
   ```

4. **CHG & Surface Linters**:

   ```bash
   python3 sdd_doc_lint/chg_lint.py <chg-file.yaml>
   python3 -m sdd_doc_lint --check-surfaces .
   ```

5. **Full Conformance Suite**:

   ```bash
   pytest tests/conformance/
   ```

6. **Pre-push Check**:

   ```bash
   bash hooks/pre_push_check.sh
   ```

### Manual Verification

- Verify that `CHG-SWF-TEMPLATE.yaml` and `CHG-GRAPH-TEMPLATE.yaml` across `09_CHG/`, `governance/chg/`, and `governance/templates/` remain 100% byte-identical.
- Verify that all SWF switch conditions parse cleanly under CNCF Serverless Workflow v0.8 DSL rules.

---

## Claim ledger

| # | Claim | Symbol | Citation |
|---|---|---|---|
| 1 | Residual review_score in BRD SWF template | `.review_score >= 90` | framework/layers/01_BRD/BRD-SWF-TEMPLATE.yaml:557 |
| 2 | Residual review_score in BRD workflow standard | `.review_score >= 90` | framework/layers/01_BRD/BRD_WORKFLOW_STANDARD.md:147 |
| 3 | Residual review_score in PRD SWF template | `.review_score >= 90` | framework/layers/02_PRD/PRD-SWF-TEMPLATE.yaml:390 |
| 4 | Residual review_score in PRD workflow standard | `.review_score >= 90` | framework/layers/02_PRD/PRD_WORKFLOW_STANDARD.md:148 |
| 5 | Residual review_score in EARS SWF template | `.review_score >= 90` | framework/layers/03_EARS/EARS-SWF-TEMPLATE.yaml:359 |
| 6 | Residual review_score in EARS workflow standard | `.review_score >= 90` | framework/layers/03_EARS/EARS_WORKFLOW_STANDARD.md:154 |
| 7 | Residual review_score in BDD SWF template | `.review_score >= 90` | framework/layers/04_BDD/BDD-SWF-TEMPLATE.yaml:202 |
| 8 | Residual review_score in BDD workflow standard | `.review_score >= 90` | framework/layers/04_BDD/BDD_WORKFLOW_STANDARD.md:176 |
| 9 | Residual review_score in ADR SWF template | `.review_score >= 90` | framework/layers/05_ADR/ADR-SWF-TEMPLATE.yaml:355 |
| 10 | Residual review_score in ADR workflow standard | `.review_score >= 90` | framework/layers/05_ADR/ADR_WORKFLOW_STANDARD.md:281 |
| 11 | Residual review_score in SPEC SWF template | `.review_score >= 90` | framework/layers/06_SPEC/SPEC-SWF-TEMPLATE.yaml:349 |
| 12 | Residual review_score in SPEC workflow standard | `.review_score >= 90` | framework/layers/06_SPEC/SPEC_WORKFLOW_STANDARD.md:242 |
| 13 | Residual review_score in TDD SWF template | `.review_score >= 90` | framework/layers/07_TDD/TDD-SWF-TEMPLATE.yaml:279 |
| 14 | Residual review_score in TDD workflow standard | `.review_score >= 90` | framework/layers/07_TDD/TDD_WORKFLOW_STANDARD.md:228 |
| 15 | Residual review_score in CHG SWF template | `.review_score >= 90` | framework/layers/09_CHG/CHG-SWF-TEMPLATE.yaml:329 |
| 16 | Residual review_score in EVAL SWF template | `.review_score >= 90` | framework/layers/10_EVAL/EVAL-SWF-TEMPLATE.yaml:312 |
| 17 | Residual review_score in EVAL workflow standard | `.review_score >= 90` | framework/layers/10_EVAL/EVAL_WORKFLOW_STANDARD.md:169 |
| 18 | Residual review_score in governance workflow standard | `.review_score >= 90` | framework/governance/GOVERNANCE_WORKFLOW_STANDARD.md:382 |
| 19 | Residual review_score in governance brd workflow | `.review_score >= 90` | framework/governance/workflows/brd-business-validation.sw.yaml:174 |
| 20 | Residual review_score in governance prd workflow | `.review_score >= 90` | framework/governance/workflows/prd-feature-decomposition.sw.yaml:186 |
| 21 | Residual review_score in governance ears workflow | `.review_score >= 90` | framework/governance/workflows/ears-requirements-validation.sw.yaml:187 |
| 22 | Residual review_score in governance bdd workflow | `.review_score >= 90` | framework/governance/workflows/bdd-acceptance-run.sw.yaml:129 |
| 23 | Residual review_score in governance adr workflow | `.review_score >= 90` | framework/governance/workflows/adr-decision-analysis.sw.yaml:214 |
| 24 | Residual review_score in governance spec workflow | `.review_score >= 90` | framework/governance/workflows/spec-choreography-contract.sw.yaml:201 |
| 25 | Residual review_score in governance tdd workflow | `.review_score >= 90` | framework/governance/workflows/tdd-test-execution.sw.yaml:256 |
| 26 | Residual review_score in governance chg workflow | `.review_score >= 90` | framework/governance/workflows/chg-request-flow.sw.yaml:347 |
| 27 | Residual review_score in governance eval workflow | `.review_score >= 90` | framework/governance/workflows/eval-verification-run.sw.yaml:194 |
| 28 | Residual review_score in governance iplan workflow | `.review_score >= 90` | framework/governance/workflows/iplan-escalation-flow.sw.yaml:123 |
| 29 | Residual percentage placeholder in EARS template | `bdd_ready:` | framework/layers/03_EARS/EARS-TEMPLATE.yaml:421 |
| 30 | Residual percentage placeholder in BDD template | `adr_ready:` | framework/layers/04_BDD/BDD-TEMPLATE.yaml:353 |
| 31 | Residual percentage placeholder in ADR template | `spec_ready:` | framework/layers/05_ADR/ADR-TEMPLATE.yaml:424 |
| 32 | Residual percentage placeholder in SPEC template | `tdd_ready:` | framework/layers/06_SPEC/SPEC-TEMPLATE.yaml:292 |
| 33 | Stale platform archive location in REPO_STRUCTURE | `archive/platforms/hermes/` | docs/REPO_STRUCTURE.md:87 |
| 34 | Stale distribution claim in REPO_STRUCTURE | `the plugin is the distribution` | docs/REPO_STRUCTURE.md:99 |
| 35 | Model IPLAN workflow test verifying absence of review_score | `Absence of legacy review_score >= 90` | tests/conformance/test_iplan_workflow.py:204 |
| 36 | Residual score check in EVAL workflow standard decide table | `score >= 90 and blocker_count == 0` | framework/layers/10_EVAL/EVAL_WORKFLOW_STANDARD.md:76 |
| 37 | Residual scalar spec readiness argument in ADR governance workflow | `spec_readiness_score: 95` | framework/governance/workflows/adr-decision-analysis.sw.yaml:252 |
| 38 | Residual threshold_min_score argument in eval verification workflow | `threshold_min_score: 90` | framework/governance/workflows/eval-verification-run.sw.yaml:82 |
| 39 | Residual readinessScore emission in ears governance workflow | `readinessScore: "${ .readinessScore }"` | framework/governance/workflows/ears-requirements-validation.sw.yaml:235 |
| 40 | Residual readiness#score operation in EARS SWF template | `readiness#score` | framework/layers/03_EARS/EARS-SWF-TEMPLATE.yaml:235 |
| 41 | Residual scoreReadiness action name in EARS SWF template | `name: scoreReadiness` | framework/layers/03_EARS/EARS-SWF-TEMPLATE.yaml:324 |
| 42 | Residual score parameter in review remediation flow | `score: "${ .readiness_score }"` | framework/governance/workflows/review-remediation-flow.sw.yaml:178 |
| 43 | Residual readiness target in PRD graph template | `ears_ready_target: "90/100"` | framework/layers/02_PRD/PRD-GRAPH-TEMPLATE.yaml:35 |
| 44 | Residual readiness target in EARS graph template | `bdd_ready_target: "90/100"` | framework/layers/03_EARS/EARS-GRAPH-TEMPLATE.yaml:21 |
| 45 | Residual readiness target in ADR graph template | `spec_ready_target: "90/100"` | framework/layers/05_ADR/ADR-GRAPH-TEMPLATE.yaml:24 |
| 46 | Residual readiness target in SPEC graph template | `tdd_ready_target: "90/100"` | framework/layers/06_SPEC/SPEC-GRAPH-TEMPLATE.yaml:22 |
| 47 | Residual readiness target in TDD graph template | `iplan_ready_target: "90/100"` | framework/layers/07_TDD/TDD-GRAPH-TEMPLATE.yaml:24 |

---

## Review log

### Pass 1 - 2026-10-19 - Author Initial Draft

- Conducted full-repository audit across all 10 layers, 10 governance workflows, documentation, and conformance suites.
- Validated all 35 citations live against repository files.
- Formulated 5 distinct component packages covering layer SWF templates, workflow standards, governance workflows, declarative templates, and repo documentation.
- Formatted `## Claim ledger` and `## Review log` as unnumbered H2s for `check_plan.py` gate compliance.

### Pass 2 - 2026-10-19 - Adversarial Independent Review

- Independent review conducted by subagent `53d3e38f-6d33-4098-9c77-c5a9f79a58bd`.
- Resolved Finding 1 (EARS switch ordering): added explicit short-circuit guard (`.hasAmbiguity == false`) to `EARS-SWF-TEMPLATE.yaml` and `ears-requirements-validation.sw.yaml` and aligned transition state names (`ReadinessApproved`, `AmbiguityDetected`, `BddReadyApproved`, `ClarificationRequired`).
- Resolved Finding 2: added modernization of `spec_readiness_score: 95` to `spec_ready: "PASS"` in `adr-decision-analysis.sw.yaml:252` (Claim 37).
- Resolved Finding 5: added citation for `EVAL_WORKFLOW_STANDARD.md:76` (`score >= 90 and blocker_count == 0`, Claim 36).
- Resolved Finding 6: added Component 6 codifying the normative spec bump protocol (`0.96.9` $\to$ `0.96.10`, `OLD_VERSIONS` sync in `hooks/sync-version-refs.sh`, and `python3 tests/chg/spec_gate.py` verification).
- Resolved Finding 7: centralized conformance regression testing in `tests/conformance/test_governance_workflows.py`.
- Re-validated 37 citations against repository files.

### Pass 3 - 2026-10-20 - Adversarial Self-Audit & Deep-Dive Fold

- Adversarial self-audit conducted by subagent `bdba22d0-1070-4b30-bd4b-12716785155e`.
- Resolved Finding 1.1: added modernization of `threshold_min_score: 90` $\to$ `verify_btv_pass: true` in `eval-verification-run.sw.yaml:82` (Claim 38).
- Resolved Finding 1.2: added modernization of `readinessScore` emission $\to$ `bdd_ready: "PASS"` / `"FAIL"` in `ears-requirements-validation.sw.yaml:235, 306` (Claim 39).
- Resolved Finding 1.3: modernized operation `readiness#score` $\to$ `readiness#verify` and action `scoreReadiness` $\to$ `verifyBddReadiness` in `EARS-SWF-TEMPLATE.yaml:235, 324` (Claims 40, 41).
- Resolved Finding 1.4: modernized argument `score: "${ .readiness_score }"` $\to$ `gate_verdict: "PASS"` in `review-remediation-flow.sw.yaml:178` (Claim 42).
- Resolved Finding 2.1: added modernization of scalar readiness targets (`"90/100"` $\to$ `"PASS"`) across all 5 SDD-GRAPH templates (`PRD`, `EARS`, `ADR`, `SPEC`, `TDD`, Claims 43–47).
- Resolved Finding 2.4: updated `EVAL_WORKFLOW_STANDARD.md:75` description from calculating aggregated score to BTV pass verification.
- Resolved Finding 3.1: expanded `test_chg_flows_router.py` to enforce 3-way byte parity across all three `CHG-SWF-TEMPLATE.yaml` and `CHG-GRAPH-TEMPLATE.yaml` locations.
- Re-validated all 47 citations live against repository files.
- **Result:** ready (no remaining findings). Approved for implementation via Change Request.
