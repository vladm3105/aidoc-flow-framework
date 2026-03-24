"""Common validation utilities for UCX validators.

This module provides shared infrastructure for all document type validators:

Tier 1 (Core, blocking):
- Error codes and severity handling (error_codes.py)
- File utilities: companion detection, source file collection (file_utils.py)
- Shared regex patterns (patterns.py)
- YAML frontmatter parsing (frontmatter.py)
- Tiered validation result classes (result.py)

Tier 2 (Advisory, non-blocking):
- Markdown link validation (links.py)
- SDD forward reference validation (references.py)
- Mermaid/SVG diagram consistency (diagrams.py)

Version: 1.9.2 (introduced in 1.9.0)

Usage:
    from ucx.validators.common import (
        UnifiedValidationResult,
        ValidationIssue,
        ValidationTier,
        validate_links,
        validate_forward_references,
        validate_diagrams,
    )
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
