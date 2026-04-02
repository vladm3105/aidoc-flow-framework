from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path


@dataclass(frozen=True)
class ScoreShowResult:
    score: int
    summary: dict[str, int]
    payload: dict[str, object]

    @property
    def report(self) -> dict[str, object]:
        """Alias for payload (API consistency)."""
        return self.payload


@dataclass(frozen=True)
class ScoreValidateResult:
    score: int
    threshold: int
    passed: bool
    payload: dict[str, object]

    @property
    def report(self) -> dict[str, object]:
        """Alias for payload (API consistency)."""
        return self.payload

    @property
    def is_valid(self) -> bool:
        """Alias for passed (API consistency)."""
        return self.passed


@dataclass(frozen=True)
class ScoreCompareResult:
    baseline_score: int
    candidate_score: int
    delta: int
    payload: dict[str, object]

    @property
    def report(self) -> dict[str, object]:
        """Alias for payload (API consistency)."""
        return self.payload


def _derive_score(report_payload: dict[str, object]) -> tuple[int, dict[str, int]]:
    summary = report_payload.get("summary", {})

    if isinstance(summary, dict) and "structural_errors" in summary:
        # New categorized scoring
        structural = int(summary.get("structural_errors", 0) or 0)
        cross_section = int(summary.get("cross_section_errors", 0) or 0)
        warnings = int(summary.get("warnings", 0) or 0)
        score = max(0, 100 - (structural * 20) - (cross_section * 10) - (warnings * 5))
        return score, {
            "errors": structural + cross_section,
            "structural_errors": structural,
            "cross_section_errors": cross_section,
            "warnings": warnings,
        }

    # Backward compat: old reports without categories
    errors = 0
    warnings = 0
    if isinstance(summary, dict):
        errors = int(summary.get("errors", summary.get("error_count", 0)) or 0)
        warnings = int(summary.get("warnings", summary.get("warning_count", 0)) or 0)
    if errors == 0 and warnings == 0:
        top_errors = report_payload.get("errors", [])
        top_warnings = report_payload.get("warnings", [])
        if isinstance(top_errors, list):
            errors = len(top_errors)
        if isinstance(top_warnings, list):
            warnings = len(top_warnings)
    score = max(0, 100 - (errors * 20) - (warnings * 5))
    return score, {"errors": errors, "warnings": warnings}


def _load_report(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return {}
    return payload


def show_score(*, report_file: Path) -> ScoreShowResult:
    payload = _load_report(report_file)
    score, summary = _derive_score(payload)
    return ScoreShowResult(
        score=score,
        summary=summary,
        payload={
            "report_file": str(report_file),
            "score": score,
            "summary": summary,
        },
    )


def validate_score(*, report_file: Path, threshold: int) -> ScoreValidateResult:
    show_result = show_score(report_file=report_file)
    passed = show_result.score >= threshold
    return ScoreValidateResult(
        score=show_result.score,
        threshold=threshold,
        passed=passed,
        payload={
            "report_file": str(report_file),
            "score": show_result.score,
            "threshold": threshold,
            "passed": passed,
        },
    )


def compare_scores(*, baseline_report_file: Path, candidate_report_file: Path) -> ScoreCompareResult:
    baseline = show_score(report_file=baseline_report_file)
    candidate = show_score(report_file=candidate_report_file)
    delta = candidate.score - baseline.score
    return ScoreCompareResult(
        baseline_score=baseline.score,
        candidate_score=candidate.score,
        delta=delta,
        payload={
            "baseline_report_file": str(baseline_report_file),
            "candidate_report_file": str(candidate_report_file),
            "baseline_score": baseline.score,
            "candidate_score": candidate.score,
            "delta": delta,
        },
    )
