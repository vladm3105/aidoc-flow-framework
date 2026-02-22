"""Unit tests for rag/search.py with mocked database."""

from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from rag.exceptions import RAGUnavailableError
from rag.models import RAGStats, SearchResult
from rag.search import (
    _build_hybrid_query,
    _build_search_query,
    get_document_chunks,
    get_learnings_for_topic,
    get_rag_stats,
    get_similar_analyses,
    hybrid_search,
    list_documents,
    semantic_search,
)


class TestBuildSearchQuery:
    """Tests for search query building."""

    def test_basic_query(self):
        embedding = [0.1] * 768
        sql, params = _build_search_query(embedding, None, None, None, None, None, top_k=5)

        assert "embedding <=> %s::vector" in sql
        assert "LIMIT %s" in sql
        assert params[-1] == 5

    def test_ticker_filter(self):
        embedding = [0.1] * 768
        sql, params = _build_search_query(
            embedding,
            ticker="NVDA",
            doc_type=None,
            section=None,
            date_from=None,
            date_to=None,
            top_k=5,
        )

        assert "c.ticker = %s" in sql
        assert "NVDA" in params

    def test_doc_type_filter(self):
        embedding = [0.1] * 768
        sql, params = _build_search_query(
            embedding,
            ticker=None,
            doc_type="earnings-analysis",
            section=None,
            date_from=None,
            date_to=None,
            top_k=5,
        )

        assert "c.doc_type = %s" in sql
        assert "earnings-analysis" in params

    def test_section_filter(self):
        embedding = [0.1] * 768
        sql, params = _build_search_query(
            embedding,
            ticker=None,
            doc_type=None,
            section="thesis",
            date_from=None,
            date_to=None,
            top_k=5,
        )

        assert "c.section_label ILIKE %s" in sql
        assert "%thesis%" in params

    def test_date_range_filter(self):
        embedding = [0.1] * 768
        sql, params = _build_search_query(
            embedding,
            ticker=None,
            doc_type=None,
            section=None,
            date_from=date(2025, 1, 1),
            date_to=date(2025, 12, 31),
            top_k=5,
        )

        assert "c.doc_date >= %s" in sql
        assert "c.doc_date <= %s" in sql


class TestSemanticSearch:
    """Tests for semantic search."""

    @patch("rag.search.get_embedding")
    @patch("psycopg.connect")
    def test_search_returns_results(self, mock_connect, mock_embed):
        mock_embed.return_value = [0.1] * 768

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            (
                "doc-001",
                "/path/to/doc.yaml",
                "earnings-analysis",
                "NVDA",
                date(2025, 1, 1),
                "Thesis",
                "Long NVDA",
                100,
                0.2,
            ),  # distance 0.2 = similarity 0.8
        ]
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_connect.return_value.__exit__ = MagicMock(return_value=False)

        results = semantic_search("NVDA earnings analysis", ticker="NVDA")

        assert len(results) == 1
        assert results[0].doc_id == "doc-001"
        assert results[0].similarity == 0.8

    @patch("rag.search.get_embedding")
    @patch("psycopg.connect")
    def test_search_filters_low_similarity(self, mock_connect, mock_embed):
        mock_embed.return_value = [0.1] * 768

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            (
                "doc-001",
                "/path/to/doc.yaml",
                "earnings-analysis",
                "NVDA",
                date(2025, 1, 1),
                "Thesis",
                "Long NVDA",
                100,
                0.8,
            ),  # distance 0.8 = similarity 0.2 (below threshold)
        ]
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_connect.return_value.__exit__ = MagicMock(return_value=False)

        results = semantic_search("unrelated query", min_similarity=0.3)

        assert len(results) == 0

    @patch("rag.search.get_embedding")
    def test_search_raises_on_embed_failure(self, mock_embed):
        mock_embed.side_effect = Exception("Embedding failed")

        with pytest.raises(RAGUnavailableError, match="embed query"):
            semantic_search("test query")


