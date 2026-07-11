"""API-based LLM execution via LiteLLM.

Uses litellm.acompletion() as universal gateway supporting 100+ LLM providers
including OpenAI, Anthropic, Google, and OpenRouter.
"""

from __future__ import annotations

import contextlib
import logging
import os
import threading

from .contracts import ExecutorResult
from .registry import ExecutorConfig

logger = logging.getLogger(__name__)

# Module-global lock serializing env injection around the LiteLLM call. This is a
# threading.Lock, NOT an asyncio.Lock: the review saga fans branches over a
# ThreadPoolExecutor, each worker running its own event loop via asyncio.run, so
# an asyncio.Lock would bind to whichever loop first created it and raise
# RuntimeError ("bound to a different event loop") under cross-thread contention.
# A threading.Lock is loop-agnostic and safe across those threads. It is held
# across the awaited acompletion call, so parallel API-executor branches serialize
# on env injection — acceptable: correctness over the (currently non-default)
# concurrency of the API path.
_api_env_lock = threading.Lock()


@contextlib.contextmanager
def _inject_env(
    config_env: dict[str, str] | None,
    project_env: dict[str, str] | None,
):
    """Temporarily set config + project env vars in os.environ for LiteLLM.

    Merge order: os.environ (base) < config.env < project_env.
    Restores original values on exit. Respects BLOCKED_ENV_VARS.
    """
    merged = {**(config_env or {}), **(project_env or {})}
    if not merged:
        yield
        return

    from mcp_server.env_manager import BLOCKED_ENV_VARS

    saved: dict[str, str | None] = {}
    for key, val in merged.items():
        if key in BLOCKED_ENV_VARS:
            continue
        saved[key] = os.environ.get(key)  # None if absent
        os.environ[key] = val
    try:
        yield
    finally:
        for key, prev in saved.items():
            if prev is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = prev


def _resolve_overrides(
    config: ExecutorConfig,
    project_env: dict[str, str] | None,
) -> tuple[str, str, int, str]:
    """Return (model, api_base, timeout, api_key_env) with project overrides applied.

    Precedence: UCX_EXECUTOR_* env vars > config fields.
    """
    env = project_env or {}
    model = env.get("UCX_EXECUTOR_MODEL", "") or config.model
    api_base = env.get("UCX_EXECUTOR_API_BASE", "") or config.api_base

    # Validate api_key_env redirect against BLOCKED_ENV_VARS
    raw_key_env = env.get("UCX_EXECUTOR_API_KEY_ENV", "")
    if raw_key_env:
        from mcp_server.env_manager import BLOCKED_ENV_VARS

        if raw_key_env in BLOCKED_ENV_VARS:
            logger.warning(
                "UCX_EXECUTOR_API_KEY_ENV='%s' is a blocked system variable — ignoring",
                raw_key_env,
            )
            api_key_env = config.api_key_env
        else:
            api_key_env = raw_key_env
    else:
        api_key_env = config.api_key_env

    timeout_str = env.get("UCX_EXECUTOR_TIMEOUT", "")
    try:
        timeout = int(timeout_str) if timeout_str else config.timeout
    except ValueError:
        logger.warning(
            "Invalid UCX_EXECUTOR_TIMEOUT='%s', using default %d", timeout_str, config.timeout
        )
        timeout = config.timeout

    return model, api_base, timeout, api_key_env


