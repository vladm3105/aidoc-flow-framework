"""Packaging: VERSION and FRAMEWORK_SPEC_VERSION are aligned across the bundle."""

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "conformance"))
from _spec import FRAMEWORK, plugin_bundle_root

SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")


class VersionGateTests(unittest.TestCase):
    def test_framework_version_is_semver(self):
        v = (FRAMEWORK / "VERSION").read_text(encoding="utf-8").strip()
        self.assertRegex(v, SEMVER_RE)

    def test_framework_spec_version_files_match_framework_version(self):
        v = (FRAMEWORK / "VERSION").read_text(encoding="utf-8").strip()
        for candidate in [
            plugin_bundle_root() / "FRAMEWORK_SPEC_VERSION",
            FRAMEWORK.parent / "platforms" / "hermes" / "FRAMEWORK_SPEC_VERSION",
        ]:
            if candidate.exists():
                self.assertEqual(
                    candidate.read_text(encoding="utf-8").strip(),
                    v,
                    f"{candidate} mismatch with framework/VERSION",
                )
