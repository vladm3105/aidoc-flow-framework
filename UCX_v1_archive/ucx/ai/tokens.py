"""Token counting and budget management for LLM requests.

Provides utilities for counting tokens, managing budgets, and truncating content.
"""

from dataclasses import dataclass, field
from typing import Optional

from ucx.config.settings import TokenConfig
from ucx.observability.logging import get_logger

logger = get_logger(__name__)


class TokenCounter:
    """
    Counts tokens for text content.

    Uses tiktoken for accurate counting when available,
    falls back to character-based estimation.
    """

    def __init__(self, model: str = "cl100k_base") -> None:
        """
        Initialize the token counter.

        Args:
            model: Tiktoken model/encoding name
        """
        self._model = model
        self._encoding = None
        self._tiktoken_available = False

        try:
            import tiktoken
            self._encoding = tiktoken.get_encoding(model)
            self._tiktoken_available = True
            logger.debug("TokenCounter using tiktoken", model=model)
        except ImportError:
            logger.debug("TokenCounter using estimation (tiktoken not available)")

    def count(self, text: str) -> int:
        """
        Count tokens in text.

        Args:
            text: Text to count

        Returns:
            Token count
        """
        if not text:
            return 0

        if self._tiktoken_available and self._encoding:
            return len(self._encoding.encode(text))

        # Fallback: estimate ~4 characters per token for English
        return len(text) // 4

    def count_messages(self, messages: list[dict]) -> int:
        """
        Count tokens in a list of messages.

        Args:
            messages: List of message dicts with 'role' and 'content'

        Returns:
            Total token count
        """
        total = 0
        for msg in messages:
            # Count content
            content = msg.get("content", "")
            total += self.count(content)

            # Add overhead for message structure (~4 tokens per message)
            total += 4

        # Add overhead for conversation structure
        total += 3

        return total


@dataclass
class TokenBudget:
    """
    Manages token budget for a session or request.

    Tracks usage and enforces limits.
    """

    max_input_tokens: int = 100000
    max_output_tokens: int = 8000
    budget_per_session: Optional[int] = None
    reserve_output_tokens: int = 2000

    # Usage tracking
    input_tokens_used: int = 0
    output_tokens_used: int = 0

    @property
    def total_used(self) -> int:
        """Total tokens used."""
        return self.input_tokens_used + self.output_tokens_used

    @property
    def remaining_session_budget(self) -> Optional[int]:
        """Remaining session budget, if limited."""
        if self.budget_per_session is None:
            return None
        return self.budget_per_session - self.total_used

    @property
    def available_input_tokens(self) -> int:
        """Available tokens for next input."""
        available = self.max_input_tokens - self.reserve_output_tokens

        if self.budget_per_session:
            session_remaining = self.budget_per_session - self.total_used
            available = min(available, session_remaining - self.reserve_output_tokens)

        return max(0, available)

    def can_make_request(self, estimated_input: int) -> bool:
        """
        Check if a request can be made within budget.

        Args:
            estimated_input: Estimated input tokens

        Returns:
            True if request is within budget
        """
        if estimated_input > self.available_input_tokens:
            return False

        if self.budget_per_session:
            estimated_total = estimated_input + self.reserve_output_tokens
            if self.total_used + estimated_total > self.budget_per_session:
                return False

        return True

    def record_usage(self, input_tokens: int, output_tokens: int) -> None:
        """
        Record token usage.

        Args:
            input_tokens: Input tokens used
            output_tokens: Output tokens used
        """
        self.input_tokens_used += input_tokens
        self.output_tokens_used += output_tokens

        logger.debug(
            "Token usage recorded",
            input=input_tokens,
            output=output_tokens,
            total=self.total_used,
        )

    def reset(self) -> None:
        """Reset usage counters."""
        self.input_tokens_used = 0
        self.output_tokens_used = 0

    @classmethod
    def from_config(cls, config: TokenConfig) -> "TokenBudget":
        """Create from TokenConfig."""
        return cls(
            max_input_tokens=config.max_input_tokens,
            max_output_tokens=config.max_output_tokens,
            budget_per_session=config.budget_per_session,
            reserve_output_tokens=config.reserve_output_tokens,
        )


