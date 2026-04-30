"""
Unit tests for drift_check.py script.

Tests artifact scanning, drift analysis, and report generation.
TASKS Reference: TASKS-05.02.01
"""

import pytest
from datetime import datetime, timedelta
from pathlib import Path

# Add parent to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'scripts'))

from drift_check import (
    ArtifactScanner,
    DriftAnalyzer,
    Artifact,
    DriftStatus,
)


class TestArtifactScanner:
    """Tests for ArtifactScanner class."""

    def test_scan_directory(self, sample_docs_structure):
        """Test scanning directory for artifacts."""
        scanner = ArtifactScanner()
        artifacts = scanner.scan_directory(sample_docs_structure)

        assert len(artifacts) >= 3  # BRD, PRD, ADR
        artifact_types = {a.artifact_type for a in artifacts}
        assert 'BRD' in artifact_types
        assert 'PRD' in artifact_types
        assert 'ADR' in artifact_types

    def test_detect_type_from_content(self, temp_dir):
        """Test detecting artifact type."""
        scanner = ArtifactScanner()

        brd_file = temp_dir / 'BRD-01.md'
        brd_file.touch()

        artifact = scanner._parse_artifact(brd_file)
        assert artifact is not None
        assert artifact.artifact_type == 'BRD'

    def test_get_last_modified(self, temp_dir):
        """Test getting last modification time."""
        scanner = ArtifactScanner()

        test_file = temp_dir / 'BRD-01.md'
        test_file.write_text('test content')

        artifact = scanner._parse_artifact(test_file)
        assert artifact is not None
        assert isinstance(artifact.last_modified, datetime)

    def test_extract_tasks_refs(self, temp_dir):
        """Test extracting TASKS references from content."""
        scanner = ArtifactScanner()

        brd_file = temp_dir / 'BRD-01.md'
        brd_file.write_text("""
# BRD-01

@tasks: TASKS-01.02.03
Related to TASKS-01.03.01

Implementation in TASKS-02
""")

        refs = scanner._extract_tasks_refs(brd_file)
        assert 'TASKS-01.02.03' in refs
        assert 'TASKS-01.03.01' in refs

    def test_exclusion_patterns(self, temp_dir, sample_config_file):
        """Test exclusion patterns."""
        from drift_check import ConfigLoader
        config = ConfigLoader(sample_config_file)
        scanner = ArtifactScanner(config)

        # Create file in excluded path
        generated_dir = temp_dir / 'docs' / 'generated'
        generated_dir.mkdir(parents=True)
        (generated_dir / 'BRD-GEN.md').touch()

        # Should be excluded
        assert scanner._is_excluded(generated_dir / 'BRD-GEN.md') is True


class TestDriftAnalyzer:
    """Tests for DriftAnalyzer class."""

    def test_calculate_drift_days_no_issues(self, temp_dir):
        """Test drift calculation with no related issues."""
        analyzer = DriftAnalyzer(max_age_days=14)

        # Create artifact modified 5 days ago
        artifact = Artifact(
            path=temp_dir / 'BRD-01.md',
            artifact_type='BRD',
            layer=1,
            last_modified=datetime.now() - timedelta(days=5),
        )

        drift_days = analyzer.calculate_drift_days(artifact, [])
        assert drift_days == 5

    def test_calculate_drift_days_with_recent_issue(self, temp_dir):
        """Test drift calculation with recent issue close."""
        analyzer = DriftAnalyzer(max_age_days=14)

        # Artifact modified 10 days ago
        artifact = Artifact(
            path=temp_dir / 'BRD-01.md',
            artifact_type='BRD',
            layer=1,
            last_modified=datetime.now() - timedelta(days=10),
            tasks_refs=['TASKS-01'],
        )

        # Issue closed 5 days ago
        issues = [{
            'number': 1,
            'title': '[P1-TASKS-01] Test',
            'closed_at': datetime.now() - timedelta(days=5),
            'tasks_id': 'TASKS-01',
        }]

        drift_days = analyzer.calculate_drift_days(artifact, issues)
        # Drift = 10 - 5 = 5 days since issue closed after artifact modified
        assert drift_days == 5

    def test_compare_timestamps_current(self, temp_dir):
        """Test timestamp comparison - artifact is current."""
        analyzer = DriftAnalyzer(max_age_days=14, warning_threshold=7)

        artifact = Artifact(
            path=temp_dir / 'BRD-01.md',
            artifact_type='BRD',
            layer=1,
            last_modified=datetime.now() - timedelta(days=3),
        )

        status = analyzer.compare_timestamps(artifact, [])
        assert status.status == 'current'

    def test_compare_timestamps_warning(self, temp_dir):
        """Test timestamp comparison - artifact needs attention."""
        analyzer = DriftAnalyzer(max_age_days=14, warning_threshold=7)

        artifact = Artifact(
            path=temp_dir / 'BRD-01.md',
            artifact_type='BRD',
            layer=1,
            last_modified=datetime.now() - timedelta(days=10),
        )

        status = analyzer.compare_timestamps(artifact, [])
        assert status.status == 'warning'

    def test_compare_timestamps_stale(self, temp_dir):
        """Test timestamp comparison - artifact is stale."""
        analyzer = DriftAnalyzer(max_age_days=14, warning_threshold=7)

        artifact = Artifact(
            path=temp_dir / 'BRD-01.md',
            artifact_type='BRD',
            layer=1,
            last_modified=datetime.now() - timedelta(days=20),
        )

        status = analyzer.compare_timestamps(artifact, [])
        assert status.status == 'stale'

    def test_generate_report(self, temp_dir):
        """Test report generation."""
        analyzer = DriftAnalyzer(max_age_days=14)

        drifts = [
            DriftStatus(
                artifact=Artifact(
                    path=temp_dir / 'BRD-01.md',
                    artifact_type='BRD',
                    layer=1,
                    last_modified=datetime.now() - timedelta(days=20),
                ),
                drift_days=20,
                status='stale',
            ),
            DriftStatus(
                artifact=Artifact(
                    path=temp_dir / 'PRD-01.md',
                    artifact_type='PRD',
                    layer=2,
                    last_modified=datetime.now() - timedelta(days=5),
                ),
                drift_days=5,
                status='current',
            ),
        ]

        report = analyzer.generate_report(drifts)

        assert '# Documentation Drift Report' in report
        assert 'Stale: 1' in report
        assert 'Current: 1' in report
        assert 'BRD-01.md' in report
