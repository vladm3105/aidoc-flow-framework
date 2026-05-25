"""Tests for API executor (LiteLLM integration)."""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import pytest
from mcp_server.executor.registry import ExecutorConfig, ExecutorType


def _api_config(
    name: str = "api/test", model: str = "test-model", api_key_env: str = "TEST_API_KEY", **kw
) -> ExecutorConfig:
    return ExecutorConfig(
        name=name,
        executor_type=ExecutorType.API,
        model=model,
        api_key_env=api_key_env,
        **kw,
    )


def _mock_litellm(response_text: str = "ok"):
    """Create a mock litellm module with working acompletion."""
    mock = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = response_text
    mock.acompletion = AsyncMock(return_value=mock_response)
    mock.AuthenticationError = type("AuthenticationError", (Exception,), {})
    mock.RateLimitError = type("RateLimitError", (Exception,), {})
    mock.Timeout = type("Timeout", (Exception,), {})
    mock.APIError = type("APIError", (Exception,), {})
    return mock


class TestApiKeyResolution:
    def test_project_env_takes_priority(self):
        mock_lit = _mock_litellm()
        with patch.dict("sys.modules", {"litellm": mock_lit}):
            with patch.dict("os.environ", {"TEST_API_KEY": "env_key"}):
                from mcp_server.executor.api_runner import run_api_executor

                config = _api_config()
                result = asyncio.get_event_loop().run_until_complete(
                    run_api_executor(
                        config, "test prompt", project_env={"TEST_API_KEY": "project_key"}
                    )
                )
                call_kwargs = mock_lit.acompletion.call_args[1]
                assert call_kwargs["api_key"] == "project_key"
                assert result.exit_code == 0

    def test_falls_back_to_os_environ(self):
        mock_lit = _mock_litellm()
        with patch.dict("sys.modules", {"litellm": mock_lit}):
            with patch.dict("os.environ", {"TEST_API_KEY": "env_key"}):
                from mcp_server.executor.api_runner import run_api_executor

                config = _api_config()
                asyncio.get_event_loop().run_until_complete(run_api_executor(config, "test prompt"))
                call_kwargs = mock_lit.acompletion.call_args[1]
                assert call_kwargs["api_key"] == "env_key"


class TestApiExecutorSuccess:
    def test_returns_response_content(self):
        mock_lit = _mock_litellm("Generated content here")
        with patch.dict("sys.modules", {"litellm": mock_lit}):
            from mcp_server.executor.api_runner import run_api_executor

            config = _api_config()
            result = asyncio.get_event_loop().run_until_complete(
                run_api_executor(config, "test prompt", project_env={"TEST_API_KEY": "key"})
            )
        assert result.exit_code == 0
        assert result.stdout == "Generated content here"
        assert result.executor_name == "api/test"

    def test_system_prompt_included(self):
        mock_lit = _mock_litellm()
        with patch.dict("sys.modules", {"litellm": mock_lit}):
            from mcp_server.executor.api_runner import run_api_executor

            config = _api_config()
            asyncio.get_event_loop().run_until_complete(
                run_api_executor(
                    config,
                    "user msg",
                    system_prompt="system msg",
                    project_env={"TEST_API_KEY": "key"},
                )
            )
            messages = mock_lit.acompletion.call_args[1]["messages"]
            assert messages[0] == {"role": "system", "content": "system msg"}
            assert messages[1] == {"role": "user", "content": "user msg"}

    def test_api_base_passed_when_set(self):
        mock_lit = _mock_litellm()
        with patch.dict("sys.modules", {"litellm": mock_lit}):
            from mcp_server.executor.api_runner import run_api_executor

            config = _api_config(api_base="https://custom.api.com")
            asyncio.get_event_loop().run_until_complete(
                run_api_executor(config, "test", project_env={"TEST_API_KEY": "k"})
            )
            assert mock_lit.acompletion.call_args[1]["api_base"] == "https://custom.api.com"


