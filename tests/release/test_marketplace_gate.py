"""Release: aggregate gate — release-time invariants in one suite."""

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "conformance"))
from _spec import plugin_bundle_root


class NoNetworkEgressTests(unittest.TestCase):
    """No plugin-bundled python code may import network modules."""

    FORBIDDEN = [
        r"^\s*import\s+requests\b",
        r"^\s*from\s+requests\b",
        r"^\s*import\s+urllib\.request\b",
        r"^\s*from\s+urllib\.request\b",
        r"^\s*import\s+httpx\b",
        r"^\s*from\s+httpx\b",
        r"\bsocket\.socket\b",
    ]

    def test_no_network_imports_in_plugin_code(self):
        scan_roots = [plugin_bundle_root() / "sdd_doc_lint"]
        offenders: list[tuple[str, str]] = []
        for root in scan_roots:
            if not root.exists():
                continue
            for py in root.rglob("*.py"):
                text = py.read_text(encoding="utf-8")
                for pattern in self.FORBIDDEN:
                    if re.search(pattern, text, re.MULTILINE):
                        offenders.append((str(py), pattern))
        self.assertFalse(offenders, f"forbidden network calls: {offenders}")


class NoDangerousFlagDefaultsTests(unittest.TestCase):
    """Ensure no unauthorized skip-permission bypasses exist in skills, commands, or agents."""

    AUTOPILOT_SKILLS = {
        "doc-brd-autopilot",
        "doc-prd-autopilot",
        "doc-ears-autopilot",
        "doc-bdd-autopilot",
        "doc-adr-autopilot",
        "doc-spec-autopilot",
        "doc-tdd-autopilot",
        "doc-iplan-autopilot",
        "doc-chg-autopilot",
    }

    def test_no_dangerously_skip_permissions_literal_in_skills_commands_agents(self):
        plugin_root = plugin_bundle_root()
        offenders = []
        scan_dirs = [plugin_root / "skills", plugin_root / "commands", plugin_root / "agents"]
        for d in scan_dirs:
            if not d.is_dir():
                continue
            for f in d.rglob("*.md"):
                text = f.read_text(encoding="utf-8")
                if "--dangerously-skip-permissions" in text:
                    offenders.append(str(f.relative_to(plugin_root)))
        self.assertFalse(
            offenders,
            f"Surfaces should not contain raw --dangerously-skip-permissions: {offenders}",
        )

    def test_allow_skip_permissions_only_in_authorized_autopilot_skills(self):
        plugin_root = plugin_bundle_root()
        offenders = []
        scan_dirs = [plugin_root / "skills", plugin_root / "commands", plugin_root / "agents"]
        for d in scan_dirs:
            if not d.is_dir():
                continue
            for f in d.rglob("*.md"):
                text = f.read_text(encoding="utf-8")
                if "--allow-skip-permissions" in text:
                    rel_dir = f.parent.name
                    if rel_dir not in self.AUTOPILOT_SKILLS:
                        offenders.append(str(f.relative_to(plugin_root)))
        self.assertFalse(
            offenders,
            f"Only authorized autopilot skills may advertise --allow-skip-permissions: {offenders}",
        )


class ManifestSchemaTests(unittest.TestCase):
    def test_plugin_json_exists(self):
        self.assertTrue((plugin_bundle_root() / ".claude-plugin" / "plugin.json").exists())
