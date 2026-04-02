from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any, cast

import yaml  # type: ignore[import-untyped]

from mcp_server.utils.source_files import collect_source_files, extract_doc_id, is_yaml_document
from mcp_server.utils.template_naming import resolve_template_path
from mcp_server.validation.cross_section import (
    run_cross_section_checks,
    run_cross_section_checks_md,
)
from mcp_server.validation.brd_rules import (
    run_brd_cross_section_checks,
    run_brd_cross_section_checks_md,
)


@dataclass(frozen=True)
class ValidationRunResult:
    report: dict[str, object]
    report_json: str
    report_text: str
    is_valid: bool
    report_path: Path | None
    summary_path: Path | None


def _collect_markdown_files(document_path: Path) -> list[Path]:
    if document_path.is_file():
        source_artifacts = [
            path
            for path in sorted(document_path.parent.glob("*.md"))
            if "REVIEW" not in path.name.upper()
            and "REPORT" not in path.name.upper()
            and "_validate_copy" not in path.stem
            and "_remediate_copy" not in path.stem
            and re.match(r"^[A-Z]+-\d+_.+\.md$", path.name)
        ]
        if len(source_artifacts) == 1:
            source_path = source_artifacts[0]
            # When a canonical monolithic source is present, validate that source only.
            if document_path != source_path and document_path.suffix.lower() == ".md":
                return [source_path]
        return [document_path]

    candidates = sorted(document_path.glob("*.md"))
    filtered = [
        path
        for path in candidates
        if "REVIEW" not in path.name.upper() and "REPORT" not in path.name.upper()
    ]

    # Prefer canonical source artifact when present:
    # <DOC-ID>_<slug>.md and exclude derived variants like *_validate_copy.md/*_remediate_copy.md.
    source_artifacts = [
        path
        for path in filtered
        if "_validate_copy" not in path.stem
        and "_remediate_copy" not in path.stem
        and re.match(r"^[A-Z]+-\d+_.+\.md$", path.name)
    ]
    if len(source_artifacts) == 1:
        return source_artifacts

    return filtered


def _collect_yaml_files(document_path: Path) -> list[Path]:
    """Collect YAML document files, excluding templates and derived copies."""
    if document_path.is_file() and document_path.suffix.lower() in (".yaml", ".yml"):
        if "TEMPLATE" not in document_path.name.upper():
            return [document_path]
        return []
    if not document_path.is_dir():
        return []
    candidates = sorted(document_path.glob("*.yaml"))
    source_artifacts = [
        path
        for path in candidates
        if re.match(r"^[A-Z]+-\d+_.+\.yaml$", path.name)
        and "TEMPLATE" not in path.name.upper()
        and "_validate_copy" not in path.stem
        and "_remediate_copy" not in path.stem
    ]
    if len(source_artifacts) == 1:
        return source_artifacts
    return [
        path
        for path in candidates
        if re.match(r"^[A-Z]+-\d+_.+\.yaml$", path.name)
        and "TEMPLATE" not in path.name.upper()
        and "_validate_copy" not in path.stem
        and "_remediate_copy" not in path.stem
    ]


def _validate_yaml_metadata(
    yaml_data: dict[str, object],
    template: dict[str, object],
    errors: list[str],
    warnings: list[str],
    passes: list[str],
) -> None:
    """Validate YAML document metadata against template requirements."""
    metadata = yaml_data.get("metadata", {})
    if not isinstance(metadata, dict):
        warnings.append("YAML document missing metadata section")
        return

    # Tag validation
    tags = metadata.get("tags", [])
    tag_set = {t for t in tags if isinstance(t, str)} if isinstance(tags, list) else set()
    for required_tag in _extract_required_tags(template):
        if required_tag in tag_set:
            passes.append(f"required tag present: {required_tag}")
        else:
            errors.append(f"Missing required tag: {required_tag}")

    # Document type check
    doc_type_val = metadata.get("document_type")
    if isinstance(doc_type_val, str) and doc_type_val == "template":
        warnings.append(
            "document_type is 'template' — should be instance type (e.g., 'brd-document')"
        )