class TestApiExecutorErrors:
    def test_missing_litellm_returns_exit_neg7(self):
        from mcp_server.executor.api_runner import run_api_executor

        config = _api_config()
        # Remove litellm from sys.modules to simulate ImportError
        saved = sys.modules.pop("litellm", None)
        try:
            with patch.dict("sys.modules", {"litellm": None}):
                result = asyncio.get_event_loop().run_until_complete(
                    run_api_executor(config, "test")
                )
            assert result.exit_code == -7
            assert "litellm" in result.stderr
        finally:
            if saved is not None:
                sys.modules["litellm"] = saved

    def test_timeout_returns_exit_neg1(self):
        mock_lit = _mock_litellm()
        timeout_exc = mock_lit.Timeout
        mock_lit.acompletion = AsyncMock(side_effect=timeout_exc())
        with patch.dict("sys.modules", {"litellm": mock_lit}):
            from mcp_server.executor.api_runner import run_api_executor

            config = _api_config()
            result = asyncio.get_event_loop().run_until_complete(
                run_api_executor(config, "test", project_env={"TEST_API_KEY": "k"})
            )
        assert result.exit_code == -1
        assert "timed out" in result.stderr

    def test_auth_error_returns_exit_neg4(self):
        mock_lit = _mock_litellm()
        auth_exc = mock_lit.AuthenticationError
        mock_lit.acompletion = AsyncMock(side_effect=auth_exc("bad key"))
        with patch.dict("sys.modules", {"litellm": mock_lit}):
            from mcp_server.executor.api_runner import run_api_executor

            config = _api_config()
            result = asyncio.get_event_loop().run_until_complete(
                run_api_executor(config, "test", project_env={"TEST_API_KEY": "k"})
            )
        assert result.exit_code == -4
        assert "TEST_API_KEY" in result.stderr

    def test_rate_limit_returns_exit_neg5(self):
        mock_lit = _mock_litellm()
        rate_exc = mock_lit.RateLimitError
        mock_lit.acompletion = AsyncMock(side_effect=rate_exc("throttled"))
        with patch.dict("sys.modules", {"litellm": mock_lit}):
            from mcp_server.executor.api_runner import run_api_executor

            config = _api_config()
            result = asyncio.get_event_loop().run_until_complete(
                run_api_executor(config, "test", project_env={"TEST_API_KEY": "k"})
            )
        assert result.exit_code == -5
        assert "Rate limit" in result.stderr


class TestEnvInjection:
    def test_config_env_injected_and_restored(self):
        from mcp_server.executor.api_runner import _inject_env

        original = os.environ.get("TEST_INJECT_VAR")
        with _inject_env({"TEST_INJECT_VAR": "injected"}, None):
            assert os.environ["TEST_INJECT_VAR"] == "injected"
        assert os.environ.get("TEST_INJECT_VAR") == original

    def test_project_env_wins_over_config_env(self):
        from mcp_server.executor.api_runner import _inject_env

        with _inject_env(
            {"TEST_INJECT_VAR": "from_config"},
            {"TEST_INJECT_VAR": "from_project"},
        ):
            assert os.environ["TEST_INJECT_VAR"] == "from_project"

    def test_blocked_vars_excluded(self):
        from mcp_server.executor.api_runner import _inject_env

        original_path = os.environ.get("PATH")
        with _inject_env({"PATH": "/evil"}, None):
            assert os.environ.get("PATH") == original_path

    def test_absent_vars_cleaned_up(self):
        from mcp_server.executor.api_runner import _inject_env

        os.environ.pop("TEST_TEMP_INJECT_99", None)
        with _inject_env({"TEST_TEMP_INJECT_99": "temp"}, None):
            assert os.environ["TEST_TEMP_INJECT_99"] == "temp"
        assert "TEST_TEMP_INJECT_99" not in os.environ

    def test_preexisting_vars_restored(self):
        from mcp_server.executor.api_runner import _inject_env

        os.environ["TEST_PREEXIST_VAR"] = "original"
        try:
            with _inject_env({"TEST_PREEXIST_VAR": "temporary"}, None):
                assert os.environ["TEST_PREEXIST_VAR"] == "temporary"
            assert os.environ["TEST_PREEXIST_VAR"] == "original"
        finally:
            os.environ.pop("TEST_PREEXIST_VAR", None)

    def test_empty_sources_is_noop(self):
        from mcp_server.executor.api_runner import _inject_env

        snap = dict(os.environ)
        with _inject_env(None, None):
            pass
        # Only check relevant keys — other env changes from test framework are ok
        assert os.environ.get("PATH") == snap.get("PATH")

    def test_env_restored_after_exception(self):
        from mcp_server.executor.api_runner import _inject_env

        os.environ["TEST_EXCEPTION_VAR"] = "original"
        os.environ.pop("TEST_TEMP_EXCEPTION_VAR", None)
        try:
            with pytest.raises(RuntimeError):
                with _inject_env(
                    {"TEST_EXCEPTION_VAR": "modified", "TEST_TEMP_EXCEPTION_VAR": "temp"},
                    None,
                ):
                    assert os.environ["TEST_EXCEPTION_VAR"] == "modified"
                    assert os.environ["TEST_TEMP_EXCEPTION_VAR"] == "temp"
                    raise RuntimeError("simulated failure")
            assert os.environ["TEST_EXCEPTION_VAR"] == "original"
            assert "TEST_TEMP_EXCEPTION_VAR" not in os.environ
        finally:
            os.environ.pop("TEST_EXCEPTION_VAR", None)
            os.environ.pop("TEST_TEMP_EXCEPTION_VAR", None)