class ContentTruncator:
    """
    Truncates content to fit within token limits.

    Supports multiple truncation strategies:
    - head: Keep beginning, truncate end
    - tail: Keep end, truncate beginning
    - middle: Keep beginning and end, truncate middle
    - smart: Truncate at logical boundaries (paragraphs, sections)
    """

    def __init__(
        self,
        strategy: str = "smart",
        counter: Optional[TokenCounter] = None,
    ) -> None:
        """
        Initialize the truncator.

        Args:
            strategy: Truncation strategy
            counter: Token counter to use
        """
        self._strategy = strategy
        self._counter = counter or TokenCounter()

    def truncate(
        self,
        text: str,
        max_tokens: int,
        preserve_structure: bool = True,
    ) -> str:
        """
        Truncate text to fit within token limit.

        Args:
            text: Text to truncate
            max_tokens: Maximum tokens
            preserve_structure: Try to preserve markdown structure

        Returns:
            Truncated text
        """
        current_tokens = self._counter.count(text)

        if current_tokens <= max_tokens:
            return text

        logger.debug(
            "Truncating content",
            current_tokens=current_tokens,
            max_tokens=max_tokens,
            strategy=self._strategy,
        )

        if self._strategy == "head":
            return self._truncate_head(text, max_tokens)
        elif self._strategy == "tail":
            return self._truncate_tail(text, max_tokens)
        elif self._strategy == "middle":
            return self._truncate_middle(text, max_tokens)
        else:  # smart
            return self._truncate_smart(text, max_tokens, preserve_structure)

    def _truncate_head(self, text: str, max_tokens: int) -> str:
        """Keep beginning, truncate end."""
        # Binary search for optimal length
        low, high = 0, len(text)

        while low < high:
            mid = (low + high + 1) // 2
            if self._counter.count(text[:mid]) <= max_tokens:
                low = mid
            else:
                high = mid - 1

        truncated = text[:low]

        # Try to end at sentence boundary
        last_sentence = truncated.rfind(". ")
        if last_sentence > len(truncated) * 0.8:
            truncated = truncated[:last_sentence + 1]

        return truncated + "\n\n[Content truncated...]"

    def _truncate_tail(self, text: str, max_tokens: int) -> str:
        """Keep end, truncate beginning."""
        low, high = 0, len(text)

        while low < high:
            mid = (low + high) // 2
            if self._counter.count(text[mid:]) <= max_tokens:
                high = mid
            else:
                low = mid + 1

        truncated = text[low:]

        # Try to start at paragraph boundary
        first_para = truncated.find("\n\n")
        if first_para > 0 and first_para < len(truncated) * 0.2:
            truncated = truncated[first_para + 2:]

        return "[Earlier content truncated...]\n\n" + truncated

    def _truncate_middle(self, text: str, max_tokens: int) -> str:
        """Keep beginning and end, truncate middle."""
        # Allocate tokens to head and tail
        head_tokens = max_tokens // 2
        tail_tokens = max_tokens - head_tokens - 10  # Reserve for marker

        head = self._truncate_head(text, head_tokens).rstrip("[Content truncated...]").rstrip()
        tail = self._truncate_tail(text, tail_tokens).lstrip("[Earlier content truncated...]").lstrip()

        return f"{head}\n\n[...content truncated...]\n\n{tail}"

    def _truncate_smart(
        self,
        text: str,
        max_tokens: int,
        preserve_structure: bool,
    ) -> str:
        """Truncate at logical boundaries."""
        if not preserve_structure:
            return self._truncate_head(text, max_tokens)

        # Split into sections (markdown headers)
        sections = self._split_sections(text)

        if len(sections) <= 1:
            return self._truncate_head(text, max_tokens)

        # Build result by adding sections until limit
        result_parts = []
        remaining_tokens = max_tokens - 50  # Reserve for truncation note

        for i, section in enumerate(sections):
            section_tokens = self._counter.count(section)

            if remaining_tokens >= section_tokens:
                result_parts.append(section)
                remaining_tokens -= section_tokens
            else:
                # Try to fit partial section
                if remaining_tokens > 100:
                    partial = self._truncate_head(section, remaining_tokens)
                    result_parts.append(partial)
                break

        result = "\n\n".join(result_parts)

        if len(result_parts) < len(sections):
            result += f"\n\n[{len(sections) - len(result_parts)} section(s) truncated...]"

        return result

    def _split_sections(self, text: str) -> list[str]:
        """Split text into sections by markdown headers."""
        import re

        # Split on markdown headers
        sections = re.split(r"(?=^#{1,3}\s)", text, flags=re.MULTILINE)

        # Filter empty sections
        return [s.strip() for s in sections if s.strip()]
