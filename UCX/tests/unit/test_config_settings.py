"""Unit tests for ucx.config.settings."""

from __future__ import annotations

import os

import pytest

from ucx.config.settings import UCXSettings


class TestUCXSettingsDefaults:
    def test_default_ai_model(self) -> None:
        s = UCXSettings()
        assert "claude" in s.ai_model

    def test_default_ai_api_key_is_none(self) -> None:
        s = UCXSettings()
        assert s.ai_api_key is None

    def test_default_max_fix_iterations(self) -> None:
        s = UCXSettings()
        assert s.max_fix_iterations == 3

    def test_default_log_level_is_info(self) -> None:
        s = UCXSettings()
        assert s.log_level == "INFO"

    def test_default_log_format_is_json(self) -> None:
        s = UCXSettings()
        assert s.log_format == "json"

    def test_default_ai_max_tokens(self) -> None:
        s = UCXSettings()
        assert s.ai_max_tokens == 8192


class TestUCXSettingsOverride:
    def test_constructor_override(self) -> None:
        s = UCXSettings(ai_model="gpt-4o", log_level="DEBUG", max_fix_iterations=5)
        assert s.ai_model == "gpt-4o"
        assert s.log_level == "DEBUG"
        assert s.max_fix_iterations == 5

    def test_env_var_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("UCX_LOG_LEVEL", "WARNING")
        monkeypatch.setenv("UCX_AI_MAX_TOKENS", "4096")
        s = UCXSettings()
        assert s.log_level == "WARNING"
        assert s.ai_max_tokens == 4096

    def test_env_var_prefix_is_ucx(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # Without prefix, it should NOT be picked up
        monkeypatch.setenv("LOG_LEVEL", "WARNING")
        s = UCXSettings()
        # Still default
        assert s.log_level == "INFO"