class TestGetSimilarAnalyses:
    """Tests for similar analyses lookup."""

    @patch("rag.search.semantic_search")
    def test_finds_similar_analyses(self, mock_search):
        mock_search.return_value = [
            SearchResult(
                doc_id="doc-001",
                file_path="/path/to/doc.yaml",
                doc_type="earnings-analysis",
                ticker="NVDA",
                doc_date=date(2025, 1, 1),
                section_label="Thesis",
                content="Long NVDA",
                similarity=0.85,
            )
        ]

        results = get_similar_analyses("NVDA", "earnings-analysis", top_k=3)

        assert len(results) == 1
        mock_search.assert_called_once()
        call_kwargs = mock_search.call_args[1]
        assert call_kwargs["ticker"] == "NVDA"
        assert call_kwargs["top_k"] == 3


class TestGetLearningsForTopic:
    """Tests for topic-based learnings lookup."""

    @patch("rag.search.semantic_search")
    def test_finds_learnings(self, mock_search):
        mock_search.return_value = []

        results = get_learnings_for_topic("disposition effect", top_k=5)

        mock_search.assert_called_once()
        call_kwargs = mock_search.call_args[1]
        assert call_kwargs["doc_type"] == "learning"
        assert call_kwargs["top_k"] == 5


class TestGetRagStats:
    """Tests for RAG statistics."""

    @patch("psycopg.connect")
    def test_get_stats(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        # Mock multiple cursor calls in order:
        # 1. doc count: fetchone
        # 2. chunk count: fetchone
        # 3. doc types: fetchall
        # 4. tickers: fetchall
        # 5. last_embed: fetchone
        # 6. model info: fetchone
        mock_cursor.fetchone.side_effect = [
            (10,),  # doc count
            (50,),  # chunk count
            (None,),  # last_embed (can be None datetime)
            ("nomic-embed-text", "1.0.0"),  # model info
        ]
        mock_cursor.fetchall.side_effect = [
            [("earnings-analysis", 5), ("trade-journal", 5)],  # doc types
            [("NVDA",), ("AMD",)],  # tickers
        ]

        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_connect.return_value.__exit__ = MagicMock(return_value=False)

        stats = get_rag_stats()

        assert isinstance(stats, RAGStats)
        assert stats.document_count == 10
        assert stats.chunk_count == 50


class TestListDocuments:
    """Tests for document listing."""

    @patch("psycopg.connect")
    def test_list_all_documents(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            ("doc-001", "/path/doc1.yaml", "earnings-analysis", "NVDA", date(2025, 1, 1), 5, None),
            ("doc-002", "/path/doc2.yaml", "trade-journal", "AMD", date(2025, 1, 2), 3, None),
        ]
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_connect.return_value.__exit__ = MagicMock(return_value=False)

        docs = list_documents()

        assert len(docs) == 2
        assert docs[0]["doc_id"] == "doc-001"

    @patch("psycopg.connect")
    def test_list_filtered_by_ticker(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            ("doc-001", "/path/doc1.yaml", "earnings-analysis", "NVDA", date(2025, 1, 1), 5, None),
        ]
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_connect.return_value.__exit__ = MagicMock(return_value=False)

        docs = list_documents(ticker="NVDA")

        # Verify ticker filter was applied
        call_args = mock_cursor.execute.call_args
        assert "ticker = %s" in call_args[0][0]


class TestGetDocumentChunks:
    """Tests for chunk retrieval."""

    @patch("psycopg.connect")
    def test_get_chunks(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            ("thesis", "Thesis", 0, "Long NVDA", 50),
            ("risks", "Risks", 0, "Export controls", 30),
        ]
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_connect.return_value.__exit__ = MagicMock(return_value=False)

        chunks = get_document_chunks("doc-001")

        assert len(chunks) == 2
        assert chunks[0]["section_path"] == "thesis"
        assert chunks[1]["content_tokens"] == 30


class TestBuildHybridQuery:
    """Tests for hybrid search query building."""

    def test_basic_hybrid_query(self):
        embedding = [0.1] * 768
        sql, params = _build_hybrid_query(
            query="NVDA earnings",
            embedding=embedding,
            ticker=None,
            doc_type=None,
            section=None,
            date_from=None,
            date_to=None,
            top_k=5,
            vector_weight=0.7,
            bm25_weight=0.3,
        )

        # Check CTEs are present
        assert "WITH vector_results AS" in sql
        assert "bm25_results AS" in sql
        assert "FULL OUTER JOIN" in sql

        # Check RRF scoring formula
        assert "60.0 + COALESCE(v.v_rank" in sql
        assert "60.0 + COALESCE(b.b_rank" in sql

        # Check ordering
        assert "ORDER BY hybrid_score DESC" in sql

    def test_hybrid_query_with_ticker_filter(self):
        embedding = [0.1] * 768
        sql, params = _build_hybrid_query(
            query="earnings thesis",
            embedding=embedding,
            ticker="NVDA",
            doc_type=None,
            section=None,
            date_from=None,
            date_to=None,
            top_k=5,
            vector_weight=0.7,
            bm25_weight=0.3,
        )

        assert "c.ticker = %s" in sql
        assert "NVDA" in params

    def test_hybrid_query_weights_in_params(self):
        embedding = [0.1] * 768
        sql, params = _build_hybrid_query(
            query="test",
            embedding=embedding,
            ticker=None,
            doc_type=None,
            section=None,
            date_from=None,
            date_to=None,
            top_k=10,
            vector_weight=0.8,
            bm25_weight=0.2,
        )

        # Weights should be in params
        assert 0.8 in params
        assert 0.2 in params
        assert 10 in params  # top_k


class TestHybridSearch:
    """Tests for hybrid search function."""

    @patch("rag.search.get_embedding")
    @patch("psycopg.connect")
    def test_hybrid_search_returns_results(self, mock_connect, mock_embed):
        mock_embed.return_value = [0.1] * 768

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            (
                "doc-001",
                "/path/to/doc.yaml",
                "earnings-analysis",
                "NVDA",
                date(2025, 1, 1),
                "Thesis",
                "Long NVDA on data center",
                100,
                0.025,
            ),
        ]
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_connect.return_value.__exit__ = MagicMock(return_value=False)

        results = hybrid_search("NVDA earnings", ticker="NVDA")

        assert len(results) == 1
        assert results[0].doc_id == "doc-001"
        assert results[0].similarity == 0.025  # hybrid score

    @patch("rag.search.get_embedding")
    @patch("psycopg.connect")
    def test_hybrid_search_filters_low_scores(self, mock_connect, mock_embed):
        mock_embed.return_value = [0.1] * 768

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            (
                "doc-001",
                "/path",
                "earnings-analysis",
                "NVDA",
                date(2025, 1, 1),
                "Thesis",
                "content",
                100,
                0.005,
            ),  # Below min_score
        ]
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_connect.return_value.__exit__ = MagicMock(return_value=False)

        results = hybrid_search("test", min_score=0.01)

        assert len(results) == 0  # Filtered out

    @patch("rag.search.get_embedding")
    @patch("rag.search.semantic_search")
    @patch("psycopg.connect")
    def test_hybrid_search_falls_back_on_error(self, mock_connect, mock_semantic, mock_embed):
        mock_embed.return_value = [0.1] * 768
        mock_connect.return_value.__enter__ = MagicMock(
            side_effect=Exception("content_tsv column not found")
        )
        mock_semantic.return_value = [
            SearchResult(
                doc_id="fallback-001",
                file_path="/path",
                doc_type="earnings-analysis",
                ticker="NVDA",
                doc_date=None,
                section_label="Thesis",
                content="Fallback result",
                similarity=0.8,
            )
        ]

        results = hybrid_search("test query")

        # Should fall back to semantic search
        mock_semantic.assert_called_once()
        assert len(results) == 1
        assert results[0].doc_id == "fallback-001"

    @patch("rag.search.get_embedding")
    def test_hybrid_search_raises_on_embed_failure(self, mock_embed):
        mock_embed.side_effect = Exception("Embedding failed")

        with pytest.raises(RAGUnavailableError, match="embed query"):
            hybrid_search("test query")
