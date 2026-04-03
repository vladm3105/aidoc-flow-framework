from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import shutil
from typing import Any

from mcp_server.reporting import build_action_id, build_finding_id
from mcp_server.utils.source_files import extract_doc_id


PLACEHOLDER_PATTERN = re.compile(r"\b(TODO|TBD|FIXME|XXX)\b", re.IGNORECASE)


def _priority_from_severity(severity: str) -> str:
    if severity == "tier1":
        return "P1"
    if severity == "tier2":
        return "P2"
    return "P3"


def _build_finding_entry(
    *,
    file_path: str,
    doc_type: str,
    layer: str,
    category: str,
    severity: str,
    message: str,
    recommended_action: str,
    finding_ids: set[str],
    action_ids: set[str],
) -> dict[str, Any]:
    priority = _priority_from_severity(severity)
    finding_id = build_finding_id(
        priority=priority,
        identity_fields={
            "file": file_path,
            "doc_type": doc_type,
            "layer": layer,
            "category": category,
            "severity": severity,
            "message": message,
            "recommended_action": recommended_action,
        },
        existing_ids=finding_ids,
    )
    finding_ids.add(finding_id)

    action_id = build_action_id(
        identity_fields={
            "file": file_path,
            "doc_type": doc_type,
            "layer": layer,
            "category": category,
            "recommended_action": recommended_action,
            "priority": priority,
        },
        existing_ids=action_ids,
    )
    action_ids.add(action_id)

    return {
        "finding_id": finding_id,
        "action_id": action_id,
        "priority": priority,
        "file": file_path,
        "category": category,
        "severity": severity,
        "message": message,
        "recommended_action": recommended_action,
    }


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
        if "_validated" not in path.stem
        and "_remediate_copy" not in path.stem
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


