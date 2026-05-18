"""Integration tests for project_env threading through executor chain."""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import pytest

from mcp_server.executor.cli_runner import ExecutorResult, run_cli_executor
from mcp_server.executor.registry import ExecutorConfig, ExecutorType


def _make_config(**overrides) -> ExecutorConfig:
    defaults = {
        "name": "test-echo",
        "executor_type": ExecutorType.CLI,
        "command": "echo",
        "args": [],
        "prompt_mode": "positional",
        "timeout": 10,
    }
    defaults.update(overrides)
    return ExecutorConfig(**defaults)


class TestProjectEnvThreading:
    def test_project_env_passed_to_subprocess(self) -> None:
        """Verify project_env vars are visible in the subprocess environment."""
        config = _make_config(command="bash", args=["-c", "echo $TEST_PROJECT_VAR"])
        result = asyncio.get_event_loop().run_until_complete(
            run_cli_executor(
                config=config,
                prompt="ignored",
                project_env={"TEST_PROJECT_VAR": "hello_from_env"},
            )
        )
        assert result.exit_code == 0
        assert "hello_from_env" in result.stdout

    def test_project_env_overrides_config_env(self) -> None:
        """project_env should override config.env (merge order: os < config < project)."""
        config = _make_config(
            command="bash",
            args=["-c", "echo $SHARED_KEY"],
            env={"SHARED_KEY": "from_config"},
        )
        result = asyncio.get_event_loop().run_until_complete(
            run_cli_executor(
                config=config,
                prompt="ignored",
                project_env={"SHARED_KEY": "from_project"},
            )
        )
        assert result.exit_code == 0
        assert "from_project" in result.stdout

    def test_missing_project_env_backward_compatible(self) -> None:
        """When project_env is None, executor works as before."""
        config = _make_config(command="echo", args=["hello"])
        result = asyncio.get_event_loop().run_until_complete(
            run_cli_executor(
                config=config,
                prompt="world",
                project_env=None,
            )
        )
        assert result.exit_code == 0
        assert "hello" in result.stdout
