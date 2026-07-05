from __future__ import annotations

import sys
from pathlib import Path

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
    map_sections_for_personas,
)


def test_build_prompt_bundle_emits_required_context_and_metadata() -> None:
    bundle = build_prompt_bundle(
        personas=["architect"],
        doc_type="brd",
        structure_blocks=["level1_overview", "level2_relevant", "format_rules"],
        included_sections=[
            SourceSection(section_id="1.0", title="Overview", content="overview text"),
            SourceSection(section_id="2.0", title="Architecture", content="architecture text"),
        ],
        skipped_sections=[
            SourceSection(
                section_id="9.0", title="Appendix Ref", content="appendix ref", included=False
            )
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
    assert bundle.metadata.personas == ["architect"]
    assert bundle.metadata.doc_type == "brd"
    assert bundle.metadata.sections_included == ["1.0", "2.0"]
    assert bundle.metadata.tokens_total > 0


def test_build_prompt_bundle_is_deterministic_for_identical_inputs() -> None:
    kwargs = dict(
        personas=["operator"],
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


def test_build_prompt_bundle_fails_fast_for_missing_personas() -> None:
    try:
        build_prompt_bundle(
            personas=[],
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
        assert "personas is required" in exc.errors
    else:
        raise AssertionError("Expected ContractValidationError")


def test_map_sections_for_personas_filters_by_semantic_category() -> None:
    result = map_sections_for_personas(
        ["architect"],
        [
            SourceSection(
                section_id="1.0",
                title="Architecture Overview",
                content="system architecture and component design",
            ),
            SourceSection(
                section_id="9.0", title="Glossary", content="reference metadata appendix"
            ),
        ],
    )

    assert [section.section_id for section in result.included_sections] == ["1.0"]
    assert [section.section_id for section in result.skipped_sections] == ["9.0"]
    assert "1.0" in result.category_confidence


def test_inspect_prompt_bundle_emits_warning_when_format_block_missing() -> None:
    bundle = build_prompt_bundle(
        personas=["operator"],
        doc_type="spec",
        structure_blocks=["level1_overview", "appendix_index"],
        included_sections=[
            SourceSection(section_id="1.0", title="Ops", content="monitoring and logs")
        ],
        skipped_sections=[],
        discovered_snippets=[],
        appendix_index=[],
    )

    inspection = inspect_prompt_bundle(bundle)
    assert inspection["warnings"]


def test_prompt_metadata_sidecar_serialization_is_json() -> None:
    bundle = build_prompt_bundle(
        personas=["architect"],
        doc_type="brd",
        structure_blocks=["level1_overview", "format_rules"],
        included_sections=[
            SourceSection(section_id="1.0", title="Overview", content="overview text")
        ],
        skipped_sections=[],
        discovered_snippets=[],
        appendix_index=[],
    )

    serialized = serialize_prompt_metadata_sidecar(bundle.metadata)
    assert '"personas": ["architect"]' in serialized
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

    (tmp_path / "UCX/skills/persona_mappings.yaml").write_text('version: "1.0"\n', encoding="utf-8")
    (tmp_path / "UCX/skills/personas/architect.md").write_text(
        "Architect domain knowledge", encoding="utf-8"
    )
    (tmp_path / "UCX/prompts/templates/review/UCR_PROMPT_BRD_PROJECT.md").write_text(
        "Review template body", encoding="utf-8"
    )

    assembly = assemble_project_review_prompt(
        project_root=tmp_path,
        personas=["architect"],
        doc_type="brd",
        template_name="UCR_PROMPT_BRD_PROJECT.md",
        sections=[
            SourceSection(
                section_id="1.0",
                title="Architecture Overview",
                content="system architecture and integration design",
            ),
            SourceSection(
                section_id="9.0", title="Appendix", content="reference appendix metadata"
            ),
        ],
    )

    assert "Architect domain knowledge" in assembly.prompt_text
    assert "Review template body" in assembly.prompt_text
    assert assembly.bundle.metadata.personas == ["architect"]


def test_assemble_project_review_prompt_with_layer_includes_template_schema_assets(
    tmp_path: Path,
) -> None:
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

    (tmp_path / "UCX/skills/persona_mappings.yaml").write_text('version: "1.0"\n', encoding="utf-8")
    (tmp_path / "UCX/skills/personas/architect.md").write_text(
        "Architect domain knowledge", encoding="utf-8"
    )
    (tmp_path / "UCX/prompts/templates/review/UCR_PROMPT_BRD_PROJECT.md").write_text(
        "Review template body", encoding="utf-8"
    )
    (tmp_path / "UCX/templates/layers/01_BRD/BRD-MVP-TEMPLATE.md").write_text(
        "BRD template layer asset", encoding="utf-8"
    )
    (tmp_path / "UCX/templates/layers/01_BRD/BRD_MVP_SCHEMA.yaml").write_text(
        "schema_version: '1.0'\n", encoding="utf-8"
    )

    assembly = assemble_project_review_prompt(
        project_root=tmp_path,
        personas=["architect"],
        doc_type="brd",
        template_name="UCR_PROMPT_BRD_PROJECT.md",
        sections=[
            SourceSection(
                section_id="1.0",
                title="Architecture Overview",
                content="system architecture and integration design",
            ),
            SourceSection(
                section_id="9.0", title="Appendix", content="reference appendix metadata"
            ),
        ],
        layer="01_BRD",
    )

    assert "MCP Actionable Review Rules" in assembly.prompt_text
    assert "BRD-MVP-TEMPLATE.md" in assembly.prompt_text
    assert "BRD_MVP_SCHEMA.yaml" in assembly.prompt_text


def test_multi_persona_format_block_contains_headers_and_separators() -> None:
    """M-6: Verify multi-persona formatting with 2+ personas."""
    from mcp_server.prompts.context_builder import _format_persona_block

    pairs = [
        ("architect", "Architect domain knowledge"),
        ("tech_lead", "Tech lead domain knowledge"),
        ("operator", "Operator domain knowledge"),
    ]
    result = _format_persona_block(pairs)

    assert "### Persona 1: ARCHITECT" in result
    assert "### Persona 2: TECH_LEAD" in result
    assert "### Persona 3: OPERATOR" in result
    assert "---" in result
    assert "Architect domain knowledge" in result
    assert "Tech lead domain knowledge" in result


def test_multi_persona_format_block_single_persona_no_wrapper() -> None:
    pairs = [("architect", "Architect domain knowledge")]
    from mcp_server.prompts.context_builder import _format_persona_block

    result = _format_persona_block(pairs)
    assert "### Persona" not in result
    assert result == "Architect domain knowledge"


def test_resolve_personas_fallback_to_config(tmp_path: Path) -> None:
    """M-7: Verify personas=None resolves from persona_mappings.yaml."""
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

    (tmp_path / "UCX/skills/personas/architect.md").write_text(
        "Architect knowledge", encoding="utf-8"
    )
    (tmp_path / "UCX/skills/personas/tech_lead.md").write_text(
        "Tech lead knowledge", encoding="utf-8"
    )
    mapping_yaml = (
        'version: "1.0"\n'
        "review:\n"
        "  brd:\n"
        "    personas: [architect, tech_lead]\n"
        "    mode: sequential\n"
    )
    (tmp_path / "UCX/skills/persona_mappings.yaml").write_text(mapping_yaml, encoding="utf-8")

    from mcp_server.prompts.context_builder import _resolve_personas

    result = _resolve_personas(tmp_path, None, "brd", "review")
    assert len(result) == 2
    assert result[0][0] == "architect"
    assert result[1][0] == "tech_lead"
    assert "Architect knowledge" in result[0][1]


def test_map_sections_for_personas_union_includes_all_categories() -> None:
    """Verify union of categories from multiple personas includes sections for any persona."""
    sections = [
        SourceSection(
            section_id="1.0",
            title="Architecture",
            content="system architecture and component design",
        ),
        SourceSection(
            section_id="2.0", title="Compliance", content="regulation compliance audit policy"
        ),
        SourceSection(section_id="9.0", title="Glossary", content="reference metadata appendix"),
    ]
    # architect has: functional, quality, technical, integration
    # auditor has: compliance, risk, quality, integration
    # Union should include both architecture (technical) and compliance sections
    result = map_sections_for_personas(["architect", "auditor"], sections)
    included_ids = [s.section_id for s in result.included_sections]
    assert "1.0" in included_ids
    assert "2.0" in included_ids
    assert "9.0" not in included_ids  # metadata still skipped


def test_resolve_personas_remediation_default_fallback(tmp_path: Path) -> None:
    """I-2: Verify remediation._default fallback works for unknown doctype."""
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

    (tmp_path / "UCX/skills/personas/architect.md").write_text(
        "Architect knowledge", encoding="utf-8"
    )
    (tmp_path / "UCX/skills/personas/chairperson.md").write_text(
        "Chairperson knowledge", encoding="utf-8"
    )
    mapping_yaml = (
        'version: "1.0"\n'
        "remediation:\n"
        "  _default:\n"
        "    personas: [architect, chairperson]\n"
        "    mode: sequential\n"
        "    loading: adaptive\n"
    )
    (tmp_path / "UCX/skills/persona_mappings.yaml").write_text(mapping_yaml, encoding="utf-8")

    from mcp_server.prompts.context_builder import _resolve_personas

    result = _resolve_personas(tmp_path, None, "brd", "remediation")
    assert len(result) == 2
    assert result[0][0] == "architect"
    assert result[1][0] == "chairperson"


def _minimal_review_ucx(root: Path, template_body: str) -> None:
    for relative in [
        Path("UCX/skills/personas"),
        Path("UCX/skills/layer_aliases"),
        Path("UCX/prompts/templates/creation"),
        Path("UCX/prompts/templates/review"),
        Path("UCX/prompts/templates/remediation"),
        Path("UCX/templates"),
        Path("UCX/templates/layers"),
    ]:
        (root / relative).mkdir(parents=True, exist_ok=True)
    (root / "UCX/skills/persona_mappings.yaml").write_text('version: "1.0"\n', encoding="utf-8")
    (root / "UCX/skills/personas/architect.md").write_text("Architect", encoding="utf-8")
    (root / "UCX/prompts/templates/review/UCR_PROMPT_BRD_PROJECT.md").write_text(
        template_body, encoding="utf-8"
    )


def test_assemble_review_prompt_inlines_document_body(tmp_path: Path) -> None:
    # HERMES-REVIEW-CONTENT-DELIVERY: the review lens must actually receive the body.
    _minimal_review_ucx(tmp_path, "Review template body")
    assembly = assemble_project_review_prompt(
        project_root=tmp_path,
        personas=["architect"],
        doc_type="brd",
        template_name="UCR_PROMPT_BRD_PROJECT.md",
        sections=[
            SourceSection(
                section_id="1.0",
                title="Overview",
                content="UNIQUEBODYTOKEN system architecture integration detail",
            ),
        ],
    )
    assert "## Document to Review" in assembly.prompt_text
    assert "UNIQUEBODYTOKEN" in assembly.prompt_text  # the body now reaches the lens


def test_assemble_review_prompt_dedupes_template_placeholder(tmp_path: Path) -> None:
    # A template that carries the `## Document to Review` / [PASTE …] placeholder must
    # yield exactly ONE populated Document-to-Review block (no duplicate, no residue).
    template = (
        "Review the artifact.\n\n"
        "## Document to Review\n\n"
        "[PASTE BRD DOCUMENT CONTENT BELOW THIS LINE]\n"
    )
    _minimal_review_ucx(tmp_path, template)
    assembly = assemble_project_review_prompt(
        project_root=tmp_path,
        personas=["architect"],
        doc_type="brd",
        template_name="UCR_PROMPT_BRD_PROJECT.md",
        sections=[
            SourceSection(
                section_id="1.0", title="Overview", content="architecture integration content"
            ),
        ],
    )
    assert assembly.prompt_text.count("## Document to Review") == 1
    assert "PASTE BRD DOCUMENT CONTENT" not in assembly.prompt_text
    assert "architecture integration content" in assembly.prompt_text
