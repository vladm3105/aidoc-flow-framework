"""
UCX Category-Weighted Scoring Module.

Implements a unified scoring system that maps review findings to standardized
categories with per-category weights and caps, ensuring consistent scores
across all document types.

Version: 1.12.0 (PLAN-002)

Usage:
    from ucx.scoring import (
        ScoringCalculator,
        Finding,
        calculate_weighted_score,
        load_weights,
        Category,
    )

    # Create findings
    findings = [
        Finding(id="BRD.01.01.01", priority="P0", text="Missing scope", persona="auditor"),
        Finding(id="AUD-P1-002", priority="P1", text="KYC timeline unclear", persona="auditor"),
    ]

    # Calculate weighted score
    result = calculate_weighted_score(findings, doc_type="brd")

    print(f"Score: {result.weighted_score}/100 ({result.pass_status})")
    print(result.get_category_summary_table())
"""

from .categories import (
    Category,
    CategoryDefinition,
    CATEGORY_DEFINITIONS,
    PERSONA_CATEGORY_MAP,
    categorize_by_element_code,
    categorize_by_keyword,
    extract_element_code,
    get_category_by_id,
    get_category_by_name,
    get_persona_primary_category,
)
from .calculator import (
    CategoryScore,
    Finding,
    ScoringCalculator,
    ScoringResult,
    calculate_legacy_score,
    calculate_weighted_score,
)
from .conflicts import (
    CategoryConflictResolver,
    ConflictResolution,
    ResolutionMethod,
    parse_category_tag,
    strip_category_tag,
)
from .weights import (
    CategoryWeight,
    DocumentTypeWeights,
    ScoringConfigError,
    ScoringThresholds,
    get_all_document_types,
    get_weight_for_category,
    load_weights,
    validate_config_file,
    DEFAULT_WEIGHTS,
)

__all__ = [
    # Categories
    "Category",
    "CategoryDefinition",
    "CATEGORY_DEFINITIONS",
    "PERSONA_CATEGORY_MAP",
    "categorize_by_element_code",
    "categorize_by_keyword",
    "extract_element_code",
    "get_category_by_id",
    "get_category_by_name",
    "get_persona_primary_category",
    # Calculator
    "CategoryScore",
    "Finding",
    "ScoringCalculator",
    "ScoringResult",
    "calculate_legacy_score",
    "calculate_weighted_score",
    # Conflicts
    "CategoryConflictResolver",
    "ConflictResolution",
    "ResolutionMethod",
    "parse_category_tag",
    "strip_category_tag",
    # Weights
    "CategoryWeight",
    "DocumentTypeWeights",
    "ScoringConfigError",
    "ScoringThresholds",
    "get_all_document_types",
    "get_weight_for_category",
    "load_weights",
    "validate_config_file",
    "DEFAULT_WEIGHTS",
]

__version__ = "1.12.0"
