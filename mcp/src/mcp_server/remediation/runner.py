from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
import shutil
from typing import Any


PLACEHOLDER_PATTERN = re.compile(r"\b(TODO|TBD|FIXME|XXX)\b", re.IGNORECASE)


@dataclass(frozen=True)
class RemediationRunResult:
    report: dict[str, object]
    report_json: str
    report_text: str
    report_path: Path | None
    summary_path: Path | None


@dataclass(frozen=True)
class ValidateFixRunResult:
    report: dict[str, object]
    report_json: str
    report_text: str
    derived_paths: list[Path]
    report_path: Path | None
    summary_path: Path | None


@dataclass(frozen=True)
class RemediateFixRunResult:
    report: dict[str, object]
    report_json: str
    report_text: str
    derived_paths: list[Path]
    report_path: Path | None
    summary_path: Path | None


def _collect_markdown_files(document_path: Path) -> list[Path]:
    if document_path.is_file():
        return [document_path]
    candidates = sorted(document_path.glob("*.md"))
    filtered = [
        path
        for path in candidates
        if "REVIEW" not in path.name.upper() and "REPORT" not in path.name.upper()
    ]
    source_artifacts = [
        path
        for path in filtered
        if "_validation" not in path.stem
        and "_remediated" not in path.stem
        and re.match(r"^[A-Z]+-\d+_.+\.md$", path.name)
    ]
    if len(source_artifacts) == 1:
        return source_artifacts
    return filtered


def _has_frontmatter(text: str) -> bool:
    return text.startswith("---\n") and "\n---" in text[4:]


def _write_report_files(output_dir: Path | None, json_name: str, txt_name: str, report_json: str, report_text: str) -> tuple[Path | None, Path | None]:
    if output_dir is None:
        return None, None
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / json_name
    summary_path = output_dir / txt_name
    report_path.write_text(report_json, encoding="utf-8")
    summary_path.write_text(report_text, encoding="utf-8")
    return report_path, summary_path


def _validate_optional_report_path(report_path: Path | None, label: str) -> None:
    if report_path is None:
        return
    if not report_path.exists() or not report_path.is_file():
        raise FileNotFoundError(f"Invalid {label} path: {report_path}")
    try:
        payload = json.loads(report_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid {label} JSON: {report_path}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"Invalid {label} payload type: {report_path}")


def _as_text(title: str, report: dict[str, object], detail_key: str) -> str:
    lines = [
        title,
        f"Document: {report.get('document_path', '')}",
        f"Doc type: {report.get('doc_type', '')}",
        f"Layer: {report.get('layer', '')}",
        "",
    ]
    items = report.get(detail_key, [])
    if isinstance(items, list) and items:
        lines.append("Items:")
        for item in items:
            lines.append(f"- {item}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def run_remediation_build(
    *,
    project_root: Path,
    doc_type: str,
    layer: str,
    document_path: Path,
    review_report: Path | None = None,
    output_dir: Path | None = None,
) -> RemediationRunResult:
    files = _collect_markdown_files(document_path)
    findings: list[dict[str, Any]] = []

    for file_path in files:
        content = file_path.read_text(encoding="utf-8")
        if not _has_frontmatter(content):
            findings.append(
                {
                    "file": str(file_path),
                    "category": "frontmatter",
                    "severity": "tier1",
                    "message": "Missing YAML frontmatter",
                    "recommended_action": "add_frontmatter",
                }
            )
        if PLACEHOLDER_PATTERN.search(content):
            findings.append(
                {
                    "file": str(file_path),
                    "category": "placeholder",
                    "severity": "tier2",
                    "message": "Contains placeholder tokens",
                    "recommended_action": "replace_placeholders",
                }
            )

    if review_report is not None and review_report.exists():
        findings.append(
            {
                "file": str(review_report),
                "category": "review_report",
                "severity": "tier2",
                "message": "Review report linked for downstream manual remediation",
                "recommended_action": "apply_review_findings",
            }
        )

    report: dict[str, object] = {
        "project_root": str(project_root),
        "document_path": str(document_path),
        "doc_type": doc_type,
        "layer": layer,
        "review_report": str(review_report) if review_report else None,
        "files_checked": [str(path) for path in files],
        "findings": findings,
        "summary": {
            "total_findings": len(findings),
            "tier1_findings": sum(1 for item in findings if item["severity"] == "tier1"),
            "tier2_findings": sum(1 for item in findings if item["severity"] == "tier2"),
        },
    }

    report_json = json.dumps(report, sort_keys=True)
    report_text = _as_text("MCP Remediation Report", report, "findings")
    report_path, summary_path = _write_report_files(
        output_dir,
        "remediation_report.json",
        "remediation_report.txt",
        report_json,
        report_text,
    )

    return RemediationRunResult(
        report=report,
        report_json=report_json,
        report_text=report_text,
        report_path=report_path,
        summary_path=summary_path,
    )


def _canonical_stem(src: Path) -> str:
    """Strip UCX stage suffixes (_validation, _remediated) from stem."""
    stem = src.stem
    for postfix in ("_validation", "_remediated"):
        if stem.endswith(postfix):
            return stem[: -len(postfix)]
    return stem


