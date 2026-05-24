"""Integration tests for project_env threading through API executor chain."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp_server.executor.registry import ExecutorConfig, ExecutorType


def _make_config(**overrides) -> ExecutorConfig:
    defaults = {
        "name": "api/test",
        "executor_type": ExecutorType.API,
        "model": "openai/gpt-4o-mini",
        "api_key_env": "TEST_API_KEY",
        "timeout": 10,
    }
    defaults.update(overrides)
    return ExecutorConfig(**defaults)


class TestProjectEnvThreading:
    def test_project_env_passed_to_api_runner(self) -> None:
        config = _make_config()
        mock_response = type(
            "Resp",
            (),
            {
                "choices": [
                    type("Choice", (), {"message": type("Msg", (), {"content": "ok"})()})()
                ],
                "usage": None,
            },
        )()

        mock_litellm = type(
            "LiteLLM",
            (),
            {
                "acompletion": AsyncMock(return_value=mock_response),
                "AuthenticationError": Exception,
                "RateLimitError": Exception,
                "Timeout": Exception,
                "APIError": Exception,
            },
        )()

        with patch.dict("sys.modules", {"litellm": mock_litellm}):
            from mcp_server.executor.api_runner import run_api_executor

            result = asyncio.get_event_loop().run_until_complete(
                run_api_executor(
                    config=config,
                    prompt="hello",
                    project_env={"TEST_API_KEY": "project_key"},
                )
            )

        assert result.exit_code == 0
        call_kwargs = mock_litellm.acompletion.call_args[1]
        assert call_kwargs["api_key"] == "project_key"

    def test_project_env_overrides_config_env(self) -> None:
        config = _make_config(env={"TEST_ENV_FLAG": "from_config"})
        seen = {"value": None}

        async def _fake_completion(*_args, **_kwargs):
            import os

            seen["value"] = os.environ.get("TEST_ENV_FLAG")
            return type(
                "Resp",
                (),
                {
                    "choices": [
                        type("Choice", (), {"message": type("Msg", (), {"content": "ok"})()})()
                    ],
                    "usage": None,
                },
            )()

        mock_litellm = type(
            "LiteLLM",
            (),
            {
                "acompletion": staticmethod(_fake_completion),
                "AuthenticationError": Exception,
                "RateLimitError": Exception,
                "Timeout": Exception,
                "APIError": Exception,
            },
        )()

        with patch.dict("sys.modules", {"litellm": mock_litellm}):
            from mcp_server.executor.api_runner import run_api_executor

            result = asyncio.get_event_loop().run_until_complete(
                run_api_executor(
                    config=config,
                    prompt="hello",
                    project_env={
                        "TEST_API_KEY": "project_key",
                        "TEST_ENV_FLAG": "from_project",
                    },
                )
            )

        assert result.exit_code == 0
        assert seen["value"] == "from_project"
