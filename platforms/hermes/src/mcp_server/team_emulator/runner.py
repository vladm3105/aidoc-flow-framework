from __future__ import annotations

import re
from datetime import date
from pathlib import Path

from mcp_server.team_emulator.models import CouncilRole, TeamPlanArtifacts, TeamPlanRequest
from mcp_server.team_emulator.templates import (
    render_approval_request,
    render_conflicts_and_risks,
    render_council_transcript,
    render_implementation_plan,
    render_intake,
)

TECH_WORDS = ("runtime", "command", "plugin", "hermes", "code", "repo", "implementation")
GTM_WORDS = ("sales", "pricing", "customer", "launch", "marketing", "partner")
LEGAL_WORDS = ("contract", "legal", "terms", "dpa", "trademark")
COMPLIANCE_WORDS = ("compliance", "audit", "governance", "evidence", "iso", "eu ai act")
ALLOWED_ROLES = frozenset(
    {
        "ceo",
        "cto-platform",
        "aidoc-flow-lead",
        "aidoc-flow-eng-lead",
        "iplanic-lead",
        "aiops-flow-lead",
        "head-of-marketing",
        "head-of-sales",
        "sales-engineer",
        "customer-success-manager",
        "devrel-community",
        "finance-ops",
        "legal-contracts",
        "head-of-compliance",
        "head-of-partnerships",
    }
)


def _slug(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return cleaned or "team-plan"


def select_roles(request: TeamPlanRequest) -> tuple[str, ...]:
    if request.requested_roles:
        unknown = sorted(set(request.requested_roles) - ALLOWED_ROLES)
        if unknown:
            raise ValueError(f"Unknown role id(s): {', '.join(unknown)}")
        roles = ["ceo", *[role for role in request.requested_roles if role != "ceo"]]
        return tuple(dict.fromkeys(roles))

    text = f"{request.supervisor_request} {request.context}".lower()
    roles = ["ceo"]
    if any(word in text for word in TECH_WORDS):
        roles.extend(["cto-platform", "aidoc-flow-eng-lead", "devrel-community"])
    if any(word in text for word in GTM_WORDS):
        roles.extend(["head-of-marketing", "head-of-sales", "customer-success-manager"])
    if any(word in text for word in LEGAL_WORDS):
        roles.append("legal-contracts")
    if any(word in text for word in COMPLIANCE_WORDS):
        roles.append("head-of-compliance")
    return tuple(dict.fromkeys(roles))


def roles_dir_for(request: TeamPlanRequest) -> Path:
    return (request.roles_dir or request.project_root / ".claude" / "agents").resolve()


def load_role_profile(request: TeamPlanRequest, role_id: str) -> str:
    profile_path = roles_dir_for(request) / f"{role_id}.md"
    if not profile_path.exists():
        raise FileNotFoundError(f"Missing role profile: {profile_path}")
    return profile_path.read_text(encoding="utf-8")


def profile_grounding(role_id: str, profile_text: str) -> str:
    lines = [line.strip() for line in profile_text.splitlines() if line.strip()]
    for marker in ("You are", "## Core responsibilities", "## Hard limits", "## Source of truth"):
        for line in lines:
            if marker in line:
                return f"{role_id}: {line[:220]}"
    return f"{role_id}: {lines[0][:220] if lines else 'profile loaded'}"


def _next_available_folder(base: Path) -> Path:
    if not base.exists():
        return base
    for index in range(2, 1000):
        candidate = base.with_name(f"{base.name}-v{index}")
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"No available simulation folder name for {base}")


def _role_note(role_id: str, request: TeamPlanRequest) -> CouncilRole:
    profile_text = load_role_profile(request, role_id)
    grounding = profile_grounding(role_id, profile_text)
    return CouncilRole(
        role_id=role_id,
        profile_grounding=grounding,
        recommendation=(
            f"Plan the requested work from the {role_id} perspective before implementation."
        ),
        risks="Planning may drift into execution unless the approval stop is explicit.",
        required_context="Read the supervisor request, current repo guidance, and affected project docs.",
        suggested_steps=(
            "Contribute concise risks, required context, implementation steps, and approval concerns."
        ),
        approval_concerns=(
            "Do not execute yellow/red actions or implementation work during simulation."
        ),
    )


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def run_team_plan(request: TeamPlanRequest) -> TeamPlanArtifacts:
    slug = _slug(request.slug)
    folder = _next_available_folder(
        request.project_root / "ops" / "team-simulations" / f"{date.today().isoformat()}_{slug}"
    )
    roles = select_roles(request)
    notes = tuple(_role_note(role, request) for role in roles)

    intake = folder / "00_intake.md"
    transcript = folder / "01_council-transcript.md"
    conflicts = folder / "02_conflicts-and-risks.md"
    plan = folder / "03_implementation-plan.md"
    approval = folder / "04_approval-request.md"

    _write(intake, render_intake(request, roles))
    _write(transcript, render_council_transcript(notes))
    _write(conflicts, render_conflicts_and_risks())
    _write(plan, render_implementation_plan(request, notes))
    _write(approval, render_approval_request())

    return TeamPlanArtifacts(
        folder=folder,
        intake_path=intake,
        transcript_path=transcript,
        conflicts_path=conflicts,
        implementation_plan_path=plan,
        approval_request_path=approval,
        selected_roles=roles,
    )
