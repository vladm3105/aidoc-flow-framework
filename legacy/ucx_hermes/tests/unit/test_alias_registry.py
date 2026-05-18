from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp_server.skills import (  # noqa: E402
    CANONICAL_CROSS_LAYER_TOOLS,
    LAYER_PREFIXES,
    REVIEW_CROSS_LAYER_TOOLS,
    build_alias_registry,
    resolve_tool_call,
    validate_alias_registry,
)


def test_cross_layer_tools_expose_aliases_for_all_configured_layers() -> None:
    registry = build_alias_registry()
    for canonical_tool in CANONICAL_CROSS_LAYER_TOOLS:
        aliases = registry[canonical_tool]["aliases"]
        assert len(aliases) == len(LAYER_PREFIXES)

    assert validate_alias_registry(registry) == {}


def test_alias_call_preserves_canonical_tool_identity_and_alias_invoked_metadata() -> None:
    resolution = resolve_tool_call("brd_trace")
    assert resolution.canonical_tool == "trace"
    assert resolution.alias_invoked == "brd_trace"
    assert resolution.layer == "brd"


def test_canonical_tool_resolution_keeps_alias_invoked_empty() -> None:
    resolution = resolve_tool_call("workflow")
    assert resolution.canonical_tool == "workflow"
    assert resolution.alias_invoked is None
    assert resolution.layer is None


def test_review_tools_expose_per_layer_aliases() -> None:
    registry = build_alias_registry()
    for canonical_tool in REVIEW_CROSS_LAYER_TOOLS:
        aliases = registry[canonical_tool]["aliases"]
        assert len(aliases) == len(LAYER_PREFIXES)
        assert "spec_review" in aliases
        assert "tdd_review" in aliases
        assert "iplan_review" in aliases
        assert "tasks_review" in aliases