def _build_validate_fix_prompt(
    report: dict[str, object],
    validation_report_path: Path | None,
) -> str:
    """Build an actionable fix prompt that includes validation findings.

    Reads the validation report (JSON) and embeds errors/warnings in the
    prompt so the executor knows exactly what to fix in the derived copy.
    """
    lines = [
        "# Validate-Fix Task",
        "",
        f"**Document**: {report.get('document_path', '')}",
        f"**Doc type**: {report.get('doc_type', '')}",
        f"**Layer**: {report.get('layer', '')}",
        "",
    ]

    # Derived files to edit
    derived = report.get("derived_paths", [])
    if isinstance(derived, list) and derived:
        lines.append("## Files to Fix (derived copies — source is protected)")
        lines.append("")
        for path in derived:
            lines.append(f"- `{path}`")
        lines.append("")

    # Read and embed validation findings
    validation_data: dict[str, Any] = {}
    if validation_report_path and validation_report_path.exists():
        try:
            validation_data = json.loads(
                validation_report_path.read_text(encoding="utf-8")
            )
        except (json.JSONDecodeError, OSError):
            pass

    errors = validation_data.get("errors", [])
    warnings = validation_data.get("warnings", [])

    if errors or warnings:
        lines.append("## Validation Findings to Fix")
        lines.append("")

    if errors:
        lines.append(f"### Errors ({len(errors)})")
        lines.append("")
        for error in errors:
            lines.append(f"- {error}")
        lines.append("")

    if warnings:
        lines.append(f"### Warnings ({len(warnings)})")
        lines.append("")
        for warning in warnings:
            lines.append(f"- {warning}")
        lines.append("")

    # Document context from validation report
    passes = validation_data.get("passes", [])
    if passes:
        lines.append("## Validation Passes (context)")
        lines.append("")
        for p in passes:
            lines.append(f"- {p}")
        lines.append("")

    # Instructions
    lines.append("## Instructions")
    lines.append("")
    lines.append(
        "Fix the errors and warnings listed above in the derived copy file(s). "
        "Do NOT modify the original source document. "
        "Read the derived file, identify the root cause of each error, "
        "and apply targeted edits to resolve each finding."
    )
    lines.append("")
    lines.append("### Fix Strategy")
    lines.append("")
    lines.append(
        "1. **Read the derived file first** to understand the document structure."
    )
    lines.append(
        "2. **For phantom ID errors (SDD-XS-001)**: Find where the ID is "
        "referenced, then find the correct existing ID it should point to. "
        "Match by semantic role — read the context around the reference "
        "(e.g., story title, requirement description) and find the defined "
        "element whose meaning aligns. Do NOT create new elements; remap "
        "to existing IDs."
    )
    lines.append(
        "3. **For propagation warnings (BRD-XS-001)**: Add the missing "
        "technology/decision name to the referenced section text."
    )
    lines.append(
        "4. **For phase alignment errors (BRD-XS-002)**: Ensure phase "
        "names match between scope and implementation sections."
    )
    lines.append(
        "5. **For entity consistency warnings (BRD-XS-004)**: Either "
        "remove the stale entity from the executive summary or add it "
        "to the functional requirements."
    )
    lines.append("")
    lines.append(
        "After fixing, the derived file should pass `sdd_validate` "
        "with zero errors from the rules above."
    )
    lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _build_remediate_fix_prompt(
    report: dict[str, object],
    remediation_report_path: Path | None,
) -> str:
    """Build an actionable remediation-fix prompt with review findings.

    Reads the remediation report (JSON) and embeds findings in the prompt
    so the executor knows what to fix in the derived remediated copy.
    """
    lines = [
        "# Remediate-Fix Task",
        "",
        f"**Document**: {report.get('document_path', '')}",
        f"**Doc type**: {report.get('doc_type', '')}",
        f"**Layer**: {report.get('layer', '')}",
        "",
    ]

    derived = report.get("derived_paths", [])
    if isinstance(derived, list) and derived:
        lines.append("## Files to Fix (derived copies — source is protected)")
        lines.append("")
        for path in derived:
            lines.append(f"- `{path}`")
        lines.append("")

    # Read and embed remediation findings
    remediation_data: dict[str, Any] = {}
    if remediation_report_path and remediation_report_path.exists():
        try:
            remediation_data = json.loads(
                remediation_report_path.read_text(encoding="utf-8")
            )
        except (json.JSONDecodeError, OSError):
            pass

    findings = remediation_data.get("findings", [])
    if findings:
        lines.append(f"## Remediation Findings ({len(findings)})")
        lines.append("")
        for finding in findings:
            if not isinstance(finding, dict):
                continue
            severity = finding.get("severity", "unknown")
            message = finding.get("message", "")
            action = finding.get("recommended_action", "")
            file_path = finding.get("file_path", "")
            lines.append(f"- [{severity}] {message}")
            if action:
                lines.append(f"  Action: {action}")
            if file_path:
                lines.append(f"  File: {file_path}")
        lines.append("")

    lines.append("## Instructions")
    lines.append("")
    lines.append(
        "Fix the findings listed above in the derived copy file(s). "
        "Do NOT modify the original source document or the validation copy. "
        "Read the derived file, identify the root cause of each finding, "
        "and apply targeted edits to resolve each issue."
    )
    lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _get_required_yaml_keys(doc_type: str) -> list[str]:
    """Return minimum required top-level YAML keys per document type."""
    normalized = doc_type.strip().lower()
    common = ["metadata", "traceability"]
    specific: dict[str, list[str]] = {
        "brd": ["document_control", "executive_summary", "functional_requirements"],
        "prd": ["document_control", "features"],
        "ears": ["document_control", "requirements"],
        "spec": ["document_control", "implementation"],
    }
    return common + specific.get(normalized, ["document_control"])


