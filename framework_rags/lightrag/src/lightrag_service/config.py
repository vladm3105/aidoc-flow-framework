"""Configuration loader for LightRAG service."""

import os
from pathlib import Path
from typing import Any


def load_env_config(env_path: str | Path | None = None) -> dict[str, Any]:
    """Load configuration from environment file.

    Args:
        env_path: Path to .env file. Defaults to config/default.env.

    Returns:
        Configuration dictionary.
    """
    config = {}

    # Load from file if exists
    if env_path:
        env_path = Path(env_path)
        if env_path.exists():
            config = _parse_env_file(env_path)

    # Override with actual environment variables
    env_mappings = {
        # Server
        "HOST": "host",
        "PORT": "port",
        "WORKING_DIR": "working_dir",
        "INPUT_DIR": "input_dir",
        # LLM
        "LLM_BINDING": "llm_binding",
        "LLM_MODEL": "llm_model",
        "LLM_TIMEOUT": "llm_timeout",
        # Embedding
        "EMBEDDING_BINDING": "embedding_binding",
        "EMBEDDING_MODEL": "embedding_model",
        "EMBEDDING_DIM": "embedding_dim",
        # Storage
        "LIGHTRAG_KV_STORAGE": "kv_storage",
        "LIGHTRAG_VECTOR_STORAGE": "vector_storage",
        "LIGHTRAG_GRAPH_STORAGE": "graph_storage",
        # PostgreSQL
        "POSTGRES_HOST": "postgres_host",
        "POSTGRES_PORT": "postgres_port",
        "POSTGRES_USER": "postgres_user",
        "POSTGRES_PASSWORD": "postgres_password",
        "POSTGRES_DATABASE": "postgres_database",
        # Neo4j
        "NEO4J_URI": "neo4j_uri",
        "NEO4J_USERNAME": "neo4j_username",
        "NEO4J_PASSWORD": "neo4j_password",
        # Query
        "DEFAULT_QUERY_MODE": "default_query_mode",
        "TOP_K": "top_k",
        # Entity extraction
        "CHUNK_SIZE": "chunk_size",
        "CHUNK_OVERLAP_SIZE": "chunk_overlap_size",
        # Auth
        "LIGHTRAG_API_KEY": "api_key",
        # Reranker
        "RERANK_BINDING": "rerank_binding",
        "RERANK_MODEL": "rerank_model",
        "RERANK_TOP_K": "rerank_top_k",
    }

    for env_var, config_key in env_mappings.items():
        value = os.environ.get(env_var)
        if value:
            # Convert numeric values
            if config_key in ("port", "embedding_dim", "top_k", "chunk_size",
                             "chunk_overlap_size", "rerank_top_k", "llm_timeout"):
                try:
                    value = int(value)
                except ValueError:
                    pass
            config[config_key] = value

    return config


def _parse_env_file(env_path: Path) -> dict[str, Any]:
    """Parse .env file into dictionary.

    Args:
        env_path: Path to .env file.

    Returns:
        Dictionary of environment variables.
    """
    config = {}
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith("#"):
                continue
            # Parse key=value
            if "=" in line:
                key, value = line.split("=", 1)
                config[key.strip()] = value.strip()
    return config


def get_neo4j_config() -> dict[str, str]:
    """Get Neo4j connection configuration."""
    return {
        "uri": os.environ.get("NEO4J_URI", "bolt://localhost:7687"),
        "username": os.environ.get("NEO4J_USERNAME", "neo4j"),
        "password": os.environ.get("NEO4J_PASSWORD", "neo4jpass"),
    }


def get_postgres_config() -> dict[str, Any]:
    """Get PostgreSQL connection configuration."""
    return {
        "host": os.environ.get("POSTGRES_HOST", "localhost"),
        "port": int(os.environ.get("POSTGRES_PORT", "5432")),
        "user": os.environ.get("POSTGRES_USER", "raguser"),
        "password": os.environ.get("POSTGRES_PASSWORD", "ragpass"),
        "database": os.environ.get("POSTGRES_DATABASE", "ragdb"),
    }
