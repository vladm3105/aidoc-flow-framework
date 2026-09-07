"""Structured logging for ucx_hermes operations.

Writes JSON-lines logs to {project_root}/UCX/logs/ucx_hermes.log.
Falls back to stderr if the log directory cannot be created."""

from __future__ import annotations

import json
import logging
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_LOG_SUBDIR = "UCX/logs"
_LOG_FILENAME = "ucx_hermes.log"
_configured_project_root: Path | None = None
_file_handler: logging.FileHandler | None = None

logger = logging.getLogger("ucx_hermes")


class _JsonFormatter(logging.Formatter):
    """Emit each log record as a single JSON line."""

    def format(self, record: logging.LogRecord) -> str:
        entry: dict[str, Any] = {
            "ts": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        # Merge extra fields attached via `extra=` kwarg
        for key in (
            "tool",
            "executor",
            "doc_type",
            "layer",
            "document",
            "exit_code",
            "duration_ms",
            "prompt_chars",
            "stdout_chars",
            "errors",
            "warnings",
            "passes",
            "working_dir",
            "stage",
        ):
            val = getattr(record, key, None)
            if val is not None:
                entry[key] = val
        return json.dumps(entry, default=str)


def configure_logging(project_root: Path) -> Path | None:
    """Set up file logging to project UCX logs directory.

    Returns the log file path, or None if file logging could not be set up.
    """
    global _configured_project_root, _file_handler

    if _configured_project_root == project_root and _file_handler is not None:
        return Path(_file_handler.baseFilename)

    log_dir = project_root / _LOG_SUBDIR
    if not log_dir.parent.exists():
        legacy_dir = project_root / "docs" / "UCX" / "logs"
        if legacy_dir.parent.exists():
            log_dir = legacy_dir
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        return None

    log_path = log_dir / _LOG_FILENAME

    # Remove previous handler if reconfiguring
    if _file_handler is not None:
        logger.removeHandler(_file_handler)
        _file_handler.close()

    handler = logging.FileHandler(str(log_path), encoding="utf-8")
    handler.setFormatter(_JsonFormatter())
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    _file_handler = handler
    _configured_project_root = project_root

    logger.info(
        "ucx_hermes logging configured",
        extra={"tool": "logging_config", "working_dir": str(project_root)},
    )
    return log_path


def log_tool_call(
    tool: str,
    arguments: dict[str, Any],
    project_root: Path | None = None,
) -> float:
    """Log a tool invocation. Returns start time for duration calculation."""
    if project_root is not None:
        configure_logging(project_root)

    extra: dict[str, Any] = {"tool": tool}
    for key in ("doc_type", "layer", "document", "executor"):
        if key in arguments:
            extra[key] = str(arguments[key])

    logger.info(f"tool_call: {tool}", extra=extra)
    return time.monotonic()


def log_tool_result(
    tool: str,
    start_time: float,
    *,
    errors: int = 0,
    warnings: int = 0,
    passes: int = 0,
    is_valid: bool | None = None,
) -> None:
    """Log a tool result with timing."""
    duration_ms = int((time.monotonic() - start_time) * 1000)
    extra: dict[str, Any] = {
        "tool": tool,
        "duration_ms": duration_ms,
        "errors": errors,
        "warnings": warnings,
        "passes": passes,
    }
    status = "passed" if is_valid else ("failed" if is_valid is False else "complete")
    logger.info(f"tool_result: {tool} → {status} ({duration_ms}ms)", extra=extra)


def log_executor_launch(
    executor: str,
    prompt_chars: int,
    working_dir: str | None = None,
    timeout: int | None = None,
) -> float:
    """Log an executor launch. Returns start time."""
    extra: dict[str, Any] = {
        "executor": executor,
        "prompt_chars": prompt_chars,
        "stage": "executor_launch",
    }
    if working_dir:
        extra["working_dir"] = working_dir
    if timeout:
        extra["duration_ms"] = timeout * 1000  # max expected

    logger.info(f"executor_launch: {executor} ({prompt_chars} chars)", extra=extra)
    return time.monotonic()


def log_executor_result(
    executor: str,
    start_time: float,
    exit_code: int,
    stdout_chars: int = 0,
) -> None:
    """Log an executor completion."""
    duration_ms = int((time.monotonic() - start_time) * 1000)
    extra: dict[str, Any] = {
        "executor": executor,
        "exit_code": exit_code,
        "stdout_chars": stdout_chars,
        "duration_ms": duration_ms,
        "stage": "executor_result",
    }
    level = logging.INFO if exit_code == 0 else logging.WARNING
    logger.log(
        level, f"executor_result: {executor} exit={exit_code} ({duration_ms}ms)", extra=extra
    )
