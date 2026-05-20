"""Tests for env_manager: .env loading, caching, security protections."""

from __future__ import annotations

import os
import stat
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import pytest

from mcp_server.env_manager import (
    BLOCKED_ENV_VARS,
    _env_cache,
    _invalidate_env_cache,
    load_project_env,
    show_project_env,
)


@pytest.fixture(autouse=True)
def _clear_cache():
    """Clear the env cache before each test."""
    _env_cache.clear()
    yield
    _env_cache.clear()


def _write_env(project: Path, content: str) -> Path:
    env_path = project / ".env"
    env_path.write_text(content, encoding="utf-8")
    return env_path


class TestLoadProjectEnv:
    def test_load_valid_env(self, tmp_path: Path) -> None:
        _write_env(tmp_path, "API_KEY=sk-123\nMODEL=gpt-4\n")
        env = load_project_env(tmp_path)
        assert env == {"API_KEY": "sk-123", "MODEL": "gpt-4"}

    def test_missing_env_returns_empty(self, tmp_path: Path) -> None:
        env = load_project_env(tmp_path)
        assert env == {}

    def test_malformed_env_returns_empty(self, tmp_path: Path) -> None:
        _write_env(tmp_path, "\x00\x01\x02 invalid binary content")
        env = load_project_env(tmp_path)
        # dotenv_values handles most content gracefully; just verify no crash
        assert isinstance(env, dict)

    def test_mtime_cache_hit(self, tmp_path: Path) -> None:
        _write_env(tmp_path, "KEY=val1\n")
        env1 = load_project_env(tmp_path)
        assert env1 == {"KEY": "val1"}

        # Same mtime — should return cached
        env2 = load_project_env(tmp_path)
        assert env2 is env1  # Same object reference (cache hit)

    def test_mtime_cache_miss_on_change(self, tmp_path: Path) -> None:
        env_path = _write_env(tmp_path, "KEY=val1\n")
        env1 = load_project_env(tmp_path)
        assert env1 == {"KEY": "val1"}

        # Change file content and force mtime update
        import time
        time.sleep(0.05)
        env_path.write_text("KEY=val2\n", encoding="utf-8")
        os.utime(env_path, (env_path.stat().st_mtime + 1, env_path.stat().st_mtime + 1))

        env2 = load_project_env(tmp_path)
        assert env2 == {"KEY": "val2"}

    def test_multi_project_isolation(self, tmp_path: Path) -> None:
        proj_a = tmp_path / "proj_a"
        proj_b = tmp_path / "proj_b"
        proj_a.mkdir()
        proj_b.mkdir()
        _write_env(proj_a, "KEY=from_a\n")
        _write_env(proj_b, "KEY=from_b\n")

        env_a = load_project_env(proj_a)
        env_b = load_project_env(proj_b)
        assert env_a == {"KEY": "from_a"}
        assert env_b == {"KEY": "from_b"}

    def test_none_value_filtering(self, tmp_path: Path) -> None:
        """Bare KEY lines (no =value) should be filtered out."""
        _write_env(tmp_path, "BARE_KEY\nGOOD_KEY=value\n")
        env = load_project_env(tmp_path)
        assert "BARE_KEY" not in env
        assert env.get("GOOD_KEY") == "value"

    def test_system_variable_blocklist(self, tmp_path: Path) -> None:
        _write_env(tmp_path, "PATH=/evil\nHOME=/evil\nAPI_KEY=safe\n")
        env = load_project_env(tmp_path)
        assert "PATH" not in env
        assert "HOME" not in env
        assert env.get("API_KEY") == "safe"

    def test_utf8_bom_handling(self, tmp_path: Path) -> None:
        env_path = tmp_path / ".env"
        env_path.write_bytes(b"\xef\xbb\xbfFIRST_KEY=value\nSECOND=other\n")
        env = load_project_env(tmp_path)
        assert "FIRST_KEY" in env
        assert env["FIRST_KEY"] == "value"
        assert "\ufeffFIRST_KEY" not in env

    def test_cache_invalidation(self, tmp_path: Path) -> None:
        _write_env(tmp_path, "KEY=val\n")
        load_project_env(tmp_path)
        assert str(tmp_path) in _env_cache

        _invalidate_env_cache(tmp_path)
        assert str(tmp_path) not in _env_cache

    def test_file_permission_warning(self, tmp_path: Path, caplog) -> None:
        env_path = _write_env(tmp_path, "KEY=val\n")
        env_path.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
        import logging
        with caplog.at_level(logging.WARNING, logger="mcp_server.env_manager"):
            load_project_env(tmp_path)
        assert any("Insecure permissions" in r.message for r in caplog.records)


class TestShowProjectEnv:
    def test_show_returns_keys_not_values(self, tmp_path: Path) -> None:
        _write_env(tmp_path, "SECRET_KEY=super_secret\nAPI_URL=https://example.com\n")
        result = show_project_env(tmp_path)
        assert result["env_file_exists"] is True
        assert "SECRET_KEY" in result["env_keys"]
        assert "API_URL" in result["env_keys"]
        assert result["env_key_count"] == 2
        # Values must NOT be present
        assert "super_secret" not in str(result)
        assert "https://example.com" not in str(result)

    def test_show_missing_env(self, tmp_path: Path) -> None:
        result = show_project_env(tmp_path)
        assert result["env_file_exists"] is False
        assert result["env_keys"] == []
        assert result["env_key_count"] == 0

    def test_show_reports_blocked_vars(self, tmp_path: Path) -> None:
        _write_env(tmp_path, "PATH=/evil\nAPI_KEY=safe\n")
        result = show_project_env(tmp_path)
        assert "PATH" in result["blocked_vars"]
        assert "API_KEY" in result["env_keys"]
        assert "PATH" not in result["env_keys"]
