"""
End-to-end integration tests for UCX SDD scoring.

Tests the full flow: review → scan → score calculation.
"""

import json
import tempfile
from pathlib import Path

import pytest
import yaml

from ucx.scoring import (
    Category,
    Finding,
    ScoringCalculator,
    ScoringResult,
    calculate_legacy_score,
    calculate_weighted_score,
    load_weights,
    validate_config_file,
)


class TestScoringE2E:
    """End-to-end tests for scoring module."""

    @pytest.fixture
    def sample_findings(self) -> list[Finding]:
        """Create a realistic set of findings for testing."""
        return [
            # Compliance findings (Auditor)
            Finding("AUD-P0-001", "P0", "KYC verification timeline not specified [CAT:compliance]", "auditor", raw_category_tag="compliance"),
            Finding("AUD-P0-002", "P0", "SAR reporting process not documented [CAT:compliance]", "auditor", raw_category_tag="compliance"),
            Finding("AUD-P1-003", "P1", "AML screening trigger unclear [CAT:compliance]", "auditor", raw_category_tag="compliance"),

            # Functional findings (Tech Lead, Product Owner)
            Finding("BRD.01.01.01", "P0", "User registration flow incomplete", "tech_lead"),  # Element code 01
            Finding("PO-P0-001", "P0", "Order cancellation feature missing [CAT:functional]", "product_owner", raw_category_tag="functional"),
            Finding("TL-P1-002", "P1", "Error handling for payment timeout not specified [CAT:functional]", "tech_lead", raw_category_tag="functional"),

            # Integration findings
            Finding("INT-P0-001", "P0", "Partner API contract undefined [CAT:integration]", "integration_lead", raw_category_tag="integration"),
            Finding("INT-P1-002", "P1", "Webhook retry policy not specified [CAT:integration]", "integration_lead", raw_category_tag="integration"),

            # Architecture findings
            Finding("ARCH-P1-001", "P1", "Database failover strategy not documented [CAT:architecture]", "architect", raw_category_tag="architecture"),

            # Risk findings
            Finding("STRAT-P0-001", "P0", "Competitor launch timeline not factored [CAT:risk]", "strategist", raw_category_tag="risk"),

            # Acceptance findings
            Finding("BRD.06.01.01", "P1", "Acceptance criteria not measurable", "product_owner"),  # Element code 06
            Finding("PO-P2-003", "P2", "Minor formatting issue in test scenario [CAT:acceptance]", "product_owner", raw_category_tag="acceptance"),
        ]

    def test_full_scoring_flow(self, sample_findings):
        """Test complete scoring flow with realistic findings."""
        calculator = ScoringCalculator("brd")
        result = calculator.calculate(sample_findings)

        # Verify result structure
        assert isinstance(result, ScoringResult)
        assert result.doc_type == "brd"
        assert 0 <= result.weighted_score <= 100
        assert result.pass_status in ["PASS", "WARN", "FAIL"]

        # Verify finding counts
        assert result.total_p0 == 6  # 6 P0 findings
        assert result.total_p1 == 5  # 5 P1 findings
        assert result.total_p2 == 1  # 1 P2 finding
        assert result.total_findings == 12

        # Verify category distribution
        assert Category.COMPLIANCE in result.category_scores
        assert Category.FUNCTIONAL in result.category_scores
        assert Category.INTEGRATION in result.category_scores

        # Compliance should have 3 findings (2 P0, 1 P1)
        compliance_score = result.category_scores[Category.COMPLIANCE]
        assert compliance_score.p0_count == 2
        assert compliance_score.p1_count == 1

    def test_category_caps_applied(self, sample_findings):
        """Test that category caps prevent excessive deductions."""
        calculator = ScoringCalculator("brd")
        result = calculator.calculate(sample_findings)

        # Check compliance category (weight 0.20, max_deduction 20)
        compliance_score = result.category_scores[Category.COMPLIANCE]
        # Raw deduction: (2*10) + (1*3) = 23
        assert compliance_score.raw_deduction == 23
        # Capped at 20
        assert compliance_score.capped_deduction == 20

    def test_weighted_score_calculation(self, sample_findings):
        """Test weighted score is calculated correctly."""
        calculator = ScoringCalculator("brd")
        result = calculator.calculate(sample_findings)

        # Verify score is reasonable (not negative, capped at 100)
        assert result.weighted_score >= 0
        assert result.weighted_score <= 100

        # With 6 P0s across categories, score should be lower than 100
        # but with caps, not extremely low
        assert result.weighted_score < 100

    def test_legacy_vs_weighted_comparison(self, sample_findings):
        """Compare legacy and weighted scoring."""
        # Calculate weighted score
        calculator = ScoringCalculator("brd")
        weighted_result = calculator.calculate(sample_findings)

        # Calculate legacy score
        legacy_score = calculate_legacy_score(
            p0_count=weighted_result.total_p0,
            p1_count=weighted_result.total_p1,
            p2_count=weighted_result.total_p2,
        )

        # Legacy: 100 - (6*10) - (5*3) - (1*1) = 100 - 60 - 15 - 1 = 24
        assert legacy_score == 24

        # Weighted should be higher due to caps
        assert weighted_result.weighted_score > legacy_score

    def test_category_summary_table_generation(self, sample_findings):
        """Test markdown table generation for Chairperson manifest."""
        calculator = ScoringCalculator("brd")
        result = calculator.calculate(sample_findings)

        table = result.get_category_summary_table()

        # Verify table structure
        assert "| Category |" in table
        assert "| P0 |" in table
        assert "| compliance |" in table
        assert "| functional |" in table
        assert "| **Total** |" in table

    def test_all_document_types(self):
        """Test scoring works for all 11 document types."""
        doc_types = [
            "brd", "prd", "ears", "bdd", "adr",
            "sys", "req", "spec", "ctr", "tasks", "tspec"
        ]

        findings = [
            Finding("TEST-P0-001", "P0", "Test finding [CAT:functional]", "tech_lead", raw_category_tag="functional"),
            Finding("TEST-P1-002", "P1", "Test finding [CAT:quality]", "architect", raw_category_tag="quality"),
        ]

        for doc_type in doc_types:
            calculator = ScoringCalculator(doc_type)
            result = calculator.calculate(findings)

            assert result.doc_type == doc_type
            assert 0 <= result.weighted_score <= 100
            assert result.total_findings == 2


