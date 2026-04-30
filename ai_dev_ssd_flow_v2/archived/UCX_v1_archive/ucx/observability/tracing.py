"""OpenTelemetry tracing configuration for UCX.

Provides distributed tracing with automatic span creation and context propagation.
"""

from contextlib import contextmanager
from typing import Any, Generator, Optional

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider, Span
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.trace import Tracer, Status, StatusCode
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

# Global tracer cache
_tracers: dict[str, Tracer] = {}
_provider: Optional[TracerProvider] = None


def setup_tracing(
    service_name: str = "ucx",
    service_version: str = "1.0.0",
    endpoint: Optional[str] = None,
    sample_rate: float = 1.0,
    console_export: bool = False,
) -> TracerProvider:
    """
    Initialize OpenTelemetry tracing.

    Args:
        service_name: Name of the service for traces
        service_version: Version of the service
        endpoint: OTLP exporter endpoint (e.g., http://localhost:4317)
        sample_rate: Trace sampling rate (0.0 to 1.0)
        console_export: Export traces to console (for debugging)

    Returns:
        Configured TracerProvider
    """
    global _provider

    if _provider is not None:
        return _provider

    # Create resource with service info
    resource = Resource.create({
        SERVICE_NAME: service_name,
        SERVICE_VERSION: service_version,
        "deployment.environment": "development",
    })

    # Create tracer provider
    _provider = TracerProvider(resource=resource)

    # Add OTLP exporter if endpoint configured
    if endpoint:
        try:
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
                OTLPSpanExporter,
            )

            otlp_exporter = OTLPSpanExporter(endpoint=endpoint)
            _provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
        except ImportError:
            pass  # OTLP exporter not available

    # Add console exporter for debugging
    if console_export:
        console_exporter = ConsoleSpanExporter()
        _provider.add_span_processor(BatchSpanProcessor(console_exporter))

    # Set as global provider
    trace.set_tracer_provider(_provider)

    return _provider


def get_tracer(name: str = "ucx") -> Tracer:
    """
    Get an OpenTelemetry tracer instance.

    Args:
        name: Tracer name (typically module name)

    Returns:
        Tracer instance
    """
    if name not in _tracers:
        _tracers[name] = trace.get_tracer(
            name,
            "1.0.0",
            schema_url="https://opentelemetry.io/schemas/1.21.0",
        )
    return _tracers[name]


def get_current_span() -> Optional[Span]:
    """Get the current active span, if any."""
    span = trace.get_current_span()
    if span and span.is_recording():
        return span
    return None


def set_span_attribute(key: str, value: Any) -> None:
    """
    Set an attribute on the current span.

    Args:
        key: Attribute key
        value: Attribute value
    """
    span = get_current_span()
    if span:
        span.set_attribute(key, value)


def set_span_status(status: StatusCode, description: Optional[str] = None) -> None:
    """
    Set the status of the current span.

    Args:
        status: Status code (OK, ERROR, UNSET)
        description: Optional status description
    """
    span = get_current_span()
    if span:
        span.set_status(Status(status, description))


def record_exception(exception: Exception) -> None:
    """
    Record an exception on the current span.

    Args:
        exception: Exception to record
    """
    span = get_current_span()
    if span:
        span.record_exception(exception)
        span.set_status(Status(StatusCode.ERROR, str(exception)))


@contextmanager
def create_span(
    name: str,
    attributes: Optional[dict[str, Any]] = None,
    tracer_name: str = "ucx",
) -> Generator[Span, None, None]:
    """
    Create a new span as a context manager.

    Args:
        name: Span name
        attributes: Optional span attributes
        tracer_name: Name of the tracer to use

    Yields:
        The created span
    """
    tracer = get_tracer(tracer_name)
    with tracer.start_as_current_span(name, attributes=attributes) as span:
        try:
            yield span
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            raise


def extract_context(carrier: dict[str, str]) -> trace.Context:
    """
    Extract trace context from a carrier (e.g., HTTP headers).

    Args:
        carrier: Dictionary containing trace context

    Returns:
        Extracted context
    """
    propagator = TraceContextTextMapPropagator()
    return propagator.extract(carrier)


def inject_context(carrier: dict[str, str]) -> None:
    """
    Inject trace context into a carrier (e.g., HTTP headers).

    Args:
        carrier: Dictionary to inject trace context into
    """
    propagator = TraceContextTextMapPropagator()
    propagator.inject(carrier)
