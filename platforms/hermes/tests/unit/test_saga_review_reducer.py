from __future__ import annotations

import sys
from pathlib import Path

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
    assert len(first[0].provenance) == 2


def test_reduce_persona_findings_uses_priority_and_tie_break_rules() -> None:
    records = [
        {
            "priority": "P2",
            "category": "zeta",
            "persona": "architect",
            "message": "Missing control boundary",
            "target_layer": "spec",
            "recommended_action": "Define explicit control boundary",
            "branch_id": "branch-b",
            "parse_status": "strict_json",
        },
        {
            "priority": "P1",
            "category": "alpha",
            "persona": "auditor",
            "message": "Missing control boundary",
            "target_layer": "spec",
            "recommended_action": "Define explicit control boundary",
            "branch_id": "branch-a",
            "parse_status": "structured_block",
        },
    ]

    reduced = reduce_persona_findings(records)
    assert len(reduced) == 1
    assert reduced[0].priority == "P1"
    assert reduced[0].category == "alpha"
    assert reduced[0].personas == ["architect", "auditor"]
    assert [p["branch_id"] for p in reduced[0].provenance] == ["branch-a", "branch-b"]
