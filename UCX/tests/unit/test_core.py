"""Unit tests for core module."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from ucx.config.settings import UCXConfig
from ucx.models.enums import DocType, Status
from ucx.core.checkpoint import Checkpoint, CheckpointManager
from ucx.core.drift import DriftMonitor


class TestCheckpoint:
    """Tests for Checkpoint dataclass."""

    def test_checkpoint_creation(self):
        """Test creating a checkpoint."""
        checkpoint = Checkpoint(
            checkpoint_id="test_20240101_120000",
            created_at="2024-01-01T12:00:00",
            updated_at="2024-01-01T12:00:00",
            operation="autopilot",
            pending_items=["item1", "item2", "item3"],
        )
        assert checkpoint.checkpoint_id == "test_20240101_120000"
        assert checkpoint.operation == "autopilot"
        assert len(checkpoint.pending_items) == 3

    def test_checkpoint_progress(self):
        """Test progress calculation."""
        checkpoint = Checkpoint(
            checkpoint_id="test_001",
            created_at="2024-01-01T12:00:00",
            updated_at="2024-01-01T12:00:00",
            operation="batch",
            completed_items=["a", "b"],
            pending_items=["c", "d"],
        )
        assert checkpoint.progress == 0.5  # 2/4

    def test_checkpoint_progress_empty(self):
        """Test progress with no items."""
        checkpoint = Checkpoint(
            checkpoint_id="test_002",
            created_at="2024-01-01T12:00:00",
            updated_at="2024-01-01T12:00:00",
            operation="batch",
        )
        assert checkpoint.progress == 0.0

    def test_checkpoint_to_dict(self):
        """Test checkpoint serialization."""
        checkpoint = Checkpoint(
            checkpoint_id="test_003",
            created_at="2024-01-01T12:00:00",
            updated_at="2024-01-01T12:00:00",
            operation="autopilot",
        )
        data = checkpoint.to_dict()
        assert data["checkpoint_id"] == "test_003"
        assert data["operation"] == "autopilot"

    def test_checkpoint_from_dict(self):
        """Test checkpoint deserialization."""
        data = {
            "checkpoint_id": "test_004",
            "created_at": "2024-01-01T12:00:00",
            "updated_at": "2024-01-01T12:00:00",
            "operation": "batch",
            "state": {},
            "completed_items": [],
            "pending_items": ["x"],
            "current_item": None,
            "current_iteration": 0,
            "last_score": 0,
            "errors": [],
        }
        checkpoint = Checkpoint.from_dict(data)
        assert checkpoint.checkpoint_id == "test_004"
        assert len(checkpoint.pending_items) == 1


class TestCheckpointManager:
    """Tests for CheckpointManager."""

    def test_manager_initialization(self, tmp_path: Path):
        """Test checkpoint manager initialization."""
        config = UCXConfig(
            enable_checkpoints=True,
            checkpoint_dir=str(tmp_path / "checkpoints"),
        )
        manager = CheckpointManager(config, tmp_path / "checkpoints")
        assert manager is not None

    def test_manager_create_checkpoint(self, tmp_path: Path):
        """Test creating a new checkpoint."""
        config = UCXConfig(
            enable_checkpoints=True,
            checkpoint_dir=str(tmp_path / "checkpoints"),
        )
        manager = CheckpointManager(config, tmp_path / "checkpoints")

        checkpoint = manager.create(
            operation="test",
            items=["item1", "item2"],
        )

        assert checkpoint.operation == "test"
        assert len(checkpoint.pending_items) == 2

    def test_manager_complete_item(self, tmp_path: Path):
        """Test completing an item."""
        config = UCXConfig(
            enable_checkpoints=True,
            checkpoint_dir=str(tmp_path / "checkpoints"),
        )
        manager = CheckpointManager(config, tmp_path / "checkpoints")

        checkpoint = manager.create(
            operation="test",
            items=["item1", "item2"],
        )

        checkpoint = manager.complete_item(checkpoint, "item1")

        assert "item1" in checkpoint.completed_items
        assert "item1" not in checkpoint.pending_items
        assert checkpoint.progress == 0.5

    def test_manager_load_save(self, tmp_path: Path):
        """Test saving and loading checkpoint."""
        config = UCXConfig(
            enable_checkpoints=True,
            checkpoint_dir=str(tmp_path / "checkpoints"),
        )
        manager = CheckpointManager(config, tmp_path / "checkpoints")

        checkpoint = manager.create(
            operation="persist_test",
            items=["a", "b"],
        )

        # Load it back
        loaded = manager.load(checkpoint.checkpoint_id)
        assert loaded is not None
        assert loaded.checkpoint_id == checkpoint.checkpoint_id

    def test_manager_list_checkpoints(self, tmp_path: Path):
        """Test listing checkpoints."""
        config = UCXConfig(
            enable_checkpoints=True,
            checkpoint_dir=str(tmp_path / "checkpoints"),
        )
        manager = CheckpointManager(config, tmp_path / "checkpoints")

        manager.create(operation="op1", items=["a"])
        manager.create(operation="op2", items=["b"])

        all_checkpoints = manager.list_checkpoints()
        assert len(all_checkpoints) >= 2

        op1_checkpoints = manager.list_checkpoints(operation="op1")
        assert all(c.operation == "op1" for c in op1_checkpoints)


class TestDriftMonitor:
    """Tests for DriftMonitor."""

    def test_monitor_initialization(self):
        """Test drift monitor initialization."""
        config = UCXConfig()
        monitor = DriftMonitor(config)
        assert monitor is not None

    def test_monitor_check_no_cache(self, tmp_path: Path):
        """Test checking drift with no cache."""
        config = UCXConfig()
        monitor = DriftMonitor(config)

        target = tmp_path / "doc.md"
        target.write_text("# Test Document")

        has_drift, changed = monitor.check(target)

        # No cache means no drift detected
        assert has_drift is False
        assert len(changed) == 0

    def test_monitor_track_upstream(self, tmp_path: Path):
        """Test tracking an upstream document."""
        config = UCXConfig()
        monitor = DriftMonitor(config)

        target = tmp_path / "PRD.md"
        target.write_text("# PRD")

        upstream = tmp_path / "BRD.md"
        upstream.write_text("# BRD")

        # Track upstream
        monitor.track(target, upstream)

        # Cache should now exist
        cache_path = target.parent / ".drift_cache.json"
        assert cache_path.exists()

    def test_monitor_clear_cache(self, tmp_path: Path):
        """Test clearing drift cache."""
        config = UCXConfig()
        monitor = DriftMonitor(config)

        target = tmp_path / "doc.md"
        target.write_text("# Test")

        upstream = tmp_path / "upstream.md"
        upstream.write_text("# Upstream")

        # Create cache
        monitor.track(target, upstream)
        cache_path = target.parent / ".drift_cache.json"
        assert cache_path.exists()

        # Clear cache
        monitor.clear_cache(target)
        assert not cache_path.exists()
