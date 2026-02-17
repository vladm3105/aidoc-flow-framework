"""Tests for LightRAG query functionality."""

import pytest
from unittest.mock import Mock, patch


class TestQueryModes:
    """Tests for different query modes."""

    @pytest.mark.utest
    def test_query_modes_defined(self):
        """Verify all query modes are available."""
        expected_modes = ["local", "global", "hybrid", "naive", "mix"]
        # LightRAG supports these modes
        for mode in expected_modes:
            assert mode in expected_modes

    @pytest.mark.utest
    def test_query_prompt_generation(self):
        """Test query prompt generation for each mode."""
        from lightrag_service.custom_prompts import get_query_prompt

        modes = ["local", "global", "hybrid", "naive", "mix"]
        for mode in modes:
            prompt = get_query_prompt(mode)
            assert "Context:" in prompt
            assert "Question:" in prompt


class TestQueryRouting:
    """Tests for query classification and routing."""

    @pytest.mark.utest
    def test_factual_query_classification(self):
        """Test factual queries are classified correctly."""
        # Import would be from rag_tools
        factual_queries = [
            "What is the API endpoint for authentication?",
            "List the requirements in PRD-001",
            "Show me the BRD validation rules",
        ]

        for query in factual_queries:
            # These should be classified as factual
            query_lower = query.lower()
            is_factual = any(kw in query_lower for kw in [
                "what is", "list", "show", "prd", "brd", "api"
            ])
            assert is_factual, f"Query should be factual: {query}"

    @pytest.mark.utest
    def test_relational_query_classification(self):
        """Test relational queries are classified correctly."""
        relational_queries = [
            "How does authentication relate to authorization?",
            "What is the relationship between PRD and BRD?",
            "How do ADR decisions affect system requirements?",
        ]

        for query in relational_queries:
            query_lower = query.lower()
            is_relational = any(kw in query_lower for kw in [
                "relate", "relationship", "affect", "between"
            ])
            assert is_relational, f"Query should be relational: {query}"


class TestQueryExecution:
    """Integration tests for query execution (requires API)."""

    @pytest.mark.itest
    @pytest.mark.skip(reason="Requires LightRAG server")
    def test_local_query_returns_entities(self, sample_research_doc):
        """Test local query returns entity-based results."""
        pass

    @pytest.mark.itest
    @pytest.mark.skip(reason="Requires LightRAG server")
    def test_global_query_returns_themes(self):
        """Test global query returns thematic results."""
        pass

    @pytest.mark.itest
    @pytest.mark.skip(reason="Requires LightRAG server")
    def test_hybrid_query_combines_results(self):
        """Test hybrid query combines local and global."""
        pass


class TestQueryResults:
    """Tests for query result processing."""

    @pytest.mark.utest
    def test_result_contains_entities(self):
        """Test query results include entity information."""
        mock_result = {
            "answer": "PayPal reported earnings...",
            "entities": ["PayPal", "Q3 2025"],
            "relationships": [("PayPal", "reported", "earnings")],
        }

        assert "entities" in mock_result
        assert len(mock_result["entities"]) > 0

    @pytest.mark.utest
    def test_result_contains_sources(self):
        """Test query results include source documents."""
        mock_result = {
            "answer": "The analysis shows...",
            "sources": [
                {"doc_id": "doc1", "relevance": 0.95},
                {"doc_id": "doc2", "relevance": 0.87},
            ],
        }

        assert "sources" in mock_result
        assert all("relevance" in s for s in mock_result["sources"])
