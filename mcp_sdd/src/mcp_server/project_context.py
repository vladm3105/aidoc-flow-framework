"""Session and config-level default project resolution.

Resolution order: explicit argument > session override > SDD_DEFAULT_PROJECT env var > config default.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_session_project: Path | None = None
_config_default_project: Path | None = None


def set_config_default(project_root: Path) -> None:
    """Set config-level default project. Called once at server startup from executors.json."""
    global _config_default_project
    _config_default_project = project_root
    logger.info("Config default project set to %s", project_root)


def get_config_default() -> Path | None:
    """Return config-level default project or None."""
    return _config_default_project


def set_session_project(project_root: Path) -> dict[str, Any]:
    """Set session-level default project. Returns confirmation.

    Validates path is a directory (does not require UCX/ subdirectory).
    """
    global _session_project
    if not project_root.is_dir():
        raise ValueError(
            f"Cannot set session project: '{project_root}' is not a directory"
        )
    _session_project = project_root
    logger.info("Session project set to %s", project_root)
    return {
        "session_project": str(project_root),
        "previous": None,
    }


def get_session_project() -> Path | None:
    """Return current session project or None."""
    return _session_project


def clear_session_project() -> None:
    """Clear session project (revert to config/env default)."""
    global _session_project
    _session_project = None
    logger.info("Session project cleared")


def resolve_project(explicit: str | None) -> Path:
    """Resolve project from explicit arg > session > env var > config > error.

    Raises ValueError when no project can be resolved.
    Logs warning if resolved directory no longer exists.
    """
    # 1. Explicit argument
    if explicit:
        return Path(explicit).expanduser().resolve()

    # 2. Session override
    if _session_project is not None:
        if not _session_project.is_dir():
            logger.warning(
                "Session project '%s' no longer exists as a directory", _session_project
            )
        return _session_project

    # 3. SDD_DEFAULT_PROJECT env var
    env_default = os.environ.get("SDD_DEFAULT_PROJECT")
    if env_default:
        resolved = Path(env_default).expanduser().resolve()
        if not resolved.is_dir():
            logger.warning(
                "SDD_DEFAULT_PROJECT='%s' is not a directory", env_default
            )
        return resolved

    # 4. Config default (from executors.json)
    if _config_default_project is not None:
        if not _config_default_project.is_dir():
            logger.warning(
                "Config default project '%s' no longer exists as a directory",
                _config_default_project,
            )
        return _config_default_project

    raise ValueError("No project specified and no default configured")


# ── Per-call project snapshot ──────────────────────────────────────────────

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ProjectContext:
    """Immutable snapshot of project-specific configuration for a single tool call."""

    project_root: Path
    project_env: dict[str, str] = field(default_factory=dict)
    executor_overrides: dict = field(default_factory=dict)
    # executor_overrides typed as dict (not dict[str, ExecutorConfig]) to avoid
    # circular import — registry.py imports are deferred to resolve().

    @staticmethod
    def resolve(project_arg: str | None) -> "ProjectContext | None":
        """Build context from a project argument. Returns None if no project.

        Handles both None and "" as no-project (returns None).
        """
        if not project_arg:
            return None
        project_root = Path(project_arg).expanduser().resolve()

        from mcp_server.env_manager import load_project_env
        from mcp_server.executor.registry import load_project_executor_config

        return ProjectContext(
            project_root=project_root,
            project_env=load_project_env(project_root),
            executor_overrides=load_project_executor_config(project_root),
        )
