"""Routes executor calls by type (CLI or API)."""

from __future__ import annotations

from pathlib import Path

from .registry import ExecutorType, get_executor
from .cli_runner import ExecutorResult, run_cli_executor
from .api_runner import run_api_executor


async def run_executor(
    name: str,
    prompt: str,
    working_dir: Path | None = None,
    timeout: int | None = None,
) -> ExecutorResult:
    """Dispatch to CLI or API executor based on registry type."""
    config = get_executor(name)

    if config.executor_type == ExecutorType.CLI:
        return await run_cli_executor(
            config=config,
            prompt=prompt,
            working_dir=working_dir,
            timeout=timeout,
        )
    elif config.executor_type == ExecutorType.API:
        return await run_api_executor(
            config=config,
            prompt=prompt,
            timeout=timeout,
        )
    else:
        return ExecutorResult(
            stdout="",
            stderr=f"Unknown executor type: {config.executor_type}",
            exit_code=-3,
            executor_name=name,
        )
