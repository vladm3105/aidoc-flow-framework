"""Live acceptance: Layer 4 — BDD."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[0]))
from _live_harness import assert_live_layer_conformant, skipUnlessLive  # noqa: E402


@skipUnlessLive
class LayerBddLiveTests(unittest.TestCase):
    def test_doc_bdd_emits_conformant_artifact(self):
        assert_live_layer_conformant(
            self,
            layer_index=4,
            prompt=(
                "/aidoc-flow:doc-bdd Create BDD-01 from the staged EARS-01. "
                "Use Given/When/Then. "
                "Output: docs/04_BDD/BDD-01_url_shortener.md."
            ),
        )


if __name__ == "__main__":
    unittest.main()
