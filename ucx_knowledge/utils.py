"""Shared utility helpers for ucx_knowledge modules."""

from pathlib import Path


def is_real_document(file_path: str) -> bool:
    """Heuristic check to skip templates/examples for ingestion."""
    p = Path(file_path)
    if not p.exists() or not p.is_file():
        return False
    s = str(p).lower()
    excluded = ["template", "example", "fixtures", "__pycache__", ".git/"]
    return not any(token in s for token in excluded)
