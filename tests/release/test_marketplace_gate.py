"""Release: aggregate gate — release-time invariants in one suite."""

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "conformance"))
from _spec import plugin_bundle_root, skill_dirs


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
    """No SKILL.md may include '--dangerously-skip-permissions' as a default."""

    def test_no_skip_permissions_default_in_skills(self):
        offenders = []
        for skill in skill_dirs():
            if not skill.is_dir():
                continue
            md = skill / "SKILL.md"
            if not md.exists():
                continue
            text = md.read_text(encoding="utf-8")
            if "--dangerously-skip-permissions" in text:
                offenders.append(skill.name)
        self.assertFalse(
            offenders, f"SKILL.md should not advertise --dangerously-skip-permissions: {offenders}"
        )


class ManifestSchemaTests(unittest.TestCase):
    def test_plugin_json_exists(self):
        self.assertTrue((plugin_bundle_root() / ".claude-plugin" / "plugin.json").exists())
