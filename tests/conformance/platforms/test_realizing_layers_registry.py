"""Conformance: the reference linter's ``REALIZING_LAYERS`` constant matches the
spec's normative realizing map (``registry/LAYER_REGISTRY.yaml`` ``realizing_layers``).

The element-level backward-coverage map (COV02 / D-0039) is declared normatively
in the framework registry so an independent engine can implement COV02 from the
spec alone. This guard asserts the reference ``sdd_doc_lint`` constant has not
drifted from that declaration (FRWK-REVIEW-002 D1).
"""

import sys
import unittest

from _spec import REPO_ROOT, load_registry

sys.path.insert(0, str(REPO_ROOT / "tools"))
from sdd_doc_lint import REALIZING_LAYERS  # noqa: E402


class RealizingLayersRegistry(unittest.TestCase):
    def test_registry_declares_realizing_layers(self):
        block = load_registry().get("realizing_layers")
        self.assertIsInstance(
            block, dict, "registry/LAYER_REGISTRY.yaml must declare a realizing_layers map"
        )

    def test_lint_constant_matches_registry(self):
        block = load_registry().get("realizing_layers") or {}
        registry_norm = {k: tuple(v) for k, v in block.items()}
        lint_norm = {k: tuple(v) for k, v in REALIZING_LAYERS.items()}
        self.assertEqual(
            lint_norm,
            registry_norm,
            "sdd_doc_lint.REALIZING_LAYERS drifted from registry realizing_layers — "
            "reconcile the constant and the registry block",
        )
