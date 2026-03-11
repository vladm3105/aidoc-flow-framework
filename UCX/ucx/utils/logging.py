"""Extended logging utilities for UCX."""

import logging
import os
import sys
import time
from contextlib import contextmanager
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Optional

try:
    import structlog
    HAS_STRUCTLOG = True
except ImportError:
    HAS_STRUCTLOG = False


# Global logger instance
_logger: Optional[logging.Logger] = None


def setup_logging(
    level: str = "INFO",
    format: str = "console",
    name: str = "ucx",
    log_file: Optional[Path] = None,
    include_caller: bool = True,
) -> logging.Logger:
    """
    Set up logging for UCX.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        format: Output format (console, json, verbose)
        name: Logger name
        log_file: Optional file to write logs to
        include_caller: Include caller info in logs

    Returns:
        Configured logger
    """
    global _logger

    # Get level from env var if set
    level = os.environ.get("UCX_LOG_LEVEL", level).upper()
    log_level = getattr(logging, level, logging.INFO)

    # Get format from env var if set
    format = os.environ.get("UCX_LOG_FORMAT", format).lower()

    if HAS_STRUCTLOG and format == "json":
        processors = [
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
        ]
        if include_caller:
            processors.append(structlog.processors.CallsiteParameterAdder(
                parameters=[
                    structlog.processors.CallsiteParameter.FILENAME,
                    structlog.processors.CallsiteParameter.LINENO,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                ]
            ))
        processors.append(structlog.processors.JSONRenderer())

        structlog.configure(
            processors=processors,
            wrapper_class=structlog.stdlib.BoundLogger,
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

        # Configure stdlib logging for structlog
        logging.basicConfig(
            format="%(message)s",
            stream=sys.stderr,
            level=log_level,
        )

        _logger = structlog.get_logger(name)
        return _logger

    # Standard logging
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Clear existing handlers
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(log_level)

    if format == "verbose":
        formatter = logging.Formatter(
            "%(asctime)s | %(name)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(funcName)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    elif format == "json":
        formatter = logging.Formatter(
            '{"time": "%(asctime)s", "name": "%(name)s", "level": "%(levelname)s", '
            '"file": "%(filename)s", "line": %(lineno)d, "func": "%(funcName)s", "message": "%(message)s"}'
        )
    else:  # console
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%H:%M:%S",
        )

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(log_level)
        file_handler.setFormatter(logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(filename)s:%(lineno)d | %(message)s"
        ))
        logger.addHandler(file_handler)

    _logger = logger
    return logger


def get_logger(name: str = "ucx") -> logging.Logger:
    """
    Get logger instance.

    Automatically sets up logging if not already configured.
    """
    global _logger

    if _logger is None:
        setup_logging()

    if name == "ucx":
        return _logger

    return logging.getLogger(name)


@contextmanager
def log_context(**kwargs):
    """
    Context manager for adding context to log messages.

    Example:
        >>> with log_context(doc_type="brd", phase="review"):
        ...     logger.info("Processing document")
    """
    logger = get_logger()

    if HAS_STRUCTLOG and hasattr(logger, "bind"):
        bound_logger = logger.bind(**kwargs)
        yield bound_logger
    else:
        # For standard logging, prefix messages
        prefix = " ".join(f"{k}={v}" for k, v in kwargs.items())
        yield _ContextLogger(logger, prefix)


class _ContextLogger:
    """Wrapper to add context prefix to standard logger."""

    def __init__(self, logger: logging.Logger, prefix: str):
        self._logger = logger
        self._prefix = prefix

    def _format(self, msg: str) -> str:
        return f"[{self._prefix}] {msg}"

    def debug(self, msg: str, *args, **kwargs):
        self._logger.debug(self._format(msg), *args, **kwargs)

    def info(self, msg: str, *args, **kwargs):
        self._logger.info(self._format(msg), *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs):
        self._logger.warning(self._format(msg), *args, **kwargs)

    def error(self, msg: str, *args, **kwargs):
        self._logger.error(self._format(msg), *args, **kwargs)

    def exception(self, msg: str, *args, **kwargs):
        self._logger.exception(self._format(msg), *args, **kwargs)


