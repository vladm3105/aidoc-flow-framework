"""Unit tests for observability module."""

import pytest
from unittest.mock import MagicMock, patch

from ucx.observability.logging import get_logger, setup_logging
from ucx.observability.metrics import UCXMetrics, get_metrics
from ucx.observability.context import get_trace_info, get_trace_id, get_span_id
from ucx.observability.llm_instrumentation import (
    LLMInstrumentation,
    LLMRequest,
    LLMResponse,
)


class TestLogging:
    """Tests for logging module."""

    def test_get_logger_returns_logger(self):
        """Test get_logger returns a structlog logger."""
        logger = get_logger("test_module")
        assert logger is not None

    def test_get_logger_same_name_returns_same_instance(self):
        """Test same logger name returns same instance."""
        logger1 = get_logger("same_module")
        logger2 = get_logger("same_module")
        assert logger1 is logger2

    def test_setup_logging_sets_level(self):
        """Test setup_logging accepts log level."""
        # Should not raise
        setup_logging(level="DEBUG")


class TestMetrics:
    """Tests for metrics module."""

    def test_get_metrics_returns_singleton(self):
        """Test get_metrics returns singleton instance."""
        metrics1 = get_metrics()
        metrics2 = get_metrics()
        assert metrics1 is metrics2

    def test_metrics_record_llm_request(self):
        """Test recording LLM request metrics."""
        metrics = get_metrics()
        # Should not raise
        metrics.record_llm_request(
            input_tokens=100,
            output_tokens=50,
            latency_ms=500.0,
            model="claude-3-opus",
            phase="ucr",
        )

    def test_metrics_record_document_reviewed(self):
        """Test recording document review metrics."""
        metrics = get_metrics()
        metrics.record_document_reviewed(
            doc_type="brd",
            score=85,
            duration_ms=1000.0,
        )

    def test_metrics_record_validation(self):
        """Test recording validation metrics."""
        metrics = get_metrics()
        metrics.record_validation(
            doc_type="prd",
            error_count=2,
            score=75,
        )


class TestTraceContext:
    """Tests for trace context module."""

    def test_get_trace_info_no_span(self):
        """Test get_trace_info with no active span."""
        info = get_trace_info()
        assert "trace_id" in info
        assert "span_id" in info
        # Without active span, values are None
        assert info["trace_id"] is None

    def test_get_trace_id_no_span(self):
        """Test get_trace_id with no active span."""
        trace_id = get_trace_id()
        assert trace_id is None

    def test_get_span_id_no_span(self):
        """Test get_span_id with no active span."""
        span_id = get_span_id()
        assert span_id is None


class TestLLMInstrumentation:
    """Tests for LLM instrumentation module."""

    def test_llm_request_creation(self):
        """Test creating an LLM request."""
        request = LLMRequest(
            model="claude-3-opus",
            prompt="Test prompt",
            max_tokens=1000,
            phase="ucr",
            doc_type="brd",
        )
        assert request.model == "claude-3-opus"
        assert request.prompt == "Test prompt"
        assert request.max_tokens == 1000

    def test_llm_response_creation(self):
        """Test creating an LLM response."""
        response = LLMResponse(
            content="Test response",
            model="claude-3-opus",
            response_id="resp123",
            input_tokens=100,
            output_tokens=50,
            latency_ms=500.0,
        )
        assert response.content == "Test response"
        assert response.input_tokens == 100
        assert response.output_tokens == 50

    def test_llm_instrumentation_init(self):
        """Test LLM instrumentation initialization."""
        instr = LLMInstrumentation(capture_content=False)
        assert instr._capture_content is False
