"""Base classes for UCX plugins.

Defines the plugin interface and data structures.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from ucx.config.settings import UCXConfig
from ucx.models.enums import DocType


class PluginPriority(Enum):
    """Plugin execution priority."""

    FIRST = 0
    HIGH = 25
    NORMAL = 50
    LOW = 75
    LAST = 100


@dataclass
class PluginContext:
    """Context passed to plugin hooks.

    Attributes:
        config: UCX configuration
        doc_type: Document type being processed
        target_path: Target document path
        phase: Current processing phase (ucc/ucr/ucrem)
        iteration: Current iteration number
        data: Additional context data
    """

    config: UCXConfig
    doc_type: Optional[DocType] = None
    target_path: Optional[Path] = None
    phase: str = ""
    iteration: int = 1
    data: dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from context data."""
        return self.data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a value in context data."""
        self.data[key] = value


@dataclass
class PluginResult:
    """Result from plugin execution.

    Attributes:
        success: Whether the plugin executed successfully
        modified: Whether the plugin modified the context
        message: Optional message
        data: Additional result data
        stop_chain: If True, stop further plugin execution
    """

    success: bool = True
    modified: bool = False
    message: Optional[str] = None
    data: dict[str, Any] = field(default_factory=dict)
    stop_chain: bool = False

    @classmethod
    def ok(cls, message: Optional[str] = None, **data: Any) -> "PluginResult":
        """Create a successful result."""
        return cls(success=True, message=message, data=data)

    @classmethod
    def fail(cls, message: str, **data: Any) -> "PluginResult":
        """Create a failed result."""
        return cls(success=False, message=message, data=data)

    @classmethod
    def modified(cls, message: Optional[str] = None, **data: Any) -> "PluginResult":
        """Create a result indicating modification."""
        return cls(success=True, modified=True, message=message, data=data)

    @classmethod
    def stop(cls, message: Optional[str] = None) -> "PluginResult":
        """Create a result that stops the plugin chain."""
        return cls(success=True, stop_chain=True, message=message)


class UCXPlugin(ABC):
    """Base class for UCX plugins.

    Plugins can extend UCX functionality by implementing hooks
    for various phases of document processing.

    Example:
        class MyPlugin(UCXPlugin):
            name = "my-plugin"
            version = "1.0.0"

            def on_pre_create(self, context: PluginContext) -> PluginResult:
                # Custom logic before document creation
                return PluginResult.ok()
    """

    # Plugin metadata - override in subclass
    name: str = "base-plugin"
    version: str = "0.0.0"
    description: str = ""
    author: str = ""
    priority: PluginPriority = PluginPriority.NORMAL

    # Enabled document types (None = all)
    enabled_doc_types: Optional[list[DocType]] = None

    # Enabled phases (None = all)
    enabled_phases: Optional[list[str]] = None

    def __init__(self, config: Optional[UCXConfig] = None) -> None:
        """Initialize the plugin.

        Args:
            config: UCX configuration
        """
        self._config = config or UCXConfig()
        self._enabled = True

    @property
    def enabled(self) -> bool:
        """Check if plugin is enabled."""
        return self._enabled

    def enable(self) -> None:
        """Enable the plugin."""
        self._enabled = True

    def disable(self) -> None:
        """Disable the plugin."""
        self._enabled = False

    def should_run(self, context: PluginContext) -> bool:
        """Check if plugin should run for given context.

        Args:
            context: Plugin context

        Returns:
            True if plugin should run
        """
        if not self._enabled:
            return False

        # Check doc type filter
        if self.enabled_doc_types is not None:
            if context.doc_type not in self.enabled_doc_types:
                return False

        # Check phase filter
        if self.enabled_phases is not None:
            if context.phase not in self.enabled_phases:
                return False

        return True

    # Hook methods - override as needed

    def on_initialize(self, context: PluginContext) -> PluginResult:
        """Called when plugin is initialized."""
        return PluginResult.ok()

    def on_shutdown(self, context: PluginContext) -> PluginResult:
        """Called when plugin is shutting down."""
        return PluginResult.ok()

    def on_pre_create(self, context: PluginContext) -> PluginResult:
        """Called before document creation."""
        return PluginResult.ok()

    def on_post_create(self, context: PluginContext) -> PluginResult:
        """Called after document creation."""
        return PluginResult.ok()

    def on_pre_review(self, context: PluginContext) -> PluginResult:
        """Called before document review."""
        return PluginResult.ok()

    def on_post_review(self, context: PluginContext) -> PluginResult:
        """Called after document review."""
        return PluginResult.ok()

    def on_pre_remediate(self, context: PluginContext) -> PluginResult:
        """Called before document remediation."""
        return PluginResult.ok()

    def on_post_remediate(self, context: PluginContext) -> PluginResult:
        """Called after document remediation."""
        return PluginResult.ok()

    def on_error(self, context: PluginContext, error: Exception) -> PluginResult:
        """Called when an error occurs."""
        return PluginResult.ok()

    def on_progress(
        self, context: PluginContext, current: int, total: int, message: str
    ) -> PluginResult:
        """Called to report progress."""
        return PluginResult.ok()

    @abstractmethod
    def execute(self, context: PluginContext) -> PluginResult:
        """Main plugin execution logic.

        Args:
            context: Plugin context

        Returns:
            Plugin result
        """
        pass
