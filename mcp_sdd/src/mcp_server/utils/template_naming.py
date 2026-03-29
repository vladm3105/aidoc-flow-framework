"""Resolution helpers for template naming migration.

Supports both unified naming ({ARTIFACT}-TEMPLATE.yaml) and legacy
naming ({ARTIFACT}-MVP-TEMPLATE.yaml) with new-name-first resolution.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable


def resolve_template_path(layer_dir: Path, artifact: str, suffix: str) -> Path | None:
    """Try unified name first, fall back to MVP name.

    Args:
        layer_dir: Directory containing template files (e.g., ai_dev_ssd_flow/01_BRD/)
        artifact: Artifact type uppercase (e.g., "BRD")
        suffix: File extension including dot (e.g., ".yaml")

    Returns:
        Path to template file, or None if neither naming convention found.
    """
    for pattern in (f"{artifact}-TEMPLATE{suffix}", f"{artifact}-MVP-TEMPLATE{suffix}"):
        path = layer_dir / pattern
        if path.exists():
            return path
    return None


def load_tuned_template(
    doc_type: str,
    loader_fn: Callable[..., str],
    **loader_kwargs: Any,
) -> str | None:
    """Try unified template name first, fall back to MVP name.

    Searches in order: .yaml (unified), .md (unified), .md (MVP legacy).

    Args:
        doc_type: Document type (e.g., "brd")
        loader_fn: Function that loads template by name (raises FileNotFoundError if missing)
        **loader_kwargs: Additional kwargs passed to loader_fn

    Returns:
        Template content string, or None if neither name exists.
    """
    for suffix in ("-TEMPLATE.yaml", "-TEMPLATE.md", "-MVP-TEMPLATE.md"):
        name = f"{doc_type.upper()}{suffix}"
        try:
            return loader_fn(template_name=name, **loader_kwargs)
        except FileNotFoundError:
            continue
    return None
