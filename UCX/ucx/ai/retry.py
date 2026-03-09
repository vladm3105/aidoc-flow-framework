"""Retry policies for AI client operations.

Provides exponential backoff with jitter for handling transient failures.
"""

import asyncio
import random
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, TypeVar, Union

from ucx.config.settings import RetryConfig
from ucx.observability.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


@dataclass
class RetryState:
    """Tracks state across retry attempts."""

    attempt: int = 0
    total_delay: float = 0.0
    last_error: Optional[Exception] = None
    errors: list[Exception] = field(default_factory=list)


class RetryPolicy:
    """
    Configurable retry policy with exponential backoff.

    Supports:
    - Exponential backoff with configurable base
    - Optional jitter to prevent thundering herd
    - Maximum delay cap
    - Customizable retry conditions
    """

    # Default retryable exceptions
    DEFAULT_RETRYABLE = (
        ConnectionError,
        TimeoutError,
        OSError,
    )

    def __init__(
        self,
        config: Optional[RetryConfig] = None,
        retryable_exceptions: Optional[tuple[type[Exception], ...]] = None,
        retry_condition: Optional[Callable[[Exception], bool]] = None,
    ) -> None:
        """
        Initialize the retry policy.

        Args:
            config: Retry configuration
            retryable_exceptions: Tuple of exception types to retry
            retry_condition: Custom function to determine if error is retryable
        """
        self._config = config or RetryConfig()
        self._retryable_exceptions = retryable_exceptions or self.DEFAULT_RETRYABLE
        self._retry_condition = retry_condition

        logger.debug(
            "RetryPolicy initialized",
            max_attempts=self._config.max_attempts,
            base_delay=self._config.base_delay,
        )

    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for a given attempt number.

        Args:
            attempt: Current attempt number (1-indexed)

        Returns:
            Delay in seconds
        """
        # Exponential backoff
        delay = self._config.base_delay * (
            self._config.exponential_base ** (attempt - 1)
        )

        # Cap at max delay
        delay = min(delay, self._config.max_delay)

        # Add jitter if enabled
        if self._config.jitter:
            jitter = random.uniform(0, delay * 0.1)
            delay += jitter

        return delay

    def should_retry(self, error: Exception, attempt: int) -> bool:
        """
        Determine if an error should be retried.

        Args:
            error: The exception that occurred
            attempt: Current attempt number

        Returns:
            True if should retry
        """
        # Check attempt limit
        if attempt >= self._config.max_attempts:
            return False

        # Check custom condition
        if self._retry_condition:
            return self._retry_condition(error)

        # Check exception type
        if isinstance(error, self._retryable_exceptions):
            return True

        # Check for retryable error messages
        error_str = str(error).lower()
        retryable_messages = [
            "rate limit",
            "timeout",
            "connection",
            "temporarily unavailable",
            "overloaded",
            "529",  # Anthropic overloaded
            "503",  # Service unavailable
            "502",  # Bad gateway
        ]

        return any(msg in error_str for msg in retryable_messages)

    def execute(
        self,
        func: Callable[..., T],
        *args: Any,
        **kwargs: Any,
    ) -> T:
        """
        Execute a function with retry logic.

        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result

        Raises:
            Exception: Last exception if all retries exhausted
        """
        state = RetryState()

        while True:
            state.attempt += 1

            try:
                result = func(*args, **kwargs)
                if state.attempt > 1:
                    logger.info(
                        "Retry succeeded",
                        attempt=state.attempt,
                        total_delay=state.total_delay,
                    )
                return result

            except Exception as e:
                state.last_error = e
                state.errors.append(e)

                if not self.should_retry(e, state.attempt):
                    logger.error(
                        "Retry exhausted",
                        attempt=state.attempt,
                        error=str(e),
                    )
                    raise

                delay = self.calculate_delay(state.attempt)
                state.total_delay += delay

                logger.warning(
                    "Retrying after error",
                    attempt=state.attempt,
                    delay=delay,
                    error=str(e),
                )

                time.sleep(delay)

    async def execute_async(
        self,
        func: Callable[..., T],
        *args: Any,
        **kwargs: Any,
    ) -> T:
        """
        Execute an async function with retry logic.

        Args:
            func: Async function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result

        Raises:
            Exception: Last exception if all retries exhausted
        """
        state = RetryState()

        while True:
            state.attempt += 1

            try:
                result = await func(*args, **kwargs)
                if state.attempt > 1:
                    logger.info(
                        "Async retry succeeded",
                        attempt=state.attempt,
                        total_delay=state.total_delay,
                    )
                return result

            except Exception as e:
                state.last_error = e
                state.errors.append(e)

                if not self.should_retry(e, state.attempt):
                    logger.error(
                        "Async retry exhausted",
                        attempt=state.attempt,
                        error=str(e),
                    )
                    raise

                delay = self.calculate_delay(state.attempt)
                state.total_delay += delay

                logger.warning(
                    "Async retrying after error",
                    attempt=state.attempt,
                    delay=delay,
                    error=str(e),
                )

                await asyncio.sleep(delay)


def with_retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    retryable_exceptions: Optional[tuple[type[Exception], ...]] = None,
) -> Callable:
    """
    Decorator to add retry logic to a function.

    Args:
        max_attempts: Maximum retry attempts
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        retryable_exceptions: Exception types to retry

    Returns:
        Decorated function
    """
    config = RetryConfig(
        max_attempts=max_attempts,
        base_delay=base_delay,
        max_delay=max_delay,
    )
    policy = RetryPolicy(config, retryable_exceptions)

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        if asyncio.iscoroutinefunction(func):
            async def async_wrapper(*args: Any, **kwargs: Any) -> T:
                return await policy.execute_async(func, *args, **kwargs)
            return async_wrapper
        else:
            def sync_wrapper(*args: Any, **kwargs: Any) -> T:
                return policy.execute(func, *args, **kwargs)
            return sync_wrapper

    return decorator
