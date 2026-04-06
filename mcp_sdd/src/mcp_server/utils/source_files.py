"""Shared source file collection for validation, consistency, and remediation runners."""

from __future__ import annotations

import re
from pathlib import Path

# Pattern for SDD source artifacts: TYPE-NN_slug.ext
_SOURCE_PATTERN = re.compile(r"^[A-Z]+-\d+_.+\.(md|yaml|yml)$")

# Sub-framework code for mcp_sdd (UCX = Unified Context Framework)
UCX_SUB_CODE = "ucx"

# Report naming patterns (PLAN-021)
# Format: {DOC-ID}.{SUB}.{STAGE}.{FORMAT}
# SUB is always explicit: ucx, gov, kb
REPORT_PATTERN = re.compile(
    r"^[A-Z]+-\d+\."
    r"(?:ucx|gov|kb)\."
    r"(?:validate_fix|validate|review|remediate|remediate_fix|"
    r"consistency|links|prescreen|score)"
    r"(?:\.v\d+)?"
    r"\.(?:json|md|txt)$"
)

DERIVED_COPY_PATTERN = re.compile(
    r"^[A-Z]+-\d+_.+_(?:validated|remediate_copy)\.(?:md|yaml|yml)$"
)

# Stems and name substrings that mark derived / non-source files
_DERIVED_STEMS = ("_validated", "_remediate_copy")
_EXCLUDED_NAMES = ("TEMPLATE", "REVIEW", "REPORT")


def _is_excluded(path: Path) -> bool:
    """Return True if *path* is a derived copy or non-source artifact."""
    stem_lower = path.stem.lower()
    name_upper = path.name.upper()
    if any(tag in stem_lower for tag in _DERIVED_STEMS):
        return True
    if any(tag in name_upper for tag in _EXCLUDED_NAMES):
        return True
    if DERIVED_COPY_PATTERN.match(path.name):
        return True
    return False


def collect_source_files(
    document_path: Path,
    extensions: tuple[str, ...] = (".md", ".yaml", ".yml"),
) -> list[Path]:
    """Collect source document files, excluding templates and derived copies.

    Handles both file and directory inputs.

    Excludes:
    - *_validation.* (derived validation copies)
    - *_remediated.* (derived remediated copies)
    - *TEMPLATE* (template files)
    - *REVIEW* and *REPORT* in filename (review/audit artifacts)

    When a directory contains exactly one canonical source artifact
    (matching TYPE-NN_slug pattern), returns only that file.
    """
    if document_path.is_file():
        if document_path.suffix.lower() in extensions and not _is_excluded(document_path):
            return [document_path]
        return []

    # Directory mode
    candidates = [
        f
        for f in sorted(document_path.iterdir())
        if f.is_file()
        and f.suffix.lower() in extensions
        and not _is_excluded(f)
    ]

    canonical = [f for f in candidates if _SOURCE_PATTERN.match(f.name)]
    if len(canonical) == 1:
        return canonical

    return sorted(candidates)


def extract_doc_id(path: Path) -> str:
    """Extract document ID (e.g., 'BRD-03') from filename or parent folder.

    Handles:
    - BRD-03_security_compliance.yaml -> BRD-03
    - BRD-03_security_compliance/ (directory) -> BRD-03
    - BRD-03.validate.json (report) -> BRD-03
    """
    name = path.name if path.is_file() else path.name
    match = re.match(r"^([A-Z]+-\d+)", name)
    if match:
        return match.group(1)
    match = re.match(r"^([A-Z]+-\d+)", path.parent.name)
    return match.group(1) if match else "UNKNOWN"


def is_yaml_document(path: Path) -> bool:
    """Check if a path is a YAML document file."""
    return path.suffix.lower() in (".yaml", ".yml")
