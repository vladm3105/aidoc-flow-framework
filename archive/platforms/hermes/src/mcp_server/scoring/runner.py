from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


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


def _extract_readiness_gate(report_payload: dict[str, object]) -> tuple[str | None, int | None]:
    doc_type_val = report_payload.get("doc_type")
    if not isinstance(doc_type_val, str):
        return None, None
    doc_type = doc_type_val.strip().lower()
    if doc_type not in {"tdd", "iplan"}:
        return doc_type, None

    field = "iplan_ready_score"

    # score field is resolved from document payload via validation messages, so inspect passes/warnings/errors text
    for bucket_name in ("passes", "warnings", "errors"):
        bucket = report_payload.get(bucket_name, [])
        if not isinstance(bucket, list):
            continue
        for item in bucket:
            if not isinstance(item, str):
                continue
            if f"{field}" in item:
                m = re.search(r"(\d+)\s*/\s*(\d+)", item)
                if m is not None:
                    return doc_type, int(m.group(1))

    return doc_type, None


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


# Framework-documented per-layer audit_threshold default (PROFILE-TEMPLATE.yaml).
# A profile audit_threshold value is raise-only: honored only when >= this default.
_FRAMEWORK_AUDIT_DEFAULT = 90


def _normalize_layer_key(layer: str) -> str:
    """`04_BDD` / `bdd` / `BDD` → `BDD` (the ADAPTATION_SURFACE layer vocabulary).

    Mirrors ``prompts.context_builder._normalize_layer_key`` (kept local to avoid a
    scoring→prompts dependency).
    """
    return layer.rsplit("_", 1)[-1].upper() if layer else layer


def _resolve_audit_threshold(audit_threshold: dict | None, doc_type: str | None) -> int | None:
    """Raise-only `audit_threshold` for the report's layer (HERMES-ADAPT-ENFORCE-001).

    Returns the profile's per-layer value ONLY when it is a real int
    >= the framework default (90); a missing map / missing key / malformed
    (non-int, or bool) / below-default value returns ``None`` so the gate is never
    weakened. `bool` is excluded explicitly because it is an `int` subclass.
    """
    if not audit_threshold or not doc_type:
        return None
    key = _normalize_layer_key(str(doc_type))
    raw = audit_threshold.get(key)
    if raw is None:
        return None
    if isinstance(raw, bool) or not isinstance(raw, int):
        # A misconfigured value is a config error worth signalling (mirrors the
        # profile.py coercers); a valid-but-below-default value is intentionally
        # silent (spec: "out of surface, ignored").
        logger.warning("profile.audit_threshold[%s] = %r is not an integer — ignoring", key, raw)
        return None
    if raw < _FRAMEWORK_AUDIT_DEFAULT:
        return None
    return raw


def validate_score(
    *,
    report_file: Path,
    threshold: int,
    audit_threshold: dict | None = None,
) -> ScoreValidateResult:
    payload = _load_report(report_file)
    show_result = show_score(report_file=report_file)

    doc_type, readiness_value = _extract_readiness_gate(payload)
    effective_threshold = threshold
    threshold_source = "caller"
    readiness_gate = None

    if doc_type in {"tdd", "iplan"}:
        # TDD/IPLAN carry a hard readiness gate (>= 90). Fail-closed by intent:
        # if the readiness score can't be extracted from the report
        # (readiness_value is None), the gate does NOT pass — a missing/unparseable
        # readiness signal is treated as "not ready", never silently waved through.
        if 90 > effective_threshold:
            effective_threshold = 90
            threshold_source = "readiness_floor"
        readiness_gate = {
            "doc_type": doc_type,
            "required_minimum": 90,
            "readiness_value": readiness_value,
            "gate_passed": readiness_value is not None and readiness_value >= 90,
        }

    # Raise-only profile audit_threshold (never weakens): a per-layer profile value
    # >= the framework default (90) can only push the gate UP.
    profile_threshold = _resolve_audit_threshold(audit_threshold, doc_type)
    if profile_threshold is not None and profile_threshold > effective_threshold:
        effective_threshold = profile_threshold
        threshold_source = "profile"

    passed = show_result.score >= effective_threshold
    if readiness_gate is not None and readiness_gate["gate_passed"] is False:
        passed = False

    return ScoreValidateResult(
        score=show_result.score,
        threshold=effective_threshold,
        passed=passed,
        payload={
            "report_file": str(report_file),
            "score": show_result.score,
            "threshold": effective_threshold,
            "threshold_source": threshold_source,
            "passed": passed,
            "requested_threshold": threshold,
            "readiness_gate": readiness_gate,
        },
    )


def compare_scores(
    *, baseline_report_file: Path, candidate_report_file: Path
) -> ScoreCompareResult:
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
