"""UCX configuration.

Provides configuration management for UCX Framework.
"""

from ucx.config.settings import (
    UCXConfig,
    RetryConfig,
    RateLimitConfig,
    TokenConfig,
    OTELConfig,
)
from ucx.config.layer_skills import LAYER_SKILLS, FIXER_SKILLS, get_skills_for_phase
from ucx.config.defaults import (
    Defaults,
    get_defaults,
    get_model_context_size,
    get_model_output_limit,
    get_doc_layer,
    get_required_sections,
)
from ucx.config.schema import (
    ConfigFileSchema,
    load_config_file,
    find_config_file,
    generate_config_template,
)

__all__ = [
    # Settings
    "UCXConfig",
    "RetryConfig",
    "RateLimitConfig",
    "TokenConfig",
    "OTELConfig",
    # Layer skills
    "LAYER_SKILLS",
    "FIXER_SKILLS",
    "get_skills_for_phase",
    # Defaults
    "Defaults",
    "get_defaults",
    "get_model_context_size",
    "get_model_output_limit",
    "get_doc_layer",
    "get_required_sections",
    # Schema
    "ConfigFileSchema",
    "load_config_file",
    "find_config_file",
    "generate_config_template",
]
