"""Unit tests for AI module."""

import datetime
import pytest
from unittest.mock import MagicMock, patch, AsyncMock

from ucx.ai.cli_client import CLIClient
from ucx.ai.litellm_client import LiteLLMClient
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
            "_run_availability_preflight",
            return_value=None,
        ):
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

        with patch.object(client, "_run_availability_preflight", return_value=None):
            with patch.object(client, "_execute_cli", return_value=response):
                generated = client.generate("Create a PRD")

        assert generated == response

    def test_generate_rejects_json_error_payload(self):
        """JSON-style error payloads returned as text should be rejected."""
        client = CLIClient(cli_tool="claude")

        with patch.object(client, "_run_availability_preflight", return_value=None):
            with patch.object(client, "_execute_cli", return_value='{"error":"invalid api key"}'):
                with pytest.raises(AIClientError, match="invalid api key"):
                    client.generate("Create a PRD")

    def test_preflight_passes_and_allows_main_request(self):
        """CLI generate should run all 3 preflight phases and proceed when they all pass."""
        client = CLIClient(cli_tool="claude")
        expected_epoch = str(int(datetime.datetime.now(datetime.timezone.utc).timestamp()))
        main_response = "# PRD-01: Platform\n\n## 1. Document Control\n"

        # Phase 1 budget check gets "OK", Phase 3 epoch probe gets expected_epoch,
        # main generate() call gets the PRD content.
        with patch.object(
            client,
            "_execute_cli",
            side_effect=["OK", expected_epoch, main_response],
        ):
            generated = client.generate("Create a PRD")

        assert generated == main_response

    def test_preflight_blocks_main_request_on_date_mismatch(self):
        """CLI generate should fail early when preflight date probe is incorrect."""
        client = CLIClient(cli_tool="claude")

        with patch.object(client, "_execute_cli", return_value="946684800"):
            with pytest.raises(AIClientError, match="preflight failed"):
                client.generate("Create a PRD")


