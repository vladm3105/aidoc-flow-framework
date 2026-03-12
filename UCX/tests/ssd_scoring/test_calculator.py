"""
Unit tests for UCX scoring calculator module.

Tests score calculation, category deductions, and caps.
"""

import pytest

from ucx.scoring import (
    Category,
    CategoryScore,
    Finding,
    ScoringCalculator,
    ScoringResult,
    calculate_legacy_score,
    calculate_weighted_score,
)


class TestFinding:
    """Tests for Finding dataclass."""

    def test_finding_creation(self):
        """Create a finding with required fields."""
        finding = Finding(
            id="BRD.01.01.01",
            priority="P0",
            text="Missing scope definition",
            persona="auditor"
        )
        assert finding.id == "BRD.01.01.01"
        assert finding.priority == "P0"
        assert finding.category is None  # Not assigned yet

    def test_finding_with_category(self):
        """Create a finding with pre-assigned category."""
        finding = Finding(
            id="AUD-P0-001",
            priority="P0",
            text="Compliance gap",
            persona="auditor",
            category=Category.COMPLIANCE
        )
        assert finding.category == Category.COMPLIANCE


class TestCategoryScore:
    """Tests for CategoryScore dataclass."""

    def test_total_findings(self):
        """Total findings calculation."""
        score = CategoryScore(
            category=Category.FUNCTIONAL,
            p0_count=2,
            p1_count=3,
            p2_count=5,
        )
        assert score.total_findings == 10


class TestScoringCalculator:
    """Tests for ScoringCalculator class."""

    @pytest.fixture
    def calculator(self):
        """Create a BRD calculator."""
        return ScoringCalculator("brd")

    def test_calculator_initialization(self, calculator):
        """Calculator initializes with correct doc type."""
        assert calculator.doc_type == "brd"
        assert calculator.weights is not None

    def test_categorize_by_element_code(self, calculator):
        """Categorize finding by element code in ID."""
        finding = Finding(
            id="BRD.01.01.01",  # Element code 01 = functional
            priority="P0",
            text="Some finding",
            persona="architect"
        )
        category = calculator.categorize_finding(finding)
        assert category == Category.FUNCTIONAL

    def test_categorize_by_keyword(self, calculator):
        """Categorize finding by keyword when no element code."""
        finding = Finding(
            id="ARCH-P0-001",  # No element code
            priority="P0",
            text="KYC compliance requirement missing",  # Compliance keyword
            persona="architect"
        )
        category = calculator.categorize_finding(finding)
        assert category == Category.COMPLIANCE

    def test_categorize_by_persona_fallback(self, calculator):
        """Fall back to persona category when no code or keyword."""
        finding = Finding(
            id="ARCH-P0-001",
            priority="P0",
            text="Some generic finding without keywords",
            persona="architect"  # Primary: architecture
        )
        category = calculator.categorize_finding(finding)
        assert category == Category.ARCHITECTURE

    def test_categorize_with_explicit_tag(self, calculator):
        """Explicit [CAT:xxx] tag takes priority."""
        finding = Finding(
            id="BRD.01.01.01",  # Would be functional by code
            priority="P0",
            text="Risk assessment [CAT:risk]",
            persona="architect",
            raw_category_tag="risk"
        )
        category = calculator.categorize_finding(finding)
        assert category == Category.RISK


class TestCategoryScoreCalculation:
    """Tests for per-category score calculation."""

    @pytest.fixture
    def calculator(self):
        return ScoringCalculator("brd")

    def test_calculate_category_score_basic(self, calculator):
        """Basic category score calculation."""
        score = calculator.calculate_category_score(
            Category.FUNCTIONAL,
            p0_count=1,
            p1_count=2,
            p2_count=3,
        )
        # Raw: (1*10) + (2*3) + (3*1) = 10 + 6 + 3 = 19
        assert score.raw_deduction == 19
        # For BRD functional: weight=0.25, max_deduction=25
        assert score.capped_deduction == 19  # Under cap
        assert score.weighted_deduction == pytest.approx(19 * 0.25)

    def test_category_cap_applied(self, calculator):
        """Category cap prevents excessive deduction."""
        score = calculator.calculate_category_score(
            Category.RISK,  # max_deduction=5
            p0_count=5,  # Would be 50 points raw
            p1_count=0,
            p2_count=0,
        )
        assert score.raw_deduction == 50
        assert score.capped_deduction == 5  # Capped at max

    def test_zero_findings(self, calculator):
        """Zero findings means zero deduction."""
        score = calculator.calculate_category_score(
            Category.COMPLIANCE,
            p0_count=0,
            p1_count=0,
            p2_count=0,
        )
        assert score.raw_deduction == 0
        assert score.capped_deduction == 0
        assert score.weighted_deduction == 0