class TestResolveOverrides:
    def test_model_override(self):
        from mcp_server.executor.api_runner import _resolve_overrides

        config = _api_config(model="default-model")
        model, _, _, _ = _resolve_overrides(config, {"UCX_EXECUTOR_MODEL": "override-model"})
        assert model == "override-model"

    def test_api_base_override(self):
        from mcp_server.executor.api_runner import _resolve_overrides

        config = _api_config(api_base="https://default.api.com")
        _, api_base, _, _ = _resolve_overrides(
            config, {"UCX_EXECUTOR_API_BASE": "https://override.api.com"}
        )
        assert api_base == "https://override.api.com"

    def test_timeout_override_valid(self):
        from mcp_server.executor.api_runner import _resolve_overrides

        config = _api_config(timeout=300)
        _, _, timeout, _ = _resolve_overrides(config, {"UCX_EXECUTOR_TIMEOUT": "600"})
        assert timeout == 600

    def test_timeout_override_invalid_falls_back(self):
        from mcp_server.executor.api_runner import _resolve_overrides

        config = _api_config(timeout=300)
        _, _, timeout, _ = _resolve_overrides(config, {"UCX_EXECUTOR_TIMEOUT": "not_a_number"})
        assert timeout == 300

    def test_api_key_env_redirect(self):
        from mcp_server.executor.api_runner import _resolve_overrides

        config = _api_config(api_key_env="OPENAI_API_KEY")
        _, _, _, api_key_env = _resolve_overrides(
            config, {"UCX_EXECUTOR_API_KEY_ENV": "MY_CUSTOM_KEY"}
        )
        assert api_key_env == "MY_CUSTOM_KEY"

    def test_api_key_env_blocked_falls_back(self):
        from mcp_server.executor.api_runner import _resolve_overrides

        config = _api_config(api_key_env="OPENAI_API_KEY")
        _, _, _, api_key_env = _resolve_overrides(config, {"UCX_EXECUTOR_API_KEY_ENV": "PATH"})
        assert api_key_env == "OPENAI_API_KEY"

    def test_empty_overrides_use_config(self):
        from mcp_server.executor.api_runner import _resolve_overrides

        config = _api_config(
            model="my-model", api_base="https://api.com", timeout=300, api_key_env="MY_KEY"
        )
        model, api_base, timeout, api_key_env = _resolve_overrides(config, {})
        assert model == "my-model"
        assert api_base == "https://api.com"
        assert timeout == 300
        assert api_key_env == "MY_KEY"