class TestLiteLLMClientPreflight:
    """Tests for universal preflight in LiteLLM client."""

    def test_preflight_fails_when_date_mismatch(self):
        """LiteLLM client should fail when date probe response is incorrect."""
        client = LiteLLMClient(model="opus")

        class _Msg:
            def __init__(self, content):
                self.content = content

        class _Choice:
            def __init__(self, content):
                self.message = _Msg(content)

        class _Resp:
            def __init__(self, content):
                self.choices = [_Choice(content)]
                self.usage = None

        class _FakeLiteLLM:
            def completion(self, **kwargs):
                return _Resp("946684800")

            def token_counter(self, model, text):
                return max(1, len(text) // 4)

        client._litellm = _FakeLiteLLM()

        with pytest.raises(AIClientError, match="preflight failed"):
            client.generate("Create a PRD")


class TestCLIClientPreflightPhases:
    """Unit tests for the 3-phase CLIClient preflight sub-methods."""

    import subprocess as _subprocess  # used in parametrize side_effects

    # ---- Phase 1: _run_budget_check ----------------------------------------

    def test_budget_check_quota_in_response_returns_quota_exceeded(self):
        """A response containing a quota phrase should return 'quota_exceeded'."""
        client = CLIClient(cli_tool="claude")
        with patch.object(client, "_execute_cli", return_value="rate limit exceeded"):
            assert client._run_budget_check() == "quota_exceeded"

    def test_budget_check_rate_limit_phrase_returns_quota_exceeded(self):
        """'too many requests' in response → 'quota_exceeded'."""
        client = CLIClient(cli_tool="gemini")
        with patch.object(client, "_execute_cli", return_value="Error 429 too many requests"):
            assert client._run_budget_check() == "quota_exceeded"

    def test_budget_check_ok_response_returns_ok(self):
        """A clean 'OK' response → 'ok'."""
        client = CLIClient(cli_tool="claude")
        with patch.object(client, "_execute_cli", return_value="OK"):
            assert client._run_budget_check() == "ok"

    def test_budget_check_empty_response_returns_no_response(self):
        """An empty response → 'no_response'."""
        client = CLIClient(cli_tool="codex")
        with patch.object(client, "_execute_cli", return_value=""):
            assert client._run_budget_check() == "no_response"

    def test_budget_check_timeout_returns_no_response(self):
        """A TimeoutExpired during the budget probe → 'no_response'."""
        import subprocess
        client = CLIClient(cli_tool="claude")
        with patch.object(
            client, "_execute_cli",
            side_effect=subprocess.TimeoutExpired("claude", 30),
        ):
            assert client._run_budget_check() == "no_response"

    def test_budget_check_called_process_error_with_quota_hint(self):
        """CalledProcessError whose stderr contains a quota hint → 'quota_exceeded'."""
        import subprocess
        client = CLIClient(cli_tool="aider")
        exc = subprocess.CalledProcessError(
            1, "aider", output="", stderr="insufficient_quota: plan limit reached"
        )
        with patch.object(client, "_execute_cli", side_effect=exc):
            assert client._run_budget_check() == "quota_exceeded"

    def test_budget_check_called_process_error_without_quota_hint(self):
        """CalledProcessError without a quota hint → 'no_response'."""
        import subprocess
        client = CLIClient(cli_tool="aider")
        exc = subprocess.CalledProcessError(1, "aider", output="", stderr="some other error")
        with patch.object(client, "_execute_cli", side_effect=exc):
            assert client._run_budget_check() == "no_response"

    def test_budget_check_file_not_found_returns_no_response(self):
        """FileNotFoundError (binary missing) → 'no_response'; capability check follows."""
        client = CLIClient(cli_tool="claude")
        with patch.object(client, "_execute_cli", side_effect=FileNotFoundError()):
            assert client._run_budget_check() == "no_response"

    # ---- Phase 1 Ollama: _run_ollama_budget_check --------------------------

    def test_ollama_budget_check_service_running_and_model_found(self):
        """ollama list returns OK and model name present → 'ok'."""
        client = CLIClient(cli_tool="ollama", model="llama3")
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stdout = "llama3   7B   ..."
        with patch("subprocess.run", return_value=mock_proc):
            assert client._run_ollama_budget_check() == "ok"

    def test_ollama_budget_check_model_not_in_list(self):
        """Model absent from ollama list → 'no_response'."""
        client = CLIClient(cli_tool="ollama", model="mistral")
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stdout = "llama3   7B   ..."  # mistral is missing
        with patch("subprocess.run", return_value=mock_proc):
            assert client._run_ollama_budget_check() == "no_response"

    def test_ollama_budget_check_daemon_not_running(self):
        """ollama list fails (daemon down) → 'no_response'."""
        import subprocess
        client = CLIClient(cli_tool="ollama")
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("ollama", 10)):
            assert client._run_ollama_budget_check() == "no_response"

    def test_ollama_budget_check_binary_missing(self):
        """ollama binary not found → 'no_response'."""
        client = CLIClient(cli_tool="ollama")
        with patch("subprocess.run", side_effect=FileNotFoundError()):
            assert client._run_ollama_budget_check() == "no_response"

    # ---- Phase 2: _run_capability_check ------------------------------------

    def test_capability_check_binary_found_and_responsive(self):
        """Version command succeeds → (True, first_line)."""
        client = CLIClient(cli_tool="claude")
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stdout = "claude 1.2.3\n"
        mock_proc.stderr = ""
        with patch("subprocess.run", return_value=mock_proc):
            ok, msg = client._run_capability_check()
        assert ok is True
        assert "claude" in msg

    def test_capability_check_binary_not_found(self):
        """FileNotFoundError for version command → (False, install hint)."""
        client = CLIClient(cli_tool="claude")
        with patch("subprocess.run", side_effect=FileNotFoundError()):
            ok, msg = client._run_capability_check()
        assert ok is False
        assert "not found in PATH" in msg
        assert "npm install" in msg  # install hint should be present

    def test_capability_check_nonzero_exit(self):
        """Version command returning non-zero → (False, exit-code msg)."""
        client = CLIClient(cli_tool="gemini")
        mock_proc = MagicMock()
        mock_proc.returncode = 1
        mock_proc.stdout = ""
        mock_proc.stderr = "some internal error"
        with patch("subprocess.run", return_value=mock_proc):
            ok, msg = client._run_capability_check()
        assert ok is False
        assert "exit code 1" in msg

    def test_capability_check_timeout(self):
        """Version command times out → (False, timeout msg)."""
        import subprocess
        client = CLIClient(cli_tool="codex")
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("codex", 10)):
            ok, msg = client._run_capability_check()
        assert ok is False
        assert "timed out" in msg

    # ---- Full 3-phase preflight flow ---------------------------------------

    def test_preflight_quota_exceeded_raises_immediately(self):
        """Phase 1 quota → AIClientError with retry guidance; Phase 2 not reached."""
        client = CLIClient(cli_tool="claude")
        with patch.object(client, "_run_budget_check", return_value="quota_exceeded"):
            with pytest.raises(AIClientError, match="quota or rate limit"):
                client._run_availability_preflight()

    def test_preflight_no_response_tool_missing_raises_capability_error(self):
        """Phase 1 no_response + Phase 2 failure → AIClientError about missing tool."""
        client = CLIClient(cli_tool="claude")
        with patch.object(client, "_run_budget_check", return_value="no_response"):
            with patch.object(
                client, "_run_capability_check",
                return_value=(False, "claude not found in PATH. Install: npm install -g ..."),
            ):
                with pytest.raises(AIClientError, match="capability check failed"):
                    client._run_availability_preflight()

    def test_preflight_no_response_tool_installed_raises_service_error(self):
        """Phase 1 no_response + Phase 2 pass → AIClientError about service/network."""
        client = CLIClient(cli_tool="claude")
        with patch.object(client, "_run_budget_check", return_value="no_response"):
            with patch.object(
                client, "_run_capability_check",
                return_value=(True, "claude 1.0.0"),
            ):
                with pytest.raises(AIClientError, match="no response from claude"):
                    client._run_availability_preflight()

    def test_preflight_ok_then_date_mismatch_raises(self):
        """Phase 1 ok + Phase 3 date mismatch → AIClientError about date probe."""
        client = CLIClient(cli_tool="claude")
        with patch.object(client, "_run_budget_check", return_value="ok"):
            with patch.object(client, "_execute_cli", return_value="946684800"):
                with pytest.raises(AIClientError, match="preflight failed"):
                    client._run_availability_preflight()

    def test_preflight_accepts_iso_date_when_epoch_is_inconsistent(self):
        """Accept valid ISO date fallback when epoch value in response is inconsistent."""
        client = CLIClient(cli_tool="claude")
        expected = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
        # Simulates Claude-style drift where prose includes the right ISO date,
        # but epoch token maps to a different day.
        response = (
            f"**{expected} in UTC epoch**: `1774252800`\n"
            "(That's 2026-03-21T00:00:00Z. Current moment would vary by time of day.)"
        )

        with patch.object(client, "_run_budget_check", return_value="ok"):
            with patch.object(client, "_execute_cli", return_value=response):
                # Should pass via ISO fallback instead of raising date mismatch.
                client._run_availability_preflight()


