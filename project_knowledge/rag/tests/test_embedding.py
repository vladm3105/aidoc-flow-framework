"""Unit tests for rag/embedding_client.py."""

from unittest.mock import MagicMock, patch

import pytest

from rag.embedding_client import (
    EmbeddingClient,
    get_embedding,
    get_embedding_client,
)
from rag.exceptions import EmbeddingUnavailableError


class TestEmbeddingClient:
    """Tests for EmbeddingClient class."""

    def test_init_with_config(self):
        config = {
            "embedding": {
                "fallback_chain": ["ollama", "openrouter"],
                "dimensions": 768,
                "timeout_seconds": 30,
            }
        }
        client = EmbeddingClient(config=config)
        assert client.fallback_chain == ["ollama", "openrouter"]
        assert client.dimensions == 768
        assert client.timeout == 30

    def test_init_defaults(self):
        client = EmbeddingClient(config={})
        # Defaults from config file (may include fallbacks)
        assert len(client.fallback_chain) > 0  # Has at least one provider
        assert client.dimensions == 1536  # OpenAI text-embedding-3-large default
        assert client.timeout == 30


class TestOllamaEmbedding:
    """Tests for Ollama embedding."""

    @patch("requests.post")
    def test_ollama_embed_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "embeddings": [[0.1, 0.2, 0.3] * 256]  # 768 dimensions
        }
        mock_post.return_value = mock_response

        config = {
            "embedding": {
                "fallback_chain": ["ollama"],
                "dimensions": 768,
                "ollama": {
                    "base_url": "http://localhost:11434",
                    "model": "nomic-embed-text",
                },
            }
        }
        client = EmbeddingClient(config=config)
        embedding = client.get_embedding("test text")

        assert len(embedding) == 768
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "api/embed" in call_args[0][0]

    @patch("requests.post")
    def test_ollama_embed_empty_response(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"embeddings": []}
        mock_post.return_value = mock_response

        config = {
            "embedding": {
                "fallback_chain": ["ollama"],
                "dimensions": 768,
            }
        }
        client = EmbeddingClient(config=config)

        with pytest.raises(EmbeddingUnavailableError):
            client.get_embedding("test text")


class TestOpenRouterEmbedding:
    """Tests for OpenRouter embedding fallback."""

    @patch("requests.post")
    @patch.dict("os.environ", {"OPENROUTER_API_KEY": "test-key"})
    def test_openrouter_embed_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": [{"embedding": [0.1, 0.2, 0.3] * 256}]}
        mock_post.return_value = mock_response

        config = {
            "embedding": {
                "fallback_chain": ["openrouter"],
                "dimensions": 768,
                "openrouter": {
                    "model": "openai/text-embedding-3-small",
                },
            }
        }
        client = EmbeddingClient(config=config)
        embedding = client.get_embedding("test text")

        assert len(embedding) == 768
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "openrouter.ai" in call_args[0][0]


class TestFallbackChain:
    """Tests for embedding fallback behavior."""

    @patch("requests.post")
    def test_fallback_on_error(self, mock_post):
        # First call (ollama) fails, second call (openrouter) succeeds
        ollama_response = MagicMock()
        ollama_response.raise_for_status.side_effect = Exception("Ollama down")

        openrouter_response = MagicMock()
        openrouter_response.json.return_value = {"data": [{"embedding": [0.1] * 768}]}

        mock_post.side_effect = [
            Exception("Ollama down"),
            openrouter_response,
        ]

        config = {
            "embedding": {
                "fallback_chain": ["ollama", "openrouter"],
                "dimensions": 768,
                "openrouter": {"api_key": "test-key"},
            }
        }
        client = EmbeddingClient(config=config)
        embedding = client.get_embedding("test text")

        assert len(embedding) == 768
        assert mock_post.call_count == 2

    @patch("requests.post")
    def test_all_providers_fail(self, mock_post):
        mock_post.side_effect = Exception("All down")

        config = {
            "embedding": {
                "fallback_chain": ["ollama", "openrouter"],
                "dimensions": 768,
                "openrouter": {"api_key": "test-key"},
            }
        }
        client = EmbeddingClient(config=config)

        with pytest.raises(EmbeddingUnavailableError, match="All embedding providers failed"):
            client.get_embedding("test text")


class TestBatchEmbedding:
    """Tests for batch embedding."""

    @patch("requests.post")
    def test_batch_embedding(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"embeddings": [[0.1] * 768]}
        mock_post.return_value = mock_response

        config = {
            "embedding": {
                "fallback_chain": ["ollama"],
                "dimensions": 768,
            }
        }
        client = EmbeddingClient(config=config)
        embeddings = client.get_embeddings_batch(["text1", "text2", "text3"])

        assert len(embeddings) == 3
        assert mock_post.call_count == 3


class TestSingleton:
    """Tests for singleton pattern."""

    @patch("rag.embedding_client._client", None)
    @patch("rag.embedding_client._config", {})
    def test_get_embedding_client_creates_singleton(self):
        client1 = get_embedding_client()
        client2 = get_embedding_client()
        assert client1 is client2

    @patch("requests.post")
    @patch("rag.embedding_client._client", None)
    def test_convenience_get_embedding(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"embeddings": [[0.1] * 768]}
        mock_post.return_value = mock_response

        with patch(
            "rag.embedding_client._config",
            {"embedding": {"fallback_chain": ["ollama"], "dimensions": 768}},
        ):
            embedding = get_embedding("test")
            assert len(embedding) == 768