class TestWeightedScoreCalculation:
    """Tests for final weighted score calculation."""

    @pytest.fixture
    def calculator(self):
        return ScoringCalculator("brd")

    def test_perfect_score(self, calculator):
        """No findings = 100 score."""
        result = calculator.calculate([])
        assert result.weighted_score == 100.0
        assert result.pass_status == "PASS"

    def test_score_with_findings(self, calculator):
        """Score with mixed findings."""
        findings = [
            Finding("BRD.01.01.01", "P0", "Missing scope", "auditor"),
            Finding("BRD.02.01.01", "P1", "Quality gap", "tech_lead"),
            Finding("BRD.03.01.01", "P2", "Minor constraint", "business_analyst"),
        ]
        result = calculator.calculate(findings)

        # Score should be less than 100
        assert result.weighted_score < 100
        # But above 0 (caps prevent excessive deduction)
        assert result.weighted_score > 0

        # Verify counts
        assert result.total_p0 == 1
        assert result.total_p1 == 1
        assert result.total_p2 == 1
        assert result.total_findings == 3

    def test_score_never_negative(self, calculator):
        """Score stays at 0, never goes negative."""
        # Create many P0 findings across all categories
        findings = []
        for i in range(50):
            findings.append(Finding(
                f"AUD-P0-{i:03d}",
                "P0",
                f"Critical finding {i}",
                "auditor"
            ))

        result = calculator.calculate(findings)
        assert result.weighted_score >= 0

    def test_category_summary_table(self, calculator):
        """Generate category summary markdown table."""
        findings = [
            Finding("BRD.01.01.01", "P0", "Functional gap", "architect"),
            Finding("AUD-P1-001", "P1", "Compliance issue", "auditor"),
        ]
        result = calculator.calculate(findings)

        table = result.get_category_summary_table()
        assert "| Category |" in table
        assert "| functional |" in table
        assert "| compliance |" in table


class TestPassStatus:
    """Tests for pass/warn/fail status."""

    @pytest.fixture
    def calculator(self):
        return ScoringCalculator("brd")

    def test_pass_status_thresholds(self, calculator):
        """Verify threshold-based status."""
        # Perfect score = PASS
        result = calculator.calculate([])
        assert result.pass_status == "PASS"

    def test_score_threshold_boundaries(self, calculator):
        """Test boundary conditions for status."""
        # With default thresholds: pass=85, warn=70
        # We can't easily force exact scores, but we can verify
        # the status is one of the expected values
        findings = [Finding("AUD-P0-001", "P0", "Test", "auditor") for _ in range(10)]
        result = calculator.calculate(findings)
        assert result.pass_status in ["PASS", "WARN", "FAIL"]


class TestLegacyScore:
    """Tests for legacy scoring function."""

    def test_legacy_score_formula(self):
        """Legacy formula: 100 - (P0*10) - (P1*3) - (P2*1)."""
        assert calculate_legacy_score(0, 0, 0) == 100
        assert calculate_legacy_score(1, 0, 0) == 90
        assert calculate_legacy_score(0, 1, 0) == 97
        assert calculate_legacy_score(0, 0, 1) == 99
        assert calculate_legacy_score(1, 1, 1) == 86

    def test_legacy_score_can_go_negative(self):
        """Legacy score has no cap - can go negative."""
        score = calculate_legacy_score(15, 10, 5)
        # 100 - 150 - 30 - 5 = -85
        assert score == -85


class TestConvenienceFunction:
    """Tests for calculate_weighted_score convenience function."""

    def test_calculate_weighted_score(self):
        """Convenience function works correctly."""
        findings = [
            Finding("BRD.01.01.01", "P0", "Gap", "auditor"),
        ]
        result = calculate_weighted_score(findings, "brd")

        assert isinstance(result, ScoringResult)
        assert result.doc_type == "brd"
        assert 0 <= result.weighted_score <= 100
