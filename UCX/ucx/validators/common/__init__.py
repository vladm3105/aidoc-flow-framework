"""Common validation utilities for UCX validators.

This module provides shared infrastructure for all document type validators:
- Error codes and severity handling
- File utilities (companion detection, source file collection)
- Shared regex patterns
- YAML frontmatter parsing
- Tiered validation result classes
"""

from ucx.validators.common.error_codes import (
    Severity,
    ErrorCode,
    ERROR_REGISTRY,
    get_error,
    format_error,
    calculate_exit_code,
    list_codes_by_type,
)
from ucx.validators.common.file_utils import (
    is_companion_report,
    collect_source_files,
    is_section_based_layout,
)
from ucx.validators.common.patterns import (
    YAML_FRONTMATTER_PATTERN,
    ELEMENT_ID_PATTERNS,
    SECTION_HEADING_PATTERN,
    TAG_PATTERNS,
)
from ucx.validators.common.frontmatter import (
    parse_frontmatter,
    validate_frontmatter_fields,
)
from ucx.validators.common.result import (
    ValidationIssue,
    UnifiedValidationResult,
    ValidationTier,
)
from ucx.validators.common.links import (
    validate_links,
    extract_markdown_links,
)
from ucx.validators.common.references import (
    validate_forward_references,
    get_document_type_from_path,
    get_document_layer,
    LAYER_MAP,
)
from ucx.validators.common.diagrams import (
    validate_diagrams,
    extract_mermaid_blocks,
    parse_mermaid_nodes,
)

__all__ = [
    # Error codes
    "Severity",
    "ErrorCode",
    "ERROR_REGISTRY",
    "get_error",
    "format_error",
    "calculate_exit_code",
    "list_codes_by_type",
    # File utilities
    "is_companion_report",
    "collect_source_files",
    "is_section_based_layout",
    # Patterns
    "YAML_FRONTMATTER_PATTERN",
    "ELEMENT_ID_PATTERNS",
    "SECTION_HEADING_PATTERN",
    "TAG_PATTERNS",
    # Frontmatter
    "parse_frontmatter",
    "validate_frontmatter_fields",
    # Results
    "ValidationIssue",
    "UnifiedValidationResult",
    "ValidationTier",
    # Tier 2: Links
    "validate_links",
    "extract_markdown_links",
    # Tier 2: Forward References
    "validate_forward_references",
    "get_document_type_from_path",
    "get_document_layer",
    "LAYER_MAP",
    # Tier 2: Diagrams
    "validate_diagrams",
    "extract_mermaid_blocks",
    "parse_mermaid_nodes",
]
