# Governance Documentation

Governance rules, templates, and workflows for the UCX Framework.

## SDD v3.2 Baseline

Canonical delivery chain:

`BRD->PRD->EARS->BDD->ADR->SPEC->TDD->IPLAN->Code`

Canonical references:

- `framework/registry/LAYER_REGISTRY.yaml`
- `framework/governance/DOC_GOVERNANCE_CORE.md`
- `framework/governance/chg/`

## Plan Taxonomy (Authoritative)

UCX governance uses three plan types with separate purposes and storage boundaries:

| Plan Type | Purpose | Location | Retention |
|---|---|---|---|
| Document-layer IPLAN | Layer-8 bridge from SDD artifacts to implementation execution | Project SDD lifecycle output (`docs/IPLAN/`, `UCX/08_IPLAN/`, or equivalent) | Permanent |
| Permanent development plan | Operational planning for project development, sequencing, and execution history | `plans/` (or `governance/plans/` in governance-template repos) | Permanent |
| Temporary plan | Bug fixes, document corrections, and minor one-off work that does not require long-term tracking | `tmp/` | Disposable |

Promotion rule: if a temporary plan grows into new functionality, cross-cutting dependency management, or multi-session execution, move it to a permanent development plan under `plans/`.

## Active vs Deprecated Policy

- Active: all files under `governance/` unless explicitly marked `Deprecated`.
- Deprecated: transition-only files with a replacement reference and removal criteria.
- Validation: active files must not reference legacy framework roots.

## Core Governance Docs

- `governance/GOVERNANCE_RULES.md`
- `governance/AI_ISSUE_LIFECYCLE.md`

## Hermes Governance Skill Mapping

Hermes governance operations are implemented in `ucx_hermes/skills/hermes/`:

- `ucx-github-governance` -> issue/PR governance state transitions, acceptance-criteria sync, and round-based merge gates.
- `ucx-github-deploy-governance` -> CI/CD, QA, staging/production readiness, and post-deployment reopen loop.
- `ucx-sdd-bridge` -> UCX V3 lifecycle orchestration and MCP-gated document flow.

KB support skills:

- `ucx-kb-context` -> retrieval enrichment during lifecycle stages.
- `ucx-kb-maintenance` -> governance-controlled KB writes after approved implementation evidence.

## Bridge Docs (v3)

- `governance/TASKS_IPLAN_BRIDGE.md` (v3 artifact-to-IPLAN trace bridge)
- `governance/TSPEC_BDD_QA_BRIDGE.md` (TDD+BDD to QA execution)
- `governance/CHG_GOVERNANCE_BRIDGE.md` (CHG gate overlay to governance)

## Governance Automation

- `scripts/workflows/verify_acceptance_criteria.py`
- `scripts/workflows/generate_iplan_from_issue.py`
- `scripts/workflows/execute_qa_tests.py`
- `scripts/workflows/validate_governance.py`

Deprecated automation:

- `scripts/workflows/sync_tasks_from_issues.py` (legacy TASKS sync, disabled)

## SDD Integration

Use `framework/` for active templates and guidance.
Legacy framework roots are deprecated and not part of active governance.

Document-layer lifecycle orchestration is MCP-only for UCX V3. CLI usage is reserved for approved IPLAN implementation execution tasks.

Template validation policy:

- Files under `governance/templates/` are project scaffold sources and may contain links that resolve only after scaffolding into a target repo.
- For framework-repo quality gates, validate non-template governance docs directly.
- For template link gates, run validation in the scaffolded target-project context.

## Issue Creation Pattern

```
Human creates REF/project context
    ↓
Hermes generates v3 artifacts (BRD..TDD)
    ↓
Hermes creates implementation issue(s)
    ↓
Hermes creates planning artifacts per issue (roadmap, planning index, changelog plan)
    ↓
Hermes reviews and fixes planning gaps, then approves plan set
    ↓
Hermes creates IPLAN per issue and records approval before coding
    ↓
Execution agent executes issue in ai:ready (ai:ready -> ai:in-progress -> ai:review-requested)
```

## Operational Issue-Fix Pattern (Production)

```
Observability stack emits alerts/incidents
    ↓
Hermes triages and creates GitHub issue with severity, impact, repro context, traceability
    ↓
Policy gate approves issue for autonomous execution by moving workflow state to ai:ready
    ↓
Hermes completes planning-first governance artifacts and explicit plan approval
    ↓
Execution agent (Claude Code/Codex/OpenCode) fixes issue and submits PR
    ↓
Round 1 PR gates: sdd_validate -> sdd_review -> sdd_remediate -> post-remediation sdd_validate -> Hermes final blocker-gap check
    ↓
If Round 1 fails: execute Round 2 with same gate sequence
    ↓
If Round 2 fails: escalate to human review and block merge
    ↓
If gates pass: merge PR and close linked issue(s)
    ↓
Hermes reviews post-deployment evidence; if regressions are detected, open follow-up issue(s)
```

## Default Ownership Split

1. Hermes monitors observability signals through integrated telemetry systems and triage inputs.
2. Hermes opens and prioritizes GitHub issues with implementation traceability (`@spec`, `@tdd`, `@iplan`) and acceptance criteria.
3. Only issues in `ai:ready` are eligible for autonomous execution.
4. Execution agents (Claude Code, Codex, OpenCode, or equivalent) perform fix implementation, PR submission, validation, and deployment workflows.
5. Hermes performs round-based PR governance and merge-time escalation decisions.
