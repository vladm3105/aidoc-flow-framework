"""Unit tests for rag/chunk.py."""

from unittest.mock import mock_open, patch

import pytest

from rag.chunk import (
    _get_nested_value,
    _infer_doc_type,
    chunk_yaml_document,
    chunk_yaml_section,
    prepare_chunk_text,
)
from rag.exceptions import ChunkingError
from rag.models import ChunkResult


class TestPrepareChunkText:
    """Tests for chunk text preparation."""

    def test_with_ticker(self):
        result = prepare_chunk_text(
            section_label="Thesis",
            content="Long NVDA on data center demand",
            ticker="NVDA",
            doc_type="earnings-analysis",
        )
        assert "[earnings-analysis]" in result
        assert "[NVDA]" in result
        assert "[Thesis]" in result
        assert "Long NVDA" in result

    def test_without_ticker(self):
        result = prepare_chunk_text(
            section_label="Summary",
            content="Market overview",
            ticker=None,
            doc_type="research-analysis",
        )
        assert "[research-analysis]" in result
        assert "[Summary]" in result
        assert "[None]" not in result

    def test_content_on_newline(self):
        result = prepare_chunk_text(
            section_label="Test",
            content="Content here",
            ticker="NVDA",
            doc_type="test",
        )
        assert result.endswith("\nContent here")


class TestGetNestedValue:
    """Tests for nested value extraction."""

    def test_simple_key(self):
        doc = {"ticker": "NVDA"}
        assert _get_nested_value(doc, "ticker") == "NVDA"

    def test_nested_key(self):
        doc = {"thesis": {"summary": "Long thesis"}}
        assert _get_nested_value(doc, "thesis.summary") == "Long thesis"

    def test_deep_nested_key(self):
        doc = {"a": {"b": {"c": {"d": "deep"}}}}
        assert _get_nested_value(doc, "a.b.c.d") == "deep"

    def test_missing_key(self):
        doc = {"ticker": "NVDA"}
        assert _get_nested_value(doc, "missing") is None

    def test_missing_nested_key(self):
        doc = {"thesis": {"summary": "test"}}
        assert _get_nested_value(doc, "thesis.missing") is None

    def test_non_dict_intermediate(self):
        doc = {"ticker": "NVDA"}
        assert _get_nested_value(doc, "ticker.something") is None


class TestInferDocType:
    """Tests for document type inference from path."""

    def test_earnings_path(self):
        assert _infer_doc_type("/knowledge/analysis/earnings/NVDA.yaml") == "earnings-analysis"

    def test_trades_path(self):
        assert _infer_doc_type("/knowledge/trades/NVDA_20250101.yaml") == "trade-journal"

    def test_stock_path(self):
        assert _infer_doc_type("/analysis/stock/NVDA.yaml") == "stock-analysis"

    def test_research_path(self):
        assert _infer_doc_type("/analysis/research/datacenter.yaml") == "research-analysis"

    def test_ticker_profiles_path(self):
        assert _infer_doc_type("/knowledge/ticker-profiles/NVDA.yaml") == "ticker-profile"

    def test_unknown_path(self):
        assert _infer_doc_type("/random/path/file.yaml") == "unknown"


class TestChunkYamlSection:
    """Tests for section chunking."""

    def test_split_by_paragraphs(self):
        content = "First paragraph content.\n\nSecond paragraph content.\n\nThird paragraph."
        chunks = chunk_yaml_section(
            content=content,
            section_path="thesis",
            section_label="Thesis",
            ticker="NVDA",
            doc_type="earnings-analysis",
            max_tokens=20,
        )
        assert len(chunks) >= 1
        for chunk in chunks:
            assert isinstance(chunk, ChunkResult)
            assert chunk.section_path == "thesis"

    def test_preserves_section_metadata(self):
        content = "Some long content that needs splitting. " * 50
        chunks = chunk_yaml_section(
            content=content,
            section_path="risks",
            section_label="Risks",
            ticker="NVDA",
            doc_type="earnings-analysis",
            max_tokens=100,
        )
        for chunk in chunks:
            assert chunk.section_path == "risks"
            assert chunk.section_label == "Risks"

    def test_chunk_index_increments(self):
        # Create content that will be split into multiple chunks by paragraphs
        content = "Paragraph one content.\n\nParagraph two content.\n\nParagraph three."
        chunks = chunk_yaml_section(
            content=content,
            section_path="test",
            section_label="Test",
            ticker="NVDA",
            doc_type="test",
            max_tokens=5,  # Small enough to force splits
        )
        if len(chunks) > 1:
            indices = [c.chunk_index for c in chunks]
            assert indices == list(range(len(chunks)))


class TestChunkYamlDocument:
    """Tests for full document chunking."""

    def test_rejects_missing_file(self):
        with pytest.raises(ChunkingError, match="not found"):
            chunk_yaml_document("/nonexistent/file.yaml")

    @patch("builtins.open", mock_open(read_data=""))
    @patch("pathlib.Path.exists", return_value=True)
    def test_rejects_empty_yaml(self, mock_exists):
        with pytest.raises(ChunkingError, match="Empty"):
            chunk_yaml_document("/path/to/empty.yaml")

    @patch("rag.chunk._section_mappings", {})
    @patch(
        "builtins.open", mock_open(read_data="ticker: NVDA\nthesis: Long NVDA\n_meta:\n  id: test")
    )
    @patch("pathlib.Path.exists", return_value=True)
    def test_chunks_simple_document(self, mock_exists):
        chunks = chunk_yaml_document("/path/to/doc.yaml", min_tokens=1)

        # Should have chunks for ticker and thesis (not _meta)
        assert len(chunks) >= 1

    @patch(
        "rag.chunk._section_mappings",
        {
            "earnings-analysis": {
                "sections": [{"path": "thesis", "label": "Thesis"}],
                "skip": ["_meta"],
            }
        },
    )
    @patch(
        "builtins.open",
        mock_open(read_data="_meta:\n  doc_type: earnings-analysis\nthesis: Strong demand signal"),
    )
    @patch("pathlib.Path.exists", return_value=True)
    def test_uses_section_mappings(self, mock_exists):
        chunks = chunk_yaml_document("/path/to/earnings.yaml", min_tokens=1)

        # Should only have thesis section based on mapping
        assert any(c.section_label == "Thesis" for c in chunks)
