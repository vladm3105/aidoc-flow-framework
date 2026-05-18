"""Trace context propagation utilities.

Provides helpers for extracting and injecting OpenTelemetry trace context
across process boundaries and into logs/requests.
"""

from typing import Any, Optional

from opentelemetry import trace
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator


def get_trace_context() -> dict[str, str]:
    """
    Get the current trace context as a dictionary.

    Returns:
        Dictionary with trace context headers (traceparent, tracestate)
    """
    carrier: dict[str, str] = {}
    propagator = TraceContextTextMapPropagator()
    propagator.inject(carrier)
    return carrier


def inject_trace_context(carrier: dict[str, Any]) -> dict[str, Any]:
    """
    Inject trace context into a carrier dictionary.

    This is useful for adding trace context to outgoing requests,
    message headers, or other contexts.

    Args:
        carrier: Dictionary to inject trace context into

    Returns:
        The carrier with trace context added
    """
    propagator = TraceContextTextMapPropagator()
    propagator.inject(carrier)
    return carrier


def extract_trace_context(carrier: dict[str, str]) -> trace.Context:
    """
    Extract trace context from a carrier dictionary.

    This is useful for restoring trace context from incoming requests,
    message headers, or other contexts.

    Args:
        carrier: Dictionary containing trace context headers

    Returns:
        Extracted trace context
    """
    propagator = TraceContextTextMapPropagator()
    return propagator.extract(carrier)


def get_trace_id() -> Optional[str]:
    """
    Get the current trace ID as a hex string.

    Returns:
        32-character hex trace ID, or None if no active span
    """
    span = trace.get_current_span()
    if span and span.is_recording():
        ctx = span.get_span_context()
        if ctx.is_valid:
            return format(ctx.trace_id, "032x")
    return None


def get_span_id() -> Optional[str]:
    """
    Get the current span ID as a hex string.

    Returns:
        16-character hex span ID, or None if no active span
    """
    span = trace.get_current_span()
    if span and span.is_recording():
        ctx = span.get_span_context()
        if ctx.is_valid:
            return format(ctx.span_id, "016x")
    return None


def get_trace_info() -> dict[str, Optional[str]]:
    """
    Get complete trace information for the current span.

    Returns:
        Dictionary with trace_id, span_id, and trace_flags
    """
    span = trace.get_current_span()
    if span and span.is_recording():
        ctx = span.get_span_context()
        if ctx.is_valid:
            return {
                "trace_id": format(ctx.trace_id, "032x"),
                "span_id": format(ctx.span_id, "016x"),
                "trace_flags": format(ctx.trace_flags, "02x"),
            }
    return {
        "trace_id": None,
        "span_id": None,
        "trace_flags": None,
    }


class TraceContextManager:
    """
    Context manager for handling trace context across operations.

    Usage:
        with TraceContextManager(incoming_headers) as ctx:
            # Operations run within the restored context
            ...
            # Get context to propagate to downstream services
            outgoing_headers = ctx.get_propagation_headers()
    """

    def __init__(self, carrier: Optional[dict[str, str]] = None) -> None:
        """
        Initialize the trace context manager.

        Args:
            carrier: Optional carrier with incoming trace context
        """
        self._carrier = carrier or {}
        self._token: Optional[object] = None

    def __enter__(self) -> "TraceContextManager":
        """Enter the trace context."""
        if self._carrier:
            ctx = extract_trace_context(self._carrier)
            self._token = trace.context.attach(ctx)
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the trace context."""
        if self._token is not None:
            trace.context.detach(self._token)

    def get_propagation_headers(self) -> dict[str, str]:
        """Get headers for propagating trace context to downstream services."""
        return get_trace_context()

    def get_trace_info(self) -> dict[str, Optional[str]]:
        """Get current trace information."""
        return get_trace_info()
