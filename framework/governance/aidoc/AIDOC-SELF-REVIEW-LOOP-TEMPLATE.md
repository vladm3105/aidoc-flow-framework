# Architecture & Operational Standard: Autonomous Multi-Agent Dual Self-Review Protocol

## Document Control

| Field | Value |
|---|---|
| Version | 1.1 |
| Status | Approved |
| Last Updated | 2026-10-06 |
| Author | Framework Maintainer |
| Framework Version | 0.89.0 |

**Scope:** Two-Stage Review & Remediation Loop for `[Project Name]`
**Governing Rules:** `REVIEW_REMEDIATION_FLOW.md`, `CI_AUTONOMOUS_PR_STANDARD.md`, `AGENTS.md`
**Canonical Template:** `framework/governance/aidoc/AIDOC-SELF-REVIEW-LOOP-TEMPLATE.md`

---

## 1. Purpose & Motivation

To guarantee software quality and prevent regressions in autonomous agent workflows, all deliverables must pass through a structured quality loop. Self-approving without independent verification invites cognitive blindness and subtle defect propagation.

This standard establishes the **Two-Stage Review & Fix Architecture**, the **Strict Independence Rule (Judge ≠ Generator)**, and the **Four-Lens Review Rubric**.

---

## 2. Two-Stage Review & Fix Architecture

Quality assurance executes across two distinct lifecycle stages:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ STAGE A: Proposal & Specification Review (Pre-Implementation)              │
│ - Target: Requirements, architecture specs, ADRs, test plans, IPLANs        │
│ - Objective: Eliminate ambiguity, missing failure modes, schema errors      │
│ - Outcome: Pass 1 Author Self-Review + Pass 2 Independent Review -> Signoff │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STAGE B: Implementation PR Review (Post-Implementation / Pre-Merge)         │
│ - Target: Code diffs, unit/integration test coverage, anti-mock compliance   │
│ - Objective: Verify correctness, test fidelity, performance, zero regressions│
│ - Outcome: Pass 1 Local Gate Run + Pass 2 Independent Code Audit -> Merge   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Strict Independence Mandate (Judge ≠ Generator)

1. **Role Separation:** The agent acting as reviewer/judge MUST be distinct from the authoring agent.
2. **Fresh Context Isolation:** The review pass must execute in an isolated session or subagent container without carrying prior author brainstorming or drafting prompts.
3. **Review-Only Authority:** The judge evaluates, scores, and emits concrete, located findings. The judge NEVER modifies the files under review during the review pass; fixes must be applied by the generator in a subsequent remediation pass.

---

## 4. Four-Lens Review Rubric

Every review pass evaluates the submission against four non-negotiable lenses:

### Lens 1: Correctness & Contract Adherence
- Does the code/specification satisfy all upstream requirements?
- Are boundary conditions, empty inputs, null pointers, and error returns handled gracefully?
- Do public API contracts and schemas match Layer 06 SPEC definitions?

### Lens 2: Anti-Mock & Real-Environment Fidelity
- Do integration tests exercise real external dependencies (databases, queues, storage)?
- Are unit tests free of trivial synthetic stubs that mock away real database behaviors?
- Does the test suite assert authentic status codes, schema layouts, and data persistence?

### Lens 3: Governance & Traceability Discipline
- Are all modified files listed in the authorizing IPLAN `file_manifest`?
- Do requirements and test cases carry valid traceability tags (`req_refs`, `spec_refs`)?
- Does the git branch conform to `feature/<issue>-<slug>` with clean commit messages?

### Lens 4: Security, Sandbox & Isolation
- Are inputs validated and sanitized against injection (SQL, command, XSS, prompt)?
- Does the code adhere to least-privilege principles without hardcoded tokens or secrets?
- Are multi-worktree port and container namespace isolations maintained?

---

## 5. Finding Severity & 3-Strike Remediation Saga

| Severity | Definition | Action Required |
|---|---|---|
| **Critical** | Correctness bug, data loss risk, contract break, security flaw | Blocks approval; must remediate immediately |
| **Medium** | Missing error branch, unhandled edge case, mock violation | Blocks approval; must remediate before merge |
| **Low** | Code style, documentation typo, minor optimization | Advisory; optional remediation |
| **Acknowledged** | Documented technical debt or deliberate tradeoff | Advisory; logged in review record |

### Remediation Circuit Breaker (3-Strike Cap)
The review→remediation cycle repeats until all Critical and Medium findings are resolved, up to a maximum of **3 iterations**. If convergence is not achieved after 3 cycles, the workflow HALTS and escalates to human maintainers.

---

## 6. Commit Audit Trail Mandate

To certify that the self-review loop completed, the PR commit range MUST carry one of the following literal phrases:

- `Multi-agent self-review per OPS-0065 (<agents>): PASS`
- `Self-review skipped per founder OK — <reason>` (Strictly reserved for human maintainer authorization)
