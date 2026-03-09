"""Integration tests for UCX API.

Tests the public API classes with mock AI client.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock

from ucx.api import UCXAutopilot, UCCPhase, UCRPhase, UCRemPhase
from ucx.config.settings import UCXConfig
from ucx.models.enums import DocType, Status


class TestUCXAutopilotIntegration:
    """Integration tests for UCXAutopilot."""

    @pytest.fixture
    def config(self) -> UCXConfig:
        """Create test configuration."""
        return UCXConfig(
            model="mock",
            max_iterations=2,
            min_score=85,
            skip_drift=True,
        )

    def test_autopilot_initialization(self, config: UCXConfig):
        """Test autopilot initializes correctly."""
        pilot = UCXAutopilot(config=config)
        assert pilot is not None
        # Access via property or public interface
        assert hasattr(pilot, "config") or hasattr(pilot, "_config")

    def test_autopilot_with_config(self):
        """Test autopilot accepts config."""
        config = UCXConfig(
            model="sonnet",
            max_iterations=5,
            min_score=95,
        )
        pilot = UCXAutopilot(config=config)
        assert pilot is not None


class TestUCCPhaseIntegration:
    """Integration tests for UCC phase."""

    @pytest.fixture
    def config(self) -> UCXConfig:
        """Create test configuration."""
        return UCXConfig(model="mock")

    def test_ucc_phase_initialization(self, config: UCXConfig):
        """Test UCC phase initializes correctly."""
        ucc = UCCPhase(config=config)
        assert ucc is not None

    def test_ucc_phase_with_config(self):
        """Test UCC phase with custom config."""
        config = UCXConfig(model="haiku", load_skills=False)
        ucc = UCCPhase(config=config)
        assert ucc is not None


class TestUCRPhaseIntegration:
    """Integration tests for UCR phase."""

    @pytest.fixture
    def config(self) -> UCXConfig:
        """Create test configuration."""
        return UCXConfig(model="mock", min_score=80)

    def test_ucr_phase_initialization(self, config: UCXConfig):
        """Test UCR phase initializes correctly."""
        ucr = UCRPhase(config=config)
        assert ucr is not None


class TestUCRemPhaseIntegration:
    """Integration tests for UCRem phase."""

    @pytest.fixture
    def config(self) -> UCXConfig:
        """Create test configuration."""
        return UCXConfig(model="mock")

    def test_ucrem_phase_initialization(self, config: UCXConfig):
        """Test UCRem phase initializes correctly."""
        ucrem = UCRemPhase(config=config)
        assert ucrem is not None


class TestAPIWorkflow:
    """Test complete API workflow integration."""

    @pytest.fixture
    def tmp_doc_dir(self, tmp_path: Path) -> Path:
        """Create temporary document directory."""
        doc_dir = tmp_path / "docs"
        doc_dir.mkdir()
        return doc_dir

    @pytest.fixture
    def sample_brd(self, tmp_doc_dir: Path) -> Path:
        """Create sample BRD document."""
        brd_path = tmp_doc_dir / "BRD-01.md"
        brd_path.write_text("""# BRD-01: Test Business Requirements

## 1. Executive Summary
This is a test BRD document.

## 2. Business Objectives
- Objective 1
- Objective 2

## 3. Stakeholder Analysis
| Stakeholder | Role |
|-------------|------|
| User        | End user |

## 4. Success Metrics
- Metric 1: 90% satisfaction
""")
        return brd_path

    def test_config_loading(self, tmp_doc_dir: Path):
        """Test configuration can be loaded from file."""
        config_path = tmp_doc_dir / "ucx.yaml"
        config_path.write_text("""
model: sonnet
max_iterations: 4
min_score: 88
""")
        config = UCXConfig.from_yaml(config_path)
        assert config.model == "sonnet"
        # Note: max_iterations uses alias 'max_iter' but direct field works too
        assert config.min_score == 88

    def test_validator_integration(self, sample_brd: Path):
        """Test validator can be used through API."""
        from ucx.validators.registry import get_validator

        validator = get_validator(DocType.BRD)
        result = validator.validate(sample_brd)

        assert result is not None
        assert hasattr(result, "status")
        assert hasattr(result, "errors")
        assert hasattr(result, "warnings")

    def test_prompt_loading_integration(self):
        """Test prompt loading works correctly."""
        from ucx.prompts.loader import PromptLoader

        loader = PromptLoader()

        # list_templates returns flat list of template paths
        templates = loader.list_templates()
        assert len(templates) > 0
        # Check that we have ucc templates
        ucc_templates = [t for t in templates if t.startswith("ucc/")]
        assert len(ucc_templates) > 0

    def test_skill_loading_integration(self):
        """Test skill loading works correctly."""
        from ucx.skills.loader import SkillLoader

        loader = SkillLoader()

        # Should be able to list skills
        skills = loader.list_skills()
        assert len(skills) > 0
        assert "architect" in skills

    def test_drift_monitor_integration(self, sample_brd: Path, tmp_doc_dir: Path):
        """Test drift monitor can track documents."""
        from ucx.core.drift import DriftMonitor

        monitor = DriftMonitor()

        # Create upstream
        upstream = tmp_doc_dir / "REF.md"
        upstream.write_text("# Reference Document")

        # Track upstream
        monitor.track(sample_brd, upstream)

        # Check drift (should be none initially)
        has_drift, changed = monitor.check(sample_brd)
        assert has_drift is False

        # Modify upstream
        upstream.write_text("# Reference Document\n\nModified content")

        # Check drift again
        has_drift, changed = monitor.check(sample_brd, upstream)
        assert has_drift is True
        assert len(changed) > 0

    def test_checkpoint_integration(self, tmp_path: Path):
        """Test checkpoint manager works correctly."""
        from ucx.core.checkpoint import CheckpointManager

        config = UCXConfig(
            enable_checkpoints=True,
            checkpoint_dir=str(tmp_path / "checkpoints"),
        )
        manager = CheckpointManager(config, tmp_path / "checkpoints")

        # Create checkpoint
        checkpoint = manager.create(
            operation="test_workflow",
            items=["doc1", "doc2", "doc3"],
        )

        assert checkpoint is not None
        assert len(checkpoint.pending_items) == 3

        # Complete an item
        checkpoint = manager.complete_item(checkpoint, "doc1")
        assert "doc1" in checkpoint.completed_items
        assert checkpoint.progress == pytest.approx(1/3)

        # List checkpoints
        checkpoints = manager.list_checkpoints(operation="test_workflow")
        assert len(checkpoints) >= 1
