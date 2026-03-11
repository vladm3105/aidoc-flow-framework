"""LiteLLM AI client implementation for multi-provider support."""

import time
from typing import Optional
import os

from ucx.ai.base import BaseAIClient
from ucx.exceptions import AIClientError
from ucx.utils.logging import (
    get_logger,
    log_ai_request,
    log_ai_response,
)


class LiteLLMClient(BaseAIClient):
    """
    LiteLLM-based AI client supporting multiple LLM providers.

    Supports: OpenAI, Anthropic, Azure, Ollama, Gemini, Mistral, and more.

    Model formats:
        - "opus" / "sonnet" / "haiku" → Maps to Claude models
        - "anthropic/claude-opus-4-5-20251101" → Explicit Anthropic
        - "openai/gpt-4o" → OpenAI
        - "azure/gpt-4" → Azure OpenAI
        - "ollama/llama3" → Local Ollama
        - "gemini/gemini-pro" → Google Gemini
        - "mistral/mistral-large" → Mistral AI

    Example:
        >>> client = LiteLLMClient(model="opus")
        >>> response = client.generate("Write a haiku about code")
        >>> print(response)

        >>> # Use OpenAI
        >>> client = LiteLLMClient(model="openai/gpt-4o")

        >>> # Use local Ollama
        >>> client = LiteLLMClient(model="ollama/llama3", api_base="http://localhost:11434")
    """

    # Short aliases for Claude models
    MODEL_ALIASES = {
        "opus": "anthropic/claude-opus-4-5-20251101",
        "sonnet": "anthropic/claude-sonnet-4-20250514",
        "haiku": "anthropic/claude-3-5-haiku-20241022",
    }

    def __init__(
        self,
        model: str = "opus",
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
    ):
        """
        Initialize LiteLLM client.

        Args:
            model: Model identifier. Accepts short aliases (opus, sonnet, haiku)
                   or full LiteLLM format (provider/model-name)
            api_key: API key (defaults to provider-specific env var)
            api_base: Custom API base URL (for proxies, Ollama, etc.)
        """
        super().__init__(model)

        # Resolve aliases to full model names
        self.model_id = self.MODEL_ALIASES.get(model.lower(), model)

        # Store configuration
        self.api_key = api_key
        self.api_base = api_base or os.environ.get("LITELLM_API_BASE")

        self._litellm = None
        self.logger = get_logger("ucx.ai.litellm")

        # Extract provider from model ID
        self.provider = self.model_id.split("/")[0] if "/" in self.model_id else "anthropic"

        self.logger.debug(
            f"Initialized LiteLLMClient: model={self.model_id} provider={self.provider} "
            f"api_base={self.api_base or 'default'}"
        )

    @property
    def litellm(self):
        """Lazy import of litellm module."""
        if self._litellm is None:
            try:
                import litellm
                self._litellm = litellm
                # Disable verbose logging by default
                litellm.set_verbose = False
                self.logger.debug("Loaded litellm module")
            except ImportError:
                self.logger.error("litellm package not installed")
                raise AIClientError(
                    "litellm package not installed. Run: pip install litellm",
                    model=self.model,
                )
        return self._litellm

    def generate(
        self,
        prompt: str,
        *,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Generate text from prompt using LiteLLM.

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate (default: 8192)
            temperature: Sampling temperature
            system_prompt: Optional system prompt

        Returns:
            Generated text

        Raises:
            AIClientError: On API failure
        """
        max_tokens = max_tokens or 8192

        prompt_tokens = self.count_tokens(prompt)
        system_tokens = self.count_tokens(system_prompt) if system_prompt else 0
        total_input_tokens = prompt_tokens + system_tokens

        self.logger.info(
            f"Generate request: model={self.model_id} provider={self.provider} "
            f"prompt_tokens={prompt_tokens} system_tokens={system_tokens} "
            f"max_tokens={max_tokens} temperature={temperature}"
        )

        # Log AI request
        log_ai_request(
            provider=self.provider,
            model=self.model_id,
            prompt_tokens=total_input_tokens,
            operation="generate",
        )

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Build kwargs
        kwargs = {
            "model": self.model_id,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        # Add optional parameters
        if self.api_key:
            kwargs["api_key"] = self.api_key
        if self.api_base:
            kwargs["api_base"] = self.api_base

        start_time = time.perf_counter()

        try:
            self.logger.debug(f"Calling litellm.completion with model={self.model_id}")
            response = self.litellm.completion(**kwargs)

            duration_ms = (time.perf_counter() - start_time) * 1000
            content = response.choices[0].message.content

            # Extract token usage from response if available
            response_tokens = 0
            if hasattr(response, "usage") and response.usage:
                response_tokens = response.usage.completion_tokens or self.count_tokens(content)
                total_tokens = response.usage.total_tokens or (total_input_tokens + response_tokens)
                self.logger.debug(
                    f"Token usage: input={response.usage.prompt_tokens} "
                    f"output={response.usage.completion_tokens} total={total_tokens}"
                )
            else:
                response_tokens = self.count_tokens(content)

            # Log AI response
            log_ai_response(
                provider=self.provider,
                model=self.model_id,
                response_tokens=response_tokens,
                duration_ms=duration_ms,
                success=True,
            )

            self.logger.info(
                f"Generate complete: response_tokens={response_tokens} "
                f"response_chars={len(content)} duration_ms={duration_ms:.0f}"
            )

            return content

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Log failed response
            log_ai_response(
                provider=self.provider,
                model=self.model_id,
                response_tokens=0,
                duration_ms=duration_ms,
                success=False,
            )

            self.logger.error(f"LiteLLM API error: {type(e).__name__}: {e}")
            raise AIClientError(
                f"LiteLLM API error: {e}",
                model=self.model_id,
            )

    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text using LiteLLM's token counter.

        Args:
            text: Text to count

        Returns:
            Number of tokens
        """
        if not text:
            return 0

        try:
            count = self.litellm.token_counter(model=self.model_id, text=text)
            return count
        except Exception as e:
            self.logger.debug(f"Token counting fallback (litellm failed): {e}")
            # Fallback to rough approximation
            return len(text) // 4

    def get_model_info(self) -> dict:
        """
        Get model information from LiteLLM.

        Returns:
            Dict with model metadata (max_tokens, supports_function_calling, etc.)
        """
        try:
            info = self.litellm.get_model_info(self.model_id)
            self.logger.debug(f"Model info for {self.model_id}: {info}")
            return info
        except Exception as e:
            self.logger.debug(f"Failed to get model info: {e}")
            return {"model": self.model_id}

    @classmethod
    def list_models(cls) -> list[str]:
        """
        List available model aliases.

        Returns:
            List of short model aliases
        """
        return list(cls.MODEL_ALIASES.keys())
