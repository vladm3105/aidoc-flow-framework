"""Pytest configuration for Haystack RAG tests."""

import os
import sys
from pathlib import Path

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def sample_document():
    """Sample markdown document for testing."""
    return """---
title: Test PRD Document
doc_type: PRD
version: "1.0"
---

# Product Requirements Document

## Overview

This is a test document for the Haystack RAG service.

## Requirements

1. The system shall support markdown documents
2. The system shall extract metadata from frontmatter
3. The system shall split documents into chunks
"""


@pytest.fixture
def config():
    """Test configuration."""
    return {
        "embedding": {
            "model": "text-embedding-3-small",
            "dimensions": 1536,
        },
        "splitting": {
            "split_by": "sentence",
            "split_length": 5,
            "split_overlap": 1,
        },
        "retrieval": {
            "vector_top_k": 5,
            "reranker_top_k": 3,
        },
    }


@pytest.fixture
def mock_openai_key(monkeypatch):
    """Set mock OpenAI API key for testing."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key-for-testing")
