from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp_server.models.context_engineering_contracts import (  # noqa: E402
    AppendixIndexEntry,
    RelevantSnippet,
    deterministic_fingerprint,
    serialize_prompt_metadata_sidecar,
)
from mcp_server.prompts import (  # noqa: E402
    ContractValidationError,
    SourceSection,
    assemble_project_review_prompt,
    build_prompt_bundle,
    inspect_prompt_bundle,
    map_sections_for_persona,
)



def test_build_prompt_bundle_emits_required_context_and_metadata() -> None:
    bundle = build_prompt_bundle(
        persona="architect",
        doc_type="brd",
        structure_blocks=["level1_overview", "level2_relevant", "format_rules"],
        included_sections=[
            SourceSection(section_id="1.0", title="Overview", content="overview text"),
            SourceSection(section_id="2.0", title="Architecture", content="architecture text"),
        ],
        skipped_sections=[
            SourceSection(section_id="9.0", title="Appendix Ref", content="appendix ref", included=False)
        ],
        discovered_snippets=[
            RelevantSnippet(
                section_id="7.2",
                keyword="retry",
                text="retry policy snippet",
                confidence=0.9,
            )
        ],
        appendix_index=[
            AppendixIndexEntry(
                appendix_id="APP-1",
                title="Operational Appendix",
                token_estimate=220,
                summary="rollback and retry details",
            )
        ],
    )

    assert bundle.context.sections_included == ["1.0", "2.0"]
    assert bundle.context.sections_skipped == ["9.0"]
    assert bundle.metadata.persona == "architect"
    assert bundle.metadata.doc_type == "brd"
    assert bundle.metadata.sections_included == ["1.0", "2.0"]
    assert bundle.metadata.tokens_total > 0



def test_build_prompt_bundle_is_deterministic_for_identical_inputs() -> None:
    kwargs = dict(
        persona="operator",
        doc_type="spec",
        structure_blocks=["level1_overview", "level2_relevant", "appendix_index"],
        included_sections=[
            SourceSection(section_id="3.0", title="Ops", content="logs metrics alerts"),
        ],
        skipped_sections=[],
        discovered_snippets=[],
        appendix_index=[
            AppendixIndexEntry(
                appendix_id="APP-OPS",
                title="Operations",
                token_estimate=100,
                summary="diagnostics summary",
            )
        ],
    )

    bundle_one = build_prompt_bundle(**kwargs)
    bundle_two = build_prompt_bundle(**kwargs)

    assert deterministic_fingerprint(bundle_one) == deterministic_fingerprint(bundle_two)



def test_build_prompt_bundle_fails_fast_for_missing_persona() -> None:
    try:
        build_prompt_bundle(
            persona="",
            doc_type="brd",
            structure_blocks=["level1_overview"],
            included_sections=[
                SourceSection(section_id="1.0", title="Overview", content="overview text"),
            ],
            skipped_sections=[],
            discovered_snippets=[],
            appendix_index=[],
        )
    except ContractValidationError as exc:
        assert "persona is required" in exc.errors
    else:
        raise AssertionError("Expected ContractValidationError")


def test_map_sections_for_persona_filters_by_semantic_category() -> None:
    result = map_sections_for_persona(
        "architect",
        [
            SourceSection(section_id="1.0", title="Architecture Overview", content="system architecture and component design"),
            SourceSection(section_id="9.0", title="Glossary", content="reference metadata appendix"),
        ],
    )

    assert [section.section_id for section in result.included_sections] == ["1.0"]
    assert [section.section_id for section in result.skipped_sections] == ["9.0"]
    assert "1.0" in result.category_confidence


def test_inspect_prompt_bundle_emits_warning_when_format_block_missing() -> None:
    bundle = build_prompt_bundle(
        persona="operator",
        doc_type="spec",
        structure_blocks=["level1_overview", "appendix_index"],
        included_sections=[SourceSection(section_id="1.0", title="Ops", content="monitoring and logs")],
        skipped_sections=[],
        discovered_snippets=[],
        appendix_index=[],
    )

    inspection = inspect_prompt_bundle(bundle)
    assert inspection["warnings"]


