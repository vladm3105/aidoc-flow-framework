"""Unit tests for AI module."""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock

from ucx.ai.cli_client import CLIClient
from ucx.config.settings import RetryConfig
from ucx.exceptions import AIClientError
from ucx.ai.retry import RetryPolicy, RetryState
from ucx.ai.tokens import TokenCounter, TokenBudget, ContentTruncator


class TestRetryPolicy:
    """Tests for RetryPolicy."""

    def test_default_policy(self):
        """Test default retry policy."""
        policy = RetryPolicy()
        assert policy._config.max_attempts == 3
        assert policy._config.base_delay == 1.0
        assert policy._config.exponential_base == 2.0

    def test_custom_policy(self):
        """Test custom retry policy."""
        config = RetryConfig(
            max_attempts=5,
            base_delay=0.5,
            max_delay=30.0,
            exponential_base=3.0,
        )
        policy = RetryPolicy(config)
        assert policy._config.max_attempts == 5
        assert policy._config.base_delay == 0.5

    def test_calculate_delay(self):
        """Test delay calculation."""
        config = RetryConfig(
            base_delay=1.0,
            exponential_base=2.0,
            jitter=False,
        )
        policy = RetryPolicy(config)

        # First retry: 1 * 2^0 = 1
        delay1 = policy.calculate_delay(1)
        assert delay1 == 1.0

        # Second retry: 1 * 2^1 = 2
        delay2 = policy.calculate_delay(2)
        assert delay2 == 2.0

        # Third retry: 1 * 2^2 = 4
        delay3 = policy.calculate_delay(3)
        assert delay3 == 4.0

    def test_should_retry_retryable_errors(self):
        """Test should_retry for retryable errors."""
        policy = RetryPolicy()

        # Rate limit error should retry (attempt 1, under max)
        # Note: Implementation checks for "rate limit" with space
        assert policy.should_retry(Exception("rate limit exceeded"), attempt=1) is True

        # Timeout error should retry
        assert policy.should_retry(Exception("connection timeout"), attempt=1) is True

        # Connection error (matching exception type) should retry
        assert policy.should_retry(ConnectionError("connection failed"), attempt=1) is True

    def test_should_retry_max_retries(self):
        """Test should_retry respects max retries."""
        config = RetryConfig(max_attempts=2)
        policy = RetryPolicy(config)

        # Under max attempts with retryable error - should retry
        assert policy.should_retry(ConnectionError("connection failed"), attempt=1) is True

        # At max attempts - should not retry even for retryable error
        assert policy.should_retry(ConnectionError("connection failed"), attempt=2) is False


class TestRetryState:
    """Tests for RetryState."""

    def test_state_creation(self):
        """Test creating retry state."""
        state = RetryState()
        assert state.attempt == 0
        assert state.total_delay == 0.0
        assert state.last_error is None

    def test_state_manual_update(self):
        """Test manually updating retry state."""
        state = RetryState()
        state.attempt = 1
        state.total_delay = 1.5
        state.last_error = Exception("test")

        assert state.attempt == 1
        assert state.total_delay == 1.5
        assert state.last_error is not None


class TestTokenCounter:
    """Tests for TokenCounter."""

    def test_counter_initialization(self):
        """Test token counter initialization."""
        counter = TokenCounter()
        assert counter is not None

    def test_count_tokens_empty(self):
        """Test counting empty string."""
        counter = TokenCounter()
        count = counter.count("")
        assert count == 0

    def test_count_tokens_simple(self):
        """Test counting simple text."""
        counter = TokenCounter()
        count = counter.count("Hello, world!")
        assert count > 0

    def test_count_tokens_long(self):
        """Test counting longer text."""
        counter = TokenCounter()
        text = "word " * 1000
        count = counter.count(text)
        assert count > 0


class TestTokenBudget:
    """Tests for TokenBudget."""

    def test_budget_creation(self):
        """Test creating token budget."""
        budget = TokenBudget(
            max_input_tokens=10000,
            max_output_tokens=4000,
            reserve_output_tokens=500,
        )
        assert budget.max_input_tokens == 10000
        assert budget.max_output_tokens == 4000
        assert budget.reserve_output_tokens == 500

    def test_available_tokens(self):
        """Test calculating available tokens."""
        budget = TokenBudget(
            max_input_tokens=10000,
            max_output_tokens=4000,
            reserve_output_tokens=500,
        )
        available = budget.available_input_tokens
        assert available == 10000 - 500  # max_input - reserve

    def test_budget_check_ok(self):
        """Test budget check with sufficient tokens."""
        budget = TokenBudget(
            max_input_tokens=10000,
            max_output_tokens=4000,
            reserve_output_tokens=500,
        )
        is_ok = budget.can_make_request(5000)
        assert is_ok is True

    def test_budget_check_exceeded(self):
        """Test budget check with insufficient tokens."""
        budget = TokenBudget(
            max_input_tokens=10000,
            max_output_tokens=4000,
            reserve_output_tokens=500,
        )
        is_ok = budget.can_make_request(15000)
        assert is_ok is False


class TestContentTruncator:
    """Tests for ContentTruncator."""

    def test_truncator_creation(self):
        """Test creating content truncator."""
        truncator = ContentTruncator(strategy="head")
        assert truncator._strategy == "head"

    def test_truncate_short_content(self):
        """Test truncating short content."""
        truncator = ContentTruncator()
        content = "Short content"
        result = truncator.truncate(content, max_tokens=1000)
        assert result == content

    def test_truncate_long_content(self):
        """Test truncating long content."""
        truncator = ContentTruncator()
        content = "This is a very long piece of content " * 100
        result = truncator.truncate(content, max_tokens=10)
        assert len(result) < len(content)

    def test_truncate_preserves_structure(self):
        """Test truncation with structure preservation."""
        truncator = ContentTruncator(strategy="smart")
        content = "Word1 Word2 Word3 Word4 Word5 Word6 Word7 Word8 Word9 Word10"
        result = truncator.truncate(content, max_tokens=20, preserve_structure=True)
        # Result should be truncated
        assert len(result) <= len(content)


class TestCLIClientResponseValidation:
    """Tests for CLI response-level error detection."""

    def test_generate_rejects_error_like_plain_text(self):
        """CLI text error payloads should raise AIClientError even with exit code 0."""
        client = CLIClient(cli_tool="claude")

        with patch.object(
            client,
            "_execute_cli",
            return_value="Error: rate limit exceeded. Try '--help' for help.",
        ):
            with pytest.raises(AIClientError, match="error-like text response"):
                client.generate("Create a PRD")

    def test_generate_accepts_markdown_document_with_error_words(self):
        """Valid markdown content should pass even if it mentions error handling."""
        client = CLIClient(cli_tool="claude")
        response = """---
title: Test
---

# PRD-01: Platform

## 5. Error Handling

System SHALL handle transient errors with retries.
"""

        with patch.object(client, "_execute_cli", return_value=response):
            generated = client.generate("Create a PRD")

        assert generated == response

    def test_generate_rejects_json_error_payload(self):
        """JSON-style error payloads returned as text should be rejected."""
        client = CLIClient(cli_tool="claude")

        with patch.object(client, "_execute_cli", return_value='{"error":"invalid api key"}'):
            with pytest.raises(AIClientError, match="invalid api key"):
                client.generate("Create a PRD")
