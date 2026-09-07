"""Live acceptance: invoke each layer's autopilot in sequence."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[0]))
from _live_harness import invoke_skill, skipUnlessLive  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _harness import run_lint  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "conformance"))
from _spec import ARTIFACTS  # noqa: E402

SEED = "Build a URL shortener: shorten, redirect, count clicks. Target: 1M URLs/day."


@skipUnlessLive
class FullpathLiveTests(unittest.TestCase):
    def test_full_chain_from_seed_produces_all_8_layers(self):
        with tempfile.TemporaryDirectory() as td:
            ws = Path(td)
            (ws / "seed").mkdir()
            (ws / "seed" / "initial-requirements.md").write_text(SEED, encoding="utf-8")

            invoke_skill(
                "/aidoc-flow:doc-brd-autopilot from seed/initial-requirements.md write BRD-01",
                cwd=ws,
                timeout=480,
                test_id="T4L.fullpath.brd",
            )
            for layer in ["prd", "ears", "bdd", "adr", "spec", "tdd", "iplan"]:
                invoke_skill(
                    f"/aidoc-flow:doc-{layer}-autopilot continue the chain",
                    cwd=ws,
                    timeout=480,
                    test_id=f"T4L.fullpath.{layer}",
                )

            for idx, name in enumerate(ARTIFACTS, start=1):
                with self.subTest(layer=name):
                    folder = ws / "docs" / f"{idx:02d}_{name}"
                    hits = list(folder.rglob(f"{name}-01*"))
                    self.assertTrue(hits, f"{folder}: no artifact emitted")

            rc, findings = run_lint(ws / "docs")
            self.assertEqual(rc, 0, f"live fullpath lint failed:\n{findings}")
