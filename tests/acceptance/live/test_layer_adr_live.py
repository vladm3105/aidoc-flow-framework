"""Live acceptance: Layer 5 — ADR."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[0]))
from _live_harness import assert_live_layer_conformant, skipUnlessLive  # noqa: E402


@skipUnlessLive
class LayerAdrLiveTests(unittest.TestCase):
    def test_doc_adr_emits_conformant_artifact(self):
        assert_live_layer_conformant(
            self,
            layer_index=5,
            prompt=(
                "/aidoc-flow:doc-adr Create ADR-01 for the short-code-generation decision "
                "(Status: Accepted). "
                "Output: docs/05_ADR/ADR-01_short_code_strategy.md."
            ),
        )


if __name__ == "__main__":
    unittest.main()
