from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class TeamPlanRequest:
    project_root: Path
    supervisor_request: str
    slug: str
    roles_dir: Path | None = None
    context: str = ""
    constraints: tuple[str, ...] = ()
    requested_roles: tuple[str, ...] = ()


@dataclass(frozen=True)
class CouncilRole:
    role_id: str
    profile_grounding: str
    recommendation: str
    risks: str
    required_context: str
    suggested_steps: str
    approval_concerns: str


@dataclass(frozen=True)
class TeamPlanArtifacts:
    folder: Path
    intake_path: Path
    transcript_path: Path
    conflicts_path: Path
    implementation_plan_path: Path
    approval_request_path: Path
    selected_roles: tuple[str, ...] = field(default_factory=tuple)
