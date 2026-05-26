from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp_server.review.review_scoring import (  # noqa: E402
    canonical_persona,
    load_crew_weights,
    score_review,
)

# EARS crew (framework/governance/REVIEW_CREWS.yaml):
#   requirements_specialist 35, tech_lead 25, qa_lead 20, adversary 20  (sum 100)
_FULL_EARS = {
    "requirements_specialist": 100.0,
    "tech_lead": 100.0,
    "qa_lead": 100.0,
    "adversary": 100.0,
}


def test_persona_alias_maps_hermes_to_framework() -> None:
    assert canonical_persona("chaos_engineer") == "adversary"
    assert canonical_persona("chairperson") == "synthesizer"
    assert canonical_persona("tech_lead") == "tech_lead"


def test_crew_weights_load_and_sum_to_100() -> None:
    weights = load_crew_weights("ears")  # doc-type form, case-insensitive
    assert weights == load_crew_weights("EARS")
    assert sum(weights.values()) == 100
    assert "adversary" in weights


def test_full_crew_weighted_average() -> None:
    r = score_review(layer="EARS", lens_scores=_FULL_EARS, findings=[])
    assert r.score == 100.0
    assert r.raw_weighted == 100.0
    assert r.no_blocking is True
    assert r.coverage.missing == []
    assert r.coverage.coverage_ratio == 1.0
    assert r.coverage.quorum_met is True
    assert r.coverage.low_confidence is False


def test_hermes_persona_name_is_mapped_for_weighting() -> None:
    # chaos_engineer must count as the crew's `adversary` lens.
    scores = {
        "requirements_specialist": 100.0,
        "tech_lead": 100.0,
        "qa_lead": 100.0,
        "chaos_engineer": 100.0,
    }
    r = score_review(layer="EARS", lens_scores=scores, findings=[])
    assert "adversary" in r.coverage.ran
    assert r.coverage.missing == []
    assert r.score == 100.0


def test_unresolved_p0_fails() -> None:
    r = score_review(
        layer="EARS",
        lens_scores=_FULL_EARS,
        findings=[{"priority": "P0", "message": "blocking"}],
    )
    assert r.has_unresolved_p0 is True
    assert r.no_blocking is False
    assert r.score == 0.0


def test_unresolved_p1_capped_below_gate() -> None:
    r = score_review(
        layer="EARS",
        lens_scores=_FULL_EARS,
        findings=[{"priority": "P1", "message": "should fix"}],
        gate_threshold=90.0,
    )
    assert r.has_unresolved_p1 is True
    assert r.no_blocking is False
    assert r.score == 89.0  # min(100, 90 - 1)


def test_resolved_blocking_finding_does_not_block() -> None:
    r = score_review(
        layer="EARS",
        lens_scores=_FULL_EARS,
        findings=[{"priority": "P0", "resolved": True}],
    )
    assert r.has_unresolved_p0 is False
    assert r.no_blocking is True
    assert r.score == 100.0


def test_partial_crew_renormalises_and_flags_quorum() -> None:
    # requirements_specialist (35) + tech_lead (25) = 60/100 weight ran.
    r = score_review(
        layer="EARS",
        lens_scores={"requirements_specialist": 80.0, "tech_lead": 100.0},
        findings=[],
    )
    # weighted over the lenses that ran: (80*35 + 100*25) / 60
    assert r.raw_weighted == 88.33
    assert r.coverage.coverage_ratio == 0.6
    assert r.coverage.quorum_met is True
    assert set(r.coverage.missing) == {"qa_lead", "adversary"}


def test_below_quorum_is_low_confidence() -> None:
    # only requirements_specialist (35/100) ran -> 0.35 < 0.5 quorum
    r = score_review(
        layer="EARS",
        lens_scores={"requirements_specialist": 100.0},
        findings=[],
    )
    assert r.coverage.coverage_ratio == 0.35
    assert r.coverage.quorum_met is False
    assert r.coverage.low_confidence is True


def test_unknown_layer_raises() -> None:
    with pytest.raises(KeyError):
        score_review(layer="NOPE", lens_scores={}, findings=[])


def test_hermes_review_crews_cover_framework_crews() -> None:
    """Every framework review-crew persona is covered by the Hermes review mapping
    (after the framework<->Hermes alias). Locks the Phase-1 crew reconciliation."""
    import yaml
    from mcp_server.review.review_scoring import _default_crews_path, _load_crews

    crews = _load_crews(_default_crews_path())
    pm = yaml.safe_load((ROOT / "skills" / "persona_mappings.yaml").read_text(encoding="utf-8"))
    review = pm.get("review", {})

    for layer, weights in crews.items():
        expected = set(weights)
        doc_map = review.get(layer.lower(), {})
        hermes = doc_map.get("personas", []) if isinstance(doc_map, dict) else []
        mapped = {canonical_persona(p) for p in hermes}
        missing = expected - mapped
        assert missing == set(), f"{layer}: framework lenses not covered by Hermes crew: {missing}"
