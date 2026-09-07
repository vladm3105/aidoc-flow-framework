"""Live acceptance: Layer 3 — EARS."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[0]))
from _live_harness import assert_live_layer_conformant, skipUnlessLive  # noqa: E402


@skipUnlessLive
class LayerEarsLiveTests(unittest.TestCase):
    def test_doc_ears_emits_conformant_artifact(self):
        assert_live_layer_conformant(
            self,
            layer_index=3,
            prompt=(
                "/aidoc-flow:doc-ears Create EARS-01 from the staged PRD-01. "
                "Use WHEN-THE-SHALL-WITHIN form. "
                "Output: docs/03_EARS/EARS-01_url_shortener.md."
            ),
        )


if __name__ == "__main__":
    unittest.main()
