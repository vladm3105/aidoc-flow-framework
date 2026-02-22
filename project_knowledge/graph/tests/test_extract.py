"""Unit tests for graph/extract.py."""

from datetime import datetime
from unittest.mock import patch

import pytest

from graph.exceptions import ExtractionError
from graph.extract import (
    _apply_confidence_thresholds,
    _flatten_doc_for_relations,
    _get_field_value,
    _infer_doc_type,
    _parse_json_response,
    extract_document,
    extract_text,
)
from graph.models import EntityExtraction, ExtractionResult


class TestGetFieldValue:
    """Tests for field value extraction from YAML documents."""

    def test_simple_field(self):
        doc = {"ticker": "NVDA", "price": 145.50}
        assert _get_field_value(doc, "ticker") == "NVDA"
        assert _get_field_value(doc, "price") == "145.5"

    def test_nested_field(self):
        doc = {"thesis": {"summary": "Long NVDA", "edge": "Strong demand"}}
        assert _get_field_value(doc, "thesis.summary") == "Long NVDA"

    def test_array_field(self):
        doc = {"risks": [{"risk": "Export controls"}, {"risk": "Competition"}]}
        result = _get_field_value(doc, "risks[].risk")
        assert "Export controls" in result
        assert "Competition" in result

    def test_missing_field(self):
        doc = {"ticker": "NVDA"}
        assert _get_field_value(doc, "missing") is None

    def test_deep_nested_field(self):
        doc = {"level1": {"level2": {"level3": "value"}}}
        assert _get_field_value(doc, "level1.level2.level3") == "value"


class TestFlattenDocForRelations:
    """Tests for document flattening."""

    def test_simple_flatten(self):
        doc = {"ticker": "NVDA", "thesis": "Long thesis"}
        skip = ["_meta"]
        result = _flatten_doc_for_relations(doc, skip)
        assert "ticker: NVDA" in result
        assert "thesis: Long thesis" in result

    def test_skip_fields(self):
        doc = {"ticker": "NVDA", "_meta": {"id": "test"}, "thesis": "Long"}
        skip = ["_meta"]
        result = _flatten_doc_for_relations(doc, skip)
        assert "_meta" not in result
        assert "id: test" not in result
        assert "ticker: NVDA" in result


class TestInferDocType:
    """Tests for document type inference."""

    def test_earnings_analysis(self):
        assert _infer_doc_type("/path/to/earnings/NVDA_20250101.yaml") == "earnings-analysis"

    def test_trade_journal(self):
        assert _infer_doc_type("/knowledge/trades/NVDA_20250101.yaml") == "trade-journal"

    def test_stock_analysis(self):
        assert _infer_doc_type("/analysis/stock/NVDA.yaml") == "stock-analysis"

    def test_unknown_type(self):
        assert _infer_doc_type("/random/path/file.yaml") == "unknown"


class TestParseJsonResponse:
    """Tests for LLM JSON response parsing."""

    def test_clean_json(self):
        response = '[{"type": "Ticker", "value": "NVDA"}]'
        result = _parse_json_response(response)
        assert len(result) == 1
        assert result[0]["type"] == "Ticker"

    def test_markdown_wrapped_json(self):
        response = '```json\n[{"type": "Ticker", "value": "NVDA"}]\n```'
        result = _parse_json_response(response)
        assert len(result) == 1
        assert result[0]["type"] == "Ticker"

    def test_json_with_surrounding_text(self):
        response = 'Here are the entities: [{"type": "Ticker", "value": "NVDA"}] Done!'
        result = _parse_json_response(response)
        assert len(result) == 1

    def test_invalid_json(self):
        response = "This is not JSON at all"
        result = _parse_json_response(response)
        assert result == []

    def test_empty_array(self):
        response = "[]"
        result = _parse_json_response(response)
        assert result == []


class TestApplyConfidenceThresholds:
    """Tests for confidence threshold filtering."""

    def test_high_confidence_kept(self):
        result = ExtractionResult(
            source_doc_id="test",
            source_doc_type="test",
            source_file_path="test.yaml",
            source_text_hash="abc123",
            extracted_at=datetime.now(),
            extractor="test",
            extraction_version="1.0.0",
        )
        result.entities = [
            EntityExtraction(type="Ticker", value="NVDA", confidence=0.9, evidence=""),
        ]

        with patch(
            "graph.extract._config",
            {"extraction": {"commit_threshold": 0.7, "flag_threshold": 0.5}},
        ):
            filtered = _apply_confidence_thresholds(result)

        assert len(filtered.entities) == 1
        assert not filtered.entities[0].needs_review

    def test_medium_confidence_flagged(self):
        result = ExtractionResult(
            source_doc_id="test",
            source_doc_type="test",
            source_file_path="test.yaml",
            source_text_hash="abc123",
            extracted_at=datetime.now(),
            extractor="test",
            extraction_version="1.0.0",
        )
        result.entities = [
            EntityExtraction(type="Ticker", value="NVDA", confidence=0.6, evidence=""),
        ]

        with patch(
            "graph.extract._config",
            {"extraction": {"commit_threshold": 0.7, "flag_threshold": 0.5}},
        ):
            filtered = _apply_confidence_thresholds(result)

        assert len(filtered.entities) == 1
        assert filtered.entities[0].needs_review

    def test_low_confidence_removed(self):
        result = ExtractionResult(
            source_doc_id="test",
            source_doc_type="test",
            source_file_path="test.yaml",
            source_text_hash="abc123",
            extracted_at=datetime.now(),
            extractor="test",
            extraction_version="1.0.0",
        )
        result.entities = [
            EntityExtraction(type="Ticker", value="NVDA", confidence=0.3, evidence=""),
        ]

        with patch(
            "graph.extract._config",
            {"extraction": {"commit_threshold": 0.7, "flag_threshold": 0.5}},
        ):
            filtered = _apply_confidence_thresholds(result)

        assert len(filtered.entities) == 0


class TestExtractDocument:
    """Tests for full document extraction (mocked)."""

    @patch("graph.extract.is_real_document")
    def test_rejects_template(self, mock_is_real):
        mock_is_real.return_value = False

        with pytest.raises(ExtractionError, match="template"):
            extract_document("/path/to/template.yaml")

    @patch("graph.extract.is_real_document")
    def test_rejects_missing_file(self, mock_is_real):
        mock_is_real.return_value = True

        with pytest.raises(ExtractionError, match="not found"):
            extract_document("/nonexistent/file.yaml")


class TestExtractText:
    """Tests for text extraction (mocked)."""

    @patch("graph.extract._call_ollama_rate_limited")
    @patch(
        "graph.extract._config",
        {"extraction": {"timeout_seconds": 30, "commit_threshold": 0.7, "flag_threshold": 0.5}},
    )
    def test_extracts_from_text(self, mock_ollama):
        mock_ollama.return_value = (
            '[{"type": "Ticker", "value": "NVDA", "confidence": 0.9, "evidence": "test"}]'
        )

        result = extract_text(
            text="NVDA is a strong buy for AI data center growth",
            doc_type="research-analysis",
            doc_id="test-001",
        )

        assert result.source_doc_id == "test-001"
        assert result.source_doc_type == "research-analysis"
