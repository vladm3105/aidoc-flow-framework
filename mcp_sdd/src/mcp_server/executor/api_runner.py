"""Stub for API-based LLM execution via LiteLLM.

Not implemented in v0.1.0. Raises NotImplementedError with install guidance.
When implemented (v0.2.0): uses litellm.acompletion() as universal gateway
supporting 100+ LLM providers.
"""

from __future__ import annotations

from .registry import ExecutorConfig
from .cli_runner import ExecutorResult


async def run_api_executor(
    config: ExecutorConfig,
    prompt: str,
    system_prompt: str | None = None,
    timeout: int | None = None,
) -> ExecutorResult:
    """Execute prompt via LLM API. Requires litellm package.

    Raises NotImplementedError in v0.1.0.
    """
    raise NotImplementedError(
        f"API executor '{config.name}' (model={config.model}) is not yet implemented. "
        "API executor support requires the litellm package: pip install litellm. "
        "Implementation planned for v0.2.0."
    )
