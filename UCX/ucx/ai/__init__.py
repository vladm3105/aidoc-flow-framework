"""UCX AI client abstraction."""

from ucx.ai.base import BaseAIClient
from ucx.ai.litellm_client import LiteLLMClient

# Keep ClaudeClient for backward compatibility
from ucx.ai.claude import ClaudeClient

# Default client is now LiteLLM
AIClient = LiteLLMClient

__all__ = ["BaseAIClient", "LiteLLMClient", "ClaudeClient", "AIClient"]
