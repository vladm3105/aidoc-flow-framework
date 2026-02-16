"""
Unit tests for chg_generator.py script.

Tests change classification and CHG document generation.
TASKS Reference: TASKS-05.02.03
"""

import pytest
from pathlib import Path

# Add parent to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'scripts'))

from chg_generator import (
    ChangeClassifier,
    CHGDocumentGenerator,
    ChangeRequest,
    ChangeLevel,
)


class TestChangeClassifier:
    """Tests for ChangeClassifier class."""

    def test_classify_bug_fix(self):
        """Test classifying bug fix as L1."""
        classifier = ChangeClassifier()
        level = classifier.classify_change("Fix null pointer bug", [11])
        assert level == ChangeLevel.L1

    def test_classify_feature(self):
        """Test classifying new feature as L2 or L3."""
        classifier = ChangeClassifier()

        # Feature affecting multiple layers
        level = classifier.classify_change("Add email notification feature", [2, 9, 11])
        assert level == ChangeLevel.L2

    def test_classify_architecture_change(self):
        """Test classifying architecture change as L3."""
        classifier = ChangeClassifier()
        level = classifier.classify_change("Major architecture redesign", [1, 2, 3, 4, 5])
        assert level == ChangeLevel.L3

    def test_classify_scope_based(self):
        """Test classification based on layer scope."""
        classifier = ChangeClassifier()

        # Many layers = L3
        level = classifier.classify_change("Update system", [1, 2, 3, 4, 5, 6, 7, 8])
        assert level == ChangeLevel.L3

    def test_identify_affected_layers_cascade(self):
        """Test layer cascade for BRD changes."""
        classifier = ChangeClassifier()
        change = ChangeRequest(
            description="Update requirements",
            affected_layers=[1],
            change_level=ChangeLevel.L2,
        )

        all_layers = classifier.identify_affected_layers(change)
        # BRD change cascades to PRD, EARS, BDD
        assert 1 in all_layers
        assert 2 in all_layers
        assert 3 in all_layers
        assert 4 in all_layers

    def test_determine_gates(self):
        """Test gate determination from layers."""
        classifier = ChangeClassifier()

        # Layers 1-4 -> GATE-01
        gates = classifier.determine_gates([1, 2, 3])
        assert 'GATE-01' in gates

        # Layers 5-8 -> GATE-05
        gates = classifier.determine_gates([5, 6])
        assert 'GATE-05' in gates

        # Mixed layers
        gates = classifier.determine_gates([2, 9, 11])
        assert 'GATE-01' in gates
        assert 'GATE-09' in gates

    def test_get_artifacts_for_layers(self):
        """Test artifact names for layers."""
        classifier = ChangeClassifier()

        artifacts = classifier.get_artifacts_for_layers([1, 2, 9, 11])
        assert 'BRD' in artifacts
        assert 'PRD' in artifacts
        assert 'SPEC' in artifacts
        assert 'TASKS' in artifacts


class TestCHGDocumentGenerator:
    """Tests for CHGDocumentGenerator class."""

    def test_create_chg_document_l1(self):
        """Test L1 (Patch) CHG document generation."""
        generator = CHGDocumentGenerator()
        change = ChangeRequest(
            description="Fix login bug",
            affected_layers=[11],
            change_level=ChangeLevel.L1,
            rationale="Bug affecting production users",
        )

        doc = generator.create_chg_document(change, 1)

        assert 'CHG-001' in doc
        assert 'Fix login bug' in doc
        assert 'L1 (Patch)' in doc
        assert 'TASKS' in doc

    def test_create_chg_document_l2(self):
        """Test L2 (Minor) CHG document generation."""
        generator = CHGDocumentGenerator()
        change = ChangeRequest(
            description="Add localization support",
            affected_layers=[2, 9, 11],
            change_level=ChangeLevel.L2,
        )

        doc = generator.create_chg_document(change, 2)

        assert 'CHG-002' in doc
        assert 'L2 (Minor)' in doc
        assert 'Product Owner' in doc  # L2 requires PO approval

    def test_create_chg_document_l3(self):
        """Test L3 (Major) CHG document generation."""
        generator = CHGDocumentGenerator()
        change = ChangeRequest(
            description="Architecture redesign",
            affected_layers=[1, 2, 3, 4, 5],
            change_level=ChangeLevel.L3,
        )

        doc = generator.create_chg_document(change, 3)

        assert 'CHG-003' in doc
        assert 'L3 (Major)' in doc
        assert 'Architect' in doc  # L3 requires Architect approval

    def test_gate_checklists_included(self):
        """Test that appropriate gate checklists are included."""
        generator = CHGDocumentGenerator()
        change = ChangeRequest(
            description="Update requirements",
            affected_layers=[1, 2],
            change_level=ChangeLevel.L2,
        )

        doc = generator.create_chg_document(change, 4)

        assert 'GATE-01' in doc
        assert 'BRD impact assessed' in doc
        assert 'PRD updated' in doc

    def test_generate_impact_analysis(self):
        """Test impact analysis generation."""
        generator = CHGDocumentGenerator()

        # High impact (many layers)
        change = ChangeRequest(
            description="Major change",
            affected_layers=[1, 2, 3, 4, 5, 6],
            change_level=ChangeLevel.L3,
        )
        impact = generator.generate_impact_analysis(change)
        assert impact.technical_impact == 'High'

        # Low impact (single layer)
        change = ChangeRequest(
            description="Bug fix",
            affected_layers=[11],
            change_level=ChangeLevel.L1,
        )
        impact = generator.generate_impact_analysis(change)
        assert impact.technical_impact == 'Low'
