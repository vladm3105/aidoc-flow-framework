"""Open executor registry for CLI and API agents.

Ships with built-in executors. Accepts new ones at runtime via
register_executor() or via executors.json config file at server startup.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class ExecutorType(str, Enum):
    CLI = "cli"
    API = "api"


@dataclass
class ExecutorConfig:
    """Configuration for a CLI or API executor."""

    name: str
    executor_type: ExecutorType
    # CLI fields
    command: str = ""
    args: list[str] = field(default_factory=list)
    prompt_mode: str = ""  # "file" | "positional"
    # API fields (stub for v0.1.0)
    model: str = ""
    api_base: str = ""
    api_key_env: str = ""
    # Common fields
    status: str = "active"  # "active" | "experimental" | "stub"
    timeout: int = 300
    env: dict[str, str] | None = None


BUILTIN_CLI_EXECUTORS: dict[str, dict] = {
    "claude": {
        "command": "claude",
        "args": ["-p", "--output-format", "json", "--verbose"],
        "prompt_mode": "file",
    },
    "codex": {
        "command": "codex",
        "args": ["exec"],
        "prompt_mode": "positional",
    },
    "gemini": {
        "command": "gemini",
        "args": [],
        "prompt_mode": "positional",
    },
    "opencode": {
        "command": "opencode",
        "args": ["run"],
        "prompt_mode": "positional",
    },
    "copilot-cli": {
        "command": "gh",
        "args": ["copilot"],
        "prompt_mode": "positional",
        "status": "experimental",
    },
}

BUILTIN_API_STUBS: dict[str, dict] = {
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
}

_registry: dict[str, ExecutorConfig] = {}


def _build_config(name: str, raw: dict, executor_type: ExecutorType) -> ExecutorConfig:
    return ExecutorConfig(
        name=name,
        executor_type=executor_type,
        command=raw.get("command", ""),
        args=raw.get("args", []),
        prompt_mode=raw.get("prompt_mode", ""),
        model=raw.get("model", ""),
        api_base=raw.get("api_base", ""),
        api_key_env=raw.get("api_key_env", ""),
        status=raw.get("status", "stub" if executor_type == ExecutorType.API else "active"),
        timeout=raw.get("timeout", 300),
        env=raw.get("env"),
    )


def _init_builtins() -> None:
    for name, raw in BUILTIN_CLI_EXECUTORS.items():
        _registry[name] = _build_config(name, raw, ExecutorType.CLI)
    for name, raw in BUILTIN_API_STUBS.items():
        _registry[name] = _build_config(name, raw, ExecutorType.API)


def load_config_file(path: Path) -> int:
    """Load additional executors from a JSON config file. Returns count loaded."""
    if not path.is_file():
        return 0
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        logger.warning("executors.json must be a JSON array, got %s", type(data).__name__)
        return 0
    count = 0
    for entry in data:
        if not isinstance(entry, dict) or "name" not in entry:
            continue
        name = entry["name"]
        exec_type = ExecutorType(entry.get("executor_type", "cli"))
        _registry[name] = _build_config(name, entry, exec_type)
        count += 1
        logger.info("Loaded executor from config: %s (%s)", name, exec_type.value)
    return count


def get_executor(name: str) -> ExecutorConfig:
    """Get executor config by name. Raises KeyError if not registered."""
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
