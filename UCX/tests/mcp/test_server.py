"""Tests for UCX v2 MCP server registration."""

from __future__ import annotations

import pytest
from fastmcp import FastMCP

from ucx.config.settings import UCXSettings
from ucx.mcp.server import create_server


def test_server_creates_without_error() -> None:
    """Server creation should succeed with default settings."""
    settings = UCXSettings()
    server = create_server(settings)
    assert isinstance(server, FastMCP)


@pytest.mark.anyio
async def test_server_registers_brd_tools() -> None:
    """All brd_* tools must be registered."""
    server = create_server(UCXSettings())
    tool_names = {t.name for t in await server.list_tools()}
    assert "brd_validate" in tool_names
    assert "brd_review" in tool_names
    assert "brd_remediate" in tool_names
    assert "brd_status" in tool_names


@pytest.mark.anyio
async def test_server_registers_prd_tools() -> None:
    """All prd_* tools must be registered."""
    server = create_server(UCXSettings())
    tool_names = {t.name for t in await server.list_tools()}
    assert "prd_validate" in tool_names
    assert "prd_validate_fix" in tool_names
    assert "prd_review" in tool_names
    assert "prd_remediate" in tool_names
    assert "prd_remediate_apply" in tool_names
    assert "prd_artifacts" in tool_names
    assert "prd_status" in tool_names


@pytest.mark.anyio
async def test_server_registers_all_layer_namespaces() -> None:
    """All 7 layer namespaces must have at least a validate tool registered."""
    server = create_server(UCXSettings())
    tool_names = {t.name for t in await server.list_tools()}
    expected_validate_tools = {
        "brd_validate",
        "prd_validate",
        "ears_validate",
        "adr_validate",
        "sys_validate",
        "req_validate",
        "ctr_validate",
    }
    assert expected_validate_tools.issubset(tool_names), (
        f"Missing tools: {expected_validate_tools - tool_names}"
    )
