from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from mcp_server.models.context_engineering_contracts import serialize_prompt_metadata_sidecar
from mcp_server.prompts import (
    SourceSection,
    assemble_project_creation_prompt,
    assemble_project_review_prompt,
    inspect_prompt_bundle,
)
from mcp_server.review.section_hygiene import strip_author_self_claim


@dataclass(frozen=True)
class ReviewRunResult:
    prompt_text: str
    sidecar_json: str
    inspection: dict[str, object]
    layer_asset_names: list[str]
    prompt_path: Path | None
    sidecar_path: Path | None
    inspection_path: Path | None


def run_project_review_build(
    *,
    project_root: Path,
    personas: list[str] | None = None,
    doc_type: str,
    template_name: str,
    sections: list[SourceSection],
    layer: str | None = None,
    output_dir: Path | None = None,
    playbook_text: str | None = None,
) -> ReviewRunResult:
    # REVIEW_TEAM.md §Strip author self-claim (MUST, both team + single_pass): the
    # shared builder is the single chokepoint every review-lens prompt flows through
    # (saga branches/aggregate, MCP prompt_only, CLI single_pass), so strip here.
    sections = strip_author_self_claim(sections)
    assembly = assemble_project_review_prompt(
        project_root=project_root,
        personas=personas,
        doc_type=doc_type,
        template_name=template_name,
        sections=sections,
        layer=layer,
        playbook_text=playbook_text,
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
        layer_asset_names=[
            item.removeprefix("### Layer asset: ").strip()
            for item in assembly.prompt_text.splitlines()
            if item.startswith("### Layer asset: ")
        ],
        prompt_path=prompt_path,
        sidecar_path=sidecar_path,
        inspection_path=inspection_path,
    )


@dataclass(frozen=True)
class CreationRunResult:
    prompt_text: str
    sidecar_json: str
    inspection: dict[str, object]
    layer_asset_names: list[str]
    layer_assets: dict[str, str]
    document_template_text: str | None
    prompt_path: Path | None
    sidecar_path: Path | None
    inspection_path: Path | None


@dataclass(frozen=True)
class CreationArtifactResult:
    target_path: Path
    template_source: str
    prompt_path: Path | None
    sidecar_path: Path | None
    inspection_path: Path | None


def run_project_creation_build(
    *,
    project_root: Path,
    personas: list[str] | None = None,
    doc_type: str,
    layer: str,
    template_name: str,
    sections: list[SourceSection] | None = None,
    output_dir: Path | None = None,
) -> CreationRunResult:
    assembly = assemble_project_creation_prompt(
        project_root=project_root,
        personas=personas,
        doc_type=doc_type,
        layer=layer,
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
        prompt_path = output_dir / "creation_prompt.txt"
        sidecar_path = output_dir / "creation_prompt_sidecar.json"
        inspection_path = output_dir / "creation_prompt_inspection.json"

        prompt_path.write_text(assembly.prompt_text, encoding="utf-8")
        sidecar_path.write_text(sidecar_json, encoding="utf-8")
        inspection_path.write_text(json.dumps(inspection, sort_keys=True), encoding="utf-8")

    return CreationRunResult(
        prompt_text=assembly.prompt_text,
        sidecar_json=sidecar_json,
        inspection=inspection,
        layer_asset_names=sorted(assembly.layer_assets.keys()),
        layer_assets=dict(assembly.layer_assets),
        document_template_text=assembly.document_template_text,
        prompt_path=prompt_path,
        sidecar_path=sidecar_path,
        inspection_path=inspection_path,
    )


def run_project_creation_artifact(
    *,
    project_root: Path,
    personas: list[str] | None = None,
    doc_type: str,
    layer: str,
    template_name: str,
    target_path: Path,
    sections: list[SourceSection] | None = None,
    output_dir: Path | None = None,
    overwrite: bool = False,
) -> CreationArtifactResult:
    creation_result = run_project_creation_build(
        project_root=project_root,
        personas=personas,
        doc_type=doc_type,
        layer=layer,
        template_name=template_name,
        sections=sections,
        output_dir=output_dir,
    )

    target_path = target_path.expanduser().resolve()
    target_path.parent.mkdir(parents=True, exist_ok=True)
    if target_path.exists() and not overwrite:
        raise FileExistsError(f"Target document already exists: {target_path}")

    if creation_result.document_template_text:
        final_content = creation_result.document_template_text
        template_source = "project_template"
    else:
        template_name = next(
            (name for name in creation_result.layer_asset_names if "-TEMPLATE" in name),
            None,
        )
        if template_name is None:
            raise ValueError("No layer template asset found for final artifact creation")
        final_content = creation_result.layer_assets[template_name]
        template_source = f"layer_asset:{template_name}"

    target_path.write_text(final_content, encoding="utf-8")

    return CreationArtifactResult(
        target_path=target_path,
        template_source=template_source,
        prompt_path=creation_result.prompt_path,
        sidecar_path=creation_result.sidecar_path,
        inspection_path=creation_result.inspection_path,
    )
