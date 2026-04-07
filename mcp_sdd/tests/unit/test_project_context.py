"""Tests for project_context: session state, config default, resolve chain."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import pytest

from mcp_server.project_context import (
    ProjectContext,
    clear_session_project,
    get_session_project,
    resolve_project,
    set_config_default,
    set_session_project,
)
import mcp_server.project_context as pc


@pytest.fixture(autouse=True)
def _clean_state():
    """Reset all project context state between tests."""
    pc._session_project = None
    pc._config_default_project = None
    yield
    pc._session_project = None
    pc._config_default_project = None


class TestResolveProject:
    def test_explicit_arg_returns_it(self, tmp_path: Path) -> None:
        result = resolve_project(str(tmp_path))
        assert result == tmp_path

    def test_session_override_returns_it(self, tmp_path: Path) -> None:
        set_session_project(tmp_path)
        result = resolve_project(None)
        assert result == tmp_path

    def test_env_var_returns_it(self, tmp_path: Path) -> None:
        with patch.dict(os.environ, {"SDD_DEFAULT_PROJECT": str(tmp_path)}):
            result = resolve_project(None)
        assert result == tmp_path

    def test_config_default_returns_it(self, tmp_path: Path) -> None:
        set_config_default(tmp_path)
        result = resolve_project(None)
        assert result == tmp_path

    def test_nothing_raises_value_error(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            # Ensure SDD_DEFAULT_PROJECT is not set
            os.environ.pop("SDD_DEFAULT_PROJECT", None)
            with pytest.raises(ValueError, match="No project specified"):
                resolve_project(None)

    def test_precedence_explicit_over_session(self, tmp_path: Path) -> None:
        proj_a = tmp_path / "a"
        proj_b = tmp_path / "b"
        proj_a.mkdir()
        proj_b.mkdir()
        set_session_project(proj_a)
        result = resolve_project(str(proj_b))
        assert result == proj_b

    def test_precedence_session_over_env_var(self, tmp_path: Path) -> None:
        proj_a = tmp_path / "a"
        proj_b = tmp_path / "b"
        proj_a.mkdir()
        proj_b.mkdir()
        set_session_project(proj_a)
        with patch.dict(os.environ, {"SDD_DEFAULT_PROJECT": str(proj_b)}):
            result = resolve_project(None)
        assert result == proj_a

    def test_precedence_env_var_over_config(self, tmp_path: Path) -> None:
        proj_a = tmp_path / "a"
        proj_b = tmp_path / "b"
        proj_a.mkdir()
        proj_b.mkdir()
        set_config_default(proj_a)
        with patch.dict(os.environ, {"SDD_DEFAULT_PROJECT": str(proj_b)}):
            result = resolve_project(None)
        assert result == proj_b

    def test_stale_session_directory_warns(self, tmp_path: Path, caplog) -> None:
        proj = tmp_path / "stale"
        proj.mkdir()
        set_session_project(proj)
        proj.rmdir()
        import logging
        with caplog.at_level(logging.WARNING, logger="mcp_server.project_context"):
            result = resolve_project(None)
        assert result == proj
        assert any("no longer exists" in r.message for r in caplog.records)


class TestSetSessionProject:
    def test_validates_directory(self, tmp_path: Path) -> None:
        result = set_session_project(tmp_path)
        assert result["session_project"] == str(tmp_path)
        assert get_session_project() == tmp_path

    def test_rejects_file_path(self, tmp_path: Path) -> None:
        f = tmp_path / "file.txt"
        f.write_text("x")
        with pytest.raises(ValueError, match="not a directory"):
            set_session_project(f)

    def test_does_not_require_ucx_subdir(self, tmp_path: Path) -> None:
        """Project may not have UCX/ yet (sdd_init creates it later)."""
        empty_dir = tmp_path / "fresh_project"
        empty_dir.mkdir()
        set_session_project(empty_dir)
        assert get_session_project() == empty_dir

    def test_rejects_nonexistent_path(self, tmp_path: Path) -> None:
        missing = tmp_path / "nope"
        with pytest.raises(ValueError, match="not a directory"):
            set_session_project(missing)


class TestProjectContext:
    def test_resolve_none_returns_none(self) -> None:
        assert ProjectContext.resolve(None) is None

    def test_resolve_empty_string_returns_none(self) -> None:
        assert ProjectContext.resolve("") is None

    def test_resolve_returns_context(self, tmp_path: Path) -> None:
        ctx = ProjectContext.resolve(str(tmp_path))
        assert ctx is not None
        assert ctx.project_root == tmp_path
        assert isinstance(ctx.project_env, dict)
        assert isinstance(ctx.executor_overrides, dict)

    def test_context_is_frozen(self, tmp_path: Path) -> None:
        ctx = ProjectContext.resolve(str(tmp_path))
        with pytest.raises(AttributeError):
            ctx.project_root = tmp_path / "other"  # type: ignore[misc]

    def test_missing_env_returns_empty_dict(self, tmp_path: Path) -> None:
        ctx = ProjectContext.resolve(str(tmp_path))
        assert ctx.project_env == {}

    def test_missing_executors_json_returns_empty_dict(self, tmp_path: Path) -> None:
        ctx = ProjectContext.resolve(str(tmp_path))
        assert ctx.executor_overrides == {}

    def test_loads_project_env(self, tmp_path: Path) -> None:
        env_file = tmp_path / ".env"
        env_file.write_text("MY_VAR=hello\n")
        ctx = ProjectContext.resolve(str(tmp_path))
        assert ctx.project_env.get("MY_VAR") == "hello"

    def test_loads_executor_overrides(self, tmp_path: Path) -> None:
        ucx_dir = tmp_path / "UCX"
        ucx_dir.mkdir()
        import json
        (ucx_dir / "executors.json").write_text(json.dumps({
            "executors": [
                {"name": "test-exec", "executor_type": "api", "model": "test-model"}
            ]
        }))
        ctx = ProjectContext.resolve(str(tmp_path))
        assert "test-exec" in ctx.executor_overrides


class TestClearSessionProject:
    def test_clear_reverts_to_config(self, tmp_path: Path) -> None:
        proj_a = tmp_path / "a"
        proj_b = tmp_path / "b"
        proj_a.mkdir()
        proj_b.mkdir()
        set_config_default(proj_b)
        set_session_project(proj_a)
        assert resolve_project(None) == proj_a
        clear_session_project()
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("SDD_DEFAULT_PROJECT", None)
            result = resolve_project(None)
        assert result == proj_b

    def test_get_session_returns_none_after_clear(self, tmp_path: Path) -> None:
        set_session_project(tmp_path)
        clear_session_project()
        assert get_session_project() is None
