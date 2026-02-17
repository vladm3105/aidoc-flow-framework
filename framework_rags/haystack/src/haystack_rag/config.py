"""Configuration loader for Haystack RAG service."""

import os
from pathlib import Path
from typing import Any

import yaml


def load_config(config_path: str | Path | None = None) -> dict[str, Any]:
    """Load configuration from YAML file.

    Args:
        config_path: Path to config file. Defaults to config/default.yaml.

    Returns:
        Configuration dictionary.
    """
    if config_path is None:
        config_path = Path(__file__).parent.parent.parent / "config" / "default.yaml"

    config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path) as f:
        config = yaml.safe_load(f)

    # Override with environment variables
    config = _apply_env_overrides(config)

    return config


def _apply_env_overrides(config: dict[str, Any]) -> dict[str, Any]:
    """Apply environment variable overrides to config."""
    env_mappings = {
        "OPENAI_API_KEY": ("embedding", "api_key"),
        "COHERE_API_KEY": ("retrieval", "reranker_api_key"),
        "PG_CONN_STR": ("vector_store", "connection_string"),
        "HAYHOOKS_PORT": ("server", "port"),
    }

    for env_var, config_path in env_mappings.items():
        value = os.environ.get(env_var)
        if value:
            _set_nested(config, config_path, value)

    return config


def _set_nested(d: dict, keys: tuple[str, ...], value: Any) -> None:
    """Set a nested dictionary value."""
    for key in keys[:-1]:
        d = d.setdefault(key, {})
    d[keys[-1]] = value


def get_pg_connection_string() -> str:
    """Get PostgreSQL connection string from environment."""
    return os.environ.get(
        "PG_CONN_STR",
        "postgresql://raguser:ragpass@localhost:5432/ragdb"
    )
