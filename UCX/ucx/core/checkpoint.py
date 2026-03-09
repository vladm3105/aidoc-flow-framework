"""Checkpoint management for long-running operations.

Provides save/restore capability for resuming interrupted operations.
"""

import json
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from ucx.config.settings import UCXConfig
from ucx.observability.logging import get_logger

logger = get_logger(__name__)


@dataclass
class Checkpoint:
    """Represents a checkpoint state."""

    checkpoint_id: str
    created_at: str
    updated_at: str
    operation: str  # autopilot, batch, etc.
    state: dict[str, Any] = field(default_factory=dict)
    completed_items: list[str] = field(default_factory=list)
    pending_items: list[str] = field(default_factory=list)
    current_item: Optional[str] = None
    current_iteration: int = 0
    last_score: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def progress(self) -> float:
        """Calculate progress percentage."""
        total = len(self.completed_items) + len(self.pending_items)
        if total == 0:
            return 0.0
        return len(self.completed_items) / total

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Checkpoint":
        """Create from dictionary."""
        return cls(**data)


class CheckpointManager:
    """
    Manages checkpoints for long-running UCX operations.

    Provides:
    - Checkpoint creation and saving
    - Checkpoint restoration
    - Progress tracking
    - Cleanup utilities
    """

    def __init__(
        self,
        config: UCXConfig,
        checkpoint_dir: Optional[Path] = None,
    ) -> None:
        """
        Initialize the checkpoint manager.

        Args:
            config: UCX configuration
            checkpoint_dir: Directory for checkpoint files
        """
        self._config = config
        self._checkpoint_dir = checkpoint_dir or Path(
            config.checkpoint_dir or ".ucx_checkpoints"
        )
        self._enabled = config.enable_checkpoints

        if self._enabled:
            self._checkpoint_dir.mkdir(parents=True, exist_ok=True)

        logger.debug(
            "CheckpointManager initialized",
            enabled=self._enabled,
            directory=str(self._checkpoint_dir),
        )

    def create(
        self,
        operation: str,
        items: list[str],
        state: Optional[dict[str, Any]] = None,
    ) -> Checkpoint:
        """
        Create a new checkpoint.

        Args:
            operation: Operation type (autopilot, batch, etc.)
            items: List of items to process
            state: Optional initial state

        Returns:
            New Checkpoint instance
        """
        now = datetime.now().isoformat()
        checkpoint_id = f"{operation}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        checkpoint = Checkpoint(
            checkpoint_id=checkpoint_id,
            created_at=now,
            updated_at=now,
            operation=operation,
            state=state or {},
            pending_items=items.copy(),
        )

        if self._enabled:
            self._save(checkpoint)

        logger.info(
            "Checkpoint created",
            checkpoint_id=checkpoint_id,
            items=len(items),
        )

        return checkpoint

    def update(
        self,
        checkpoint: Checkpoint,
        current_item: Optional[str] = None,
        iteration: Optional[int] = None,
        score: Optional[int] = None,
        state: Optional[dict[str, Any]] = None,
    ) -> Checkpoint:
        """
        Update a checkpoint.

        Args:
            checkpoint: Checkpoint to update
            current_item: Current item being processed
            iteration: Current iteration number
            score: Current score
            state: Additional state to merge

        Returns:
            Updated Checkpoint
        """
        checkpoint.updated_at = datetime.now().isoformat()

        if current_item is not None:
            checkpoint.current_item = current_item

        if iteration is not None:
            checkpoint.current_iteration = iteration

        if score is not None:
            checkpoint.last_score = score

        if state:
            checkpoint.state.update(state)

        if self._enabled:
            self._save(checkpoint)

        return checkpoint

    def complete_item(
        self,
        checkpoint: Checkpoint,
        item: str,
        success: bool = True,
        error: Optional[str] = None,
    ) -> Checkpoint:
        """
        Mark an item as complete.

        Args:
            checkpoint: Checkpoint to update
            item: Item that was completed
            success: Whether processing was successful
            error: Optional error message

        Returns:
            Updated Checkpoint
        """
        if item in checkpoint.pending_items:
            checkpoint.pending_items.remove(item)

        checkpoint.completed_items.append(item)

        if not success and error:
            checkpoint.errors.append(f"{item}: {error}")

        checkpoint.current_item = None
        checkpoint.updated_at = datetime.now().isoformat()

        if self._enabled:
            self._save(checkpoint)

        logger.debug(
            "Item completed",
            checkpoint_id=checkpoint.checkpoint_id,
            item=item,
            success=success,
            progress=f"{checkpoint.progress:.1%}",
        )

        return checkpoint

    def load(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """
        Load a checkpoint by ID.

        Args:
            checkpoint_id: Checkpoint ID to load

        Returns:
            Checkpoint if found, None otherwise
        """
        path = self._checkpoint_dir / f"{checkpoint_id}.json"

        if not path.exists():
            logger.warning("Checkpoint not found", checkpoint_id=checkpoint_id)
            return None

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            checkpoint = Checkpoint.from_dict(data)
            logger.info("Checkpoint loaded", checkpoint_id=checkpoint_id)
            return checkpoint
        except Exception as e:
            logger.error(
                "Failed to load checkpoint",
                checkpoint_id=checkpoint_id,
                error=str(e),
            )
            return None

    def load_latest(self, operation: Optional[str] = None) -> Optional[Checkpoint]:
        """
        Load the most recent checkpoint.

        Args:
            operation: Optional operation type to filter by

        Returns:
            Most recent Checkpoint if found
        """
        checkpoints = self.list_checkpoints(operation)

        if not checkpoints:
            return None

        # Sort by updated_at descending
        checkpoints.sort(key=lambda c: c.updated_at, reverse=True)
        return checkpoints[0]

    def list_checkpoints(
        self,
        operation: Optional[str] = None,
    ) -> list[Checkpoint]:
        """
        List all checkpoints.

        Args:
            operation: Optional operation type to filter by

        Returns:
            List of Checkpoint instances
        """
        checkpoints = []

        for path in self._checkpoint_dir.glob("*.json"):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                checkpoint = Checkpoint.from_dict(data)

                if operation is None or checkpoint.operation == operation:
                    checkpoints.append(checkpoint)
            except Exception as e:
                logger.warning(
                    "Failed to load checkpoint file",
                    path=str(path),
                    error=str(e),
                )

        return checkpoints

    def delete(self, checkpoint_id: str) -> bool:
        """
        Delete a checkpoint.

        Args:
            checkpoint_id: Checkpoint ID to delete

        Returns:
            True if deleted
        """
        path = self._checkpoint_dir / f"{checkpoint_id}.json"

        if path.exists():
            path.unlink()
            logger.info("Checkpoint deleted", checkpoint_id=checkpoint_id)
            return True

        return False

    def cleanup(self, max_age_days: int = 7) -> int:
        """
        Clean up old checkpoints.

        Args:
            max_age_days: Delete checkpoints older than this

        Returns:
            Number of checkpoints deleted
        """
        from datetime import timedelta

        cutoff = datetime.now() - timedelta(days=max_age_days)
        deleted = 0

        for checkpoint in self.list_checkpoints():
            try:
                updated = datetime.fromisoformat(checkpoint.updated_at)
                if updated < cutoff:
                    self.delete(checkpoint.checkpoint_id)
                    deleted += 1
            except Exception:
                pass

        logger.info("Checkpoint cleanup complete", deleted=deleted)
        return deleted

    def _save(self, checkpoint: Checkpoint) -> None:
        """Save checkpoint to disk."""
        path = self._checkpoint_dir / f"{checkpoint.checkpoint_id}.json"
        path.write_text(
            json.dumps(checkpoint.to_dict(), indent=2),
            encoding="utf-8",
        )
