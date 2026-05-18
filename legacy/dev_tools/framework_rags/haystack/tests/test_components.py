"""Tests for custom Haystack components."""

import pytest
from haystack import Document

from haystack_rag.components.metadata_enricher import MetadataEnricher


class TestMetadataEnricher:
    """Tests for MetadataEnricher component."""

    def test_extract_frontmatter(self):
        """Test YAML frontmatter extraction."""
        enricher = MetadataEnricher()
        content = """---
title: Test Document
doc_type: PRD
version: "1.0"
author: Test Author
---

# Content here
"""
        doc = Document(content=content, meta={})
        result = enricher.run([doc])

        assert len(result["documents"]) == 1
        meta = result["documents"][0].meta
        assert meta.get("doc_type") == "PRD"
        assert meta.get("version") == "1.0"
        assert meta.get("author") == "Test Author"

    def test_extract_from_path(self):
        """Test metadata extraction from file path."""
        enricher = MetadataEnricher()
        doc = Document(
            content="# Test content",
            meta={"file_path": "/opt/data/project/docs/02_PRD/PRD-001_auth.md"}
        )
        result = enricher.run([doc])

        meta = result["documents"][0].meta
        assert meta.get("doc_type") == "PRD"
        assert meta.get("layer") == 2

    def test_layer_inference(self):
        """Test layer inference from doc_type."""
        enricher = MetadataEnricher()

        test_cases = [
            ("BRD", 1),
            ("PRD", 2),
            ("EARS", 3),
            ("BDD", 4),
            ("ADR", 5),
            ("SYS", 6),
            ("REQ", 7),
            ("CTR", 8),
            ("SPEC", 9),
            ("TSPEC", 10),
            ("TASKS", 11),
        ]

        for doc_type, expected_layer in test_cases:
            doc = Document(
                content="# Test",
                meta={"file_path": f"/docs/{doc_type}-001.md"}
            )
            result = enricher.run([doc])
            assert result["documents"][0].meta.get("layer") == expected_layer

    def test_multiple_documents(self):
        """Test processing multiple documents."""
        enricher = MetadataEnricher()
        docs = [
            Document(content="Doc 1", meta={"file_path": "PRD-001.md"}),
            Document(content="Doc 2", meta={"file_path": "BRD-001.md"}),
            Document(content="Doc 3", meta={"file_path": "SPEC-001.md"}),
        ]
        result = enricher.run(docs)

        assert len(result["documents"]) == 3
        assert result["documents"][0].meta["doc_type"] == "PRD"
        assert result["documents"][1].meta["doc_type"] == "BRD"
        assert result["documents"][2].meta["doc_type"] == "SPEC"
