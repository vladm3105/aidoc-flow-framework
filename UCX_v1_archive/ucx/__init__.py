"""
UCX - Unified Context Framework

AI-driven document lifecycle management with multi-persona authoring, review, and remediation.

Example:
    >>> from ucx import UCXAutopilot, UCXConfig
    >>>
    >>> # Configure and run autopilot
    >>> config = UCXConfig(model="opus", max_iterations=3)
    >>> autopilot = UCXAutopilot(config)
    >>> result = autopilot.run(
    ...     doc_type="brd",
    ...     target="docs/01_BRD/BRD-01",
    ...     from_ref="docs/00_REF/"
    ... )
    >>> print(f"Status: {result.status}, Score: {result.score}")

    >>> # Use individual phases
    >>> from ucx import UCCPhase, UCRPhase, UCRemPhase
    >>> ucc = UCCPhase()
    >>> ucr = UCRPhase()
    >>> ucrem = UCRemPhase()
"""

from ucx.version import __version__

# API Classes
from ucx.api.autopilot import UCXAutopilot
from ucx.api.creation import UCCPhase
from ucx.api.review import UCRPhase
from ucx.api.remediation import UCRemPhase

# Configuration
from ucx.config.settings import UCXConfig

# Models
from ucx.models.document import Document
from ucx.models.review import ReviewResult
from ucx.models.fix import FixProposal
from ucx.models.drift_cache import DriftCache
from ucx.models.enums import DocType, Status, Confidence

# Exceptions
from ucx.exceptions import (
    UCXError,
    ConfigurationError,
    ValidationError,
    AIClientError,
    PromptError,
)

__all__ = [
    # Version
    "__version__",
    # API
    "UCXAutopilot",
    "UCCPhase",
    "UCRPhase",
    "UCRemPhase",
    # Config
    "UCXConfig",
    # Models
    "Document",
    "ReviewResult",
    "FixProposal",
    "DriftCache",
    "DocType",
    "Status",
    "Confidence",
    # Exceptions
    "UCXError",
    "ConfigurationError",
    "ValidationError",
    "AIClientError",
    "PromptError",
]
