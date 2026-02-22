"""Unit tests for rag/hybrid.py."""

from datetime import date
from unittest.mock import MagicMock, patch

from rag.hybrid import (
    build_analysis_context,
    format_context,
    get_bias_warnings,
    get_hybrid_context,
    get_strategy_recommendations,
)
from rag.models import HybridContext, SearchResult


class TestFormatContext:
    """Tests for context formatting."""

    def test_format_empty_context(self):
        result = format_context([], {}, "NVDA")
        assert "## Context for NVDA" in result

    def test_format_with_graph_context(self):
        graph_context = {
            "peers": [{"peer": "AMD"}, {"peer": "INTC"}],
            "competitors": [{"competitor": "AMD Inc"}],
            "risks": [{"risk": "Export controls"}],
            "supply_chain": {
                "suppliers": ["TSMC"],
                "customers": ["Microsoft", "Meta"],
            },
        }

        result = format_context([], graph_context, "NVDA")

        assert "### Knowledge Graph" in result
        assert "**Sector Peers**: AMD, INTC" in result
        assert "**Competitors**: AMD Inc" in result
        assert "**Known Risks**: Export controls" in result
        assert "**Suppliers**: TSMC" in result
        assert "**Customers**: Microsoft, Meta" in result

    def test_format_with_vector_results(self):
        vector_results = [
            SearchResult(
                doc_id="EA-NVDA-Q4-2025",
                file_path="/path/to/doc.yaml",
                doc_type="earnings-analysis",
                ticker="NVDA",
                doc_date=date(2025, 1, 1),
                section_label="Thesis",
                content="Strong data center demand expected",
                similarity=0.85,
            )
        ]

        result = format_context(vector_results, {}, "NVDA")

        assert "### Past Analyses" in result
        assert "**EA-NVDA-Q4-2025**" in result
        assert "earnings-analysis" in result
        assert "Similarity: 0.85" in result
        assert "Strong data center demand" in result

    def test_format_truncates_long_content(self):
        long_content = "A" * 600
        vector_results = [
            SearchResult(
                doc_id="test",
                file_path="/path",
                doc_type="test",
                ticker="NVDA",
                doc_date=None,
                section_label="Test",
                content=long_content,
                similarity=0.8,
            )
        ]

        result = format_context(vector_results, {}, "NVDA")

        assert "..." in result
        assert len(result) < len(long_content) + 200


class TestGetHybridContext:
    """Tests for hybrid context retrieval."""

    @patch("rag.hybrid.get_similar_analyses")
    @patch("rag.hybrid.semantic_search")
    @patch("rag.hybrid.get_learnings_for_topic")
    def test_combines_sources(self, mock_learnings, mock_search, mock_similar):
        mock_similar.return_value = [
            SearchResult(
                doc_id="doc-001",
                file_path="/path",
                doc_type="earnings-analysis",
                ticker="NVDA",
                doc_date=None,
                section_label="Thesis",
                content="Past analysis",
                similarity=0.9,
            )
        ]
        mock_search.return_value = [
            SearchResult(
                doc_id="doc-002",
                file_path="/path",
                doc_type="research",
                ticker="NVDA",
                doc_date=None,
                section_label="Summary",
                content="Query result",
                similarity=0.8,
            )
        ]
        mock_learnings.return_value = []

        with patch("graph.layer.TradingGraph") as mock_graph:
            mock_instance = MagicMock()
            mock_instance.health_check.return_value = True
            mock_instance.get_ticker_context.return_value = {}
            mock_graph.return_value.__enter__ = MagicMock(return_value=mock_instance)
            mock_graph.return_value.__exit__ = MagicMock(return_value=False)

            result = get_hybrid_context("NVDA", "earnings analysis")

        assert isinstance(result, HybridContext)
        assert result.ticker == "NVDA"
        assert len(result.vector_results) == 2

    @patch("rag.hybrid.get_similar_analyses")
    @patch("rag.hybrid.semantic_search")
    @patch("rag.hybrid.get_learnings_for_topic")
    def test_deduplicates_results(self, mock_learnings, mock_search, mock_similar):
        # Same doc returned by multiple searches
        result = SearchResult(
            doc_id="doc-001",
            file_path="/path",
            doc_type="earnings-analysis",
            ticker="NVDA",
            doc_date=None,
            section_label="Thesis",
            content="Same doc",
            similarity=0.9,
        )
        mock_similar.return_value = [result]
        mock_search.return_value = [result]  # Duplicate
        mock_learnings.return_value = []

        with patch("graph.layer.TradingGraph") as mock_graph:
            mock_instance = MagicMock()
            mock_instance.health_check.return_value = False
            mock_graph.return_value.__enter__ = MagicMock(return_value=mock_instance)
            mock_graph.return_value.__exit__ = MagicMock(return_value=False)

            context = get_hybrid_context("NVDA", "test query")

        # Should have only one result after dedup
        assert len(context.vector_results) == 1

    @patch("rag.hybrid.get_similar_analyses")
    @patch("rag.hybrid.semantic_search")
    @patch("rag.hybrid.get_learnings_for_topic")
    def test_handles_graph_failure(self, mock_learnings, mock_search, mock_similar):
        mock_similar.return_value = []
        mock_search.return_value = []
        mock_learnings.return_value = []

        with patch("graph.layer.TradingGraph") as mock_graph:
            mock_graph.return_value.__enter__ = MagicMock(side_effect=Exception("Graph down"))

            # Should not raise, just log warning
            context = get_hybrid_context("NVDA", "test query")

        assert context.graph_context == {}


