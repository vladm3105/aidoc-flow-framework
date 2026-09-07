from __future__ import annotations

from mcp_server.team_emulator.models import CouncilRole, TeamPlanRequest


def render_intake(request: TeamPlanRequest, selected_roles: tuple[str, ...]) -> str:
    constraints = "\n".join(f"- {item}" for item in request.constraints)
    roles = "\n".join(f"- {role}" for role in selected_roles)
    return f"""# Intake

Supervisor request: {request.supervisor_request}

Context: {request.context or "No additional context provided."}

Constraints:
{constraints or "- Stop before implementation."}

Selected chair: ceo

Selected roles:
{roles}
"""


def render_role_section(role: CouncilRole) -> str:
    return f"""## {role.role_id}

Profile grounding:
{role.profile_grounding}

Recommendation:
{role.recommendation}

Risks:
{role.risks}

Required context:
{role.required_context}

Suggested implementation steps:
{role.suggested_steps}

Approval concerns:
{role.approval_concerns}
"""


def render_council_transcript(roles: tuple[CouncilRole, ...]) -> str:
    return "# Council Transcript\n\n" + "\n".join(render_role_section(role) for role in roles)


def render_conflicts_and_risks() -> str:
    return """# Conflicts And Risks

## Agreements

- The emulator produces visible role-by-role recommendations.
- The implementation plan requires supervisor approval before execution.

## Tensions

- Runtime automation must not bypass human approval.

## Risk Controls

- Require `Status: Awaiting supervisor approval`.
- Keep implementation outside the emulator.
"""


def render_implementation_plan(request: TeamPlanRequest, roles: tuple[CouncilRole, ...]) -> str:
    role_summary = "\n".join(f"- `{role.role_id}`: {role.recommendation}" for role in roles)
    return f"""# Implementation Plan

## Supervisor Request

{request.supervisor_request}

## Goal

Produce an approval-ready implementation plan from an AI employee council simulation.

## Assumptions

- The founder is the supervisor.
- The AI CEO chairs the council.
- Implementation starts only after human approval.

## Scope

- Planning artifacts.
- Council transcript.
- Approval request.

## Non-Scope

- Executing the generated plan.
- Performing yellow/red actions.

## Council Summary

The selected roles recommend planning the work before implementation and preserving the approval stop.

## Role Recommendations

{role_summary}

## Conflicts / Tradeoffs

Lightweight planning is faster; full runtime automation should preserve the same artifact contract.

## Approval Gates

- Human supervisor approves this plan before implementation.

## Tasks

1. Review the role transcript.
2. Review risks and approval gates.
3. Approve, edit, or reject this plan.

## Validation

- Confirm required simulation artifacts exist.
- Confirm this plan includes the approval-waiting status.

## Rollback / Recovery

Delete this simulation folder if the plan is rejected.

## Human Approval Checklist

- [ ] Role transcript is understandable.
- [ ] Plan scope is correct.
- [ ] Approval gates are correct.

## AI Agent Execution Notes

Execute only after supervisor approval.

## Status

Status: Awaiting supervisor approval
"""


def render_approval_request() -> str:
    return """# Approval Request

Requested decision: Approve, edit, or reject the generated implementation plan.

Autonomy tier: Yellow. Human approval is required before execution.

Recommended option: Approve only if the plan is ready for an implementation agent.

Blast radius: Planning artifacts only until the supervisor approves implementation.

Rollback path: Delete this simulation folder.
"""
