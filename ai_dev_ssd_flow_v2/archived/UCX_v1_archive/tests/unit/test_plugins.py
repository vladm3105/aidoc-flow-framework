"""Unit tests for plugins module."""

import pytest
from pathlib import Path

from ucx.config.settings import UCXConfig
from ucx.plugins.base import (
    UCXPlugin,
    PluginContext,
    PluginResult,
    PluginPriority,
)
from ucx.plugins.registry import PluginRegistry, get_registry
from ucx.plugins.hooks import Hook, HookType, pre_create, post_review


class TestPluginContext:
    """Tests for plugin context."""

    def test_context_creation(self):
        """Test creating a plugin context."""
        config = UCXConfig()
        context = PluginContext(config=config)
        assert context.config is not None
        assert context.phase == ""
        assert context.iteration == 1

    def test_context_get_set(self):
        """Test context data access."""
        config = UCXConfig()
        context = PluginContext(config=config)

        context.set("key", "value")
        assert context.get("key") == "value"
        assert context.get("missing", "default") == "default"


class TestPluginResult:
    """Tests for plugin result."""

    def test_result_ok(self):
        """Test creating success result."""
        result = PluginResult.ok("Success message")
        assert result.success is True
        assert result.message == "Success message"

    def test_result_fail(self):
        """Test creating failure result."""
        result = PluginResult.fail("Error message")
        assert result.success is False
        assert result.message == "Error message"

    def test_result_modified(self):
        """Test creating modified result."""
        result = PluginResult.modified("Data changed")
        assert result.success is True
        assert result.modified is True

    def test_result_stop(self):
        """Test creating stop chain result."""
        result = PluginResult.stop("Stop processing")
        assert result.stop_chain is True


class TestUCXPlugin:
    """Tests for UCX plugin base class."""

    def test_plugin_subclass(self):
        """Test creating a plugin subclass."""

        class TestPlugin(UCXPlugin):
            name = "test-plugin"
            version = "1.0.0"

            def execute(self, context: PluginContext) -> PluginResult:
                return PluginResult.ok()

        plugin = TestPlugin()
        assert plugin.name == "test-plugin"
        assert plugin.version == "1.0.0"
        assert plugin.enabled is True

    def test_plugin_enable_disable(self):
        """Test enabling/disabling plugin."""

        class TestPlugin(UCXPlugin):
            name = "toggle-plugin"
            version = "1.0.0"

            def execute(self, context: PluginContext) -> PluginResult:
                return PluginResult.ok()

        plugin = TestPlugin()
        assert plugin.enabled is True

        plugin.disable()
        assert plugin.enabled is False

        plugin.enable()
        assert plugin.enabled is True

    def test_plugin_should_run(self):
        """Test should_run logic."""

        class TestPlugin(UCXPlugin):
            name = "filter-plugin"
            version = "1.0.0"
            enabled_phases = ["ucr"]

            def execute(self, context: PluginContext) -> PluginResult:
                return PluginResult.ok()

        plugin = TestPlugin()
        config = UCXConfig()

        context_ucr = PluginContext(config=config, phase="ucr")
        context_ucc = PluginContext(config=config, phase="ucc")

        assert plugin.should_run(context_ucr) is True
        assert plugin.should_run(context_ucc) is False


class TestPluginRegistry:
    """Tests for plugin registry."""

    def test_registry_singleton(self):
        """Test registry singleton pattern."""
        registry1 = get_registry()
        registry2 = get_registry()
        assert registry1 is registry2

    def test_registry_register(self):
        """Test registering a plugin."""

        class MyPlugin(UCXPlugin):
            name = "my-plugin"
            version = "1.0.0"

            def execute(self, context: PluginContext) -> PluginResult:
                return PluginResult.ok()

        registry = PluginRegistry()
        plugin = MyPlugin()
        registry.register(plugin)

        assert registry.get("my-plugin") is plugin

    def test_registry_unregister(self):
        """Test unregistering a plugin."""

        class TempPlugin(UCXPlugin):
            name = "temp-plugin"
            version = "1.0.0"

            def execute(self, context: PluginContext) -> PluginResult:
                return PluginResult.ok()

        registry = PluginRegistry()
        plugin = TempPlugin()
        registry.register(plugin)
        assert registry.get("temp-plugin") is not None

        result = registry.unregister("temp-plugin")
        assert result is True
        assert registry.get("temp-plugin") is None


class TestHooks:
    """Tests for hook system."""

    def test_hook_registration(self):
        """Test registering a hook handler."""
        Hook.clear()

        @pre_create()
        def my_pre_create(context: PluginContext) -> PluginResult:
            return PluginResult.ok("Pre-create executed")

        assert len(Hook._handlers[HookType.PRE_CREATE]) == 1

    def test_hook_execution(self):
        """Test executing hooks."""
        Hook.clear()

        @post_review()
        def my_post_review(context: PluginContext) -> PluginResult:
            return PluginResult.ok("Post-review executed")

        config = UCXConfig()
        context = PluginContext(config=config)

        results = Hook.execute(HookType.POST_REVIEW, context)
        assert len(results) == 1
        assert results[0].success is True

    def test_hook_clear(self):
        """Test clearing hooks."""
        Hook.clear()

        @pre_create()
        def temp_hook(context: PluginContext) -> PluginResult:
            return PluginResult.ok()

        assert len(Hook._handlers[HookType.PRE_CREATE]) == 1

        Hook.clear(HookType.PRE_CREATE)
        assert len(Hook._handlers[HookType.PRE_CREATE]) == 0
