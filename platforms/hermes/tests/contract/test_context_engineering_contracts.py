from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp_server.models.context_engineering_contracts import (  # noqa: E402
    AppendixIndexEntry,
    ContextContract,
    PromptBundle,
    PromptMetadataSidecar,
    RelevantSnippet,
    deterministic_fingerprint,
    validate_context_contract,
    validate_prompt_metadata_sidecar,
)


def build_valid_context() -> ContextContract:
    return ContextContract(
        sections_included=["1", "2"],
        sections_skipped=["3"],
        discovered_snippets=[
            RelevantSnippet(
                section_id="2.1",
                keyword="retry",
                text="retry policy snippet",
                confidence=0.8,
            )
        ],
        appendix_index=[
            AppendixIndexEntry(
                appendix_id="APP-A",
                title="Appendix A",
                token_estimate=200,
                summary="policy summary",
            )
        ],
        token_estimate=1200,
    )


def build_valid_metadata() -> PromptMetadataSidecar:
    return PromptMetadataSidecar(
        personas=["architect"],
        doc_type="brd",
        structure_blocks=["level1_overview", "level2_relevant"],
        sections_included=["1", "2"],
        sections_skipped=["3"],
        tokens_total=1300,
    )


def test_context_contract_validation_passes_for_valid_payload() -> None:
    context = build_valid_context()
    assert validate_context_contract(context) == []


def test_context_contract_validation_fails_for_empty_sections_included() -> None:
    context = ContextContract(
        sections_included=[],
        sections_skipped=["3"],
        discovered_snippets=[],
        appendix_index=[],
        token_estimate=10,
    )
    errors = validate_context_contract(context)
    assert "sections_included must be non-empty" in errors


def test_prompt_metadata_validation_requires_required_fields() -> None:
    metadata = PromptMetadataSidecar(
        personas=[],
        doc_type="",
        structure_blocks=[],
        tokens_total=0,
    )
    errors = validate_prompt_metadata_sidecar(metadata)
    assert "personas is required" in errors
    assert "doc_type is required" in errors
    assert "structure_blocks must be non-empty" in errors
    assert "tokens_total must be > 0" in errors


def test_deterministic_fingerprint_is_stable_for_identical_input() -> None:
    bundle1 = PromptBundle(context=build_valid_context(), metadata=build_valid_metadata())
    bundle2 = PromptBundle(context=build_valid_context(), metadata=build_valid_metadata())

    assert deterministic_fingerprint(bundle1) == deterministic_fingerprint(bundle2)
