"""Mock AI client for testing."""

from typing import Optional
from ucx.ai.base import BaseAIClient


class MockAIClient(BaseAIClient):
    """
    Mock AI client for testing without API calls.

    Example:
        >>> client = MockAIClient()
        >>> client.add_response("review", "# Review Report\\nScore: 95")
        >>> response = client.generate("Review this document")
        >>> assert "Score: 95" in response
    """

    def __init__(self, model: str = "mock"):
        """Initialize mock client."""
        super().__init__(model)
        self.responses: dict[str, str] = {}
        self.default_response = "Mock response"
        self.call_history: list[str] = []

    def add_response(self, keyword: str, response: str) -> None:
        """
        Add a response for prompts containing keyword.

        Args:
            keyword: Keyword to match in prompt
            response: Response to return
        """
        self.responses[keyword.lower()] = response

    def set_default_response(self, response: str) -> None:
        """Set default response for unmatched prompts."""
        self.default_response = response

    def generate(
        self,
        prompt: str,
        *,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
    ) -> str:
        """
        Return mock response based on prompt keywords.

        Args:
            prompt: Input prompt
            max_tokens: Ignored
            temperature: Ignored

        Returns:
            Mock response
        """
        self.call_history.append(prompt)

        prompt_lower = prompt.lower()
        for keyword, response in self.responses.items():
            if keyword in prompt_lower:
                return response

        return self.default_response

    def count_tokens(self, text: str) -> int:
        """Return estimated token count."""
        return len(text) // 4

    def clear_history(self) -> None:
        """Clear call history."""
        self.call_history.clear()

    @property
    def last_prompt(self) -> Optional[str]:
        """Get last prompt sent."""
        return self.call_history[-1] if self.call_history else None
