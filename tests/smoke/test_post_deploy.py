"""Smoke: install plugin from marketplace URL and run the doc-flow probe.

Skipped unless MARKETPLACE_URL is set and the claude CLI is available.
"""

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

MARKETPLACE_URL = os.environ.get("MARKETPLACE_URL")
HAS_CLAUDE = shutil.which("claude") is not None


@unittest.skipUnless(
    MARKETPLACE_URL and HAS_CLAUDE, "MARKETPLACE_URL not set or claude CLI unavailable"
)
class PostDeploySmokeTests(unittest.TestCase):
    def test_install_and_invoke_doc_flow(self):
        with tempfile.TemporaryDirectory() as td:
            ws = Path(td)
            installer = Path(__file__).resolve().parent / "install-from-marketplace.sh"
            r = subprocess.run(
                ["bash", str(installer), str(ws)],
                env={**os.environ},
                capture_output=True,
                text=True,
            )
            self.assertEqual(r.returncode, 0, f"install failed:\n{r.stderr}")
            probe = subprocess.run(
                [
                    "claude",
                    "--dangerously-skip-permissions",
                    "-p",
                    "/aidoc-flow:doc-flow scan and report status",
                ],
                cwd=str(ws),
                capture_output=True,
                text=True,
                timeout=420,
            )
            self.assertEqual(probe.returncode, 0, f"doc-flow failed:\n{probe.stderr}")
            banned = [
                "compact 10-section",
                "documented walkthrough",
                "pinned to lint",
                "enterprise template",
                "10-section markdown",
            ]
            lc = probe.stdout.lower()
            for phrase in banned:
                self.assertNotIn(phrase, lc, f"post-deploy probe contains banned: {phrase}")
