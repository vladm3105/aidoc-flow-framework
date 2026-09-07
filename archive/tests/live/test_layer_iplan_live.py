"""Live acceptance: Layer 8 — IPLAN."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[0]))
from _live_harness import assert_live_layer_conformant, skipUnlessLive  # noqa: E402


@skipUnlessLive
class LayerIplanLiveTests(unittest.TestCase):
    def test_doc_iplan_emits_conformant_artifact(self):
        assert_live_layer_conformant(
            self,
            layer_index=8,
            prompt=(
                "/aidoc-flow:doc-iplan Create IPLAN-01 (permanent) for SPEC-01 + TDD-01. "
                "file_manifest must list tests before implementation. "
                "Output: docs/08_IPLAN/IPLAN-01_shorten_service.yaml."
            ),
        )


if __name__ == "__main__":
    unittest.main()
