"""Claude AI client implementation."""

from typing import Optional
import os

from ucx.ai.base import BaseAIClient
from ucx.exceptions import AIClientError


class ClaudeClient(BaseAIClient):
    """
    Claude AI client using the Anthropic SDK.

    Example:
        >>> client = ClaudeClient(model="opus")
        >>> response = client.generate("Write a haiku about code")
        >>> print(response)
    """

    MODEL_MAP = {
        "opus": "claude-opus-4-5-20251101",
        "sonnet": "claude-sonnet-4-20250514",
        "haiku": "claude-3-5-haiku-20241022",
    }

    def __init__(self, model: str = "opus", api_key: Optional[str] = None):
        """
        Initialize Claude client.

        Args:
            model: Model name (opus, sonnet, haiku) or full model ID
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
        """
        super().__init__(model)

        # Resolve model name to full ID
        self.model_id = self.MODEL_MAP.get(model.lower(), model)

        # Get API key
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")

        self._client = None

    @property
    def client(self):
        """Get or create Anthropic client."""
        if self._client is None:
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                raise AIClientError(
                    "anthropic package not installed. Run: pip install anthropic",
                    model=self.model,
                )
            except Exception as e:
                raise AIClientError(
                    f"Failed to initialize Anthropic client: {e}",
                    model=self.model,
                )
        return self._client

    def generate(
        self,
        prompt: str,
        *,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
    ) -> str:
        """
        Generate text from prompt using Claude.

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate (default: 8192)
            temperature: Sampling temperature

        Returns:
            Generated text

        Raises:
            AIClientError: On API failure
        """
        max_tokens = max_tokens or 8192

        try:
            message = self.client.messages.create(
                model=self.model_id,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ],
            )
            return message.content[0].text

        except Exception as e:
            raise AIClientError(
                f"Claude API error: {e}",
                model=self.model,
            )

    def count_tokens(self, text: str) -> int:
        """
        Estimate token count.

        Uses rough approximation: ~4 characters per token.

        Args:
            text: Text to count

        Returns:
            Estimated number of tokens
        """
        # Rough approximation
        return len(text) // 4
