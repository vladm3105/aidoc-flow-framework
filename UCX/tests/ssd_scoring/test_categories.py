"""
Unit tests for UCX scoring categories module.

Tests category definitions, element code extraction, and categorization logic.
"""

import pytest

from ucx.scoring import (
    Category,
    CATEGORY_DEFINITIONS,
    categorize_by_element_code,
    categorize_by_keyword,
    extract_element_code,
    get_category_by_id,
    get_category_by_name,
    get_persona_primary_category,
    PERSONA_CATEGORY_MAP,
)


class TestCategoryEnum:
    """Tests for Category enum."""

    def test_all_categories_defined(self):
        """All expected categories exist."""
        expected = [
            "functional", "quality", "compliance", "constraints",
            "integration", "acceptance", "risk", "architecture", "other"
        ]
        actual = [c.value for c in Category]
        assert sorted(actual) == sorted(expected)

    def test_category_count(self):
        """9 categories total (8 scoring + OTHER)."""
        assert len(Category) == 9


class TestCategoryDefinitions:
    """Tests for CATEGORY_DEFINITIONS."""

    def test_all_categories_have_definitions(self):
        """Every Category enum has a definition."""
        for cat in Category:
            assert cat in CATEGORY_DEFINITIONS, f"Missing definition for {cat}"

    def test_definitions_have_required_fields(self):
        """Each definition has required fields."""
        for cat, defn in CATEGORY_DEFINITIONS.items():
            assert defn.id, f"{cat} missing id"
            assert defn.name, f"{cat} missing name"
            assert defn.description, f"{cat} missing description"
            assert isinstance(defn.element_codes, tuple), f"{cat} element_codes not tuple"
            assert isinstance(defn.keywords, tuple), f"{cat} keywords not tuple"

    def test_category_ids_unique(self):
        """Category IDs are unique."""
        ids = [defn.id for defn in CATEGORY_DEFINITIONS.values()]
        assert len(ids) == len(set(ids)), "Duplicate category IDs found"


class TestExtractElementCode:
    """Tests for extract_element_code function."""

    @pytest.mark.parametrize("finding_id,expected_code", [
        # Standard dot notation
        ("BRD.01.01.01", 1),
        ("BRD.02.03.01", 2),
        ("PRD.07.01.02", 7),
        ("REQ.91.01.01", 91),
        # Edge cases
        ("BRD.01", 1),
        ("BRD.99.01.01", 99),
    ])
    def test_dot_notation_extraction(self, finding_id, expected_code):
        """Extract element codes from dot notation IDs."""
        assert extract_element_code(finding_id) == expected_code

    @pytest.mark.parametrize("finding_id,expected_code", [
        # Bracket notation
        ("REQ[01]-001", 1),
        ("BRD[07]-P0-001", 7),
    ])
    def test_bracket_notation_extraction(self, finding_id, expected_code):
        """Extract element codes from bracket notation."""
        assert extract_element_code(finding_id) == expected_code

    @pytest.mark.parametrize("finding_id", [
        # No element code
        "ARCH-P0-001",
        "AUD-P1-002",
        "TL-P2-003",
        "random-text",
        "",
    ])
    def test_no_element_code(self, finding_id):
        """Return None when no element code found."""
        assert extract_element_code(finding_id) is None


class TestCategorizeByElementCode:
    """Tests for categorize_by_element_code function."""

    @pytest.mark.parametrize("code,expected_category", [
        # Functional: 01, 22, 24
        (1, Category.FUNCTIONAL),
        (22, Category.FUNCTIONAL),
        (24, Category.FUNCTIONAL),
        # Quality: 02, 91-99
        (2, Category.QUALITY),
        (91, Category.QUALITY),
        (99, Category.QUALITY),
        # Constraints: 03, 04
        (3, Category.CONSTRAINTS),
        (4, Category.CONSTRAINTS),
        # Integration: 05, 16, 20
        (5, Category.INTEGRATION),
        (16, Category.INTEGRATION),
        (20, Category.INTEGRATION),
        # Acceptance: 06, 14, 40-45
        (6, Category.ACCEPTANCE),
        (14, Category.ACCEPTANCE),
        (40, Category.ACCEPTANCE),
        (45, Category.ACCEPTANCE),
        # Risk: 07
        (7, Category.RISK),
        # Architecture: 10, 12, 13, 32
        (10, Category.ARCHITECTURE),
        (12, Category.ARCHITECTURE),
        (13, Category.ARCHITECTURE),
        (32, Category.ARCHITECTURE),
    ])
    def test_element_code_mapping(self, code, expected_category):
        """Element codes map to correct categories."""
        assert categorize_by_element_code(code) == expected_category

    @pytest.mark.parametrize("code", [0, 8, 50, 100, -1])
    def test_unmapped_codes(self, code):
        """Unmapped codes return None."""
        assert categorize_by_element_code(code) is None


