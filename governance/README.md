# Governance Documentation

Governance rules, templates, and workflows for the Docs Flow Framework.

## SDD v3.2 Baseline

Canonical delivery chain:

`BRD->PRD->EARS->BDD->ADR->SPEC->TDD->IPLAN->Code`

Canonical references:
- `ai_dev_flow_v3/LAYER_REGISTRY.yaml`
- `ai_dev_flow_v3/DOC_GOVERNANCE_CORE.md`
- `ai_dev_flow_v3/CHG/`

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

Use `ai_dev_flow_v3/` for active templates and guidance.
Legacy framework roots are deprecated and not part of active governance.

## Issue Creation Pattern

```
Human creates REF/project context
    ↓
AI generates v3 artifacts (BRD..TDD)
    ↓
AI creates implementation issue(s)
    ↓
AI creates IPLAN per issue before coding
    ↓
AI executes issue (ai:ready -> ai:in-progress -> ai:review-requested)
```
