"""Conformance: every plugin agent declares an explicit tool allowlist and model
(PLUGIN-PREPROD-001 `PREPROD-M2`).

An `agents/*.md` that omits `tools:` does not get a smaller tool set — it
**inherits every tool**, including `Write`, `Edit` and `Bash`. So the omission is
invisible in review (the file looks like any other agent) and silently grants the
broadest possible access. `requirements-analyst.md` shipped that way through
plugin `0.24.0`: it was the only one of eleven declaring neither key.

`test_plugin_manifest.py::test_agents_have_name_and_description` already covers
identity. This module covers the *scoping* half, which is a security property
rather than a metadata one, and which nothing else in the suite asserts.

The model check is not decoration: `docs/AGENTS.md` §"Model tiers" defines
exactly three tiers, and an agent naming anything else contradicts the shipped
documentation of its own roster.
"""

from __future__ import annotations

import re
import unittest

import yaml
from _spec import REPO_ROOT

PLUGIN = REPO_ROOT / "platforms" / "claude-code-plugin"
AGENTS = PLUGIN / "agents"

# The three tiers documented in platforms/claude-code-plugin/docs/AGENTS.md
# §"Model tiers". `inherit` is deliberately absent — it is the unscoped state
# this guard exists to reject.
DOCUMENTED_MODELS = frozenset({"opus", "sonnet", "haiku"})

# A single entry in the comma-separated `tools:` string, e.g. `Read` or
# `mcp__brave-search__brave_web_search` — MCP server names may contain hyphens.
# Deliberately strict: it admits a bare tool name only, not the
# `Tool(scope:*)` form, which is settings-level permission syntax and is not
# part of the agent `tools:` field.
TOOL_TOKEN = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")

# Agents whose `custom_fields.access` says read-only must not hold an editing
# tool. `Bash` is deliberately NOT in this set: `traceability-auditor` and the
# review lenses genuinely shell out to run the validation tooling. So this
# guards what the allowlist can enforce, which is narrower than the read-only
# claim itself — see docs/AGENTS.md §"Naming".
EDITING_TOOLS = frozenset({"Write", "Edit", "NotebookEdit"})


def _frontmatter(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    data = yaml.safe_load(text[3:end])
    return data if isinstance(data, dict) else {}


def _agent_files():
    return sorted(p for p in AGENTS.glob("*.md") if p.name != "README.md")


class AgentFrontmatter(unittest.TestCase):
    def test_agents_directory_is_populated(self):
        """Vacuity guard: every other test here iterates the glob, so a moved or
        renamed `agents/` directory would make them all pass on zero files."""
        self.assertTrue(AGENTS.is_dir(), f"missing {AGENTS}")
        self.assertTrue(_agent_files(), f"no agent definitions under {AGENTS}")

    def test_every_agent_declares_tools(self):
        """No agent may inherit the full tool set by omission."""
        for agent in _agent_files():
            with self.subTest(agent=agent.name):
                fm = _frontmatter(agent)
                self.assertIn(
                    "tools",
                    fm,
                    f"{agent.name} declares no 'tools:' — it inherits every tool, "
                    "including Write, Edit and Bash. Declare an explicit allowlist.",
                )
                tools = fm["tools"]
                self.assertIsInstance(
                    tools, str, f"{agent.name} 'tools:' must be a comma-separated string"
                )
                names = [t.strip() for t in tools.split(",")]
                self.assertTrue(
                    names and all(names), f"{agent.name} has an empty entry in 'tools:'"
                )
                for name in names:
                    self.assertRegex(
                        name, TOOL_TOKEN, f"{agent.name} lists a malformed tool: {name!r}"
                    )

    def test_read_only_agents_hold_no_editing_tool(self):
        """`docs/AGENTS.md` presents the review gates as read-only, which is a
        security claim. `custom_fields.access` already records it per agent, so
        the claim is machine-checkable — and until now nothing checked it."""
        checked = []
        for agent in _agent_files():
            fm = _frontmatter(agent)
            if (fm.get("custom_fields") or {}).get("access") != "read-only":
                continue
            checked.append(agent.name)
            with self.subTest(agent=agent.name):
                names = {t.strip() for t in str(fm.get("tools", "")).split(",")}
                self.assertFalse(
                    names & EDITING_TOOLS,
                    f"{agent.name} is declared access: read-only but holds "
                    f"{sorted(names & EDITING_TOOLS)}",
                )
        self.assertTrue(
            checked,
            "no agent declares custom_fields.access: read-only — either the key "
            "was renamed or the review gates lost their marking; this test "
            "would otherwise pass by checking nothing",
        )

    def test_every_agent_declares_a_documented_model(self):
        for agent in _agent_files():
            with self.subTest(agent=agent.name):
                fm = _frontmatter(agent)
                self.assertIn("model", fm, f"{agent.name} declares no 'model:'")
                self.assertIn(
                    fm["model"],
                    DOCUMENTED_MODELS,
                    f"{agent.name} declares model {fm['model']!r}, which is not one of "
                    f"the tiers docs/AGENTS.md documents ({sorted(DOCUMENTED_MODELS)})",
                )


if __name__ == "__main__":
    unittest.main()