class TestCategorizeByKeyword:
    """Tests for categorize_by_keyword function."""

    @pytest.mark.parametrize("text,expected_category", [
        # Compliance (highest priority)
        ("KYC verification required", Category.COMPLIANCE),
        ("Must comply with PCI-DSS", Category.COMPLIANCE),
        ("AML screening mandatory", Category.COMPLIANCE),
        ("GDPR data handling", Category.COMPLIANCE),
        # Functional
        ("User login feature", Category.FUNCTIONAL),
        ("Capability to export", Category.FUNCTIONAL),
        # Quality
        ("Performance requirements", Category.QUALITY),
        ("Scalability concerns", Category.QUALITY),
        # Acceptance
        ("Test scenario missing", Category.ACCEPTANCE),
        ("Acceptance criteria unclear", Category.ACCEPTANCE),
        # Integration
        ("API integration with partner", Category.INTEGRATION),
        ("Third-party webhook", Category.INTEGRATION),
        # Architecture
        ("Architecture decision needed", Category.ARCHITECTURE),
        ("Component design pattern", Category.ARCHITECTURE),
        # Risk
        ("Risk mitigation strategy", Category.RISK),
        ("Threat assessment", Category.RISK),
        # Constraints
        ("Budget constraint noted", Category.CONSTRAINTS),
        ("Assumption about timeline", Category.CONSTRAINTS),
    ])
    def test_keyword_matching(self, text, expected_category):
        """Keywords match to correct categories."""
        assert categorize_by_keyword(text) == expected_category

    def test_no_keyword_match(self):
        """Return None when no keywords match."""
        assert categorize_by_keyword("random unrelated text xyz") is None

    def test_case_insensitive(self):
        """Keyword matching is case-insensitive."""
        assert categorize_by_keyword("aml COMPLIANCE") == Category.COMPLIANCE
        assert categorize_by_keyword("FEATURE capability") == Category.FUNCTIONAL


class TestGetCategoryByIdAndName:
    """Tests for category lookup functions."""

    def test_get_by_id(self):
        """Get category by ID."""
        assert get_category_by_id("CAT-01") == Category.FUNCTIONAL
        assert get_category_by_id("CAT-03") == Category.COMPLIANCE
        assert get_category_by_id("CAT-99") == Category.OTHER

    def test_get_by_id_invalid(self):
        """Invalid ID returns None."""
        assert get_category_by_id("CAT-100") is None
        assert get_category_by_id("invalid") is None

    def test_get_by_name(self):
        """Get category by name."""
        assert get_category_by_name("functional") == Category.FUNCTIONAL
        assert get_category_by_name("COMPLIANCE") == Category.COMPLIANCE
        assert get_category_by_name("Risk") == Category.RISK

    def test_get_by_name_invalid(self):
        """Invalid name returns None."""
        assert get_category_by_name("invalid") is None
        assert get_category_by_name("") is None


class TestPersonaCategoryMapping:
    """Tests for persona to category mapping."""

    def test_all_personas_mapped(self):
        """All expected personas have mappings."""
        expected_personas = [
            "architect", "auditor", "tech_lead", "strategist",
            "devils_advocate", "operator", "integration_lead",
            "product_owner", "business_analyst", "fact_checker", "chairperson"
        ]
        for persona in expected_personas:
            assert persona in PERSONA_CATEGORY_MAP, f"Missing mapping for {persona}"

    def test_persona_primary_category(self):
        """Get primary category for personas."""
        assert get_persona_primary_category("architect") == Category.ARCHITECTURE
        assert get_persona_primary_category("auditor") == Category.COMPLIANCE
        assert get_persona_primary_category("product_owner") == Category.FUNCTIONAL
        assert get_persona_primary_category("operator") == Category.QUALITY

    def test_persona_variations(self):
        """Handle persona name variations."""
        # Spaces to underscores
        assert get_persona_primary_category("tech lead") == Category.FUNCTIONAL
        # Hyphens to underscores
        assert get_persona_primary_category("tech-lead") == Category.FUNCTIONAL
        # Mixed case
        assert get_persona_primary_category("Tech_Lead") == Category.FUNCTIONAL

    def test_chairperson_no_primary(self):
        """Chairperson has no primary category (synthesis only)."""
        assert get_persona_primary_category("chairperson") is None
        assert get_persona_primary_category("fact_checker") is None
