from __future__ import annotations

import json
from dataclasses import asdict, replace
from pathlib import Path

from .saga_models import (
    SagaBranchState,
    SagaRunState,
    can_transition,
)


def _read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")


def _to_run_state(payload: dict[str, object]) -> SagaRunState:
    raw_branches = payload.get("branches", {})
    branches: dict[str, SagaBranchState] = {}
    if isinstance(raw_branches, dict):
        for key, value in raw_branches.items():
            if isinstance(value, dict):
                branches[key] = SagaBranchState(**value)
    return SagaRunState(
        review_run_id=str(payload.get("review_run_id", "")),
        document_path=str(payload.get("document_path", "")),
        document_fingerprint=str(payload.get("document_fingerprint", "")),
        personas_requested=list(payload.get("personas_requested", [])),
        status=str(payload.get("status", "PREPARED")),
        created_at=str(payload.get("created_at", "")),
        updated_at=str(payload.get("updated_at", "")),
        retry_count=int(payload.get("retry_count", 0)),
        branches=branches,
        compensation_actions=list(payload.get("compensation_actions", [])),
    )


def create_saga_journal(*, output_dir: Path, run: SagaRunState) -> Path:
    journal_path = output_dir / f"{run.review_run_id}_saga_journal_v001.json"
    _write_json(journal_path, asdict(run))
    return journal_path


def load_saga_journal(*, journal_path: Path) -> SagaRunState:
    return _to_run_state(_read_json(journal_path))


def append_compensation_event(
    *,
    journal_path: Path,
    action: dict[str, object],
) -> SagaRunState:
    run = load_saga_journal(journal_path=journal_path)
    actions = [*run.compensation_actions, action]
    updated = replace(run, compensation_actions=actions)
    _write_json(journal_path, asdict(updated))
    return updated


def update_run_status(*, journal_path: Path, target: str) -> SagaRunState:
    run = load_saga_journal(journal_path=journal_path)
    if not can_transition(current=run.status, target=target):
        raise ValueError(f"Invalid saga transition: {run.status} -> {target}")
    updated = replace(run, status=target)
    _write_json(journal_path, asdict(updated))
    return updated


def set_branch_state(
    *,
    journal_path: Path,
    branch: SagaBranchState,
) -> SagaRunState:
    run = load_saga_journal(journal_path=journal_path)
    branches = dict(run.branches)
    branches[branch.branch_id] = branch
    updated = replace(run, branches=branches)
    _write_json(journal_path, asdict(updated))
    return updated
