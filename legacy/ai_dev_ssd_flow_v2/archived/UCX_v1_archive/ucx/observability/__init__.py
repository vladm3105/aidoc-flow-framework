"""UCX Observability Module.

Provides OpenTelemetry tracing, structlog logging, and metrics for UCX operations.

Usage:
    from ucx.observability import setup_observability, get_logger, get_tracer

    # Initialize observability (call once at startup)
    setup_observability(config)

    # Get logger with trace context
    logger = get_logger(__name__)
    logger.info("Processing document", doc_id="BRD-01")

    # Get tracer for spans
    tracer = get_tracer(__name__)
    with tracer.start_as_current_span("ucc_create") as span:
        span.set_attribute("doc_type", "brd")
        ...
"""

from ucx.observability.logging import get_logger, setup_logging
from ucx.observability.tracing import get_tracer, setup_tracing
from ucx.observability.metrics import UCXMetrics, get_metrics
from ucx.observability.context import get_trace_context, inject_trace_context
from ucx.observability.llm_instrumentation import LLMInstrumentation

__all__ = [
    # Logging
    "get_logger",
    "setup_logging",
    # Tracing
    "get_tracer",
    "setup_tracing",
    # Metrics
    "UCXMetrics",
    "get_metrics",
    # Context
    "get_trace_context",
    "inject_trace_context",
    # LLM
    "LLMInstrumentation",
    # Setup helper
    "setup_observability",
]


def setup_observability(config: "UCXConfig") -> None:
    """
    Initialize all observability components.

    Args:
        config: UCX configuration with OTEL settings
    """
    from ucx.config.settings import UCXConfig

    # Setup logging first
    setup_logging(
        level=config.log_level,
        format=config.log_format,
        service_name=config.otel.service_name,
    )

    # Setup tracing if enabled
    if config.otel.enabled:
        setup_tracing(
            service_name=config.otel.service_name,
            service_version=config.otel.service_version,
            endpoint=config.otel.endpoint,
            sample_rate=config.otel.sample_rate,
            console_export=config.otel.console_export,
        )

    # Initialize metrics
    get_metrics(service_name=config.otel.service_name)
