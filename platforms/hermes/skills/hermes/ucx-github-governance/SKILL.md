---
name: ucx-github-governance
description: |
  Hermes governance skill for GitHub issue and PR lifecycle control aligned to
  governance/GOVERNANCE_RULES.md and UCX V3 round-based gate policy.
version: 1.1.0
category: governance
author: UCX Framework Team
requires: []
---

# UCX GitHub Governance Skill

## Purpose

Manage issue->plan-set->PR governance flow in GitHub while preserving UCX V3
control-plane/execution-plane separation.

## Canonical Label Flow

Use governance label progression exactly:

`ai:ready -> ai:in-progress -> ai:review-requested`

Rules:

- Only `ai:ready` issues are eligible for autonomous execution.
- Do not use `ai:approved` or `ai:rejected`.
- Transition to `ai:in-progress` only after required plan artifacts are approved.
- Use `ai:review-requested` when acceptance criteria verification is complete and PR is ready for review.

## Mandatory Issue Workflow

Before coding:

1. Initialize project context when required (`sdd_init`, then `sdd_preflight`).
2. Complete issue analysis.
3. Create planning-first artifacts (layer roadmap, planning index, changelog plan).
4. Review planning artifacts for gaps.
5. Fix gaps or record explicit deferrals with rationale.
6. Create required plan artifact(s): document-layer IPLAN and/or permanent development plan (`PLAN-NNN_*`, preferred).
7. Review plan artifact(s) for step clarity and acceptance-criteria mapping.
8. Record explicit plan approval (human reviewer or independent LLM-as-judge session).
9. Start implementation by transitioning issue to `ai:in-progress`.

Before review request:

1. Verify linked-issue acceptance criteria with evidence.
2. Update issue checkboxes based on verified evidence only.
3. Add direct PR link (number + URL) to linked issue.

After review round:

1. Post review outcomes back to linked issue.
2. If re-review required, post delta findings and next actions.

## Round-Based PR Governance (Mandatory)

For autonomous execution PRs, run two-round maximum gate policy:

1. `sdd_validate`
2. `sdd_review`
3. `sdd_remediate`
4. post-remediation `sdd_validate`
5. Hermes final blocker-gap/inconsistency review

If Round 1 fails, run Round 2 with same sequence.
If Round 2 fails, mark escalation `REQUIRED`, block merge, require human review.

## GitHub PR Policy

- Ensure branch naming follows governance conventions.
- Ensure PR body links issue and traceability tags.
- Ensure AI review status labels are recorded (`ai:review-passed` / `ai:review-failed`) when enabled by workflow.
- Do not merge while escalation is active.

## UCX V3 Boundaries

- Document-layer lifecycle decisions remain UCX MCP-gated.
- This skill manages GitHub governance state and policy transitions.
- Implementation execution remains owned by execution agents.

## Failure Handling

If governance state is inconsistent:

1. Stop autonomous transition.
2. Record mismatch (label/state/evidence gap).
3. Request human/operator resolution.
