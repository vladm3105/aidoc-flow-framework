from __future__ import annotations

import asyncio
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def test_lifecycle_pipeline_stops_on_saga_escalated_review(tmp_path: Path) -> None:
    import mcp_server.tool_registry as tr

    original = tr._dispatch
    branch_summary = tmp_path / "BRD-00_validation-fixed_saga_branch_summary_v001.json"
    branch_summary.write_text("{}", encoding="utf-8")

    async def mock_dispatch(name: str, arguments: dict):
        if name == "sdd_validate":
            return {"passed": True, "is_valid": True}
        if name == "sdd_review":
            return {
                "passed": False,
                "review_mode": "saga_parallel",
                "saga_status": "ESCALATED",
                "error": "Branch retries exhausted",
                "branch_summary_path": str(branch_summary),
                "reducer_summary_path": None,
                "synthesis_summary_path": None,
            }
        return {"passed": True}

    async def _run():
        tr._dispatch = mock_dispatch
        try:
            return await tr._handle_lifecycle_pipeline(
                {
                    "project": "/tmp/test",
                    "doc_type": "brd",
                    "layer": "01_BRD",
                    "document": "/tmp/test/docs/01_BRD/BRD-01/",
                    "review_mode": "saga_parallel",
                    "stages": ["validate", "review", "remediate"],
                }
            )
        finally:
            tr._dispatch = original

    payload = asyncio.get_event_loop().run_until_complete(_run())
    assert payload.get("_stopped_at") == "review"
    assert "Branch retries exhausted" in str(payload.get("_reason", ""))
    review_payload = payload.get("review", {})
    assert Path(review_payload["branch_summary_path"]).exists()


def test_lifecycle_pipeline_continues_on_saga_closed_review(tmp_path: Path) -> None:
    import mcp_server.tool_registry as tr

    original = tr._dispatch
    branch_summary = tmp_path / "BRD-00_validation-fixed_saga_branch_summary_v001.json"
    reducer_summary = tmp_path / "BRD-00_validation-fixed_saga_reducer_summary_v001.json"
    synthesis_summary = tmp_path / "BRD-00_validation-fixed_saga_synthesis_summary_v001.json"
    branch_summary.write_text("{}", encoding="utf-8")
    reducer_summary.write_text("{}", encoding="utf-8")
    synthesis_summary.write_text("{}", encoding="utf-8")

    async def mock_dispatch(name: str, arguments: dict):
        if name == "sdd_review":
            return {
                "passed": True,
                "review_mode": "saga_parallel",
                "saga_status": "CLOSED",
                "branch_summary_path": str(branch_summary),
                "reducer_summary_path": str(reducer_summary),
                "synthesis_summary_path": str(synthesis_summary),
            }
        return {"passed": True}

    async def _run():
        tr._dispatch = mock_dispatch
        try:
            return await tr._handle_lifecycle_pipeline(
                {
                    "project": "/tmp/test",
                    "doc_type": "brd",
                    "layer": "01_BRD",
                    "document": "/tmp/test/docs/01_BRD/BRD-01/",
                    "review_mode": "saga_parallel",
                    "stages": ["validate", "review", "remediate"],
                }
            )
        finally:
            tr._dispatch = original

    payload = asyncio.get_event_loop().run_until_complete(_run())
    assert "_stopped_at" not in payload
    assert "review" in payload.get("_completed_stages", [])
    assert "remediate" in payload.get("_completed_stages", [])
    review_payload = payload.get("review", {})
    assert Path(review_payload["branch_summary_path"]).exists()
    assert Path(review_payload["reducer_summary_path"]).exists()
    assert Path(review_payload["synthesis_summary_path"]).exists()
