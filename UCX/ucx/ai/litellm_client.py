"""LiteLLM AI client implementation for multi-provider support."""

import datetime
import time
from typing import Optional
import os
import re

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

    PREFLIGHT_PROMPT = (
        "Availability check. Return ONLY the current UTC date in YYYY-MM-DD format. "
        "No prose, no markdown, no explanation."
    )

    # Minimal prompt for the Phase 1 budget/rate-limit probe.
    BUDGET_CHECK_PROMPT = "Return ONLY: OK"
    BUDGET_CHECK_EXPECTED = "OK"
    # Short timeout for the budget probe; fail-fast if the API is unresponsive.
    BUDGET_CHECK_TIMEOUT = 30  # seconds

    # Rate-limit / quota phrases that may appear in API error messages or
    # model output when the service is throttling requests.
    QUOTA_HINT_PATTERNS = [
        "rate limit",
        "rate_limit",
        "quota",
        "too many requests",
        "insufficient_quota",    # OpenAI quota exhausted
        "resource_exhausted",    # Gemini gRPC status
        "overloaded",            # Anthropic overloaded_error
        "429",                   # HTTP Too Many Requests
    ]

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

        # GPT-5 family currently only supports temperature=1.
        effective_temperature = temperature
        model_name = self.model_id.lower()
        if "gpt-5" in model_name and temperature != 1:
            effective_temperature = 1.0
            self.logger.warning(
                f"Model {self.model_id} requires temperature=1. "
                f"Auto-adjusting from {temperature} to {effective_temperature}."
            )

        prompt_tokens = self.count_tokens(prompt)
        system_tokens = self.count_tokens(system_prompt) if system_prompt else 0
        total_input_tokens = prompt_tokens + system_tokens

        self.logger.info(
            f"Generate request: model={self.model_id} provider={self.provider} "
            f"prompt_tokens={prompt_tokens} system_tokens={system_tokens} "
            f"max_tokens={max_tokens} temperature={effective_temperature}"
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
            "temperature": effective_temperature,
        }

        # Add optional parameters
        if self.api_key:
            kwargs["api_key"] = self.api_key
        if self.api_base:
            kwargs["api_base"] = self.api_base

        start_time = time.perf_counter()

        try:
            self._run_availability_preflight()

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

    def _run_availability_preflight(self) -> None:
        """
        Run a 3-phase preflight before every LiteLLM generation call.

        Phase 1 – Budget / rate-limit check
            Send ``BUDGET_CHECK_PROMPT`` ("Return ONLY: OK") with
            ``max_tokens=8`` and ``BUDGET_CHECK_TIMEOUT`` seconds.
            Catch provider-specific rate-limit exceptions.
            Result: ``"ok"`` | ``"quota_exceeded"`` | ``"no_response"``

        Phase 2 – Capability check  (runs ONLY when Phase 1 → ``"no_response"``)
            Verify the model ID is known to LiteLLM via its static model-info
            registry (no network call).  This distinguishes "unknown model" from
            "known model that is temporarily unreachable".

        Phase 3 – Date probe  (runs ONLY when Phase 1 → ``"ok"``)
            Ask the model for the current UTC date and validate the response.
        """
        # ── Phase 1: Budget / rate-limit check ─────────────────────────────
        self.logger.debug(
            "Preflight Phase 1: budget/rate-limit check (%s)", self.provider
        )
        budget_result = self._run_budget_check()

        if budget_result == "quota_exceeded":
            raise AIClientError(
                f"Usage quota or rate limit detected for {self.model_id}. "
                "Choose another model and retry.",
                model=self.model_id,
            )

        if budget_result == "no_response":
            # ── Phase 2: Capability check ───────────────────────────────────
            self.logger.debug(
                "Preflight Phase 2: capability check (%s)", self.provider
            )
            cap_ok, cap_message = self._run_capability_check()
            if not cap_ok:
                raise AIClientError(
                    f"LLM capability check failed for {self.model_id}: {cap_message}",
                    model=self.model_id,
                )
            raise AIClientError(
                f"LLM budget/rate-limit check: no response from {self.model_id} "
                f"(model registered: {cap_message}). "
                "Possible causes: network issue, service outage, or rate limiting.",
                model=self.model_id,
            )

        # ── Phase 3: Date probe ─────────────────────────────────────────────
        self.logger.debug("Preflight Phase 3: date probe (%s)", self.provider)
        expected_utc_date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")

        preflight_kwargs = {
            "model": self.model_id,
            "messages": [{"role": "user", "content": self.PREFLIGHT_PROMPT}],
            "max_tokens": 32,
            "temperature": 0,
        }
        if self.api_key:
            preflight_kwargs["api_key"] = self.api_key
        if self.api_base:
            preflight_kwargs["api_base"] = self.api_base

        response = self.litellm.completion(**preflight_kwargs)
        content = response.choices[0].message.content.strip()
        detected_date = self._extract_iso_date(content)

        if detected_date != expected_utc_date:
            raise AIClientError(
                "LLM availability preflight failed: date probe mismatch. "
                f"Expected UTC date {expected_utc_date}, got '{content}'.",
                model=self.model_id,
            )

        self.logger.debug(
            "LLM preflight passed: expected_utc_date=%s detected_date=%s",
            expected_utc_date,
            detected_date,
        )

    def _run_budget_check(self) -> str:
        """
        Phase 1: Send ``BUDGET_CHECK_PROMPT`` to detect quota / rate-limit issues.

        Uses ``max_tokens=8`` and ``BUDGET_CHECK_TIMEOUT`` seconds so the probe
        consumes negligible tokens and fails fast when the API is throttling.

        Returns:
            ``"ok"``             – API is responsive and within quota.
            ``"quota_exceeded"`` – Provider returned a rate-limit / quota error.
            ``"no_response"``    – Timeout, network error, or empty response.
        """
        try:
            self.logger.debug(
                "Budget check: sending minimal prompt to %s (timeout=%ss)",
                self.model_id,
                self.BUDGET_CHECK_TIMEOUT,
            )
            preflight_kwargs: dict = {
                "model": self.model_id,
                "messages": [{"role": "user", "content": self.BUDGET_CHECK_PROMPT}],
                "max_tokens": 8,
                "temperature": 0,
                "timeout": self.BUDGET_CHECK_TIMEOUT,
            }
            if self.api_key:
                preflight_kwargs["api_key"] = self.api_key
            if self.api_base:
                preflight_kwargs["api_base"] = self.api_base

            response = self.litellm.completion(**preflight_kwargs)
            content = response.choices[0].message.content.strip()

            if not content:
                self.logger.debug("Budget check: empty response from %s", self.model_id)
                return "no_response"

            lower = content.lower()
            if any(p in lower for p in self.QUOTA_HINT_PATTERNS):
                self.logger.warning(
                    "Budget check: quota/rate-limit signal in response from %s: %.80s",
                    self.model_id,
                    content,
                )
                return "quota_exceeded"

            self.logger.debug("Budget check: OK for %s", self.model_id)
            return "ok"

        except Exception as exc:
            err_str = str(exc).lower()
            err_type = type(exc).__name__.lower()
            is_quota = (
                any(p in err_str for p in self.QUOTA_HINT_PATTERNS)
                or "ratelimit" in err_type
                or "quota" in err_type
                or "overloaded" in err_type
                or "resourceexhausted" in err_type
            )
            if is_quota:
                self.logger.warning(
                    "Budget check: quota/rate-limit exception from %s: %s",
                    self.model_id,
                    exc,
                )
                return "quota_exceeded"

            self.logger.debug(
                "Budget check: no_response from %s (%s: %s)",
                self.model_id,
                type(exc).__name__,
                exc,
            )
            return "no_response"

    def _run_capability_check(self) -> tuple[bool, str]:
        """
        Phase 2: Verify the model ID is registered in LiteLLM's static model
        registry.  No network call is made.

        Returns:
            ``(True,  info_str)``  – Model is known; includes max-token count.
            ``(False, error_msg)`` – Model not recognised by LiteLLM.
        """
        try:
            info = self.litellm.get_model_info(self.model_id)
            max_tokens = info.get("max_tokens", "unknown") if info else "unknown"
            msg = f"model={self.model_id} max_tokens={max_tokens}"
            self.logger.debug("Capability check OK for %s: %s", self.model_id, msg)
            return True, msg
        except Exception as exc:
            # get_model_info may raise for unknown / custom models.
            # Treat as a soft pass so custom endpoints aren’t blocked.
            msg = f"model info unavailable for {self.model_id}: {exc}"
            self.logger.debug("Capability check (soft pass): %s", msg)
            return True, msg

    def _extract_iso_date(self, text: str) -> Optional[str]:
        """Extract first ISO date token from response text."""
        match = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", text)
        return match.group(1) if match else None

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
