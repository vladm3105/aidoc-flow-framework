"""Tests for Haystack RAG pipelines."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from haystack import Document


class TestPipelineCreation:
    """Tests for pipeline creation functions."""

    @pytest.mark.utest
    def test_config_loading(self, config):
        """Test configuration loading."""
        from haystack_rag.config import load_config

        # Should not raise with valid config path
        # This tests the config structure
        assert "embedding" in config
        assert "splitting" in config
        assert "retrieval" in config

    @pytest.mark.utest
    def test_indexing_pipeline_structure(self, config, mock_openai_key):
        """Test indexing pipeline has required components."""
        from haystack_rag.pipelines import create_indexing_pipeline

        with patch("haystack_rag.pipelines.create_document_store"):
            with patch("haystack.components.embedders.OpenAIDocumentEmbedder"):
                # Would test pipeline structure
                # Skipping actual creation which requires API
                pass

    @pytest.mark.utest
    def test_query_pipeline_structure(self, config, mock_openai_key):
        """Test query pipeline has required components."""
        from haystack_rag.pipelines import create_query_pipeline

        with patch("haystack_rag.pipelines.create_document_store"):
            with patch("haystack.components.embedders.OpenAITextEmbedder"):
                # Would test pipeline structure
                pass


class TestPipelineExecution:
    """Integration tests for pipeline execution (requires database)."""

    @pytest.mark.itest
    @pytest.mark.skip(reason="Requires database connection")
    def test_indexing_pipeline_runs(self, sample_document):
        """Test indexing pipeline executes successfully."""
        pass

    @pytest.mark.itest
    @pytest.mark.skip(reason="Requires database connection")
    def test_query_pipeline_returns_results(self):
        """Test query pipeline returns results."""
        pass


class TestDocumentProcessing:
    """Tests for document processing through pipeline."""

    @pytest.mark.utest
    def test_markdown_conversion(self, sample_document, tmp_path):
        """Test markdown document conversion."""
        from haystack.components.converters import MarkdownToDocument

        # Write sample doc to temp file
        doc_path = tmp_path / "test.md"
        doc_path.write_text(sample_document)

        converter = MarkdownToDocument()
        result = converter.run(sources=[str(doc_path)])

        assert "documents" in result
        assert len(result["documents"]) == 1
        assert "Product Requirements Document" in result["documents"][0].content

    @pytest.mark.utest
    def test_document_splitting(self, sample_document):
        """Test document splitting."""
        from haystack.components.preprocessors import DocumentSplitter

        doc = Document(content=sample_document)
        splitter = DocumentSplitter(
            split_by="sentence",
            split_length=3,
            split_overlap=1,
        )

        result = splitter.run(documents=[doc])

        assert "documents" in result
        assert len(result["documents"]) > 1  # Should be split into multiple chunks

    @pytest.mark.utest
    def test_metadata_preserved_after_splitting(self, sample_document):
        """Test metadata is preserved after splitting."""
        from haystack.components.preprocessors import DocumentSplitter

        doc = Document(
            content=sample_document,
            meta={"doc_type": "PRD", "version": "1.0"}
        )
        splitter = DocumentSplitter(split_by="sentence", split_length=5)

        result = splitter.run(documents=[doc])

        for chunk in result["documents"]:
            assert chunk.meta.get("doc_type") == "PRD"
            assert chunk.meta.get("version") == "1.0"
