"""Integration tests for project_env threading through API executor chain."""

from __future__ import annotations

import asyncio
import sys
import threading
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


class TestEnvLockCrossThread:
    """Regression for HERMES-REVIEW-001 C1 (H2).

    The API-executor env lock must be a module-global ``threading.Lock``, not a
    lazily-created ``asyncio.Lock``. The review saga fans branches over a
    ``ThreadPoolExecutor`` where each worker drives its own event loop via
    ``asyncio.run``; a loop-bound ``asyncio.Lock`` cached on first use would raise
    ``RuntimeError`` ("bound to a different event loop") when a later thread's loop
    tries to acquire it. This test drives ``run_api_executor`` from several threads,
    each with its own ``asyncio.run`` loop, and asserts none raise and none hang.
    """

    def test_env_lock_survives_cross_thread_asyncio_run(self) -> None:
        config = _make_config()

        def _make_response():
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

        async def _fake_completion(*_args, **_kwargs):
            # Hold the lock long enough that the other threads must WAIT on it.
            # Waiting is what makes the loop-bind bug fire: a waiter enqueues a
            # Future on its own loop, and the holder (a different thread/loop)
            # completing the wake-up trips "bound to a different event loop". A
            # no-op yield would take the uncontended fast path and hide the bug.
            await asyncio.sleep(0.1)
            return _make_response()

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

        worker_count = 4
        errors: list[BaseException] = []
        exit_codes: list[int] = []
        lock = threading.Lock()
        # Release all workers together so they collide on the env lock (one wins,
        # the rest must wait — the condition that surfaces the loop-bind bug).
        gate = threading.Barrier(worker_count)

        def _worker() -> None:
            try:
                from mcp_server.executor.api_runner import run_api_executor

                gate.wait(timeout=10)
                result = asyncio.run(
                    run_api_executor(
                        config=config,
                        prompt="hello",
                        project_env={"TEST_API_KEY": "project_key"},
                    )
                )
                with lock:
                    exit_codes.append(result.exit_code)
            except BaseException as exc:  # noqa: BLE001 — capture for assertion
                with lock:
                    errors.append(exc)

        with patch.dict("sys.modules", {"litellm": mock_litellm}):
            threads = [threading.Thread(target=_worker) for _ in range(worker_count)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join(timeout=15)

        assert not any(thread.is_alive() for thread in threads), (
            "a worker hung acquiring the env lock (deadlock/loop-bind regression)"
        )
        assert not errors, f"cross-thread env-lock contention raised: {errors!r}"
        assert exit_codes == [0] * worker_count
