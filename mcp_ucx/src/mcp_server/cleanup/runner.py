"""Stage artifact cleanup engine.

Prunes obsolete validation, review, and remediation artifacts from document
folders while keeping the latest N versions per artifact type.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from mcp_server.utils.source_files import REPORT_PATTERN

_REMEDIATE_VERSION_RE = re.compile(r"_remediate_v(\d+)")
_VERSIONED_REPORT_RE = re.compile(r"\.v(\d+)\.")
_SOURCE_PATTERN = re.compile(r"^[A-Z]+-\d+_.+\.(md|yaml|yml)$")


@dataclass
class CleanResult:
    """Result of a cleanup operation."""

    deleted: list[str] = field(default_factory=list)
    kept: list[str] = field(default_factory=list)
    dry_run: bool = True
    total_bytes_freed: int = 0


def _classify_stage(name: str) -> str | None:
    """Return the stage category for a file, or None if not a stage artifact."""
    if REPORT_PATTERN.match(name):
        if ".validate" in name:
            return "validate"
        if ".review." in name:
            return "review"
        if ".remediate" in name:
            return "remediate"
        if ".score" in name or ".prescreen" in name or ".consistency" in name or ".links" in name:
            return "validate"
    stem = Path(name).stem
    if "_validated" in stem:
        return "validate"
    if "_remediate_copy" in stem or _REMEDIATE_VERSION_RE.search(stem):
        return "remediate"
    return None


def _version_key(path: Path) -> int:
    """Extract version number for sorting. Higher = newer."""
    m = _REMEDIATE_VERSION_RE.search(path.stem)
    if m:
        return int(m.group(1))
    m = _VERSIONED_REPORT_RE.search(path.name)
    if m:
        return int(m.group(1))
    return 0


def _is_source_document(path: Path) -> bool:
    """Return True if path is a source document that must never be deleted."""
    if not _SOURCE_PATTERN.match(path.name):
        return False
    stem = path.stem
    if "_validated" in stem or "_remediate_copy" in stem or _REMEDIATE_VERSION_RE.search(stem):
        return False
    return True


def run_clean(
    document_path: Path,
    stages: list[str],
    keep: int = 1,
    dry_run: bool = True,
) -> CleanResult:
    """Remove obsolete stage artifacts, keeping the latest *keep* per category.

    Args:
        document_path: Document file or directory to clean.
        stages: Stage categories to clean. Use ["all"] for everything.
        keep: Number of latest versions to retain per artifact type.
        dry_run: If True, list files without deleting.
    """
    folder = document_path if document_path.is_dir() else document_path.parent
    if not folder.is_dir():
        return CleanResult(dry_run=dry_run)

    target_stages = set(stages)
    clean_all = "all" in target_stages

    # Group files by (stage, base_category)
    groups: dict[tuple[str, str], list[Path]] = {}
    for path in sorted(folder.iterdir()):
        if not path.is_file():
            continue
        if _is_source_document(path):
            continue

        stage = _classify_stage(path.name)
        if stage is None:
            continue
        if not clean_all and stage not in target_stages:
            continue

        # Sub-group: report vs derived copy
        stem = path.stem
        if REPORT_PATTERN.match(path.name):
            # Group reports by their stage+format (e.g. validate.json, validate.txt)
            suffix = path.suffix
            group_key = (stage, f"report{suffix}")
        elif "_remediate_copy" in stem:
            group_key = (stage, "legacy_copy")
        elif _REMEDIATE_VERSION_RE.search(stem):
            group_key = (stage, "versioned_copy")
        elif "_validated" in stem:
            group_key = (stage, "validated_copy")
        else:
            group_key = (stage, "other")

        groups.setdefault(group_key, []).append(path)

    result = CleanResult(dry_run=dry_run)

    for group_key, paths in groups.items():
        # Sort by version number (higher = newer), then by mtime as tiebreaker
        paths.sort(key=lambda p: (_version_key(p), p.stat().st_mtime))

        # Legacy copies: delete if versioned copies exist
        if group_key[1] == "legacy_copy":
            versioned_key = (group_key[0], "versioned_copy")
            if versioned_key in groups and groups[versioned_key]:
                for path in paths:
                    result.deleted.append(str(path))
                    if not dry_run:
                        size = path.stat().st_size
                        path.unlink()
                        result.total_bytes_freed += size
                continue

        # Keep the latest `keep` items, delete the rest
        to_keep = paths[-keep:] if keep > 0 else []
        to_delete = paths[:-keep] if keep > 0 else paths

        for path in to_keep:
            result.kept.append(str(path))
        for path in to_delete:
            result.deleted.append(str(path))
            if not dry_run:
                size = path.stat().st_size
                path.unlink()
                result.total_bytes_freed += size

    return result
