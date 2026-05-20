from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutorResult:
    """Result from an executor run."""

    stdout: str
    stderr: str
    exit_code: int
    executor_name: str
    metadata: dict[str, object] | None = None