def _parse_frontmatter(content: str) -> dict[str, object]:
    if not content.startswith("---\n"):
        return {}
    end = content.find("\n---", 4)
    if end == -1:
        return {}

    raw = content[4:end]
    parsed = yaml.safe_load(raw)
    if isinstance(parsed, dict):
        return parsed
    return {}


def _resolve_canonical_template_root(project_root: Path) -> Path:
    project_local = project_root / "ai_dev_ssd_flow"
    if project_local.exists():
        return project_local

    framework_root = Path(__file__).resolve().parents[4]
    return framework_root / "ai_dev_ssd_flow"


def _load_layer_yaml_template(*, project_root: Path, layer: str) -> tuple[dict[str, object], str | None]:
    if "_" not in layer:
        return {}, f"Invalid layer format: {layer}. Expected format like 01_BRD"

    artifact = layer.split("_", 1)[1].strip().upper()
    template_root = _resolve_canonical_template_root(project_root)
    template_path = resolve_template_path(template_root / layer, artifact, ".yaml")
    if template_path is None:
        return {}, f"Missing canonical layer template in: {template_root / layer}"

    parsed = yaml.safe_load(template_path.read_text(encoding="utf-8"))
    if isinstance(parsed, dict):
        return parsed, None
    return {}, f"Invalid canonical layer template payload: {template_path}"


def _extract_required_custom_fields(schema: dict[str, object]) -> list[str]:
    metadata = schema.get("metadata", {})
    if not isinstance(metadata, dict):
        return []

    required = metadata.get("required_custom_fields", {})
    if not isinstance(required, dict):
        return []

    required_fields: list[str] = []
    for field_name, field_spec in required.items():
        if not isinstance(field_spec, dict):
            continue
        if field_spec.get("required", True):
            required_fields.append(field_name)
    return sorted(required_fields)


def _extract_required_tags(schema: dict[str, object]) -> list[str]:
    metadata = schema.get("metadata", {})
    if not isinstance(metadata, dict):
        return []
    tags = metadata.get("required_tags", [])
    if isinstance(tags, list):
        return [tag for tag in tags if isinstance(tag, str)]
    return []


def _extract_required_section_patterns(template: dict[str, object]) -> list[tuple[str, str]]:
    patterns: list[tuple[str, str]] = [("Title (H1)", r"^#\s+")]

    sections = template.get("sections", [])
    if not isinstance(sections, list):
        return patterns

    for item in sections:
        if not isinstance(item, dict):
            continue

        if item.get("required", True) is False:
            continue

        title = item.get("title")
        if not isinstance(title, str):
            continue

        number = item.get("number")
        escaped_title = re.escape(title.strip())
        if isinstance(number, int) or isinstance(number, str):
            escaped_number = re.escape(str(number).strip())
            pattern = rf"^##+\s*(?:{escaped_number}[.)]?\s*)?{escaped_title}\s*$"
            patterns.append((title, pattern))
            continue

        patterns.append((title, rf"^##+\s*{escaped_title}\s*$"))

    return patterns


