"""Integration tests for weighted scoring in review flow.

Tests Phase 8 integration of ScoringCalculator into ReviewMemory and ReviewResult.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
import tempfile
import os

from ucx.core.review_memory import ReviewMemory
from ucx.models.review import ReviewResult
from ucx.models.enums import Status, ValidationStatus
from ucx.scoring.calculator import Finding, ScoringResult, CategoryScore, ScoringCalculator
from ucx.scoring.categories import Category


class TestReviewMemoryScoring:
    """Test weighted scoring integration in ReviewMemory."""

    def test_extract_findings_with_category_tag(self, tmp_path):
        """Test that explicit [CAT:xxx] tags are extracted."""
        memory = ReviewMemory(tmp_path, "brd")

        responses = {
            "auditor": """
## Auditor Review

**[P0-001]** [CAT:compliance] Missing SAR filing requirement
This is a critical compliance gap.

**[P1-001]** [CAT:risk] Insufficient risk mitigation
Risk assessment incomplete.
""",
        }

        findings = memory._extract_findings(responses)

        assert len(findings) == 2
        assert findings[0]["category"] == "compliance"
        assert findings[1]["category"] == "risk"

    def test_extract_findings_fallback_to_persona(self, tmp_path):
        """Test category fallback when no explicit tag."""
        memory = ReviewMemory(tmp_path, "brd")

        responses = {
            "auditor": """
**[P0-001]** Missing regulatory requirement
No explicit category tag here.
""",
        }

        findings = memory._extract_findings(responses)

        assert len(findings) == 1
        # Auditor's primary category is compliance
        assert findings[0]["category"] == "compliance"

    def test_calculate_weighted_score(self, tmp_path):
        """Test weighted score calculation from findings."""
        memory = ReviewMemory(tmp_path, "brd")

        findings = [
            {"id": "P0-001", "priority": "P0", "title": "Critical", "persona": "auditor", "category": "compliance"},
            {"id": "P1-001", "priority": "P1", "title": "Major", "persona": "architect", "category": "architecture"},
            {"id": "P2-001", "priority": "P2", "title": "Minor", "persona": "tech_lead", "category": "quality"},
        ]

        result = memory.calculate_weighted_score(findings)

        assert isinstance(result, ScoringResult)
        assert result.total_p0 == 1
        assert result.total_p1 == 1
        assert result.total_p2 == 1
        assert 0 <= result.weighted_score <= 100

    def test_calculate_weighted_score_empty_findings(self, tmp_path):
        """Test weighted score with no findings (perfect score)."""
        memory = ReviewMemory(tmp_path, "brd")

        findings = []
        result = memory.calculate_weighted_score(findings)

        assert result.weighted_score == 100.0
        assert result.total_p0 == 0
        assert result.total_p1 == 0
        assert result.total_p2 == 0


class TestReviewResultWeightedScore:
    """Test weighted score extraction in ReviewResult."""

    def test_from_report_extracts_weighted_score(self, tmp_path):
        """Test that weighted_score is extracted from frontmatter."""
        report_content = """---
title: "UCR Review Report: BRD"
custom_fields:
  scoring_method: category-weighted-v1.12.0
  weighted_score: 85.5
  p0_findings: 0
  p1_findings: 5
  p2_findings: 10
---

# Review Report

**Weighted Score**: 85.5/100
"""
        report_path = tmp_path / "test_report.md"
        report_path.write_text(report_content)
        doc_path = tmp_path / "doc"
        doc_path.mkdir()

        result = ReviewResult.from_report(report_path, doc_path)

        assert result.weighted_score == 85.5
        assert result.findings["P0"] == 0
        assert result.findings["P1"] == 5
        assert result.findings["P2"] == 10
        assert result.status == Status.PASS  # 85.5 >= 85 and P0 == 0

    def test_from_report_warns_status(self, tmp_path):
        """Test WARN status for scores 70-84."""
        report_content = """---
