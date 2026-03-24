"""Structured logging configuration with OpenTelemetry integration.

Uses structlog for structured logging with automatic trace context injection.
"""

import logging
import sys
from typing import Any, Optional

import structlog
from structlog.types import Processor


# Global logger cache
_loggers: dict[str, structlog.BoundLogger] = {}
_configured = False


def _add_trace_context(
    logger: logging.Logger,
    method_name: str,
    event_dict: dict[str, Any],
) -> dict[str, Any]:
    """Add OpenTelemetry trace context to log events."""
    try:
        from opentelemetry import trace

        span = trace.get_current_span()
        if span and span.is_recording():
            ctx = span.get_span_context()
            if ctx.is_valid:
                event_dict["trace_id"] = format(ctx.trace_id, "032x")
                event_dict["span_id"] = format(ctx.span_id, "016x")
    except ImportError:
        pass  # OpenTelemetry not available

    return event_dict


def _add_service_info(service_name: str) -> Processor:
    """Create processor to add service info to log events."""

    def processor(
        logger: logging.Logger,
        method_name: str,
        event_dict: dict[str, Any],
    ) -> dict[str, Any]:
        event_dict["service"] = service_name
        return event_dict

    return processor


def setup_logging(
    level: str = "INFO",
    format: str = "console",
    service_name: str = "ucx",
    log_file: Optional[str] = None,
) -> None:
    """
    Configure structured logging with OpenTelemetry integration.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        format: Output format (console, json)
        service_name: Service name to include in logs
        log_file: Optional file path for log output
    """
    global _configured

    if _configured:
        return

    # Determine processors based on format
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        _add_service_info(service_name),
        _add_trace_context,
    ]

    if format == "json":
        # JSON format for production
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]
    else:
        # Console format for development
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(
                colors=True,
                exception_formatter=structlog.dev.plain_traceback,
            ),
        ]

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper(), logging.INFO)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
        cache_logger_on_first_use=True,
    )

    # Also configure standard logging for libraries
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stderr,
        level=getattr(logging, level.upper(), logging.INFO),
    )

    # Suppress noisy loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("anthropic").setLevel(logging.WARNING)
    logging.getLogger("opentelemetry").setLevel(logging.WARNING)

    _configured = True


def get_logger(name: str = "ucx") -> structlog.BoundLogger:
    """
    Get a structlog logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Bound logger with context support
    """
    if name not in _loggers:
        _loggers[name] = structlog.get_logger(name)
    return _loggers[name]


def bind_context(**kwargs: Any) -> None:
    """
    Bind context variables to all subsequent log calls.

    Args:
        **kwargs: Key-value pairs to add to log context
    """
    structlog.contextvars.bind_contextvars(**kwargs)


def clear_context() -> None:
    """Clear all bound context variables."""
    structlog.contextvars.clear_contextvars()


def unbind_context(*keys: str) -> None:
    """
    Remove specific keys from the log context.

    Args:
        *keys: Keys to remove
    """
    structlog.contextvars.unbind_contextvars(*keys)
