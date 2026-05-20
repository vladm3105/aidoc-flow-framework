"""Tests for handle_tool project injection and _PROJECT_TOOLS set."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from unittest.mock import patch, AsyncMock

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import pytest

from mcp_server.tool_registry import TOOLS, _PROJECT_TOOLS, handle_tool
import mcp_server.project_context as pc


@pytest.fixture(autouse=True)
def _clean_state():
    pc._session_project = None
    pc._config_default_project = None
    yield
    pc._session_project = None
    pc._config_default_project = None


class TestProjectToolsSet:
    def test_project_tools_contains_expected(self) -> None:
        expected_project_tools = {
            "sdd_init", "sdd_validate", "sdd_preflight",
            "sdd_personas_show", "sdd_personas_set", "sdd_personas_diff",
            "sdd_env_show", "sdd_set_project", "sdd_list_executors",
            "sdd_create_build", "sdd_create", "sdd_review",
            "sdd_remediate", "sdd_run_lifecycle", "sdd_clean",
        }
        assert expected_project_tools.issubset(_PROJECT_TOOLS)

    def test_non_project_tools_excluded(self) -> None:
        non_project = {"sdd_scan", "sdd_consistency",
                       "sdd_validate_links", "sdd_prescreen", "sdd_next_action",
                       "sdd_get_project"}
        assert non_project.isdisjoint(_PROJECT_TOOLS)


class TestHandleToolInjection:
    def test_injects_project_for_project_tool_when_omitted(self, tmp_path: Path) -> None:
        pc._session_project = tmp_path
        arguments = {"context": "any"}

        # Patch _dispatch to capture what arguments it receives
        with patch("mcp_server.tool_registry._dispatch", new_callable=AsyncMock) as mock_dispatch:
            mock_dispatch.return_value = {"status": "ready"}
            asyncio.get_event_loop().run_until_complete(
                handle_tool("sdd_preflight", arguments)
            )
            # After injection, arguments should have "project"
            assert arguments.get("project") == str(tmp_path)

    def test_does_not_inject_for_non_project_tool(self) -> None:
        pc._session_project = Path("/some/path")
        arguments = {"report_file": "/some/report.json"}

        with patch("mcp_server.tool_registry._dispatch", new_callable=AsyncMock) as mock_dispatch:
            mock_dispatch.return_value = {"count": 0}
            asyncio.get_event_loop().run_until_complete(
                handle_tool("sdd_scan", arguments)
            )
            assert "project" not in arguments

    def test_does_not_override_explicit_project(self, tmp_path: Path) -> None:
        explicit = tmp_path / "explicit"
        explicit.mkdir()
        session = tmp_path / "session"
        session.mkdir()
        pc._session_project = session
        arguments = {"project": str(explicit), "context": "any"}

        with patch("mcp_server.tool_registry._dispatch", new_callable=AsyncMock) as mock_dispatch:
            mock_dispatch.return_value = {"status": "ready"}
            asyncio.get_event_loop().run_until_complete(
                handle_tool("sdd_preflight", arguments)
            )
            # Should keep explicit, not replace with session
            assert arguments["project"] == str(explicit)