def _build_text_report(report: dict[str, object]) -> str:
    summary_raw = report.get("summary", {})
    summary = summary_raw if isinstance(summary_raw, dict) else {}
    status = "PASSED" if bool(summary.get("is_valid", False)) else "FAILED"
    error_count = int(summary.get("errors", 0))
    warning_count = int(summary.get("warnings", 0))

    lines = [
        "MCP Validation Report",
        f"Document: {report['document_path']}",
        f"Layer: {report['layer']}",
        f"Status: {status}",
        f"Errors: {error_count}",
        f"Warnings: {warning_count}",
        "",
    ]

    errors_raw = report.get("errors", [])
    error_items = errors_raw if isinstance(errors_raw, list) else []
    if error_items:
        lines.append("Errors:")
        lines.extend(f"- {item}" for item in error_items)
        lines.append("")

    warnings_raw = report.get("warnings", [])
    warning_items = warnings_raw if isinstance(warnings_raw, list) else []
    if warning_items:
        lines.append("Warnings:")
        lines.extend(f"- {item}" for item in warning_items)
        lines.append("")

    passes_raw = report.get("passes", [])
    pass_items = passes_raw if isinstance(passes_raw, list) else []
    if pass_items:
        lines.append("Passes:")
        lines.extend(f"- {item}" for item in pass_items)
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _run_doc_type_parity_checks(*, doc_type: str, content: str, errors: list[str], passes: list[str]) -> None:
    normalized = doc_type.strip().lower()

    if normalized == "ears":
        # EARS parity requires a trigger clause and explicit system actor semantics.
        has_trigger = re.search(r"\b(WHEN|IF|WHILE)\b", content, re.IGNORECASE)
        has_actor_clause = re.search(r"\bTHE\s+SYSTEM\s+SHALL\b", content, re.IGNORECASE)
        if not has_trigger:
            errors.append("Missing EARS trigger clause: <WHEN|IF|WHILE>")
            return
        if not has_actor_clause:
            errors.append("Missing EARS actor clause: THE SYSTEM SHALL")
            return
        passes.append("ears syntax present: trigger + THE SYSTEM SHALL")
        return

    if normalized == "spec":
        # SPEC parity requires structured implementation content.
        if re.search(r"```yaml[\s\S]*?```", content, re.IGNORECASE):
            passes.append("spec structure present: fenced yaml block")
        else:
            errors.append("Missing SPEC structure: fenced yaml block (```yaml ... ```)")
        return

    if normalized == "tasks":
        # TASKS parity requires executable checklist items.
        if re.search(r"^\s*-\s*\[[ xX]\]\s+", content, re.MULTILINE):
            passes.append("tasks structure present: markdown checkbox list")
        else:
            errors.append("Missing TASKS structure: markdown checkbox list item")
        return

    if normalized == "ctr":
        # CTR parity requires explicit API or contract structure token.
        if re.search(r"\b(openapi\s*:|endpoint\b|contract\b)", content, re.IGNORECASE):
            passes.append("ctr structure present: contract token")
        else:
            errors.append("Missing CTR structure: openapi/endpoint/contract token")
        return


