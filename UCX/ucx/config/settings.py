"""UCX v2 settings — loaded from environment variables or .env file.

Environment variable prefix: UCX_

Example .env:
    UCX_AI_MODEL=claude-3-7-sonnet-20250219
    UCX_AI_API_KEY=sk-ant-...
    UCX_LOG_LEVEL=INFO
"""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class UCXSettings(BaseSettings):
    """UCX runtime configuration.

    All fields can be set via environment variables (prefix: UCX_).
    """

    model_config = SettingsConfigDict(
        env_prefix="UCX_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # AI provider
    ai_model: str = Field(
        default="claude-3-7-sonnet-20250219",
        description="LiteLLM model identifier for review and remediation AI calls.",
    )
    ai_api_key: str | None = Field(
        default=None,
        description="API key for the AI provider. Leave unset to use environment default.",
    )
    ai_max_tokens: int = Field(
        default=8192,
        description="Maximum tokens per AI call.",
    )

    # Validation
    max_fix_iterations: int = Field(
        default=3,
        description="Maximum validate → fix cycles before giving up.",
    )

    # Observability
    log_level: str = Field(
        default="INFO",
        description="Logging level: DEBUG | INFO | WARNING | ERROR",
    )
    log_format: str = Field(
        default="json",
        description="Log format: json | text",
    )
