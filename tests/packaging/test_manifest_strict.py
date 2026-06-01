"""Packaging: `claude plugin validate --strict` passes on the bundle."""

import shutil
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "conformance"))
from _spec import plugin_bundle_root


@unittest.skipUnless(shutil.which("claude"), "claude CLI not on PATH")
class ManifestStrictTests(unittest.TestCase):
    def test_plugin_validate_strict_succeeds(self):
        result = subprocess.run(
            ["claude", "plugin", "validate", str(plugin_bundle_root()), "--strict"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(
            result.returncode,
            0,
            f"validate --strict failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}",
        )


if __name__ == "__main__":
    unittest.main()
