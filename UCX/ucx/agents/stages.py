"""Document lifecycle stage definitions for UCX v2.

Stages are shared across all document layers. Layer-specific stages
(e.g. PRD _validation copy) are expressed as sub-states of REVIEWED.
"""

from __future__ import annotations

from enum import Enum


class Stage(str, Enum):
    """Document workflow stage.

    Progression:
        CREATED → VALIDATED → REVIEWED → REMEDIATED → COMPLETE
    """

    CREATED = "created"
    VALIDATED = "validated"
    REVIEWED = "reviewed"
    REMEDIATED = "remediated"
    COMPLETE = "complete"


# Valid forward transitions
TRANSITIONS: dict[Stage, list[Stage]] = {
    Stage.CREATED: [Stage.VALIDATED],
    Stage.VALIDATED: [Stage.REVIEWED, Stage.CREATED],  # CREATED = re-validate after fixes
    Stage.REVIEWED: [Stage.REMEDIATED, Stage.VALIDATED],
    Stage.REMEDIATED: [Stage.COMPLETE, Stage.REVIEWED],
    Stage.COMPLETE: [],
}


def can_transition(current: Stage, target: Stage) -> bool:
    """Check whether a stage transition is valid."""
    return target in TRANSITIONS.get(current, [])