def run_project_validation_build(
    *,
    project_root: Path,
    doc_type: str,
    layer: str,
    document_path: Path,
    output_dir: Path | None = None,
) -> ValidationRunResult:
    template, template_error = _load_layer_yaml_template(project_root=project_root, layer=layer)

    errors: list[str] = []
    warnings: list[str] = []
    passes: list[str] = []
    files: list[Path] = []
    combined_content = ""

    if template_error is not None:
        errors.append(template_error)

    # --- YAML/MD decision fork ---
    # TODO: replace _collect_markdown_files with collect_source_files after full validation
    yaml_files = [f for f in collect_source_files(document_path, extensions=(".yaml", ".yml")) if is_yaml_document(f)]

    if yaml_files:
        # ===== YAML validation path =====
        files = yaml_files
        yaml_text = yaml_files[0].read_text(encoding="utf-8")
        yaml_data = yaml.safe_load(yaml_text)
        if not isinstance(yaml_data, dict):
            errors.append("YAML file did not parse to a mapping")
            yaml_data = {}
        else:
            passes.append(f"yaml_parsed: {yaml_files[0].name}")

        _validate_yaml_metadata(yaml_data, template, errors, warnings, passes)

        structural_error_count = len(errors)

        # Tier 1: Generic cross-section (all layers)
        run_cross_section_checks(
            yaml_data=yaml_data,
            doc_type=doc_type,
            errors=errors,
            warnings=warnings,
            passes=passes,
        )
        # Tier 2: Layer-specific cross-section
        if doc_type.strip().lower() == "brd":
            run_brd_cross_section_checks(
                yaml_data=yaml_data,
                errors=errors,
                warnings=warnings,
                passes=passes,
            )
        cross_section_error_count = len(errors) - structural_error_count
        combined_content = yaml_text
    else:
        # ===== Existing MD validation path (unchanged) =====
        files = _collect_markdown_files(document_path)

        if not files:
            errors.append("No markdown or YAML files found to validate")

        frontmatter: dict[str, object] = {}
        if files:
            frontmatter = _parse_frontmatter(files[0].read_text(encoding="utf-8"))
            if not frontmatter:
                errors.append("Missing or invalid YAML frontmatter")

        custom_fields_raw = frontmatter.get("custom_fields") if isinstance(frontmatter, dict) else None
        custom_fields: dict[str, Any]
        if custom_fields_raw is None:
            custom_fields = {}
        elif isinstance(custom_fields_raw, dict):
            custom_fields = cast(dict[str, Any], custom_fields_raw)
        else:
            errors.append("custom_fields must be a mapping")
            custom_fields = {}

        for field_name in _extract_required_custom_fields(template):
            if field_name in custom_fields:
                passes.append(f"custom_fields.{field_name} present")
            else:
                errors.append(f"Missing required custom field: custom_fields.{field_name}")

        tags_raw = frontmatter.get("tags") if isinstance(frontmatter, dict) else None
        tags: list[Any]
        if tags_raw is None:
            tags = []
        elif isinstance(tags_raw, list):
            tags = tags_raw
        else:
            errors.append("tags must be an array")
            tags = []

        tag_set = {tag for tag in tags if isinstance(tag, str)}
        for required_tag in _extract_required_tags(template):
            if required_tag in tag_set:
                passes.append(f"required tag present: {required_tag}")
            else:
                errors.append(f"Missing required tag: {required_tag}")

        combined_content = "\n\n".join(path.read_text(encoding="utf-8") for path in files) if files else ""
        for section_name, pattern in _extract_required_section_patterns(template):
            try:
                if re.search(pattern, combined_content, re.MULTILINE):
                    passes.append(f"required section present: {section_name}")
                else:
                    errors.append(f"Missing required section: {section_name}")
            except re.error:
                warnings.append(f"Skipped invalid schema regex for section: {section_name}")

        _run_doc_type_parity_checks(
            doc_type=doc_type,
            content=combined_content,
            errors=errors,
            passes=passes,
        )

        structural_error_count = len(errors)

        # Tier 1: Generic cross-section (degraded MD path)
        run_cross_section_checks_md(
            content=combined_content,
            doc_type=doc_type,
            errors=errors,
            warnings=warnings,
            passes=passes,
        )
        # Tier 2: Layer-specific (degraded MD path)
        if doc_type.strip().lower() == "brd":
            run_brd_cross_section_checks_md(
                content=combined_content,
                errors=errors,
                warnings=warnings,
                passes=passes,
            )
        cross_section_error_count = len(errors) - structural_error_count

    is_valid = len(errors) == 0
    report: dict[str, object] = {
        "document_path": str(document_path),
        "doc_type": doc_type,
        "layer": layer,
        "files_checked": [str(path) for path in files],
        "checks": {
            "required_custom_fields": _extract_required_custom_fields(template),
            "required_tags": _extract_required_tags(template),
            "required_sections": [name for name, _ in _extract_required_section_patterns(template)],
        },
        "errors": errors,
        "warnings": warnings,
        "passes": passes,
        "summary": {
            "errors": len(errors),
            "structural_errors": structural_error_count,
            "cross_section_errors": cross_section_error_count,
            "warnings": len(warnings),
            "passes": len(passes),
            "is_valid": is_valid,
        },
    }

    report_json = json.dumps(report, sort_keys=True)
    report_text = _build_text_report(report)

    report_path: Path | None = None
    summary_path: Path | None = None
    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        doc_id = extract_doc_id(document_path)
        report_path = output_dir / f"{doc_id}.ucx.validate.json"
        summary_path = output_dir / f"{doc_id}.ucx.validate.txt"
        report_path.write_text(report_json, encoding="utf-8")
        summary_path.write_text(report_text, encoding="utf-8")

    return ValidationRunResult(
        report=report,
        report_json=report_json,
        report_text=report_text,
        is_valid=is_valid,
        report_path=report_path,
        summary_path=summary_path,
    )
