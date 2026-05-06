"""Open executor registry for API agents.

Ships with built-in executors. Accepts new ones at runtime via
register_executor() or via executors.json config file at server startup.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class ExecutorType(str, Enum):
    API = "api"


@dataclass
class ExecutorConfig:
    """Configuration for an API executor."""

    name: str
    executor_type: ExecutorType
    # API fields
    model: str = ""
    api_base: str = ""
    api_key_env: str = ""
    # Common fields
    status: str = "active"  # "active" | "experimental" | "stub"
    timeout: int = 300
    env: dict[str, str] | None = None


BUILTIN_API_EXECUTORS: dict[str, dict] = {
    "api/gpt-4o": {
        "model": "gpt-4o",
        "api_key_env": "OPENAI_API_KEY",
    },
    "api/claude-sonnet": {
        "model": "claude-sonnet-4-20250514",
        "api_key_env": "ANTHROPIC_API_KEY",
    },
    "api/gemini-pro": {
        "model": "gemini/gemini-2.5-pro",
        "api_key_env": "GEMINI_API_KEY",
    },
    "api/openrouter": {
        "model": "openrouter/auto",
        "api_key_env": "OPENROUTER_API_KEY",
    },
}

_registry: dict[str, ExecutorConfig] = {}


def _resolve_executor_type(raw_entry: dict, *, source_label: str) -> ExecutorType | None:
    """Resolve executor type, skipping unsupported legacy entries safely."""
    raw_value = str(raw_entry.get("executor_type", "api")).strip().lower()
    if raw_value == "api":
        return ExecutorType.API
    if raw_value == "cli":
        logger.warning(
            "%s executor '%s' uses deprecated executor_type='cli' and was skipped (API-only runtime).",
            source_label,
            raw_entry.get("name", "<unknown>"),
        )
        return None
    logger.warning(
        "%s executor '%s' has unsupported executor_type='%s' and was skipped.",
        source_label,
        raw_entry.get("name", "<unknown>"),
        raw_value,
    )
    return None


def _build_config(name: str, raw: dict, executor_type: ExecutorType) -> ExecutorConfig:
    return ExecutorConfig(
        name=name,
        executor_type=executor_type,
        model=raw.get("model", ""),
        api_base=raw.get("api_base", ""),
        api_key_env=raw.get("api_key_env", ""),
        status=raw.get("status", "active"),
        timeout=raw.get("timeout", 300),
        env=raw.get("env"),
    )


def _init_builtins() -> None:
    for name, raw in BUILTIN_API_EXECUTORS.items():
        _registry[name] = _build_config(name, raw, ExecutorType.API)


def load_config_file(path: Path) -> int:
    """Load executors and optional default_project from a JSON config file.

    Accepts two formats:
    - Object: {"default_project": "...", "executors": [...]}
    - Array (backward-compat): [{...}, ...] treated as executors-only

    Returns count of executors loaded.
    """
    if not path.is_file():
        return 0
    data = json.loads(path.read_text(encoding="utf-8"))

    # Backward-compat: plain array → executors-only
    if isinstance(data, list):
        executors = data
        default_project = None
    elif isinstance(data, dict):
        executors = data.get("executors", [])
        default_project = data.get("default_project")
    else:
        logger.warning("executors.json: expected object or array, got %s", type(data).__name__)
        return 0

    if default_project:
        from mcp_server.project_context import set_config_default
        set_config_default(Path(default_project).expanduser().resolve())

    if not isinstance(executors, list):
        logger.warning("executors.json: 'executors' field must be an array")
        return 0

    count = 0
    for entry in executors:
        if not isinstance(entry, dict) or "name" not in entry:
            continue
        name = entry["name"]
        exec_type = _resolve_executor_type(entry, source_label="Global config")
        if exec_type is None:
            continue
        _registry[name] = _build_config(name, entry, exec_type)
        count += 1
        logger.info("Loaded executor from config: %s (%s)", name, exec_type.value)
    return count


def load_project_executor_config(project_root: Path) -> dict[str, ExecutorConfig]:
    """Load project-specific executor overrides from {project}/UCX/executors.json.

    Returns a dict of executor configs (does NOT modify global registry).
    Returns empty dict if file missing or invalid.
    """
    project_config = project_root / "UCX" / "executors.json"
    if not project_config.is_file():
        return {}

    try:
        data = json.loads(project_config.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Invalid project executors.json at %s: %s", project_config, exc)
        return {}

    # Accept same formats as server config
    if isinstance(data, list):
        executors = data
    elif isinstance(data, dict):
        executors = data.get("executors", [])
    else:
        logger.warning(
            "Project executors.json at %s: expected object or array, got %s",
            project_config, type(data).__name__,
        )
        return {}

    if not isinstance(executors, list):
        logger.warning("Project executors.json at %s: 'executors' must be an array", project_config)
        return {}

    result: dict[str, ExecutorConfig] = {}
    for entry in executors:
        if not isinstance(entry, dict) or "name" not in entry:
            continue
        ename = entry["name"]
        exec_type = _resolve_executor_type(entry, source_label=f"Project config at {project_config}")
        if exec_type is None:
            continue
        result[ename] = _build_config(ename, entry, exec_type)
        logger.info("Loaded project executor override: %s (%s)", ename, exec_type.value)
    return result


def get_executor(name: str, project_overrides: dict[str, ExecutorConfig] | None = None) -> ExecutorConfig:
    """Get executor config by name. Project overrides take precedence over global."""
    if project_overrides and name in project_overrides:
        return project_overrides[name]
    if name not in _registry:
        available = ", ".join(sorted(_registry.keys()))
        raise KeyError(f"Unknown executor '{name}'. Available: {available}")
    return _registry[name]


def list_executors() -> list[ExecutorConfig]:
    """Return all registered executors."""
    return list(_registry.values())


def register_executor(config: ExecutorConfig) -> None:
    """Register or replace an executor at runtime."""
    _registry[config.name] = config
    logger.info("Registered executor: %s (%s)", config.name, config.executor_type.value)


def remove_executor(name: str) -> None:
    """Unregister an executor. Raises KeyError if not found."""
    if name not in _registry:
        raise KeyError(f"Executor '{name}' not found in registry")
    del _registry[name]
    logger.info("Removed executor: %s", name)


# Initialize builtins on import
_init_builtins()
