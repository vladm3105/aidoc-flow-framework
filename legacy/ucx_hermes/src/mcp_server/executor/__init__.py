"""Executor package — API agent dispatch for LLM-dependent tools."""

from .registry import (
    ExecutorConfig,
    ExecutorType,
    get_executor,
    list_executors,
    load_project_executor_config,
    register_executor,
    remove_executor,
)
from .dispatcher import run_executor
from .contracts import ExecutorResult

__all__ = [
    "ExecutorConfig",
    "ExecutorResult",
    "ExecutorType",
    "get_executor",
    "list_executors",
    "load_project_executor_config",
    "register_executor",
    "remove_executor",
    "run_executor",
]
