"""Regression tests — tool contract stability.

These tests lock the public MCP tool interface so that future implementation
work in PLAN-001 through PLAN-005 cannot inadvertently remove tools, rename
parameters, or change tool counts.

A regression test failure means:
  - A tool was removed or renamed (breaking agent callers)
  - A required parameter was dropped or renamed
  - The return type contract changed

Tests are parameterized against the full expected tool catalog so
any omission is caught immediately.
"""

from __future__ import annotations

import inspect

import pytest

from ucx.config.settings import UCXSettings
from ucx.mcp.server import create_server
from ucx.mcp.tools.brd import BRDTools
from ucx.mcp.tools.prd import PRDTools
from ucx.mcp.tools.ears import EARSTools
from ucx.mcp.tools.adr import ADRTools
from ucx.mcp.tools.sys import SYSTools
from ucx.mcp.tools.req import REQTools
from ucx.mcp.tools.ctr import CTRTools


# ---------------------------------------------------------------------------
# Expected tool catalog — update this when adding new tools intentionally
# ---------------------------------------------------------------------------

EXPECTED_TOOLS: dict[str, list[str]] = {
    "brd": ["brd_validate", "brd_review", "brd_remediate", "brd_status"],
    "prd": [
        "prd_validate",
        "prd_validate_fix",
        "prd_review",
        "prd_remediate",
        "prd_remediate_apply",
        "prd_artifacts",
        "prd_status",
    ],
    "ears": ["ears_validate", "ears_review", "ears_remediate", "ears_status"],
    "adr": ["adr_validate", "adr_review", "adr_remediate", "adr_status"],
    "sys": ["sys_validate", "sys_review", "sys_remediate", "sys_status"],
    "req": ["req_validate", "req_review", "req_remediate", "req_status"],
    "ctr": ["ctr_validate", "ctr_review", "ctr_remediate", "ctr_status"],
}

EXPECTED_TOTAL_TOOLS = sum(len(v) for v in EXPECTED_TOOLS.values())  # 31


# ---------------------------------------------------------------------------
# Required parameter contracts per tool
# ---------------------------------------------------------------------------

REQUIRED_PARAMS: dict[str, list[str]] = {
    # BRD
    "brd_validate": ["brd_path"],
    "brd_review": ["brd_path"],
    "brd_remediate": ["brd_path", "review_report_path"],
    "brd_status": ["brd_dir"],
    # PRD
    "prd_validate": ["prd_path"],
    "prd_validate_fix": ["prd_path"],
    "prd_review": ["validation_prd_path"],
    "prd_remediate": ["validation_prd_path", "review_report_path"],
    "prd_remediate_apply": ["validation_prd_path", "remediation_report_path"],
    "prd_artifacts": ["prd_dir"],
    "prd_status": ["prd_dir"],
    # EARS
    "ears_validate": ["ears_path"],
    "ears_review": ["ears_path"],
    "ears_remediate": ["ears_path", "review_report_path"],
    "ears_status": ["ears_dir"],
    # ADR
    "adr_validate": ["adr_path"],
    "adr_review": ["adr_path"],
    "adr_remediate": ["adr_path", "review_report_path"],
    "adr_status": ["adr_dir"],
    # SYS
    "sys_validate": ["sys_path"],
    "sys_review": ["sys_path"],
    "sys_remediate": ["sys_path", "review_report_path"],
    "sys_status": ["sys_dir"],
    # REQ
    "req_validate": ["req_path"],
    "req_review": ["req_path"],
    "req_remediate": ["req_path", "review_report_path"],
    "req_status": ["req_dir"],
    # CTR
    "ctr_validate": ["ctr_path"],
    "ctr_review": ["ctr_path"],
    "ctr_remediate": ["ctr_path", "review_report_path"],
    "ctr_status": ["ctr_dir"],
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _settings() -> UCXSettings:
    return UCXSettings()


def _all_expected_tools() -> list[str]:
    return [name for names in EXPECTED_TOOLS.values() for name in names]


# ---------------------------------------------------------------------------
# Registration regression
# ---------------------------------------------------------------------------


@pytest.mark.anyio
async def test_total_tool_count_has_not_decreased() -> None:
    """Registered tool count must not drop below the expected baseline."""
    server = create_server(_settings())
    registered = await server.list_tools()
    assert len(registered) >= EXPECTED_TOTAL_TOOLS, (
        f"Expected ≥{EXPECTED_TOTAL_TOOLS} tools, got {len(registered)}. "
        f"Missing: {set(_all_expected_tools()) - {t.name for t in registered}}"
    )


@pytest.mark.anyio
@pytest.mark.parametrize("tool_name", _all_expected_tools())
async def test_each_expected_tool_is_registered(tool_name: str) -> None:
    """Every tool in the expected catalog must be registered in the server."""
    server = create_server(_settings())
    registered_names = {t.name for t in await server.list_tools()}
    assert tool_name in registered_names, (
        f"Tool '{tool_name}' was removed from the registry"
    )


# ---------------------------------------------------------------------------
# Parameter contract regression
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("layer,tool_class", [
    ("brd", BRDTools),
    ("prd", PRDTools),
    ("ears", EARSTools),
    ("adr", ADRTools),
    ("sys", SYSTools),
    ("req", REQTools),
    ("ctr", CTRTools),
])
def test_tool_class_has_register_method(layer: str, tool_class: type) -> None:
    """Every tool class must have a register(mcp) method."""
    instance = tool_class(_settings())
    assert hasattr(instance, "register"), f"{tool_class.__name__} missing register()"
    assert callable(instance.register)


@pytest.mark.parametrize("tool_name,required_params", REQUIRED_PARAMS.items())
def test_tool_method_has_required_parameters(
    tool_name: str, required_params: list[str]
) -> None:
    """Tool method signatures must include all required parameters.

    This test inspects the method directly on the tool class rather than
    going through the MCP server, giving faster, synchronous feedback.
    """
    layer_prefix = tool_name.split("_")[0]
    tool_class_map = {
        "brd": BRDTools,
        "prd": PRDTools,
        "ears": EARSTools,
        "adr": ADRTools,
        "sys": SYSTools,
        "req": REQTools,
        "ctr": CTRTools,
    }
    tool_class = tool_class_map[layer_prefix]
    instance = tool_class(_settings())

    # Method name on the class matches the tool name
    method = getattr(instance, tool_name, None)
    assert method is not None, (
        f"{tool_class.__name__}.{tool_name}() method not found"
    )

    sig = inspect.signature(method)
    actual_params = set(sig.parameters.keys()) - {"self"}
    for param in required_params:
        assert param in actual_params, (
            f"{tool_name}() missing required parameter '{param}'. "
            f"Actual params: {actual_params}"
        )


# ---------------------------------------------------------------------------
# Naming convention regression
# ---------------------------------------------------------------------------


@pytest.mark.anyio
async def test_no_tool_uses_generic_ucx_prefix() -> None:
    """v2 must not register any tools with the old 'ucx_*' namespace."""
    server = create_server(_settings())
    for tool in await server.list_tools():
        assert not tool.name.startswith("ucx_"), (
            f"Found v1-style 'ucx_*' tool in v2 server: '{tool.name}'"
        )


@pytest.mark.anyio
async def test_all_tool_names_are_snake_case() -> None:
    """Tool names must be lowercase snake_case."""
    server = create_server(_settings())
    for tool in await server.list_tools():
        assert tool.name == tool.name.lower(), (
            f"Tool name '{tool.name}' contains uppercase letters"
        )
        assert " " not in tool.name, (
            f"Tool name '{tool.name}' contains spaces"
        )
