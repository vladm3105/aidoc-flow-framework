"""LLM instrumentation using OpenTelemetry GenAI semantic conventions.

Implements the OpenTelemetry Semantic Conventions for GenAI (gen_ai.*) to provide
standardized observability for LLM operations.

Reference: https://opentelemetry.io/docs/specs/semconv/gen-ai/
"""

import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Generator, Optional

from opentelemetry import trace
from opentelemetry.trace import Span, SpanKind, Status, StatusCode

from ucx.observability.tracing import get_tracer
from ucx.observability.metrics import get_metrics
from ucx.observability.logging import get_logger


# GenAI Semantic Convention attribute names
class GenAIAttributes:
    """OpenTelemetry GenAI semantic convention attribute names."""

    # System attributes
    SYSTEM = "gen_ai.system"
    REQUEST_MODEL = "gen_ai.request.model"
    RESPONSE_MODEL = "gen_ai.response.model"

    # Token attributes
    REQUEST_MAX_TOKENS = "gen_ai.request.max_tokens"
    REQUEST_TEMPERATURE = "gen_ai.request.temperature"
    REQUEST_TOP_P = "gen_ai.request.top_p"
    USAGE_INPUT_TOKENS = "gen_ai.usage.input_tokens"
    USAGE_OUTPUT_TOKENS = "gen_ai.usage.output_tokens"

    # Response attributes
    RESPONSE_FINISH_REASONS = "gen_ai.response.finish_reasons"
    RESPONSE_ID = "gen_ai.response.id"

    # Content attributes (optional, privacy-sensitive)
    PROMPT = "gen_ai.prompt"
    COMPLETION = "gen_ai.completion"

    # Custom UCX attributes
    UCX_PHASE = "ucx.phase"
    UCX_DOC_TYPE = "ucx.doc_type"
    UCX_DOC_ID = "ucx.doc_id"
    UCX_ITERATION = "ucx.iteration"


@dataclass
class LLMRequest:
    """Represents an LLM request with all relevant parameters."""

    model: str
    prompt: str
    max_tokens: int = 8000
    temperature: float = 0.7
    top_p: float = 1.0
    system: str = "anthropic"

    # UCX-specific context
    phase: Optional[str] = None  # ucc, ucr, ucrem
    doc_type: Optional[str] = None
    doc_id: Optional[str] = None
    iteration: Optional[int] = None


@dataclass
class LLMResponse:
    """Represents an LLM response with usage information."""

    content: str
    model: str
    response_id: str
    input_tokens: int
    output_tokens: int
    finish_reason: str = "end_turn"
    latency_ms: float = 0.0

    @property
    def total_tokens(self) -> int:
        """Total tokens used in request + response."""
        return self.input_tokens + self.output_tokens


