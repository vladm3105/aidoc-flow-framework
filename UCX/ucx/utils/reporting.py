"""Reporting path and naming utilities for UCX standards."""

from __future__ import annotations

import re
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

import yaml

from ucx.models.enums import DocType


def extract_doc_id(doc_path: Path, doc_type: DocType) -> str:
    """Extract canonical document ID from a file/directory path."""
    name = doc_path.name if doc_path.is_dir() else doc_path.stem
    pattern = rf"({doc_type.value.upper()}-\d+)"
    match = re.search(pattern, name, re.IGNORECASE)
    if match:
        return match.group(1).upper()

    parent_name = doc_path.parent.name if doc_path.is_file() else name
    parent_match = re.search(pattern, parent_name, re.IGNORECASE)
    if parent_match:
        return parent_match.group(1).upper()

    return f"{doc_type.value.upper()}-XX"


def resolve_doc_id_strict(doc_path: Path, doc_type: DocType) -> str:
    """Resolve canonical document ID with hard-fail on path mismatches.

    Rules:
    - Directory paths must include `{DOC_TYPE}-NN` in folder name.
    - File paths may include ID in file stem and/or parent folder name.
    - If both file and parent provide IDs and they differ, raise ValueError.
    - If no ID can be resolved, raise ValueError.
    """
    token = doc_type.value.upper()
    pattern = re.compile(rf"({token}-\d+)", re.IGNORECASE)

    if doc_path.is_dir():
        match = pattern.search(doc_path.name)
        if not match:
            raise ValueError(
                f"Cannot resolve document ID from directory '{doc_path.name}' for type {token}"
            )
        return match.group(1).upper()

    stem_match = pattern.search(doc_path.stem)
    parent_match = pattern.search(doc_path.parent.name)

    stem_id = stem_match.group(1).upper() if stem_match else None
    parent_id = parent_match.group(1).upper() if parent_match else None

    if stem_id and parent_id and stem_id != parent_id:
        raise ValueError(
            f"Document ID mismatch: file '{stem_id}' != parent folder '{parent_id}'"
        )

    resolved = stem_id or parent_id
    if not resolved:
        raise ValueError(
            f"Cannot resolve document ID from file '{doc_path.name}' for type {token}"
        )
    return resolved


def report_filename(doc_id: str, report_kind: str, version: int) -> str:
    """Build canonical UCX report filename for a versioned report."""
    kind_map = {
        "validation": "UCX_validation_report",
        "review": "UCX_review_report",
        "remediation": "UCX_remediation_report",
    }
    if report_kind not in kind_map:
        raise ValueError(f"Unsupported report kind: {report_kind}")
    return f"{doc_id}.{kind_map[report_kind]}_v{version:03d}.md"


def next_report_version(search_dir: Path, doc_id: str, report_kind: str) -> int:
    """Return the next canonical UCX report version for a document."""
    kind_map = {
        "validation": "UCX_validation_report",
        "review": "UCX_review_report",
        "remediation": "UCX_remediation_report",
    }
    if report_kind not in kind_map:
        raise ValueError(f"Unsupported report kind: {report_kind}")

    prefix = kind_map[report_kind]
    pattern = re.compile(rf"^{re.escape(doc_id)}\.{prefix}_v(\d{{3}})\.md$")
    max_version = 0
    for file in search_dir.glob(f"{doc_id}.{prefix}_v*.md"):
        match = pattern.match(file.name)
        if match:
            max_version = max(max_version, int(match.group(1)))
    return max_version + 1


def ensure_report_schema(
    content: str,
    *,
    report_type: str,
    source_artifact_type: str,
    source_artifact_id: str,
    report_version: int,
    validator_or_reviewer: str,
) -> str:
    """Ensure markdown report has required UCX schema frontmatter fields."""
    fm: dict[str, Any]
    body = content

    match = re.match(r"\A---\n(.*?)\n---\n?(.*)\Z", content, re.DOTALL)
    if match:
        raw_fm = match.group(1)
        parsed = yaml.safe_load(raw_fm) or {}
        fm = parsed if isinstance(parsed, dict) else {}
        body = match.group(2)
    else:
        fm = {}

    fm.setdefault("title", f"UCX {report_type.title()} Report: {source_artifact_id}")
    fm.setdefault("tags", [f"ucx-{report_type}", "ucx-report"])
    if not isinstance(fm.get("tags"), list):
        fm["tags"] = [str(fm["tags"])]

    custom_fields = fm.get("custom_fields")
    if not isinstance(custom_fields, dict):
        custom_fields = {}

    custom_fields["report_type"] = report_type
    custom_fields["source_artifact_type"] = source_artifact_type.lower()
    custom_fields["source_artifact_id"] = source_artifact_id
    custom_fields.setdefault("status", "DRAFT")
    custom_fields["report_version"] = f"v{report_version:03d}"
    custom_fields["validator_or_reviewer"] = validator_or_reviewer
    custom_fields.setdefault("generated_at", datetime.now(UTC).isoformat())

    if report_type == "validation":
        custom_fields.setdefault("tier1_errors", 0)
        custom_fields.setdefault("tier1_warnings", 0)
        custom_fields.setdefault("tier2_warnings", 0)
        custom_fields.setdefault("checks_run", 0)
    elif report_type == "review":
        custom_fields.setdefault("weighted_score", 0.0)
        custom_fields.setdefault("p0_findings", 0)
        custom_fields.setdefault("p1_findings", 0)
        custom_fields.setdefault("p2_findings", 0)
        custom_fields.setdefault("personas_applied", 0)
    elif report_type == "remediation":
        custom_fields.setdefault("findings_addressed", 0)
        custom_fields.setdefault("changes_applied", 0)
        custom_fields.setdefault("remaining_findings", 0)

    fm["custom_fields"] = custom_fields
    fm_text = yaml.safe_dump(fm, sort_keys=False).strip()
    return f"---\n{fm_text}\n---\n\n{body.lstrip()}"
