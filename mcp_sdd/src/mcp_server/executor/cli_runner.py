"""Async subprocess runner for CLI AI agents."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path

from .registry import ExecutorConfig


@dataclass(frozen=True)
class ExecutorResult:
    """Result from an executor subprocess."""

    stdout: str
    stderr: str
    exit_code: int
    executor_name: str


async def run_cli_executor(
    config: ExecutorConfig,
    prompt: str,
    working_dir: Path | None = None,
    timeout: int | None = None,
    project_env: dict[str, str] | None = None,
) -> ExecutorResult:
    """Spawn a CLI AI agent subprocess with the given prompt.

    All executors receive the prompt as a positional argument.
    """
    effective_timeout = timeout if timeout is not None else config.timeout

    cmd_parts = [config.command, *config.args, prompt]

    import os
    if config.env or project_env:
        env = {**os.environ, **(config.env or {}), **(project_env or {})}
    else:
        env = None

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd_parts,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(working_dir) if working_dir else None,
            env=env,
        )

        stdout_bytes, stderr_bytes = await asyncio.wait_for(
            process.communicate(),
            timeout=effective_timeout,
        )

        return ExecutorResult(
            stdout=stdout_bytes.decode("utf-8", errors="replace"),
            stderr=stderr_bytes.decode("utf-8", errors="replace"),
            exit_code=process.returncode or 0,
            executor_name=config.name,
        )

    except asyncio.TimeoutError:
        if process.returncode is None:
            process.kill()
            await process.wait()
        return ExecutorResult(
            stdout="",
            stderr=f"Executor '{config.name}' timed out after {effective_timeout}s",
            exit_code=-1,
            executor_name=config.name,
        )
    except FileNotFoundError:
        return ExecutorResult(
            stdout="",
            stderr=f"Executor '{config.name}' not found. Ensure '{config.command}' is installed and in PATH.",
            exit_code=-2,
            executor_name=config.name,
        )
