"""Logging utilities."""

import logging
import sys
from typing import Optional

try:
    import structlog
    HAS_STRUCTLOG = True
except ImportError:
    HAS_STRUCTLOG = False


def setup_logging(
    level: str = "INFO",
    format: str = "console",
    name: str = "ucx",
) -> logging.Logger:
    """
    Set up logging for UCX.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        format: Output format (console, json)
        name: Logger name

    Returns:
        Configured logger
    """
    log_level = getattr(logging, level.upper(), logging.INFO)

    if HAS_STRUCTLOG and format == "json":
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.JSONRenderer(),
            ],
            wrapper_class=structlog.stdlib.BoundLogger,
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )
        return structlog.get_logger(name)

    # Standard logging
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(log_level)

        if format == "console":
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        else:
            formatter = logging.Formatter(
                '{"time": "%(asctime)s", "name": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}'
            )

        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def get_logger(name: str = "ucx") -> logging.Logger:
    """Get logger instance."""
    return logging.getLogger(name)
