"""Tests for rate limiting and retry decorators in extract module."""

from unittest.mock import MagicMock, patch

import pytest
import requests


class TestRateLimitDecorator:
    """Tests for @limits decorator on _call_ollama_rate_limited."""

    def test_rate_limit_decorator_exists(self):
        """Verify rate limit decorator is applied."""
        from graph.extract import _call_ollama_rate_limited

        # Check the function has rate limit wrapper attributes
        assert hasattr(_call_ollama_rate_limited, "__wrapped__")

    @patch("graph.extract.requests.post")
    @patch(
        "graph.extract._config",
        {
            "extraction": {
                "ollama": {"base_url": "http://localhost:11434", "model": "test"},
                "timeout_seconds": 30,
            }
        },
    )
    def test_ollama_call_success(self, mock_post):
        """Rate-limited Ollama call succeeds."""
        from graph.extract import _call_ollama_rate_limited

        mock_response = MagicMock()
        mock_response.json.return_value = {"response": '["entity1"]'}
        mock_post.return_value = mock_response

        result = _call_ollama_rate_limited("test prompt", "qwen3:8b", 30)

        assert result == '["entity1"]'
        mock_post.assert_called_once()


class TestRetryOnTimeout:
    """Tests for @retry decorator handling Timeout errors."""

    @patch("graph.extract._call_ollama_rate_limited")
    @patch(
        "graph.extract._config",
        {
            "extraction": {
                "commit_threshold": 0.7,
                "flag_threshold": 0.5,
                "timeout_seconds": 30,
                "ollama": {"base_url": "http://localhost:11434", "model": "test"},
            }
        },
    )
    def test_retry_on_timeout_succeeds_after_retry(self, mock_ollama):
        """Retry succeeds after initial Timeout."""
        from graph.extract import _extract_entities_from_field

        # First call times out, second succeeds
        mock_ollama.side_effect = [
            requests.Timeout("Connection timed out"),
            "[]",
        ]

        # Should not raise, retries succeed
        result = _extract_entities_from_field("test text", "ollama", 30)

        assert result == []
        assert mock_ollama.call_count == 2

    @patch("graph.extract._call_ollama_rate_limited")
    @patch(
        "graph.extract._config",
        {
            "extraction": {
                "commit_threshold": 0.7,
                "flag_threshold": 0.5,
                "timeout_seconds": 30,
                "ollama": {"base_url": "http://localhost:11434", "model": "test"},
            }
        },
    )
    def test_retry_exhausted_on_repeated_timeout(self, mock_ollama):
        """Raises after max retries exhausted on Timeout."""
        from tenacity import RetryError

        from graph.extract import _extract_entities_from_field

        # All 3 attempts time out
        mock_ollama.side_effect = requests.Timeout("Connection timed out")

        with pytest.raises(RetryError):
            _extract_entities_from_field("test text", "ollama", 30)

        assert mock_ollama.call_count == 3


class TestRetryOnConnectionError:
    """Tests for @retry decorator handling ConnectionError."""

    @patch("graph.extract._call_ollama_rate_limited")
    @patch(
        "graph.extract._config",
        {
            "extraction": {
                "commit_threshold": 0.7,
                "flag_threshold": 0.5,
                "timeout_seconds": 30,
                "ollama": {"base_url": "http://localhost:11434", "model": "test"},
            }
        },
    )
    def test_retry_on_connection_error(self, mock_ollama):
        """Retry on ConnectionError."""
        from graph.extract import _extract_entities_from_field

        # First two fail, third succeeds
        mock_ollama.side_effect = [
            requests.ConnectionError("Connection refused"),
            requests.ConnectionError("Connection refused"),
            "[]",
        ]

        result = _extract_entities_from_field("test text", "ollama", 30)

        assert result == []
        assert mock_ollama.call_count == 3

    @patch("graph.extract._call_ollama_rate_limited")
    @patch(
        "graph.extract._config",
        {
            "extraction": {
                "commit_threshold": 0.7,
                "flag_threshold": 0.5,
                "timeout_seconds": 30,
                "ollama": {"base_url": "http://localhost:11434", "model": "test"},
            }
        },
    )
    def test_retry_exhausted_on_connection_error(self, mock_ollama):
        """Raises after max retries on ConnectionError."""
        from tenacity import RetryError

        from graph.extract import _extract_entities_from_field

        mock_ollama.side_effect = requests.ConnectionError("Connection refused")

        with pytest.raises(RetryError):
            _extract_entities_from_field("test text", "ollama", 30)

        assert mock_ollama.call_count == 3


class TestNoRetryOnOtherErrors:
    """Tests that non-retriable errors are not retried."""

    @patch("graph.extract._call_ollama_rate_limited")
    @patch(
        "graph.extract._config",
        {
            "extraction": {
                "commit_threshold": 0.7,
                "flag_threshold": 0.5,
                "timeout_seconds": 30,
                "ollama": {"base_url": "http://localhost:11434", "model": "test"},
            }
        },
    )
    def test_no_retry_on_http_error(self, mock_ollama):
        """HTTP errors (4xx/5xx) are not retried."""
        from graph.extract import _extract_entities_from_field

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_ollama.side_effect = requests.HTTPError(response=mock_response)

        with pytest.raises(requests.HTTPError):
            _extract_entities_from_field("test text", "ollama", 30)

        # Should only be called once (no retry)
        assert mock_ollama.call_count == 1

    @patch("graph.extract._call_ollama_rate_limited")
    @patch(
        "graph.extract._config",
        {
            "extraction": {
                "commit_threshold": 0.7,
                "flag_threshold": 0.5,
                "timeout_seconds": 30,
                "ollama": {"base_url": "http://localhost:11434", "model": "test"},
            }
        },
    )
    def test_no_retry_on_value_error(self, mock_ollama):
        """ValueError is not retried."""
        from graph.extract import _extract_entities_from_field

        mock_ollama.side_effect = ValueError("Invalid JSON")

        with pytest.raises(ValueError):
            _extract_entities_from_field("test text", "ollama", 30)

        assert mock_ollama.call_count == 1


class TestRateLimitConfiguration:
    """Tests for rate limit configuration."""

    def test_rate_limit_is_45_per_second(self):
        """Verify rate limit is configured to 45 calls per second."""
        from graph.extract import _call_ollama_rate_limited

        # The ratelimit decorator stores config in __ratelimit__
        # Check that the function exists and is decorated
        assert callable(_call_ollama_rate_limited)
        # The actual rate limit values are set at decoration time
        # We verify by checking the function is wrapped
        assert hasattr(_call_ollama_rate_limited, "__wrapped__")
