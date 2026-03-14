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

    # AI Client Settings
    ai_mode: str = Field(
        default="cli",
        description="AI client mode: 'cli' for CLI agents, 'api' for LiteLLM API calls",
    )
    cli_tool: str = Field(
        default="claude",
        description="CLI tool to use in cli mode (claude, gemini, ollama, aider)",
    )
    cli_timeout: int = Field(
        default=600,
        description="CLI command timeout in seconds",
        ge=30,
        le=1800,
    )
    model: str = Field(
        default="opus",
        description="AI model: opus/sonnet/haiku for Claude CLI, or LiteLLM format (provider/model) for API mode",
    )
    api_base: Optional[str] = Field(
        default=None,
        description="Custom API base URL (API mode only - for proxies, Ollama, Azure, etc.)",
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key (API mode only - defaults to provider-specific env var)",
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

    # Project Directory (REQUIRED for analysis)
    project_dir: Optional[Path] = Field(
        default=None,
        description="Project root directory containing docs/UCX/. REQUIRED for review/fix/remediation.",
    )

    # Prompts
    prompt_dir: Optional[Path] = Field(
        default=None,
        description="Framework prompt templates directory (reference only, not for analysis)",
    )
    project_prompt_dir: Optional[Path] = Field(
        default=None,
        description="DEPRECATED - use project_dir instead",
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

    # Web Search
    enable_web_search: bool = Field(
        default=False,
        description="Enable web search for deeper analysis (fact-checking, best practices, solutions)",
    )
    web_search_domains: Optional[list[str]] = Field(
        default=None,
        description="Allowed domains for web search (None = all domains)",
    )
    web_search_blocked_domains: Optional[list[str]] = Field(
        default=None,
        description="Blocked domains for web search",
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

    # Scoring (v1.12.0+)
    scoring_method: str = Field(
        default="weighted",
        description="Scoring method: 'weighted' (category-weighted with caps) or 'legacy' (simple deduction)",
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
        # Default to framework skills directory (/UCX/skills/)
        # Note: ucx/skills/personas/ is deprecated as of v1.7.2
        return Path(__file__).parent.parent.parent / "skills"

    def get_prompt_dir(self) -> Path:
        """Get framework prompt directory, using default if not set."""
        if self.prompt_dir:
            return self.prompt_dir
        # Default to package prompts directory
        return Path(__file__).parent.parent / "prompts" / "templates"

    def get_project_dir(self) -> Optional[Path]:
        """
        Get project root directory.

        CRITICAL: This is REQUIRED for review/fix/remediation operations.
        The project directory must contain docs/UCX/ with
        project-specific prompts and personas.

        Returns:
            Project root path, or None if not configured
        """
        if self.project_dir:
            return self.project_dir

        # Legacy: check project_prompt_dir and infer project root
        if self.project_prompt_dir:
            # project_prompt_dir might be docs/UCX/review
            # Try to infer project root
            path = self.project_prompt_dir
            for _ in range(4):  # Check up to 4 levels up
                if (path / "docs" / "UCX").exists():
                    return path
                path = path.parent

        return None

    def get_project_prompt_dir(self) -> Optional[Path]:
        """DEPRECATED: Use get_project_dir() instead."""
        project_dir = self.get_project_dir()
        if project_dir:
            return project_dir / "docs" / "UCX" / "review"
        return self.project_prompt_dir

    def get_template_dir(self) -> Path:
        """Get template directory, using default if not set."""
        if self.template_dir:
            return self.template_dir
        # Default to framework templates
        return Path(__file__).parent.parent.parent / "templates"

    def get_ai_client(self):
        """
        Get AI client based on configuration.

        Returns:
            AI client instance (CLIClient or LiteLLMClient)

        Example:
            >>> config = UCXConfig(ai_mode="cli", cli_tool="claude")
            >>> client = config.get_ai_client()

            >>> config = UCXConfig(ai_mode="api", model="openai/gpt-4o")
            >>> client = config.get_ai_client()

            >>> # With web search enabled
            >>> config = UCXConfig(ai_mode="cli", enable_web_search=True)
            >>> client = config.get_ai_client()
        """
        from ucx.ai import get_client

        return get_client(
            mode=self.ai_mode,
            cli_tool=self.cli_tool,
            timeout=self.cli_timeout,
            model=self.model,
            api_key=self.api_key,
            api_base=self.api_base,
            enable_web_search=self.enable_web_search,
        )
