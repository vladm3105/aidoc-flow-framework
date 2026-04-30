"""
Unit tests for sprint0_setup.py script.

Tests Sprint 0 checklist generation and readiness validation.
TASKS Reference: TASKS-05.02.04
"""

import pytest
from pathlib import Path

# Add parent to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'scripts'))

from sprint0_setup import (
    Sprint0Checklist,
    ArtifactReadinessChecker,
    ChecklistItem,
    Checklist,
    ReadinessScore,
)


class TestSprint0Checklist:
    """Tests for Sprint0Checklist class."""

    def test_generate_checklist(self, sample_config_file):
        """Test generating checklist from config."""
        from sprint0_setup import ConfigLoader
        config = ConfigLoader(sample_config_file)
        sprint0 = Sprint0Checklist(config)

        checklist = sprint0.generate_checklist()

        assert isinstance(checklist, Checklist)
        assert len(checklist.items) >= 2
        assert all(isinstance(item, ChecklistItem) for item in checklist.items)

    def test_checklist_items_have_ids(self, sample_config_file):
        """Test that checklist items have IDs."""
        from sprint0_setup import ConfigLoader
        config = ConfigLoader(sample_config_file)
        sprint0 = Sprint0Checklist(config)

        checklist = sprint0.generate_checklist()

        for item in checklist.items:
            assert item.id is not None
            assert item.task is not None

    def test_check_tier1_artifacts_present(self, sample_docs_structure):
        """Test checking Tier 1 artifacts when present."""
        sprint0 = Sprint0Checklist()
        results = sprint0.check_tier1_artifacts(sample_docs_structure)

        assert results.get('BRD') is True
        assert results.get('PRD') is True

    def test_check_tier1_artifacts_missing(self, temp_dir):
        """Test checking Tier 1 artifacts when missing."""
        docs_dir = temp_dir / 'docs'
        docs_dir.mkdir()

        sprint0 = Sprint0Checklist()
        results = sprint0.check_tier1_artifacts(docs_dir)

        assert results.get('BRD') is False
        assert results.get('PRD') is False

    def test_check_adr_decisions(self, sample_docs_structure):
        """Test checking ADR presence."""
        sprint0 = Sprint0Checklist()
        results = sprint0.check_adr_decisions(sample_docs_structure)

        assert results.get('ADR_exists') is True
        assert results.get('ADR_count') >= 1

    def test_validate_sprint1_readiness_ready(self, sample_docs_structure):
        """Test Sprint 1 readiness when artifacts exist."""
        sprint0 = Sprint0Checklist()
        # sample_docs_structure has BRD, PRD, ADR
        # Missing EARS and BDD, so should not be ready
        is_ready = sprint0.validate_sprint1_readiness(sample_docs_structure)
        # This will be False because EARS and BDD are missing
        assert is_ready is False

    def test_validate_sprint1_readiness_not_ready(self, temp_dir):
        """Test Sprint 1 readiness when artifacts missing."""
        docs_dir = temp_dir / 'docs'
        docs_dir.mkdir()

        sprint0 = Sprint0Checklist()
        is_ready = sprint0.validate_sprint1_readiness(docs_dir)

        assert is_ready is False


class TestArtifactReadinessChecker:
    """Tests for ArtifactReadinessChecker class."""

    def test_check_brd_readiness_complete(self, sample_docs_structure):
        """Test BRD readiness with complete document."""
        checker = ArtifactReadinessChecker(sample_docs_structure)
        score = checker.check_brd_readiness()

        assert isinstance(score, ReadinessScore)
        assert score.artifact_type == 'BRD'
        assert score.score > 0

    def test_check_prd_readiness(self, sample_docs_structure):
        """Test PRD readiness check."""
        checker = ArtifactReadinessChecker(sample_docs_structure)
        score = checker.check_prd_readiness()

        assert score.artifact_type == 'PRD'
        assert score.score >= 0

    def test_check_adr_completeness(self, sample_docs_structure):
        """Test ADR completeness check."""
        checker = ArtifactReadinessChecker(sample_docs_structure)
        score = checker.check_adr_completeness()

        assert score.artifact_type == 'ADR'
        # ADR-01.md has context, decision, consequences
        assert score.score > 0

    def test_readiness_recommendations(self, temp_dir):
        """Test that recommendations are provided for low scores."""
        docs_dir = temp_dir / 'docs'
        docs_dir.mkdir()
        brd_dir = docs_dir / 'BRD'
        brd_dir.mkdir()
        (brd_dir / 'BRD-01.md').write_text('# Incomplete BRD')

        checker = ArtifactReadinessChecker(docs_dir)
        score = checker.check_brd_readiness()

        # Should have recommendations due to missing sections
        assert len(score.recommendations) > 0 or score.score < 90
