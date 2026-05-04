from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp_server.review.saga_reducer import reduce_persona_findings  # noqa: E402


def test_reduce_persona_findings_deduplicates_and_is_deterministic() -> None:
    records = [
        {
            "priority": "P1",
            "category": "quality",
            "persona": "architect",
            "message": "Add explicit retry policy",
            "target_layer": "spec",
            "recommended_action": "Define retry policy in section 7",
            "branch_id": "b1",
        },
        {
            "priority": "P1",
            "category": "quality",
            "persona": "auditor",
            "message": "Add explicit retry policy",
            "target_layer": "spec",
            "recommended_action": "Define retry policy in section 7",
            "branch_id": "b2",
        },
    ]

    first = reduce_persona_findings(records)
    second = reduce_persona_findings(records)

    assert len(first) == 1
    assert len(second) == 1
    assert first[0].finding_id == second[0].finding_id
    assert first[0].action_id == second[0].action_id
    assert first[0].personas == ["architect", "auditor"]