class TestConfigIntegration:
    """Integration tests for scoring configuration."""

    def test_default_config_loads(self):
        """Test default configuration loads correctly."""
        weights = load_weights("brd")

        assert weights.doc_type == "brd"
        assert len(weights.categories) == 8  # 8 categories (not counting OTHER)

        # Verify weights sum to 100%
        total = sum(cat.weight for cat in weights.categories.values())
        assert abs(total - 1.0) < 0.001

    def test_project_override_loads(self):
        """Test project-specific overrides are applied."""
        # Create temp config
        config = {
            "document_types": {
                "brd": {
                    "categories": {
                        "functional": {"weight": 0.30},
                        "compliance": {"weight": 0.15},  # Balance change
                    }
                }
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config, f)
            f.flush()

            weights = load_weights("brd", project_config_path=Path(f.name))

        assert weights.categories["functional"].weight == 0.30
        assert weights.categories["compliance"].weight == 0.15

    def test_config_validation(self):
        """Test configuration file validation."""
        # Valid config
        valid_config = {
            "defaults": {
                "thresholds": {"pass": 85, "warn": 70}
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(valid_config, f)
            f.flush()
            errors = validate_config_file(Path(f.name))

        assert len(errors) == 0

        # Invalid config
        invalid_config = {
            "document_types": {
                "brd": {
                    "categories": {
                        "functional": {"weight": 1.5}  # > 1.0
                    }
                }
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(invalid_config, f)
            f.flush()
            errors = validate_config_file(Path(f.name))

        assert len(errors) > 0


class TestCLIIntegration:
    """Integration tests for CLI scoring commands."""

    def test_scoring_show_command(self):
        """Test ucx scoring show command."""
        from click.testing import CliRunner
        from ucx.cli.main import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["scoring", "show", "brd"])

        assert result.exit_code == 0
        assert "Scoring Weights: BRD" in result.output
        assert "functional" in result.output
        assert "compliance" in result.output

    def test_scoring_show_yaml_format(self):
        """Test ucx scoring show with YAML format."""
        from click.testing import CliRunner
        from ucx.cli.main import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["scoring", "show", "brd", "--format", "yaml"])

        assert result.exit_code == 0
        # Should be valid YAML
        parsed = yaml.safe_load(result.output)
        assert parsed["doc_type"] == "brd"
        assert "categories" in parsed

    def test_scoring_validate_command(self):
        """Test ucx scoring validate command."""
        from click.testing import CliRunner
        from ucx.cli.main import cli

        # Create valid config
        config = {"defaults": {"thresholds": {"pass": 85}}}

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config, f)
            f.flush()

            runner = CliRunner()
            result = runner.invoke(cli, ["scoring", "validate", f.name])

        assert result.exit_code == 0
        assert "Validation passed" in result.output


class TestBackwardCompatibility:
    """Tests for backward compatibility with pre-v1.12.0 reports."""

    def test_findings_without_category_tags(self):
        """Test findings without [CAT:xxx] tags are categorized."""
        findings = [
            Finding("AUD-P0-001", "P0", "KYC verification missing", "auditor"),
            Finding("ARCH-P1-001", "P1", "Architecture gap", "architect"),
            Finding("BRD.01.01.01", "P0", "Missing scope", "business_analyst"),
        ]

        calculator = ScoringCalculator("brd")
        result = calculator.calculate(findings)

        # Should categorize by element code or persona fallback
        assert result.total_findings == 3
        assert result.uncategorized_count == 0 or result.uncategorized_count < 3

    def test_legacy_score_backward_compatible(self):
        """Test legacy score function produces expected results."""
        # Same formula as pre-v1.12.0
        assert calculate_legacy_score(0, 0, 0) == 100
        assert calculate_legacy_score(10, 0, 0) == 0
        assert calculate_legacy_score(5, 10, 5) == 15  # 100 - 50 - 30 - 5


class TestScoreVariance:
    """Tests for score variance and consistency."""

    def test_deterministic_scoring(self):
        """Test same findings produce same score."""
        findings = [
            Finding("AUD-P0-001", "P0", "Test [CAT:compliance]", "auditor", raw_category_tag="compliance"),
            Finding("TL-P1-001", "P1", "Test [CAT:functional]", "tech_lead", raw_category_tag="functional"),
        ]

        scores = []
        for _ in range(5):
            calculator = ScoringCalculator("brd")
            result = calculator.calculate(findings)
            scores.append(result.weighted_score)

        # All scores should be identical
        assert len(set(scores)) == 1
