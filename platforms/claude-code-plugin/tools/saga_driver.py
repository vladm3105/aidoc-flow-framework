#!/usr/bin/env python3
"""Deterministic preemptive orchestrator for the review-saga lifecycle.

Plays the same role for the Claude Code plugin that `saga_orchestrator.py`
plays for Hermes: drives the create-review-revise loop, validates state
machine transitions against `framework/governance/REVIEW_SAGA.md`, manages
the durable saga.json journal, and dispatches each phase as a separately-
budgeted subprocess.

Invoked by `doc-<layer>-autopilot` SKILLs (thin entry points) via Bash.

Per SAGA-PARITY-001 Phase 2 Amendment 1, this script SUPERSEDES the
cooperative-enforcement pattern in Phase 2's original SKILL prompts -
which empirically failed (2026-06-05 verification: invalid transitions,
non-terminal final status, no subprocess dispatch).

Spec authority: `framework/governance/REVIEW_SAGA.md` and
`framework/governance/saga.schema.json`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

# Spec authority: framework/governance/REVIEW_SAGA.md "Transition table"
# A conformance test asserts this matches the spec table exactly.
_ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "PREPARED": {"FANOUT_STARTED", "PARTIAL_TIMEOUT"},
    "FANOUT_STARTED": {"BRANCH_RUNNING", "PARTIAL_TIMEOUT"},
    "BRANCH_RUNNING": {"BRANCH_COMPLETED", "BRANCH_FAILED", "PARTIAL_TIMEOUT"},
    "BRANCH_FAILED": {"BRANCH_COMPENSATING", "ESCALATED", "BRANCH_COMPLETED"},
    "BRANCH_COMPENSATING": {"BRANCH_RUNNING", "ESCALATED"},
    "BRANCH_COMPLETED": {"FANIN_REDUCED", "PARTIAL_TIMEOUT"},
    "FANIN_REDUCED": {"SYNTHESIZED", "PARTIAL_TIMEOUT"},
    "SYNTHESIZED": {"CLOSED"},
    "ESCALATED": set(),
    "CLOSED": set(),
    "PARTIAL_TIMEOUT": set(),
}

# Per layer, the crew (persona names) drawn from REVIEW_CREWS.yaml.
# Keep in sync with framework/governance/REVIEW_CREWS.yaml.
# Drift is caught by tests/conformance/test_saga_driver_invariants.py
# via test_layer_crews_match_yaml (Pass-4 A7).
_LAYER_CREWS: dict[str, list[str]] = {
    "01_BRD": ["business_analyst", "architect", "auditor", "chaos_engineer", "security_engineer"],
    "02_PRD": [
        "product_owner",
        "architect",
        "tech_lead",
        "chaos_engineer",
        "security_engineer",
        "auditor",
    ],
    "03_EARS": [
        "requirements_specialist",
        "tech_lead",
        "qa_lead",
        "chaos_engineer",
        "security_engineer",
    ],
    "04_BDD": [
        "qa_lead",
        "tech_lead",
        "chaos_engineer",
        "security_engineer",
        "operator",
        "auditor",
    ],
    "05_ADR": [
        "architect",
        "tech_lead",
        "chaos_engineer",
        "security_engineer",
        "operator",
        "auditor",
    ],
    "06_SPEC": [
        "architect",
        "tech_lead",
        "integration_lead",
        "chaos_engineer",
        "security_engineer",
    ],
    "07_TDD": [
        "qa_lead",
        "tech_lead",
        "chaos_engineer",
        "security_engineer",
        "operator",
        "auditor",
    ],
    "08_IPLAN": [
        "tech_lead",
        "architect",
        "operator",
        "integration_lead",
        "auditor",
        "chaos_engineer",
    ],
}

SOFT_DEADLINE_SECONDS = 1500
SUBPROCESS_TIMEOUT_SECONDS = 1800
MAX_ITERATIONS = 3


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _det_run_id(*, artifact_path: str, personas: list[str], time_bucket: str) -> str:
    payload = f"{artifact_path}|{','.join(sorted(personas))}|{time_bucket}"
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def _det_branch_id(*, run_id: str, persona: str) -> str:
    return hashlib.sha256(f"{run_id}|{persona}".encode()).hexdigest()[:12]


@dataclass
class SagaContext:
    layer: str
    layer_type: str
    artifact_id: str
    artifact_path: Path
    saga_dir: Path
    saga_file: Path
    start_epoch: float = field(default_factory=time.time)
    threshold: int = 90
    plugin_dir: Path | None = None


def load_or_init_saga(ctx: SagaContext, seed_path: Path) -> dict:
    """Load existing saga.json or initialize a fresh one.

    Entry conditions handled here:
    - saga.json missing -> fresh init (pre-Phase-2 blackboard migration
      if slot files are present).
    - status CLOSED or ESCALATED -> log + sys.exit(0).
    - status PARTIAL_TIMEOUT or any other in-flight state -> resume.
    """
    if ctx.saga_file.exists():
        saga = json.loads(ctx.saga_file.read_text())
        status = saga.get("status", "")
        if status == "CLOSED":
            print(
                f"saga already CLOSED for {ctx.artifact_id}; "
                f"iteration {saga.get('iteration', 1)} complete"
            )
            sys.exit(0)
        if status == "ESCALATED":
            print(f"saga ESCALATED for {ctx.artifact_id}; human review required")
            sys.exit(0)
        return saga

    ctx.saga_dir.mkdir(parents=True, exist_ok=True)
    crew = _LAYER_CREWS[ctx.layer]
    run_id = _det_run_id(
        artifact_path=str(ctx.artifact_path),
        personas=crew,
        time_bucket=datetime.now(UTC).strftime("%Y%m%d"),
    )

    existing_slots = list(ctx.saga_dir.glob("*.json"))
    pre_phase2_slots = [s for s in existing_slots if s.stem in crew and s.name != "saga.json"]

    if pre_phase2_slots:
        branches = {}
        for slot in pre_phase2_slots:
            branches[slot.stem] = {
                "branch_id": _det_branch_id(run_id=run_id, persona=slot.stem),
                "status": "BRANCH_COMPLETED",
                "attempt": 0,
                "started_at": _utc_now_iso(),
                "ended_at": _utc_now_iso(),
            }
        return {
            "review_run_id": run_id,
            "artifact_id": ctx.artifact_id,
            "layer": ctx.layer,
            "personas_requested": crew,
            "status": "BRANCH_COMPLETED",
            "iteration": 1,
            "current_phase": "re-review",
            "created_at": _utc_now_iso(),
            "updated_at": _utc_now_iso(),
            "branches": branches,
            "transitions": [
                {
                    "ts": _utc_now_iso(),
                    "from": None,
                    "to": "BRANCH_COMPLETED",
                    "scope": "run",
                }
            ],
            "compensation_actions": [],
        }

    return {
        "review_run_id": run_id,
        "artifact_id": ctx.artifact_id,
        "layer": ctx.layer,
        "personas_requested": crew,
        "status": "PREPARED",
        "iteration": 1,
        "current_phase": "draft",
        "created_at": _utc_now_iso(),
        "updated_at": _utc_now_iso(),
        "branches": {},
        "transitions": [
            {
                "ts": _utc_now_iso(),
                "from": None,
                "to": "PREPARED",
                "scope": "run",
            }
        ],
        "compensation_actions": [],
    }


def can_transition(*, current: str, target: str) -> bool:
    return target in _ALLOWED_TRANSITIONS.get(current, set())


def append_transition(
    saga: dict, *, from_state: str | None, to_state: str, scope: str = "run"
) -> None:
    """Append a transition. Raises ValueError on invalid transitions
    (preemptive enforcement)."""
    if from_state is not None and not can_transition(current=from_state, target=to_state):
        raise ValueError(
            f"Invalid transition: {from_state} -> {to_state} "
            f"(allowed: {sorted(_ALLOWED_TRANSITIONS.get(from_state, set()))})"
        )
    saga["transitions"].append(
        {
            "ts": _utc_now_iso(),
            "from": from_state,
            "to": to_state,
            "scope": scope,
        }
    )
    saga["updated_at"] = _utc_now_iso()


def write_saga(ctx: SagaContext, saga: dict) -> None:
    """Atomic write: temp file + rename."""
    tmp = ctx.saga_file.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(saga, indent=2))
    tmp.replace(ctx.saga_file)


def check_break_circuit(ctx: SagaContext, saga: dict) -> bool:
    """Return True if soft deadline crossed; saga.json is updated with
    PARTIAL_TIMEOUT and caller should exit."""
    elapsed = time.time() - ctx.start_epoch
    if elapsed > SOFT_DEADLINE_SECONDS:
        append_transition(saga, from_state=saga["status"], to_state="PARTIAL_TIMEOUT", scope="run")
        saga["status"] = "PARTIAL_TIMEOUT"
        write_saga(ctx, saga)
        print(
            f"break-circuit fired at {elapsed:.0f}s elapsed; "
            f"saga PARTIAL_TIMEOUT; current_phase={saga['current_phase']}"
        )
        return True
    return False


def resume_from_partial_timeout(saga: dict) -> None:
    """Per Phase 2 Pass 4 G-R1: walk transitions[] backward to find the
    pre-PARTIAL_TIMEOUT state. Set saga.status to that state so the loop
    continues from there. Do NOT append a transition with from: PARTIAL_TIMEOUT.
    """
    if saga["status"] != "PARTIAL_TIMEOUT":
        return
    for t in reversed(saga["transitions"]):
        if t["to"] != "PARTIAL_TIMEOUT":
            saga["status"] = t["to"]
            return
    saga["status"] = "PREPARED"


def dispatch_phase(ctx: SagaContext, phase: str, brief: str) -> int:
    """Dispatch a phase subprocess. Returns the subprocess exit code.

    `phase` is one of: 'draft', 'review', 'fixer', 're-review'.
    """
    slash = {
        "draft": f"/aidoc-flow:doc-{ctx.layer_type.lower()}",
        "review": f"/aidoc-flow:doc-{ctx.layer_type.lower()}-audit",
        "fixer": f"/aidoc-flow:doc-{ctx.layer_type.lower()}-fixer",
        "re-review": f"/aidoc-flow:doc-{ctx.layer_type.lower()}-audit",
    }[phase]
    cmd = [
        "timeout",
        str(SUBPROCESS_TIMEOUT_SECONDS),
        "claude",
        "--plugin-dir",
        str(ctx.plugin_dir),
        "--dangerously-skip-permissions",
        "-p",
        f"{slash} {brief}",
    ]
    print(f"dispatch: {phase} ({slash}) ...")
    result = subprocess.run(cmd, capture_output=False, check=False)
    return result.returncode


def read_verdict_score(ctx: SagaContext) -> tuple[int, str]:
    """Read .aidoc/review/<layer>/<id>/verdict.json. Returns (score, status).

    Returns (0, "MISSING") if verdict.json absent - caller treats this as
    an AUDIT FAILURE (per Pass-4 A9), distinct from a low content score
    (FAIL with score). Driver escalates rather than dispatching fixer.
    """
    verdict_path = ctx.saga_dir / "verdict.json"
    if not verdict_path.exists():
        return 0, "MISSING"
    v = json.loads(verdict_path.read_text())
    return v.get("content_score", 0), v.get("combined_status", "UNKNOWN")


def validate_and_repair_branches(ctx: SagaContext, saga: dict) -> None:
    """Per Pass-4 A8: after audit subprocess returns, validate that every
    branches[<persona>] entry has required fields per saga.schema.json
    (branch_id, status, attempt). If missing/malformed, repair from existing
    blackboard slot file mtimes.

    Per Pass-5 P5-2: if no slot file exists for a persona that's in the
    crew, fall back to saga.created_at as both started_at and ended_at.
    """
    crew = _LAYER_CREWS[ctx.layer]
    fallback_ts = saga.get("created_at", _utc_now_iso())
    for persona in crew:
        branch = saga.get("branches", {}).get(persona, {})
        slot_path = ctx.saga_dir / f"{persona}.json"
        if slot_path.exists():
            slot_ts = datetime.fromtimestamp(slot_path.stat().st_mtime, tz=UTC).isoformat()
        else:
            slot_ts = fallback_ts
        if "branch_id" not in branch or not branch["branch_id"]:
            branch["branch_id"] = _det_branch_id(run_id=saga["review_run_id"], persona=persona)
        if branch.get("status") not in {
            "BRANCH_RUNNING",
            "BRANCH_COMPLETED",
            "BRANCH_FAILED",
            "BRANCH_COMPENSATING",
        }:
            branch["status"] = "BRANCH_COMPLETED" if slot_path.exists() else "BRANCH_FAILED"
        if "attempt" not in branch:
            branch["attempt"] = 0
        if not branch.get("started_at"):
            branch["started_at"] = slot_ts
        if not branch.get("ended_at"):
            branch["ended_at"] = slot_ts
        saga.setdefault("branches", {})[persona] = branch


def _advance_after_phase(ctx: SagaContext, saga: dict, phase: str) -> None:
    """Apply the state-machine transition for a completed phase + decide
    next phase based on verdict.json (for review/re-review phases)."""
    if phase == "draft":
        append_transition(saga, from_state="PREPARED", to_state="FANOUT_STARTED")
        saga["status"] = "FANOUT_STARTED"
        saga["current_phase"] = "review"
    elif phase in ("review", "re-review"):
        validate_and_repair_branches(ctx, saga)

        score, status = read_verdict_score(ctx)
        if status == "MISSING":
            saga["compensation_actions"].append(
                {
                    "ts": _utc_now_iso(),
                    "branch": "*",
                    "reason": (f"audit phase '{phase}' returned but verdict.json absent"),
                    "action": "escalate",
                }
            )
            append_transition(saga, from_state=saga["status"], to_state="ESCALATED")
            saga["status"] = "ESCALATED"
            return

        if status == "PASS":
            append_transition(saga, from_state=saga["status"], to_state="FANIN_REDUCED")
            append_transition(saga, from_state="FANIN_REDUCED", to_state="SYNTHESIZED")
            append_transition(saga, from_state="SYNTHESIZED", to_state="CLOSED")
            saga["status"] = "CLOSED"
            saga["current_phase"] = "finalize"
        else:
            if saga["iteration"] < MAX_ITERATIONS:
                saga["current_phase"] = "fixer"
            else:
                append_transition(saga, from_state=saga["status"], to_state="ESCALATED")
                saga["status"] = "ESCALATED"
    elif phase == "fixer":
        saga["iteration"] += 1
        saga["current_phase"] = "re-review"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Saga driver for plugin autopilot")
    parser.add_argument("--layer", required=True, help="e.g. 01_BRD")
    parser.add_argument(
        "--artifact-id",
        default=os.environ.get("ARTIFACT_ID"),
        help="e.g. BRD-01; falls back to $ARTIFACT_ID",
    )
    parser.add_argument(
        "--artifact-path",
        default=os.environ.get("ARTIFACT_PATH"),
        help="output path; falls back to $ARTIFACT_PATH",
    )
    parser.add_argument(
        "--seed",
        default=os.environ.get("PREV_OUTPUT"),
        help="upstream seed; falls back to $PREV_OUTPUT",
    )
    parser.add_argument("--threshold", type=int, default=90)
    parser.add_argument(
        "--plugin-dir",
        default=os.environ.get("CLAUDE_PLUGIN_ROOT", os.environ.get("PLUGIN_DIR", "")),
    )
    args = parser.parse_args(argv)

    for name in ("artifact_id", "artifact_path", "seed"):
        if not getattr(args, name):
            env_name = "PREV_OUTPUT" if name == "seed" else name.upper()
            parser.error(f"--{name.replace('_', '-')} or ${env_name} required")
    if not args.plugin_dir:
        parser.error("--plugin-dir or $CLAUDE_PLUGIN_ROOT/$PLUGIN_DIR required")

    layer_type = args.layer.split("_", 1)[1]
    project_root = Path(args.artifact_path).parents[2]
    saga_dir = project_root / ".aidoc" / "review" / args.layer / args.artifact_id

    ctx = SagaContext(
        layer=args.layer,
        layer_type=layer_type,
        artifact_id=args.artifact_id,
        artifact_path=Path(args.artifact_path),
        saga_dir=saga_dir,
        saga_file=saga_dir / "saga.json",
        threshold=args.threshold,
        plugin_dir=Path(args.plugin_dir),
    )

    saga = load_or_init_saga(ctx, Path(args.seed))
    resume_from_partial_timeout(saga)
    write_saga(ctx, saga)

    while saga["status"] not in {"CLOSED", "ESCALATED"}:
        if check_break_circuit(ctx, saga):
            return 0

        phase = saga["current_phase"]
        brief = (
            f"Artifact {args.artifact_id} at {args.artifact_path}; "
            f"seed at {args.seed}; saga at {ctx.saga_file}; "
            f"iteration {saga['iteration']}"
        )
        rc = dispatch_phase(ctx, phase, brief)

        if rc == 0:
            _advance_after_phase(ctx, saga, phase)
        else:
            saga["compensation_actions"].append(
                {
                    "ts": _utc_now_iso(),
                    "branch": "*",
                    "reason": f"phase {phase} subprocess exit {rc}",
                    "action": "escalate",
                }
            )
            append_transition(saga, from_state=saga["status"], to_state="ESCALATED", scope="run")
            saga["status"] = "ESCALATED"

        write_saga(ctx, saga)

    print(
        f"saga {saga['status']} for {ctx.artifact_id} "
        f"(iteration {saga['iteration']}, "
        f"{len(saga['transitions'])} transitions)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
