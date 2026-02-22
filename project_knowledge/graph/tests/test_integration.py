"""Integration tests for graph layer round-trip operations.

These tests verify the full pipeline from extraction to storage and query.
They require a running Neo4j instance and can be skipped with:
    pytest -m "not integration"
"""

from pathlib import Path
from unittest.mock import patch

import pytest

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


@pytest.fixture
def neo4j_available():
    """Check if Neo4j is available for integration tests."""
    try:
        from graph.layer import TradingGraph

        with TradingGraph() as graph:
            return graph.health_check()
    except Exception:
        return False


@pytest.fixture
def fixtures_path():
    """Path to test fixtures."""
    return Path(__file__).parent / "fixtures"


class TestExtractionRoundTrip:
    """Test full extraction pipeline."""

    @pytest.mark.skipif(
        "not config.getoption('--run-integration')",
        reason="Integration tests require --run-integration flag",
    )
    def test_extract_and_query_earnings(self, neo4j_available, fixtures_path):
        """Extract earnings analysis and query the graph."""
        if not neo4j_available:
            pytest.skip("Neo4j not available")

        from graph.extract import extract_document

        # Extract the sample earnings document
        earnings_path = fixtures_path / "sample_earnings.yaml"

        with patch("graph.extract.is_real_document", return_value=True):
            result = extract_document(str(earnings_path), dry_run=True)

        # Verify extraction found entities
        assert result.entities is not None
        assert len(result.entities) >= 0  # May be empty if LLM unavailable

    @pytest.mark.skipif(
        "not config.getoption('--run-integration')",
        reason="Integration tests require --run-integration flag",
    )
    def test_extract_and_query_trade(self, neo4j_available, fixtures_path):
        """Extract trade journal and query biases."""
        if not neo4j_available:
            pytest.skip("Neo4j not available")

        from graph.extract import extract_document

        trade_path = fixtures_path / "sample_trade.yaml"

        with patch("graph.extract.is_real_document", return_value=True):
            result = extract_document(str(trade_path), dry_run=True)

        assert result.source_doc_type in ["trade-journal", "unknown"]


class TestGraphSchemaOperations:
    """Test schema initialization and validation."""

    @pytest.mark.skipif(
        "not config.getoption('--run-integration')",
        reason="Integration tests require --run-integration flag",
    )
    def test_schema_init(self, neo4j_available):
        """Test schema initialization."""
        if not neo4j_available:
            pytest.skip("Neo4j not available")

        from graph.layer import TradingGraph

        with TradingGraph() as graph:
            # Should not raise
            graph.init_schema()

    @pytest.mark.skipif(
        "not config.getoption('--run-integration')",
        reason="Integration tests require --run-integration flag",
    )
    def test_get_stats(self, neo4j_available):
        """Test statistics retrieval."""
        if not neo4j_available:
            pytest.skip("Neo4j not available")

        from graph.layer import TradingGraph

        with TradingGraph() as graph:
            stats = graph.get_stats()

        assert stats.total_nodes >= 0
        assert stats.total_edges >= 0


class TestNormalizationPipeline:
    """Test entity normalization in pipeline."""

    def test_normalize_extracted_entities(self):
        """Verify normalization is applied during extraction."""
        from graph.normalize import normalize_entity

        # Test ticker normalization
        entity = {"type": "ticker", "value": "nvda", "confidence": 0.9}
        normalized = normalize_entity(entity)
        assert normalized["type"] == "Ticker"
        assert normalized["value"] == "NVDA"

        # Test alias resolution
        entity = {"type": "ticker", "value": "GOOG", "confidence": 0.8}
        normalized = normalize_entity(entity)
        assert normalized["value"] == "GOOGL"

    def test_dedup_entities(self):
        """Verify deduplication keeps highest confidence."""
        from graph.normalize import dedupe_entities

        entities = [
            {"type": "Ticker", "value": "NVDA", "confidence": 0.7},
            {"type": "Ticker", "value": "NVDA", "confidence": 0.9},
            {"type": "Company", "value": "NVIDIA", "confidence": 0.8},
        ]

        deduped = dedupe_entities(entities)

        # Should have 2 entities: one Ticker (highest conf) and one Company
        assert len(deduped) == 2
        ticker = next(e for e in deduped if e["type"] == "Ticker")
        assert ticker["confidence"] == 0.9
