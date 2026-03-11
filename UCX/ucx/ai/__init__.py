"""UCX AI client abstraction.

UCX supports two modes of AI interaction:

1. **CLI Mode**: Execute CLI agents (Claude CLI, Gemini CLI, etc.) via shell commands
   - Model parameter: opus/sonnet/haiku passed via --model flag to Claude CLI
   - Default: opus

2. **API Mode**: Direct API calls via LiteLLM to providers (OpenAI, Anthropic, OpenRouter)
   - Model parameter: LiteLLM format (provider/model)

Example:
    >>> # CLI mode - uses Claude CLI with opus model (default)
    >>> from ucx.ai import get_client
    >>> client = get_client(mode="cli", cli_tool="claude")
    >>> response = client.generate("Analyze this code...")

    >>> # CLI mode - uses Claude CLI with sonnet model
    >>> client = get_client(mode="cli", cli_tool="claude", model="sonnet")

    >>> # API mode - uses LiteLLM
    >>> client = get_client(mode="api", model="openai/gpt-4o")
    >>> response = client.generate("Analyze this code...")
"""

from ucx.ai.base import BaseAIClient
from ucx.ai.litellm_client import LiteLLMClient
from ucx.ai.cli_client import CLIClient

# Keep ClaudeClient for backward compatibility
from ucx.ai.claude import ClaudeClient


def get_client(
    mode: str = "cli",
    *,
    # CLI mode options
    cli_tool: str = "claude",
    timeout: int = 300,
    # Model (used in both modes)
    model: str = "opus",
    # API mode only options
    api_key: str = None,
    api_base: str = None,
    # Web search (CLI mode only, currently)
    enable_web_search: bool = False,
    **kwargs,
) -> BaseAIClient:
    """
    Factory function to create the appropriate AI client.

    Args:
        mode: Client mode - "cli" for CLI agents, "api" for LiteLLM API calls
        cli_tool: CLI tool to use (claude, gemini, ollama) - CLI mode
        timeout: Command timeout in seconds - CLI mode
        model: Model name - opus/sonnet/haiku for CLI mode, provider/model for API mode
        api_key: API key - API mode only
        api_base: Custom API base URL - API mode only
        enable_web_search: Enable web search for deeper analysis (Claude CLI only)
        **kwargs: Additional client-specific arguments

    Returns:
        AI client instance

    Example:
        >>> # Use Claude CLI with default opus model
        >>> client = get_client(mode="cli", cli_tool="claude")

        >>> # Use Claude CLI with sonnet model
        >>> client = get_client(mode="cli", cli_tool="claude", model="sonnet")

        >>> # Use Claude CLI with web search enabled
        >>> client = get_client(mode="cli", cli_tool="claude", enable_web_search=True)

        >>> # Use OpenAI API via LiteLLM
        >>> client = get_client(mode="api", model="openai/gpt-4o")

        >>> # Use local Ollama API
        >>> client = get_client(
        ...     mode="api",
        ...     model="ollama/llama3",
        ...     api_base="http://localhost:11434"
        ... )
    """
    mode = mode.lower()

    if mode == "cli":
        # For CLI mode, only pass model if it's a recognized alias
        cli_model = None
        if model and model.lower() in ("opus", "sonnet", "haiku"):
            cli_model = model.lower()
        return CLIClient(
            cli_tool=cli_tool,
            model=cli_model,
            timeout=timeout,
            working_dir=kwargs.get("working_dir"),
            env_vars=kwargs.get("env_vars"),
            enable_web_search=enable_web_search,
        )
    elif mode == "api":
        # Note: Web search not yet supported in API mode
        if enable_web_search:
            import logging
            logging.getLogger("ucx.ai").warning(
                "Web search is only supported in CLI mode with Claude. Ignoring enable_web_search."
            )
        return LiteLLMClient(
            model=model,
            api_key=api_key,
            api_base=api_base,
        )
    else:
        raise ValueError(f"Invalid mode: {mode}. Use 'cli' or 'api'.")


# Default client alias (API mode with LiteLLM)
AIClient = LiteLLMClient

__all__ = [
    "BaseAIClient",
    "LiteLLMClient",
    "CLIClient",
    "ClaudeClient",
    "AIClient",
    "get_client",
]
