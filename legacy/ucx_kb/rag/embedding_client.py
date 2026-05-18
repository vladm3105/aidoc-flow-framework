"""Embedding client with Ollama-first, LiteLLM/OpenRouter fallback."""

import logging
import os
from pathlib import Path

import requests
import yaml

from .exceptions import EmbeddingUnavailableError

log = logging.getLogger(__name__)

# Default embedding dimensions (1536 for pgvector index compatibility)
DEFAULT_EMBED_DIMS = 1536  # OpenAI text-embedding-3-large with truncation

# Load configuration
_config_path = Path(__file__).parent / "config.yaml"
_config: dict = {}


def _expand_env_vars(content: str) -> str:
    """Expand ${VAR} and ${VAR:-default} patterns in config."""
    import re

    pattern = r"\$\{([A-Z_][A-Z0-9_]*)(?::-([^}]*))?\}"

    def replacer(match):
        var_name = match.group(1)
        default = match.group(2) if match.group(2) is not None else ""
        return os.getenv(var_name, default)

    return re.sub(pattern, replacer, content)


if _config_path.exists():
    with open(_config_path) as f:
        config_content = f.read()
        config_content = _expand_env_vars(config_content)
        _config = yaml.safe_load(config_content)


def get_embed_dimensions() -> int:
    """Get configured embedding dimensions."""
    return int(_config.get("embedding", {}).get("dimensions", DEFAULT_EMBED_DIMS))


class EmbeddingClient:
    """Embedding with configurable default provider and fallback chain."""

    def __init__(self, config: dict | None = None):
        """Initialize embedding client."""
        self.config = config or _config
        embedding_config = self.config.get("embedding", {})
        # Use default_provider first, then fallback chain
        default_provider = embedding_config.get("default_provider", "").strip("}")
        fallback_chain = embedding_config.get("fallback_chain", ["ollama"])
        # Build provider chain: default_provider first (if set), then fallback_chain
        if default_provider and default_provider not in fallback_chain:
            self.fallback_chain = [default_provider] + fallback_chain
        elif default_provider:
            # Move default_provider to front of fallback_chain
            self.fallback_chain = [default_provider] + [
                p for p in fallback_chain if p != default_provider
            ]
        else:
            self.fallback_chain = fallback_chain
        self.dimensions = int(embedding_config.get("dimensions", DEFAULT_EMBED_DIMS))
        self.timeout = int(embedding_config.get("timeout_seconds", 30))

    def get_embedding(self, text: str) -> list[float]:
        """
        Get embedding vector for text.
        Tries each provider in fallback chain until success.

        Args:
            text: Input text to embed

        Returns:
            Embedding vector (list of floats)

        Raises:
            EmbeddingUnavailableError: If all providers fail
        """
        errors = []

        for provider in self.fallback_chain:
            try:
                if provider == "ollama":
                    return self._ollama_embed(text)
                elif provider == "openrouter":
                    return self._openrouter_embed(text)
                elif provider == "openai":
                    return self._openai_embed(text)
                else:
                    log.warning(f"Unknown embedding provider: {provider}")
                    continue
            except Exception as e:
                log.warning(f"Embedding via {provider} failed: {e}")
                errors.append(f"{provider}: {e}")
                continue

        raise EmbeddingUnavailableError(f"All embedding providers failed: {'; '.join(errors)}")

    def get_embeddings_batch(self, texts: list[str], batch_size: int = 10) -> list[list[float]]:
        """
        Batch embedding for multiple texts.

        Args:
            texts: List of texts to embed
            batch_size: Number of texts per batch

        Returns:
            List of embedding vectors
        """
        embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]

            for text in batch:
                embedding = self.get_embedding(text)
                embeddings.append(embedding)

        return embeddings

    def _ollama_embed(self, text: str) -> list[float]:
        """Local Ollama embedding ($0)."""
        cfg = self.config.get("embedding", {}).get("ollama", {})
        base_url = cfg.get("base_url", "http://localhost:11434")
        model = cfg.get("model", "nomic-embed-text")

        response = requests.post(
            f"{base_url}/api/embed",
            json={"model": model, "input": text},
            timeout=self.timeout,
        )
        response.raise_for_status()

        result = response.json()
        embeddings = result.get("embeddings", [])

        if not embeddings:
            raise ValueError("No embeddings returned from Ollama")

        embedding = embeddings[0]

        if len(embedding) != self.dimensions:
            log.warning(f"Dimension mismatch: got {len(embedding)}, expected {self.dimensions}")

        return embedding

    def _openrouter_embed(self, text: str) -> list[float]:
        """OpenRouter embedding (cloud fallback)."""
        cfg = self.config.get("embedding", {}).get("openrouter", {})
        api_key = cfg.get("api_key") or os.getenv("OPENROUTER_API_KEY", "")
        model = cfg.get("model", "openai/text-embedding-3-small")

        if not api_key:
            raise ValueError("OpenRouter API key not configured")

        response = requests.post(
            "https://openrouter.ai/api/v1/embeddings",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "input": text,
            },
            timeout=self.timeout,
        )
        response.raise_for_status()

        result = response.json()
        embedding = result["data"][0]["embedding"]

        # Truncate to configured dimensions if needed
        return embedding[: self.dimensions]

    def _openai_embed(self, text: str) -> list[float]:
        """OpenAI embedding (alternative fallback)."""
        cfg = self.config.get("embedding", {}).get("openai", {})
        api_key = cfg.get("api_key") or os.getenv("OPENAI_API_KEY", "")
        model = cfg.get("model", "text-embedding-3-small")

        if not api_key:
            raise ValueError("OpenAI API key not configured")

        response = requests.post(
            "https://api.openai.com/v1/embeddings",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "input": text,
                "dimensions": self.dimensions,
            },
            timeout=self.timeout,
        )
        response.raise_for_status()

        result = response.json()
        return result["data"][0]["embedding"]


# Singleton instance
_client: EmbeddingClient | None = None


def get_embedding_client() -> EmbeddingClient:
    """Get singleton embedding client."""
    global _client
    if _client is None:
        _client = EmbeddingClient()
    return _client


def get_embedding(text: str) -> list[float]:
    """Convenience function to get embedding."""
    return get_embedding_client().get_embedding(text)


def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """Convenience function to get batch embeddings."""
    return get_embedding_client().get_embeddings_batch(texts)