def run_remediation_build(
    *,
    project_root: Path,
    doc_type: str,
    layer: str,
    document_path: Path,
    review_report: Path | None = None,
    output_dir: Path | None = None,
) -> RemediationRunResult:
    # Default output to the parent document folder per PLAN-017 convention.
    if output_dir is None:
        output_dir = document_path.parent if document_path.is_file() else document_path

    files = _collect_markdown_files(document_path)
    findings: list[dict[str, Any]] = []
    finding_ids: set[str] = set()
    action_ids: set[str] = set()

    for file_path in files:
        content = file_path.read_text(encoding="utf-8")
        # YAML documents (.yaml/.yml) are structured data — they don't use
        # markdown frontmatter delimiters.  Only check .md files.
        is_yaml_file = file_path.suffix.lower() in (".yaml", ".yml")
        if not is_yaml_file and not _has_frontmatter(content):
            findings.append(
                _build_finding_entry(
                    file_path=str(file_path),
                    doc_type=doc_type,
                    layer=layer,
                    category="frontmatter",
                    severity="tier1",
                    message="Missing YAML frontmatter",
                    recommended_action="add_frontmatter",
                    finding_ids=finding_ids,
                    action_ids=action_ids,
                )
            )
        if PLACEHOLDER_PATTERN.search(content):
            findings.append(
                _build_finding_entry(
                    file_path=str(file_path),
                    doc_type=doc_type,
                    layer=layer,
                    category="placeholder",
                    severity="tier2",
                    message="Contains placeholder tokens",
                    recommended_action="replace_placeholders",
                    finding_ids=finding_ids,
                    action_ids=action_ids,
                )
            )

    # YAML structure validation
    for file_path in files:
        if file_path.suffix.lower() not in (".yaml", ".yml"):
            continue
        try:
            import yaml as _yaml
            yaml_data = _yaml.safe_load(file_path.read_text(encoding="utf-8"))
        except Exception:
            findings.append(
                _build_finding_entry(
                    file_path=str(file_path),
                    doc_type=doc_type,
                    layer=layer,
                    category="yaml_parse",
                    severity="tier1",
                    message="YAML file failed to parse",
                    recommended_action="fix_yaml_syntax",
                    finding_ids=finding_ids,
                    action_ids=action_ids,
                )
            )
            continue

        if not isinstance(yaml_data, dict):
            continue

        # Check for required top-level keys based on doc_type
        required_keys = _get_required_yaml_keys(doc_type)
        for key in required_keys:
            if key not in yaml_data:
                findings.append(
                    _build_finding_entry(
                        file_path=str(file_path),
                        doc_type=doc_type,
                        layer=layer,
                        category="yaml_structure",
                        severity="tier2",
                        message=f"Missing required YAML section: {key}",
                        recommended_action=f"add_{key}_section",
                        finding_ids=finding_ids,
                        action_ids=action_ids,
                    )
                )

        # Check for empty sections
        for key, value in yaml_data.items():
            if key in ("id", "title") or key.startswith("_"):
                continue
            if value is None or value == {} or value == []:
                findings.append(
                    _build_finding_entry(
                        file_path=str(file_path),
                        doc_type=doc_type,
                        layer=layer,
                        category="yaml_structure",
                        severity="tier2",
                        message=f"Empty YAML section: {key}",
                        recommended_action=f"populate_{key}_section",
                        finding_ids=finding_ids,
                        action_ids=action_ids,
                    )
                )

        # Validate element ID format
        import re as _re
        _ID_PATTERN = _re.compile(r"^[A-Z]{2,8}\.\d{2,}\.[0-9a-f]{4,8}$")
        _bad_ids: list[str] = []
        def _check_ids(obj: object, path: str = "") -> None:
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if k == "id" and isinstance(v, str) and v.strip():
                        if not _ID_PATTERN.match(v) and not v.startswith("{"):  # skip template placeholders
                            _bad_ids.append(v)
                    _check_ids(v, f"{path}.{k}")
            elif isinstance(obj, list):
                for item in obj:
                    _check_ids(item, path)
        _check_ids(yaml_data)

        if _bad_ids:
            findings.append(
                _build_finding_entry(
                    file_path=str(file_path),
                    doc_type=doc_type,
                    layer=layer,
                    category="element_id",
                    severity="tier2",
                    message=f"Invalid element ID format ({len(_bad_ids)} found): {_bad_ids[:3]}",
                    recommended_action="fix_element_ids",
                    finding_ids=finding_ids,
                    action_ids=action_ids,
                )
            )

    _review_summary_data: dict[str, object] | None = None

    if review_report is not None and review_report.exists():
        from mcp_server.remediation.review_parser import parse_review_report
        review_summary, review_findings = parse_review_report(review_report)

        if review_findings:
            capped = review_findings[:50]
            for rf in capped:
                findings.append(
                    _build_finding_entry(
                        file_path=str(review_report),
                        doc_type=doc_type,
                        layer=layer,
                        category="review_finding",
                        severity=rf.severity,
                        message=rf.message,
                        recommended_action=rf.recommended_action,
                        finding_ids=finding_ids,
                        action_ids=action_ids,
                    )
                )
            if len(review_findings) > 50:
                findings.append(
                    _build_finding_entry(
                        file_path=str(review_report),
                        doc_type=doc_type,
                        layer=layer,
                        category="review_finding_overflow",
                        severity="tier2",
                        message=f"{len(review_findings) - 50} additional review findings not shown (see review report)",
                        recommended_action="review_full_report",
                        finding_ids=finding_ids,
                        action_ids=action_ids,
                    )
                )
            if review_summary:
                import dataclasses as _dc
                _review_summary_data = _dc.asdict(review_summary)
        else:
            # Fallback: parsing returned nothing, keep pointer
            findings.append(
                _build_finding_entry(
                    file_path=str(review_report),
                    doc_type=doc_type,
                    layer=layer,
                    category="review_report",
                    severity="tier2",
                    message="Review report linked for downstream manual remediation",
                    recommended_action="apply_review_findings",
                    finding_ids=finding_ids,
                    action_ids=action_ids,
                )
            )

    report: dict[str, object] = {
        "project_root": str(project_root),
        "document_path": str(document_path),
        "doc_type": doc_type,
        "layer": layer,
        "review_report": str(review_report) if review_report else None,
        "review_summary": _review_summary_data,
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
    doc_id = extract_doc_id(document_path)
    report_path, summary_path = _write_report_files(
        output_dir,
        f"{doc_id}.ucx.remediate.json",
        f"{doc_id}.ucx.remediate.txt",
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
    """Strip stage suffixes from stem."""
    stem = src.stem
    for postfix in ("_validated", "_remediate_copy"):
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


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _guard_source_integrity(source_paths: list[Path], operation: str, apply_fn: Any) -> tuple[list[Path], dict[str, object]]:
    snapshots: dict[Path, str] = {}
    for path in source_paths:
        if path.exists() and path.is_file():
            snapshots[path] = path.read_text(encoding="utf-8")

    derived_paths = apply_fn()

    restored_files: list[str] = []
    integrity_events: list[dict[str, str]] = []
    for path, original in snapshots.items():
        current = path.read_text(encoding="utf-8") if path.exists() else ""
        if current != original:
            path.write_text(original, encoding="utf-8")
            restored_files.append(str(path))
            integrity_events.append(
                {
                    "path": str(path),
                    "before_hash": _hash_text(original),
                    "after_hash": _hash_text(current),
                }
            )

    telemetry: dict[str, object] = {}
    if snapshots:
        telemetry = {
            "operation": operation,
            "source_protection_enabled": True,
            "source_files_monitored": [str(path) for path in snapshots],
            "restoration_events": len(restored_files),
            "restored_files": restored_files,
            "integrity_events": integrity_events,
            "guard_status": "restored" if restored_files else "clean",
        }
    return derived_paths, telemetry


def _resolve_source_document_path(document_path: Path) -> Path:
    if document_path.is_file():
        return document_path

    candidates = sorted(document_path.glob("*.md")) + sorted(document_path.glob("*.yaml"))
    filtered = [
        path
        for path in candidates
        if "REVIEW" not in path.name.upper() and "REPORT" not in path.name.upper()
    ]
    source_artifacts = [
        path
        for path in filtered
        if "_validated" not in path.stem
        and "_remediate_copy" not in path.stem
        and re.match(r"^[A-Z]+-\d+_.+\.(md|yaml)$", path.name)
    ]
    if len(source_artifacts) == 1:
        return source_artifacts[0]
    return document_path


def _resolve_validation_copy_path(document_path: Path) -> Path:
    """Find the _validated derived copy in a folder."""
    if document_path.is_file():
        return document_path
    candidates = []
    for ext in ("*.md", "*.yaml", "*.yml"):
        candidates.extend(
            path for path in sorted(document_path.glob(ext))
            if "_validated" in path.stem
            and re.match(r"^[A-Z]+-\d+_.+_validated\.", path.name)
        )
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

    source_paths = [effective_document_path] if effective_document_path.is_file() else []

    def _apply_copy() -> list[Path]:
        if effective_document_path.is_file():
            return [_copy_with_suffix(effective_document_path, "validated", output_dir)]
        return _copy_tree_with_suffix(effective_document_path, "validated", output_dir)

    derived_paths, telemetry = _guard_source_integrity(source_paths, "validate-fix", _apply_copy)

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
    if telemetry:
        report["source_protection_telemetry"] = telemetry

    report_json = json.dumps(report, sort_keys=True)
    report_text = _build_validate_fix_prompt(report, validation_report)
    doc_id = extract_doc_id(document_path)
    report_path, summary_path = _write_report_files(
        output_dir,
        f"{doc_id}.ucx.validate_fix.json",
        f"{doc_id}.ucx.validate_fix.txt",
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

    source_paths: list[Path] = []
    if effective_document_path.is_file():
        source_paths.append(effective_document_path)
        base_source = effective_document_path.parent / f"{_canonical_stem(effective_document_path)}.md"
        if base_source.exists() and base_source != effective_document_path:
            source_paths.append(base_source)

    def _apply_copy() -> list[Path]:
        if effective_document_path.is_file():
            return [_copy_with_canonical_suffix(effective_document_path, "remediate_copy", output_dir)]
        return _copy_tree_with_suffix(effective_document_path, "remediate_copy", output_dir)

    derived_paths, telemetry = _guard_source_integrity(source_paths, "remediate-fix", _apply_copy)

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
    if telemetry:
        report["source_protection_telemetry"] = telemetry

    report_json = json.dumps(report, sort_keys=True)
    report_text = _build_remediate_fix_prompt(report, remediation_report)
    doc_id = extract_doc_id(document_path)
    report_path, summary_path = _write_report_files(
        output_dir,
        f"{doc_id}.ucx.remediate_fix.json",
        f"{doc_id}.ucx.remediate_fix.txt",
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