class TestBuildAnalysisContext:
    """Tests for analysis context building."""

    @patch("rag.hybrid.get_hybrid_context")
    def test_builds_context_string(self, mock_hybrid):
        mock_hybrid.return_value = HybridContext(
            ticker="NVDA",
            vector_results=[],
            graph_context={},
            formatted="## Context for NVDA\n",
        )

        result = build_analysis_context("NVDA", "earnings-analysis")

        assert isinstance(result, str)
        assert "NVDA" in result


class TestGetBiasWarnings:
    """Tests for bias warning retrieval."""

    def test_returns_bias_list(self):
        with patch("graph.layer.TradingGraph") as mock_graph:
            mock_instance = MagicMock()
            mock_instance.health_check.return_value = True
            mock_instance.run_cypher.return_value = [
                {"bias": "disposition-effect", "outcome": "loss", "occurrences": 3},
            ]
            mock_graph.return_value.__enter__ = MagicMock(return_value=mock_instance)
            mock_graph.return_value.__exit__ = MagicMock(return_value=False)

            warnings = get_bias_warnings("NVDA")

        assert len(warnings) == 1
        assert warnings[0]["bias"] == "disposition-effect"
        assert warnings[0]["occurrences"] == 3

    def test_handles_graph_unavailable(self):
        with patch("graph.layer.TradingGraph") as mock_graph:
            mock_graph.return_value.__enter__ = MagicMock(side_effect=Exception("Down"))

            warnings = get_bias_warnings("NVDA")

        assert warnings == []


class TestGetStrategyRecommendations:
    """Tests for strategy recommendation retrieval."""

    def test_returns_strategy_list(self):
        with patch("graph.layer.TradingGraph") as mock_graph:
            mock_instance = MagicMock()
            mock_instance.health_check.return_value = True
            mock_instance.run_cypher.return_value = [
                {"strategy": "earnings-momentum", "win_rate": 0.75, "trades": 8},
            ]
            mock_graph.return_value.__enter__ = MagicMock(return_value=mock_instance)
            mock_graph.return_value.__exit__ = MagicMock(return_value=False)

            recs = get_strategy_recommendations("NVDA")

        assert len(recs) == 1
        assert recs[0]["strategy"] == "earnings-momentum"
        assert recs[0]["win_rate"] == 0.75

    def test_handles_graph_unavailable(self):
        with patch("graph.layer.TradingGraph") as mock_graph:
            mock_graph.return_value.__enter__ = MagicMock(side_effect=Exception("Down"))

            recs = get_strategy_recommendations("NVDA")

        assert recs == []
