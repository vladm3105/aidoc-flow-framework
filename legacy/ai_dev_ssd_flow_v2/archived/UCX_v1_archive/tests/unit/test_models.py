"""Tests for UCX models."""

import pytest
from pathlib import Path
from datetime import datetime

from ucx.models.enums import DocType, Status, Confidence, Priority
from ucx.models.document import Document
from ucx.models.review import ReviewResult, ValidationResult
from ucx.models.fix import FixProposal, FixAction
from ucx.models.drift_cache import DriftCache


class TestDocType:
    """Tests for DocType enum."""

    def test_from_string(self):
        assert DocType.from_string("brd") == DocType.BRD
        assert DocType.from_string("BRD") == DocType.BRD
        assert DocType.from_string("prd") == DocType.PRD

    def test_layer(self):
        assert DocType.BRD.layer == 1
        assert DocType.PRD.layer == 2
        assert DocType.TSPEC.layer == 10

    def test_display_name(self):
        assert DocType.BRD.display_name == "Business Requirements Document"


class TestDocument:
    """Tests for Document model."""

    def test_from_path(self, sample_brd):
        doc = Document.from_path(sample_brd)

        assert doc.doc_id == "BRD-01"
        assert doc.doc_type == DocType.BRD
        assert doc.version == "1.0"
        assert doc.exists

    def test_read_content(self, sample_brd):
        doc = Document.from_path(sample_brd)
        content = doc.read_content()

        assert "Executive Summary" in content
        assert "BRD.01.01.01" in content


class TestReviewResult:
    """Tests for ReviewResult model."""

    def test_from_report(self, sample_review_report, sample_brd):
        result = ReviewResult.from_report(sample_review_report, sample_brd)

        assert result.score == 72
        assert result.findings["P0"] == 1
        assert result.findings["P1"] == 2
        assert result.findings["P2"] == 1
        assert result.has_critical
        assert result.total_findings == 4

    def test_get_findings_by_priority(self, sample_review_report, sample_brd):
        result = ReviewResult.from_report(sample_review_report, sample_brd)
        p1_findings = result.get_findings_by_priority(Priority.P1)

        assert "P1-1" in p1_findings
        assert "P1-2" in p1_findings


class TestFixProposal:
    """Tests for FixProposal model."""

    def test_from_yaml(self):
        yaml_str = """
fix_id: FIX-P0-01
source_finding: P0-1
priority: P0
confidence: auto-safe
target_file: "BRD-01.md"
target_section: "5.0"
fix_type: add_text
fix_action:
  position: after
  anchor: "## 5. Constraints"
  text: "New constraint text"
rationale: Missing constraint
validated_by:
  - Architect Fixer
verification: Check section 5 exists
"""
        fix = FixProposal.from_yaml(yaml_str)

        assert fix.fix_id == "FIX-P0-01"
        assert fix.priority == Priority.P0
        assert fix.confidence == Confidence.AUTO_SAFE
        assert fix.can_auto_apply
        assert not fix.needs_review

    def test_to_yaml(self):
        fix = FixProposal(
            fix_id="FIX-P1-01",
            source_finding="P1-1",
            priority=Priority.P1,
            confidence=Confidence.AUTO_ASSISTED,
            target_file=Path("doc.md"),
            target_section="3.0",
            fix_type=FixType.MODIFY_TEXT,
            fix_action=FixAction(old_text="old", new_text="new"),
            rationale="Fix requirement",
            validated_by=["QA Fixer"],
        )

        yaml_str = fix.to_yaml()
        assert "fix_id: FIX-P1-01" in yaml_str
        assert "confidence: auto-assisted" in yaml_str


class TestDriftCache:
    """Tests for DriftCache model."""

    def test_save_and_load(self, tmp_path):
        cache = DriftCache(
            document_id="BRD-01",
            upstream_mode="ref",
        )
        cache.add_review(85, "PASS", False)

        cache_path = tmp_path / ".drift_cache.json"
        cache.save(cache_path)

        loaded = DriftCache.load(cache_path)
        assert loaded.document_id == "BRD-01"
        assert loaded.upstream_mode == "ref"
        assert len(loaded.review_history) == 1
        assert loaded.latest_score == 85

    def test_track_upstream(self, tmp_path):
        # Create upstream file
        upstream = tmp_path / "spec.md"
        upstream.write_text("Specification content")

        cache = DriftCache(document_id="BRD-01")
        cache.track_upstream(upstream)

        assert "spec.md" in cache.upstream_documents
        assert cache.upstream_mode == "ref"
        assert cache.upstream_documents["spec.md"].hash.startswith("sha256:")

    def test_check_drift(self, tmp_path):
        # Create and track upstream file
        upstream = tmp_path / "spec.md"
        upstream.write_text("Original content")

        cache = DriftCache(document_id="BRD-01")
        cache.track_upstream(upstream)

        # No drift initially
        drift, changed = cache.check_drift(upstream)
        assert not drift

        # Modify file
        upstream.write_text("Modified content")

        # Should detect drift
        drift, changed = cache.check_drift(upstream)
        assert drift
        assert "spec.md" in changed


# Import FixType for test
from ucx.models.enums import FixType
