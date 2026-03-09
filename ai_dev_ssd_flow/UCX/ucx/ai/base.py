"""Base AI client interface."""

from abc import ABC, abstractmethod
from typing import Optional


class BaseAIClient(ABC):
    """Abstract base class for AI clients."""

    def __init__(self, model: str = "opus"):
        """
        Initialize AI client.

        Args:
            model: Model identifier
        """
        self.model = model

    @abstractmethod
    def generate(
        self,
        prompt: str,
        *,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
    ) -> str:
        """
        Generate text from prompt.

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            Generated text
        """
        pass

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text.

        Args:
            text: Text to count

        Returns:
            Number of tokens
        """
        pass
