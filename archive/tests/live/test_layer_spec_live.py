"""Live acceptance: Layer 6 — SPEC."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[0]))
from _live_harness import assert_live_layer_conformant, skipUnlessLive  # noqa: E402


@skipUnlessLive
class LayerSpecLiveTests(unittest.TestCase):
    def test_doc_spec_emits_conformant_artifact(self):
        assert_live_layer_conformant(
            self,
            layer_index=6,
            prompt=(
                "/aidoc-flow:doc-spec Create SPEC-01 for the shorten service (C4-L3 only) "
                "from the staged ADR-01. "
                "Output: docs/06_SPEC/SPEC-01_shorten_service/SPEC-01_shorten_service.yaml."
            ),
        )


if __name__ == "__main__":
    unittest.main()
