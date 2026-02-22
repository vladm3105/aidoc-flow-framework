"""Unit tests for rag/embed.py with mocked database."""

from datetime import date
from unittest.mock import MagicMock, mock_open, patch

import pytest

from rag.embed import (
    _compute_file_hash,
    _infer_doc_type,
    _parse_date,
    delete_document,
    embed_document,
    embed_text,
    reembed_all,
)
from rag.exceptions import EmbedError


class TestParseDate:
    """Tests for date parsing."""

    def test_iso_format(self):
        result = _parse_date("2025-01-15")
        assert result == date(2025, 1, 15)

    def test_compact_format(self):
        result = _parse_date("20250115")
        assert result == date(2025, 1, 15)

    def test_us_format(self):
        result = _parse_date("01/15/2025")
        assert result == date(2025, 1, 15)

    def test_none_input(self):
        assert _parse_date(None) is None

    def test_invalid_format(self):
        assert _parse_date("invalid") is None


class TestInferDocType:
    """Tests for document type inference."""

    def test_earnings_path(self):
        assert _infer_doc_type("/knowledge/analysis/earnings/NVDA.yaml") == "earnings-analysis"

    def test_trades_path(self):
        assert _infer_doc_type("/knowledge/trades/NVDA_20250101.yaml") == "trade-journal"

    def test_research_path(self):
        assert _infer_doc_type("/analysis/research/macro.yaml") == "research-analysis"

    def test_unknown_path(self):
        assert _infer_doc_type("/random/file.yaml") == "unknown"


class TestComputeFileHash:
    """Tests for file hash computation."""

    @patch("builtins.open", mock_open(read_data=b"test content"))
    def test_compute_hash(self):
        hash_val = _compute_file_hash("/path/to/file.yaml")
        assert len(hash_val) == 64  # SHA-256 hex digest

    @patch("builtins.open", mock_open(read_data=b"test content"))
    def test_same_content_same_hash(self):
        hash1 = _compute_file_hash("/file1.yaml")
        hash2 = _compute_file_hash("/file2.yaml")
        assert hash1 == hash2


class TestEmbedDocument:
    """Tests for document embedding (mocked)."""

    @patch("rag.embed.is_real_document")
    def test_rejects_template(self, mock_is_real):
        mock_is_real.return_value = False

        with pytest.raises(EmbedError, match="template"):
            embed_document("/path/to/template.yaml")

    @patch("rag.embed.is_real_document")
    def test_rejects_missing_file(self, mock_is_real):
        mock_is_real.return_value = True

        with pytest.raises(EmbedError, match="not found"):
            embed_document("/nonexistent/file.yaml")

    @patch("rag.embed.is_real_document", return_value=True)
    @patch("rag.embed._get_document_by_id")
    @patch("rag.embed._compute_file_hash")
    @patch("pathlib.Path.exists", return_value=True)
    @patch("builtins.open", mock_open(read_data="ticker: NVDA\n_meta:\n  id: test-001"))
    def test_skips_unchanged_document(self, mock_exists, mock_hash, mock_get_doc, mock_is_real):
        mock_hash.return_value = "abc123"
        mock_get_doc.return_value = {"file_hash": "abc123", "chunk_count": 3}

        result = embed_document("/path/to/doc.yaml")

        assert result.error_message == "unchanged"
        assert result.doc_id == "test-001"

    @patch("rag.embed.is_real_document", return_value=True)
    @patch("rag.embed._get_document_by_id", return_value=None)
    @patch("rag.embed._compute_file_hash", return_value="abc123")
    @patch("rag.embed.chunk_yaml_document")
    @patch("rag.embed.get_embeddings_batch")
    @patch("rag.embed._store_document")
    @patch("rag.embed._log_embed")
    @patch("pathlib.Path.exists", return_value=True)
    @patch(
        "builtins.open",
        mock_open(read_data="ticker: NVDA\n_meta:\n  id: test-001\n  doc_type: earnings-analysis"),
    )
    def test_embeds_new_document(
        self,
        mock_exists,
        mock_log,
        mock_store,
        mock_embed_batch,
        mock_chunk,
        mock_hash,
        mock_get_doc,
        mock_is_real,
    ):
        from rag.models import ChunkResult

        mock_chunk.return_value = [
            ChunkResult(
                section_path="thesis",
                section_label="Thesis",
                chunk_index=0,
                content="Long NVDA",
                content_tokens=10,
                prepared_text="[earnings-analysis] [NVDA] [Thesis]\nLong NVDA",
            )
        ]
        mock_embed_batch.return_value = [[0.1] * 768]

        result = embed_document("/path/to/doc.yaml")

        assert result.doc_id == "test-001"
        assert result.chunk_count == 1
        mock_store.assert_called_once()


class TestEmbedText:
    """Tests for text embedding."""

    @patch("rag.embed.get_embedding")
    @patch("rag.embed._store_document")
    def test_embeds_raw_text(self, mock_store, mock_embed):
        mock_embed.return_value = [0.1] * 768

        result = embed_text(
            text="NVDA is a strong buy",
            doc_id="ext-001",
            doc_type="external",
            ticker="NVDA",
        )

        assert result.doc_id == "ext-001"
        assert result.chunk_count == 1
        mock_store.assert_called_once()


class TestDeleteDocument:
    """Tests for document deletion."""

    @patch("psycopg.connect")
    def test_delete_existing_document(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1,)  # Document found
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_connect.return_value.__exit__ = MagicMock(return_value=False)

        result = delete_document("test-001")

        assert result is True

    @patch("psycopg.connect")
    def test_delete_nonexistent_document(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None  # Document not found
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_connect.return_value.__exit__ = MagicMock(return_value=False)

        result = delete_document("nonexistent")

        assert result is False


class TestReembedAll:
    """Tests for bulk re-embedding."""

    @patch("psycopg.connect")
    @patch("rag.embed.embed_document")
    @patch("pathlib.Path.exists", return_value=True)
    def test_reembed_all_documents(self, mock_exists, mock_embed, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            ("/path/to/doc1.yaml",),
            ("/path/to/doc2.yaml",),
        ]
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_connect.return_value.__exit__ = MagicMock(return_value=False)

        count = reembed_all()

        assert count == 2
        assert mock_embed.call_count == 2

    @patch("psycopg.connect")
    def test_reembed_with_version_filter(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_connect.return_value.__exit__ = MagicMock(return_value=False)

        count = reembed_all(version="1.0.0")

        assert count == 0
        # Verify query included version filter
        call_args = mock_cursor.execute.call_args
        assert "embed_version" in call_args[0][0]
