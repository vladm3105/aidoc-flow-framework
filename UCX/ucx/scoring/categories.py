"""
UCX Category Definitions and Element Code Mappings.

Based on ID_NAMING_STANDARDS.md standardized element type codes (01-99).

Categories:
    CAT-01: functional   - Functional requirements completeness
    CAT-02: quality      - Quality attributes coverage
    CAT-03: compliance   - Regulatory and compliance requirements
    CAT-04: constraints  - Constraints and assumptions
    CAT-05: integration  - Dependencies and integrations
    CAT-06: acceptance   - Acceptance criteria and testability
    CAT-07: risk         - Risk identification and mitigation
    CAT-08: architecture - Architecture decisions
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Category(Enum):
    """Scoring categories mapped to ID_NAMING_STANDARDS element type codes."""

    FUNCTIONAL = "functional"
    QUALITY = "quality"
    COMPLIANCE = "compliance"
    CONSTRAINTS = "constraints"
    INTEGRATION = "integration"
    ACCEPTANCE = "acceptance"
    RISK = "risk"
    ARCHITECTURE = "architecture"
    OTHER = "other"  # Fallback for uncategorized findings


@dataclass(frozen=True)
class CategoryDefinition:
    """Definition of a scoring category."""

    id: str
    name: str
    description: str
    element_codes: tuple[int, ...]
    keywords: tuple[str, ...] = field(default_factory=tuple)

    def matches_element_code(self, code: int) -> bool:
        """Check if element code belongs to this category."""
        return code in self.element_codes

    def matches_keyword(self, text: str) -> bool:
        """Check if text contains any category keywords (case-insensitive)."""
        text_lower = text.lower()
        return any(kw.lower() in text_lower for kw in self.keywords)


# Category definitions based on PLAN-002 and ID_NAMING_STANDARDS.md
CATEGORY_DEFINITIONS: dict[Category, CategoryDefinition] = {
    Category.FUNCTIONAL: CategoryDefinition(
        id="CAT-01",
        name="Functional Completeness",
        description="Functional requirements completeness",
        element_codes=(1, 22, 24),
        keywords=("functional", "feature", "capability", "use case", "user story"),
    ),
    Category.QUALITY: CategoryDefinition(
        id="CAT-02",
        name="Quality Attributes",
        description="Quality attributes coverage",
        element_codes=(2, 91, 92, 93, 94, 95, 96, 97, 98, 99),
        keywords=(
            "performance", "scalability", "reliability", "availability",
            "maintainability", "security", "usability", "portability",
        ),
    ),
    Category.COMPLIANCE: CategoryDefinition(
        id="CAT-03",
        name="Compliance & Regulatory",
        description="Regulatory and compliance requirements",
        element_codes=(),  # Cross-cutting, matched by keyword
        keywords=(
            # Fintech (default)
            "FinCEN", "OFAC", "PCI-DSS", "AML", "KYC", "SAR", "CTR", "MTL",
            "BSA", "FFIEC", "SOX", "GLBA",
            # General
            "GDPR", "CCPA", "SOC2", "ISO27001", "PII", "encryption", "audit",
            "compliance", "regulatory", "regulation", "mandate", "license",
        ),
    ),
    Category.CONSTRAINTS: CategoryDefinition(
        id="CAT-04",
        name="Constraints & Assumptions",
        description="Constraints and assumptions",
        element_codes=(3, 4),
        keywords=(
            "constraint", "assumption", "limitation", "boundary", "scope",
            "prerequisite", "dependency",
        ),
    ),
    Category.INTEGRATION: CategoryDefinition(
        id="CAT-05",
        name="Dependencies & Integration",
        description="Dependencies and integrations",
        element_codes=(5, 16, 20),
        keywords=(
            "integration", "interface", "API", "dependency", "external",
            "third-party", "partner", "connector", "webhook",
        ),
    ),
    Category.ACCEPTANCE: CategoryDefinition(
        id="CAT-06",
        name="Acceptance & Testability",
        description="Acceptance criteria and testability",
        element_codes=(6, 14, 40, 41, 42, 43, 44, 45),
        keywords=(
            "acceptance", "test", "testable", "measurable", "verifiable",
            "criteria", "validation", "verification", "BDD", "scenario",
        ),
    ),
    Category.RISK: CategoryDefinition(
        id="CAT-07",
        name="Risk Management",
        description="Risk identification and mitigation",
        element_codes=(7,),
        keywords=(
            "risk", "mitigation", "contingency", "threat", "vulnerability",
            "impact", "likelihood", "severity",
        ),
    ),
    Category.ARCHITECTURE: CategoryDefinition(
        id="CAT-08",
        name="Architecture & Decisions",
        description="Architecture decisions",
        element_codes=(10, 12, 13, 32),
        keywords=(
            "architecture", "decision", "ADR", "design", "pattern",
            "component", "module", "system", "structure",
        ),
    ),
    Category.OTHER: CategoryDefinition(
        id="CAT-99",
        name="Uncategorized",
        description="Findings that could not be categorized",
        element_codes=(),
        keywords=(),
    ),
}


def get_category_by_id(category_id: str) -> Optional[Category]:
    """Get category enum by its ID (e.g., 'CAT-01' -> Category.FUNCTIONAL)."""
    for cat, defn in CATEGORY_DEFINITIONS.items():
        if defn.id == category_id:
            return cat
    return None


def get_category_by_name(name: str) -> Optional[Category]:
    """Get category enum by its name (e.g., 'functional' -> Category.FUNCTIONAL)."""
    try:
        return Category(name.lower())
    except ValueError:
        return None


def extract_element_code(finding_id: str) -> Optional[int]:
    """
    Extract element type code from a finding ID.

    Finding IDs may follow patterns like:
    - BRD.01.01.03 -> element code 01
    - ARCH-P0-001 -> no element code (prefix-based)
    - REQ.02.01 -> element code 02

    Returns:
        Element type code as int, or None if not extractable.
    """
    # Try to extract from dot-notation ID (e.g., BRD.01.01.03)
    parts = finding_id.split(".")
    if len(parts) >= 2:
        try:
            # Second segment is typically the element type code
            return int(parts[1])
        except ValueError:
            pass

    # Try to extract from bracket notation (e.g., [01])
    match = re.search(r"\[(\d{2})\]", finding_id)
    if match:
        return int(match.group(1))

    return None


def categorize_by_element_code(code: int) -> Optional[Category]:
    """
    Categorize a finding by its element type code.

    Args:
        code: Element type code (1-99).

    Returns:
        Category enum, or None if code doesn't match any category.
    """
    for category, defn in CATEGORY_DEFINITIONS.items():
        if category != Category.OTHER and defn.matches_element_code(code):
            return category
    return None


def categorize_by_keyword(text: str) -> Optional[Category]:
    """
    Categorize a finding by keyword matching in its text.

    Checks categories in priority order.

    Args:
        text: Finding text to analyze.

    Returns:
        Category enum, or None if no keywords match.
    """
    # Priority order: compliance first (cross-cutting), then others
    priority_order = [
        Category.COMPLIANCE,
        Category.FUNCTIONAL,
        Category.QUALITY,
        Category.ACCEPTANCE,
        Category.INTEGRATION,
        Category.ARCHITECTURE,
        Category.RISK,
        Category.CONSTRAINTS,
    ]

    for category in priority_order:
        defn = CATEGORY_DEFINITIONS[category]
        if defn.matches_keyword(text):
            return category

    return None


# Persona to primary/secondary category mapping
PERSONA_CATEGORY_MAP: dict[str, tuple[list[Category], list[Category]]] = {
    "architect": (
        [Category.ARCHITECTURE, Category.QUALITY, Category.INTEGRATION],
        [Category.FUNCTIONAL],
    ),
    "auditor": (
        [Category.COMPLIANCE, Category.CONSTRAINTS, Category.RISK],
        [],
    ),
    "tech_lead": (
        [Category.FUNCTIONAL, Category.QUALITY, Category.INTEGRATION],
        [Category.ACCEPTANCE],
    ),
    "strategist": (
        [Category.CONSTRAINTS, Category.RISK, Category.ARCHITECTURE],
        [Category.FUNCTIONAL],
    ),
    "devils_advocate": (
        # All categories (validation role)
        list(Category),
        [],
    ),
    "operator": (
        [Category.QUALITY, Category.RISK],
        [],
    ),
    "integration_lead": (
        [Category.INTEGRATION, Category.ACCEPTANCE],
        [Category.FUNCTIONAL],
    ),
    "product_owner": (
        [Category.FUNCTIONAL, Category.ACCEPTANCE],
        [Category.CONSTRAINTS],
    ),
    "business_analyst": (
        [Category.CONSTRAINTS, Category.FUNCTIONAL],
        [Category.RISK],
    ),
    "fact_checker": (
        # Cross-validation role - no primary categories
        [],
        [],
    ),
    "chairperson": (
        # Synthesis only - no findings
        [],
        [],
    ),
}


def get_persona_primary_category(persona: str) -> Optional[Category]:
    """
    Get the primary category for a persona.

    Used as fallback when element code and keyword matching fail.

    Args:
        persona: Persona name (lowercase, underscore-separated).

    Returns:
        First primary category, or None if persona not mapped.
    """
    persona_key = persona.lower().replace(" ", "_").replace("-", "_")
    mapping = PERSONA_CATEGORY_MAP.get(persona_key)
    if mapping and mapping[0]:
        return mapping[0][0]
    return None
