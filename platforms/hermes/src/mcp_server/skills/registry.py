from __future__ import annotations

from dataclasses import dataclass
from typing import cast

# The 8-layer SDD flow prefixes (BRD → IPLAN). The legacy SYS/REQ/CTR/TSPEC
# layers were removed (they are not part of the 8-layer framework); `tasks`
# remains as the IPLAN rename-alias.
LAYER_PREFIXES: tuple[str, ...] = (
    "brd",
    "prd",
    "ears",
    "bdd",
    "adr",
    "spec",
    "tdd",
    "iplan",
    "tasks",
)

CANONICAL_CROSS_LAYER_TOOLS: tuple[str, ...] = (
    "trace",
    "matrix",
    "code",
    "tests",
    "workflow",
    "report",
)

REVIEW_CROSS_LAYER_TOOLS: tuple[str, ...] = ("review",)


@dataclass(frozen=True)
class AliasResolution:
    requested_tool: str
    canonical_tool: str
    alias_invoked: str | None
    layer: str | None


def build_alias_registry(
    *,
    canonical_tools: tuple[str, ...] = CANONICAL_CROSS_LAYER_TOOLS,
    review_tools: tuple[str, ...] = REVIEW_CROSS_LAYER_TOOLS,
    layer_prefixes: tuple[str, ...] = LAYER_PREFIXES,
) -> dict[str, dict[str, object]]:
    registry: dict[str, dict[str, object]] = {}
    for canonical_tool in canonical_tools + review_tools:
        aliases = tuple(f"{layer}_{canonical_tool}" for layer in layer_prefixes)
        registry[canonical_tool] = {
            "canonical_tool": canonical_tool,
            "aliases": aliases,
            "review_tool": canonical_tool in review_tools,
        }
    return registry


def validate_alias_registry(
    registry: dict[str, dict[str, object]],
    *,
    layer_prefixes: tuple[str, ...] = LAYER_PREFIXES,
) -> dict[str, list[str]]:
    missing: dict[str, list[str]] = {}
    for canonical_tool, payload in registry.items():
        aliases = set(cast(tuple[str, ...], payload.get("aliases", ())))
        expected = [f"{layer}_{canonical_tool}" for layer in layer_prefixes]
        absent = [alias for alias in expected if alias not in aliases]
        if absent:
            missing[canonical_tool] = absent
    return missing


def resolve_tool_call(
    requested_tool: str,
    *,
    registry: dict[str, dict[str, object]] | None = None,
) -> AliasResolution:
    active_registry = registry or build_alias_registry()

    if requested_tool in active_registry:
        return AliasResolution(
            requested_tool=requested_tool,
            canonical_tool=requested_tool,
            alias_invoked=None,
            layer=None,
        )

    for canonical_tool, payload in active_registry.items():
        aliases = cast(tuple[str, ...], payload.get("aliases", ()))
        if requested_tool not in aliases:
            continue
        layer = requested_tool.split("_", 1)[0]
        return AliasResolution(
            requested_tool=requested_tool,
            canonical_tool=canonical_tool,
            alias_invoked=requested_tool,
            layer=layer,
        )

    raise KeyError(f"Unknown tool or alias: {requested_tool}")
