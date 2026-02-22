"""Pytest fixtures for RAG layer tests."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def sample_earnings_yaml():
    """Load sample earnings analysis fixture."""
    fixture_path = (
        Path(__file__).parent.parent.parent
        / "graph"
        / "tests"
        / "fixtures"
        / "sample_earnings.yaml"
    )
    with open(fixture_path) as f:
        return f.read()


@pytest.fixture
def sample_trade_yaml():
    """Load sample trade journal fixture."""
    fixture_path = (
        Path(__file__).parent.parent.parent / "graph" / "tests" / "fixtures" / "sample_trade.yaml"
    )
    with open(fixture_path) as f:
        return f.read()


@pytest.fixture
def mock_database():
    """Mock PostgreSQL connection for unit tests."""
    with patch("psycopg.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_connect.return_value.__exit__ = MagicMock(return_value=False)

        yield {
            "connection": mock_conn,
            "cursor": mock_cursor,
        }


@pytest.fixture
def mock_embedding_client():
    """Mock embedding client for tests."""
    with patch("rag.embedding_client.requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {"embeddings": [[0.1] * 1536]}
        mock_post.return_value = mock_response
        yield mock_post


@pytest.fixture
def mock_config():
    """Mock RAG configuration."""
    config = {
        "embedding": {
            "default_provider": "openai",
            "fallback_chain": ["openai", "ollama"],
            "dimensions": 1536,
            "timeout_seconds": 30,
            "openai": {
                "model": "text-embedding-3-large",
            },
            "ollama": {
                "base_url": "http://localhost:11434",
                "model": "nomic-embed-text",
            },
        },
        "chunking": {
            "max_tokens": 1500,
            "min_tokens": 50,
        },
        "logging": {
            "embed_log": "logs/rag_embed.jsonl",
        },
    }
    with patch("rag.embed._config", config):
        with patch("rag.embedding_client._config", config):
            yield config


@pytest.fixture
def sample_embedding():
    """Sample 1536-dimensional embedding vector."""
    return [0.1 + i * 0.001 for i in range(1536)]
