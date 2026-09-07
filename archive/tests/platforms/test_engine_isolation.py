"""Conformance: neither platform's runtime-significant surface
references the other's engine (PC4). Scope: runtime files only
(``src/``, ``pyproject.toml``, ``.claude-plugin/``, ``commands/``,
``agents/``); READMEs, docs, and skill prose are documentary and
allowed to mention the other platform."""

import re
import unittest

from _spec import PLATFORMS_ROOT

# Forbidden tokens per platform — case-insensitive substring match.
HERMES_FORBIDDEN = (
    "claude-plugin",
    "claude_plugin",
    ".claude-plugin/",
    "skill_view",
    "aidoc-flow:",
)
PLUGIN_FORBIDDEN = (
    "mcp_server",
    "sdd_validate",
    "hermes-server",
    "mcp-ucx",
)

# Runtime-significant scopes per platform (relative to platform root).
HERMES_SCOPE = (
    "src",
    "pyproject.toml",
)
PLUGIN_SCOPE = (
    ".claude-plugin",
    "commands",
    "agents",
)


def _violations(platform_root, scopes, forbidden):
    """Yield (file, line_no, line) for any forbidden-token hit."""
    pattern = re.compile(
        "|".join(re.escape(tok) for tok in forbidden),
        re.IGNORECASE,
    )
    for scope in scopes:
        path = platform_root / scope
        if not path.exists():
            continue
        files = [path] if path.is_file() else [p for p in path.rglob("*") if p.is_file()]
        for file in files:
            try:
                lines = file.read_text(encoding="utf-8").splitlines()
            except (UnicodeDecodeError, PermissionError):
                continue
            for i, line in enumerate(lines, start=1):
                if pattern.search(line):
                    yield (file, i, line)


def _format_hits(hits):
    return "\n  ".join(f"{f}:{n}: {line.strip()}" for f, n, line in hits)


class PlatformEngineIsolationTests(unittest.TestCase):
    def test_hermes_does_not_reference_plugin_engine(self):
        hermes = PLATFORMS_ROOT / "hermes"
        if not hermes.exists():
            self.skipTest("hermes platform absent")
        hits = list(_violations(hermes, HERMES_SCOPE, HERMES_FORBIDDEN))
        self.assertEqual(
            hits,
            [],
            "Hermes runtime surface references plugin engine:\n  " + _format_hits(hits),
        )

    def test_plugin_does_not_reference_hermes_engine(self):
        plugin = PLATFORMS_ROOT / "claude-code-plugin"
        if not plugin.exists():
            self.skipTest("claude-code-plugin platform absent")
        hits = list(_violations(plugin, PLUGIN_SCOPE, PLUGIN_FORBIDDEN))
        self.assertEqual(
            hits,
            [],
            "Plugin runtime surface references Hermes engine:\n  " + _format_hits(hits),
        )
