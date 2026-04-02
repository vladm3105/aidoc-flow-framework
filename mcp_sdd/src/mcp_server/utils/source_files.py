"""Shared source file collection for validation, consistency, and remediation runners."""

from __future__ import annotations

import re
from pathlib import Path

# Pattern for SDD source artifacts: TYPE-NN_slug.ext
_SOURCE_PATTERN = re.compile(r"^[A-Z]+-\d+_.+\.(md|yaml|yml)$")

# Stems and name substrings that mark derived / non-source files
_DERIVED_STEMS = ("_validation", "_remediated")
_EXCLUDED_NAMES = ("TEMPLATE", "REVIEW", "REPORT")


def _is_excluded(path: Path) -> bool:
    """Return True if *path* is a derived copy or non-source artifact."""
    stem_lower = path.stem.lower()
    name_upper = path.name.upper()
    if any(tag in stem_lower for tag in _DERIVED_STEMS):
        return True
    return any(tag in name_upper for tag in _EXCLUDED_NAMES)


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


def is_yaml_document(path: Path) -> bool:
    """Check if a path is a YAML document file."""
    return path.suffix.lower() in (".yaml", ".yml")
