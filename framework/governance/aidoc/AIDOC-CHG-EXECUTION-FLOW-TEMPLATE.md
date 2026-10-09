# Architecture & Operational Standard: Autonomous Phased CHG Execution Flow

## Document Control

| Field | Value |
|---|---|
| Version | 1.1 |
| Status | Approved |
| Last Updated | 2026-10-06 |
| Author | Framework Maintainer |
| Framework Version | 0.91.1 |

**Scope:** Autonomous End-to-End CHG Processing for `[Project Name]`
**Governing Rules:** `AGENTS.md`, `GOVERNANCE_WORKFLOW_STANDARD.md`, `CI_AUTONOMOUS_PR_STANDARD.md`, `DOC_GOVERNANCE_CORE.md`
**Canonical Template:** `framework/governance/aidoc/AIDOC-CHG-EXECUTION-FLOW-TEMPLATE.md`

---

## 1. Purpose & Motivation

Executing changes across the Three-Tier Architecture (`seed/` → `docs/modules/` → `docs/sdd/` → `docs/sdd/08_IPLAN/` → code/tests → `docs/sdd/10_EVAL/`) is governed by the deterministic **8-Step Autonomous CHG Lifecycle**:
1. **Step #1: CHG Request Creation** (authoring the authorizing CHG in `status: Proposed`; zero repo files modified prior).
2. **Step #2: Primary Author Self-Review (Pass 1)** (identifying and fixing gaps in proposal, scope, checklist, and testing plan).
3. **Step #3: Independent Second Self-Review (Pass 2)** (adversarial evaluation by fresh-context judge against 4-lens rubric).
4. **Step #4: Formal Gate Approval** (recording `gate_approval`, advancing CHG to `status: Approved`).
5. **Step #5: CHG Implementation Execution** (advancing CHG to `status: In-Progress`; executing Tier 1 Seed updates with versioning, Tier 2 Module updates with versioning, Phase 0 SDD lifecycle, Phase 1 IPLAN authoring, and Phase 2 phased code/test delivery).
6. **Step #6: Submit PR & Auto-Merge on Green** (monitoring CI checks via 15-second polling watchdog and auto-merging).
7. **Step #7: Conditional DEV Deployment** (deploying DEV environment and running smoke tests for deployable code/schema changes; skipped for documentation/governance syncs).
8. **Step #8: Conditional Layer 10 EVAL Report** (generating authentic EVAL report with status PASS for deployable changes; clean governance sync closeout for non-deployable changes).

This specification standardizes this end-to-end engine, eliminating the governance gap where seed/module documents were modified prematurely before formal CHG review and approval, and mandating explicit document versioning across all architectural tiers.

---

## 2. Core Invariants

