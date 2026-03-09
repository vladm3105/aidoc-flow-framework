"""Plugin registry for UCX.

Manages plugin discovery, loading, and lifecycle.
"""

import importlib
import importlib.util
from pathlib import Path
from typing import Optional, Type

from ucx.config.settings import UCXConfig
from ucx.plugins.base import UCXPlugin, PluginContext, PluginResult, PluginPriority
from ucx.observability.logging import get_logger

logger = get_logger(__name__)

# Global registry instance
_registry: Optional["PluginRegistry"] = None


def get_registry() -> "PluginRegistry":
    """Get the global plugin registry.

    Returns:
        The global PluginRegistry instance
    """
    global _registry
    if _registry is None:
        _registry = PluginRegistry()
    return _registry


class PluginRegistry:
    """
    Registry for UCX plugins.

    Handles:
    - Plugin registration
    - Plugin discovery from directories
    - Hook execution
    - Plugin lifecycle management
    """

    def __init__(self, config: Optional[UCXConfig] = None) -> None:
        """Initialize the plugin registry.

        Args:
            config: UCX configuration
        """
        self._config = config or UCXConfig()
        self._plugins: dict[str, UCXPlugin] = {}
        self._plugin_classes: dict[str, Type[UCXPlugin]] = {}
        self._initialized = False

        logger.debug("PluginRegistry initialized")

    @property
    def plugins(self) -> dict[str, UCXPlugin]:
        """Get all registered plugin instances."""
        return self._plugins.copy()

    def register_class(self, plugin_class: Type[UCXPlugin]) -> None:
        """Register a plugin class.

        Args:
            plugin_class: Plugin class to register
        """
        name = plugin_class.name
        if name in self._plugin_classes:
            logger.warning("Plugin class already registered", plugin=name)
            return

        self._plugin_classes[name] = plugin_class
        logger.debug("Plugin class registered", plugin=name)

    def register(self, plugin: UCXPlugin) -> None:
        """Register a plugin instance.

        Args:
            plugin: Plugin instance to register
        """
        name = plugin.name
        if name in self._plugins:
            logger.warning("Plugin already registered", plugin=name)
            return

        self._plugins[name] = plugin
        logger.info("Plugin registered", plugin=name, version=plugin.version)

    def unregister(self, name: str) -> bool:
        """Unregister a plugin.

        Args:
            name: Plugin name to unregister

        Returns:
            True if plugin was unregistered
        """
        if name in self._plugins:
            del self._plugins[name]
            logger.info("Plugin unregistered", plugin=name)
            return True
        return False

    def get(self, name: str) -> Optional[UCXPlugin]:
        """Get a plugin by name.

        Args:
            name: Plugin name

        Returns:
            Plugin instance or None
        """
        return self._plugins.get(name)

    def discover(self, directory: Path) -> int:
        """Discover and load plugins from a directory.

        Looks for Python files with UCXPlugin subclasses.

        Args:
            directory: Directory to search for plugins

        Returns:
            Number of plugins discovered
        """
        if not directory.exists():
            logger.warning("Plugin directory not found", directory=str(directory))
            return 0

        count = 0
        for path in directory.glob("*.py"):
            if path.name.startswith("_"):
                continue

            try:
                # Load module
                spec = importlib.util.spec_from_file_location(
                    f"ucx_plugin_{path.stem}", path
                )
                if spec is None or spec.loader is None:
                    continue

                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Find plugin classes
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (
                        isinstance(attr, type)
                        and issubclass(attr, UCXPlugin)
                        and attr is not UCXPlugin
                    ):
                        self.register_class(attr)
                        count += 1

            except Exception as e:
                logger.error(
                    "Failed to load plugin",
                    path=str(path),
                    error=str(e),
                )

        logger.info("Plugin discovery complete", directory=str(directory), count=count)
        return count

    def instantiate_all(self) -> int:
        """Instantiate all registered plugin classes.

        Returns:
            Number of plugins instantiated
        """
        count = 0
        for name, plugin_class in self._plugin_classes.items():
            if name not in self._plugins:
                try:
                    plugin = plugin_class(self._config)
                    self.register(plugin)
                    count += 1
                except Exception as e:
                    logger.error(
                        "Failed to instantiate plugin",
                        plugin=name,
                        error=str(e),
                    )

        return count

    def initialize_all(self, context: PluginContext) -> list[PluginResult]:
        """Initialize all plugins.

        Args:
            context: Plugin context

        Returns:
            List of results from each plugin
        """
        results = []
        for plugin in self._get_sorted_plugins():
            if plugin.should_run(context):
                try:
                    result = plugin.on_initialize(context)
                    results.append(result)
                except Exception as e:
                    logger.error(
                        "Plugin initialization failed",
                        plugin=plugin.name,
                        error=str(e),
                    )
                    results.append(PluginResult.fail(str(e)))

        self._initialized = True
        return results

    def shutdown_all(self, context: PluginContext) -> list[PluginResult]:
        """Shutdown all plugins.

        Args:
            context: Plugin context

        Returns:
            List of results from each plugin
        """
        results = []
        for plugin in reversed(self._get_sorted_plugins()):
            try:
                result = plugin.on_shutdown(context)
                results.append(result)
            except Exception as e:
                logger.error(
                    "Plugin shutdown failed",
                    plugin=plugin.name,
                    error=str(e),
                )
                results.append(PluginResult.fail(str(e)))

        self._initialized = False
        return results

    def execute_hook(
        self,
        hook_name: str,
        context: PluginContext,
        error: Optional[Exception] = None,
    ) -> list[PluginResult]:
        """Execute a hook on all applicable plugins.

        Args:
            hook_name: Name of the hook method (e.g., "on_pre_create")
            context: Plugin context
            error: Optional error (for on_error hook)

        Returns:
            List of results from each plugin
        """
        results = []

        for plugin in self._get_sorted_plugins():
            if not plugin.should_run(context):
                continue

            hook_method = getattr(plugin, hook_name, None)
            if hook_method is None:
                continue

            try:
                if hook_name == "on_error" and error is not None:
                    result = hook_method(context, error)
                else:
                    result = hook_method(context)

                results.append(result)

                # Check if chain should stop
                if result.stop_chain:
                    logger.debug(
                        "Plugin chain stopped",
                        plugin=plugin.name,
                        hook=hook_name,
                    )
                    break

            except Exception as e:
                logger.error(
                    "Plugin hook execution failed",
                    plugin=plugin.name,
                    hook=hook_name,
                    error=str(e),
                )
                results.append(PluginResult.fail(str(e)))

        return results

    def _get_sorted_plugins(self) -> list[UCXPlugin]:
        """Get plugins sorted by priority.

        Returns:
            Sorted list of plugins
        """
        return sorted(
            self._plugins.values(),
            key=lambda p: p.priority.value,
        )

    def clear(self) -> None:
        """Clear all registered plugins."""
        self._plugins.clear()
        self._plugin_classes.clear()
        self._initialized = False
        logger.debug("Plugin registry cleared")
