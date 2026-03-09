"""Default configuration values for UCX.

Provides centralized default values for all UCX settings.
"""

from dataclasses import dataclass, field
from typing import Any


# ============================================================================
# Model Defaults
# ============================================================================

DEFAULT_MODEL = "opus"
AVAILABLE_MODELS = ["opus", "sonnet", "haiku"]

MODEL_CONTEXTS = {
    "opus": 200000,
    "sonnet": 200000,
    "haiku": 200000,
}

MODEL_OUTPUT_LIMITS = {
    "opus": 16000,
    "sonnet": 8192,
    "haiku": 8192,
}


# ============================================================================
# Autopilot Defaults
# ============================================================================

DEFAULT_MAX_ITERATIONS = 3
DEFAULT_MIN_SCORE = 90
DEFAULT_BATCH_SIZE = 3

# Score thresholds
SCORE_THRESHOLD_PASS = 90
SCORE_THRESHOLD_WARN = 70
SCORE_THRESHOLD_FAIL = 0


# ============================================================================
# Retry Defaults
# ============================================================================

DEFAULT_RETRY_ATTEMPTS = 3
DEFAULT_RETRY_BASE_DELAY = 1.0
DEFAULT_RETRY_MAX_DELAY = 60.0
DEFAULT_RETRY_EXPONENTIAL_BASE = 2.0
DEFAULT_RETRY_JITTER = True

# Retryable error patterns
RETRYABLE_ERROR_PATTERNS = [
    "rate limit",
    "rate_limit",
    "timeout",
    "connection",
    "overloaded",
    "503",
    "529",
]

RETRYABLE_EXCEPTION_TYPES = (
    ConnectionError,
    TimeoutError,
)


# ============================================================================
# Rate Limiting Defaults
# ============================================================================

DEFAULT_REQUESTS_PER_MINUTE = 50
DEFAULT_TOKENS_PER_MINUTE = 100000
DEFAULT_CONCURRENT_REQUESTS = 5
DEFAULT_BURST_ALLOWANCE = 1.2


# ============================================================================
# Token Defaults
# ============================================================================

DEFAULT_MAX_INPUT_TOKENS = 100000
DEFAULT_MAX_OUTPUT_TOKENS = 8000
DEFAULT_RESERVE_OUTPUT_TOKENS = 2000
DEFAULT_TRUNCATION_STRATEGY = "smart"

TRUNCATION_STRATEGIES = ["smart", "head", "tail", "middle"]


# ============================================================================
# OTEL Defaults
# ============================================================================

DEFAULT_OTEL_ENABLED = True
DEFAULT_OTEL_SERVICE_NAME = "ucx"
DEFAULT_OTEL_SERVICE_VERSION = "1.0.0"
DEFAULT_OTEL_SAMPLE_RATE = 1.0
DEFAULT_OTEL_CAPTURE_CONTENT = False


# ============================================================================
# Logging Defaults
# ============================================================================

DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_LOG_FORMAT = "console"
LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR"]
LOG_FORMATS = ["console", "json"]


# ============================================================================
# Processing Defaults
# ============================================================================

DEFAULT_MAX_WORKERS = 3
DEFAULT_HASH_ALGORITHM = "sha256"


# ============================================================================
# Document Type Defaults
# ============================================================================

DOC_TYPES = [
    "brd",
    "prd",
    "ears",
    "bdd",
    "adr",
    "sys",
    "req",
    "ctr",
    "spec",
    "tspec",
]

DOC_TYPE_LAYERS = {
    "brd": 1,
    "prd": 2,
    "ears": 3,
    "bdd": 4,
    "adr": 5,
    "sys": 6,
    "req": 7,
    "ctr": 8,
    "spec": 9,
    "tspec": 10,
}


# ============================================================================
# File Patterns
# ============================================================================

DEFAULT_DOC_PATTERN = "*.md"
DEFAULT_FEATURE_PATTERN = "*.feature"
DEFAULT_YAML_PATTERN = "*.yaml"

DRIFT_CACHE_FILE = ".drift_cache.json"
CHECKPOINT_FILE = ".checkpoint.json"


# ============================================================================
# Validation Defaults
# ============================================================================

DEFAULT_ID_PATTERN = r"^[A-Z]{2,5}-\d{2,3}(\.\d{2,3})?$"

# Section patterns by document type
REQUIRED_SECTIONS = {
    "brd": [
        "Executive Summary",
        "Business Objectives",
        "Stakeholder Analysis",
        "Success Metrics",
    ],
    "prd": [
        "Overview",
        "User Stories",
        "Acceptance Criteria",
        "Dependencies",
    ],
    "ears": [
        "Requirements",
    ],
    "bdd": [
        "Feature",
        "Scenario",
    ],
    "adr": [
        "Context",
        "Decision",
        "Consequences",
    ],
    "sys": [
        "System Requirements",
        "Interface Requirements",
    ],
    "req": [
        "Requirements",
    ],
    "ctr": [
        "Schema",
        "Validation",
    ],
    "spec": [
        "Specification",
        "Implementation",
    ],
    "tspec": [
        "Test Specification",
        "Test Cases",
    ],
}


# ============================================================================
# Default Configuration Bundle
# ============================================================================

@dataclass
class Defaults:
    """Bundled default values for easy access."""

    # Models
    model: str = DEFAULT_MODEL
    available_models: list[str] = field(default_factory=lambda: AVAILABLE_MODELS)

    # Autopilot
    max_iterations: int = DEFAULT_MAX_ITERATIONS
    min_score: int = DEFAULT_MIN_SCORE
    batch_size: int = DEFAULT_BATCH_SIZE

    # Retry
    retry_attempts: int = DEFAULT_RETRY_ATTEMPTS
    retry_base_delay: float = DEFAULT_RETRY_BASE_DELAY
    retry_max_delay: float = DEFAULT_RETRY_MAX_DELAY

    # Rate limiting
    requests_per_minute: int = DEFAULT_REQUESTS_PER_MINUTE
    tokens_per_minute: int = DEFAULT_TOKENS_PER_MINUTE
    concurrent_requests: int = DEFAULT_CONCURRENT_REQUESTS

    # Tokens
    max_input_tokens: int = DEFAULT_MAX_INPUT_TOKENS
    max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS
    reserve_output_tokens: int = DEFAULT_RESERVE_OUTPUT_TOKENS

    # Logging
    log_level: str = DEFAULT_LOG_LEVEL
    log_format: str = DEFAULT_LOG_FORMAT

    # Processing
    max_workers: int = DEFAULT_MAX_WORKERS
    hash_algorithm: str = DEFAULT_HASH_ALGORITHM


def get_defaults() -> Defaults:
    """Get default configuration values."""
    return Defaults()


def get_model_context_size(model: str) -> int:
    """Get context window size for a model."""
    return MODEL_CONTEXTS.get(model.lower(), MODEL_CONTEXTS[DEFAULT_MODEL])


def get_model_output_limit(model: str) -> int:
    """Get output token limit for a model."""
    return MODEL_OUTPUT_LIMITS.get(model.lower(), MODEL_OUTPUT_LIMITS[DEFAULT_MODEL])


def get_doc_layer(doc_type: str) -> int:
    """Get SDD layer for a document type."""
    return DOC_TYPE_LAYERS.get(doc_type.lower(), 0)


def get_required_sections(doc_type: str) -> list[str]:
    """Get required sections for a document type."""
    return REQUIRED_SECTIONS.get(doc_type.lower(), [])
