from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ScanRunResult:
    report: dict[str, object]
    report_json: str
    report_text: str
    report_path: Path | None
    summary_path: Path | None


def run_scan(*, report_file: Path, output_dir: Path | None = None) -> ScanRunResult:
    payload = json.loads(report_file.read_text(encoding="utf-8"))
    errors = payload.get("errors", []) if isinstance(payload, dict) else []
    warnings = payload.get("warnings", []) if isinstance(payload, dict) else []

    categories: dict[str, int] = {}
    for item in errors + warnings:
        if not isinstance(item, str):
            continue
        category = item.split(":", 1)[0].strip().lower() if ":" in item else "general"
        categories[category] = categories.get(category, 0) + 1

    report: dict[str, object] = {
        "report_file": str(report_file),
        "categories": categories,
        "summary": {
            "error_count": len(errors) if isinstance(errors, list) else 0,
            "warning_count": len(warnings) if isinstance(warnings, list) else 0,
            "category_count": len(categories),
        },
    }
    report_json = json.dumps(report, sort_keys=True)
    report_text = "MCP Scan Report\n" + report_json + "\n"

    report_path: Path | None = None
    summary_path: Path | None = None
    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        report_path = output_dir / "scan_report.json"
        summary_path = output_dir / "scan_report.txt"
        report_path.write_text(report_json, encoding="utf-8")
        summary_path.write_text(report_text, encoding="utf-8")

    return ScanRunResult(
        report=report,
        report_json=report_json,
        report_text=report_text,
        report_path=report_path,
        summary_path=summary_path,
    )
