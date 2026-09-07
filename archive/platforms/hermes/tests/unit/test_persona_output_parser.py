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


def test_parser_captures_lens_score_location_id() -> None:
    raw = (
        '{"lens_score": 82, "findings":[{"priority":"P1","message":"x",'
        '"recommended_action":"y","location":"section 3","target_layer":"spec"}]}'
    )
    result = parse_persona_output(
        output_text=raw, persona="qa_lead", branch_id="b1", attempt=1, default_layer="spec"
    )
    assert result.lens_score == 82.0
    f = result.findings[0]
    assert f["location"] == "section 3"
    assert f["id"]  # stable id captured/derived


def test_parser_recommendation_alias_and_stable_id() -> None:
    raw = '{"findings":[{"priority":"P2","message":"gap","recommendation":"fix it"}]}'
    first = parse_persona_output(
        output_text=raw, persona="architect", branch_id="b1", attempt=1, default_layer="spec"
    )
    second = parse_persona_output(
        output_text=raw, persona="architect", branch_id="b9", attempt=2, default_layer="spec"
    )
    assert first.findings[0]["recommended_action"] == "fix it"
    # id is stable across runs (persona|location|message), independent of branch/attempt
    assert first.findings[0]["id"] == second.findings[0]["id"]
    assert first.lens_score is None  # absent -> None


def test_parser_invalid_lens_score_is_none() -> None:
    raw = '{"lens_score":"high","findings":[{"priority":"P3","message":"m"}]}'
    result = parse_persona_output(
        output_text=raw, persona="tech_lead", branch_id="b1", attempt=1, default_layer="spec"
    )
    assert result.lens_score is None


def test_fallback_finding_has_location_and_id() -> None:
    result = parse_persona_output(
        output_text="not json", persona="auditor", branch_id="b2", attempt=1, default_layer="spec"
    )
    assert result.parse_status == "fallback"
    assert result.findings[0]["location"] == ""
    assert result.findings[0]["id"]


def test_parser_clean_empty_preserves_score_and_rationale() -> None:
    # H-6.1 V1: a clean 100/0 output with a rationale is a successful empty result
    # (not a fallback P1); lens_score is preserved so the cap is reachable.
    raw = '{"lens_score": 100, "findings": [], "no_findings_rationale": "§2 examined, clean"}'
    result = parse_persona_output(
        output_text=raw, persona="auditor", branch_id="b1", attempt=1, default_layer="01_BRD"
    )
    assert result.parse_status != "fallback"
    assert result.findings == []
    assert result.lens_score == 100.0
    assert result.no_findings_rationale == "§2 examined, clean"


def test_parser_clean_empty_without_rationale_preserves_score() -> None:
    # H-6.1 V2: 100/0 with no rationale -> empty, score preserved, rationale None.
    raw = '{"lens_score": 100, "findings": []}'
    result = parse_persona_output(
        output_text=raw, persona="auditor", branch_id="b1", attempt=1, default_layer="01_BRD"
    )
    assert result.parse_status != "fallback"
    assert result.findings == []
    assert result.lens_score == 100.0
    assert result.no_findings_rationale is None


def test_parser_clean_empty_no_findings_key() -> None:
    # H-6.1 M2: valid dict with a score but no `findings` key -> clean-empty, not fallback.
    raw = '{"lens_score": 100}'
    result = parse_persona_output(
        output_text=raw, persona="auditor", branch_id="b1", attempt=1, default_layer="01_BRD"
    )
    assert result.parse_status != "fallback"
    assert result.findings == []
    assert result.lens_score == 100.0


def test_parser_no_score_no_findings_still_fallback() -> None:
    # H-6.1 V3: no lens_score AND no findings -> still the diagnostic fallback P1.
    raw = '{"summary": "looks fine"}'
    result = parse_persona_output(
        output_text=raw, persona="auditor", branch_id="b1", attempt=1, default_layer="01_BRD"
    )
    assert result.parse_status == "fallback"
    assert len(result.findings) == 1
    assert result.findings[0]["category"] == "parser"
