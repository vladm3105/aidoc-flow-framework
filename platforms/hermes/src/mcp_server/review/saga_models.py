from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


@dataclass(frozen=True)
class SagaBranchState:
    branch_id: str
    persona: str
    status: str = "BRANCH_RUNNING"
    attempt: int = 0
    started_at: str = field(default_factory=_utc_now_iso)
    ended_at: str | None = None
    error_code: str | None = None


@dataclass(frozen=True)
class SagaRunState:
    review_run_id: str
    document_path: str
    document_fingerprint: str
    personas_requested: list[str]
    status: str = "PREPARED"
    created_at: str = field(default_factory=_utc_now_iso)
    updated_at: str = field(default_factory=_utc_now_iso)
    retry_count: int = 0
    branches: dict[str, SagaBranchState] = field(default_factory=dict)
    compensation_actions: list[dict[str, object]] = field(default_factory=list)


_ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "PREPARED": {"FANOUT_STARTED"},
    "FANOUT_STARTED": {"BRANCH_RUNNING"},
    "BRANCH_RUNNING": {"BRANCH_COMPLETED", "BRANCH_FAILED"},
    "BRANCH_FAILED": {"BRANCH_COMPENSATING", "ESCALATED", "BRANCH_COMPLETED"},
    "BRANCH_COMPENSATING": {"BRANCH_RUNNING", "ESCALATED"},
    "BRANCH_COMPLETED": {"FANIN_REDUCED"},
    "FANIN_REDUCED": {"SYNTHESIZED"},
    "SYNTHESIZED": {"CLOSED"},
    "ESCALATED": set(),
    "CLOSED": set(),
}


def deterministic_review_run_id(
    *,
    document_path: Path | str,
    document_fingerprint: str,
    personas: list[str],
    time_bucket: str,
) -> str:
    normalized_path = str(Path(document_path).as_posix())
    persona_key = ",".join(sorted(personas))
    payload = f"{normalized_path}|{document_fingerprint}|{persona_key}|{time_bucket}"
    return sha256(payload.encode("utf-8")).hexdigest()[:16]


def deterministic_branch_id(*, review_run_id: str, persona: str) -> str:
    payload = f"{review_run_id}|{persona}"
    return sha256(payload.encode("utf-8")).hexdigest()[:12]


def can_transition(*, current: str, target: str) -> bool:
    return target in _ALLOWED_TRANSITIONS.get(current, set())


def transition_run_status(run: SagaRunState, *, target: str) -> SagaRunState:
    if not can_transition(current=run.status, target=target):
        raise ValueError(f"Invalid saga transition: {run.status} -> {target}")
    return replace(run, status=target, updated_at=_utc_now_iso())