@contextmanager
def log_timing(operation: str, level: str = "DEBUG"):
    """
    Context manager for timing operations.

    Example:
        >>> with log_timing("AI request"):
        ...     response = client.generate(prompt)
    """
    logger = get_logger()
    log_func = getattr(logger, level.lower(), logger.debug)

    start_time = time.perf_counter()
    log_func(f"Starting: {operation}")

    try:
        yield
    finally:
        elapsed = time.perf_counter() - start_time
        log_func(f"Completed: {operation} ({elapsed:.2f}s)")


def log_function_call(level: str = "DEBUG"):
    """
    Decorator for logging function calls with arguments and timing.

    Example:
        >>> @log_function_call()
        ... def process_document(doc_path):
        ...     ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger()
            log_func = getattr(logger, level.lower(), logger.debug)

            # Format arguments for logging
            arg_str = ", ".join(
                [repr(a)[:50] for a in args[:3]] +
                [f"{k}={repr(v)[:30]}" for k, v in list(kwargs.items())[:3]]
            )
            if len(args) > 3 or len(kwargs) > 3:
                arg_str += ", ..."

            func_name = f"{func.__module__}.{func.__name__}"
            log_func(f"Calling {func_name}({arg_str})")

            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                elapsed = time.perf_counter() - start_time
                log_func(f"Returned {func_name} ({elapsed:.2f}s)")
                return result
            except Exception as e:
                elapsed = time.perf_counter() - start_time
                logger.error(f"Failed {func_name} ({elapsed:.2f}s): {type(e).__name__}: {e}")
                raise

        return wrapper
    return decorator


def log_ai_request(
    provider: str,
    model: str,
    prompt_tokens: int,
    operation: str = "generate",
):
    """Log AI request details."""
    logger = get_logger()
    logger.info(
        f"AI Request: provider={provider} model={model} "
        f"prompt_tokens={prompt_tokens} operation={operation}"
    )


def log_ai_response(
    provider: str,
    model: str,
    response_tokens: int,
    duration_ms: float,
    success: bool = True,
):
    """Log AI response details."""
    logger = get_logger()
    status = "success" if success else "failed"
    logger.info(
        f"AI Response: provider={provider} model={model} "
        f"response_tokens={response_tokens} duration_ms={duration_ms:.0f} status={status}"
    )


def log_review_result(
    doc_type: str,
    doc_path: str,
    score: int,
    p0_count: int,
    p1_count: int,
    p2_count: int,
):
    """Log review result summary."""
    logger = get_logger()
    logger.info(
        f"Review Result: doc_type={doc_type} path={doc_path} "
        f"score={score} P0={p0_count} P1={p1_count} P2={p2_count}"
    )


def log_phase_start(phase: str, doc_type: str, target: str):
    """Log phase start."""
    logger = get_logger()
    logger.info(f"Phase Start: phase={phase} doc_type={doc_type} target={target}")


def log_phase_end(phase: str, doc_type: str, success: bool, duration_s: float):
    """Log phase end."""
    logger = get_logger()
    status = "success" if success else "failed"
    logger.info(f"Phase End: phase={phase} doc_type={doc_type} status={status} duration_s={duration_s:.1f}")


def log_cli_command(command: list[str], timeout: int):
    """Log CLI command execution."""
    logger = get_logger()
    cmd_str = " ".join(command[:5])
    if len(command) > 5:
        cmd_str += " ..."
    logger.debug(f"CLI Command: {cmd_str} timeout={timeout}s")


def log_cli_result(command: str, returncode: int, duration_s: float, output_len: int):
    """Log CLI command result."""
    logger = get_logger()
    logger.debug(
        f"CLI Result: command={command} returncode={returncode} "
        f"duration_s={duration_s:.1f} output_len={output_len}"
    )
