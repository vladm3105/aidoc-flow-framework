"""UCX configuration with Pydantic settings."""

from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RetryConfig(BaseModel):
    """Retry policy configuration for AI requests."""

    max_attempts: int = Field(
        default=3,
        description="Maximum retry attempts",
        ge=1,
        le=10,
    )
    base_delay: float = Field(
        default=1.0,
        description="Base delay in seconds",
        ge=0.1,
    )
    max_delay: float = Field(
        default=60.0,
        description="Maximum delay in seconds",
    )
    exponential_base: float = Field(
        default=2.0,
        description="Exponential backoff base",
    )
    jitter: bool = Field(
        default=True,
        description="Add random jitter to delays",
    )


class RateLimitConfig(BaseModel):
    """Rate limiting configuration for Claude API."""

    requests_per_minute: int = Field(
        default=50,
        description="Maximum requests per minute",
        ge=1,
    )
    tokens_per_minute: int = Field(
        default=100000,
        description="Maximum tokens per minute",
        ge=1000,
    )
    concurrent_requests: int = Field(
        default=5,
        description="Maximum concurrent requests",
        ge=1,
    )
    burst_allowance: float = Field(
        default=1.2,
        description="Burst multiplier for short periods",
        ge=1.0,
    )


class TokenConfig(BaseModel):
    """Token budget configuration for LLM requests."""

    max_input_tokens: int = Field(
        default=100000,
        description="Maximum input tokens per request",
    )
    max_output_tokens: int = Field(
        default=8000,
        description="Maximum output tokens per request",
    )
    budget_per_session: Optional[int] = Field(
        default=None,
        description="Total token budget per session (None = unlimited)",
    )
    truncation_strategy: str = Field(
        default="smart",
        description="Content truncation strategy (smart, head, tail, middle)",
    )
    reserve_output_tokens: int = Field(
        default=2000,
        description="Tokens to reserve for output when truncating input",
    )


class OTELConfig(BaseModel):
    """OpenTelemetry configuration."""

    enabled: bool = Field(
        default=True,
        description="Enable OpenTelemetry tracing and metrics",
    )
    endpoint: Optional[str] = Field(
        default=None,
        description="OTLP exporter endpoint (e.g., http://localhost:4317)",
    )
    service_name: str = Field(
        default="ucx",
        description="Service name for OTEL traces",
    )
    service_version: str = Field(
        default="1.0.0",
        description="Service version for OTEL traces",
    )
    llm_capture_content: bool = Field(
        default=False,
        description="Capture LLM prompt/response content in traces (privacy risk)",
    )
    sample_rate: float = Field(
        default=1.0,
        description="Trace sampling rate (0.0 to 1.0)",
        ge=0.0,
        le=1.0,
    )
    console_export: bool = Field(
        default=False,
        description="Export traces to console (for debugging)",
    )


class UCXConfig(BaseSettings):
    """
    UCX configuration with environment variable support.

    All settings can be overridden via environment variables with UCX_ prefix.

    Example:
        >>> config = UCXConfig(model="sonnet", max_iterations=5)
        >>> print(config.model)
        'sonnet'

        # Or via environment variables:
        # UCX_MODEL=sonnet UCX_MAX_ITER=5 python -m ucx ...
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="UCX_",
        extra="ignore",
    )

    # AI Model Settings
    model: str = Field(
        default="opus",
        description="AI model (opus, sonnet, haiku) or LiteLLM format (provider/model)",
    )
    api_base: Optional[str] = Field(
        default=None,
        description="Custom API base URL (for proxies, Ollama, Azure, etc.)",
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key (defaults to provider-specific env var)",
    )

    # Autopilot Settings
    max_iterations: int = Field(
        default=3,
        alias="max_iter",
        description="Maximum review/fix cycles",
        ge=1,
        le=10,
    )
    min_score: int = Field(
        default=90,
        description="Minimum passing score (0-100)",
        ge=0,
        le=100,
    )
    batch_size: int = Field(
        default=3,
        description="Number of documents per batch",
        ge=1,
        le=10,
    )

    # Drift Monitoring
    skip_drift: bool = Field(
        default=False,
        description="Disable drift monitoring",
    )
    hash_algorithm: str = Field(
        default="sha256",
        description="Hash algorithm for drift detection",
    )

    # Skill Loading
    load_skills: bool = Field(
        default=True,
        description="Enable skill loading into prompts",
    )
    skill_dir: Optional[Path] = Field(
        default=None,
        description="Custom skill definitions directory",
    )

    # Prompts
    prompt_dir: Optional[Path] = Field(
        default=None,
        description="Custom prompt templates directory",
    )
    template_dir: Optional[Path] = Field(
        default=None,
        description="Custom document templates directory",
    )

    # Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR)",
    )
    log_format: str = Field(
        default="console",
        description="Log format (console, json)",
    )

    # Output
    output_dir: Optional[Path] = Field(
        default=None,
        description="Default output directory for generated files",
    )

    # Validation
    skip_validation: bool = Field(
        default=False,
        description="Skip validation phase in UCR",
    )

    # Nested Configuration
    retry: RetryConfig = Field(
        default_factory=RetryConfig,
        description="Retry policy configuration",
    )
    rate_limit: RateLimitConfig = Field(
        default_factory=RateLimitConfig,
        description="Rate limiting configuration",
    )
    tokens: TokenConfig = Field(
        default_factory=TokenConfig,
        description="Token budget configuration",
    )
    otel: OTELConfig = Field(
        default_factory=OTELConfig,
        description="OpenTelemetry configuration",
    )

    # Parallel Processing
    max_workers: int = Field(
        default=3,
        description="Maximum concurrent workers for batch processing",
        ge=1,
        le=10,
    )

    # Checkpointing
    enable_checkpoints: bool = Field(
        default=False,
        description="Enable checkpoint/resume for long operations",
    )
    checkpoint_dir: Optional[Path] = Field(
        default=None,
        description="Directory for checkpoint files",
    )

    @classmethod
    def from_yaml(cls, path: Path) -> "UCXConfig":
        """
        Load configuration from YAML file.

        Args:
            path: Path to YAML configuration file

        Returns:
            UCXConfig instance
        """
        import yaml

        if not path.exists():
            return cls()

        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return cls(**data)

    def get_skill_dir(self) -> Path:
        """Get skill directory, using default if not set."""
        if self.skill_dir:
            return self.skill_dir
        # Default to package skills directory
        return Path(__file__).parent.parent / "skills" / "personas"

    def get_prompt_dir(self) -> Path:
        """Get prompt directory, using default if not set."""
        if self.prompt_dir:
            return self.prompt_dir
        # Default to package prompts directory
        return Path(__file__).parent.parent / "prompts" / "templates"

    def get_template_dir(self) -> Path:
        """Get template directory, using default if not set."""
        if self.template_dir:
            return self.template_dir
        # Default to framework templates
        return Path(__file__).parent.parent.parent / "templates"