class TestLiteLLMClientBudgetCheck:
    """Unit tests for Phase 1 (_run_budget_check) in LiteLLMClient."""

    def _make_client_with_fake_litellm(self, completion_fn=None, get_model_info_fn=None):
        """Helper: create a LiteLLMClient with a fake litellm module."""
        client = LiteLLMClient(model="opus")

        class _Msg:
            def __init__(self, content):
                self.content = content

        class _Choice:
            def __init__(self, content):
                self.message = _Msg(content)

        class _Resp:
            def __init__(self, content):
                self.choices = [_Choice(content)]
                self.usage = None

        class _FakeLiteLLM:
            def completion(self_, **kwargs):
                if completion_fn:
                    return completion_fn(**kwargs)
                return _Resp("OK")

            def token_counter(self_, model, text):
                return max(1, len(text) // 4)

            def get_model_info(self_, model):
                if get_model_info_fn:
                    return get_model_info_fn(model)
                return {"max_tokens": 4096}

        client._litellm = _FakeLiteLLM()
        return client, _Resp

    def test_budget_check_ok_response(self):
        """A clean response (no quota patterns) → 'ok'."""
        client, _Resp = self._make_client_with_fake_litellm(
            completion_fn=lambda **kw: _Resp("OK")
        )
        assert client._run_budget_check() == "ok"

    def test_budget_check_quota_in_content(self):
        """Response text containing a quota phrase → 'quota_exceeded'."""
        client, _Resp = self._make_client_with_fake_litellm(
            completion_fn=lambda **kw: _Resp("Error: rate limit exceeded")
        )
        assert client._run_budget_check() == "quota_exceeded"

    def test_budget_check_empty_content(self):
        """Empty response → 'no_response'."""
        client, _Resp = self._make_client_with_fake_litellm(
            completion_fn=lambda **kw: _Resp("")
        )
        assert client._run_budget_check() == "no_response"

    def test_budget_check_rate_limit_exception(self):
        """A RateLimitError-named exception → 'quota_exceeded'."""
        client, _ = self._make_client_with_fake_litellm()

        class FakeRateLimitError(Exception):
            pass

        def _raise(**kw):
            raise FakeRateLimitError("rate limit exceeded")

        client._litellm.completion = _raise  # type: ignore[method-assign]
        # Exception name doesn't contain 'ratelimit' but message does
        assert client._run_budget_check() == "quota_exceeded"

    def test_budget_check_network_error_returns_no_response(self):
        """A generic network exception → 'no_response'."""
        client, _ = self._make_client_with_fake_litellm()

        def _raise(**kw):
            raise ConnectionError("network unreachable")

        client._litellm.completion = _raise  # type: ignore[method-assign]
        assert client._run_budget_check() == "no_response"

    def test_capability_check_model_known(self):
        """get_model_info returns data → (True, info string)."""
        client, _ = self._make_client_with_fake_litellm(
            get_model_info_fn=lambda m: {"max_tokens": 8192}
        )
        ok, msg = client._run_capability_check()
        assert ok is True
        assert "max_tokens=8192" in msg

    def test_capability_check_model_unknown_soft_pass(self):
        """get_model_info raises for unknown model → (True, soft-pass message)."""
        client, _ = self._make_client_with_fake_litellm(
            get_model_info_fn=lambda m: (_ for _ in ()).throw(ValueError("unknown model"))
        )
        ok, msg = client._run_capability_check()
        # Unknown models should soft-pass to avoid blocking custom endpoints
        assert ok is True
        assert "unavailable" in msg
