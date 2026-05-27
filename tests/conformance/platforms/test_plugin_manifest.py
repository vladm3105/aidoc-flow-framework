"""Conformance: the Claude Code plugin is a valid, installable, self-contained
unit (PLUGIN-MARKETPLACE P1).

Deterministic checks that fail CI if the manifest, component frontmatter, hook
config, or bundled references regress:

* ``plugin.json`` — valid JSON; ``name`` kebab-case; ``description`` present;
  recommended ``version`` / ``author`` / ``license`` present.
* every ``skills/*/SKILL.md`` has a non-empty ``description``.
* every ``agents/*.md`` has ``name`` + non-empty ``description``.
* ``hooks/hooks.json`` — valid JSON with a ``hooks`` object.
* **Bundled-reference resolution** — every ``${CLAUDE_PLUGIN_ROOT}/framework/…``
  path a plugin file cites resolves to a real file/dir in the vendored bundle
  (the check that would have caught the 47 broken refs).
"""

import json
import re
import unittest

import yaml
from _spec import REPO_ROOT

PLUGIN = REPO_ROOT / "platforms" / "claude-code-plugin"
MANIFEST = PLUGIN / ".claude-plugin" / "plugin.json"
HOOKS = PLUGIN / "hooks" / "hooks.json"
BUNDLE = PLUGIN / "framework"

KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
PLUGIN_ROOT_REF = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/(framework/[^\s`)\]]+)")
# Placeholder paths (template/example forms), not concrete bundled files.
PLACEHOLDER = re.compile(r"<|>|\bNN_|\b0N_|\.\.\.|…")
SCAN_SUFFIXES = (".md", ".yaml", ".yml", ".json", ".sh")


def _frontmatter(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[3:end]
    data = yaml.safe_load(block)
    return data if isinstance(data, dict) else {}


def _plugin_files():
    """Every plugin file we scan for references — excludes the vendored bundle
    (its internal cross-refs are advisory; see D-0022 / Approach A.5)."""
    for path in sorted(PLUGIN.rglob("*")):
        if not path.is_file() or path.suffix not in SCAN_SUFFIXES:
            continue
        if BUNDLE in path.parents:
            continue
        yield path


class PluginManifest(unittest.TestCase):
    def test_manifest_valid(self):
        self.assertTrue(MANIFEST.is_file(), f"missing {MANIFEST}")
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertIn("name", data, "plugin.json must have a name")
        self.assertRegex(data["name"], KEBAB, "plugin.json name must be kebab-case")
        self.assertTrue(data.get("description", "").strip(), "plugin.json needs a description")
        for field in ("version", "author", "license"):
            self.assertIn(field, data, f"plugin.json should declare '{field}'")

    def test_hooks_valid(self):
        self.assertTrue(HOOKS.is_file(), f"missing {HOOKS}")
        data = json.loads(HOOKS.read_text(encoding="utf-8"))
        self.assertIsInstance(data.get("hooks"), dict, "hooks.json needs a 'hooks' object")

    def test_skills_have_description(self):
        skill_files = sorted((PLUGIN / "skills").glob("*/SKILL.md"))
        self.assertTrue(skill_files, "no skills found")
        for skill in skill_files:
            with self.subTest(skill=skill.parent.name):
                fm = _frontmatter(skill)
                self.assertTrue(
                    str(fm.get("description", "")).strip(),
                    f"{skill.relative_to(PLUGIN)} needs a frontmatter description",
                )

    def test_agents_have_name_and_description(self):
        agent_files = sorted(p for p in (PLUGIN / "agents").glob("*.md") if p.name != "README.md")
        self.assertTrue(agent_files, "no agents found")
        for agent in agent_files:
            with self.subTest(agent=agent.name):
                fm = _frontmatter(agent)
                self.assertTrue(str(fm.get("name", "")).strip(), f"{agent.name} needs a name")
                self.assertTrue(
                    str(fm.get("description", "")).strip(),
                    f"{agent.name} needs a description",
                )

    def test_bundled_references_resolve(self):
        dangling = []
        for path in _plugin_files():
            text = path.read_text(encoding="utf-8")
            for m in PLUGIN_ROOT_REF.finditer(text):
                ref = m.group(1).rstrip(".,;:")
                if PLACEHOLDER.search(ref):
                    continue
                target = PLUGIN / ref
                if not (target.is_file() or target.is_dir()):
                    line = text.count("\n", 0, m.start()) + 1
                    dangling.append(f"{path.relative_to(PLUGIN)}:{line}: {ref}")
        self.assertFalse(
            dangling,
            "references to the vendored bundle that do not resolve "
            f"({len(dangling)}):\n  " + "\n  ".join(dangling[:25]),
        )


if __name__ == "__main__":
    unittest.main()
