"""Live acceptance: Layer 2 — PRD."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[0]))
from _live_harness import assert_live_layer_conformant, skipUnlessLive  # noqa: E402


@skipUnlessLive
class LayerPrdLiveTests(unittest.TestCase):
    def test_doc_prd_emits_conformant_artifact(self):
        assert_live_layer_conformant(
            self,
            layer_index=2,
            prompt=(
                "/aidoc-flow:doc-prd Create PRD-01 from the staged BRD-01 in docs/01_BRD/. "
                "Write to docs/02_PRD/PRD-01_url_shortener/."
            ),
        )


if __name__ == "__main__":
    unittest.main()
