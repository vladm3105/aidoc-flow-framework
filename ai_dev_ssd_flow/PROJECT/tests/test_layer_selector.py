"""
Unit tests for layer_selector.py script.

Tests work item classification and layer recommendations.
TASKS Reference: TASKS-05.02.06
"""

import pytest
from pathlib import Path

# Add parent to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'scripts'))

from layer_selector import (
    WorkItemClassifier,
    LayerRecommender,
    DecisionTreeRunner,
    WorkType,
    LayerRecommendation,
)


class TestWorkItemClassifier:
    """Tests for WorkItemClassifier class."""

    def test_classify_new_feature(self):
        """Test classifying new feature."""
        classifier = WorkItemClassifier()
        work_type = classifier.classify_work_type("Add new authentication feature")
        assert work_type == WorkType.NEW_FEATURE

    def test_classify_enhancement(self):
        """Test classifying enhancement."""
        classifier = WorkItemClassifier()
        work_type = classifier.classify_work_type("Improve performance of search")
        assert work_type == WorkType.ENHANCEMENT

    def test_classify_bug_fix(self):
        """Test classifying bug fix."""
        classifier = WorkItemClassifier()
        work_type = classifier.classify_work_type("Fix null pointer error in login")
        assert work_type == WorkType.BUG_FIX

    def test_classify_hotfix(self):
        """Test classifying hotfix."""
        classifier = WorkItemClassifier()
        work_type = classifier.classify_work_type("Urgent hotfix for production crash")
        assert work_type == WorkType.HOTFIX

    def test_classify_config_change(self):
        """Test classifying configuration change."""
        classifier = WorkItemClassifier()
        work_type = classifier.classify_work_type("Update configuration settings")
        assert work_type == WorkType.CONFIG_CHANGE

    def test_classify_refactoring(self):
        """Test classifying refactoring."""
        classifier = WorkItemClassifier()
        work_type = classifier.classify_work_type("Refactor authentication module")
        assert work_type == WorkType.REFACTORING

    def test_is_new_capability(self):
        """Test detecting new capability."""
        classifier = WorkItemClassifier()

        assert classifier.is_new_capability("Add new dashboard") is True
        assert classifier.is_new_capability("Fix existing bug") is False

    def test_is_bug_fix(self):
        """Test detecting bug fix."""
        classifier = WorkItemClassifier()

        assert classifier.is_bug_fix("Fix login error") is True
        assert classifier.is_bug_fix("Add new feature") is False


class TestLayerRecommender:
    """Tests for LayerRecommender class."""

    def test_recommend_layers_new_feature(self, sample_config_file):
        """Test layer recommendation for new feature."""
        from layer_selector import ConfigLoader
        config = ConfigLoader(sample_config_file)
        recommender = LayerRecommender(config)

        layers = recommender.recommend_layers(WorkType.NEW_FEATURE)
        # New feature should include all layers
        assert 1 in layers  # BRD
        assert 11 in layers  # TASKS

    def test_recommend_layers_bug_fix(self, sample_config_file):
        """Test layer recommendation for bug fix."""
        from layer_selector import ConfigLoader
        config = ConfigLoader(sample_config_file)
        recommender = LayerRecommender(config)

        layers = recommender.recommend_layers(WorkType.BUG_FIX)
        # Bug fix should only include TASKS
        assert layers == [11]

    def test_recommend_artifacts(self, sample_config_file):
        """Test artifact recommendation."""
        from layer_selector import ConfigLoader
        config = ConfigLoader(sample_config_file)
        recommender = LayerRecommender(config)

        artifacts = recommender.recommend_artifacts([1, 2, 9, 11])
        assert 'BRD' in artifacts
        assert 'PRD' in artifacts
        assert 'SPEC' in artifacts
        assert 'TASKS' in artifacts

    def test_estimate_effort_high(self, sample_config_file):
        """Test high effort estimation."""
        from layer_selector import ConfigLoader
        config = ConfigLoader(sample_config_file)
        recommender = LayerRecommender(config)

        effort = recommender.estimate_effort([1, 2, 3, 4, 5, 6, 7, 8, 9])
        assert effort == 'High'

    def test_estimate_effort_medium(self, sample_config_file):
        """Test medium effort estimation."""
        from layer_selector import ConfigLoader
        config = ConfigLoader(sample_config_file)
        recommender = LayerRecommender(config)

        effort = recommender.estimate_effort([1, 2, 9, 11])
        assert effort == 'Medium'

    def test_estimate_effort_low(self, sample_config_file):
        """Test low effort estimation."""
        from layer_selector import ConfigLoader
        config = ConfigLoader(sample_config_file)
        recommender = LayerRecommender(config)

        effort = recommender.estimate_effort([11])
        assert effort == 'Low'

    def test_get_recommendation(self, sample_config_file):
        """Test getting full recommendation."""
        from layer_selector import ConfigLoader
        config = ConfigLoader(sample_config_file)
        recommender = LayerRecommender(config)

        rec = recommender.get_recommendation(WorkType.BUG_FIX)

        assert isinstance(rec, LayerRecommendation)
        assert rec.work_type == WorkType.BUG_FIX
        assert rec.layers == [11]
        assert 'TASKS' in rec.artifacts


class TestDecisionTreeRunner:
    """Tests for DecisionTreeRunner class."""

    def test_run_automated_bug_fix(self, sample_config_file):
        """Test automated classification for bug fix."""
        from layer_selector import ConfigLoader
        config = ConfigLoader(sample_config_file)
        runner = DecisionTreeRunner(config)

        rec = runner.run_automated('bug_fix', 'Fix login error')

        assert rec.work_type == WorkType.BUG_FIX
        assert rec.layers == [11]

    def test_run_automated_new_feature(self, sample_config_file):
        """Test automated classification for new feature."""
        from layer_selector import ConfigLoader
        config = ConfigLoader(sample_config_file)
        runner = DecisionTreeRunner(config)

        rec = runner.run_automated('new_feature', 'Add reporting dashboard')

        assert rec.work_type == WorkType.NEW_FEATURE
        assert 1 in rec.layers

    def test_run_automated_from_description(self, sample_config_file):
        """Test automated classification from description only."""
        from layer_selector import ConfigLoader
        config = ConfigLoader(sample_config_file)
        runner = DecisionTreeRunner(config)

        rec = runner.run_automated('', 'Fix critical bug in payment processing')

        assert rec.work_type == WorkType.BUG_FIX
