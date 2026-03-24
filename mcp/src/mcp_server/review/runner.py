from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from mcp_server.models.context_engineering_contracts import serialize_prompt_metadata_sidecar
from mcp_server.prompts import SourceSection, assemble_project_review_prompt, inspect_prompt_bundle


@dataclass(frozen=True)
class ReviewRunResult:
    prompt_text: str
    sidecar_json: str
    inspection: dict[str, object]
    prompt_path: Path | None
    sidecar_path: Path | None
    inspection_path: Path | None


def run_project_review_build(
    *,
    project_root: Path,
    persona: str,
    doc_type: str,
    template_name: str,
    sections: list[SourceSection],
    output_dir: Path | None = None,
) -> ReviewRunResult:
    assembly = assemble_project_review_prompt(
        project_root=project_root,
        persona=persona,
        doc_type=doc_type,
        template_name=template_name,
        sections=sections,
    )
    inspection = inspect_prompt_bundle(assembly.bundle)
    sidecar_json = serialize_prompt_metadata_sidecar(assembly.bundle.metadata)

    prompt_path: Path | None = None
    sidecar_path: Path | None = None
    inspection_path: Path | None = None
    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        prompt_path = output_dir / "review_prompt.txt"
        sidecar_path = output_dir / "review_prompt_sidecar.json"
        inspection_path = output_dir / "review_prompt_inspection.json"

        prompt_path.write_text(assembly.prompt_text, encoding="utf-8")
        sidecar_path.write_text(sidecar_json, encoding="utf-8")
        inspection_path.write_text(json.dumps(inspection, sort_keys=True), encoding="utf-8")

    return ReviewRunResult(
        prompt_text=assembly.prompt_text,
        sidecar_json=sidecar_json,
        inspection=inspection,
        prompt_path=prompt_path,
        sidecar_path=sidecar_path,
        inspection_path=inspection_path,
    )
