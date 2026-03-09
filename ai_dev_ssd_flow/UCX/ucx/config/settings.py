"""UCX configuration with Pydantic settings."""

from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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
        description="AI model to use (opus, sonnet, haiku)",
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
