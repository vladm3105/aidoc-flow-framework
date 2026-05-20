from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re

from mcp_server.utils.source_files import extract_doc_id


PLACEHOLDER_PATTERN = re.compile(r"\b(TODO|TBD|FIXME|XXX)\b", re.IGNORECASE)


@dataclass(frozen=True)
class PrescreenRunResult:
    report: dict[str, object]
    report_json: str
    report_text: str
    report_path: Path | None
    summary_path: Path | None


def _collect_document_files(document_path: Path) -> list[Path]:
    if document_path.is_file():
        return [document_path]
    return sorted(document_path.glob("*.md")) + sorted(document_path.glob("*.yaml")) + sorted(document_path.glob("*.yml"))


def run_prescreen(*, document_path: Path, output_dir: Path | None = None) -> PrescreenRunResult:
    files = _collect_document_files(document_path)
    candidates: list[dict[str, object]] = []

    for file_path in files:
        text = file_path.read_text(encoding="utf-8")
        is_yaml = file_path.suffix.lower() in (".yaml", ".yml")
        missing_frontmatter = False if is_yaml else not (text.startswith("---\n") and "\n---" in text[4:])
        has_placeholders = bool(PLACEHOLDER_PATTERN.search(text))
        flags = []
        if missing_frontmatter:
            flags.append("missing_frontmatter")
        if has_placeholders:
            flags.append("contains_placeholders")

        if flags:
            candidates.append(
                {
                    "file": str(file_path),
                    "flags": flags,
                    "priority": "high" if "missing_frontmatter" in flags else "medium",
                }
            )

    report: dict[str, object] = {
        "document_path": str(document_path),
        "candidates": candidates,
        "summary": {
            "files_scanned": len(files),
            "candidates_found": len(candidates),
            "high_priority": sum(1 for item in candidates if item["priority"] == "high"),
            "medium_priority": sum(1 for item in candidates if item["priority"] == "medium"),
        },
    }
    report_json = json.dumps(report, sort_keys=True)
    report_text = "MCP Prescreen Report\n" + report_json + "\n"

    report_path: Path | None = None
    summary_path: Path | None = None
    # Default output to the parent document folder per PLAN-017 convention.
    if output_dir is None:
        output_dir = document_path.parent if document_path.is_file() else document_path
    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        doc_id = extract_doc_id(document_path)
        report_path = output_dir / f"{doc_id}.ucx.prescreen.json"
        summary_path = output_dir / f"{doc_id}.ucx.prescreen.txt"
        report_path.write_text(report_json, encoding="utf-8")
        summary_path.write_text(report_text, encoding="utf-8")

    return PrescreenRunResult(
        report=report,
        report_json=report_json,
        report_text=report_text,
        report_path=report_path,
        summary_path=summary_path,
    )
