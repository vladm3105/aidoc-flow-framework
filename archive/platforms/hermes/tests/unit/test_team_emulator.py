from __future__ import annotations

import asyncio
import sys
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp_server.team_emulator.models import TeamPlanRequest  # noqa: E402
from mcp_server.team_emulator.runner import run_team_plan, select_roles  # noqa: E402
from mcp_server.tool_registry import TOOLS, handle_tool  # noqa: E402


def _write_role_profiles(root: Path, roles: tuple[str, ...] = ("ceo", "cto-platform")) -> Path:
    roles_dir = root / ".claude" / "agents"
    roles_dir.mkdir(parents=True, exist_ok=True)
    for role in roles:
        (roles_dir / f"{role}.md").write_text(
            f"---\nname: {role}\ndescription: {role} test profile\n---\n\n"
            f"You are the {role} test role.\n\n## Core responsibilities\n\n"
            f"- Provide {role}-specific planning guidance.\n",
            encoding="utf-8",
        )
    return roles_dir


def test_select_roles_always_includes_ceo_and_relevant_technical_roles(
    tmp_path: Path,
) -> None:
    request = TeamPlanRequest(
        project_root=tmp_path,
        supervisor_request="Build a Hermes runtime command for the Claude plugin workflow",
        slug="hermes-runtime-command",
    )

    assert select_roles(request) == (
        "ceo",
        "cto-platform",
        "aidoc-flow-eng-lead",
        "devrel-community",
    )


def test_select_roles_rejects_unknown_requested_role(tmp_path: Path) -> None:
    request = TeamPlanRequest(
        project_root=tmp_path,
        supervisor_request="Plan work",
        slug="plan-work",
        requested_roles=("ceo", "invented-seat"),
    )

    with pytest.raises(ValueError, match="Unknown role"):
        select_roles(request)


def test_run_team_plan_writes_required_artifacts(tmp_path: Path) -> None:
    roles_dir = _write_role_profiles(tmp_path)
    request = TeamPlanRequest(
        project_root=tmp_path,
        supervisor_request="Create a team emulator for planning work",
        slug="team-emulator",
        roles_dir=roles_dir,
        context="Operations repo planning workflow",
        constraints=("Stop before implementation",),
        requested_roles=("ceo", "cto-platform"),
    )

    artifacts = run_team_plan(request)

    assert artifacts.folder == (
        tmp_path / "ops" / "team-simulations" / f"{date.today().isoformat()}_team-emulator"
    )
    assert artifacts.intake_path.exists()
    assert artifacts.transcript_path.exists()
    assert artifacts.conflicts_path.exists()
    assert artifacts.implementation_plan_path.exists()
    assert artifacts.approval_request_path.exists()
    plan_text = artifacts.implementation_plan_path.read_text(encoding="utf-8")
    assert "Status: Awaiting supervisor approval" in plan_text
    transcript_text = artifacts.transcript_path.read_text(encoding="utf-8")
    assert "## ceo" in transcript_text
    assert "Profile grounding:" in transcript_text
    assert "You are the ceo test role" in transcript_text
    assert "Recommendation:" in transcript_text


def test_run_team_plan_uses_collision_safe_folder(tmp_path: Path) -> None:
    roles_dir = _write_role_profiles(tmp_path)
    existing = tmp_path / "ops" / "team-simulations" / f"{date.today().isoformat()}_team-emulator"
    existing.mkdir(parents=True)

    artifacts = run_team_plan(
        TeamPlanRequest(
            project_root=tmp_path,
            supervisor_request="Create a team emulator for planning work",
            slug="team-emulator",
            roles_dir=roles_dir,
            requested_roles=("ceo",),
        )
    )

    assert artifacts.folder.name.endswith("-v2")


def test_run_team_plan_fails_when_role_profile_missing(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Missing role profile"):
        run_team_plan(
            TeamPlanRequest(
                project_root=tmp_path,
                supervisor_request="Plan work",
                slug="plan-work",
                requested_roles=("ceo",),
            )
        )


def test_sdd_team_plan_tool_is_registered() -> None:
    names = {tool.name for tool in TOOLS}
    assert "sdd_team_plan" in names


def test_sdd_team_plan_dispatch_writes_plan(tmp_path: Path) -> None:
    roles_dir = _write_role_profiles(tmp_path, ("ceo", "cto-platform"))
    result = asyncio.run(
        handle_tool(
            "sdd_team_plan",
            {
                "project": str(tmp_path),
                "supervisor_request": "Plan a team emulator",
                "slug": "team-emulator",
                "roles_dir": str(roles_dir),
                "context": "Operations planning",
                "constraints": ["Stop for approval"],
                "requested_roles": ["ceo", "cto-platform"],
            },
        )
    )

    payload = result[0].text
    assert "Status: Awaiting supervisor approval" in payload
    assert "03_implementation-plan.md" in payload
