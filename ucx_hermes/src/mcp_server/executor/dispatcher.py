"""Routes executor calls to API executors."""

from __future__ import annotations

from pathlib import Path

from .registry import ExecutorConfig, ExecutorType, get_executor
from .contracts import ExecutorResult
from .api_runner import run_api_executor
from mcp_server.logging_config import log_executor_launch, log_executor_result


async def run_executor(
    name: str,
    prompt: str,
    working_dir: Path | None = None,
    timeout: int | None = None,
    project_env: dict[str, str] | None = None,
    system_prompt: str | None = None,
    project_overrides: dict[str, ExecutorConfig] | None = None,
    generation_params: dict[str, object] | None = None,
) -> ExecutorResult:
    """Dispatch to API executor based on registry type."""
    config = get_executor(name, project_overrides=project_overrides)

    start = log_executor_launch(
        executor=name,
        prompt_chars=len(prompt),
        working_dir=str(working_dir) if working_dir else None,
        timeout=timeout,
    )

    if config.executor_type == ExecutorType.API:
        result = await run_api_executor(
            config=config,
            prompt=prompt,
            system_prompt=system_prompt,
            timeout=timeout,
            project_env=project_env,
            generation_params=generation_params,
        )
    else:
        result = ExecutorResult(
            stdout="",
            stderr=f"Unsupported executor type: {config.executor_type}. API executors only.",
            exit_code=-3,
            executor_name=name,
        )

    log_executor_result(
        executor=name,
        start_time=start,
        exit_code=result.exit_code,
        stdout_chars=len(result.stdout) if result.stdout else 0,
    )
    return result
