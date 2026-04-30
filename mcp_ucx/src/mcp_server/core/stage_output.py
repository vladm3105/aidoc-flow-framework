from __future__ import annotations

from pathlib import Path


STAGE_OUTPUT_ROOT = ".ucx"
STAGE_CREATE = "creation"
STAGE_VALIDATE = "validate"
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
    """Resolve output directory for an MCP stage with document-folder defaults."""
    if stage not in SUPPORTED_STAGES:
        raise ValueError(f"Unsupported stage: {stage}")

    if output_dir is not None:
        if output_dir.name == STAGE_OUTPUT_ROOT:
            return output_dir / stage
        if output_dir.parent.name == STAGE_OUTPUT_ROOT:
            return output_dir
        return output_dir

    # Default: write artifacts into .ucx/{stage} under the document folder.
    if document_dir is not None:
        return document_dir / STAGE_OUTPUT_ROOT / stage

    # Fallback when no document context exists (for example, creation without sections).
    return project_root / "docs" / STAGE_OUTPUT_ROOT / stage