async def run_api_executor(
    config: ExecutorConfig,
    prompt: str,
    system_prompt: str | None = None,
    timeout: int | None = None,
    project_env: dict[str, str] | None = None,
    generation_params: dict[str, object] | None = None,
) -> ExecutorResult:
    """Execute prompt via LLM API. Requires litellm package."""
    try:
        import litellm
    except ImportError:
        return ExecutorResult(
            stdout="",
            stderr=(
                f"API executor '{config.name}' requires litellm. "
                "Install with: pip install 'hermes-server[api]' or pip install litellm"
            ),
            exit_code=-7,
            executor_name=config.name,
        )

    # Apply UCX_EXECUTOR_* overrides from project env
    model, api_base, cfg_timeout, api_key_env = _resolve_overrides(config, project_env)

    # Resolve API key: project .env > os.environ
    api_key = None
    if api_key_env:
        if project_env:
            api_key = project_env.get(api_key_env)
        if not api_key:
            api_key = os.environ.get(api_key_env)

    effective_timeout = timeout if timeout is not None else cfg_timeout

    messages: list[dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    kwargs: dict = {
        "model": model,
        "messages": messages,
        "timeout": effective_timeout,
    }

    # Optional generation settings for LiteLLM-compatible providers.
    if generation_params:
        if generation_params.get("temperature") is not None:
            kwargs["temperature"] = generation_params["temperature"]
        if generation_params.get("top_p") is not None:
            kwargs["top_p"] = generation_params["top_p"]
        if generation_params.get("max_output_tokens") is not None:
            kwargs["max_tokens"] = generation_params["max_output_tokens"]

        # top_k is provider-specific; pass via extra_body when present.
        if generation_params.get("top_k") is not None:
            kwargs["extra_body"] = {"top_k": generation_params["top_k"]}
    if api_key:
        kwargs["api_key"] = api_key
    if api_base:
        kwargs["api_base"] = api_base

    # Lock serializes env injection so concurrent API calls with different
    # project envs don't interleave os.environ mutations. The lock covers
    # the full acompletion call because LiteLLM may read env vars at any
    # point during request setup. MCP servers typically process one tool
    # call at a time, so this is not a practical bottleneck.
    with _api_env_lock:
        with _inject_env(config.env, project_env):
            try:
                response = await litellm.acompletion(**kwargs)
                choices = getattr(response, "choices", None) or []
                if not choices:
                    # A provider returning zero choices would otherwise raise a bare
                    # IndexError that loses the executor-context wrapping the other
                    # error paths give; surface it as a normal executor failure.
                    return ExecutorResult(
                        stdout="",
                        stderr=f"API executor '{config.name}' returned no choices",
                        exit_code=1,
                        executor_name=config.name,
                        metadata={"model": model, "api_base": api_base},
                    )
                content = choices[0].message.content or ""
                usage_raw = getattr(response, "usage", None)
                usage: dict[str, object] | None = None
                if usage_raw is not None:
                    if isinstance(usage_raw, dict):
                        usage = usage_raw
                    else:
                        usage = {
                            "prompt_tokens": getattr(usage_raw, "prompt_tokens", None),
                            "completion_tokens": getattr(usage_raw, "completion_tokens", None),
                            "total_tokens": getattr(usage_raw, "total_tokens", None),
                        }
                return ExecutorResult(
                    stdout=content,
                    stderr="",
                    exit_code=0,
                    executor_name=config.name,
                    metadata={
                        "model": model,
                        "api_base": api_base,
                        "usage": usage,
                    },
                )
            except litellm.AuthenticationError as exc:
                key_hint = f" (check {api_key_env})" if api_key_env else ""
                return ExecutorResult(
                    stdout="",
                    stderr=f"Authentication failed for '{config.name}'{key_hint}: {exc}",
                    exit_code=-4,
                    executor_name=config.name,
                )
            except litellm.RateLimitError as exc:
                return ExecutorResult(
                    stdout="",
                    stderr=f"Rate limit for '{config.name}': {exc}. Retry after backoff.",
                    exit_code=-5,
                    executor_name=config.name,
                )
            except litellm.Timeout:
                return ExecutorResult(
                    stdout="",
                    stderr=f"Executor '{config.name}' timed out after {effective_timeout}s",
                    exit_code=-1,
                    executor_name=config.name,
                )
            except litellm.APIError as exc:
                return ExecutorResult(
                    stdout="",
                    stderr=f"API error for '{config.name}' (model={model}): {exc}",
                    exit_code=-6,
                    executor_name=config.name,
                )
