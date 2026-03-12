"""
UCX Category Weight Configuration and Validation.

Handles loading, validation, and merging of scoring weights
from default config and project overrides.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import yaml

from .categories import Category

logger = logging.getLogger(__name__)


class ScoringConfigError(Exception):
    """Raised when scoring configuration is invalid."""

    pass


@dataclass
class CategoryWeight:
    """Weight configuration for a single category."""

    weight: float  # 0.0 to 1.0
    max_deduction: int  # Maximum points that can be deducted
    element_codes: list[int]
    keywords: list[str]
    description: str

    @property
    def weight_percent(self) -> float:
        """Return weight as percentage (0-100)."""
        return self.weight * 100


@dataclass
class ScoringThresholds:
    """Score thresholds for pass/warn/fail."""

    pass_threshold: int = 85
    warn_threshold: int = 70
    fail_threshold: int = 0


@dataclass
class DocumentTypeWeights:
    """Complete weight configuration for a document type."""

    doc_type: str
    categories: dict[str, CategoryWeight]
    thresholds: ScoringThresholds

    def validate(self) -> None:
        """
        Validate that weights sum to 100%.

        Raises:
            ScoringConfigError: If weights don't sum to 1.0 (100%).
        """
        total = sum(cat.weight for cat in self.categories.values())
        if abs(total - 1.0) > 0.001:
            raise ScoringConfigError(
                f"{self.doc_type.upper()} weights sum to {total*100:.1f}%, must be 100%"
            )


# Default weights for all document types (from PLAN-002)
DEFAULT_WEIGHTS: dict[str, dict[str, float]] = {
    "brd": {
        "functional": 0.25,
        "quality": 0.15,
        "compliance": 0.20,
        "constraints": 0.10,
        "integration": 0.10,
        "acceptance": 0.10,
        "risk": 0.05,
        "architecture": 0.05,
    },
    "prd": {
        "functional": 0.30,
        "quality": 0.15,
        "compliance": 0.15,
        "constraints": 0.10,
        "integration": 0.10,
        "acceptance": 0.10,
        "risk": 0.05,
        "architecture": 0.05,
    },
    "ears": {
        "functional": 0.35,
        "quality": 0.10,
        "compliance": 0.10,
        "constraints": 0.10,
        "integration": 0.10,
        "acceptance": 0.15,
        "risk": 0.05,
        "architecture": 0.05,
    },
    "bdd": {
        "functional": 0.20,
        "quality": 0.15,
        "compliance": 0.10,
        "constraints": 0.10,
        "integration": 0.15,
        "acceptance": 0.25,
        "risk": 0.025,
        "architecture": 0.025,
    },
    "adr": {
        "functional": 0.10,
        "quality": 0.15,
        "compliance": 0.10,
        "constraints": 0.15,
        "integration": 0.15,
        "acceptance": 0.05,
        "risk": 0.15,
        "architecture": 0.15,
    },
    "sys": {
        "functional": 0.30,
        "quality": 0.20,
        "compliance": 0.10,
        "constraints": 0.10,
        "integration": 0.10,
        "acceptance": 0.10,
        "risk": 0.05,
        "architecture": 0.05,
    },
    "req": {
        "functional": 0.40,
        "quality": 0.15,
        "compliance": 0.10,
        "constraints": 0.05,
        "integration": 0.10,
        "acceptance": 0.15,
        "risk": 0.025,
        "architecture": 0.025,
    },
    "spec": {
        "functional": 0.25,
        "quality": 0.20,
        "compliance": 0.10,
        "constraints": 0.05,
        "integration": 0.15,
        "acceptance": 0.15,
        "risk": 0.05,
        "architecture": 0.05,
    },
    "ctr": {
        "functional": 0.15,
        "quality": 0.10,
        "compliance": 0.20,
        "constraints": 0.15,
        "integration": 0.20,
        "acceptance": 0.10,
        "risk": 0.05,
        "architecture": 0.05,
    },
    "tasks": {
        "functional": 0.30,
        "quality": 0.10,
        "compliance": 0.05,
        "constraints": 0.10,
        "integration": 0.15,
        "acceptance": 0.15,
        "risk": 0.10,
        "architecture": 0.05,
    },
    "tspec": {
        "functional": 0.25,
        "quality": 0.20,
        "compliance": 0.10,
        "constraints": 0.05,
        "integration": 0.15,
        "acceptance": 0.20,
        "risk": 0.025,
        "architecture": 0.025,
    },
}

# Default max deductions per category
DEFAULT_MAX_DEDUCTIONS: dict[str, int] = {
    "functional": 25,
    "quality": 15,
    "compliance": 20,
    "constraints": 10,
    "integration": 10,
    "acceptance": 10,
    "risk": 5,
    "architecture": 5,
}

# Default element codes per category
DEFAULT_ELEMENT_CODES: dict[str, list[int]] = {
    "functional": [1, 22, 24],
    "quality": [2, 91, 92, 93, 94, 95, 96, 97, 98, 99],
    "compliance": [],  # Cross-cutting, keyword-based
    "constraints": [3, 4],
    "integration": [5, 16, 20],
    "acceptance": [6, 14, 40, 41, 42, 43, 44, 45],
    "risk": [7],
    "architecture": [10, 12, 13, 32],
}

# Default compliance keywords (fintech-focused)
DEFAULT_COMPLIANCE_KEYWORDS: list[str] = [
    "FinCEN", "OFAC", "PCI-DSS", "AML", "KYC", "SAR", "CTR", "MTL",
    "BSA", "FFIEC", "SOX", "GLBA", "GDPR", "CCPA", "SOC2", "ISO27001",
]


def _build_category_weight(
    category: str,
    weight: float,
    overrides: Optional[dict[str, Any]] = None,
) -> CategoryWeight:
    """Build a CategoryWeight from defaults and optional overrides."""
    max_deduction = DEFAULT_MAX_DEDUCTIONS.get(category, 10)
    element_codes = list(DEFAULT_ELEMENT_CODES.get(category, []))
    keywords = []
    description = f"{category.title()} requirements"

    if category == "compliance":
        keywords = list(DEFAULT_COMPLIANCE_KEYWORDS)

    if overrides:
        if "max_deduction" in overrides:
            max_deduction = overrides["max_deduction"]
        if "element_codes" in overrides:
            element_codes = list(overrides["element_codes"])
        if "keywords" in overrides:
            keywords = list(overrides["keywords"])
        if "keywords_append" in overrides:
            keywords.extend(overrides["keywords_append"])
        if "description" in overrides:
            description = overrides["description"]

    return CategoryWeight(
        weight=weight,
        max_deduction=max_deduction,
        element_codes=element_codes,
        keywords=keywords,
        description=description,
    )


def load_weights(
    doc_type: str,
    config_path: Optional[Path] = None,
    project_config_path: Optional[Path] = None,
) -> DocumentTypeWeights:
    """
    Load scoring weights for a document type.

    Loads from:
    1. Built-in defaults
    2. UCX config file (if exists)
    3. Project config file (if exists)

    Args:
        doc_type: Document type (e.g., 'brd', 'prd').
        config_path: Path to UCX scoring_weights.yaml.
        project_config_path: Path to project-specific config.

    Returns:
        DocumentTypeWeights with merged configuration.

    Raises:
        ScoringConfigError: If weights don't sum to 100%.
    """
    doc_type_lower = doc_type.lower()

    # Start with defaults
    if doc_type_lower not in DEFAULT_WEIGHTS:
        logger.warning(
            f"No default weights for {doc_type}, using BRD defaults"
        )
        base_weights = DEFAULT_WEIGHTS["brd"].copy()
    else:
        base_weights = DEFAULT_WEIGHTS[doc_type_lower].copy()

    # Load and merge config files
    overrides: dict[str, Any] = {}

    for path in [config_path, project_config_path]:
        if path and path.exists():
            try:
                with open(path) as f:
                    config = yaml.safe_load(f) or {}

                # Check for industry template extends
                if "extends" in config:
                    template_name = config["extends"]
                    template_path = path.parent / "templates" / f"{template_name}.yaml"
                    if template_path.exists():
                        with open(template_path) as tf:
                            template = yaml.safe_load(tf) or {}
                            _merge_config(overrides, template)

                # Merge document-type specific config
                doc_config = config.get("document_types", {}).get(doc_type_lower, {})
                _merge_config(overrides, doc_config)

                # Merge default overrides
                default_config = config.get("defaults", {})
                _merge_config(overrides, default_config)

            except Exception as e:
                logger.warning(f"Failed to load config from {path}: {e}")

    # Build category weights
    categories: dict[str, CategoryWeight] = {}
    for cat_name, weight in base_weights.items():
        cat_overrides = overrides.get("categories", {}).get(cat_name, {})

        # Allow weight override
        if "weight" in cat_overrides:
            weight = cat_overrides["weight"]

        categories[cat_name] = _build_category_weight(cat_name, weight, cat_overrides)

    # Build thresholds
    threshold_config = overrides.get("thresholds", {})
    thresholds = ScoringThresholds(
        pass_threshold=threshold_config.get("pass", 85),
        warn_threshold=threshold_config.get("warn", 70),
        fail_threshold=threshold_config.get("fail", 0),
    )

    # Create and validate
    result = DocumentTypeWeights(
        doc_type=doc_type_lower,
        categories=categories,
        thresholds=thresholds,
    )

    result.validate()

    return result


def _merge_config(base: dict, override: dict) -> None:
    """Deep merge override into base dict (in-place)."""
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _merge_config(base[key], value)
        else:
            base[key] = value


def validate_config_file(path: Path) -> list[str]:
    """
    Validate a scoring configuration file.

    Args:
        path: Path to YAML config file.

    Returns:
        List of validation errors (empty if valid).
    """
    errors = []

    try:
        with open(path) as f:
            config = yaml.safe_load(f) or {}
    except Exception as e:
        return [f"Failed to parse YAML: {e}"]

    # Check document types
    doc_types = config.get("document_types", {})
    for doc_type, doc_config in doc_types.items():
        categories = doc_config.get("categories", {})
        if categories:
            # Check if this is a partial override
            if len(categories) < 8:
                logger.warning(
                    f"{doc_type}: Partial override ({len(categories)} categories). "
                    "Other categories will use defaults."
                )

            # Check weight values
            for cat_name, cat_config in categories.items():
                if "weight" in cat_config:
                    weight = cat_config["weight"]
                    if not 0 <= weight <= 1:
                        errors.append(
                            f"{doc_type}.{cat_name}: weight {weight} must be 0-1"
                        )

    # Check defaults
    defaults = config.get("defaults", {})
    default_categories = defaults.get("categories", {})
    if default_categories:
        total = sum(
            cat.get("weight", 0)
            for cat in default_categories.values()
        )
        if abs(total - 1.0) > 0.001 and total > 0:
            errors.append(f"defaults: weights sum to {total*100:.1f}%, expected 100%")

    return errors


def get_all_document_types() -> list[str]:
    """Return list of all supported document types."""
    return list(DEFAULT_WEIGHTS.keys())


def get_weight_for_category(
    doc_type: str,
    category: Category,
) -> tuple[float, int]:
    """
    Get weight and max deduction for a category.

    Args:
        doc_type: Document type.
        category: Category enum.

    Returns:
        Tuple of (weight, max_deduction).
    """
    weights = load_weights(doc_type)
    cat_name = category.value
    if cat_name in weights.categories:
        cat = weights.categories[cat_name]
        return cat.weight, cat.max_deduction
    return 0.0, 0