class TestProjectExecutorConfig:
    def test_missing_file_returns_empty(self, tmp_path):
        from mcp_server.executor.registry import load_project_executor_config

        result = load_project_executor_config(tmp_path)
        assert result == {}

    def test_valid_file_returns_configs(self, tmp_path):
        import json

        from mcp_server.executor.registry import load_project_executor_config

        ucx_dir = tmp_path / "UCX"
        ucx_dir.mkdir()
        (ucx_dir / "executors.json").write_text(
            json.dumps(
                {
                    "executors": [
                        {"name": "proj-api", "executor_type": "api", "model": "gpt-4o-mini"}
                    ]
                }
            )
        )
        result = load_project_executor_config(tmp_path)
        assert "proj-api" in result
        assert result["proj-api"].model == "gpt-4o-mini"

    def test_malformed_json_returns_empty(self, tmp_path):
        from mcp_server.executor.registry import load_project_executor_config

        ucx_dir = tmp_path / "UCX"
        ucx_dir.mkdir()
        (ucx_dir / "executors.json").write_text("not json")
        result = load_project_executor_config(tmp_path)
        assert result == {}

    def test_project_override_takes_precedence(self):
        from mcp_server.executor.registry import ExecutorConfig, ExecutorType, get_executor

        override = {
            "api/gpt-4o": ExecutorConfig(
                name="api/gpt-4o",
                executor_type=ExecutorType.API,
                model="openai/custom-model",
                timeout=999,
            )
        }
        config = get_executor("api/gpt-4o", project_overrides=override)
        assert config.model == "openai/custom-model"
        assert config.timeout == 999

    def test_global_registry_unchanged_after_project_load(self, tmp_path):
        import json

        from mcp_server.executor.registry import _registry, load_project_executor_config

        ucx_dir = tmp_path / "UCX"
        ucx_dir.mkdir()
        (ucx_dir / "executors.json").write_text(
            json.dumps(
                {
                    "executors": [
                        {"name": "proj-only", "executor_type": "api", "model": "openai/gpt-4o-mini"}
                    ]
                }
            )
        )
        load_project_executor_config(tmp_path)
        assert "proj-only" not in _registry

    def test_array_format_accepted(self, tmp_path):
        import json

        from mcp_server.executor.registry import load_project_executor_config

        ucx_dir = tmp_path / "UCX"
        ucx_dir.mkdir()
        (ucx_dir / "executors.json").write_text(
            json.dumps([{"name": "arr-exec", "executor_type": "api", "model": "m"}])
        )
        result = load_project_executor_config(tmp_path)
        assert "arr-exec" in result

    def test_two_projects_independent(self, tmp_path):
        import json

        from mcp_server.executor.registry import load_project_executor_config

        for name in ("proj_a", "proj_b"):
            d = tmp_path / name / "UCX"
            d.mkdir(parents=True)
            (d / "executors.json").write_text(
                json.dumps(
                    {
                        "executors": [
                            {
                                "name": f"exec-{name}",
                                "executor_type": "api",
                                "model": f"openai/{name}",
                            }
                        ]
                    }
                )
            )
        a = load_project_executor_config(tmp_path / "proj_a")
        b = load_project_executor_config(tmp_path / "proj_b")
        assert "exec-proj_a" in a and "exec-proj_b" not in a
        assert "exec-proj_b" in b and "exec-proj_a" not in b

    def test_project_config_skips_legacy_cli_executor(self, tmp_path):
        import json

        from mcp_server.executor.registry import load_project_executor_config

        ucx_dir = tmp_path / "UCX"
        ucx_dir.mkdir()
        (ucx_dir / "executors.json").write_text(
            json.dumps(
                {
                    "executors": [
                        {"name": "legacy-cli", "executor_type": "cli", "command": "claude"},
                        {"name": "api-ok", "executor_type": "api", "model": "openai/gpt-4o-mini"},
                    ]
                }
            )
        )
        result = load_project_executor_config(tmp_path)
        assert "legacy-cli" not in result
        assert "api-ok" in result
