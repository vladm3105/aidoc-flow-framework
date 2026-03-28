"""Async subprocess runner for CLI AI agents."""

from __future__ import annotations

import asyncio
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .registry import ExecutorConfig


PROMPT_SIZE_THRESHOLD = 4096  # bytes — prompts larger than this use file delivery


@dataclass(frozen=True)
class ExecutorResult:
    """Result from an executor subprocess."""

    stdout: str
    stderr: str
    exit_code: int
    executor_name: str
    prompt_file: str | None = None


async def run_cli_executor(
    config: ExecutorConfig,
    prompt: str,
    working_dir: Path | None = None,
    timeout: int | None = None,
) -> ExecutorResult:
    """Spawn a CLI AI agent subprocess with the given prompt.

    Prompt delivery depends on config.prompt_mode and prompt size:
    - "file": always pipe prompt via stdin
    - "positional": append as argument if short, fall back to stdin if >4KB
    """
    effective_timeout = timeout if timeout is not None else config.timeout
    use_stdin = False
    prompt_file_path: str | None = None

    cmd_parts = [config.command, *config.args]

    if config.prompt_mode == "file":
        use_stdin = True
    elif config.prompt_mode == "positional":
        if len(prompt.encode("utf-8")) > PROMPT_SIZE_THRESHOLD:
            use_stdin = True
        else:
            cmd_parts.append(prompt)
    else:
        cmd_parts.append(prompt)

    # Write prompt to temp file for stdin delivery and debugging
    tmp_file = None
    stdin_data: bytes | None = None
    if use_stdin:
        tmp_file = tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".md",
            prefix="sdd_prompt_",
            delete=False,
            encoding="utf-8",
        )
        tmp_file.write(prompt)
        tmp_file.flush()
        prompt_file_path = tmp_file.name
        tmp_file.close()
        stdin_data = prompt.encode("utf-8")

    env = None
    if config.env:
        import os
        env = {**os.environ, **config.env}

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd_parts,
            stdin=asyncio.subprocess.PIPE if stdin_data else None,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(working_dir) if working_dir else None,
            env=env,
        )

        stdout_bytes, stderr_bytes = await asyncio.wait_for(
            process.communicate(input=stdin_data),
            timeout=effective_timeout,
        )

        return ExecutorResult(
            stdout=stdout_bytes.decode("utf-8", errors="replace"),
            stderr=stderr_bytes.decode("utf-8", errors="replace"),
            exit_code=process.returncode or 0,
            executor_name=config.name,
            prompt_file=prompt_file_path,
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
            prompt_file=prompt_file_path,
        )
    except FileNotFoundError:
        return ExecutorResult(
            stdout="",
            stderr=f"Executor '{config.name}' not found. Ensure '{config.command}' is installed and in PATH.",
            exit_code=-2,
            executor_name=config.name,
            prompt_file=prompt_file_path,
        )
