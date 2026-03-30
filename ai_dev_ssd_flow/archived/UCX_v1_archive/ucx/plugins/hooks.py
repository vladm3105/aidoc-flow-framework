"""Hook definitions and decorators for UCX plugins.

Provides decorators for registering hook handlers.
"""

from enum import Enum
from functools import wraps
from typing import Callable, Optional, TypeVar, Any

from ucx.plugins.base import PluginContext, PluginResult

# Type variable for hook functions
F = TypeVar("F", bound=Callable[..., PluginResult])


class HookType(Enum):
    """Types of hooks available in UCX."""

    # Lifecycle hooks
    INITIALIZE = "initialize"
    SHUTDOWN = "shutdown"

    # Creation phase hooks
    PRE_CREATE = "pre_create"
    POST_CREATE = "post_create"

    # Review phase hooks
    PRE_REVIEW = "pre_review"
    POST_REVIEW = "post_review"

    # Remediation phase hooks
    PRE_REMEDIATE = "pre_remediate"
    POST_REMEDIATE = "post_remediate"

    # Error handling
    ON_ERROR = "on_error"

    # Progress reporting
    ON_PROGRESS = "on_progress"


class Hook:
    """Hook registration and management.

    Allows registering standalone functions as hook handlers.

    Example:
        @Hook.register(HookType.PRE_CREATE)
        def my_pre_create_hook(context: PluginContext) -> PluginResult:
            # Custom logic
            return PluginResult.ok()
    """

    _handlers: dict[HookType, list[Callable]] = {
        hook_type: [] for hook_type in HookType
    }

    @classmethod
    def register(
        cls,
        hook_type: HookType,
        priority: int = 50,
    ) -> Callable[[F], F]:
        """Decorator to register a hook handler.

        Args:
            hook_type: Type of hook to register for
            priority: Execution priority (lower = earlier)

        Returns:
            Decorator function
        """

        def decorator(func: F) -> F:
            cls._handlers[hook_type].append((priority, func))
            # Sort by priority
            cls._handlers[hook_type].sort(key=lambda x: x[0])
            return func

        return decorator

    @classmethod
    def execute(
        cls,
        hook_type: HookType,
        context: PluginContext,
        error: Optional[Exception] = None,
    ) -> list[PluginResult]:
        """Execute all handlers for a hook type.

        Args:
            hook_type: Type of hook to execute
            context: Plugin context
            error: Optional error (for ON_ERROR hook)

        Returns:
            List of results from handlers
        """
        results = []

        for _priority, handler in cls._handlers[hook_type]:
            try:
                if hook_type == HookType.ON_ERROR and error is not None:
                    result = handler(context, error)
                else:
                    result = handler(context)

                results.append(result)

                if result.stop_chain:
                    break

            except Exception as e:
                results.append(PluginResult.fail(str(e)))

        return results

    @classmethod
    def clear(cls, hook_type: Optional[HookType] = None) -> None:
        """Clear registered handlers.

        Args:
            hook_type: Specific hook type to clear, or None for all
        """
        if hook_type is not None:
            cls._handlers[hook_type] = []
        else:
            for ht in HookType:
                cls._handlers[ht] = []


# Convenience decorators for common hooks


def pre_create(priority: int = 50) -> Callable[[F], F]:
    """Decorator to register a pre-create hook handler.

    Args:
        priority: Execution priority (lower = earlier)

    Example:
        @pre_create()
        def validate_upstream(context: PluginContext) -> PluginResult:
            if not context.get("upstream_path"):
                return PluginResult.fail("Upstream path required")
            return PluginResult.ok()
    """
    return Hook.register(HookType.PRE_CREATE, priority)


def post_create(priority: int = 50) -> Callable[[F], F]:
    """Decorator to register a post-create hook handler.

    Args:
        priority: Execution priority (lower = earlier)

    Example:
        @post_create()
        def notify_on_create(context: PluginContext) -> PluginResult:
            # Send notification
            return PluginResult.ok()
    """
    return Hook.register(HookType.POST_CREATE, priority)


def pre_review(priority: int = 50) -> Callable[[F], F]:
    """Decorator to register a pre-review hook handler.

    Args:
        priority: Execution priority (lower = earlier)

    Example:
        @pre_review()
        def check_document_exists(context: PluginContext) -> PluginResult:
            if not context.target_path.exists():
                return PluginResult.fail("Document not found")
            return PluginResult.ok()
    """
    return Hook.register(HookType.PRE_REVIEW, priority)


def post_review(priority: int = 50) -> Callable[[F], F]:
    """Decorator to register a post-review hook handler.

    Args:
        priority: Execution priority (lower = earlier)

    Example:
        @post_review()
        def record_review_metrics(context: PluginContext) -> PluginResult:
            score = context.get("review_score", 0)
            # Record metrics
            return PluginResult.ok()
    """
    return Hook.register(HookType.POST_REVIEW, priority)


def pre_remediate(priority: int = 50) -> Callable[[F], F]:
    """Decorator to register a pre-remediate hook handler.

    Args:
        priority: Execution priority (lower = earlier)

    Example:
        @pre_remediate()
        def backup_document(context: PluginContext) -> PluginResult:
            # Create backup before remediation
            return PluginResult.ok()
    """
    return Hook.register(HookType.PRE_REMEDIATE, priority)


def post_remediate(priority: int = 50) -> Callable[[F], F]:
    """Decorator to register a post-remediate hook handler.

    Args:
        priority: Execution priority (lower = earlier)

    Example:
        @post_remediate()
        def verify_fixes(context: PluginContext) -> PluginResult:
            # Verify fixes were applied correctly
            return PluginResult.ok()
    """
    return Hook.register(HookType.POST_REMEDIATE, priority)


def on_error(priority: int = 50) -> Callable[[F], F]:
    """Decorator to register an error handler.

    Args:
        priority: Execution priority (lower = earlier)

    Example:
        @on_error()
        def log_error(context: PluginContext, error: Exception) -> PluginResult:
            # Log error details
            return PluginResult.ok()
    """
    return Hook.register(HookType.ON_ERROR, priority)


# Context manager for hook execution


class HookContext:
    """Context manager for executing pre/post hook pairs.

    Example:
        with HookContext(HookType.PRE_CREATE, HookType.POST_CREATE, context):
            # Create document
            pass
    """

    def __init__(
        self,
        pre_hook: HookType,
        post_hook: HookType,
        context: PluginContext,
    ) -> None:
        """Initialize hook context.

        Args:
            pre_hook: Hook to execute on enter
            post_hook: Hook to execute on exit
            context: Plugin context
        """
        self.pre_hook = pre_hook
        self.post_hook = post_hook
        self.context = context
        self.pre_results: list[PluginResult] = []
        self.post_results: list[PluginResult] = []

    def __enter__(self) -> "HookContext":
        """Execute pre-hook on enter."""
        self.pre_results = Hook.execute(self.pre_hook, self.context)
        return self

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[Exception],
        exc_tb: Any,
    ) -> bool:
        """Execute post-hook on exit.

        If an exception occurred, execute error hook first.
        """
        if exc_val is not None:
            Hook.execute(HookType.ON_ERROR, self.context, exc_val)

        self.post_results = Hook.execute(self.post_hook, self.context)
        return False  # Don't suppress exceptions