custom_fields:
  weighted_score: 75.0
  p0_findings: 0
  p1_findings: 10
  p2_findings: 5
---
"""
        report_path = tmp_path / "test_report.md"
        report_path.write_text(report_content)
        doc_path = tmp_path / "doc"
        doc_path.mkdir()

        result = ReviewResult.from_report(report_path, doc_path)

        assert result.weighted_score == 75.0
        assert result.status == Status.NEEDS_MANUAL  # Warning range

    def test_from_report_fail_status(self, tmp_path):
        """Test FAIL status for scores < 70 or P0 > 0."""
        report_content = """---
custom_fields:
  weighted_score: 65.0
  p0_findings: 2
  p1_findings: 5
  p2_findings: 3
---
"""
        report_path = tmp_path / "test_report.md"
        report_path.write_text(report_content)
        doc_path = tmp_path / "doc"
        doc_path.mkdir()

        result = ReviewResult.from_report(report_path, doc_path)

        assert result.weighted_score == 65.0
        assert result.status == Status.FAIL

    def test_from_report_legacy_fallback(self, tmp_path):
        """Test fallback to legacy score extraction when no frontmatter."""
        report_content = """
# Legacy Review Report

Score: 72

## Findings

**P0-001**: Critical issue
**P0-002**: Another critical
**P1-001**: Major issue
"""
        report_path = tmp_path / "test_report.md"
        report_path.write_text(report_content)
        doc_path = tmp_path / "doc"
        doc_path.mkdir()

        result = ReviewResult.from_report(report_path, doc_path)

        # Falls back to regex extraction
        assert result.score == 72
        assert result.weighted_score == 0.0  # No frontmatter
        assert result.findings["P0"] == 2
        assert result.findings["P1"] == 1


class TestFormatScoringSummary:
    """Test scoring summary formatting."""

    def test_format_scoring_summary_pass(self, tmp_path):
        """Test scoring summary format for passing score."""
        memory = ReviewMemory(tmp_path, "brd")

        # Use the actual calculator to create result
        calculator = ScoringCalculator(doc_type="brd")
        findings = [
            Finding(id="P1-001", priority="P1", text="Issue 1", persona="auditor", category=Category.COMPLIANCE),
            Finding(id="P1-002", priority="P1", text="Issue 2", persona="auditor", category=Category.COMPLIANCE),
            Finding(id="P2-001", priority="P2", text="Issue 3", persona="architect", category=Category.FUNCTIONAL),
        ]
        scoring_result = calculator.calculate(findings)

        dedup_stats = {"total_findings": 3, "unique_findings": 3}

        summary = memory._format_scoring_summary(scoring_result, dedup_stats)

        assert "**Weighted Score**:" in summary
        assert "### Category Breakdown" in summary
        assert "PRD-Ready Status" in summary

    def test_format_scoring_summary_fail(self, tmp_path):
        """Test scoring summary format for failing score."""
        memory = ReviewMemory(tmp_path, "brd")

        # Create result with many P0s
        calculator = ScoringCalculator(doc_type="brd")
        findings = [
            Finding(id="P0-001", priority="P0", text="Critical 1", persona="auditor", category=Category.COMPLIANCE),
            Finding(id="P0-002", priority="P0", text="Critical 2", persona="auditor", category=Category.COMPLIANCE),
            Finding(id="P0-003", priority="P0", text="Critical 3", persona="auditor", category=Category.COMPLIANCE),
            Finding(id="P0-004", priority="P0", text="Critical 4", persona="architect", category=Category.FUNCTIONAL),
            Finding(id="P0-005", priority="P0", text="Critical 5", persona="architect", category=Category.FUNCTIONAL),
        ]
        scoring_result = calculator.calculate(findings)

        summary = memory._format_scoring_summary(scoring_result, {})

        assert "**Weighted Score**:" in summary
        assert "Not Ready" in summary