class LLMInstrumentation:
    """
    OpenTelemetry instrumentation for LLM operations.

    Provides automatic tracing, metrics, and logging for LLM requests
    following GenAI semantic conventions.

    Usage:
        instrumentation = LLMInstrumentation(capture_content=False)

        with instrumentation.span(request) as span:
            response = await client.generate(request.prompt)
            instrumentation.record_response(span, response)
    """

    def __init__(
        self,
        capture_content: bool = False,
        tracer_name: str = "ucx.llm",
    ) -> None:
        """
        Initialize LLM instrumentation.

        Args:
            capture_content: Whether to capture prompt/completion content
                            (privacy-sensitive, defaults to False)
            tracer_name: Name for the tracer
        """
        self._capture_content = capture_content
        self._tracer = get_tracer(tracer_name)
        self._metrics = get_metrics()
        self._logger = get_logger(tracer_name)

    @contextmanager
    def span(
        self,
        request: LLMRequest,
        operation_name: Optional[str] = None,
    ) -> Generator[Span, None, None]:
        """
        Create an instrumented span for an LLM operation.

        Args:
            request: LLM request parameters
            operation_name: Optional custom operation name

        Yields:
            The created span for additional instrumentation
        """
        span_name = operation_name or f"gen_ai.{request.phase or 'generate'}"

        # Build span attributes
        attributes = {
            GenAIAttributes.SYSTEM: request.system,
            GenAIAttributes.REQUEST_MODEL: request.model,
            GenAIAttributes.REQUEST_MAX_TOKENS: request.max_tokens,
            GenAIAttributes.REQUEST_TEMPERATURE: request.temperature,
            GenAIAttributes.REQUEST_TOP_P: request.top_p,
        }

        # Add UCX-specific attributes
        if request.phase:
            attributes[GenAIAttributes.UCX_PHASE] = request.phase
        if request.doc_type:
            attributes[GenAIAttributes.UCX_DOC_TYPE] = request.doc_type
        if request.doc_id:
            attributes[GenAIAttributes.UCX_DOC_ID] = request.doc_id
        if request.iteration is not None:
            attributes[GenAIAttributes.UCX_ITERATION] = request.iteration

        # Add prompt content if enabled
        if self._capture_content:
            # Truncate to avoid huge spans
            prompt_preview = request.prompt[:1000]
            if len(request.prompt) > 1000:
                prompt_preview += "...[truncated]"
            attributes[GenAIAttributes.PROMPT] = prompt_preview

        start_time = time.perf_counter()

        with self._tracer.start_as_current_span(
            span_name,
            kind=SpanKind.CLIENT,
            attributes=attributes,
        ) as span:
            try:
                # Log request
                self._logger.debug(
                    "LLM request started",
                    model=request.model,
                    phase=request.phase,
                    doc_type=request.doc_type,
                    max_tokens=request.max_tokens,
                )

                yield span

            except Exception as e:
                # Record error
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))

                elapsed_ms = (time.perf_counter() - start_time) * 1000
                self._metrics.llm_errors.add(
                    1,
                    {"model": request.model, "phase": request.phase or "unknown"},
                )

                self._logger.error(
                    "LLM request failed",
                    model=request.model,
                    phase=request.phase,
                    error=str(e),
                    latency_ms=elapsed_ms,
                )
                raise

    def record_response(
        self,
        span: Span,
        response: LLMResponse,
    ) -> None:
        """
        Record LLM response metrics and attributes on the span.

        Args:
            span: The span to record on
            response: LLM response data
        """
        # Add response attributes to span
        span.set_attribute(GenAIAttributes.RESPONSE_MODEL, response.model)
        span.set_attribute(GenAIAttributes.RESPONSE_ID, response.response_id)
        span.set_attribute(GenAIAttributes.USAGE_INPUT_TOKENS, response.input_tokens)
        span.set_attribute(GenAIAttributes.USAGE_OUTPUT_TOKENS, response.output_tokens)
        span.set_attribute(
            GenAIAttributes.RESPONSE_FINISH_REASONS, [response.finish_reason]
        )

        # Add completion content if enabled
        if self._capture_content:
            completion_preview = response.content[:1000]
            if len(response.content) > 1000:
                completion_preview += "...[truncated]"
            span.set_attribute(GenAIAttributes.COMPLETION, completion_preview)

        # Record metrics
        phase = span.attributes.get(GenAIAttributes.UCX_PHASE, "unknown")
        self._metrics.record_llm_request(
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            latency_ms=response.latency_ms,
            model=response.model,
            phase=str(phase),
            success=True,
        )

        # Log success
        self._logger.info(
            "LLM request completed",
            model=response.model,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            latency_ms=response.latency_ms,
            finish_reason=response.finish_reason,
        )

        span.set_status(Status(StatusCode.OK))

    def record_error(
        self,
        span: Span,
        error: Exception,
        request: LLMRequest,
        latency_ms: float,
    ) -> None:
        """
        Record an LLM error on the span.

        Args:
            span: The span to record on
            error: The exception that occurred
            request: The original request
            latency_ms: Latency before error
        """
        span.record_exception(error)
        span.set_status(Status(StatusCode.ERROR, str(error)))

        self._metrics.llm_errors.add(
            1,
            {"model": request.model, "phase": request.phase or "unknown"},
        )

        self._logger.error(
            "LLM request error",
            model=request.model,
            phase=request.phase,
            error=str(error),
            error_type=type(error).__name__,
            latency_ms=latency_ms,
        )


# Convenience function for simple instrumentation
def instrument_llm_call(
    model: str,
    prompt: str,
    phase: Optional[str] = None,
    doc_type: Optional[str] = None,
    capture_content: bool = False,
) -> LLMInstrumentation:
    """
    Create an LLM instrumentation instance for a single call.

    Args:
        model: Model name
        prompt: Prompt text
        phase: UCX phase (ucc, ucr, ucrem)
        doc_type: Document type
        capture_content: Whether to capture content

    Returns:
        Configured LLMInstrumentation instance
    """
    return LLMInstrumentation(capture_content=capture_content)
