"""Agentic workflow engine for UCX v2.

Agents call MCP tools to drive documents through lifecycle stages.
This module provides the stage machine that tool handlers consult.

Implementation: docs/plans/PLAN-005_agentic_workflow.md
"""

from __future__ import annotations

from ucx.agents.stages import Stage, can_transition


class WorkflowEngine:
    """Minimal stage machine for document lifecycle management.

    MCP tool handlers create a WorkflowEngine per tool call to validate
    stage preconditions and compute the next recommended step.

    Full implementation via PLAN-005.
    """

    def __init__(self, current_stage: Stage) -> None:
        self._stage = current_stage

    @property
    def stage(self) -> Stage:
        return self._stage

    def next_step(self, layer: str) -> str:
        """Return a human-readable next-step recommendation for the agent.

        Args:
            layer: Document layer prefix (e.g. "brd", "prd").

        Returns:
            Tool name the agent should call next (e.g. "brd_review").
        """
        next_stages = {
            Stage.CREATED: f"{layer}_validate",
            Stage.VALIDATED: f"{layer}_review",
            Stage.REVIEWED: f"{layer}_remediate",
            Stage.REMEDIATED: f"{layer}_validate",  # re-validate after remediation
            Stage.COMPLETE: "none — workflow complete",
        }
        return next_stages.get(self._stage, "unknown")

    def assert_can_proceed(self, target: Stage) -> None:
        """Raise if the transition from current stage to target is invalid.

        Args:
            target: The stage the caller intends to enter.

        Raises:
            ValueError: If the transition is not permitted.
        """
        if not can_transition(self._stage, target):
            raise ValueError(
                f"Stage transition {self._stage} → {target} is not permitted. "
                f"Current stage: {self._stage.value}"
            )
