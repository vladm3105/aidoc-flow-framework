"""Shared utility helpers for ucx_kb modules."""

from pathlib import Path


def is_real_document(file_path: str, include_archived: bool = False) -> bool:
    """Heuristic check to skip non-canonical files during ingestion."""
    p = Path(file_path)
    if not p.exists() or not p.is_file():
        return False

    lower_path = str(p).lower()
    excluded_substrings = ("template", "example", "fixtures", "__pycache__", ".git/")
    if any(token in lower_path for token in excluded_substrings):
        return False

    if "_legacy" in p.stem.lower():
        return False

    if include_archived:
        return True

    excluded_segments = {"archive", "archived"}
    for segment in (part.lower() for part in p.parts):
        if segment in excluded_segments:
            return False
        if segment.endswith("_archive"):
            return False

    return True
