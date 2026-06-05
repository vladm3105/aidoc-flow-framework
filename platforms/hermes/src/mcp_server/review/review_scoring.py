"""Deterministic review scoring + coverage, conforming to the framework spec.

Implements the scoring/conflict/gate policy of
``framework/governance/REVIEW_TEAM.md`` over the per-layer crews in
``framework/governance/REVIEW_CREWS.yaml``:

- **Aggregate score** = the weighted average of the crew's ``lens_score``s using
  the per-layer persona weights (renormalised over the lenses that actually ran),
  **then capped**: an unresolved P0 ⇒ fail (0); an unresolved P1 ⇒ capped below
  the gate threshold.
- **Coverage** = which crew lenses ran vs. were expected; below the crew's quorum
  the result is flagged *low-confidence → human review*.

The numeric score is **advisory**; the deterministic gate (per ``REVIEW_TEAM.md``)
is the structural ``sdd_doc_lint`` floor **plus** "no unresolved P0/P1" — this
module computes the second component (``no_blocking``) and the advisory score, not
the structural floor.

The framework crews use engine-agnostic persona names (e.g.
``chaos_engineer``, ``security_engineer``, ``synthesizer``); Hermes' runtime
personas (``chaos_engineer``, ``chairperson``) are mapped to them here so a
Hermes review scores against the framework weights. As of framework spec 0.12.0
(CHAOS-SEC-SPLIT-001, D-0030) the framework public name ``chaos_engineer``
matches Hermes' runtime name — the prior translation layer is removed.
``security_engineer`` is the new first-class lens; Hermes runtime adopts the
identity binding for it.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import yaml

# Hermes runtime persona name -> framework REVIEW_CREWS persona name.
# Only non-identity mappings are listed; everything else maps to itself.
# `chaos_engineer` now maps identity-to-identity (framework spec 0.12.0).
FRAMEWORK_PERSONA_ALIASES: dict[str, str] = {
    "chairperson": "synthesizer",
}

_GATE_THRESHOLD_DEFAULT = 90.0
_QUORUM_DEFAULT = 0.5
_BLOCKING = {"P0", "P1"}


def canonical_persona(name: str) -> str:
    """Map a Hermes persona name to its framework REVIEW_CREWS name."""
    return FRAMEWORK_PERSONA_ALIASES.get(name, name)


def _default_crews_path() -> Path:
    # .../platforms/hermes/src/mcp_server/review/review_scoring.py
    #   parents[5] == repository root
    return Path(__file__).resolve().parents[5] / "framework" / "governance" / "REVIEW_CREWS.yaml"


@lru_cache(maxsize=8)
def _load_crews(crews_path: Path) -> dict[str, dict[str, int]]:
    data = yaml.safe_load(crews_path.read_text(encoding="utf-8"))
    crews = data.get("crews", {}) if isinstance(data, dict) else {}
    out: dict[str, dict[str, int]] = {}
    for layer, crew in crews.items():
        review = (crew or {}).get("review", {}) if isinstance(crew, dict) else {}
        out[str(layer).upper()] = {str(p): int(w) for p, w in review.items()}
    return out


def load_crew_weights(layer: str, crews_path: Path | None = None) -> dict[str, int]:
    """Return the ``{framework_persona: weight}`` review crew for a layer.

    ``layer`` accepts either the artifact prefix (``EARS``) or a doc-type
    (``ears``); it is matched case-insensitively against the crews file.
    """
    path = crews_path or _default_crews_path()
    crews = _load_crews(path)
    key = str(layer).upper()
    if key not in crews:
        raise KeyError(f"No review crew for layer {layer!r} in {path}")
    return dict(crews[key])


@dataclass(frozen=True)
class CoverageReport:
    expected: list[str]
    ran: list[str]
    missing: list[str]
    quorum: float
    coverage_ratio: float  # ran crew-weight / total crew-weight
    quorum_met: bool
    low_confidence: bool


@dataclass(frozen=True)
class ReviewScore:
    score: float  # advisory readiness score, 0-100 (weighted + capped)
    raw_weighted: float  # weighted average before capping
    has_unresolved_p0: bool
    has_unresolved_p1: bool
    no_blocking: bool  # the "no unresolved P0/P1" gate component (advisory floor)
    gate_threshold: float
    coverage: CoverageReport


def _is_unresolved_blocking(findings: list[dict[str, object]]) -> tuple[bool, bool]:
    has_p0 = False
    has_p1 = False
    for f in findings:
        if not isinstance(f, dict):
            continue
        if f.get("resolved") is True:
            continue
        priority = str(f.get("priority", "")).upper().strip()
        if priority == "P0":
            has_p0 = True
        elif priority == "P1":
            has_p1 = True
    return has_p0, has_p1


def score_review(
    *,
    layer: str,
    lens_scores: dict[str, float],
    findings: list[dict[str, object]],
    gate_threshold: float = _GATE_THRESHOLD_DEFAULT,
    quorum: float = _QUORUM_DEFAULT,
    crews_path: Path | None = None,
) -> ReviewScore:
    """Compute the deterministic weighted/capped score + coverage for a review.

    ``lens_scores`` maps persona name (Hermes or framework naming) to its
    ``lens_score`` (0-100). ``findings`` are the reduced findings; a finding
    counts as blocking unless it carries ``resolved: True``.
    """
    weights = load_crew_weights(layer, crews_path)
    total_weight = sum(weights.values())

    # Normalise lens-score keys to framework persona names; keep only crew members.
    canonical_scores: dict[str, float] = {}
    for name, value in lens_scores.items():
        cname = canonical_persona(name)
        if cname in weights:
            canonical_scores[cname] = float(value)

    expected = sorted(weights)
    ran = sorted(canonical_scores)
    missing = sorted(set(expected) - set(ran))

    ran_weight = sum(weights[p] for p in ran)
    raw_weighted = (
        sum(canonical_scores[p] * weights[p] for p in ran) / ran_weight if ran_weight else 0.0
    )

    has_p0, has_p1 = _is_unresolved_blocking(findings)
    if has_p0:
        score = 0.0
    elif has_p1:
        score = min(raw_weighted, gate_threshold - 1.0)
    else:
        score = raw_weighted

    coverage_ratio = (ran_weight / total_weight) if total_weight else 0.0
    quorum_met = coverage_ratio >= quorum
    coverage = CoverageReport(
        expected=expected,
        ran=ran,
        missing=missing,
        quorum=quorum,
        coverage_ratio=round(coverage_ratio, 4),
        quorum_met=quorum_met,
        low_confidence=not quorum_met,
    )

    return ReviewScore(
        score=round(score, 2),
        raw_weighted=round(raw_weighted, 2),
        has_unresolved_p0=has_p0,
        has_unresolved_p1=has_p1,
        no_blocking=not (has_p0 or has_p1),
        gate_threshold=gate_threshold,
        coverage=coverage,
    )
