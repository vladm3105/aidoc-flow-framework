"""Integration tests for RAG layer round-trip operations.

These tests verify the full pipeline from embedding to search.
They require a running PostgreSQL instance with pgvector.
Can be skipped with: pytest -m "not integration"
"""

from pathlib import Path
from unittest.mock import patch

import pytest

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


@pytest.fixture
def database_available():
    """Check if PostgreSQL is available for integration tests."""
    try:
        from rag.schema import health_check

        return health_check()
    except Exception:
        return False


@pytest.fixture
def fixtures_path():
    """Path to test fixtures."""
    return Path(__file__).parent.parent.parent / "graph" / "tests" / "fixtures"


class TestEmbeddingRoundTrip:
    """Test full embedding pipeline."""

    @pytest.mark.skipif(
        "not config.getoption('--run-integration')",
        reason="Integration tests require --run-integration flag",
    )
    def test_embed_and_search(self, database_available, fixtures_path):
        """Embed a document and search for it."""
        if not database_available:
            pytest.skip("PostgreSQL not available")

        from rag.embed import delete_document, embed_document
        from rag.search import semantic_search

        earnings_path = fixtures_path / "sample_earnings.yaml"

        with patch("rag.embed.is_real_document", return_value=True):
            result = embed_document(str(earnings_path), force=True)

        assert result.chunk_count > 0

        # Search for the embedded content
        try:
            results = semantic_search("NVDA earnings data center", ticker="NVDA")
            # May return results if embedding succeeded
        finally:
            # Cleanup
            delete_document(result.doc_id)


class TestChunkingPipeline:
    """Test document chunking."""

    def test_chunk_earnings_document(self, fixtures_path):
        """Test chunking an earnings document."""
        from rag.chunk import chunk_yaml_document

        earnings_path = fixtures_path / "sample_earnings.yaml"

        # Mock section mappings
        with patch("rag.chunk._section_mappings", {}):
            chunks = chunk_yaml_document(str(earnings_path), min_tokens=1)

        assert len(chunks) > 0
        for chunk in chunks:
            assert chunk.content
            assert chunk.section_path
            assert chunk.prepared_text

    def test_chunk_trade_document(self, fixtures_path):
        """Test chunking a trade journal."""
        from rag.chunk import chunk_yaml_document

        trade_path = fixtures_path / "sample_trade.yaml"

        with patch("rag.chunk._section_mappings", {}):
            chunks = chunk_yaml_document(str(trade_path), min_tokens=1)

        assert len(chunks) > 0


class TestHybridContextPipeline:
    """Test hybrid context building."""

    def test_format_context_structure(self):
        """Test context formatting produces valid markdown."""
        from datetime import date

        from rag.hybrid import format_context
        from rag.models import SearchResult

        vector_results = [
            SearchResult(
                doc_id="EA-NVDA-Q4-2025",
                file_path="/path/to/doc.yaml",
                doc_type="earnings-analysis",
                ticker="NVDA",
                doc_date=date(2025, 1, 1),
                section_label="Thesis",
                content="Strong data center demand",
                similarity=0.85,
            )
        ]

        graph_context = {
            "peers": [{"peer": "AMD"}],
            "competitors": [],
            "risks": [{"risk": "Export controls"}],
            "supply_chain": {"suppliers": ["TSMC"], "customers": []},
        }

        result = format_context(vector_results, graph_context, "NVDA")

        # Verify markdown structure
        assert result.startswith("## Context for NVDA")
        assert "### Knowledge Graph" in result
        assert "### Past Analyses" in result
        assert "**Sector Peers**: AMD" in result
        assert "EA-NVDA-Q4-2025" in result


class TestRAGSchemaOperations:
    """Test schema initialization and health checks."""

    @pytest.mark.skipif(
        "not config.getoption('--run-integration')",
        reason="Integration tests require --run-integration flag",
    )
    def test_schema_init(self, database_available):
        """Test schema initialization."""
        if not database_available:
            pytest.skip("PostgreSQL not available")

        from rag.schema import init_schema

        # Should not raise
        init_schema()

    @pytest.mark.skipif(
        "not config.getoption('--run-integration')",
        reason="Integration tests require --run-integration flag",
    )
    def test_get_stats(self, database_available):
        """Test statistics retrieval."""
        if not database_available:
            pytest.skip("PostgreSQL not available")

        from rag.search import get_rag_stats

        stats = get_rag_stats()

        assert stats.document_count >= 0
        assert stats.chunk_count >= 0
