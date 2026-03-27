from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re


SOURCE_PATTERN = re.compile(r"^[A-Z]+-\d+_.+\.md$")


@dataclass(frozen=True)
class ConsistencyRunResult:
    payload: dict[str, object]
    report_json: str
    report_text: str
    passed: bool
    report_path: Path | None
    summary_path: Path | None


def _render_text(payload: dict[str, object]) -> str:
    status = str(payload.get("status", "blocked")).upper()
    lines = [
        "MCP Consistency Report",
        f"Target: {payload.get('target_path')}",
        f"Status: {status}",
        "",
    ]

    errors = payload.get("errors", [])
    if isinstance(errors, list) and errors:
        lines.append("Errors:")
        lines.extend(f"- {item}" for item in errors if isinstance(item, str))
        lines.append("")

    warnings = payload.get("warnings", [])
    if isinstance(warnings, list) and warnings:
        lines.append("Warnings:")
        lines.extend(f"- {item}" for item in warnings if isinstance(item, str))
        lines.append("")

    details = payload.get("details", {})
    if isinstance(details, dict):
        lines.append("Details:")
        for key in sorted(details):
            lines.append(f"- {key}: {details[key]}")

    return "\n".join(lines).rstrip() + "\n"


def _resolve_source(folder: Path, target_path: Path) -> tuple[Path | None, list[str]]:
    if target_path.is_file():
        return target_path, []

    candidates = sorted(path for path in folder.glob("*.md") if SOURCE_PATTERN.match(path.name))
    candidates = [path for path in candidates if "_validation" not in path.stem and "_remediated" not in path.stem]
    if len(candidates) == 0:
        return None, ["missing_source_artifact"]
    if len(candidates) > 1:
        return None, ["ambiguous_source_artifact"]
    return candidates[0], []


def run_consistency_check(*, target_path: Path, output_dir: Path | None = None) -> ConsistencyRunResult:
    folder = target_path if target_path.is_dir() else target_path.parent
    source, source_errors = _resolve_source(folder=folder, target_path=target_path)

    errors: list[str] = list(source_errors)
    warnings: list[str] = []
    details: dict[str, object] = {
        "source": None,
        "validation_report": None,
        "validation_copy": None,
        "remediated_copy": None,
        "review_report": None,
        "remediation_report": None,
    }

    if source is not None:
        details["source"] = source.name
        stem = source.stem
        doc_id = stem.split("_", 1)[0] if "_" in stem else stem

        validation_report = folder / f"{doc_id}_validation_report.md"
        validation_copy = folder / f"{stem}_validation.md"
        remediated_copy = folder / f"{stem}_remediated.md"

        review_reports = sorted(folder.glob("*_review_report_v*.md")) + sorted(folder.glob(f"{doc_id}.R_review_report_v*.md"))
        remediation_reports = sorted(folder.glob("*_remediation_report_v*.md")) + sorted(folder.glob(f"{doc_id}.F_fix_report_v*.md"))

        details["validation_report"] = validation_report.name if validation_report.exists() else None
        details["validation_copy"] = validation_copy.name if validation_copy.exists() else None
        details["remediated_copy"] = remediated_copy.name if remediated_copy.exists() else None
        details["review_report"] = review_reports[-1].name if review_reports else None
        details["remediation_report"] = remediation_reports[-1].name if remediation_reports else None

        if validation_copy.exists() and not validation_report.exists():
            errors.append("validation_copy_without_validation_report")
        if remediated_copy.exists() and not validation_copy.exists():
            errors.append("remediated_copy_without_validation_copy")
        if remediated_copy.exists() and not remediation_reports:
            errors.append("remediated_copy_without_remediation_report")
        if validation_report.exists() and not validation_copy.exists():
            warnings.append("validation_report_without_validation_copy")

    passed = len(errors) == 0
    payload: dict[str, object] = {
        "status": "pass" if passed else "blocked",
        "target_path": str(target_path),
        "errors": errors,
        "warnings": warnings,
        "details": details,
    }

    report_json = json.dumps(payload, sort_keys=True)
    report_text = _render_text(payload)

    report_path: Path | None = None
    summary_path: Path | None = None
    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        report_path = output_dir / "consistency_report.json"
        summary_path = output_dir / "consistency_report.txt"
        report_path.write_text(report_json, encoding="utf-8")
        summary_path.write_text(report_text, encoding="utf-8")

    return ConsistencyRunResult(
        payload=payload,
        report_json=report_json,
        report_text=report_text,
        passed=passed,
        report_path=report_path,
        summary_path=summary_path,
    )
