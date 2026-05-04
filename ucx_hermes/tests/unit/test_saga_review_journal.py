from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp_server.review.saga_journal import (  # noqa: E402
    create_saga_journal,
    load_saga_journal,
    update_run_status,
)
from mcp_server.review.saga_models import SagaRunState  # noqa: E402


def test_saga_journal_create_load_and_transition(tmp_path: Path) -> None:
    run = SagaRunState(
        review_run_id="run001",
        document_path="/tmp/doc.md",
        document_fingerprint="abc",
        personas_requested=["architect"],
    )
    journal_path = create_saga_journal(output_dir=tmp_path, run=run)
    loaded = load_saga_journal(journal_path=journal_path)
    assert loaded.review_run_id == "run001"
    assert loaded.status == "PREPARED"

    updated = update_run_status(journal_path=journal_path, target="FANOUT_STARTED")
    assert updated.status == "FANOUT_STARTED"


def test_saga_journal_rejects_invalid_transition(tmp_path: Path) -> None:
    run = SagaRunState(
        review_run_id="run002",
        document_path="/tmp/doc.md",
        document_fingerprint="xyz",
        personas_requested=["architect"],
    )
    journal_path = create_saga_journal(output_dir=tmp_path, run=run)
    try:
        update_run_status(journal_path=journal_path, target="CLOSED")
    except ValueError as exc:
        assert "Invalid saga transition" in str(exc)
    else:
        raise AssertionError("Expected invalid transition to raise ValueError")