def test_prompt_metadata_sidecar_serialization_is_json() -> None:
    bundle = build_prompt_bundle(
        persona="architect",
        doc_type="brd",
        structure_blocks=["level1_overview", "format_rules"],
        included_sections=[SourceSection(section_id="1.0", title="Overview", content="overview text")],
        skipped_sections=[],
        discovered_snippets=[],
        appendix_index=[],
    )

    serialized = serialize_prompt_metadata_sidecar(bundle.metadata)
    assert '"persona": "architect"' in serialized
    assert '"doc_type": "brd"' in serialized


def test_assemble_project_review_prompt_uses_project_ucx_assets(tmp_path: Path) -> None:
    for relative in [
        Path("UCX/skills/personas"),
        Path("UCX/skills/layer_aliases"),
        Path("UCX/prompts/templates/creation"),
        Path("UCX/prompts/templates/review"),
        Path("UCX/prompts/templates/remediation"),
        Path("UCX/templates"),
        Path("UCX/templates/layers"),
    ]:
        (tmp_path / relative).mkdir(parents=True, exist_ok=True)

    (tmp_path / "UCX/skills/personas/architect.md").write_text("Architect domain knowledge", encoding="utf-8")
    (tmp_path / "UCX/prompts/templates/review/UCR_PROMPT_BRD_PROJECT.md").write_text("Review template body", encoding="utf-8")

    assembly = assemble_project_review_prompt(
        project_root=tmp_path,
        persona="architect",
        doc_type="brd",
        template_name="UCR_PROMPT_BRD_PROJECT.md",
        sections=[
            SourceSection(section_id="1.0", title="Architecture Overview", content="system architecture and integration design"),
            SourceSection(section_id="9.0", title="Appendix", content="reference appendix metadata"),
        ],
    )

    assert "Architect domain knowledge" in assembly.prompt_text
    assert "Review template body" in assembly.prompt_text
    assert assembly.bundle.metadata.persona == "architect"


def test_assemble_project_review_prompt_with_layer_includes_template_schema_assets(tmp_path: Path) -> None:
    for relative in [
        Path("UCX/skills/personas"),
        Path("UCX/skills/layer_aliases"),
        Path("UCX/prompts/templates/creation"),
        Path("UCX/prompts/templates/review"),
        Path("UCX/prompts/templates/remediation"),
        Path("UCX/templates"),
        Path("UCX/templates/layers/01_BRD"),
    ]:
        (tmp_path / relative).mkdir(parents=True, exist_ok=True)

    (tmp_path / "UCX/skills/personas/architect.md").write_text("Architect domain knowledge", encoding="utf-8")
    (tmp_path / "UCX/prompts/templates/review/UCR_PROMPT_BRD_PROJECT.md").write_text("Review template body", encoding="utf-8")
    (tmp_path / "UCX/templates/layers/01_BRD/BRD-MVP-TEMPLATE.md").write_text("BRD template layer asset", encoding="utf-8")
    (tmp_path / "UCX/templates/layers/01_BRD/BRD_MVP_SCHEMA.yaml").write_text("schema_version: '1.0'\n", encoding="utf-8")

    assembly = assemble_project_review_prompt(
        project_root=tmp_path,
        persona="architect",
        doc_type="brd",
        template_name="UCR_PROMPT_BRD_PROJECT.md",
        sections=[
            SourceSection(section_id="1.0", title="Architecture Overview", content="system architecture and integration design"),
            SourceSection(section_id="9.0", title="Appendix", content="reference appendix metadata"),
        ],
        layer="01_BRD",
    )

    assert "MCP Actionable Review Rules" in assembly.prompt_text
    assert "BRD-MVP-TEMPLATE.md" in assembly.prompt_text
    assert "BRD_MVP_SCHEMA.yaml" in assembly.prompt_text
