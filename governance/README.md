# Governance Documentation

Governance rules, templates, and workflows for the UCX Framework.

## SDD v3.2 Baseline

Canonical delivery chain:

`BRD->PRD->EARS->BDD->ADR->SPEC->TDD->IPLAN->Code`

Canonical references:
- `ucx_flow_v3/LAYER_REGISTRY.yaml`
- `ucx_flow_v3/DOC_GOVERNANCE_CORE.md`
- `ucx_flow_v3/CHG/`

## Active vs Deprecated Policy

- Active: all files under `governance/` unless explicitly marked `Deprecated`.
- Deprecated: transition-only files with a replacement reference and removal criteria.
- Validation: active files must not reference legacy framework roots.

## Core Governance Docs

- `governance/GOVERNANCE_RULES.md`
- `governance/SDD_DEPTH_GUIDE.md`
- `governance/AI_ISSUE_LIFECYCLE.md`

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

Use `ucx_flow_v3/` for active templates and guidance.
Legacy framework roots are deprecated and not part of active governance.

## Issue Creation Pattern

```
Human creates REF/project context
    ↓
Hermes generates v3 artifacts (BRD..TDD)
    ↓
Hermes creates implementation issue(s)
    ↓
Hermes creates IPLAN per issue before coding
    ↓
Execution agent executes approved issue (ai:ready -> ai:in-progress -> ai:review-requested)
```

## Operational Issue-Fix Pattern (Production)

```
Observability stack emits alerts/incidents
    ↓
Hermes triages and creates GitHub issue with severity, impact, repro context, traceability
    ↓
Policy gate approves issue for autonomous execution by moving workflow state to ai:ready
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
3. Only approved issues in `ai:ready` are eligible for autonomous execution.
4. Execution agents (Claude Code, Codex, OpenCode, or equivalent) perform fix implementation, PR submission, validation, and deployment workflows.
5. Hermes performs round-based PR governance and merge-time escalation decisions.
