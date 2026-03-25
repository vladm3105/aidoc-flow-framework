from __future__ import annotations

from pathlib import Path


STAGE_OUTPUT_ROOT = ".ucx_create"
STAGE_CREATE = "creation"
STAGE_VALIDATE = "validation"
STAGE_REVIEW = "review"
STAGE_REMEDIATE = "remediation"
SUPPORTED_STAGES = {
    STAGE_CREATE,
    STAGE_VALIDATE,
    STAGE_REVIEW,
    STAGE_REMEDIATE,
}


def resolve_stage_output_dir(
    *,
    stage: str,
    project_root: Path,
    output_dir: Path | None = None,
    document_dir: Path | None = None,
) -> Path:
    """Resolve output directory for an MCP stage with hidden per-doc defaults."""
    if stage not in SUPPORTED_STAGES:
        raise ValueError(f"Unsupported stage: {stage}")

    if output_dir is not None:
        if output_dir.name == STAGE_OUTPUT_ROOT:
            return output_dir / stage
        if output_dir.parent.name == STAGE_OUTPUT_ROOT:
            return output_dir
        return output_dir

    base_dir = document_dir if document_dir is not None else (project_root / "docs")
    return base_dir / STAGE_OUTPUT_ROOT / stage
