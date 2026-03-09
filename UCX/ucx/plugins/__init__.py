"""UCX Plugin System.

Provides extensibility through plugins and hooks.
"""

from ucx.plugins.base import UCXPlugin, PluginContext, PluginResult
from ucx.plugins.registry import PluginRegistry, get_registry
from ucx.plugins.hooks import (
    Hook,
    HookType,
    pre_create,
    post_create,
    pre_review,
    post_review,
    pre_remediate,
    post_remediate,
    on_error,
)

__all__ = [
    # Base classes
    "UCXPlugin",
    "PluginContext",
    "PluginResult",
    # Registry
    "PluginRegistry",
    "get_registry",
    # Hooks
    "Hook",
    "HookType",
    "pre_create",
    "post_create",
    "pre_review",
    "post_review",
    "pre_remediate",
    "post_remediate",
    "on_error",
]
