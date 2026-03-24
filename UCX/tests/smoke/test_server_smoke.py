"""Smoke tests — verify the UCX v2 MCP server starts and is queryable.

Smoke tests check end-to-end plumbing without testing business logic.
They run fast and require no external services.

A smoke test failure indicates a startup-level regression:
broken imports, bad server config, missing tool registration.
"""

from __future__ import annotations

import pytest
from fastmcp import FastMCP

from ucx.config.settings import UCXSettings
from ucx.mcp.server import create_server
from ucx.version import __version__


# ---------------------------------------------------------------------------
# Server lifecycle
# ---------------------------------------------------------------------------


def test_server_version_is_2() -> None:
    """Package must report v2.x."""
    major = int(__version__.split(".")[0])
    assert major == 2, f"Expected v2.x, got {__version__}"


def test_server_creates_with_default_settings() -> None:
    """Server must start without any environment variables set."""
    server = create_server()
    assert isinstance(server, FastMCP)


def test_server_creates_with_explicit_settings() -> None:
    """Server must accept explicit UCXSettings."""
    settings = UCXSettings(log_level="DEBUG")
    server = create_server(settings)
    assert isinstance(server, FastMCP)


def test_two_server_instances_are_independent() -> None:
    """Each create_server() call returns a distinct object."""
    s1 = create_server()
    s2 = create_server()
    assert s1 is not s2


# ---------------------------------------------------------------------------
# Tool availability
# ---------------------------------------------------------------------------


@pytest.mark.anyio
async def test_server_lists_tools() -> None:
    """Server must return a non-empty tool list."""
    server = create_server()
    tools = await server.list_tools()
    assert len(tools) > 0


@pytest.mark.anyio
async def test_tool_count_is_at_least_31() -> None:
    """All 31 stub tools must be registered."""
    server = create_server()
    tools = await server.list_tools()
    assert len(tools) >= 31, f"Expected ≥31 tools, got {len(tools)}: {[t.name for t in tools]}"


@pytest.mark.anyio
async def test_all_seven_layer_prefixes_present() -> None:
    """Every SDD layer namespace must appear at least once."""
    server = create_server()
    tool_names = {t.name for t in await server.list_tools()}
    for prefix in ["brd", "prd", "ears", "adr", "sys", "req", "ctr"]:
        matching = [n for n in tool_names if n.startswith(f"{prefix}_")]
        assert len(matching) >= 1, f"No tools found for layer prefix '{prefix}_'"


@pytest.mark.anyio
async def test_tool_names_follow_convention() -> None:
    """All registered tools must follow the {layer}_{action} naming pattern."""
    server = create_server()
    valid_prefixes = {"brd", "prd", "ears", "adr", "sys", "req", "ctr"}
    for tool in await server.list_tools():
        parts = tool.name.split("_", 1)
        assert len(parts) == 2, f"Tool name '{tool.name}' does not contain '_'"
        assert parts[0] in valid_prefixes, (
            f"Tool '{tool.name}' has unknown layer prefix '{parts[0]}'"
        )


@pytest.mark.anyio
async def test_all_tools_have_descriptions() -> None:
    """Every registered tool must expose a non-empty description."""
    server = create_server()
    for tool in await server.list_tools():
        assert tool.description, f"Tool '{tool.name}' has no description"
        assert len(tool.description.strip()) > 10, (
            f"Tool '{tool.name}' description is too short: '{tool.description}'"
        )


# ---------------------------------------------------------------------------
# Import surface
# ---------------------------------------------------------------------------


def test_ucx_package_importable() -> None:
    import ucx
    assert ucx.__version__ == __version__


def test_exceptions_importable() -> None:
    from ucx.exceptions import UCXError, UCXValidationError, UCXDocumentNotFound  # noqa: F401


def test_validators_importable() -> None:
    from ucx.validators.result import ValidationResult, Finding, Severity  # noqa: F401
    from ucx.validators.base import Validator  # noqa: F401


def test_agents_importable() -> None:
    from ucx.agents.stages import Stage, can_transition  # noqa: F401
    from ucx.agents.workflow import WorkflowEngine  # noqa: F401


def test_models_importable() -> None:
    from ucx.models.document import DocumentLayer, LAYER_REGISTRY  # noqa: F401


def test_config_importable() -> None:
    from ucx.config.settings import UCXSettings  # noqa: F401