1. **Strict Prohibition of `--no-verify` & Hook Bypasses (HARD BLOCK):** AI agents are strictly forbidden from passing `--no-verify`, `--skip-verification`, or any force override on commits, pushes, or PR merges. All client-side hooks (`PostToolUse`, `PreCommit`, secret scanning, YAML linting) and remote CI status checks must be 100% strictly GREEN.
2. **Worktree & Branch Isolation:** Every phase and implementation step must execute in an isolated git worktree on a dedicated branch created from `origin/dev` (`git worktree add ../<project>-<task> -b feature/<branch-name> origin/dev`). Committing directly to integration branches (`dev`) or release branches (`staging`, `main`) is strictly prohibited (`WORKTREE_FLOW.md`).
3. **Dual Independent Self-Review:** Every PR targeting `dev` and every CHG request proposal must pass Pass 1 (Author self-review & local deterministic gates) and Pass 2 (Independent second-opinion judge, 4-lens rubric) per `CI_AUTONOMOUS_PR_STANDARD.md` Invariant 4.
4. **IPLAN Implementation Gate:** Zero implementation code may be written without an active IPLAN in `status: In Progress` referencing the authorizing CHG and listing every target file in its `file_manifest` (`DOC_GOVERNANCE_CORE.md` §3.13).
5. **Mandatory Issue Linking & Closing Report:** Every PR opened must link the governing issue using platform closing keywords (`Closes #N`, `Fixes #N`) for full resolution, or `Relates to #N` for intermediate phased steps. Upon confirmed merge, an anti-blind closure report must be posted to the issue thread (`CI_AUTONOMOUS_PR_STANDARD.md` Invariant 6).
6. **Zero Dummy Mocks or Placeholders:** Real interface contracts, real database assertions, and concrete test data. No `assert True` stubs or bypassed test bodies.
7. **Live DEV Deployment & Smoke Verification:** Code modifying runtime services, database schemas, or infrastructure configurations must be deployed to the DEV environment and verified with live smoke tests before claiming completion.
8. **Monotonic Status Progression:** CHG and IPLAN step statuses move strictly forward (`Pending` → `In-Progress` → `Completed` / `Implemented` → `Verified`). Statuses must never regress.
9. **Layer 10 EVAL Closeout Gate:** An IPLAN reaches `status: Verified` and a CHG reaches `status: Completed` only upon the production of an authentic Evaluation Report (`docs/sdd/10_EVAL/EVAL-{NN}/reports/EVAL-{NN}-RPT-001.yaml`) with verdict `PASS` (for deployable changes).
10. **Universal CHG Tracking Invariant (HARD BLOCK):** ANY activity that makes changes to the project (code, configuration, database schemas/migrations, frontend assets, tests, or governance/documentation) MUST be authorized and tracked via formal CHG flows (CHG request). Pure research, exploratory diagnostics, read-only code/log investigation, or inquiry tasks are the sole un-gated exception.
11. **Standardized 8-Step Lifecycle Sequencing Invariant (HARD BLOCK):** Changes must execute in strict sequence: Step #1 (CHG Creation) MUST occur prior to modifying any project files. Seed Docs (Tier 1) and Module Docs (Tier 2) updates occur ONLY in Step #5 after Step #4 formal approval. Modifying seed or module docs before CHG approval is strictly prohibited.
12. **Mandatory Seed & Module Document Versioning Invariant (HARD BLOCK):** As soon as seed documents are improved/evolved or module documents are updated, all documents must have explicit versioning (`Version: X.Y`, `Status`, `Date`, `Authoring CHG`, `Revision History`) and be registered in master index registries.
13. **Approval Authority Matrix & Verifiable Evidence:** Change weight and blast radius govern who holds authority to approve changes (Step #4) and auto-merge PRs (Step #6):
    - **C1 (`DIR2C` / `CODE2C`):** Pass 2 Autonomous AI Orchestrator / Judge. Auto-merge on `dev` when CI green.
    - **C2 (`CODE2S` / `SEED2C`):** Pass 2 Autonomous AI Orchestrator / Judge citing delegating issue/prompt evidence. Auto-merge on `dev` when CI green.
    - **C3 (`SDD2C` / `SEED2C` cross-layer):** Strictly Human Founder Gate (`GATE-10`, `Owner (C3)`). Auto-merge on `dev` strictly gated by explicit C3 Gate Approval.
    - **Promotions (`dev` -> `staging` -> `main`):** Strictly Human Founder via repository Web UI. Zero autonomous auto-merge.

---

## 3. End-to-End Standardized 8-Step Cascade

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP #1: CHG Request Creation (Proposed)                                    │
│ - Author docs/sdd/09-CHG/CHG-{NN}_{slug}.yaml in status: Proposed           │
│ - ZERO project files (seed, modules, SDD, code) modified prior              │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEPS #2 & #3: Dual Self-Review (Pass 1 & Pass 2)                           │
│ - Pass 1: Author self-review & fix (scope, checklist, testing plan)         │
│ - Pass 2: Independent judge evaluation (4-Lens Rubric)                      │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Verdict: PASS
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP #4: Formal Gate Approval (Approved)                                    │
│ - Approver per Approval Authority Matrix (C1/C2: Judge, C3: Human Founder)  │
│ - Record gate_approval with verifiable evidence; advance status to Approved  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Approved
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP #5: CHG Implementation Execution (In-Progress)                         │
│ - Advance CHG status to In-Progress                                         │
│ - Tier 1: Update Seed Docs (with explicit document versioning)              │
│ - Tier 2: Update Module Docs (with explicit document versioning & index)   │
│ - Phase 0: SDD Lifecycle (BRD/PRD -> EARS/BDD -> ADR -> SPEC -> TDD)       │
│ - Phase 1: Author IPLAN (complete file_manifest with PENDING items)         │
│ - Phase 2: Phased Code & Test Implementation (manifest PENDING -> DONE)     │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Implementation complete & tests green
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP #6: Submit PR & Auto-Merge on Green                                    │
│ - Open PR targeting dev with dual self-review audit trail & issue link      │
│ - Arm native auto-merge (gh pr merge --auto --squash)                       │
│ - 15s Polling Watchdog monitors checks until squash merge to dev            │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Squash merged to dev
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP #7: Conditional DEV Deployment (Condition-Gated)                       │
│ - Deployable (backend code, schemas, configs): deploy & run smoke tests     │
│ - Non-Deployable (docs, governance sync, SDD-only): deployment skipped      │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP #8: Conditional Layer 10 Evaluation Report (EVAL Closeout)             │
│ - Deployable: generate authentic Layer 10 EVAL report (verdict: PASS),      │
│   advance IPLAN to Verified, advance CHG to Completed                      │
│ - Non-Deployable: clean governance sync PR advancing CHG to Completed       │
│ - Publish final Issue Implementation & Closure Report; clean up worktree    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Multi-Tier Circuit Breakers (Anti-Infinite Loop System)

To guarantee that autonomous execution never enters an uncontrolled loop, exhausts compute, or cascades errors, the engine enforces six non-negotiable circuit breakers:

| Breaker | Threshold | Trigger Condition | System Action |
| :--- | :--- | :--- | :--- |
| **CB-1: Review-Fix Iteration Breaker** | Max 2 remediation passes | Pass 2 judge returns `REVISE` or `BLOCK` twice consecutively on the same step | **HALT.** Escalate to human founder with exact dissenting findings and proposed alternatives. |
| **CB-2: CI Polling Deadline** | 15 minutes (60 cycles @ 15s) | Required status checks remain pending, queued, or running after 15 minutes | **HALT.** Abort polling, diagnose stuck workflow run via platform API, and alert human founder. |
| **CB-3: CI Failure Remediation Cap** | Exactly 1 retry attempt | Required CI status checks fail on `dev` pull request | **REMEDIATE ONCE.** Pull run logs, apply targeted fix on feature branch, re-verify locally, push commit. If checks fail a second time, **HALT** immediately. |
| **CB-4: Monotonic Phase State Invariant** | 0 regressions allowed | Attempt to modify a `Completed` step or regress CHG/IPLAN status | **FATAL REJECT.** Completed steps are immutable. Post-implementation defects must be addressed via new follow-up issue/CHG. |
| **CB-5: Git Divergence & Conflict Lock** | 0 force-pushes allowed | Remote integration branch diverges during feature work (`DIRTY` / `CONFLICTING`) | Merge cleanly from updated `origin/dev`. Autonomous resolution authorized for Class 1 (Deterministic/Additive) conflicts. If Class 2 (Semantic/Architectural) conflicts occur, abort merge and **HALT** immediately. |
| **CB-6: Scope Boundary Escort** | Out-of-manifest file edit | Implementation requires touching files not listed in IPLAN `file_manifest` | **HALT.** Do not write to unauthorized files. Update IPLAN or submit feedback issue. |

---

## 5. Phase 3 Routing: Deployable vs Non-Deployable Changes

Execution bifurcates based on whether the change requires live environment deployment:

1. **Deployable Changes (Code, Config, Database Migrations):**
   - Whenever source code, runtime configuration, or database migrations are created or changed, the agent MUST execute the full terminal cascade:
     1. Deploy DEV environment: `[deploy command]`
     2. Execute live smoke test suite: `[smoke test command]`
     3. Generate authentic Layer 10 EVAL report: `[python3 scripts/test/generate_eval_report.py --iplan <IPLAN> --chg <CHG>]`
     4. Advance IPLAN to `Verified` and CHG to `Completed`.
2. **Non-Deployable Changes (Governance, Documentation, SDD-Only):**
   - For pure documentation and governance changes, Phase 3 requires zero live deployment or smoke testing.
   - The change completes directly via a clean governance sync PR, advancing status to `Completed` once static analysis and dual self-review pass.

---

## 6. Operational Checklist for Autonomous Agents

Before initiating autonomous execution on any CHG:
- [ ] Verify CHG status is `Approved` or `In-Progress` with recorded gate approval.
- [ ] Verify `testing_plan:` is declared in the CHG (for code/schema changes).
- [ ] Confirm Phase 0 SDD documents are approved and merged to `dev`.
- [ ] Confirm IPLAN is `In Progress` with complete `file_manifest` before writing code.
- [ ] Enforce worktree isolation and dependency hydration for every step.
- [ ] Verify zero `--no-verify` flags are present in any script or command.
- [ ] Deploy DEV environment and verify smoke tests before opening PR for runtime changes.
- [ ] Check circuit breaker counters before each iteration.
- [ ] Maintain 15-second polling watchdog until PR merge confirmation.
- [ ] Execute clean worktree removal and `dev` fast-forward before initiating the next step.
- [ ] Generate Layer 10 EVAL report upon completion of deployable changes.
- [ ] Advance IPLAN to `Verified` and CHG to `Completed` in the final closeout PR.
