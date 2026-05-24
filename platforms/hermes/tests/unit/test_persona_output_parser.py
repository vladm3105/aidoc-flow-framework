from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp_server.review.persona_output_parser import parse_persona_output  # noqa: E402


def test_parse_persona_output_strict_json() -> None:
    raw = (
        '{"findings":[{"priority":"P1","category":"quality","message":"Use explicit retries",'
        '"recommended_action":"Add retry policy","target_layer":"spec"}]}'
    )
    result = parse_persona_output(
        output_text=raw,
        persona="architect",
        branch_id="b1",
        attempt=1,
        default_layer="spec",
    )

    assert result.parse_status == "strict_json"
    assert len(result.findings) == 1
    assert result.findings[0]["persona"] == "architect"
    assert result.findings[0]["branch_id"] == "b1"


def test_parse_persona_output_fallback_on_malformed() -> None:
    result = parse_persona_output(
        output_text="non-json response",
        persona="auditor",
        branch_id="b2",
        attempt=2,
        default_layer="01_BRD",
    )

    assert result.parse_status == "fallback"
    assert len(result.findings) == 1
    assert result.findings[0]["category"] == "parser"
    assert result.findings[0]["target_layer"] == "01_BRD"
