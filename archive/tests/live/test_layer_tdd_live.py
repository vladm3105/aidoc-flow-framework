"""Live acceptance: Layer 7 — TDD."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[0]))
from _live_harness import assert_live_layer_conformant, skipUnlessLive  # noqa: E402


@skipUnlessLive
class LayerTddLiveTests(unittest.TestCase):
    def test_doc_tdd_emits_conformant_artifact(self):
        assert_live_layer_conformant(
            self,
            layer_index=7,
            prompt=(
                "/aidoc-flow:doc-tdd Create TDD-01 from SPEC-01 + BDD-01. "
                "Each test case has a `type` attribute. "
                "Output: docs/07_TDD/TDD-01_shorten_service.yaml."
            ),
        )


if __name__ == "__main__":
    unittest.main()