def _copy_with_suffix(src: Path, suffix: str, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / f"{src.stem}_{suffix}{src.suffix}"
    target.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    return target


def _copy_with_canonical_suffix(src: Path, suffix: str, output_dir: Path) -> Path:
    """Copy src to output_dir using the canonical base stem (stripping stage postfixes)."""
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / f"{_canonical_stem(src)}_{suffix}{src.suffix}"
    target.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    return target


def _copy_tree_with_suffix(src_dir: Path, suffix: str, output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    target_root = output_dir / f"{src_dir.name}_{suffix}"
    if target_root.exists():
        shutil.rmtree(target_root)
    target_root.mkdir(parents=True, exist_ok=True)

    copied: list[Path] = []
    for src in sorted(src_dir.glob("*.md")):
        dst = target_root / src.name
        dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        copied.append(dst)
    return copied


def _resolve_source_document_path(document_path: Path) -> Path:
    if document_path.is_file():
        return document_path

    candidates = sorted(document_path.glob("*.md"))
    filtered = [
        path
        for path in candidates
        if "REVIEW" not in path.name.upper() and "REPORT" not in path.name.upper()
    ]
    source_artifacts = [
        path
        for path in filtered
        if "_validation" not in path.stem
        and "_remediated" not in path.stem
        and re.match(r"^[A-Z]+-\d+_.+\.md$", path.name)
    ]
    if len(source_artifacts) == 1:
        return source_artifacts[0]
    return document_path


def _resolve_validation_copy_path(document_path: Path) -> Path:
    """When given a folder, find the _validation derived copy; fallback to original path."""
    if document_path.is_file():
        return document_path
    candidates = [
        path
        for path in sorted(document_path.glob("*.md"))
        if path.stem.endswith("_validation")
        and re.match(r"^[A-Z]+-\d+_.+_validation\.md$", path.name)
    ]
    if len(candidates) == 1:
        return candidates[0]
    return document_path


def run_validate_fix_build(
    *,
    project_root: Path,
    doc_type: str,
    layer: str,
    document_path: Path,
    validation_report: Path | None = None,
    output_dir: Path | None = None,
) -> ValidateFixRunResult:
    _validate_optional_report_path(validation_report, "validation report")

    effective_document_path = _resolve_source_document_path(document_path)

    if output_dir is None:
        output_dir = effective_document_path.parent if effective_document_path.is_file() else document_path

    if effective_document_path.is_file():
        derived_paths = [_copy_with_suffix(effective_document_path, "validation", output_dir)]
    else:
        derived_paths = _copy_tree_with_suffix(effective_document_path, "validation", output_dir)

    report: dict[str, object] = {
        "project_root": str(project_root),
        "document_path": str(effective_document_path),
        "doc_type": doc_type,
        "layer": layer,
        "validation_report": str(validation_report) if validation_report else None,
        "derived_paths": [str(path) for path in derived_paths],
        "summary": {
            "derived_artifacts_created": len(derived_paths),
            "source_protected": True,
            "applied_changes": "none (copy-only deterministic baseline)",
        },
    }

    report_json = json.dumps(report, sort_keys=True)
    report_text = _as_text("MCP Validate-Fix Report", report, "derived_paths")
    report_path, summary_path = _write_report_files(
        output_dir,
        "validate_fix_report.json",
        "validate_fix_report.txt",
        report_json,
        report_text,
    )

    return ValidateFixRunResult(
        report=report,
        report_json=report_json,
        report_text=report_text,
        derived_paths=derived_paths,
        report_path=report_path,
        summary_path=summary_path,
    )


def run_remediate_fix_build(
    *,
    project_root: Path,
    doc_type: str,
    layer: str,
    document_path: Path,
    remediation_report: Path | None = None,
    output_dir: Path | None = None,
) -> RemediateFixRunResult:
    _validate_optional_report_path(remediation_report, "remediation report")

    effective_document_path = _resolve_validation_copy_path(document_path)

    if output_dir is None:
        output_dir = effective_document_path.parent if effective_document_path.is_file() else document_path

    if effective_document_path.is_file():
        derived_paths = [_copy_with_canonical_suffix(effective_document_path, "remediated", output_dir)]
    else:
        derived_paths = _copy_tree_with_suffix(effective_document_path, "remediated", output_dir)

    report: dict[str, object] = {
        "project_root": str(project_root),
        "document_path": str(effective_document_path),
        "doc_type": doc_type,
        "layer": layer,
        "remediation_report": str(remediation_report) if remediation_report else None,
        "derived_paths": [str(path) for path in derived_paths],
        "summary": {
            "derived_artifacts_created": len(derived_paths),
            "source_protected": True,
            "applied_changes": "none (copy-only deterministic baseline)",
        },
    }

    report_json = json.dumps(report, sort_keys=True)
    report_text = _as_text("MCP Remediate-Fix Report", report, "derived_paths")
    report_path, summary_path = _write_report_files(
        output_dir,
        "remediate_fix_report.json",
        "remediate_fix_report.txt",
        report_json,
        report_text,
    )

    return RemediateFixRunResult(
        report=report,
        report_json=report_json,
        report_text=report_text,
        derived_paths=derived_paths,
        report_path=report_path,
        summary_path=summary_path,
    )
