"""Configuration file schema for UCX.

Defines the schema for UCX configuration files (ucx.yaml, ucx.json).
"""

from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


class ConfigFileSchema(BaseModel):
    """
    Schema for UCX configuration files.

    Supports both YAML and JSON formats.

    Example ucx.yaml:
        model: sonnet
        max_iterations: 5
        min_score: 85
        retry:
          max_attempts: 5
          base_delay: 2.0
        otel:
          enabled: true
          endpoint: http://localhost:4317
    """

    # Core settings
    model: Optional[str] = Field(
        default=None,
        description="AI model (opus, sonnet, haiku)",
    )
    max_iterations: Optional[int] = Field(
        default=None,
        alias="max_iter",
        ge=1,
        le=10,
    )
    min_score: Optional[int] = Field(
        default=None,
        ge=0,
        le=100,
    )
    batch_size: Optional[int] = Field(
        default=None,
        ge=1,
        le=10,
    )

    # Drift settings
    skip_drift: Optional[bool] = None
    hash_algorithm: Optional[str] = None

    # Skills & prompts
    load_skills: Optional[bool] = None
    skill_dir: Optional[str] = None
    prompt_dir: Optional[str] = None
    template_dir: Optional[str] = None

    # Logging
    log_level: Optional[str] = None
    log_format: Optional[str] = None

    # Output
    output_dir: Optional[str] = None

    # Validation
    skip_validation: Optional[bool] = None

    # Parallel processing
    max_workers: Optional[int] = Field(default=None, ge=1, le=10)

    # Checkpointing
    enable_checkpoints: Optional[bool] = None
    checkpoint_dir: Optional[str] = None

    # Nested configs
    retry: Optional[dict[str, Any]] = None
    rate_limit: Optional[dict[str, Any]] = None
    tokens: Optional[dict[str, Any]] = None
    otel: Optional[dict[str, Any]] = None

    @field_validator("model")
    @classmethod
    def validate_model(cls, v: Optional[str]) -> Optional[str]:
        """Validate model name."""
        if v is not None:
            valid_models = ["opus", "sonnet", "haiku"]
            if v.lower() not in valid_models:
                raise ValueError(f"model must be one of: {', '.join(valid_models)}")
            return v.lower()
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: Optional[str]) -> Optional[str]:
        """Validate log level."""
        if v is not None:
            valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
            if v.upper() not in valid_levels:
                raise ValueError(f"log_level must be one of: {', '.join(valid_levels)}")
            return v.upper()
        return v

    @field_validator("log_format")
    @classmethod
    def validate_log_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate log format."""
        if v is not None:
            valid_formats = ["console", "json"]
            if v.lower() not in valid_formats:
                raise ValueError(f"log_format must be one of: {', '.join(valid_formats)}")
            return v.lower()
        return v


def load_config_file(path: Path) -> dict[str, Any]:
    """
    Load and validate configuration from file.

    Args:
        path: Path to config file (YAML or JSON)

    Returns:
        Validated configuration dictionary

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file format is invalid
    """
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    suffix = path.suffix.lower()

    if suffix in (".yaml", ".yml"):
        import yaml

        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    elif suffix == ".json":
        import json

        data = json.loads(path.read_text(encoding="utf-8"))
    else:
        raise ValueError(f"Unsupported config format: {suffix}")

    # Validate against schema
    schema = ConfigFileSchema(**data)
    return schema.model_dump(exclude_none=True)


def find_config_file(start_dir: Optional[Path] = None) -> Optional[Path]:
    """
    Find configuration file by searching up directory tree.

    Looks for: ucx.yaml, ucx.yml, ucx.json, .ucx.yaml, .ucx.yml, .ucx.json

    Args:
        start_dir: Directory to start search (defaults to cwd)

    Returns:
        Path to config file if found, None otherwise
    """
    if start_dir is None:
        start_dir = Path.cwd()

    config_names = [
        "ucx.yaml",
        "ucx.yml",
        "ucx.json",
        ".ucx.yaml",
        ".ucx.yml",
        ".ucx.json",
    ]

    current = start_dir.resolve()

    while current != current.parent:
        for name in config_names:
            config_path = current / name
            if config_path.exists():
                return config_path
        current = current.parent

    return None


def generate_config_template(include_comments: bool = True) -> str:
    """
    Generate a configuration file template.

    Args:
        include_comments: Include descriptive comments

    Returns:
        YAML configuration template string
    """
    if include_comments:
        return '''# UCX Configuration File
# Place this file as ucx.yaml in your project root

# AI Model Settings
# model: opus                 # AI model (opus, sonnet, haiku)

# Autopilot Settings
# max_iterations: 3           # Maximum review/fix cycles (1-10)
# min_score: 90               # Minimum passing score (0-100)
# batch_size: 3               # Documents per batch (1-10)

# Drift Monitoring
# skip_drift: false           # Disable drift monitoring
# hash_algorithm: sha256      # Hash algorithm for drift detection

# Skills & Prompts
# load_skills: true           # Enable skill loading
# skill_dir: null             # Custom skills directory
# prompt_dir: null            # Custom prompts directory
# template_dir: null          # Custom templates directory

# Logging
# log_level: INFO             # DEBUG, INFO, WARNING, ERROR
# log_format: console         # console, json

# Output
# output_dir: null            # Default output directory

# Validation
# skip_validation: false      # Skip validation in UCR

# Parallel Processing
# max_workers: 3              # Concurrent workers (1-10)

# Checkpointing
# enable_checkpoints: false   # Enable checkpoint/resume
# checkpoint_dir: null        # Checkpoint directory

# Retry Configuration
# retry:
#   max_attempts: 3           # Maximum retry attempts
#   base_delay: 1.0           # Base delay in seconds
#   max_delay: 60.0           # Maximum delay
#   exponential_base: 2.0     # Backoff multiplier
#   jitter: true              # Add random jitter

# Rate Limiting
# rate_limit:
#   requests_per_minute: 50
#   tokens_per_minute: 100000
#   concurrent_requests: 5
#   burst_allowance: 1.2

# Token Budget
# tokens:
#   max_input_tokens: 100000
#   max_output_tokens: 8000
#   truncation_strategy: smart
#   reserve_output_tokens: 2000

# OpenTelemetry
# otel:
#   enabled: true
#   endpoint: null            # OTLP endpoint (e.g., http://localhost:4317)
#   service_name: ucx
#   llm_capture_content: false
#   sample_rate: 1.0
#   console_export: false
'''
    else:
        return '''model: opus
max_iterations: 3
min_score: 90
batch_size: 3
skip_drift: false
load_skills: true
log_level: INFO
log_format: console
max_workers: 3
enable_checkpoints: false
'''
