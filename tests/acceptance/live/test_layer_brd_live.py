"""Live acceptance: Layer 1 — BRD."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[0]))
from _live_harness import assert_live_layer_conformant, skipUnlessLive  # noqa: E402


@skipUnlessLive
class LayerBrdLiveTests(unittest.TestCase):
    def test_doc_brd_emits_conformant_artifact(self):
        assert_live_layer_conformant(
            self,
            layer_index=1,
            prompt=(
                "/aidoc-flow:doc-brd Create BRD-01 from this brief and write it to "
                "docs/01_BRD/BRD-01_url_shortener/. Brief: Build a URL shortener with "
                "shorten, redirect, click-count features."
            ),
        )


if __name__ == "__main__":
    unittest.main()
